/-
Built circle-only argument-principle package: promotion of the independently
accepted W1, A1-A4 statement surface in
`domains/riemann-hypothesis/ARG_PRINCIPLE_CONTRACT.md` (acceptance record:
`notes/reviews/ARG_PRINCIPLE_ACCEPTANCE_2026_08_08.md`; promotion record:
`notes/reviews/ARG_PRINCIPLE_PROMOTION_2026_08_09.md`).

Five declarations. W1 evaluates the contour integral of `(z - w)⁻¹` over a
circle when `w` lies outside the closed disc, giving zero. A1 upgrades agreement
off a codiscrete set to agreement on a neighbourhood, at a point of
accumulation. A2 is the deliverable: for `f` analytic on a closed disc and
nonvanishing on its boundary circle, the contour integral of the logarithmic
derivative equals `2πi` times the divisor sum over the open disc — the argument
principle in the one form the pin supports without a winding-number theory. A3
is its vanishing criterion, and A4 records that the integral is `2πi` times a
natural number.

State: this package is GENERIC complex analysis over pinned Mathlib, with zero
repository prerequisites — it imports no repo module. It mentions no zeta
function, no xi, no `completedRiemannZeta₀`, no `LSeries`, no critical strip;
every statement quantifies over an arbitrary `f`. It closes NO barrier row of
`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` and no `S1-*` item.

`S1-GLOBAL-ZEROS` deserves an explicit sentence, since a divisor sum is the
closest any of this comes to a counting statement. That row asks for global
enumeration and counting FOR ζ OR ξ, with route-specific truncations among its
exit items. A2 sums the divisor of an arbitrary `f` over an arbitrary open disc,
names no particular function, and chooses no truncation family. The row is
therefore OPEN and untouched — not closed, not advanced, not partially closed —
and the same holds for every other barrier. The capability-map effect is
INVENTORY ONLY: generic machinery lowers the cost of a future exit and never
retires a row. This package proves, disproves, advances, and evidences nothing
about the Riemann Hypothesis in either direction, and selects no route.

`0 < R` IS LOAD-BEARING FOR TRUTH in A2, A3 and A4, not a convenience. At
`R = -1` the closed ball, the sphere and the open ball are all empty, so every
hypothesis is vacuous and the divisor sum is `0`, while the contour integral is
not: `∮ z in C(0,-1), 1/z = 2πi ≠ 0`. A4 fails too — with `f = z⁻¹` the integral
is `-2πi`, and `∃ n : ℕ` forbids a negative count. Each of the three statements
carries that refutation in its docstring. This is recorded here because the
acceptance record had judged A4's `0 < R` to be mere convenience, and an editor
under `RH-015` found the counterexample that shows otherwise.

Module placement: `ResearchOS/Analysis/`, deliberately NOT
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`. The surface is
domain-neutral, so filing it under the RH subtree would present generic
machinery as RH-lane content; these rows are `AP-*` rows of the domain-neutral
`analysis-generic` lane, the same shelf as the `MB-`, `PL-`, `HK-`, `TC-` and
`GO-` rows already there.

Kernel verdict: delivered by CI on this promotion change, never by this header.
`lake build` compiles the module, the no-incomplete-proof gate scans it, the
regenerated `ResearchOS/LedgerAxiomAudit.lean` + `check_axioms.py` enforce the
per-row `standard` axiom base, and `gen_researchos_registry.py --check` enforces
inverse coverage. If any gate is red, no row is counted.

Honest expectation, recorded before the verdict rather than after: the drafter
flagged A2 as ~330 lines of assembly with several higher-order unification
points and named it the declaration most likely to need a repair round. Its
inline `FALLBACK` notes are densest for that reason. A rejection there is an
ordinary round, not a surprise.

All five public declarations are ledgered as `AP-*` rows in
`VERIFIED_RESEARCHOS.md` and audited through the generated
`ResearchOS/LedgerAxiomAudit.lean` with axiom base `standard`.

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0).
-/
import Mathlib.MeasureTheory.Integral.CircleIntegral   -- ∮ (:385/:389), integral_congr :425,
                                                       -- integral_add :451, integral_fun_sum :461,
                                                       -- integral_const_mul :527,
                                                       -- integral_eq_zero_of_hasDerivWithinAt'
                                                       --   :538,
                                                       -- integral_sub_inv_of_mem_ball :699,
                                                       -- ContinuousOn.circleIntegrable :337
import Mathlib.Analysis.Complex.CauchyIntegral         -- DiffContOnCl.circleIntegral_eq_zero :459
import Mathlib.Analysis.Meromorphic.Divisor            -- MeromorphicOn.divisor :39, divisor_apply
                                                       -- :68/:71, ball finiteness :104,
                                                       -- divisor_nonneg :177
import Mathlib.Analysis.Meromorphic.FactorizedRational -- extract_zeros_poles :291, mulSupport :52,
                                                       -- analyticAt :81, ne_zero :94
import Mathlib.Analysis.Meromorphic.NormalForm         -- AnalyticOnNhd.meromorphicNFOn :567,
                                                       -- zero_set_eq_divisor_support :578
import Mathlib.Analysis.Analytic.IsolatedZeros         -- frequently_eq_iff_eventually_eq :141
import Mathlib.Analysis.Calculus.LogDeriv              -- logDeriv calculus :37/:54/:73/:87
import Mathlib.Analysis.SpecialFunctions.Complex.LogDeriv -- Complex.hasDerivAt_log :37 [W1 only]

open Complex Metric Filter Function
open scoped Real Topology

/-
Preamble carried VERBATIM from the contract (§Candidate fields, "Proposed module
preamble"); no import is added and none is removed. Its sufficiency was checked
mechanically this session by computing the PUBLIC-import closure of these eight
modules over the pinned tree (the module system at v4.31.0 re-exports only
`public import`, so plain `import` lines do NOT transit). Every further module
consumed below is inside that closure and therefore needs no extra import line:

  Analysis/Meromorphic/IsolatedZeros.lean  (A1's :99; a `public import` of
      FactorizedRational.lean:9)
  Analysis/Meromorphic/Basic.lean          (AnalyticAt.meromorphicAt :40,
                                            AnalyticOnNhd.meromorphicOn :475)
  Analysis/Meromorphic/Order.lean          (AnalyticAt.meromorphicOrderAt_eq :279)
  Analysis/Analytic/Order.lean             (:133, :624)
  Analysis/Analytic/Constructions.lean     (AnalyticAt.mul :639 / .div :992 / .zpow :929,
                                            each with `@[to_fun]`, hence the `fun_*` twins)
  Analysis/Calculus/FDeriv/Analytic.lean   (:126, :176, :441, :457)
  Analysis/Calculus/DiffContOnCl.lean      (DifferentiableOn.diffContOnCl_ball :127)
  Analysis/Normed/Module/RCLike/Real.lean  (closure_ball :59, NormedSpace.sphere_nonempty :128)
  Analysis/Normed/Module/Convex.lean       (convex_closedBall :71)
  Analysis/Convex/PathConnected.lean       (Convex.isPreconnected :93)
  Analysis/Normed/Module/FiniteDimension.lean (the `ProperSpace ℂ` instance that
                                            isCompact_closedBall and :104 need)
  Analysis/Complex/Basic.lean              (slitPlane :634, mem_slitPlane_of_norm_lt_one :689)
  Analysis/SpecialFunctions/Complex/Log.lean (Complex.two_pi_I_ne_zero :139)
  Topology/LocallyFinsupp.lean             (support :138, supportWithinDomain :140,
                                            apply_eq_zero_of_notMem :197, finiteSupport :254,
                                            le_def :404)
  Topology/ClusterPt.lean                  (accPt_principal_iff_nhdsWithin :225,
                                            AccPt.mono :230, :261)
  Topology/Neighborhoods.lean              (EventuallyEq.eq_of_nhds :153, nhdsWithin_mono :289)
  Topology/Algebra/Monoid.lean             (continuousOn_finsetSum, to_additive twin of :950)
  Topology/Algebra/GroupWithZero.lean      (ContinuousOn.inv₀ :129)
  Algebra/BigOperators/Finprod.lean        (:353 and its to_additive twin)
  Algebra/BigOperators/Pi.lean             (Finset.prod_apply :45, Finset.prod_fn :51)
  Algebra/BigOperators/Ring/Finset.lean    (Int.cast_sum :377, Finset.sum_mul :56)
  Algebra/Order/BigOperators/Group/Finset.lean (sum_nonneg / sum_eq_zero_iff_of_nonneg,
                                            to_additive twins named at :119 and :164)
  Data/Int/Cast/Lemmas.lean                (Int.cast_eq_zero :57)
  Data/ENat/Basic.lean                     (ENat.map_eq_top_iff :526)

`open Filter` is load-bearing: `𝓟` and `codiscreteWithin` resolve only under it.
`open scoped Topology` supplies `𝓝` and `𝓝[≠]`. `open Complex` is NOT relied on
for name resolution anywhere below — every `Complex.*` and `Metric.*` name is
written fully qualified, exactly as the contract's statement blocks spell them,
so that a stage-two implementer may drop the `open` line without touching a
proof.
-/

/-! ## W1. The docstring-flagged gap `[GEN]` `[PIN]` — the warm-up

Closes the gap recorded in the module docstring of
`MeasureTheory/Integral/CircleIntegral.lean:54-56` ("The case `n = -1`,
`|w - c| > R` is not covered by these lemmas …"). Contract §2 W1.

Route taken: the LOG-PRIMITIVE route (contract-primary), via
`circleIntegral.integral_eq_zero_of_hasDerivWithinAt'` (CircleIntegral.lean:538),
which quantifies over `sphere c |R|` and carries NO sign hypothesis on `R` — so
the statement is uniform in the sign of `R` with no radius flip anywhere. The
recorded alternative (Cauchy + the `|R|` flip through
`Real.circleAverage_abs_radius`, CircleAverage.lean:135) is NOT taken here; see
obligation S1AP-W1e in the contract for its cost, and the fallback note at the
end of this proof. -/

