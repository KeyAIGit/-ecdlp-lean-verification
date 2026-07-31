# HYP-SELECT-002 - GLV-Semaev continuation decision

Date: 2026-07-30

Audited base: `main` at
`13a7663f93c49444acd5052bf5bc163349fbaa27`

Decision status: `PREREGISTERED / EXECUTION NOT YET AUTHORIZED`

Novelty status: `NOVELTY UNVERIFIED` except where a cited primary source
establishes that an ingredient is known.

This review follows the KeyAI ECDLP Hypothesis Selection Constitution v3.0.
It is a research-allocation decision, not an ECDLP result.

## 1. DECISION

[DERIVED] Do not give the GLV-Semaev line another broad attack cycle. Give
the exact M16 line one final, bounded enabling test:
`HYP-M16-FIXED-TARGET-YIELD-001`. The test asks whether exact relations for
targets fixed before relation sampling remain on the endpoint-nonzero,
`BalancedPropagatedRegular` locus often enough that the TASK-025 single
affine chart is usable, or whether the apparent regular locus is a
constructed-target or small-field artifact. A positive result promotes only
one later solver-slope experiment. A negative result pauses the affine M16
line and redirects the primary budget to a mechanistically independent
portfolio. The orthogonal hedge is
`HYP-SGGM-MODEL-MAP-001`, an explicit applicability or non-applicability map
for structured generic-group lower bounds.

## 2. DECISION TARGET

Decision: whether the completed GLV-Semaev/M16 representation line deserves
one more primary cycle, must be narrowed to one critical test, or should be
displaced.

Horizon and budget:

- one bounded decision cycle;
- at most four CPU-hours, 4 GiB peak RAM, and one working day for the primary
  pilot after separate repository authorization;
- 70% primary test, 20% orthogonal hedge, 10% directly required validation
  and ledger work;
- synthetic toy curves and self-generated targets only;
- no direct secp256k1 target, discrete-log recovery, large solver run,
  parameter sweep, or route promotion.

Available instruments:

- exact finite-field and elliptic-curve arithmetic in Python;
- the checked M16 semantic, exceptional-fiber, projective, chart, strata,
  and propagation artifacts;
- Lean 4 and Mathlib through repository CI;
- independent standard-library validators and immutable JSON/SHA-256
  artifacts.

Most expensive unknown:

[UNKNOWN] Whether fixed-target relation acquisition and subsequent solving
retain any useful scaling after membership probability, exceptional fibers,
relation independence, rank, and recovery are charged end to end.

## 3. CURRENT STATE DELTA

[REPRODUCED] TASK-025 is merged into `main`. Its remote Lean and docs-sync
workflows passed, and its independent local replay passed. The canonical
ledger contains 306 rows and about 267 distinct results. The checked project
sources report no `sorry` and no project-specific custom axioms.

[KNOWN] TASK-025 proves conditional representation facts:

- necessary logical mask reductions `377 -> 129 -> 69 -> 36`;
- an independent boundary-only reduction `129 -> 60`;
- six prefix plus six suffix obstruction values;
- exact reduction to the empty-mask affine chart under affine inputs,
  nonzero endpoints, and `BalancedPropagatedRegular`.

[KNOWN] TASK-025 does not prove symbolic nonzeroness, nonemptiness, density,
probability, target-uniformity, witness uniqueness, relation yield, rank,
solver behavior, recovery, or total cost.

[OBSERVATION] A previous instrumented HYP-SELECT-001 run recorded one
synthetic balanced-regular constructed-target witness and an independent
validator pass. Its unpublished local branch and bytes were removed during
workspace cleanup before publication. Therefore that observation is not
treated as current repository-canonical `[REPRODUCED]` evidence. Its first
role in this cycle is a deterministic recovery/sanity fixture, not support
for scaling.

[OBSERVATION] `HYP_GLV_SEMAEV_001` remains parked. No attack route, native
Research Engine experiment, or promotion run is currently authorized.

[REPRODUCED] The coordinatewise `x_i^3` quotient premise is already closed:
it quotients by `C3^m`, not the diagonal `C3`, and loses relative phase.
Earlier P0-P4 measurements establish only bounded negatives, inconclusive
toy behavior, or resource exhaustion in their recorded scopes.

