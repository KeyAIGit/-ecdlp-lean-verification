# Research Engine v0 to v0.2 migration

Date: 2026-07-25

Status: shadow, non-executing, and not a route-promotion decision.

## Why this migration exists

Research Engine v0 retained outcomes and ranked supplied candidates well, but
candidate creation, scientific truth, mutable lifecycle state, and
authorization were too tightly coupled. v0.2 separates those concerns while
preserving the eight historical events exactly.

## Architecture

The migrated control plane has four layers:

1. Typed evidence computes source claims, target properties, mechanism
   requirements, applicability cells, and zero-cost desk decisions.
2. Claim state represents
   `route -> research_question -> claim -> mechanism_variant -> evidence_event`.
   Claim disposition is separate from assurance.
3. The generation plane emits research-question seeds, compiles structured
   proposals through five digest-bound reviews, and may retain a
   non-executable quality-cleared draft. A fluent prose packet cannot replace
   its mechanism, prediction, full-cost, and validator-design contracts.
4. The v0.2 lifecycle consumes immutable candidate snapshots, computes
   admissibility and an exhaustive bounded portfolio, and keeps recommendation
   distinct from dated owner authorization.

`data/research_engine_shadow_intake.json` is the left-hand shadow queue. It is
derived from unread primary sources, typed property-resolution cells, missing
cost bridges, and claim reopening conditions. Its rows are not hypotheses or
executable candidates.

## Immutable and mutable data

An immutable candidate snapshot owns mechanism, prediction, cost, validator,
evidence, and frozen scoring contracts. Any scientific edit mints a new
digest, invalidating prior reviews and creating a new calibration subject.
Mechanism, validator, and bounded-experiment snapshots must also bind a
registered quality-cleared draft containing the exact proposal digest and all
five review-artifact digests. The snapshot and draft must carry the same
protected-main-reachable or immutable-evidence-tagged `source_commit`.

A validator may be present in a proposal only as
`design_only_unverified`. Lifecycle readiness requires
`ready_evidence_bound`: path independence and artifact recomputation are
verified separately, while source independence is bound to an independent
human attestation. Self-declared independence booleans are insufficient.

Append-only lifecycle events own:

`idea -> screened -> mechanism_specified -> validator_ready -> admissible
-> recommended -> authorized -> running -> terminal`

The engine computes `admissible` and `recommended`. Creating `authorized`
requires both a separate dated owner decision bound to the exact candidate
digest and the matching append-only lifecycle transition. The policy names the
allowed owner role, requires a timezone-aware timestamp, and applies the latest
decision so a revocation cannot be shadowed by an older approval. Terminal and
superseded candidates occupy no current selection slot; an already authorized
candidate remains visible after its recommendation slot is released. Any
invalid append-only lifecycle event fails the whole selection cycle closed; it
cannot satisfy a dependency while merely leaving a warning behind.

## Historical-event migration

The files `REO-2026-07-24-001` through `008` are referenced through a
version-pinned reader. They are not rewritten to acquire v0.2 fields.

- Canonical JSON review root:
  `d9de2351a499d395d09005199aac73744c1bf212ff9759ceed5d229d076ca7a3`.
- Eight raw-file SHA-256 values are pinned independently by
  `scripts/build_research_engine_v02_state.py`.
- Historical migrations and structural evidence are excluded from Brier
  calibration.
- Native calibration events are keyed by unique append-only `event_id`; a
  duplicated record is rejected rather than counted as another observation.

## Scientific semantics retained

- `R-GLV-SEMAEV` remains `open_parked`.
- The independent `u_i = x_i^3` fixed-target quotient is a bounded-negative
  child claim.
- Positive covariance theorems have `lean_kernel` assurance.
- Exhaustive stabilizer classification has `certificate_replayed` assurance,
  not `lean_kernel`.
- P0-P4 remain historical empirical evidence.
- A phase-preserving successor needs a new exact mechanism identity.
- Faithful Petit, Weil descent, the PKC smooth-subgroup construction, the PKC
  auxiliary-curve construction, and historical toy P4 are distinct.

## Selection and calibration

Scoring reports low, base, and high information-gain scenarios, rank
sensitivity, robustness, and an explicit uncalibrated state. Portfolio
selection is exhaustive for at most twelve candidates and accounts for
budgets, dependencies, correlations, diversity, and shared setup. Larger
sets produce a coverage artifact rather than silent truncation. Dependencies
must already have an accepted terminal outcome at the required version; merely
placing a prerequisite in the same portfolio does not satisfy it. Calibration
outcome records cannot satisfy dependencies without the corresponding valid
terminal lifecycle transition. Only one active immutable version of a
candidate ID may enter a comparison.

Current generated state contains no lifecycle candidates. Shadow intake has
four non-executable proposal stubs:

1. Kudo CANS 2018 primary-source ingestion.
2. PKC smooth-subgroup applicability and desk-cost analysis.
3. PKC auxiliary-curve construction and applicability.
4. Faithful generalized-root and recovery full-cost specification.

The desired phase-preserving GLV quotient remains parked because no exact map
exists.

## Acceptance and regeneration

The nineteen owner regressions are machine-mapped in
`repo/RESEARCH_ENGINE_V0_2_ACCEPTANCE.json`. The principal commands are:

```text
python3 scripts/build_typed_evidence_state.py --check
python3 scripts/research_claims.py --check
python3 scripts/build_research_engine_state.py --check
python3 scripts/build_research_engine_v02_state.py --check
python3 scripts/build_research_shadow_intake.py --check
python3 scripts/check_research_engine_v02_acceptance.py
python3 scripts/check_scientific_semantics.py
python3 scripts/check_generated_fixpoint.py --check
```

This migration authorizes zero experiments, recommends zero current
candidates, promotes zero routes, and performs zero exact-target runs.
