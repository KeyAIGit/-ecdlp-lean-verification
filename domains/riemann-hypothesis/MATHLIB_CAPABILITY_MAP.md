# RH-001 pinned Mathlib capability and barrier map

Status: **drafted from the exact pinned revision; independently replayed
2026-08-05 with 0 mismatches (all positive rows) and 12/12 negative rows
confirmed — see `notes/reviews/RH001_INDEPENDENT_REPLAY_2026_08_05.md` and
the dated addendum at the end of this file**

Audit date: 2026-08-04

Mathlib revision: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`
(v4.31.0 in this repository's `lake-manifest.json`)

Canonical target: `_root_.RiemannHypothesis`

Companion replay record: `MATHLIB_SEARCH_LOG.md`

## Decision summary

The pinned library already contains a serious formal analytic-number-theory
base: the Riemann zeta function, its pole-removed entire completion, functional
equations, the exact RH proposition, trivial zeros, nonvanishing for
`re(s) ≥ 1`, and a closed discrete zero set finite in compact windows.

It does **not** contain the next route interfaces needed by the admitted RH
criteria:

1. no named standard Riemann xi function or exact xi-to-zeta zero bridge;
2. no zeta- or xi-specialized multiplicity/divisor API;
3. no global enumeration, symmetric cutoff, or multiplicity-aware sum over
   nontrivial zeros;
4. no zeta/xi order-one growth theorem or Hadamard factorization;
5. no Riemann-Weil explicit formula, Li coefficients, Li criterion, or
   Nyman-Beurling specialization.

Generic analytic order, meromorphic divisor, Mellin, Jensen,
Phragmen-Lindelof, `Lp`, simple-function density, and fractional-part machinery
exist. They reduce some implementation cost, but they do not discharge the
zeta-specific statements.

The route-neutral first mathematical gate is an exact bridge from Mathlib's
target to the source-side critical-line and zero-free-half-plane formulations.
An entire normalized `riemannXi` bridge and multiplicity preservation are then
shared infrastructure for the Li/Weil and explicit-formula routes, but are not
prerequisites for Nyman-Beurling. This is foundation work, not evidence that RH
is closer to solution. No RH Lean declaration may be added or counted until a
non-ECDLP result ledger and axiom audit cover it.

## Meaning of the audit labels

| label | meaning |
|---|---|
| `PRESENT` | an exact reusable declaration exists at the pinned revision |
| `GENERIC` | reusable general infrastructure exists, but no zeta/xi specialization was found |
| `DERIVABLE-CANDIDATE` | the audited declarations appear sufficient for a theorem-sized bridge, but no such declaration exists yet |
| `NOT-FOUND-IN-SCOPE` | the reproducible searches in `MATHLIB_SEARCH_LOG.md` returned no declaration-level hit in the audited source scope |

`NOT-FOUND-IN-SCOPE` is deliberately weaker than a claim that no logically
equivalent theorem exists anywhere in Mathlib. The audit distinguishes missing
reusable API from mathematical non-derivability.

## Exact formal target

Pinned `Mathlib/NumberTheory/LSeries/RiemannZeta.lean:182` defines:

```lean
def RiemannHypothesis : Prop :=
  ∀ (s : ℂ) (_ : riemannZeta s = 0)
    (_ : ¬∃ n : ℕ, s = -2 * (n + 1)) (_ : s ≠ 1),
    s.re = 1 / 2
