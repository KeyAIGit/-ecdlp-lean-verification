#!/usr/bin/env python3
"""Replay an elementary implicit characterization of odd-cycle parity.

This is deliberately not classified as an algorithmic compression result.  It checks
that a constant-size local equation uniquely defines the alternating word on an odd
cycle, while random-access evaluation at an elliptic-curve point remains open.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from uorc056_hrpcx_pole_degree_barrier_v2 import FROZEN, point_add


PROFILE_ID = "UORC-056-HRPCX-COMPACT-SPECIFICATION-GAP-V4"


def check_curve(curve) -> dict[str, object]:
    p, n = curve.p, curve.n
    generator = (curve.gx, curve.gy)

    points = [None]
    current = None
    for _ in range(1, n):
        current = point_add(current, generator, p)
        if current is None:
            raise AssertionError((curve.name, "early orbit closure"))
        points.append(current)
    if point_add(points[-1], generator, p) is not None:
        raise AssertionError((curve.name, "orbit did not close"))

    values = [1 if k % 2 == 0 else p - 1 for k in range(n)]
    point_to_index = {point: index for index, point in enumerate(points)}
    local_checks = 0
    for index, point in enumerate(points):
        predecessor = point_add(point, (generator[0], (-generator[1]) % p), p)
        predecessor_index = point_to_index[predecessor]
        left = (values[index] + values[predecessor_index]) % p
        expected = 2 % p if point is None else 0
        if left != expected:
            raise AssertionError((curve.name, index, left, expected))
        local_checks += 1

    # Non-wrap equations force alternation.  The odd wrap equation fixes f(O)=1.
    reconstructed = [0] * n
    reconstructed[0] = 1
    for index in range(1, n):
        reconstructed[index] = (-reconstructed[index - 1]) % p
    if (reconstructed[0] + reconstructed[-1]) % p != 2 % p:
        raise AssertionError((curve.name, "wrap equation failed"))
    if reconstructed != values:
        raise AssertionError((curve.name, "unique solution mismatch"))

    return {
        "name": curve.name,
        "p": p,
        "n": n,
        "local_equations_checked": local_checks,
        "unique_solution_verified": True,
        "solution": "f([k]G)=(-1)^k",
    }


def run() -> dict[str, object]:
    checks = [check_curve(curve) for curve in FROZEN]
    return {
        "profile_id": PROFILE_ID,
        "status": "proved_elementary_implicit_characterization",
        "theorem": {
            "public_equation": "(I+T)f=2*delta_O",
            "solution": "f([k]G)=(-1)^k",
            "uniqueness": "odd-cycle wrap fixes the alternating recurrence",
        },
        "checks": checks,
        "aggregate": {
            "curves": len(checks),
            "equations": sum(check["local_equations_checked"] for check in checks),
            "uniqueness_failures": sum(not check["unique_solution_verified"] for check in checks),
        },
        "decision": {
            "constant_size_implicit_equation_exists": True,
            "equation_is_an_elementary_restatement_of_canonical_parity": True,
            "algorithmic_compression_proved": False,
            "polynomial_time_parity_algorithm_proved": False,
            "polylog_random_access_evaluator_found": False,
            "direct_local_propagation_cost": "Theta(n) worst case",
            "specification_is_hrpcx_solution": False,
            "standalone_algorithmic_significance": "none without a random-access solver",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
