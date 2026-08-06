# RH-001 independent replay record

Date: 2026-08-05

Scope: adversarial, declaration-level replay of
`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` (all four inventory
tables plus the exact-target section and the sign-inconsistency claim) against
the exact pinned Mathlib revision. This record closes the `RH-001` exit bullet
"an independent reviewer can reproduce the inventory from the pinned revision"
with a durable, reproducible artifact. It claims no proof and no progress on
the Riemann Hypothesis.

## Method and revision identity

A fresh checkout of Mathlib was fetched at the exact pinned commit and
verified:

```bash
git init mathlib4 && cd mathlib4
git remote add origin https://github.com/leanprover-community/mathlib4
git fetch --depth 1 origin fabf563a7c95a166b8d7b6efca11c8b4dc9d911f
git checkout FETCH_HEAD
git rev-parse HEAD   # = fabf563a7c95a166b8d7b6efca11c8b4dc9d911f
```

Each positive row was checked with `nl -ba` + `sed`/`grep` on the pinned file:
the declaration name must exist, the claimed line must be the line of the
declaration keyword, and the claimed boundary/hypothesis note must be faithful
to the actual statement. Negative rows were re-searched over the audited scope
of `MATHLIB_SEARCH_LOG.md` with multiple name fragments per interface, then
strengthened by whole-tree greps over `Mathlib/`. Four independent replay
passes (three positive slices, one negative slice) were executed by separate
agents; a fifth and sixth agent adversarially reviewed the derived theorem
contract against the same tree (see `TARGET_BRIDGE_CONTRACT.md`).

## Result summary

- **Positive inventory: 0 mismatches.** Every declaration in all three
  capability tables exists at the exact claimed `file:line` with the claimed
  hypotheses and boundary semantics.
- **Negative inventory: 12/12 `NOT-FOUND-IN-SCOPE` rows confirmed**, none
  refuted; several are strengthened to whole-tree absence (see below).
- **Sign-inconsistency claim confirmed**: the top module comment of
  `RiemannZeta.lean` (line 20) states `Λ₀(s) = Λ(s) + 1/(s-1) - 1/s`, while the
  proved theorem `completedRiemannZeta_eq` (line 84) gives
  `Λ(s) = Λ₀(s) - 1/s - 1/(1-s)`, i.e. `Λ₀(s) = Λ(s) + 1/s - 1/(s-1)` — both
  correction terms opposite in sign. The per-declaration docstrings (lines 62,
  88) agree with the theorem; only the top module comment is inconsistent. The
  map's "theorem is authoritative" resolution is therefore independently
  verified.
- **Anchor completion**: `riemannZeta_zero : riemannZeta 0 = -1/2`, cited in
  the map's target section without a locator, is at
  `Mathlib/NumberTheory/LSeries/RiemannZeta.lean:149`.
- **Row-count reconciliation**: the map's tables contain 11 rows ("zeta and
  its completion"), 13 rows ("zeros, half-planes, and convergent formulae"),
  15 declaration rows across the 17-line "generic infrastructure" span
  (multi-declaration rows), and 12 negative-interface rows. Internal tasking
  digests that mention "12" or "15" rows for the first two tables refer to
  check counts (rows plus extra claims), not to missing rows. All rows of all
  tables were checked.
- **Candidate count**: the map's RH-002 admission table admits exactly three
  route families, satisfying the RH-001 output bullet "no more than three
  candidates admitted to RH-002".

## Additions surfaced by the replay (PRESENT capabilities not in the map)

Two generic capabilities exist at the pin and are recorded in the map's dated
addendum; they lower estimated formalization cost only and change no label,
no disposition, and no evidence status:

| capability | exact pinned declaration | relevance |
|---|---|---|
| Fourier-Plancherel on `L²` | `MeasureTheory.Lp.fourierTransformₗᵢ`, `Mathlib/Analysis/Fourier/LpSpace.lean:50`; `MeasureTheory.Lp.norm_fourier_eq`, line 89 | reduces `SC-NB-04` (Fourier-Mellin isometry) to the log-substitution and scaling unitaries plus the dense-core formula |
| Borel-Caratheodory | `Complex.borelCaratheodory`, `Mathlib/Analysis/Complex/BorelCaratheodory.lean` | generic input to future Landau-type log-derivative estimates in any explicit-formula program |

## Scope boundary of this record

