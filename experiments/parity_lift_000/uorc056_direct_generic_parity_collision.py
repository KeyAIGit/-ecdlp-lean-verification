#!/usr/bin/env python3
"""Exact arithmetic replay for the direct generic parity collision boundary.

The executable accepts no curve, point, key, wallet, scalar target, or runtime
instance. It verifies only finite-field affine-label collision facts on frozen
small prime orders and records a public secp256k1 integer certificate.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

FROZEN_PRIMES = (7, 11, 13, 17, 19, 23, 31)
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def minimum_labels_for_exact_parity(order: int) -> int:
    """Least L with L(L-1) >= order-1."""
    if order < 3 or order % 2 == 0:
        raise ValueError("order must be odd and at least three")
    candidate = (1 + math.isqrt(4 * order - 3)) // 2
    while candidate * (candidate - 1) < order - 1:
        candidate += 1
    while candidate > 0 and (candidate - 1) * (candidate - 2) >= order - 1:
        candidate -= 1
    return candidate


def run_affine_case(order: int) -> dict[str, object]:
    if not all(order % divisor for divisor in range(2, math.isqrt(order) + 1)):
        raise ValueError("frozen order must be prime")

    forms = [(slope, intercept) for slope in range(order) for intercept in range(order)]
    distinct_slope_pairs = 0
    parallel_pairs = 0
    verified_collision_solutions = 0

    for (a, b), (c, d) in itertools.combinations(forms, 2):
        if a == c:
            if b == d:
                raise AssertionError("distinct forms unexpectedly identical")
            for scalar in range(order):
                if (a * scalar + b - c * scalar - d) % order == 0:
                    raise AssertionError("parallel distinct forms collided")
            parallel_pairs += 1
            continue

        scalar = (d - b) * pow((a - c) % order, -1, order) % order
        if (a * scalar + b - c * scalar - d) % order != 0:
            raise AssertionError("computed affine collision is not a solution")
        for other in range(order):
            equality = (a * other + b - c * other - d) % order == 0
            if equality != (other == scalar):
                raise AssertionError("affine equality did not have a unique solution")
        distinct_slope_pairs += 1
        verified_collision_solutions += 1

    half = (order - 1) // 2
    even_nonzero = [scalar for scalar in range(1, order) if scalar % 2 == 0]
    odd_nonzero = [scalar for scalar in range(1, order) if scalar % 2 == 1]
    if len(even_nonzero) != half or len(odd_nonzero) != half:
        raise AssertionError("canonical nonzero parity classes are not balanced")

    labels = minimum_labels_for_exact_parity(order)
    if labels * (labels - 1) < order - 1:
        raise AssertionError("declared threshold has insufficient collision capacity")
    if (labels - 1) * (labels - 2) >= order - 1:
        raise AssertionError("declared threshold is not minimal")

    return {
        "order": order,
        "affine_forms": len(forms),
        "unordered_distinct_form_pairs": len(forms) * (len(forms) - 1) // 2,
        "distinct_slope_pairs": distinct_slope_pairs,
        "parallel_distinct_pairs": parallel_pairs,
        "unique_collision_solutions_verified": verified_collision_solutions,
        "nonzero_even_scalars": len(even_nonzero),
        "nonzero_odd_scalars": len(odd_nonzero),
        "balanced_half": half,
        "minimum_exact_labels": labels,
        "previous_label_count_fails": (labels - 1) * (labels - 2) < order - 1,
        "threshold_label_count_succeeds_capacity": labels * (labels - 1) >= order - 1,
    }


def secp256k1_certificate() -> dict[str, object]:
    order = SECP_N
    labels = minimum_labels_for_exact_parity(order)
    previous = labels - 1
    exact_capacity = labels * (labels - 1)
    previous_capacity = previous * (previous - 1)
    if labels != 1 << 128:
        raise AssertionError("unexpected secp256k1 exact label threshold")
    return {
        "n": order,
        "n_bit_length": order.bit_length(),
        "nonzero_parity_class_size": (order - 1) // 2,
        "exact_generic_label_lower_bound": labels,
        "exact_generic_label_lower_bound_power": "2^128",
        "lower_bound_bit_length": labels.bit_length(),
        "threshold_capacity": exact_capacity,
        "threshold_capacity_excess": exact_capacity - (order - 1),
        "previous_label_count": previous,
        "previous_capacity": previous_capacity,
        "previous_capacity_deficit": (order - 1) - previous_capacity,
        "exact_threshold_verified": previous_capacity < order - 1 <= exact_capacity,
        "uniform_success_bound": (
            "success <= 1/2 + L(L-1)/(2(n-1)) on uniform nonzero scalar"
        ),
        "exactness_condition": "L(L-1) >= n-1",
        "full_cost_interpretation": (
            "all distinct generic labels materialized in preprocessing, advice, "
            "memory, or online group operations are charged"
        ),
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "coordinate_specific_evaluator_ruled_out": False,
        "public_parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cases = [run_affine_case(order) for order in FROZEN_PRIMES]
    aggregate = {
        "cases": len(cases),
        "total_affine_forms": sum(case["affine_forms"] for case in cases),
        "total_unordered_form_pairs": sum(
            case["unordered_distinct_form_pairs"] for case in cases
        ),
        "total_unique_collision_solutions": sum(
            case["unique_collision_solutions_verified"] for case in cases
        ),
        "all_parity_classes_balanced": all(
            case["nonzero_even_scalars"] == case["nonzero_odd_scalars"]
            for case in cases
        ),
        "all_affine_pairs_have_at_most_one_collision": all(
            case["distinct_slope_pairs"]
            == case["unique_collision_solutions_verified"]
            for case in cases
        ),
        "all_exact_thresholds_minimal": all(
            case["previous_label_count_fails"]
            and case["threshold_label_count_succeeds_capacity"]
            for case in cases
        ),
    }
    payload = {
        "package": "UORC056-DIRECT-GENERIC-PARITY-COLLISION-E1",
        "model": (
            "prime-order generic cyclic group; deterministic no-collision path; "
            "computed encodings represented by distinct affine forms a*k+b"
        ),
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Every exact generic parity evaluator must materialize at least L "
            "distinct affine labels with L(L-1)>=n-1. For secp256k1 the exact "
            "integer threshold is L=2^128. This is a direct parity bound and "
            "does not apply to non-generic coordinate/CM circuits."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
