# HYP-SELECT-004 — hundred-candidate mechanism screen

Date: 2026-07-30

Audited remote default branch:
`main` at `1f4464e7d5fb0bcdff9fd5f5bf09fa4a557ea41a`

Decision status:
`CONDITIONAL PRIMARY / ZERO-SOLVER EXACTNESS GATE`

Novelty status:
`NOVELTY UNVERIFIED`, except for ingredients explicitly attributed to
primary literature or repository-reproduced results.

This review follows the KeyAI ECDLP Hypothesis Selection Constitution v3.0.
It is a research-allocation decision, not an ECDLP result.

## 1. DECISION

[DERIVED] Do not give the GLV-Semaev line another main cycle.  Select the
known `p+1` nonsplit-torus trace family as the new conditional attack parent
`HYP-PPLUS1-TRACE-RELATION-001`, but authorize only its exact critical
lemma, `HYP-TORUS-CIRCUIT-FIDELITY-001`: determine whether the odd factors
actually present in `secp256k1.p+1` admit a reduced, bounded-fiber,
division-free `O(log H)` trace circuit whose structural advantage survives
matched controls.  No Semaev, Groebner, F4, or key-recovery solver receives
budget at this stage.  The orthogonal hedge is
`HYP-COORDINATE-HIDDEN-SHIFT-001`, which uses a shifted
coordinate-character sequence and has no factor base, Semaev system, or
elimination failure mode.

The decision is not based on prior investment.  It is based on a cheap
test that can close a real source-to-secp256k1 gap.  The probability of an
attack-level effect remains low.

## 2. DECISION TARGET

Decision: after the M16 regime failure, which one of 100 raw hypotheses
deserves the next bounded research cycle?

Horizon and constraints:

- one screening and exactness cycle;
- one conditional attack parent, one orthogonal hedge, and one enabling
  task;
- classical representation-aware, single-target ECDLP only;
- synthetic data, toy curves, and public constants only;
- at most four CPU-hours, 8 GiB peak RAM, zero GPU-hours, and zero
  production solver runs before review;
- 70% torus exactness/causality, 20% coordinate-hidden-shift hedge, and
  10% screening ledger, validators, and CI.

The most expensive unknown is not whether a Dickson identity exists.  It
is whether a compact circuit changes solving cost rather than merely
compressing the description of a polynomial with enormous geometric
degree.

## 3. CURRENT STATE DELTA

[REPRODUCED] The remote default branch and nine open draft PRs were audited.
The current hypothesis registry retains `HYP_GLV_SEMAEV_001` and
`HYP_WARD_EDS_001` as parked, and the bounded M16 fixed-target singleton as
closed.  No route-selection authorization or native experiment candidate is
active.

[REPRODUCED] Open PR 270 contains a `p+1` trace proposal, but it is
diverged from `main` and is not canonical evidence.  Its motivating trace
construction is already known from WCC 2017.  Its broad statement about
one-dimensional algebraic groups needs the word “affine”, and its
arity-window arithmetic is incomplete when higher arities and other
divisors are admitted.

[KNOWN] The inspected WCC 2017 source constructs a factor base from roots
of unity in `F_(p^2)` followed by the trace to `F_p` when `p+1` has a
suitable factor.  Its low-degree experiments are specialized to
`p = 3 mod 4`, arity two, and `N=2^r` near `sqrt(p)`.  It makes no
secp256k1 or asymptotic attack claim.

[REPRODUCED] The 100-row discovery ledger contains exactly:

- 34 Semaev/elimination/factor-base candidates;
- 33 curve/CM/GLV/isogeny/coordinate candidates;
- 33 generic-bound/algorithm/ML/lattice candidates.

The hard-gate result is:

- 49 `PASS`;
- 18 `REFORMULATE`;
- 33 `KILL`.

After model separation, correlation clustering, and Pareto filtering, the
portfolio result is:

- 8 shortlist candidates;
- 14 merged into those candidates;
- 42 deferred;
- 33 killed;
- 3 adjacent nonce-leakage/key-recovery candidates excluded from pure
  ECDLP.

The complete row-level ledger is
`data/hyp_select_004_raw_100.tsv`; its independent replay is
`scripts/certs/hyp_select_004_screen_check.py`.

[REPRODUCED] The first bounded toy exactness replay passed on seven distinct
prime fields and seven odd prime torus subgroups:

