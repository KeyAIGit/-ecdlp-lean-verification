#!/usr/bin/env python3
"""Exact arithmetic replay for the H-RPCX rational-DAG degree floor V8.

The paper theorem combines two elementary bounds:

1. An exact nonconstant +/-1 rational decoder on the n-1 nonzero subgroup
   points has pole degree at least (n-1)/2.
2. Starting from x and y on a short Weierstrass curve, whose pole degrees are
   2 and 3, a rational arithmetic DAG with g binary +,-,* gates has pole
   degree at most 3*2^g. Inversion preserves pole degree. Shared nodes are
   charged once, so this is a genuine DAG gate ledger, not a formula-tree
   ledger.

Consequently 3*2^g >= (n-1)/2. For secp256k1 the minimum possible g under
this model is exactly 254.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
PROFILE_ID = "UORC-056-HRPCX-RATIONAL-DAG-DEGREE-FLOOR-V8"
BASE_POLE_DEGREE = 3
TARGET_POLE_DEGREE = (N - 1) // 2


def ceil_log2_ratio(numerator: int, denominator: int) -> int:
    if numerator <= 0 or denominator <= 0:
        raise ValueError("positive inputs required")
    gates = 0
    capacity = denominator
    while capacity < numerator:
        capacity *= 2
        gates += 1
    return gates


def run() -> dict[str, object]:
    minimum_binary_gates = ceil_log2_ratio(TARGET_POLE_DEGREE, BASE_POLE_DEGREE)
    assert minimum_binary_gates == 254
    assert BASE_POLE_DEGREE * (1 << (minimum_binary_gates - 1)) < TARGET_POLE_DEGREE
    assert TARGET_POLE_DEGREE <= BASE_POLE_DEGREE * (1 << minimum_binary_gates)

    budget_table = []
    for base_budget in (1, 2, 3, 4, 8, 16, 256, 65536):
        budget_table.append(
            {
                "charged_initial_pole_budget": base_budget,
                "minimum_binary_gates": ceil_log2_ratio(TARGET_POLE_DEGREE, base_budget),
            }
        )

    return {
        "profile_id": PROFILE_ID,
        "status": "proved_paper_theorem_with_exact_secp_arithmetic",
        "model": {
            "inputs": "public constants and the affine coordinate functions x,y on secp256k1",
            "allowed_unary_gate": "inversion of a nonzero rational function",
            "allowed_binary_gates": ["addition", "subtraction", "multiplication"],
            "cost": "each computed binary DAG node is charged once; shared nodes may be reused",
            "decoder": "one rational function regular on every nonzero subgroup point and equal to exact +/-1 parity",
        },
        "paper_theorem": {
            "decoder_lower_bound": "pole_degree(f) >= (n-1)/2",
            "dag_upper_bound": "pole_degree(f) <= 3*2^g",
            "combined_bound": "g >= ceil(log2((n-1)/6))",
        },
        "secp256k1": {
            "n": N,
            "target_pole_degree": TARGET_POLE_DEGREE,
            "minimum_binary_DAG_gates": minimum_binary_gates,
            "gate_253_capacity": BASE_POLE_DEGREE * (1 << 253),
            "gate_254_capacity": BASE_POLE_DEGREE * (1 << 254),
            "budget_table": budget_table,
        },
        "decision": {
            "rational_DAG_with_at_most_253_binary_gates_can_decode_exact_parity": False,
            "rational_DAG_with_254_or_more_binary_gates_exists": "open",
            "polynomial_time_parity_algorithm_proved": False,
            "practically_fast_parity_algorithm_proved": False,
            "general_arithmetic_circuit_lower_bound_proved": False,
        },
        "claim_boundary": {
            "proved": "a direct rational decoder from x,y needs at least 254 charged binary arithmetic DAG gates",
            "not_proved": [
                "that 254 gates suffice",
                "that any rational parity decoder exists",
                "a lower bound for branch, character, comparison, theta, p-adic, or other nonrational primitives",
                "a lower bound when high-degree precomputed leaves are supplied without charging their construction",
                "nonexistence of a classical polynomial-time parity algorithm",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
