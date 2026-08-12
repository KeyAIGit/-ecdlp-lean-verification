#!/usr/bin/env python3
"""Bounded replay for CANONICAL-MIDPOINT-CIRCULARITY-005.

The program checks only public arithmetic identities on frozen integer ranges.
It accepts no external group point, key, scalar, wallet, or production target.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def verify_binary_splits(k_max: int = 127) -> dict[str, int | bool]:
    candidate_splits_checked = 0
    valid_splits_checked = 0

    for k in range(k_max + 1):
        canonical_midpoint = k // 2
        canonical_bit = k % 2
        assert k == 2 * canonical_midpoint + canonical_bit
        assert k - 2 * canonical_midpoint == canonical_bit

        for midpoint in range(k + 1):
            for bit in (0, 1):
                candidate_splits_checked += 1
                if k == 2 * midpoint + bit:
                    valid_splits_checked += 1
                    assert midpoint == canonical_midpoint
                    assert bit == canonical_bit

    return {
        "k_min": 0,
        "k_max": k_max,
        "candidate_splits_checked": candidate_splits_checked,
        "valid_splits_checked": valid_splits_checked,
        "all_valid_midpoints_are_floor_halves": True,
        "all_valid_corrections_equal_parity": True,
    }


def verify_odd_cycle_halves(n_max: int = 127) -> dict[str, int | bool]:
    odd_orders_checked = 0
    scalar_cases_checked = 0
    odd_branch_corrections_checked = 0
    even_branch_equalities_checked = 0

    for n in range(3, n_max + 1, 2):
        odd_orders_checked += 1
        correction = (n + 1) // 2
        for k in range(n):
            scalar_cases_checked += 1
            bit = k % 2
            canonical_midpoint = k // 2
            public_half = (k + bit * n) // 2

            assert 0 <= public_half < n
            assert 2 * public_half == k + bit * n
            assert (2 * public_half) % n == k
            assert public_half == canonical_midpoint + bit * correction
            assert (public_half == canonical_midpoint) == (bit == 0)

            if bit == 0:
                even_branch_equalities_checked += 1
            else:
                odd_branch_corrections_checked += 1
                assert public_half - canonical_midpoint == correction

    return {
        "odd_n_min": 3,
        "odd_n_max": n_max,
        "odd_orders_checked": odd_orders_checked,
        "scalar_cases_checked": scalar_cases_checked,
        "even_branch_equalities_checked": even_branch_equalities_checked,
        "odd_branch_corrections_checked": odd_branch_corrections_checked,
        "all_public_halves_are_canonical_representatives": True,
        "all_public_halves_double_to_targets_mod_order": True,
        "all_half_corrections_equal_parity_times_half_order": True,
    }


def build_result() -> dict[str, object]:
    return {
        "schema_version": "0.1-untrusted",
        "package": "CANONICAL-MIDPOINT-CIRCULARITY-005",
        "date": "2026-08-12",
        "binary_split": verify_binary_splits(),
        "odd_cycle_half": verify_odd_cycle_halves(),
        "claim_boundary": (
            "Integer and cyclic-index arithmetic only; not an unconditional EDS, "
            "theta, coordinate-circuit, or ECDLP lower bound."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    result = build_result()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