```text
CERT_OK TORUS-PRIME-TRACE-EXACTNESS-GATE-001 cases=7 solver_runs=0
```

In that scope, norm-one subgroup traces equal the roots of
`D_H(X)-2`; the raw degree is `H`, the squarefree trace degree is
`(H+1)/2`, the trace fibers have sizes one and two, and the logarithmic
Dickson recurrence agrees with the literal recurrence on every field
element.  The `j=0` lift histograms did not uniformly dominate non-`j=0`
controls.

[REPRODUCED] Exact integer replay shows

```text
p+1 is divisible by 16 * 7,322,137 * 45,422,601,869,677
```

and gives trace degrees `3,661,069` and `22,711,300,934,839` for the two odd
factors.  The factors pass a deterministic 64-bit Miller-Rabin replay.  This
is not yet a Lean primality theorem, and the remaining 184-bit cofactor is
not certified prime in this cycle.

[HEURISTIC] For the large odd factor, the unfiltered arity-six heuristic
`D^6 > 6! p` holds, but charging six independent one-half curve-lift
probabilities reverses the inequality.  Therefore exact lift density and
relation incidence, not the raw trace cardinality, control the next
decision.

## 4. RELEVANT BARRIERS

### B-TORUS-DEGREE — description length is not solving degree

For odd `H=2s+1`,

```text
D_H(X)-2 = (X-2) * (U_s(X)+U_(s-1)(X))^2.
```

The squarefree trace polynomial still has degree `(H+1)/2`.  Eliminating
the auxiliary circuit variables reconstructs that degree.  A small
quadratic circuit can hide rather than remove the full algebraic degree.

### B-TORUS-NONTRANSFER — the torus is not the elliptic group

The norm-one torus supplies candidate `x` coordinates.  It does not provide
a homomorphism into `E(F_p)`, known factor-base logarithms, or independent
relations.  Curve lifting, relation generation, rank, recovery, and linear
algebra remain separate costs.

### B-TORUS-SCALING — one fixed prime is not an exponent family

The exact secp256k1 divisor pattern can support a concrete-cost question.
An exponent claim additionally needs a controlled family of primes, curves,
and torus divisors.  A convenient toy family cannot be substituted for that
mechanism.

### B-SPARSE-SGGM — representation awareness still needs a model escape

The trace factor bases have tiny density in `F_p`.  A faithful mapping into
a structured generic-group oracle could restore a square-root barrier.
The current x-only naive SGGM map is refuted, but broader applicability is
unresolved.

### B-GLV-SUNK-COST — finite symmetry is not a new mechanism

The order-three GLV action, isolated-infinity propagation, forced
coordinates, and mask reductions are valid local algebra.  Existing
replays do not show a GLV-specific yield, rank, or solver-scaling advantage.
They do not justify another GLV-Semaev allocation.

## 5. CANDIDATE TABLE

Scores are decision-journal values from 0 to 5.  Higher `C` and `R` mean
greater cost and artifact risk.

