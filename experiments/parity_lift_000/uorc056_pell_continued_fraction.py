#!/usr/bin/env python3
"""Frozen replay for the standard Pell continued-fraction boundary.

No external point, key, wallet, hidden scalar, or production-sized DLP target is
accepted. The script reconstructs the B7A principal factors on the ten frozen
toy curves and audits only their ordinary polynomial Euclidean representations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from uorc056_oriented_principal_pell_core import (
    FROZEN_CASES,
    SECP_N,
    normalize_vector,
    nullspace_mod,
    orbit,
    poly_divmod,
    trim,
)


def poly_gcd(left: list[int], right: list[int], p: int) -> list[int]:
    left = trim(left.copy(), p)
    right = trim(right.copy(), p)
    while right != [0]:
        _, remainder = poly_divmod(left, right, p)
        left, right = right, trim(remainder, p)
    if left == [0]:
        return [0]
    scale = pow(left[-1], -1, p)
    return trim([(scale * value) % p for value in left], p)


def principal_polynomials(
    p: int, order: int, generator: tuple[int, int]
) -> tuple[list[int], list[int], list[int]]:
    points = orbit(generator, order, p)
    half = (order - 1) // 2
    pole_order = half + 1
    support = [points[index] for index in range(2, order, 2)]
    sum_scalar = (-pow(4, -1, order)) % order
    anchor = points[(-sum_scalar) % order]
    if anchor is None or any(point is None for point in support):
        raise AssertionError("unexpected identity in principal support")

    degree_a = pole_order // 2
    degree_b = (pole_order - 3) // 2
    count_a = degree_a + 1
    count_b = degree_b + 1
    rows: list[list[int]] = []
    for point in support + [anchor]:
        if point is None:
            raise AssertionError("unexpected identity row")
        x_coordinate, y_coordinate = point
        rows.append(
            [pow(x_coordinate, exponent, p) for exponent in range(count_a)]
            + [
                y_coordinate * pow(x_coordinate, exponent, p) % p
                for exponent in range(count_b)
            ]
        )

    basis = nullspace_mod(rows, p)
    if len(basis) != 1:
        raise AssertionError("principal nullspace was not one-dimensional")
    vector = normalize_vector(basis[0], p)
    polynomial_a = trim(vector[:count_a], p)
    polynomial_b = trim(vector[count_a:], p)
    return polynomial_a, polynomial_b, poly_gcd(polynomial_a, polynomial_b, p)


def euclidean_quotients(
    numerator: list[int], denominator: list[int], p: int
) -> tuple[list[list[int]], list[int]]:
    left = trim(numerator.copy(), p)
    right = trim(denominator.copy(), p)
    if len(left) < len(right):
        left, right = right, left
    quotients: list[list[int]] = []
    while right != [0]:
        quotient, remainder = poly_divmod(left, right, p)
        quotients.append(trim(quotient, p))
        left, right = right, trim(remainder, p)
    return quotients, left


def run_case(
    p: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    polynomial_a, polynomial_b, declared_gcd = principal_polynomials(
        p, order, generator
    )
    numerator, denominator = polynomial_a, polynomial_b
    if len(numerator) < len(denominator):
        numerator, denominator = denominator, numerator

    quotients, terminal_gcd = euclidean_quotients(numerator, denominator, p)
    quotient_degrees = [len(quotient) - 1 for quotient in quotients]
    numerator_degree = len(numerator) - 1
    denominator_degree = len(denominator) - 1
    gcd_degree = len(terminal_gcd) - 1

    if len(declared_gcd) - 1 != gcd_degree:
        raise AssertionError("terminal gcd mismatch")
    if sum(quotient_degrees) != numerator_degree - gcd_degree:
        raise AssertionError("quotient degrees did not telescope")

    coefficient_slots = sum(degree + 1 for degree in quotient_degrees)
    if coefficient_slots < numerator_degree - gcd_degree:
        raise AssertionError("coefficient slots undercount reduced degree")

    return {
        "field_prime": p,
        "order": order,
        "generator": generator,
        "degree_a": len(polynomial_a) - 1,
        "degree_b": len(polynomial_b) - 1,
        "numerator_degree": numerator_degree,
        "denominator_degree": denominator_degree,
        "gcd_degree": gcd_degree,
        "euclidean_quotient_count": len(quotients),
        "euclidean_quotient_degrees": quotient_degrees,
        "euclidean_quotient_degree_sum": sum(quotient_degrees),
        "materialized_quotient_coefficient_slots": coefficient_slots,
        "degree_one_quotients": sum(degree == 1 for degree in quotient_degrees),
        "a_nonzero_coefficients": sum(value != 0 for value in polynomial_a),
        "b_nonzero_coefficients": sum(value != 0 for value in polynomial_b),
        "telescoping_identity_exact": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP_N
    if n % 8 != 1:
        raise AssertionError("unexpected secp256k1 order residue")
    h = (n - 1) // 4
    forced_b_degree = h - 1
    gcd_degree_upper_bound = 1
    reduced_degree_lower_bound = forced_b_degree - gcd_degree_upper_bound
    return {
        "n": n,
        "n_bit_length": n.bit_length(),
        "n_mod_8": n % 8,
        "quarter_parameter_h": h,
        "principal_pole_order": (n + 1) // 2,
        "forced_b_degree": forced_b_degree,
        "public_exception_gcd_degree_upper_bound": gcd_degree_upper_bound,
        "reduced_euclidean_degree_lower_bound": reduced_degree_lower_bound,
        "reduced_degree_lower_bound_ge_2_pow_253": (
            reduced_degree_lower_bound >= 2 ** 253
        ),
        "standard_explicit_continued_fraction_sub_sqrt": False,
        "transposed_single_value_factor_evaluation_closed": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "public_parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    aggregate = {
        "cases": len(cases),
        "total_principal_numerator_degree": sum(
            case["numerator_degree"] for case in cases
        ),
        "total_gcd_degree": sum(case["gcd_degree"] for case in cases),
        "total_euclidean_quotients": sum(
            case["euclidean_quotient_count"] for case in cases
        ),
        "total_euclidean_quotient_degree": sum(
            case["euclidean_quotient_degree_sum"] for case in cases
        ),
        "total_materialized_quotient_coefficient_slots": sum(
            case["materialized_quotient_coefficient_slots"] for case in cases
        ),
        "total_degree_one_quotients": sum(
            case["degree_one_quotients"] for case in cases
        ),
        "all_telescoping_identities_exact": all(
            case["telescoping_identity_exact"] for case in cases
        ),
        "largest_order": max(case["order"] for case in cases),
        "largest_quotient_count": max(
            case["euclidean_quotient_count"] for case in cases
        ),
    }
    payload = {
        "package": "UORC056-PELL-CONTINUED-FRACTION-B16",
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Ordinary Euclidean quotients have total degree equal to the "
            "reduced input degree. Explicit continued-fraction or half-gcd "
            "state therefore has linear representation size. An implicit "
            "transposed single-value evaluator remains open."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
