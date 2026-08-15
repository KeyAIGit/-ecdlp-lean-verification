#!/usr/bin/env python3
"""Exact replay for UORC-056 C33 oriented addition carry cocycle.

This package studies the exact obstruction encountered when one tries to lift
ordinary elliptic-curve addition into an addition law for the marked oriented
root

    Y_G(x([k]G)) / y([k]G) = (-1)^k.

Only frozen public toy curves, public prime orders and public secp256k1
constants are used. The evaluator code never accepts an external unknown-scalar
point, wallet, key or production target.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Iterable, Optional

Point = Optional[tuple[int, int]]

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def add(self, left: Point, right: Point) -> Point:
        p = self.p
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if left == right:
            if y1 % p == 0:
                return None
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (slope * slope - x1 - x2) % p
        y3 = (slope * (x1 - x3) - y1) % p
        return x3, y3

    def neg(self, point: Point) -> Point:
        if point is None:
            return None
        return point[0], (-point[1]) % self.p

    def mul(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        out: Point = None
        addend = point
        value = scalar
        while value:
            if value & 1:
                out = self.add(out, addend)
            addend = self.add(addend, addend)
            value >>= 1
        return out


@dataclass(frozen=True)
class Instance:
    name: str
    curve: Curve
    n: int
    G: tuple[int, int]


INSTANCES = (
    Instance("E7-P43-N31", Curve(43, 0, 7), 31, (2, 12)),
    Instance("E7-P67-N79", Curve(67, 0, 7), 79, (2, 22)),
    Instance("E7-P79-N67", Curve(79, 0, 7), 67, (1, 18)),
    Instance("E7-P127-N127", Curve(127, 0, 7), 127, (1, 32)),
    Instance("E7-P163-N139", Curve(163, 0, 7), 139, (2, 34)),
)

DIAGNOSTIC_ORDERS = (3, 5, 7, 11, 13, 17, 19, 31)
GAUGE_ENUMERATION_ORDERS = (3, 5, 7, 11, 13)
TRIPLE_EXHAUSTIVE_ORDERS = (3, 5, 7, 11, 13, 17, 19, 31)


def canonical(value: int, order: int) -> int:
    return value % order


def sigma(value: int, order: int) -> int:
    """Canonical parity sign on representatives 0,...,order-1."""
    return 1 if canonical(value, order) % 2 == 0 else -1


def carry(value_left: int, value_right: int, order: int) -> int:
    """The canonical one-wrap carry sign for two canonical residues."""
    left = canonical(value_left, order)
    right = canonical(value_right, order)
    return 1 if left + right < order else -1


def carry_from_sigma(value_left: int, value_right: int, order: int) -> int:
    return (
        sigma(value_left, order)
        * sigma(value_right, order)
        * sigma(value_left + value_right, order)
    )


def carry_matrix(order: int, nonzero_only: bool = False) -> list[list[int]]:
    indices = range(1, order) if nonzero_only else range(order)
    return [[carry(a, b, order) for b in indices] for a in indices]


def bareiss_det(matrix: list[list[int]]) -> int:
    """Fraction-free exact determinant, sufficient for the small replay."""
    size = len(matrix)
    if size == 0:
        return 1
    work = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for pivot_index in range(size - 1):
        if work[pivot_index][pivot_index] == 0:
            swap = next(
                (row for row in range(pivot_index + 1, size)
                 if work[row][pivot_index] != 0),
                None,
            )
            if swap is None:
                return 0
            work[pivot_index], work[swap] = work[swap], work[pivot_index]
            sign = -sign
        pivot = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, size):
            for col in range(pivot_index + 1, size):
                numerator = (
                    work[row][col] * pivot
                    - work[row][pivot_index] * work[pivot_index][col]
                )
                work[row][col] = numerator // previous
        previous = pivot
        for row in range(pivot_index + 1, size):
            work[row][pivot_index] = 0
        for col in range(pivot_index + 1, size):
            work[pivot_index][col] = work[pivot_index][col]
    return sign * work[-1][-1]


def matrix_rank_mod(matrix: list[list[int]], modulus: int) -> int:
    work = [[entry % modulus for entry in row] for row in matrix]
    row_count = len(work)
    col_count = len(work[0]) if row_count else 0
    rank = 0
    for col in range(col_count):
        pivot = next(
            (row for row in range(rank, row_count) if work[row][col]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][col], -1, modulus)
        work[rank] = [(value * inverse) % modulus for value in work[rank]]
        for row in range(row_count):
            if row == rank or work[row][col] == 0:
                continue
            factor = work[row][col]
            work[row] = [
                (left - factor * right) % modulus
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == row_count:
            break
    return rank


def expected_full_determinant(order: int) -> int:
    sign = -1 if (order * (order - 1) // 2) % 2 else 1
    return sign * (2 ** (order - 1))


def expected_nonzero_determinant(order: int) -> int:
    # Row differences reduce the matrix to an anti-diagonal of n-2 entries -2.
    width = order - 2
    anti_sign = -1 if (width * (width - 1) // 2) % 2 else 1
    return ((-2) ** width) * anti_sign


def all_sign_gauges(order: int) -> list[tuple[int, ...]]:
    """Enumerate normalized +/-1 gauges h with delta h equal to carry."""
    solutions: list[tuple[int, ...]] = []
    for tail in product((-1, 1), repeat=order - 1):
        gauge = (1,) + tail
        valid = True
        for left in range(order):
            for right in range(order):
                target = carry(left, right, order)
                observed = (
                    gauge[left]
                    * gauge[right]
                    * gauge[(left + right) % order]
                )
                if observed != target:
                    valid = False
                    break
            if not valid:
                break
        if valid:
            solutions.append(gauge)
    return solutions


def selected_product_matches_parity(order: int, selected: Iterable[int]) -> bool:
    selected_set = tuple(selected)
    for value in range(order):
        out = 1
        for jump in selected_set:
            out *= carry(value, jump, order)
        if out != sigma(value, order):
            return False
    return True


def parity_linear_coefficients(order: int) -> list[int]:
    # The unique exact expansion sigma(a)=sum_b sigma(b) carry(a,b).
    return [sigma(jump, order) for jump in range(order)]


def point_table(instance: Instance) -> list[Point]:
    table = [instance.curve.mul(k, instance.G) for k in range(instance.n)]
    if table[0] is not None or any(point is None for point in table[1:]):
        raise AssertionError(f"invalid frozen subgroup table: {instance.name}")
    if instance.curve.mul(instance.n, instance.G) is not None:
        raise AssertionError(f"generator order mismatch: {instance.name}")
    return table


def cyclic_scalar_checks(order: int) -> dict[str, int | bool]:
    pair_checks = 0
    reconstruction_checks = 0
    diagonal_checks = 0
    halving_checks = 0
    negation_covariance_checks = 0
    opposite_checks = 0
    cocycle_checks = 0

    inverse_two = pow(2, -1, order)
    negative_half = (order - 1) // 2

    for left in range(order):
        for right in range(order):
            direct = carry(left, right, order)
            if direct != carry_from_sigma(left, right, order):
                raise AssertionError("carry/sigma identity failed")
            pair_checks += 1

            reconstructed = direct * sigma(left, order) * sigma(right, order)
            if reconstructed != sigma(left + right, order):
                raise AssertionError("oriented reconstruction failed")
            reconstruction_checks += 1

            result = (left + right) % order
            negated = carry(-left, -right, order)
            if left and right and result:
                if negated != -direct:
                    raise AssertionError("generic generator-negation covariance failed")
            elif left and right and result == 0:
                if direct != -1 or negated != direct:
                    raise AssertionError("opposite-pair covariance failed")
                opposite_checks += 1
            negation_covariance_checks += 1

    for value in range(order):
        half = inverse_two * value % order
        if carry(half, half, order) != sigma(value, order):
            raise AssertionError("public-halving reduction failed")
        halving_checks += 1

        if value != 0:
            negative_half_value = negative_half * value % order
            if carry(negative_half_value, negative_half_value, order) != -sigma(value, order):
                raise AssertionError("negative-half terminal-chain identity failed")
            diagonal_checks += 1

    if order in TRIPLE_EXHAUSTIVE_ORDERS:
        for left in range(order):
            for middle in range(order):
                for right in range(order):
                    first = (
                        carry(left, middle, order)
                        * carry(left + middle, right, order)
                    )
                    second = (
                        carry(middle, right, order)
                        * carry(left, middle + right, order)
                    )
                    if first != second:
                        raise AssertionError("carry 2-cocycle identity failed")
                    cocycle_checks += 1

    return {
        "order": order,
        "pair_checks": pair_checks,
        "reconstruction_checks": reconstruction_checks,
        "diagonal_checks": diagonal_checks,
        "halving_checks": halving_checks,
        "generator_negation_covariance_checks": negation_covariance_checks,
        "opposite_pair_checks": opposite_checks,
        "cocycle_checks": cocycle_checks,
    }


def matrix_diagnostics(order: int, modulus: int | None = None) -> dict[str, int | bool]:
    full = carry_matrix(order)
    nonzero = carry_matrix(order, nonzero_only=True)
    expected_full = expected_full_determinant(order)
    expected_nonzero = expected_nonzero_determinant(order)

    exact_full = bareiss_det(full) if order <= 31 else None
    exact_nonzero = bareiss_det(nonzero) if order <= 31 else None
    if exact_full is not None and exact_full != expected_full:
        raise AssertionError("full carry determinant formula failed")
    if exact_nonzero is not None and exact_nonzero != expected_nonzero:
        raise AssertionError("nonzero carry determinant formula failed")

    rank_full = matrix_rank_mod(full, modulus) if modulus is not None else order
    rank_nonzero = matrix_rank_mod(nonzero, modulus) if modulus is not None else order - 1
    if modulus is not None:
        if rank_full != order:
            raise AssertionError("full carry matrix lost rank in odd characteristic")
        if rank_nonzero != order - 1:
            raise AssertionError("nonzero carry matrix lost rank in odd characteristic")

    coefficients = parity_linear_coefficients(order)
    for value in range(order):
        reconstructed = sum(
            coefficients[jump] * carry(value, jump, order)
            for jump in range(order)
        )
        if reconstructed != sigma(value, order):
            raise AssertionError("unique linear carry expansion failed")

    all_jump_product = tuple(range(1, order))
    if not selected_product_matches_parity(order, all_jump_product):
        raise AssertionError("all-jump multiplicative integration failed")

    unique_fixed_jump_product = None
    if order <= 13:
        survivors = []
        jumps = tuple(range(1, order))
        for mask in range(1 << len(jumps)):
            selected = [jumps[index] for index in range(len(jumps)) if (mask >> index) & 1]
            if selected_product_matches_parity(order, selected):
                survivors.append(selected)
        if survivors != [list(jumps)]:
            raise AssertionError("fixed-jump multiplicative minimality failed")
        unique_fixed_jump_product = True

    return {
        "order": order,
        "modulus": modulus,
        "expected_full_determinant": expected_full,
        "expected_nonzero_determinant": expected_nonzero,
        "exact_full_determinant_checked": exact_full is not None,
        "exact_nonzero_determinant_checked": exact_nonzero is not None,
        "full_rank": rank_full,
        "nonzero_rank": rank_nonzero,
        "all_linear_coefficients_nonzero": all(value != 0 for value in coefficients),
        "all_nontrivial_jump_product_is_parity": True,
        "unique_fixed_jump_product_verified": unique_fixed_jump_product,
    }


def frozen_curve_replay(instance: Instance) -> dict[str, int | bool | str]:
    curve = instance.curve
    n = instance.n
    table = point_table(instance)
    inverse_two = pow(2, -1, n)

    marked_generators = 0
    query_halving_checks = 0
    oriented_addition_checks = 0
    scalar_carry_checks = 0
    anchor_checks = 0
    generic_negation_checks = 0

    for marker in range(1, n):
        marked_generators += 1
        marked_point = table[marker]
        if marked_point is None:
            raise AssertionError("marked generator became identity")
        anchor_y = (-marked_point[1]) % curve.p
        expected_anchor = sigma(1, n) * marked_point[1] % curve.p
        if anchor_y != expected_anchor:
            raise AssertionError("public anchor normalization failed")
        anchor_checks += 1

        for query_scalar in range(1, n):
            absolute_query = marker * query_scalar % n
            query = table[absolute_query]
            if query is None:
                raise AssertionError("nonzero query became identity")
            half = curve.mul(inverse_two, query)
            expected_half = table[marker * (inverse_two * query_scalar % n) % n]
            if half != expected_half or curve.add(half, half) != query:
                raise AssertionError("public EC halving failed")
            half_label = inverse_two * query_scalar % n
            if carry(half_label, half_label, n) != sigma(query_scalar, n):
                raise AssertionError("EC halving/carry parity reduction failed")
            query_halving_checks += 1

        # Full pair replay for every marked generator. All point values are
        # looked up from the one public frozen subgroup table.
        for left_scalar in range(1, n):
            left_abs = marker * left_scalar % n
            left = table[left_abs]
            assert left is not None
            left_y = left[1]
            left_oriented = sigma(left_scalar, n) * left_y % curve.p
            for right_scalar in range(1, n):
                right_abs = marker * right_scalar % n
                right = table[right_abs]
                assert right is not None
                result_scalar = (left_scalar + right_scalar) % n
                c = carry(left_scalar, right_scalar, n)
                if c != carry_from_sigma(left_scalar, right_scalar, n):
                    raise AssertionError("frozen scalar carry mismatch")
                scalar_carry_checks += 1

                result = curve.add(left, right)
                expected_result = table[marker * result_scalar % n]
                if result != expected_result:
                    raise AssertionError("frozen point addition mismatch")

                negated_carry = carry(-left_scalar, -right_scalar, n)
                if result_scalar:
                    if negated_carry != -c:
                        raise AssertionError("frozen generic negation covariance failed")
                    generic_negation_checks += 1
                else:
                    if negated_carry != c or c != -1:
                        raise AssertionError("frozen opposite pair carry failed")

                if result is None:
                    continue
                result_y = result[1]
                result_oriented = sigma(result_scalar, n) * result_y % curve.p
                right_y = right[1]
                right_oriented = sigma(right_scalar, n) * right_y % curve.p
                left_side = result_oriented * left_y * right_y % curve.p
                right_side = (
                    c
                    * left_oriented
                    * right_oriented
                    * result_y
                ) % curve.p
                if left_side != right_side:
                    raise AssertionError("denominator-free oriented addition law failed")
                oriented_addition_checks += 1

    matrix = matrix_diagnostics(n, curve.p)
    return {
        "instance": instance.name,
        "p": curve.p,
        "n": n,
        "marked_generators": marked_generators,
        "anchor_checks": anchor_checks,
        "query_halving_checks": query_halving_checks,
        "scalar_carry_checks": scalar_carry_checks,
        "oriented_addition_checks": oriented_addition_checks,
        "generic_generator_negation_checks": generic_negation_checks,
        "carry_matrix_full_rank_mod_p": matrix["full_rank"] == n,
        "carry_matrix_nonzero_rank_mod_p": matrix["nonzero_rank"] == n - 1,
    }


def build_payload() -> dict[str, object]:
    scalar_orders = sorted(set(DIAGNOSTIC_ORDERS) | {instance.n for instance in INSTANCES})
    scalar_replay = [cyclic_scalar_checks(order) for order in scalar_orders]
    matrix_replay = [matrix_diagnostics(order) for order in DIAGNOSTIC_ORDERS]
    frozen_replay = [frozen_curve_replay(instance) for instance in INSTANCES]

    gauge_replay = []
    for order in GAUGE_ENUMERATION_ORDERS:
        solutions = all_sign_gauges(order)
        expected = tuple(sigma(value, order) for value in range(order))
        if solutions != [expected]:
            raise AssertionError("normalized binary carry gauge was not unique")
        gauge_replay.append({
            "order": order,
            "candidate_gauges": 2 ** (order - 1),
            "solutions": len(solutions),
            "unique_solution_is_parity": True,
        })

    half = (SECP_N - 1) // 2
    full_fibre_pole_lower_bound = SECP_N - 1
    payload: dict[str, object] = {
        "profile_id": "UORC-056-ORIENTED-ADDITION-COCYCLE-C33",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "exact_normal_form": {
            "carry_definition": "C_G(P,Q)=sigma_G(P)*sigma_G(Q)*sigma_G(P+Q)",
            "scalar_formula": "C(a,b)=+1 if [a]_n+[b]_n<n, else -1",
            "oriented_addition": "Y(P+Q)*y(P)*y(Q)=C(P,Q)*Y(P)*Y(Q)*y(P+Q)",
            "cocycle": "C(P,Q)C(P+Q,R)=C(Q,R)C(P,Q+R)",
            "public_halving_decoder": "sigma(Q)=C([2^-1]Q,[2^-1]Q)",
            "negative_half_decoder": "sigma(Q)=-C([(n-1)/2]Q,[(n-1)/2]Q)",
        },
        "scalar_replay": scalar_replay,
        "gauge_replay": gauge_replay,
        "matrix_replay": matrix_replay,
        "frozen_curve_replay": frozen_replay,
        "aggregate": {
            "scalar_orders": len(scalar_replay),
            "scalar_pair_checks": sum(int(row["pair_checks"]) for row in scalar_replay),
            "scalar_cocycle_checks": sum(int(row["cocycle_checks"]) for row in scalar_replay),
            "marked_generators": sum(int(row["marked_generators"]) for row in frozen_replay),
            "anchor_checks": sum(int(row["anchor_checks"]) for row in frozen_replay),
            "query_halving_checks": sum(int(row["query_halving_checks"]) for row in frozen_replay),
            "frozen_scalar_carry_checks": sum(int(row["scalar_carry_checks"]) for row in frozen_replay),
            "frozen_oriented_addition_checks": sum(int(row["oriented_addition_checks"]) for row in frozen_replay),
            "binary_gauge_solutions_across_screens": sum(int(row["solutions"]) for row in gauge_replay),
            "all_frozen_carry_matrices_full_rank": all(
                bool(row["carry_matrix_full_rank_mod_p"])
                and bool(row["carry_matrix_nonzero_rank_mod_p"])
                for row in frozen_replay
            ),
            "errors": 0,
        },
        "secp256k1": {
            "p": SECP_P,
            "n": SECP_N,
            "n_is_odd": SECP_N % 2 == 1,
            "inverse_two_mod_n": pow(2, -1, SECP_N),
            "negative_half_multiplier": half,
            "full_carry_matrix_determinant_absolute_value": "2^(n-1)",
            "full_carry_matrix_determinant_bit_length": SECP_N,
            "full_carry_matrix_rank": SECP_N,
            "nonzero_carry_matrix_rank": SECP_N - 1,
            "fixed_jump_product_factors_required": SECP_N - 1,
            "direct_fixed_G_carry_fibre_pole_degree_lower_bound": full_fibre_pole_lower_bound,
            "gcd_n_p_minus_one": __import__("math").gcd(SECP_N, SECP_P - 1),
            "base_field_nontrivial_multiplicative_gauge_character_exists": False,
        },
        "theorems": {
            "binary_carry_gauge_uniqueness": (
                "A normalized +/-1 cochain with coboundary C is sigma itself, "
                "because two trivializations differ by a homomorphism from an "
                "odd cyclic group to +/-1."
            ),
            "base_field_gauge_uniqueness": (
                "Any F_p^*-valued trivialization of the carry differs from sigma "
                "by a character H->F_p^*. For secp256k1 gcd(n,p-1)=1, so the "
                "character is trivial."
            ),
            "extension_field_dichotomy": (
                "Over an extension, every nontrivial character on prime H has "
                "full order n. Removing carry by a multiplicative state therefore "
                "imports a faithful dual phase."
            ),
            "carry_matrix_rank": (
                "The n by n carry matrix has determinant "
                "(-1)^(n(n-1)/2)*2^(n-1), hence full rank in every field of "
                "characteristic different from two."
            ),
            "fixed_jump_product_minimality": (
                "The product of carry fibres over jumps 1,...,n-1 equals parity, "
                "and every one of the n-1 thresholds is necessary."
            ),
            "generator_blind_local_addition_obstruction": (
                "For P,Q,P+Q nonzero, changing G to -G negates C_G(P,Q), while "
                "ordinary addition coordinates and line data are unchanged."
            ),
            "direct_carry_rational_degree": (
                "A rational function F(P,G)=C_G(P,G) regular on H has F-1 zero "
                "at n-1 points and is nonzero, so its pole degree is at least n-1."
            ),
        },
        "decision": {
            "public_oriented_anchor_used": True,
            "exact_lifted_addition_law_found": True,
            "missing_factor_identified_as_carry_cocycle": True,
            "doubling_carry_is_parity_complete": True,
            "binary_carry_free_gauge_found_beyond_parity": False,
            "base_field_multiplicative_carry_free_state_found": False,
            "fixed_jump_linear_subroot_integration_found": False,
            "fixed_jump_multiplicative_subroot_integration_found": False,
            "generator_blind_standard_addition_formula_can_supply_carry": False,
            "dynamic_carry_aggregation_found": False,
            "nonlocal_propagation_law_found": False,
            "numeric_scalar_control_used": False,
            "all_point_public_Q_replay_passed": True,
            "exact_oriented_root_extraction_found": False,
            "exact_parity_extraction_found": False,
            "complete_cost_gate_passed": False,
            "compact_branch_odd_evaluator_found": False,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "scientific_boundary": (
            "C33 closes direct binary lifted-addition states, carry-free scalar "
            "gauges, generator-blind standard addition leaves, fixed separated "
            "linear carry dictionaries and fixed-jump carry monomials. It does "
            "not close a richer field-valued nonautonomous circuit that aggregates "
            "dynamic carry factors implicitly."
        ),
        "next_frontier": "DYNAMIC-ORIENTED-CARRY-AGGREGATION-C34",
    }
    body = dict(payload)
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    payload["digest"] = digest
    return payload


def write_or_check(path: Path, payload: dict[str, object], check: bool) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != rendered:
            raise SystemExit("C33 oriented-addition artifact drift")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    write_or_check(args.out, payload, args.check)
    aggregate = payload["aggregate"]
    print("UORC056_ORIENTED_ADDITION_COCYCLE_C33_OK")
    print(json.dumps(aggregate, indent=2, sort_keys=True))
    print(f"digest={payload['digest']}")


if __name__ == "__main__":
    main()
