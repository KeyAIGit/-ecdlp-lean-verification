#!/usr/bin/env python3
"""Fixtures guarding the count-integrity gate hardening (scripts/check_counts.py).

Designed with an adversarial workflow (audit → design → red-team); this locks in the
robust, false-positive-free subset that survived the red-team, and documents the vectors
it closes:

  * count_ledger_rows table-identity guard — a stray prose/status table above the
    `### Coverage restatements` cutoff whose rows end in a `proved…` cell cannot inflate the
    recount (real ledger rows cite a backticked Lean name);
  * off_canonical_claims bidirectional scan — an `N ledger rows` / `~N distinct` figure that
    differs from canonical fails in BOTH directions (stale-low leftover AND stale-high /
    reverted-bump inflation), while small-number adjective uses and non-`ledger rows`
    phrasings pass;
  * canonical-line uniqueness — a duplicate `**N ledger rows / ~M distinct …**` block is
    detectable (re.search would otherwise mask it behind the first hit).

Deliberately NOT covered (deferred as fragile per the red-team; recorded in the PR): the
elaborate multi-noun/SEP scanner, break-based table anchoring, unicode-dash / split-tag /
line-wrap evasions, and check_status_consistency node-pin tightening.

Run: python3 scripts/test_check_counts.py   (plain asserts, no pytest needed)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_counts as cc  # noqa: E402
import gen_stats as gs      # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_ROW = "| **thm** | `Ecdlp.Curve.foo` | F.lean | Mathlib | proved |"


def test_count_ledger_rows_table_identity_guard():
    stray = "| Build health | green | 3/3 | fast | proved |"   # a table row, but no backtick
    text = "\n".join([_ROW, _ROW, stray]) + "\n### Coverage restatements\n" + _ROW
    assert cc.count_ledger_rows(text) == 2, "stray non-backtick table must not inflate; cutoff respected"
    assert gs.count_ledger_rows(text)[0] == 2, "gen_stats recount must mirror the guard"


def test_off_canonical_bidirectional():
    R, D = 254, 215
    assert cc.off_canonical_claims("we verified 228 ledger rows here", R, D), "stale-LOW rows must flag"
    assert cc.off_canonical_claims("now up to 300 ledger rows", R, D), "stale-HIGH rows must flag"
    assert cc.off_canonical_claims("about ~240 distinct results", R, D), "stale-HIGH distinct must flag"
    assert cc.off_canonical_claims("209 distinct kernel-verified", R, D), "no-tilde stale distinct must flag"
    assert not cc.off_canonical_claims("**254 ledger rows / ~215 distinct** now", R, D), "canonical passes"
    assert not cc.off_canonical_claims("39 rows are alternate-form", R, D), "'rows' not 'ledger rows' passes"
    assert not cc.off_canonical_claims("exactly 3 distinct primes divide it", R, D), "below floor passes"
    assert not cc.off_canonical_claims("~33 rows of supporting lemmas", R, D), "sub-count 'rows' passes"


def test_canonical_uniqueness_detectable():
    canon = "**254 ledger rows / ~215 distinct kernel-verified results** (39 rows are alternate-form)"

    def collect(text):
        return [ln for ln in text.splitlines()
                if cc.CANON_RE.search(ln) and "count-check: ignore" not in ln]

    assert len(collect(canon)) == 1, "the single canonical line is found"
    dup = canon + "\n**300 ledger rows / ~250 distinct kernel-verified results**"
    assert len(collect(dup)) == 2, "a duplicate/leftover canonical block must be detectable"
    marked = canon + "\n**300 ledger rows / ~250 distinct kernel-verified results** count-check: ignore"
    assert len(collect(marked)) == 1, "an ignore-marked historical canonical mention is exempt"


def test_live_tree_stays_green():
    v = (ROOT / "VERIFIED.md").read_text(encoding="utf-8")
    cc_rows = cc.count_ledger_rows(v)
    gs_rows = gs.count_ledger_rows(v)[0]
    assert cc_rows == gs_rows > 0, f"recounts must agree and be positive (cc={cc_rows}, gs={gs_rows})"
    assert cc.main() == 0, "check_counts must pass on the live tree"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\nall {len(tests)} count-gate fixtures passed")
