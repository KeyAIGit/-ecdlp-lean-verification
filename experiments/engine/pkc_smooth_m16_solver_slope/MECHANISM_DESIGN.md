# HYP-M16-SOLVER-SLOPE-001 — source-faithful mechanism design

Date: 2026-07-30

Status: `PROPOSAL INTAKE: NEEDS_REVISION / NOT EXECUTABLE`

Model: classical, representation-aware, plain single target.

This document specifies the smallest source-faithful test that could change
the status of the Petit M16 route. It is not a solver input, a run
configuration, an authorization, or an ECDLP result.

## 1. Exact objects and notation

Keep the relation arity, field size, and relation coefficients separate:

- `k = 16` is the fixed number of factor-base leaves;
- `ell_p = ceil(log2 p)` is the toy field-size variable;
- `q = #E(F_p)` is the prime order of the cofactor-one toy curve;
- `m_q = ceil(log2 q)` is the group-order bit size;
- `G` is the fixed generator;
- `Q = [z]G` is the one fixed synthetic DLP target, with `z` hidden from the
  producer and solver but retained by the independent validator;
- `alpha_j, beta_j in Z/qZ` are known coefficients of relation attempt `j`;
- `R_j = [alpha_j]G + [beta_j]Q` is that attempt's relation point;
- `D` is a preregistered divisor of `p - 1`;
- `H_D = {x in F_p^* : x^D = 1}`;
- `F_D = {P in E(F_p) : x(P) in H_D}`;
- `U` is the number of usable factor-base columns modulo negation.

For the secp256k1 desk instance only,
`D = 2 * 3 * 7 * 13441 = 564522`. No secp256k1 target may be used by a toy
test.

The usable factor-base size is not assumed to be `D`. For the `j = 0` arm it
must be counted from

`U = (D + S_H) / 2`,

where

`S_H = sum_(x in H_D) chi(x^3 + 7)`.

Failed lifts, two-torsion, duplicate coordinates, negation classes, GLV
aliases, and unusable columns are reported rather than replaced by nominal
degree.

## 2. Fixed DLP target and varying relation stream

One synthetic `Q` is committed before the relation experiment. Each attempt
then samples and commits fresh `(alpha_j, beta_j, R_j)` before any
relation-system or solver randomness. Within-curve arms reuse the identical
coefficient and point stream.

On the regular affine chart, attempt `j` uses:

1. `x_i^D = 1` for `i = 1, ..., 16`;
2. `S3(x_1, x_2, u_2) = 0`;
3. `S3(u_(i-1), x_i, u_i) = 0` for `i = 3, ..., 15`;
4. `S3(u_15, x_16, x(R_j)) = 0`.

The secp256k1 desk artifact demonstrates one encoding of this regular chart:

- 16 leaf variables;
- 14 affine intermediate variables;
- 368 membership-circuit auxiliaries;
- 384 quadratic membership equations;
- 15 quartic `S3` equations;
- 398 variables and 399 equations in total;
- maximum input degree four.

These are representation counts, not dimension, solving-degree, memory, or
runtime bounds.

## 3. Exceptional-locus completeness

Before authorization, one policy must be frozen:

1. an input-level theorem, proved independently of returned affine
   witnesses, that every solution of every frozen instance lies in the
   regular chart; or
2. the exact projective chart cover, with every branch constructed, solved,
   recovered, and charged.

Checking regularity only after an affine solver returns proves soundness of
those witnesses, not completeness; it cannot justify omitting exceptional
solutions. Extension-only roots, infinity slots, identity prefixes,
rational two-torsion, repeated/tangent fibers, endpoint failures, and
invalid projective pairs remain separate dispositions.

## 4. Exact recovery and linear equations

Every candidate is untrusted until a separately implemented path:

1. checks each membership and `S3`/projective equation;
2. lifts every finite `x_i` to `E(F_p)` or rejects it;
3. replays the ordered tree with signs, identity states, backpointers, and
   multiplicities;
4. accepts only terminal sum `R_j` or `-R_j`, and normalizes the latter by
   negating the full recovered row;
5. aggregates repeated signed factor-base columns;
6. independently verifies the elliptic-curve relation;
7. retains `alpha_j`, `beta_j`, the coefficient commitment, topology,
   normalized row, and rejection disposition.

If canonical column `F_i = [lambda_i]G` and the normalized signed
coefficients are `c_ij`, every retained row must verify

