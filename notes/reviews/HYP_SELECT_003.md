# HYP-SELECT-003 — source-faithful M16 allocation decision

Date: 2026-07-30

Audited base: `main` at
`bc2f04a71d168b34bce3d68c1d7cef33b4af9e4e`

Decision status:
`PROPOSAL INTAKE: NEEDS_REVISION / EXECUTION NOT AUTHORIZED`

Novelty status: `NOVELTY UNVERIFIED` except for ingredients explicitly
attributed to primary literature or repository-checked results.

This review follows the KeyAI ECDLP Hypothesis Selection Constitution v3.0.
It is a research-allocation decision, not an ECDLP result.

## 1. DECISION

[DERIVED] Do not grant GLV-Semaev another solver or architecture cycle.
Retain only the conditional attack proposal
`HYP-M16-SOLVER-SLOPE-001`, narrowed to one critical prerequisite: before
any solver is written, exhibit a source-faithful size regime, relation
stream, causal controls, exact yield bridge, and common cost unit in which
the Petit `k=16` threshold is actually identified. The proposed
12–24-bit ladder already fails that regime test: balance forces
`D <= [11,13,15,17,20]`, so `D` is never large relative to `k=16`.
Classify that ladder `INAPPLICABLE FOR AN EXPONENT TEST`, keep compute at
zero, and require a separately reviewed larger safe synthetic ladder.
If none can be frozen, pause the M16 attack interpretation and move the next
primary allocation to an orthogonal barrier program. Keep
`HYP-SGGM-MODEL-MAP-001` as the hedge, with only the naive subgroup map
`sigma(a)=pointX([a]G)`, `star=S3/H-output` refuted; broader SGGM applicability
remains `[UNKNOWN]`.

## 2. DECISION TARGET

Decision: after TASK-026, does the M16 line deserve a source-faithful
solver-slope cycle, a narrower critical test, or replacement by an
independent mechanism?

Horizon and constraints:

- one proposal/review cycle;
- zero experimental CPU-hours and GPU-hours;
- no TASK-026 rerun, solver implementation, route promotion, or
  secp256k1 target;
- 70% primary mechanism/test, 20% SGGM barrier hedge, 10% directly necessary
  provenance and validation;
- one primary bet, one orthogonal hedge, one enabling task.

Available instruments:

- exact TASK-015–025 M16 representation and recovery artifacts;
- completed TASK-026 residual-sampling bundle;
- primary-source extracts for Petit–Kosters–Messeng and
  Amadori–Pintore–Sala;
- Lean/Mathlib and deterministic repository validators.

Most expensive unknown:

[UNKNOWN] Whether a size regime exists in which the exact
`x^D=1` factor base and recursive `S3` system retain a causal
solver-attempt advantage after measured yield, recovery, rank,
preprocessing, memory, and linear algebra.

## 3. CURRENT STATE DELTA

[REPRODUCED] TASK-026 ran once under its consumed authorization:
3,000,000 synthetic residual trials, 911 accepted exact relations, 907 on
the affine regular locus, and 6,186,769 independent replay checks.

[REFUTED] In that scope, the GLV-specific regularity explanation did not
survive its matched plain control. The pooled orbit-minus-plain
differences at subgroup-bit sizes 19, 21, and 23 were approximately
`-0.00699`, `-0.00633`, and `0`, with overlapping intervals.

[DERIVED] TASK-025 is a local conditional chart simplification. It does not
change the key space or establish relation yield, solver cost, rank, or
complexity.

[KNOWN] TASK-026 did not use the source factor base `x^D=1`, a polynomial
solver, source-faithful relation coefficients, rank recovery, or sparse
linear algebra. It is not a solver-slope result.

[REPRODUCED] The desk artifact records 398 variables, 399 equations, and
maximum input degree four for one regular-chart representation. These are
inventory counts, not solving bounds.

[DERIVED] A source-faithful single-target experiment fixes
`Q=[z]G` but varies relation points
`R_j=[alpha_j]G+[beta_j]Q`. Retained rows must keep
`alpha_j,beta_j` and verify
`sum_i c_ij lambda_i - beta_j z = alpha_j (mod q)`.
The earlier one-`R`/target-coefficient-`-1` formulation was not sufficient
for rank or key recovery.

