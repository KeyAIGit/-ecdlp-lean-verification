#!/usr/bin/env python3
"""Exact arithmetic replay for the H-RPCX rational semiconjugacy barrier V7.

The paper theorem is geometric. This replay instantiates the exact secp256k1
degree tradeoff and imports the verified embedding-degree certificate from V6
for the degree-one Mobius branch.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from uorc056_hrpcx_autonomous_linear_state_barrier_v6 import K, N, secp_certificate

PROFILE_ID = "UORC-056-HRPCX-RATIONAL-SEMICONJUGACY-BARRIER-V7"
UPDATE_DEGREES = (2, 3, 4, 8, 16, 32, 64, 128, 256, 1024, 65536)


def ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def run() -> dict[str, object]:
    secp = secp_certificate()
    thresholds = [
        {
            "update_degree_D": degree,
            "minimum_state_map_degree_delta": ceil_div(N, degree + 1),
            "minimum_state_map_degree_bit_length": ceil_div(N, degree + 1).bit_length(),
        }
        for degree in UPDATE_DEGREES
    ]

    return {
        "profile_id": PROFILE_ID,
        "status": "proved_paper_theorem_with_exact_secp_instantiation",
        "model": {
            "state": "one nonconstant projective rational coordinate S:E->P^1 over F_(p^d)",
            "update": "one fixed rational map F:P^1->P^1 of degree D",
            "identity_tested_on": "all n subgroup points",
            "decoder": "arbitrary deterministic decoder",
        },
        "paper_theorem": {
            "finite_to_global": "if n>(D+1)*delta, S(P+G)=F(S(P)) on all subgroup points extends to a global rational identity",
            "global_rigidity": "a global semiconjugacy with translation of order n forces F^n=id and therefore D=1",
            "degree_tradeoff": "for D>=2, exact subgroup semiconjugacy requires (D+1)*delta>=n",
            "degree_one_branch": "for D=1, F is Mobius and V6 forces 2*d>=ord_n(p)",
        },
        "secp256k1": {
            "n": N,
            "embedding_degree_K": K,
            "mobius_extension_degree_lower_bound": (K + 1) // 2,
            "nonlinear_degree_thresholds": thresholds,
        },
        "decision": {
            "one_coordinate_rational_autonomous_state_with_polylog_delta_and_polylog_D_possible": False,
            "degree_one_mobius_over_polylog_extension_possible": False,
            "high_degree_low_DAG_size_state_closed": False,
            "multicoordinate_nonlinear_state_closed": False,
            "query_dependent_random_access_closed": False,
            "general_HPCX_refuted": False,
        },
        "claim_boundary": {
            "proved": "low-degree one-coordinate rational semiconjugacies cannot realize exact secp256k1 parity transport",
            "not_proved": [
                "a circuit lower bound for evaluating a huge-degree state map",
                "no multivariate nonlinear state works",
                "no direct random-access evaluator works",
                "no classical polynomial-time parity algorithm exists",
            ],
        },
        "consistency_checks": {
            "v6_embedding_degree_matches": secp["embedding_degree"] == K,
            "all_thresholds_satisfy_tradeoff": all(
                (item["update_degree_D"] + 1) * item["minimum_state_map_degree_delta"] >= N
                for item in thresholds
            ),
            "all_predecessors_fail_tradeoff": all(
                item["minimum_state_map_degree_delta"] == 0
                or (item["update_degree_D"] + 1) * (item["minimum_state_map_degree_delta"] - 1) < N
                for item in thresholds
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
