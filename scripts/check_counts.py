#!/usr/bin/env python3
"""Count-consistency gate (CI).

The repo's headline theorem count drifted three times (96/98/85/99/108/128 all appeared
across docs for the same body of work). This gate fails the build if any RETIRED headline
count string reappears in the narrative docs, and sanity-checks that the canonical figure
is present in VERIFIED.md.

Canonical figure (single source of truth): "116 ledger rows / ~106 distinct results".
Update CANONICAL_PRESENT / RETIRED here (and only here) if the real count changes.

Usage:  python3 scripts/check_counts.py
"""
from __future__ import annotations

import sys
from pathlib import Path

DOCS = [
    "README.md", "AGENTS.md", "BARRIERS.md", "VERIFIED.md",
    "data/knowledge_graph.md", "CLAUDE.md",
]

# Retired headline strings that must NOT reappear (regex-free substring match). These are
# specifically count-headline phrasings, not bare numbers, to avoid false positives on
# unrelated uses of the digits (and the legitimate "128 ... retired" disclaimer).
RETIRED = [
    "~99 named", "~96 named", "~98 named", "85 named results",
    "~99 named-result", "108 theorems", "96 named", "98 named",
    "128 theorems verified", "128 named",
]

# Must appear somewhere in VERIFIED.md so the canonical figure stays discoverable.
CANONICAL_PRESENT = ["~106 distinct", "116 ledger rows"]


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    failures: list[str] = []

    for doc in DOCS:
        p = root / doc
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            for bad in RETIRED:
                if bad in line:
                    failures.append(f"{doc}:{i}: retired count headline '{bad}': {line.strip()}")

    verified = (root / "VERIFIED.md")
    if verified.exists():
        vtext = verified.read_text(encoding="utf-8")
        for need in CANONICAL_PRESENT:
            if need not in vtext:
                failures.append(f"VERIFIED.md: canonical figure '{need}' is missing")

    if failures:
        print("COUNT CONSISTENCY FAILED — fix these to the canonical figure "
              "'116 ledger rows / ~106 distinct results':")
        print("\n".join("  " + f for f in failures))
        return 1
    print("count consistency OK: no retired headline counts; canonical figure present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