[REPRODUCED] `REGIME_AUDIT.json` and its independent integer replay show
that if `ceil(log2 p)` is `[12,15,18,21,24]` and
`D^16 <= 2*16!*p`, exact integer arithmetic gives
`D <= [11,13,15,17,20]`. The first three rows force `D<k`; all rows have
`D` close to `k`, and `U<=D`. Repetition/stabilizer effects therefore
invalidate use of the simple large-factor-base yield approximation as an
M16 exponent test on this ladder.

[REPRODUCED] `pointX(P)=pointX(-P)` and a concrete Lean theorem witnesses
that `pointX` is not injective on secp256k1 points.

[DERIVED] This refutes only the naive SGGM subgroup labeling
`sigma(a)=pointX([a]G)`. The Kummer `S3/H` output relation also fails to define a
single-valued `star`; no theorem rules out a different faithful SGGM
simulation.

## 4. RELEVANT BARRIERS

### B-M16-FIDELITY — one target is not one relation point

The DLP input `Q` is fixed. Fresh committed
`(alpha_j,beta_j,R_j)` are required per relation attempt. A fixed `R` has
only bounded expected decompositions near balance and cannot supply the
rank system.

### B-M16-REGIME — the safe toy ladder does not identify the asymptotic

At `k=16` and at most 24 field bits, balance makes `D` roughly 11–20.
Exact tuple/multiset yield and stabilizers dominate. A small-ladder pass can
calibrate recovery only; it cannot establish a `7/16` solver exponent.

### B-M16-TOTAL — the two thresholds apply to different costs

The source term `T_attempt(E,16,L)` is expected solver work per attempted
System (4), including failed attempts and timeouts. Under the source balance
heuristic its necessary reference is `p^(7/16)`. Complete equal-success
single-target work, including reciprocal yield, recovery, rank, and linear
algebra, must separately beat `q^(1/2)`.

### B-M16-CONTROLS — no impossible “perfectly matched random set”

An arbitrary random root set cannot generally have both the exact
root/lift histogram and the small exponentiation DAG of `x^D-1`. Root
histogram, circuit topology, coset structure, literal representation, and
curve family require separate controls.

### B-M16-EXCEPTIONAL — output regularity does not prove completeness

Either an input-level theorem proves that all solutions are in one affine
chart, or the complete projective cover is solved and charged. Checking
returned witnesses cannot rule out omitted exceptional roots.

### B-GENERIC-SCOPE — representation access is not an escape theorem

Coordinates and `x^D=1` lie outside a classical black-box group oracle, but
that alone supplies no faster algorithm. The published SGGM theorem also
cannot be transferred without an injective label map, partial
single-valued operation, algebraic axioms, distribution, and density.

## 5. CANDIDATE TABLE

Scores are decision-journal values from 0 to 5. Higher `C` and `R` mean
greater cost and artifact risk.

| ID | Type | Mechanism | V | M | B | D | S | F | G | U | C | R | Main barrier | Decisive test | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| HYP-M16-SOLVER-SLOPE-001 | ATTACK | composed subgroup + recursive S3 | 5 | 2 | 1 | 5 | 2 | 2 | 5 | 5 | 4 | 5 | source regime and complete cost | zero-compute regime/yield feasibility gate | REFORMULATE / CONDITIONAL PRIMARY |
| HYP-M16-COMPLETE-COST-BARRIER-001 | ENABLING | exact cost and rank bridge | 4 | 5 | 4 | 5 | 5 | 5 | 5 | 5 | 1 | 1 | common unit and hidden terms | symbolic ledger plus rank semantics | PASS / ENABLING |
| HYP-SGGM-MODEL-MAP-001 | BARRIER | structured generic-group simulation | 4 | 4 | 3 | 5 | 3 | 4 | 5 | 4 | 2 | 2 | no faithful operation map | construct map or first failed axiom | PASS / HEDGE; NAIVE MAP REFUTED |
| HYP-PPLUS1-TRACE-M67-001 | ATTACK | nonsplit-torus trace factor base | 4 | 3 | 2 | 4 | 4 | 3 | 4 | 3 | 3 | 4 | known mechanism; delta unisolated | source-checked delta and matched toy | REFORMULATE / DEFER |
| HYP-EDS-OBSERVABLE-INVERSION-001 | ATTACK | elliptic-divisibility observable | 3 | 1 | 1 | 3 | 3 | 3 | 4 | 4 | 2 | 3 | observable is a point re-encoding | information-equivalence test | KILL AS ATTACK |
| HYP-CM-ISOGENY-CIRCUIT-001 | ATTACK | CM/isogeny factor-base transfer | 4 | 1 | 1 | 3 | 2 | 2 | 3 | 3 | 4 | 5 | no exact map or recovery | specify map, fibers, total cost | KILL AS STATED |

