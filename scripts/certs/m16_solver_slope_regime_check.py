#!/usr/bin/env python3
"""Replay the exact integer M16 small-ladder regime certificate."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "experiments"
    / "engine"
    / "pkc_smooth_m16_solver_slope"
    / "REGIME_AUDIT.json"
)


def maximum_balanced_degree(field_bits: int, arity: int) -> int:
    """Largest D allowed by D^k <= 2*k!*(2^field_bits-1)."""
    bound = 2 * math.factorial(arity) * ((1 << field_bits) - 1)
    degree = 0
    while (degree + 1) ** arity <= bound:
        degree += 1
    assert degree**arity <= bound
    assert (degree + 1) ** arity > bound
    return degree


def main() -> int:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    arity = artifact["fixed_arity"]
    expected = {12: 11, 15: 13, 18: 15, 21: 17, 24: 20}
    observed: dict[int, int] = {}

    for row in artifact["rows"]:
        bits = row["field_bits"]
        assert row["max_p"] == (1 << bits) - 1
        degree = maximum_balanced_degree(bits, arity)
        assert degree == row["max_D"]
        assert row["D_less_than_k"] is (degree < arity)
        observed[bits] = degree

    assert observed == expected
    assert all(observed[bits] < arity for bits in (12, 15, 18))
    assert max(observed.values()) == 20
    print("CERT_OK M16-SOLVER-SLOPE-REGIME-AUDIT-001")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
