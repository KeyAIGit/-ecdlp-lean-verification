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

Current central task: `TASK-009` in `tasks/ECDLP_RESEARCH.md`.

Current bounded structural binding:
`RS-2026-07-24-001` / `GLV-SEMAEV-ITER-001` / `R-GLV-SEMAEV` /
`HYP_GLV_SEMAEV_001` / `TASK-009`.
No experiment hypothesis or attack route is promoted.

Architecture sources: `repo/FORMAL_SUBSTRATE.json`,
`repo/RESEARCH_ENGINE_V0.json`, and `repo/ARTIFACTS.yaml`.

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
