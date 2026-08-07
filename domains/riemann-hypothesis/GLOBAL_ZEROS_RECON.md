# `S1-GLOBAL-ZEROS` reconnaissance note

Status: **reconnaissance only — capability note, not a contract, not a Lean
draft, not a promotion.** Nothing here claims a proof, selects or unparks a
route, asserts that any barrier is closed or stale, or asserts progress on the
truth of the Riemann Hypothesis. Honest negative findings are recorded on the
same footing as positive ones.

Audit date: 2026-08-07

Mathlib revision: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0), verified
this session by `git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`.
Local checkout read with ripgrep/`sed` only; **no Lean toolchain is available in
this container, so every feasibility judgement below is a source-reading
estimate and none of it has been kernel-checked.**

Barrier under examination, `MATHLIB_CAPABILITY_MAP.md:387`:

> `S1-GLOBAL-ZEROS` | no global enumeration, symmetric truncation, convergence,
> or counting API | Li sums, canonical product, explicit formula | exit
> evidence: finite divisor sums, weighted summability, star convergence of
> `Σ 1/ρ`, existence of source-matched limits with multiplicity, including
> `|ρ| ≤ T` for Li and `|Im ρ| < T` for Weil, plus absolute convergence of the
> Weil scalar-product combination

Repository state assumed: `TargetBridge.lean` and `Xi.lean` merged and
kernel-checked; `Conj.lean` CI-green and pending merge; `S1-MULTIPLICITY` in
flight with `MULTIPLICITY_CONTRACT.md` drafted and **awaiting independent
acceptance**, and `drafts/RiemannMult.lean` unbuilt.

---

## 1. Headline

Three things, stated separately because they are easy to conflate.

1. **The pin carries substantially more zero-side machinery than the barrier
   row's four-word gap phrase suggests.** In particular a global,
   multiplicity-carrying divisor object (`MeromorphicOn.divisor f Set.univ`), a
   full Nevanlinna value-distribution layer with a genuine counting function
   (`logCounting`, `characteristic`, First Main Theorem), Jensen's formula, and
   a proved growth-implies-zero-count inequality (`AnalyticOnNhd.sum_divisor_le`).
   **Only the Nevanlinna layer is unrecorded in `MATHLIB_CAPABILITY_MAP.md`**
   (Annex A-1): the map already carries `MeromorphicOn.divisor` at row 132 and
   "Jensen formula and divisor bound" — `MeromorphicOn.circleAverage_log_norm`
   *and* `AnalyticOnNhd.sum_divisor_le` — at row 133, and names both in the
   summary paragraph at `:35`. The genuinely new inventory is
   `Mathlib/Analysis/Complex/ValueDistribution/` and the symmetric-truncation
   summation filters of §2.5.

2. **None of that retires the row.** Per `MULTIPLICITY_CONTRACT.md` finding A4
   and death condition 9, capability-map rows are scoped to *this repository's*
   ζ/ξ layer; generic pinned machinery lowers cost and never closes a row. The
   pinned counting function is also the wrong object: it is radial and
   *logarithmically weighted*, whereas `SC-XI-01`(2) asks for the unweighted
   `N_ξ(T) = Σ_{|ρ| ≤ T} m(ρ)`. Substituting one for the other would be a fresh
   semantic mismatch of exactly the kind the register at
   `MATHLIB_CAPABILITY_MAP.md:394-407` exists to catch.

3. **As written, this barrier cannot be closed by route-neutral work, and it
   should not be the next target.** Five of the six clauses in its exit string
   name either a route-frozen truncation convention (`|ρ| ≤ T` for Li vs.
   `|Im ρ| < T` for Weil — declared non-interchangeable by `SC-BRIDGE-02`) or a
   Route-A-only convergence fact. Closing the row therefore requires freezing a
   convention, which is a route selection; `ROUTE_TRIAGE.md` selected zero
   routes. Separately, everything asymptotic under this row is downstream of
   `S1-GROWTH`, which has no contract, no draft, and no accepted statement
   surface in this repository. See §7.

---

## 2. Inventory: what exists at the pin

All locators re-verified this session against the pinned tree. Line numbers are
the declaration keyword line, not the doc-comment opener.

### 2.1 Zeta zeros (repo-relevant, already partly mapped)

| capability | pinned declaration | boundary |
|---|---|---|
| ζ zero set | `riemannZetaZeros`, `NumberTheory/LSeries/ZetaZeros.lean:33` | `Set ℂ`; multiplicity erased |
| membership | `mem_riemannZetaZeros`, `:35` | definitional |
| closed / discrete | `isClosed_riemannZetaZeros`, `:57`; `isDiscrete_riemannZetaZeros`, `:60` | topology only |
| finite in compacts | `IsCompact.inter_riemannZetaZeros_finite`, `:64` | the whole public counting surface for ζ at the pin |
| escape from compacts | `tendsto_riemannZeta_cofinite_cocompact`, `:70` | already recorded at map row 115 |

The file is 74 lines. There is no ζ multiplicity, no ordering, no `N(T)`, no
density, and no rectangle- or strip-indexed statement. Rows 112–115 of the
capability map already carry all five of these.

### 2.2 Divisor and locally-finite-support layer

| capability | pinned declaration | note |
|---|---|---|
| divisor of a meromorphic function | `MeromorphicOn.divisor`, `Analysis/Meromorphic/Divisor.lean:39` | ℤ-valued, `locallyFinsuppWithin U ℤ`; **already at map row 132** |
| global case is first-class | `Function.locallyFinsupp`, `Topology/LocallyFinsupp.lean:61` (abbrev for `U = Set.univ`) | with `meromorphicOn_univ`, `Meromorphic/Basic.lean:659` |
| structure | `Function.locallyFinsuppWithin`, `Topology/LocallyFinsupp.lean:48` | carries the local-finiteness field |
| support discrete / closed / finite | `.discreteSupport` `:218`, `.closedSupport` `:237`, `.finiteSupport` `:254` | `.finiteSupport` needs `IsCompact U` |
| restriction maps | `restrict` `:584`, `restrictMonoidHom` `:625` | no pullback/`comap` (repo `DEFERRED-1`) |
| divisor finiteness on compacts | `divisor_support_finite_of_subset`, `Divisor.lean:91`; `divisor_ball_support_finite`, `:104` | compactness-gated |
| analytic ⇒ effective | `AnalyticOnNhd.divisor_nonneg`, `Divisor.lean:177` | |

Supporting bridges, all verified: `IsCompact.finite`
(`Topology/Compactness/Compact.lean:1046`),
`Metric.finite_isBounded_inter_isClosed` (`Topology/MetricSpace/Bounded.lean:627`),
`mem_codiscrete'` / `compl_mem_codiscrete_iff` (`Topology/DiscreteSubset.lean:343` / `:347`),
`AnalyticOnNhd.preimage_zero_mem_codiscreteWithin` / `.preimage_zero_mem_codiscrete`
(`Analysis/Analytic/Order.lean:664` / `:682`),
`analyticOnNhd_univ_iff_differentiable` (`Analysis/Complex/CauchyIntegral.lean:678`),
`IsCompact.reProdIm` (`Analysis/Complex/Basic.lean:706`),
`Set.ncard` (`Data/Set/Card.lean:628`).

### 2.3 Nevanlinna value-distribution layer — **not currently in the capability map**

`Mathlib/Analysis/Complex/ValueDistribution/` contains `Cartan.lean`,
`CharacteristicFunction.lean`, `FirstMainTheorem.lean`, `LogCounting/Basic.lean`,
`LogCounting/Asymptotic.lean`, `Proximity/Basic.lean`.

