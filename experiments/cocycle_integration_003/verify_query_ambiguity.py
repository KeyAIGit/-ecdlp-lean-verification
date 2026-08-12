#!/usr/bin/env python3
"""Bounded replay for GENERIC-COCYCLE-INTEGRATION-003.

The script accepts no external group point, scalar, key, wallet, or production
instance. It verifies the elementary two-flip witness and the exact minimum
query-cardinality criterion on finite cycles.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Iterable


SEED = 20260812


def parity(items: set[int]) -> int:
    return len(items) & 1


def two_flip_witness(n: int, k: int, queried: set[int]) -> tuple[int, int] | None:
    """Return opposite-side unqueried edges, or None iff one side is covered."""
    cut = set(range(k))
    complement = set(range(k, n))
    if cut <= queried or complement <= queried:
        return None

    inside = min(cut - queried)
    outside = min(complement - queried)

    baseline: set[int] = set()
    flipped = {inside, outside}
    assert parity(baseline) == parity(flipped)
    assert all((edge in baseline) == (edge in flipped) for edge in queried)
    assert parity(baseline & cut) != parity(flipped & cut)
    return inside, outside


def exhaustive_check(n_max: int = 14) -> dict[str, int | bool]:
    query_sets_checked = 0
    cut_instances = 0
    largest_minimum = 0

    for n in range(2, n_max + 1):
        universe = set(range(n))
        for k in range(1, n):
            cut_instances += 1
            cut = set(range(k))
            complement = universe - cut
            minimum_determining = n + 1

            for mask in range(1 << n):
                queried = {edge for edge in range(n) if (mask >> edge) & 1}
                determines = cut <= queried or complement <= queried
                witness = two_flip_witness(n, k, queried)
                assert (witness is None) == determines
                if determines:
                    minimum_determining = min(minimum_determining, len(queried))
                query_sets_checked += 1

            expected = min(k, n - k)
            assert minimum_determining == expected
            largest_minimum = max(largest_minimum, minimum_determining)

    return {
        "n_min": 2,
        "n_max": n_max,
        "cut_instances": cut_instances,
        "query_sets_checked": query_sets_checked,
        "all_ambiguity_iff_side_not_covered": True,
        "all_minimum_query_sizes_equal_min_cut_complement": True,
        "largest_exact_minimum_query_size": largest_minimum,
    }


def sampled_query_sets(n: int, k: int, rng: random.Random) -> Iterable[set[int]]:
    cut = set(range(k))
    complement = set(range(k, n))
    yield set()
    yield set(range(n))
    if cut:
        yield cut - {min(cut)}
    if complement:
        yield complement - {min(complement)}
    for _ in range(20):
        yield {edge for edge in range(n) if rng.random() < 0.5}


def deterministic_large_check(n_max: int = 127) -> dict[str, int | bool]:
    rng = random.Random(SEED)
    query_transcripts_checked = 0
    ambiguous_transcripts_witnessed = 0

    for n in range(5, n_max + 1, 2):
        universe = set(range(n))
        for k in range(1, n):
            cut = set(range(k))
            complement = universe - cut
            for queried in sampled_query_sets(n, k, rng):
                determines = cut <= queried or complement <= queried
                witness = two_flip_witness(n, k, queried)
                assert (witness is None) == determines
                query_transcripts_checked += 1
                if witness is not None:
                    ambiguous_transcripts_witnessed += 1

    return {
        "odd_n_min": 5,
        "odd_n_max": n_max,
        "query_transcripts_checked": query_transcripts_checked,
        "ambiguous_transcripts_witnessed": ambiguous_transcripts_witnessed,
        "all_checks_passed": True,
        "seed": SEED,
    }


def build_result() -> dict[str, object]:
    return {
        "schema_version": "0.1-untrusted",
        "package": "GENERIC-COCYCLE-INTEGRATION-003",
        "date": "2026-08-12",
        "exact_exhaustive": exhaustive_check(),
        "deterministic_large_samples": deterministic_large_check(),
        "claim_boundary": (
            "Finite replay of the combinatorial witness only; not an EDS-specific, "
            "coordinate-circuit, or unconditional ECDLP lower bound."
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
