#!/usr/bin/env python3
"""Generate machine-readable stats for the verified ECDLP layer.

Single source of truth is the canonical figure in ``VERIFIED.md``
(`**N ledger rows / ~M distinct kernel-verified results**`, guaranteed present
by ``scripts/check_counts.py``). This derives the public numbers from it so any
external site can fetch a stable JSON instead of scraping markdown.

Writes two files (kept in the repo so they are fetchable via raw.githubusercontent):
  - ``data/stats.json``            — full stats object
  - ``badges/theorems.json``       — shields.io endpoint-badge format

Run locally (``python3 scripts/gen_stats.py``) or in CI
(``.github/workflows/docs-sync.yml``). With ``--check`` it verifies the on-disk
files are in sync and exits non-zero if not (so the figures cannot silently
drift).

Raw URLs for a site to consume (main branch):
  https://raw.githubusercontent.com/KeyAIGit/-ecdlp-lean-verification/main/data/stats.json
  https://raw.githubusercontent.com/KeyAIGit/-ecdlp-lean-verification/main/badges/theorems.json
Live shields badge:
  https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/KeyAIGit/-ecdlp-lean-verification/main/badges/theorems.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIED = ROOT / "VERIFIED.md"
STATS_JSON = ROOT / "data" / "stats.json"
BADGE_JSON = ROOT / "badges" / "theorems.json"

CANON_RE = re.compile(
    r"\*\*(\d+)\s+ledger rows\s*/\s*~(\d+)\s+distinct kernel-verified results\*\*"
)


def compute_stats() -> dict:
    text = VERIFIED.read_text(encoding="utf-8")
    m = CANON_RE.search(text)
    if not m:
        raise SystemExit(
            "gen_stats: canonical figure not found in VERIFIED.md "
            "(expected '**N ledger rows / ~M distinct kernel-verified results**')"
        )
    ledger_rows = int(m.group(1))
    distinct = int(m.group(2))

    # Cross-checks derived from the tree (not authoritative, but surfaced).
    proved_dir = ROOT / "Ecdlp" / "Proved"
    proved_modules = len(list(proved_dir.glob("*.lean"))) if proved_dir.is_dir() else 0
    # Count actual '| proved |' rows in the ledger table as an independent tally.
    proved_row_cells = len(re.findall(r"\|\s*proved\s*\|", text))

    return {
        "schemaVersion": 1,
        "project": "ecdlp-lean-verification",
        "curve": "secp256k1",
        "toolchain": "Lean 4 + Mathlib v4.31.0",
        "ledger_rows": ledger_rows,
        "distinct_results": distinct,
        "proved_modules": proved_modules,
        "proved_ledger_cells": proved_row_cells,
        "sorry_count": 0,
        "custom_axioms": 0,
        "invariant": "green build = every listed theorem fully proved (no sorry, no custom axioms)",
        "source_of_truth": "VERIFIED.md canonical figure",
    }


def badge(stats: dict) -> dict:
    return {
        "schemaVersion": 1,
        "label": "verified theorems",
        "message": f"{stats['distinct_results']} ({stats['ledger_rows']} rows)",
        "color": "brightgreen",
    }


def render() -> tuple[str, str]:
    stats = compute_stats()
    return (
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n",
        json.dumps(badge(stats), indent=2, ensure_ascii=False) + "\n",
    )


def main(argv: list[str]) -> int:
    stats_text, badge_text = render()
    if "--check" in argv:
        ok = True
        for path, want in ((STATS_JSON, stats_text), (BADGE_JSON, badge_text)):
            have = path.read_text(encoding="utf-8") if path.exists() else None
            if have != want:
                print(f"gen_stats: {path.relative_to(ROOT)} is out of sync "
                      f"(run `python3 scripts/gen_stats.py`)")
                ok = False
        if ok:
            print("gen_stats: stats files in sync with VERIFIED.md")
            return 0
        return 1

    STATS_JSON.parent.mkdir(parents=True, exist_ok=True)
    BADGE_JSON.parent.mkdir(parents=True, exist_ok=True)
    STATS_JSON.write_text(stats_text, encoding="utf-8")
    BADGE_JSON.write_text(badge_text, encoding="utf-8")
    print(f"gen_stats: wrote {STATS_JSON.relative_to(ROOT)} and "
          f"{BADGE_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