`sum_i c_ij * lambda_i - beta_j * z = alpha_j (mod q)`.

The sparse linear system therefore has the factor-base logarithms and `z` as
explicit unknowns, coefficient row
`(c_1j, ..., c_Uj, -beta_j)`, and right-hand side `alpha_j`. Rank is
recomputed over `Z/qZ`; a candidate `z` is accepted only after `[z]G = Q`.
One fixed `R` with target coefficient `-1` is not source-faithful and cannot
support this rank argument.

## 5. Claimed cost-changing mechanism

[CONJECTURE] The low-degree circuit for `x^D = 1`, coupled to the sparse
recursive `S3` presentation, reduces the expected exact polynomial-solving
work per attempted relation system as size grows. If real, the reduction
must survive exact recovery, reciprocal yield, rank acquisition,
preprocessing, memory, and sparse linear algebra.

The non-generic information is the explicit multiplicative-subgroup
predicate and its composed circuit. The finite order-three GLV orbit is not
the proposed lever.

The claim fails in the tested scope if the effect is reproduced by a
causally matched control, disappears under ordering/seeds, or remains a
bounded constant.

## 6. Controls without impossible matching claims

Within one curve block, all arms share
`(p,E,q,G,Q)`, the committed `(alpha_j,beta_j,R_j)` stream, solver version,
monomial order, workers, stopping rule, arithmetic accounting, and resource
cap:

1. `SOURCE_COMPOSED`: exact `H_D` and its exponentiation circuit;
2. `UNFACTORED`: the same roots through literal `x^D - 1`, isolating only
   representation choice;
3. `COSET`: `c H_D` for committed nonzero `c`, preserving multiplicative
   structure and circuit scale while changing the source set;
4. `ROOT_HISTOGRAM`: exactly `D` random coordinates with the same
   lift/nonlift/two-torsion histogram, encoded by a charged product tree;
5. `DAG_RANDOMIZED`: the same gate topology and degree profile with frozen
   randomized constants/wiring; its root and lift counts are measured, not
   silently conditioned to match.

Construction rejection and conditioning costs are retained. No arbitrary
root set is claimed to have both the root histogram and the small
exponentiation DAG of `x^D - 1`.

`J0_ABLATION` is a separate curve-family block. It uses the same `p` and,
when constructible, the same prime order `q` via a non-`j = 0` curve in the
isogeny class. It necessarily has new `(E',G',Q',R'_j)`: use the same hidden
synthetic scalar `z` and coefficient stream, not the same points. If equal
order is unavailable, match `m_q`, balance, success normalization, and
report it as a separately normalized family rather than a pair. Loss of an
effect there indicates a possible `j=0`-by-circuit interaction; it does not
alone refute every secp256k1-specific mechanism.

Pollard rho is run against the same fixed `Q`, subgroup order, success
normalization, and primary arithmetic unit.

## 7. Cost bridge and primary units

The source partial model is

`P(p,k) + k! * p / D^(k-1) * T_attempt(E,k,L) + D^omega`,

where `T_attempt` is expected polynomial-solving work for one attempted
System (4), including failures and frozen timeout charges. It is not
per-recovered-relation cost.

Under the heuristic balance `D^k approximately k! * p`, the source-level
necessary condition is

`T_attempt(E,k,L) < p^(1/2 - 1/k)`.

For `k = 16`, this reference is `p^(7/16)`. It is necessary, not sufficient,
and is meaningful only when the balance/yield approximation is valid.

The complete ledger is

`W_total = W_attack_setup
         + W_attempt_stream
         + W_solve
         + W_recovery
         + W_dedup
         + W_rank
         + W_linear_algebra
         + W_candidate_verification`.

The primary work unit is a frozen prime-field primitive-operation equivalent
(`PFPO`): additions, subtractions, multiplications, and squarings in
`F_p` or `F_q` count separately as one primitive; inversion, extension-field
arithmetic, group operations, solver arithmetic, and sparse linear algebra
are expanded into those primitives through frozen algorithms. Pollard rho
uses the same expansion. Report the operation vector as well as its sum, and
repeat the conclusion under preregistered alternative addition/squaring
weights. Wall time, CPU time, RSS, storage, and parallel work are secondary
metrics and are never added to `PFPO`.

