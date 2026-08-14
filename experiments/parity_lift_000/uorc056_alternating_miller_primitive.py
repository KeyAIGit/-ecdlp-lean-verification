#!/usr/bin/env python3
"""Exact divisor replay for UORC056 ALTERNATING MILLER PRIMITIVE B8.

The script uses only frozen public odd prime orders. It manipulates divisor
coefficients on the cyclic subgroup and evaluates no unknown point.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
FROZEN_ORDERS = (7, 31, 61, 79, 67, 79, 127, 139, 199, 313)


def add(left: list[int], right: list[int]) -> list[int]:
    return [a + b for a, b in zip(left, right, strict=True)]


def subtract(left: list[int], right: list[int]) -> list[int]:
    return [a - b for a, b in zip(left, right, strict=True)]


def line_divisor(order: int, centre: int) -> list[int]:
    result = [0] * order
    result[centre % order] += 1
    result[1] += 1
    result[(centre + 1) % order] -= 1
    result[0] -= 1
    return result


def miller_divisor(order: int, scalar: int, point_label: int) -> list[int]:
    result = [0] * order
    result[point_label % order] += scalar
    result[(scalar * point_label) % order] -= 1
    result[0] -= scalar - 1
    return result


def negate_pullback(divisor: list[int]) -> list[int]:
    order = len(divisor)
    return [divisor[(-label) % order] for label in range(order)]


def translate_argument(divisor: list[int], step: int) -> list[int]:
    """Divisor of P -> f(P+[step]G)."""
    order = len(divisor)
    return [divisor[(label + step) % order] for label in range(order)]


def divisor_degree(divisor: list[int]) -> int:
    return sum(divisor)


def divisor_class(divisor: list[int]) -> int:
    order = len(divisor)
    return sum(label * coefficient for label, coefficient in enumerate(divisor)) % order


def run_case(order: int) -> dict[str, object]:
    middle = (order - 1) // 2
    delta = [0] * order
    for label in range(1, order):
        delta[label] = 1 if label % 2 == 0 else -1

    alternating = [0] * order
    complementary = [0] * order
    line_divisor_checks = 0
    for centre in range(1, order, 2):
        alternating = add(alternating, line_divisor(order, centre))
        line_divisor_checks += 1
    for centre in range(2, order, 2):
        complementary = add(complementary, line_divisor(order, centre))
        line_divisor_checks += 1

    expected_alternating = [-value for value in delta]
    expected_alternating[1] += middle
    expected_alternating[0] -= middle
    if alternating != expected_alternating:
        raise AssertionError("alternating Miller divisor failed")

    expected_complementary = delta.copy()
    expected_complementary[1] += middle + 1
    expected_complementary[0] -= middle + 1
    if complementary != expected_complementary:
        raise AssertionError("complementary Miller divisor failed")

    full_miller = miller_divisor(order, order, 1)
    if add(alternating, complementary) != full_miller:
        raise AssertionError("alternating and complementary products did not give f_n")

    half_miller = miller_divisor(order, middle, 1)
    principalization = subtract(half_miller, alternating)
    expected_principalization = delta.copy()
    expected_principalization[middle] -= 1
    expected_principalization[0] += 1
    if principalization != expected_principalization:
        raise AssertionError("oriented divisor principalization failed")

    local_parity_checks = 0
    for label in range(1, order):
        if label == middle:
            continue
        expected = 1 if label % 2 == 0 else -1
        if principalization[label] != expected:
            raise AssertionError("nonexceptional local order lost parity")
        local_parity_checks += 1

    alternating_neg = negate_pullback(alternating)
    norm_correction = subtract(
        miller_divisor(order, middle + 1, 1),
        miller_divisor(order, middle, order - 1),
    )
    if add(alternating_neg, norm_correction) != complementary:
        raise AssertionError("involution/complement relation failed")
    if add(alternating, alternating_neg) != subtract(full_miller, norm_correction):
        raise AssertionError("compact involution norm divisor failed")

    shifted = translate_argument(alternating, 2)
    two_step = subtract(shifted, alternating)
    expected_two_step = [0] * order
    expected_two_step[order - 1] += middle + 2
    expected_two_step[order - 2] -= middle + 1
    expected_two_step[1] -= middle
    expected_two_step[0] += middle - 1
    if two_step != expected_two_step:
        raise AssertionError("two-step cocycle divisor failed")
    if divisor_degree(two_step) != 0 or divisor_class(two_step) != 0:
        raise AssertionError("two-step divisor was not principal")

    return {
        "order": order,
        "middle": middle,
        "line_divisor_checks": line_divisor_checks,
        "local_parity_checks": local_parity_checks,
        "alternating_divisor_exact": True,
        "principalization_exact": True,
        "full_miller_partition_exact": True,
        "involution_norm_exact": True,
        "two_step_divisor_exact": True,
        "two_step_support": sum(1 for value in two_step if value),
        "two_step_degree": divisor_degree(two_step),
        "two_step_class": divisor_class(two_step),
    }


def secp256k1_certificate() -> dict[str, object]:
    middle = (SECP_N - 1) // 2
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "middle": middle,
        "alternating_edges": middle,
        "ordinary_miller_scalars": [SECP_N, middle, middle + 1],
        "two_step_divisor_support_points": 4,
        "two_step_scalar_coefficient_bit_length": middle.bit_length(),
        "local_edge_has_logarithmic_addition_chain_description": True,
        "absolute_segment_value_known": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "selected_successor": "UORC056-ALTERNATING-MILLER-SEGMENT-B9",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "uorc056_alternating_miller_primitive_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_ORDERS]
    payload = {
        "package": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056-ALTERNATING-MILLER-PRIMITIVE-B8",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "line_divisor_checks": sum(
                case["line_divisor_checks"] for case in cases
            ),
            "local_parity_checks": sum(
                case["local_parity_checks"] for case in cases
            ),
            "all_alternating_divisors_exact": all(
                case["alternating_divisor_exact"] for case in cases
            ),
            "all_principalizations_exact": all(
                case["principalization_exact"] for case in cases
            ),
            "all_full_miller_partitions_exact": all(
                case["full_miller_partition_exact"] for case in cases
            ),
            "all_involution_norms_exact": all(
                case["involution_norm_exact"] for case in cases
            ),
            "all_two_step_divisors_exact": all(
                case["two_step_divisor_exact"] for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "The oriented half-divisor is exactly the potential of an "
            "alternating product of ordinary Miller edges. Its complement, "
            "involution norm, and two-step translation edge all reduce to "
            "ordinary logarithmic-length Miller divisor data. The remaining "
            "unknown is the absolute endpoint segment value of this public "
            "two-step cocycle."
        ),
        "claim_boundary": [
            "All divisor coefficient identities are exact on the cyclic subgroup.",
            "The replay does not implement or time a generalized Miller evaluator.",
            "The package supplies a compact local cocycle, not its global primitive at an unknown endpoint.",
            "No parity oracle, EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