/-- The integral of `(z - w)⁻¹` over the circle of centre `c` and radius `R`
vanishes when `w` lies outside the closed disc.

**The excluded region is `Metric.closedBall c |R|` — the closed disc of
GEOMETRIC radius `|R|`, not of radius `R`.** This is mandatory to state (contract
§2 W1, "Mandatory docstring", and §5.4): the declaration name records
`notMem_closedBall` but not the absolute value, and reading it as
`closedBall c R` gives a FALSE statement. Counterexample at the pin (contract
§5.2): at `c = w = 0`, `R = -1` the hypothesis `w ∉ closedBall c R` holds
vacuously because `closedBall 0 (-1) = ∅` (`Metric.closedBall_eq_empty`,
Topology/MetricSpace/Pseudo/Defs.lean:468), while
`∮ z in C(0, -1), (z - 0)⁻¹ = 2 * π * I ≠ 0` by
`circleIntegral.integral_sub_center_inv` (CircleIntegral.lean:532, whose
hypothesis is exactly `R ≠ 0`). Mathlib's own
`circleIntegral.integral_sub_zpow_of_undef` (:557) has the same silent `|R|`, so
the name is convention-conformant; the convention is what produced the defect. -/
theorem circleIntegral.integral_sub_inv_of_notMem_closedBall {c w : ℂ} {R : ℝ}
    (hw : w ∉ Metric.closedBall c |R|) :
    (∮ z in C(c, R), (z - w)⁻¹) = 0 := by
  -- `w` strictly outside: `|R| < ‖w - c‖`.
  have hlt : |R| < ‖w - c‖ :=
    not_le.mp fun h => hw (mem_closedBall_iff_norm.mpr h)
    -- `mem_closedBall_iff_norm : b ∈ closedBall a r ↔ ‖b - a‖ ≤ r` is the
    -- `to_additive` twin named at Analysis/Normed/Group/Basic.lean:876 over
    -- `mem_closedBall_iff_norm''` (:877). `not_le : ¬a ≤ b ↔ b < a`.
    -- FALLBACK if the twin's name does not resolve — exact alternative text:
    --   have hlt : |R| < ‖w - c‖ := by
    --     rw [← dist_eq_norm]
    --     exact not_le.mp fun h => hw (Metric.mem_closedBall.mpr h)
    --   (`Metric.mem_closedBall : y ∈ closedBall x ε ↔ dist y x ≤ ε`,
    --    Topology/MetricSpace/Pseudo/Defs.lean:421, `Iff.rfl`.)
  have hwc : w - c ≠ 0 := norm_pos_iff.mp (lt_of_le_of_lt (abs_nonneg R) hlt)
    -- `norm_pos_iff : 0 < ‖a‖ ↔ a ≠ 0` — to_additive twin named at
    -- Analysis/Normed/Group/Basic.lean:993 over `norm_pos_iff'` (:994).
  have hcw : c - w ≠ 0 := sub_ne_zero_of_ne (Ne.symm (sub_ne_zero.mp hwc))
    -- `sub_ne_zero : a - b ≠ 0 ↔ a ≠ b` — to_additive twin of `div_ne_one`,
    -- Algebra/Group/Basic.lean:753.
  have hnormcw : ‖c - w‖ = ‖w - c‖ := norm_sub_rev c w
    -- to_additive twin of `norm_div_rev`, Analysis/Normed/Group/Basic.lean:65.
  -- Pin the PRIMITIVE with `(f := …)` before `intro`, never a bare `apply`:
  -- the implicit `f` of CircleIntegral.lean:538 does not occur in the
  -- conclusion, so a bare `apply` leaves `?f` open across `intro z hz`
  -- (contract, pin lens finding 5 / S1AP-W1a).
  refine circleIntegral.integral_eq_zero_of_hasDerivWithinAt'
    (f := fun u : ℂ => Complex.log ((u - w) / (c - w))) ?_
    -- CircleIntegral.lean:538, `[CompleteSpace E]` satisfied at `E = ℂ`;
    -- its hypothesis quantifies over `sphere c |R|`, matching `hw`.
  intro z hz
  have hzc : ‖z - c‖ = |R| := mem_sphere_iff_norm.mp hz
    -- to_additive twin named at Analysis/Normed/Group/Basic.lean:885 over
    -- `mem_sphere_iff_norm'` (:886).
    -- FALLBACK — exact alternative text:
    --   have hzc : ‖z - c‖ = |R| := by
    --     rw [← dist_eq_norm]; exact Metric.mem_sphere.mp hz
  have hzw : z - w ≠ 0 := by
    intro h
    rw [sub_eq_zero] at h
    subst h
    exact hlt.ne' hzc
    -- `hlt.ne' : ‖w - c‖ ≠ |R|` (`LT.lt.ne' : a < b → b ≠ a`) against
    -- `hzc : ‖w - c‖ = |R|` after the substitution.
    -- FALLBACK if `subst` orients the other way (the `_`-free names above are
    -- the only place this matters) — exact alternative text for the block:
    --   intro h; rw [sub_eq_zero] at h; rw [h] at hzc; exact hlt.ne' hzc
  -- S1AP-W1b, discharged by a NAMED pinned lemma rather than by hand.
  -- `Complex.mem_slitPlane_of_norm_lt_one : ‖z‖ < 1 → 1 + z ∈ slitPlane`
  -- (Analysis/Complex/Basic.lean:689, proved from `ball_one_subset_slitPlane`
  -- :683) removes the whole `re (1 + q) ≥ 1 - ‖q‖` estimate the contract
  -- skeleton spelled out by hand — that estimate is exactly :683's proof.
  have hquot : (z - w) / (c - w) = 1 + (z - c) / (c - w) := by
    field_simp <;> ring
    -- `<;> ring` rather than `field_simp` alone, and rather than `field_simp; ring`
    -- on two lines. `field_simp` clears denominators but does not run `ring`, so a
    -- ring-shaped residue may remain; but if simp's own lemmas happen to close the
    -- goal, a following `ring` dies with "no goals". `<;>` runs `ring` on zero or
    -- one remaining goal and is therefore correct in BOTH branches. This exact
    -- defect — bare `field_simp` leaving a residue — cost the three-circles
    -- package a CI round on 2026-08-08 (TC-ALG, `notes/reviews/THREE_CIRCLES_PROMOTION_2026_08_08.md`).
    -- FALLBACK 1 (if the combinator itself misbehaves): `field_simp` then `ring` as
    -- separate tactics, accepting the "no goals" risk in the other branch.
    -- FALLBACK 2 (fully manual, no `field_simp`) — exact alternative text:
    --   rw [eq_comm, add_comm, div_add_one hcw]   -- Algebra/Field/Basic.lean:45
    --   congr 1
    --   ring
  have hlt1 : ‖(z - c) / (c - w)‖ < 1 := by
    rw [norm_div, div_lt_one (norm_pos_iff.mpr hcw), hnormcw, hzc]
    -- `norm_div : ‖a / b‖ = ‖a‖ / ‖b‖`, Analysis/Normed/Field/Basic.lean:66.
    exact hlt
  have hmem : (z - w) / (c - w) ∈ Complex.slitPlane := by
    rw [hquot]
    exact Complex.mem_slitPlane_of_norm_lt_one hlt1
  -- S1AP-W1a: the affine derivative, then the chain rule, then the arithmetic.
  have haff : HasDerivAt (fun u : ℂ => (u - w) / (c - w)) ((c - w)⁻¹) z := by
    simpa using ((hasDerivAt_id z).sub_const w).div_const (c - w)
    -- `hasDerivAt_id` — Analysis/Calculus/Deriv/Basic.lean:681, `x` EXPLICIT
    -- (variable block `(s x L)` at :673), so `hasDerivAt_id z` is correct.
    -- `.sub_const` — Analysis/Calculus/Deriv/Add.lean:403, the alias of
    -- `hasDerivAt_sub_const_iff (c : F)` (:400); it produces the `(· - w)`
    -- LAMBDA shape. `.div_const` — Analysis/Calculus/Deriv/Mul.lean:558,
    -- giving the derivative `1 / (c - w)`; `simpa` closes the `id z` and
    -- `one_div` seams.
    -- FALLBACK — exact alternative text:
    --   simpa [one_div] using (((hasDerivAt_id' (𝕜 := ℂ) z)).sub_const w).div_const (c - w)
    -- (`hasDerivAt_id' : HasDerivAt (fun x : 𝕜 => x) 1 x`, Deriv/Basic.lean:684,
    --  avoids the `id` unfolding altogether.)
  have hval : ((z - w) / (c - w))⁻¹ * (c - w)⁻¹ = (z - w)⁻¹ := by
    rw [inv_div]                      -- Algebra/Group/Basic.lean:396
    field_simp <;> ring
    -- `<;> ring` for the reason recorded at `hquot` above: correct whether or not
    -- `field_simp` leaves a residue. This step is load-bearing — `hval` is what
    -- turns the chain-rule constant into the stated derivative.
    -- FALLBACK: `rw [inv_div]; field_simp` then `ring` separately, or fully manual:
    --   rw [inv_div, div_mul_eq_mul_div, mul_inv_cancel₀ hcw, one_div]
  have hd : HasDerivAt (fun u : ℂ => Complex.log ((u - w) / (c - w))) (z - w)⁻¹ z := by
    have hchain : HasDerivAt (Complex.log ∘ fun u : ℂ => (u - w) / (c - w))
        (((z - w) / (c - w))⁻¹ * (c - w)⁻¹) z :=
      (Complex.hasDerivAt_log hmem).comp z haff
      -- `Complex.hasDerivAt_log` — SpecialFunctions/Complex/LogDeriv.lean:37.
      -- `HasDerivAt.comp` — Analysis/Calculus/Deriv/Comp.lean:258, with `x`
      -- EXPLICIT (trailing `(x)` of the variable block at :71, comment :67-:68),
      -- which is what makes `.comp z (…)` correct. Its conclusion is a
      -- `Function.comp`, not a lambda — hence the separate `have` and the
      -- defeq `exact` below rather than a `rw`.
    rw [hval] at hchain
    exact hchain
    -- FALLBACK if `exact` balks at `Function.comp` vs the lambda (this is the
    -- head-symbol seam, not a defeq failure) — exact alternative text:
    --   simpa [Function.comp_def] using hchain
  exact hd.hasDerivWithinAt
  -- RECORDED ALTERNATIVE ROUTE (contract §2 W1, obligation S1AP-W1e, NOT taken):
  -- Cauchy + the `|R|` flip. For `0 ≤ R`, `fun z => (z - w)⁻¹` is
  -- `DiffContOnCl ℂ · (ball c R)` (differentiable off `w`, and
  -- `w ∉ closedBall c R = closure (ball c R)` by `closure_ball`,
  -- Analysis/Normed/Module/RCLike/Real.lean:59; the `R = 0` case is
  -- `circleIntegral.integral_radius_zero`, CircleIntegral.lean:422), so
  -- `DiffContOnCl.circleIntegral_eq_zero` (CauchyIntegral.lean:459) closes it.
  -- For `R < 0` that route needs an `∮`-level flip, which is PRESENT AS
  -- MATHEMATICS and ABSENT AS A NAMED `∮` LEMMA at the pin: run
  -- `Real.circleAverage_eq_circleIntegral` (CircleAverage.lean:96, `R ≠ 0`) at
  -- the weighted integrand `fun z ↦ (z - c) • g z` at both radii, cancel the
  -- `(z - c)⁻¹ •` weight with
  -- `circleIntegral.circleIntegral_congr_codiscreteWithin` (:430, `R ≠ 0`) —
  -- NOT `integral_congr` (:425), whose `0 ≤ R` excludes exactly the sign case
  -- at issue — then apply `Real.circleAverage_abs_radius` (:135).

/-! ## A1. Codiscrete agreement upgrades to local agreement `[GEN]` `[PIN]` — the bridge

Contract §2 A1. **Not a new move**: Mathlib already proves the meromorphic,
PUNCTURED form of exactly this bridge at
`MeromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin`
(Analysis/Meromorphic/IsolatedZeros.lean:99, namespace `MeromorphicAt` :31-:130,
section variables :24-:27 identical to A1's binder context). The ONLY delta is
punctured `𝓝[≠] x` → unpunctured `𝓝 x`, which is obligation S1AP-BRIDGE (LOW
after `RH-015`, downgraded from HIGH; it does NOT gate A2-A4). -/

theorem AnalyticAt.eventuallyEq_of_codiscreteWithin
    {𝕜 : Type*} [NontriviallyNormedField 𝕜]
    {E : Type*} [NormedAddCommGroup E] [NormedSpace 𝕜 E]
    {f g : 𝕜 → E} {U : Set 𝕜} {x : 𝕜}
    (hf : AnalyticAt 𝕜 f x) (hg : AnalyticAt 𝕜 g x)
    (hxU : x ∈ U) (hacc : AccPt x (𝓟 U))
    (h : f =ᶠ[Filter.codiscreteWithin U] g) :
    f =ᶠ[𝓝 x] g := by
  -- 1. `AnalyticAt ⇒ MeromorphicAt` on both sides — Meromorphic/Basic.lean:40
  --    (`@[fun_prop] lemma AnalyticAt.meromorphicAt`, root level).
  -- 2. The pinned punctured bridge — Meromorphic/IsolatedZeros.lean:99.
  have hpunct : f =ᶠ[𝓝[≠] x] g :=
    hf.meromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin
      hg.meromorphicAt hxU hacc h
  -- 3. Punctured `EventuallyEq` ⇒ `Frequently`. The `[NeBot (𝓝[≠] x)]` that
  --    `Filter.Eventually.frequently` (Order/Filter/Basic.lean:756) demands is
  --    supplied by instance search from `NormedField.nhdsNE_neBot`
  --    (Analysis/Normed/Field/Basic.lean:242 — `@[instance]` at :241, stated for
  --    `[NontriviallyNormedField α]`, which is exactly A1's typeclass), so NO
  --    manual `NeBot` argument appears here.
  --    NOTE (failure class: a lemma name that does not exist at the pin): the
  --    contract skeleton writes `(…).frequently`. `Filter.EventuallyEq` is a
  --    plain `def` (Order/Filter/Defs.lean:297) and there is NO
  --    `Filter.EventuallyEq.frequently` at the pin — grepped this session. The
  --    dot notation therefore has to unfold the `def` to reach
  --    `Filter.Eventually.frequently`. It is written out below with an explicit
  --    type ascription so the unfolding happens in `isDefEq`, not in
  --    dot-notation resolution.
  have hfreq : ∃ᶠ z in 𝓝[≠] x, f z = g z := Filter.Eventually.frequently hpunct
  -- 4. The analytic identity principle upgrades frequent agreement on the
  --    punctured filter to eventual agreement on the full one —
  --    Analysis/Analytic/IsolatedZeros.lean:141 (namespace `AnalyticAt` :120-:203).
  exact (hf.frequently_eq_iff_eventually_eq hg).mp hfreq
  -- FALLBACK (S1AP-BRIDGE, contract-recorded, in order):
  -- (i) if `Filter.Eventually.frequently hpunct` will not unify because the
  --     `EventuallyEq` def does not unfold, insert the unfolding by hand:
  --       have hpunct' : ∀ᶠ z in 𝓝[≠] x, f z = g z := hpunct
  --       have hfreq := hpunct'.frequently
  -- (ii) the full v1.1 filter-algebra route, every link of which is also pinned:
  --       have h₁ : ¬ AccPt x (𝓟 (U \ {z | f z = g z})) :=
  --         (mem_codiscreteWithin_accPt.mp h) x hxU   -- DiscreteSubset.lean:217
  --         -- NB: ROOT-LEVEL, not `Filter.…`. DiscreteSubset.lean opens no
  --         -- `namespace Filter`; only the DEF at :201 carries the explicit
  --         -- `Filter.` prefix (`def Filter.codiscreteWithin`), while :203, :217
  --         -- and their neighbours are plain root names.
  --       have h₂ : AccPt x (𝓟 (U ∩ {z | f z = g z})) := by
  --         refine (accPt_sup.mp (hacc.mono ?_)).resolve_right h₁   -- ClusterPt.lean:190
  --         rw [← Filter.sup_principal]
  --         exact Filter.principal_mono.mpr (fun y hy => by
  --           by_cases hy' : f y = g y
  --           · exact Or.inl ⟨hy, hy'⟩
  --           · exact Or.inr ⟨hy, hy'⟩)
  --       exact (hf.frequently_eq_iff_eventually_eq hg).mp
  --         ((accPt_iff_frequently_nhdsNE.mp h₂).mono fun y hy => hy.2)  -- ClusterPt.lean:217
  -- (iii) `AccPt.mono` (ClusterPt.lean:230) in place of the `sup` step;
  -- (iv) LAST RESORT ONLY, and it must be RECORDED as a dropped statement, not
  --      silently done: specialise A1 to `𝕜 = ℂ`, `U = closedBall c R` and
  --      inline it into A2. **Do NOT instead weaken A2 by assuming the
  --      factorization pointwise — that is contract death condition 6.**

/-! ## A2. Circle-only argument principle, analytic case `[GEN]` `[PIN]` — the main statement

Contract §2 A2. This is the package's genuinely un-pinned content, and its
step 7 carries the package's only HIGH obligation, S1AP-LOGD. -/

/-- The circle integral of the logarithmic derivative of an analytic,
boundary-nonvanishing `f` equals `2πI` times the divisor sum over the open disc.

`hR : 0 < R` IS REQUIRED FOR TRUTH, not for convenience (contract §2 A2, §5.2,
death condition 8(b)). At `R = -1` with `f = id`, `c = 0` both hypotheses are
vacuous (`closedBall 0 (-1) = ∅` by Pseudo/Defs.lean:468, `sphere 0 (-1) = ∅`
by :442), the divisor sum is `0` because `ball 0 (-1) = ∅` (:387) and the
divisor's `toFun` guards on `z ∈ U` (Divisor.lean:39-:41), while the left side
is `2πI ≠ 0` by CircleIntegral.lean:532. `0 = 2πI` is false. Nothing below
relaxes `0 < R`. -/
theorem Complex.circleIntegral_logDeriv_eq_divisor_sum
    {f : ℂ → ℂ} {c : ℂ} {R : ℝ} (hR : 0 < R)
    (hf : AnalyticOnNhd ℂ f (Metric.closedBall c R))
    (hf₀ : ∀ z ∈ Metric.sphere c R, f z ≠ 0) :
    (∮ z in C(c, R), deriv f z / f z)
      = 2 * Real.pi * Complex.I
          * ((∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u : ℤ) : ℂ) := by
  classical
  ----------------------------------------------------------------------------
  -- Step 0. Geometry of the disc.  `0 < R` enters here and never leaves.
  ----------------------------------------------------------------------------
  have hsphCB : Metric.sphere c R ⊆ Metric.closedBall c R :=
    Metric.sphere_subset_closedBall            -- Pseudo/Defs.lean:480
  have hballCB : Metric.ball c R ⊆ Metric.closedBall c R :=
    Metric.ball_subset_closedBall              -- Pseudo/Defs.lean:477
  have hCBcpt : IsCompact (Metric.closedBall c R) := isCompact_closedBall c R
    -- `ProperSpace` field, exported at Topology/MetricSpace/ProperSpace.lean:42 (the class is :39 and the field :40; :41 is blank);
    -- the `ProperSpace ℂ` instance comes from finite-dimensionality.
  have hCBconn : IsPreconnected (Metric.closedBall c R) :=
    (convex_closedBall c R).isPreconnected
    -- `convex_closedBall` — Analysis/Normed/Module/Convex.lean:71;
    -- `Convex.isPreconnected` — Analysis/Convex/PathConnected.lean:93.
  have hmero : MeromorphicOn f (Metric.closedBall c R) := hf.meromorphicOn
    -- Meromorphic/Basic.lean:475.
  have hznotball : ∀ z ∈ Metric.sphere c R, z ∉ Metric.ball c R := by
    intro z hz hzb
    exact absurd (Metric.mem_ball.mp hzb)      -- Pseudo/Defs.lean:371
      (by rw [Metric.mem_sphere.mp hz]; exact lt_irrefl R)   -- :431
  ----------------------------------------------------------------------------
  -- Step 2 (S1AP-FIN).  `f` is nowhere locally constant zero on the closed ball.
  -- `0 < R` is what makes the sphere NONEMPTY, hence what makes `hf₀` non-vacuous,
  -- hence what supplies the finite-order seed.  This is the soundness hinge.
  ----------------------------------------------------------------------------
  obtain ⟨z₀, hz₀⟩ : (Metric.sphere c R).Nonempty :=
    NormedSpace.sphere_nonempty.mpr hR.le      -- RCLike/Real.lean:128
  have hord₀ : analyticOrderAt f z₀ ≠ ⊤ := by
    rw [(hf z₀ (hsphCB hz₀)).analyticOrderAt_eq_zero.mpr (hf₀ z₀ hz₀)]
    -- `AnalyticAt.analyticOrderAt_eq_zero : analyticOrderAt f z₀ = 0 ↔ f z₀ ≠ 0`
    -- — Analysis/Analytic/Order.lean:133 (`protected`, so dot notation only).
    simp
    -- FALLBACK: `exact WithTop.zero_ne_top` (the goal is `(0 : ℕ∞) ≠ ⊤`).
  have h₂f : ∀ u : Metric.closedBall c R, meromorphicOrderAt f ↑u ≠ ⊤ := by
    rintro ⟨u, hu⟩
    -- the `∀ u : ↥CB` subtype binder needs the `obtain`/`rintro` idiom (S1M-16d
    -- pattern of the built `Mult.lean`); the `show` then discharges the residual
    -- `↑⟨u, hu⟩` projection-of-constructor so the rewrite matches syntactically.
    show meromorphicOrderAt f u ≠ ⊤
    rw [(hf u hu).meromorphicOrderAt_eq]
    -- `AnalyticAt.meromorphicOrderAt_eq : meromorphicOrderAt f x
    --   = (analyticOrderAt f x).map (↑)` — Analysis/Meromorphic/Order.lean:279.
    simpa using hf.analyticOrderAt_ne_top_of_isPreconnected hCBconn
      (hsphCB hz₀) hu hord₀
    -- `AnalyticOnNhd.analyticOrderAt_ne_top_of_isPreconnected` —
    -- Analysis/Analytic/Order.lean:624 (namespace `AnalyticOnNhd` :575-:700).
    -- The `simpa` discharges `ENat.map_eq_top_iff` (Data/ENat/Basic.lean:526,
    -- `@[simp]`), which is the carrier hop `ℕ∞ → WithTop ℤ`.
    -- FALLBACK — exact alternative text for the last line:
    --   rw [Ne, ENat.map_eq_top_iff]
    --   exact hf.analyticOrderAt_ne_top_of_isPreconnected hCBconn (hsphCB hz₀) hu hord₀
  ----------------------------------------------------------------------------
  -- Step 3.  Finiteness of the divisor's support is a THEOREM, never a hypothesis
  -- (contract decision D5).
  ----------------------------------------------------------------------------
  have h₃f : (MeromorphicOn.divisor f (Metric.closedBall c R)).support.Finite :=
    (MeromorphicOn.divisor f (Metric.closedBall c R)).finiteSupport hCBcpt
    -- `Function.locallyFinsuppWithin.finiteSupport` — Topology/LocallyFinsupp.lean:254;
    -- `.support` is the reducible abbrev at :138 for `Function.support ⇑D`.
  ----------------------------------------------------------------------------
  -- Step 4.  Extract zeros and poles.
  ----------------------------------------------------------------------------
  obtain ⟨g, hg, hg₀, hfg⟩ := hmero.extract_zeros_poles h₂f h₃f
  -- `MeromorphicOn.extract_zeros_poles` — FactorizedRational.lean:291. Its
  -- DOCSTRING (:285-:290) opens "If `f` is meromorphic on an OPEN set `U`" but
  -- its BINDERS (section variables :35-:38 are bare `𝕜, E, U : Set 𝕜`) carry no
  -- `IsOpen`, and THE BINDERS GOVERN — so `U := closedBall c R` is legal. Do not
  -- stall on that docstring (contract §0, truth lens finding 5).
  have hg₀' : ∀ z ∈ Metric.closedBall c R, g z ≠ 0 := fun z hz => hg₀ ⟨z, hz⟩
  ----------------------------------------------------------------------------
  -- Step 5 (S1AP-SUPP).  The divisor vanishes on the sphere; its support sits
  -- inside the OPEN ball.  Taken by the contract's recorded pointwise fallback
  -- (`divisor_apply` + `analyticOrderAt_eq_zero`) rather than through
  -- `zero_set_eq_divisor_support` (:578), whose conclusion is oriented
  -- `U ∩ f ⁻¹' {0} = support …` — the wrong direction here. :578 IS used, on the
  -- ball carrier, in A3 where that orientation is the one wanted.
  ----------------------------------------------------------------------------
  have hDsph : ∀ z ∈ Metric.sphere c R,
      MeromorphicOn.divisor f (Metric.closedBall c R) z = 0 := by
    intro z hz
    rw [MeromorphicOn.AnalyticOnNhd.divisor_apply hf (hsphCB hz),
      (hf z (hsphCB hz)).analyticOrderAt_eq_zero.mpr (hf₀ z hz)]
    -- `MeromorphicOn.AnalyticOnNhd.divisor_apply` — Divisor.lean:71. THE NAME
    -- MUST BE FULLY QUALIFIED: :71 takes an `AnalyticOnNhd` hypothesis but sits
    -- inside `namespace MeromorphicOn` with no `_root_`, so dot notation on an
    -- `AnalyticOnNhd` term looks for a root-level `AnalyticOnNhd.divisor_apply`
    -- that does not exist (contract §0 naming trap; built precedent
    -- repo:ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:390).
    simp
    -- goal is `((0 : ℕ∞).map (↑)).untop₀ = 0`; `ENat.map_zero` (ENat/Basic.lean:517)
    -- and `WithTop.untop₀_coe` are both `@[simp]`.
  have hDball : ∀ u, MeromorphicOn.divisor f (Metric.closedBall c R) u ≠ 0 →
      u ∈ Metric.ball c R := by
    intro u hu
    have huCB : u ∈ Metric.closedBall c R :=
      (MeromorphicOn.divisor f (Metric.closedBall c R)).supportWithinDomain hu
      -- LocallyFinsupp.lean:140; `hu : D u ≠ 0` is `u ∈ Function.support ⇑D`
      -- definitionally.
    rcases lt_or_eq_of_le (Metric.mem_closedBall.mp huCB) with h | h
    · exact Metric.mem_ball.mpr h
    · exact absurd (hDsph u (Metric.mem_sphere.mpr h)) hu
  have hsuppD :
      Function.support (⇑(MeromorphicOn.divisor f (Metric.closedBall c R)))
        ⊆ ↑h₃f.toFinset :=
    fun u hu => Finset.mem_coe.mpr (h₃f.mem_toFinset.mpr hu)
    -- `Set.Finite.mem_toFinset` — Data/Set/Finite/Basic.lean:106 (`hs` EXPLICIT,
    -- variable block :103, so `h₃f.mem_toFinset` is the right spelling);
    -- `Finset.mem_coe` — Data/Finset/Defs.lean:126.
  have hsphne : ∀ z ∈ Metric.sphere c R, ∀ u ∈ h₃f.toFinset, z - u ≠ 0 := by
    intro z hz u hu huz
    rw [sub_eq_zero] at huz
    subst huz
    exact hznotball _ hz (hDball _ (h₃f.mem_toFinset.mp hu))
    -- the `_`s are deliberate: `subst` may orient either way and the argument is
    -- symmetric in which of `z`, `u` survives.
  ----------------------------------------------------------------------------
  -- Step 6 input (S1AP-A1a).  Every sphere point accumulates the closed ball.
  -- `0 < R` is used AGAIN here, through `closure_ball`'s `R ≠ 0`.
  ----------------------------------------------------------------------------
  have hacc : ∀ z ∈ Metric.sphere c R, AccPt z (𝓟 (Metric.closedBall c R)) := by
    intro z hz
    rw [accPt_principal_iff_nhdsWithin]
    -- `accPt_principal_iff_nhdsWithin : AccPt x (𝓟 s) ↔ (𝓝[s \ {x}] x).NeBot`
    -- — Topology/ClusterPt.lean:225.
    have hnb : (𝓝[Metric.ball c R] z).NeBot := by
      rw [← mem_closure_iff_nhdsWithin_neBot, closure_ball c hR.ne']
      -- `mem_closure_iff_nhdsWithin_neBot` — ClusterPt.lean:261;
      -- `closure_ball (x) {r} (hr : r ≠ 0)` — RCLike/Real.lean:59.
      exact hsphCB hz
    refine hnb.mono (nhdsWithin_mono z ?_)
    -- `Filter.NeBot.mono` — Order/Filter/Basic.lean:263;
    -- `nhdsWithin_mono` — Topology/Neighborhoods.lean:289.
    intro y hy
    refine ⟨hballCB hy, ?_⟩
    intro hyz
    rw [Set.mem_singleton_iff] at hyz
    exact hznotball z hz (hyz ▸ hy)
    -- FALLBACK if `▸` picks the wrong orientation — exact alternative text:
    --   subst hyz; exact hznotball _ hz hy
  ----------------------------------------------------------------------------
  -- Step 7 preparation (S1AP-LOGD, the package's ONLY HIGH obligation).
  -- The finprod lives in the FUNCTION monoid `ℂ → ℂ`; `logDeriv_prod` (:73)
  -- concludes on the LAMBDA `logDeriv (∏ i ∈ s, f i ·) x`. Those are defeq but
  -- NOT syntactically equal, and `rw` compares HEAD SYMBOLS, so the conversion
  -- is done ONCE here, explicitly, via `Finset.prod_fn`, instead of being left
  -- for a rewrite to discover.  Contract, pin lens finding 2: the lambda hazard
  -- is present at ALL THREE shapes (:56, :75, :87), not only at :87.
  ----------------------------------------------------------------------------
  have hmulsupp : Function.mulSupport
      (fun u => ((· - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ))
        ⊆ ↑h₃f.toFinset := by
    rw [Function.FactorizedRational.mulSupport]   -- FactorizedRational.lean:52
    exact hsuppD
  have hprodfun :
      (∏ᶠ u, ((· - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ))
        = fun y : ℂ => ∏ u ∈ h₃f.toFinset,
            (y - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u := by
    rw [finprod_eq_prod_of_mulSupport_subset _ hmulsupp, Finset.prod_fn]
    first
    | rfl
    | (funext y; simp [Finset.prod_apply, Pi.pow_apply])
    -- KERNEL ROUND 1 (PR #329) rejected this step with `unsolved goals`: after the
    -- rewrite the goal is
    --   (fun a => ∏ c ∈ s, ((fun x => x - c) ^ D c) a) = fun y => ∏ u ∈ s, (y - u) ^ D u
    -- i.e. only the POINTWISE POWER application remains. `Pi.pow_apply`
    -- (Algebra/Notation/Pi/Defs.lean:136) is `rfl` and is generic over the `Pow`
    -- instance at :133, so it covers this ℤ exponent — but `rw`'s trailing auto-rfl
    -- runs at REDUCIBLE transparency and will not unfold the Pi power under a
    -- binder. An explicit `rfl` tactic runs at default transparency and does. The
    -- `first` combinator keeps the drafter's recorded fallback as the second arm
    -- rather than replacing it, so if the defeq route ever stops working the simp
    -- route still fires and neither arm can die with "no goals".
    -- `finprod_eq_prod_of_mulSupport_subset` — Algebra/BigOperators/Finprod.lean:354 (:353 is the `@[to_additive]` attribute line);
    -- `Finset.prod_fn : ∏ c ∈ s, g c = fun a ↦ ∏ c ∈ s, g c a` —
    -- Algebra/BigOperators/Pi.lean:51 (the "unapplied" analogue of
    -- `Finset.prod_apply` :45).  The residual goal is closed by `rfl` because
    -- `Pi.pow_apply` (Algebra/Notation/Pi/Defs.lean:136) is a `rfl` lemma.
    -- FALLBACK if `rw`'s trailing `rfl` does not fire — exact alternative text:
    --   rw [finprod_eq_prod_of_mulSupport_subset _ hmulsupp]
    --   funext y
    --   simp [Finset.prod_apply, Pi.pow_apply]
  ----------------------------------------------------------------------------
  -- Step 10 preparation.  `logDeriv g` is analytic on a neighbourhood of the
  -- closed ball, hence `DiffContOnCl` on the open one.
  ----------------------------------------------------------------------------
  have hlogg : AnalyticOnNhd ℂ (fun z => deriv g z / g z) (Metric.closedBall c R) :=
    fun z hz => ((hg z hz).deriv).fun_div (hg z hz) (hg₀' z hz)
    -- `AnalyticAt.deriv` — FDeriv/Analytic.lean:457, `[CompleteSpace F]` at `ℂ`;
    -- `AnalyticAt.fun_div` is the `@[to_fun]` twin (attribute at
    -- Analysis/Analytic/Constructions.lean:991) of `AnalyticAt.div` (:992),
    -- whose Pi-level `f / g` conclusion would NOT match the lambda here.
    -- The `fun_*` naming convention is Mathlib's own — see
    -- FactorizedRational.lean:86/:88 using `AnalyticAt.fun_zpow_nonneg`/`fun_zpow` (:84 is `intro u`, :87 is `rwa [← h₂]`).
  ----------------------------------------------------------------------------
  -- Steps 6 + 7.  The pointwise identity on the sphere.
  ----------------------------------------------------------------------------
  have hkey : Set.EqOn (fun z => deriv f z / f z)
      (fun z => (∑ u ∈ h₃f.toFinset,
            (MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ) * (z - u)⁻¹)
          + deriv g z / g z) (Metric.sphere c R) := by
    intro z hz
    show deriv f z / f z
        = (∑ u ∈ h₃f.toFinset,
            (MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ) * (z - u)⁻¹)
          + deriv g z / g z
    have hzCB : z ∈ Metric.closedBall c R := hsphCB hz
    have hDz : MeromorphicOn.divisor f (Metric.closedBall c R) z = 0 := hDsph z hz
    have hφz : AnalyticAt ℂ (∏ᶠ u,
        ((· - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ)) z :=
      Function.FactorizedRational.analyticAt (le_of_eq hDz.symm)   -- :81
    have hφz₀ : (∏ᶠ u,
        ((· - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ)) z ≠ 0 :=
      Function.FactorizedRational.ne_zero hDz                      -- :94
    have hgz : AnalyticAt ℂ g z := hg z hzCB
    have hgz₀ : g z ≠ 0 := hg₀' z hzCB
    -- S1AP-SMUL. `hfg`'s right-hand side is `φ • g` (Pi-level `smul`), not
    -- `fun y => φ y * g y`. At `E = ℂ` the identification is `smul_eq_mul`
    -- (Algebra/Group/Action/Defs.lean:74, a `rfl`) through `Pi.smul_apply` (the
    -- `to_additive` twin generated by the attribute line at
    -- Algebra/Notation/Pi/Defs.lean:135 over `Pi.pow_apply` :136 — it has NO
    -- declaration line of its own, which is why grepping for it finds nothing).
    -- It is discharged HERE, once, pointwise, rather than being left to a
    -- defeq check inside A1's application.
    have hfg' : f =ᶠ[Filter.codiscreteWithin (Metric.closedBall c R)]
        fun y => (∏ᶠ u, ((· - u)
          ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ)) y * g y := by
      filter_upwards [hfg] with y hy
      simpa [Pi.smul_apply, smul_eq_mul] using hy
      -- FALLBACK — exact alternative text: `exact hy` (the two sides are `rfl`-equal
      -- because `Pi.instSMul` is pointwise and `SMul ℂ ℂ` is `Mul.toSMul`).
    -- A1 at `z`.
    have hlocal : f =ᶠ[𝓝 z]
        fun y => (∏ᶠ u,
            ((· - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ)) y * g y :=
      AnalyticAt.eventuallyEq_of_codiscreteWithin (hf z hzCB) (hφz.fun_mul hgz)
        hzCB (hacc z hz) hfg'
      -- `AnalyticAt.fun_mul` is the `@[to_fun]` twin (attribute at
      -- Constructions.lean:638) of `AnalyticAt.mul` (:639).
    have hfz : f z
        = (∏ᶠ u,
            ((· - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ)) z * g z :=
      hlocal.eq_of_nhds        -- Topology/Neighborhoods.lean:153
    have hdz : deriv f z
        = deriv (fun y => (∏ᶠ u, ((· - u)
            ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ)) y * g y) z :=
      hlocal.deriv_eq          -- Analysis/Calculus/Deriv/Basic.lean:647
    -- S1AP-LOGD, part 1: split the logarithmic derivative of the product.
    have hsplit : deriv f z / f z
        = logDeriv (∏ᶠ u,
              ((· - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ)) z
            + logDeriv g z := by
      rw [hdz, hfz]
      exact logDeriv_mul z hφz₀ hgz₀ hφz.differentiableAt hgz.differentiableAt
      -- `logDeriv_mul {f g} (x : 𝕜) (hf) (hg) (hdf) (hdg)` — LogDeriv.lean:54-:56.
      -- ITS FIRST ARGUMENT `(x : 𝕜)` IS EXPLICIT AND PRECEDES `hf`: a call
      -- written `logDeriv_mul hφz₀ hgz₀ …` is wrong by one argument (contract,
      -- pin lens finding 1).  The `exact` succeeds by defeq: `logDeriv F z`
      -- unfolds to `deriv F z / F z` (`logDeriv` is `deriv f / f`,
      -- LogDeriv.lean:34, and `logDeriv_apply` :37 is `rfl`), and the lambda
      -- `(fun y => φ y * g y) z` beta-reduces to `φ z * g z`.
      -- `AnalyticAt.differentiableAt` — FDeriv/Analytic.lean:126.
      -- FALLBACK — exact alternative text if the defeq is not found. Ascribe the
      -- goal into `logDeriv` shape with `show`, then apply:
      --   show logDeriv (fun y => φ y * g y) z = logDeriv φ z + logDeriv g z
      --   exact logDeriv_mul z hφz₀ hgz₀ hφz.differentiableAt hgz.differentiableAt
      --
      -- CORRECTED 2026-08-08 by the RH-016 fidelity review. An earlier version of
      -- this fallback read `rw [hdz, hfz, ← logDeriv_apply]` and CANNOT FIRE.
      -- `logDeriv_apply (f) (x) : logDeriv f x = deriv f x / f x` (LogDeriv.lean:37),
      -- so the reverse rewrite matches `deriv ?f ?x / ?f ?x` and demands the SAME
      -- syntactic `?f` applied to the same `?x` in numerator and denominator. After
      -- `rw [hfz]` the numerator carries the lambda `fun y => φ y * g y` while the
      -- denominator is the already-reduced `φ z * g z`, so no such `?f` exists and
      -- the rewrite finds nothing. Recording it is worth more than deleting it: a
      -- fallback is consulted only in the emergency it exists for, so a fallback
      -- that cannot fire is worse than none, and this one would have been reached
      -- exactly when the primary `exact` had already failed.
    -- S1AP-LOGD, part 2: expand the factorized rational factor.
    have hne : ∀ u ∈ h₃f.toFinset,
        (fun y : ℂ => (y - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u) z ≠ 0 :=
      fun u hu => zpow_ne_zero _ (hsphne z hz u hu)
      -- `zpow_ne_zero (n) (h : a ≠ 0) : a ^ n ≠ 0` —
      -- Algebra/GroupWithZero/Units/Basic.lean:412.
    have hdiff : ∀ u ∈ h₃f.toFinset, DifferentiableAt ℂ
        (fun y : ℂ => (y - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u) z :=
      fun u hu =>
        (AnalyticAt.fun_zpow
          (by show AnalyticAt ℂ (fun y : ℂ => y - u) z; fun_prop)
          (hsphne z hz u hu)).differentiableAt
      -- KERNEL ROUND 1 (PR #329) rejected the bare `(by fun_prop)` here:
      --   `fun_prop` was unable to prove `AnalyticAt ?m.1468 (HSub.hSub z) u`
      --   Failed to infer `(?m.1468 : Type ?u.694)` when applying `analyticAt_const`
      -- Two things went wrong and the second is caused by the first. The SCALAR
      -- FIELD was an unassigned metavariable `?m.1468`, because nothing in the
      -- expected type had fixed it before the tactic ran; with the field unknown
      -- the elaborator also mis-associated the arguments and went looking for
      -- `(z - ·)` analytic at `u` instead of `(· - u)` analytic at `z`. The `show`
      -- pins the field AND the function shape AND the point before `fun_prop`
      -- starts, so neither failure can recur. This is the same hazard class the
      -- drafter hoisted at two other sites and missed here.
      -- `AnalyticAt.fun_zpow` is the `@[to_fun]` twin (attribute
      -- Constructions.lean:928) of `AnalyticAt.zpow` (:929), whose hypotheses
      -- are `(h₁f : AnalyticAt 𝕜 f z) (h₂f : f z ≠ 0)`.
      -- FALLBACK if `fun_prop` cannot see `AnalyticAt ℂ (fun y => y - u) z`
      -- — exact alternative text for the first argument:
      --   (analyticAt_id.fun_sub analyticAt_const)
    have hlogφ : logDeriv (∏ᶠ u,
          ((· - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ)) z
        = ∑ u ∈ h₃f.toFinset,
            (MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ) * (z - u)⁻¹ := by
      have h1 : logDeriv (∏ᶠ u,
            ((· - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ → ℂ)) z
          = ∑ u ∈ h₃f.toFinset,
              logDeriv (fun y : ℂ =>
                (y - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u) z := by
        rw [hprodfun]
        exact logDeriv_prod hne hdiff
        -- `logDeriv_prod` — LogDeriv.lean:73-:75, concluding on the LAMBDA
        -- `logDeriv (∏ i ∈ s, f i ·) x`.  Using `exact` (not `rw`) is deliberate:
        -- the RIGHT-hand side of the goal determines `f` by first-order matching,
        -- so no higher-order unification against the product shape is needed.
        -- FALLBACK — exact alternative text, pinning `f` positionally:
        --   rw [hprodfun]
        --   exact logDeriv_prod (𝕜 := ℂ) (𝕜' := ℂ) (s := h₃f.toFinset)
        --     (f := fun u => fun y : ℂ =>
        --       (y - u) ^ MeromorphicOn.divisor f (Metric.closedBall c R) u)
        --     (x := z) hne hdiff
      rw [h1]
      refine Finset.sum_congr rfl fun u hu => ?_
      -- `hdu` is hoisted out of the `rw` ON PURPOSE.  Written inline as
      -- `logDeriv_fun_zpow (by fun_prop) …`, the tactic block's goal is
      -- `DifferentiableAt ℂ ?f z` with `?f` still unassigned — it is only fixed
      -- by the rewrite's own matching, so the `by` would be elaborated against a
      -- metavariable.  Naming it first makes the rewrite pattern fully concrete.
      have hdu : DifferentiableAt ℂ (fun y : ℂ => y - u) z := by fun_prop
      -- FALLBACK if `fun_prop` misses it — exact alternative text:
      --   have hdu : DifferentiableAt ℂ (fun y : ℂ => y - u) z :=
      --     differentiableAt_id.sub_const u
      -- (`differentiableAt_id` — Analysis/Calculus/FDeriv/Basic.lean:697, stated
      --  on `id`; `DifferentiableAt.sub_const` — FDeriv/Add.lean:779.  The `id`
      --  vs `fun y => y` gap is closed by the ascribed type of the `have`.)
      rw [logDeriv_fun_zpow hdu
        (MeromorphicOn.divisor f (Metric.closedBall c R) u), logDeriv_apply]
      -- `logDeriv_fun_zpow (hdf) (n) : logDeriv (f · ^ n) x = n * logDeriv f x`
      -- — LogDeriv.lean:87.  `(f · ^ n)` is the lambda `fun y => f y ^ n`, which
      -- is why the sum above is carried in lambda form throughout.
      simp
      -- goal is `↑(D u) * (deriv (fun y => y - u) z / (z - u)) = ↑(D u) * (z - u)⁻¹`.
      -- The `@[simp]` lemmas that do it are the UNAPPLIED pair
      -- `deriv_sub_const_fun` (Analysis/Calculus/Deriv/Add.lean:418) and
      -- `deriv_id''` (Analysis/Calculus/Deriv/Basic.lean:699), then `one_div`.
      -- NOTE the applied `deriv_sub_const` (Add.lean:414) is NOT `@[simp]` — only
      -- its `fun`-form twin is; do not cite the wrong one when repairing.
      -- FALLBACK — exact alternative text replacing the `simp`:
      --   have hd1 : deriv (fun y : ℂ => y - u) z = 1 :=
      --     HasDerivAt.deriv (by simpa using (hasDerivAt_id z).sub_const u)
      --   rw [hd1, one_div]
    rw [hsplit, hlogφ, logDeriv_apply]
  ----------------------------------------------------------------------------
  -- Step 8 (S1AP-INT).  Integrability of each piece on the sphere, supplied
  -- BEFORE the splits.  `0 ≤ R` (from `hR`) is required by :337 and :425.
  ----------------------------------------------------------------------------
  have hcont₁ : ∀ u ∈ h₃f.toFinset,
      ContinuousOn
        (fun z : ℂ => (MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ) * (z - u)⁻¹)
        (Metric.sphere c R) := by
    intro u hu
    have hinv : ContinuousOn (fun z : ℂ => (z - u)⁻¹) (Metric.sphere c R) :=
      ContinuousOn.inv₀ (by fun_prop) (fun z hz => hsphne z hz u hu)
      -- `ContinuousOn.inv₀ (hf) (h0 : ∀ x ∈ s, f x ≠ 0)` —
      -- Topology/Algebra/GroupWithZero.lean:129.  The expected type here fixes
      -- `f := fun z => z - u` BEFORE the `by fun_prop` runs, which is why the
      -- inline tactic block is safe at this occurrence.
      -- FALLBACK — exact alternative text for the first argument:
      --   (continuousOn_id.sub continuousOn_const)
    exact continuousOn_const.mul hinv
  have hint₁ : CircleIntegrable
      (fun z : ℂ => ∑ u ∈ h₃f.toFinset,
        (MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ) * (z - u)⁻¹) c R :=
    ContinuousOn.circleIntegrable hR.le (continuousOn_finsetSum _ hcont₁)
    -- `ContinuousOn.circleIntegrable (hR : 0 ≤ R) (hf)` — CircleIntegral.lean:337
    -- (`hR` is the FIRST explicit argument, which is why this is not written
    -- with dot notation); `continuousOn_finsetSum` is the `to_additive` twin of
    -- `continuousOn_finsetProd`, Topology/Algebra/Monoid.lean:950.
  have hint₂ : CircleIntegrable (fun z : ℂ => deriv g z / g z) c R :=
    ContinuousOn.circleIntegrable hR.le
      ((hlogg.mono hsphCB).differentiableOn.continuousOn)
    -- `AnalyticOnNhd.mono` — Analysis/Analytic/Basic.lean:498;
    -- `AnalyticOnNhd.differentiableOn` — FDeriv/Analytic.lean:176.
  ----------------------------------------------------------------------------
  -- Steps 8-10.  Rewrite under the integral, split, evaluate.
  ----------------------------------------------------------------------------
  have hterm : ∀ u ∈ h₃f.toFinset,
      (∮ z in C(c, R),
          (MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ) * (z - u)⁻¹)
        = (MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ)
            * (2 * Real.pi * Complex.I) := by
    intro u hu
    rw [circleIntegral.integral_const_mul,                       -- :527
      circleIntegral.integral_sub_inv_of_mem_ball                -- :699
        (hDball u (h₃f.mem_toFinset.mp hu))]
  have hgzero : (∮ z in C(c, R), deriv g z / g z) = 0 := by
    refine DiffContOnCl.circleIntegral_eq_zero hR.le ?_          -- CauchyIntegral.lean:459
    exact hlogg.differentiableOn.diffContOnCl_ball subset_rfl
    -- `DifferentiableOn.diffContOnCl_ball (hf : DifferentiableOn 𝕜 f U)
    --    (hc : closedBall c R ⊆ U) : DiffContOnCl 𝕜 f (ball c R)`
    -- — Analysis/Calculus/DiffContOnCl.lean:127, instantiated at `U := closedBall c R`.
  have hNeq : (∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u)
      = ∑ u ∈ h₃f.toFinset, MeromorphicOn.divisor f (Metric.closedBall c R) u := by
    -- S1AP-SEAM: the two carriers give the SAME function.  On the ball both
    -- sides are `(meromorphicOrderAt f u).untop₀`; off the ball the ball-divisor
    -- is `0` by :197, and the closed-ball divisor is `0` either because `u` is on
    -- the sphere (`hDsph`) or because `u ∉ closedBall` (:197 again).
    have hDeq : ∀ u : ℂ, MeromorphicOn.divisor f (Metric.ball c R) u
        = MeromorphicOn.divisor f (Metric.closedBall c R) u := by
      intro u
      by_cases hu : u ∈ Metric.ball c R
      · rw [MeromorphicOn.divisor_apply (hf.mono hballCB).meromorphicOn hu,   -- :68
          MeromorphicOn.divisor_apply hmero (hballCB hu)]
      · rw [(MeromorphicOn.divisor f (Metric.ball c R)).apply_eq_zero_of_notMem hu]
        by_cases hu' : u ∈ Metric.closedBall c R
        · refine (hDsph u ?_).symm
          have h1 : dist u c ≤ R := Metric.mem_closedBall.mp hu'
          have h2 : ¬ dist u c < R := fun h => hu (Metric.mem_ball.mpr h)
          exact Metric.mem_sphere.mpr (le_antisymm h1 (not_lt.mp h2))
        · rw [(MeromorphicOn.divisor f (Metric.closedBall c R)).apply_eq_zero_of_notMem hu']
    exact (finsum_congr hDeq).trans (finsum_eq_sum_of_support_subset _ hsuppD)
    -- `finsum_congr` / `finsum_eq_sum_of_support_subset` are the `to_additive`
    -- twins of `finprod_congr` (Finprod.lean:239) and
    -- `finprod_eq_prod_of_mulSupport_subset` (:353).
  have hsum : (∑ u ∈ h₃f.toFinset, ∮ z in C(c, R),
        (MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ) * (z - u)⁻¹)
      = ∑ u ∈ h₃f.toFinset,
          (MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ)
            * (2 * Real.pi * Complex.I) :=
    Finset.sum_congr rfl hterm
  rw [circleIntegral.integral_congr hR.le hkey,                  -- :425
    circleIntegral.integral_add hint₁ hint₂,                     -- :451
    circleIntegral.integral_fun_sum                              -- :461
      (fun u hu => ContinuousOn.circleIntegrable hR.le (hcont₁ u hu)),
    hsum, hgzero, add_zero, hNeq, ← Finset.sum_mul, ← Int.cast_sum]
  -- `Finset.sum_mul` — Algebra/BigOperators/Ring/Finset.lean:56;
  -- `Int.cast_sum` — Algebra/BigOperators/Ring/Finset.lean:377 (S1AP-CAST).
  exact mul_comm _ _
  -- FALLBACK for the whole closing chain, if `rw` stalls on
  -- `circleIntegral.integral_fun_sum` (its `f` is a two-argument metavariable and
  -- the match is higher-order) — exact alternative text pinning `f`:
  --   rw [circleIntegral.integral_fun_sum
  --     (f := fun (u : ℂ) (z : ℂ) =>
  --       (MeromorphicOn.divisor f (Metric.closedBall c R) u : ℂ) * (z - u)⁻¹)
  --     (fun u hu => ContinuousOn.circleIntegrable hR.le (hcont₁ u hu))]
  -- FALLBACK for the final cast/commutation step, if the two `rw`s misfire:
  --   rw [hNeq]; push_cast [Finset.sum_mul]; ring

/-! ## A3. Zero-detector `[GEN]` `[PIN]` — corollary 1

Contract §2 A3. -/

/-- The circle integral of `deriv f / f` vanishes exactly when `f` has no zero in
the open disc.

`hR : 0 < R` IS REQUIRED FOR TRUTH HERE TOO. The A2 witness refutes A3 directly:
at `f = id`, `c = 0`, `R = -1` both hypotheses are vacuous, the right side is
vacuously TRUE (`ball 0 (-1) = ∅`) and the left side is FALSE (the integral is
`2πI ≠ 0`). An `iff` with a false left and a true right is false. -/
theorem Complex.circleIntegral_logDeriv_eq_zero_iff
    {f : ℂ → ℂ} {c : ℂ} {R : ℝ} (hR : 0 < R)
    (hf : AnalyticOnNhd ℂ f (Metric.closedBall c R))
    (hf₀ : ∀ z ∈ Metric.sphere c R, f z ≠ 0) :
    (∮ z in C(c, R), deriv f z / f z) = 0 ↔ ∀ z ∈ Metric.ball c R, f z ≠ 0 := by
  classical
  have hsphCB : Metric.sphere c R ⊆ Metric.closedBall c R := Metric.sphere_subset_closedBall
  have hballCB : Metric.ball c R ⊆ Metric.closedBall c R := Metric.ball_subset_closedBall
  have hCBconn : IsPreconnected (Metric.closedBall c R) := (convex_closedBall c R).isPreconnected
  have hfb : AnalyticOnNhd ℂ f (Metric.ball c R) := hf.mono hballCB
  -- The `≠ ⊤` supply again, now on the ball carrier; the seed still comes from
  -- the NONEMPTY sphere, i.e. from `0 < R`.
  obtain ⟨z₀, hz₀⟩ : (Metric.sphere c R).Nonempty := NormedSpace.sphere_nonempty.mpr hR.le
  have hord₀ : analyticOrderAt f z₀ ≠ ⊤ := by
    rw [(hf z₀ (hsphCB hz₀)).analyticOrderAt_eq_zero.mpr (hf₀ z₀ hz₀)]
    simp
  have h₂fb : ∀ u : Metric.ball c R, meromorphicOrderAt f ↑u ≠ ⊤ := by
    rintro ⟨u, hu⟩
    show meromorphicOrderAt f u ≠ ⊤
    rw [(hfb u hu).meromorphicOrderAt_eq]
    simpa using hf.analyticOrderAt_ne_top_of_isPreconnected hCBconn
      (hsphCB hz₀) (hballCB hu) hord₀
  -- Here the `U ∩ f ⁻¹' {0} = support …` orientation of :578 is the wanted one.
  have hzeroset : Metric.ball c R ∩ f ⁻¹' {0}
      = Function.support (⇑(MeromorphicOn.divisor f (Metric.ball c R))) :=
    hfb.meromorphicNFOn.zero_set_eq_divisor_support h₂fb
    -- `AnalyticOnNhd.meromorphicNFOn` — NormalForm.lean:567;
    -- `MeromorphicNFOn.zero_set_eq_divisor_support` — NormalForm.lean:578.
  have hfin : (MeromorphicOn.divisor f (Metric.ball c R)).support.Finite :=
    MeromorphicOn.divisor_ball_support_finite hf.meromorphicOn   -- Divisor.lean:104
  have hnn : ∀ u, 0 ≤ MeromorphicOn.divisor f (Metric.ball c R) u := fun u => by
    simpa using MeromorphicOn.AnalyticOnNhd.divisor_nonneg hfb u
    -- `MeromorphicOn.AnalyticOnNhd.divisor_nonneg` — Divisor.lean:177, FULLY
    -- QUALIFIED for the same namespace reason as :71 (built precedent
    -- repo:ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:412).
    -- `0 ≤ D` is the pointwise order of LocallyFinsupp.lean:401, so `… u` is a
    -- plain application; the `simpa` only clears `coe_zero` (:347).
    -- FALLBACK — exact alternative text:
    --   simpa using (Function.locallyFinsuppWithin.le_def.mp
    --     (MeromorphicOn.AnalyticOnNhd.divisor_nonneg hfb)) u
  have hsupp : Function.support (⇑(MeromorphicOn.divisor f (Metric.ball c R)))
      ⊆ ↑hfin.toFinset :=
    fun u hu => Finset.mem_coe.mpr (hfin.mem_toFinset.mpr hu)
  have hN : (∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u) = 0
      ↔ ∀ z ∈ Metric.ball c R, f z ≠ 0 := by
    rw [finsum_eq_sum_of_support_subset _ hsupp,
      Finset.sum_eq_zero_iff_of_nonneg (fun u _ => hnn u)]
    -- `Finset.sum_eq_zero_iff_of_nonneg` is the `to_additive` twin named at
    -- Algebra/Order/BigOperators/Group/Finset.lean:164 over
    -- `Finset.prod_eq_one_iff_of_one_le'` (:165) — S1AP-A3b.
    -- FALLBACK if that twin's name does not resolve — exact alternative text:
    --   rw [finsum_eq_sum_of_support_subset _ hsupp]
    --   rw [show (∑ u ∈ hfin.toFinset, MeromorphicOn.divisor f (Metric.ball c R) u) = 0
    --         ↔ ∀ u ∈ hfin.toFinset, MeromorphicOn.divisor f (Metric.ball c R) u = 0 from
    --       Finset.sum_eq_zero_iff_of_nonneg (fun u _ => hnn u)]
    constructor
    · intro hzero z hz hfz
      have hmem : z ∈ Function.support (⇑(MeromorphicOn.divisor f (Metric.ball c R))) := by
        rw [← hzeroset]
        exact ⟨hz, hfz⟩
      exact hmem (hzero z (hfin.mem_toFinset.mpr hmem))
    · intro hno u hu
      by_contra hcon
      have hmem : u ∈ Function.support (⇑(MeromorphicOn.divisor f (Metric.ball c R))) := hcon
      rw [← hzeroset] at hmem
      exact hno u hmem.1 hmem.2
  rw [Complex.circleIntegral_logDeriv_eq_divisor_sum hR hf hf₀, mul_eq_zero]
  simp only [Complex.two_pi_I_ne_zero, false_or, Int.cast_eq_zero]
  -- `Complex.two_pi_I_ne_zero : (2 * ↑π * I : ℂ) ≠ 0` —
  -- Analysis/SpecialFunctions/Complex/Log.lean:139, itself proved from
  -- `Real.pi_ne_zero` (Trigonometric/Basic.lean:165) and `Complex.I_ne_zero`
  -- (Data/Complex/Basic.lean:257).  `Int.cast_eq_zero` — Data/Int/Cast/Lemmas.lean:57,
  -- applicable because `ℂ` is `CharZero` (S1AP-A3a).
  exact hN
  -- FALLBACK if the `simp only` does not clear both disjuncts — exact
  -- alternative text replacing the last two lines:
  --   constructor
  --   · rintro (h | h)
  --     · exact absurd h Complex.two_pi_I_ne_zero
  --     · exact hN.mp (by exact_mod_cast h)
  --   · intro h
  --     exact Or.inr (by exact_mod_cast hN.mpr h)

/-! ## A4. Quantization `[GEN]` `[PIN]` — corollary 2

Contract §2 A4. -/

/-- The circle integral of `deriv f / f` lies in `2πI · ℕ`.

`hR : 0 < R` IS REQUIRED FOR TRUTH HERE TOO — and this corrects the stage-one
acceptance record, which judged A4's `0 < R` to be mere convenience. `∃ n : ℕ`
forbids a NEGATIVE count, and at `R < 0` the hypotheses are vacuous so `f` is
unconstrained and may carry a pole: at `f = fun z : ℂ => z⁻¹`, `c = 0`, `R = -1`
the contour has `‖z‖ = 1`, so `z ≠ 0` and `deriv f z / f z = -(z - 0)⁻¹`
(`deriv_inv`, Analysis/Calculus/Deriv/Inv.lean:66), giving `-(2πI)` by
CircleIntegral.lean:527 and :532. `2πI · (n : ℂ) = -2πI` has no natural-number
solution, so A4 is FALSE at `R = -1`. -/
theorem Complex.exists_nat_circleIntegral_logDeriv_eq
    {f : ℂ → ℂ} {c : ℂ} {R : ℝ} (hR : 0 < R)
    (hf : AnalyticOnNhd ℂ f (Metric.closedBall c R))
    (hf₀ : ∀ z ∈ Metric.sphere c R, f z ≠ 0) :
    ∃ n : ℕ, (∮ z in C(c, R), deriv f z / f z) = 2 * Real.pi * Complex.I * (n : ℂ) := by
  classical
  have hballCB : Metric.ball c R ⊆ Metric.closedBall c R := Metric.ball_subset_closedBall
  have hfb : AnalyticOnNhd ℂ f (Metric.ball c R) := hf.mono hballCB
  have hfin : (MeromorphicOn.divisor f (Metric.ball c R)).support.Finite :=
    MeromorphicOn.divisor_ball_support_finite hf.meromorphicOn   -- Divisor.lean:104
  have hnn : ∀ u, 0 ≤ MeromorphicOn.divisor f (Metric.ball c R) u := fun u => by
    simpa using MeromorphicOn.AnalyticOnNhd.divisor_nonneg hfb u -- Divisor.lean:177
  have hsupp : Function.support (⇑(MeromorphicOn.divisor f (Metric.ball c R)))
      ⊆ ↑hfin.toFinset :=
    fun u hu => Finset.mem_coe.mpr (hfin.mem_toFinset.mpr hu)
  have hNnn : 0 ≤ ∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u := by
    rw [finsum_eq_sum_of_support_subset _ hsupp]
    exact Finset.sum_nonneg fun u _ => hnn u
    -- `Finset.sum_nonneg` is the `to_additive` twin named at
    -- Algebra/Order/BigOperators/Group/Finset.lean:119 over `Finset.one_le_prod'`
    -- (:120); it has no declaration line of its own.
  have hcast : ((∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u : ℤ) : ℂ)
      = (((∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u).toNat : ℕ) : ℂ) := by
    exact_mod_cast (Int.toNat_of_nonneg hNnn).symm
    -- `Int.toNat_of_nonneg : 0 ≤ a → ↑a.toNat = a`.  NO `Mathlib/` LOCATOR IS
    -- GIVEN, DELIBERATELY: the name is used 33 times inside Mathlib at the pin
    -- but is DECLARED NOWHERE under `Mathlib/` — it is a Lean-core `Int` lemma,
    -- and this file's rule is that a locator must be read before it is written.
    -- A stage-two implementer must confirm the name and argument order at
    -- elaboration time (contract §0, A4 dependency note).
    -- FALLBACK if the name has moved — exact alternative text:
    --   have h := Int.toNat_of_nonneg hNnn
    --   exact_mod_cast h.symm
    -- and, if `Int.toNat_of_nonneg` itself is unavailable, replace the whole
    -- `hcast`/witness construction by `Int.natAbs`:
    --   refine ⟨(∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u).natAbs, ?_⟩
    --   rw [Complex.circleIntegral_logDeriv_eq_divisor_sum hR hf hf₀]
    --   congr 1
    --   exact_mod_cast (Int.natAbs_of_nonneg hNnn).symm
  refine ⟨(∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u).toNat, ?_⟩
  rw [Complex.circleIntegral_logDeriv_eq_divisor_sum hR hf hf₀, hcast]
  -- Both sides are now syntactically equal, so `rw`'s trailing `rfl` closes the
  -- goal (S1AP-A4 is exactly this cast shuffle).
  -- FALLBACK if it does not — exact alternative text to append:
  --   ring