Hard gates:

- `HYP-M16-SOLVER-SLOPE-001`: `REFORMULATE` at EXACTNESS and SCALING.
  The relation/cost correction is precise, but no admissible asymptotic
  regime is frozen. It receives only the zero-compute gate.
- `HYP-M16-COMPLETE-COST-BARRIER-001`: `PASS` as the sole enabling task.
- `HYP-SGGM-MODEL-MAP-001`: `PASS` as a barrier test; the naive map is
  killed, broader applicability remains unknown.
- `HYP-PPLUS1-TRACE-M67-001`: `REFORMULATE` at NOVELTY and EXACTNESS.
- `HYP-EDS-OBSERVABLE-INVERSION-001`: `KILL` at MECHANISM and
  BARRIER ESCAPE.
- `HYP-CM-ISOGENY-CIRCUIT-001`: `KILL` at EXACTNESS, MECHANISM, and
  NON-CIRCULARITY.

## 6. KILLED OR DEFERRED

- `HYP-PPLUS1-TRACE-M67-001`: known trace-family overlap is unresolved.
  Reopen with a source-checked arity-specific density, exact recovery, and a
  changed cost term.
- `HYP-EDS-OBSERVABLE-INVERSION-001`: no independently accessible
  scalar-bearing observable or cheaper inverse exists. Reopen only with
  both.
- `HYP-CM-ISOGENY-CIRCUIT-001`: “CM structure” is not an algorithm. Reopen
  with an efficient map, bounded fibers, preserved relations, recovery, and
  total cost.
- Broad GLV-Semaev development is killed by sunk-cost protection. Only the
  conditional source-faithful premise remains.

## 7. TOP COMPETING EXPLANATIONS

- `H_NEW`: multiplicative-subgroup circuit structure lowers expected
  per-attempt elimination work and the advantage survives complete cost.
- `H_KNOWN`: a low-degree encoding, coset symmetry, root count, or solver
  engineering explains only a constant.
- `H_ARTIFACT`: tiny fields, repetition, selected divisors, unmatched
  controls, solver order, conditioning, shared code, or timeout deletion
  creates the effect.
- `H_NULL`: the gap disappears with size; reciprocal yield, rank, memory, or
  linear algebra restores square-root or worse work.

| Observation | H_NEW | H_KNOWN | H_ARTIFACT | H_NULL |
|---|---|---|---|---|
| exact producer/validator replay | pass | pass | often fail | pass |
| source beats only literal unfactored encoding | possible | expected constant | possible | vanishes |
| source beats root, DAG, coset, and ordering controls with growing gap | expected | not expected | unstable | gap closes |
| exact repetition/yield model predicts observations | required | compatible | often fails | compatible |
| `U95(s_attempt) < 7/16` in a justified balance regime | required | no | unstable | no |
| `U95(s_total) < 1/2` at equal success | required | no | unstable | no |
| `U95(s_source-s_control) < 0` for every causal control | required | no | control-sensitive | no |

## 8. PRIMARY BET DOSSIER

HYP-ID: `HYP-M16-SOLVER-SLOPE-001`

Name: source-faithful per-attempt and complete-cost slope of the arity-16
Petit relation family

Type: `ATTACK`

Status: `PROPOSED / NEEDS_REVISION / NOT EXECUTABLE`

1. **Exact statement.** [CONJECTURE] In a preregistered balanced regime
   where exact tuple yield validates the source approximation, the
   `x^D=1` circuit plus recursive `S3` system has a growing causal
   per-attempt solver advantage that survives full single-target cost.