[KNOWN] The proposed nonsplit-torus trace construction is not a new
mechanism: the project's inspected WCC 2017 source extract already records
the `p+1`, `F_(p^2)` root and trace construction. Any arity-6/7 or
secp256k1-specific version must be screened as a parameter extension, not
advertised as a novel route. Evidence:
`data/source_claim_extracts/yokota_kudo_yasuda2017_wcc.json`.

## 4. RELEVANT BARRIERS

### B-M16-1 - Finite chart reduction is not a cost reduction

[DERIVED] Reducing conditional representation branches from 377 to one does
not reduce the secret-key space and does not establish a smaller exponent.
It can remove implementation branching only on the stated regular locus.

### B-M16-2 - Fixed-target acquisition

[KNOWN] Prime-field summation-polynomial methods move cost into relation
generation and polynomial solving. A constructed target obtained by summing
chosen leaves makes relation existence tautological and cannot estimate
fixed-target acquisition.

### B-M16-3 - Total relation cost

[DERIVED] Any usable comparison must charge at least:

`attempts per accepted relation + polynomial solving + recovery + rank
acquisition + sparse linear algebra + preprocessing`.

TASK-025 controls none of those terms.

### B-M16-4 - Generic-group scope

[KNOWN] Shoup's generic lower bound applies to black-box group algorithms.
The M16 line reads coordinates and polynomial representations, so the
classical generic-group theorem does not automatically apply. Conversely,
using coordinates is not itself evidence that the bound is escaped.

### B-M16-5 - Finite automorphism groups

[KNOWN] GLV and finite automorphism orbits supply established constant-factor
speedups and representation identifications. A change in exponent requires
a separate mechanism affecting relation probability, solving-degree growth,
dimension, or another scaling parameter.

## 5. CANDIDATE TABLE

Scores are decision-journal values from 0 to 5, not calibrated physical
probabilities. `C` and `R` increase with cost and artifact risk.

| ID | Type | Mechanism | V | M | B | D | S | F | G | U | C | R | Main barrier | Cheapest decisive test | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| HYP-M16-FIXED-TARGET-YIELD-001 | ENABLING | Fixed-before-sampling targets plus exact regularity classification | 3 | 4 | 1 | 5 | 4 | 4 | 5 | 5 | 2 | 3 | Constructed-target leakage and acquisition cost | Exact-per-trial residual sampler on fixed `E_7` toys with orbit/plain controls | PASS / PRIMARY |
| HYP-M16-SOLVER-SLOPE-001 | ATTACK | Lower growth of solving degree or matrix cost on the exact affine M16 system | 5 | 2 | 1 | 5 | 4 | 2 | 5 | 5 | 4 | 5 | Relation acquisition and unmeasured solver scaling | Held-out multi-size solver comparison after primary gate | REFORMULATE / DEFER |
| HYP-PPLUS1-TRACE-M67-001 | ATTACK | Nonsplit-torus trace factor base at arity 6 or 7 | 4 | 3 | 2 | 4 | 4 | 3 | 4 | 3 | 3 | 4 | Known WCC 2017 mechanism; exact extension uncertain | Exact source comparison and one matched toy system | REFORMULATE / DEFER |
| HYP-SGGM-MODEL-MAP-001 | BARRIER | Map the permitted coordinate operations to a structured generic-group model, or certify the failed assumption | 3 | 3 | 4 | 4 | 3 | 3 | 5 | 3 | 2 | 2 | Model applicability may fail | Operation-by-operation applicability matrix with one formal boundary lemma | PASS / HEDGE |
| HYP-CM-SEXTIC-CIRCUIT-001 | ATTACK | CM/isogeny-derived low-degree source-map circuit | 4 | 2 | 1 | 3 | 2 | 2 | 3 | 3 | 4 | 5 | No exact map, recovery semantics, or cost bridge | Specify map and recovery before arithmetic search | KILL AS STATED |
| HYP-EDS-OBSERVABLE-INVERSION-001 | ATTACK/BARRIER | EDS observable exposing more than a point re-encoding | 3 | 2 | 3 | 3 | 3 | 2 | 4 | 4 | 3 | 2 | Existing observable is a re-encoding with no inversion mechanism | Exact information-equivalence test | KILL / DEFER |
| HYP-RELATION-COST-LOWER-BOUND-001 | BARRIER | Decompose total cost into yield, relation cost, rank, and linear algebra | 3 | 5 | 4 | 4 | 5 | 5 | 4 | 4 | 1 | 1 | Assumptions must not smuggle in independence | Applicability proof for the current generator | PASS / DEFER |

