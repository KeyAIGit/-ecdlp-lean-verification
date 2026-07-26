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

Current central task: `TASK-010` in `tasks/ECDLP_RESEARCH.md`.

`TASK-008` remains the parked proposal-intake lane. It does not become active
while the v0.2 sanitation lifecycle is in remediation.

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