```

This remains the sole target. A xi-line theorem may later be proved equivalent
to it, but must not replace it with a competing proposition.

Semantic points that any bridge must preserve:

- `riemannZeta` is totalized at the classical pole `s = 1`;
- the target explicitly excludes negative even trivial zeros and `s = 1`;
- the zero hypothesis itself rules out `s = 0`, since `riemannZeta_zero` gives
  `ζ(0) = -1/2`;
- `riemannZetaZeros : Set ℂ` records membership only, not multiplicity;
- the target does not itself package the critical strip, conjugation symmetry,
  a zero ordering, or a zero-counting function.

## Declaration-level inventory

All locators below are line numbers at the pinned revision.

### Riemann zeta and its completion

| capability | label | exact pinned declaration | boundary |
|---|---|---|---|
| zeta function | `PRESENT` | `riemannZeta`, `RiemannZeta.lean:119` | totalized function `ℂ → ℂ` |
| analyticity | `PRESENT` | `differentiableAt_riemannZeta`, line 137; `analyticOn_riemannZeta`, line 144 | away from `s = 1` |
| completed zeta | `PRESENT` | `completedRiemannZeta`, line 67 | totalized at exceptional points |
| pole-removed completion | `PRESENT` | `completedRiemannZeta₀`, line 63 | additive pole correction |
| entire completion | `PRESENT` | `differentiable_completedZeta₀`, line 89 | global differentiability over `ℂ` |
| relation between completions | `PRESENT` | `completedRiemannZeta_eq`, line 84 | exact source for all sign algebra |
| completion symmetry | `PRESENT` | `completedRiemannZeta₀_one_sub`, line 99; `completedRiemannZeta_one_sub`, line 105 | symmetry under `s ↦ 1-s` |
| zeta/completion relation | `PRESENT` | `riemannZeta_def_of_ne_zero`, line 152; `riemannZeta_eq_completedRiemannZeta₀`, line 157; `riemannZeta_eq_mul_completedRiemannZeta₀`, line 162 | exceptional-point hypotheses differ |
| zeta functional equation | `PRESENT` | `riemannZeta_one_sub`, line 176 | carries negative-integer and pole exclusions |
| residue at one | `PRESENT` | `riemannZeta_residue_one`, line 239 | punctured-neighborhood limit |
| local Laurent remainder | `PRESENT` | `tendsto_riemannZeta_sub_one_div`, `ZetaAsymp.lean:332`; `isBigO_riemannZeta_sub_one_div`, line 365 | local statement, not a global meromorphic specialization |

### Zeros, half-planes, and convergent formulae

| capability | label | exact pinned declaration | boundary |
|---|---|---|---|
| trivial zeros | `PRESENT` | `riemannZeta_neg_two_mul_nat_add_one`, `RiemannZeta.lean:171` | negative even integers `-2(n+1)` |
| right open half-plane nonvanishing | `PRESENT` | `riemannZeta_ne_zero_of_one_lt_re`, `Dirichlet.lean:326` | `1 < re(s)` |
| right closed half-plane nonvanishing | `PRESENT` | `riemannZeta_ne_zero_of_one_le_re`, `Nonvanishing.lean:410` | `1 ≤ re(s)`, including the assigned value at `1` |
| zero set | `PRESENT` | `riemannZetaZeros`, `ZetaZeros.lean:33`; `mem_riemannZetaZeros`, line 35 | set-valued, no multiplicity |
| closed/discrete zero set | `PRESENT` | `isClosed_riemannZetaZeros`, line 57; `isDiscrete_riemannZetaZeros`, line 60 | topological discreteness |
| finite zeros in compact windows | `PRESENT` | `IsCompact.inter_riemannZetaZeros_finite`, line 64 | finite set intersection |
| escape from compacts | `PRESENT` | `tendsto_riemannZeta_cofinite_cocompact`, line 70 | cofinite-to-cocompact statement |
| Dirichlet series | `PRESENT` | `zeta_eq_tsum_one_div_nat_cpow`, `RiemannZeta.lean:204` | only `1 < re(s)` |
| Euler product | `PRESENT` | `riemannZeta_eulerProduct_hasProd`, `EulerProduct/DirichletLSeries.lean:89`; `riemannZeta_eulerProduct`, line 102 | only `1 < re(s)` |
| exponential-log Euler product | `PRESENT` | `riemannZeta_eulerProduct_exp_log`, line 160 | only `1 < re(s)` |
| von Mangoldt arithmetic function | `PRESENT` | `ArithmeticFunction.vonMangoldt`, `VonMangoldt.lean:65`; `vonMangoldt_sum`, line 102 | arithmetic side only |
| zeta logarithmic derivative | `PRESENT` | `LSeries_vonMangoldt_eq_deriv_riemannZeta_div`, `Dirichlet.lean:434` | only `1 < re(s)` |
| L-series derivatives | `PRESENT` | `LSeries_deriv`, `LSeries/Deriv.lean:86`; `LSeries_iteratedDeriv`, line 133 | within the absolute-convergence half-plane |

### Reusable generic analytic infrastructure

| capability | label | exact pinned declaration | missing specialization |
|---|---|---|---|
| real gamma factor | `PRESENT` | `Gammaℝ`, `Gamma/Deligne.lean:43` | already used by completed zeta |
| gamma zero classification | `PRESENT` | `Gammaℝ_eq_zero_iff`, line 73 | must be combined with exact nontrivial-zero exclusions |
| inverse gamma entire | `PRESENT` | `differentiable_Gammaℝ_inv`, line 88 | does not by itself give a xi/zeta zero bridge |
| analytic zero order | `GENERIC` | `analyticOrderAt`, `Analysis/Analytic/Order.lean:47`; `analyticOrderAt_ne_zero`, line 129; product law, line 497 | no `analyticOrderAt riemannZeta` theorem |
| meromorphic order | `GENERIC` | `meromorphicOrderAt`, `Analysis/Meromorphic/Order.lean:47` | no zeta specialization |
| meromorphic divisor | `GENERIC` | `MeromorphicOn.divisor`, `Analysis/Meromorphic/Divisor.lean:39` | no zeta or xi divisor |
| Jensen formula and divisor bound | `GENERIC` | `MeromorphicOn.circleAverage_log_norm`, `Analysis/Complex/JensenFormula.lean:307`; `AnalyticOnNhd.sum_divisor_le`, line 389 | no zeta/xi growth input |
| Phragmen-Lindelof | `GENERIC` | `PhragmenLindelof.vertical_strip`, `Analysis/Complex/PhragmenLindelof.lean:275` | no zeta boundary-growth package |
| Mellin transform | `GENERIC` | `mellin`, `Analysis/MellinTransform.lean:91`; `HasMellin`, line 160 | no Nyman fractional-part identity |
| Mellin inversion | `GENERIC` | `mellinInv_mellin_eq`, `Analysis/MellinInversion.lean:98` | substantial convergence and integrability hypotheses remain |
| functional-equation Mellin pair | `GENERIC` | `WeakFEPair.hasMellin`, `LSeries/AbstractFuncEq.lean:414`; zeta construction input `hurwitzEvenFEPair`, `HurwitzZetaEven.lean:254` | used by the existing zeta construction, but not a Nyman closure theorem |
| complete `Lp` space | `GENERIC` | `MeasureTheory.Lp.instCompleteSpace`, `LpSpace/Complete.lean:378` | no RH-specific objects |
| `L²` inner-product space | `GENERIC` | `MeasureTheory.L2.innerProductSpace`, `MeasureTheory/Function/L2Space.lean:192`; the module imports `GramMatrix` | exact Nyman functions and Gram entries still absent |
| simple functions dense in `Lp` | `GENERIC` | `Lp.simpleFunc.isDenseEmbedding`, `SimpleFuncDenseLp.lean:648`; `denseRange`, line 670 | assumes `Fact (1 ≤ p)` and `p ≠ ∞`; no Báez-Duarte span or Gram system |
| fractional part | `GENERIC` | `Int.fract`, `Algebra/Order/Floor/Defs.lean:259` | no `ρ_a(x) = fract(1/(ax))` measurability/integrability package |

### Missing named route interfaces

| interface | label | consequence |
|---|---|---|
| standard Riemann xi | `NOT-FOUND-IN-SCOPE` | no entire object whose zeros are already identified with nontrivial zeta zeros |
| conjugation symmetry for zeta/completion | `NOT-FOUND-IN-SCOPE` | fourfold zero symmetry is not a reusable declaration |
| critical-strip localization | `NOT-FOUND-IN-SCOPE` | must be derived with the xi bridge and right-half-plane nonvanishing |
| zeta/xi analytic order equality | `NOT-FOUND-IN-SCOPE` | multiplicity is not transported |
| zeta/xi divisor | `NOT-FOUND-IN-SCOPE` | no multiplicity-aware global zero object |
| nontrivial-zero enumeration or counting function | `NOT-FOUND-IN-SCOPE` | no canonical `N(T)`, ordered sequence, or symmetric finite truncation |
| multiplicity-aware zero sum | `NOT-FOUND-IN-SCOPE` | Li and explicit-formula sums cannot yet be stated source-faithfully |
| vertical growth and finite/order-one entire growth | `NOT-FOUND-IN-SCOPE` | Hadamard and contour arguments are blocked |
| canonical product or Hadamard factorization | `NOT-FOUND-IN-SCOPE` | no product over xi zeros |
| Riemann-Weil prime-zero explicit formula | `NOT-FOUND-IN-SCOPE` | von Mangoldt and the right-half-plane log derivative are only inputs |
| Li/Keiper coefficients and criterion | `NOT-FOUND-IN-SCOPE` | local derivative and global zero-sum definitions are absent |
| Nyman-Beurling/Báez-Duarte objects and equivalence | `NOT-FOUND-IN-SCOPE` | only generic `Lp`, Mellin, and fractional-part infrastructure exists |

## Gate 0: safe entire xi specification

### Sign source of truth

There is a documentation inconsistency inside the pinned
`RiemannZeta.lean`:

- the top module comment describes the pole correction with the opposite sign;
- the inline definition comment and the proved theorem
  `completedRiemannZeta_eq` agree with each other.

The theorem, not the prose comment, is authoritative:

```text
Λ(s) = Λ₀(s) - 1/s - 1/(1-s).
```

Multiplying by `s(s-1)` gives, away from `0` and `1`,

```text
s(s-1) Λ(s) = 1 + s(s-1) Λ₀(s).
```

Therefore the safe proposed entire normalization is:

```lean
noncomputable def riemannXi (s : ℂ) : ℂ :=
  (1 + s * (s - 1) * completedRiemannZeta₀ s) / 2
