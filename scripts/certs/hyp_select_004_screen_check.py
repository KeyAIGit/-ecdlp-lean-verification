#!/usr/bin/env python3
"""Replay the HYP-SELECT-004 100-candidate screening ledger."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCREEN = ROOT / "data" / "hyp_select_004_raw_100.tsv"

EXPECTED_SHORTLIST = {
    "HYP-PPLUS1-TRACE-RELATION-001",
    "HYP-TORUS-CIRCUIT-FIDELITY-001",
    "HYP-ISOGENY-REPRESENTATION-SLOPE-001",
    "HYP-COORDINATE-HIDDEN-SHIFT-001",
    "HYP-SGGM-SPARSE-APPLICABILITY-001",
    "HYP-INDUCED-SUBSET-CONSERVATION-001",
    "HYP-SEMAEV-RELATION-INCIDENCE-001",
    "HYP-END-TO-END-COST-BRIDGE-001",
}


def main() -> int:
    with SCREEN.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    assert len(rows) == 100
    assert len({row["id"] for row in rows}) == 100
    assert Counter(row["id"].split("-")[0] for row in rows) == {
        "H4": 34,
        "HCS": 33,
        "ALG": 33,
    }
    assert Counter(row["hard_gate"] for row in rows) == {
        "PASS": 49,
        "REFORMULATE": 18,
        "KILL": 33,
    }
    assert Counter(row["portfolio"] for row in rows) == {
        "DEFERRED": 42,
        "KILLED": 33,
        "MERGED": 14,
        "SHORTLIST": 8,
        "ADJACENT": 3,
    }

    shortlist = {
        row["canonical"] for row in rows if row["portfolio"] == "SHORTLIST"
    }
    assert shortlist == EXPECTED_SHORTLIST
    assert all(
        row["hard_gate"] in {"PASS", "REFORMULATE"}
        for row in rows
        if row["portfolio"] == "SHORTLIST"
    )
    assert all(
        row["type"] in {"ADJACENT", "BARRIER"}
        for row in rows
        if row["portfolio"] == "ADJACENT"
    )
    assert all(row["family"] and row["short_claim"] for row in rows)

    print(
        "CERT_OK HYP-SELECT-004 "
        "raw=100 pass=49 reformulate=18 kill=33 shortlist=8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
