#!/usr/bin/env python3
"""Generate STATUS.md — the ONE canonical human snapshot.

The single source of operational truth for any reader (human or AI, large or small context).
Every number here is pulled live from the machine sources, never hand-typed, so it cannot drift:
  - data/stats.json          (ledger_rows, distinct_results, proved_modules, sorry, axioms)
  - data/frontier_map.json   (corpus status_summary, completeness)
Other summary docs should link to STATUS.md rather than duplicate counts.

Run: python3 scripts/gen_status.py   (also run by the docs-sync workflow on every ledger change)
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATS = ROOT / "data" / "stats.json"
FM = ROOT / "data" / "frontier_map.json"
OUT = ROOT / "STATUS.md"


def main() -> int:
    s = json.loads(STATS.read_text(encoding="utf-8"))
    fm = json.loads(FM.read_text(encoding="utf-8"))
    ss = fm["status_summary"]
    meta = fm["meta"]
    total = meta.get("corpus_claims", sum(ss.values()))

    def g(k, d=0):
        return s.get(k, d)

    md = f"""# STATUS — canonical snapshot

> **Generated** by `scripts/gen_status.py` from `data/stats.json` + `data/frontier_map.json`.
> Do not hand-edit the numbers. Other summary docs should link here, not duplicate counts.

## Verified asset (the ledger)
| metric | value | source |
|---|---|---|
| ledger rows | **{g('ledger_rows')}** | `VERIFIED.md` → `data/stats.json` |
| distinct results | **~{g('distinct_results')}** | `data/stats.json` |
| proved modules | **{g('proved_modules')}** | `data/stats.json` |
| `sorry` | **{g('sorry_count')}** | axiom-audit + no-sorry gate |
| custom axioms | **{g('custom_axioms')}** | axiom-audit gate |

Toolchain: {g('toolchain', 'Lean 4 + Mathlib (see lakefile.toml)')}.

## Corpus coverage (the 486-claim map)
The 486 corpus claims (`data/KG_CLAIM_FORMALIZATION_v1.csv`) are a *different* denominator from the
ledger: most verified theorems are foundations/new results, not original corpus items. Current
frontier-map status (adversarially-verified upgrades in `data/corpus_coverage_overrides.json`):

| status | claims | meaning |
|---|---|---|
| verified | **{ss.get('verified',0)}** | a named kernel-verified theorem discharges the claim |
| partial | **{ss.get('partial',0)}** | a theorem addresses part of it |
| tractable | **{ss.get('tractable',0)}** | reachable now, no theorem yet |
| blocked | **{ss.get('blocked',0)}** | needs a missing Mathlib foundation |
| informal | **{ss.get('informal',0)}** | not a formal statement by nature |
| unassigned | **{ss.get('unassigned',0)}** | not yet triaged |
| **total** | **{total}** | frontier completeness {meta.get('frontier_completeness_pct','?')}% |

## What is true right now (honest)
- This is a **verified substrate** for ECDLP / secp256k1 research. It does **not** solve ECDLP on
  secp256k1, and claims no shortcut.
- The generic-group `Ω(√n)` bound (formalized here) constrains only **black-box** algorithms; it
  says nothing about non-generic attacks on this concrete curve, whose hardness is an **open
  conjecture**, not a theorem.
- Strongest layers: verified secp256k1 arithmetic + machine-checked primality (Pratt); the
  generic-DLP `Θ(√n)` combinatorial core; attack-boundary facts (anti-MOV / anti-Smart); torsion /
  division-polynomial work; Semaev `S₃`/`S₄`; the early Weil ladder (W1–W3).
- Honest labels: the protocol library is **verified protocol algebra** (abstract identities), not
  proven security of deployed protocols; the GLV object has its **homomorphism half** proved, the
  `[λ]` eigenvalue still open; the real prover path is the **tactic ladder + human-in-loop**
  (external model-provers attempted, 0 accepted).

## Main current bottleneck
Point counting `#E(𝔽_p) = n` — the keystone that gates the GLV eigenvalue `glvPoint G = λ·G`, the
`Module (ℤ/n)` structure on the real point group, and honest instantiation of the protocol algebra.

## Where to go deeper
`WORK_SCOPE.md` (the improvement program) · `VERIFIED.md` (ledger) · `BARRIERS.md` (no-go map) ·
`notes/FOUNDATIONS.md` (Weil/Semaev ladder) · `TRUST_REPORT.md` (trust boundary) ·
`data/frontier_map.json` (queryable per-claim status).
"""
    OUT.write_text(md, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {g('ledger_rows')} rows / ~{g('distinct_results')} "
          f"distinct; corpus verified={ss.get('verified',0)}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
