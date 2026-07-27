# Opus 5 handoff: Research Engine v0 scientific audit

> **FROZEN HISTORICAL SNAPSHOT.** This handoff predates the merged v0 baseline
> and is retained for provenance only. Current remediation is governed by
> `RESEARCH-ENGINE-V0.2-SANITATION-001`, `TASK-010`, and
> `notes/reviews/RESEARCH_ENGINE_V0_2_BASELINE_AUDIT.md`.

## Role

Act as an independent mathematical and experimental-design reviewer. Do not
merge either implementation and do not optimize for agreement with Codex or
the earlier Claude prototype.

Repository: `KeyAIGit/-ecdlp-lean-verification`

Primary branch to review once published: `agent/research-engine-v0`

Comparison branch: `claude/research-engine-v0` at `b1bc926`

Base: `origin/main` at `1a1b5ddba7e9a6e3d40f189892e83529f5bc6616`

## Current checkpoint

An initial independent review found four blocking scientific issues, and the
branch now takes the conservative disposition:

- `RE0-001` is intake with `missing_independent_validator=true`; the former
  summary-field comparator is now only a framework fixture.
- `RE0-002` and `RE0-003` are intake with
  `missing_exact_mechanism=true` and `missing_independent_validator=true`.
- the selector returns `0 selected / 0 ready`;
- native validators emit canonical per-instance outcomes, and the Engine
  derives the event label through a frozen exhaustive precedence;
- Ward EDS event `004` is `supported` only for the torsion identity;
- partially validated event `007` is `inconclusive`.

Additional adversarial hardening after the first security pass:

- framework fixtures cannot satisfy a scientific validator gate by metadata
  reassignment; policy validation, selection, and run replay accept implemented
  validators only under `experiments/engine/validators/`;
- the eight migrated outcomes are review-anchored by one root digest in
  validator code, so changing an event and its policy digest together still
  fails. This is deliberately described as review-anchored, not absolutely
  immutable: an intentional re-baseline must change event, policy, and code in
  the same reviewed diff.

Treat these as proposed remediations to attack, not conclusions to endorse.
Your highest-leverage contribution is now either an exact quotient
specification or a precise obstruction, plus a validator/certificate design
that can genuinely recompute from raw artifacts.

## Why this review exists

The useful parts of the Claude decision-layer prototype have already been
integrated into the repository-native Engine: boolean gates before scoring,
computed EIG, threat-model-first rejection, retrospective checks, `supported`
as an empirical outcome, separate threat/decision/evidence axes, and explicit
decision deltas.

The remaining risks are scientific rather than cosmetic:

1. A validator must recompute from raw evidence rather than compare two
   producer-supplied summaries.
2. A proposed GLV/Semaev quotient is not a mechanism until its map, algebraic
   presentation, exceptional locus, relation semantics, and recovery path are
   exact.
3. Every native measurement pattern must map mechanically to one outcome; a
   researcher must not choose between `falsified`, `bounded_negative`, and
   `inconclusive` after seeing data.
4. Historical migration labels must reproduce the source artifacts without
   turning scope-only confirmations into negative attack evidence.

## Task A: exact quotient feasibility

Audit `RE0-002-NONREDUNDANT-INVARIANT-QUOTIENT` and
`RE0-003-M3-INVARIANT-F4-SCALING` in `repo/RESEARCH_ENGINE_V0.json`.

Determine whether a mathematically faithful nonredundant quotient can be
specified for the committed GLV/Semaev setting. A valid proposal must freeze:

- the group action and exact invariant map;
- source and target rings;
- generators or elimination ideal;
- saturation/localization and every excluded exceptional component;
- orbit and stabilizer treatment;
- the map between quotient solutions and the original EC relation set;
- duplicate counting and sign handling;
- recovery of the original relation;
- the exact implementation entrypoint and independent validation plan;
- a prediction that distinguishes a scaling mechanism from a fixed orbit-size
  constant.

If any item is unavailable, conclude that RE0-002 is mechanism-development
intake rather than a selectable experiment. Prefer a minimal counterexample or
well-definedness obstruction over optimistic prose.

## Task B: raw-artifact validation contract

Audit `scripts/research_engine_lib.py`,
`experiments/engine/validators/`, and the run schemas.

Design the smallest validator contract that can recompute the decisive result
from raw, hashed artifacts. It must not receive the producer's claimed value,
result digest, supported value, or outcome label. Specify:

- raw ideal/generator artifact format;
- raw external solver output and basis/certificate format;
- independent EC relation-replay artifact;
- tool identity, version, command, seed, and source-commit provenance;
- which parts can be checked by a capability-restricted pure validator;
- which independence claims remain human/source-review obligations;
- an exhaustive aggregate classifier from validated instance results and
  resource states to one terminal outcome.

Do not call a comparison of two fields in one producer-authored JSON document
independent validation.

## Task C: historical outcome audit

Review all eight files under `experiments/engine/outcomes/` against their cited
`README.md`, `RESULTS.md`, run manifests, and validators.

Pay particular attention to:

- `REO-2026-07-24-004`: its source says it confirms known torsion structure and
  draws no attack or no-advantage conclusion.
- `REO-2026-07-24-007`: its validation is partial and the decisive claim is not
  validated.

For every event, independently return the uniquely justified label from:

`proved`, `supported`, `falsified`, `bounded_negative`, `inapplicable`,
`inconclusive`, `resource_exhausted`.

Separate "the measured identity was supported" from "the attack mechanism was
negatively tested." Preserve exact scope and reopening conditions.

## Output

Return:

1. Severity-ranked findings with exact file and line references.
2. A concrete quotient specification or a precise reason it is not yet one.
3. A raw-artifact validator design and outcome-classifier table.
4. A table of all eight historical labels with source-backed justification.
5. A verdict on which candidates, if any, may be selected or marked ready.
6. Residual scientific risks that cannot be removed mechanically.

No claim of ECDLP progress, no direct secp256k1 experiment, no merge.
