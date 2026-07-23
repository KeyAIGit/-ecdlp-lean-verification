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
the same branch. No task in this queue authorizes an experiment run or
destructive cleanup. Merge authority is delegated but requires green CI, a
reviewed scope, and a documented rollback path.

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

### TASK-010 - Periodic independent adversarial audit

Status: parked_until_independent_reviewer_available
Kind: review | ops
Hypothesis: none
Why it matters: An independent reviewer can still find architecture, scope, or
deletion risks that internal gates do not model.
Inputs:
- a stable, integrated project checkpoint
- all green local gates and GitHub CI
- a review packet covering architecture, formal trust, route decisions,
  experiment provenance, generated artifacts, and residual risks
Expected output:
- One independent adversarial review with severity-ranked findings.
- A disposition for every finding and a release/maintenance recommendation.
Exit criteria:
- Review happens at a meaningful stable checkpoint.
- Actionable findings are resolved or explicitly accepted with rationale.
- Review remains additional evidence and does not block otherwise authorized,
  green, rollback-safe merges.
Files allowed to edit:
- the final review packet and files needed to resolve accepted findings
Files that must be regenerated:
- all derived artifacts touched by accepted findings
How to verify:
- rerun local and GitHub gates after the final finding-resolution pass

### TASK-011 - Validate the external product pilot

Status: active
Kind: product | research | ops
Hypothesis: `CH-001` and `CH-002` in `repo/PRODUCT_MODEL.json`
Why it matters: The secp256k1 repository proves that the research-state loop can
work in one owner-operated environment. It does not prove that another team has
the same pain, can use the contracts, or will return. Product work should now
reduce that uncertainty instead of adding speculative platform features.
Inputs:
- `repo/PRODUCT_MODEL.json`
- the generated public workspace and route explorer
- one candidate external Lean/formalization team or repository
Expected output:
- A dated pilot brief naming the user, existing workflow, failure points, and
  narrow project boundary.
- One observed onboarding session using the current reference environment.
- A go/change/stop decision for `CH-001` and `CH-002`.
Exit criteria:
- A non-owner can identify current state, blockers, and next action in ten
  minutes or less.
- The user names a repeated workflow painful enough to test on a second project.
- No customer, retention, or willingness-to-pay claim is published without
  direct evidence.
Files allowed to edit:
- `repo/PRODUCT_MODEL.json`
- product research notes linked from that model
- public site generators and directly affected checks
Files that must be regenerated:
- `index.html`
- `dashboard.html`
- `explore.html`
How to verify:
- `python scripts/check_product_model.py`
- `python scripts/build_dashboard.py`
- `python scripts/check_status_consistency.py`
- browser validation on desktop and mobile

### TASK-012 - Build configurable intake after a pilot contract

Status: blocked_on_external_pilot_contract
Kind: product | data | ops
Hypothesis: exactly one validated customer hypothesis from `TASK-011`
Why it matters: A hosted or multi-project platform is justified only after a
real team exposes the minimum adapter boundary. Building it earlier would
replace evidence with architecture.
Inputs:
- a completed `TASK-011` pilot decision
- one external repository/corpus with permission to use it
- a minimal claim, evidence, task, and verifier-adapter contract
Expected output:
- Repository or corpus intake with a pinned source manifest.
- A workspace generated without editing KeyAI's generator code.
- One candidate run with captured verifier output, decision history, export,
  and rollback.
Exit criteria:
- A non-owner completes the ingest -> structure -> decide -> execute -> verify
  -> retain loop on the second project.
- The implementation satisfies the MVP provenance, state-drift, and external
  pilot metrics in `repo/PRODUCT_MODEL.json`.
- Authentication, billing, and additional verifier adapters remain out of
  scope unless the pilot requires them.
Files allowed to edit:
- only paths named by the future pilot implementation contract
Files that must be regenerated:
- every public, agent-facing, and machine-readable view affected by the adapter
How to verify:
- adapter-specific tests
- product-model and repository gates
- an observed end-to-end pilot run

## Task Contract Template

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