```

This is a proposed contract, not a declaration currently in Mathlib or this
repository.

### Required bridge package

The first theorem-sized package should prove, in this order:

1. `Differentiable ℂ riemannXi` from
   `differentiable_completedZeta₀` and polynomial closure;
2. `riemannXi (1-s) = riemannXi s` from
   `completedRiemannZeta₀_one_sub` and invariance of `s(s-1)`;
3. `riemannXi 0 = 1/2` and `riemannXi 1 = 1/2` directly from the definition;
4. away from `0,1`, equality with
   `s(s-1) completedRiemannZeta s / 2`;
5. the exact zero correspondence:

```lean
theorem riemannXi_eq_zero_iff_riemannZeta_eq_zero
    {s : ℂ} (hs0 : s ≠ 0) (hs1 : s ≠ 1)
    (htriv : ¬ ∃ n : ℕ, s = -2 * (n + 1)) :
    riemannXi s = 0 ↔ riemannZeta s = 0
```

The proof obligation is not just field algebra. It must use
`Gammaℝ_eq_zero_iff` to show that the gamma factor is nonzero under exactly the
stated exclusions.

After that, prove in a non-circular order:

- xi is nonzero at every negative even point: symmetry maps `-2(n+1)` to
  `2n+3`, where the zero bridge and
  `riemannZeta_ne_zero_of_one_le_re` give nonvanishing; handle `0` and `1`
  separately with the already proved values `1/2`;
- every remaining xi zero lies in `0 < re(s) < 1`, using xi symmetry, the
  just-proved exclusion, and right-half-plane nonvanishing;
- the xi zero-line formulation is equivalent to the existing
  `_root_.RiemannHypothesis`;
- at each nontrivial zero, `analyticOrderAt riemannXi s` equals
  `analyticOrderAt riemannZeta s`.

Conjugation symmetry is a separate `S1` declaration/proof obligation. It must
not be silently inferred from the `s ↦ 1-s` functional equation. Route A needs
all of the following before a one-sided Li criterion or Gram norm is used:

- `riemannXi (conj s) = conj (riemannXi s)` and the analogous zeta statement
  on its valid domain;
- preservation of zero multiplicity under conjugation and `s ↦ 1-s`;
- invariance of the xi divisor under `ρ ↦ 1-conj(ρ)`.

## Dependency DAGs for the three admitted RH-002 routes

The target-equivalence gate is common infrastructure and is not counted as a
theorem-bearing route. The xi/divisor package is shared by Routes A and C only.

### Cross-route target bridge

```text
_root_.RiemannHypothesis + exact exceptional-point contract
  + zeta functional equation and GammaR zero classification
  + zeta nonvanishing for re >= 1
  -> exact nontrivial-zero domain
  -> equivalence with zero-free re > 1/2 and critical-line formulations
