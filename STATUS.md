# STATUS — canonical snapshot

> **Generated** by `scripts/gen_status.py` from `data/stats.json`,
> `data/frontier_map.json`, `repo/PRODUCT_MODEL.json`, and
> `repo/PILOT_PROTOCOL.json`, `repo/ECDLP_DECISION_SUBSTRATE.json`, and
> `repo/ECDLP_TYPED_EVIDENCE_V0.json`, `data/typed_evidence_state.json`, and
> `data/research_engine_state.json`, `data/research_engine_v02_state.json`, and
> `data/research_engine_shadow_intake.json`.
> Do not hand-edit the numbers. Other summary docs should link here, not duplicate counts.

## Verified asset (the ledger)
| metric | value | source |
|---|---|---|
| ledger rows | **300** | `VERIFIED.md` → `data/stats.json` |
| distinct results | **~261** | `data/stats.json` |
| proved modules | **169** | `data/stats.json` |
| `sorry` | **0** | axiom-audit + no-sorry gate |
| custom axioms | **0** | axiom-audit gate |

Toolchain: Lean 4 + Mathlib v4.31.0.

## Product state
- **Category:** verification workspace for AI research.
- **Current stage:** Reference deployment. The repository demonstrates the full research-state loop on one difficult domain, but it is not yet a self-serve hosted product.
- **Reference deployment:** this secp256k1 repository demonstrates the research-state loop on one
  difficult domain; it is evidence for the product design, not a claim of a hosted multi-project
  product or an ECDLP break.
- **MVP boundary:** A non-owner research team can connect a second project, obtain a trustworthy initial map, run one candidate through its verifier, and understand the resulting decision without editing KeyAI's generator code.
- **External pilot:** KEYAI-PILOT-001 is **recruiting**. No external pilot session has been completed or recorded.
- **Customer evidence:** 2 customer hypotheses are recorded:
  2 unvalidated. Status changes require dated evidence.
- **Accelerator boundary:** Not ready today. A technical MVP is necessary but not sufficient; a credible accelerator narrative additionally requires repeatable buyer evidence across more than one team and direct willingness-to-pay evidence.

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
- KeyAI is a **verification workspace for AI research**. This repository is its public
  **verified substrate** and reference deployment for ECDLP / secp256k1 research. It does **not**
  solve ECDLP on secp256k1, and claims no shortcut.
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
volume**. Decision `RS-2026-07-24-001` evaluated all **17 attack routes** and
recorded **1 route in completed bounded structural work**
(`R-GLV-SEMAEV`), while promoting
**0 routes**. The completed work resolved one exact S3/S4 polynomial-symmetry
question and one S4 fixed-target uncertainty; it was not an attack experiment or a route promotion. The map contains
**11 foundation decisions**,
bounded exploration authorized = **false**,
promotion experiments authorized =
**false**, selected attack route =
**none**.

The `build_now` foundations are `F-EVALUATION-CONTRACT`, `F-BENCHMARK-ORACLE`.
They make future candidates comparable and independently checkable; the completed structural
work did not activate a parked experiment hypothesis. The formal gaps `E[n] ≅ (ℤ/n)²`,
Weil reciprocity/pairing, general point-division
bridges, p-adic formal groups, lattice reduction, isogenies, and quantum circuits remain mapped,
but none is automatically next merely because Mathlib lacks it. Route selection reopens only
when new evidence satisfies a recorded reconsideration trigger and the proposal gate.

## Research Engine v0
The engine normalizes **9 hypotheses** and retains
**8 outcome events**:
**8 migrated historical** and
**0 native**. Its historical
no-reopen guard matched four frozen cases; this is not predictive EIG calibration. Predictive
calibration currently contains **0 native
outcomes**. Before synthesis, the typed evidence layer materializes
**7 mechanism/property cells**:
**3 decided at desk** and
**2 eligible to emit a bounded research question**.
Its **3 desk decisions** are non-experimental and authorize
nothing. The generation layer currently emits
**2 source-grounded seeds**, with
**0 submitted proposals**,
**0 quality-cleared proposals**, and
**0 retained non-executable drafts**.
Creative output is untrusted and zero retained drafts is a valid cycle result.
Selected bounded explorations: **0** (none). Ready now: **0** (none). **0 candidates remain at intake** behind exact-mechanism or independent-validator hard gates.

## Research Engine v0.2 lifecycle
The v0.2 lifecycle currently contains
**0 immutable candidate snapshots**,
**0 admissible**,
**0 recommended**, and
**0 authorized**. Recommendation cannot create
authorization; authorization requires a separate dated owner decision bound to the exact
candidate digest. The eight historical events are referenced without migration, with both their
canonical review root and raw file bytes pinned.