Hard-gate summary:

- `HYP-M16-FIXED-TARGET-YIELD-001`: PASS all gates as an enabling test;
  novelty remains unverified and no attack improvement is claimed.
- `HYP-M16-SOLVER-SLOPE-001`: REFORMULATE at GATE 6 until fixed-target
  relation acquisition and an exact input generator exist.
- `HYP-PPLUS1-TRACE-M67-001`: REFORMULATE at GATE 8 because the mechanism is
  known and the claimed arity-specific delta is not yet isolated.
- `HYP-SGGM-MODEL-MAP-001`: PASS as a barrier hedge; the output may be a
  rigorous non-applicability boundary rather than a lower bound.
- `HYP-CM-SEXTIC-CIRCUIT-001`: KILL at GATES 1, 2, and 3 in its current form.
- `HYP-EDS-OBSERVABLE-INVERSION-001`: KILL at GATES 2 and 4 until an
  independently accessible observable and inversion mechanism are given.
- `HYP-RELATION-COST-LOWER-BOUND-001`: PASS, but Pareto-deferred because it
  does not answer the cheaper fixed-target question first.

## 6. KILLED OR DEFERRED

- `HYP-M16-SOLVER-SLOPE-001`: deferred because a solver benchmark before
  measuring accepted fixed-target inputs would optimize an unvalidated
  sampling regime. Return only after the primary promotion gate.
- `HYP-PPLUS1-TRACE-M67-001`: deferred under NOVELTY/EXACTNESS. Return after
  a primary-source delta identifies an arity-specific system not already
  covered by WCC 2017 and supplies exact recovery.
- `HYP-CM-SEXTIC-CIRCUIT-001`: killed as an attack proposal. Return only with
  an explicit efficiently computable map, preserved operations, recovery
  semantics, and a falsifiable cost prediction.
- `HYP-EDS-OBSERVABLE-INVERSION-001`: killed/deferred because the measured
  sequence is currently a point re-encoding. Return only if a new observable
  is cheaper to obtain than the discrete log and changes an inversion step.
- `HYP-RELATION-COST-LOWER-BOUND-001`: retained as a later barrier artifact,
  not funded as the primary bet.

## 7. TOP COMPETING EXPLANATIONS

- `H_NEW`: exact fixed-target M16 relations retain a non-collapsing
  balanced-regular fraction, and some representation-aware structural effect
  survives matched controls. This is still only an enabling mechanism.
- `H_KNOWN`: balanced regularity is common on both the M16 family and matched
  controls. TASK-025 then removes representation branching but supplies only
  a constant/local simplification.
- `H_ARTIFACT`: the prior positive witness depended on a target constructed
  from the leaves, one seed, one field, target leakage, or a shared producer
  and validator error.
- `H_NULL`: after separating the expected fixed-`B` acceptance decline, the
  conditional regular fraction deteriorates with subgroup size, so the
  conditional single chart does not provide a usable scalable input family.

| Observation | H_NEW | H_KNOWN | H_ARTIFACT | H_NULL |
|---|---|---|---|---|
| Independent recovery fixture | Pass | Pass | Often fails | May pass |
| Fixed-before-sampling targets | Follow exact `2B/n`-aware prediction | Follow matched baseline | Fails or implementation-dependent | Acceptance-normalized regularity declines |
| Conditional regular fraction | Stable and control-distinct | Stable but control-equal | Seed/producer dependent | Adverse slope |
| Orbit-closed/plain ablation | Mechanism-specific delta | No delta beyond finite-orbit accounting | Unstable delta | Delta vanishes |
| Independent validator | Pass | Pass | Fails | Pass |
| End-to-end implication | Opens solver-slope test | Local simplification only | Reject evidence | Pause line |

## 8. PRIMARY BET DOSSIER

