# HYP-M16-SOLVER-SLOPE-001 — validator design

Date: 2026-07-30

Status: `DESIGN ONLY / UNVERIFIED`

The validator must be independently authored and must not import producer or
solver orchestration code. This document names what it must recompute before
any future authorization can exist.

## Proposal-integrity checks

Before accepting an experiment bundle, the validator must:

- recompute the proposal JSON digest;
- recompute the bound mechanism-note and validator-note SHA-256 values;
- recompute prompt and evidence-context digests from their canonical
  definitions;
- reject sentinel or design-only implementation identities;
- verify that every implementation digest names the exact executable bytes
  used by the run;
- verify that every source commit is allowed by the scientific-provenance
  policy and that the recorded protected ref resolves to its pinned commit.

The current proposal deliberately fails the executable-identity and
independence checks.

## Raw artifacts

One immutable record per curve block, arm, seed, fixed DLP target, and
relation attempt must contain primitive data rather than a claimed outcome:

- curve parameters, subgroup generator/order, `Q`, and target commitment;
- per-attempt `alpha_j`, `beta_j`, `R_j`, commitment time, and
  pre-solver-randomness transcript;
- `D`, its factorization, complete membership representation, and exact
  coordinate root/lift histogram;
- exceptional-chart policy and either its input-level completeness theorem
  or every projective branch;
- input polynomial system and canonical monomial order;
- solver version/digest, command, seed, trace, timeout disposition, matrices,
  and resource receipt;
- every raw candidate assignment;
- every accepted and rejected lift/recovery disposition;
- recovered signed points and canonical coefficient row
  `(c_1j,...,c_Uj,-beta_j)` with right-hand side `alpha_j`;
- incremental rank transcript over `Z/qZ`;
- linear-algebra input/output, recovered `z`, and `[z]G = Q` verification;
- the full prime-field primitive-operation vector plus CPU, wall, memory,
  storage, and parallel-work receipts;
- experimental curve/control search costs, separated from the attack ledger.

Producer fields named `claimed_outcome`, `claimed_exponent`,
`claimed_relation`, `claimed_rank`, or `claimed_speedup` are
non-authoritative.

## Independent recomputation

The validator must:

1. reconstruct each finite field, curve, subgroup, generator, and `Q`;
2. verify primality/order claims or bind a separate certificate;
3. recompute `H_D`, liftability, `U`, root histograms, cosets, randomized
   DAG outputs, and all cross-family matching claims;
4. recompute every `R_j = [alpha_j]G + [beta_j]Q` and verify commitment
   ordering before solver randomness;
5. evaluate every membership and `S3`/projective equation;
6. recover signed points without producer recovery code;
7. replay exact group relations and reject extension-only or exceptional
   failures;
8. canonicalize rows and verify
   `sum_i c_ij lambda_i - beta_j z = alpha_j (mod q)`;
9. replay duplicate collapse and incremental rank over `Z/qZ`;
10. recompute sparse matrices, linear algebra, candidate `z`, and
    `[z]G = Q`;
11. expand every attack operation, solver operation, Pollard operation, and
    linear-algebra operation into the frozen `PFPO` accounting;
12. recompute exact repeated-tuple/stabilizer/yield diagnostics and `k/D`,
    `k/U`;
13. fit separately preregistered `s_attempt`, `s_total`, and every paired
    `Delta_c`, including frozen timeout/right-censoring rules;
14. recompute the composite positive-margin metric without deleting sizes,
    seeds, attempts, or controls after seeing outcomes;
15. evaluate the frozen outcome matrix mechanically.

## Independence axes

Required before execution:

- path independence: different arithmetic/recovery implementation;
- artifact independence: decisive claims reconstructed from primitive raw
  records;
- source independence: at least one reviewer not sharing proposal context;
- producer and validator identities differ;
- solver output is treated as adversarial input;
- fault injection covers coefficient-stream mutation, target substitution,
  row-sign mutation, omitted exceptional branches, timeout deletion,
  rank inflation, and operation-count tampering.

The present state satisfies none of these requirements. A future review may
specify them, but may not mark them verified without evidence.

## Failure labels

Apply the following deterministic precedence:

1. `INVALID_IMPLEMENTATION`: an accepted candidate, coefficient stream,
   rank result, or candidate `z` fails independent exact replay. Stop and
   emit no scientific outcome.
2. `INAPPLICABLE`: no source-faithful regime and causal controls can be
   frozen under policy.
3. `RESOURCE_EXHAUSTED`: an immutable authorized cap ends before a decision.
4. `INCONCLUSIVE/ARTIFACT`: leakage, unmatched control, conditioning,
   seed/order dependence, or accounting invalidates causal interpretation.
5. `FALSIFIED/KNOWN_REPRESENTATION_EFFECT`: a frozen equivalence test shows a
   causal control reproduces the effect, or only a bounded
   composed-vs-unfactored encoding constant remains.
6. `SUPPORTED/SUPPORTED_TOY_ONLY`: all exact checks and all three positive
   margins pass.
7. `BOUNDED_NEGATIVE`: no equivalence classification applies, but a cost or
   causal-gap criterion fails with adequate precision.
8. `INCONCLUSIVE`: every other valid but underpowered or censored case.

An implementation failure invalidates the run; it does not by itself refute
the mathematical mechanism. Failure to build a valid family is
`INAPPLICABLE`, not `FALSIFIED`.

## Pre-execution gate

No `run.py`, solver configuration, executable validator, candidate budget,
or experiment authorization belongs in this proposal cycle. The design
becomes executable only after:

1. the zero-compute regime audit identifies a defensible larger ladder;
2. exact tuple/yield accounting and the complete cost unit are accepted;
3. all five digest-bound proposal reviews exist and blockers are resolved;
4. exact curve/control/attempt tables, estimator, timeouts, rank target, and
   immutable instance cap are frozen;
5. executable producer/baseline/validator digests replace design sentinels;
6. an independent validator fixture passes fault injection;
7. a new dated decision allocates a bounded safe synthetic budget.
