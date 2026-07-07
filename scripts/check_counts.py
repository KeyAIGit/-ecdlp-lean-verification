#!/usr/bin/env python3
"""Count-consistency gate (CI).

The repo's headline theorem count drifted three times (96/98/85/99/108/128 all appeared
across docs for the same body of work). This gate fails the build if any RETIRED headline
count string reappears in the narrative docs, and sanity-checks that the canonical figure
is present in VERIFIED.md.

Canonical figure (single source of truth): "189 ledger rows / ~167 distinct results".
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
    "~115 distinct", "126 ledger rows", "126 rows",
    "~118 distinct", "132 ledger rows", "132 rows",
    "~119 distinct", "133 ledger rows", "133 rows",
    "~120 distinct", "134 ledger rows", "134 rows",
    "~121 distinct", "135 ledger rows", "135 rows",
    "~122 distinct", "136 ledger rows", "136 rows",
    "~123 distinct", "137 ledger rows", "137 rows",
    "~124 distinct", "138 ledger rows", "138 rows",
    "~125 distinct", "139 ledger rows", "139 rows",
    "~126 distinct", "140 ledger rows", "140 rows",
    "~127 distinct", "141 ledger rows", "141 rows",
    "~128 distinct", "142 ledger rows", "142 rows",
    "~129 distinct", "143 ledger rows", "143 rows",
    "~130 distinct", "144 ledger rows", "144 rows",
    "~131 distinct", "145 ledger rows", "145 rows",
    "~132 distinct", "146 ledger rows", "146 rows",
    "~133 distinct", "147 ledger rows", "147 rows",
    "148 ledger rows", "148 rows",
    "~134 distinct", "149 ledger rows", "149 rows",
    "~135 distinct", "150 ledger rows", "150 rows",
    "151 ledger rows", "151 rows",
    "~136 distinct", "152 ledger rows", "152 rows",
    "~137 distinct", "153 ledger rows", "153 rows",
    "154 ledger rows", "154 rows",
    "~138 distinct", "155 ledger rows", "155 rows",
    "156 ledger rows", "156 rows",
    "~139 distinct", "157 ledger rows", "157 rows",
    "~140 distinct", "158 ledger rows", "158 rows",
    "159 ledger rows", "159 rows",
    "~141 distinct", "160 ledger rows", "160 rows",
    "~142 distinct", "161 ledger rows", "161 rows",
    "~143 distinct", "162 ledger rows", "162 rows",
    "~144 distinct", "163 ledger rows", "163 rows",
    "~145 distinct", "164 ledger rows", "164 rows",
    "~146 distinct", "165 ledger rows", "165 rows",
    "~147 distinct", "166 ledger rows", "166 rows",
    "~148 distinct", "167 ledger rows", "167 rows",
    "~149 distinct", "168 ledger rows", "168 rows",
    "~150 distinct", "169 ledger rows", "169 rows",
    "170 ledger rows", "170 rows",
    "~151 distinct", "171 ledger rows", "171 rows",
    "172 ledger rows", "172 rows",
    "~152 distinct", "173 ledger rows", "173 rows",
    "~153 distinct", "174 ledger rows", "174 rows",
    "~154 distinct", "175 ledger rows", "175 rows",
    "~155 distinct", "176 ledger rows", "176 rows",
    "~156 distinct", "177 ledger rows", "177 rows",
    "~157 distinct", "178 ledger rows", "178 rows",
    "179 ledger rows", "179 rows",
    "~158 distinct", "180 ledger rows", "180 rows",
    "~159 distinct", "181 ledger rows", "181 rows",
    "~160 distinct", "182 ledger rows", "182 rows",
    "~161 distinct", "183 ledger rows", "183 rows",
    "~162 distinct", "184 ledger rows", "184 rows",
    "~163 distinct", "185 ledger rows", "185 rows",
    "~164 distinct", "186 ledger rows", "186 rows",
    "~165 distinct", "187 ledger rows", "187 rows",
    "~166 distinct", "188 ledger rows", "188 rows",
    "~167 distinct", "189 ledger rows", "189 rows",
    "~168 distinct", "190 ledger rows", "190 rows",
    "~169 distinct", "191 ledger rows", "191 rows",
    "~170 distinct", "193 ledger rows", "193 rows",
    "192 ledger rows", "192 rows",
    "194 ledger rows", "194 rows",
    "195 ledger rows", "195 rows",
    "~171 distinct", "196 ledger rows", "196 rows",
    "197 ledger rows", "197 rows",
]

# Must appear somewhere in VERIFIED.md so the canonical figure stays discoverable.
CANONICAL_PRESENT = ["~172 distinct", "198 ledger rows"]


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
              "'142 ledger rows / ~128 distinct results':")
        print("\n".join("  " + f for f in failures))
        return 1
    print("count consistency OK: no retired headline counts; canonical figure present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
