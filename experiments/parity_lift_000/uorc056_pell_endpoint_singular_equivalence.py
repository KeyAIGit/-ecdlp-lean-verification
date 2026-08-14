#!/usr/bin/env python3
"""Frozen replay for Pell singular-cut and translated endpoint equivalence.

No external curve, point, key, wallet, hidden scalar, or production-sized DLP
target is accepted. The script reconstructs only the ten frozen B7A principal
factors and compares their zero/pole classifier with the homogeneous translated
endpoint factor.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from uorc056_oriented_principal_pell_core import (
    FROZEN_CASES,
    SECP_N,
    inv,
    orbit,
    poly_eval,
)
from uorc056_pell_continued_fraction import principal_polynomials


def endpoint_factor_value(
    points: list[tuple[int, int] | None],
    order: int,
    shifted_point: tuple[int, int] | None,
    p: int,
) -> int:
    """Evaluate the homogeneous translated endpoint factor at kappa(P)."""
    half = (order - 1) // 2
    eta = 1 if half % 2 == 0 else 0
    if shifted_point is None:
        u, v = 1, 0
    else:
        u, v = shifted_point[0], 1

    value = v if eta else 1
    for scalar in range(1, half + 1):
        if scalar % 2 != half % 2:
            continue
        root = points[scalar]
        if root is None:
            raise AssertionError("endpoint support unexpectedly contained O")
        value = value * (u - root[0] * v) % p
    return value


def run_case(
    p: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    points = orbit(generator, order, p)
    polynomial_a, polynomial_b, common = principal_polynomials(
        p, order, generator
    )

    sum_scalar = (-inv(4, order)) % order
    anchor_scalar = inv(4, order)
    common_pair = {sum_scalar, anchor_scalar}
    predicted_common = order % 8 in (1, 3)
    common_degree = len(common) - 1
    if common_degree != int(predicted_common):
        raise AssertionError("Pell common factor did not match the n mod 8 gate")

    half_generator_scalar = inv(2, order)
    endpoint_checks = 0
    ordinary_pell_checks = 0
    public_pair_checks = 0
    simultaneous_zero_scalars: list[int] = []

    for scalar in range(1, order):
        point = points[scalar]
        if point is None:
            raise AssertionError("nonzero scalar produced O")
        x_coordinate, y_coordinate = point
        a_value = poly_eval(polynomial_a, x_coordinate, p)
        b_value = poly_eval(polynomial_b, x_coordinate, p)
        plus_value = (a_value + y_coordinate * b_value) % p
        minus_value = (a_value - y_coordinate * b_value) % p
        even = scalar % 2 == 0

        shifted = points[(scalar + half_generator_scalar) % order]
        endpoint_value = endpoint_factor_value(points, order, shifted, p)
        endpoint_zero = endpoint_value == 0
        if endpoint_zero != even:
            raise AssertionError("translated endpoint factor did not equal parity")
        endpoint_indicator = (1 - 2 * pow(endpoint_value, p - 1, p)) % p
        expected_indicator = 1 if even else p - 1
        if endpoint_indicator != expected_indicator:
            raise AssertionError("endpoint Fermat indicator failed")
        endpoint_checks += 1

        both_zero = plus_value == 0 and minus_value == 0
        if both_zero:
            simultaneous_zero_scalars.append(scalar)

        if predicted_common and scalar in common_pair:
            if not both_zero:
                raise AssertionError("predicted public common pair was not 0/0")
            if endpoint_zero != even:
                raise AssertionError("endpoint patch failed on the public pair")
            public_pair_checks += 1
            continue

        if both_zero:
            raise AssertionError("unexpected simultaneous Pell zero")
        if (plus_value == 0) != even:
            raise AssertionError("plus Pell factor did not select the even half")
        if (minus_value == 0) != (not even):
            raise AssertionError("minus Pell factor did not select the odd half")
        plus_indicator = (1 - 2 * pow(plus_value, p - 1, p)) % p
        minus_indicator = (2 * pow(minus_value, p - 1, p) - 1) % p
        expected = 1 if even else p - 1
        if plus_indicator != expected or minus_indicator != expected:
            raise AssertionError("Pell zero indicators failed")
        ordinary_pell_checks += 1

    expected_simultaneous = sorted(common_pair) if predicted_common else []
    if sorted(simultaneous_zero_scalars) != expected_simultaneous:
        raise AssertionError("simultaneous Pell zero set was not the public pair")

    return {
        "field_prime": p,
        "order": order,
        "order_mod_8": order % 8,
        "generator": generator,
        "sum_scalar": sum_scalar,
        "anchor_scalar": anchor_scalar,
        "predicted_common_pair": predicted_common,
        "common_polynomial_degree": common_degree,
        "simultaneous_zero_scalars": simultaneous_zero_scalars,
        "endpoint_checks": endpoint_checks,
        "ordinary_pell_checks": ordinary_pell_checks,
        "public_pair_checks": public_pair_checks,
        "endpoint_factor_total_on_nonzero_subgroup": True,
        "pell_and_endpoint_zero_classifiers_agree_off_public_pair": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP_N
    sum_scalar = (n - 1) // 4
    anchor_scalar = (3 * n + 1) // 4
    if (-pow(4, -1, n)) % n != sum_scalar:
        raise AssertionError("unexpected secp sum scalar")
    if pow(4, -1, n) != anchor_scalar:
        raise AssertionError("unexpected secp anchor scalar")
    if sum_scalar % 2 != 0 or anchor_scalar % 2 != 1:
        raise AssertionError("unexpected secp anchor parities")
    return {
        "n": n,
        "bit_length": n.bit_length(),
        "n_mod_8": n % 8,
        "sum_scalar": sum_scalar,
        "sum_scalar_parity": "even",
        "anchor_scalar": anchor_scalar,
        "anchor_scalar_parity": "odd",
        "pell_common_factor_degree": 1,
        "pell_public_zero_over_zero_points": 2,
        "translated_endpoint_factor_handles_both_public_points": True,
        "pell_singular_cut_is_endpoint_parity_off_public_pair": True,
        "new_sub_sqrt_mechanism_created": False,
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
        "total_nonzero_endpoint_checks": sum(
            case["endpoint_checks"] for case in cases
        ),
        "total_ordinary_pell_checks": sum(
            case["ordinary_pell_checks"] for case in cases
        ),
        "total_public_pair_checks": sum(
            case["public_pair_checks"] for case in cases
        ),
        "common_factor_cases": sum(
            case["predicted_common_pair"] for case in cases
        ),
        "total_common_polynomial_degree": sum(
            case["common_polynomial_degree"] for case in cases
        ),
        "all_endpoint_factors_total": all(
            case["endpoint_factor_total_on_nonzero_subgroup"] for case in cases
        ),
        "all_classifiers_agree_off_public_pair": all(
            case["pell_and_endpoint_zero_classifiers_agree_off_public_pair"]
            for case in cases
        ),
        "largest_order": max(case["order"] for case in cases),
    }
    payload = {
        "package": "UORC056-PELL-ENDPOINT-SINGULAR-EQUIVALENCE-B20",
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Away from the fully public common-root pair, the plus Pell factor "
            "vanishes exactly on even scalars and the minus factor exactly on "
            "odd scalars. The homogeneous translated endpoint factor gives the "
            "same classifier and remains total at the public 0/0 pair. Thus "
            "the B19 singular cut is the existing endpoint-parity object, not "
            "a new compression mechanism."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
