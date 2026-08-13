#!/usr/bin/env python3
"""Exact arithmetic replay for ADDITIVE-SQUARE-CLASS-CONDUCTOR-039.

The package studies the uniform one-addition family

    F_m(Q) = x(Q)^(2^m) - x(Q)

on E: y^2 = x^3 + 7.  It does not evaluate a hidden key or claim that this
family decodes carry.  It verifies the fixed-public arithmetic entering the
counterexample to an addition-count-only conductor lower bound:

* separability of T^(2^m)-T;
* the degree of its overlap with the three finite branch values T^3+7=0;
* the resulting geometric odd-support formula 2*(2^m-b_m);
* the secp256k1 m=127 specialization, where b_m=0 and the support is 2^128.

Only polynomial arithmetic modulo the cubic branch polynomial is required;
T^(2^m)-T is never materialized.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from nonlocal_odd_anchor_screen import FROZEN_CASES

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
RATIONAL_DEGREE_BARRIER = 54157620742477409023451113735280473968


def trim(poly: list[int], modulus: int) -> list[int]:
    poly = [coefficient % modulus for coefficient in poly]
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def poly_sub(left: list[int], right: list[int], modulus: int) -> list[int]:
    size = max(len(left), len(right))
    result = [0] * size
    for index in range(size):
        a = left[index] if index < len(left) else 0
        b = right[index] if index < len(right) else 0
        result[index] = (a - b) % modulus
    return trim(result, modulus)


def poly_mul(left: list[int], right: list[int], modulus: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] = (result[i + j] + a * b) % modulus
    return trim(result, modulus)


def poly_divmod(
    numerator: list[int], denominator: list[int], modulus: int
) -> tuple[list[int], list[int]]:
    numerator = trim(numerator[:], modulus)
    denominator = trim(denominator[:], modulus)
    if denominator == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    quotient = [0] * max(1, len(numerator) - len(denominator) + 1)
    inverse_lead = pow(denominator[-1], -1, modulus)
    while numerator != [0] and len(numerator) >= len(denominator):
        shift = len(numerator) - len(denominator)
        coefficient = numerator[-1] * inverse_lead % modulus
        quotient[shift] = coefficient
        for index, value in enumerate(denominator):
            numerator[index + shift] = (
                numerator[index + shift] - coefficient * value
            ) % modulus
        numerator = trim(numerator, modulus)
    return trim(quotient, modulus), numerator


def poly_mod(
    numerator: list[int], denominator: list[int], modulus: int
) -> list[int]:
    return poly_divmod(numerator, denominator, modulus)[1]


def poly_pow_mod(
    base: list[int], exponent: int, denominator: list[int], modulus: int
) -> list[int]:
    result = [1]
    power = poly_mod(base, denominator, modulus)
    while exponent:
        if exponent & 1:
            result = poly_mod(poly_mul(result, power, modulus), denominator, modulus)
        power = poly_mod(poly_mul(power, power, modulus), denominator, modulus)
        exponent >>= 1
    return result


def poly_gcd(left: list[int], right: list[int], modulus: int) -> list[int]:
    left = trim(left, modulus)
    right = trim(right, modulus)
    while right != [0]:
        left, right = right, poly_mod(left, right, modulus)
    inverse_lead = pow(left[-1], -1, modulus)
    return trim([coefficient * inverse_lead for coefficient in left], modulus)


def branch_overlap(field_prime: int, m: int) -> tuple[int, list[int]]:
    """Return deg gcd(T^(2^m)-T, T^3+7) and the monic gcd."""
    cubic = [7 % field_prime, 0, 0, 1]
    coordinate = [0, 1]
    exponent = 1 << m
    remainder = poly_sub(
        poly_pow_mod(coordinate, exponent, cubic, field_prime),
        coordinate,
        field_prime,
    )
    common = poly_gcd(cubic, remainder, field_prime)
    return len(common) - 1, common


def run_case(field_prime: int, m: int) -> dict[str, object]:
    exponent = 1 << m
    separable = (exponent - 1) % field_prime != 0
    overlap, common = branch_overlap(field_prime, m)
    odd_support = 2 * (exponent - overlap)
    lower_bound = 2 * (exponent - 3)
    if not separable:
        status = "excluded_inseparable"
    else:
        status = "verified"
        if not (0 <= overlap <= 3):
            raise AssertionError("branch overlap exceeded the cubic degree")
        if odd_support < lower_bound:
            raise AssertionError("odd-support lower bound failed")
    return {
        "p": field_prime,
        "m": m,
        "power_degree": exponent,
        "separable": separable,
        "branch_overlap_degree": overlap,
        "branch_gcd": common,
        "odd_support_degree": odd_support,
        "uniform_lower_bound": lower_bound,
        "squaring_gates": m,
        "additive_gates": 1,
        "total_arithmetic_gates": m + 1,
        "status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "additive_square_class_conductor_results.json"
        ),
    )
    args = parser.parse_args()

    toy_rows: list[dict[str, object]] = []
    for field_prime, _order, _generator in FROZEN_CASES:
        for m in range(1, 13):
            toy_rows.append(run_case(field_prime, m))

    verified = [row for row in toy_rows if row["status"] == "verified"]
    excluded = [row for row in toy_rows if row["status"] != "verified"]

    secp_m = 127
    secp_row = run_case(SECP256K1_P, secp_m)
    expected_support = 1 << 128
    sqrt_floor = math.isqrt(SECP256K1_N)
    if secp_row["branch_overlap_degree"] != 0:
        raise AssertionError("secp256k1 m=127 branch overlap was nonzero")
    if secp_row["odd_support_degree"] != expected_support:
        raise AssertionError("secp256k1 odd-support degree was not 2^128")
    if expected_support <= sqrt_floor:
        raise AssertionError("counterfamily did not cross the square-root scale")

    rational_map_degree = 2 * (1 << secp_m)
    if rational_map_degree <= RATIONAL_DEGREE_BARRIER:
        raise AssertionError("counterfamily did not cross the prior degree barrier")

    payload = {
        "package": "ADDITIVE-SQUARE-CLASS-CONDUCTOR-039",
        "scope": (
            "fixed public polynomial arithmetic for the one-addition conductor "
            "counterfamily; no external point or discrete-log target"
        ),
        "toy_rows": toy_rows,
        "secp256k1": {
            **secp_row,
            "subgroup_order": SECP256K1_N,
            "sqrt_order_floor": sqrt_floor,
            "odd_support_exceeds_sqrt_order": True,
            "rational_map_degree": rational_map_degree,
            "prior_rational_degree_barrier": RATIONAL_DEGREE_BARRIER,
            "degree_barrier_crossed": True,
        },
        "aggregate": {
            "toy_cases": len(FROZEN_CASES),
            "m_values_per_case": 12,
            "verified_rows": len(verified),
            "excluded_inseparable_rows": len(excluded),
            "all_verified_overlap_degrees_at_most_three": all(
                int(row["branch_overlap_degree"]) <= 3 for row in verified
            ),
            "all_verified_support_bounds_hold": all(
                int(row["odd_support_degree"]) >= int(row["uniform_lower_bound"])
                for row in verified
            ),
        },
        "decision": (
            "Odd-support degree and Kummer-cover genus cannot yield a lower "
            "bound from the number of additions alone. The uniform family "
            "x^(2^m)-x uses one subtraction and m squarings while its geometric "
            "odd support is 2*(2^m-b_m), b_m<=3. On fixed secp256k1 at m=127, "
            "b_m=0 and the support is exactly 2^128, already above floor(sqrt(n))."
        ),
        "claim_boundary": [
            "The counterfamily is not a carry or hard-R3 decoder.",
            "It may vanish on subgroup points and is used only to reject an addition-count-only proof invariant.",
            "No universal arithmetic-circuit lower bound is proved.",
            "No external point, key, wallet, or production-sized target is processed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
