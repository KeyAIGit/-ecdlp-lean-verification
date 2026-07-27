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

Current central task: `TASK-016` in `tasks/ECDLP_RESEARCH.md`.

`TASK-010` is accepted at
`85f85d4ca0b9dba323bfdd05ce8750d6db4732ac`. `TASK-008` remains the parked
proposal-intake lane because TASK-016 is a non-executable semantics bridge,
not a hypothesis candidate or experiment.

Current scientific activation order:

1. `TASK-014` has closed the first evidence and arithmetic desk cycle; its
   native phase remains blocked.
2. `TASK-015` completed the M16 symbolic desk with a scoped blocker and zero
   retained hypotheses; the cell remains open and non-executable.
3. `TASK-016` gives sole desk priority to the exact source-faithful ideal and
   recovery semantics for `CELL-M-PKC-SMOOTH-M16` /
   `RSI-D8BBA6340789`.
4. The auxiliary-curve cell stays parked until a primary source supplies a
   finite search domain with a completeness criterion.
5. Any later candidate, solver, or experiment still requires the normal
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
