# HYP-M16-FIXED-TARGET-YIELD-001 preregistration

Preregistered: 2026-07-30

Audited base:
`13a7663f93c49444acd5052bf5bc163349fbaa27`

Lifecycle state: `SCREENED / PREREGISTERED`

Execution authorization: `NONE`

This document must be merged before outcome generation. Execution requires a
later dated authorization binding the same hypothesis, task, scope, producer,
validator, and budget in the canonical decision substrate, research queue,
and hypothesis ledger.

## 1. Decision this test will make

Decide whether TASK-025's conditional single-affine-chart theorem has a
fixed-target toy relation family usable enough to justify exactly one later
solver-slope test.

The terminal decisions are:

- `PROMOTE_TO_SOLVER_SLOPE_TEST`;
- `CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION`;
- `KILL_AFFINE_M16_CONTINUATION`;
- `PAUSE_INCONCLUSIVE`;
- `REJECT_AS_ARTIFACT`.

No outcome promotes an attack route or supports a secp256k1 complexity claim.

## 2. Exact tested claim

[CONJECTURE] On the three preregistered synthetic `E_7` toy subgroups, exact
ordered 16-coordinate relations for targets committed before leaf sampling
contain an endpoint-nonzero and `BalancedPropagatedRegular` subfamily whose
conditional frequency does not meet the collapse rule in Section 13.

This is an enabling claim about the availability of TASK-025's exact affine
chart. It is not a claim about a faithful PKC smooth-subgroup factor base,
solving-degree growth, independent relation rank, total relation-generation
cost, or ECDLP advantage.

## 3. Computational model and safety scope

- classical representation-aware arithmetic;
- exact prime-field and elliptic-curve operations;
- self-generated toy curves, bases, targets, and leaves only;
- no wallet, external public key, foreign key material, network target, or
  secp256k1 discrete-log instance;
- no discrete-log oracle;
- no general Gröbner/F4/msolve/Sage solver;
- no direct `S17` expansion;
- no curve larger than the three frozen toy rows.

The target scalar is excluded from the runtime sampler API. The sampler
receives only the public toy point `R`.

## 4. Competing explanations

`H_NEW`

: A representation-aware GLV-orbit structure makes the fixed-target
  balanced-regular subfamily persist differently from a matched plain base.

`H_KNOWN`

: Balanced regularity is common in both orbit-closed and matched plain bases.
  TASK-025 is then a correct local representation simplification, not a new
  complexity mechanism.

`H_ARTIFACT`

: Positive evidence depends on a constructed target, target/seed leakage,
  repeated data, a shared arithmetic defect, or one selected field.

`H_NULL`

: The conditional balanced-regular fraction deteriorates with subgroup size;
  no usable trend is established.

## 5. Frozen curve table

All rows use the exact curve:

`E_7/F_p : y^2 = x^3 + 7`.

The following table was found by a deterministic CM search and replayed with
the current independent standard-library EC oracle. It remains
`[OBSERVATION, NOT YET REPOSITORY-REPRODUCED]` until `curve_table.json` and
its independent certificate are committed and validated.

| m = ceil(log2 n) | p | #E(F_p) | n | h | G | beta | lambda |
|---:|---:|---:|---:|---:|---|---:|---:|
| 19 | 262153 | 262567 | 262567 | 1 | `(1,135720)` | 217087 | 191707 |
| 21 | 1048783 | 1050337 | 1050337 | 1 | `(1,558043)` | 858341 | 484979 |
| 23 | 16777711 | 16773843 | 5591281 | 3 | `(8760145,10159998)` | 3243663 | 4073091 |

Before any outcome run, the independent validator must check:

- primality of `p` and `n`;
- the CM/order certificate and `#E(F_p) = h*n`;
- `G` is on `E_7`, `[n]G = O`, and the declared cofactor is correct;
- `beta^3 = 1`, `beta != 1`;
- `lambda^2 + lambda + 1 = 0 mod n`;
- `[lambda]G = (beta*x_G,y_G)`.

