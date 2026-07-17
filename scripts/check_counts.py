#!/usr/bin/env python3
"""Count-consistency gate (CI).

The repo's headline theorem count drifted repeatedly (96/98/85/99/108/128 all appeared
across docs for the same body of work; later the prose figure lagged the ledger table
itself: 226→227, 235→227, 239→228). This gate now does three things:

1. **Recounts the ledger table** in ``VERIFIED.md`` (same logic as
   ``scripts/gen_stats.py``) and fails if the canonical prose line
   (``**N ledger rows / ~M distinct kernel-verified results**``) does not match the
   recount, or if ``rows − alternate-form ≠ distinct``.
2. Fails if any ``N ledger rows`` / ``~N distinct`` figure in the narrative docs differs
   from the current canonical value — in **both** directions, so a stale-low leftover AND
   a stale-high / reverted-bump inflation are caught (the earlier below-only generated
   retired set was blind to figures above current). A small hand-list of older
   ``named`` / ``theorems`` phrasings (``RETIRED_STATIC``) is still matched as substrings.
3. Sanity-checks that **exactly one** canonical figure line is present in ``VERIFIED.md``
   (a duplicate/leftover would hide drift behind ``re.search``'s first match).

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


ROWS_CLAIM_RE = re.compile(r"(\d+)\s+ledger rows")
DIST_CLAIM_RE = re.compile(r"~?(\d+)\s+distinct")


def count_ledger_rows(text: str) -> int:
    """Recount the main ledger table (rows with a `proved…` status cell AND a backticked
    Lean name, above the tracked-separately sections). Mirrors scripts/gen_stats.py.

    The backtick requirement is a table-identity guard: every real ledger row cites its
    theorem in backticks, so a stray prose/status table above the `### Coverage
    restatements` cutoff whose rows merely end in a `proved…` cell cannot silently inflate
    the headline."""
    total = 0
    for line in text.splitlines():
        if line.startswith(HEADLINE_END):
            break
        if not line.startswith("| "):
            continue
        if "`" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[-1].startswith("proved"):
            total += 1
    return total


def off_canonical_claims(line: str, rows: int, distinct: int) -> list[str]:
    """Off-canonical count-claim scan (bidirectional). Return a description for every
    ``N ledger rows`` / ``~N distinct`` figure in `line` that is in the headline magnitude
    range (``>= ROWS_FLOOR`` / ``>= DISTINCT_FLOOR``) yet differs from the current canonical
    value — catching BOTH a stale-low leftover AND a stale-high / reverted-bump inflation
    (the old generated retired set only covered figures *below* current and was blind
    upward). The magnitude floor keeps small adjective uses (``3 distinct``, ``39 rows``)
    from tripping it. The caller skips ``count-check: ignore`` lines."""
    out: list[str] = []
    for n in ROWS_CLAIM_RE.findall(line):
        if int(n) >= ROWS_FLOOR and int(n) != rows:
            out.append(f"off-canonical '{n} ledger rows' (canonical {rows})")
    for n in DIST_CLAIM_RE.findall(line):
        if int(n) >= DISTINCT_FLOOR and int(n) != distinct:
            out.append(f"off-canonical '~{n} distinct' (canonical {distinct})")
    return out


def main() -> int:
    failures: list[str] = []

    vpath = ROOT / "VERIFIED.md"
    vtext = vpath.read_text(encoding="utf-8") if vpath.exists() else ""
    rows = count_ledger_rows(vtext)
    m_alt = ALT_RE.search(vtext)
    # Exactly one non-ignored canonical prose line must exist. re.search returns only the
    # FIRST match, so a duplicate or leftover '**N ledger rows / ~M distinct …**' block would
    # otherwise hide drift behind the first hit (and a stale-high second copy is invisible to
    # any below-only retired scan). Count them and fail closed on 0 or >1.
    canon_lines = [ln for ln in vtext.splitlines()
                   if CANON_RE.search(ln) and "count-check: ignore" not in ln]
    m_canon = CANON_RE.search(canon_lines[0]) if canon_lines else None

    if rows <= 0:
        failures.append("VERIFIED.md: no ledger rows found in the main table")
    if not m_alt:
        failures.append("VERIFIED.md: alternate-form figure '(N rows are alternate-form' missing")
    if len(canon_lines) == 0:
        failures.append("VERIFIED.md: canonical figure "
                        "'**N ledger rows / ~M distinct kernel-verified results**' missing")
    elif len(canon_lines) > 1:
        failures.append(
            f"VERIFIED.md: {len(canon_lines)} canonical-format lines found (must be exactly "
            "one; a duplicate or leftover hides drift behind re.search's first match): "
            f"{[ln.strip()[:70] for ln in canon_lines]}")

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

    # Two scans over the narrative docs: (1) RETIRED_STATIC — the older 'named'/'theorems'
    # phrasings, matched as exact substrings; (2) off_canonical_claims — every
    # 'N ledger rows' / '~N distinct' figure in the headline magnitude range that differs
    # from the current canonical value, in BOTH directions (replaces the old generated
    # below-only retired set, which was blind to figures above current). Lines carrying
    # 'count-check: ignore' are exempt (for intentional historical mentions).
    for doc in DOCS:
        p = ROOT / doc
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if "count-check: ignore" in line:
                continue
            for bad in RETIRED_STATIC:
                if bad in line:
                    failures.append(f"{doc}:{i}: retired count headline '{bad}': {line.strip()}")
            for desc in off_canonical_claims(line, rows, distinct):
                failures.append(f"{doc}:{i}: {desc}: {line.strip()}")

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