Shadow intake contains **4 non-executable proposal
stubs** and **1 parked desired-property record**.
These are research questions, not hypotheses or candidates:
**0 admissible**,
**0 recommended**, and
**0 authorized**. `TASK-010` is accepted at
`85f85d4ca0b9dba323bfdd05ce8750d6db4732ac`. `TASK-018` froze the recursive
projective S17 contract, recorded the forward algebraic argument, replayed
bounded S4/S5 forward/reverse fixtures, and completed with a scoped
universal-reverse-projection blocker and zero retained hypotheses. `TASK-019`
then kernel-checked the generic fixed-degree projective-resultant common-root
theorem and the exact literal TASK-018 Sylvester unit-one bridge, and
completed with a scoped frozen-recursion blocker and zero retained
hypotheses. Current work is `TASK-020`, which keeps
`CELL-M-PKC-SMOOTH-M16` as a non-executable frozen-recursive-`C_r`
specialization question; the universal reverse `C16 → C2` induction remains
open downstream.
`TASK-008` remains parked because no hypothesis proposal has quality-cleared.

The Engine's bounded-exploration capability is
**true**, while the current decision's experiment
authorization is **false** and the promotion gate is
**false**. `GLV-SEMAEV-ITER-001` is complete; its
certificates and kernel-checked identities authorize no hypothesis run. `TASK-020` authorizes no
S17 expansion or evaluation, polynomial-system materialization, solver, cost inference, target
computation, or route promotion. Any later experiment needs
a new dated decision plus the normal fixed budgets, dependency order, and retained terminal
outcome.

## Active work protocol
`tasks/NEXT.md` is the queue router. ECDLP research is owned by
`tasks/ECDLP_RESEARCH.md`; product validation is owned by `tasks/KEYAI_PRODUCT.md`. Together they
retain 3-7 active task contracts. Product traffic, site work, pilots, and portability never count
as ECDLP progress.

The product authority is `repo/PRODUCT_MODEL.json`; `scripts/check_product_model.py` enforces its
claim boundary. Public surfaces must distinguish current capabilities, the reference deployment,
customer hypotheses, and future product direction.

The route authority is `repo/ECDLP_DECISION_SUBSTRATE.json`; its Markdown view is generated.
The engine policies are `repo/RESEARCH_ENGINE_V0.json`,
`repo/HYPOTHESIS_GENERATION_V0.json`, and
`repo/RESEARCH_ENGINE_LIFECYCLE_V0.json`; typed applicability is owned by
`repo/ECDLP_TYPED_EVIDENCE_V0.json`, materialized in
`data/typed_evidence_state.json`, and the combined generated state is
`data/research_engine_state.json`. The v0.2 lifecycle and shadow intake are
`data/research_engine_v02_state.json` and
`data/research_engine_shadow_intake.json`. The candidate-neutral validation contract lives in
`experiments/framework/`. No one file authorizes promotion by itself.

The hypothesis registry is `experiments/HYPOTHESES.yaml`. It records testable
directions, evidence, and exit criteria; it is not a theorem ledger.

The drift gate is `scripts/check_status_consistency.py`. Run it whenever stats,
frontier, graph, dashboard/site counters, tasks, or hypotheses change.

## Where to go deeper
`README.md` (the front door) · `repo/PRODUCT_MODEL.json` (product and MVP authority) ·
`repo/ECDLP_DECISION_SUBSTRATE.json` (route decisions) ·
`repo/RESEARCH_ENGINE_V0.json` (exploration policy and selector) ·
`repo/ECDLP_TYPED_EVIDENCE_V0.json` (claim-level applicability screens) ·
`repo/HYPOTHESIS_GENERATION_V0.json` (seed and proposal-quality policy) ·
`repo/RESEARCH_ENGINE_LIFECYCLE_V0.json` (immutable candidate lifecycle) ·
`repo/RESEARCH_ENGINE_V0_2_ACCEPTANCE.json` (19 regression cases) ·
`data/typed_evidence_state.json` (materialized mechanism/property cells) ·
`data/research_engine_state.json` (generated engine state) ·
`data/research_engine_v02_state.json` (generated lifecycle state) ·
`data/research_engine_shadow_intake.json` (non-executable shadow queue) ·
`tasks/NEXT.md` (queue router) · `tasks/ECDLP_RESEARCH.md` (research queue) ·
`tasks/KEYAI_PRODUCT.md` (product queue) ·
`experiments/HYPOTHESES.yaml` (hypotheses + exit criteria) · `PUBLISHABLE_UNITS.md` (the 3
standalone results) · `ROADMAP.md` (strategy & program) · `VERIFIED.md` (ledger) ·
`BARRIERS.md` (no-go map) · `notes/FOUNDATIONS.md` (Weil/Semaev ladder) ·
`notes/POINT_COUNTING_KEYSTONE.md` (the `#E=n` keystone) · `TRUST_REPORT.md` (trust boundary) ·
`data/frontier_map.json` (queryable per-claim status) ·
`experiments/framework/README.md` (candidate-evaluation contract).