| ID | Type | Mechanism | V | M | B | D | S | F | G | U | C | R | Main barrier | Decisive test | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| HYP-PPLUS1-TRACE-RELATION-001 | ATTACK | norm-one trace factor base plus lower-arity Semaev relations | 5 | 3 | 2 | 5 | 3 | 3 | 5 | 4 | 3 | 5 | compact circuit may hide full degree and yield cost | exact circuit gate, then matched incidence law | CONDITIONAL PARENT / NO SOLVER |
| HYP-TORUS-CIRCUIT-FIDELITY-001 | ENABLING | reduced odd-order Dickson circuit with exact fibers | 4 | 5 | 3 | 5 | 4 | 5 | 5 | 4 | 1 | 2 | reducedness, saturation, width, and eliminated degree | source/toy exactness plus same-DAG controls | PRIMARY ACTIVE TEST |
| HYP-COORDINATE-HIDDEN-SHIFT-001 | ATTACK | shifted character sequence `chi(x([k]G))` | 5 | 2 | 2 | 5 | 5 | 4 | 5 | 3 | 2 | 4 | likely flat spectrum and `Theta(q)` preprocessing | held-out spectrum and end-to-end sparse recovery | ORTHOGONAL HEDGE |
| HYP-ISOGENY-REPRESENTATION-SLOPE-001 | ATTACK | low-degree isogenous presentation | 4 | 2 | 1 | 3 | 3 | 2 | 3 | 2 | 4 | 5 | likely presentation constant; same solver failure mode | matched isogeny-neighbor slope | DEFER |
| HYP-SEMAEV-RELATION-INCIDENCE-001 | BARRIER | exact structured-set relation-count law | 5 | 4 | 4 | 5 | 4 | 3 | 5 | 4 | 3 | 3 | singular fibers and degree growth in arity | exact counts then incidence bound | SHORTLIST / NEXT IF PRIMARY PASSES |
| HYP-SGGM-SPARSE-APPLICABILITY-001 | BARRIER | structured-oracle simulation with density | 4 | 4 | 4 | 5 | 3 | 3 | 5 | 4 | 2 | 2 | faithful labels and partial operation not yet built | first failed or satisfied SGGM axiom | SHORTLIST / DEFER THIS CYCLE |
| HYP-INDUCED-SUBSET-CONSERVATION-001 | BARRIER | return time cancels subset birthday gain | 3 | 5 | 4 | 4 | 5 | 5 | 4 | 3 | 1 | 1 | does not cover a direct closed transition | induced-chain theorem and coefficient audit | SHORTLIST / CONDITIONAL |
| HYP-END-TO-END-COST-BRIDGE-001 | BARRIER | attempt-yield, rank, LA, recovery exponent maximum | 4 | 5 | 4 | 4 | 5 | 5 | 5 | 5 | 1 | 1 | independence and tail assumptions must be explicit | conditional theorem plus cost certificate | SHORTLIST / REQUIRED LATER |

No arbitrary aggregate score is used.  The primary wins because its next
test has the highest discrimination and negative information gain per unit
cost, not because its attack probability is high.

## 6. KILLED OR DEFERRED

- Broad GLV, `x^3`, C3/C6 quotient, and hidden-endomorphism variants: killed
  or merged under MECHANISM/BARRIER ESCAPE/IMPACT.  A fixed orbit changes
  constants unless a separate growing parameter is shown.
- Smart lifts, twist transfers, anomalous/isogenous transfers, MOV-by-CM,
  auxiliary torsion CRT, and direct EDS homomorphisms: killed by order,
  domain, or non-circularity obstructions.
- Pseudo-Mersenne arithmetic and optimized rho/vOW variants: deferred as
  implementation constants, not exponent mechanisms.
- Alternative Groebner, resultant, RUR, toric, saturation, and hybrid
  formulations: deferred because they optimize a solver before an exact
  source factor base and scaling regime are established.
- ML solver scheduling and counterexample search: retained as possible
  tools, not ECDLP mechanisms; no budget this cycle.
- Nonce HNP/BKZ candidates: classified `ADJACENT KEY-RECOVERY`, not pure
  ECDLP.
- Low-degree isogeny representation: deferred because it shares the
  elimination failure mode of the primary and currently predicts at most a
  presentation-dependent constant.

## 7. TOP COMPETING EXPLANATIONS

- `H_NEW`: the reduced odd-factor trace circuit has coefficient structure
  that lowers causal solver width/slope, while exact lift and independent
  relation yield survive.
- `H_KNOWN`: WCC's known trace construction and Dickson identities provide
  only a compact representation or bounded constant.
- `H_ARTIFACT`: nonreduced `D_H-2`, spurious auxiliary roots, selected toy
  factors, shared implementation, or unmatched controls create the effect.
- `H_NULL`: the circuit is exact, but geometric degree, relation scarcity,
  rank, memory, or linear algebra restores square-root-or-worse total work.

| Observation | H_NEW | H_KNOWN | H_ARTIFACT | H_NULL |
|---|---|---|---|---|
| exact trace/root/fiber replay | pass | pass | often fail | pass |
| raw polynomial is nonreduced, squarefree degree `(H+1)/2` | expected | expected | exposes one artifact | expected |
| `j=0` lift yield uniformly beats controls | mechanism-dependent | no | unstable | no |
| structural proxy beats literal and same-DAG controls with growing gap | expected | no growing gap | seed/order-sensitive | no |
| exact relation incidence exceeds corrected random-density law | required | bounded symmetry only | unstable | no |
| complete equal-success work below `q^(1/2)` | required | no | non-reproducible | no |

The completed toy exactness replay weakens only one narrow
`H_ARTIFACT` branch.  It does not distinguish `H_NEW`, `H_KNOWN`, and
`H_NULL`.

