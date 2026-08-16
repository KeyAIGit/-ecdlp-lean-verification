#!/usr/bin/env python3
"""Machine-readable C42 decision package."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from uorc056_c42_antifrobenius_minor import build_minor_payload
from uorc056_c42_glv_transposed_resultant import build_glv_payload

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def ceil_div(numerator: int, denominator: int) -> int:
    return (numerator + denominator - 1) // denominator


def ceil_sqrt(value: int) -> int:
    root = math.isqrt(value)
    return root if root * root == value else root + 1


def exact_two_level_width(length: int) -> dict[str, int]:
    # For a fixed sum w=b+g, the largest possible product is floor(w^2/4).
    # Hence the optimum is the least w with floor(w^2/4) >= length.
    minimum_width = ceil_sqrt(4 * length)
    baby = minimum_width // 2
    giant = minimum_width - baby
    if baby * giant < length:
        raise AssertionError("two-level width certificate failed")
    if minimum_width > 2:
        previous = minimum_width - 1
        if (previous // 2) * (previous - previous // 2) >= length:
            raise AssertionError("two-level width is not minimal")
    return {
        "length": length,
        "baby_width": baby,
        "giant_count": giant,
        "minimum_width": minimum_width,
    }


def build_payload() -> dict[str, Any]:
    glv = build_glv_payload()
    minor = build_minor_payload()

    half_degree = (SECP_N - 1) // 2
    glv_block = (SECP_N - 1) // 6
    if half_degree != 3 * glv_block:
        raise AssertionError("secp256k1 half degree is not three GLV blocks")
    two_level = exact_two_level_width(glv_block)

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-ORIENTED-TRANSPOSED-RESULTANT-C42",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "predecessor": "C41 incomplete oriented-product compression boundary",
        "glv_relative_norm": glv,
        "antifrobenius_minor": minor,
        "secp256k1_cost_frontier": {
            "n": SECP_N,
            "n_mod_6": SECP_N % 6,
            "half_degree": half_degree,
            "half_degree_bit_length": half_degree.bit_length(),
            "glv_block_degree": glv_block,
            "glv_block_degree_bit_length": glv_block.bit_length(),
            "half_degree_equals_three_blocks": half_degree == 3 * glv_block,
            "ceil_sqrt_glv_block": ceil_sqrt(glv_block),
            "ceil_sqrt_glv_block_bit_length": ceil_sqrt(glv_block).bit_length(),
            "exact_two_level_product_frontier": two_level,
            "ceil_sqrt_group_order": ceil_sqrt(SECP_N),
        },
        "claim_boundary": {
            "proved_or_replayed": [
                "exact target-root localization of the two orbit branches",
                "exact cubic GLV relative-norm factorization on frozen and held-out curves",
                "exact reduction of determinant dimension from (n-1)/2 to (n-1)/6",
                "density of the explicit quotient representation on the declared finite corpus",
                "complete affine quadratic-character screen of the anti-Frobenius 2x2 minor",
                "exact secp256k1 dimension and two-level product arithmetic",
            ],
            "not_claimed": [
                "an unrestricted resultant or arithmetic-circuit lower bound",
                "production secp256k1 coefficient-density theorem",
                "optimality of every transposed-resultant algorithm",
                "a parity oracle",
                "a sub-square-root ECDLP algorithm",
            ],
        },
        "decision": {
            "exact_query_root_localization_found": True,
            "exact_glv_cubic_relative_norm_found": True,
            "glv_reduction_changes_only_the_constant_factor": True,
            "explicit_glv_quotient_representation_is_linear_scale": True,
            "antifrobenius_minor_affine_character_grammar_closed": True,
            "target_dependent_transposed_resultant_bypasses_oriented_root": False,
            "short_subroot_oriented_resultant_evaluator_found": False,
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "aggregate": {
            "curves": int(glv["aggregate"]["curves"]),
            "frozen_curves": int(glv["aggregate"]["frozen"]),
            "heldout_curves": int(glv["aggregate"]["heldout"]),
            "relative_norm_targets": int(
                glv["aggregate"]["relative_norm_targets"]
            ),
            "localized_branch_checks": int(
                glv["aggregate"]["localized_branch_checks"]
            ),
            "antifrobenius_character_candidates": int(
                minor["aggregate"]["candidates"]
            ),
            "antifrobenius_character_survivors": int(
                minor["aggregate"]["survivors"]
            ),
            "errors": int(glv["aggregate"]["errors"])
            + int(minor["aggregate"]["errors"]),
        },
        "successor": {
            "id": "LOCAL-GLV-GAUGE-BREAKING-C43",
            "target": (
                "construct an unsquared, anchor-normalized relation coupling the "
                "three GLV branch values before taking the global norm"
            ),
            "rejection_gate": (
                "a candidate depending only on branch squares, symmetric norms, "
                "or a dense quotient table is not new"
            ),
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = build_payload()
    if args.out:
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("UORC056_ORIENTED_TRANSPOSED_RESULTANT_C42_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
