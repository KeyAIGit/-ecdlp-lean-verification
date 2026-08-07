# `S1-EXPLICIT` reconnaissance note

Status: **reconnaissance only — capability note, not a contract, not a Lean
draft, not a promotion.** Nothing here claims a proof, selects or unparks a
route, asserts that any barrier is closed or stale, or asserts progress on the
truth of the Riemann Hypothesis. Honest negative findings are recorded on the
same footing as positive ones. No barrier is re-scoped: the exit string at
`MATHLIB_CAPABILITY_MAP.md:390` is quoted in full, never narrowed, and no
theorem below is offered as a substitute for it.

Audit date: 2026-08-07

Mathlib revision: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0), verified
this session by `git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`.
Repository HEAD at write time: `6a1195f` — a PR #315 working-branch commit;
the mainline carries the identical content as the squash commit `9129e8c`,
and none of this note's branch hashes is a mainline ancestor (Annex B-1).
Local checkouts read with
ripgrep/`sed`/`grep -n` only; **no Lean toolchain is available in this
container, so every feasibility judgement below is a source-reading estimate
and none of it has been kernel-checked.** Following `GLOBAL_ZEROS_RECON.md`
Annex A-5, no search used `rg -E` (ripgrep parses that as `--encoding` and the
invocation aborts without running); every search quoted below was `rg -n` /
`rg -ni` and was either re-run this session or is attributed to the same-day,
same-pin scout that ran it. Line numbers are declaration-keyword lines, not
doc-comment openers (Annex A-8 of the first sibling).

Barrier under examination, `MATHLIB_CAPABILITY_MAP.md:390` (re-extracted this
session; note the tasking prompt's own truncation of the exit string is not
carried into this note):

> `S1-EXPLICIT` | no Riemann-Weil explicit formula | Weil-first Li and direct
> explicit-formula route | exact test class, transform convention, residues,
> and limiting procedure

Repository state at HEAD `6a1195f`: `S1-XI`, `S1-MULTIPLICITY`, and `S1-CONJ`
are CLOSED (sixth map addendum, ⊙ `:626-656`; PRs #304/#307/#313 — note the
main-table cell at `map:386` still reads "OPEN; local … discharged", a
stale-cell/addendum split the closures themselves resolve in the addendum's
favour per `tasks/RIEMANN_HYPOTHESIS.md:43-45`); the single ACTIVE
queue slot is `RH-012` (zero-set slice drafting plus separate kernel
promotion, under `S1-GLOBAL-ZEROS`; ⊙ `tasks/RIEMANN_HYPOTHESIS.md:45-50`,
activated by the dated RH-011 acceptance — branch commit `e9b5090`, mainline
squash `9129e8c`); `drafts/` contains
nine files — the four merged-package drafts, four pillar drafts
(`MellinBound.lean`, `HarnackDisc.lean`, `PolyLiouville.lean`,
`ThreeCircles.lean`), and the `README.md` ledger (count corrected, Annex
B-3) — and **none of them claims `S1-EXPLICIT` scope** (verified
this session by listing and by `grep -rn "explicit formula" ResearchOS/ Ecdlp/`
→ 0 hits).

Relation to the sibling notes. `GLOBAL_ZEROS_RECON.md` and `GROWTH_RECON.md`
(both merged, with adversarial-review Annexes) were read in full first,
including their recorded discipline lessons: runnable search commands only, no
"all ingredients pinned" claim without spot-checks, no barrier re-scoping, and
softened negatives named as the defect class this lane gets caught on. This
note contradicts no verified sibling finding. It carries three refinements and
several state corrections, each disclosed where made and collected in §5;
mirror obligations are discharged in §4 and §5.

---

## 1. Headline

Four things, stated separately because they are easy to conflate.

1. **The "transform convention" clause of the exit string is the strong
   quarter at the pin — largely already satisfied by pinned conventions that
   match the source contracts byte-for-byte in meaning.** The pinned Mellin
   transform `mellin f s = ∫ t in Ioi 0, (t : ℂ) ^ (s - 1) • f t`
   (`Mathlib/Analysis/MellinTransform.lean:91`, re-extracted this session) is
   definitionally `SC-BOMB-01`'s `Mellin(f)(s) = ∫₀^∞ f(x) x^s dx/x`
   (`SOURCE_CONTRACTS.md:448`, same exponent convention `x^s dx/x = x^{s−1}dx`);
   the pinned Fourier transform is the unitary analyst convention
   (`fourierChar`, `Circle.lean:208`: `𝐞 x = exp(2πix)`; `fourierIntegral`,
   `FourierTransform.lean:82`); and `mellinInv` (`MellinTransform.lean:96`) is
   the classical `(2πi)⁻¹∫_{(σ)}` vertical-line integral. No convention
   translation layer is needed. This does not exhaust the clause: its
   `J`/`tilde` involutions and the `Mellin(f_g)` factorization remain repo
   work (§4.1; Annex B-6). Additionally, a **Mellin↔Fourier bridge is
   already a pinned theorem** — `mellin_eq_fourier` / `mellinInv_eq_fourierInv`
   (`MellinInversion.lean:49` / `:75`, first re-extracted this session) — and
   is absent from both sibling notes and from `MATHLIB_CAPABILITY_MAP.md`,
   whose `SC-NB-04` note (`map:345-348`) still books the log-substitution as
   manual work.