## 8. PRIMARY BET DOSSIER

HYP-ID: `HYP-PPLUS1-TRACE-RELATION-001`

Name: odd-factor norm-one trace relations for prime-field ECDLP

Type: `ATTACK`

Status: `SCREENED / CONDITIONAL / NO SOLVER AUTHORIZATION`

1. **Exact statement.** [CONJECTURE] There is a controlled safe family
   `(p_i,E_i,H_i)` with `H_i | p_i+1`, `q_i=#E_i(F_p)` prime, and
   `m_i=ceil(log2 q_i)` growing, for which a reduced norm-one trace circuit
   and a fixed-target relation pipeline have total expected cost
   `q_i^(1/2-epsilon+o(1))` for some fixed `epsilon>0`.  The concrete
   secp256k1 claim is separately that at least one exact divisor/arity
   choice has total equal-success cost below the Pollard baseline.
2. **Mechanism.** A trace factor base of size about `H/2` is described by a
   logarithmic Dickson/Lucas circuit; lower arity and circuit structure
   might reduce elimination width while retaining relation yield.
3. **secp256k1 structure.** The mechanism uses exact divisors of `p+1` and
   the curve equation only in the trace-to-curve lift.  It does not rely on
   GLV, `j=0`, or a finite automorphism as its claimed scaling lever.
4. **Model.** Classical representation-aware, one target, no leakage,
   oracle, quantum step, or multi-target amortization.
5. **Baseline.** Equal-success Pollard rho; WCC power-of-two trace
   presentation; literal squarefree polynomial; raw nonreduced Dickson
   polynomial; same-root, same-DAG randomized, coset, and non-`j=0`
   controls.
6. **Claimed improvement.** Potential exponent change; none is established.
7. **Variables.** `q=#E(F_p)`, `m=ceil(log2 q)`, torus order `H`, trace
   degree `D=floor(H/2)+1`, relation arity `k`, lift density, independent
   relation yield, solving work, memory, rank, and sparse-LA work.
8. **Known barrier.** Circuit size does not bound geometric degree,
   degree of regularity, Macaulay size, or quotient dimension.
9. **Proposed escape.** Demonstrate that source coefficients and circuit
   width, not eliminated degree, control a growing causal solver gap.
10. **Hidden assumptions.** Exact saturation, unique auxiliary witnesses,
    bounded trace and curve-lift fibers, a controlled scaling family,
    independent relation rows, complete recovery, and honest timeout/tail
    accounting.
11. **Nearest known work.** WCC 2017 supplies the `p+1` trace family and
    small arity-two experiments.  Amadori–Pintore–Sala and the
    Petit–Kosters–Messeng line supply nearby prime-field Semaev pipelines.
12. **Why not merely a constant.** Promotion requires a negative paired
    slope difference against every causal control and complete cost below
    exponent one-half.
13. **Testable prediction.** The exact circuit passes root/fiber checks,
    a coefficient-specific structural gap survives same-DAG controls, and
    corrected relation incidence exceeds the null prediction.
14. **Scaling forecast.** `H_NEW` widens the normalized gap;
    `H_KNOWN` remains bounded; `H_NULL` converges or reverses.
15. **Controls.** Power-of-two and odd-order torus subgroups, literal and
    reduced polynomials, same-DAG random coefficients, matched trace-root
    histograms, `j=0` and non-`j=0` curves, fixed public targets, independent
    validators, and preregistered orderings.
16. **Cheapest decisive test.** Complete
    `TORUS-PRIME-TRACE-CAUSALITY-001` without a solver.
17. **Death criterion.** Root/fiber/circuit exactness fails; no
    division-free reduced circuit exists; circuit width and algebraic
    proxies are dominated by matched controls; exact lift/yield leaves no
    viable arity; or a faithful sparse-SGGM reduction closes the mechanism.
18. **Promotion criterion.** Exact selected-factor certificates and at
    least five held-out sizes show a preregistered causal structural gap.
    This promotes only one bounded toy solver pilot, not an attack claim.
19. **Budget before review.** Four CPU-hours, 8 GiB RAM, zero GPU-hours,
    zero production solver runs.
20. **Information value if false.** Closes the only currently concrete
    non-GLV affine one-dimensional trace factor-base extension for the
    actual secp256k1 `p+1` divisor pattern.
