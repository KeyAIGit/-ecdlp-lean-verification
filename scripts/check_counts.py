#!/usr/bin/env python3
"""Count-consistency gate (CI).

The repo's headline theorem count drifted repeatedly (96/98/85/99/108/128 all appeared
across docs for the same body of work; later the prose figure lagged the ledger table
itself: 226→227, 235→227, 239→228). This gate now does three things:

1. **Recounts the ledger table** in ``VERIFIED.md`` (same logic as
   ``scripts/gen_stats.py``) and fails if the canonical prose line
   (``**N ledger rows / ~M distinct kernel-verified results**``) does not match the
   recount, or if ``rows − alternate-form ≠ distinct``.
2. Fails if any RETIRED headline-count string reappears in the narrative docs. The
   retired set is **generated** from the current figures (every older
   ``N ledger rows`` / ``N rows`` / ``~M distinct``), so bumping the count never
   requires editing a hand-grown list again.
3. Sanity-checks that the current canonical figure is present in ``VERIFIED.md``.

The one human-facing snapshot is ``STATUS.md`` (generated); other summary docs must
point to it rather than re-state counts, and are scanned below so a stale copy fails
the build. A line documenting this gate may quote retired strings — mark it
``count-check: ignore`` to exempt it.

Usage:  python3 scripts/check_counts.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOCS = [
    "README.md", "AGENTS.md", "BARRIERS.md", "VERIFIED.md",
    "data/knowledge_graph.md", "CLAUDE.md",
    # summary docs that historically drifted — now scanned so they can't silently re-drift
    "STATUS.md", "TRUST_REPORT.md", "ABSTRACT_SCOPE.md",
    "COVERAGE.md", "REPOSITORY_ARCHITECTURE.md",
    "ROADMAP.md", "repo/CLEANUP_PLAN.md",
]

# Retired headline strings that must NOT reappear (regex-free substring match) and are
# not of the generated "N ledger rows / N rows / ~M distinct" shape. These are
# specifically count-headline phrasings, not bare numbers, to avoid false positives on
# unrelated uses of the digits (and the legitimate "128 ... retired" disclaimer).
RETIRED_STATIC = [
    "~99 named", "~96 named", "~98 named", "85 named results",
    "~99 named-result", "108 theorems", "96 named", "98 named",
    "128 theorems verified", "128 named",
]

# Floors for the generated retired ranges — the smallest figures that ever appeared as
# a "ledger rows / distinct" headline (older headlines used the phrasings above).
ROWS_FLOOR = 126
DISTINCT_FLOOR = 115

CANON_RE = re.compile(
    r"\*\*(\d+)\s+ledger rows\s*/\s*~(\d+)\s+distinct kernel-verified results\*\*"
)
ALT_RE = re.compile(r"\((\d+)\s+rows are alternate-form")
HEADLINE_END = "### Coverage restatements"


def count_ledger_rows(text: str) -> int:
    """Recount the main ledger table (rows with a `proved…` status cell, above the
    tracked-separately sections). Mirrors scripts/gen_stats.py."""
    total = 0
    for line in text.splitlines():
        if line.startswith(HEADLINE_END):
            break
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[-1].startswith("proved"):
            total += 1
    return total


def main() -> int:
    failures: list[str] = []

    vpath = ROOT / "VERIFIED.md"
    vtext = vpath.read_text(encoding="utf-8") if vpath.exists() else ""
    rows = count_ledger_rows(vtext)
    m_alt = ALT_RE.search(vtext)
    m_canon = CANON_RE.search(vtext)

    if rows <= 0:
        failures.append("VERIFIED.md: no ledger rows found in the main table")
    if not m_alt:
        failures.append("VERIFIED.md: alternate-form figure '(N rows are alternate-form' missing")
    if not m_canon:
        failures.append("VERIFIED.md: canonical figure "
                        "'**N ledger rows / ~M distinct kernel-verified results**' missing")

    distinct = rows - int(m_alt.group(1)) if m_alt else 0
    if m_alt and m_canon:
        prose_rows, prose_distinct = int(m_canon.group(1)), int(m_canon.group(2))
        if prose_rows != rows:
            failures.append(
                f"VERIFIED.md: canonical line says {prose_rows} ledger rows but the table "
                f"recount gives {rows} — update the canonical line")
        if prose_distinct != distinct:
            failures.append(
                f"VERIFIED.md: canonical line says ~{prose_distinct} distinct but "
                f"rows({rows}) − alternate-form({int(m_alt.group(1))}) = {distinct} — "
                "update the canonical line (or the alternate-form figure)")

    # Generated retired set: every older headline figure below the current ones.
    retired = list(RETIRED_STATIC)
    for r in range(ROWS_FLOOR, max(rows, ROWS_FLOOR)):
        retired.append(f"{r} ledger rows")
        retired.append(f"{r} rows")
    for d in range(DISTINCT_FLOOR, max(distinct, DISTINCT_FLOOR)):
        retired.append(f"~{d} distinct")

    for doc in DOCS:
        p = ROOT / doc
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if "count-check: ignore" in line:
                continue
            for bad in retired:
                if bad in line:
                    failures.append(f"{doc}:{i}: retired count headline '{bad}': {line.strip()}")

    if failures:
        print("COUNT CONSISTENCY FAILED — fix these to the canonical figure "
              f"'{rows} ledger rows / ~{distinct} distinct results' "
              "(or point the doc at STATUS.md):")
        print("\n".join("  " + f for f in failures))
        return 1
    print(f"count consistency OK: table recount {rows} rows / ~{distinct} distinct matches "
          "the canonical figure; no retired headline counts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
