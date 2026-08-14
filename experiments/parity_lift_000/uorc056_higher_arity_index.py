#!/usr/bin/env python3
"""Combinatorial replay for UORC056 HIGHER-ARITY INDEX B5.

No external point, key, wallet, unknown scalar, or production-sized target is
accepted. The screen studies explicit intermediate degrees only.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
FROZEN_ORDERS = (7, 31, 61, 79, 67, 79, 127, 139, 199, 313)


def ceil_sqrt(value: int) -> int:
    root = math.isqrt(value)
    return root if root * root == value else root + 1


def quadratic_root_bound(value: int) -> int:
    """Smallest C with value <= C^2+C."""
    candidate = max(0, (math.isqrt(1 + 4 * value) - 1) // 2)
    while candidate * candidate + candidate < value:
        candidate += 1
    return candidate


def run_case(order: int) -> dict[str, object]:
    half = (order - 1) // 2

    # Root of an arbitrary explicit binary resultant tree. A and B are the
    # represented child degrees, and leftover is evaluated explicitly.
    root_parameter_checks = 0
    best_root_cost = half
    best_root_sizes = (0, 0, half)
    for left_degree in range(half + 1):
        for right_degree in range(half + 1):
            leftover = max(0, half - left_degree * right_degree)
            maximum_state = max(left_degree, right_degree, leftover)
            if half > left_degree * right_degree + leftover:
                raise AssertionError("root coverage failed")
            if half > maximum_state * maximum_state + maximum_state:
                raise AssertionError("root square boundary failed")
            if maximum_state < best_root_cost:
                best_root_cost = maximum_state
                best_root_sizes = (left_degree, right_degree, leftover)
            root_parameter_checks += 1

    proved_root_lower_bound = quadratic_root_bound(half)
    if best_root_cost < proved_root_lower_bound:
        raise AssertionError("root optimum violated proved lower bound")

    # Three leaf sets: after the first elliptic resultant the child degree is
    # A=2ab; the remaining set contributes B=2c. If 4abc covers the target,
    # then A*B covers it and max(A,B)^2 >= M.
    three_set_checks = 0
    best_three_stage_degree: int | None = None
    best_three_sizes: tuple[int, int, int] | None = None
    for size_i in range(1, half + 1):
        for size_j in range(1, half + 1):
            first_stage_degree = 2 * size_i * size_j
            for size_l in range(1, half + 1):
                if 4 * size_i * size_j * size_l < half:
                    continue
                second_input_degree = 2 * size_l
                maximum_degree = max(first_stage_degree, second_input_degree)
                if maximum_degree * maximum_degree < half:
                    raise AssertionError("three-set intermediate bound failed")
                if (
                    best_three_stage_degree is None
                    or maximum_degree < best_three_stage_degree
                ):
                    best_three_stage_degree = maximum_degree
                    best_three_sizes = (size_i, size_j, size_l)
                three_set_checks += 1

    if best_three_stage_degree is None or best_three_sizes is None:
        raise AssertionError("three-set search produced no covering system")
    if best_three_stage_degree < ceil_sqrt(half):
        raise AssertionError("three-set optimum fell below sqrt(M)")

    return {
        "order": order,
        "half_size": half,
        "root_parameter_checks": root_parameter_checks,
        "best_explicit_root_state": best_root_cost,
        "best_explicit_root_sizes": best_root_sizes,
        "proved_root_state_lower_bound": proved_root_lower_bound,
        "three_set_covering_checks": three_set_checks,
        "best_three_stage_degree": best_three_stage_degree,
        "best_three_set_sizes": best_three_sizes,
        "three_set_sqrt_lower_bound": ceil_sqrt(half),
    }


def secp256k1_certificate() -> dict[str, object]:
    half = (SECP_N - 1) // 2
    root_bound = quadratic_root_bound(half)
    no_leftover_bound = ceil_sqrt(half)
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "half_size": half,
        "explicit_root_state_lower_bound": root_bound,
        "no_leftover_child_degree_lower_bound": no_leftover_bound,
        "root_bound_bit_length": root_bound.bit_length(),
        "fixed_exponent_is_one_half": True,
        "does_explicit_higher_arity_tree_meet_subroot": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "selected_successor": "UORC056-TRANSPOSED-KERNEL-EVALUATION-B6",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "uorc056_higher_arity_index_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_ORDERS]
    payload = {
        "package": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056-HIGHER-ARITY-INDEX-B5",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "root_parameter_checks": sum(
                case["root_parameter_checks"] for case in cases
            ),
            "three_set_covering_checks": sum(
                case["three_set_covering_checks"] for case in cases
            ),
            "all_root_bounds_hold": all(
                case["best_explicit_root_state"]
                >= case["proved_root_state_lower_bound"]
                for case in cases
            ),
            "all_three_set_bounds_hold": all(
                case["best_three_stage_degree"]
                >= case["three_set_sqrt_lower_bound"]
                for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Higher-arity leaf decompositions can have cube-root-size leaf "
            "sets, but every explicit hierarchical binary resultant has root "
            "children A,B and residual c with M <= AB+c. If C=max(A,B,c), "
            "then M <= C^2+C, so one represented state remains Omega(sqrt M). "
            "The explicit higher-arity index/resultant architecture therefore "
            "cannot meet a fixed-epsilon sub-square-root cost gate."
        ),
        "claim_boundary": [
            "The inequalities are exact for the declared explicit binary-resultant representation model.",
            "The three-set screen is an exhaustive integer-cardinality replay on the frozen toy orders.",
            "The result does not cover direct sparse multivariate or transposed black-box algorithms.",
            "No parity oracle, EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
