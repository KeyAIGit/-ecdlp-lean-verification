#!/usr/bin/env python3
"""Exact abstract replay for UORC056 local-cocycle query boundary B18.

No elliptic-curve target, private key, wallet, unknown scalar, or production DLP
input is accepted. Production constants are used only for public cost counts.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from uorc056_oriented_principal_pell_core import SECP_N

CYCLE_ORDERS = (7, 11, 13)
FIELD_PRIME = 101


def inv(value: int) -> int:
    return pow(value % FIELD_PRIME, -1, FIELD_PRIME)


def component_labels(order: int, edge_mask: int) -> list[int]:
    adjacency: list[list[int]] = [[] for _ in range(order)]
    for edge in range(order):
        if edge_mask >> edge & 1:
            target = (edge + 1) % order
            adjacency[edge].append(target)
            adjacency[target].append(edge)

    labels = [-1] * order
    component = 0
    for start in range(order):
        if labels[start] != -1:
            continue
        labels[start] = component
        stack = [start]
        while stack:
            vertex = stack.pop()
            for target in adjacency[vertex]:
                if labels[target] == -1:
                    labels[target] = component
                    stack.append(target)
        component += 1
    return labels


def cocycle(potential: list[int]) -> list[int]:
    order = len(potential)
    return [
        potential[(index + 1) % order] * inv(potential[index]) % FIELD_PRIME
        for index in range(order)
    ]


def build_case(order: int) -> dict[str, object]:
    base_potential = [pow(3, index + 1, FIELD_PRIME) for index in range(order)]
    base_cocycle = cocycle(base_potential)
    if math.prod(base_cocycle) % FIELD_PRIME != 1:
        raise AssertionError("base cyclic norm was not one")

    query_masks = 0
    target_pairs = 0
    disconnected_pairs = 0
    connected_pairs = 0
    gauge_checks = 0
    minimum_queries = {target: order + 1 for target in range(1, order)}

    for edge_mask in range(1 << order):
        query_masks += 1
        labels = component_labels(order, edge_mask)
        query_count = edge_mask.bit_count()
        anchor_component = labels[0]

        for target in range(1, order):
            target_pairs += 1
            if labels[target] == anchor_component:
                connected_pairs += 1
                minimum_queries[target] = min(minimum_queries[target], query_count)
                continue

            disconnected_pairs += 1
            target_component = labels[target]
            gauge = [1] * order
            for vertex in range(order):
                if labels[vertex] == target_component:
                    gauge[vertex] = 2
                elif labels[vertex] != anchor_component:
                    gauge[vertex] = 3
            gauged_potential = [
                gauge[index] * base_potential[index] % FIELD_PRIME
                for index in range(order)
            ]
            gauged_cocycle = cocycle(gauged_potential)

            if gauged_potential[0] != base_potential[0]:
                raise AssertionError("component gauge changed anchor")
            if gauged_potential[target] == base_potential[target]:
                raise AssertionError("component gauge did not change target")
            for edge in range(order):
                if edge_mask >> edge & 1 and gauged_cocycle[edge] != base_cocycle[edge]:
                    raise AssertionError("queried local edge changed under gauge")
            if math.prod(gauged_cocycle) % FIELD_PRIME != 1:
                raise AssertionError("gauged cyclic norm was not one")
            gauge_checks += 1

    expected_minimum = {
        target: min(target, order - target) for target in range(1, order)
    }
    if minimum_queries != expected_minimum:
        raise AssertionError("minimum connecting edge count was not cycle distance")

    return {
        "order": order,
        "query_masks": query_masks,
        "target_pairs": target_pairs,
        "disconnected_pairs": disconnected_pairs,
        "connected_pairs": connected_pairs,
        "gauge_checks": gauge_checks,
        "minimum_queries_by_target": minimum_queries,
        "worst_target_queries": max(minimum_queries.values()),
        "expected_worst_target_queries": (order - 1) // 2,
        "all_component_gauges_indistinguishable": True,
        "minimum_queries_equal_cycle_distance": True,
    }


def secp_certificate() -> dict[str, object]:
    midpoint = (SECP_N - 1) // 2
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "worst_case_local_edge_queries": midpoint,
        "worst_case_local_edge_queries_bit_length": midpoint.bit_length(),
        "all_target_edge_table_minimum": SECP_N - 1,
        "black_box_edge_only_model_is_subroot": False,
        "nonlocal_algebraic_identity_remains_open": True,
        "parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cases = [build_case(order) for order in CYCLE_ORDERS]
    aggregate = {
        "cases": len(cases),
        "query_masks": sum(case["query_masks"] for case in cases),
        "target_pairs": sum(case["target_pairs"] for case in cases),
        "disconnected_pairs": sum(case["disconnected_pairs"] for case in cases),
        "connected_pairs": sum(case["connected_pairs"] for case in cases),
        "gauge_checks": sum(case["gauge_checks"] for case in cases),
        "all_component_gauges_indistinguishable": all(
            case["all_component_gauges_indistinguishable"] for case in cases
        ),
        "all_minimum_queries_equal_cycle_distance": all(
            case["minimum_queries_equal_cycle_distance"] for case in cases
        ),
        "all_worst_targets_are_midpoints": all(
            case["worst_target_queries"] == case["expected_worst_target_queries"]
            for case in cases
        ),
    }
    payload = {
        "package": "UORC056-LOCAL-COCYCLE-QUERY-BOUNDARY-B18",
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp_certificate(),
        "decision": (
            "In the black-box local-cocycle model, queried edge values and one "
            "anchor do not determine a target outside the queried connected "
            "component. A component gauge preserves every queried edge and the "
            "anchor while changing the target. Worst-case propagation on the "
            "odd cycle needs (n-1)/2 local edges. Only a genuinely nonlocal "
            "algebraic identity can escape this boundary."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