Toy curve/control search is an experimental feasibility cost, reported
separately. It is not charged as adversarial work once a public
`(p,E,G,Q)` is fixed. Factor-base construction, attack preprocessing, every
attempt including failures/timeouts, recovery, rank, and linear algebra are
charged to the single-target attack ledger. Use a fixed 50% end-to-end
target-recovery probability as the median-run comparison convention and
also report conversion to 90%; no 5% target is used.

## 8. Zero-compute regime audit

The previously proposed `[12,15,18,21,24]`-bit ladder cannot itself support
an M16 exponent claim. From

`D^16 <= 2 * 16! * p` and `ceil(log2 p) = ell_p`

the exact integer upper bounds on `D` are:

| `ell_p` | 12 | 15 | 18 | 21 | 24 |
|---:|---:|---:|---:|---:|---:|
| maximum `D` | 11 | 13 | 15 | 17 | 20 |

The machine-replayable certificate is `REGIME_AUDIT.json`, checked by
`scripts/certs/m16_solver_slope_regime_check.py`.

Thus the first three rows force `D < k`, and all rows have `D` close to
`k`; moreover `U <= D`. Repetitions and stabilizers cannot be ignored, so
the simple `D^16/(16!p)` yield approximation and its `7/16` interpretation
are not identified on this ladder.

The cheap decisive gate is therefore combinatorial, not a solver run:

1. count ordered tuples and multisets with repetitions exactly;
2. measure or exactly enumerate relation yield and stabilizers;
3. report `k/D` and `k/U`;
4. determine a source-faithful larger regime in which the balance
   approximation can be justified;
5. freeze the relation stream, controls, rank target, estimator, timeout
   treatment, and immutable instance cap.

The <=24-bit ladder may be used only for arithmetic/recovery fault injection
and method calibration. A pass may authorize review of a larger safe
synthetic ladder; it cannot support a solver exponent or secp256k1
extrapolation. If no admissible regime can be frozen, classify the route
`INAPPLICABLE` under the current policy.

## 9. Future decision statistics

If a later review authorizes a larger balanced validation, compute three
separate, preregistered one-sided upper bounds:

1. `s_attempt`, the slope of expected `log2(PFPO)` for one solver attempt
   versus `ell_p`, including timeouts: require `s_attempt < 7/16`;
2. `s_total`, the slope of `log2(W_total)` versus `m_q` at equal target
   success: require `s_total < 1/2`;
3. for every causal control `c`, the paired difference
   `Delta_c = s_source - s_c`: require `Delta_c < 0`.

The estimator, seed/size blocks, weights, right-censoring rule, invalid-size
rule, and confidence construction must be frozen before any data. A
composite machine metric may be the minimum positive margin

`min(7/16-U95(s_attempt), 1/2-U95(s_total), min_c -U95(Delta_c))`;

it is positive only when all three decisions pass. This composite does not
replace reporting each component.

## 10. Outcomes and current blocker

Future classification must use this precedence so one bundle receives at
most one canonical outcome:

1. `INVALID_IMPLEMENTATION`: producer/validator exactness disagreement;
   stop and issue no scientific outcome.
2. `INAPPLICABLE`: no regime satisfying the source and control contract can
   be frozen.
3. `RESOURCE_EXHAUSTED`: an otherwise valid run reaches the immutable cap
   before a decision.
4. `INCONCLUSIVE` with subtype `ARTIFACT`: leakage, unmatched conditioning,
   seed/order dependence, or accounting invalidates causal interpretation.
5. `FALSIFIED` with subtype `KNOWN_REPRESENTATION_EFFECT`: a preregistered
   equivalence test shows a causal control reproduces the source effect, or
   only the composed-vs-unfactored bounded encoding constant remains.
6. `SUPPORTED` with display label `SUPPORTED_TOY_ONLY`: every exact check
   passes and all three positive margins meet the guard band.
7. `BOUNDED_NEGATIVE`: no equivalence result applies, but a cost threshold
   or causal-gap requirement fails with adequate precision.
8. `INCONCLUSIVE`: all remaining valid but underpowered or censored cases.

The equivalence margin, adequate-precision rule, and timeout treatment must
be frozen with the estimator. A category may not be selected by narrative
judgment after the data.

[DERIVED] The exact relation semantics are now specified, but the current
<=24-bit ladder is unsuitable for the advertised exponent test. No larger
source-faithful family, exact combinatorial yield bridge, producer, solver,
causal control suite, estimator, cap, or independent validator is frozen.
The compute budget is zero. The next admissible operation is the
zero-compute regime/feasibility review, not a solver run.
