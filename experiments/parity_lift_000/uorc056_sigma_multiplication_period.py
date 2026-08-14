#!/usr/bin/env python3
"""Exact cyclic replay for UORC056 SIGMA MULTIPLICATION PERIOD B10.

Only frozen public prime orders are used. No curve point, key, wallet, or
unknown scalar is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
FROZEN_ORDERS = (7, 31, 61, 79, 67, 79, 127, 139, 199, 313)


def translation_orbit(order: int, step: int) -> list[int]:
    result: list[int] = []
    current = 0
    while current not in result:
        result.append(current)
        current = (current + step) % order
    return result


def run_case(order: int) -> dict[str, object]:
    if order % 2 == 0:
        raise AssertionError("order must be odd")
    middle = (order - 1) // 2
    odd_half = set(range(1, order, 2))
    even_half = set(range(2, order, 2))
    if len(odd_half) != middle or len(even_half) != middle:
        raise AssertionError("half cardinality failed")
    if odd_half & even_half or odd_half | even_half != set(range(1, order)):
        raise AssertionError("parity halves did not partition nonzero labels")

    translation_checks = 0
    full_orbit_checks = 0
    for step in range(1, order):
        orbit = translation_orbit(order, step)
        if len(orbit) != order:
            raise AssertionError("nonzero translation had a proper orbit")
        full_orbit_checks += 1
        shifted_odd = {(label + step) % order for label in odd_half}
        shifted_even = {(label + step) % order for label in even_half}
        if shifted_odd == odd_half or shifted_even == even_half:
            raise AssertionError("parity half had a nontrivial stabilizer")
        translation_checks += 2

    step_two_orbit = translation_orbit(order, 2)
    if len(step_two_orbit) != order or math.gcd(2, order) != 1:
        raise AssertionError("two-step traversal was not full")

    # Neither half plus the identity is closed under addition, except the tiny
    # degenerate order where the check is still explicit.
    odd_with_zero = odd_half | {0}
    even_with_zero = even_half | {0}
    odd_closed = all((a + b) % order in odd_with_zero for a in odd_with_zero for b in odd_with_zero)
    even_closed = all((a + b) % order in even_with_zero for a in even_with_zero for b in even_with_zero)
    if odd_closed or even_closed:
        raise AssertionError("a parity half accidentally formed a subgroup")

    return {
        "order": order,
        "middle": middle,
        "nonzero_translation_steps": order - 1,
        "translation_stabilizer_rejections": translation_checks,
        "full_orbit_checks": full_orbit_checks,
        "step_two_orbit_length": len(step_two_orbit),
        "odd_half_is_not_subgroup": True,
        "even_half_is_not_subgroup": True,
        "translation_stabilizer_is_trivial": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    middle = (SECP_N - 1) // 2
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "half_size": middle,
        "proper_nontrivial_subgroups": 0,
        "step_two_orbit_length": SECP_N,
        "standard_sigma_subgroup_product": "full kernel or trivial subgroup only",
        "full_kernel_product_selects_orientation": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "b_track_open_problem": "endpoint-only nonlinear alternating-Miller evaluation",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "uorc056_sigma_multiplication_period_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_ORDERS]
    payload = {
        "package": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056-SIGMA-MULTIPLICATION-PERIOD-B10",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "translation_stabilizer_rejections": sum(
                case["translation_stabilizer_rejections"] for case in cases
            ),
            "full_orbit_checks": sum(
                case["full_orbit_checks"] for case in cases
            ),
            "all_stabilizers_trivial": all(
                case["translation_stabilizer_is_trivial"] for case in cases
            ),
            "all_step_two_orbits_full": all(
                case["step_two_orbit_length"] == case["order"]
                for case in cases
            ),
            "all_halves_not_subgroups": all(
                case["odd_half_is_not_subgroup"]
                and case["even_half_is_not_subgroup"]
                for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "On every prime-order cycle, each nonzero translation generates "
            "the full cycle, while either parity half has intermediate size. "
            "The alternating half therefore has trivial translation stabilizer "
            "and is not a proper subgroup orbit or coset union available to a "
            "standard lower-period sigma multiplication formula. The only "
            "nontrivial subgroup product is the full generator-blind kernel norm."
        ),
        "claim_boundary": [
            "The cyclic orbit and stabilizer statements are exact.",
            "The closure concerns standard subgroup/orbit multiplication formulas.",
            "It does not exclude a nonperiodic endpoint identity or arbitrary nonlinear circuit.",
            "No parity oracle, EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