```

This bridge must be stated directly for Mathlib's totalized `riemannZeta` and
must carry the pole, trivial-zero, and gamma-factor exclusions. It does not
require a global divisor or zero multiplicity.

### Routes A/C xi and global-zero gate

```text
completedRiemannZeta₀ entire + s <-> 1-s symmetry
  + Gammaℝ zero classification
  + zeta nonvanishing for re >= 1
  -> normalized entire riemannXi
  -> xi/zeta zero correspondence with exact exceptions
  -> xi nonvanishing at 0, 1, and negative even points
  -> critical-strip localization and target equivalence
  -> conjugation symmetry for xi/zeta
  -> analytic-order equality at nontrivial zeros
  -> multiplicity-aware xi divisor invariant under reflection/conjugation
  -> finite compact restrictions with multiplicity
```

### Route A: Weil-first Li positivity

```text
target bridge + A/C gate -> divisor and symmetries
A/C gate -> xi vertical growth and order one
divisor + order-one growth -> normalized Hadamard product
Hadamard product + local analytic log and iterated derivatives
  -> local/global Li equality

divisor + finite cutoff sums
  + Lagarias/Bombieri-Lagarias weighted summability hypothesis (1.6)
  + star convergence of sum 1/rho
  + existence of each Li |rho| <= T cutoff limit
  + local/global equality
  -> Li coefficients with multiplicity

divisor + Weil |Im rho| < T limit + exact Weil test class
  + absolute convergence of the Weil scalar-product combination
  -> Riemann-Weil explicit formula

Li coefficients + explicit convention bridge to Lagarias G_n functions
  -> zero-side Hermitian Weil Gram identity as basis and diagnostic

explicit formula + convention bridge + Lagarias G_n functions
  -> arithmetic prime/archimedean representation of the same Weil form
  -> new uniform positivity/coercivity theorem for every positive index
  -> one-sided Li equivalence, using rho -> 1-conj(rho) symmetry
  -> _root_.RiemannHypothesis
```

The local logarithm branch requires its own contract: exhibit a neighborhood of
`1` on which xi is nonzero; construct analytic `L` with `exp L = xi`; fix a
normalization or prove the Li derivative is branch-independent; then prove the
local derivative equals the global star-sum through the normalized Hadamard
product. A global `Complex.log ∘ riemannXi` is not an acceptable substitute.

The admitted main track is the arithmetic Weil-first branch, not a bypass
through finite zero-side Gram matrices. The zero-side identity selects a
structured basis and exposes the exact target coefficient; the explicit
formula must feed the prime/archimedean representation used by the proposed
uniform positivity theorem.

The Bombieri/Weil and Lagarias formulations are not definitionally the same.
Before transporting positivity, RH-002 must record and prove the relevant
inverse-Mellin correspondence, autocorrelation/conjugation convention,
regularity and decay, moment conditions, quadratic-form sign, and zero-cutoff
conversion. Until then, a sign obtained in one convention cannot be used in the
other.

### Route B: Nyman-Beurling/Báez-Duarte closure

```text
cross-route target bridge
  + L2 inner-product/Gram API + Lp completeness/closure + Int.fract + Mellin API
  -> freeze real H = L2((0,infinity), dx), chi = 1_(0,1],
     rho_a(x) = fract(1/(a*x)), and B_nat = span {rho_a | a in N, 1 <= a}
  -> measurability, L2 membership, dilation, and finite spans
  -> source identity -zeta(s)/s = integral_0^infinity x^(s-1) rho_1(x) dx
     for exactly 0 < re(s) < 1
  -> complexification and the equation (2.6) Fourier-Mellin isometry
     M(f)(tau) = integral_0^infinity x^(-1/2+i*tau) f(x) dx
     into L2(R, d tau/(2*pi))
  -> source-exact closure equivalence, including the 1/zeta direction
  -> explicit approximant family with a proved bound B(N) -> 0
  -> _root_.RiemannHypothesis
```

This is the Báez-Duarte natural-span `(0,∞), dx` normalization. The closure is
first a real-Hilbert-space statement; the Fourier-Mellin argument uses its
complexification with the transform and target measure above. The v2 PDF
literally typesets the target interval as `(∞,∞)` and its measure as
`(2π)^(-1/2) dt`; these are recorded as apparent source errata, not copied into
the formal contract. Renaming the bound variable from `t` to `τ` to match (2.6),
substituting `x = exp(u)`, and applying standard Plancherel to the unnormalized
Fourier transform gives `ℝ` and `dτ/(2π)`. The source extract and formal proof
must preserve this derivation explicitly. If a later source extract uses the
classical `(0,1)` generators `{θ/x}`, its Mellin identity contains the affine
term `θ/(s-1) - θ^s ζ(s)/s`; cancellation requires the source side
condition `Σ c_k θ_k = 0`. The two normalizations must not be mixed silently.
The published RH-to-closure direction also uses RH-dependent Littlewood and
Lindelof inputs for `1/ζ`. Those are legitimate inside an equivalence proof
with RH as hypothesis, but importing them as unconditional pilot estimates
would be circular. In particular, the raw natural approximants
`Σ_{a≤N} μ(a)ρ_a` are not an admitted pilot family: Báez-Duarte records that
they diverge in `H`. Any admitted modification needs a distinct source contract
and a non-circular decreasing error target.

### Route C: explicit-formula dependency screen; direct route parked

```text
vonMangoldt + zeta'/zeta for re > 1
  + cross-route target bridge and A/C multiplicity-aware zero gate
  + vertical growth, contour shift, pole/zero residues
  -> source-exact prime-zero explicit formula
  -> a named global test-function/inequality family with frozen parameters,
     norm, transform convention, and off-line-zero exclusion mechanism
  -> uniform bound excluding every off-line zero, not density-one control
  -> _root_.RiemannHypothesis
