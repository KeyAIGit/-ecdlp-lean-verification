#!/usr/bin/env python3
"""Exact replay for the direct generic parity collision boundary.

No curve, point, key, wallet, unknown scalar, or runtime target is accepted.
The replay exhausts affine labels over frozen small prime fields and records
public integer certificates for secp256k1.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

FROZEN_PRIMES = (7, 11, 13, 17, 19, 23, 31)
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def minimum_labels(order: int) -> int:
    """Least L such that L(L-1) >= order-1."""
    candidate = (1 + math.isqrt(4 * order - 3)) // 2
    while candidate * (candidate - 1) < order - 1:
        candidate += 1
    while candidate > 0 and (candidate - 1) * (candidate - 2) >= order - 1:
        candidate -= 1
    return candidate


def minimum_online_labels(order: int, stored: int) -> int:
    """Least T such that T(2S+T-1) >= order-1."""
    linear = 2 * stored - 1
    discriminant = linear * linear + 4 * (order - 1)
    candidate = max(0, (-linear + math.isqrt(discriminant)) // 2)
    while candidate * (2 * stored + candidate - 1) < order - 1:
        candidate += 1
    while candidate > 0:
        previous = (candidate - 1) * (2 * stored + candidate - 2)
        if previous < order - 1:
            break
        candidate -= 1
    return candidate


def run_case(order: int) -> dict[str, object]:
    forms = [(a, b) for a in range(order) for b in range(order)]
    distinct_slope_pairs = 0
    parallel_pairs = 0

    for (a, b), (c, d) in itertools.combinations(forms, 2):
        if a == c:
            if b == d:
                raise AssertionError("distinct forms were identical")
            if any((a * k + b - c * k - d) % order == 0 for k in range(order)):
                raise AssertionError("parallel distinct forms collided")
            parallel_pairs += 1
            continue

        root = (d - b) * pow((a - c) % order, -1, order) % order
        solutions = [
            k for k in range(order)
            if (a * k + b - c * k - d) % order == 0
        ]
        if solutions != [root]:
            raise AssertionError("affine collision was not unique")
        distinct_slope_pairs += 1

    half = (order - 1) // 2
    even = sum(k % 2 == 0 for k in range(1, order))
    odd = sum(k % 2 == 1 for k in range(1, order))
    if even != half or odd != half:
        raise AssertionError("nonzero parity classes were not balanced")

    labels = minimum_labels(order)
    if not ((labels - 1) * (labels - 2) < order - 1 <= labels * (labels - 1)):
        raise AssertionError("exact label threshold failed")

    tradeoff_checks = 0
    for stored in range(labels + 1):
        online = minimum_online_labels(order, stored)
        capacity = online * (2 * stored + online - 1)
        previous = 0 if online == 0 else (online - 1) * (2 * stored + online - 2)
        if not (previous < order - 1 <= capacity):
            raise AssertionError("preprocessing-online threshold failed")
        if (stored + online) ** 2 < order - 1:
            raise AssertionError("total square-root implication failed")
        tradeoff_checks += 1

    return {
        "order": order,
        "affine_forms": len(forms),
        "unordered_distinct_form_pairs": len(forms) * (len(forms) - 1) // 2,
        "distinct_slope_pairs": distinct_slope_pairs,
        "parallel_distinct_pairs": parallel_pairs,
        "unique_collision_solutions_verified": distinct_slope_pairs,
        "nonzero_even_scalars": even,
        "nonzero_odd_scalars": odd,
        "minimum_exact_labels": labels,
        "preprocessing_online_tradeoff_checks": tradeoff_checks,
        "exact_threshold_minimal": True,
    }


def secp_certificate() -> dict[str, object]:
    order = SECP_N
    labels = minimum_labels(order)
    previous = labels - 1
    if labels != 2 ** 128:
        raise AssertionError("unexpected secp256k1 threshold")

    examples: dict[str, object] = {}
    for exponent in (0, 64, 96, 112, 120, 127, 128, 129, 160, 192, 224, 255):
        stored = 0 if exponent == 0 else 2 ** exponent
        online = minimum_online_labels(order, stored)
        capacity = online * (2 * stored + online - 1)
        prior = 0 if online == 0 else (online - 1) * (2 * stored + online - 2)
        examples["0" if exponent == 0 else f"2^{exponent}"] = {
            "stored_labels": stored,
            "minimum_online_labels": online,
            "total_labels": stored + online,
            "tradeoff_verified": prior < order - 1 <= capacity,
        }

    return {
        "n": order,
        "n_bit_length": order.bit_length(),
        "nonzero_parity_class_size": (order - 1) // 2,
        "exact_generic_label_lower_bound": labels,
        "exact_generic_label_lower_bound_power": "2^128",
        "threshold_capacity": labels * (labels - 1),
        "threshold_capacity_excess": labels * (labels - 1) - (order - 1),
        "previous_label_count": previous,
        "previous_capacity": previous * (previous - 1),
        "previous_capacity_deficit": (order - 1) - previous * (previous - 1),
        "exact_threshold_verified": (
            previous * (previous - 1) < order - 1 <= labels * (labels - 1)
        ),
        "uniform_success_bound": (
            "success <= 1/2 + L(L-1)/(2(n-1))"
        ),
        "exactness_condition": "L(L-1) >= n-1",
        "preprocessing_online_condition": "T(2S+T-1) >= n-1",
        "preprocessing_online_examples": examples,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "coordinate_specific_evaluator_ruled_out": False,
        "public_parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_PRIMES]
    aggregate = {
        "cases": len(cases),
        "total_affine_forms": sum(case["affine_forms"] for case in cases),
        "total_unordered_form_pairs": sum(
            case["unordered_distinct_form_pairs"] for case in cases
        ),
        "total_unique_collision_solutions": sum(
            case["unique_collision_solutions_verified"] for case in cases
        ),
        "total_preprocessing_online_tradeoff_checks": sum(
            case["preprocessing_online_tradeoff_checks"] for case in cases
        ),
        "all_parity_classes_balanced": all(
            case["nonzero_even_scalars"] == case["nonzero_odd_scalars"]
            for case in cases
        ),
        "all_affine_pairs_have_at_most_one_collision": True,
        "all_exact_thresholds_minimal": all(
            case["exact_threshold_minimal"] for case in cases
        ),
    }
    payload = {
        "package": "UORC056-DIRECT-GENERIC-PARITY-COLLISION-E1",
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp_certificate(),
        "decision": (
            "Exact generic parity needs L(L-1)>=n-1; with S stored and T "
            "online labels it needs T(2S+T-1)>=n-1. The exact secp256k1 "
            "label threshold without preprocessing is 2^128."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