2. **Mechanism.** Sparse multiplicative-subgroup circuit structure changes
   elimination, not merely GLV orbit size.
3. **secp256k1 structure.** The desk motivation uses
   `D=564522 | p-1`, `j=0`, and `y^2=x^3+7`; tests are synthetic and must
   ablate `j=0`.
4. **Model.** Classical representation-aware, plain single target; no
   leakage, quantum step, oracle, or multi-target amortization.
5. **Baseline.** Equal-success Pollard rho plus within-curve literal,
   coset, root-histogram, and DAG controls; non-`j=0` is a separate matched
   family.
6. **Claimed improvement.** Potential exponent change; none is established.
7. **Variables.** `k=16` fixed, `ell_p=ceil(log2 p)` and
   `m_q=ceil(log2 q)` scale; generic baseline `O(sqrt(q))`.
8. **Known barrier.** Yield, solving, recovery, rank, preprocessing, memory,
   and linear algebra can absorb all local gains.
9. **Proposed escape.** Use explicit coordinate/circuit structure absent
   from a generic oracle and demonstrate a growing causal gap.
10. **Hidden assumptions.** Suitable balanced family, exact completeness,
    solver completeness, stable timeout accounting, relation independence,
    and validator independence.
11. **Nearest work.** Petit–Kosters–Messeng 2016 and
    Amadori–Pintore–Sala 2018; neither establishes a sub-Pollard
    prime-field attack.
12. **Not merely a constant.** Promotion requires a negative paired slope
    difference against every causal control, not a bounded ratio.
13. **Prediction.** In a justified regime,
    `U95(s_attempt)<7/16`, `U95(s_total)<1/2`, and
    `U95(s_source-s_control)<0` for every control.
14. **Scaling forecast.** `H_NEW` widens the normalized gap;
    `H_KNOWN` keeps a constant; `H_NULL` converges or reverses.
15. **Controls.** Literal polynomial, multiplicative coset,
    root-histogram product tree, randomized same-DAG, cross-family
    non-`j=0`, seeds, orderings, and Pollard.
16. **Cheapest decisive test.** Prove/freeze the source regime and exact
    tuple/yield bridge before implementing a solver.
17. **Death criterion.** No admissible regime/controls can be frozen, or a
    future exact test lacks the growing causal gap or either cost threshold.
18. **Promotion criterion.** A new review accepts the regime, relation
    stream, cost unit, estimator, cap, independent validator, and all three
    decision margins.
19. **Budget before review.** Zero CPU-hours and GPU-hours.
20. **Value if false.** Closes the last source-faithful M16
    exponent-change claim under current policy and prevents solver
    infrastructure around an unidentified regime.
21. **Artifact risk.** Very high; the current ladder has `D≈k`, and
    algebra systems are order- and representation-sensitive.
22. **Required artifacts.** Exact family/tuple certificate, committed
    coefficient streams, canonical systems, raw solver matrices, recovery
    and rank transcripts, `PFPO` ledger, validator output, and hashes.
23. **Novelty.** New to repository intake; global novelty unverified.
24. **Critical question.** Can a safe increasing family reach a regime
    where the M16 source approximation and causal controls are both valid?

Barrier answers:

- The method uses coordinates and `x^D=1`, not only abstract operations.
- Those are unavailable to a classical generic-group oracle.
- No lower-bound assumption is thereby automatically escaped.
- Every shifted bottleneck is named and must be charged.
- The 12–24-bit effect cannot be extrapolated to 256 bits.
- Exactness failure invalidates a run; absence of a valid regime makes the
  proposal inapplicable; neither is mislabeled as a global refutation.

## 9. ORTHOGONAL HEDGE

`HYP-SGGM-MODEL-MAP-001` asks a different question: can the relevant
representation operations be simulated inside a stronger generic model?

[REFUTED] The naive map fails:

- `sigma(a)=pointX([a]G)` is noninjective;
- the Kummer output relation defined by `S3/H` is not a partial
  single-valued `star`.

[UNKNOWN] Full signed labels may avoid the first witness but do not
automatically supply `star`, SGGM algebraic axioms, unique factorization, a
simulation theorem, or a useful density bound. The hedge is independent of
solver performance and cannot rescue a failed slope test.

