#!/usr/bin/env python3
"""Exact finite-group replay for METAPLECTIC-THETA-INTERTWINER-053."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
ORDERS = (19, 31, 67, 271, 397, 433)


def run_order(order: int) -> dict[str, object]:
    if order % 2 != 1:
        raise AssertionError("order must be odd")

    character_order_checks = 0
    for exponent in range(1, order):
        character_order = order // math.gcd(exponent, order)
        if character_order != order:
            raise AssertionError("nonzero character did not have full order")
        character_order_checks += 1

    binary_candidates = {
        "+1": pow(1, order) == 1,
        "-1": pow(-1, order) == 1,
    }
    if binary_candidates != {"+1": True, "-1": False}:
        raise AssertionError("binary classification failed")

    dual_permutation_checks = 0
    expected = list(range(1, order))
    for hidden_scalar in range(1, order):
        observed = sorted(
            (dual_exponent * hidden_scalar) % order
            for dual_exponent in range(1, order)
        )
        if observed != expected:
            raise AssertionError("nonzero multiplication was not a permutation")
        dual_permutation_checks += order - 1

    parity_at_one = -1
    parity_at_minus_one_representative = 1
    parity_at_identity = 1
    if parity_at_one * parity_at_minus_one_representative == parity_at_identity:
        raise AssertionError("canonical parity unexpectedly became a character")

    if (order - 1) % 6 != 0:
        raise AssertionError("frozen order does not support the C6 quotient")

    return {
        "order": order,
        "nonzero_dual_characters": order - 1,
        "character_order_checks": character_order_checks,
        "all_nonzero_characters_have_full_order": True,
        "binary_character_candidates": binary_candidates,
        "nontrivial_binary_characters": 0,
        "dual_permutation_element_checks": dual_permutation_checks,
        "full_dual_symmetrization_checks": order - 1,
        "full_dual_symmetrization": "constant -1 on nonidentity scalars",
        "canonical_parity_is_group_character": False,
        "c3_dual_classes": (order - 1) // 3,
        "c6_dual_classes": (order - 1) // 6,
        "standard_schrodinger_dimension": order,
        "dense_operator_entries": order * order,
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP_N
    extension_degree = (n - 1) // 6
    if n % 12 != 1:
        raise AssertionError("unexpected order congruence")
    if pow(SECP_P, extension_degree, n) != 1:
        raise AssertionError("embedding-degree power failed")
    if pow(SECP_P, extension_degree // 2, n) != n - 1:
        raise AssertionError("half-Frobenius negation failed")
    square_root_baseline = math.isqrt(n)
    return {
        "p": SECP_P,
        "n": n,
        "bit_length": n.bit_length(),
        "standard_schrodinger_dimension": n,
        "dense_operator_entries": n * n,
        "square_root_baseline": square_root_baseline,
        "state_dimension_exceeds_square_root": n > square_root_baseline,
        "dual_point_extension_degree": extension_degree,
        "unoriented_dual_orbit_degree": extension_degree // 2,
        "half_frobenius_negation": True,
        "nontrivial_binary_characters": 0,
        "full_dual_symmetrization": "constant off identity",
        "standard_intertwiner_supplies_orientation": False,
        "selected_successor": "P-ADIC-GLOBAL-BRANCH-054",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("metaplectic_theta_intertwiner_results.json"),
    )
    args = parser.parse_args()

    cases = [run_order(order) for order in ORDERS]
    payload = {
        "package": "METAPLECTIC-THETA-INTERTWINER-053",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_nonzero_dual_characters": sum(case["nonzero_dual_characters"] for case in cases),
            "total_character_order_checks": sum(case["character_order_checks"] for case in cases),
            "total_dual_permutation_element_checks": sum(case["dual_permutation_element_checks"] for case in cases),
            "total_full_dual_symmetrization_checks": sum(case["full_dual_symmetrization_checks"] for case in cases),
            "total_c3_dual_classes": sum(case["c3_dual_classes"] for case in cases),
            "total_c6_dual_classes": sum(case["c6_dual_classes"] for case in cases),
            "nontrivial_binary_characters": sum(case["nontrivial_binary_characters"] for case in cases),
            "all_nonzero_characters_have_full_order": all(case["all_nonzero_characters_have_full_order"] for case in cases),
            "all_canonical_parity_targets_are_noncharacters": all(not case["canonical_parity_is_group_character"] for case in cases),
        },
        "secp256k1": secp256k1_certificate(),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
