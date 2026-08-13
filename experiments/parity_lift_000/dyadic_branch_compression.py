#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def run_order(order: int) -> dict[str, object]:
    if order < 5 or order % 2 == 0:
        raise AssertionError("order must be odd and at least five")

    depth_results: list[dict[str, object]] = []
    scalar_checks = 0
    wrong_branch_checks = 0
    correction_pair_checks = 0

    depth = 1
    while 1 << depth < order:
        two_power = 1 << depth
        inverse = pow(two_power, -1, order)
        corrections = [inverse * residue % order for residue in range(two_power)]

        if len(set(corrections)) != two_power:
            raise AssertionError("dyadic corrections were not distinct")

        for left in range(two_power):
            for right in range(left + 1, two_power):
                if corrections[left] == corrections[right]:
                    raise AssertionError("distinct residues produced one correction")
                correction_pair_checks += 1

        for scalar in range(order):
            quotient, residue = divmod(scalar, two_power)
            public_half = inverse * scalar % order
            corrected = (public_half - corrections[residue]) % order
            if corrected != quotient:
                raise AssertionError("correct residue failed to recover canonical quotient")
            scalar_checks += 1

            for wrong_residue in range(two_power):
                if wrong_residue == residue:
                    continue
                wrong_candidate = (public_half - corrections[wrong_residue]) % order
                if wrong_candidate == quotient:
                    raise AssertionError("an incorrect dyadic branch recovered the quotient")
                wrong_branch_checks += 1

        depth_results.append(
            {
                "depth": depth,
                "two_power": two_power,
                "branch_states": two_power,
                "inverse_two_power_mod_order": inverse,
                "scalar_checks": order,
                "wrong_branch_checks": order * (two_power - 1),
                "corrections_distinct": True,
            }
        )
        depth += 1

    return {
        "order": order,
        "depths": depth_results,
        "depth_count": len(depth_results),
        "scalar_checks": scalar_checks,
        "wrong_branch_checks": wrong_branch_checks,
        "correction_pair_checks": correction_pair_checks,
    }


def secp_certificate() -> dict[str, object]:
    n = SECP_N
    sqrt_n = math.isqrt(n - 1) + 1
    depths = [64, 96, 128, 129, 192, 255]
    rows = []
    for depth in depths:
        branch_states = 1 << depth
        if branch_states >= n:
            raise AssertionError("selected secp depth must satisfy 2^d<n")
        rows.append(
            {
                "depth": depth,
                "branch_states": branch_states,
                "relative_to_pollard": branch_states / sqrt_n,
            }
        )
    if sqrt_n != 1 << 128:
        raise AssertionError("unexpected secp square-root ceiling")
    return {
        "n": n,
        "bit_length": n.bit_length(),
        "ceil_sqrt_n": sqrt_n,
        "pollard_depth": 128,
        "branch_states_at_pollard_depth": 1 << 128,
        "first_depth_above_pollard": 129,
        "depth_rows": rows,
        "selected_successor": "NONLINEAR-DYADIC-SELECTOR-044",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("dyadic_branch_compression_results.json"),
    )
    args = parser.parse_args()

    orders = [run_order(order) for order in range(5, 128, 2)]
    payload = {
        "package": "DYADIC-BRANCH-COMPRESSION-043",
        "orders": orders,
        "aggregate": {
            "orders": len(orders),
            "total_depths": sum(case["depth_count"] for case in orders),
            "total_scalar_checks": sum(case["scalar_checks"] for case in orders),
            "total_wrong_branch_checks": sum(case["wrong_branch_checks"] for case in orders),
            "total_correction_pair_checks": sum(
                case["correction_pair_checks"] for case in orders
            ),
            "all_corrections_distinct": True,
            "all_correct_branches_recover_quotient": True,
            "all_wrong_branches_rejected": True,
        },
        "secp256k1": secp_certificate(),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
