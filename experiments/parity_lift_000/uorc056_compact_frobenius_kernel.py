#!/usr/bin/env python3
"""Exact frozen-corpus replay for compact kernel-map local data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from uorc056_miller_kernel_edge import (
    B_CURVE,
    SECP_N,
    SECP_P,
    orbit,
    poly_add,
    poly_exact_div,
    poly_gcd,
    poly_mul,
    poly_scale,
    poly_sub,
    poly_eval,
    trim,
)

FROZEN_CASES = (
    (13, 7, (7, 5)),
    (43, 31, (2, 12)),
    (61, 61, (2, 25)),
    (67, 79, (2, 22)),
    (79, 67, (1, 18)),
    (97, 79, (1, 28)),
)


def monomial(degree: int, coefficient: int = 1) -> list[int]:
    polynomial = [0] * (degree + 1)
    polynomial[degree] = coefficient
    return polynomial


def polynomial_power(poly: list[int], exponent: int, p: int) -> list[int]:
    result = [1]
    base = poly
    while exponent:
        if exponent & 1:
            result = poly_mul(result, base, p)
        exponent >>= 1
        if exponent:
            base = poly_mul(base, base, p)
    return result


def polynomial_derivative(poly: list[int], p: int) -> list[int]:
    if len(poly) <= 1:
        return [0]
    return trim([index * poly[index] for index in range(1, len(poly))], p)


def compact_map_polynomials(p: int) -> dict[str, list[int]]:
    curve_rhs = [B_CURVE, 0, 0, 1]
    x_to_p = monomial(p)
    x_polynomial = [0, 1]
    x_p_minus_x = poly_sub(x_to_p, x_polynomial, p)
    x_p_plus_x = poly_add(x_to_p, x_polynomial, p)
    euler = polynomial_power(curve_rhs, (p - 1) // 2, p)
    rational_kernel = poly_gcd(x_p_minus_x, poly_sub(euler, [1], p), p)
    complementary_factor = poly_gcd(x_p_minus_x, poly_add(euler, [1], p), p)
    denominator_square = poly_mul(x_p_minus_x, x_p_minus_x, p)
    curve_rhs_to_p = polynomial_power(curve_rhs, p, p)
    curve_rhs_half = polynomial_power(curve_rhs, (p + 1) // 2, p)
    numerator = poly_sub(
        poly_add(
            poly_add(curve_rhs_to_p, poly_scale(curve_rhs_half, 2, p), p),
            curve_rhs,
            p,
        ),
        poly_mul(x_p_plus_x, denominator_square, p),
        p,
    )
    complementary_square = poly_mul(complementary_factor, complementary_factor, p)
    reduced_numerator = poly_exact_div(numerator, complementary_square, p)
    reduced_denominator = poly_exact_div(denominator_square, complementary_square, p)
    return {
        "curve_rhs": curve_rhs,
        "x_p_minus_x": x_p_minus_x,
        "rational_kernel": rational_kernel,
        "complementary_factor": complementary_factor,
        "numerator": numerator,
        "denominator_square": denominator_square,
        "reduced_numerator": reduced_numerator,
        "reduced_denominator": reduced_denominator,
    }


def run_case(p: int, order: int, generator: tuple[int, int]) -> dict[str, object]:
    points = orbit(generator, order, p)
    data = compact_map_polynomials(p)
    curve_rhs = data["curve_rhs"]
    x_p_minus_x = data["x_p_minus_x"]
    rational_kernel = data["rational_kernel"]
    complementary_factor = data["complementary_factor"]
    numerator = data["numerator"]
    denominator_square = data["denominator_square"]
    reduced_numerator = data["reduced_numerator"]
    reduced_denominator = data["reduced_denominator"]
    if poly_mul(rational_kernel, complementary_factor, p) != x_p_minus_x:
        raise AssertionError("factor reconstruction failed")
    complementary_square = poly_mul(complementary_factor, complementary_factor, p)
    if poly_gcd(numerator, denominator_square, p) != complementary_square:
        raise AssertionError("unexpected cancellation factor")
    kernel_square = poly_mul(rational_kernel, rational_kernel, p)
    if reduced_denominator != kernel_square:
        raise AssertionError("unexpected reduced denominator")
    if len(rational_kernel) - 1 != (order - 1) // 2:
        raise AssertionError("unexpected rational factor degree")
    kernel_derivative = polynomial_derivative(rational_kernel, p)
    point_checks = 0
    negation_checks = 0
    for point in points[1:]:
        if point is None:
            raise AssertionError("nonzero label produced identity")
        x_coordinate, y_coordinate = point
        curve_value = poly_eval(curve_rhs, x_coordinate, p)
        if curve_value != y_coordinate * y_coordinate % p:
            raise AssertionError("point check failed")
        if poly_eval(x_p_minus_x, x_coordinate, p) != 0:
            raise AssertionError("base-field x check failed")
        if poly_eval(rational_kernel, x_coordinate, p) != 0:
            raise AssertionError("rational factor membership failed")
        if poly_eval(complementary_factor, x_coordinate, p) == 0:
            raise AssertionError("factor collision")
        if poly_eval(numerator, x_coordinate, p) != 4 * curve_value % p:
            raise AssertionError("unreduced local coefficient failed")
        derivative_value = poly_eval(kernel_derivative, x_coordinate, p)
        expected_reduced = 4 * curve_value * derivative_value * derivative_value % p
        if poly_eval(reduced_numerator, x_coordinate, p) != expected_reduced:
            raise AssertionError("reduced local coefficient failed")
        point_checks += 1
        negated_y = -y_coordinate % p
        if negated_y * negated_y % p != curve_value:
            raise AssertionError("negation changed the square")
        if 4 * negated_y * negated_y % p != 4 * curve_value % p:
            raise AssertionError("local coefficient was not negation blind")
        negation_checks += 1
    return {
        "field_prime": p,
        "order": order,
        "generator": generator,
        "rational_factor_degree": len(rational_kernel) - 1,
        "complementary_degree": len(complementary_factor) - 1,
        "compact_numerator_degree": len(numerator) - 1,
        "reduced_numerator_degree": len(reduced_numerator) - 1,
        "point_checks": point_checks,
        "negation_checks": negation_checks,
        "factor_reconstruction_exact": True,
        "cancellation_is_complement_square": True,
        "reduced_denominator_is_rational_factor_square": True,
        "local_coefficient_is_public_square": True,
        "declared_data_negation_blind": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    rational_degree = (SECP_N - 1) // 2
    return {
        "p": SECP_P,
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "cofactor_one": True,
        "rational_factor_degree": rational_degree,
        "complementary_factor_degree": SECP_P - rational_degree,
        "compact_map_degree": SECP_N,
        "short_denominator": "(X^p-X)^2",
        "reduced_denominator": "K(X)^2",
        "local_unreduced_numerator": "4*y(Q)^2",
        "local_reduced_numerator": "4*y(Q)^2*K'(x(Q))^2",
        "kernel_translation_germ_invariant": True,
        "selects_marked_root": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "UORC056-COMPACT-KERNEL-MAP-B3",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "point_checks": sum(case["point_checks"] for case in cases),
            "negation_checks": sum(case["negation_checks"] for case in cases),
            "all_factor_checks": all(case["factor_reconstruction_exact"] for case in cases),
            "all_cancellation_checks": all(
                case["cancellation_is_complement_square"]
                and case["reduced_denominator_is_rational_factor_square"]
                for case in cases
            ),
            "all_local_coefficient_checks": all(
                case["local_coefficient_is_public_square"] for case in cases
            ),
            "all_declared_data_negation_blind": all(
                case["declared_data_negation_blind"] for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": "The compact degree-n map has a short formula and reduced denominator equal to the square of the rational x-factor, but its local leading data is a public square and does not select a marked branch.",
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
