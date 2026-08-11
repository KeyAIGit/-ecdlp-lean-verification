# secp256k1 M16 exact all-roots cost-bracket contract

Date: 2026-08-10

Audited base: `6cde2788c72f46d21491deec30a66a094f4ad263`

Status: `PURE-MATH CONTRACT / NON-EXECUTABLE / NO COMPUTE AUTHORIZATION`

Current verdict: `INCONCLUSIVE`

This note specifies one possible next mathematical task. It does not select a
research task, update a route, retain a hypothesis, authorize an implementation,
or claim an attack on secp256k1. In particular, it changes none of `tasks/`,
`STATUS.md`, generated state, proposal state, or route state.

## 1. Question and threat model

The narrow question is whether there is an **exact, target-adaptive all-roots
algorithm** for the literal secp256k1 arity-16 System (4), together with a
complete base-field recovery fiber, whose rigorously counted cost can be placed
strictly on one side of the repository ceiling

```text
B = 26470005625446268964608938870039985.
```

The model is classical, representation-aware, plain single target. It permits
the public coordinates of secp256k1 and the published composed-map equations.
It permits no leakage, auxiliary secret-dependent input, quantum step,
multi-target amortization, or chosen private target. The original DLP input is
`Q = [z]G`, with `Q != O`; `z` is not available to the algorithm.

The task is intentionally output- and proof-oriented. A claimed fast
elimination, a list of some roots, a sound filter for returned candidates, or a
timing extrapolation does not satisfy it.

## 2. Primary-source pins

Only primary literature is used for the external mechanism and baseline below.
Repository certificates are listed separately in Section 3.