2. **Both flanks of the formula are rich at the pin; the middle is empty.**
   Analytic flank: L² Plancherel (`Lp.fourierTransformₗᵢ`, `LpSpace.lean:50`,
   already at the map's addendum `:485-488`), Fourier inversion, Poisson
   summation in four forms up to a hypothesis-free Schwartz version
   (`SchwartzMap.tsum_eq_tsum_fourier`, `PoissonSummation.lean:230`), Schwartz
   space, tempered distributions. Arithmetic flank, for `re s > 1`: Λ with its
   convolution identities, `L ↗Λ s = −ζ′(s)/ζ(s)`
   (`LSeries_vonMangoldt_eq_deriv_riemannZeta_div`, `Dirichlet.lean:434`,
   hypothesis `1 < s.re`), Euler products, Chebyshev ψ/θ with two-sided
   Chebyshev bounds, a full Abel-summation toolkit, and a
   partial-sums-to-integral representation of any L-series
   (`LSeries_eq_mul_integral`, `SumCoeff.lean:137`). **Two whole load-bearing
   files are unrecorded in the capability map and search log**:
   `Mathlib/NumberTheory/Chebyshev.lean` (703 lines) and
   `Mathlib/NumberTheory/AbelSummation.lean` (399 lines); also unmapped:
   `LSeries/MellinEqDirichlet.lean`, `LSeries/PrimesInAP.lean`'s prime-power
   decomposition and residue-class `−L′/L` package, and
   `SumCoeff.lean:336/:362`'s Abelian residue theorems.

3. **The "residues" and "limiting procedure" clauses are empty at the pin, and
   the "exact test class" clause is empty on both sides.** Re-run this session,
   tree-wide: `rg -ni "riemann.?weil|weil.?explicit" Mathlib/` → 0;
   `rg -ni "perron" Mathlib/NumberTheory/` → 0; `rg -ni
   "argument.?principle|winding" Mathlib/` → 0 (no contour residue theorem —
   mirrors both siblings' corrected searches); `rg -ni "mertens"
   Mathlib/NumberTheory/` → 0; `rg -ni "wiener" Mathlib/` → 1 (a prose
   doc-comment, `PrimesInAP.lean:298`); `rg -n "PrimeNumberTheorem" Mathlib/` →
   1 (an attribution doc-comment, `Chebyshev.lean:56`). No Tauberian theorem;
   the pinned `SumCoeff.lean:336` direction is Abelian only. Neither
   `SC-BOMB-01`'s class `W` nor `SC-WEIL-01`'s class `A` exists as a bundled
   class anywhere. Everything arithmetic stops at the line `re s = 1`; the one
   pinned ζ residue is `riemannZeta_residue_one` (`LSeries/RiemannZeta.lean:239`).

4. **As written, this barrier is not a closable next target, and the honest
   verdict of this note — stated plainly here and argued in §7–§8 — is
   do-not-attempt.** Its consumers are exactly the two parked routes (A and C;
   Route B consumes nothing from it, checked at both the obligation and the
   bar/preregistration level — §4.4); its exit clause "exact test class" is
   singular where the contract package requires **two proved-distinct class
   families** (`SC-BRIDGE-03`, `SOURCE_CONTRACTS.md:603`), so freezing one
   silently selects a formulation, which is a partial route selection under a
   zero-route disposition; its hard mathematical half (contour shift, residues,
   limiting procedure) is blocked simultaneously on absent generic machinery
   (no argument principle, no residue theorem, no Perron), on `S1-GROWTH` G3
   (`ζ′/ζ` in the strip), and on `S1-GLOBAL-ZEROS` (existence of the zero-sum
   limits); and its single hardest purely-own item, `SC-BOMB-03`
   autocorrelation closure, is rated "a genuine blocker" by `ROUTE_TRIAGE.md`
   (`:296-297`). What the barrier can absorb now is exactly what this note is:
   reconnaissance, plus zero-Lean-cost record-keeping.

---

## 2. Inventory: what exists at the pin

Locators marked ⊙ were re-extracted this session by `sed -n "${n}p"`; unmarked
locators are inherited from the three same-day, same-pin scout passes, whose
sample re-verification rate this session was 22/22 (Annex).

### 2.1 Transform conventions — verbatim, source-matched

⊙ `Mathlib/Analysis/Complex/Circle.lean:208` — `fourierChar : AddChar ℝ Circle`
with `toFun z := .exp (2 * π * z)`; notation `𝐞` `:213`. The file's doc calls
this "the analyst convention that there is a `2 * π` in the exponent".

⊙ `Mathlib/Analysis/Fourier/FourierTransform.lean:82` —
`VectorFourier.fourierIntegral e μ L f w = ∫ v, e (-L v w) • f v ∂μ`; the `𝓕`
instance for finite-dimensional real inner-product spaces gives
`𝓕 f w = ∫ v, exp(−2πi⟪v,w⟫) • f v` (`fourier_eq'` `:441`), inverse with
`+2πi` (`fourierInv_eq'` `:460`). Unitary; no prefactor.

⊙ `Mathlib/Analysis/MellinTransform.lean:91` — `mellin f s = ∫ t in Ioi 0,
(t : ℂ) ^ (s - 1) • f t`; `MellinConvergent` `:45`;
⊙ `mellinInv` `:96` — `(1 / (2 * π)) • ∫ y : ℝ, (x : ℂ) ^ (-(σ + y * I)) •
f (σ + y * I)`, i.e. the classical vertical-line inversion with `ds = i dy`;
`Complex.VerticalIntegrable` `:86`; `HasMellin` `:160`.

⊙ `Mathlib/Analysis/MellinInversion.lean:49` — `mellin_eq_fourier`:
`mellin f s = 𝓕 (fun u ↦ (Real.exp (-s.re * u) • f (Real.exp (-u)))) (s.im /
(2 * π))`; `mellinInv_eq_fourierInv` `:75`; inversion `mellinInv_mellin_eq`
`:98` (hypotheses `0 < x`, `MellinConvergent f σ`, `VerticalIntegrable (mellin
f) σ`, `ContinuousAt f x`; `mellin_inversion` is a deprecated alias since
2025-11-16).

L-series conventions: `LSeries.term` (`LSeries/Basic.lean:74`, `if n = 0 then 0
else f n / n ^ s`), `LSeries` `:164`, `LSeriesSummable` `:173`,
`abscissaOfAbsConv` (`Convergence.lean:30`).

**Naming hazard for any future draft** (transforms scout, spot-confirmed at
`:102`/`:230` ⊙): the 2025-11-16 Fourier typeclass refactor makes `𝓕`/`𝓕⁻` the
typeclass methods `fourier`/`fourierInv` (`Fourier/Notation.lean:57-58`); the
older `…fourierIntegral…` names survive only as `@[deprecated]` aliases —
e.g. Poisson summation is now `Real.tsum_eq_tsum_fourier`, not
`Real.tsum_eq_tsum_fourierIntegral`.

### 2.2 Test-function classes (generic only — neither source class exists)

| capability | pinned declaration |
|---|---|
| Schwartz space `𝓢(E, F)` | `SchwartzMap`, `Distribution/SchwartzSpace/Basic.lean:78` |
| Fourier as CLM/CLE on `𝓢` | `fourierTransformCLM`, `SchwartzSpace/Fourier.lean:51`; exchange identities `:171-:239` |
| compactly supported `𝓓(Ω, F)` | `TestFunction`, `Distribution/TestFunction.lean:67`; `ContDiffBump`, `BumpFunction/Basic.lean:70` |
| temperate growth symbols | `Function.HasTemperateGrowth`, `Distribution/TemperateGrowth.lean:40` |
| tempered distributions `𝓢'` | `TemperedDistribution`, `Distribution/TemperedDistribution.lean:53`; Fourier multipliers `FourierMultiplier.lean:50,:143` |

**Honest negatives, at full strength:** there is no bundled class of piecewise
`C¹` functions with first-kind discontinuities and midpoint values
(`SC-BOMB-01`'s `W`; `rg -ni "first.?kind.*discontinuit" Mathlib/` → 0, per the
transforms scout), and no strip-holomorphic-with-decay class of any kind
(`SC-WEIL-01`'s `A`). Both would be repo-side definitions; the exit clause
"exact test class" is repo work by construction, and §4.2 records why writing
either definition is formulation-selecting.

### 2.3 Plancherel, inversion, Poisson

| capability | pinned declaration |
|---|---|
| L² Plancherel | ⊙ `MeasureTheory.Lp.fourierTransformₗᵢ`, `Fourier/LpSpace.lean:50`; `norm_fourier_eq` `:89` (already map addendum `:485-488`) |
| Schwartz Plancherel | `integral_inner_fourier_fourier`, `SchwartzSpace/Fourier.lean:320`; Hausdorff-Young endpoint `:308` |
| Fourier inversion | `Integrable.fourierInv_fourier_eq`, `Fourier/Inversion.lean:165` |
| Poisson summation, 4 forms | ⊙ `Real.tsum_eq_tsum_fourier`, `PoissonSummation.lean:102` (most general); rpow-decay forms `:197`, `:212`; ⊙ Schwartz form `:230` (no side conditions) |
| Riemann–Lebesgue | `Real.zero_at_infty_fourier`, `RiemannLebesgueLemma.lean:215` |
| convolution theorem (Schwartz) | `fourier_convolution`, `Fourier/Convolution.lean:191` |
| worked Poisson→theta→ζ chain | `Complex.tsum_exp_neg_quadratic` (`Gaussian/PoissonSummation.lean:87`) → `JacobiTheta/TwoVariable.lean` → the `hurwitzEvenFEPair` functional equation the repo's ξ sits on (GROWTH_RECON §2.6-2.7, mirrored unchanged) |
| circle Parseval | `tsum_sq_fourierCoeff`, `Fourier/AddCircle.lean:452` |

### 2.4 Mellin infrastructure — mirrored from `GROWTH_RECON.md`, one refinement

Re-verified rather than re-litigated (GROWTH §2.6/§3.1): convergence and
differentiability API (`mellinConvergent_of_isBigO_rpow` `:277` and family);
`StrongFEPair.hasMellin` (`AbstractFuncEq.lean:203`, all `s`) and
`WeakFEPair.hasMellin` (`:414`); and the load-bearing negative — **no norm
bound for `mellin`**: ⊙ `rg -n "norm_mellin|‖mellin" Mathlib/` → 0 hits,
re-run this session. Also absent (transforms scout): Mellin-Plancherel, Mellin
convolution theorem. Present: substitution API (`mellin_comp_rpow` `:116` and
family), endpoint special values `hasMellin_one_Ioc` `:438` (`= 1/s`) and
`hasMellin_cpow_Ioc` `:453` — a pinned model of, not identical to, the
endpoint-term shapes in `SC-BOMB-02`'s `Mellin(f)(0)`/`Mellin(f)(1)` (Annex
B-5).

**Refinement of both siblings (not a contradiction):** `mellin_eq_fourier` /
`mellinInv_eq_fourierInv` (§2.1) appear in neither sibling nor in the map. For
this barrier they matter: any vertical-line limiting procedure for `mellinInv`
can be routed to the Fourier side, where inversion, Plancherel, and
Riemann–Lebesgue are pinned; and part of the `SC-NB-04` log-substitution cost
the map's addendum still books is already a theorem.

Sum-against-kernel bridge, unmapped: ⊙ `hasSum_mellin`
(`LSeries/MellinEqDirichlet.lean:24`) — from `HasSum (fun i ↦ a i * rexp (-p i
* t)) (F t)` and summability of `‖a i‖ / p i ^ s.re`, concludes `HasSum (fun i
↦ Gamma s * a i / p i ^ s) (mellin F s)` for `0 < re s`. Exponential kernels
only; the pinned "sum against a test kernel = transform" shape.

### 2.5 Arithmetic side — complete for `re s > 1`, two files unmapped

Von Mangoldt (`ArithmeticFunction/VonMangoldt.lean`; map row area already
carries `:65`, `:102`): ⊙ `vonMangoldt` `:65`; `vonMangoldt_sum` `:102`
(`∑ i ∈ n.divisors, Λ i = Real.log n`); convolution identities `:119-:133`;
`vonMangoldt_le_log` `:151`; `vonMangoldt_ne_zero_iff` `:92`.

Chebyshev (`NumberTheory/Chebyshev.lean`, 703 lines, upstreamed from the
PrimeNumberTheoremAnd project per its `:56` doc; **not in the map or search
log** — verified by the primes scout's `rg -ni "chebyshev|abelsummation"` over
both, and independently plausible given the addendum text read this session):
⊙ `psi` `:70` (`∑ n ∈ Ioc 0 ⌊x⌋₊, Λ n`), ⊙ `theta` `:77`; upper bounds ⊙
`psi_le_const_mul_self` `:413` (`ψ x ≤ (log 4 + 4) * x`), `theta_le_log4_mul_x`
`:166`; lower bounds `psi_ge` `:438`, `theta_ge` `:455`; ψ↔θ comparison
`psi_sub_theta_le` `:450`; generic prime-power double sum
`sum_PrimePow_eq_sum_sum` `:308`; ⊙ π↔θ by Abel summation
`primeCounting_eq_theta_div_log_add_integral` `:484` with converse `:520`;
asymptotic bookkeeping `:588-:697`. No `IsEquivalent` in the file: these are
Chebyshev-order bounds, not PNT.

Abel summation (`NumberTheory/AbelSummation.lean`, 399 lines; **not in the
map**): ⊙ `sum_mul_eq_sub_sub_integral_mul` `:129` and its family (`:175`,
`:189`, `:200`, `₀`/`₀'`/`₁` `:211/:229/:239`), limit forms `:281`, `:300`,
summability criteria `:366`, `:378`. Discrete counterpart
`Finset.sum_Ioc_by_parts` (`Algebra/BigOperators/Module.lean:47`).

L-series and −ζ′/ζ: ⊙ `LSeries_vonMangoldt_eq_deriv_riemannZeta_div`
(`LSeries/Dirichlet.lean:434`) — `L ↗Λ s = - deriv riemannZeta s / riemannZeta
s` for `1 < s.re`, already mapped; derivative/convolution/positivity API
(`Deriv.lean:80-:157`, `Convolution.lean:62-:196`, `Positivity.lean:99`);
twisted `L (↗χ * ↗Λ) s = -deriv (L ↗χ) s / L ↗χ s` (`Dirichlet.lean:407`);
1-line nonvanishing `riemannZeta_ne_zero_of_one_le_re` (`Nonvanishing.lean:410`).
⊙ `LSeries_eq_mul_integral` (`SumCoeff.lean:137`): `LSeries f s = s * ∫ t in
Ioi 1, (∑ k ∈ Icc 1 ⌊t⌋₊, f k) * t ^ (-(s+1))` under a partial-sum `=O` and
summability; ⊙ Abelian residue theorem
`LSeries_tendsto_sub_mul_nhds_one_of_tendsto_sum_div` `:336` (+ `:362`).

Euler products: `riemannZeta_eulerProduct` (`DirichletLSeries.lean:102`),
exp/log form `:160` (both already mapped), generic `EulerProduct` machinery
(`EulerProduct/Basic.lean:174-:366`, `ExpLog.lean:27,:39`). ⊙ Prime-power
support decomposition `tprod_eq_tprod_primes_of_mulSupport_subset_prime_powers`
(`LSeries/PrimesInAP.lean:87`, with `@[to_additive]`) — the exact reshaping
`Σ_n Λ(n)g(n) = Σ_p Σ_k log p · g(p^{k+1})` needs.

Residue models: ⊙ `riemannZeta_residue_one` (`LSeries/RiemannZeta.lean:239`) —
`Tendsto (fun s ↦ (s - 1) * riemannZeta s) (𝓝[≠] 1) (𝓝 1)`, the source of the
explicit formula's `x` main term; and ⊙ `LFunctionResidueClassAux`
(`PrimesInAP.lean:304`, with `continuousOn_…` `:333`, `eqOn_…` `:348`) — a
complete pinned working model of "−L′/L with the `1/(s−1)` principal part
subtracted, continuous up to the 1-line minus zeros". No ζ-instance of that
pattern is stated (`q = 1` is not specialized to `riemannZeta`).

### 2.6 Repository side

No built, in-flight, or queued package consumes any `S1-EXPLICIT` fact:
⊙ `grep -rn "explicit formula" ResearchOS/ Ecdlp/` → 0; the xi package claim
boundary (`XI_PACKAGE_CONTRACT.md:27`) excludes every route research
obligation — the explicit formula falls under that exclusion but is not named
there (wording corrected, Annex B-2); the seven pillar
contracts and the four pillar drafts at HEAD (`MellinBound.lean`,
`HarnackDisc.lean`, `PolyLiouville.lean`, `ThreeCircles.lean` and their
contracts, headers read by the demand scout, drafts listed this session) all
sit under `S1-GROWTH` / `S1-GLOBAL-ZEROS` / the upstream pool, and none claims
`S1-EXPLICIT` scope.

---

## 3. What is genuinely missing

Split as the siblings split it: generic material that would be a natural
Mathlib upstream, versus source/ζ-specific work that must be built here. Every
ABSENT verdict is a search verdict (limits in §5.5); searches marked ⊙ were
re-run this session.

### 3.1 Generic — natural Mathlib upstreams, no ζ/ξ/RH content

| missing item | search evidence | note |
|---|---|---|
| argument principle / winding number / contour residue theorem | ⊙ `rg -ni "argument.?principle|winding" Mathlib/` → 0 | mirrors both siblings' corrected searches, including the `LogDeriv.lean:146` caveat (a `Tendsto` at a simple zero, no contour, no multiplicity). Nearest tools: rectangle Cauchy–Goursat `Complex.integral_boundary_rect_eq_zero_of_differentiableOn` (`CauchyIntegral.lean:295`) and the circle-integral representation formulas in the same file. Consumed by this barrier's "residues" clause and by `S1-GROWTH` G3 alike |
| Perron formula (truncated or not); any vertical-line contour shift of a Dirichlet series | ⊙ `rg -ni "perron" Mathlib/NumberTheory/` → 0 (tree-wide hits are Perron–Frobenius and an author name) | the sole pinned vertical-line inversion is the generic `mellinInv_mellin_eq`, whose `VerticalIntegrable (mellin f) σ` hypothesis nothing ζ-shaped satisfies at the pin |
| Tauberian theorem for Dirichlet series (Wiener–Ikehara or any) | ⊙ `rg -ni "wiener" Mathlib/` → 1 hit, a prose doc-comment (`PrimesInAP.lean:298`) | `SumCoeff.lean:336` is the Abelian direction only |
| Mertens' theorems | ⊙ `rg -ni "mertens" Mathlib/NumberTheory/` → 0 | closest pinned: `Nat.Primes.not_summable_one_div`, `summable_rpow` (`SumPrimeReciprocals.lean:89,:93`) |
| PNT in any form | ⊙ `rg -n "PrimeNumberTheorem" Mathlib/` → 1 hit, an attribution doc-comment (`Chebyshev.lean:56`) | Chebyshev-order bounds are the ceiling at the pin |
| norm bound for `mellin` | ⊙ `rg -n "norm_mellin|‖mellin" Mathlib/` → 0 | **owned by `S1-GROWTH`'s note** (GROWTH §6 row 1); listed here only because the limiting-procedure clause would also consume it; not claimed under this barrier |
| Mellin-Plancherel; Mellin convolution theorem | transforms scout, searches over both Mellin files → 0 | partial mitigation: `mellin_eq_fourier` transports Fourier-side Plancherel |
| generic bundled piecewise-`C¹`/first-kind-discontinuity function class | transforms scout: `rg -ni "first.?kind.*discontinuit" Mathlib/` → 0 | the generic *substrate* for class `W`; the class itself is source-specific (§3.2) |
| complex Stirling / `‖Complex.Gamma‖` bounds | mirrored from GROWTH §3.1, not re-run | consumed by this barrier's archimedean term (§3.2) |

### 3.2 Source/ζ-specific — cannot be pushed upstream, must be built here

| missing item | note |
|---|---|
| **the Riemann–Weil / trace explicit formula itself, in either form** | ⊙ `rg -ni "riemann.?weil|weil.?explicit" Mathlib/` → 0; `rg -ni "explicit.?formula"` over `Mathlib/NumberTheory/ Mathlib/Analysis/` hits only value-formula docstrings (transforms + demand scouts, re-confirmed by the demand scout). The barrier's core object, absent in every form |
| bundled class `W` + `BombieriAdmissible` (`SC-BOMB-01` `SC:435-458`, `SC-BOMB-03` `SC:504-513`) | repo definitions; midpoint convention and moment conditions `Mellin(g)(0)=Mellin(g)(1)=0` included; **formulation-selecting** (§4.2) |
| bundled class `A` + Li class `L`, involutions `tilde`/`J`, Mellin realization of `J` (`SC-WEIL-01` `SC:357-406`, `SC-WEIL-02` `SC:408-431`) | repo definitions plus the proved obligation that `J` is a conjugate-linear involution preserving `A`; **formulation-selecting**; Route A only |
| `SC-BOMB-03` autocorrelation closure (`W` closed under `f_g`, Fubini-justified `Mellin(f_g)(s) = Mellin(g)(s)·conj(Mellin(g)(1−conj s))`, `SC:515-536`) | unproved in the source; `ROUTE_TRIAGE.md:296-297` (⊙): "the `SC-BOMB-03` regularity bridge is a genuine blocker". The single hardest purely-this-barrier item, and the only one that is mathematics rather than definition/convention |
| the archimedean term `(log 4π + γ)f(1) + ∫₁^∞ (…) dx/(x−x^{−1})` (`SC:469-472`) | consumes the absent complex-Γ machinery (GROWTH §3.1); the γ development (`Harmonic/EulerMascheroni.lean`) exists |
| bridge `Chebyshev.psi` ↔ `LSeries ↗Λ` | primes scout: `rg -n "Chebyshev.psi|chebyshev" Mathlib/NumberTheory/LSeries/` → 0; paper assembly E1 in §6 |
| Λ-sums against a named test class | nothing instantiates one; the pieces (`sum_PrimePow_eq_sum_sum`, the `tsum` decomposition, Abel summation) are all test-function-generic |
| `SC-BRIDGE-04` local cutoff (`x = 1/T, x = T`), endpoint+finite-prime combination before the limit (`SC:614-641`) | this barrier's per the sibling A-9 boundary; nothing at the pin instantiates it; terminates in the `RESEARCH-OBLIGATION` that is the RH-equivalent target (`SC:636-641`) |
| `ζ'/ζ` beyond `re s > 1`; the contour shift into the strip | **G3, owned by `S1-GROWTH`** (`map:388` overlap noted at GROWTH §1(2), §7.1); recorded by citation, not re-claimed |
| existence of the `|Im ρ| < T` / `|ρ| ≤ T` zero-sum limits | **owned by `S1-GLOBAL-ZEROS`** (its exit string, `map:387`); the *identification* of the limit as the residue output of a contour shift is this barrier plus G3 — exactly the split GROWTH_RECON drew |

---

## 4. Repo-side demand analysis

Which rows consume which clause of the exit string, and for which route.
`SOURCE_CONTRACTS.md` anchors are the **current** lines — the demand scout
found, and this session confirmed on five headers, that commit `c802dc1`
shifted all `SC-WEIL`/`SC-BOMB`/`SC-BRIDGE` anchors +17 relative to the
sibling notes' citations (which were correct when written): ⊙ `SC-WEIL-01`
`:357`, `SC-WEIL-02` `:408`, `SC-BOMB-01` `:435`, `SC-BOMB-02` `:460`,
`SC-BOMB-03` `:494`, `SC-BRIDGE-01/02/03/04` `:549/:586/:603/:614`.

### 4.1 By exit clause

| exit clause | consuming rows (current anchors) | pin status | route |
|---|---|---|---|
| exact test class | `SC-BOMB-01` `:439-446` (class `W`: piecewise `C¹`, first-kind discontinuities, midpoint values, `O(x^δ)`/`O(x^{−1−δ})` decay); `SC-BOMB-03` `:504-513` (`BombieriAdmissible` = `W` + two moment conditions, with the anti-shrink sentence at `:512-513`); `SC-WEIL-01` `:359-369` (class `A`: holomorphic on `0<re s<1`, `O(1/|s|)` for `|im s| ≥ 1`); `SC-WEIL-02` `:410-416` (Li class `L`, `G_n`); negatively `SC-BRIDGE-03` `:603-612` (`G_n ∉ W`; direct substitution invalid) | absent on both sides; only generic Schwartz/`𝓓` substrate exists (§2.2) | C and A-via-C (`W`); A only (`A`, `L`) |
| transform convention | `SC-BOMB-01` `:448-458` (`Mellin(f)(s) = ∫₀^∞ f(x) x^s dx/x`); `SC-WEIL-01` `:371-390` (`tilde`, `J`); `SC-BOMB-03` `:531-536` (derived `Mellin(f_g)` factorization) | **present and source-matched** for the Mellin/Fourier conventions (§2.1); the involutions `J`/`tilde` and the `Mellin(f_g)` identity are repo work | shared A/C for the base convention; A for `J` |
| residues | `SC-BOMB-02` `:467`, `:488-492` (`Mellin(f)(0)`/`Mellin(f)(1)` kept on the spectral side; minus sign on the zero term; multiplicity "required by the residue theorem") | pinned: `riemannZeta_residue_one`, the `LFunctionResidueClassAux` model, `hasMellin_one_Ioc`/`hasMellin_cpow_Ioc`; absent: any contour residue theorem to consume them | C and A-via-C |
| limiting procedure | `SC-BOMB-02` `:475-487` (strict `|im ρ| < T`, `T` through positive reals); `SC-WEIL-02` `:429-431` ("All terms must be obtained from one common finite cutoff before taking limits…"); `SC-BRIDGE-01` `:553-584` (rearrangement legitimacy); `SC-BRIDGE-04` `:614-641` (one common `T`; local cutoff and pre-limit combination = this barrier; spectral cutoff = `S1-GLOBAL-ZEROS`) | absent | A and C; the limits' *existence* is `S1-GLOBAL-ZEROS` |

### 4.2 The "exact test class" clause is formulation-selecting

The exit string's singular "exact test class" is under-determined: the
contract package requires two proved-distinct families — `W`/`BombieriAdmissible`
for the trace form and `A`/`L` for the extended covariance form — plus the
separation `SC-BRIDGE-03` and the conversion `SC-BRIDGE-02` (`:586-601`:
"Sharing the symbol `T` is not a proof", mirrored from the first sibling at
its then-anchor). Freezing one class alone silently selects a formulation —
the exact analogue of the truncation-freezing problem `GLOBAL_ZEROS_RECON.md`
§7 diagnosed. Structural contrast, worth carrying (demand scout, adopted):
`S1-GROWTH`'s exit is *consumed but currently unstatable* ("the selected
theorem" has no referent); `S1-EXPLICIT`'s exit is *statable but currently
unconsumed* — every clause has a concrete `SC` referent, and no unparked
consumer exists. Neither is a closable next target; the reasons differ.

### 4.3 Cross-barrier dependency, statement level

Refinement of the first sibling (recorded by the demand scout, adopted here;
not a contradiction): `S1-GLOBAL-ZEROS`'s sixth exit clause — absolute
convergence of the Weil combination `⟨F,G⟩_W = Σ m(ρ)F(ρ)J(G)(ρ)` — cannot be
*stated* without this barrier's class `A` and involution `J`, since its terms
are `F(ρ)J(G)(ρ)` for `F,G ∈ A`. So `S1-EXPLICIT` is upstream of one
`S1-GLOBAL-ZEROS` exit clause at statement level, while `S1-GROWTH` is
upstream of it at proof level. This slightly strengthens, and does not
contradict, the sibling's non-closability verdict for that row.

### 4.4 Route B consumes nothing from this barrier — checked in both places

Stated at full strength because the check was done, not because it is
convenient (the sibling A-4 lesson): no `SC-NB` row (`SC:645-860`) contains a
test class, transform-convention obligation of this barrier, residue, or
limiting procedure; the Route B DAG (`map:323-359`) has no explicit-formula
node; and — unlike for `S1-GLOBAL-ZEROS` and `S1-GROWTH`, where the siblings'
corrections found bar-level consumption — Route B's bar and preregistration
also consume nothing here: the Burnol window sum (`ROUTE_TRIAGE.md:182-183`,
`:231-232`) is a zero sum with no test function. (`SC-NB-04`'s Fourier–Mellin
isometry uses the *conventions* this barrier's clause names, but as Route B's
own `S2-NYMAN` obligation, not as explicit-formula infrastructure; the map
already books it separately at `:345-348`.)

### 4.5 Consumers are exactly the two parked routes

Route A (`PARK`; alive as a formalization lane per the 2026-08-07 disposition
review) via `map:290-314`; Route C (`PARK`; Route A's required dependency
screen) via `map:361-376`, with ⊙ `map:374-375`: "The explicit formula remains
mandatory shared infrastructure for Weil-first Li, but Route C receives no
independent [budget]". Of the triage's seven-link Route C chain (⊙
`:287-299`), the cheap prefix (i)–(iii) is now entirely closed at HEAD;
everything under this barrier sits in the "large" suffix (vi)–(vii) of the
"plausibly 10k-30k lines" estimate, whose item (vii) carries the strict
`|im ρ| < T` cutoff and the `SC-BOMB-03` "genuine blocker" note verbatim.

---

## 5. Where the scouts disagreed, and where evidence is thin

1. **The barrier row's own line number.** The transforms scout cited the row
   at `MATHLIB_CAPABILITY_MAP.md:388` and claimed it "verbatim, re-extracted";
   `:388` is `S1-GROWTH`. The demand scout cited `:390`. ⊙ Verified this
   session: **`:390` is correct**, and the row text matches the demand scout's
   quote (four clauses, including "and limiting procedure", which the tasking
   prompt's own header truncated). The transforms scout's substantive content
   was unaffected — it quoted the full exit string in its body — but a note
   whose lane was caught on locator discipline must not propagate that anchor.

2. **State drift across the three passes, and beyond them.** (a) The demand
   scout's SC-anchor correction (+17 after commit `c802dc1`) is right; five
   headers re-verified this session (§4 preamble). The sibling notes' `SC:`
   anchors are stale by +17 and were correct when written; this note uses
   current anchors throughout. (b) The demand scout's own repo state is
   already stale: it reports HEAD `3783f31` and "current queue RH-011", but
   HEAD at write time is `6a1195f`, four commits later (⊙ `git log`): two
   drafts commits (`ff00bd2`, `aab3ad2`) adding `MellinBound.lean`,
   `HarnackDisc.lean`, `PolyLiouville.lean`, `ThreeCircles.lean` — none
   claiming `S1-EXPLICIT` scope, listing verified ⊙ — then the RH-011
   acceptance and RH-012 activation (`e9b5090`), then the decision-block
   update (`6a1195f`). All four are PR #315 **branch** hashes: the mainline
   squash-merged them as the single commit `9129e8c`, so none of the four is
   an ancestor of any mainline head, and a mainline `git log` will not find
   them (Annex B-1). `RH-011` is recorded completed 2026-08-07 with the
   ACTIVE slot moved to `RH-012` (⊙ `tasks/RIEMANN_HYPOTHESIS.md:45-50`).
   Neither drift changes any verdict; both are recorded so this note does not
   freeze a stale state.

3. **Overlap claims between the two inventory scouts are complementary, not
   conflicting.** The transforms scout's unmapped finds (`mellin_eq_fourier`,
   the Fourier typeclass refactor) and the primes scout's
   (`Chebyshev.lean`, `AbelSummation.lean`, `MellinEqDirichlet.lean`,
   `PrimesInAP.lean`, `SumCoeff.lean:336`) are disjoint; both sets are carried
   into the proposed amendments. Their capability-map row-number citations for
   the Mellin rows differ by one ("135-137" vs "136-137"); this note cites map
   rows only by anchors it re-extracted and does not adjudicate that cell.

4. **"All ingredients pinned" for the §6 assemblies E1/E2.** The primes scout
   named every ingredient; this session re-extracted the six load-bearing
   declaration lines (`SumCoeff.lean:137`, `Chebyshev.lean:70/:413`,
   `Dirichlet.lean:434`, `PrimesInAP.lean:87`, `VonMangoldt.lean:65`). The
   scout's own disclosed soft points stand un-discharged: ℝ→ℂ cast
   bookkeeping and `Icc`/`Ioc` seam conversions were not stress-tested, and
   nothing was kernel-checked. Per the sibling discipline these rows are
   marked "yes, spot-checked, seams untested" — not plain "yes".

5. **Absence proofs are search proofs.** The searches most at risk, named by
   the scouts and endorsed here: a Perron-shaped theorem under a
   `mellinInv`-flavored name (the transforms scout read `MellinInversion.lean`
   end to end — it is not there); residue calculus under `circleIntegral`
   names; "smoothed sum" / "test class" phrasing. A theorem present under an
   unguessed name would be missed.

6. **`Chebyshev.lean` is recent upstream** (2025 copyright, upstreamed from
   PrimeNumberTheoremAnd): its API may still be moving above the pin. That
   affects the durability of cost estimates built against it, not its presence
   at this pin.

---

## 6. Cost estimate per missing item

Units follow the earlier barriers: statement count (the `X`/`Z`/`M` convention,
by analogy only) and whether all ingredients are pinned. Source-reading
estimates; **no Lean was run**. Per the standing rule, no row is described as
small unless every ingredient is demonstrably pinned and named.

**Scope boundary for this table** (mirroring siblings A-9/A-10). Rows tagged
`S1-GROWTH` or `S1-GLOBAL-ZEROS` appear as blockers of, or immediate
neighbours of, this barrier — not as items claimed under `S1-EXPLICIT`.
`S1-EXPLICIT` owns the test-class definitions and their growth/regularity
conditions (per GROWTH §6's boundary, textually forced by `map:388`'s
"zeta/xi" scoping — the conditions constrain test functions, not ζ/ξ), the
transform-convention and residue conventions, and `SC-BRIDGE-04`'s *local*
cutoff. It does not own G3, the spectral cutoff, or the zero-sum limits.

| item | statements | all ingredients pinned? | blocked on |
|---|---|---|---|
| transform-convention reconciliation (source `x^s dx/x` ↔ pinned `mellin`; unitary Fourier) | 0 Lean — a mismatch-register record | — (definitional match, spot-checked ⊙) | nothing. Zero-cost, route-neutral; `map:404` ("Weil test-function class and transform | generic Fourier/Mellin infrastructure | exact regularity, symmetry, decay, normalization, and residue conditions absent", ⊙) half-carries it already |
| E1: `L ↗Λ s = s * ∫ t in Ioi 1, (ψ t : ℂ) * t^(-(s+1))` for `re s > 1` | ~2–4 | **yes, spot-checked, seams untested** — `LSeries_eq_mul_integral` (`:137`, `r = 1`), `LSeriesSummable_vonMangoldt` (`Dirichlet.lean:379`), `psi_le_const_mul_self` (`:413`), `psi` (`:70`); casts and `Icc`/`Ioc` seams not stress-tested (§5.4) | nothing. An ingredient, not an exit; `corpus.md:99-100` applies |
| E2: `L ↗Λ s = Σ'_p Σ'_k log p / p^{(k+1)s}` for `re s > 1` | ~2–3 | **yes, spot-checked, seams untested** — `tsum_eq_tsum_primes_of_support_subset_prime_powers` (`PrimesInAP.lean:87`), `vonMangoldt_ne_zero_iff` (`:92`), `LSeriesSummable_vonMangoldt` | nothing. Same caveat |
| definition: class `W` (+ midpoint convention) and `BombieriAdmissible` | ~2 defs + ~6–12 API — **definition and basic API only**: `SC-BOMB-01`'s strip-analyticity clause (`Mellin(f)` analytic on `−δ < re s < 1+δ`) is consumer-facing work this row does not book, and its piecewise-integrability seams are unpinned (Annex B-4) | **partly** — no pinned piecewise-`C¹`/first-kind-discontinuity substrate (§3.1); decay via `=O` filters is pinned | **formulation-selecting** (§4.2); consumers parked |
| definition: class `A`, class `L`, involutions `tilde`/`J`, `J` preserves `A` | ~3 defs + ~6–10 | **mostly** — `DifferentiableOn`, `=O`, `starRingEnd` all pinned; the `A.7` Mellin realization of `J` needs the Fourier bridge (pinned, §2.1) | **formulation-selecting**; Route A only |
| `SC-BOMB-03` autocorrelation closure (`W` closed under `f_g`; Fubini; `Mellin(f_g)` factorization) | unknown; triage-rated blocker | **no** — genuine unproved mathematics; the source itself does not prove it (`SC:515-529`: "a formalization blocker rather than an implicit premise") | the `W` definition; and it is the hardest purely-own item |
| archimedean term (`(log 4π + γ)f(1) + ∫₁^∞ …`) | ~4–8 once Γ inputs exist | **no** — complex-Γ asymptotics absent (GROWTH §3.1); γ pinned | complex Stirling (`S1-GROWTH` neighbour / upstream) |
| Perron / vertical-line contour shift for `−ζ′/ζ` against a test transform | **large** | **no** — no argument principle, no residue theorem, no Perron at the pin; `ζ'/ζ` exists only on `re s > 1` | generic contour machinery (upstream-sized) **and** G3 (`S1-GROWTH`) **and** the zero-sum limits (`S1-GLOBAL-ZEROS`) |
| the explicit formula proper (`SC-BOMB-02` trace form, or `SC-WEIL-02` Gram identities via LAG07 Thm 3.1) | **large** — the triage's (vii) | **no** | all of the above; triage: "large; the `SC-BOMB-03` regularity bridge is a genuine blocker" |
| `SC-BRIDGE-04` local-cutoff regularization and pre-limit combination | ~4–8 once the formula exists | **no** | the formula; downstream terminates in the RH-equivalent `RESEARCH-OBLIGATION` (`SC:636-641`) |
| generic contour/residue machinery (argument principle, residue theorem, Perron) offered upstream | **large** | **no** — nothing at the pin | a genuinely new upstream development; covered by **no** drafted pillar contract (the seven pillars deliberately stop short of contour integration) |

For calibration: everything from the `W`/`A` definitions downward sits inside
the triage's "plausibly 10k-30k lines" Route C estimate, in its non-cheap
suffix (§4.5). E1+E2 together are the size of half a small package and are the
only rows with a pinned-and-named ingredient list.

---

## 7. Misallocation warning

The following items have **no consumer other than a parked route**. Building
any of them first would spend budget on a route that `ROUTE_TRIAGE.md`
explicitly did not select, and in most cases is additionally blocked. The §6
scope boundary applies: `S1-GROWTH` and `S1-GLOBAL-ZEROS` rows appear as
blockers, not as items claimed here.

| item | row(s) | sole consumer(s) | why flagged |
|---|---|---|---|
| classes `W`/`BombieriAdmissible`; classes `A`/`L`; `J` | `SC-BOMB-01/-03`, `SC-WEIL-01/-02` | Routes A and C — both `PARK` | **sharpest flag**: additionally formulation-selecting (§4.2). Writing either definition pair is a partial route selection under a zero-route disposition |
| `SC-BOMB-03` closure | `SC:494-545`; triage (vii) | Route C + A-via-C — both `PARK` | "a genuine blocker"; unproved in the source; maximum difficulty, zero unparked demand |
| the explicit formula proper | `SC-BOMB-02`; `SC-WEIL-02`; `map:390` | Routes A and C — both `PARK` | blocked on three barriers simultaneously (§6); the "blocks" column names only parked machinery |
| archimedean term | `SC:469-472` | same | blocked on absent complex-Γ machinery |
| `SC-BRIDGE-04` local cutoff package | `SC:614-641` | **Route A only** | its stated downstream is the RH-equivalent `RESEARCH-OBLIGATION` itself |
| E1/E2 (arithmetic-side identities, `re s > 1`) | §6 | Routes A and C (as future inputs) — both `PARK` | cheap and route-neutral *as statements*, but with **zero unparked consumers**; building them now buys nothing any active queue item needs. Flagged despite being this note's only pinned-ingredient rows |
| generic contour/residue machinery, if built **in-repo** | §3.1 | parked routes only, in-repo | route-neutral and RH-free, but "large", and the correct venue is upstream (Option C); in-repo it would be parked-route budget. Upstream, it fires only the cost-only triggers `A-T4`/`C-T3`, which never auto-`SELECT` (GROWTH §7.2, incl. its B-1 attribution correction) |

**Structural consequence, stated plainly.** Every clause of the exit string at
`map:390` either is already satisfied by the pin (the base transform
conventions — which therefore cannot be "built" as progress), or is
formulation-selecting (test classes), or is blocked on absent generic
machinery plus two other open barriers (residues, limiting procedure). The
demand scout's contrast holds: the exit is statable but unconsumed. **Closing
this row is not available to route-neutral work, and no unparked work is
waiting on it.**

---

## 8. Recommendation — options, not a selection; and the honest verdict

Selection belongs to the maintainer and to the queue. Five options with their
honest costs; this note picks none.

**The honest verdict first, as the tasking requires, stated plainly:
`S1-EXPLICIT` should not be attempted next. Do not attempt.** Grounds, each
established above: (i) its consumers are exactly the two parked routes, with
the Route B negative verified at both levels (§4.4-4.5) and zero in-repo or
queued consumers (§2.6) — the active slot, `RH-012`, sits under
`S1-GLOBAL-ZEROS`; (ii) its only non-blocked, non-selecting work is either
zero-Lean-cost record-keeping or `re s > 1` ingredients with no unparked
consumer (§7); (iii) its substantive half is blocked on absent generic contour
machinery **and** on `S1-GROWTH` G3 **and** on `S1-GLOBAL-ZEROS` limits —
three simultaneous blockers, two of them barriers the sibling notes have
already, on their own grounds, judged not-attemptable-next; (iv) its cheapest
distinctive items (the class definitions) are formulation-selecting, which is
a partial route selection the triage's zero-route disposition forbids; and
(v) its hardest own item is a triage-certified "genuine blocker". This is a
stronger do-not-attempt than either sibling's: `S1-GROWTH` at least had a
convention-free pilot candidate (its G1) consumed by all three route families;
`S1-EXPLICIT` has no analogue — its one "already fine" quarter needs no
building and its every buildable item serves parked routes only.

**Option A — do nothing under this barrier; let the active queue proceed.**
`RH-012` (zero-set slice drafting) is the dated ACTIVE slot and consumes
nothing from this barrier. The option with zero ordering hazards. If the queue
wants a next item, it already has one, and it is not here.

**Option B — zero-Lean-cost record-keeping only.** Apply the proposed map
amendments below: the transform-convention reconciliation into the mismatch
register (a *match* record — rarer and cheaper than a mismatch), and the
unmapped-inventory rows (`Chebyshev.lean`, `AbelSummation.lean`,
`mellin_eq_fourier`, `MellinEqDirichlet.lean`, `PrimesInAP.lean`,
`SumCoeff.lean:336`). Pure documentation; closes nothing; makes the next
consumer of the map see the true pin. This is the only work under this barrier
with a live consumer (the map's readers), and it is not Lean work.

**Option C — offer the generic contour/residue pool upstream rather than
building it here.** Argument principle, winding number, contour residue
theorem, Perron for Mellin/Dirichlet integrals. Route-neutral, RH-free,
reviewable on its own merits, genuinely large, long review latency, not a
repository barrier item, and covered by no drafted pillar contract. Upstream
landing would fire `A-T4`/`C-T3` — both cost-only, never auto-`SELECT` (with
the sibling's B-1 caveat on which preamble carries that clause).

**Option D — the E1/E2 ingredient slice, only if a future dated decision
revives an explicit-formula consumer.** ~4–7 statements, the only rows here
with pinned-and-named ingredients (spot-checked, seams untested, not
kernel-checked). Preregister its limits if ever contracted: `re s > 1` only;
ingredients, not exits; removes no named barrier; currently zero unparked
consumers (§7's flag applies today and is the reason this option is
conditional).

**Option E — fix the row's wording question first.** The maintainer may
reasonably conclude that a row whose "exact test class" is singular where the
contracts require two proved-distinct families, and whose transform-convention
clause is already pin-satisfied, should be reworded or split before any work
is scheduled against it. A map-file decision, not a mathematical item; this
note does not make it.

**Proposed capability-map amendments** (recon output; **not applied**; none
retires a row):

1. Add `PRESENT` rows for `NumberTheory/Chebyshev.lean` (ψ `:70`, θ `:77`,
   two-sided Chebyshev bounds `:166/:413/:438/:455`, `sum_PrimePow_eq_sum_sum`
   `:308`, π↔θ Abel identities `:484/:520`) and
   `NumberTheory/AbelSummation.lean` (`sum_mul_eq_sub_sub_integral_mul` `:129`
   and family, limit forms `:281/:300`, `summable_mul_of_bigO_atTop` `:366`),
   each gapped "re s > 1 / Chebyshev-order only; no PNT, no Mertens, no
   Tauberian, no bridge to `LSeries ↗Λ`".
2. Add a `GENERIC` row for **`mellin_eq_fourier` / `mellinInv_eq_fourierInv`**
   (`MellinInversion.lean:49/:75`), gapped "no ζ/ξ instance; transports
   Fourier Plancherel/inversion to the Mellin side", and update the `SC-NB-04`
   note at `:345-348` accordingly (part of the booked log-substitution is a
   pinned theorem).
3. Add `PRESENT`/`GENERIC` rows for `hasSum_mellin`
   (`MellinEqDirichlet.lean:24`), the prime-power decomposition
   (`PrimesInAP.lean:87/:99`), the `LFunctionResidueClassAux` package
   (`:304/:333/:348`), and the Abelian residue theorems
   (`SumCoeff.lean:336/:362`, gapped "Abelian direction only; the Tauberian
   converse is absent").
4. Add a semantic-mismatch-register row recording a **match**: `SC-BOMB-01`'s
   `Mellin` convention = pinned `mellin` definitionally; pinned Fourier is the
   source's unitary convention; and a **hazard** row: the 2025-11-16 Fourier
   refactor's deprecated-alias layer (`tsum_eq_tsum_fourierIntegral` →
   `tsum_eq_tsum_fourier`, etc.).
5. Record the §3 ABSENT findings individually with their searches: no explicit
   formula in any form, no Perron, no Tauberian/Wiener–Ikehara, no Mertens, no
   PNT, no bundled `W`/`A`-type class, no Mellin-Plancherel/convolution.
6. Note in the `S1-EXPLICIT` row that its "exact test class" clause is
   route-indexed in practice (two proved-distinct families per
   `SC-BRIDGE-03`), and that its transform-convention clause is
   pin-satisfied — a single exit string invites reporting the cheap quarter as
   progress on the row.
7. Correct any copy of the sibling notes' `SC:` anchors on next edit (+17
   shift, §4 preamble); the sibling texts themselves need no reopening for
   this — their anchors were correct when written and their Annexes say so.

Whether to apply any of these is a maintainer decision on the map file. No
route is unparked, no revival bar is claimed met, no barrier is declared
closed or stale, and no statement in this note bears on the truth of the
Riemann Hypothesis.

---

## Annex A — verification log, 2026-08-07

Method: synthesis of three same-day scout passes (transforms, primes-side,
demand) over the same pin, followed by an independent verification pass this
session. Re-verified this session by direct extraction (⊙ marks in the text):
the pin (`git rev-parse HEAD`); repo HEAD `6a1195f` and the four commits past
the demand scout's `3783f31` (branch hashes; mainline squash `9129e8c` —
Annex B-1); the barrier row at `map:390` (resolving the
transforms scout's `:388` error); five current `SC-*` header anchors
(`:357/:408/:435/:460/:494` and `SC-BRIDGE` `:549/:586/:603/:614`);
`map:374-375`, `:345-348`, `:404` (correcting the scouts' `:401` for the
Weil test-function row), `:485-494`; triage `:287-299` including the
`SC-BOMB-03` "genuine blocker" sentence; `SC:443-448` and `:512-513`;
`corpus.md:99-100`; `tasks/RIEMANN_HYPOTHESIS.md:45-50` (RH-011 completed,
RH-012 active); the `drafts/` listing; the repo-side zero-consumer grep; and
22 Mathlib declaration lines across `MellinTransform.lean`,
`MellinInversion.lean`, `FourierTransform.lean`, `LpSpace.lean`,
`PoissonSummation.lean`, `Circle.lean`, `Chebyshev.lean`,
`AbelSummation.lean`, `SumCoeff.lean`, `Dirichlet.lean`, `PrimesInAP.lean`,
`MellinEqDirichlet.lean`, `RiemannZeta.lean`, `VonMangoldt.lean` — all 22
matched the scouts' citations. Re-run this session: the seven negative
searches quoted in §1(3) and §3 (`riemann.?weil`, `perron`,
`argument.?principle|winding`, `mertens`, `wiener`, `PrimeNumberTheorem`,
`norm_mellin`), all with the reported hit counts.

Not verified, and named as such: nothing is kernel-checked (no toolchain);
locators not marked ⊙ rest on the scouts' same-day extraction with the 22/22
sample above; the E1/E2 "pinned" claims were spot-checked at declaration level
only, with cast/`Icc` seams untested; ABSENT verdicts are search-absence
(§5.5); statement counts follow the `X`/`Z`/`M` convention by analogy only;
and `E`-generality instance paths of the analysis-side declarations were not
audited (mirroring GROWTH §5.8).

Re-read end to end for route selection, unparking, staleness assertions,
barrier closure, or RH progress: **none found.** The verdict "do not attempt"
is a queue-order recommendation offered to the maintainer, not a row
amendment. No file other than this note is created or amended.

---

## Annex B — adversarial red-team review, 2026-08-07

Independent hostile pass, same day, same pin (`fabf563a` re-verified;
mainline head at review `77a6673`). Method: every ⊙ locator re-extracted
from scratch; every quoted search re-run verbatim; costs, negatives, scope
boundaries, and route-selection language attacked. Findings fixed in place
above, each marked with its B-number.

| # | severity | finding | status |
|---|---|---|---|
| **B-1** | MEDIUM | **Mainline-unreachable commit hashes.** The header, state block, §5.2, and Annex A cited `ff00bd2`/`aab3ad2`/`e9b5090`/`6a1195f` as "repository HEAD"/"four commits past `3783f31`". All four exist only on the PR #315 working branch; the mainline squash-merged them as the single commit `9129e8c` before this note landed, and `git merge-base --is-ancestor` confirms none is a mainline ancestor. A reader at any mainline head cannot reproduce the note's `git log` claims as written. Every *content* claim survives at `9129e8c` (four pillar drafts added, RH-011 completed, RH-012 activated, decision block updated — re-verified against `tasks/RIEMANN_HYPOTHESIS.md:40-50` and the `drafts/` listing). Same defect class as the lane's locator-discipline lessons (first sibling A-8), on git anchors instead of file lines | **FIXED** — squash mapping added at all four occurrences |
| **B-2** | MINOR | **Overstated written exclusion, in the convenient direction.** §2.6 claimed the xi claim boundary "excludes it in writing"; `XI_PACKAGE_CONTRACT.md:27` actually excludes "enumeration, growth, Hadamard products, conjugation, or any route's research obligation" — the explicit formula is covered by subsumption, never named. The zero-consumer finding survives regardless (the grep is 0 hits), but the overstatement strengthened §8's verdict, which is exactly the direction this lane must not soften or inflate toward | **FIXED** — reworded |
| **B-3** | MINOR | **Draft-count arithmetic.** The state block called the `README.md` ledger a "pillar draft" to reach "five"; §2.6 then listed four files as "the five pillar drafts". Actual `drafts/` at HEAD: nine files = four merged-package drafts + four pillar Lean drafts + `README.md` (re-listed this review) | **FIXED** — both occurrences now say four + ledger |
| **B-4** | MINOR | **Optimistic cost booking on the class-`W` row.** §6's "~2 defs + ~6–12 API" read as if it covered the `SC-BOMB-01` surface, but that contract's strip-analyticity clause (`Mellin(f)` analytic on `−δ < re s < 1+δ`, `SC:454-458`) is separate consumer-facing work whose piecewise-integrability seams have no pinned substrate (§3.1's 0-hit search). The row was already marked "partly" pinned, so no estimate was falsified; it was under-scoped | **FIXED** — obligation named in the row; estimate deliberately not re-guessed |
| **B-5** | TRIVIAL | §2.4 called `hasMellin_one_Ioc`/`hasMellin_cpow_Ioc` "exactly the endpoint-term shapes" of `SC-BOMB-02`'s `Mellin(f)(0)`/`Mellin(f)(1)`. They are indicator/cpow models with the right pole shape (`1/s`), not those terms — "exactly" overstated an analogy | **FIXED** — "a pinned model of, not identical to" |
| **B-6** | TRIVIAL | §1(1)'s "largely already satisfied" headline could be read as retiring the transform-convention clause, i.e. incipient barrier re-scoping, since the clause's consuming rows (§4.1) include the unbuilt `J`/`tilde` involutions and the `Mellin(f_g)` factorization. §4.1 disclosed this; §1 did not | **FIXED** — non-exhaustion sentence added to §1(1). The exit string remains quoted in full and un-narrowed |

**What survived attack unchanged.** (i) All eleven quoted searches re-run this
review and reproduced with the exact reported hit counts: `riemann.?weil|
weil.?explicit` 0; `perron` in `NumberTheory/` 0 (tree-wide: Perron–Frobenius
and an author name, as stated); `argument.?principle|winding` 0; `mertens` 0;
`wiener` 1 (`PrimesInAP.lean:298`, prose); `PrimeNumberTheorem` 1
(`Chebyshev.lean:56`, attribution); `norm_mellin|‖mellin` 0;
`first.?kind.*discontinuit` 0; repo `grep -rn "explicit formula" ResearchOS/
Ecdlp/` 0; `explicit.?formula` over `NumberTheory/`+`Analysis/` value-formula
docstrings only; `Chebyshev.psi|chebyshev` in `LSeries/` 0. A hunt for a
residue theorem under unguessed names (`find -iname "*residue*"`, `rg -l
residue Analysis/Complex/`) found only algebraic-geometry residue fields and
`SumOverResidueClass` — the §3.1 ABSENT verdicts stand. (ii) Roughly 45
Mathlib declaration-line locators re-extracted across 25 files — every one
matched, including the full Chebyshev/AbelSummation inventories (703/399
lines confirmed, 0 `IsEquivalent`), the `mellin`/`mellinInv` definitions
byte-for-byte, the 2025-11-16 deprecation layer, and the
`@[to_additive tsum_eq_tsum_primes_of_support_subset_prime_powers]` attribute
at `PrimesInAP.lean:86` (so §2.5's `tprod_…` and §6-E2's `tsum_…` names are
both real, one attribute apart, not a citation error). (iii) The +17 SC
anchor shift verified directly against `c802dc1^`: `SC-WEIL-01` 340→357,
`SC-BOMB-01` 418→435, `SC-BRIDGE-04` 597→614, `SC-NB-01` 628→645. (iv) All
repo-side anchors: `map:386/387/388/390/404` and `:345-348/:374-375/:485-488/
:626-656`; `triage:296-297` ("genuine blocker" verbatim), `:287-299`,
`:182-183/:231-232`; `tasks:43-50`; `corpus:99-100`; the SC-BOMB/WEIL/BRIDGE
content quotes including `:512-513` and `:636-641`. (v) The E1 shape against
`LSeries_eq_mul_integral`'s actual `Icc 1 ⌊t⌋₊` statement — the disclosed
`Icc`/`Ioc` seam is real and correctly not waved away. (vi) Sibling mirrors:
GROWTH §6 owns the `mellin` norm bound (its `:391`), GROWTH `:833` supports
the "G1 consumed by all three route families" contrast, GLOBAL-ZEROS §7 is
the truncation-freezing diagnosis §4.2 cites, and the B-1 attribution caveat
on `A-T4`/`C-T3` is carried correctly. No sibling contradiction found.
(vii) No softened negative found — B-2 was the dual defect, an overstated
positive. (viii) No route selection, no unparking, no barrier closure or
staleness assertion, no RH-truth claim; §8's "do not attempt" is a
recommendation with grounds that all survived re-verification.

**Red-team verdict: the note SURVIVES.** Its four headline claims, §3's
ABSENT table, §4's demand analysis, §6's only-pinned-rows calibration
(E1/E2), §7's misallocation flags, and §8's do-not-attempt verdict are all
confirmed at the pin after the six corrections above. The two systemic
lessons for the lane: quote git anchors only from the history a mainline
reader can reproduce (B-1), and "in writing" means named, not subsumed (B-2).
This annex amends only this note; nothing else is created, amended, closed,
selected, or re-scoped, and nothing here bears on the truth of the Riemann
Hypothesis.
