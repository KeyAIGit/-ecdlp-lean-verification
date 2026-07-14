# STATUS — canonical snapshot

> **Generated** by `scripts/gen_status.py` from `data/stats.json` + `data/frontier_map.json`.
> Do not hand-edit the numbers. Other summary docs should link here, not duplicate counts.

## Verified asset (the ledger)
| metric | value | source |
|---|---|---|
| ledger rows | **227** | `VERIFIED.md` → `data/stats.json` |
| distinct results | **~191** | `data/stats.json` |
| proved modules | **106** | `data/stats.json` |
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
  division-polynomial work; Semaev `S₃`/`S₄`; the early Weil ladder (W1–W3); the **weak
  point-counting keystone** `addOrderOf G = n` (⟨G⟩ cyclic of order `n`, no Hasse/`#E`).
- Honest labels: the protocol library is **verified protocol algebra** (identities that hold in any
  `ℤ/n`-module), now also **instantiated on the concrete curve subgroup ⟨G⟩** — not a proof of
  deployed-protocol security against a real adversary. The GLV endomorphism acts as the eigenvalue
  `[λ]` **on all of ⟨G⟩** (`glvPoint P = λ·P` for `P ∈ ⟨G⟩`, proved), via the weak keystone;
  extending it to the **full** group `E(𝔽_p)` is still open. The real prover path is the **tactic
  ladder + human-in-loop** (external model-provers attempted, 0 accepted).

## Main current bottleneck
Point counting `#E(𝔽_p) = n` (the **strong** keystone, needs Hasse — absent from Mathlib v4.31).
On the crypto subgroup ⟨G⟩ the GLV eigenvalue `glvPoint = [λ]`, the `Module (ℤ/n)` structure, and
the instantiated protocol algebra are **already proved** via the weak keystone `addOrderOf G = n`.
What `#E = n` still gates is **extending those ⟨G⟩ results to the whole point group** `E(𝔽_p)`
(cofactor 1 ⇒ `E(𝔽_p) = ⟨G⟩`) and the full `E[n] ≅ (ℤ/n)²` torsion structure.

## Active work protocol
The active queue is `tasks/NEXT.md`. Keep it short (3-7 task contracts) so a
small-context agent can start work without rereading the whole repository.

The hypothesis registry is `experiments/HYPOTHESES.yaml`. It records testable
directions, evidence, and exit criteria; it is not a theorem ledger.

The drift gate is `scripts/check_status_consistency.py`. Run it whenever stats,
frontier, graph, dashboard/site counters, tasks, or hypotheses change.

## Where to go deeper
`READ_FIRST.md` (orientation for low-context readers) · `tasks/NEXT.md` (active queue) ·
`experiments/HYPOTHESES.yaml` (hypotheses + exit criteria) · `PUBLISHABLE_UNITS.md` (the 3
standalone results) · `WORK_SCOPE.md` (the improvement program) · `VERIFIED.md` (ledger) ·
`BARRIERS.md` (no-go map) · `notes/FOUNDATIONS.md` (Weil/Semaev ladder) ·
`notes/POINT_COUNTING_KEYSTONE.md` (the `#E=n` keystone) · `TRUST_REPORT.md` (trust boundary) ·
`data/frontier_map.json` (queryable per-claim status).