This record replays the **Mathlib capability map** only. The source-side
package `SOURCE_CONTRACTS.md` remains in its declared state — "proposed
source-contract package under independent review" — and its adversarial
source-to-formalization review (against the SHA-256-pinned PDFs) is **not**
performed here; it is carried explicitly as a review precondition of `RH-003`
(see `TARGET_BRIDGE_CONTRACT.md` §Review preconditions). `RH-001` closes with
that carve-out stated rather than silently absorbed.

## Row-level replay evidence

### Riemann zeta and its completion (+ target-section claims)

| capability | declaration(s) | claimed locator | replay | actual evidence |
|---|---|---|---|---|
| zeta function | `riemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:119 | **CONFIRMED** | RiemannZeta.lean:119 `def riemannZeta := hurwitzZetaEven 0` |
| analyticity | `differentiableAt_riemannZeta; analyticOn_riemannZeta` | RiemannZeta.lean:137; RiemannZeta.lean:144 | **CONFIRMED** | 137 `theorem differentiableAt_riemannZeta {s : ℂ} (hs' : s ≠ 1) : DifferentiableAt ℂ riemannZeta s`; 144 `lemma analyticOn_riemannZeta : AnalyticOnNhd ℂ riemannZeta {1}ᶜ` |
| completed zeta | `completedRiemannZeta` | RiemannZeta.lean:67 | **CONFIRMED** | 67 `def completedRiemannZeta (s : ℂ) : ℂ := completedHurwitzZetaEven 0 s` |
| pole-removed completion | `completedRiemannZeta₀` | RiemannZeta.lean:63 | **CONFIRMED** | 63 `def completedRiemannZeta₀ (s : ℂ) : ℂ := completedHurwitzZetaEven₀ 0 s` |
| entire completion | `differentiable_completedZeta₀` | RiemannZeta.lean:89 | **CONFIRMED** | 89 `theorem differentiable_completedZeta₀ : Differentiable ℂ completedRiemannZeta₀` |
| relation between completions | `completedRiemannZeta_eq` | RiemannZeta.lean:84 | **CONFIRMED** | 84-85 `lemma completedRiemannZeta_eq (s : ℂ) : completedRiemannZeta s = completedRiemannZeta₀ s - 1 / s - 1 / (1 - s)` |
| completion symmetry | `completedRiemannZeta₀_one_sub; completedRiemannZeta_one_sub` | RiemannZeta.lean:99; RiemannZeta.lean:105 | **CONFIRMED** | 99 `theorem completedRiemannZeta₀_one_sub (s : ℂ) : completedRiemannZeta₀ (1 - s) = completedRiemannZeta₀ s`; 105 `theorem completedRiemannZeta_one_sub (s : ℂ) : completedRiemannZeta (1 - s) = completedRiemannZeta s` |
| zeta/completion relation | `riemannZeta_def_of_ne_zero; riemannZeta_eq_completedRiemannZeta₀; riemannZeta_eq_mul_completedRiemannZeta₀` | RiemannZeta.lean:152; 157; 162 | **CONFIRMED** | 152 `lemma riemannZeta_def_of_ne_zero {s : ℂ} (hs : s ≠ 0) : riemannZeta s = completedRiemannZeta s / Gammaℝ s`; 157 `lemma riemannZeta_eq_completedRiemannZeta₀ {s : ℂ} (hs : s ≠ 0) ...`; 162 `lemma riemannZeta_eq_mul_co |
| zeta functional equation | `riemannZeta_one_sub` | RiemannZeta.lean:176 | **CONFIRMED** | 176 `theorem riemannZeta_one_sub {s : ℂ} (hs : ∀ n : ℕ, s ≠ -n) (hs' : s ≠ 1) : riemannZeta (1 - s) = 2 * (2 * π) ^ (-s) * Gamma s * cos (π * s / 2) * riemannZeta s` |
| residue at one | `riemannZeta_residue_one` | RiemannZeta.lean:239 | **CONFIRMED** | 239 `lemma riemannZeta_residue_one : Tendsto (fun s ↦ (s - 1) * riemannZeta s) (𝓝[≠] 1) (𝓝 1)` |
| local Laurent remainder | `tendsto_riemannZeta_sub_one_div; isBigO_riemannZeta_sub_one_div` | Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:332; line 365 | **CONFIRMED** | 332 `theorem _root_.tendsto_riemannZeta_sub_one_div : Tendsto (fun s : ℂ ↦ riemannZeta s - 1 / (s - 1)) (𝓝[≠] 1) (𝓝 γ)`; 365 `lemma _root_.isBigO_riemannZeta_sub_one_div ... =O[𝓝 1] (fun _ ↦ 1 : ℂ → F)` |
| extra (a): RiemannHypothesis definition | `RiemannHypothesis, 4-hypothesis form` | RiemannZeta.lean:182 | **CONFIRMED** | 182-183 `def RiemannHypothesis : Prop := ∀ (s : ℂ) (_ : riemannZeta s = 0) (_ : ¬∃ n : ℕ, s = -2 * (n + 1)) (_ : s ≠ 1), s.re = 1 / 2` |
| extra (b): zeta at zero | `riemannZeta_zero gives ζ(0) = -1/2` | (no line claimed; actual RiemannZeta.lean:149) | **CONFIRMED** | 149 `theorem riemannZeta_zero : riemannZeta 0 = -1 / 2` |
| extra (c): module-comment sign discrepancy | `top module comment states pole correction with OPPOSITE sign from completedRiemannZeta_eq` | RiemannZeta.lean top comment vs line 84 | **CONFIRMED** | Comment line 19-20: `completedRiemannZeta₀`: the entire function `Λ₀` satisfying `Λ₀(s) = Λ(s) + 1 / (s - 1) - 1 / s` wherever the RHS is defined. Theorem lines 84-85: `completedRiemannZeta s = completedRiemannZeta₀ s -  |
| extra (d): ZetaAsymp locators | `tendsto_riemannZeta_sub_one_div at ZetaAsymp.lean:332; isBigO_riemannZeta_sub_one_div at 365` | Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:332 and :365 | **CONFIRMED** | 332 `theorem _root_.tendsto_riemannZeta_sub_one_div ...` (limit γ, the Euler-Mascheroni constant); 365 `lemma _root_.isBigO_riemannZeta_sub_one_div {F : Type*} [Norm F] [One F] [NormOneClass F] ...` |

Mismatches: **0**.

### Zeros, half-planes, and convergent formulae

| capability | declaration(s) | claimed locator | replay | actual evidence |
|---|---|---|---|---|
| trivial zeros | `riemannZeta_neg_two_mul_nat_add_one` | RiemannZeta.lean:171 | **CONFIRMED** | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:171 — theorem riemannZeta_neg_two_mul_nat_add_one (n : ℕ) : riemannZeta (-2 * (n + 1)) = 0 |
| right open half-plane nonvanishing | `riemannZeta_ne_zero_of_one_lt_re` | Dirichlet.lean:326 | **CONFIRMED** | Mathlib/NumberTheory/LSeries/Dirichlet.lean:326 — lemma riemannZeta_ne_zero_of_one_lt_re {s : ℂ} (hs : 1 < s.re) : riemannZeta s ≠ 0 |
| right closed half-plane nonvanishing | `riemannZeta_ne_zero_of_one_le_re` | Nonvanishing.lean:410 | **CONFIRMED** | Mathlib/NumberTheory/LSeries/Nonvanishing.lean:410 — lemma _root_.riemannZeta_ne_zero_of_one_le_re ⦃s : ℂ⦄ (hs : 1 ≤ s.re) : riemannZeta s ≠ 0 |
| zero set | `riemannZetaZeros; mem_riemannZetaZeros` | ZetaZeros.lean:33; line 35 | **CONFIRMED** | Mathlib/NumberTheory/LSeries/ZetaZeros.lean:33 — def riemannZetaZeros : Set ℂ := riemannZeta ⁻¹' {0}; line 35 mem_riemannZetaZeros |
| closed/discrete zero set | `isClosed_riemannZetaZeros; isDiscrete_riemannZetaZeros` | ZetaZeros.lean:57; line 60 | **CONFIRMED** | Mathlib/NumberTheory/LSeries/ZetaZeros.lean:57 — lemma isClosed_riemannZetaZeros : IsClosed riemannZetaZeros; line 60 isDiscrete_riemannZetaZeros : IsDiscrete riemannZetaZeros |
| finite zeros in compact windows | `IsCompact.inter_riemannZetaZeros_finite` | ZetaZeros.lean:64 | **CONFIRMED** | Mathlib/NumberTheory/LSeries/ZetaZeros.lean:64 — lemma IsCompact.inter_riemannZetaZeros_finite {S : Set ℂ} (hS : IsCompact S) : (S ∩ riemannZetaZeros).Finite |
| escape from compacts | `tendsto_riemannZeta_cofinite_cocompact` | ZetaZeros.lean:70 | **CONFIRMED** | Mathlib/NumberTheory/LSeries/ZetaZeros.lean:70 — lemma tendsto_riemannZeta_cofinite_cocompact : Tendsto ((↑) : riemannZetaZeros → ℂ) cofinite (cocompact ℂ) |
| Dirichlet series | `zeta_eq_tsum_one_div_nat_cpow` | RiemannZeta.lean:204 | **CONFIRMED** | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:204 — theorem zeta_eq_tsum_one_div_nat_cpow {s : ℂ} (hs : 1 < re s) : riemannZeta s = ∑' n : ℕ, 1 / (n : ℂ) ^ s |
| Euler product | `riemannZeta_eulerProduct_hasProd; riemannZeta_eulerProduct` | EulerProduct/DirichletLSeries.lean:89; line 102 | **CONFIRMED** | Mathlib/NumberTheory/EulerProduct/DirichletLSeries.lean:89 — theorem riemannZeta_eulerProduct_hasProd (hs : 1 < s.re) : HasProd ...; line 102 riemannZeta_eulerProduct (hs : 1 < s.re) : Tendsto ... |
| exponential-log Euler product | `riemannZeta_eulerProduct_exp_log` | EulerProduct/DirichletLSeries.lean:160 | **CONFIRMED** | Mathlib/NumberTheory/EulerProduct/DirichletLSeries.lean:160 — theorem riemannZeta_eulerProduct_exp_log {s : ℂ} (hs : 1 < s.re) : exp (∑' p : Nat.Primes, -Complex.log (1 - p ^ (-s))) = riemannZeta s |
| von Mangoldt arithmetic function | `ArithmeticFunction.vonMangoldt; vonMangoldt_sum` | VonMangoldt.lean:65; line 102 | **CONFIRMED** | Mathlib/NumberTheory/ArithmeticFunction/VonMangoldt.lean:65 — noncomputable def vonMangoldt : ArithmeticFunction ℝ; line 102 vonMangoldt_sum : ∑ i ∈ n.divisors, Λ i = Real.log n |
| zeta logarithmic derivative | `LSeries_vonMangoldt_eq_deriv_riemannZeta_div` | Dirichlet.lean:434 | **CONFIRMED** | Mathlib/NumberTheory/LSeries/Dirichlet.lean:434 — lemma LSeries_vonMangoldt_eq_deriv_riemannZeta_div {s : ℂ} (hs : 1 < s.re) : L ↗Λ s = - deriv riemannZeta s / riemannZeta s |
| L-series derivatives | `LSeries_deriv; LSeries_iteratedDeriv` | LSeries/Deriv.lean:86; line 133 | **CONFIRMED** | Mathlib/NumberTheory/LSeries/Deriv.lean:86 — lemma LSeries_deriv {f : ℕ → ℂ} {s : ℂ} (h : abscissaOfAbsConv f < s.re) : deriv (LSeries f) s = -LSeries (logMul f) s; line 133 LSeries_iteratedDeriv, same hypothesis |

Mismatches: **0**.

### Reusable generic analytic infrastructure (+ analyticOrderNatAt)

| capability | declaration(s) | claimed locator | replay | actual evidence |
|---|---|---|---|---|
| real gamma factor | `Gammaℝ` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:43 | **CONFIRMED** | Deligne.lean:43 `noncomputable def Gammaℝ (s : ℂ) := π ^ (-s / 2) * Gamma (s / 2)` |
| gamma zero classification | `Gammaℝ_eq_zero_iff` | Deligne.lean:73 | **CONFIRMED** | Deligne.lean:73 `lemma Gammaℝ_eq_zero_iff {s : ℂ} : Gammaℝ s = 0 ↔ ∃ n : ℕ, s = -(2 * n)` |
| inverse gamma entire | `differentiable_Gammaℝ_inv` | Deligne.lean:88 | **CONFIRMED** | Deligne.lean:88 `lemma differentiable_Gammaℝ_inv : Differentiable ℂ (fun s ↦ (Gammaℝ s)⁻¹)` |
| analytic zero order | `analyticOrderAt; analyticOrderAt_ne_zero; product law` | Mathlib/Analysis/Analytic/Order.lean:47; :129; :497 | **CONFIRMED** | Order.lean:47 `noncomputable def analyticOrderAt (f : 𝕜 → E) (z₀ : 𝕜) : ℕ∞`; :129 `analyticOrderAt_ne_zero`; :497 `theorem analyticOrderAt_mul ... = analyticOrderAt f z₀ + analyticOrderAt g z₀` (product/additivity law) |
| meromorphic order | `meromorphicOrderAt` | Mathlib/Analysis/Meromorphic/Order.lean:47 | **CONFIRMED** | Order.lean:47 `noncomputable def meromorphicOrderAt (f : 𝕜 → E) (x : 𝕜) : WithTop ℤ` |
| meromorphic divisor | `MeromorphicOn.divisor` | Mathlib/Analysis/Meromorphic/Divisor.lean:39 | **CONFIRMED** | Divisor.lean:39 `noncomputable def divisor (f : 𝕜 → E) (U : Set 𝕜) : Function.locallyFinsuppWithin U ℤ` |
| Jensen formula and divisor bound | `MeromorphicOn.circleAverage_log_norm; AnalyticOnNhd.sum_divisor_le` | Mathlib/Analysis/Complex/JensenFormula.lean:307; :389 | **CONFIRMED** | JensenFormula.lean:307 `theorem MeromorphicOn.circleAverage_log_norm`; :389 `theorem AnalyticOnNhd.sum_divisor_le` |
| Phragmen-Lindelof | `PhragmenLindelof.vertical_strip` | Mathlib/Analysis/Complex/PhragmenLindelof.lean:275 | **CONFIRMED** | PhragmenLindelof.lean:275 `theorem vertical_strip (hfd : DiffContOnCl ℂ f (re ⁻¹' Ioo a b)) ...` |
| Mellin transform | `mellin; HasMellin` | Mathlib/Analysis/MellinTransform.lean:91; :160 | **CONFIRMED** | MellinTransform.lean:91 `def mellin (f : ℝ → E) (s : ℂ) : E := ∫ t : ℝ in Ioi 0, (t : ℂ) ^ (s - 1) • f t`; :160 `def HasMellin` |
| Mellin inversion | `mellinInv_mellin_eq` | Mathlib/Analysis/MellinInversion.lean:98 | **CONFIRMED** | MellinInversion.lean:98 `theorem mellinInv_mellin_eq` with hypotheses MellinConvergent, VerticalIntegrable, ContinuousAt — matching the 'substantial convergence and integrability hypotheses' note |
| functional-equation Mellin pair | `WeakFEPair.hasMellin; hurwitzEvenFEPair` | Mathlib/NumberTheory/LSeries/AbstractFuncEq.lean:414; HurwitzZetaEven.lean:254 | **CONFIRMED** | AbstractFuncEq.lean:414 `theorem hasMellin [CompleteSpace E] {s : ℂ} (hs : P.k < s.re) : HasMellin (P.f · - P.f₀) s (P.Λ s)`; HurwitzZetaEven.lean:254 `def hurwitzEvenFEPair (a : UnitAddCircle) : WeakFEPair ℂ` |
| complete Lp space | `MeasureTheory.Lp.instCompleteSpace` | Mathlib/MeasureTheory/Function/LpSpace/Complete.lean:378 | **CONFIRMED** | Complete.lean:378 `instance instCompleteSpace [CompleteSpace E] [hp : Fact (1 ≤ p)] : CompleteSpace (Lp E p μ)` |
| L² inner-product space | `MeasureTheory.L2.innerProductSpace; module imports GramMatrix` | Mathlib/MeasureTheory/Function/L2Space.lean:192 | **CONFIRMED** | L2Space.lean:192 `instance innerProductSpace : InnerProductSpace 𝕜 (α →₂[μ] E)`; file header line 8 `public import Mathlib.Analysis.InnerProductSpace.GramMatrix` — import note faithful |
| simple functions dense in Lp | `Lp.simpleFunc.isDenseEmbedding; denseRange` | Mathlib/MeasureTheory/Function/SimpleFuncDenseLp.lean:648; :670 | **CONFIRMED** | SimpleFuncDenseLp.lean:648 `lemma isDenseEmbedding (hp_ne_top : p ≠ ∞)`; :670 `protected theorem denseRange (hp_ne_top : p ≠ ∞)`; both in scope of line 637 `variable [Fact (1 ≤ p)]` — 'assumes Fact (1 ≤ p) and p ≠ ∞' fai |
| fractional part | `Int.fract` | Mathlib/Algebra/Order/Floor/Defs.lean:259 | **CONFIRMED** | Floor/Defs.lean:259 `def fract (a : α) : α := a - floor a`, inside `namespace Int` opened at line 246 |
| SOURCE_CONTRACTS.md claim | `analyticOrderNatAt` | Mathlib/Analysis/Analytic/Order.lean:61 | **CONFIRMED** | Order.lean:61 `noncomputable def analyticOrderNatAt (f : 𝕜 → E) (z₀ : 𝕜) : ℕ := (analyticOrderAt f z₀).toNat` |

Mismatches: **0**.

### Missing named route interfaces (negative replay)

| interface | replay result | near-miss / candidate hits |
|---|---|---|
| standard Riemann xi | **CONFIRMED_ABSENT_IN_SCOPE** | none |
| conjugation symmetry for zeta/completion | **CONFIRMED_ABSENT_IN_SCOPE** | none |
| critical-strip localization | **CONFIRMED_ABSENT_IN_SCOPE** | none |
| zeta/xi analytic order equality | **CONFIRMED_ABSENT_IN_SCOPE** | Near-miss (generic only): analyticOrderAt at Mathlib/Analysis/Analytic/Order.lean:47, meromorphicOrderAt at Mathlib/Analysis/Meromorphic/Order.lean:47 — never specialized to zeta. |
| zeta/xi divisor | **CONFIRMED_ABSENT_IN_SCOPE** | Near-miss (generic only): MeromorphicOn.divisor at Mathlib/Analysis/Meromorphic/Divisor.lean:39 — the multiplicity-aware divisor machinery exists but is never applied to riemannZeta/xi. |
| nontrivial-zero enumeration or counting function | **CONFIRMED_ABSENT_IN_SCOPE** | Near-miss (generic only): countingFunction_finsum_eq_finsum_add at Mathlib/Analysis/Complex/JensenFormula.lean:275 and ValueDistribution.logCounting at Mathlib/Analysis/Complex/ValueDistribution/LogCounting/Basic.lean:96,272 — generic Nevanlinna (log-)counting functions for meromorphic functions on  |
| multiplicity-aware zero sum | **CONFIRMED_ABSENT_IN_SCOPE** | none |
| vertical growth / order-one entire growth for zeta or xi | **CONFIRMED_ABSENT_IN_SCOPE** | Near-miss: isBigO_riemannZeta_sub_one_div at Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:365 — boundedness of zeta - 1/(s-1) near s=1 only; not vertical-strip or order-one growth. |
| canonical product / Hadamard factorization | **CONFIRMED_ABSENT_IN_SCOPE** | none |
| Riemann-Weil prime-zero explicit formula | **CONFIRMED_ABSENT_IN_SCOPE** | none |
| Li/Keiper coefficients and criterion | **CONFIRMED_ABSENT_IN_SCOPE** | none |
| Nyman-Beurling/Baez-Duarte objects and equivalence | **CONFIRMED_ABSENT_IN_SCOPE** | none |

### Beyond-scope strengthening (whole-tree greps)

Whole-tree searches over all of `Mathlib/` at the pin support extending the
most load-bearing negatives beyond the audited scope: `riemannXi` — 0 hits
tree-wide; Hadamard factorization for finite-order entire functions — absent
tree-wide (all `hadamard` hits are the three-lines theorem, the
Cauchy-Hadamard radius formula, or matrix entrywise products; no finite-order
entire-function concept exists at the pin); riemannZeta (or any completion)
related to complex conjugation — 0 hits across all 16 files tree-wide that
mention `riemannZeta`; Li/Keiper coefficients, Nyman-Beurling/Báez-Duarte
objects, a zero-counting `N(T)`, and a Riemann-Weil explicit formula — 0
relevant hits tree-wide. The only near-miss machinery found is the generic
Nevanlinna value-distribution and meromorphic-divisor API already recorded as
`GENERIC` in the map. `NOT-FOUND-IN-SCOPE` labels remain scoped as defined by
the map; this paragraph records additional evidence, not a new label.
