#!/usr/bin/env python3
"""Generate the deterministic TASK-018 recursive-projective certificate.

The producer freezes a fixed-degree binary resultant recursion C2 through C16
without expanding or evaluating C16.  Exact low-degree fixtures exercise the
projective-infinity and extension-root boundaries.  No solver, rank, yield,
cost, or discrete-log computation is performed.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any


ARTIFACT_ID = "PKC-SMOOTH-M16-PROJECTIVE-S17-BRIDGE-001"
SCHEMA_VERSION = "1.0"
M = 16
EXCLUDED_CHARACTERISTICS = (2, 3, 7)

TASK017_ARTIFACT = (
    "experiments/engine/pkc_smooth_m16_exceptional_fibers/artifact.json"
)
TASK017_SHA256 = (
    "578db732807a452e26de03dcd338d62c25a7d90490a62bbf427b1f96c3a869cf"
)
TASK016_ARTIFACT = (
    "experiments/engine/pkc_smooth_m16_semantic_bridge/artifact.json"
)
TASK016_SHA256 = (
    "963eea60097807ae0aa66a5d881b0c34bf0497ade53ed4d37d38861a73887c19"
)
PRIMARY_CLAIM_EXTRACT = (
    "data/source_claim_extracts/petit_kosters_messeng2016.json"
)
PRIMARY_CLAIM_EXTRACT_SHA256 = (
    "f8839553f6935ed5cd331369cc13d91124373750c757b28eeca3ee773835f14f"
)

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"

Projective = tuple[int, int]
F25 = tuple[int, int]


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency_record(path: str, expected_sha256: str) -> dict[str, Any]:
    absolute = REPO_ROOT / path
    if not absolute.is_file():
        raise FileNotFoundError(path)
    observed = file_sha256(absolute)
    if observed != expected_sha256:
        raise AssertionError(
            f"dependency digest mismatch for {path}: {observed}"
        )
    return {
        "path": path,
        "required_sha256": expected_sha256,
        "observed_sha256": observed,
        "digest_match": True,
    }


def p1(prime: int) -> list[Projective]:
    return [(x, 1) for x in range(prime)] + [(1, 0)]


def projective_record(value: Projective) -> dict[str, Any]:
    x, z = value
    if x == 0 and z == 0:
        return {"X": 0, "Z": 0, "kind": "invalid"}
    if z == 0:
        return {"X": 1, "Z": 0, "kind": "infinity"}
    normalized_x = x * pow(z, -1, _record_prime) % _record_prime
    return {
        "X": normalized_x,
        "Z": 1,
        "kind": "finite",
        "x": normalized_x,
    }


# Set immediately around record construction.  Keeping the prime explicit in
# the artifact helper avoids silently comparing coordinates from two fields.
_record_prime = 0


def h_coefficients(
    left: Projective, right: Projective, prime: int
) -> list[int]:
    """Coefficients [U^2, U*V, V^2] of H(left,right,[U:V])."""
    x1, z1 = left
    x2, z2 = right
    return [
        (
            x1 * x1 * z2 * z2
            + z1 * z1 * x2 * x2
            - 2 * x1 * z1 * x2 * z2
        )
        % prime,
        (
            -2 * x1 * x1 * x2 * z2
            - 2 * x1 * z1 * x2 * x2
            - 28 * z1 * z1 * z2 * z2
        )
        % prime,
        (
            x1 * x1 * x2 * x2
            - 28
            * (
                x1 * z1 * z2 * z2
                + z1 * z1 * x2 * z2
            )
        )
        % prime,
    ]


def binary_eval(
    coefficients: list[int], value: Projective, prime: int
) -> int:
    u, v = value
    a2, a1, a0 = coefficients
    return (a2 * u * u + a1 * u * v + a0 * v * v) % prime


def h_eval(
    first: Projective,
    second: Projective,
    third: Projective,
    prime: int,
) -> int:
    return binary_eval(h_coefficients(first, second, prime), third, prime)


def poly_trim_asc(value: list[int], prime: int) -> list[int]:
    result = [coefficient % prime for coefficient in value]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_add_asc(
    left: list[int], right: list[int], prime: int
) -> list[int]:
    size = max(len(left), len(right))
    result = [0] * size
    for index in range(size):
        result[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        ) % prime
    return poly_trim_asc(result, prime)


def poly_scale_asc(
    value: list[int], scalar: int, prime: int
) -> list[int]:
    return poly_trim_asc(
        [(scalar * coefficient) % prime for coefficient in value],
        prime,
    )


def poly_mul_asc(
    left: list[int], right: list[int], prime: int
) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] = (
                result[left_index + right_index]
                + left_value * right_value
            ) % prime
    return poly_trim_asc(result, prime)


def poly_eval_desc(
    coefficients: list[int], value: int, prime: int
) -> int:
    result = 0
    for coefficient in coefficients:
        result = (result * value + coefficient) % prime
    return result


def poly_mul_desc(
    left: list[int], right: list[int], prime: int
) -> list[int]:
    ascending = poly_mul_asc(
        list(reversed(left)), list(reversed(right)), prime
    )
    return list(reversed(ascending))


def permutation_sign(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def determinant_poly_asc(
    matrix: list[list[list[int]]], prime: int
) -> list[int]:
    size = len(matrix)
    total = [0]
    for permutation in itertools.permutations(range(size)):
        term = [1]
        for row, column in enumerate(permutation):
            term = poly_mul_asc(term, matrix[row][column], prime)
        total = poly_add_asc(
            total,
            poly_scale_asc(term, permutation_sign(permutation), prime),
            prime,
        )
    return total


def determinant_mod(matrix: list[list[int]], prime: int) -> int:
    work = [[value % prime for value in row] for row in matrix]
    determinant = 1
    size = len(work)
    inverses = [0] + [pow(value, prime - 2, prime) for value in range(1, prime)]
    for column in range(size):
        pivot = next(
            (
                row
                for row in range(column, size)
                if work[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        pivot_value = work[column][column]
        determinant = determinant * pivot_value % prime
        pivot_inverse = inverses[pivot_value]
        for row in range(column + 1, size):
            if work[row][column] == 0:
                continue
            factor = work[row][column] * pivot_inverse % prime
            for offset in range(column, size):
                work[row][offset] = (
                    work[row][offset]
                    - factor * work[column][offset]
                ) % prime
    return determinant % prime


def sylvester_scalar(
    left: list[int],
    right: list[int],
    left_degree: int,
    right_degree: int,
) -> list[list[int]]:
    if len(left) != left_degree + 1:
        raise ValueError("left coefficient vector has the wrong formal degree")
    if len(right) != right_degree + 1:
        raise ValueError(
            "right coefficient vector has the wrong formal degree"
        )
    size = left_degree + right_degree
    matrix = [[0] * size for _ in range(size)]
    for shift in range(right_degree):
        matrix[shift][shift : shift + left_degree + 1] = left
    for shift in range(left_degree):
        row = right_degree + shift
        matrix[row][shift : shift + right_degree + 1] = right
    return matrix


def fixed_resultant(
    left: list[int],
    right: list[int],
    left_degree: int,
    right_degree: int,
    prime: int,
) -> int:
    return determinant_mod(
        sylvester_scalar(left, right, left_degree, right_degree),
        prime,
    )


def h_as_t_coefficient_polynomials(
    fixed_q: Projective, prime: int
) -> list[list[int]]:
    """T-descending coefficients of H(T,fixed_q,[y:1]).

    Every returned polynomial is ascending in y.
    """
    x, z = fixed_q
    return [
        [x * x % prime, -2 * x * z % prime, z * z % prime],
        [-28 * z * z % prime, -2 * x * x % prime, -2 * x * z % prime],
        [-28 * x * z % prime, -28 * z * z % prime, x * x % prime],
    ]


def c3_slice_coefficients(
    q1: Projective,
    q2: Projective,
    q3: Projective,
    prime: int,
) -> list[int]:
    """Return C3(q1,q2,q3;Y), descending in fixed degree four."""
    left = h_coefficients(q1, q2, prime)
    right = h_as_t_coefficient_polynomials(q3, prime)
    size = 4
    zero = [0]
    matrix = [[zero[:] for _ in range(size)] for _ in range(size)]
    for shift in range(2):
        for index, coefficient in enumerate(left):
            matrix[shift][shift + index] = [coefficient]
    for shift in range(2):
        for index, coefficient in enumerate(right):
            matrix[2 + shift][shift + index] = coefficient
    result_ascending = determinant_poly_asc(matrix, prime)
    if len(result_ascending) > 5:
        raise AssertionError("C3 exceeded its frozen output degree four")
    result_ascending += [0] * (5 - len(result_ascending))
    return list(reversed(result_ascending))


def curve_rhs(x: int, prime: int) -> int:
    return (x**3 + 7) % prime


def legendre_symbol(value: int, prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    result = pow(value, (prime - 1) // 2, prime)
    if result == 1:
        return 1
    if result == prime - 1:
        return -1
    raise AssertionError("Euler criterion returned an invalid value")


def coordinate_lifts_to_base(value: Projective, prime: int) -> bool:
    if value[1] == 0:
        return True
    return legendre_symbol(curve_rhs(value[0], prime), prime) >= 0


def p1_root_indices(
    first: Projective, second: Projective, domain: list[Projective], prime: int
) -> list[int]:
    coefficients = h_coefficients(first, second, prime)
    return [
        index
        for index, candidate in enumerate(domain)
        if binary_eval(coefficients, candidate, prime) == 0
    ]


def f25_add(left: F25, right: F25) -> F25:
    return ((left[0] + right[0]) % 5, (left[1] + right[1]) % 5)


def f25_mul(left: F25, right: F25) -> F25:
    # alpha^2 + 3*alpha + 4 = 0, hence alpha^2 = 2*alpha + 1.
    a, b = left
    c, d = right
    return ((a * c + b * d) % 5, (a * d + b * c + 2 * b * d) % 5)


def f25_pow(value: F25, exponent: int) -> F25:
    result = (1, 0)
    factor = value
    remaining = exponent
    while remaining:
        if remaining & 1:
            result = f25_mul(result, factor)
        factor = f25_mul(factor, factor)
        remaining >>= 1
    return result


def f25_eval_desc(coefficients: list[int], value: F25) -> F25:
    result = (0, 0)
    for coefficient in coefficients:
        result = f25_add(f25_mul(result, value), (coefficient % 5, 0))
    return result


def f25_record(value: F25) -> dict[str, int]:
    return {"constant": value[0], "alpha": value[1]}


def recursion_schedule() -> list[dict[str, Any]]:
    schedule: list[dict[str, Any]] = []
    for r in range(2, M + 1):
        output_degree = 1 << (r - 1)
        if r == 2:
            schedule.append(
                {
                    "r": r,
                    "name": "C2",
                    "semaev_arity": 3,
                    "leaf_count": 2,
                    "construction": "C2(Q1,Q2;Y)=H(Q1,Q2,Y)",
                    "output_projective_degree": output_degree,
                    "multidegree_each_coordinate_pair": output_degree,
                    "resultant_formal_degrees": None,
                    "sylvester_size": None,
                    "materialized_in_artifact": False,
                }
            )
            continue
        previous_degree = 1 << (r - 2)
        schedule.append(
            {
                "r": r,
                "name": f"C{r}",
                "semaev_arity": r + 1,
                "leaf_count": r,
                "construction": (
                    f"C{r}(Q1,...,Q{r};Y)="
                    f"hRes_T^({previous_degree},2)("
                    f"C{r - 1}(Q1,...,Q{r - 1};T),H(T,Q{r},Y))"
                ),
                "elimination_coordinate": "T=[T_U:T_V]",
                "previous_formal_degree_in_T": previous_degree,
                "right_H_formal_degree_in_T": 2,
                "resultant_formal_degrees": [previous_degree, 2],
                "sylvester_size": previous_degree + 2,
                "degree_in_left_form_coefficients": 2,
                "degree_in_right_H_coefficients": previous_degree,
                "output_projective_degree": output_degree,
                "multidegree_each_coordinate_pair": output_degree,
                "materialized_in_artifact": False,
            }
        )
    if schedule[-1]["output_projective_degree"] != 32_768:
        raise AssertionError("unexpected C16 degree")
    if schedule[-1]["resultant_formal_degrees"] != [16_384, 2]:
        raise AssertionError("unexpected final resultant degrees")
    return schedule


def f5_infinity_fixture() -> dict[str, Any]:
    prime = 5
    left = [0, 2, 0]
    right = [0, 4, 3]
    fixed_matrix = sylvester_scalar(left, right, 2, 2)
    fixed_value = determinant_mod(fixed_matrix, prime)
    reduced_left = [2, 0]
    reduced_right = [4, 3]
    reduced_matrix = sylvester_scalar(
        reduced_left, reduced_right, 1, 1
    )
    reduced_value = determinant_mod(reduced_matrix, prime)
    domain = p1(prime)
    common = [
        candidate
        for candidate in domain
        if binary_eval(left, candidate, prime) == 0
        and binary_eval(right, candidate, prime) == 0
    ]
    if fixed_value != 0 or reduced_value != 1:
        raise AssertionError("F5 infinity fixture changed")
    if common != [(1, 0)]:
        raise AssertionError("F5 infinity fixture has unexpected roots")
    return {
        "field": "F5",
        "curve": "y^2=x^3+7 = x^3+2",
        "recursive_step": "C3=S4",
        "external_tuple_x": [0, 0, 3, 3],
        "left_H00_coefficients_descending_U": left,
        "right_H33_coefficients_descending_U": right,
        "left_binary_factorization": "2*U*V",
        "right_binary_factorization": "V*(4*U+3*V)",
        "fixed_formal_degrees": [2, 2],
        "fixed_sylvester_matrix": fixed_matrix,
        "fixed_resultant_mod_5": fixed_value,
        "fixed_common_projective_roots": [
            {"U": 1, "V": 0, "kind": "infinity"}
        ],
        "reduced_affine_coefficients_descending_t": {
            "left": reduced_left,
            "right": reduced_right,
        },
        "reduced_actual_degrees": [1, 1],
        "reduced_sylvester_matrix": reduced_matrix,
        "reduced_affine_resultant_mod_5": reduced_value,
        "reduced_affine_common_roots": [],
        "fault_detected": (
            "reducing to actual affine degree deletes the valid common "
            "projective root [1:0]"
        ),
        "required_disposition": "retain_identity_infinity_stratum",
        "status": "exact",
    }


def f5_f25_fixture() -> dict[str, Any]:
    prime = 5
    q0 = (0, 1)
    q3 = (3, 1)
    left = c3_slice_coefficients(q0, q0, q3, prime)
    right = h_coefficients(q0, q3, prime)
    expected_left = [1, 2, 0, 3, 1]
    expected_right = [4, 2, 1]
    quotient = [4, 1, 1]
    if left != expected_left or right != expected_right:
        raise AssertionError(
            f"F5 extension fixture coefficients changed: {left}, {right}"
        )
    if poly_mul_desc(right, quotient, prime) != left:
        raise AssertionError("F5 exact polynomial quotient changed")
    resultant_matrix = sylvester_scalar(left, right, 4, 2)
    resultant_value = determinant_mod(resultant_matrix, prime)
    discriminant = (right[1] ** 2 - 4 * right[0] * right[2]) % prime
    base_roots = [
        value
        for value in range(prime)
        if poly_eval_desc(right, value, prime) == 0
    ]
    alpha: F25 = (0, 1)
    conjugate = f25_pow(alpha, 5)
    all_f25 = [(a, b) for a in range(5) for b in range(5)]
    common_roots = [
        value
        for value in all_f25
        if f25_eval_desc(left, value) == (0, 0)
        and f25_eval_desc(right, value) == (0, 0)
    ]
    if resultant_value != 0 or discriminant != 3 or base_roots:
        raise AssertionError("F5/F25 extension fixture boundary changed")
    if conjugate != (2, 4) or common_roots != [alpha, conjugate]:
        raise AssertionError("F25 common roots changed")
    if legendre_symbol(curve_rhs(0, prime), prime) != -1:
        raise AssertionError("x=0 must remain an external nonlift over F5")
    vertex_values = {
        "H_Q1_Q2_W2": h_eval(q0, q0, q0, prime),
        "H_W2_Q3_W3": f25_record(f25_eval_desc(right, alpha)),
        "H_W3_Q4_QT_by_symmetry": f25_record(
            f25_eval_desc(right, alpha)
        ),
    }
    return {
        "base_field": "F5",
        "witness_field": "F25",
        "witness_field_presentation": {
            "basis": ["1", "alpha"],
            "modulus_descending_alpha": [1, 3, 4],
            "relation": "alpha^2=2*alpha+1",
            "frobenius": "alpha^5=2-alpha",
        },
        "external_tuple": {
            "Q1": {"X": 0, "Z": 1},
            "Q2": {"X": 0, "Z": 1},
            "Q3": {"X": 3, "Z": 1},
            "Q4": {"X": 0, "Z": 1},
            "QT": {"X": 3, "Z": 1},
        },
        "external_tuple_x": [0, 0, 3, 0, 3],
        "left_form": "C3(Q1,Q2,Q3;T)=S4(Q1,Q2,Q3,T)",
        "left_C3_S4_coefficients_descending_T": left,
        "right_form": "H(T,Q4,QT)",
        "right_H_coefficients_descending_T": right,
        "exact_division_quotient_descending_T": quotient,
        "exact_division_remainder": [0],
        "right_quadratic_discriminant_mod_5": discriminant,
        "right_quadratic_irreducible_over_F5": True,
        "C4_S5_formal_resultant_degrees": [4, 2],
        "C4_S5_sylvester_matrix": resultant_matrix,
        "C4_S5_resultant_mod_5": resultant_value,
        "common_roots_in_F5": base_roots,
        "common_roots_in_F25": [
            f25_record(value) for value in common_roots
        ],
        "chosen_tree_witness": {
            "W2": {"U": 0, "V": 1, "field": "F5"},
            "W3": {
                "U": f25_record(alpha),
                "V": f25_record((1, 0)),
                "field": "F25",
            },
            "vertex_values": vertex_values,
        },
        "predicate_values": {
            "RecS5_F5": True,
            "GeoCat_F25": True,
            "RatCat_F5": False,
            "Recover_F5": False,
        },
        "nonlift_external_positions_one_based": [1, 2, 4],
        "nonlift_check": {
            "x": 0,
            "curve_rhs_mod_5": 2,
            "legendre_symbol": -1,
        },
        "combined_boundary": (
            "the common top-elimination roots are in F25 and the external "
            "x=0 coordinates do not lift to E(F5); this is not a pure "
            "internal-extension counterexample with liftable externals"
        ),
        "required_disposition": "EXTERNAL_NONLIFT",
        "status": "exact",
    }


def tree_witness(
    indices: tuple[int, int, int, int, int],
    domain: list[Projective],
    roots: dict[tuple[int, int], list[int]],
) -> tuple[int, int] | None:
    q1, q2, q3, q4, target = indices
    final_roots = set(roots[(q4, target)])
    for w2 in roots[(q1, q2)]:
        for w3 in roots[(w2, q3)]:
            if w3 in final_roots:
                return w2, w3
    return None


def tuple_record(
    indices: tuple[int, int, int, int, int],
    domain: list[Projective],
    prime: int,
) -> dict[str, Any]:
    global _record_prime
    _record_prime = prime
    names = ("Q1", "Q2", "Q3", "Q4", "QT")
    return {
        name: projective_record(domain[index])
        for name, index in zip(names, indices, strict=True)
    }


def exhaustive_s5_fixture(
    prime: int, expected: dict[str, int]
) -> dict[str, Any]:
    domain = p1(prime)
    roots = {
        (left, right): p1_root_indices(
            domain[left], domain[right], domain, prime
        )
        for left in range(len(domain))
        for right in range(len(domain))
    }
    root_masks = {
        key: sum(1 << index for index in values)
        for key, values in roots.items()
    }
    triples: list[tuple[int, int, int, list[int], int]] = []
    for q1 in range(len(domain)):
        for q2 in range(len(domain)):
            w2_roots = roots[(q1, q2)]
            for q3 in range(len(domain)):
                prefix_mask = 0
                for w2 in w2_roots:
                    prefix_mask |= root_masks[(w2, q3)]
                triples.append(
                    (
                        q1,
                        q2,
                        q3,
                        c3_slice_coefficients(
                            domain[q1], domain[q2], domain[q3], prime
                        ),
                        prefix_mask,
                    )
                )
    right_forms = {
        (q4, target): h_coefficients(
            domain[q4], domain[target], prime
        )
        for q4 in range(len(domain))
        for target in range(len(domain))
    }
    liftable = [
        coordinate_lifts_to_base(value, prime) for value in domain
    ]
    counts = {
        "tuple_count": 0,
        "recursive_zero_count": 0,
        "ratcat_count": 0,
        "recursive_zero_without_ratcat_count": 0,
        "ratcat_without_recursive_zero_count": 0,
        "base_liftable_tuple_count": 0,
        "base_liftable_recursive_zero_count": 0,
        "base_liftable_ratcat_count": 0,
        "base_liftable_mismatch_count": 0,
    }
    stream = hashlib.sha256()
    stream.update(f"TASK018-F{prime}-C4-ENUMERATION-v1\n".encode())
    examples: dict[str, Any] = {}
    for q1, q2, q3, left, prefix_mask in triples:
        for q4 in range(len(domain)):
            for target in range(len(domain)):
                indices = (q1, q2, q3, q4, target)
                right = right_forms[(q4, target)]
                resultant = fixed_resultant(left, right, 4, 2, prime)
                recursive_zero = resultant == 0
                ratcat = bool(prefix_mask & root_masks[(q4, target)])
                base_liftable = all(liftable[index] for index in indices)
                counts["tuple_count"] += 1
                counts["recursive_zero_count"] += int(recursive_zero)
                counts["ratcat_count"] += int(ratcat)
                counts["recursive_zero_without_ratcat_count"] += int(
                    recursive_zero and not ratcat
                )
                counts["ratcat_without_recursive_zero_count"] += int(
                    ratcat and not recursive_zero
                )
                counts["base_liftable_tuple_count"] += int(base_liftable)
                counts["base_liftable_recursive_zero_count"] += int(
                    base_liftable and recursive_zero
                )
                counts["base_liftable_ratcat_count"] += int(
                    base_liftable and ratcat
                )
                counts["base_liftable_mismatch_count"] += int(
                    base_liftable and recursive_zero != ratcat
                )
                stream.update(
                    bytes(
                        [
                            q1,
                            q2,
                            q3,
                            q4,
                            target,
                            resultant,
                            int(ratcat),
                            int(base_liftable),
                        ]
                    )
                )
                if recursive_zero and ratcat:
                    key = (
                        "base_liftable_zero"
                        if base_liftable
                        else "ratcat_zero"
                    )
                    if key not in examples:
                        witness = tree_witness(indices, domain, roots)
                        if witness is None:
                            raise AssertionError("RatCat witness disappeared")
                        w2, w3 = witness
                        examples[key] = {
                            "external": tuple_record(
                                indices, domain, prime
                            ),
                            "witness": {
                                "W2": projective_record(domain[w2]),
                                "W3": projective_record(domain[w3]),
                            },
                            "fixed_resultant_mod_p": resultant,
                        }
                if (
                    recursive_zero
                    and not ratcat
                    and "recursive_zero_without_Fp_tree" not in examples
                ):
                    examples["recursive_zero_without_Fp_tree"] = {
                        "external": tuple_record(indices, domain, prime),
                        "fixed_resultant_mod_p": resultant,
                        "Fp_tree_witness_count": 0,
                    }
    for key, value in expected.items():
        if counts[key] != value:
            raise AssertionError(
                f"F{prime} exhaustive count {key} changed: "
                f"{counts[key]} != {value}"
            )
    if "base_liftable_zero" not in examples:
        raise AssertionError(
            f"F{prime} base-liftable example is missing"
        )
    if "recursive_zero_without_Fp_tree" not in examples:
        raise AssertionError(
            f"F{prime} recursive-zero-without-Fp-tree example is missing"
        )
    liftable_coordinate_count = sum(liftable)
    if (
        counts["base_liftable_tuple_count"]
        != liftable_coordinate_count**5
    ):
        raise AssertionError(
            f"F{prime} base-liftable tuple count is inconsistent"
        )
    return {
        "field": f"F{prime}",
        "curve": "nonsingular y^2=x^3+7",
        "projective_coordinate_count": len(domain),
        "projective_representatives_order": (
            f"[0:1],...,[{prime - 1}:1],[1:0]"
        ),
        "external_arity": 5,
        "recursive_form": "C4(Q1,Q2,Q3,Q4;QT)=S5",
        "formal_top_resultant_degrees": [4, 2],
        "enumeration": f"all ordered P1(F{prime})^5 tuples",
        "base_liftable_coordinate_count": liftable_coordinate_count,
        "base_liftable_coordinate_indices": [
            index for index, value in enumerate(liftable) if value
        ],
        "counts": counts,
        "classification": {
            "fixed_recursive_resultant_zero_count": (
                counts["recursive_zero_count"]
            ),
            "RatCat_Fp_count": counts["ratcat_count"],
            "recursive_zero_without_Fp_tree_count": (
                counts["recursive_zero_without_ratcat_count"]
            ),
            "all_external_base_liftable_zero_count": (
                counts["base_liftable_recursive_zero_count"]
            ),
            "all_external_base_liftable_Rec_vs_Rat_mismatch": (
                counts["base_liftable_mismatch_count"]
            ),
        },
        "enumeration_stream_sha256": stream.hexdigest(),
        "named_examples": examples,
        "status": "exact_exhaustive",
    }


def build_artifact() -> dict[str, Any]:
    dependencies = [
        dependency_record(TASK017_ARTIFACT, TASK017_SHA256),
        dependency_record(TASK016_ARTIFACT, TASK016_SHA256),
        dependency_record(
            PRIMARY_CLAIM_EXTRACT, PRIMARY_CLAIM_EXTRACT_SHA256
        ),
    ]
    source_paths = [
        "Ecdlp/Proved/SemaevThree.lean",
        "Ecdlp/Proved/SemaevFour.lean",
        "repo/ECDLP_TYPED_EVIDENCE_V0.json",
        "tasks/ECDLP_RESEARCH.md",
    ]
    missing_sources = [
        path for path in source_paths if not (REPO_ROOT / path).is_file()
    ]
    if missing_sources:
        raise FileNotFoundError(", ".join(missing_sources))
    schedule = recursion_schedule()
    infinity = f5_infinity_fixture()
    extension = f5_f25_fixture()
    exhaustive_small_fields = {
        "F5": exhaustive_s5_fixture(
            5,
            {
                "tuple_count": 7_776,
                "recursive_zero_count": 1_648,
                "ratcat_count": 1_072,
                "recursive_zero_without_ratcat_count": 576,
                "ratcat_without_recursive_zero_count": 0,
                "base_liftable_recursive_zero_count": 432,
                "base_liftable_ratcat_count": 432,
                "base_liftable_mismatch_count": 0,
            },
        ),
        "F11": exhaustive_s5_fixture(
            11,
            {
                "tuple_count": 248_832,
                "recursive_zero_count": 23_328,
                "ratcat_count": 15_352,
                "recursive_zero_without_ratcat_count": 7_976,
                "ratcat_without_recursive_zero_count": 0,
                "base_liftable_recursive_zero_count": 6_442,
                "base_liftable_ratcat_count": 6_442,
                "base_liftable_mismatch_count": 0,
            },
        ),
        "F13": exhaustive_s5_fixture(
            13,
            {
                "tuple_count": 537_824,
                "recursive_zero_count": 87_507,
                "ratcat_count": 81_147,
                "recursive_zero_without_ratcat_count": 6_360,
                "ratcat_without_recursive_zero_count": 0,
                "base_liftable_recursive_zero_count": 766,
                "base_liftable_ratcat_count": 766,
                "base_liftable_mismatch_count": 0,
            },
        ),
    }
    finite_boundary = exhaustive_small_fields["F13"]
    final_degree = schedule[-1]["output_projective_degree"]
    full_affine_capacity = 17 * final_degree
    fixed_target_leaf_capacity = 16 * final_degree
    if full_affine_capacity != 557_056:
        raise AssertionError("full affine degree capacity changed")
    if fixed_target_leaf_capacity != 524_288:
        raise AssertionError("fixed-target leaf subtotal changed")
    return {
        "artifact_id": ARTIFACT_ID,
        "schema_version": SCHEMA_VERSION,
        "kind": (
            "deterministic_nonexperimental_recursive_projective_"
            "definition_and_boundary_certificate"
        ),
        "scope": {
            "task": "TASK-018",
            "cell": "CELL-M-PKC-SMOOTH-M16",
            "barrier": "B-PKC-M16-COMPLETE-COST-BRIDGE",
            "cost_quantity": "CQ-SEMAEV-S17-SYSTEM-COST",
            "included": [
                "fixed-degree projective recursion C2 through C16",
                "degree and Sylvester determinant conventions",
                "recorded algebraic GeoCat-to-RecS17 argument, bounded "
                "C4=S5 replay, and universal forward/reverse proof "
                "obligations",
                "RatCat and Recover boundary separation",
                "F5/F25 explicit fixtures and exhaustive F5/F11/F13 "
                "C4=S5 replays",
            ],
            "excluded": [
                "expanded or evaluated S17",
                "materialized M16 polynomial system",
                "scheme equality, radicality, or multiplicity preservation",
                "Sage, msolve, F4, Groebner, or any solver run",
                "exact-target relation search or discrete-log computation",
                "degree of regularity, fill-in, rank, yield, memory, or cost",
                "experiment authorization, hypothesis retention, or promotion",
            ],
        },
        "depends_on": dependencies,
        "frozen_definition": {
            "name": "RecS17=C16(Q1,...,Q16;QT)",
            "curve_domain": {
                "curve": "E:y^2=x^3+7",
                "field": "any field k with char(k) not in {2,3,7}",
                "algebraic_closure": "kbar",
                "discriminant": "-16*27*7^2",
                "excluded_characteristics": list(
                    EXCLUDED_CHARACTERISTICS
                ),
            },
            "coordinate_order": [
                *[f"Q{index}=[X{index}:Z{index}]" for index in range(1, 17)],
                "QT=[XT:ZT]",
            ],
            "valid_projective_domain": (
                "every external and internal coordinate pair differs "
                "from [0:0]"
            ),
            "kummer_coordinate": {
                "identity": "kappa(O)=[1:0]",
                "affine_point": "kappa((x,y))=[x:1]",
            },
            "H_name": "H=S3h",
            "H_multidegree": [2, 2, 2],
            "H_polynomial": (
                "X1^2*X2^2*Z3^2 + X1^2*Z2^2*X3^2 + "
                "Z1^2*X2^2*X3^2 - 2*X1^2*X2*Z2*X3*Z3 - "
                "2*X1*Z1*X2^2*X3*Z3 - "
                "2*X1*Z1*X2*Z2*X3^2 - "
                "28*(X1*Z1*Z2^2*Z3^2 + "
                "Z1^2*X2*Z2*Z3^2 + Z1^2*Z2^2*X3*Z3)"
            ),
            "base_case": "C2(Q1,Q2;Y)=H(Q1,Q2,Y)",
            "recursive_case": (
                "for 3<=r<=16, C_r(Q1,...,Qr;Y)="
                "hRes_T^(2^(r-2),2)("
                "C_(r-1)(Q1,...,Q_(r-1);T),H(T,Qr,Y))"
            ),
            "elimination_order": [
                f"C{r - 1} and H eliminate T to construct C{r}"
                for r in range(3, 17)
            ],
            "final_predicate": (
                "RecS17_k(Q1,...,Q16,QT) iff "
                "C16(Q1,...,Q16;QT)=0 in k"
            ),
            "literal_materialization": {
                "C16_expanded": False,
                "C16_evaluated": False,
                "M16_system_materialized": False,
                "definition_is_recursive_dag_only": True,
            },
            "irrelevant_ideal_exclusion": {
                "external_pair_ideals": [
                    *[
                        f"<X{index},Z{index}>"
                        for index in range(1, 17)
                    ],
                    "<XT,ZT>",
                ],
                "tree_internal_pair_ideals": [
                    f"<U{index},V{index}>"
                    for index in range(2, 16)
                ],
                "excluded_locus": (
                    "the union where any listed coordinate pair is [0:0]"
                ),
                "only_allowed_set_theoretic_saturation": (
                    "the product of the 31 coordinate-pair irrelevant ideals"
                ),
                "forbidden_extra_saturands": [
                    "coordinate differences",
                    "tangent loci",
                    "duplicate loci",
                    "identity or two-torsion loci",
                ],
            },
        },
        "degree_schedule": {
            "formula": "d_r=2^(r-1), where d_r is the degree of C_r in each of its r+1 projective coordinate pairs",
            "rows": schedule,
            "rows_sha256": digest(schedule),
            "C16_external_coordinate_pair_count": 17,
            "C16_multidegree_each_external_pair": final_degree,
            "C16_multidegree_vector": [final_degree] * 17,
            "C16_final_resultant_formal_degrees": [16_384, 2],
            "C16_final_sylvester_size": 16_386,
            "full_17_coordinate_affine_total_degree_capacity": (
                full_affine_capacity
            ),
            "fixed_target_16_leaf_affine_degree_capacity_subtotal": (
                fixed_target_leaf_capacity
            ),
            "capacity_warning": (
                "557056 and 524288 are multidegree-box capacity sums, "
                "not the actual total degree, solving degree, degree of "
                "regularity, matrix size, rank, memory, or work estimate"
            ),
        },
        "coefficient_and_sylvester_convention": {
            "binary_form_coefficients": (
                "F(U,V)=sum_(i=0)^m f_i*U^(m-i)*V^i is stored "
                "as [f_0,...,f_m], descending U degree"
            ),
            "dehomogenization_chart": (
                "F(t,1)=sum f_i*t^(m-i), while the declared formal "
                "degree m and leading zero coefficients are retained"
            ),
            "sylvester_rows": (
                "for formal degrees (m,n), rows 0..n-1 are n shifted "
                "copies of [f_0,...,f_m]; rows n..n+m-1 are m shifted "
                "copies of [g_0,...,g_n]"
            ),
            "hRes_definition": "hRes_T^(m,n)(F,G)=det(Syl_(m,n)(F(t,1),G(t,1)))",
            "matrix_column_order": (
                "descending monomial slots of total Sylvester width m+n"
            ),
            "determinant_sign": "ordinary Leibniz determinant; row order above is literal",
            "swap_rule": "hRes^(m,n)(F,G)=(-1)^(m*n)*hRes^(n,m)(G,F)",
            "formal_degree_reduction": "forbidden",
            "primitive_part_or_content_division": "forbidden",
            "monic_normalization": "forbidden",
            "literal_coefficient_unit": 1,
            "literal_unit_scope": (
                "coefficient unit 1 applies only when argument order, "
                "binary coefficient order, formal degrees, Sylvester row "
                "order, and determinant convention are exactly the frozen "
                "ones"
            ),
            "projective_rescaling_rule": (
                "rescaling any valid projective coordinate representative "
                "multiplies C_r by the corresponding nonzero field scalar "
                "raised to its declared degree d_r; for C16 each of the 17 "
                "representative scalars occurs to exponent 32768"
            ),
            "unit_convention": (
                "the recursive polynomial is the literal determinant with "
                "coefficient unit 1 under the frozen convention; projective "
                "coordinate rescaling may multiply its value by the "
                "declared nonzero field unit, while no variable-dependent "
                "factor may be discarded"
            ),
            "infinity_rule": (
                "[1:0] is a common root exactly when the two retained "
                "formal leading coefficients vanish; fixed-degree "
                "resultants therefore keep this valid stratum"
            ),
        },
        "fixtures": {
            "F5_fixed_vs_reduced_infinity": infinity,
            "F5_F25_extension_only_nonlift": extension,
            "bounded_exhaustive_S5": exhaustive_small_fields,
            "F13_boundary_and_base_lift": finite_boundary,
        },
        "predicate_boundaries": {
            "RecS17_k": {
                "external_coordinates": "P1(k)^17",
                "internal_coordinates": "none in the predicate",
                "definition": "the frozen C16 determinant DAG evaluates to zero",
            },
            "GeoCat_kbar": {
                "external_coordinates": "P1(k)^17",
                "internal_coordinates": "W2,...,W15 in P1(kbar)",
                "definition": (
                    "all fifteen H vertices of the TASK-017 caterpillar vanish"
                ),
            },
            "RatCat_Fp": {
                "external_coordinates": "P1(Fp)^17",
                "internal_coordinates": "W2,...,W15 in P1(Fp)",
                "definition": "the same homogeneous caterpillar over Fp",
            },
            "Recover_Fp": {
                "inputs": (
                    "base-field leaf lifts, a full target point, supplied "
                    "valid projective internals, and exact backpointers"
                ),
                "definition": (
                    "exact point-DP recovery ending at R or -R; it is not "
                    "defined by resultant vanishing alone"
                ),
            },
            "algebraic_closure_projection_contract": {
                "field_and_domain": (
                    "for E/k nonsingular with char(k) not in {2,3,7}, "
                    "all external pairs valid, and internals in P1(kbar)"
                ),
                "projection_map": (
                    "forget W2,...,W15 from a GeoCat_kbar witness"
                ),
                "forward": (
                    "recorded algebraic argument: GeoCat_kbar should imply "
                    "RecS17_k after embedding k into kbar by common-root "
                    "vanishing at every fixed-degree resultant step; this "
                    "producer replays only bounded C4=S5 instances and does "
                    "not computationally or kernel prove generic C16 "
                    "symbolic specialization"
                ),
                "reverse": (
                    "unproved target: RecS17_k would imply GeoCat_kbar by "
                    "repeated fixed-degree projective common-root reversal "
                    "from C16 through C2, once specialization of every "
                    "symbolic resultant at finite points and [1:0] is proved"
                ),
                "inverse_witness": (
                    "target witness: one valid P1(kbar) common root at each "
                    "reverse step; no universal witness construction is "
                    "established by this producer"
                ),
                "forward_status": (
                    "algebraic_argument_recorded_bounded_replay"
                ),
                "reverse_status": "unproved_target",
                "equivalence": "not_established_universally",
                "claim_level": (
                    "contract_frozen_algebraic_argument_recorded_"
                    "bounded_replay_universal_forward_reverse_unproved"
                ),
                "missing_lemma": (
                    "specialization compatibility of fixed-degree symbolic "
                    "resultants, including the output point [1:0]"
                ),
            },
            "base_field_relations": {
                "algebraic_arguments_recorded_not_generic_C16_proofs": [
                    "RatCat_Fp should imply RecS17_Fp by fixed-resultant common-root vanishing",
                    "Recover_Fp implies RatCat_Fp on its supplied valid tree by definition",
                    "TASK-017 records RatCat_Fp signed-point semantics on its stated supplied/liftable domain",
                ],
                "bounded_replay": [
                    "C4=S5 RatCat_Fp implies recursive-resultant zero for every tuple over F5, F11, and F13",
                    "all externally base-liftable recursive zeros have an Fp tree in those three bounded replays",
                ],
                "not_established_universally": [
                    "RecS17_Fp implies GeoCat_kbar",
                    "RecS17_Fp implies RatCat_Fp",
                    "RecS17_Fp implies Recover_Fp",
                ],
                "combined_nonlift_boundary_fixture": (
                    "fixtures.F5_F25_extension_only_nonlift; it is "
                    "classified EXTERNAL_NONLIFT and is not an all-externals-"
                    "liftable counterexample"
                ),
                "liftability_localization_target": (
                    "after the universal reverse and specialization lemma "
                    "are proved, all external E(Fp)-liftability is the target "
                    "domain for RecS17_Fp iff RatCat_Fp; the current "
                    "certificate establishes this only in bounded S5 replays"
                ),
                "bounded_exhaustive_check": (
                    "the p=5,11,13 C4=S5 replays have respectively "
                    "432, 6442, and 766 base-liftable recursive zeros "
                    "and zero Rec/Rat mismatches in all three fields"
                ),
            },
            "strata": {
                "identity_or_infinity": "retain",
                "tangent_or_repeated_input": "retain",
                "rational_two_torsion": "retain",
                "duplicate_coordinates_or_roots": "retain",
                "extension_only_internal_roots": (
                    "retain for GeoCat_kbar; reject for RatCat_Fp"
                ),
                "external_nonlift": (
                    "valid projective input for Rec/Geo; reject Recover_Fp"
                ),
                "invalid_projective_pair_0_0": "exclude",
            },
        },
        "terminal_disposition": {
            "scientific_disposition": "scoped_blocker",
            "completed_scope": (
                "one fixed recursive projective S17 definition, complete "
                "degree and determinant conventions, a recorded algebraic "
                "GeoCat-to-Rec argument, and bounded C4=S5 projective, "
                "nonlift, and no-Fp-tree replays"
            ),
            "remaining_blocker": (
                "neither the generic C16 forward specialization nor the "
                "universal reverse RecS17-to-GeoCat induction is "
                "computationally or kernel proved; symbolic fixed-resultant "
                "specialization, especially at [1:0], is missing, so "
                "Rec-to-Rat/Recover and solving cost remain unestablished"
            ),
            "next_mathematical_step": (
                "prove the fixed-degree P1 resultant common-root lemma and "
                "the symbolic-resultant specialization law at finite points "
                "and [1:0], kernel-check the generic forward implication, "
                "then run the reverse C16-to-C2 induction"
            ),
            "retention_disposition": "zero_retention_success",
            "assurance": "certificate_replayed",
            "source_independence": "not_established",
            "calibration": "excluded_nonexperimental",
            "cell_status": "open_non_executable",
            "barrier_effect": "narrowed_open",
            "cost_quantity_status": "partial",
            "solving_cost_status": "unpriced",
            "rank_status": "unpriced",
            "yield_status": "unpriced",
            "authorization": "none",
            "experiment_permission": "none",
            "route_effect": "none",
            "hypothesis_effect": "none",
        },
        "unresolved_fields": [
            "kernel-checked fixed-degree projective resultant theorem",
            "symbolic-resultant specialization at finite points and [1:0]",
            "generic C16 GeoCat-to-RecS17 forward kernel proof",
            "universal reverse RecS17-to-GeoCat induction",
            "unconditional base-field rational-root projection",
            "recovery without explicit lift and supplied-coordinate hypotheses",
            "scheme equality, radicality, or multiplicity preservation",
            "degree of regularity, fill-in, rank, yield, memory, and total work",
        ],
        "producer_checks": {
            "dependency_digests_bound": True,
            "all_source_paths_exist": True,
            "schedule_rows_replayed": len(schedule),
            "C16_multidegree_checked": final_degree,
            "C16_expanded": False,
            "C16_evaluated": False,
            "generic_C16_forward_computationally_replayed": False,
            "generic_C16_forward_kernel_checked": False,
            "bounded_C4_S5_forward_replayed": True,
            "highest_materialized_recursive_form": "C3=S4 in small fixtures",
            "highest_evaluated_recursive_form": "C4=S5 in small fixtures",
            "F5_fixed_resultant": infinity["fixed_resultant_mod_5"],
            "F5_reduced_affine_resultant": (
                infinity["reduced_affine_resultant_mod_5"]
            ),
            "F25_common_root_count": len(
                extension["common_roots_in_F25"]
            ),
            "F13_tuples_replayed": finite_boundary["counts"][
                "tuple_count"
            ],
            "bounded_S5_fields_replayed": [5, 11, 13],
            "bounded_S5_total_tuples_replayed": sum(
                fixture["counts"]["tuple_count"]
                for fixture in exhaustive_small_fields.values()
            ),
            "F13_recursive_zero_without_Fp_tree_count": finite_boundary[
                "counts"
            ][
                "recursive_zero_without_ratcat_count"
            ],
            "F13_base_lift_mismatch_count": finite_boundary["counts"][
                "base_liftable_mismatch_count"
            ],
            "S17_materialized": False,
            "solver_executed": False,
            "experiment_authorized": False,
        },
    }


def write_artifact(artifact: dict[str, Any]) -> str:
    payload = canonical_bytes(artifact)
    artifact_sha = hashlib.sha256(payload).hexdigest()
    ARTIFACT_PATH.write_bytes(payload)
    HASH_PATH.write_text(
        f"{artifact_sha}  artifact.json\n", encoding="utf-8"
    )
    return artifact_sha


def check_artifact(artifact: dict[str, Any]) -> str:
    expected_payload = canonical_bytes(artifact)
    if not ARTIFACT_PATH.exists() or not HASH_PATH.exists():
        raise FileNotFoundError("artifact.json or artifact.sha256 is missing")
    actual_payload = ARTIFACT_PATH.read_bytes()
    if actual_payload != expected_payload:
        raise AssertionError("artifact.json is not at the producer fixpoint")
    actual_sha = hashlib.sha256(actual_payload).hexdigest()
    expected_hash_line = f"{actual_sha}  artifact.json\n"
    if HASH_PATH.read_text(encoding="utf-8") != expected_hash_line:
        raise AssertionError("artifact.sha256 is stale")
    return actual_sha


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that committed outputs equal a fresh deterministic build",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artifact = build_artifact()
    artifact_sha = (
        check_artifact(artifact) if args.check else write_artifact(artifact)
    )
    action = "checked" if args.check else "wrote"
    print(f"{action} {ARTIFACT_PATH}")
    print(f"sha256 {artifact_sha}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
