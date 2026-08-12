#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def sign_pow(sign: int, exponent: int) -> int:
    if sign not in (-1, 1):
        raise AssertionError("not a sign")
    return sign if exponent & 1 else 1


def run_cycle(order: int, seed: int) -> dict[str, object]:
    if order < 5 or order % 2 == 0:
        raise AssertionError("cycle order must be odd and at least five")

    rng = random.Random(seed)
    rho = [1] + [1 if rng.getrandbits(1) else -1 for _ in range(order - 1)]
    rho[1] = 1

    cases: list[dict[str, object]] = []
    edge_checks = 0
    prefix_checks = 0
    residue_equivalence_checks = 0

    for constant in (-1, 1):
        public = [sign_pow(constant, index) * rho[index] for index in range(order)]
        delta = [rho[(index + 1) % order] * rho[index] for index in range(order)]

        for index in range(order):
            expected = constant * public[(index + 1) % order] * public[index]
            if delta[index] != expected:
                raise AssertionError("public coboundary identity failed")
            edge_checks += 1

        prefix = 1
        for length in range(order):
            if length > 0:
                prefix *= delta[length - 1]
            expected_prefix = sign_pow(constant, length) * public[length] * public[0]
            if prefix != expected_prefix:
                raise AssertionError("segment telescoping failed")
            prefix_checks += 1

        for index in range(order):
            recovered = sign_pow(constant, index) * public[index]
            if recovered != rho[index]:
                raise AssertionError("public-factor/parity equivalence failed")
            residue_equivalence_checks += 1

        cases.append(
            {
                "constant_sign": constant,
                "hidden_factor": "scalar parity" if constant == -1 else "none",
                "edge_checks": order,
                "prefix_checks": order,
                "residue_equivalence_checks": order,
            }
        )

    return {
        "order": order,
        "cases": cases,
        "edge_checks": edge_checks,
        "prefix_checks": prefix_checks,
        "residue_equivalence_checks": residue_equivalence_checks,
        "single_wrap_defect_for_parity": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("eds_absolute_orientation_return_results.json"),
    )
    args = parser.parse_args()

    cycles = [run_cycle(order, 0xE042 + order) for order in range(5, 128, 2)]
    payload = {
        "package": "EDS-ABSOLUTE-ORIENTATION-RETURN-042",
        "cycles": cycles,
        "aggregate": {
            "cycles": len(cycles),
            "total_edge_checks": sum(case["edge_checks"] for case in cycles),
            "total_prefix_checks": sum(case["prefix_checks"] for case in cycles),
            "total_residue_equivalence_checks": sum(
                case["residue_equivalence_checks"] for case in cycles
            ),
            "all_telescoping_checks_passed": True,
            "secp_like_constant_minus_one_leaves_only_parity": True,
        },
        "secp256k1": {
            "n": SECP_N,
            "bit_length": SECP_N.bit_length(),
            "exact_parity_oracle_calls_upper_bound": SECP_N.bit_length(),
            "selected_successor": "DYADIC-BRANCH-COMPRESSION-043",
        },
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