| capability | pinned declaration |
|---|---|
| restriction of a global divisor to a closed disc | `Function.locallyFinsuppWithin.toClosedBall`, `LogCounting/Basic.lean:57`; `toClosedBall_divisor`, `:70` |
| logarithmic counting function (divisor form) | `Function.locallyFinsuppWithin.logCounting`, `LogCounting/Basic.lean:96` — an `AddMonoidHom` `locallyFinsupp E ℤ →+ (ℝ → ℝ)`, `D ↦ fun r ↦ ∑ᶠ z, D.toClosedBall r z * log (r * ‖z‖⁻¹) + (D 0) * log r` |
| elementary theory | `logCounting_single_eq_log_sub_const` `:131`, `logCounting_even` `:154`, `logCounting_mono` `:160`, `logCounting_strictMono` `:199`, `logCounting_nonneg` `:217`, `logCounting_le` `:235`, `logCounting_eventuallyLE` `:244` |
| counting function of a meromorphic function | `ValueDistribution.logCounting`, `LogCounting/Basic.lean:272` |
| its theory | `logCounting_even` `:347`, `logCounting_monotoneOn` `:355`, `logCounting_nonneg` `:363`, multiplicativity/subadditivity `:408-:546` |
| Jensen restated via `logCounting` | `Function.locallyFinsuppWithin.logCounting_divisor_eq_circleAverage_sub_const`, `:588` |
| growth characterization | `logCounting_isBigO_one_iff_analyticOnNhd`, `LogCounting/Asymptotic.lean:108` |
| characteristic function | `ValueDistribution.characteristic`, `CharacteristicFunction.lean:53` (`proximity f a + logCounting f a`) |
| First Main Theorem | `FirstMainTheorem.lean:97`, `:109`, `:131`, `:160` |

### 2.4 Jensen layer — the one pinned zero-count *bound* (already at map row 133)

```
Mathlib/Analysis/Complex/JensenFormula.lean:307
theorem MeromorphicOn.circleAverage_log_norm (hR : R ≠ 0)
    (h₁f : MeromorphicOn f (closedBall c |R|)) :
    circleAverage (log ‖f ·‖) c R
      = ∑ᶠ u, divisor f (closedBall c |R|) u * log (R * ‖c - u‖⁻¹)
        + divisor f (closedBall c |R|) c * log R + log ‖meromorphicTrailingCoeffAt f c‖
```

```
Mathlib/Analysis/Complex/JensenFormula.lean:389
/-- **Jensen's Inequality**: Estimates the number of zeros of `f` in a ball of
radius `r` given that `f` is analytic and bounded by `M` on a larger ball. -/
theorem AnalyticOnNhd.sum_divisor_le (r_pos : 0 < |r|) (r_lt_R : |r| < |R|)
    (hM : 1 ≤ M) (h₁f : AnalyticOnNhd ℂ f (closedBall c |R|)) (h₂f : f c ≠ 0)
    (f_bound : ∀ z ∈ sphere c |R|, ‖f z‖ ≤ M) :
    ∑ᶠ u, divisor f (closedBall c |r|) u ≤ Real.log (M / ‖f c‖) / Real.log (R / r)
```

Also present: `AnalyticOnNhd.circleAverage_log_norm`, `:375`;
`countingFunction_finsum_eq_finsum_add`, `:275`.