## 10. DECISIVE TEST

Preregistration status: `ZERO-COMPUTE GATE / NO SOLVER AUTHORIZATION`.

**Inputs**

- fixed `k=16`;
- exact balance inequality and candidate field-size policy;
- source definitions of `D,H_D,F_D,U`;
- one fixed synthetic `Q=[z]G`;
- fresh committed `(alpha_j,beta_j,R_j)` per attempted relation;
- exact repetition, permutation, stabilizer, and lift accounting;
- constructible within-curve and cross-family controls.

**Method**

1. derive exact integer `D` bounds for each candidate size;
2. compute `k/D`, `k/U`, exact multiset counts, and source-yield correction;
3. reject 12–24 bits as exponent evidence;
4. identify or fail to identify a larger safe synthetic regime;
5. freeze relation coefficients, exceptional policy, `PFPO`, rank target,
   estimator, timeouts, and instance cap;
6. submit the resulting immutable proposal to five digest-bound reviews.

**Baseline**

The source large-factor-base approximation itself is the feasibility
baseline. A future solver test additionally requires equal-success Pollard
and the separated control suite.

**Metrics**

- regime: `k/D`, `k/U`, exact/heuristic yield ratio, stabilizer mass;
- future solver: `s_attempt` versus `ell_p`;
- future complete work: `s_total` versus `m_q`;
- causal separation: paired `Delta_c=s_source-s_c`;
- secondary CPU, wall, RSS, storage, and parallel work.

**Current result**

[DERIVED] The 12–24-bit ladder is inapplicable for an M16 exponent test
because `D<=20` and `D≈k`. It remains usable only for fault injection and
recovery calibration.

**Death**

- no larger safe source-faithful regime and controls can be frozen;
- or, after a separate authorization, no growing causal gap;
- or `U95(s_attempt)>=7/16`;
- or `U95(s_total)>=1/2`.

Implementation mismatch is `INVALID_IMPLEMENTATION`; missing family is
`INAPPLICABLE`; wide intervals are `INCONCLUSIVE`.

**Promotion**

Only a new dated decision may replace zero compute after the regime,
relation stream, controls, exact cost unit, estimator, immutable cap,
executable digests, and independent validator are all frozen.

**Budget**

Current maximum: zero experimental CPU-hours, zero GPU-hours, no solver
instances.

## 11. STRONGEST COUNTERARGUMENT

The zero-compute bound may merely show that the safety cap is too small, not
that the M16 mechanism fails. Refusing a solver run could miss a real
finite-size structural signal.

Response: that signal cannot answer the stated exponent question because
`D≈k` changes the yield law and repeated leaves dominate. Running first
would optimize an unidentified surrogate. A larger safe regime can reopen
the question through a new review; sunk cost cannot.

## 12. PRE-MORTEM

Assume the bet failed after one year.

1. Most likely cause: a larger ladder was called “source-faithful” while
   tuple yield, controls, or common arithmetic units remained ambiguous.
2. Early signal: discussion returns to isolated Gröbner timings or equation
   counts without coefficient streams, rank, and `PFPO`.
3. Mitigation now: keep execution authorization at none and make every
   missing object a machine-visible blocker.

## 13. COMMITTEE RECORD AND EXECUTION PLAN

Single-session adversarial role-pass summary (these are not the five
digest-bound independent HGR reviews, which remain absent):

| Pass | Verifiable finding | Effect |
|---|---|---|
| A — Builder | Strongest coherent claim is a causal per-attempt solver advantage plus full-cost survival, with fixed `Q` and varying `R_j` | retained only as conditional proposal |
| B — Barrier attacker | current ladder has `D≈k`; one-`R` semantics and naive SGGM map fail | solver cycle denied |
| C — Complexity auditor | `7/16` applies to `T_attempt`; `1/2` applies to complete equal-success work | metrics separated |
| D — Experiment auditor | impossible perfect matching, exceptional omission, timeout deletion, and shared recovery are major artifact paths | controls and validator split |
| E — Novelty auditor | nearest primary work leaves solver cost unresolved; global novelty not established | `NOVELTY UNVERIFIED` |
| F — Portfolio chair | cheapest high-information action is the regime gate at zero compute | selected |

