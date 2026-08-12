#!/usr/bin/env python3
"""Bounded replay for STRUCTURED-SEGMENT-PRIMITIVE-004.

The program exhausts directed-cycle checkpoint sets on small orders and verifies
that complete coverage by online offsets `0 <= t < T` implies `n <= S*T`.
It accepts no external group point, key, scalar, wallet, or production target.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


SEED = 20260812


def covered_vertices(n: int, checkpoints: set[int], offsets: int) -> set[int]:
    return {
        (checkpoint + offset) % n
        for checkpoint in checkpoints
        for offset in range(offsets)
    }


def exhaustive_check(n_max: int = 14) -> dict[str, int | bool]:
    subset_offset_pairs_checked = 0
    covering_pairs_checked = 0
    order_offset_instances = 0
    largest_minimum_storage = 0

    for n in range(2, n_max + 1):
        universe = set(range(n))
        for offsets in range(1, n + 1):
            order_offset_instances += 1
            minimum_storage = n + 1
            for mask in range(1 << n):
                checkpoints = {
                    vertex for vertex in range(n) if (mask >> vertex) & 1
                }
                coverage = covered_vertices(n, checkpoints, offsets)
                subset_offset_pairs_checked += 1
                if coverage == universe:
                    covering_pairs_checked += 1
                    assert n <= len(checkpoints) * offsets
                    minimum_storage = min(minimum_storage, len(checkpoints))

            expected = (n + offsets - 1) // offsets
            assert minimum_storage == expected
            largest_minimum_storage = max(
                largest_minimum_storage, minimum_storage
            )

    return {
        "n_min": 2,
        "n_max": n_max,
        "subset_offset_pairs_checked": subset_offset_pairs_checked,
        "covering_pairs_checked": covering_pairs_checked,
        "order_offset_instances": order_offset_instances,
        "all_coverings_satisfy_order_le_storage_times_offsets": True,
        "all_minimum_storage_values_equal_ceiling_order_div_offsets": True,
        "largest_minimum_storage": largest_minimum_storage,
    }


def deterministic_large_check(n_max: int = 127) -> dict[str, int | bool]:
    rng = random.Random(SEED)
    samples_checked = 0
    covering_samples = 0

    for n in range(15, n_max + 1, 2):
        for offsets in sorted({1, 2, 3, 4, 5, max(1, n // 4), max(1, n // 2), n}):
            offsets = min(offsets, n)
            for _ in range(100):
                density = rng.random()
                checkpoints = {
                    vertex for vertex in range(n) if rng.random() < density
                }
                coverage = covered_vertices(n, checkpoints, offsets)
                samples_checked += 1
                if len(coverage) == n:
                    covering_samples += 1
                    assert n <= len(checkpoints) * offsets

    return {
        "odd_n_min": 15,
        "odd_n_max": n_max,
        "samples_checked": samples_checked,
        "covering_samples": covering_samples,
        "all_sampled_coverings_passed": True,
        "seed": SEED,
    }


def build_result() -> dict[str, object]:
    return {
        "schema_version": "0.1-untrusted",
        "package": "STRUCTURED-SEGMENT-PRIMITIVE-004",
        "date": "2026-08-12",
        "exact_exhaustive": exhaustive_check(),
        "deterministic_large_samples": deterministic_large_check(),
        "claim_boundary": (
            "Directed checkpoint-plus-local-offset coverage only; not a general "
            "EDS, theta, coordinate-circuit, or ECDLP lower bound."
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