21. **Artifact risk.** High: repeated roots, projective components, selected
    factors, solver ordering, and tiny fields can all look favorable.
22. **Required artifact.** Exact parameters, source/circuit specification,
    independent root/fiber replay, control matrix, cost ledger, and terminal
    classification.
23. **Novelty.** `NOVELTY UNVERIFIED`.  The trace family and Dickson
    identities are known.  Only a proven odd-factor causal solver-scaling
    effect could be potentially new.
24. **Critical question.** Does the circuit reduce the relevant solving
    width, or only hide a degree-`D` squarefree polynomial behind
    `O(log H)` auxiliary equations?

## 9. ORTHOGONAL HEDGE

`HYP-COORDINATE-HIDDEN-SHIFT-001` observes

```text
s_d(k) = chi_d(x([k]G)),
s_d(z+r) = chi_d(x(Q+[r]G)).
```

The shifted oracle is exact because `Q+[r]G=[z+r]G`.  The conjectured
mechanism is a sparse or otherwise exploitable Fourier description of
`s_d`, with preprocessing charged.  Its likely failure is a flat,
pseudorandom spectrum or `Theta(q)` preprocessing.  This is independent of
the primary's factor-base, trace circuit, Semaev, and elimination risks.

Hedge death criterion: held-out curve families match random-spectrum
controls, sparse recovery does not scale, or preprocessing already costs
order `q`.

Hedge promotion criterion: an independently replayed end-to-end recovery
pipeline has a stable exponent below one-half after preprocessing and query
cost.

## 10. DECISIVE TEST

Test ID: `TORUS-PRIME-TRACE-CAUSALITY-001`

The bounded seven-case exactness replay is completed.  The next test is
preregistered as follows.

- **Inputs:** the public secp256k1 modulus; the two selected odd divisors
  `7,322,137` and `45,422,601,869,677`; at least five frozen toy
  `p=3 mod 4` families with odd torus divisors; self-generated curve
  coefficients and public targets only.
- **Method:** certify selected factors; construct the squarefree trace
  polynomial, division-free Dickson circuit, saturation boundary, and
  unique auxiliary witness map; measure the source circuit before
  elimination.
- **Baselines:** raw `D_H-2`, explicit squarefree root polynomial, WCC-style
  power-of-two circuit, same-DAG randomized coefficients, equal-cardinality
  root-histogram controls, and non-`j=0` curves.
- **Independent variables:** field bits, `H` bits, trace degree, circuit
  representation, curve family, and control seed.
- **Metrics:** exact root mismatch, multiplicities, trace/lift fibers,
  circuit gates/depth/fan-out, primal-graph width, multihomogeneous/BKK
  proxy, eliminated degree, lift density, construction PFPO, time, and
  memory.
- **Sizes:** seven already replayed tiny exact cases plus the 23-bit factor;
  the 46-bit factor receives symbolic/certificate checks only before review.
- **Seeds:** deterministic exact cases; seeds `0..19` for randomized DAG and
  coordinate controls.
- **Significance:** zero exact mismatches; a causal metric must improve
  against every matched control on at least five sizes with a growing,
  preregistered normalized gap.
- **Death:** any exactness failure, unbounded/spurious fibers, division or
  branch oracle, no reduced `O(log H)` circuit, or no control-separated
  structural gap.
- **Promotion:** all exact gates pass and at least one solver-relevant proxy
  has a growing, control-separated gap; authorize one separately
  preregistered toy solver pilot.
- **Budget:** four CPU-hours, 8 GiB RAM, zero GPU, zero production solver.
- **Artifacts:** immutable parameters, replay script, raw metric table,
  independent validator, hashes, and a negative or positive terminal note.

## 11. STRONGEST COUNTERARGUMENT

The proposed circuit almost certainly compresses syntax rather than
complexity.  The squarefree polynomial still has millions or trillions of
roots, a conventional factor-base attack still needs relation acquisition
and a large rank system, and the WCC experiments already encountered memory
growth at tiny sizes.  Nothing presently links `O(log H)` circuit size to
sub-square-root total work.  The rational default is therefore that this
line fails; its selection is justified only because the exact failure can
be exposed cheaply and durably.

## 12. PRE-MORTEM

Assume the bet has failed after one year.

