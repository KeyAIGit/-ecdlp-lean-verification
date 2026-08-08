# Circle-only argument principle contract (UPSTREAM / Form A): draft v1.1

Status: **DRAFT v1.1 (2026-08-07) — non-built review artifact, offered for STAGE ONE
(INDEPENDENT CONTRACT ACCEPTANCE) ONLY. NOT Lean-checked.** No declaration below
has been elaborated; no `lake build` has been run against any of it. Under the one
invariant, the Lean kernel via CI is the sole judge of every statement in this
contract, and this document carries no kernel verdict of any kind. v1.1 folds in
the independent red-team audit of 2026-08-07 (Annex A: every `file:line` citation
re-verified at the pin; five corrections applied in place, none touching any of
the five public signatures; the four commissioned attack seams — boundary
nonvanishing, log-derivative integrability, divisor-sum finiteness, hidden
winding machinery — all held).

**Two-stage gate (same discipline as `MULTIPLICITY_CONTRACT.md`, restated in full
at the end of this file).** Stage one is *independent contract acceptance*: a
review of the statement surface W1, A1–A4 only. It produces **no built module, no
ledger row, no registry or axiom-audit entry, and no kernel verdict**. Stage two
is a **separate built promotion PR** whose verdict is delivered by CI. An
acceptance PR must not carry a promotion. The drafts-lane working file proposed
below (`drafts/ArgPrinciple.lean`) lies outside every lake target
(`lakefile.toml:2` declares `defaultTargets = ["Ecdlp", "ResearchOS"]`; the CI
build and no-incomplete-proof scan boundaries are as recorded at
`MULTIPLICITY_CONTRACT.md:17–23`), so **no green CI run on an acceptance PR is
evidence of anything about the draft.**

Working name: `drafts/ArgPrinciple.lean` (drafts lane; no module target). If it
is ever pursued as a Mathlib upstream PR instead, the pool's proposed home is
`Mathlib/Analysis/Complex/ArgumentPrinciple.lean` (`UPSTREAM_POOL.md` §7); that
choice is a maintainer negotiation and is not made here.

Statement surface: **W1, A1, A2, A3, A4** — **exactly 5 public signatures**,
every one spelled explicitly in a `lean` statement block in §2. No signature is
mandated in prose only. The package contains **zero `def`s** (see §1, decision
D2: the pool's proposed `Complex.zeroCount` def is deliberately dropped).

Scope: **route-neutral generic complex analysis**, drawn from the upstream pool
(`UPSTREAM_POOL.md` §7.1 "Form A — fix the contour to be a circle", and the
free-standing freebie flagged at §9). Every statement quantifies over an
arbitrary function `f : ℂ → ℂ` (A1 over `f g : 𝕜 → E`) with hypotheses on that
function alone. **No statement mentions `riemannZeta`, `riemannXi`, an
L-function, a critical strip, or any route.** This contract closes **no
barrier** of `MATHLIB_CAPABILITY_MAP.md`, selects and unparks **no route**, and
produces **no information about the truth of the Riemann Hypothesis.** The RH
queue (`tasks/RIEMANN_HYPOTHESIS.md`) remains the sole authority for that lane;
this document is an offered artifact, not an active task, and not authorization
to work anything.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0), verified
this session via `git -C /workspace/leanprover-community/mathlib4 rev-parse
HEAD`. Every `file:line` locator below was read from that exact tree **this
session** (paths relative to the `Mathlib/` root of the pin) unless prefixed
`repo:`. Nothing was carried over from `UPSTREAM_POOL.md` untested; §5 records
the two pool claims this contract was asked to re-verify, one of which needed a
**correction** (the warm-up's hypothesis, §5.2).

## Grounding and re-verification mandate (both pool claims re-checked)

- **Form A judged plausible from pinned Cauchy machinery** (`UPSTREAM_POOL.md`
  §7.1, §7.4, §9 rank 6): **re-verified**. Every ingredient of the §7.3 table
  that this contract consumes was re-read at the pin this session and appears
  with exact `file:line` in §0. The pool's "hardest step" call (the
  codiscreteness bridge) survives re-examination and is isolated here as its
  own statement (A1) with a fully-named lemma chain — see obligation
  **S1AP-BRIDGE**.
- **The docstring-flagged gap dischargeable via the pinned Cauchy theorem**:
  **re-verified with a correction.** The gap is real: the module docstring of
  `Mathlib/MeasureTheory/Integral/CircleIntegral.lean` (lines 54–56) says of
  the case `n = -1`, `w` outside: *"it is easier to apply Cauchy theorem, so we
  postpone the proof till we have this theorem (see …pull/10000)"*, and Cauchy
  on a disc **is** at the pin (`DiffContOnCl.circleIntegral_eq_zero`,
  `Analysis/Complex/CauchyIntegral.lean:459`, read verbatim this session). But
  the pool's proposed signature (`hw : w ∉ Metric.closedBall c R`) is **false
  as stated** for `R < 0`, and the Cauchy route alone covers only `0 ≤ R`.
  Details, counterexample (itself pinned), and the corrected hypothesis in
  §5.2; the corrected statement is W1.
- **Form B (genuine winding index) is months away** (`UPSTREAM_POOL.md` §7.2,
  §7.4): **inherited, not re-verified here**, and irrelevant to this contract:
  nothing below defines, needs, or approximates a winding number, an index, a
  homotopy invariance statement, or a `curveIntegral`↔`circleIntegral` bridge.
  Any step that starts to need one is a death condition (§Death conditions, 5).

## Candidate fields

