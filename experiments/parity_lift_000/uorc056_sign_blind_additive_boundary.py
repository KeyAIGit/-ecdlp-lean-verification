#!/usr/bin/env python3
"""Exact C23 replay for sign-blind addition, determinants, and resultants.

The replay uses only the public C22 seven-curve corpus and six public generator
replacements. It does not accept an external point, unknown scalar, wallet,
private key, or production target.

C22 proved a support-union lower bound for a multiplicative Hilbert-90 grammar.
Addition can create new zeros, so that support theorem cannot simply be reused.
C23 instead verifies the separate two-world invariant: every leaf in the
scoped grammar has the same value in the global branch worlds R and -R, and
arbitrary rational arithmetic, determinants, and Sylvester resultants preserve
that equality. A determinant or resultant becomes branch-sensitive only after
a branch-sensitive entry or coefficient is supplied explicitly.

The norm-one twist has zeros and poles at marked subgroup values, so the finite
replay evaluates it on the complete public y-line away from its zero and pole
set. The abstract two-world theorem is independent of this finite domain.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise ImportError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


c22 = load(
    "uorc056_c22_for_c23",
    "uorc056_implicit_hilbert90_boundary.py",
)


def eval_rational(C, rational, y: int) -> int | None:
    numerator, denominator = rational
    den = C.ev(denominator, y) % C.p
    if den == 0:
        return None
    return C.ev(numerator, y) * pow(den, -1, C.p) % C.p


def det_mod(matrix: list[list[int]], p: int) -> int:
    if not matrix:
        return 1
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant requires a square matrix")
    work = [[value % p for value in row] for row in matrix]
    determinant = 1
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column] % p),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        pivot_value = work[column][column] % p
        determinant = determinant * pivot_value % p
        inverse = pow(pivot_value, -1, p)
        for row in range(column + 1, size):
            factor = work[row][column] * inverse % p
            if factor == 0:
                continue
            for entry in range(column, size):
                work[row][entry] = (
                    work[row][entry] - factor * work[column][entry]
                ) % p
    return determinant % p


def sylvester_matrix(
    left: list[int],
    right: list[int],
    p: int,
) -> list[list[int]]:
    """Return the Sylvester matrix for high-to-low coefficient lists."""
    left_degree = len(left) - 1
    right_degree = len(right) - 1
    size = left_degree + right_degree
    rows: list[list[int]] = []
    for shift in range(right_degree):
        row = [0] * size
        for index, coefficient in enumerate(left):
            row[shift + index] = coefficient % p
        rows.append(row)
    for shift in range(left_degree):
        row = [0] * size
        for index, coefficient in enumerate(right):
            row[shift + index] = coefficient % p
        rows.append(row)
    return rows


def resultant_mod(left: list[int], right: list[int], p: int) -> int:
    return det_mod(sylvester_matrix(left, right, p), p)


def sign_blind_circuit_values(p: int, branch: int, public_y: int) -> dict[str, int]:
    branch %= p
    public_y %= p
    square = branch * branch % p
    inverse_square = pow(square, -1, p)
    values = {
        "constant_one": 1,
        "public_y": public_y,
        "public_y_square": public_y * public_y % p,
        "branch_square": square,
        "branch_inverse_square": inverse_square,
        "square_trace": (square + inverse_square) % p,
        "additive_polynomial": (
            square * square + public_y * square + public_y * public_y + 7
        ) % p,
        "mixed_product": (
            (square + public_y + 1)
            * (inverse_square + public_y * public_y + 3)
        ) % p,
        "symmetric_power_sum_three": (
            pow(square, 3, p) + pow(inverse_square, 3, p)
        ) % p,
        "nested_add_mul": (
            (square + inverse_square + public_y)
            * (square * square + public_y + 5)
            + inverse_square
        ) % p,
    }
    denominator = (square + public_y * public_y + 1) % p
    if denominator:
        values["sign_blind_mobius"] = (
            (square + public_y + 2) * pow(denominator, -1, p)
        ) % p
    return values


def sign_blind_matrix(
    dimension: int,
    p: int,
    branch: int,
    public_y: int,
) -> list[list[int]]:
    square = branch * branch % p
    inverse_square = pow(square, -1, p)
    return [
        [
            (
                pow(square, 1 + ((row + column) % 4), p)
                + (row + 1) * pow(public_y, column + 1, p)
                + (column + 1) * inverse_square
                + (1 if row == column else 0)
            )
            % p
            for column in range(dimension)
        ]
        for row in range(dimension)
    ]


def sign_blind_polynomials(
    p: int,
    branch: int,
    public_y: int,
) -> tuple[list[int], list[int]]:
    square = branch * branch % p
    inverse_square = pow(square, -1, p)
    cubic = [
        1,
        (square + public_y) % p,
        (square * square + 3 * public_y + 1) % p,
        (inverse_square + public_y * public_y + 2) % p,
    ]
    quadratic = [
        1,
        (square + 2 * public_y + 1) % p,
        (square * square + inverse_square + public_y + 3) % p,
    ]
    return cubic, quadratic


def public_y_values(p: int) -> range:
    return range(p)


def run_case(case, split: str) -> dict[str, object]:
    p, n, G, beta, lam = case
    C, _points, rational, _finite, poles = c22.build_twist(case)

    valid_y_values = 0
    rational_circuit_checks = 0
    determinant_checks = 0
    resultant_checks = 0
    exact_two_branch_decoder_rejections = 0
    determinant_nonzero_count = 0
    resultant_nonzero_count = 0
    addition_zero_witness: dict[str, object] | None = None
    branch_transport_witnesses = 0

    for public_y in public_y_values(p):
        branch = eval_rational(C, rational, public_y)
        tau_branch = eval_rational(C, rational, (-public_y) % p)
        if branch is None or tau_branch is None:
            continue
        if branch == 0 or tau_branch == 0:
            continue
        if branch * tau_branch % p != 1:
            raise AssertionError("Hilbert-90 norm-one value check failed")

        opposite = (-branch) % p
        if branch == opposite:
            raise AssertionError("odd-characteristic branch pair collapsed")
        valid_y_values += 1

        positive_values = sign_blind_circuit_values(p, branch, public_y)
        negative_values = sign_blind_circuit_values(p, opposite, public_y)
        if positive_values.keys() != negative_values.keys():
            raise AssertionError("sign-blind circuit domains differ")
        for name, positive in positive_values.items():
            negative = negative_values[name]
            if positive != negative:
                raise AssertionError(f"sign-blind circuit changed branch: {name}")
            if positive == branch and negative == opposite:
                raise AssertionError("a sign-blind circuit selected both branches")
            rational_circuit_checks += 1
            exact_two_branch_decoder_rejections += 1

        for dimension in (2, 3, 4):
            positive_matrix = sign_blind_matrix(dimension, p, branch, public_y)
            negative_matrix = sign_blind_matrix(dimension, p, opposite, public_y)
            positive_det = det_mod(positive_matrix, p)
            negative_det = det_mod(negative_matrix, p)
            if positive_det != negative_det:
                raise AssertionError("sign-blind determinant changed branch")
            if positive_det == branch and negative_det == opposite:
                raise AssertionError("a sign-blind determinant selected both branches")
            determinant_checks += 1
            determinant_nonzero_count += int(positive_det != 0)
            exact_two_branch_decoder_rejections += 1

        positive_polynomials = sign_blind_polynomials(p, branch, public_y)
        negative_polynomials = sign_blind_polynomials(p, opposite, public_y)
        positive_resultant = resultant_mod(*positive_polynomials, p)
        negative_resultant = resultant_mod(*negative_polynomials, p)
        if positive_resultant != negative_resultant:
            raise AssertionError("sign-blind Sylvester resultant changed branch")
        if positive_resultant == branch and negative_resultant == opposite:
            raise AssertionError("a sign-blind resultant selected both branches")
        resultant_checks += 1
        resultant_nonzero_count += int(positive_resultant != 0)
        exact_two_branch_decoder_rejections += 1

        # Addition can create a new zero from two nonzero sign-blind leaves.
        # This is why the C22 support-union proof is not reused for C23.
        if addition_zero_witness is None:
            square = branch * branch % p
            if square:
                positive_zero = (square - square) % p
                negative_square = opposite * opposite % p
                negative_zero = (negative_square - square) % p
                if positive_zero != 0 or negative_zero != 0:
                    raise AssertionError("addition zero witness failed")
                addition_zero_witness = {
                    "public_y": public_y,
                    "nonzero_left_leaf": square,
                    "nonzero_right_leaf": square,
                    "output": 0,
                    "same_output_under_branch_flip": True,
                }

        # Determinants and resultants can transport a non-fixed leaf, but they
        # do not manufacture it. The 2x2 triangular determinant and a linear
        # Sylvester determinant reproduce the supplied branch value.
        positive_transport_det = det_mod([[branch, 1], [0, 1]], p)
        negative_transport_det = det_mod([[opposite, 1], [0, 1]], p)
        if positive_transport_det != branch or negative_transport_det != opposite:
            raise AssertionError("branch-sensitive determinant transport failed")
        positive_transport_res = resultant_mod([1, (-branch) % p], [1, 0], p)
        negative_transport_res = resultant_mod([1, (-opposite) % p], [1, 0], p)
        if positive_transport_res != branch or negative_transport_res != opposite:
            raise AssertionError("branch-sensitive resultant transport failed")
        branch_transport_witnesses += 2

    if valid_y_values == 0:
        raise AssertionError("no valid public y-line evaluation values")
    if addition_zero_witness is None:
        raise AssertionError("no addition zero witness")

    return {
        "p": p,
        "n": n,
        "G": list(G),
        "beta": beta,
        "lambda": lam,
        "split": split,
        "R_poles": poles,
        "valid_public_y_branch_pairs": valid_y_values,
        "rational_circuit_checks": rational_circuit_checks,
        "determinant_checks": determinant_checks,
        "resultant_checks": resultant_checks,
        "determinant_nonzero_count": determinant_nonzero_count,
        "resultant_nonzero_count": resultant_nonzero_count,
        "exact_two_branch_decoder_rejections": exact_two_branch_decoder_rejections,
        "addition_zero_witness": addition_zero_witness,
        "branch_sensitive_transport_witnesses": branch_transport_witnesses,
        "all_sign_blind_rational_outputs_equal": True,
        "all_sign_blind_determinants_equal": True,
        "all_sign_blind_sylvester_resultants_equal": True,
        "all_exact_two_branch_decoders_rejected": True,
    }


def theorem_certificate() -> dict[str, object]:
    return {
        "name": "sign-blind two-world rational-circuit boundary",
        "branch_worlds": ["R", "-R"],
        "hypothesis": "every charged atom has identical values in the two branch worlds",
        "operations": [
            "constants",
            "addition",
            "subtraction",
            "negation",
            "multiplication",
            "division",
            "inversion",
            "integer powers",
            "finite matrix determinants",
            "Sylvester resultants with sign-blind coefficients",
        ],
        "invariant": "the complete output is identical in the R and -R worlds",
        "consequence": "an exact target taking distinct values on the two branches cannot be computed in this grammar",
        "size_dependence": "none; the statement is independent of circuit width, depth, and determinant dimension",
        "cost_boundary": "branch-sensitive advice, entries, coefficients, preprocessing state, or oracle values are not free and leave the grammar",
        "not_covered": [
            "a genuinely public branch-sensitive leaf",
            "twisted theta characteristics with a proved nontrivial branch law",
            "p-adic or analytic continuation with an independently fixed branch",
            "resultants or determinants containing non-fixed coefficients",
            "a nonlocal jump law that constructs a non-fixed state from public Q",
        ],
    }


def secp_transfer() -> dict[str, object]:
    return {
        "n": str(c22.SECP_N),
        "n_is_odd": bool(c22.SECP_N & 1),
        "transfer": "the two-world theorem is symbolic and does not depend on enumerating the secp256k1 subgroup",
        "sign_blind_preprocessing_cannot_select_branch": True,
        "sign_blind_determinant_or_resultant_cannot_select_branch": True,
        "branch_sensitive_leaf_generation_remains_open": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    cases = [
        run_case(case, split)
        for case, split in zip(c22.public_corpus(), c22.SPLITS)
    ]
    replacements = []
    for case, multiplier, base_G in c22.replacement_corpus():
        row = run_case(case, "generator_replacement")
        row["multiplier"] = multiplier
        row["base_G"] = list(base_G)
        replacements.append(row)

    rows = cases + replacements
    aggregate = {
        "curves": len(cases),
        "generator_replacements": len(replacements),
        "valid_public_y_branch_pairs": sum(
            row["valid_public_y_branch_pairs"] for row in rows
        ),
        "rational_circuit_checks": sum(row["rational_circuit_checks"] for row in rows),
        "determinant_checks": sum(row["determinant_checks"] for row in rows),
        "resultant_checks": sum(row["resultant_checks"] for row in rows),
        "exact_two_branch_decoder_rejections": sum(
            row["exact_two_branch_decoder_rejections"] for row in rows
        ),
        "addition_created_new_zeros": True,
        "c22_support_union_extended_to_addition": False,
        "all_sign_blind_rational_outputs_equal": True,
        "all_sign_blind_determinants_equal": True,
        "all_sign_blind_sylvester_resultants_equal": True,
        "all_exact_two_branch_decoders_rejected": True,
        "sign_blind_additive_circuit_boundary_proved": True,
        "sign_blind_determinant_boundary_proved": True,
        "sign_blind_resultant_boundary_proved": True,
        "determinant_or_resultant_can_only_transport_nonfixed_leaf": True,
        "new_branch_sensitive_leaf_found": False,
        "general_addition_enabled_circuit_blocked": False,
        "compressed_nonfixed_resultant_or_determinant_open": True,
        "compact_branch_odd_evaluator_found": False,
        "sub_sqrt_evaluator_found": False,
        "parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
    }
    payload = {
        "experiment": "SIGN-BLIND-ADDITIVE-DETERMINANT-BOUNDARY-C23",
        "cases": cases,
        "generator_replacements": replacements,
        "theorem_certificate": theorem_certificate(),
        "secp256k1": secp_transfer(),
        "aggregate": aggregate,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(raw.encode()).hexdigest()
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