```

No such family is currently named. The explicit formula remains mandatory
shared infrastructure for Weil-first Li, but Route C receives no independent
theorem-execution budget until a concrete family survives a new review.

## Severity-ranked barriers

| severity | barrier | blocks | exit evidence |
|---|---|---|---|
| `S0-TRUST` — **CLOSED 2026-08-05** by PR #298 (`d6e146fa`) | non-ECDLP domain result ledger and generated axiom audit were absent | adding or counting any RH Lean theorem | dedicated ledger schema, generated audit, CI coverage, and isolation test — all merged and green |
| `S0-SEMANTIC` — **CLOSED 2026-08-06** by `RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md` | totalized exceptional values and the `Λ₀` sign inconsistency invite a false bridge | every route | reviewed xi contract derived from proved declarations, with `0`, `1`, trivial-zero, and gamma cases explicit — all independently accepted |
| `S1-TARGET` — **CLOSED 2026-08-06** by PR #299 (`288d65b`) | pinned Mathlib has no exact bridge from its target to the source-side critical-line and zero-free-half-plane formulations | every route | repo-local kernel-checked exceptional-point and functional-equation bridge plus independent statement review — merged and green |
| `S1-XI` — **CLOSED 2026-08-06** by PR #304 (`afdae08`) | pinned Mathlib has no standard entire xi/zero bridge | Li/Weil and explicit formula | independently accepted, kernel-checked normalized xi package with twelve ledgered and axiom-audited declarations — merged and green |
| `S1-MULTIPLICITY` — **OPEN; local xi/zeta analytic-order equality discharged by PR #304** | zero set loses analytic multiplicity and no conjugation/reflection action preserves it | Li/Weil and explicit formula | remaining exit evidence: zeta/xi divisor interface and multiplicity-preserving divisor symmetries |
| `S1-GLOBAL-ZEROS` | no global enumeration, symmetric truncation, convergence, or counting API | Li sums, canonical product, explicit formula | finite divisor sums, weighted summability, star convergence of `Σ 1/ρ`, existence of source-matched limits with multiplicity, including `|ρ| ≤ T` for Li and `|Im ρ| < T` for Weil, plus absolute convergence of the Weil scalar-product combination |
| `S1-GROWTH` | no zeta/xi vertical or order-one growth theorem | Hadamard and contour shifts | explicit quantitative bounds sufficient for the selected theorem |
| `S1-CONJ` | no named zeta/xi conjugation symmetry or multiplicity-preserving fourfold zero action | one-sided Li positivity and Weil Gram identities | conjugation theorem plus divisor invariance under `ρ ↦ 1-conj(ρ)` |
| `S1-EXPLICIT` | no Riemann-Weil explicit formula | Weil-first Li and direct explicit-formula route | exact test class, transform convention, residues, and limiting procedure |
| `S2-LI` | no local/global Li definitions or positivity bridge | Li route | local analytic log, iterated derivative, zero-sum equality, Gram identity |
| `S2-NYMAN` | no specialized fractional-part `L²` objects or closure equivalence | Nyman route | source-exact objects, integrability, Mellin identity, and both implications |

## Semantic mismatch register

| source-side concept | pinned representation | mismatch to close |
|---|---|---|
| meromorphic `ζ` with a pole at `1` | total function with assigned exceptional value | local statements must exclude or explicitly handle `1` |
| standard entire `ξ` | only additive pole-removed `Λ₀` exists | zeros of `Λ₀` are not zeta's nontrivial zeros |
| multiset/divisor of zeros | `riemannZetaZeros : Set ℂ` | multiplicity is erased |
| sum over zeros | finite intersection of a set with compact windows | no ordering, cutoff, or multiplicity convention; Li's `|ρ| ≤ T` and Weil's `|Im ρ| < T` limits are distinct contracts |
| conditionally convergent Li star-sum | no zero-sum API | arbitrary `tsum`, rearrangement, or substitution of a different height cutoff would change the statement |
| global `log ξ` notation in paper prose | no branch-free global analytic logarithm | use a local analytic log near a proved nonzero point |
| Weil test-function class and transform | generic Fourier/Mellin infrastructure | exact regularity, symmetry, decay, normalization, and residue conditions absent |
| Hilbert-space Nyman formulation | generic complete `L²` inner-product space and GramMatrix API | Báez-Duarte uses `L²((0,∞), dx)`, `χ = 1_(0,1]`, and `ρ_a(x)={1/(ax)}`; exact membership, span, closure, Mellin-Plancherel, and analytic Gram entries are absent. The alternative `(0,1)` convention has an affine Mellin term and coefficient constraint and must not be substituted silently |
| density or average zero-free estimates | universal line statement | density-one information cannot exclude rare or finite off-line zeros |
| finite verified zero range | universal proposition | computation remains bounded evidence only |

## RH-002 admission decision

All three route families receive the same bounded **desk-review** budget in
RH-002. Only two receive candidate status. If Nyman survives desk review, its
subsequent mathematical pilot is capped at 20% of the execution budget; this is
separate from equal-budget screening.

Before execution, RH-002 must preregister for each survivor the threshold to be
beaten, the parameter tending to infinity, and a strict asymptotic margin. A
finite range, an unspecified `O`-constant, or a uniform but non-decaying bound
does not satisfy day-45 evidence.

| candidate or route family | disposition | required day-45 evidence | immediate death condition |
|---|---|---|---|
| Weil-first Li positivity | `ADMIT` as the main direct screen | a named unconditional theorem with explicit variables, constants, and range, plus a proved chain to `Re λ_n` for unbounded `n` whose remainder beats a preregistered positivity/coercivity threshold on an infinite tail | only definitions/equivalences, finite positive coefficients or PSD blocks, numerics, a rearranged conditional sum, a bound with no strict asymptotic margin, or an RH-equivalent premise |
| Nyman-Beurling/Báez-Duarte | `ADMIT` as a pilot capped at 20% of later execution budget | a concrete natural-span family `F_N`, a complete identity for `‖χ-F_N‖²`, and an explicit bound `B(N)` with proved `B(N) -> 0` and preregistered rate/constants | only a finite Gram solve, visually decreasing error, a uniform but non-decaying bound, the divergent raw family `Σ_{a≤N} μ(a)ρ_a`, or unconditional use of RH-derived Littlewood/Lindelof or zero-free `re(s)>1/2` input |
| explicit formula plus a global inequality | `PARK` as a direct route; `REQUIRED DEPENDENCY SCREEN` for Li | a named test family with frozen function, parameters, norm, transform, and proof that its bound excludes an individual off-line zero at arbitrary height | family still unnamed, or output controls only bounded height, averages, mollified values, or density-one zeros |

The de Bruijn-Newman route, free-form mollifier sweeps, random-matrix/spectral
analogies without an identified operator, and bounded zero computation remain
`PARK` or evidence-only. Equivalent criteria are not ranked as easier merely
because their surface language differs from RH.

Every survivor also requires independent replay from the pinned sources with
the exact multiplicity, cutoff, measure, branch, transform, and sign
conventions. No source-equivalent hypothesis may be relabeled as a new bound.

## First implementable foundation and stop rule

After `S0-TRUST` is closed, the first Lean PR should contain only the
route-neutral target-equivalence bridge. A following A/C-only foundation PR may
contain the normalized xi bridge package. Neither should contain Li
coefficients, a zero enumeration, or a claim of progress on RH.

Acceptance requires:

- exact name-collision and pinned-API checks;
- a paper derivation from `completedRiemannZeta_eq` rather than the conflicting
  module comment;
- explicit exceptional-point and gamma-zero cases;
- narrow build, full `lake build`, no-sorry scan, and the new domain axiom audit;
- independent review of the Lean statements against the mathematical contract.

Stop or split the package if any proof requires weakening the exclusions,
assuming a hidden nonvanishing fact, or treating totalized exceptional values as
ordinary meromorphic values. A clean blocker is preferable to a false xi bridge.

## Pinned formal and route sources

- [`RiemannZeta.lean`](https://github.com/leanprover-community/mathlib4/blob/fabf563a7c95a166b8d7b6efca11c8b4dc9d911f/Mathlib/NumberTheory/LSeries/RiemannZeta.lean)
- [`ZetaZeros.lean`](https://github.com/leanprover-community/mathlib4/blob/fabf563a7c95a166b8d7b6efca11c8b4dc9d911f/Mathlib/NumberTheory/LSeries/ZetaZeros.lean)
- [`Nonvanishing.lean`](https://github.com/leanprover-community/mathlib4/blob/fabf563a7c95a166b8d7b6efca11c8b4dc9d911f/Mathlib/NumberTheory/LSeries/Nonvanishing.lean)
- [`Dirichlet.lean`](https://github.com/leanprover-community/mathlib4/blob/fabf563a7c95a166b8d7b6efca11c8b4dc9d911f/Mathlib/NumberTheory/LSeries/Dirichlet.lean)
- [`Gamma/Deligne.lean`](https://github.com/leanprover-community/mathlib4/blob/fabf563a7c95a166b8d7b6efca11c8b4dc9d911f/Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean)
- [`Analytic/Order.lean`](https://github.com/leanprover-community/mathlib4/blob/fabf563a7c95a166b8d7b6efca11c8b4dc9d911f/Mathlib/Analysis/Analytic/Order.lean)
- [`Meromorphic/Divisor.lean`](https://github.com/leanprover-community/mathlib4/blob/fabf563a7c95a166b8d7b6efca11c8b4dc9d911f/Mathlib/Analysis/Meromorphic/Divisor.lean)
- Loeffler and Stoll, [The Riemann zeta function in Lean](https://arxiv.org/abs/2503.00959), for totalization and construction context; pinned code remains authoritative.
- Lagarias, [Li coefficients and the Weil scalar product](https://arxiv.org/pdf/math/0404394), equations (1.1)-(1.9), Theorem 2.2, equation (3.1), and Theorem 3.1; exact extracts remain an RH source-package task.
- Bombieri, [official Clay problem description](https://www.claymath.org/wp-content/uploads/2022/05/riemann.pdf), section V, pages 8-9, for the Weil explicit-formula class, transform, cutoff, moment, and sign conventions.
- Báez-Duarte, [A strengthening of the Nyman-Beurling criterion, v2](https://arxiv.org/pdf/math/0202141), Theorem 1.1, equations (1.1)-(1.3), and (2.6)-(2.8), for the exact `L²((0,∞), dx)` criterion and Mellin normalization.

## Addendum 2026-08-05 (post-replay)

Recorded after the independent replay
(`notes/reviews/RH001_INDEPENDENT_REPLAY_2026_08_05.md`); nothing below
changes any label, any disposition, or any evidence status.

1. **Replay result.** All positive inventory rows confirmed at the exact
   claimed `file:line` (0 mismatches); all 12 `NOT-FOUND-IN-SCOPE` rows
   confirmed, with `riemannXi`, Hadamard factorization for finite-order
   entire functions, and any zeta/conjugation theorem additionally absent
   tree-wide at the pin. The `Λ₀` sign inconsistency between the module
   comment and `completedRiemannZeta_eq` is independently confirmed; the
   theorem remains authoritative. `riemannZeta_zero` (cited above without a
   locator) is at `RiemannZeta.lean:149`.
2. **Two additional `PRESENT` generic capabilities** (verified at the pin):
   Fourier-Plancherel on `L²` — `MeasureTheory.Lp.fourierTransformₗᵢ`,
   `Mathlib/Analysis/Fourier/LpSpace.lean:50`, and
   `MeasureTheory.Lp.norm_fourier_eq`, line 89 — which lowers the estimated
   cost of the `SC-NB-04` Fourier-Mellin isometry to the log-substitution
   and scaling unitaries plus the dense-core pointwise formula; and
   Borel-Caratheodory — `Complex.borelCaratheodory`,
   `Mathlib/Analysis/Complex/BorelCaratheodory.lean` — a generic input to
   future Landau-type log-derivative estimates. Also useful for `SC-NB-03`:
   the Abel-summation machinery `LSeries_eq_mul_integral`
   (`Mathlib/NumberTheory/LSeries/SumCoeff.lean:137`).
3. **Stop-rule reconciliation (dated note).** The missing-interface row
   "critical-strip localization … must be derived with the xi bridge" is
   superseded for the route-neutral node: the frozen `RH-003` contract
   (`TARGET_BRIDGE_CONTRACT.md`) derives localization FE-first from
   `riemannZeta_one_sub` inside the bridge package, as the "Cross-route
   target bridge" DAG above already requires ("exact nontrivial-zero
   domain" is a bridge output). The xi package still proves its own xi-side
   localization in the A/C follow-on. This note requires explicit reviewer
   acknowledgment at RH-003 exit.

## Addendum 2026-08-06: barrier `S0-TRUST` CLOSED

The severity table's `S0-TRUST` row ("non-ECDLP domain result ledger and
generated axiom audit do not yet exist") is closed. Evidence, one-to-one
against its exit string "dedicated ledger schema, generated audit, CI
coverage, and isolation test", all merged to `main` in PR #298 and green in
CI there:

1. **dedicated ledger schema** — `VERIFIED_RESEARCHOS.md` (strict 12-column
   parser; kernel-checked-only rule; the 12 pre-existing
   `ResearchOS.NumberTheory` declarations backfilled with a dated review);
2. **generated audit** — `ResearchOS/LedgerAxiomAudit.lean` generated from
   `data/researchos_result_registry.json`, elaborated by CI and validated by
   `scripts/check_axioms.py` with per-row `axiom_base` enforcement and
   native-aux-axiom provenance;
3. **CI coverage** — registry `--check`, inverse coverage
   ("built ⇒ ledgered ⇒ audited"), cross-import guard, tightened no-sorry
   exclusions, and the audit elaboration step in `ci.yml`;
4. **isolation test** — `scripts/check_ledger_isolation.py` + fixtures: no
   RH/ResearchOS result can reach the ECDLP headline surfaces.

Consequence: the "adding or counting any RH Lean theorem" block is lifted on
the infrastructure side. Every built RH module still requires its owning
review contract and must land with its `RH-*` ledger rows, registry entries,
audit lines, and promotion review in one PR, or inverse coverage fails CI.
Design record: `S0_TRUST_DESIGN.md` (Phase 1 executed; this addendum is its
Phase 2).

## Addendum 2026-08-06 (second): barrier `S1-TARGET` CLOSED

The severity table's `S1-TARGET` row ("no exact bridge from Mathlib's target
to the source-side critical-line and zero-free-half-plane formulations") is
closed by kernel check. Evidence: merged PR #299 (`288d65b`) builds
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/TargetBridge.lean` —
P1-P5 of `TARGET_BRIDGE_CONTRACT.md`, eight declarations, `lake build`
green, no-sorry gate green, generated audit green with `standard` axiom
base per row — with the eight `RH-BRIDGE-*` ledger rows and the promotion
review record (`notes/reviews/RH_BRIDGE_PROMOTION_2026_08_06.md`) in the
same PR. Independent statement review: reviewed-and-merged by the external
reviewer. The pinned-Mathlib inventory row "critical-strip localization"
correctly remains `NOT-FOUND-IN-SCOPE`; PR #299 supplies the missing bridge
only on the repo-local built surface. The cross-route target-bridge DAG node
is an operational dependency node, not an inventory row, and is now
discharged in-repo. One kernel round exposed exactly the pre-registered P1-d
witness-cast obligation; the audit-recorded alternate closed it (see the
promotion review record). No claim about the truth of RH is made. At this
addendum point the remaining severity rows included `S1-XI` (accepted contract
and draft staged, kernel promotion pending), `S1-MULTIPLICITY`,
`S1-GLOBAL-ZEROS`, `S1-GROWTH`, `S1-CONJ`, `S1-EXPLICIT`, and `S2-*`.
The fourth addendum records the later repo-local `S1-XI` closure.