The third row samples bases and targets only from `<G>`, not from the other
cofactor cosets.

## 6. Frozen factor-base arms

Every arm has exactly `B = 384` stored affine coordinate representatives in
`<G>`. Point sign is an independent leaf choice, so `P` and `-P` share one
stored coordinate.

`GLV_ORBIT_CLOSED`

: Select 128 seed points whose three `phi` images have distinct, previously
  unused x-coordinates, and store all 384 coordinates from
  `{P, phi(P), phi^2(P)}`.

`PLAIN_MATCHED`

: Select 384 independently generated subgroup points with unique
  x-coordinates, using a separate seed domain. Do not close the set under
  `phi`.

Selection uses a SHA-256 counter PRNG domain-separated by:

`hypothesis / curve / arm / seed / role`.

The complete ordered base is frozen before target generation. Rejected
scalars, orbit collisions, x-collisions, and target/base x-collisions are
counted and retained.

These bases isolate GLV orbit closure at matched coordinate cardinality.
They do not implement the PKC 2016 multiplicative-subgroup membership
polynomial `x^D - 1`. A positive result therefore removes only the
fixed-target/regularity blocker and cannot establish source-faithful M16
yield.

## 7. Target and trial separation

For each `(curve, arm, seed)` cell:

- the target is generated from a domain-separated stream;
- the public target point and its commitment are frozen before leaves;
- the target scalar is discarded from, and inaccessible to, the trial
  sampler;
- the sampler receives only curve data, the frozen factor base, public `R`,
  and a separately derived leaf stream;
- leaves are sampled with replacement;
- repeated indices and all coordinate collisions are recorded;
- no seed, failed cell, or target may be dropped after outcomes are visible.

One separate `CONSTRUCTED_TARGET_POSITIVE_CONTROL` may choose leaves first
and define a target from their exact sum. It checks arithmetic only and is
never included in the primary estimate.

## 8. Exact per-trial relation test

For each trial:

1. sample 15 factor-base indices and 15 independent signs;
2. compute `S = sum_(i=0)^14 e_i P_i`;
3. compute the residual `T = R - S`;
4. reject if `T = O`;
5. accept exactly when `x(T)` is a stored factor-base coordinate;
6. determine the 16th sign by comparing `T` with the stored point and its
   negation;
7. replay `sum_(i=0)^15 e_i P_i = R` exactly.

This is an exact relation decision for every trial. The empirical acceptance
rate is a residual-sampling measurement, not an exact convolution and not
the cost of a polynomial solver.

## 9. Exact TASK-025 regularity labels

For every accepted coordinate tuple `q[0:16]` and target coordinate `y`, the
producer records:

1. `base_endpoint_nonzero`: `x(q_0) != x(q_1)`;
2. `final_endpoint_nonzero`: `x(q_15) != x(R)`;
3. six prefix labels corresponding to
   `propagatedPrefixValue q j != 0`, `j = 0,...,5`;
4. six suffix labels corresponding to
   `balancedSuffixValue q y j != 0`, `j = 0,...,5`;
5. `balanced_regular`, the conjunction of the twelve obstruction labels;
6. `affine_regular`, the conjunction of both endpoints and
   `balanced_regular`.

For these base-field Kummer coordinates, an obstruction vanishes exactly
when the corresponding at-most-eight points admit a signed zero sum. The
bounded exact test is:

```text
states = {O}
for P in points:
    states = unique({S + P, S - P for S in states})
obstruction_vanishes = (O in states)
```

The prefix point lists are `q[0:j+3]`.

The suffix point lists are `[R] + q[14-j:16]`.

The independent validator must reconstruct the signed states itself and bind
the index order to TASK-025. A producer/validator mismatch is
`REJECT_AS_ARTIFACT`, not a positive result.

For each accepted tuple, 16 separately seeded deterministic permutations are
evaluated as an order-sensitivity control. They are reported separately and
never replace the primary frozen-order label.

## 10. Frozen grid and budget

There are:

- three curves;
- two factor-base arms;
- five independent seeds per curve and arm.

Trials per seed:

| Subgroup n | m | Trials per seed |
|---:|---:|---:|
| 262567 | 19 | 10000 |
| 1050337 | 21 | 40000 |
| 5591281 | 23 | 250000 |

Totals:

- 1.5 million trials per arm;
- 3 million trials overall;
- expected accepted relations per `(curve, arm)` cell are approximately
  146, 146, and 172 under the diagnostic estimate `2B/n = 768/n`;
- four CPU-hours;
- 4 GiB peak RAM;
- one working day.

The diagnostic expectation is not a pass criterion. If a cell has fewer
than 100 independently replayed accepted relations after its frozen cap, its
conditional regularity result is `INCONCLUSIVE_RESOURCE_CAP`, not zero.

The run stops immediately on a safety-scope violation, target/leaf ordering
violation, unbounded memory growth, or evidence of a systematic arithmetic
defect.

## 11. Metrics and controls

Primary metric per `(curve, arm)`:

`theta = affine_regular_accepted / all_accepted`.

Report a two-sided 95% Wilson interval.

Secondary metrics:

- acceptance yield and its binomial interval;
- both endpoint-failure fractions;
- all twelve obstruction-failure fractions;
- repeated-index, repeated-coordinate, and target/base-collision rates;
- the 16-permutation order-control result;
- curve additions, doublings, field inversions where instrumented;
- CPU time, wall time, and peak RSS;
- seed dispersion;
- orbit-closed minus plain `theta` with intervals.

Required artifact controls:

- target commitment before leaves;
- SHA-256 seed-domain separation;
- constructed-target arithmetic control;
- random-label and shuffled-target negative controls;
- fresh held-out seeds;
- validator with no producer imports;
- direct exact relation replay for every accepted row;
- semantic mutations of target, leaf order, sign, curve, base membership,
  endpoint, obstruction index, and hash.

Unconditional acceptance and conditional regularity must appear in separate
columns. A decline in the expected acceptance `2B/n` must never be reported
as a decline in conditional regularity.

## 12. Scaling interpretation

The independent variable is subgroup size:

`q = n`, `m = ceil(log2 n)`.

Field bits are recorded but are not substituted for `m`.

The three points are a bounded diagnostic, not a secp256k1 extrapolation.
No exponent is claimed. In particular:

- factor-base size is fixed at 384;
- the bases are not the source-faithful `x^D - 1` family;
- the residual sampler is not a polynomial solver;
- success can at most authorize a separately preregistered solver-slope
  experiment using a source-faithful presentation.

## 13. Precommitted decisions

### Promotion to one solver-slope test

Return `PROMOTE_TO_SOLVER_SLOPE_TEST` only if:

1. all six `(curve, arm)` cells have at least 100 independently replayed
   accepted relations;
2. for both arms at `m = 21` and `m = 23`, the 95% Wilson lower bound for
   `theta` is at least 0.90;
3. there is no decline greater than 0.05 between `m = 21` and `m = 23` that
   remains unexplained by the reported intervals;
4. all curve, relation, target-ordering, hash, and semantic-mutation checks
   pass.

Promotion means only that `HYP-M16-SOLVER-SLOPE-001` may be proposed.

### Known local simplification

Return `CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION` when the promotion
regularity gates pass but the arm difference is less than 0.05 and the
intervals overlap at the two larger sizes.

This is the expected null classification, not an attack success.

### Potential new-mechanism signal

Retain `H_NEW` only as
`POTENTIALLY NOVEL / NOVELTY UNVERIFIED` when:

- the promotion gates pass;
- `GLV_ORBIT_CLOSED` exceeds `PLAIN_MATCHED` by at least 0.10 with
  nonoverlapping intervals on at least two sizes;
- the delta survives shuffled-target, order, and independent-validator
  controls.

This signal still does not promote an attack route.

### Kill

Return `KILL_AFFINE_M16_CONTINUATION` when, with at least 100 accepted rows,
the 95% Wilson upper bound for `theta` is below 0.80 for the orbit-closed arm
at `m = 21` or `m = 23`.

