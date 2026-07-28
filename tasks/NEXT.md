# Work queue router

This file is the single low-context entrypoint, not a mixed KPI surface.
Choose the queue that owns the objective:

| queue | canonical file | objective | primary KPI family |
|---|---|---|---|
| ECDLP research | `tasks/ECDLP_RESEARCH.md` | Reduce uncertainty about plain single-target secp256k1 ECDLP | Mechanisms resolved, independently validated outcomes, false promotions, information gain per cost |
| KeyAI product | `tasks/KEYAI_PRODUCT.md` | Validate the control plane with external formal-research teams | Orientation time, provenance completeness, state drift, pilot completion, return evidence |

Product work never counts as ECDLP progress. Theorem volume and toy
measurements count only when they resolve a named ECDLP uncertainty. ECDLP
results never count as external product validation.

Canonical start order:

1. Read `STATUS.md`.
2. Read this router.
3. Open exactly one owning queue.
4. Read the canonical policy named by that queue.
5. Execute only a task contract from that queue.

Current central task: none. `TASK-021` is completed; a successor must be
introduced by a new narrow task contract against the still-open complete-cost
barrier before any further research execution.

`TASK-010` is accepted at
`85f85d4ca0b9dba323bfdd05ce8750d6db4732ac`. `TASK-008` remains the parked
proposal-intake lane. Closing TASK-021 created no executable hypothesis,
experiment authorization, or route promotion.

Current scientific activation order:

1. `TASK-014` has closed the first evidence and arithmetic desk cycle; its
   native phase remains blocked.
2. `TASK-015` completed the M16 symbolic desk with a scoped blocker and zero
   retained hypotheses; the cell remains open and non-executable.
3. `TASK-016` completed with a scoped blocker: a fixed affine S3 tree is exact
   only after base-field-lift and nonidentity-prefix localization. The M16
   cell remains open and non-executable.
4. `TASK-017` completed the exact set-theoretic homogeneous projective-tree
   bridge, named exceptional-fiber classification, recovery domain, and GLV
   lift-sign replay.
5. `TASK-018` completed with a scoped blocker and zero retained hypotheses. It
   freezes the recursive projective S17 contract with fixed degrees and the
   literal Sylvester determinant under the frozen coefficient, argument, and
   row order, with coefficient unit 1 in that definition and projective
   rescaling governed by the declared multidegree. It records the forward
   algebraic argument and replays bounded S4/S5 forward/reverse fixtures; the
   generic C16 forward implication is not computationally replayed or kernel
   checked. The universal reverse projection above S4 remains unproved.
6. `TASK-019` completed with a scoped blocker and zero retained hypotheses.
   The generic fixed-degree projective-resultant/common-projective-root
   equivalence and the literal TASK-018 Sylvester determinant bridge are
   kernel checked, including zero forms, degree drop, affine roots, `[1:0]`,
   and coefficient unit exactly `1`. The general coefficient-map theorem does
   not bind the actual frozen recursive `C_r`.
7. `TASK-020` completed with a scoped blocker and zero retained hypotheses.
   The actual frozen family, coefficient-map specialization, affine and
   `[1:0]` branches, uniform output-degree bound, and unconditional one-step
   common-projective-root equivalence are kernel checked under the literal
   unit-one convention.
8. `TASK-021` completed the exact projective homogenization bridges and
   universal recursive witness extraction `C16 → C2` for
   `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`. The kernel-checked chain has
   fourteen valid projective intermediate slots; `[1:0]` is allowed and
   `[0:0]` is excluded at every level. The complete cost bridge remains open,
   and TASK-021 authorizes no S17 materialization, solver, or cost claim.
9. The auxiliary-curve cell stays parked until a primary source supplies a
   finite search domain with a completeness criterion.
10. Any later candidate, solver, or experiment still requires the normal
   review gates and a separate dated authorization.

These entries freeze further engine-schema expansion by default. They do not
authorize a solver, a route promotion, or an exact-target computation.

Most recent completed bounded structural binding:
`RS-2026-07-24-001` / `GLV-SEMAEV-ITER-001` / `R-GLV-SEMAEV` /
`HYP_GLV_SEMAEV_001` / `TASK-009`.
Only the diagonal `C3` covariance survived. No experiment hypothesis or attack
route is promoted; new work enters through proposal intake.
Proposal intake begins with a regenerated typed mechanism/property cell. A
desk-decided cell cannot emit a seed, and no generated seed or draft authorizes
execution.

Architecture sources: `repo/FORMAL_SUBSTRATE.json`,
`repo/ECDLP_TYPED_EVIDENCE_V0.json`, `repo/RESEARCH_ENGINE_V0.json`,
`repo/RESEARCH_CLAIMS_V0.json`, `repo/HYPOTHESIS_GENERATION_V0.json`,
`repo/RESEARCH_ENGINE_LIFECYCLE_V0.json`,
`repo/RESEARCH_ENGINE_V0_2_ACCEPTANCE.json`, and `repo/ARTIFACTS.yaml`.

## Task contract template

```md
# TASK

ID:
Status:
Kind: theorem | experiment | data | product | site | publication | research | review | ops | agent
Hypothesis:
Why it matters:
Inputs:
Expected output:
Exit criteria:
Files allowed to edit:
Files that must be regenerated:
How to verify:
```