- **Mechanism.** With the contour fixed to a circle the index never has to be
  defined: it is `2πI` inside (`circleIntegral.integral_sub_inv_of_mem_ball`,
  CircleIntegral.lean:699) and `0` outside (W1, the warm-up this contract
  states, closing the library's own documented gap). The zero count is not a
  new definition either: it is `∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u`,
  the finsum of Mathlib's own divisor (Divisor.lean:39), finite on compacts by
  `divisor_ball_support_finite` (Divisor.lean:104) — finiteness is a
  *theorem*, never a hypothesis (pool caveat §7.5, honored). The engine is
  `MeromorphicOn.extract_zeros_poles` (FactorizedRational.lean:291): `f` agrees
  codiscretely with `(∏ᶠ u, (· - u) ^ divisor u) • g`, `g` analytic and
  nonvanishing. The single genuinely new move (A1) upgrades that codiscrete
  agreement to a `𝓝 x`-eventual equality at every accumulation point, via the
  pinned chain `mem_codiscreteWithin_accPt` (DiscreteSubset.lean:217) →
  `accPt_sup` (ClusterPt.lean:190) → `accPt_iff_frequently_nhdsNE`
  (ClusterPt.lean:217) → `AnalyticAt.frequently_eq_iff_eventually_eq`
  (IsolatedZeros.lean:141). From there `deriv f / f` is computed pointwise on
  the sphere by the `logDeriv` calculus (LogDeriv.lean:37/:54/:73/:87), the
  circle integral splits by `circleIntegral.integral_fun_sum`
  (CircleIntegral.lean:461), the zero terms each give `2πI`
  (CircleIntegral.lean:699), and the `g` term dies by Cauchy
  (CauchyIntegral.lean:459).
- **Expected information gain.** A reusable, route-neutral disc-counting
  interface: the circle integral of the logarithmic derivative equals `2πI`
  times the divisor sum (A2); a zero-detector (A3: integral vanishes iff no
  zeros in the ball); and quantization (A4: the integral lies in
  `2πI · ℕ`). Plus W1, a few-line library-gap closure independent of the rest.
  No information about the truth of RH is produced.
- **Claim boundary.** All five statements are intended as unconditional
  consequences of pinned Mathlib theorems only — **no repo theorem is a
  prerequisite of any statement** (the repo's built `Mult.lean` is cited below
  strictly as *pattern precedent*, §4, never as a dependency). Nothing touches
  zero enumeration of any named function, growth bounds, counting-function
  estimates, Hadamard products, residue calculus, winding numbers, or any
  route's research obligation. Rouché is **deliberately absent** (§1, D3).
- **Death condition (stop rule).** Stop or split if a proof would need a new
  axiom, an unproved conjecture, a new definition, a winding index or homotopy
  machinery (Form B creep), a growth/counting bound, or a ζ/ξ instantiation;
  and do not restate W1 with the unsigned-radius hypothesis (§5.2 shows it
  false). Full list in §Death conditions.

Proposed module preamble (name-resolution review only):

```lean
import Mathlib.MeasureTheory.Integral.CircleIntegral   -- ∮, integral_sub_inv_of_mem_ball, :461, :538
import Mathlib.Analysis.Complex.CauchyIntegral         -- DiffContOnCl.circleIntegral_eq_zero (:459)
import Mathlib.Analysis.Meromorphic.Divisor            -- MeromorphicOn.divisor, ball/sphere finiteness
import Mathlib.Analysis.Meromorphic.FactorizedRational -- extract_zeros_poles (:291) + product API
import Mathlib.Analysis.Meromorphic.NormalForm         -- zero_set_eq_divisor_support (:578)
import Mathlib.Analysis.Analytic.IsolatedZeros         -- frequently_eq_iff_eventually_eq (:141)
import Mathlib.Analysis.Calculus.LogDeriv              -- logDeriv calculus (:37-:110)
import Mathlib.Analysis.SpecialFunctions.Complex.LogDeriv -- Complex.hasDerivAt_log (:37) [W1 only]

open Complex Metric Filter Function
open scoped Real Topology
```

Name-collision scan (grep over the pinned tree this session): **zero hits** for
all five proposed names — `integral_sub_inv_of_notMem_closedBall`,
`eventuallyEq_of_codiscreteWithin`, `circleIntegral_logDeriv_eq_divisor_sum`,
`circleIntegral_logDeriv_eq_zero_iff`, `exists_nat_circleIntegral_logDeriv_eq` —
and zero hits for any `argument principle` / `windingNumber` development
(consistent with `UPSTREAM_POOL.md` §0 row 6). A repo-side scan of
`drafts/` shows no `ArgPrinciple.lean`.

---

## 0. Exact pinned interface (quoted from the tree at the pin, this session)

```lean
-- MeasureTheory/Integral/CircleIntegral.lean
-- :54-56 (module docstring): "The case n = -1, |w - c| > R is not covered by these
--   lemmas. While it is possible to construct an explicit primitive, it is easier to
--   apply Cauchy theorem, so we postpone the proof till we have this theorem
--   (see https://github.com/leanprover-community/mathlib4/pull/10000)."  ← the W1 gap
def CircleIntegrable (f : ℂ → E) (c : ℂ) (R : ℝ) : Prop                       -- :176
theorem deriv_circleMap (c : ℂ) (R : ℝ) (θ : ℝ) :
    deriv (circleMap c R) θ = circleMap 0 R θ * I                             -- :129
@[simp] theorem circleIntegrable_neg_radius {c : ℂ} {R : ℝ} {f : ℂ → E} : …   -- :292
theorem ContinuousOn.circleIntegrable {f : ℂ → E} {c : ℂ} {R : ℝ} (hR : 0 ≤ R) … -- :337
theorem integral_congr {f g : ℂ → E} {c : ℂ} {R : ℝ} (hR : 0 ≤ R)
    (h : EqOn f g (sphere c R)) : …                                           -- :425
theorem integral_add … (hf : CircleIntegrable f c R) (hg : CircleIntegrable g c R) : … -- :451
theorem integral_fun_sum {ι : Type*} {s : Finset ι} {f : ι → ℂ → E} {c : ℂ} {R : ℝ}
    (h : ∀ i ∈ s, CircleIntegrable (f i) c R) :
    (∮ z in C(c, R), ∑ i ∈ s, f i z) = ∑ i ∈ s, ∮ z in C(c, R), f i z         -- :461
@[simp] theorem integral_const_mul (a : ℂ) (f : ℂ → ℂ) (c : ℂ) (R : ℝ) : …    -- :527
@[simp] theorem integral_sub_center_inv (c : ℂ) {R : ℝ} (hR : R ≠ 0) :
    (∮ z in C(c, R), (z - c)⁻¹) = 2 * π * I                                   -- :532  ← §5.2 witness
theorem integral_eq_zero_of_hasDerivWithinAt' [CompleteSpace E] {f f' : ℂ → E} {c : ℂ}
    {R : ℝ} (h : ∀ z ∈ sphere c |R|, HasDerivWithinAt f (f' z) (sphere c |R|) z) :
    (∮ z in C(c, R), f' z) = 0     -- :538 — NOTE: valid for ALL real R, sphere is |R|
theorem integral_sub_zpow_of_undef {n : ℤ} {c w : ℂ} {R : ℝ} (hn : n < 0)
    (hw : w ∈ sphere c |R|) : (∮ z in C(c, R), (z - w) ^ n) = 0               -- :557
theorem integral_sub_zpow_of_ne {n : ℤ} (hn : n ≠ -1) (c w : ℂ) (R : ℝ) : … = 0 -- :566
theorem integral_sub_inv_of_mem_ball {c w : ℂ} {R : ℝ} (hw : w ∈ ball c R) :
    (∮ z in C(c, R), (z - w)⁻¹) = 2 * π * I                                   -- :699
-- namespace circleIntegral spans :419-:584 (containing :425-:566) and reopens at :696
-- for :699 (both block boundaries read this session — Annex A, F1); all names above
-- except CircleIntegrable/deriv_circleMap/circleIntegrable* are circleIntegral.*
-- (ContinuousOn.circleIntegrable is a root-level dot name).

-- Analysis/Complex/CauchyIntegral.lean
theorem circleIntegral_eq_zero_of_differentiable_on_off_countable {R : ℝ} (h0 : 0 ≤ R)
    {f : ℂ → E} {c : ℂ} {s : Set ℂ} (hs : s.Countable) … : (∮ z in C(c, R), f z) = 0 -- :440
theorem _root_.DiffContOnCl.circleIntegral_eq_zero {R : ℝ} (h0 : 0 ≤ R) {f : ℂ → E}
    {c : ℂ} (hc : DiffContOnCl ℂ f (ball c R)) : ∮ z in C(c, R), f z = 0      -- :459

-- Analysis/Meromorphic/Divisor.lean  (namespace MeromorphicOn spans :28-:468; naming
-- trap as recorded at MULTIPLICITY_CONTRACT.md §1 — :68/:71/:177 AND :91/:104 need the
-- MeromorphicOn. prefix; only :83 below is declared _root_. At use sites, dot notation
-- on an `hf : MeromorphicOn …` argument discharges :91/:104. — Annex A, F2)
noncomputable def divisor (f : 𝕜 → E) (U : Set 𝕜) :
    Function.locallyFinsuppWithin U ℤ                                         -- :39 (TOTAL)
lemma divisor_apply {f : 𝕜 → E} (hf : MeromorphicOn f U) (hz : z ∈ U) :
    divisor f U z = (meromorphicOrderAt f z).untop₀                           -- :68
lemma AnalyticOnNhd.divisor_apply … :
    divisor f U z = ((analyticOrderAt f z).map (↑)).untop₀                    -- :71
lemma _root_.divisor_sphere_support_finite [ProperSpace 𝕜] …                  -- :83
lemma divisor_support_finite_of_subset {f : 𝕜 → E} {V : Set 𝕜} (hf : MeromorphicOn f U)
    (hU : IsCompact U) (hV : V ⊆ U) : (divisor f V).support.Finite            -- :91
lemma divisor_ball_support_finite [ProperSpace 𝕜] {f : 𝕜 → E} {R : ℝ} {c : 𝕜}
    (hf : MeromorphicOn f (Metric.closedBall c R)) :
    (divisor f (Metric.ball c R)).support.Finite                              -- :104
theorem AnalyticOnNhd.divisor_nonneg {f : 𝕜 → E} (hf : AnalyticOnNhd 𝕜 f U) :
    0 ≤ MeromorphicOn.divisor f U                                             -- :177

-- Analysis/Meromorphic/FactorizedRational.lean (no IsOpen hypothesis anywhere:
-- section variables at :35-38 are only 𝕜, E, U : Set 𝕜)
lemma Function.FactorizedRational.mulSupport (d : 𝕜 → ℤ) :
    (fun u ↦ (· - u) ^ d u).mulSupport = d.support                            -- :52
lemma Function.FactorizedRational.finprod_eq_fun {d : 𝕜 → ℤ} (h : d.HasFiniteSupport) :
    (∏ᶠ u, (· - u) ^ d u) = fun x ↦ ∏ᶠ u, (x - u) ^ d u                       -- :67
theorem Function.FactorizedRational.analyticAt {d : 𝕜 → ℤ} {x : 𝕜} (h : 0 ≤ d x) :
    AnalyticAt 𝕜 (∏ᶠ u, (· - u) ^ d u) x                                      -- :81
theorem Function.FactorizedRational.ne_zero {d : 𝕜 → ℤ} {x : 𝕜} (h : d x = 0) :
    (∏ᶠ u, (· - u) ^ d u) x ≠ 0                                               -- :94
theorem MeromorphicOn.extract_zeros_poles {f : 𝕜 → E} (h₁f : MeromorphicOn f U)
    (h₂f : ∀ u : U, meromorphicOrderAt f u ≠ ⊤) (h₃f : (divisor f U).support.Finite) :
    ∃ g : 𝕜 → E, AnalyticOnNhd 𝕜 g U ∧ (∀ u : U, g u ≠ 0) ∧
      f =ᶠ[codiscreteWithin U] (∏ᶠ u, (· - u) ^ divisor f U u) • g            -- :291

-- Analysis/Meromorphic/NormalForm.lean (root names, no namespace block)
theorem AnalyticOnNhd.meromorphicNFOn (h₁f : AnalyticOnNhd 𝕜 f U) : MeromorphicNFOn f U -- :567
theorem MeromorphicNFOn.zero_set_eq_divisor_support (h₁f : MeromorphicNFOn f U)
    (h₂f : ∀ u : U, meromorphicOrderAt f u ≠ ⊤) :
    U ∩ f ⁻¹' {0} = Function.support (MeromorphicOn.divisor f U)              -- :578

-- Analysis/Meromorphic/Basic.lean, Analysis/Meromorphic/Order.lean
lemma AnalyticOnNhd.meromorphicOn (hf : AnalyticOnNhd 𝕜 f U) : MeromorphicOn f U -- Basic:475
lemma AnalyticAt.meromorphicOrderAt_eq (hf : AnalyticAt 𝕜 f x) :
    meromorphicOrderAt f x = (analyticOrderAt f x).map (↑)                    -- Order:279

-- Analysis/Analytic/Order.lean (as re-verified at MULTIPLICITY_CONTRACT.md §0)
protected lemma AnalyticAt.analyticOrderAt_eq_zero … :
    analyticOrderAt f z₀ = 0 ↔ f z₀ ≠ 0                                       -- :133
protected lemma AnalyticAt.analyticOrderAt_ne_zero … :
    analyticOrderAt f z₀ ≠ 0 ↔ f z₀ = 0                                       -- :137
theorem AnalyticOnNhd.analyticOrderAt_ne_top_of_isPreconnected {x y : 𝕜}
    (hf : AnalyticOnNhd 𝕜 f U) (hU : IsPreconnected U) (h₁x : x ∈ U) (hy : y ∈ U)
    (h₂x : analyticOrderAt f x ≠ ⊤) : analyticOrderAt f y ≠ ⊤                 -- :624

-- Analysis/Analytic/IsolatedZeros.lean
theorem AnalyticAt.frequently_zero_iff_eventually_zero {f : 𝕜 → E} {w : 𝕜}
    (hf : AnalyticAt 𝕜 f w) : (∃ᶠ z in 𝓝[≠] w, f z = 0) ↔ ∀ᶠ z in 𝓝 w, f z = 0 -- :136
theorem AnalyticAt.frequently_eq_iff_eventually_eq (hf : AnalyticAt 𝕜 f z₀)
    (hg : AnalyticAt 𝕜 g z₀) :
    (∃ᶠ z in 𝓝[≠] z₀, f z = g z) ↔ ∀ᶠ z in 𝓝 z₀, f z = g z                    -- :141

-- Topology/DiscreteSubset.lean
def Filter.codiscreteWithin (S : Set X) : Filter X := ⨆ x ∈ S, 𝓝[S \ {x}] x   -- :201
lemma mem_codiscreteWithin {S T : Set X} :
    S ∈ codiscreteWithin T ↔ ∀ x ∈ T, Disjoint (𝓝[≠] x) (𝓟 (T \ S))           -- :203
lemma mem_codiscreteWithin_accPt {S T : Set X} :
    S ∈ codiscreteWithin T ↔ ∀ x ∈ T, ¬AccPt x (𝓟 (T \ S))                    -- :217

-- Topology/ClusterPt.lean, Topology/Defs/Filter.lean
def AccPt (x : X) (F : Filter X) : Prop                                       -- Defs/Filter:271
theorem accPt_sup {x : X} {F G : Filter X} : …                                -- ClusterPt:190
theorem accPt_iff_frequently_nhdsNE {x : X} {C : Set X} : …                   -- ClusterPt:217
theorem AccPt.mono {F G : Filter X} (h : AccPt x F) (hFG : F ≤ G) : AccPt x G -- ClusterPt:230 (Annex A, F5)
theorem mem_closure_iff_nhdsWithin_neBot : x ∈ closure s ↔ NeBot (𝓝[s] x)     -- ClusterPt:261

-- Analysis/Calculus/LogDeriv.lean, Analysis/Calculus/Deriv/Basic.lean
def logDeriv (f : 𝕜 → 𝕜')                                                     -- LogDeriv:34
theorem logDeriv_apply (f : 𝕜 → 𝕜') (x : 𝕜) : logDeriv f x = deriv f x / f x := rfl -- :37
theorem logDeriv_mul … (hf : f x ≠ 0) (hg : g x ≠ 0) …                        -- :54
theorem logDeriv_prod {ι} {s : Finset ι} {f : ι → 𝕜 → 𝕜'} {x : 𝕜}
    (hf : ∀ i ∈ s, f i x ≠ 0) …                                               -- :73
lemma logDeriv_fun_zpow {f : 𝕜 → 𝕜'} {x : 𝕜} (hdf : DifferentiableAt 𝕜 f x) (n : ℤ) :
    logDeriv (f · ^ n) x = n * logDeriv f x                                   -- :87
theorem Filter.EventuallyEq.deriv_eq (hL : f₁ =ᶠ[𝓝 x] f) : deriv f₁ x = deriv f x -- Deriv/Basic:647
theorem Filter.EventuallyEq.eq_of_nhds {f g : X → α} (h : f =ᶠ[𝓝 x] g) : f x = g x
                                                 -- Topology/Neighborhoods.lean:153 (Annex A, F3)

-- Analysis/Calculus/FDeriv/Analytic.lean
protected theorem AnalyticOnNhd.deriv [CompleteSpace F] (h : AnalyticOnNhd 𝕜 f s) : … -- :441
@[fun_prop] protected theorem AnalyticAt.deriv [CompleteSpace F] (h : AnalyticAt 𝕜 f x) : … -- :457

-- Geometry / topology of the disc
theorem closure_ball (x : E) {r : ℝ} (hr : r ≠ 0) :
    closure (ball x r) = closedBall x r          -- Analysis/Normed/Module/RCLike/Real.lean:59
theorem NormedSpace.sphere_nonempty {x : E} {r : ℝ} :
    (sphere x r).Nonempty ↔ 0 ≤ r                -- Analysis/Normed/Module/RCLike/Real.lean:128
theorem convex_closedBall (a : E) (r : ℝ) : Convex ℝ (closedBall a r)
                                                 -- Analysis/Normed/Module/Convex.lean:71
protected theorem Convex.isPreconnected {s : Set E} (h : Convex ℝ s) : IsPreconnected s
                                                 -- Analysis/Convex/PathConnected.lean:93
isCompact_closedBall (ProperSpace field)         -- Topology/MetricSpace/ProperSpace.lean:40-42

-- Finiteness / finsum plumbing
theorem Function.locallyFinsuppWithin.finiteSupport [T2Space X] [Zero Y]
    (D : locallyFinsuppWithin U Y) (hU : IsCompact U) : Set.Finite D.support
                                                 -- Topology/LocallyFinsupp.lean:254
def Function.HasFiniteMulSupport (f : α → M) : Prop := f.mulSupport.Finite
    -- Algebra/FiniteSupport/Defs.lean:28; @[to_additive] twin HasFiniteSupport = support.Finite
theorem finprod_eq_prod_of_mulSupport_subset (f : α → M) {s : Finset α}
    (h : mulSupport f ⊆ s) : …                   -- Algebra/BigOperators/Finprod.lean:354
    -- @[to_additive] twin: finsum_eq_sum_of_support_subset (the idiom Mathlib itself
    -- uses to sum divisors on compacts, Analysis/Complex/JensenFormula.lean:238/:256)
@[to_additive sum_eq_zero_iff_of_nonneg] …       -- Algebra/Order/BigOperators/Group/Finset.lean:164

-- W1-only ingredients (primitive route)
def Complex.slitPlane : Set ℂ := {z | 0 < z.re ∨ z.im ≠ 0}   -- Analysis/Complex/Basic.lean:634
lemma Complex.hasDerivAt_log {z : ℂ} (hz : z ∈ slitPlane) : HasDerivAt log z⁻¹ z
    -- Analysis/SpecialFunctions/Complex/LogDeriv.lean:37 (namespace Complex opens :27)

-- Scalars
theorem Real.pi_ne_zero : π ≠ 0        -- Analysis/SpecialFunctions/Trigonometric/Basic.lean:165
@[simp] lemma Complex.I_ne_zero : (I : ℂ) ≠ 0                 -- Data/Complex/Basic.lean:257
lemma smul_eq_mul {α : Type*} [Mul α] (a b : α) : a • b = a * b := rfl
    -- Algebra/Group/Action/Defs.lean:74 — the E = ℂ smul/mul seam of A2 step 4 (Annex A, F4)
```

---

## 1. Design decisions

**D1 — circle only (Form A), by construction.** No `def` of an index, a path,
a cycle, or a homotopy class appears anywhere. The two facts a winding number
would encode are already theorems at the pin for circles:
`circleIntegral.integral_sub_inv_of_mem_ball` (:699, inside ⇒ `2πI`) and — after
W1 — the outside ⇒ `0` case. This is exactly the Form A/Form B split of
`UPSTREAM_POOL.md` §7; Form B is out of scope and guarded by death condition 5.

**D2 — no `zeroCount` def.** The pool sketched
`noncomputable def Complex.zeroCount f c R : ℤ := ∑ᶠ u, divisor f (ball c R) u`.
Dropped. The finsum is written inline in A2–A4. Reasons: (i) the repo's contract
discipline is zero-`def` packages (`MULTIPLICITY_CONTRACT.md` death condition
7); (ii) a def is precisely the design surface a Mathlib maintainer is entitled
to reject (`UPSTREAM_POOL.md` §11.2), and an inline finsum keeps the statements
rebindable under any future upstream naming; (iii) Mathlib's own Jensen
development already sums this exact finsum inline
(`JensenFormula.lean:307-310`), so the inline form is the *native* idiom at the
pin. Recorded as **DEFERRED-AP1**.

**D3 — no Rouché.** The pool listed a Rouché signature under Form A. It does
**not** genuinely fall out of A2 and is therefore excluded rather than forced.
Honest accounting: Rouché needs, beyond A2, a comparison argument along the
segment `t ↦ f + t·(g - f)` — integer-valuedness of the normalized integral
*as a function of a parameter*, continuity of `t ↦ ∮ logDeriv (f + t(g-f))`,
and discreteness of `2πI·ℤ` to conclude constancy. None of that is assembly of
A2-shaped pieces; it is a small parameterized-integral development
(continuity of circle integrals in a parameter is not among the §0
ingredients). Forcing it in would roughly double the surface and import the
one genuinely un-pinned analytic step. Recorded as **DEFERRED-AP2**, together
with the pool's weighted form `∮ g · f'/f = 2πI Σ d(u)·g(u)` (**DEFERRED-AP3**,
which additionally needs the Cauchy integral formula step
`circleIntegral_sub_inv_smul_of_differentiable_on_off_countable`-style, a
second seam this draft does not open).

**D4 — the divisor sum is taken on the open ball; hypotheses live on the
closed ball.** `hf : AnalyticOnNhd ℂ f (closedBall c R)` is the contract's
rendering of "analytic on a neighbourhood of the closed disc" (pointwise
`AnalyticAt` at every point of the compact — no open-superset variable to
negotiate). The counted zeros are `divisor f (ball c R)`, matching
`divisor_ball_support_finite` (:104). The sphere is zero-free by `hf₀`, so
nothing is lost at the seam; the CB-vs-ball bookkeeping is obligation
**S1AP-SEAM** (LOW), discharged pointwise by `MeromorphicOn.divisor_apply`
(:68) on both sides — the same one-bridge-lemma pattern the built `Mult.lean`
uses (§4).

**D5 — finiteness is concluded, never assumed** (pool caveat §7.5). No
statement below hypothesizes "finitely many zeros", an enumeration, or a
`Finset` of zeros. Finiteness enters only as
`divisor_ball_support_finite`/`locallyFinsuppWithin.finiteSupport` applied to
the compact closed ball.

---

## 2. Statement list W1, A1 – A4

Legend: `[PIN]` provable from pinned Mathlib alone; `[GEN]` generic, natural
Mathlib upstream candidate. (No statement carries a repo prerequisite; the
`[CONJ]`-style package tags of the multiplicity contract do not occur here.)

---

### W1. The docstring-flagged gap: `(z - w)⁻¹` integrates to zero when `w` is outside `[GEN]` `[PIN]` — *the warm-up*

#### Statement

```lean
theorem circleIntegral.integral_sub_inv_of_notMem_closedBall {c w : ℂ} {R : ℝ}
    (hw : w ∉ Metric.closedBall c |R|) :
    (∮ z in C(c, R), (z - w)⁻¹) = 0
```

**Hypothesis is `|R|`, not `R` — this is a soundness correction to the pool's
sketch, not a style choice.** See §5.2: with `w ∉ closedBall c R` the statement
is *false* at `R < 0`, by the pinned `circleIntegral.integral_sub_center_inv`
(CircleIntegral.lean:532). The `|R|` form matches the file's own convention for
its integrability lemmas (`sphere c |R|` at :557, :538).

#### Proof skeleton (primitive route — uniform in the sign of `R`)

```lean
  -- w outside the closed |R|-ball: |R| < dist w c, so c ≠ w and z ≠ w on the sphere
  have hcw : c - w ≠ 0 := sub_ne_zero.2 (by
    intro h; exact hw (by simp [h, Metric.mem_closedBall, abs_nonneg]))
  apply circleIntegral.integral_eq_zero_of_hasDerivWithinAt'   -- :538, sphere c |R|, any R
  intro z hz
  -- the primitive: F z = Complex.log ((z - w) / (c - w));
  -- (z - w)/(c - w) = 1 + (z - c)/(c - w) with ‖(z - c)/(c - w)‖ = |R|/dist c w < 1,
  -- hence re > 0, hence membership in slitPlane, hence log differentiates.
  have hmem : (z - w) / (c - w) ∈ Complex.slitPlane := by
    left
    -- re (1 + q) ≥ 1 - ‖q‖ > 0 for ‖q‖ < 1; via Complex.abs_re_le_norm and the
    -- sphere bound ‖z - c‖ = |R| < dist w c = ‖w - c‖
    sorry -- (skeleton hole at stage one; see S1AP-W1b)
  have hd : HasDerivAt (fun u : ℂ => Complex.log ((u - w) / (c - w))) (z - w)⁻¹ z := by
    have h₁ := (Complex.hasDerivAt_log hmem).comp z
      (((hasDerivAt_id z).sub_const w).div_const (c - w))
    -- chain-rule constant: ((z-w)/(c-w))⁻¹ * (c-w)⁻¹ … = (z-w)⁻¹, by field_simp
    -- with hcw and (z - w) ≠ 0 (z on the sphere, w strictly outside)
    sorry -- (skeleton hole at stage one; see S1AP-W1a)
  exact hd.hasDerivWithinAt
```

*Alternative route (Cauchy, `0 ≤ R` only — the route the docstring itself
anticipates and the pool cited).* For `0 ≤ R`:
`fun z => (z - w)⁻¹` is `DiffContOnCl ℂ · (ball c R)` (differentiable wherever
`z ≠ w`, and `w ∉ closedBall c R = closure (ball c R)` for `R > 0` via
`closure_ball` RCLike/Real.lean:59; `R = 0` by
`circleIntegral.integral_radius_zero`), so
`DiffContOnCl.circleIntegral_eq_zero` (CauchyIntegral.lean:459, `h0 : 0 ≤ R`)
closes it. For `R < 0` this route needs an `∮`-level sign-flip lemma
(`∮ … C(c,R) = ∮ … C(c,|R|)`) that **does not exist at the pin** — only the
integrand-level `circleIntegrable_neg_radius` (:292) does, whose proof pattern
(periodic shift by `π`, :292–:296) is the template if the reparametrization
lemma is ever wanted. That is exactly why the primitive route is primary.

#### Pinned dependencies (W1)

`circleIntegral.integral_eq_zero_of_hasDerivWithinAt'` — CircleIntegral.lean:538
(read verbatim: quantifies over `sphere c |R|`, no sign hypothesis on `R`;
`[CompleteSpace E]`, satisfied by `E = ℂ`);
`Complex.hasDerivAt_log` — SpecialFunctions/Complex/LogDeriv.lean:37;
`Complex.slitPlane` — Analysis/Complex/Basic.lean:634;
`closure_ball` — RCLike/Real.lean:59 (alternative route);
`DiffContOnCl.circleIntegral_eq_zero` — CauchyIntegral.lean:459 (alternative
route); `circleIntegrable_neg_radius` — CircleIntegral.lean:292 (pattern only).

#### Obligations (W1)

- **S1AP-W1a** (MEDIUM). The chain-rule arithmetic
  `((z-w)/(c-w))⁻¹ * (c-w)⁻¹ = (z-w)⁻¹` under `hcw` and `z ≠ w`; `HasDerivAt.comp`
  associates the composition as `log ∘ (affine)`, and the affine derivative is
  produced by `((hasDerivAt_id z).sub_const w).div_const (c - w)`. Fallback:
  differentiate `fun u => Complex.log ((u - w) * (c - w)⁻¹)` instead
  (`.mul_const`), or split `Complex.log` of a quotient is *not* needed — only
  the derivative is, so no `log_div` branch analysis arises.
- **S1AP-W1b** (MEDIUM). The slitPlane membership: from
  `‖z - c‖ = |R| < dist w c` derive `0 < ((z - w)/(c - w)).re` by writing the
  quotient as `1 + (z - c)/(c - w)` and using `|re q| ≤ ‖q‖`
  (`Complex.abs_re_le_norm`). Pure norm arithmetic; fallback is a direct
  `Complex.ext`-free estimate `re (1 + q) = 1 + re q ≥ 1 - ‖q‖`.
- **S1AP-W1c** (LOW). `z ≠ w` for `z ∈ sphere c |R|`: `dist z c = |R| < dist w c`.
- **S1AP-W1d** (LOW, informational). If this is ever offered upstream, the
  maintainers may prefer the `0 ≤ R` + Cauchy form to match PR #10000's framing;
  both routes are recorded so the statement shape can follow review.

---

### A1. Codiscrete agreement upgrades to local agreement at an accumulation point `[GEN]` `[PIN]` — *the bridge*

#### Statement

```lean
theorem AnalyticAt.eventuallyEq_of_codiscreteWithin
    {𝕜 : Type*} [NontriviallyNormedField 𝕜]
    {E : Type*} [NormedAddCommGroup E] [NormedSpace 𝕜 E]
    {f g : 𝕜 → E} {U : Set 𝕜} {x : 𝕜}
    (hf : AnalyticAt 𝕜 f x) (hg : AnalyticAt 𝕜 g x)
    (hxU : x ∈ U) (hacc : AccPt x (𝓟 U))
    (h : f =ᶠ[Filter.codiscreteWithin U] g) :
    f =ᶠ[𝓝 x] g
```

This is the pool's named hardest step ("codiscrete agreement ⇒ pointwise
`deriv f / f` on the sphere", §7.4) isolated into one generic statement. Its
consequences at `x` — value equality (`Filter.EventuallyEq.eq_of_nhds`,
Topology/Neighborhoods.lean:153 — locator added, Annex A F3) and derivative
equality (`Filter.EventuallyEq.deriv_eq`, Deriv/Basic.lean:647) — are consumed
inline in A2 and are not separate public statements.

#### Proof skeleton

```lean
  -- 1. Split U along the agreement set S := {z | f z = g z}.
  --    h : S ∈ codiscreteWithin U; mem_codiscreteWithin_accPt (DiscreteSubset.lean:217)
  --    at x ∈ U gives  ¬ AccPt x (𝓟 (U \ S)).
  -- 2. U ⊆ (U ∩ S) ∪ (U \ S), so 𝓟 U ≤ 𝓟 (U ∩ S) ⊔ 𝓟 (U \ S) (principal mono/sup);
  --    accPt_sup (ClusterPt.lean:190) turns hacc into
  --    AccPt x (𝓟 (U ∩ S)) ∨ AccPt x (𝓟 (U \ S)), and step 1 kills the right disjunct.
  -- 3. accPt_iff_frequently_nhdsNE (ClusterPt.lean:217):
  --    ∃ᶠ z in 𝓝[≠] x, z ∈ U ∩ S — in particular ∃ᶠ z in 𝓝[≠] x, f z = g z.
  -- 4. hf.frequently_eq_iff_eventually_eq hg (IsolatedZeros.lean:141) upgrades the
  --    frequent agreement to ∀ᶠ z in 𝓝 x, f z = g z.
```

#### Pinned dependencies (A1)

`mem_codiscreteWithin_accPt` — Topology/DiscreteSubset.lean:217 (and the
`codiscreteWithin` def at :201, `mem_codiscreteWithin` at :203 as fallback);
`accPt_sup` — Topology/ClusterPt.lean:190;
`accPt_iff_frequently_nhdsNE` — Topology/ClusterPt.lean:217;
`AnalyticAt.frequently_eq_iff_eventually_eq` —
Analysis/Analytic/IsolatedZeros.lean:141 (verbatim signature quoted in §0).

#### Obligations (A1)

- **S1AP-BRIDGE** (**HIGH**). The whole statement. Every link is a named pinned
  lemma, but the filter algebra between them (EventuallyEq as set membership;
  `𝓟`-monotonicity through the `(U ∩ S) ∪ (U \ S)` split; `AccPt` unfolding
  conventions) is exactly the kind of glue where elaboration time is lost. This
  is the contract's riskiest item and it gates A2–A4. Fallbacks, in order:
  (i) replace step 2 by `AccPt.mono` (ClusterPt.lean:230, pinned — Annex A F5)
  through `U ⊆ (U ∩ S) ∪ (U \ S)` with `sup_principal`; (ii) work from
  `mem_codiscreteWithin` (:203) directly: `Disjoint (𝓝[≠] x) (𝓟 (U \ S))` plus
  `NeBot (𝓝[≠] x ⊓ 𝓟 U)` forces `NeBot (𝓝[≠] x ⊓ 𝓟 (U ∩ S))` by
  `inf_sup_left`-type lattice reasoning in `Filter`; (iii) if the generic form
  resists, specialize A1 to `𝕜 = ℂ`, `U = closedBall c R` and inline it into
  A2 — the generic statement is then dropped, A2–A4 survive unchanged, and the
  drop is recorded. **Do not** weaken A2 by *assuming* the factorization
  pointwise (death condition 6).
- **S1AP-A1a** (LOW). `AccPt` at the intended call sites exists: for
  `x ∈ sphere c R ⊆ closedBall c R`, `R > 0`,
  `x ∈ closedBall c R = closure (ball c R)` (`closure_ball`, RCLike/Real.lean:59)
  gives `NeBot (𝓝[ball c R] x)` (`mem_closure_iff_nhdsWithin_neBot`,
  ClusterPt.lean:261), and `ball c R ⊆ closedBall c R \ {x}` since `x ∉ ball`
  (it is on the sphere) — hence `AccPt x (𝓟 (closedBall c R))`. Fallback for
  interior points (not needed by A2): `𝓝[≠] x` is NeBot in a nontrivially
  normed field.

---

### A2. Circle-only argument principle, analytic case `[GEN]` `[PIN]` — *the main statement*

#### Statement

```lean
theorem Complex.circleIntegral_logDeriv_eq_divisor_sum
    {f : ℂ → ℂ} {c : ℂ} {R : ℝ} (hR : 0 < R)
    (hf : AnalyticOnNhd ℂ f (Metric.closedBall c R))
    (hf₀ : ∀ z ∈ Metric.sphere c R, f z ≠ 0) :
    (∮ z in C(c, R), deriv f z / f z)
      = 2 * Real.pi * Complex.I
          * ((∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u : ℤ) : ℂ)
```

`deriv f z / f z` is definitionally `logDeriv f z` (`logDeriv_apply`,
LogDeriv.lean:37, a `rfl`); the display form follows the pool sketch so the
statement reads without the `logDeriv` abbreviation. The divisor sum is a
finsum over the `FunLike` coercion of `MeromorphicOn.divisor f (ball c R) :
Function.locallyFinsuppWithin (ball c R) ℤ` — finite support is a *theorem*
(`divisor_ball_support_finite`, Divisor.lean:104), never a hypothesis (D5).

#### Proof skeleton

```lean
  -- Notation: CB := closedBall c R; sphere and ball as usual. E = ℂ, smul = mul.
  -- 0. Basic geometry: CB compact (isCompact_closedBall, ProperSpace ℂ),
  --    preconnected ((convex_closedBall c R).isPreconnected, Convex:71 / PathConnected:93),
  --    sphere nonempty (NormedSpace.sphere_nonempty.mpr hR.le, RCLike/Real:128).
  -- 1. hmero : MeromorphicOn f CB := hf.meromorphicOn                    (Basic:475)
  -- 2. h₂f : ∀ u : CB, meromorphicOrderAt f u ≠ ⊤ — pick z₀ ∈ sphere, f z₀ ≠ 0 (hf₀),
  --    so analyticOrderAt f z₀ = 0 (Order:133); propagate by
  --    analyticOrderAt_ne_top_of_isPreconnected (Order:624); convert carriers by
  --    AnalyticAt.meromorphicOrderAt_eq (Meromorphic/Order:279) + ENat.map_eq_top_iff
  --    (Data/ENat/Basic:526).                                            [S1AP-FIN]
  -- 3. h₃f : (divisor f CB).support.Finite :=
  --      (MeromorphicOn.divisor f CB).finiteSupport (isCompact_closedBall c R)
  --                                                             (LocallyFinsupp:254)
  -- 4. obtain ⟨g, hg, hg₀, hfg⟩ := hmero.extract_zeros_poles h₂f h₃f
  --      (FactorizedRational:291); write D := ⇑(divisor f CB), φ := ∏ᶠ u, (· - u) ^ D u.
  --      NOTE: hfg's RHS is `φ • g` (smul). With E = ℂ the pointwise identification
  --      with `φ * g` used in steps 6-7 is smul_eq_mul (Action/Defs:74, a rfl),
  --      applied through Pi.smul_apply.                                   [S1AP-SMUL]
  -- 5. Support location: D z = 0 for z ∈ sphere (divisor_apply :71 + Order:133 at hf₀);
  --    hence support D ⊆ ball, and every u ∈ support D has f u = 0
  --    (zero_set_eq_divisor_support, NormalForm:578, via hf.meromorphicNFOn :567).
  --                                                                      [S1AP-SUPP]
  -- 6. Sphere-side pointwise identity: for z ∈ sphere,
  --      f =ᶠ[𝓝 z] φ * g   -- A1 with hf z, (FactorizedRational.analyticAt :81 for φ at
  --                        -- D z = 0 ≤ …, divisor_nonneg :177) .mul (hg z …), plus
  --                        -- S1AP-A1a for the AccPt input and hfg for the codiscrete input
  --    hence deriv f z = deriv (φ * g) z (EventuallyEq.deriv_eq, Deriv/Basic:647)
  --    and f z = (φ * g) z, so
  --      deriv f z / f z = logDeriv (φ * g) z.
  -- 7. logDeriv expansion at z ∈ sphere:
  --      logDeriv (φ * g) z = ∑ u ∈ h₃f.toFinset, (D u : ℂ) * (z - u)⁻¹ + logDeriv g z
  --    via finprod_eq_prod_of_mulSupport_subset (Finprod:354) with
  --    FactorizedRational.mulSupport (:52); logDeriv_mul (:54) with
  --    φ z ≠ 0 (FactorizedRational.ne_zero :94 at D z = 0) and g z ≠ 0 (hg₀);
  --    logDeriv_prod (:73) with factors nonvanishing (z ∉ ball ∋ u); per factor
  --    logDeriv_fun_zpow (:87) and deriv (· - u) = 1.                    [S1AP-LOGD]
  -- 8. Rewrite under the integral: circleIntegral.integral_congr (:425, hR.le) with
  --    the EqOn from 6-7; split by integral_add (:451) and integral_fun_sum (:461)
  --    (integrability: ContinuousOn.circleIntegrable :337 — every term is continuous
  --    on the sphere).                                                   [S1AP-INT]
  -- 9. Zero terms: ∮ (D u : ℂ) * (z - u)⁻¹ = (D u) * 2πI by integral_const_mul (:527)
  --    and integral_sub_inv_of_mem_ball (:699), u ∈ ball by step 5.
  -- 10. g term: ∮ logDeriv g = 0 by DiffContOnCl.circleIntegral_eq_zero
  --     (CauchyIntegral:459, h0 := hR.le): logDeriv g is differentiable on ball
  --     (AnalyticAt.deriv :457 [CompleteSpace ℂ]; g ≠ 0) and continuous on
  --     closure (ball) = CB (closure_ball, RCLike/Real:59; AnalyticOnNhd.deriv :441).
  -- 11. Reassemble: ∑ u ∈ h₃f.toFinset, (D u) * 2πI = 2πI * (∑ᶠ u, divisor f (ball) u)
  --     via finsum_eq_sum_of_support_subset (Finprod:354 to_additive twin) and the
  --     CB-vs-ball pointwise seam (divisor_apply :68 on both carriers). [S1AP-SEAM]
```

#### Pinned dependencies (A2)

All of §0 except the W1-only block; the load-bearing ones by step:
extract_zeros_poles FactorizedRational.lean:291 (re-read this session: its
section carries **no `IsOpen U`** hypothesis — variables at :35–38 are bare
`𝕜, E, U : Set 𝕜` — so `U := closedBall c R` is legal);
finiteSupport LocallyFinsupp.lean:254; divisor_apply Divisor.lean:68/:71;
divisor_nonneg Divisor.lean:177; zero_set_eq_divisor_support
NormalForm.lean:578 (+ :567); Order.lean:133/:624;
Meromorphic/Order.lean:279; ENat/Basic.lean:526 (locator inherited from
`MULTIPLICITY_CONTRACT.md` §0, where it was adversarially re-verified);
A1 (this contract) + Deriv/Basic.lean:647;
FactorizedRational.lean:52/:67/:81/:94; Finprod.lean:354 and its
`to_additive` twin; LogDeriv.lean:37/:54/:73/:87;
CircleIntegral.lean:337/:425/:451/:461/:527/:699; CauchyIntegral.lean:459;
FDeriv/Analytic.lean:441/:457; RCLike/Real.lean:59/:128;
Convex.lean:71 + PathConnected.lean:93; ProperSpace.lean:40–42.

#### Obligations (A2)

- **S1AP-LOGD** (**HIGH**). Step 7, the `logDeriv` expansion of `φ * g` on the
  sphere. Every lemma is named and pinned, but the assembly crosses four
  seams in one rewrite chain: finprod→`Finset.prod` (with the `mulSupport`
  identification :52 and `Function.HasFiniteSupport` = `support.Finite` by
  `rfl`, FiniteSupport/Defs.lean:28), `logDeriv_mul`'s side conditions
  (including its differentiability binders as displayed at :54–58),
  `logDeriv_prod`'s per-factor nonvanishing, and `logDeriv_fun_zpow`'s
  `(f · ^ n)` lambda shape versus the `(· - u) ^ D u` factor shape. Fallback:
  prove the expansion by `Finset.induction` on `h₃f.toFinset` using
  `FactorizedRational.extractFactor` (:107) instead of `logDeriv_prod` — the
  pool's route (b), re-proving less of `extract_zeros_poles` than the pool
  feared because only the sphere-side identity is needed.
- **S1AP-BRIDGE** (**HIGH**, shared with A1). Step 6 consumes A1; if A1 falls to
  its fallback (iii), step 6 inlines it.
- **S1AP-FIN** (MEDIUM). Step 2, the `≠ ⊤` supply: three carrier hops
  (`ℕ∞`-order at a sphere point, preconnected propagation, `WithTop ℤ` via
  `.map (↑)`). Mirrors the S1M-FIN discharge pattern of the built `Mult.lean`
  (§4); the subtype binder `∀ u : ↥CB` needs the `obtain ⟨w, hw⟩ := u` idiom
  (cf. S1M-16d).
- **S1AP-INT** (MEDIUM). Step 8: `integral_congr` needs `EqOn` on
  `sphere c R` exactly, and the two integrability facts must be supplied
  *before* `integral_add` splits. Continuity of each summand on the sphere is
  from `f`/`g` analyticity and nonvanishing plus `u ∉ sphere`; fallback for the
  finset part is unfolding `circleIntegral` to
  `intervalIntegral.integral_finsetSum` (the proof of :461 is four lines and
  copyable).
- **S1AP-SUPP** (MEDIUM). Step 5: `zero_set_eq_divisor_support`'s conclusion is
  oriented `U ∩ f ⁻¹' {0} = support …` and is stated on the carrier `U`; the
  contract needs `support D ⊆ ball`, i.e. the complement direction at sphere
  points. Fallback: skip :578 entirely and argue pointwise — at `z ∈ sphere`,
  `divisor_apply` (:71) + `analyticOrderAt_eq_zero` (:133) give `D z = 0`
  directly, and `u ∈ support D → f u = 0` comes from `analyticOrderAt_ne_zero`
  (:137). (Then :578 is only needed for A3, where the ball carrier is used.)
- **S1AP-SEAM** (LOW). Step 11: `divisor f CB u = divisor f (ball) u` for
  `u ∈ ball` — two applications of `divisor_apply` (:68), meromorphy on the
  ball by `AnalyticOnNhd.mono` + `meromorphicOn`. Also the `ℤ → ℂ` cast
  through the `Finset.sum`.
- **S1AP-SMUL** (LOW, added by Annex A F4). Step 4's `hfg` concludes with
  `φ • g`, not `φ * g`: the smul/mul identification for `E = ℂ` is
  `smul_eq_mul` (Algebra/Group/Action/Defs.lean:74, a `rfl`) through
  `Pi.smul_apply`. One rewrite (or `show`), consumed before steps 6–7 and
  before every `AnalyticAt` instance on the product is assembled.
- **S1AP-CAST** (LOW). The final display `2 * Real.pi * Complex.I * ((… : ℤ) : ℂ)`:
  `Int.cast` push through `Finset.sum` (`Int.cast_sum`) and the
  `Real → ℂ` coercion on `π`. `push_cast`-shaped.

---

### A3. Zero-detector: the integral vanishes iff `f` has no zero in the ball `[GEN]` `[PIN]` — *corollary 1*

#### Statement

```lean
theorem Complex.circleIntegral_logDeriv_eq_zero_iff
    {f : ℂ → ℂ} {c : ℂ} {R : ℝ} (hR : 0 < R)
    (hf : AnalyticOnNhd ℂ f (Metric.closedBall c R))
    (hf₀ : ∀ z ∈ Metric.sphere c R, f z ≠ 0) :
    (∮ z in C(c, R), deriv f z / f z) = 0 ↔ ∀ z ∈ Metric.ball c R, f z ≠ 0
```

#### Proof skeleton

```lean
  -- Rewrite by A2. Then, with hb := hf.mono ball_subset_closedBall (Analytic/Basic:498):
  -- (⇐) no zeros in the ball: support (divisor f (ball)) = ball ∩ f ⁻¹' {0} = ∅ by
  --     zero_set_eq_divisor_support (NormalForm:578, on U := ball, via
  --     hb.meromorphicNFOn :567 and h₂f restricted), so the finsum is 0.
  -- (⇒) 2πI ≠ 0 (Real.pi_ne_zero Trigonometric/Basic:165, Complex.I_ne_zero
  --     Data/Complex/Basic:257, two_ne_zero) and Int.cast injectivity force
  --     ∑ᶠ u, divisor f (ball) u = 0; the divisor is nonneg (divisor_nonneg :177 on
  --     the ball carrier) with finite support (divisor_ball_support_finite :104), so
  --     finsum_eq_sum_of_support_subset + sum_eq_zero_iff_of_nonneg
  --     (Order/BigOperators/Group/Finset:164, to_additive) give divisor ≡ 0,
  --     i.e. empty support, i.e. ball ∩ f ⁻¹' {0} = ∅ by :578 again.
```

#### Pinned dependencies (A3)

A2; NormalForm.lean:567/:578 (on the ball carrier); Divisor.lean:104/:177;
Finprod.lean:354 (twin); Order/BigOperators/Group/Finset.lean:164 (twin);
`AnalyticOnNhd.mono` Analytic/Basic.lean:498 (locator inherited from
`MULTIPLICITY_CONTRACT.md` §0); Trigonometric/Basic.lean:165;
Data/Complex/Basic.lean:257.

#### Obligations (A3)

- **S1AP-A3a** (MEDIUM). The nonvanishing-cast chain
  `2 * π * I * (n : ℂ) = 0 → n = 0` (`mul_ne_zero` stack + `Int.cast_eq_zero`),
  and the `h₂f`-on-the-ball restriction for :578 (subtype binder again).
- **S1AP-A3b** (LOW). `sum_eq_zero_iff_of_nonneg` is the `to_additive` name
  generated at Finset.lean:164; if resolution stutters, sum over the explicit
  `h.toFinset` with `Finset.sum_eq_zero_iff_of_nonneg` spelled at use site.

---

### A4. Quantization: the integral lies in `2πI · ℕ` `[GEN]` `[PIN]` — *corollary 2*

#### Statement

```lean
theorem Complex.exists_nat_circleIntegral_logDeriv_eq
    {f : ℂ → ℂ} {c : ℂ} {R : ℝ} (hR : 0 < R)
    (hf : AnalyticOnNhd ℂ f (Metric.closedBall c R))
    (hf₀ : ∀ z ∈ Metric.sphere c R, f z ≠ 0) :
    ∃ n : ℕ, (∮ z in C(c, R), deriv f z / f z) = 2 * Real.pi * Complex.I * (n : ℂ)
```

#### Proof skeleton

```lean
  -- n := (∑ᶠ u, divisor f (ball c R) u).toNat. By A2 it suffices that the finsum is
  -- ≥ 0: divisor_nonneg (:177) on the ball + finite support (:104) +
  -- finsum_eq_sum_of_support_subset + Finset.sum_nonneg, then Int.toNat_of_nonneg.
```

#### Pinned dependencies (A4)

A2; Divisor.lean:104/:177; Finprod.lean:354 (twin); `Finset.sum_nonneg`,
`Int.toNat_of_nonneg` (core big-operators/order API, same files as A3's).

#### Obligations (A4)

- **S1AP-A4** (LOW). Cast shuffle `((n : ℤ) : ℂ) = (n : ℕ) → ℂ` under
  `Int.toNat_of_nonneg`; `push_cast`-shaped.

*Why A4 is worth a signature:* integer-valuedness of the normalized integral is
the exact engine a future Rouché (DEFERRED-AP2) would run on; stating it now
means the deferred item is a delta, not a redesign. It also gives the usable
one-liner "`∮ f'/f ≠ 0 → f has a zero in the ball`" together with A3.

---

## 3. Package precedent: the built `Mult.lean`, cited honestly

The merged divisor package
(repo:`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean`, built and
kernel-checked on `main`; promotion record in its header) is **pattern
precedent** for this contract in exactly three places, and **explicitly not
precedent** in a fourth:

1. **Consuming `MeromorphicOn.divisor` through the `_apply` bridge.**
   `Mult.lean:388–390` (`riemannXi_divisor_apply` via
   `MeromorphicOn.AnalyticOnNhd.divisor_apply`, Divisor.lean:71) is the built,
   kernel-checked instance of the one-bridge-lemma pattern steps 5 and 11 of
   A2 reuse, including the namespace trap (`MeromorphicOn.AnalyticOnNhd.…`
   fully qualified, dot notation does not resolve) that this contract inherits
   pre-solved.
2. **Effectivity and support identification.** `Mult.lean:410–412`
   (divisor_nonneg) and `Mult.lean:538–540`
   (`zero_set_eq_divisor_support` with its orientation and `≠ ⊤` hypothesis
   discipline) are the built patterns behind A2 step 5 and A3.
3. **The `≠ ⊤` finite-order discharge.** The S1M-FIN pattern (finite local
   order propagated through a preconnected carrier, then carried across
   `AnalyticAt.meromorphicOrderAt_eq`) is the template for A2 step 2
   (S1AP-FIN).
4. **NOT precedent: summing divisors.** `Mult.lean` proves **no** summation of
   any divisor — its own claim boundary says so in terms
   (`Mult.lean:983–984`: *"no `Finset` of zeros, no `⋃`/`∑` over zeros. What
   this file has is exactly LOCAL FINITENESS"*). The precedent for **summing a
   divisor over a compact** is pinned Mathlib itself, not the repo: Jensen's
   formula sums `∑ᶠ u, divisor f (closedBall c |R|) u * …`
   (JensenFormula.lean:307–310) through exactly the
   `finiteSupport`-on-a-compact + `finsum_eq_sum_of_support_subset` idiom
   (JensenFormula.lean:238/:256; LocallyFinsupp.lean:254; Finprod.lean:354)
   that A2 step 11 and A3/A4 use. Citing `Mult.lean` for the sums would be
   false; citing it for the divisor-interface handling is exact.

This asymmetry is also why this contract is *route-neutral by construction*:
the summation layer it adds exists at the pin only in generic form, and this
contract keeps it generic. Nothing here instantiates any statement at ζ or ξ,
and doing so is a death condition (below) — any such instantiation belongs to
a future, separately authorized, queue-governed contract.

---

## Obligation register

| ID | Statement | Severity | Content | Fallback recorded |
|---|---|---|---|---|
| **S1AP-BRIDGE** | A1 (gates A2–A4) | **HIGH** | codiscrete→`𝓝 x` upgrade: filter algebra between four named pinned lemmas (DiscreteSubset:217, ClusterPt:190/:217, IsolatedZeros:141) | yes (three routes, incl. inlining a ℂ-special case into A2) |
| **S1AP-LOGD** | A2 | **HIGH** | `logDeriv (φ * g)` expansion on the sphere: finprod→Finset seam, `logDeriv_mul/prod/fun_zpow` side conditions, lambda shapes | yes (induction via `extractFactor` :107 — pool route (b), sphere-side only) |
| S1AP-FIN | A2 | MEDIUM | `≠ ⊤` supply on the compact: Order:133 → :624 → Meromorphic/Order:279 + ENat:526; subtype binders | yes (Mult.lean S1M-FIN pattern) |
| S1AP-INT | A2 | MEDIUM | `integral_congr` EqOn shape + integrability before `integral_add`/`integral_fun_sum` | yes (unfold to `intervalIntegral.integral_finsetSum`, :461 proof copyable) |
| S1AP-SUPP | A2 | MEDIUM | support ⊆ ball and support ⊆ zeros; orientation of NormalForm:578 | yes (pointwise via :71 + :133/:137, bypassing :578 in A2) |
| S1AP-W1a | W1 | MEDIUM | chain-rule constant arithmetic for the log primitive | yes (`mul_const` variant) |
| S1AP-W1b | W1 | MEDIUM | slitPlane membership from the norm bound | yes (direct re-estimate) |
| S1AP-A3a | A3 | MEDIUM | `2πI·(n:ℂ) = 0 → n = 0` cast chain; ball-carrier `≠ ⊤` restriction | yes |
| S1AP-SEAM | A2 | LOW | CB-vs-ball divisor pointwise equality (Divisor:68 twice) | yes |
| S1AP-SMUL | A2 | LOW | `φ • g` vs `φ * g`: smul_eq_mul (Action/Defs:74, rfl) via Pi.smul_apply — Annex A F4 | yes (`show`/rewrite) |
| S1AP-CAST | A2 | LOW | `ℤ→ℂ` cast through the Finset sum | yes (`push_cast`) |
| S1AP-A1a | A1/A2 | LOW | `AccPt` at sphere points via `closure_ball` + ClusterPt:261 | yes |
| S1AP-W1c | W1 | LOW | `z ≠ w` on the sphere | yes |
| S1AP-W1d | W1 | LOW | (informational) upstream may prefer the `0 ≤ R` Cauchy form | n/a |
| S1AP-A3b | A3 | LOW | `to_additive` name resolution at Finset:164 | yes |
| S1AP-A4 | A4 | LOW | `toNat` cast shuffle | yes (`push_cast`) |

No obligation is analytic. Every analytic input — Cauchy–Goursat on the disc,
the interior circle integral, the zeros/poles factorization, isolated zeros,
divisor finiteness on compacts, the `logDeriv` calculus, and the complex `log`
derivative on the slit plane — is a quoted pinned theorem at
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, re-read this session. Nothing here
is claimed proved until the kernel checks it in a built PR after independent
review.

### Deferred items (explicitly out of this package)

- **DEFERRED-AP1** — a `zeroCount` def (dropped by D2; upstream design surface).
- **DEFERRED-AP2** — Rouché-style comparison (D3: needs parameterized-integral
  continuity + `2πI·ℤ` discreteness; does not fall out of A2; A4 is the piece
  of it that does).
- **DEFERRED-AP3** — the weighted/locating form `∮ g·f'/f` (D3: needs a Cauchy
  integral formula step this draft does not open).
- **DEFERRED-AP4** — an `∮`-level negative-radius reparametrization lemma
  (`∮ … C(c,R) = ∮ … C(c,|R|)`); pattern at CircleIntegral.lean:292–296. Not
  needed by W1's primary route.
- **DEFERRED-AP5** — the meromorphic-case argument principle (poles counted
  negatively; the pool's `MeromorphicOn.circleIntegral_logDeriv` sketch). The
  factorization engine (:291) already covers it, but the sphere-side `logDeriv`
  expansion gains a pole-factor case split, and the analytic case is the one
  with consumers in sight. A future delta, not a redesign.

---

## Claim boundary

- **This contract is an unbuilt statement surface.** Stage-one acceptance
  changes no barrier row, closes no queue task, and carries no kernel verdict.
- **No barrier is closed by building it either.** The barriers of
  `MATHLIB_CAPABILITY_MAP.md` are scoped to this repository's ζ/ξ layer; W1,
  A1–A4 quantify over arbitrary functions and mention no ζ, ξ, L-function, or
  strip. Generic machinery lowers the *cost* of some future exit; it never
  retires a row (the finding-A4 discipline of `MULTIPLICITY_CONTRACT.md`,
  inherited here verbatim). In particular this is **not** progress on
  `S1-GLOBAL-ZEROS`, whose row concerns zero *enumeration* for specific
  functions — A2's divisor sum is an integer attached to one disc, not an
  enumeration, an ordering, or a counting function `N(T)`.
- **No route is selected, advanced, or implied.** The RH queue
  (`tasks/RIEMANN_HYPOTHESIS.md`) is the lane authority;
  `repo/ECDLP_DECISION_SUBSTRATE.json` governs the ECDLP lane and currently
  selects no route; neither authorizes work from this document, and this
  document requests none.
- **No RH-truth claim.** Nothing here proves, disproves, or supplies evidence
  about the Riemann Hypothesis, and no consequence of W1/A1–A4 does either.
- **Upstream intent is optional and unowned.** If any part is offered to
  Mathlib, the timeline and design authority are Mathlib's
  (`UPSTREAM_POOL.md` §11.2); this contract binds only the repo-side drafts
  lane.

## Death conditions

Stop and re-plan — do **not** patch around — if any of the following occurs.

1. **A new axiom would be needed.** No `axiom`, no `sorry` in a built lane, no
   `admit`, no `native_decide` on an unproved side condition. The Lean kernel
   is the sole verifier.
2. **Any dependency on an unproved conjecture**, including as a hypothesis
   smuggled into a binder.
3. **A new definition becomes necessary.** The package must contain zero
   `def`s. If a `zeroCount`, an index, or a path/cycle type starts to look
   required, the item is DEFERRED-AP1/AP2 territory or belongs upstream as a
   negotiated design — stop, record, split.
4. **A ζ/ξ/L-function instantiation appears in this package.** Route
   neutrality is the licence under which this contract exists (header
   constraints of `UPSTREAM_POOL.md`); instantiating any statement at a named
   arithmetic function converts it into route work that nothing has
   authorized. A clean generic package plus a missing instantiation is the
   correct end state.
5. **Form B creep.** If any proof step starts to need a winding-number
   definition, homotopy invariance, a `curveIntegral`↔`circleIntegral` bridge,
   π₁ machinery, or null-homologous Cauchy — stop. That is the multi-month
   §7.2 project, and it does not begin as a side effect of a circle lemma.
6. **The bridge fails and a hypothesis is floated instead.** If S1AP-BRIDGE
   resists all three recorded routes, do **not** restate A2 with an assumed
   pointwise factorization, an assumed `EqOn`, or an assumed "finitely many
   zeros" (pool caveat §7.5) — record the blocker and stop. A clean blocker is
   preferable to a hollow theorem.
7. **A growth or counting bound is needed.** Jensen-type inequalities,
   `logCounting`, `N(T)`, or growth order of an entire function have no
   business in any of the five proofs; if one appears, the proof has drifted
   into a different pool item.
8. **W1 is restated with the unsigned-radius hypothesis.**
   `w ∉ Metric.closedBall c R` is a **false** premise-form at `R < 0` (§5.2,
   with a pinned counterexample witness); any draft carrying it must not
   proceed to elaboration.
9. **A barrier row or this contract is used as work authorization.** The RH
   queue is the authority; an accepted contract is a design, not a task.

---

## 5. Verification log (this session)

### 5.1 Pool claims re-verified as CORRECT

- CircleIntegral.lean **:54–56** docstring flags the `n = -1`, `w`-outside case
  and defers to Cauchy, citing PR #10000 — read verbatim (the pool cited
  ":50–56"; the operative sentence sits at :54–56 of the pin; same paragraph).
- `DiffContOnCl.circleIntegral_eq_zero` — CauchyIntegral.lean **:459**, exact
  signature quoted in §0; discharges the deferred case for `0 ≤ R`.
- `circleIntegral.integral_sub_inv_of_mem_ball` — **:699**;
  `integral_sub_zpow_of_undef`/`_of_ne` — **:557**/**:566**;
  `divisor_ball_support_finite` — **:104**; `extract_zeros_poles` — **:291**
  (with **no** open-set hypothesis, §0 note); `logDeriv_prod` — **:73**;
  `circleIntegral_congr_codiscreteWithin` — **:430** (present; not consumed by
  this contract — the deriv-side bridge A1 replaces it, as the pool's §7.4
  predicted it would have to; note its declaration sits *inside* the `:419`
  `namespace circleIntegral` block, so the full name is
  `circleIntegral.circleIntegral_congr_codiscreteWithin` — Annex A, F1).
- The pool's "hardest step" identification (codiscrete → pointwise on the
  sphere) is confirmed as the right risk locus; this contract adds the finding
  that every link of a discharge chain is individually pinned and named
  (DiscreteSubset:217, ClusterPt:190/:217/:261, IsolatedZeros:141,
  Deriv/Basic:647), which is why Form A is offered at contract level at all.

### 5.2 Correction to the pool (one defect found and fixed here)

`UPSTREAM_POOL.md` §7.1 proposes the warm-up as
`(hw : w ∉ Metric.closedBall c R) : (∮ z in C(c, R), (z - w)⁻¹) = 0`.
**This is false for `R < 0`.** Take `R = -1`, `w = c`: `Metric.closedBall c (-1)
= ∅`, so the hypothesis holds vacuously — yet the pinned
`circleIntegral.integral_sub_center_inv` (CircleIntegral.lean:532, hypothesis
only `R ≠ 0`) evaluates the integral to `2 * π * I ≠ 0`. The circle `C(c, R)`
has geometric radius `|R|`, and the file's own integrability lemmas are stated
on `sphere c |R|` (:538, :557). W1 therefore carries `w ∉ Metric.closedBall c
|R|`. Consequently the pool's "few-line addition via the Cauchy theorem" is
accurate for `0 ≤ R` only; the uniform statement uses the primitive route
(:538 + slitPlane log), which the docstring itself notes is possible. Neither
reading changes the difficulty class; the signature had to change.

### 5.3 Not verified, and stated as such

Nothing in this contract was elaborated; no statement is known to typecheck and
no skeleton is known to close. "Pinned" means *the named declaration exists in
the tree with the quoted signature text at the quoted line*, re-read this
session — it does not mean the assembly works. Form B's difficulty assessment
is inherited from the pool, not re-verified. The two `sorry` markers inside
W1's skeleton are stage-one display holes in a non-built document, not
proposed build content; a built PR containing them would violate death
condition 1 and the one invariant.

---

## Two-stage gate and promotion ordering

### Stage one — independent contract acceptance (what this document is offered for)

A reviewer accepts or rejects the statement surface W1, A1–A4: signatures,
hypothesis shapes (`|R|` in W1; `0 < R`, closed-ball analyticity, sphere
nonvanishing in A2–A4; the `AccPt`/membership pair in A1), the zero-`def`
discipline, the deferred-item boundary, and the death conditions. Acceptance
produces a review record only. It produces no built module, no `VERIFIED_*`
row, no registry entry, no axiom-audit entry, and no kernel verdict, and it
changes no barrier row and no queue state.

### Stage two — the separate built promotion PR (kernel verdict from CI)

If, and only if, work on this surface is separately authorized under the
repo's queue discipline, a stage-two PR carries the built module, its ledger
rows, the regenerated registry and axiom audit, and the promotion review
record; its verdict is delivered by CI under the one invariant (a green build
means every built theorem is fully proved; no `sorry`, no new axioms —
axiom base `standard`). An acceptance PR must not carry a promotion, and a
promotion must not cite this document as its authorization.

### What current CI does and does not say about the draft

`drafts/ArgPrinciple.lean`, if created, lies outside every lake target
(`lakefile.toml:2`), exactly as recorded for the drafts lane at
`MULTIPLICITY_CONTRACT.md:17–23`. No green CI run on a PR adding this contract
or that draft file is evidence about any statement in either.

---

## Annex A — red-team audit record (2026-08-07; all corrections applied in place above)

Independent adversarial audit of draft v1, commissioned with four attack
targets: the boundary-nonvanishing hypotheses, the log-derivative
integrability, the divisor-sum finiteness seam, and hidden dependence on
missing winding machinery. Method: every `file:line` locator in this contract
was re-read from the pinned tree (`git -C /workspace/leanprover-community/mathlib4
rev-parse HEAD` → `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, re-run this
audit session), namespace block boundaries were re-derived by grepping
`^namespace`/`^end` in every cited file, the five name-collision scans and the
`windingNumber`/`argument principle` absence scans were re-run (still zero
hits each), the repo-side citations (`lakefile.toml:2`,
`MULTIPLICITY_CONTRACT.md:17–23`, `Mult.lean:388–390/:410–412/:538–540/:983–984`,
absence of `drafts/ArgPrinciple.lean`) were re-read, and both grounding claims
were re-verified against `UPSTREAM_POOL.md` itself (§7.1 sketch at :616–:640 —
the pool's W1 premise is `w ∉ Metric.closedBall c R`, confirming §5.2's
correction is real and needed; §7.4/:702–:720 and §9 rank 6/:792 vs rank
8/:794 confirm the Form A "weeks" / Form B "months, multi-PR" split; §0 row 6
confirms the winding-absence table row). The §5.2 counterexample was
re-checked against the pin: `circleIntegral.integral_sub_center_inv`
(CircleIntegral.lean:532) carries exactly `hR : R ≠ 0`, so `R = -1`, `w = c`
refutes the pool's premise-form as claimed.

### A. Commissioned attack seams — all four held

1. **Boundary nonvanishing (A2–A4's `hf₀`).** Attacked for insufficiency
   (does sphere-only nonvanishing really supply the `≠ ⊤` order hypothesis on
   the whole closed ball?) and for vacuity (empty sphere). Both fail: for
   `0 < R` the sphere is nonempty (`NormedSpace.sphere_nonempty`,
   RCLike/Real.lean:128, re-read — its section carries a nontriviality
   hypothesis on `E`, satisfied by `ℂ`), a sphere point with `f z₀ ≠ 0` gives
   `analyticOrderAt f z₀ = 0` (Order.lean:133), and preconnectedness of the
   convex closed ball propagates `≠ ⊤` everywhere (Order.lean:624, confirmed
   inside `namespace AnalyticOnNhd`, :575–:700). The same `hf₀` then places
   `support D` strictly inside the open ball (step 5), which is what makes
   every downstream factor nonvanishing on the sphere. No weaker hypothesis
   supports the chain; no stronger one is smuggled in. **SOUND.**
2. **Log-derivative integrability (A2 step 8).** Attacked at the
   `integral_congr` → `integral_add` → `integral_fun_sum` order: `integral_congr`
   (:425, re-read) needs only `0 ≤ R` + `EqOn` on the sphere and **no**
   integrability of the `deriv f / f` side, so the rewrite legitimately
   precedes the splits; after it, every summand `(D u : ℂ) * (z - u)⁻¹` is
   continuous on the sphere (`u ∈ ball`, so `z ≠ u`) and `logDeriv g =
   deriv g / g` is continuous there (`AnalyticOnNhd.deriv`,
   FDeriv/Analytic.lean:441, `[CompleteSpace ℂ]`; `g` nonvanishing), so
   `ContinuousOn.circleIntegrable` (:337, root-level, `0 ≤ R`) supplies both
   integrability inputs. `integral_eq_zero_of_hasDerivWithinAt'` (:538, W1)
   was re-read: it internally `by_cases` on integrability, so W1 owes none.
   **SOUND.**
3. **Divisor-sum finiteness seam.** Attacked for hypothesis-smuggling (D5)
   and for a support mismatch in step 11. Neither lands: finiteness enters
   only as theorems (`divisor_ball_support_finite`, Divisor.lean:104,
   hypothesis exactly `MeromorphicOn f (closedBall c R)`, re-read;
   `Function.locallyFinsuppWithin.finiteSupport`, LocallyFinsupp.lean:254,
   namespace confirmed :119–:695), and the CB-vs-ball support inclusion is
   pointwise-checkable both ways: `divisor f (ball) u = divisor f CB u` on the
   ball (`divisor_apply` :68 twice — the `divisor` def at :39–:41 was re-read;
   its `toFun` guards on `MeromorphicOn f U ∧ z ∈ U`, so both carriers need
   their meromorphy, which `AnalyticOnNhd.mono` (Analytic/Basic.lean:498) +
   `meromorphicOn` (Meromorphic/Basic.lean:475) supply), zero off the ball by
   `supportWithinDomain`, zero on the sphere by step 5. The A2 display finsum
   is total (junk-0 on infinite support) but never vacuous under the
   hypotheses — finiteness is concluded before it is summed. Jensen precedent
   confirmed at the pin (JensenFormula.lean:238/:256/:307–:310 re-read;
   :307 sums `∑ᶠ u, divisor f (closedBall c |R|) u * …`). **SOUND.**
4. **Hidden winding machinery.** Attacked hardest at W1's primitive route
   (single-valuedness of the log primitive is exactly where a winding
   dependence would hide): the quotient `(z - w)/(c - w) = 1 + (z - c)/(c - w)`
   has norm-of-perturbation `|R| / dist c w < 1` for every sphere point, so
   the primitive's argument stays in the open right half-plane — a subset of
   `slitPlane` on which `Complex.hasDerivAt_log` (:37, namespace `Complex`
   opens :27, both re-read) is monodromy-free. No branch tracking, no index,
   no homotopy. A2's two integral evaluations are the circle-specific pinned
   theorems (:699, whose proof was re-read far enough to confirm it is a
   geometric-series `HasSum` argument, and CauchyIntegral.lean:459, whose
   `h0 : 0 ≤ R` is met by `hR.le`) — neither imports winding machinery, and
   the `∮`-level sign-flip lemma W1's alternative route would need for
   `R < 0` is correctly reported as absent at the pin (only the
   integrand-level :292 exists). Death condition 5 has no open flank.
   **SOUND.**

### B. Findings (5) — none touches a public signature

| # | Severity | Finding | Fix applied |
|---|---|---|---|
| F1 | locator | §0's namespace note read "reopens at :697"; the pinned block boundaries are `namespace circleIntegral` :419–:584 and :696–:718. Same scan found that `circleIntegral_congr_codiscreteWithin` (:430) sits *inside* the :419 block, so its full name carries the `circleIntegral.` prefix — §5.1's bare mention could mislead a future consumer. | §0 comment corrected; §5.1 mention annotated |
| F2 | completeness | The Divisor.lean naming-trap note listed :68/:71/:177 but not :91/:104, which also sit inside `namespace MeromorphicOn` (:28–:468, re-derived; only :83 is `_root_`-escaped). A3's dependency line cites `divisor_ball_support_finite` bare. | §0 note extended; dot-notation discharge recorded |
| F3 | missing pin | `EventuallyEq.eq_of_nhds` is consumed by A2 step 6 (via A1's commentary) but carried no locator — a house-style violation for a consumed lemma. Pinned: `Filter.EventuallyEq.eq_of_nhds`, Topology/Neighborhoods.lean:153. | added to §0 and to A1's commentary |
| F4 | unrecorded seam (LOW) | `extract_zeros_poles` (:291) concludes `f =ᶠ[…] (∏ᶠ …) • g` — **smul** — while A2 steps 6–7 and the mechanism prose compute with `φ * g`. For `E = ℂ` the identification is `smul_eq_mul` (Algebra/Group/Action/Defs.lean:74, a `rfl`) through `Pi.smul_apply`, but no obligation recorded the rewrite. | step-4 note added; obligation **S1AP-SMUL** (LOW) added to A2 and the register |
| F5 | missing pin | S1AP-BRIDGE fallback (i) invoked "`AccPt.mono`-style monotonicity" without verifying the lemma exists at the pin. It does: `AccPt.mono`, Topology/ClusterPt.lean:230, exactly the needed shape `AccPt x F → F ≤ G → AccPt x G` (also silently load-bearing for skeleton step 2's `𝓟`-monotonicity hop). | locator added to §0 and the fallback |

### C. Citations re-verified clean (spot list of the load-bearing ones)

CircleIntegral.lean :54–:56 (docstring sentence and PR-10000 link grep-anchored
at :54/:56 — the contract's span is exact; the pool's ":50–56" remains
same-paragraph), :129, :176, :292, :337, :425, :430, :451, :461, :527, :532
(`hR : R ≠ 0` — §5.2's witness), :538 (`sphere c |R|`, `[CompleteSpace E]`, no
sign hypothesis), :557, :566, :699; CauchyIntegral.lean :440/:459;
Divisor.lean :39/:68/:71/:83/:91/:104/:177; FactorizedRational.lean
:35–:38 (bare `U : Set 𝕜`, no `IsOpen` — confirmed), :52/:67/:81/:94/:107, and
:291 (**outside** the `Function.FactorizedRational` namespace, which closes at
:267 — so the bare name `MeromorphicOn.extract_zeros_poles` and the skeleton's
`hmero.extract_zeros_poles` dot call both resolve as written);
NormalForm.lean :567/:578; Meromorphic/Basic.lean :475; Meromorphic/Order.lean
:279; Analytic/Order.lean :133/:137 (root-level `protected AnalyticAt.*`) and
:624 (inside `namespace AnalyticOnNhd` :575–:700, matching the contract's
qualified name); IsolatedZeros.lean :136/:141 (inside `namespace AnalyticAt`
:120–:203); DiscreteSubset.lean :201/:203/:217; ClusterPt.lean
:190/:217/:230/:261; Defs/Filter.lean :271; LogDeriv.lean :34/:37 (`rfl`
confirmed)/:54 (differentiability binders confirmed as S1AP-LOGD describes)
/:73 (`(∏ i ∈ s, f i ·)` lambda shape confirmed)/:87; Deriv/Basic.lean :647;
Neighborhoods.lean :153; FDeriv/Analytic.lean :441/:457; RCLike/Real.lean
:59 (`hr : r ≠ 0`)/:128; Normed/Module/Convex.lean :71; Convex/PathConnected.lean
:93; ProperSpace.lean :40–:42; LocallyFinsupp.lean :254 (`[T2Space X]`);
FiniteSupport/Defs.lean :28; Finprod.lean :354 (+ `to_additive` twin);
Order/BigOperators/Group/Finset.lean :164 (`@[to_additive
sum_eq_zero_iff_of_nonneg]` attribute line, as the contract says);
Complex/Basic.lean :634; SpecialFunctions/Complex/LogDeriv.lean :27/:37;
Trigonometric/Basic.lean :165; Data/Complex/Basic.lean :257; ENat/Basic.lean
:526 (inside `namespace ENat` :53–:623); Analytic/Basic.lean :498;
JensenFormula.lean :238/:256/:307–:310; `circleIntegral.integral_radius_zero`
:422 (W1 alternative route). Repo side: `lakefile.toml:2`,
`MULTIPLICITY_CONTRACT.md:17–23`, all four `Mult.lean` precedent locators
including the :983–:984 claim-boundary quote, and `drafts/` contains no
`ArgPrinciple.lean`. **No stale locator was found beyond F1's two lines; no
cited signature deviated from its §0 quotation.**

### D. Statement-level truth review (audit opinion, not a kernel verdict)

W1 (in its corrected `|R|` form), A1, A2, A3, A4 were each checked for
mathematical truth under exactly the stated hypotheses, including the edge
cases `R = 0` (W1: sphere `{c}`, primitive still differentiates —
`(c-w)/(c-w) = 1 ∈ slitPlane`) and isolated points of `U` (A1: `hacc` is
genuinely necessary — a codiscrete agreement says nothing at an isolated
point, so dropping `hacc` would make A1 false; the hypothesis pair
`hxU`/`hacc` is minimal). No statement is false, vacuous, or
hypothesis-inflated as written. This is an audit opinion; under the one
invariant only a stage-two kernel run decides.

### E. Verdict

**PASS — ACCEPTED AS CORRECTED (v1.1), at stage-one review level only.**
Every citation resolves at pin `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`
with the quoted signature; the four commissioned attack seams held; the five
findings are locator/completeness-grade, are fixed in place above, and leave
all five public signatures byte-identical to draft v1. Both re-verification
mandates from the grounding were independently confirmed, including that the
pool's warm-up premise-form is false at `R < 0` and the contract's `|R|`
correction is forced. This annex closes no barrier, selects no route, claims
nothing about RH, and authorizes no work; it is a review record for stage-one
acceptance under the two-stage gate, and no statement in this file carries a
kernel verdict.