HYP-ID: `HYP-M16-FIXED-TARGET-YIELD-001`

Name: Fixed-target usability of the balanced-regular M16 affine locus

Type: `ENABLING`

Status: `SCREENED / PREREGISTERED`, not yet executable

1. Exact statement:
   [CONJECTURE] Across preregistered synthetic toy families, when the target
   is generated and committed before leaf sampling, exact M16 relations have
   an independently verifiable endpoint-nonzero and
   `BalancedPropagatedRegular` subfamily whose conditional frequency does not
   exhibit the preregistered collapse pattern.
2. Mechanism:
   TASK-025's exceptional conditions remove infinity charts. If those
   conditions hold for an accessible fixed-target relation family, the
   representation can use one exact affine chart rather than orchestrating
   exceptional masks.
3. secp256k1 structure used:
   the exact `E_7` `j=0` Kummer relation form `H`, the prime-field
   representation, and the order-three GLV orbit as measured/ablated
   structure. The pilot does not implement the source-faithful
   multiplicative-subgroup membership polynomial.
4. Computational model:
   classical representation-aware, with explicit finite-field coordinates
   and exact group operations; synthetic toy inputs only.
5. Baseline:
   on the same three `E_7` toy subgroups, a 384-coordinate
   `GLV_ORBIT_CLOSED` base versus a 384-coordinate `PLAIN_MATCHED` base.
6. Claimed improvement:
   none yet. Success removes one representation blocker and authorizes a
   later cost-slope test.
7. Complexity variables:
   `q` is group order, `m = ceil(log2 q)`. Report attempts, group operations,
   time, memory, and empirical slopes in `m`; do not infer a secp256k1
   exponent.
8. Known barrier:
   abundant or regular relations can still be computationally inaccessible;
   solver, rank, recovery, and linear algebra may dominate.
9. Proposed escape:
   none established. This test asks whether the regular-locus blocker is
   real before funding an escape claim.
10. Hidden assumptions/oracles:
    exact factor-base membership and curve arithmetic are available; target
    commitment is external to the sampler; the runtime sampler receives no
    target scalar and uses no discrete-log oracle.
