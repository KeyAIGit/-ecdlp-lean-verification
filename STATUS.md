# STATUS — canonical snapshot

> **Generated** by `scripts/gen_status.py` from `data/stats.json`,
> `data/frontier_map.json`, and `repo/ECDLP_DECISION_SUBSTRATE.json`.
> Do not hand-edit the numbers. Other summary docs should link here, not duplicate counts.

## Verified asset (the ledger)
| metric | value | source |
|---|---|---|
| ledger rows | **296** | `VERIFIED.md` → `data/stats.json` |
| distinct results | **~257** | `data/stats.json` |
| proved modules | **164** | `data/stats.json` |
| `sorry` | **0** | axiom-audit + no-sorry gate |
| custom axioms | **0** | axiom-audit gate |

Toolchain: Lean 4 + Mathlib v4.31.0.

## Corpus coverage (the 486-claim map)
The 486 corpus claims (`data/KG_CLAIM_FORMALIZATION_v1.csv`) are a *different* denominator from the
ledger: most verified theorems are foundations/new results, not original corpus items. Current
frontier-map status (adversarially-verified upgrades in `data/corpus_coverage_overrides.json`):

| status | claims | meaning |
|---|---|---|
| verified | **11** | a named kernel-verified theorem discharges the claim |
| partial | **55** | a theorem addresses part of it |
| tractable | **2** | reachable now, no theorem yet |
| blocked | **193** | needs a missing Mathlib foundation |
| informal | **225** | not a formal statement by nature |
| unassigned | **0** | not yet triaged |
| **total** | **486** | frontier completeness 100.0% |

## What is true right now (honest)
- This is a **verified substrate** for ECDLP / secp256k1 research. It does **not** solve ECDLP on
  secp256k1, and claims no shortcut.
- The generic-group `Ω(√n)` bound (formalized here) constrains only **black-box** algorithms; it
  says nothing about non-generic attacks on this concrete curve, whose hardness is an **open
  conjecture**, not a theorem.
- Strongest layers: verified secp256k1 arithmetic + machine-checked primality (Pratt); the
  generic-DLP `Θ(√n)` combinatorial core; attack-boundary facts (anti-MOV / anti-Smart); torsion /
  division-polynomial work; Semaev `S₃`/`S₄`; the early Weil ladder (W1–W3); **both point-counting
  keystones** — the weak `addOrderOf G = n` *and* the strong **`#E(𝔽_p) = n`** (proved
  curve-specifically, no Hasse/Schoof: `CurveCardinalityExact.lean`), giving
  `E(𝔽_p) = ⟨G⟩ ≃+ ℤ/n` (`CurveFullGroup.lean`, `PointGroupEquiv.lean`).
- Honest labels: the protocol library is **verified protocol algebra** (identities that hold in any
  `ℤ/n`-module), now also **instantiated on the concrete curve group** `⟨G⟩ = E(𝔽_p)` (the full
  point group, via the strong keystone) — not a proof of deployed-protocol security against a real
  adversary. The GLV endomorphism acts as the eigenvalue `[λ]` **on the whole point group**
  (`secp256k1_glvHom_eq_zsmul_unconditional`, no remaining hypotheses). The real prover path is the
  **tactic ladder + human-in-loop** (external model-provers attempted, 0 accepted).

## Main current bottleneck
The current bottleneck is **a missing proposal-level non-generic mechanism, not theorem
volume**. Decision `RS-2026-07-22-001` evaluated all **17 attack routes** and
selected **none**: no audited route currently clears the common gate for the exact plain
single-target objective. The map contains **11 foundation decisions**,
experiments authorized = **false**, selected route =
**none**.

The completed `build_now` foundations are `F-EVALUATION-CONTRACT`, `F-BENCHMARK-ORACLE`.
They make future candidates comparable and independently checkable; they do not test a parked
hypothesis. The formal gaps `E[n] ≅ (ℤ/n)²`, Weil reciprocity/pairing, general point-division
bridges, p-adic formal groups, lattice reduction, isogenies, and quantum circuits remain mapped,
but none is automatically next merely because Mathlib lacks it. Route selection reopens only
when new evidence satisfies a recorded reconsideration trigger and the proposal gate.

## Active work protocol
The active queue is `tasks/NEXT.md`. Keep it short (3-7 task contracts) so a
small-context agent can start work without rereading the whole repository.

The route authority is `repo/ECDLP_DECISION_SUBSTRATE.json`; its Markdown view is generated.
The candidate-neutral validation contract lives in `experiments/framework/`. Neither file
authorizes an experiment by itself.

The hypothesis registry is `experiments/HYPOTHESES.yaml`. It records testable
directions, evidence, and exit criteria; it is not a theorem ledger.

The drift gate is `scripts/check_status_consistency.py`. Run it whenever stats,
frontier, graph, dashboard/site counters, tasks, or hypotheses change.

## Where to go deeper
`README.md` (the front door) · `repo/ECDLP_DECISION_SUBSTRATE.json` (route decisions) ·
`tasks/NEXT.md` (active queue) ·
`experiments/HYPOTHESES.yaml` (hypotheses + exit criteria) · `PUBLISHABLE_UNITS.md` (the 3
standalone results) · `ROADMAP.md` (strategy & program) · `VERIFIED.md` (ledger) ·
`BARRIERS.md` (no-go map) · `notes/FOUNDATIONS.md` (Weil/Semaev ladder) ·
`notes/POINT_COUNTING_KEYSTONE.md` (the `#E=n` keystone) · `TRUST_REPORT.md` (trust boundary) ·
`data/frontier_map.json` (queryable per-claim status) ·
`experiments/framework/README.md` (candidate-evaluation contract).