| Source | Exact use in this contract | Pinned primary location |
|---|---|---|
| Petit, Kosters, Messeng, *Algebraic Approaches for the Elliptic Curve Discrete Logarithm Problem over Prime Fields* (PKC 2016) | Algorithm 1 and System (4) in Section 3.1; the partial cost in Section 3.2; the `p-1` composed map in Section 3.3 | [official IACR archival PDF](https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf), [DOI 10.1007/978-3-662-49387-8_1](https://doi.org/10.1007/978-3-662-49387-8_1), inspected PDF SHA-256 `2958155e2c0a379b79490be7c2dab6658bda896cce2c1b517634b4cb6892d943` |
| Semaev, *Summation polynomials and the discrete logarithm problem on elliptic curves* (2004) | Meaning of the target-specialized summation-polynomial equation | [IACR ePrint 2004/031](https://eprint.iacr.org/2004/031) |
| Amadori, Pintore, Sala, *On the Discrete Logarithm Problem for Prime-Field Elliptic Curves* (2018) | Nearest distinct one-system prime-field comparison; no cost statement is transferred to direct System (4) | [IACR ePrint 2017/609](https://eprint.iacr.org/2017/609), [DOI 10.1016/j.ffa.2018.01.009](https://doi.org/10.1016/j.ffa.2018.01.009), inspected manuscript SHA-256 `fe8ccf5ad01470315f791b97d92978e9d1b16ae2dd1cc73492c78c12448c8e2c` |
| Pollard, *Monte Carlo methods for index computation (mod p)* (1978) | Square-root rho baseline family; a matched secp256k1 implementation still needs its own PFPO expansion | [DOI 10.1090/S0025-5718-1978-0491431-9](https://doi.org/10.1090/S0025-5718-1978-0491431-9) |
| Shoup, *Lower Bounds for Discrete Logarithms and Related Problems* (EUROCRYPT 1997) | Boundary: the representation-aware System-(4) solver is outside the classical generic-group model, so the generic lower bound is not a solver lower bound here | [author PDF](https://www.shoup.net/papers/dlbounds1.pdf), [DOI 10.1007/3-540-69053-0_18](https://doi.org/10.1007/3-540-69053-0_18) |

The PKC paper specifies a generalized-root problem but does not provide a
dedicated algorithm or a theorem bounding its cost below the necessary
square-root threshold. The Amadori paper studies a different system and does
not fill that gap for the literal PKC System (4).

## 3. Frozen repository facts

The contract may use, but must not strengthen by prose, the following checked
facts at the audited base.

| Object | Frozen fact | Proof or certificate anchor |
|---|---|---|
| Base field and curve | `E/F_p : y^2 = x^3 + 7`; the full point group has cardinality the prime secp256k1 order `n` | `Ecdlp/Proved/CurveCardinalityExact.lean` |
| Source coordinate roots | `D = 564522`, and `x^D = 1` has exactly `D` roots in `F_p` | `Ecdlp/Proved/M16FactorBaseFinite.lean` |
| Base-field lifts | exactly `U = 283527` of those coordinates lift; no factor-base coordinate has `x^3+7=0`; the signed affine count is `567054` | `Ecdlp/Proved/M16FactorBaseLiftable.lean` |
| Direct source input | at `m=16`, 64 factor coordinates, 48 transition equations, 16 terminal equations, and one target-specialized `S_17`, for 65 equation members | `experiments/engine/pkc_smooth_m16_source_faithful_mechanism/artifact.json`, SHA-256 `79ee65104cfbd45ee902fbf59524a705e6db8590c8d5845a6a20cd63239c774c` |
| Optimistic ceiling | exact `B` above, with `2^114 <= B < 2^115` and `D^5 <= B < D^6` | the integer and windows are pinned by `Ecdlp/Proved/M16SolverGate.lean`; the rational partial-model derivation is recorded in `experiments/engine/pkc_smooth_m16_symbolic_desk/artifact.json`, SHA-256 `59596c3c59f5389c49742ba4a26d500445557ee6398d6aaad63c7995a93242f7` |
| Fixed-oblivious obstruction | a specific liftable signed-width-six translated-image model needs more than `2^148` fixed residual slots to half-cover the group | `Ecdlp/Proved/M16LiftableSixWidthNoGo.lean` |

These are cardinality, representation, and narrow coverage facts. None supplies
an all-roots algorithm, a solver lower or upper bound, relation rank, or an
ECDLP shortcut.

## 4. Literal target-adaptive System (4)

Let `F = F_p`. For each `i in {1,...,16}`, use four variables
`x_(i,1),...,x_(i,4)`. Freeze the literal source chain

```text
x_(i,2) = x_(i,1)^2
x_(i,3) = x_(i,2)^3
x_(i,4) = x_(i,3)^7
1 - x_(i,4)^13441 = 0.
```

Thus the composition is exactly `1 - x^564522`.

For a nonidentity affine point `R = (X_R,Y_R) in E(F)`, define

```text
Sys_R(x) :=
  S_17(x_(1,1),...,x_(16,1),X_R) = 0
  and all 64 chain/terminal equations above,

Sol_R := { x in F^64 | Sys_R(x) }.
```

`Sol_R` is a finite **set of distinct base-field assignments**. It is not a
set of complex roots, an algebraic-closure solution scheme, a list with
solver multiplicities, or a quotient by leaf permutations. If an algorithm
works over an algebraic closure, an extension field, a radical, a saturation,
or a different circuit, it must prove that the reported base-field set is
exactly `Sol_R`. Intermediate multiplicities and extension roots must still be
priced when they affect the algorithm.

The coefficient `X_R` makes the problem target-adaptive. Target-independent
data may be prepared once, but the proof and cost may not replace the family
`R |-> Sys_R` by one favorable fixed target.

## 5. Required all-roots interface

A submission must give mathematical algorithms `Pre` and `AllRoots` with a
proof object or independently checkable exact certificate satisfying:

```text
pre = Pre(p,E,D,m=16)
AllRoots(pre,R) = a canonical duplicate-free enumeration of Sol_R
```

for **every** `R in E(F) \ {O}`.

The equality is two-sided:

1. soundness: every reported assignment satisfies all 65 literal equations;
2. completeness: every `F_p` assignment satisfying the 65 literal equations
   occurs exactly once in the canonical output.

Termination is part of the theorem. A Monte Carlo omission probability is not
exact all-roots. A Las Vegas construction is admissible only if every terminal
output is certified complete and retries are included in the cost and success
quantile.

No complexity statement may be transferred from the quadratic membership
circuit or the recursive projective `S_3` tree without an explicit root
bijection for the literal direct system and a proof that every auxiliary,
infinity, denominator, degree-drop, saturation, and extension-field branch is
handled. Pointwise equivalence of `x^D=1` predicates is insufficient.

## 6. Complete recovery fiber

For `a in F`, write

```text
Lift(a) := { P in E(F) \ {O} | x(P) = a }.
```

For `x in Sol_R`, define the full target-bound recovery fiber

```text
Fib_R(x) := {
  (P_1,...,P_16,tau) |
  P_i in Lift(x_(i,1)),
  tau in {+1,-1},
  P_1 + ... + P_16 + [tau]R = O
}.
```

The required `Recover` algorithm must establish exact set equality

```text
Recover(R,x) = Fib_R(x)
```

for every nonidentity `R` and every `x in Sol_R`. This includes empty fibers
from extension-only or nonliftable solutions. It also includes repeated leaf
coordinates, both base-field lifts, both target signs, and every valid sign
assignment. Merely accepting candidates that pass the group equation proves
only one-way soundness and fails the contract.

For relation use, freeze one deterministic reference lift `P_a^+` for every
liftable coordinate `a`. If `P_i = [sigma_i]P^+_(x_i)` and
`sum_i P_i + [tau]R = O`, define

```text
c_a = sum_{i : x_i = a} sigma_i,
d_a = -tau * c_a.
```

Then `sum_a d_a P_a^+ = R`. The vector `d` is unchanged by simultaneous
negation of all `P_i` and `tau`. `Recover` must return canonical `d` rows,
their exact multiplicities, and back-pointers to all members of the fiber.
Permutation duplicates, repeated coordinates, and global-sign duplicates
must not be mistaken for independent relations.

Work now in the scalar field `K = Z/nZ`. Because the checked secp256k1 point
group is cyclic of prime order `n` with generator `G`, every deterministic
reference lift has a unique scalar `lambda_a in K` satisfying
`P_a^+ = [lambda_a]G`. Take `alpha,beta,z in K`, with `Q=[z]G`, and let the
integer coefficients `d_a` map canonically into `K`. If
`R = [alpha]G + [beta]Q`, the group equality above then implies

```text
sum_a d_a lambda_a - beta*z = alpha  (mod n)
```

and a row is usable only after that congruence and the group equation are
independently replayed. This contract asks for the complete fiber and canonical
rows; it does not assume their independence or sufficient rank.

## 7. Uniform target and equal-success quantifiers

The exactness quantifier is worst-case over the displayed affine family:

```text
for every Q in <G> \ {O},
for every R in E(F) \ {O},
AllRoots and Recover satisfy Sections 5 and 6.
```

For any later relation stream, commit `alpha_j,beta_j` before solver
randomness and set `R_j=[alpha_j]G+[beta_j]Q`. The sampling law must make its
conditioning explicit. An identity `R_j=O` is either handled by a separately
proved branch or rejected and resampled with that work charged. It is never
fed silently to the affine system.

Cost is normalized to a 50 percent complete-output success convention. After
the target-independent `Pre` object has been built, let `C_50(R)` be the least
online PFPO cap under which a randomized exact solver returns and certifies the
full `Sol_R` and every `Fib_R(x)` with probability at least `1/2`. Define the
uniform online one-system cost

```text
C_unif,50 := max_{R != O} C_50(R).
```

A target-average or easiest-target bound cannot replace this quantity. Report
the 90 percent conversion separately. Failures, restarts, and censored runs
cannot be dropped.

Any later ECDLP claim has a second, stronger equal-success obligation: for
every `Q != O`, the complete M16 procedure and matched Pollard rho must each
recover and verify `z` with the same declared probability, using the same PFPO
expansion and parallel-work convention. A pass of the one-system bracket below
does not discharge that end-to-end obligation.

## 8. PFPO ledger

Use a frozen prime-field primitive-operation equivalent (`PFPO`) vector.
Additions, subtractions, multiplications, and squarings in `F_p` and `F_n`
are separate primitive counters. Expand inversions, extension-field
arithmetic, elliptic-curve operations, Gröbner or resultant arithmetic, and
sparse linear algebra through named deterministic algorithms into that
vector. Report both the vector and the default unit-weight sum. Also report
wall time, CPU, parallel work, peak memory, writes, and storage separately;
they are not silently converted to PFPO.

Separate the target-independent setup from the online cost of one System-(4)
target:

```text
C_setup := C_pre,

C_online(R) := C_specialize(R)
             + C_allroots(R)
             + C_fiber(R)
             + C_canonicalize(R)
             + C_exact_verify(R).
```

`C_pre` includes factor-base construction, monomial/order data, elimination
templates, multiplication matrices, reusable resultants, lookup tables,
certificate infrastructure, and any other target-independent solver setup.
It is counted once, in full, in the complete single-`Q` ledger. It may be
reused across the relation points belonging to that one `Q`, but it may not be
erased or amortized across unrelated `Q` values. Any setup depending on `Q`,
`R`, or a committed relation stream is online work.

The cost theorem must give nonnegative integers `P_L,P_U,L,U` such that

```text
P_L <= C_pre <= P_U,
L <= C_unif,50 <= U.
```

Operation-count source code, sampled timings, a solving-degree guess, or a
Macaulay dimension without a proved algorithmic link is not such a theorem.

## 9. Meaning of `B`

The PKC partial model writes

```text
P(p,16) + (16! * p / D^15) * T(E,16,L) + D^omega.
```

The existing desk calculation works in the positive rationals. With natural
numbers cast into `Q`, it sets

```text
rho_0 = (ceil(sqrt(n)) : Q) = 2^128,
mu_0  = (16! * p : Q) / (D^15 : Q),
B     = max { t in Nat | mu_0*(t : Q) < rho_0 }
      = 26470005625446268964608938870039985.
```

This rational derivation is pinned by the symbolic-desk artifact SHA-256 in
Section 3. It is not a natural-number division: truncating `mu_0` before the
comparison produces a different integer and is invalid for this contract.

For `P in Nat` with `(P : Q) < rho_0`, define the stricter residual ceiling

```text
B_net(P) := max {
  t in Nat | (P : Q) + mu_0*(t : Q) < rho_0
}.
```

Thus `B_net(0)=B`, and `B_net(P) <= B`. This definition counts
target-independent preprocessing once rather than charging it once per
relation target or pretending it is free.

It obtains `B` only after optimistically setting preprocessing and linear
algebra to zero, treating field work and group work as one unit, using the
source yield heuristic, and omitting an equal-success conversion. Therefore:

- `B` is an optimistic necessary per-system screen, not a Pollard runtime;
- comparing a PFPO bracket to `B` is legitimate only under the frozen default
  PFPO unit map;
- any positive preprocessing, recovery, rank, or linear-algebra charge can
  only reduce the true residual budget;
- `U <= B` alone does not establish even the preprocessing-aware screen;
- the preprocessing-aware upper test is
  `(P_U : Q) + mu_0*(U : Q) < rho_0`; this implies
  `(P_U : Q) < rho_0` and is then equivalent to `U <= B_net(P_U)`;
- the preprocessing-aware lower test is
  `(P_L : Q) + mu_0*(L : Q) >= rho_0`;
- either separated result is decisive only for the submitted solver's status
  under this frozen optimistic screen. Because `mu_0` is still the source
  yield heuristic, `DEATH` is not an algorithmic lower bound, a route
  falsification, or a statement about every imaginable M16 algorithm.

A complete follow-on cost bridge must replace `rho_0` by a matched
`C_rho,50`, replace the heuristic multiplier by a proved relation/rank success
law, and check

```text
C_M16,50(Q) < C_rho,50(Q)
```

uniformly for `Q != O`, with `C_pre`, every attempted system, recovery,
deduplication, rank, sparse linear algebra, and final `[z]G=Q` verification
included.

## 10. Deterministic verdict rule

First apply the validity gate. A package with a missing source binding,
one-way root/recovery proof, omitted target, mixed cost units, or uncharged
preprocessing is `INVALID_CONTRACT`. That is not a mathematical death result;
its scientific disposition is `INCONCLUSIVE`.

For a valid exact package, use the following mutually exclusive rule:

| Verdict | Exact condition | Meaning |
|---|---|---|
| `PASS` | Sections 4-8 are proved for every `R != O`, finite certified upper bounds exist, and `(P_U : Q) + mu_0*(U : Q) < rho_0` (hence `U <= B_net(P_U) <= B`) | The exact direct-System-(4) all-roots plus complete-recovery construction, with target-independent setup counted once, survives the optimistic source-model screen. It does not prove a sub-Pollard ECDLP algorithm. |
| `DEATH` | Sections 4-8 are proved, certified lower bounds exist, and `(P_L : Q) + mu_0*(L : Q) >= rho_0` | The submitted exact construction misses the frozen optimistic preprocessing-aware screen. This kills its candidacy under this contract; it is not a universal runtime lower bound. |
| `INCONCLUSIVE` | Every other valid case, including a cost interval that crosses the preprocessing-aware threshold, a one-sided bound that does not separate it, or any missing end-to-end equal-success bridge | The available mathematics does not decide the cost side. |

If a future complete-cost theorem is also claimed, it receives a separate
`END_TO_END_PASS` only under the strict uniform equal-success inequality in
Section 9. Without that theorem, even `PASS` above leaves the ECDLP conclusion
`INCONCLUSIVE`.

At audited base `6cde278`, no exact target-adaptive all-roots algorithm,
two-sided direct-system recovery theorem, or PFPO bracket `[L,U]` is present.
The current verdict is therefore `INCONCLUSIVE`, not `DEATH`.

## 11. Relation to the proved `q > 2^148` no-go

`M16LiftableSixWidthNoGo.lean` studies a different model. It fixes:

1. an explicit signed width-six table;
2. one target-independent list of `q` residual points;
3. coverage only through a global sign and translated table images.

Its `q` counts literal residual slots. It is not runtime, PFPO, memory,
solver nodes, Gröbner rows, recovery work, or the number of System-(4) roots.

The solver contracted here is target-adaptive because `X_R` changes the
polynomial system. Its roots may be generated implicitly by elimination and
need not have the fixed translated-image form. The `q > 2^148` theorem is
therefore outside this solver model and supplies no lower bound `L` for
Section 8. In particular, comparing `2^148` directly with `B < 2^115` would be
a unit and model error.

Conversely, a proposed solver that actually factors through the exact fixed
width-six table and target-independent residual list falls back inside the
proved model and must respect the `q > 2^148` conclusion. A successful
target-adaptive all-roots bracket would not refute that theorem.

## 12. Missing bridges

The present `INCONCLUSIVE` verdict is localized to the following obligations.

1. A literal, target-specializable representation of direct `S_17` with an
   exact coefficient convention and no hidden materialization assumption.
2. A terminating exact algorithm for every distinct `F_p` root of the 64
   variable, 65 equation direct System (4).
3. A two-sided root-set bridge for every alternate circuit, recursive,
   projective, radical, saturation, or extension-field representation used by
   that algorithm.
4. Complete handling of degree drops, roots at infinity, denominator strata,
   nonreduced components, multiplicities that affect work, and
   extension-only solutions.
5. The exact equality `Recover(R,x)=Fib_R(x)`, including empty fibers and every
   sign, repetition, target-sign, and global-negation case.
6. Canonical row deduplication with exact multiplicity and back-pointer
   accounting.
7. A uniform 50 percent PFPO lower and upper bracket for every nonidentity
   target, with retries and completeness certificates charged.
8. A full target-independent preprocessing ledger counted once for the plain
   single target.
9. If any ECDLP conclusion is sought, proved recoverable-relation yield,
   independent-rank acquisition, sparse linear algebra, candidate recovery,
   and a matched equal-success Pollard PFPO expansion.

None of these gaps is filled by the exact factor-base census, by equation
counts, by the width-six no-go, or by the source's heuristic relation yield.

## 13. Explicit non-attack boundary

This contract authorizes only source inspection, mathematical specification,
proof, and static review. It authorizes zero CPU-hours and zero GPU-hours for
root enumeration, solver execution, parameter sweeps, target sampling, or
relation collection. It authorizes no public-key, wallet, address, challenge,
or third-party target input; no discrete-log recovery; no exact secp256k1
target computation; and no deployment or benchmarking.

It also authorizes no edits to tasks, status, generated state, proposal state,
route state, retention, promotion, or experiment authorization. Any future
implementation or bounded run requires a new dated owner decision. Even a
mathematical `PASS` here would mean only that one exact solver construction
survived an optimistic cost screen.