## Addendum 2026-08-06 (third): barrier `S0-SEMANTIC` CLOSED

The severity table's semantic false-bridge risk is closed at the contract
boundary by `notes/reviews/RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`.
Independent review accepted all twelve X1-X11 declaration surfaces after
re-deriving the `completedRiemannZeta_eq` sign, checking `xi(0) = xi(1) =
1/2` from the entire formula, exhausting the larger `GammaR` zero set into
the zero and negative-even cases, preserving the canonical
`_root_.RiemannHypothesis`, and restricting analytic-order transport to an
open-strip neighborhood with a nonvanishing analytic cofactor.

This addendum closed only the reviewed semantic specification risk. At that
acceptance point the Lean draft was still outside every build target, so
`S1-XI` remained open pending a separate promotion. The fourth addendum records
that promotion. No divisor, conjugation, growth, zero-enumeration,
route-selection, or RH-truth claim was created by the semantic acceptance.

## Addendum 2026-08-06 (fourth): barrier `S1-XI` CLOSED

Merged PR #304 (`afdae08`) promotes the independently accepted X1-X11 surface
to `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean`: eleven
contract clauses represented by twelve public declarations. The final repaired
head passed the full repository build, no-incomplete-proof gate, complete
ResearchOS inverse ledger coverage, ECDLP axiom audit, and ResearchOS per-row
axiom audit with every new row at axiom base `standard`.