1. **Most likely cause:** the circuit is exact but its quotient dimension,
   relation scarcity, or linear algebra scales with `D`, so no end-to-end
   gain exists.
2. **Early signal:** BKK/width/eliminated-degree proxies track `H`, and
   same-DAG controls erase every apparent source advantage.
3. **Action now:** forbid solver implementation until those proxies and the
   exact yield bridge pass the frozen gate; preserve the negative result as
   a barrier certificate.

## 13. EXECUTION PLAN

| Task | Input | Method | Component | Output | Completion criterion |
|---|---|---|---|---|---|
| Replay 100-screen | raw candidate rows | schema/count assertions | screening certificate | `CERT_OK` | exactly 100 unique rows and eight canonical survivors |
| Close selected-factor arithmetic | public `p`, two divisors | exact product plus primality certificate | torus exactness | parameter certificate | exact divisibility and independently replayed primality |
| Prove reduced trace identity | odd `H`, Dickson/Lucas recurrence | algebraic proof plus independent evaluation | torus exactness | root/fiber theorem | sound, complete, squarefree, bounded fibers |
| Measure circuit causality | source and matched circuits | frozen structural metrics | torus causality | raw table and terminal result | every control and budget rule evaluated |
| Screen coordinate hedge | self-generated toy groups | DFT, random-label/feature and held-out-family controls | hedge | preregistered spectrum report | preprocessing and recovery fully charged |
| Review allocation | all artifacts | Constitution v3.0 committee passes | decision note | promote/pause/kill | one explicit terminal state |

The first and bounded toy part of the second/third tasks are completed in
this branch.  No solver task has started.

## 14. REPOSITORY CHANGES

Created or updated:

- `data/hyp_select_004_raw_100.tsv` — the exact 100-row discovery ledger;
- `repo/ARTIFACTS.yaml` — classifies that ledger as a reviewed control-plane
  artifact;
- `scripts/certs/hyp_select_004_screen_check.py` — screening replay;
- `experiments/torus_prime_trace_exactness/validate.py` — independent
  torus-trace/Dickson toy replay and secp parameter audit;
- `experiments/torus_prime_trace_exactness/README.md` — method and scope;
- `experiments/torus_prime_trace_exactness/RESULTS.md` — bounded result;
- `experiments/torus_prime_trace_exactness/PREREGISTRATION.md` — frozen
  next zero-solver causality test;
- `notes/reviews/HYP_SELECT_004.md` — this allocation decision;
- `.github/workflows/ci.yml` — both new deterministic replays.

The canonical executable hypothesis registry is deliberately not activated.
This cycle creates no native Engine candidate, route authorization, solver
run, or attack claim.

## 15. CONFIDENCE

Selection confidence: **80%–90%**.  The chosen test is cheap, exact, and
closes a concrete source-to-parameter gap even if the attack parent is
false.

Estimated probability that the remaining exact reduced-circuit lemma is
correct: **90%–99%**.  Classical Dickson identities and the seven-case
replay support it, but secp factor certificates and projective/saturation
scope remain.

Estimated attack-mechanism probability: **1%–5%**.  No evidence yet links
the compact circuit to a lower solver exponent.

Estimated scaling probability conditional on a genuine solver-relevant
mechanism: **10%–25%**.  Lift density, relation rank, lack of a controlled
asymptotic divisor family, and linear algebra can still erase it.

Facts that would change the decision:

1. a theorem connecting the reduced circuit's width to a solving bound
   below the eliminated degree;
2. a faithful sparse-SGGM applicability reduction that preserves the
   relevant coordinate operations;
3. a matched held-out toy result with a growing causal gap and complete
   yield/rank/recovery accounting.

Основная ставка: HYP-PPLUS1-TRACE-RELATION-001

Следующий решающий тест: TORUS-PRIME-TRACE-CAUSALITY-001

Критерий смерти: точность root/fiber/circuit нарушена либо ни один
solver-relevant structural proxy не отделяется от всех matched controls.

Критерий повышения приоритета: все exact gates проходят и минимум на пяти
размерах сохраняется растущий control-separated structural gap,
разрешающий один отдельный toy-solver pilot.

Максимальный бюджет до review: 4 CPU-hours, 8 GiB RAM, 0 GPU-hours,
0 production solver runs.

Selection confidence: 80%–90%

Estimated mechanism probability: 1%–5%

Estimated scaling probability conditional on mechanism: 10%–25%