Also kill evidence premised on fixed-target usability if only the
constructed-target control produces relations while the independently
validated fixed-target cells do not.

This kills only continuation premised on a broadly usable TASK-025 regular
affine locus. It is not a universal Semaev or ECDLP no-go.

### Artifact rejection

Return `REJECT_AS_ARTIFACT` for:

- any producer/validator mathematical disagreement;
- target-manifest chronology violation;
- target scalar reaching the sampler;
- an unbound raw file or unknown terminal status;
- a positive result that disappears under the mandatory arithmetic replay.

### Pause / inconclusive

Return `PAUSE_INCONCLUSIVE` for:

- any cell with fewer than 100 accepted relations after its frozen cap;
- mixed results between promotion and kill bands;
- a resource cap reached before all cells finish;
- inability to reproduce the frozen curve table;
- an unresolved implementation defect discovered before interpretation.

No threshold may be changed after outcomes are available.

## 14. Independent validation contract

The validator must:

- parse raw files without importing producer code;
- verify the curve table as specified in Section 5;
- reconstruct both frozen factor-base arms and all commitments;
- recompute every accepted exact relation;
- recompute both endpoint labels;
- independently enumerate all twelve signed-zero obstruction checks;
- replay the 16-permutation control;
- recompute all summary counts and Wilson intervals;
- verify manifest chronology and every SHA-256 binding;
- reject missing terminal outcomes and unknown statuses;
- pass fault tests mutating every scientific field listed in Section 11.

The validator reports only `PASS`, `FAIL`, or `INCONCLUSIVE`, with explicit
causes.

Upstream bindings:

- `experiments/engine/pkc_smooth_m16_exceptional_fibers/artifact.json`:
  `578db732807a452e26de03dcd338d62c25a7d90490a62bbf427b1f96c3a869cf`;
- `experiments/engine/pkc_smooth_m16_frozen_projective_witness/artifact.json`:
  `89c645545d89334473d51654a41ff7ec2364857d034c64ce08d505337fa1e2d4`;
- `experiments/engine/pkc_smooth_m16_infinity_propagation/artifact.json`:
  `9330603ba1f0af9ee4902c263200709e2ec6f8c50d8d7eaab3b55bcba78e388f`;
- `Ecdlp/Proved/FrozenRecursiveProjectiveWitness.lean`:
  `5cffb444d95f7691f92bfbd094d945be7e97069edb244d5234fa06f359a852b9`;
- `Ecdlp/Proved/FrozenProjectiveInfinityPropagation.lean`:
  `7f868aab5b946a55a213ce26a461477321d6387830eed218c414f1e62853b4b4`;
- `experiments/framework/ec_oracle.py`:
  `7acc852df5a927a7954f56bd9548ec021ef0b0c92f5435e8f213363f71c72792`.

## 15. Required repository artifacts

After separate authorization, the execution branch may add only:

- `curve_table.json`;
- `run.py`;
- `validate.py` with no producer imports;
- `test_validate.py`;
- immutable raw transcript;
- `artifact.json`;
- `artifact.sha256`;
- `RESULTS.md`;
- directly affected hypothesis, task, decision, barrier, and outcome ledgers.

No site work, broad Engine refactor, new atlas, direct S17 expansion,
unrelated Lean theorem, real-world target, or branch deletion is authorized.

## 16. Final commitment

Primary bet: `HYP-M16-FIXED-TARGET-YIELD-001`

Next decisive test: three fixed `E_7` toy subgroups, matched orbit-closed and
plain 384-coordinate bases, fixed-before-leaves residual sampling, and
independent TASK-025 regularity replay

Kill criterion: Section 13's Wilson-upper-bound or fixed-target-only failure
gate

Promotion criterion: Section 13's six-cell and Wilson-lower-bound gate, only
to a source-faithful solver-slope test

Maximum budget before review: 3 million trials, four CPU-hours, 4 GiB, one
working day