Per-candidate committee record:

| ID | Strongest case for | Strongest case against | Unresolved crux | Decisive test | Decision |
|---|---|---|---|---|---|
| M16 solver slope | only surviving source-faithful positive mechanism | current ladder cannot identify its exponent | admissible larger regime | exact regime/yield gate | conditional primary, no execution |
| M16 cost bridge | cheaply exposes every hidden bottleneck | may only formalize known costs | common unit and rank sufficiency | symbolic row/cost replay | enabling |
| SGGM map | can close a family with a theorem | current primitives may not fit the model | alternative faithful labels/star | explicit simulation or failed axiom | hedge |
| p+1 trace | independent factor-base geometry | likely known mechanism variant | arity-specific density | primary-source delta plus toy | defer |
| EDS observable | existing formal assets | observable re-encodes the point | cheaper inversion | information-equivalence test | kill as attack |
| CM/isogeny circuit | secp256k1 has real CM structure | no algorithmic map or cost bridge | efficient bounded-fiber map | exact mapping dossier | kill as stated |

Execution tasks:

| Task | Input | Method | Component | Output | Completion |
|---|---|---|---|---|---|
| Correct relation semantics | PKC Algorithm 1 | separate fixed `Q` from `R_j`; define rows | mechanism note/proposal | exact row contract | key recovery is algebraically specified |
| Close small-regime claim | balance inequality | exact integer bound and repetition audit | decision note | inapplicability classification | no 12–24-bit exponent claim remains |
| Freeze cost boundary | all attack phases | define `PFPO` and separate three slopes | mechanism/validator | recomputable metrics | no mixed-unit total |
| Preserve hedge | SGGM definitions and Lean boundary | map axioms without overclaim | note/matrix/theorem | scoped barrier artifact | naive map refuted; broad scope unknown |
| Validate intake | exact proposal bytes | schema, provenance, generated-state, CI | existing validators | `needs_revision`, authorization none | all gates agree |

## 14. REPOSITORY CHANGES

This cycle may create or update only:

- this decision;
- the SGGM scope note and operation matrix;
- M16 mechanism and independent-validator designs;
- the exact M16 small-ladder regime certificate and replay script;
- one non-executable machine proposal;
- the narrow `pointX` noninjectivity theorem and verified ledger row;
- primary-source registry, scientific-provenance validation, and generated
  views required by those artifacts.

It must not change the consumed TASK-026 authorization, execution/promotion
gates, hypothesis ledger, route status, TASK-026 raw bytes, or add solver/run
code.

## 15. CONFIDENCE

Selection confidence: `85%–95%`.

Basis: exact source semantics and the integer regime bound both say a solver
run is premature; the zero-compute gate has high information per cost.

Estimated mechanism probability: `1%–8%`.

Basis: the representation lever is explicit, but there is no
source-faithful solver evidence and the prior GLV-specific explanation was
bounded negative.

Estimated scaling probability conditional on mechanism: `3%–20%`.

Basis: a real local solver effect can still be erased by yield, recovery,
rank, memory, and linear algebra; the safe test regime is not yet known.

Facts that would change the decision:

1. a primary result proves an equivalent full-cost bound;
2. a safe larger balanced family with exact yield and controls is frozen;
3. independent validation later shows all three positive margins.

Основная ставка: HYP-M16-SOLVER-SLOPE-001

Следующий решающий тест: zero-compute source-regime, exact-yield, relation-stream, control, and common-cost feasibility gate before any solver

Критерий смерти: no admissible larger safe regime and causal controls can be frozen, or a later exact test has no growing matched advantage, U95(s_attempt) >= 7/16, or U95(s_total) >= 1/2

Критерий повышения приоритета: a new review accepts the larger regime, exact tuple/yield bridge, varying committed relation stream, all causal controls, PFPO accounting, three decision margins, immutable cap, and independent validator

Максимальный бюджет до review: 0 CPU-hours, 0 GPU-hours, 0 solver instances

Selection confidence: 85%–95%

Estimated mechanism probability: 1%–8%

Estimated scaling probability conditional on mechanism: 3%–20%
