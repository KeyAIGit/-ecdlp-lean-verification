# NEXT.md

This is the only active work queue. It contains current contracts, not a progress
diary. Completed work remains discoverable in Git history, `VERIFIED.md`, and the
durable notes linked from `STATUS.md`.

Canonical start order:

1. Read `STATUS.md`.
2. Read `repo/ECDLP_DECISION_SUBSTRATE.json`.
3. Read this file.
4. Load `repo/FORMAL_SUBSTRATE.json` for Lean dependency and release decisions.
5. Load `experiments/HYPOTHESES.yaml` only when a task explicitly names a
   hypothesis.

The three maps have different owners: `data/frontier_map.json` classifies the
claim corpus, `repo/FORMAL_SUBSTRATE.json` maps the Lean release frontier, and
`repo/ECDLP_DECISION_SUBSTRATE.json` decides route applicability and project
priority for the exact secp256k1 objective. A missing Mathlib foundation does
not authorize work by itself.

If prose conflicts with a canonical or generated registry, correct the prose in
the same branch. No task in this queue authorizes an experiment run, a merge, or
piecemeal Claude review.

## Active Tasks

### TASK-008 - Maintain evidence-gated candidate intake

Status: active
Kind: research | data | ops
Hypothesis: none; intake evaluates proposals before hypothesis promotion
Why it matters: Decision `RS-2026-07-22-001` selected no current route. Future
progress must enter through new mathematical evidence, not by silently reviving
the last experiment or expanding a convenient formal library.
Inputs:
- new primary literature, author artifacts, or a concrete candidate proposal
- `repo/ECDLP_DECISION_SUBSTRATE.json`
- `data/attack_registry.json`
- `experiments/framework/`
Expected output:
- A dated evidence delta tied to one declared route and threat model.
- A pass/fail result for every proposal-level acceptance requirement.
- Either no disposition change, or a proposed new route-selection decision with
  an exact reconsideration trigger.
Exit criteria:
- New evidence is source-pinned, scope-qualified, and cross-linked.
- Conditioned, leakage, quantum, and plain-input claims remain distinct.
- No hypothesis or conditional foundation changes state inside intake alone.
Files allowed to edit:
- canonical evidence/decision registries and their generators
- directly stale architecture, status, and source prose
- candidate records under `experiments/framework/`
Files that must be regenerated:
- every derived artifact named by `repo/ARTIFACTS.yaml`
How to verify:
- `python scripts/check_ecdlp_decision_substrate.py`
- the full repository gate battery

### TASK-009 - Implement only a newly selected foundation

Status: blocked_on_new_route_selection
Kind: theorem | experiment | ops
Hypothesis: exactly one future hypothesis named by the new decision
Why it matters: Missing Mathlib infrastructure is valuable only when it resolves
a concrete uncertainty in a route that already passes the proposal gate.
Inputs:
- a dated route-selection decision superseding `RS-2026-07-22-001`
- one promoted route and matching hypothesis
- one minimal foundation contract with a falsifiable exit criterion
Expected output:
- The smallest formal or computational bridge needed for the selected route's
  next decision.
- Independent validation and full cost/provenance records where computation is
  involved.
- A route disposition update whether the result is positive or negative.
Exit criteria:
- The selected work answers its named uncertainty without claiming more.
- All unrelated foundations and hypotheses remain parked.
- Lean-facing results pass kernel, axiom, and no-`sorry` gates.
Files allowed to edit:
- only the paths declared by the future promoted task contract
Files that must be regenerated:
- every derived artifact affected by that contract
How to verify:
- route-specific checks plus the full repository gate battery

### TASK-010 - Final whole-program Claude/Opus review

Status: blocked_on_program_freeze_and_opus_availability
Kind: review | ops
Hypothesis: none
Why it matters: The user requested one adversarial review of the integrated
program, not repeated review after each tranche.
Inputs:
- the final unmerged architecture branch
- all green local gates and GitHub CI
- a review packet covering architecture, formal trust, route decisions,
  experiment provenance, generated artifacts, and residual risks
Expected output:
- One Claude/Opus adversarial review with severity-ranked findings.
- A disposition for every finding and a final merge recommendation.
Exit criteria:
- Review happens only after the program state is frozen for evaluation.
- Actionable findings are resolved or explicitly accepted with rationale.
- Merge remains a separate human decision.
Files allowed to edit:
- the final review packet and files needed to resolve accepted findings
Files that must be regenerated:
- all derived artifacts touched by accepted findings
How to verify:
- rerun local and GitHub gates after the final finding-resolution pass

## Task Contract Template

```md
# TASK

ID:
Status:
Kind: theorem | experiment | data | site | publication | ops | agent
Hypothesis:
Why it matters:
Inputs:
Expected output:
Exit criteria:
Files allowed to edit:
Files that must be regenerated:
How to verify:
```