The first promotion head exposed one proof-only X11 composition-call error.
The synchronized built file, draft, and contract skeleton now use the
point-explicit `DifferentiableAt.fun_comp'`; no statement or claim boundary
changed. Details are retained in
`notes/reviews/RH_XI_PROMOTION_2026_08_06.md`.

This closes the repo-local normalized-xi and zero-bridge barrier `S1-XI`.
Pinned-Mathlib inventory rows remain `NOT-FOUND-IN-SCOPE`, because the package
is repository-local. X11 also discharges the local xi/zeta
`analyticOrderAt`-equality component of `S1-MULTIPLICITY`, but that barrier
remains open: no divisor interface, reflection-order package, or
multiplicity-preserving divisor symmetries are present. The package proves an
equivalence of formulations, not RH, and selects no theorem-bearing route.
## Addendum 2026-08-06 (fifth): `S1-CONJ` conjugation leg landed — barrier STILL OPEN

The RH-008 promotion change adds
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Conj.lean`: the sixteen
Z1-Z9 declarations of the independently accepted
`CONJ_SYMMETRY_CONTRACT.md` — conjugation symmetry for `riemannZeta`, both
completions, and the built `riemannXi`; set-level zero-set invariance under
conjugation; the fourfold zero action over `ρ`, `1 − ρ`, `conj ρ`,
`1 − conj ρ`; and pointwise `analyticOrderAt` transport under conjugation,
including the two generic complex-analysis lemmas that are genuinely absent at
the pin (`AnalyticAt.conj_conj`, `analyticOrderAt_conj_conj`, contract
obligation `S1C-ORD`).

Conjugation is proved independently of the functional equation, as this map
requires: from the Dirichlet series on `1 < re s` plus the pinned identity
principle on `{1}ᶜ`, with the totalized value at `s = 1` handled as the
coercion of a real number. `1 − s` enters only in Z8, through the already
kernel-checked bridge P3, after conjugation is established.

**`S1-CONJ` remains OPEN.** Its exit evidence is the conjugation theorem
*together with* divisor invariance under `ρ ↦ 1 − conj ρ`. This package
supplies the conjugation leg and the pointwise order transport only; the
divisor interface and multiplicity-preserving divisor symmetries belong to the
still-open `S1-MULTIPLICITY` package. Pinned-Mathlib inventory rows stay
`NOT-FOUND-IN-SCOPE`: the package is repository-local, and no conjugation
lemma for `riemannZeta`, `completedRiemannZeta(₀)`, `hurwitzZetaEven`, or any
`LSeries` exists at the pin.

The kernel verdict for this addendum is the required CI result on the exact
promotion head; the rows count as built only through a green merged change.
No claim about the truth of RH is made, and no route is selected.
## Addendum 2026-08-07 (sixth): barriers `S1-MULTIPLICITY` and `S1-CONJ` CLOSED

Merged PR #313 (`2a20629`) promotes the RH-009-accepted M1-M17 surface to
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean`: thirty-four
public declarations, kernel-checked by the full build on the exact merged
head, with complete inverse ledger coverage (81 rows → 82 declarations),
per-row axiom base `standard`, and the drafts-lane mirror byte-identical from
the first import. The only CI repair in the promotion round was prose: the
textual no-incomplete-proof scan tripped on this module's own claim-boundary
comment asserting the absence of the banned tokens; the comment was reworded
and no proof, statement, or tactic text changed.

This closes `S1-MULTIPLICITY`: the divisor/multiplicity interface over the
pinned `MeromorphicOn.divisor` carrier (pointwise value, nonnegativity,
finite local analytic and meromorphic order, support equal to the zero set)
for xi on arbitrary carriers and for zeta on the open critical strip, with
local-order transport and divisor invariance under all three
multiplicity-preserving symmetries.

Together with the merged conjugation package (PR #307, `c277b86`), the
divisor-invariance leg under `ρ ↦ 1 − conj ρ` is now kernel-checked, which is
the second and final item of the `S1-CONJ` exit evidence. `S1-CONJ` is
therefore CLOSED: conjugation theorem (PR #307) plus divisor invariance
(PR #313).

Boundaries unchanged by this addendum: every "finite order" in the package is
a finite LOCAL analytic or meromorphic order — `S1-GROWTH` remains OPEN with
no growth bound of any kind; `S1-GLOBAL-ZEROS` remains OPEN with no
enumeration, no counting function, and no infinitude claim; no route is
selected; and nothing in either closed barrier bears on the truth of the
Riemann Hypothesis.
