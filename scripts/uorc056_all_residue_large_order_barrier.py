#!/usr/bin/env python3
"""Exact arithmetic replay for UORC-056 all-residue barrier V11.

Mathematical input (source-locked in the V11 note): Shparlinski--Stange
Lemma 5 bounds every subgroup Fourier coefficient of chi(psi_3) by 8*sqrt(p).
Fourier completion then forces every all-residue generator of prime order n to
satisfy

    floor((n-1)/3) <= 8*sqrt(p)*(2 + ln((n-1)/2)).

For secp256k1, n<2^256 and ln(2)<1 give the deliberately coarse necessary
condition

    floor((n-1)/3) <= 2064*sqrt(p).

This script certifies the negation of that condition using integers only.  It
also replays the two small exact EDS-decimation witnesses from V10 and confirms
that they lie below the large-order obstruction.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from uorc056_eds_decimation_closure import EXACT_DECIMATION_EXAMPLES, exact_decimation_record

PROFILE_ID = "UORC-056-ALL-RESIDUE-LARGE-ORDER-BARRIER-V11"
DEFAULT_OUTPUT = Path("experiments/uorc056/all_residue_large_order_barrier_results.json")

SECP256K1_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16
)
SECP256K1_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)

PSI3_FUNCTION_DEGREE = 4
FOURIER_COEFFICIENT_CONSTANT = 2 * PSI3_FUNCTION_DEGREE  # 8
COARSE_LOG_UPPER = 258  # 2 + ln((n-1)/2) < 2 + 256
COARSE_COMPLETION_CONSTANT = FOURIER_COEFFICIENT_CONSTANT * COARSE_LOG_UPPER  # 2064


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def necessary_block_length(order: int) -> int:
    if order < 5 or order % 2 == 0:
        raise ValueError("expected odd order at least five")
    return (order - 1) // 3


def harmonic_number(n: int) -> float:
    if n <= 0:
        return 0.0
    return math.fsum(1.0 / k for k in range(1, n + 1))


def exact_secp_certificate() -> dict[str, Any]:
    p = SECP256K1_P
    n = SECP256K1_N
    block = necessary_block_length(n)
    c = COARSE_COMPLETION_CONSTANT
    left_square = block * block
    right_square = c * c * p
    if not left_square > right_square:
        raise AssertionError("secp large-order certificate unexpectedly failed")

    ratio_floor = left_square // right_square
    # This float is descriptive only; the proof certificate is the integer comparison.
    log2_margin = (
        math.log2(block)
        - math.log2(c)
        - 0.5 * math.log2(p)
    )
    return {
        "p": str(p),
        "n": str(n),
        "n_bits": n.bit_length(),
        "p_bits": p.bit_length(),
        "block_N_floor_n_minus_1_over_3": str(block),
        "block_bits": block.bit_length(),
        "psi3_function_degree": PSI3_FUNCTION_DEGREE,
        "published_fourier_bound": "abs(a_hat(r)) <= 8*sqrt(p)",
        "completion_bound": "N <= 8*sqrt(p)*(2+ln((n-1)/2))",
        "coarse_log_fact": "n < 2^256 and ln(2)<1 imply 2+ln((n-1)/2) < 258",
        "coarse_completion_constant": c,
        "coarse_necessary_bound": "N <= 2064*sqrt(p)",
        "integer_certificate": "N^2 > 2064^2*p",
        "constant_square": c * c,
        "left_square": str(left_square),
        "right_square": str(right_square),
        "certificate_holds": True,
        "squared_ratio_floor": str(ratio_floor),
        "log2_ratio_margin_descriptive": f"{log2_margin:.12f}",
    }


def small_witness_consistency() -> list[dict[str, Any]]:
    rows = []
    for data in EXACT_DECIMATION_EXAMPLES:
        witness = exact_decimation_record(*data)
        p = int(witness["p"])
        n = int(witness["n"])
        block = necessary_block_length(n)
        # For tiny n, compute the actual completion RHS only as a descriptive check.
        rhs = 8.0 * math.sqrt(p) * (2.0 + math.log((n - 1) / 2.0))
        if not block <= rhs:
            raise AssertionError("small exact witness should not violate V11 necessary bound")
        rows.append(
            {
                "p": p,
                "n": n,
                "m": int(witness["m"]),
                "block_N": block,
                "completion_rhs_descriptive": f"{rhs:.12f}",
                "necessary_bound_holds": True,
                "exact_parity_decimation": True,
            }
        )
    return rows


def run() -> dict[str, Any]:
    secp = exact_secp_certificate()
    small = small_witness_consistency()
    return {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "theorem_input": {
            "fixed_probe": "psi_3",
            "degree": PSI3_FUNCTION_DEGREE,
            "subgroup_character_sum_bound": "2*d*sqrt(p)=8*sqrt(p)",
            "all_residue_implication": (
                "for N=floor((n-1)/3), chain rule forces "
                "chi(psi_3([k]P))=1 for 1<=k<=N"
            ),
            "completion_l1_bound": (
                "(1/n)*sum_r |D_N(r)| <= 1+H_((n-1)/2) "
                "<= 2+ln((n-1)/2)"
            ),
        },
        "secp256k1": secp,
        "small_exact_witness_consistency": small,
        "decision": "secp256k1_has_no_all_residue_generator_of_order_n",
        "combined_with_v10": (
            "no even m can make chi(psi_m([k]G)) equal canonical parity on secp256k1"
        ),
        "combined_with_v9": (
            "the pure single classical division-polynomial quadratic-character family "
            "is closed for secp256k1 at every index m"
        ),
        "scientific_boundary": (
            "This is not an unrestricted circuit lower bound and does not close the "
            "direct field-valued Y_G evaluator."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run())
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("V11 all-residue barrier artifact drift")
        print("UORC056_ALL_RESIDUE_LARGE_ORDER_BARRIER_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
