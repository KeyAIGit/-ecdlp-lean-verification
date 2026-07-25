# ECDLP research queue

This queue owns work that changes the evidence, uncertainty, or formal boundary
of the plain single-target secp256k1 ECDLP program. Product traffic, site work,
pilot activity, and portability rehearsals do not count as progress here.

Canonical start order:

1. Read `STATUS.md`.
2. Read `repo/ECDLP_DECISION_SUBSTRATE.json`.
3. Read `repo/RESEARCH_ENGINE_V0.json`.
4. Read this queue.
5. Load `repo/FORMAL_SUBSTRATE.json` only for a selected formal dependency.

## Active tasks

### TASK-013 - Build and calibrate Research Engine v0

Status: active
Kind: research | data | experiment | ops
Hypothesis: engine-level selection policy; bounded candidates remain tied to
their named hypotheses
Why it matters: The repository needs a closed proposal -> selection -> bounded
exploration -> validation -> retention loop without weakening the independent
promotion gate. This task lands and validates that loop before any selected toy
candidate runs.
Inputs:
- `repo/RESEARCH_ENGINE_V0.json`
- `repo/ECDLP_DECISION_SUBSTRATE.json`
- `experiments/HYPOTHESES.yaml`
- historical experiment artifacts under `experiments/`
Expected output:
- Separate exploration and promotion gates.
- Seven-outcome result taxonomy, with formal `proved` separated from empirical
  `supported`, and a five-class gap taxonomy.
- All nine hypotheses and historical runs normalized without rewriting
  provenance.
- Deterministic selector with boolean hard rejection, preregistered expected
  information gain per normalized budget, dependency order, and retrospective
  no-reopen tests.
- An ordered queue of at most three toy-only explorations; an empty queue is
  required when no proposal clears every scientific gate.
- Append-only outcome events that regenerate hypothesis and route evidence
  state.
Exit criteria:
- Promotion and exact-target work remain disabled.
- Every selected exploration has a mechanism or named validator role,
  prediction, baseline, fixed budget, stop condition, and independent
  validator.
- Every native matrix instance binds a hashed result to an independently
  recomputed classification from raw artifacts through a source-commit-bound
  pure validator. The allowed instance outcomes and exhaustive aggregate
  precedence are frozen before execution; the request contains neither the
  claimed value, terminal outcome, nor result digest.
- A named mechanism is not selectable until its exact map, algebraic
  presentation, exceptional locus, relation semantics, recovery path, and
  implementation identity are frozen.
- Native predictive calibration excludes migrated historical outcomes.
- Historical no-reopen cases reject known dead ends without claiming
  predictive selector calibration.
- A new outcome event deterministically updates the generated engine state and
  knowledge graph.
- All repository gates and generated-artifact checks pass.
Files allowed to edit:
- `repo/RESEARCH_ENGINE_V0.json`
- `repo/ECDLP_DECISION_SUBSTRATE.json`
- `experiments/engine/`
- `experiments/HYPOTHESES.yaml`
- `data/research_engine_state.json`
- task, generator, validator, graph, site, and CI files directly affected by
  the engine contract
Files that must be regenerated:
- `data/research_engine_state.json`
- every derived artifact named by `repo/ARTIFACTS.yaml`
How to verify:
- `python scripts/build_research_engine_state.py --check`
- `python scripts/check_research_engine.py`
- `python scripts/test_research_engine.py`
- `python scripts/check_ecdlp_decision_substrate.py`
- the full repository gate battery

### TASK-008 - Maintain evidence-gated candidate intake

Status: active
Kind: research | data | ops
Hypothesis: none; intake evaluates proposals before hypothesis promotion
Why it matters: New progress must enter through source-pinned mathematical
evidence or a concrete mechanism, not by silently reviving a parked route.
Inputs:
- new primary literature, author artifacts, or a concrete candidate proposal
- `repo/ECDLP_DECISION_SUBSTRATE.json`
- `data/attack_registry.json`
- `repo/RESEARCH_ENGINE_V0.json`
Expected output:
- A dated evidence delta tied to one route, threat model, and gap class.
- A pass/fail result for the relevant exploration or promotion gate.
- Either no disposition change or an explicit proposed decision delta.
Exit criteria:
- Scope and provenance are complete.
- Conditioned, leakage, quantum, and plain-input claims remain distinct.
- Intake alone cannot authorize promotion or exact-target work.
Files allowed to edit:
- canonical evidence and decision registries
- directly stale architecture, status, source, and generated view files
Files that must be regenerated:
- every affected derived artifact
How to verify:
- `python scripts/check_ecdlp_decision_substrate.py`
- `python scripts/check_research_engine.py`
- the full repository gate battery

### TASK-009 - Implement only a newly selected promotion foundation

Status: blocked_on_promotion_decision
Kind: theorem | experiment | ops
Hypothesis: exactly one future hypothesis named by a dated promotion decision
Why it matters: Missing formal infrastructure is valuable only when it resolves
a concrete uncertainty in a route that has passed promotion review.
Inputs:
- a dated route-selection decision
- one promoted route and matching hypothesis
- one minimal foundation contract with a falsifiable exit criterion
Expected output:
- The smallest formal or computational bridge needed for the selected route.
- Independent validation and full cost/provenance records.
- A route disposition update whether the result is positive or negative.
Exit criteria:
- The work answers only its named uncertainty.
- Unrelated foundations and hypotheses remain parked.
- Lean results pass kernel, axiom, and no-`sorry` gates.
Files allowed to edit:
- only paths declared by the future promoted task
Files that must be regenerated:
- every affected derived artifact
How to verify:
- route-specific checks plus the full repository gate battery

### TASK-010 - Independent adversarial audit at a stable checkpoint

Status: active_review_preparation
Kind: review | research | ops
Hypothesis: none
Why it matters: An independent reviewer should attack the split gates, selector,
candidate mechanisms, validation independence, and promotion boundary before
Research Engine v0 is treated as stable.
Inputs:
- a green Research Engine v0 branch
- `notes/reviews/RESEARCH_ENGINE_V0_CLAUDE_BRIEF.md`
- policy, generated state, outcome events, and retrospective fixtures
- architecture, formal trust, route decisions, and residual risks
Expected output:
- Severity-ranked findings with evidence.
- A disposition for every finding.
- A release or revision recommendation.
Exit criteria:
- Every blocking finding is resolved or explicitly accepted with rationale.
- The review does not silently edit canonical state or promote a route.
- All affected checks are rerun after finding resolution.
Files allowed to edit:
- review packet and files required to resolve accepted findings
Files that must be regenerated:
- all derived artifacts touched by accepted findings
How to verify:
- full local gates and GitHub CI
