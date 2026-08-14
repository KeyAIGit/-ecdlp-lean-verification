#!/usr/bin/env python3
"""Exact divisor-support replay for UORC056 MILLER MONOMIAL SUPPORT B11.

Only frozen public prime orders are used. No curve point, key, wallet, or
unknown scalar is accepted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
FROZEN_ORDERS = (7, 31, 61, 79, 67, 79, 127, 139, 199, 313)


def ceil_div(numerator: int, denominator: int) -> int:
    return (numerator + denominator - 1) // denominator


def oriented_divisor_coefficients(order: int) -> list[int]:
    middle = (order - 1) // 2
    coefficients = [0] * order
    coefficients[0] = -middle
    coefficients[1] = middle + 1
    for label in range(2, order):
        coefficients[label] = -1 if label % 2 == 0 else 1
    return coefficients


def run_case(order: int) -> dict[str, object]:
    middle = (order - 1) // 2
    coefficients = oriented_divisor_coefficients(order)
    if any(coefficient == 0 for coefficient in coefficients):
        raise AssertionError("oriented divisor had a zero coefficient")
    if sum(coefficients) != 0:
        raise AssertionError("oriented divisor lost degree zero")

    expected_counts = {
        -middle: 1,
        middle + 1: 1,
        -1: middle,
        1: middle - 1,
    }
    observed_counts: dict[int, int] = {}
    for coefficient in coefficients:
        observed_counts[coefficient] = observed_counts.get(coefficient, 0) + 1
    if observed_counts != expected_counts:
        raise AssertionError("oriented coefficient multiplicities failed")

    constant_shift_checks = 0
    minimum_shifted_support = order
    minimizing_constants: list[int] = []
    for constant in range(-middle - 2, middle + 3):
        shifted_support = sum(
            1 for coefficient in coefficients if coefficient - constant != 0
        )
        if shifted_support < minimum_shifted_support:
            minimum_shifted_support = shifted_support
            minimizing_constants = [constant]
        elif shifted_support == minimum_shifted_support:
            minimizing_constants.append(constant)
        constant_shift_checks += 1

    if minimum_shifted_support != middle + 1:
        raise AssertionError("full-orbit correction support bound failed")
    if -1 not in minimizing_constants:
        raise AssertionError("expected dominant coefficient was not minimizing")

    direct_atom_lower_bound = ceil_div(order, 4)
    corrected_atom_lower_bound = ceil_div(middle + 1, 4)
    if 4 * direct_atom_lower_bound < order:
        raise AssertionError("direct atom bound failed")
    if 4 * corrected_atom_lower_bound < middle + 1:
        raise AssertionError("corrected atom bound failed")

    return {
        "order": order,
        "middle": middle,
        "divisor_support": order,
        "constant_shift_checks": constant_shift_checks,
        "minimum_full_orbit_corrected_support": minimum_shifted_support,
        "minimizing_constants": minimizing_constants,
        "direct_atom_lower_bound": direct_atom_lower_bound,
        "corrected_atom_lower_bound": corrected_atom_lower_bound,
        "all_coefficients_nonzero": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    middle = (SECP_N - 1) // 2
    direct = ceil_div(SECP_N, 4)
    corrected = ceil_div(middle + 1, 4)
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "middle": middle,
        "oriented_divisor_support": SECP_N,
        "minimum_full_orbit_corrected_support": middle + 1,
        "direct_miller_line_atom_lower_bound": direct,
        "corrected_miller_line_atom_lower_bound": corrected,
        "corrected_atom_lower_bound_bit_length": corrected.bit_length(),
        "short_ordinary_miller_monomial_exists_in_declared_class": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "remaining_candidate": "cyclic elliptic shifted factorial / nonlinear endpoint identity",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "uorc056_miller_monomial_support_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_ORDERS]
    payload = {
        "package": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056-MILLER-MONOMIAL-SUPPORT-B11",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "oriented_divisor_support": sum(
                case["divisor_support"] for case in cases
            ),
            "constant_shift_checks": sum(
                case["constant_shift_checks"] for case in cases
            ),
            "minimum_corrected_support": sum(
                case["minimum_full_orbit_corrected_support"]
                for case in cases
            ),
            "all_coefficients_nonzero": all(
                case["all_coefficients_nonzero"] for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "The alternating Miller potential has nonzero divisor coefficient "
            "at all n kernel points. A full-orbit quotient correction can cancel "
            "at most M of them, leaving at least M+1. Since each ordinary "
            "Miller or line atom has support at most four, every direct monomial "
            "representation in the declared class uses linearly many atoms."
        ),
        "claim_boundary": [
            "The divisor coefficient pattern and constant-shift minimum are exact.",
            "The atom bound applies to products/ratios of ordinary bounded-support Miller and line functions.",
            "It does not exclude one high-degree dense-divisor atom generated by a new short circuit.",
            "No parity oracle, EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
