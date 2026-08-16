# Contract map

This directory contains hand-maintained machine-readable contracts. It is not a
collection of generated status files. Generated state belongs under `data/` or
in the rendered Markdown and HTML views named in
[`../REPOSITORY_ARCHITECTURE.md`](../REPOSITORY_ARCHITECTURE.md).

## Contract families

| Need | Primary contract | Generated or public view |
|---|---|---|
| Exact ECDLP target, route dispositions, gates, and priorities | `ECDLP_DECISION_SUBSTRATE.json` | `ECDLP_DECISION_SUBSTRATE.md`, `../explore.html` |
| Formal result families, dependencies, blockers, and release boundary | `FORMAL_SUBSTRATE.json` | `../data/knowledge_graph.json`, Workspace formal tab |
| Typed evidence and mechanism/property intersections | `ECDLP_TYPED_EVIDENCE_V0.json` | `../data/typed_evidence_state.json` |
| Claim, hypothesis, experiment, and lifecycle semantics | `RESEARCH_CLAIMS_V0.json`, `RESEARCH_ENGINE_V0.json`, `RESEARCH_ENGINE_LIFECYCLE_V0.json` | generated engine state under `../data/` |
| Product category, present capability, and MVP gate | `PRODUCT_MODEL.json` | `../index.html`, `../results.html`, `../dashboard.html` |
| External pilot qualification, safety, and evidence rules | `PILOT_PROTOCOL.json` | `../pilot.html` |
| Whole-repository ownership and edit policy | `ARTIFACTS.yaml` | `../REPOSITORY_ARCHITECTURE.md` |
| Workflow and branch inventories | `AUTOMATION_INVENTORY.json`, `BRANCH_INVENTORY.json` | their dedicated checks and review records |

## Editing rules

1. Change the contract that owns the decision, not a generated view.
2. Regenerate every dependent artifact and run its `--check` gate.
3. Keep formal proof, empirical support, route disposition, recommendation, and
   owner authorization as separate fields.
4. A missing foundation does not become a priority unless the decision contract
   records why it matters to an admissible route.
5. Do not use product or pilot evidence as mathematical progress, or vice versa.

The exhaustive path classification and cleanup policy is in `ARTIFACTS.yaml`.
Live counts remain in [`../STATUS.md`](../STATUS.md), not in this directory.
