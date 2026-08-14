#!/usr/bin/env python3
"""Exact frozen replay for UORC056 Hilbert-90 displacement boundary B16.

No external curve, point, key, wallet, unknown scalar, or production-sized DLP
input is accepted. Production constants are used only for public cost counts.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from uorc056_hilbert90_integration_core import (
    COSET_CASES,
    affine_point_count,
    construct_factor,
    factor_value,
)
from uorc056_oriented_principal_pell_core import (
    SECP_N,
    Point,
    ec_add,
    nullspace_mod,
    trim,
)


def inv(value: int, modulus: int) -> int:
    return pow(value % modulus, -1, modulus)


def all_curve_points(p: int) -> list[Point]:
    points: list[Point] = [None]
    for x in range(p):
        rhs = (x**3 + 7) % p
        for y in range(p):
            if y * y % p == rhs:
                points.append((x, y))
    return points


def poly_mul(left: list[int], right: list[int], p: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            result[i + j] = (result[i + j] + left_value * right_value) % p
    return trim(result, p)


def orbit_polynomial(values: list[int], p: int) -> list[int]:
    polynomial = [1]
    for value in values:
        polynomial = poly_mul(polynomial, [(-value) % p, 1], p)
    return polynomial


def berlekamp_massey(sequence: list[int], p: int) -> int:
    connection = [1]
    previous = [1]
    length = 0
    shift = 1
    discrepancy_scale = 1

    for index in range(len(sequence)):
        discrepancy = sequence[index] % p
        for offset in range(1, length + 1):
            discrepancy = (
                discrepancy + connection[offset] * sequence[index - offset]
            ) % p
        if discrepancy == 0:
            shift += 1
            continue

        coefficient = discrepancy * inv(discrepancy_scale, p) % p
        old_connection = connection[:]
        needed = len(previous) + shift
        if len(connection) < needed:
            connection.extend([0] * (needed - len(connection)))
        for offset, value in enumerate(previous):
            connection[offset + shift] = (
                connection[offset + shift] - coefficient * value
            ) % p

        if 2 * length <= index:
            length = index + 1 - length
            previous = old_connection
            discrepancy_scale = discrepancy
            shift = 1
        else:
            shift += 1

    return length


def proportional(left: list[int], right: list[int], p: int) -> bool:
    if len(left) != len(right):
        return False
    pivot = next((index for index, value in enumerate(left) if value % p), None)
    if pivot is None or right[pivot] % p == 0:
        return False
    scale = right[pivot] * inv(left[pivot], p) % p
    return all(scale * a % p == b % p for a, b in zip(left, right, strict=True))


def build_case(
    p: int,
    order: int,
    generator: tuple[int, int],
    _selected_coset: tuple[int, int],
    group_order: int,
) -> dict[str, object]:
    if affine_point_count(p) + 1 != group_order:
        raise AssertionError("frozen group order mismatch")

    subgroup_points, polynomial_a, polynomial_b, _, _ = construct_factor(
        p, order, generator
    )
    subgroup = set(subgroup_points)
    translation = subgroup_points[2]
    if translation is None:
        raise AssertionError("translation was the identity")

    seen: set[Point] = set()
    outside_results: list[dict[str, object]] = []
    for base in all_curve_points(p):
        if base in seen:
            continue
        orbit: list[Point] = []
        current = base
        for _ in range(order):
            orbit.append(current)
            seen.add(current)
            current = ec_add(current, translation, p)
        if current != base or len(set(orbit)) != order:
            raise AssertionError("translation orbit did not have order n")
        if base in subgroup:
            continue
        if any(point is None or point in subgroup for point in orbit):
            raise AssertionError("outside coset met the subgroup")

        values = [
            factor_value(polynomial_a, polynomial_b, point, p)
            for point in orbit
        ]
        if any(value == 0 for value in values):
            raise AssertionError("oriented factor vanished outside its divisor")

        cocycle = [
            values[(index + 1) % order] * inv(values[index], p) % p
            for index in range(order)
        ]
        if math.prod(cocycle) % p != 1:
            raise AssertionError("cyclic cocycle norm was not one")

        matrix: list[list[int]] = []
        for index, value in enumerate(cocycle):
            row = [0] * order
            row[index] = (-value) % p
            row[(index + 1) % order] = 1
            matrix.append(row)
        kernel = nullspace_mod(matrix, p)
        if len(kernel) != 1:
            raise AssertionError("cyclic recurrence nullity was not one")
        if any(entry % p == 0 for entry in kernel[0]):
            raise AssertionError("cyclic recurrence kernel was not dense")
        if not proportional(kernel[0], values, p):
            raise AssertionError("kernel vector did not reconstruct potential")

        linear_complexity = berlekamp_massey(values * 3, p)
        if linear_complexity != order:
            raise AssertionError("frozen potential had a shorter recurrence")

        polynomial = orbit_polynomial(values, p)
        if len(polynomial) != order + 1:
            raise AssertionError("orbit polynomial degree mismatch")
        if any(coefficient == 0 for coefficient in polynomial):
            raise AssertionError("frozen orbit polynomial was sparse")

        outside_results.append(
            {
                "coset_base": base,
                "orbit_length": order,
                "linear_complexity": linear_complexity,
                "recurrence_nullity": len(kernel),
                "kernel_nonzero_coordinates": sum(
                    entry % p != 0 for entry in kernel[0]
                ),
                "orbit_polynomial_nonzero_coefficients": sum(
                    coefficient != 0 for coefficient in polynomial
                ),
                "orbit_polynomial_coefficients": len(polynomial),
                "cocycle_norm": 1,
            }
        )

    expected_cosets = group_order // order - 1
    if len(outside_results) != expected_cosets:
        raise AssertionError("outside coset count mismatch")

    return {
        "field_prime": p,
        "subgroup_order": order,
        "group_order": group_order,
        "outside_cosets": outside_results,
        "outside_coset_count": len(outside_results),
        "outside_points": len(outside_results) * order,
        "all_linear_complexities_full": all(
            result["linear_complexity"] == order for result in outside_results
        ),
        "all_recurrence_nullities_one": all(
            result["recurrence_nullity"] == 1 for result in outside_results
        ),
        "all_kernel_vectors_dense": all(
            result["kernel_nonzero_coordinates"] == order
            for result in outside_results
        ),
        "all_orbit_polynomials_dense": all(
            result["orbit_polynomial_nonzero_coefficients"] == order + 1
            for result in outside_results
        ),
    }


def secp_certificate() -> dict[str, object]:
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "standard_orbit_vector_entries": SECP_N,
        "standard_cyclic_recurrence_nonzeros": 2 * SECP_N,
        "abstract_first_order_cocycle_realizes_every_nonzero_projective_vector": True,
        "low_matrix_sparsity_does_not_bound_kernel_description": True,
        "frozen_full_linear_complexity_is_not_a_secp_theorem": True,
        "compact_nonlinear_lift_found": False,
        "parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "selected_successor": "UORC056-POLYNOMIAL-PELL-SIGN-SEED-B17",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cases = [build_case(*case) for case in COSET_CASES]
    aggregate = {
        "cases": len(cases),
        "outside_cosets": sum(case["outside_coset_count"] for case in cases),
        "outside_points": sum(case["outside_points"] for case in cases),
        "orbit_polynomial_coefficients_checked": sum(
            result["orbit_polynomial_coefficients"]
            for case in cases
            for result in case["outside_cosets"]
        ),
        "recurrence_matrices_checked": sum(
            case["outside_coset_count"] for case in cases
        ),
        "all_linear_complexities_full": all(
            case["all_linear_complexities_full"] for case in cases
        ),
        "all_recurrence_nullities_one": all(
            case["all_recurrence_nullities_one"] for case in cases
        ),
        "all_kernel_vectors_dense": all(
            case["all_kernel_vectors_dense"] for case in cases
        ),
        "all_orbit_polynomials_dense": all(
            case["all_orbit_polynomials_dense"] for case in cases
        ),
    }
    payload = {
        "package": "UORC056-HILBERT90-DISPLACEMENT-BOUNDARY-B16",
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp_certificate(),
        "decision": (
            "A sparse first-order cyclic recurrence is universal for nonzero "
            "projective vectors and therefore does not itself compress the "
            "distinguished Hilbert-90 solution. Every frozen outside-coset "
            "factor sequence has full base-field linear complexity and a "
            "dense orbit polynomial. Standard linear, displacement, explicit "
            "trace, and orbit-polynomial routes remain linear-state mechanisms."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
