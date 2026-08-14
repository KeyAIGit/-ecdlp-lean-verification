#!/usr/bin/env python3
"""Exact divisor replay for UORC056 ALTERNATING MILLER SEGMENT B9.

Only frozen public odd prime orders are used. No curve point, key, wallet, or
unknown scalar is accepted.
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


def alternating_divisor(order: int) -> list[int]:
    result = [0] * order
    for centre in range(1, order, 2):
        result = add(result, line_divisor(order, centre))
    return result


def shift_argument(divisor: list[int], step: int) -> list[int]:
    order = len(divisor)
    return [divisor[(label + step) % order] for label in range(order)]


def negate_pullback(divisor: list[int]) -> list[int]:
    order = len(divisor)
    return [divisor[(-label) % order] for label in range(order)]


def segment_divisor(base: list[int], length: int) -> list[int]:
    return subtract(shift_argument(base, 2 * length), base)


def support_size(divisor: list[int]) -> int:
    return sum(1 for coefficient in divisor if coefficient)


def run_case(order: int) -> dict[str, object]:
    middle = (order - 1) // 2
    base = alternating_divisor(order)
    negated = negate_pullback(base)
    norm = add(base, negated)

    segment_support_checks = 0
    reflected_norm_checks = 0
    for length in range(1, middle + 1):
        segment = segment_divisor(base, length)
        expected_support = min(2 * length + 2, order)
        if support_size(segment) != expected_support:
            raise AssertionError("segment support formula failed")
        segment_support_checks += 1

        reflected = subtract(
            negated,
            shift_argument(negated, 2 * length),
        )
        norm_ratio = subtract(
            shift_argument(norm, 2 * length),
            norm,
        )
        if subtract(segment, reflected) != norm_ratio:
            raise AssertionError("reflected norm quotient identity failed")
        reflected_norm_checks += 1

    composition_checks = 0
    for left_length in range(1, middle + 1):
        for right_length in range(1, middle + 1 - left_length):
            whole = segment_divisor(base, left_length + right_length)
            composed = add(
                segment_divisor(base, left_length),
                shift_argument(
                    segment_divisor(base, right_length),
                    2 * left_length,
                ),
            )
            if whole != composed:
                raise AssertionError("segment composition failed")
            composition_checks += 1

    if segment_divisor(base, order) != [0] * order:
        raise AssertionError("full-cycle segment did not close")

    return {
        "order": order,
        "middle": middle,
        "segment_support_checks": segment_support_checks,
        "composition_checks": composition_checks,
        "reflected_norm_checks": reflected_norm_checks,
        "full_cycle_closure": True,
        "largest_canonical_segment_support": support_size(
            segment_divisor(base, middle)
        ),
        "largest_support_equals_order": (
            support_size(segment_divisor(base, middle)) == order
        ),
    }


def secp256k1_certificate() -> dict[str, object]:
    middle = (SECP_N - 1) // 2
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "middle": middle,
        "midpoint_segment_support": SECP_N,
        "explicit_segment_divisor_is_linear_size": True,
        "compact_norm_determines_only_reflected_quotient": True,
        "endpoint_only_segment_primitive_known": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "handoff": "research/uorc056-endpoint-segment",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "uorc056_alternating_miller_segment_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_ORDERS]
    payload = {
        "package": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056-ALTERNATING-MILLER-SEGMENT-B9",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "segment_support_checks": sum(
                case["segment_support_checks"] for case in cases
            ),
            "composition_checks": sum(
                case["composition_checks"] for case in cases
            ),
            "reflected_norm_checks": sum(
                case["reflected_norm_checks"] for case in cases
            ),
            "all_full_cycles_close": all(
                case["full_cycle_closure"] for case in cases
            ),
            "all_midpoint_supports_saturate": all(
                case["largest_support_equals_order"] for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "The alternating Miller two-step edge has an exact telescoping "
            "segment law, but the explicit segment divisor has support "
            "min(2m+2,n) and reaches the full cycle at the canonical midpoint. "
            "The compact involution norm gives only the quotient between a "
            "segment and its reflected partner. A genuinely endpoint-only "
            "segment primitive remains necessary."
        ),
        "claim_boundary": [
            "All divisor support, composition, norm, and closure identities are exact.",
            "The linear support result applies to explicit divisor-list/product representations.",
            "It does not exclude a new endpoint-only special-function or nonlinear circuit.",
            "No parity oracle, EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