Both are already recorded in `MATHLIB_CAPABILITY_MAP.md` row 133 ("Jensen
formula and divisor bound", gap "no zeta/xi growth input"), and `ROUTE_TRIAGE.md`
item (v) already relies on "the present generic Jensen formula". Nothing here is
a new inventory finding.

`sum_divisor_le` is a genuine multiplicity-weighted zero-count inequality on a
disc. It is blocked entirely on its `f_bound` hypothesis: instantiating it for ξ
requires a sup-norm bound for ξ on a circle, i.e. exactly barrier `S1-GROWTH`.
Nothing at the pin supplies it. Shape mismatch also: discs centred at `c`, not
the critical strip.

### 2.5 Product convergence machinery

| capability | pinned declaration |
|---|---|
| products over an arbitrary index type | `HasProd`, `Topology/Algebra/InfiniteSum/Defs.lean:106`; `Multipliable`, `:114` (both take a summation filter `L`, default `unconditional β`) |
| summation filters — **not currently in the capability map** | `SummationFilter`, `Topology/Algebra/InfiniteSum/SummationFilter.lean:32`; `SummationFilter.conditional`, `:216` (`atBot ×ˢ atTop` mapped to `Finset.Icc`) |
| **symmetric truncation, generic** — **not currently in the capability map** | `SummationFilter.symmetricIcc` / `symmetricIoo` / `symmetricIco` / `symmetricIoc`, `Topology/Algebra/InfiniteSum/ConditionalInt.lean:40` / `:47` / `:53` / `:59`, with `NeBot`/`LeAtTop` instances `:64-:99` and `hasProd_symmetricIcc_iff` `:155`. Requires `[Neg G] [Preorder G] [LocallyFiniteOrder G]` on the **index type** — it truncates order-intervals `Icc (-N) N`, not a subset of ℂ by `\|ρ\| ≤ T`. Closes nothing here; recorded so the barrier's "symmetric truncation" phrase is not read as "no generic API at all" |
| summable-log ⇒ multipliable | `Complex.multipliable_of_summable_log`, `SpecialFunctions/Log/Summable.lean:32`; `Real` analogue `:62` |
| `Σ f` summable ⇒ `Σ log(1+f)` summable | `Complex.summable_log_one_add_of_summable`, `:43` |
| `∏(1+f)` multipliable / nonzero | `:49`, `:169`, `:216` |
| locally uniform products | `hasProdLocallyUniformlyOn_one_add`, `Analysis/Normed/Module/MultipliableUniformlyOn.lean:130` |
| log-derivative of an infinite product | `logDeriv_tprod_eq_tsum`, `Analysis/Calculus/LogDerivUniformlyOn.lean:24` |
| finite-support Weierstrass extraction | `MeromorphicOn.extract_zeros_poles`, `Analysis/Meromorphic/FactorizedRational.lean:291` — hypothesis `(divisor f U).support.Finite`, uses `∏ᶠ` |
| single normalized Blaschke-type factor for a disc of radius `R` (not a finite Blaschke *product*) | `canonicalFactor`, `Analysis/Complex/CanonicalDecomposition.lean:50` — `fun z ↦ (R ^ 2 - conj w * z) / (R * (z - w))` |
| worked order-one precedent, `Tendsto` form | `Complex.tendsto_euler_sin_prod`, `SpecialFunctions/Trigonometric/EulerSineProd.lean:269` — a `Tendsto` over `Finset.range n` partial products (the `±` pair already combined into `1 - z²/(j+1)²`), proved by a sine-specific Wallis recursion |
| worked order-one precedent, **`Multipliable`/`tprod`/locally-uniform form — already exists at the pin** | `SpecialFunctions/Trigonometric/Cotangent.lean`: `multipliable_sineTerm` `:94`, `euler_sineTerm_tprod` `:99` (`∏' i, (1 + sineTerm x i) = sin(πx)/(πx)`), `multipliableUniformlyOn_euler_sin_prod_on_compact` `:118`, `HasProdUniformlyOn_sineTerm_prod_on_compact` `:125`, `HasProdLocallyUniformlyOn_euler_sin_prod` `:132`. Correction to an earlier draft of this note (Annex A-3) |
| Borel–Carathéodory | `Complex.borelCaratheodory`, `Analysis/Complex/BorelCaratheodory.lean:109` |

### 2.6 Repository side (already kernel-checked or CI-green)

`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean`:
`riemannXi` `:41`, `differentiable_riemannXi` `:46`, `riemannXi_one_sub` `:61`,
`riemannXi_zero` `:72`, `riemannXi_one` `:78`,
`riemannXi_eq_zero_iff_riemannZeta_eq_zero` `:120`,
`riemannXi_ne_zero_of_one_le_re` `:157`, `riemannXi_ne_zero_of_re_le_zero` `:180`,
`riemannXi_zero_mem_critical_strip` `:192`,
`analyticOrderAt_riemannXi_eq_riemannZeta` `:248`.
`Conj.lean` (CI-green, pending merge) supplies conjugation and the fourfold zero
action, `:282`, `:306`, `:317`, `:452`.

---

## 3. What is genuinely missing

Every entry below was confirmed by a tree-wide search of `Mathlib/` this
session. All the searches returned empty except where noted.

**Method correction (Annex A-5).** An earlier draft recorded these searches as
`rg -niE "…"`. In ripgrep `-E` is `--encoding`, not extended-regex, so each of
those invocations aborted with `error parsing flag -E: unknown encoding: …` and
returned nothing *because it never ran* — the same class of defect this note
records against scout 2 at §5.4 (`-r` = `--replace`). Every search below was
re-run this session with `rg -ni` / `rg -n`. **All substantive conclusions
survived; one evidence sentence did not, and is corrected in the residue row.**

### 3.1 Generic complex analysis — natural Mathlib upstreams, no ζ/ξ/RH content

| missing item | search evidence | note |
|---|---|---|
| argument principle | `rg -ni "argument.?principle" Mathlib/` → 0 hits | no `∮ f'/f` anywhere |
| winding number / index of a curve | `rg -ni "winding" Mathlib/` → 0 hits | |
| contour residue theorem | **corrected**: the `residue` hits under `Analysis/` are residue *classes* (`SumOverResidueClass.lean`, `PSeries.lean:434`), Γ-pole values (`Gamma/Deriv.lean:94`, `Gamma/Deligne.lean:95`), **and one genuine logarithmic-residue lemma** — `AnalyticAt.tendsto_mul_logDeriv_simple_zero`, `Analysis/Calculus/LogDeriv.lean:144` | the ABSENT verdict stands: that lemma is a `Tendsto` at a **simple** zero, with no contour integral, no multiplicity, and no counting consequence |
| order (growth order) of an entire function | `rg -ni "order of (an? )?entire\|growth order\|orderOfGrowth\|exponential type" Mathlib/` → 0 hits | `Analytic/Order.lean` is *local vanishing order* in `ℕ∞` |
| genus | `rg -ni "\bgenus\b" Mathlib/` → 0 hits | |
| Weierstrass elementary factors `E_p` | `rg -ni "elementaryFactor\|primaryFactor" Mathlib/` → 0 hits | |
| canonical / Hadamard product, Weierstrass product theorem | `rg -ni "canonical.?product\|hadamard.?factor\|weierstrass.?product" Mathlib/` → 1 hit, `CategoryTheory/Limits/Sifted.lean:185`, unrelated. `Analysis/Complex/Hadamard.lean` is the **three-lines theorem** (`norm_le_interp_of_mem_verticalClosedStrip`) | |
| convergence exponent of a divisor; `order ⇒ Summable (‖ρ‖⁻¹ ^ s)` | none found | `sum_divisor_le` is the per-disc ingredient; dyadic-shell summation absent |
| unweighted `n(r) = #{ρ : |ρ| ≤ r}`, and `N(r) = ∫₀ʳ n(t)/t dt` | none found | the pinned counting function is log-weighted |
| countability of a locally finite support | no `Countable` result in `Topology/LocallyFinsupp.lean` — **but this is a one-liner at the pin, not upstream work** (Annex A-7): `isDiscrete_iff_discreteTopology` (`Topology/Constructions.lean:265`) + `SecondCountableTopology.toHereditarilyLindelof` (`Topology/Compactness/Lindelof.lean:738`) + `HereditarilyLindelofSpace.isLindelof` (`:723`) + `IsLindelof.countable_of_isDiscrete` (`:655`) | not blocking either way: `tsum`/`tprod` accept arbitrary index types |
| enumeration / ordering of a zero set | no `ρ : ℕ → ℂ`, no index type, no canonical `Finset` | see §5 disagreement |
| symmetric-truncation / conditional-convergence API **instantiated at a zero set** | **locator corrected**: the generic API is `SummationFilter` (`Topology/Algebra/InfiniteSum/SummationFilter.lean:32`), `SummationFilter.conditional` (`:216`), and the `symmetricIcc`/`Ioo`/`Ico`/`Ioc` family (`InfiniteSum/ConditionalInt.lean:40,47,53,59`) — see §2.5, **not** `InfiniteSum/Defs.lean:106`, which is `def HasProd` | the gap is real but narrower than the earlier phrasing: nothing instantiates a `\|ρ\| ≤ T` or `\|Im ρ\| < T` cutoff, and the pinned filters truncate an ordered `LocallyFiniteOrder` **index type**, which a subset of ℂ is not without an enumeration |
| `Nat.card`/`ncard` applied to any zero set | `rg "ncard\|Nat.card"` over `Analysis/Complex/`, `Analysis/Meromorphic/` → 1 hit, `Polynomial/Basic.lean:147`, unrelated | `ncard` itself is total and needs no proof |

### 3.2 Zeta-specific — cannot be pushed upstream, must be built here

| missing item | note |
|---|---|
| any growth or order-one bound for ξ | barrier `S1-GROWTH`, entirely absent at the pin; `rg "zero.free\|zeroFree"` → 0 hits, so the strongest pinned zero-location facts remain `riemannZeta_ne_zero_of_one_le_re` (`Nonvanishing.lean:410`) and `_of_one_lt_re` (`Dirichlet.lean:326`) |
| identification of `divisor riemannXi Set.univ` with the nontrivial ζ zeros | adjacent to in-flight `S1-MULTIPLICITY`; that contract explicitly disclaims touching this barrier (`MULTIPLICITY_CONTRACT.md:26`) |
| multiplicity-aware ξ zero-set topology at the repo layer | repo `DEFERRED-2` (`MULTIPLICITY_CONTRACT.md:1507-1516`) |
| choice and freezing of a truncation convention | route-selecting; see §4 |
| `N_ξ(T) ≤ C·T·log T` | `SC-XI-01`(2); downstream of `S1-GROWTH` |
| the `exp(A_ξ s)` factor and its arithmetic identification | `SC-XI-01`(5) |
| multiplicity convention reconciliation | `divisor` is ℤ-valued (`Divisor.lean:39`), `analyticOrderAt` is `ℕ∞`-valued (`Analytic/Order.lean:47`); overlaps `S1-MULTIPLICITY` — coordinate, do not duplicate |

---

## 4. Repo-side demand analysis

Which contract rows consume which clause of the exit string, and for which
route. Row identifiers are `SOURCE_CONTRACTS.md` `SC-*` IDs and
`ROUTE_TRIAGE.md` Route C items (i)–(vii).

### 4.1 Truncation conventions — two, incompatible, route-indexed

| convention | contract text | consuming rows | route |
|---|---|---|---|
| radial `\|ρ\| ≤ T` | `SC-LI-02`: `lambda_n(T) = sum_{rho in S_xi, \|rho\| <= T} m(rho)*(1-(1-1/rho)^n)`, `lambda_n = lim_{T->infinity} lambda_n(T)` | `SC-XI-01`(2),(3); `SC-LI-01`; `SC-LI-03`; `SC-BRIDGE-01`; `SC-BRIDGE-04` (spectral cutoff) | **A only** |
| strict height `\|Im ρ\| < T` | `SC-BOMB-02`: `lim_{T->infinity} sum_{rho nontrivial, \|im(rho)\| < T} m(rho)*Mellin(f)(rho)`, "cutoff: strict imaginary-height cutoff" | `SC-BOMB-02`; triage Route C item (vii) | **C**, and A-via-C |
| conversion | `SC-BRIDGE-02`: "A formal bridge must prove equality of the resulting limits for the admitted test function. **Sharing the symbol `T` is not a proof.**" | any A-consumes-C composition | A+C |
| boundary insensitivity | `SC-LI-02`: formal definition should use `<= T` and prove boundary-insensitivity | `SC-LI-02` | A |
| one common regularization parameter | `SC-BRIDGE-04`: one `T`; endpoint and finite-prime contributions combined before the limit | `SC-BRIDGE-04`, `SC-WEIL-02` | A |

Enforced negatively by `SOURCE_CONTRACTS.md` §Anti-circularity rejection matrix
("replace a star-limit by `tsum` — reject"; "change `|rho| <= T` to
`|im(rho)| < T` without proof — reject"; "erase multiplicity — reject") and by
the semantic mismatch register rows "sum over zeros" and "conditionally
convergent Li star-sum" (`MATHLIB_CAPABILITY_MAP.md:401-402`).

### 4.2 Convergence obligations

| obligation | contract | route |
|---|---|---|
| weighted summability `Σ m(ρ)·re(ρ)/(1+\|ρ\|)² < ∞` (LAG07 (1.6)) | `SC-LI-01` — recorded there as a **hypothesis of the general criterion, not a proved fact**; "nonnegativity alone does not prove convergence" | A only |
| star convergence of `Σ' m(ρ)/ρ` | `SC-LI-01`, `SC-XI-01`(3) | A only |
| absolute convergence of `Σ m(ρ)ρ^(-j)`, `j ≥ 2` | `SC-LI-01` | A only |
| convergence of `Σ m(ρ)/\|ρ\|²` | `SC-XI-01`(3) | A only |
| locally uniform genus-one product convergence | `SC-XI-01`(4) | A, C |
| `A_ξ = ξ'(0)/ξ(0) = −starSum m(ρ)/ρ`, identified not absorbed | `SC-XI-01`(5), `SC-LI-03` | A |
| **absolute convergence of the Weil combination** `<F,G>_W = Σ m(ρ)F(ρ)J(G)(ρ)` | `SC-WEIL-01` ("The combined sum is absolutely convergent") → `SC-WEIL-02` | **A only** |
| existence of the combined finite-`T` regularized limit | `SC-BRIDGE-04` obligations 1–3 | A only |
| *derivation, not assumption* | `ROUTE_TRIAGE.md` Route A preregistration: BL (1.6) summability and star convergence "must be derived from a proved counting theorem, never assumed" | A |

### 4.3 Counting asymptotic

Exactly one statement in the whole contract package: `SC-XI-01`(2) — a
multiplicity-aware `N_xi(T) = sum_{rho in S_xi, |rho| <= T} m(rho)` with
`N_xi(T) <= C*T*log T` for `T >= T0 >= 2`, "derived from the source asymptotic
rather than admitted as a new hypothesis". Its Route C mirror is triage item
(v). `SC-XI-01` closes with: "`analyticOrderAt` is a local zero-order API; it is
not an entire-growth theorem." Both `SC-XI-01`(1) and triage item (iv)
("vertical growth of zeta/xi in strips (missing, serious; only real Stirling
exists)") sit upstream of it — i.e. upstream is `S1-GROWTH`.

### 4.4 Route B's *formal obligations* consume nothing from this barrier — its *bar* does

**Corrected (Annex A-4); an earlier draft of this note said "Route B consumes
nothing from this barrier", which was too strong in the convenient direction.**

The accurate split:

- **`SC-NB-01` … `SC-NB-06` contain no sum over zeros, no cutoff, no counting
  function, no divisor.** Re-read in full this session and confirmed. This
  matches the map's own DAG scoping (`MATHLIB_CAPABILITY_MAP.md:41-43` — "shared
  infrastructure for the Li/Weil and explicit-formula routes, but are not
  prerequisites for Nyman-Beurling" — and `:242`, "the xi/divisor package is
  shared by Routes A and C only"). `SC-NB-05`'s zero-free region is
  `RH-DEPENDENT` and is not a zero-sum.
- **Route B's preregistration block does consume a multiplicity-weighted sum
  over zeros.** `ROUTE_TRIAGE.md` "Preregistration binding any future pilot"
  fixes the admissible target window as `B(N) = C/log N + o(1/log N)` with
  `C ≥ Σ_{Re ρ = 1/2} m(ρ)²/|ρ|²`, and the obstruction paragraph states Burnol's
  bound `liminf_{N→∞} d_N² log N ≥ Σ_{Re ρ = 1/2} m(ρ)²/|ρ|²` "with zeros counted
  through their multiplicities". That object is a multiplicity-weighted zero sum
  whose convergence is `SC-XI-01`(3)-adjacent — i.e. squarely inside this
  barrier.

The practical consequence is small and should not be inflated: the Route B bar
is recorded by the triage as "logically equivalent in strength to RH" and is not
a formalization target. But it is **false** to say the barrier has no Route B
consumer, and this note does not say so.

### 4.5 Where the demands hit the route bars

- **Route A bar** ("a proved chain to `Re λ_n` for unbounded `n`"): `Re λ_n` is
  undefined without `SC-LI-02`'s star limit, which needs `SC-LI-01`, which the
  triage requires be derived from `SC-XI-01`(2). The Gram route additionally
  needs `SC-WEIL-01`'s absolute convergence. **Every clause of the exit string
  except "finite divisor sums" is load-bearing for Route A's bar and for
  nothing else in-repo.**
- **Route C bar**: consumes `SC-BOMB-02`'s `|Im ρ| < T` limit with multiplicity
  (item (vii)), item (v)'s `N(T) ≪ T log T`, and `SC-BRIDGE-02` whenever a
  `|ρ| ≤ T` object enters.
- **Route B bar**: consumes no `SC-NB-*` `FORMAL-OBLIGATION` of this barrier, but
  its preregistered admissible window is stated in terms of
  `Σ_{Re ρ = 1/2} m(ρ)²/|ρ|²` — a multiplicity-weighted zero sum. See §4.4 as
  corrected.

---

## 5. Where the scouts disagreed, and where evidence is thin

Recorded plainly, because two of these are substantive.

1. **"The row's 'counting API' clause is inaccurate / out of date."** Scouts 1
   and 2 both concluded this and recommended amending the row. Scout 3 objected
   on governance grounds, citing `MULTIPLICITY_CONTRACT.md` finding A4 and death
   condition 9: rows are scoped to this repository's ζ/ξ layer, and generic
   pinned machinery lowers cost without retiring a row. **This note sides with
   scout 3 on the governance point and with scouts 1–2 on the factual point.**
   Both are true and they do not conflict: the pin does have a counting API, the
   capability map does not record it, the row stays open, and the correct output
   is a *proposed inventory amendment* for the maintainer, not a row closure.
   Nothing here amends any file other than this note.

2. **"Global enumeration exists via `divisor f Set.univ`."** Scout 2 asserted
   this; scouts 1 and 3 did not. `divisor f Set.univ` is a
   multiplicity-carrying, locally finite *divisor object*. It supplies no index
   type, no ordering, no sequence, and no `Finset`. Calling it an "enumeration"
   is loose usage that would, if copied into the map, understate the gap. This
   note treats "global enumeration" as **still absent**, and records instead
   that the pin supplies a global *multiplicity-carrying zero object* — which is
   a different and weaker claim.

3. **Line numbers.** Scout 1's `LogCounting` locators (`:95`, `:268`, `:153`,
   `:159`, `:194`, `:216`, `:231`, `:240`) are consistently 1–5 lines early;
   they anchor on doc-comment openers. Verified declaration lines are `:96`,
   `:272`, `:154`, `:160`, `:199`, `:217`, `:235`, `:244`. Scout 2's
   `canonicalFactor` locator `:51` is `:50`. Also, `logCounting_even` and
   `logCounting_nonneg` each exist **twice** in the same file, in the
   `Function.locallyFinsuppWithin` namespace (`:154`, `:217`) and in the
   `ValueDistribution` namespace (`:347`, `:363`); the scouts cited different
   ones without saying so. Any future map amendment must carry the namespace.

4. **Scout 2 flagged its own method.** Several of its early ripgrep invocations
   used `-r`, which ripgrep parses as `--replace`, corrupting that output. Its
   signatures were re-read afterwards. All locators it kept were independently
   re-verified here.

5. **Thin evidence — the "finiteness in a rectangle is provable today" claim.**
   Scout 1 gave two paper routes to `(rect ∩ {z | riemannXi z = 0}).Finite`,
   mirroring `ZetaZeros.lean:64`. The ingredients all exist and the chain reads
   correctly on paper (`differentiable_riemannXi` → `analyticOnNhd_univ_iff_differentiable`
   → `preimage_zero_mem_codiscrete` with the `riemannXi_zero` witness →
   `compl_mem_codiscrete_iff` → `IsCompact.finite`, with `IsCompact.reProdIm`
   for the rectangle). **This has not been kernel-checked** — no toolchain here —
   and it should be treated as an estimate, not a result. Scout 1's own two
   caveats are worth carrying forward: the statement has **no existence
   content** (`Set.Finite` is vacuously true of `∅`; nothing at the pin or in
   this repo proves ξ has any zero anywhere), and the Weil-shaped strip
   `|Im ρ| < T` is not compact — it is only reducible to a compact rectangle
   *via* the repo's own `riemannXi_ne_zero_of_one_le_re` (`Xi.lean:157`),
   `riemannXi_ne_zero_of_re_le_zero` (`:180`) and
   `riemannXi_zero_mem_critical_strip` (`:192`).

6. **Wording risk already in the repo.** `MULTIPLICITY_CONTRACT.md:1427`
   ("**No counting.** No `N(T)`, no `|ρ| ≤ T` truncation, no zero-density, no
   `logCounting`") and `:1599` ("**No counting function.** …", same body) both
   deny a counting function. In context these are scope disclaimers for that contract and they correctly
   forward such statements to `S1-GLOBAL-ZEROS`. But the phrasing can be misread
   as "Mathlib has no `logCounting`", which is false. Worth a clarifying edit if
   that file is reopened — a prose fix, not a scope change.

---

## 6. Cost estimate per missing item

Units follow the earlier barriers: **statement count** (the `X1–X11`,
`Z1–Z9`, `M1–M17` convention) and **whether all ingredients are pinned**. These
are source-reading estimates; no Lean was run.

**Scope boundary for this table (Annex A-9/A-10).** Rows tagged `S1-GROWTH`,
`SC-BOMB-02`, `SC-BRIDGE-02` and `SC-BRIDGE-04` are listed here **as blockers
of, or immediate neighbours of, this barrier — not as items claimed under
`S1-GLOBAL-ZEROS`**. `S1-GROWTH` owns every ξ growth bound. `S1-EXPLICIT` owns
the explicit formula's "exact test class, transform convention, residues, and
limiting procedure": in particular `SC-BRIDGE-04`'s *local* cutoff
(`x = 1/T`, `x = T`) and its requirement that endpoint and finite-prime
contributions be combined before the limit are `S1-EXPLICIT` content. Only the
**spectral** cutoff `|ρ| ≤ T` and the zero-sum limits belong to this row, per
the exit string at `MATHLIB_CAPABILITY_MAP.md:387`.

| item | statements | all ingredients pinned? | blocked on |
|---|---|---|---|
| ξ zero-set discreteness / closedness / compact-finiteness **/ countability** (repo `DEFERRED-2` in full) | ~4–6 | **yes** (`.discreteSupport` `:218`, `.closedSupport` `:237`, `.finiteSupport` `:254`, ζ template at `ZetaZeros.lean:57,60,64`; countability via `isDiscrete_iff_discreteTopology` `Constructions.lean:265` + `IsLindelof.countable_of_isDiscrete` `Lindelof.lean:655`) | `S1-MULTIPLICITY` M13 landing |
| finite divisor sums over an arbitrary compact truncation set `K` | ~2–3 | **yes** (`finiteSupport`, `divisor_support_finite_of_subset` `:91`, `IsCompact.reProdIm` `:706`) | same; and must be stated parameterized by `K` |
| well-definedness of `∑ᶠ ρ, divisor ξ K ρ • w ρ` for a compact `K` | ~1–2 | **yes** | the previous row; alone it is a restatement, see §7 |
| definition: order (growth order) of an entire function | ~1 def + ~6–10 API | **yes, but softer than the other `yes` rows** — `limsup` and `log` are present; there is **no named sup-norm-on-a-sphere API** at the pin, so the sup must be assembled from `IsCompact.exists_isMaxOn` (`Topology/Order/Compact.lean:246`) or `sSup` by hand | nothing — but it is a *definition*, and the API around it is the work |
| definition: Weierstrass elementary factors `E_p` + the `‖1 − E_p(z)‖ ≤ ‖z‖^(p+1)` estimate | ~1 def + ~3–5 | **yes** | nothing |
| convergence exponent: `order ⇒ Summable (‖ρ‖⁻¹ ^ (1+ε))` over `divisor f univ` | ~5–10 | **partly** — the hard analytic core is already proved as `sum_divisor_le` (`JensenFormula.lean:389`); missing is dyadic-shell summation, Abel bookkeeping, and a countability/enumeration convenience layer | the order definition above |
| unweighted `n(r)` and the Stieltjes relation `N(r) = ∫₀ʳ n(t)/t dt` | ~4–8 | **no** — no unweighted disc count exists | the counting definitions |
| general Weierstrass product theorem | large | **no** | elementary factors + convergence exponent |
| Hadamard factorization for finite-order entire functions | large | **no** (`Complex.borelCaratheodory`, `BorelCaratheodory.lean:109`, helps with the `exp(polynomial)` half) | all of the above |
| argument principle / winding number / contour residue theorem | large | **no** — nothing at the pin | a genuinely new upstream development |
| any ξ sup-norm bound on circles or vertical lines (`S1-GROWTH`) | unknown | **no** | nothing exists; no contract, no draft, no accepted statement surface |
| `N_ξ(T) ≤ C·T·log T` (`SC-XI-01`(2)) | ~2–4 once its inputs exist | **no** | `S1-GROWTH` **and** the counting definitions |
| `SC-LI-01` summability / star convergence | ~4–8 | **no** | `SC-XI-01`(2), i.e. `S1-GROWTH` |
| genus-one canonical product + `A_ξ` (`SC-XI-01`(4),(5)) | large | **no** | Hadamard + `S1-GROWTH` |
| `SC-WEIL-01` absolute convergence of the Weil combination | ~3–6 | **no** | `SC-LI-01` chain |
| `SC-BOMB-02` `\|Im ρ\| < T` limit with multiplicity | large | **no** | `S1-GROWTH`, contour shift; triage rates it "large" and `SC-BOMB-03` "a genuine blocker" |
| `SC-BRIDGE-02` cutoff conversion | ~2–4 | **no** | meaningless until *both* conventions are instantiated |

For calibration: `ROUTE_TRIAGE.md` Route C estimates the whole explicit-formula
chain at "plausibly 10k-30k lines of new Lean", "of which only (i)-(iii) are
cheap". Everything in the lower two thirds of this table sits inside that
estimate.

---

## 7. Misallocation warning

The following items have **no consumer other than a parked route**. Building any
of them first would spend budget on a route that `ROUTE_TRIAGE.md` explicitly
did not select, and in most cases is additionally blocked. The §6 scope-boundary
paragraph applies here too: `S1-GROWTH` and `S1-EXPLICIT` rows appear as
blockers, not as items claimed under this barrier.

| item | row(s) | sole consumer(s) | why flagged |
|---|---|---|---|
| `N_ξ(T) ≤ C·T·log T` | `SC-XI-01`(2); triage item (v) | Routes A and C — both `PARK` | also **not next-buildable**: downstream of `SC-XI-01`(1) and triage item (iv), i.e. of `S1-GROWTH`, which has no contract and no draft here |
| weighted summability (LAG07 (1.6)) | `SC-LI-01` | **Route A only** | triage preregistration forbids assuming it; must come from a proved counting theorem |
| star convergence of `Σ' m(ρ)/ρ`; `Σ m(ρ)/\|ρ\|²`; absolute convergence for `j ≥ 2` | `SC-LI-01`, `SC-XI-01`(3) | **Route A only** | same chain |
| genus-one canonical product; `A_ξ` identification | `SC-XI-01`(4),(5) | Routes A and C — both `PARK` | blocked: no Hadamard factorization and no definition of entire order at the pin (§3.1) |
| **absolute convergence of the Weil scalar-product combination** | `SC-WEIL-01` → `SC-WEIL-02` | **Route A only** | hardest flag: its only function is to make `‖G_n‖²_W = 2 Re λ_n` well-posed, and the triage records that `LAG07` Thm 3.1 is "an unconditional identity between two quantities neither of which is unconditionally bounded below" |
| existence of the `\|ρ\| ≤ T` limit with multiplicity | `SC-LI-02`, `SC-BRIDGE-01`, `SC-BRIDGE-04` | **Route A only** | convention-selecting — building it *is* a partial route selection |
| existence of the `\|Im ρ\| < T` limit with multiplicity | `SC-BOMB-02`; triage item (vii) | Route C + Route A's dependency screen — both `PARK` | convention-selecting; `SC-BOMB-03` is "a genuine blocker" |
| cutoff conversion `\|ρ\| ≤ T` ↔ `\|Im ρ\| < T` | `SC-BRIDGE-02` | only where A consumes C — both `PARK` | strictly after two route-only items |
| combined finite-`T` regularized expression and its limit | `SC-BRIDGE-04` obligations 1–3 | **Route A only** | its stated downstream is `2·re(lambda_n)` and then the `RESEARCH-OBLIGATION` "prove a uniform arithmetic lower bound strong enough to give `re(lambda_n) >= 0`" — the RH-equivalent target itself |

**Structural consequence, stated plainly.** Only one clause of the exit string
at `MATHLIB_CAPABILITY_MAP.md:387` — "finite divisor sums" — is convention-free.
The other five name a route-frozen cutoff or a route-only convergence fact.
Closing this row therefore requires freezing one of two mutually
non-interchangeable truncation conventions, which is a route selection; the
triage selected zero routes. **`S1-GLOBAL-ZEROS` is therefore not a closable
next target in the current repository state.**

---

## 8. Recommendation — options, not a selection

Selection belongs to the maintainer and to the queue. Four options are laid out
with their honest costs; this note picks none of them.

**Option A — do nothing under this barrier now; finish `S1-MULTIPLICITY`
first.** `MULTIPLICITY_CONTRACT.md` is drafted but **awaiting independent
acceptance**, and its `[#306]` half is blocked on `Conj.lean` merging. Every
convention-free item under `S1-GLOBAL-ZEROS` sits strictly downstream of it
(specifically of M13). This is the option with the fewest ordering hazards.

**Option B — the narrow neutral slice (`N1`+`N2`), after `S1-MULTIPLICITY`
lands.** Two items, both unconditional, both cheap, neither convention-selecting:

- **N2** — multiplicity-aware ξ zero-set discreteness / closedness /
  compact-finiteness / countability. This is repo `DEFERRED-2`
  (`MULTIPLICITY_CONTRACT.md:1507-1515`, "it would also be the first step toward
  `S1-GLOBAL-ZEROS`"). **Correction (Annex A-7):** an earlier draft called this
  "`DEFERRED-2` verbatim" while silently dropping `DEFERRED-2`'s fourth item,
  *countability* — the one sub-item this note's own §3.1 lists as absent from
  `Topology/LocallyFinsupp.lean`. It is restored here, and it is cheap: see the
  §6 row. N2 mirrors what the pin already gives for ζ without multiplicity.
  ~4–6 statements, all ingredients pinned.
- **N1** — finite divisor sums over an **arbitrary compact truncation set**.
  ~2–3 statements, all ingredients pinned. This is the only convention-free
  clause of the exit string, and it retires the "sum over zeros" and
  "multiset/divisor of zeros" entries of the semantic mismatch register
  (`MATHLIB_CAPABILITY_MAP.md:400-401`), which is barrier-*removal* under
  `corpus.md`'s rule that "equivalent restatements are not progress unless they
  remove a named barrier".

  **Neutrality condition, non-negotiable:** the statement must be parameterized
  by the truncation set (arbitrary compact `K`, or arbitrary `U` with
  `IsCompact U`). Hard-wiring `|ρ| ≤ T` silently selects Route A's `SC-LI-02`
  convention; hard-wiring `|Im ρ| < T` selects Route C's `SC-BOMB-02`
  convention. `SC-BRIDGE-02` is explicit that these are not interchangeable.

  **Honest caveat:** N1+N2 *advance* the row; they do not close it, and must not
  be reported as closing it. A companion item N3 (well-definedness of
  `∑ᶠ ρ, divisor ξ K ρ • w ρ`) is a pure restatement without N1 and earns its
  place only as the statement form N1's theorem inhabits.

**Option C — generic upstream complex analysis, offered to Mathlib rather than
built here.** The bulk of this barrier's missing mass is route-neutral,
RH-free, and would be reviewable on its own merits inside the Kebekus/Loeffler
value-distribution development already at the pin: order of an entire function;
Weierstrass elementary factors `E_p`; convergence exponent of a divisor
(`order ⇒ Summable (‖ρ‖⁻¹^s)`, whose hard core `sum_divisor_le` is already
proved); Weierstrass/Hadamard factorization in general form. None of these
mentions ζ, ξ, or RH. This is the largest genuinely neutral pool, but it is
upstream work with a long review latency and it is not a repository barrier
item.

**Two items were removed from this list (Annex A-3, A-7), because the pin
already has them:**

- a `Multipliable`/`tprod`/locally-uniform Euler sine product — already
  `Cotangent.lean:94,99,118,125,132`;
- countability of a locally finite support — already a one-liner from
  `Constructions.lean:265` + `Lindelof.lean:655,723,738`.

Proposing already-pinned work as an upstream contribution overstates the
remaining mass of this barrier's neutral pool, and is corrected here.

**Option D — treat `S1-GROWTH` as the real gate.** The honest reading of §4 and
§7 is that `S1-GROWTH` is the unstarted barrier that actually blocks Routes A
and C, that it is a strict prerequisite for the quantitative half of
`S1-GLOBAL-ZEROS` (via `sum_divisor_le`'s `f_bound` hypothesis), and that it has
no contract, no draft, and no accepted statement surface here. If the program
wants the next *substantive* foundation item rather than the next *cheap* one, a
reconnaissance note on `S1-GROWTH` — not a contract — is the item that would
change what is known.

**Proposed capability-map amendments** (recon output; **not applied**, and none
of them retires a row):

1. Add `GENERIC` inventory rows for the Nevanlinna layer:
   `Function.locallyFinsuppWithin.logCounting` (`LogCounting/Basic.lean:96`),
   `ValueDistribution.logCounting` (`:272`), `toClosedBall` (`:57`),
   `ValueDistribution.characteristic` (`CharacteristicFunction.lean:53`),
   `logCounting_isBigO_one_iff_analyticOnNhd` (`LogCounting/Asymptotic.lean:108`),
   each with the gap "disc-shaped, logarithmically weighted, no ζ/ξ instance, no
   unweighted `n(r)`".
2. Add a semantic-mismatch-register row: **`logCounting` is not `N_ξ(T)`** —
   log-weighted and radial vs. `SC-XI-01`(2)'s unweighted `Σ_{|ρ| ≤ T} m(ρ)`;
   and radial, hence serving no part of the Weil `|Im ρ| < T` contract.
3. Add `PRESENT`/`GENERIC` rows for `Function.locallyFinsuppWithin.finiteSupport`
   (`Topology/LocallyFinsupp.lean:254`) and `MeromorphicOn.extract_zeros_poles`
   (`FactorizedRational.lean:291`, finite-support-gated).
3b. Add a `GENERIC` row for the summation-filter layer: `SummationFilter`
   (`InfiniteSum/SummationFilter.lean:32`), `SummationFilter.conditional`
   (`:216`), and `symmetricIcc`/`Ioo`/`Ico`/`Ioc`
   (`InfiniteSum/ConditionalInt.lean:40,47,53,59`), with the gap "truncates an
   ordered `LocallyFiniteOrder` index type, not a subset of ℂ by `|ρ| ≤ T` or
   `|Im ρ| < T`; no ζ/ξ instance". Without this row the barrier phrase
   "symmetric truncation" reads as "no generic API exists", which is false.
4. Record the §3.1 `ABSENT` findings individually with their searches —
   argument principle, winding number, contour residue theorem, Hadamard/
   Weierstrass product, order of an entire function, genus, zero-free regions
   beyond `Re ≥ 1`. These are currently implied by the severity table but not
   individually evidenced.
5. Note in the `S1-GLOBAL-ZEROS` row that `S1-GROWTH` is a strict prerequisite
   for its quantitative half, and that only "finite divisor sums" among its exit
   clauses is convention-free.

Whether to apply any of these is a maintainer decision on the map file. No route
is unparked, no revival bar is claimed met, no barrier is declared closed or
stale, and no statement in this note bears on the truth of the Riemann
Hypothesis.

---

## Annex — adversarial review, 2026-08-07

Independent adversarial review of this note against the pinned tree
(`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD` =
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, re-verified) and against
`MATHLIB_CAPABILITY_MAP.md`, `ROUTE_TRIAGE.md`, `SOURCE_CONTRACTS.md`,
`MULTIPLICITY_CONTRACT.md`, `Xi.lean`, `Conj.lean`. Every locator in §2, §3 and
§5 was re-grepped. Source reading only; **no Lean toolchain, nothing below is
kernel-checked**. Fixes applied in place; the review changed no verdict of the
note and retired no barrier.

| id | severity | finding | disposition |
|---|---|---|---|
| **A-1** | MEDIUM-HIGH | §1(1) claimed "None of this is currently recorded in `MATHLIB_CAPABILITY_MAP.md`" for five items. False for three: `MeromorphicOn.divisor` is map row 132; `MeromorphicOn.circleAverage_log_norm` **and** `AnalyticOnNhd.sum_divisor_le` are map row 133 ("Jensen formula and divisor bound", gap "no zeta/xi growth input"); the summary at map `:35` names "meromorphic divisor, … Jensen". This inflated the note's own novelty | **FIXED** — §1(1) rewritten to claim only the Nevanlinna layer and the §2.5 summation filters; §2.2 and §2.4 now say "already at map row 132 / 133". §8 amendment 1 was already correctly scoped and is unchanged |
| **A-2** | MEDIUM | §3.1 mis-located the conditional-summation API as `InfiniteSum/Defs.lean:106` (that is `def HasProd`), and missed the pin's dedicated **symmetric-truncation** family entirely: `SummationFilter.symmetricIcc`/`Ioo`/`Ico`/`Ioc`, `InfiniteSum/ConditionalInt.lean:40,47,53,59`, plus `SummationFilter` `:32` and `conditional` `:216` in `SummationFilter.lean`. This is the pinned API closest to the barrier's own phrase "symmetric truncation" | **FIXED** — new §2.5 rows, §3.1 row rewritten, map amendment 3b added. **Closes nothing**: these filters truncate an ordered `LocallyFiniteOrder` *index type*; a subset of ℂ cut by `\|ρ\| ≤ T` is not one without an enumeration, which §5(2) records as still absent |
| **A-3** | MEDIUM | §2.5 and §8 Option C asserted that `Complex.tendsto_euler_sin_prod` is not available in `Multipliable`/`tprod` form and offered a restatement as upstream work. The pin already has it: `Cotangent.lean` `multipliable_sineTerm` `:94`, `euler_sineTerm_tprod` `:99`, `multipliableUniformlyOn_euler_sin_prod_on_compact` `:118`, `HasProdUniformlyOn_sineTerm_prod_on_compact` `:125`, `HasProdLocallyUniformlyOn_euler_sin_prod` `:132` | **FIXED** — §2.5 row split into `Tendsto` form and the existing `Multipliable` form; the item removed from Option C |
| **A-4** | MEDIUM | Softening in a convenient direction. §4.4's heading and §4.5's bullet said Route B "consumes nothing from this barrier", contradicting §4.4's own sentence. `ROUTE_TRIAGE.md`'s Route B **preregistration** fixes the admissible window as `B(N) = C/log N + o(1/log N)` with `C ≥ Σ_{Re ρ = 1/2} m(ρ)²/\|ρ\|²`, and its obstruction paragraph states Burnol's bound "with zeros counted through their multiplicities" — a multiplicity-weighted zero sum, i.e. inside this barrier. Understating this made the barrier look purely Route-A/C, which happens to support §7 and Option D | **FIXED** — §4.4 rewritten as an explicit split (`SC-NB-*` obligations: no consumption; Route B bar: yes), §4.5 bullet corrected. The practical consequence is explicitly not inflated: the triage records the Route B bar as "logically equivalent in strength to RH" |
| **A-5** | LOW-MEDIUM | §3.1's "search evidence" column quoted commands of the form `rg -niE "…"`. In ripgrep `-E` is `--encoding`; every such command aborts with `error parsing flag -E: unknown encoding: …` and returns nothing *because it never ran*. Same defect class the note records against scout 2 at §5.4 | **FIXED** — all searches re-run with `rg -ni`; commands corrected in the table; a method-correction paragraph added. **All substantive ABSENT verdicts survived** (argument principle, winding, genus, elementary factors, entire order / exponential type: 0 hits; canonical/Hadamard/Weierstrass product: 1 unrelated hit, `CategoryTheory/Limits/Sifted.lean:185`) |
| **A-6** | LOW-MEDIUM | §3.1's residue row claimed "every `residue` hit under `Analysis/` is a residue *class* or a Γ-pole value". False: `AnalyticAt.tendsto_mul_logDeriv_simple_zero`, `Analysis/Calculus/LogDeriv.lean:144`, is a genuine logarithmic-residue lemma | **FIXED** — row corrected. The ABSENT verdict stands: it is a `Tendsto` at a **simple** zero, with no contour integral, no multiplicity, no counting consequence |
| **A-7** | LOW-MEDIUM | Optimism plus an inaccurate quotation. §8 Option B called N2 "repo `DEFERRED-2` verbatim" while dropping `DEFERRED-2`'s fourth item, **countability** — the very sub-item §3.1 lists as absent — and §8 Option C then proposed countability as *upstream work*. In fact countability is a one-liner at the pin: `isDiscrete_iff_discreteTopology` (`Topology/Constructions.lean:265`) + `SecondCountableTopology.toHereditarilyLindelof` (`Lindelof.lean:738`) + `HereditarilyLindelofSpace.isLindelof` (`:723`) + `IsLindelof.countable_of_isDiscrete` (`:655`) | **FIXED** — countability restored to N2 and to the §6 row (estimate raised `~3–5` → `~4–6`), §3.1 row annotated, item removed from Option C |
| **A-8** | LOW | Wrong locators, in a note whose §5.3 makes locator precision its own finding: `mem_riemannZetaZeros` cited `:36`, actual `ZetaZeros.lean:35` (map row 112 already had `:35`); `Function.locallyFinsupp` cited `:60`, actual `Topology/LocallyFinsupp.lean:61`; "the file is 75 lines", actual 74; §4.4 cited `MATHLIB_CAPABILITY_MAP.md:44-45` for DAG scoping, which is `:41-43` (`:44-45` is the ledger/axiom-audit rule; `:242` was correct); §5.6 cited `MULTIPLICITY_CONTRACT.md:1428` for "No counting function", which is `:1599` — `:1427` reads "**No counting.**"; `DEFERRED-2` cited as `:1507-1516`, actual `:1507-1515` (`:1516` starts `DEFERRED-3`) | **FIXED** — all six corrected |
| **A-9** | LOW | Scope creep toward `S1-EXPLICIT`. §4.2 and §7 assigned `SC-BRIDGE-04` obligations 1–3 wholly to this barrier. `SC-BRIDGE-04` also fixes a *local* cutoff (`x = 1/T`, `x = T`) and requires endpoint and finite-prime contributions be combined before the limit — arithmetic-side regularization, which is `S1-EXPLICIT` exit evidence ("residues, and limiting procedure", map `:390`). Only the **spectral** cutoff `\|ρ\| ≤ T` is this row's, per the exit string at map `:387` | **FIXED** — scope-boundary paragraph added to §6 and referenced from §7. No rows deleted: the spectral half is genuinely this barrier's |
| **A-10** | LOW | Scope blur toward `S1-GROWTH`: §6 and §7 list `S1-GROWTH` items inside this barrier's tables. Disclosed by the row labels rather than concealed, but not stated | **FIXED** — same scope-boundary paragraph states that those rows are blockers, not items claimed under `S1-GLOBAL-ZEROS` |
| **A-11** | LOW | §6's "definition: order of an entire function — all ingredients pinned: **yes** (`limsup`, `log`, sup-norm on spheres all present)". No named sup-norm-on-a-sphere API exists at the pin; the sup must be assembled from `IsCompact.exists_isMaxOn` (`Topology/Order/Compact.lean:246`) | **FIXED** — the `yes` is retained but explicitly marked softer than the other `yes` rows, with the real ingredient named |
| **A-12** | LOW (cosmetic) | §2.5 called `canonicalFactor` (`CanonicalDecomposition.lean:50`) a "finite Blaschke factor". At the pin it is `fun z ↦ (R ^ 2 - conj w * z) / (R * (z - w))` — one normalized Blaschke-type factor for a disc of radius `R`, not a finite Blaschke product | **FIXED** — relabelled with the definition inline |

### Verified sound, no change

- **Every §2.2, §2.3, §2.4 and §2.6 locator re-grepped and exact** apart from
  A-8's two. Spot-confirmed: `divisor` `Divisor.lean:39`;
  `divisor_support_finite_of_subset` `:91`; `divisor_ball_support_finite` `:104`;
  `AnalyticOnNhd.divisor_nonneg` `:177`; `.discreteSupport/.closedSupport/.finiteSupport`
  `LocallyFinsupp.lean:218/237/254`; `restrict` `:584`, `restrictMonoidHom` `:625`,
  and **no `comap`/pullback anywhere in that file** (repo `DEFERRED-1` stands);
  `toClosedBall` `:57`, `toClosedBall_divisor` `:70`,
  `locallyFinsuppWithin.logCounting` `:96`, `ValueDistribution.logCounting` `:272`,
  and the whole `:131–:244` / `:347–:546` elementary theory; `characteristic`
  `CharacteristicFunction.lean:53`; FMT `:97,:109,:131,:160`;
  `logCounting_isBigO_one_iff_analyticOnNhd` `Asymptotic.lean:108`;
  `JensenFormula.lean:275,307,375,389`; `HasProd` `:106` / `Multipliable` `:114`;
  `Log/Summable.lean:32,43,49,62,169,216`; `Xi.lean` `41,46,61,72,78,120,157,180,192,248`;
  `Conj.lean` `282,306,317,452`. The two theorem statements quoted verbatim in
  §2.4 match the source.
- **§5.3's line-number corrections are themselves correct** — the
  `LogCounting` declaration lines really are `:96,:272,:154,:160,:199,:217,:235,:244`,
  `canonicalFactor` really is `:50`, and `logCounting_even` / `logCounting_nonneg`
  really do exist twice (`Function.locallyFinsuppWithin` `:154`/`:217`,
  `ValueDistribution` `:347`/`:363`).
- **Every `SC-*` quotation checked against `SOURCE_CONTRACTS.md` and found
  verbatim** — `SC-XI-01`(1)–(5) (`:170`), `SC-LI-01` (`:220`), `SC-LI-02`
  (`:251`), `SC-WEIL-01`/`-02` (`:340`/`:391`), `SC-BOMB-02` (`:443`),
  `SC-BRIDGE-01`/`-02`/`-04` (`:532`/`:569`/`:597`), the anti-circularity
  rejection matrix (`:845`), and `SC-NB-01…06` (`:628–:800`, re-read in full for
  A-4).
- **Every `ROUTE_TRIAGE.md` quotation checked** — three `PARK` dispositions, the
  Route A bar, Route C items (i)–(vii) including (iv) "missing, serious; only
  real Stirling exists" and (v), the "10k-30k lines … only (i)-(iii) are cheap"
  calibration, and `SC-BOMB-03` "a genuine blocker".
- **§3.1's core ABSENT findings all hold** under corrected searches, including
  the load-bearing one: **no unweighted `n(r)`**. The only `countingFunction`
  hits in the tree are `JensenFormula.lean:275` and its doc reference; the pinned
  counting function really is `∑ᶠ z, D.toClosedBall r z * log (r * ‖z‖⁻¹) + D 0 * log r`
  (`LogCounting/Basic.lean:96`) — radial and log-weighted. §1(2) and amendment 2
  are correct to refuse the substitution for `SC-XI-01`(2).
- **§5.5's two caveats hold.** No `Set.Finite` existence content: Mathlib proves
  trivial ζ zeros exist (`riemannZeta_neg_two_mul_nat_add_one`,
  `RiemannZeta.lean:171`) but `riemannXi_ne_zero_of_re_le_zero` (`Xi.lean:180`)
  excludes them, and nothing at the pin or in this repo proves any ξ zero exists
  anywhere. The paper chain to rectangle finiteness reads correctly and remains
  **an estimate, not a result**.
- **Governance.** §1(2) and §5(1) apply `MULTIPLICITY_CONTRACT.md` finding A4
  (`:1701`) and death condition 9 (`:1664`) faithfully. Re-read end to end for
  route selection, unparking, staleness or RH progress: **none found**, before or
  after these fixes. No row is retired; no file other than this note is amended.

### Unresolved concerns (not fixed)

1. **Nothing here is kernel-checked.** No Lean toolchain in this container. §5.5's
   rectangle-finiteness chain and every "all ingredients pinned = **yes**" in §6
   are source-reading estimates. A-11 shows at least one such `yes` was softer
   than its phrasing implied; the others were not individually stress-tested.
2. **The §6 statement counts are unvalidated.** They follow the `X`/`Z`/`M`
   convention by analogy only. The three "large" rows and the one "unknown" row
   (`S1-GROWTH`) carry no evidence beyond the triage's own 10k-30k figure.
3. **§7's "not a closable next target" is a structural reading, not a proof.** It
   rests on the claim that five of six exit clauses are convention-bound. That
   reading is well supported by `SC-BRIDGE-02` and the mismatch register, but it
   is an interpretation of the exit string at map `:387`, and the maintainer may
   read the string differently. §8 correctly leaves selection open.
4. **A-2's symmetric-truncation filters deserve a second look before any N1 is
   drafted.** They are the nearest pinned analogue to the barrier's own language,
   and the neutrality condition in Option B (parameterize by an arbitrary compact
   `K`) should be checked against them so that a future draft neither hard-wires
   a cutoff nor silently adopts an index-type order the zero set does not have.
5. **A-4's Route B consumption was found only by reading the triage's
   preregistration block.** Other bars and preregistration blocks in the program
   were not audited for zero-side objects in this pass; there may be further
   consumers of this barrier recorded outside `SC-*` `FORMAL-OBLIGATION`s.
