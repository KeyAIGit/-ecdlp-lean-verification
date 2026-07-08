# STATUS — canonical snapshot

> **Generated** by `scripts/gen_status.py` from `data/stats.json` + `data/frontier_map.json`.
> Do not hand-edit the numbers. Other summary docs should link here, not duplicate counts.

## Verified asset (the ledger)
| metric | value | source |
|---|---|---|
| ledger rows | **214** | `VERIFIED.md` → `data/stats.json` |
| distinct results | **~179** | `data/stats.json` |
| proved modules | **86** | `data/stats.json` |
| `sorry` | **0** | axiom-audit + no-sorry gate |
| custom axioms | **0** | axiom-audit gate |

Toolchain: Lean 4 + Mathlib v4.31.0.

## Corpus coverage (the 486-claim map)
The 486 corpus claims (`data/KG_CLAIM_FORMALIZATION_v1.csv`) are a *different* denominator from the
ledger: most verified theorems are foundations/new results, not original corpus items. Current
frontier-map status (adversarially-verified upgrades in `data/corpus_coverage_overrides.json`):

| status | claims | meaning |
|---|---|---|
| verified | **10** | a named kernel-verified theorem discharges the claim |
| partial | **46** | a theorem addresses part of it |
| tractable | **31** | reachable now, no theorem yet |
| blocked | **143** | needs a missing Mathlib foundation |
| informal | **161** | not a formal statement by nature |
| unassigned | **95** | not yet triaged |
| **total** | **486** | frontier completeness 80.5% |

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
`READ_FIRST.md` (orientation for low-context readers) · `PUBLISHABLE_UNITS.md` (the 3 standalone
results) · `WORK_SCOPE.md` (the improvement program) · `VERIFIED.md` (ledger) · `BARRIERS.md`
(no-go map) · `notes/FOUNDATIONS.md` (Weil/Semaev ladder) ·
`notes/POINT_COUNTING_KEYSTONE.md` (the `#E=n` keystone) · `TRUST_REPORT.md` (trust boundary) ·
`data/frontier_map.json` (queryable per-claim status).