11. Nearest known work:
    Semaev summation-polynomial methods; Petit-Kosters-Messeng prime-field
    factor bases; subsequent analyses of relation yield and solving
    assumptions. Exact novelty of this regular-locus diagnostic is
    unverified. Primary locators used by this decision are the
    [PKC 2016 paper](https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf),
    [Amadori-Pintore-Sala 2017](https://eprint.iacr.org/2017/609),
    [Shoup's generic-group lower bound](https://doi.org/10.1007/3-540-69053-0_18),
    and the
    [structured generic-group model](https://eprint.iacr.org/2026/384).
12. Why not merely a known constant:
    it does not claim otherwise. A control-equal positive result is explicitly
    classified as local/constant simplification.
13. Testable prediction:
    target-hidden exact accepted relations and their regularity labels replay
    identically in an independent validator.
14. Scaling prediction:
    no adverse trend in conditional regular fraction over the bounded pilot;
    relation-acquisition cost is reported separately and may still grow
    prohibitively.
15. Controls:
    three fixed `E_7` subgroups, five independent seeds, orbit-closed versus
    matched plain coordinate sets, shuffled targets, random labels,
    16-permutation order checks, and a constructed-target positive control
    explicitly excluded from the primary estimate.
16. Cheapest decisive test:
    exact-per-trial fixed-target residual sampling of 15 signed leaves plus a
    factor-base residual, followed by balanced-obstruction replay.
17. Death criterion:
    with at least 100 accepted rows, the preregistered Wilson upper-bound
    collapse occurs on the orbit arm at `m=21` or `m=23`; or only the
    constructed-target control succeeds.
18. Promotion criterion:
    all six curve/arm cells have at least 100 accepted rows, independent
    replay passes, the `GLV_ORBIT_CLOSED` arm passes the preregistered Wilson
    lower bound at both larger sizes, and its unexplained decline does not
    exceed 0.05. The plain arm is the paired mechanism control and is not an
    additional promotion threshold. Promotion is only to
    `HYP-M16-SOLVER-SLOPE-001`.
19. Maximum budget:
    three million trials, four CPU-hours, 4 GiB peak RAM, and one working
    day.
20. Information value if false:
    closes the nearest bridge from TASK-025's local algebra to an executable
    M16 input family and prevents a large solver/Lean expansion.
21. Artifact risk:
    high without target commitment and independent arithmetic; moderate after
    the preregistered controls.
22. Required repository artifact:
    immutable preregistration, raw JSONL trials, summary JSON, SHA-256
    manifest, independent validator that does not import producer code, tests
    for semantic mutations, and a ledger transition for every outcome.
23. Novelty:
    `NOVELTY UNVERIFIED`; no novelty claim is required for a decision test.
24. Critical unresolved question:
    even if regular relations are accessible, does exact polynomial solving
    exhibit any favorable end-to-end slope after recovery and rank?

Barrier audit:

- The method is not generic-only: it reads coordinates, factor-base
  membership, and `H`-relation structure.
- The representation information is unavailable to a black-box generic
  algorithm, but no lower-bound assumption has yet been shown to fail in a
  way that changes complexity.
- The original difficulty may move into relation sampling, polynomial
  solving, membership density, recovery, rank, preprocessing, or linear
  algebra; the test records acquisition separately.
- No effect at 256 bits is inferred from the toy pilot.
- The minimum refutation is failure of target-hidden accepted relations or a
  preregistered adverse regularity trend after exact replay.

## 9. ORTHOGONAL HEDGE

`HYP-SGGM-MODEL-MAP-001` is a barrier hypothesis with a different failure
mode. It does not depend on finding M16 relations or on the balanced-regular
locus. It inventories the exact allowed operations of the current
representation-aware proposal and attempts either:

1. a faithful reduction to the assumptions of a structured generic-group
   lower-bound model; or
2. a machine-checkable witness identifying the first model assumption that
   fails and the extra information exposed.

A failure to map is not evidence of an attack. Its value is a precise model
boundary and a reusable filter for future coordinate-based ideas.

No second enabling task is selected: the primary bet itself is the sole
enabling task.

## 10. DECISIVE TEST

The executable preregistration is
`experiments/engine/pkc_smooth_m16_fixed_target_yield/PREREGISTRATION.md`.

Pre-run commitments:

- publish the exact frozen curve table, seeds, target commitment, factor-base
  construction, controls, trial caps, metrics,
  collapse threshold, and promotion threshold before producing outcomes;
- keep target creation separate from the relation producer;
- store each terminal curve, arm, seed, trial, and validation outcome;
- validate curve membership, factor-base membership, exact point relation,
  endpoint determinants, all six prefix and six suffix obstruction labels,
  operation counts, hashes, and target-before-leaves ordering independently;
- treat a resource-cap exhaustion as `INCONCLUSIVE`, never as refutation;
- do not run a general polynomial solver in this cycle.

## 11. STRONGEST COUNTERARGUMENT

The fixed-target regularity pilot may be scientifically correct but
decision-irrelevant. `BalancedPropagatedRegular` excludes finitely many
proper algebraic conditions and is therefore expected to hold frequently on
large random-looking inputs. Demonstrating that expectation on toy curves
would merely confirm that TASK-025 is a clean affine representation. It would
not reduce relation-finding cost, degree of regularity, or linear algebra.
Accordingly, the promotion gate is deliberately narrow and the mechanism
probability for a complexity-relevant effect remains low.

## 12. PRE-MORTEM

Suppose the bet has failed one year later.

1. Most likely reason:
   the project confused a high conditional regular fraction on arbitrary
   matched bases with evidence for the source-faithful `x^D-1` factor base,
   then optimized a solver around an untested membership family.
2. Early signal:
   regularity looks excellent in both orbit and plain arms while
   source-faithful membership and polynomial solver cost remain unmeasured.
3. Action now:
   report residual acceptance and conditional regularity separately,
   disclose the non-source-faithful bases, and prohibit solver expansion
   until a source-faithful input generator and favorable cost-slope
   hypothesis pass review.

## 13. EXECUTION PLAN

| Task | Input | Method | Responsible component | Output | Completion criterion |
|---|---|---|---|---|---|
| Recover HYP-SELECT-001 fixture | Prior recorded parameters and current TASK-025 definitions | Deterministic regeneration and independent replay | Producer + standalone validator | Recovery JSON and hash | Byte-independent mathematical replay passes |
| Freeze primary preregistration | Current decision and exact experiment contract | Immutable Markdown plus machine-readable config | Research ledger | Pre-outcome commit | All thresholds and caps fixed before outcomes |
| Build toy-family producer | Three frozen `E_7` rows and committed targets | Exact residual sampling with two matched bases | Producer | Raw trials and accepted witnesses | Every curve/arm/seed reaches one terminal state |
| Build independent validator | Raw JSONL and public config | Separate arithmetic implementation, no producer imports | Validator | PASS/FAIL report | Replays all accepted rows and hashes |
| Run bounded pilot | Preregistered cells only | Deterministic seeds under resource caps | Runner | Raw and summary artifacts | Every cell completes or is marked resource-exhausted |
| Classify outcome | Raw evidence and controls | Apply precommitted gates | Committee | Ledger transition | ACTIVE/PROMOTED/KILLED/PAUSED recorded with scope |
| Execute hedge | Current operation vocabulary and primary literature | Assumption-by-assumption model map | Barrier desk | Applicability matrix | First failed or satisfied assumption is explicit |

## 14. REPOSITORY CHANGES

This preregistration branch should contain:

- `notes/reviews/HYP_SELECT_002.md`;
- `experiments/engine/pkc_smooth_m16_fixed_target_yield/PREREGISTRATION.md`;
- only the generated source-registry and shadow-intake updates required by
  repository fixpoint gates.

Before execution, a separate dated authorization change must consistently
update:

- `tasks/ECDLP_RESEARCH.md`;
- `experiments/HYPOTHESES.yaml`;
- `repo/ECDLP_DECISION_SUBSTRATE.json`;
- directly generated decision/status views required by repository gates.

The execution branch must add:

- a producer and bounded config;
- a non-importing independent validator and validator fault tests;
- raw JSONL, summary JSON, and SHA-256 manifest;
- a negative-result record even if the outcome is null, inconclusive, or
  resource-exhausted;
- the exact hypothesis transition, prior update, next permitted step, and
  relevant barrier-map delta.

No theorem-count work, site work, architecture change, direct S17 expansion,
or unrelated refactor belongs in this cycle.

## 15. CONFIDENCE

Selection confidence: 75-90%.

Basis: the test is bounded, attacks the closest unresolved decision gate,
has strong constructed-target and matched controls, and can prevent a much
larger solver campaign. The range reflects uncertainty about whether enough
fixed-target relations can be acquired under a useful toy density within the
budget.

Estimated mechanism probability: 2-10% for any complexity-relevant mechanism.

Basis: the current result is a conditional representation theorem. Known
finite GLV symmetry normally changes constants, and no favorable
relation-generation or solving exponent has been observed.

Estimated scaling probability conditional on a real mechanism: 10-30%.

Basis: even a genuine regular-locus effect can disappear after charging
membership density, solving degree, recovery, rank, and sparse linear
algebra.

Facts that would change the decision:

1. an exact, independently verified fixed-target input generator with a
   favorable acquisition slope;
2. a control-separated reduction in solving-degree or end-to-end cost on a
   held-out size;
3. a primary-source or theorem-level barrier that proves the current
   operation family cannot improve the exponent, or a precise failure of that
   barrier's assumptions.

Primary bet: `HYP-M16-FIXED-TARGET-YIELD-001`

Next decisive test: exact-per-trial target-committed residual sampling on
three fixed `E_7` toy subgroups plus independent balanced-regularity replay
for orbit-closed and matched plain bases

Kill criterion: with at least 100 accepted rows, the orbit-arm Wilson upper
bound is below 0.80 at `m=21` or `m=23`, or only constructed-target controls
succeed

Promotion criterion: all six cells have at least 100 accepted rows,
independent replay passes, the orbit arm at `m=21,23` has Wilson lower bound
at least 0.90, and its unexplained decline does not exceed 0.05; the plain arm
remains the paired mechanism control, and promotion is only to the
solver-slope test

Maximum budget before review: four CPU-hours, 4 GiB peak RAM, one working day
