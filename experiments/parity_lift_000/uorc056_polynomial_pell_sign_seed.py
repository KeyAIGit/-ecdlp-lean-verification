#!/usr/bin/env python3
"""Exact frozen replay for UORC056 polynomial-Pell sign seed B17.

No external curve, point, key, wallet, unknown scalar, or production-sized DLP
input is accepted. Production constants are used only for public cost counts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from uorc056_hilbert90_integration_core import construct_factor
from uorc056_oriented_principal_pell_core import (
    B_CURVE,
    FROZEN_CASES,
    SECP_N,
    inv,
    kernel_polynomial,
    orbit,
    poly_eval,
    poly_mul,
    poly_sub,
    trim,
)


def negate_polynomial(polynomial: list[int], p: int) -> list[int]:
    return trim([(-coefficient) % p for coefficient in polynomial], p)


def equal_polynomials(left: list[int], right: list[int], p: int) -> bool:
    left = trim(left, p)
    right = trim(right, p)
    return left == right


def pell_norm(polynomial_a: list[int], polynomial_b: list[int], p: int) -> list[int]:
    curve = [B_CURVE % p, 0, 0, 1]
    return poly_sub(
        poly_mul(polynomial_a, polynomial_a, p),
        poly_mul(curve, poly_mul(polynomial_b, polynomial_b, p), p),
        p,
    )


def build_case(p: int, order: int, generator: tuple[int, int]) -> dict[str, object]:
    points, polynomial_a, polynomial_b, sum_scalar, anchor_scalar = construct_factor(
        p, order, generator
    )
    negative_generator = (generator[0], (-generator[1]) % p)
    (
        negative_points,
        negative_a,
        negative_b,
        negative_sum_scalar,
        negative_anchor_scalar,
    ) = construct_factor(p, order, negative_generator)

    if sum_scalar != negative_sum_scalar or anchor_scalar != negative_anchor_scalar:
        raise AssertionError("relative public scalar anchors changed")

    kernel = kernel_polynomial(points, order, p)
    negative_kernel = kernel_polynomial(negative_points, order, p)
    if not equal_polynomials(kernel, negative_kernel, p):
        raise AssertionError("Kummer kernel changed under generator negation")

    sum_point = points[sum_scalar]
    negative_sum_point = negative_points[negative_sum_scalar]
    if sum_point is None or negative_sum_point is None:
        raise AssertionError("public sum anchor was the identity")
    if sum_point[0] != negative_sum_point[0]:
        raise AssertionError("public anchor x-coordinate changed")

    if not equal_polynomials(negative_a, negate_polynomial(polynomial_a, p), p):
        raise AssertionError("normalized A did not negate")
    if not equal_polynomials(negative_b, polynomial_b, p):
        raise AssertionError("normalized B changed")

    norm = pell_norm(polynomial_a, polynomial_b, p)
    negative_norm = pell_norm(negative_a, negative_b, p)
    if not equal_polynomials(norm, negative_norm, p):
        raise AssertionError("quadratic Pell norm changed under conjugation")

    x_generator, y_generator = generator
    seed = (
        poly_eval(polynomial_a, x_generator, p)
        - y_generator * poly_eval(polynomial_b, x_generator, p)
    ) % p
    opposite = (
        poly_eval(polynomial_a, x_generator, p)
        + y_generator * poly_eval(polynomial_b, x_generator, p)
    ) % p
    if seed != 0 or opposite == 0:
        raise AssertionError("marked generator seed did not select one conjugate")

    x_negative, y_negative = negative_generator
    negative_seed = (
        poly_eval(negative_a, x_negative, p)
        - y_negative * poly_eval(negative_b, x_negative, p)
    ) % p
    negative_opposite = (
        poly_eval(negative_a, x_negative, p)
        + y_negative * poly_eval(negative_b, x_negative, p)
    ) % p
    if negative_seed != 0 or negative_opposite == 0:
        raise AssertionError("negated marked seed failed")

    parity_checks = 0
    public_exceptions: list[int] = []
    public_pair = {sum_scalar, anchor_scalar}
    for scalar in range(1, order):
        point = points[scalar]
        if point is None:
            raise AssertionError("nonzero subgroup scalar was the identity")
        x_value, y_value = point
        a_value = poly_eval(polynomial_a, x_value, p)
        b_value = poly_eval(polynomial_b, x_value, p)
        if a_value == 0:
            if b_value != 0 or scalar not in public_pair:
                raise AssertionError("unexpected selector denominator exception")
            public_exceptions.append(scalar)
            continue
        selector = (-y_value * b_value * inv(a_value, p)) % p
        expected = 1 if scalar % 2 == 0 else p - 1
        if selector != expected:
            raise AssertionError("Pell selector lost canonical parity")
        parity_checks += 1

    pole_order = (order + 1) // 2
    coefficient_count = len(polynomial_a) + len(polynomial_b)
    if coefficient_count != pole_order:
        raise AssertionError("explicit Pell coefficient count mismatch")

    return {
        "field_prime": p,
        "order": order,
        "generator": generator,
        "negative_generator": negative_generator,
        "degree_a": len(polynomial_a) - 1,
        "degree_b": len(polynomial_b) - 1,
        "explicit_coefficient_count": coefficient_count,
        "expected_coefficient_count": pole_order,
        "public_sum_scalar": sum_scalar,
        "public_anchor_scalar": anchor_scalar,
        "public_exceptions": public_exceptions,
        "parity_checks": parity_checks,
        "kernel_generator_blind": True,
        "anchor_x_generator_blind": True,
        "normalized_a_negates": True,
        "normalized_b_fixed": True,
        "pell_norm_generator_blind": True,
        "marked_seed_exact": True,
        "negated_marked_seed_exact": True,
    }


def secp_certificate() -> dict[str, object]:
    half = (SECP_N - 1) // 2
    pole_order = (SECP_N + 1) // 2
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "kummer_degree": half,
        "explicit_pell_coefficients": pole_order,
        "explicit_pell_coefficients_bit_length": pole_order.bit_length(),
        "symmetric_pell_data_selects_conjugate": False,
        "public_marked_generator_seed_exists": True,
        "standard_half_gcd_requires_oriented_root_or_dense_output": True,
        "one_point_seed_subroot_propagation_found": False,
        "parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "selected_successor": "UORC056-NONLINEAR-SEED-PROPAGATION-B18",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cases = [build_case(*case) for case in FROZEN_CASES]
    aggregate = {
        "cases": len(cases),
        "parity_checks": sum(case["parity_checks"] for case in cases),
        "public_exceptions": sum(len(case["public_exceptions"]) for case in cases),
        "generator_reversal_checks": len(cases),
        "pell_norm_checks": len(cases),
        "marked_seed_checks": 2 * len(cases),
        "all_kernel_data_generator_blind": all(
            case["kernel_generator_blind"] and case["anchor_x_generator_blind"]
            for case in cases
        ),
        "all_normalized_solutions_conjugate": all(
            case["normalized_a_negates"] and case["normalized_b_fixed"]
            for case in cases
        ),
        "all_pell_norms_equal": all(case["pell_norm_generator_blind"] for case in cases),
        "all_marked_seeds_exact": all(
            case["marked_seed_exact"] and case["negated_marked_seed_exact"]
            for case in cases
        ),
        "all_explicit_coefficient_counts_exact": all(
            case["explicit_coefficient_count"] == case["expected_coefficient_count"]
            for case in cases
        ),
    }
    payload = {
        "package": "UORC056-POLYNOMIAL-PELL-SIGN-SEED-B17",
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp_certificate(),
        "decision": (
            "The symmetric polynomial-Pell input is invariant under quadratic "
            "conjugation and cannot by itself select the marked generator. A "
            "public one-point seed at G selects the conjugate mathematically, "
            "but standard half-gcd/subresultant methods either consume an "
            "explicit oriented modular root or construct the Theta(n)-coefficient "
            "Pell solution. No sub-square-root seed propagation is found."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
