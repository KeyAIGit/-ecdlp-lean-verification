# Circle-only argument principle contract (UPSTREAM / Form A): draft v1.2

Status: **DRAFT v1.2 (2026-08-09) — non-built review artifact, ACCEPTED AT STAGE ONE
(INDEPENDENT CONTRACT ACCEPTANCE) on 2026-08-08. NOT Lean-checked.** No declaration
below has been elaborated; no `lake build` has been run against any of it. Under the
one invariant, the Lean kernel via CI is the sole judge of every statement in this
contract, and this document carries no kernel verdict of any kind. v1.1 folded in
the independent red-team audit of 2026-08-07 (Annex A: every `file:line` citation
re-verified at the pin; five corrections applied in place, none touching any of
the five public signatures; the four commissioned attack seams — boundary
nonvanishing, log-derivative integrability, divisor-sum finiteness, hidden
winding machinery — all held).

**v1.2 (2026-08-09, RH-015) applies the editorial fixes enumerated by the
stage-one acceptance record `notes/reviews/ARG_PRINCIPLE_ACCEPTANCE_2026_08_08.md`
(three lenses, zero blocking findings, no lens asking for a signature change).
All five public signatures are BYTE-IDENTICAL to v1.0 and v1.1** — the acceptance
is only valid for the surface as it stands, so a signature edit here would
silently invalidate the acceptance it implements. What changed in v1.2 is prose,
locators, obligation severities, proof skeletons, deferred-item text, the claim
boundary, and the death conditions. Two of the applied fixes materially re-price
the package and both were re-confirmed against the pin before being applied
(§0 and §5.4): **A1 is no longer the package's hard step** (S1AP-BRIDGE
downgraded HIGH → LOW), and the `|R|` sign-flip previously reported as absent at
the pin **exists as mathematics** via `Real.circleAverage_abs_radius`. Two
enumerated fixes were **declined**, both recorded with reasons in §5.4: a
proposed rename of A1 and a proposed rename of W1 are signature changes, and
this pass does not make those.

**Two-stage gate (same discipline as `MULTIPLICITY_CONTRACT.md`, restated in full
at the end of this file).** Stage one is *independent contract acceptance*: a
review of the statement surface W1, A1–A4 only. It produces **no built module, no
ledger row, no registry or axiom-audit entry, and no kernel verdict**. Stage two
is a **separate built promotion PR** whose verdict is delivered by CI. An
acceptance PR must not carry a promotion. The drafts-lane working file proposed
below (`domains/riemann-hypothesis/drafts/ArgPrinciple.lean` — spelled in full
here because **there is no top-level `drafts/` directory in this repository**;
the drafts lane is `domains/riemann-hypothesis/drafts/`, which currently holds
eleven files. The bare `drafts/…` shorthand used later in this document is
inherited verbatim from `MULTIPLICITY_CONTRACT.md:17` and is the sibling
contracts' abbreviation, not a path. A stage-two author must create the file
under the full path; a file at a top-level `drafts/` would still be outside
every lake target, so the CI-scope argument below survives either reading, but
the file would be in the wrong lane) lies outside every lake target
(`lakefile.toml:2` declares `defaultTargets = ["Ecdlp", "ResearchOS"]`; the CI
build and no-incomplete-proof scan boundaries are as recorded at
`MULTIPLICITY_CONTRACT.md:17–23`), so **no green CI run on an acceptance PR is
evidence of anything about the draft.**

Working name: `domains/riemann-hypothesis/drafts/ArgPrinciple.lean` (drafts
lane; no module target). If it
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
L-function, a critical strip, or any route.** This contract **closes no barrier,
advances no barrier, and partially closes no barrier** of
`MATHLIB_CAPABILITY_MAP.md` — its capability-map effect is **INVENTORY ONLY** —
selects and unparks **no route**, bears on **no conjecture**, and provides **no
evidence for or against the Riemann Hypothesis** in either direction. The RH
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
  codiscreteness bridge) is isolated here as its own statement (A1) — but that
  call **does not survive re-examination and is retracted in v1.2**: the
  meromorphic form of exactly this bridge is already pinned
  (`MeromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin`,
  Meromorphic/IsolatedZeros.lean:99), and A1 is a short corollary of it. See
  §5.4 finding 1 and obligation **S1AP-BRIDGE**, downgraded to LOW.
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
  nonvanishing. A1 upgrades that codiscrete agreement to a `𝓝 x`-eventual
  equality at every accumulation point. **A1 is not a new move.** Mathlib
  already proves the meromorphic, punctured form of precisely this bridge —
  `MeromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin`
  (Meromorphic/IsolatedZeros.lean:99), whose four hypotheses are A1's four
  hypotheses with the strictly weaker `MeromorphicAt` in place of `AnalyticAt`,
  and whose section variables (:24–:27) are A1's binder context verbatim. The
  only delta is punctured → unpunctured: feed the pinned lemma through
  `AnalyticAt.meromorphicAt` (Meromorphic/Basic.lean:40), take `.frequently`
  (legitimate because `NormedField.nhdsNE_neBot`, Normed/Field/Basic.lean:242,
  is an `@[instance]` for `[NontriviallyNormedField 𝕜]` — exactly A1's
  typeclass, so no manual `NeBot` argument is needed), and close with
  `AnalyticAt.frequently_eq_iff_eventually_eq` (Analytic/IsolatedZeros.lean:141).
  That is a three-line term proof; see A1's skeleton and S1AP-BRIDGE (LOW).
  **The genuinely un-pinned content of this package is A2's assembly, not A1.**
  From there `deriv f / f` is computed pointwise on
  the sphere by the `logDeriv` calculus (LogDeriv.lean:37/:54/:73/:87), the
  circle integral splits by `circleIntegral.integral_fun_sum`
  (CircleIntegral.lean:461), the zero terms each give `2πI`
  (CircleIntegral.lean:699), and the `g` term dies by Cauchy
  (CauchyIntegral.lean:459).
- **Expected information gain.** A reusable, route-neutral disc-counting
  interface: the circle integral of the logarithmic derivative equals `2πI`
  times the divisor sum (A2); a zero-detector (A3: integral vanishes iff no
  zeros in the ball); and quantization (A4: the integral lies in
  `2πI · ℕ`). Plus W1, a self-contained library-gap closure independent of the
  rest (few-line via Cauchy for `0 ≤ R`; the uniform-sign statement adopted here
  costs more than "a few lines" on either recorded route — the log-primitive
  route carries S1AP-W1a/W1b and the Cauchy+flip route carries S1AP-W1e, see
  §2 W1 and §5.2). No information about the truth of RH is produced.
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
(consistent with `UPSTREAM_POOL.md` §0 row 6). A repo-side scan shows no
`ArgPrinciple.lean` anywhere in the repository; the drafts lane is
`domains/riemann-hypothesis/drafts/` (eleven files: HarnackDisc, MellinBound,
PolyLiouville, README, RiemannConj, RiemannGrowthOrder, RiemannMult,
RiemannTargetBridge, RiemannXi, ThreeCircles, ZeroSetSlice).

**What this scan does NOT establish, and the v1.2 correction that forced the
caveat.** A name-collision scan greps the five PROPOSED NAMES. It cannot detect
a **semantic duplicate living under a different name**, and in this package it
did not: `MeromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin`
(Meromorphic/IsolatedZeros.lean:99) is the pinned meromorphic form of A1 and
shares no name fragment with `eventuallyEq_of_codiscreteWithin`, so the scan
reported zero hits while the mathematics was already in the library. Zero name
hits therefore means "the proposed identifiers are free", never "the statement
is new". Whoever offers any of these upstream owes a separate SEMANTIC search
(by statement shape and by neighbouring-file reading, not by name) before
claiming novelty to a maintainer.

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
def circleIntegral (f : ℂ → E) (c : ℂ) (R : ℝ) : E :=
    ∫ θ : ℝ in 0..2 * π, deriv (circleMap c R) θ • f (circleMap c R θ)        -- :385
    -- notation ∮ z in C(c, R), … at :389; documented as ∮_{|z-c|=|R|} at :16/:60
@[simp] theorem integral_radius_zero (f : ℂ → E) (c : ℂ) : (∮ z in C(c, 0), f z) = 0 -- :422
theorem circleMap_neg_radius {r x : ℝ} {c : ℂ} :
    circleMap c (-r) x = circleMap c r (x + π)                                -- :162
theorem circleIntegral_congr_codiscreteWithin {c : ℂ} {R : ℝ} {f₁ f₂ : ℂ → ℂ}
    (hf : f₁ =ᶠ[codiscreteWithin (sphere c |R|)] f₂) (hR : R ≠ 0) :
    (∮ z in C(c, R), f₁ z) = (∮ z in C(c, R), f₂ z)                           -- :430
    -- ← inside the :419 block, so the full name is
    --   circleIntegral.circleIntegral_congr_codiscreteWithin (Annex A, F1).
    -- NOTE (v1.2): unlike integral_congr (:425, `hR : 0 ≤ R`), :430 carries only
    -- `R ≠ 0`, so it is the congruence lemma that survives NEGATIVE radii. That
    -- matters for the W1 Cauchy+flip route below (S1AP-W1e).
-- namespace circleIntegral spans :419-:584 (containing :425-:566) and reopens at :696
-- for :699 (both block boundaries read this session — Annex A, F1); all names above
-- except CircleIntegrable/deriv_circleMap/circleIntegrable*/circleIntegral/
-- circleMap_neg_radius are circleIntegral.* (ContinuousOn.circleIntegrable is a
-- root-level dot name).
-- ABSENCE, re-verified this pass by grepping `neg_radius|abs_radius` over the whole
-- file: CircleIntegral.lean contains NO ∮-level sign-flip lemma. The only radius-sign
-- lemmas here are circleMap_neg_radius (:162, pointwise on the parametrization) and
-- circleIntegrable_neg_radius (:292, integrand-level). See the CircleAverage block
-- below for where the ∮-level flip actually comes from.

-- MeasureTheory/Integral/CircleAverage.lean  ← ADDED v1.2. THE `|R|` FLIP LIVES HERE.
-- namespace Real spans :42-:382, so every name below is Real.circleAverage*.
-- Section variables at :36-:40: {E} [NormedAddCommGroup E] [NormedSpace ℝ E] … and
-- {f f₁ f₂ : ℂ → E} {c : ℂ} {R : ℝ}; the def carries `variable (f c R) in`, so f, c, R
-- are EXPLICIT on `circleAverage` itself.
noncomputable def circleAverage : E :=
    (2 * π)⁻¹ • ∫ θ in 0..2 * π, f (circleMap c R θ)                          -- :54
lemma circleAverage_eq_integral_add (η : ℝ) :
    circleAverage f c R = (2 * π)⁻¹ • ∫ θ in 0..2 * π, f (circleMap c R (θ + η)) -- :117
@[simp] theorem circleAverage_neg_radius :
    circleAverage f c (-R) = circleAverage f c R                              -- :129
@[simp] theorem circleAverage_abs_radius :
    circleAverage f c |R| = circleAverage f c R                               -- :135
theorem circleAverage_eq_circleIntegral {F : Type*} [NormedAddCommGroup F]
    [NormedSpace ℂ F] {f : ℂ → F} (h : R ≠ 0) :
    circleAverage f c R = (2 * π * I)⁻¹ • (∮ z in C(c, R), (z - c)⁻¹ • f z)   -- :96
-- READ :135 AND :96 TOGETHER. :135 is the sign flip, already proved, `@[simp]`.
-- :96 is the only bridge at the pin between circleAverage and circleIntegral, and it
-- inserts a `(z - c)⁻¹ •` weight; recovering a bare ∮ from it means running :96 at the
-- weighted integrand `fun z ↦ (z - c) • g z` and cancelling the weight along the path
-- (legitimate: c ∉ sphere c |R| for R ≠ 0). That cancellation cannot use :425
-- (`0 ≤ R`) precisely in the sign case the flip exists to handle; use :430 (`R ≠ 0`)
-- or unfold. Hence the v1.2 wording: the flip is PRESENT AS MATHEMATICS and ABSENT AS
-- A NAMED ∮ LEMMA, and its derivation is short but not free — see DEFERRED-AP4 and
-- obligation S1AP-W1e. The v1.1 claim that the flip "does not exist at the pin" is
-- withdrawn as misleading.

-- Analysis/Complex/CauchyIntegral.lean
theorem circleIntegral_eq_zero_of_differentiable_on_off_countable {R : ℝ} (h0 : 0 ≤ R)
    {f : ℂ → E} {c : ℂ} {s : Set ℂ} (hs : s.Countable) … : (∮ z in C(c, R), f z) = 0 -- :440
theorem _root_.DiffContOnCl.circleIntegral_eq_zero {R : ℝ} (h0 : 0 ≤ R) {f : ℂ → E}
    {c : ℂ} (hc : DiffContOnCl ℂ f (ball c R)) : ∮ z in C(c, R), f z = 0      -- :459

-- Analysis/Meromorphic/Divisor.lean  (namespace MeromorphicOn spans :28-:468, re-derived
-- this pass; naming trap as recorded at MULTIPLICITY_CONTRACT.md §1. THE TRAP HAS TWO
-- SIDES AND THE v1.1 NOTE BLURRED THEM (acceptance record, pin lens finding 4):
--   * :68 / :91 / :104 take a `MeromorphicOn` hypothesis. Dot notation on an
--     `hf : MeromorphicOn …` argument RESOLVES all three (`hf.divisor_apply`,
--     `hf.divisor_support_finite_of_subset`, `hf.divisor_ball_support_finite`).
--   * :71 (`AnalyticOnNhd.divisor_apply`) and :177 (`AnalyticOnNhd.divisor_nonneg`)
--     take an `AnalyticOnNhd` hypothesis but SIT INSIDE `namespace MeromorphicOn`
--     with no `_root_`. Dot notation on an `AnalyticOnNhd` hypothesis does NOT
--     resolve them — it looks for a root-level `AnalyticOnNhd.divisor_apply`, which
--     does not exist. The fully-qualified `MeromorphicOn.AnalyticOnNhd.divisor_apply`
--     / `MeromorphicOn.AnalyticOnNhd.divisor_nonneg` is MANDATORY. Built precedent,
--     kernel-checked on main: repo:ResearchOS/AnalyticNumberTheory/RiemannHypothesis/
--     Mult.lean:390 and :412 write exactly those two fully-qualified names.
--   * only :83 is `_root_`-escaped.
-- A2 steps 5 and 11, A3 and A4 all consume :71/:177, so this is the side that bites.
-- §3 point 1 states it correctly; this note now matches. — Annex A F2, extended v1.2)
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
-- section variables at :35-38 are only 𝕜, E, U : Set 𝕜.
-- DOCSTRING WARNING (acceptance record, truth lens finding 5, re-read this pass):
-- the docstring of :291 at :285-:290 begins "If `f` is meromorphic on an OPEN set
-- `U`, …". The binders carry no `IsOpen` and THE BINDERS GOVERN, so the use here
-- with `U := closedBall c R` is legal. A stage-two implementer will meet that
-- docstring and must not stall on it or conclude the use is illegitimate.)
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
-- (namespace AnalyticAt :120-:203, re-derived; :136 and :141 both inside it)

-- Analysis/Meromorphic/IsolatedZeros.lean  ← ADDED v1.2. THIS IS A1, ALREADY PROVED
-- AT THE PIN IN ITS MEROMORPHIC, PUNCTURED FORM. The v1.1 contract never cited this
-- file; that omission is what let A1 be priced as the package's HIGH-severity gate.
-- namespace MeromorphicAt spans :31-:130. Section variables at :24-:27 read
--   {𝕜 : Type*} [NontriviallyNormedField 𝕜]
--   {E : Type*} [NormedAddCommGroup E] [NormedSpace 𝕜 E]
--   {U : Set 𝕜} {x : 𝕜} {f g : 𝕜 → E}
-- which is A1's binder context verbatim (A1 orders {f g}/{U}/{x} differently; all
-- four are implicit, so the contexts are the same context).
theorem eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin (hf : MeromorphicAt f x)
    (hg : MeromorphicAt g x) (h₁x : x ∈ U) (h₂x : AccPt x (𝓟 U))
    (h : f =ᶠ[codiscreteWithin U] g) :
    f =ᶠ[𝓝[≠] x] g                                                            -- :99
--   ^ NOTE THE SHAPE DIFFERENCE THAT IS THE WHOLE DELTA TO A1: this concludes in the
--     PUNCTURED filter 𝓝[≠] x; A1 concludes in the UNPUNCTURED 𝓝 x. Hypotheses are
--     identical up to AnalyticAt ⇒ MeromorphicAt (strictly weaker here, so free).
theorem eventuallyEq_zero_nhdsNE_of_eventuallyEq_zero_codiscreteWithin
    (hf : MeromorphicAt f x) (h₁x : x ∈ U) (h₂x : AccPt x (𝓟 U))
    (h : f =ᶠ[codiscreteWithin U] 0) : f =ᶠ[𝓝[≠] x] 0                         -- :59
theorem frequently_eq_iff_eventuallyEq (hf : MeromorphicAt f x)
    (hg : MeromorphicAt g x) :
    (∃ᶠ z in 𝓝[≠] x, f z = g z) ↔ f =ᶠ[𝓝[≠] x] g                              -- :88
theorem eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin_preperfect
    (hf : MeromorphicAt f x) (hg : MeromorphicAt g x) (hx : x ∈ U)
    (hU : Preperfect U) (h : f =ᶠ[codiscreteWithin U] g) : f =ᶠ[𝓝[≠] x] g     -- :109
theorem eventually_nhdsSet_eventuallyEq_codiscreteWithin (hf : MeromorphicOn f U)
    (hg : MeromorphicOn g U) (hU : Preperfect U) (h : f =ᶠ[codiscreteWithin U] g) :
    ∀ᶠ x in 𝓝ˢ U, f =ᶠ[𝓝[≠] x] g                                              -- :118

-- The two remaining ingredients of A1's three-line discharge (ADDED v1.2)
@[fun_prop] lemma AnalyticAt.meromorphicAt {f : 𝕜 → E} {x : 𝕜} (hf : AnalyticAt 𝕜 f x) :
    MeromorphicAt f x            -- Analysis/Meromorphic/Basic.lean:40 (root level)
@[instance] theorem nhdsNE_neBot (x : α) : NeBot (𝓝[≠] x)
    -- Analysis/Normed/Field/Basic.lean:242, inside `namespace NormedField` (:193-),
    -- section `Nontrivially` with `variable (α) [NontriviallyNormedField α]` and
    -- `variable {α}` re-hiding α at :239. IT IS AN INSTANCE and its typeclass is
    -- exactly A1's, so `Filter.Eventually.frequently` (Order/Filter/Basic.lean:756,
    -- `[NeBot f]`) fires on 𝓝[≠] x with NO manual NeBot argument in A1's proof.

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
-- :54 AND :73 ARE QUOTED IN FULL (v1.2, acceptance record pin lens finding 1). The
-- v1.1 elisions here hid an EXPLICIT POSITIONAL argument and two DifferentiableAt
-- binders; every other elision in this §0 hides only implicits. `(x : 𝕜)` is
-- EXPLICIT in logDeriv_mul and PRECEDES hf, so a call written `logDeriv_mul hφ hg …`
-- is wrong by one argument.
theorem logDeriv_mul {f g : 𝕜 → 𝕜'} (x : 𝕜) (hf : f x ≠ 0) (hg : g x ≠ 0)
    (hdf : DifferentiableAt 𝕜 f x) (hdg : DifferentiableAt 𝕜 g x) :
      logDeriv (fun z => f z * g z) x = logDeriv f x + logDeriv g x           -- :54-:56
theorem logDeriv_prod {ι : Type*} {s : Finset ι} {f : ι → 𝕜 → 𝕜'} {x : 𝕜}
    (hf : ∀ i ∈ s, f i x ≠ 0) (hd : ∀ i ∈ s, DifferentiableAt 𝕜 (f i) x) :
    logDeriv (∏ i ∈ s, f i ·) x = ∑ i ∈ s, logDeriv (f i) x                   -- :73-:75
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

-- W1 skeleton auxiliaries — ADDED v1.2 (acceptance record, pin lens finding 3: these
-- were consumed by S1AP-W1a/W1b prose with no file:line, contrary to the house rule
-- Annex A F3 enforced for EventuallyEq.eq_of_nhds). All five opened this pass; two of
-- them are load-bearing EXPLICITNESS facts the skeleton silently got right.
@[bound] theorem Complex.abs_re_le_norm (z : ℂ) : |z.re| ≤ ‖z‖
    -- Analysis/Complex/Norm.lean:38, inside `namespace Complex` (:22-:389).
    -- HOMONYM WARNING: RCLike.abs_re_le_norm (z : K) : |re z| ≤ ‖z‖ lives at
    -- Analysis/RCLike/Basic.lean:690 (namespace RCLike :94-:766). With `open Complex`
    -- active the intended one resolves, but write `Complex.abs_re_le_norm` if it stutters.
theorem HasDerivAt.comp (hh₂ : HasDerivAt h₂ h₂' (h x)) (hh : HasDerivAt h h' x) :
    HasDerivAt (h₂ ∘ h) (h₂' * h') x
    -- Analysis/Calculus/Deriv/Comp.lean:258, with `x` EXPLICIT — re-declared by the
    -- trailing `(x)` of the variable block at :71, whose comment at :67-:68 says
    -- "we put x explicit to help the elaborator". THIS IS WHAT MAKES the skeleton's
    -- `.comp z (…)` correct. Note the conclusion is a `Function.comp`, not a lambda.
theorem hasDerivAt_id : HasDerivAt id 1 x
    -- Analysis/Calculus/Deriv/Basic.lean:681, under `variable (s x L)` at :673, so `x`
    -- is EXPLICIT and `hasDerivAt_id z` is correct as written.
alias ⟨_, HasDerivAt.sub_const⟩ := hasDerivAt_sub_const_iff
    -- Analysis/Calculus/Deriv/Add.lean:403, an alias of
    -- `@[simp] theorem hasDerivAt_sub_const_iff (c : F) : HasDerivAt (f · - c) f' x ↔
    --  HasDerivAt f f' x` (:400). So `.sub_const w` produces the `(· - w)` LAMBDA
    -- shape, which is what the composition in W1's skeleton must be matched against.
theorem HasDerivAt.div_const (hc : HasDerivAt c c' x) (d : 𝕜') : …
    -- Analysis/Calculus/Deriv/Mul.lean:558 (and HasDerivAt.mul_const at :305, the
    -- S1AP-W1a fallback).

-- Pi-level pointwise seams — ADDED v1.2 (pin lens finding 3 could not open a
-- declaration site for `Pi.smul_apply`; here it is, and its non-primed status
-- explained). Both live in `namespace Pi`, Algebra/Notation/Pi/Defs.lean:29-:165.
@[to_additive (attr := simp)]
lemma Pi.mul_apply (f g : ∀ i, M i) (i : ι) : (f * g) i = f i * g i := rfl    -- :70
lemma Pi.pow_apply (f : ∀ i, M i) (a : α) (i : ι) : (f ^ a) i = f i ^ a := rfl -- :136
    -- ← `Pi.smul_apply` IS THE `to_additive` TWIN OF :136, generated by the attribute
    --   line at :135 (`@[to_additive (attr := simp, to_additive) (reorder := 5 6)
    --   smul_apply]`). It therefore has NO declaration line of its own, which is why a
    --   grep for `theorem Pi.smul_apply` finds nothing. The DEPENDENT primed variant
    --   `Pi.smul_apply'` at Algebra/Group/Action/Pi.lean:41 is a different lemma; the
    --   non-dependent `Pi.smul_apply` is the one S1AP-SMUL wants.

-- Cast / order plumbing consumed by A2 step 11, A3 and A4 — ADDED v1.2 (pin lens
-- finding 3: A3/A4 cited these as "core big-operators/order API" with no locator).
@[simp, norm_cast] lemma Int.cast_sum [AddCommGroupWithOne R] (s : Finset ι) (f : ι → ℤ) :
    ↑(∑ x ∈ s, f x : ℤ) = ∑ x ∈ s, (f x : R)
    -- Algebra/BigOperators/Ring/Finset.lean:377, inside `namespace Int` :348-:386.
@[simp] lemma Int.cast_eq_zero {n : ℤ} : (n : α) = 0 ↔ n = 0
    -- Data/Int/Cast/Lemmas.lean:57, under `variable [AddGroupWithOne α] [CharZero α]`
    -- (:49/:55), inside `namespace Int` :34-:125. ℂ is CharZero, so A3's chain closes.
@[to_additive sum_nonneg] theorem Finset.one_le_prod' (h : ∀ i ∈ s, 1 ≤ f i) : 1 ≤ ∏ i ∈ s, f i
    -- Algebra/Order/BigOperators/Group/Finset.lean:120 (attribute line :119), inside
    -- `namespace Finset` :32-:602. `Finset.sum_nonneg (h : ∀ i ∈ s, 0 ≤ f i) :
    -- 0 ≤ ∑ i ∈ s, f i` is the to_additive twin named on that attribute line and has
    -- no declaration line of its own — same situation as Pi.smul_apply above.
-- `Int.toNat_of_nonneg` (A4): NO LOCATOR IS GIVEN, DELIBERATELY. It is used 33 times
-- inside Mathlib at the pin but DECLARED NOWHERE UNDER `Mathlib/` — it is a Lean-core
-- `Int` lemma. The house rule is that a locator must be read before it is written, and
-- there is no `Mathlib/` file:line to read. A stage-two drafter should confirm the name
-- and argument order at elaboration time rather than trusting a citation here.

-- Empty-region lemmas behind the negative-radius soundness witness (§5.2) — ADDED v1.2.
-- All three inside `namespace Metric`, Topology/MetricSpace/Pseudo/Defs.lean:361-:941.
theorem ball_eq_empty : ball x ε = ∅ ↔ ε ≤ 0                                  -- :387
@[simp] theorem sphere_eq_empty_of_neg (hε : ε < 0) : sphere x ε = ∅          -- :442
@[simp] theorem closedBall_eq_empty : closedBall x ε = ∅ ↔ ε < 0              -- :468
theorem deriv_inv : deriv (fun x => x⁻¹) x = -(x ^ 2)⁻¹
    -- Analysis/Calculus/Deriv/Inv.lean:66 — used only by the A4 witness in §5.2.

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

**Mandatory docstring on the built declaration (v1.2, acceptance record truth
lens finding 4).** The proposed name records `notMem_closedBall` but not that
the ball is `closedBall c |R|` rather than `closedBall c R`, and this document
elevates exactly that `R`-vs-`|R|` confusion to a death condition (8) and to the
one correction it made to the pool. A consumer who applies the lemma by name,
reading `closedBall c R`, is the precise failure mode being guarded against.
Mathlib's own `integral_sub_zpow_of_undef` (:557) has the same silent `|R|`, so
the name is convention-conformant — but that convention is what produced the
pool's defect. **A stage-two build of W1 must therefore carry a docstring
stating that the excluded region is `Metric.closedBall c |R|`, the closed disc
of GEOMETRIC radius `|R|`, and cross-referencing §5.2.** The alternative repair
the acceptance record offered — renaming to `..._of_notMem_closedBall_abs` or
`..._of_abs_lt_dist` — is a **change to a public signature** and is therefore
**not made in this pass**; see §5.4. If a future reviewer prefers the rename, it
returns the surface to contract review rather than being applied editorially.

#### Proof skeleton (primitive route — uniform in the sign of `R`)

```lean
  -- w outside the closed |R|-ball: |R| < dist w c, so c ≠ w and z ≠ w on the sphere
  have hcw : c - w ≠ 0 := sub_ne_zero.2 (by
    intro h; exact hw (by simp [h, Metric.mem_closedBall, abs_nonneg]))
  -- v1.2: `refine … (f := …) ?_`, NOT a bare `apply`. The primitive `f` in :538 is an
  -- implicit argument that does NOT occur in the conclusion, so a bare `apply` opens a
  -- metavariable ?f in the context before `intro z hz` and only closes it at the final
  -- `exact hd.hasDerivWithinAt` — the same shape as confirmed failure class (B), a
  -- lemma applied with its intermediate object left undetermined. It should succeed
  -- here (the assignment has no dependence on z), but pinning the primitive up front
  -- is free and a wasted CI round is not. (Acceptance record, pin lens finding 5;
  -- recorded under S1AP-W1a.)
  refine circleIntegral.integral_eq_zero_of_hasDerivWithinAt'
    (f := fun u : ℂ => Complex.log ((u - w) / (c - w))) ?_   -- :538, sphere c |R|, any R
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

*Recorded alternative route: Cauchy + the `|R|` flip. Uniform in the sign of `R`.*
For `0 ≤ R`, `fun z => (z - w)⁻¹` is `DiffContOnCl ℂ · (ball c R)`
(differentiable wherever `z ≠ w`, and `w ∉ closedBall c R = closure (ball c R)`
for `R > 0` via `closure_ball` RCLike/Real.lean:59; `R = 0` by
`circleIntegral.integral_radius_zero`, :422), so
`DiffContOnCl.circleIntegral_eq_zero` (CauchyIntegral.lean:459, `h0 : 0 ≤ R`)
closes it. For `R < 0` this route needs an `∮`-level sign flip
`∮ … C(c,R) = ∮ … C(c,|R|)`, after which `0 ≤ |R|` and Cauchy applies verbatim
(the hypothesis `w ∉ closedBall c |R|` is already stated at `|R|`, so nothing
else moves).

**Status of that flip, corrected in v1.2 (acceptance record, truth lens finding
2).** v1.1 said the flip "does not exist at the pin". That sentence is literally
true of a NAMED `∮` lemma — re-verified this pass by grepping
`neg_radius|abs_radius` over the whole of CircleIntegral.lean, which yields only
`circleMap_neg_radius` (:162) and the integrand-level
`circleIntegrable_neg_radius` (:292) — but it is **misleading in effect and is
withdrawn**, because it invites a drafter to abandon the Cauchy route when the
mathematics is already in the library one file over:

- `Real.circleAverage_abs_radius : circleAverage f c |R| = circleAverage f c R`
  (CircleAverage.lean:135, `@[simp]`) IS the flip, proved, on
  `circleAverage_neg_radius` (:129) / `circleAverage_eq_integral_add` (:117) /
  `circleMap_neg_radius` (CircleIntegral.lean:162);
- `Real.circleAverage_eq_circleIntegral` (:96, `h : R ≠ 0`) is the bridge to `∮`.

**Honest cost, which the finding's "~3 lines" understates and this contract does
not repeat.** The bridge at :96 carries a `(z - c)⁻¹ •` weight, so recovering a
bare `∮` means applying it at the weighted integrand `fun z ↦ (z - c) • g z` at
both radii and cancelling the weight along the path. The cancellation is sound
(`c ∉ sphere c |R|` for `R ≠ 0`) but it cannot be done with
`circleIntegral.integral_congr` (:425), whose `0 ≤ R` excludes exactly the sign
case the flip exists for; use `circleIntegral.circleIntegral_congr_codiscreteWithin`
(:430, hypothesis `R ≠ 0`) or unfold `circleIntegral`. Add the `R = 0` split
(:422) and the `smul`/`mul` seam and it is a short, real derivation, not three
lines. It is registered as **S1AP-W1e** (MEDIUM).

**Which route is primary.** Both are recorded in full and **the log-primitive
route stays primary**; the acceptance record's proposal to promote Cauchy+flip
to primary and retire S1AP-W1a/W1b/W1c is **partially declined** (§5.4). The
existence half of that finding is confirmed and applied above. The cost half is
not: promoting Cauchy+flip does not retire two MEDIUM obligations, it substitutes
S1AP-W1e for them, and demoting W1a/W1b would tell a drafter to skip preparing
work that is still on the critical path of whichever route is chosen. The choice
between the two is a stage-two implementation decision to be made with the
elaborator in hand, and both are costed here so that it can be.

#### Pinned dependencies (W1)

`circleIntegral.integral_eq_zero_of_hasDerivWithinAt'` — CircleIntegral.lean:538
(read verbatim: quantifies over `sphere c |R|`, no sign hypothesis on `R`;
`[CompleteSpace E]`, satisfied by `E = ℂ`);
`Complex.hasDerivAt_log` — SpecialFunctions/Complex/LogDeriv.lean:37;
`Complex.slitPlane` — Analysis/Complex/Basic.lean:634;
`closure_ball` — RCLike/Real.lean:59 (alternative route);
`DiffContOnCl.circleIntegral_eq_zero` — CauchyIntegral.lean:459 (alternative
route); `circleIntegral.integral_radius_zero` — CircleIntegral.lean:422
(alternative route, `R = 0` case); `circleIntegrable_neg_radius` —
CircleIntegral.lean:292 (pattern only);
`Real.circleAverage_abs_radius` — CircleAverage.lean:135, with
`circleAverage_neg_radius` :129, `circleAverage_eq_integral_add` :117,
`circleAverage_eq_circleIntegral` :96 and
`circleIntegral.circleIntegral_congr_codiscreteWithin` :430 (alternative route,
`R < 0` case — all added v1.2);
`Complex.abs_re_le_norm` — Analysis/Complex/Norm.lean:38;
`HasDerivAt.comp` — Deriv/Comp.lean:258 (`x` explicit);
`hasDerivAt_id` — Deriv/Basic.lean:681 (`x` explicit);
`HasDerivAt.sub_const` — Deriv/Add.lean:403 (alias of :400);
`HasDerivAt.div_const` — Deriv/Mul.lean:558 (`HasDerivAt.mul_const` :305 for the
fallback) — the last five added v1.2, previously named in the obligations below
with no locator.

#### Obligations (W1)

- **S1AP-W1a** (MEDIUM). The chain-rule arithmetic
  `((z-w)/(c-w))⁻¹ * (c-w)⁻¹ = (z-w)⁻¹` under `hcw` and `z ≠ w`; `HasDerivAt.comp`
  (Deriv/Comp.lean:258, `x` explicit — this is what makes the skeleton's `.comp z (…)`
  correct) associates the composition as `log ∘ (affine)`, and the affine derivative is
  produced by `((hasDerivAt_id z).sub_const w).div_const (c - w)` (Deriv/Basic.lean:681
  with `x` explicit; Deriv/Add.lean:403; Deriv/Mul.lean:558). Two shape seams to expect:
  `.sub_const` yields the `(· - w)` lambda spelling and `.comp` concludes in
  `Function.comp`, while the skeleton displays `fun u : ℂ => Complex.log ((u - w) /
  (c - w))` — defeq, not syntactically equal, so a `show` may be needed. Fallback:
  differentiate `fun u => Complex.log ((u - w) * (c - w)⁻¹)` instead
  (`.mul_const`, Deriv/Mul.lean:305), or split `Complex.log` of a quotient is *not*
  needed — only the derivative is, so no `log_div` branch analysis arises.
  Also recorded here (v1.2, pin lens finding 5): apply :538 as
  `refine … (f := fun u : ℂ => Complex.log ((u - w) / (c - w))) ?_`, never a bare
  `apply`, so the implicit primitive is pinned before `intro z hz`.
- **S1AP-W1b** (MEDIUM). The slitPlane membership: from
  `‖z - c‖ = |R| < dist w c` derive `0 < ((z - w)/(c - w)).re` by writing the
  quotient as `1 + (z - c)/(c - w)` and using `|re q| ≤ ‖q‖`
  (`Complex.abs_re_le_norm`, Analysis/Complex/Norm.lean:38 — beware the RCLike
  homonym at RCLike/Basic.lean:690). Pure norm arithmetic; fallback is a direct
  `Complex.ext`-free estimate `re (1 + q) = 1 + re q ≥ 1 - ‖q‖`.
- **S1AP-W1c** (LOW). `z ≠ w` for `z ∈ sphere c |R|`: `dist z c = |R| < dist w c`.
- **S1AP-W1e** (MEDIUM, added v1.2). The `∮`-level radius flip
  `∮ … C(c,R) = ∮ … C(c,|R|)`, needed only if the Cauchy alternative route is taken.
  It is NOT a named lemma at the pin but IS derivable there: run
  `Real.circleAverage_eq_circleIntegral` (CircleAverage.lean:96, `R ≠ 0`) at the
  weighted integrand `fun z ↦ (z - c) • g z` for both `R` and `|R|`, cancel the
  `(z - c)⁻¹ •` weight along the path (`c ∉ sphere c |R|` for `R ≠ 0`) using
  `circleIntegral.circleIntegral_congr_codiscreteWithin` (:430, `R ≠ 0`) — **not**
  `integral_congr` (:425), whose `0 ≤ R` excludes the case at issue — apply
  `Real.circleAverage_abs_radius` (:135), and dispatch `R = 0` by
  `circleIntegral.integral_radius_zero` (:422). Seams: the `smul`/`mul`
  identification at `E = ℂ` (as in S1AP-SMUL) and the `R = 0` split. Fallback:
  reconstruct the flip directly from `circleMap_neg_radius` (:162) plus 2π-periodicity,
  copying the proof pattern of `circleIntegrable_neg_radius` (:292–:296).
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

**A1 IS A SHORT COROLLARY OF A PINNED LEMMA. Re-priced in v1.2; read this before
planning any work on it.** v1.1 called A1 "the single genuinely new move" and
"the pool's named hardest step", and registered `S1AP-BRIDGE` as HIGH gating
A2–A4. **Both descriptions are withdrawn and the severity is now LOW.** Mathlib
proves the meromorphic, punctured form of exactly this bridge:

```lean
-- Mathlib/Analysis/Meromorphic/IsolatedZeros.lean:99, namespace MeromorphicAt (:31-:130)
theorem eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin (hf : MeromorphicAt f x)
    (hg : MeromorphicAt g x) (h₁x : x ∈ U) (h₂x : AccPt x (𝓟 U))
    (h : f =ᶠ[codiscreteWithin U] g) :
    f =ᶠ[𝓝[≠] x] g
```

Its four hypotheses are A1's four hypotheses with `MeromorphicAt` in place of
`AnalyticAt` — strictly weaker, hence free — and its section variables (:24–:27)
are A1's binder context verbatim. **The only delta is the filter: :99 concludes
in the PUNCTURED `𝓝[≠] x`, A1 in the UNPUNCTURED `𝓝 x`.** That gap is closed by
one round trip through the analytic identity principle, and the punctured →
unpunctured step needs no manual `NeBot` argument because
`NormedField.nhdsNE_neBot` (Normed/Field/Basic.lean:242) is an `@[instance]`
stated for `[NontriviallyNormedField α]`, which is precisely A1's typeclass.

A1's own contribution is therefore the `AnalyticAt`-flavoured unpunctured
packaging — worth stating, since A2 consumes the unpunctured form at sphere
points, but not a research step and not a gate. **The genuinely un-pinned
content of this package is A2's assembly.**

Its consequences at `x` — value equality (`Filter.EventuallyEq.eq_of_nhds`,
Topology/Neighborhoods.lean:153 — locator added, Annex A F3) and derivative
equality (`Filter.EventuallyEq.deriv_eq`, Deriv/Basic.lean:647) — are consumed
inline in A2 and are not separate public statements.

#### Proof skeleton

```lean
  -- v1.2 primary route: three lines, term-mode, from the pinned meromorphic bridge.
  -- 1. AnalyticAt ⇒ MeromorphicAt on both sides: AnalyticAt.meromorphicAt
  --    (Meromorphic/Basic.lean:40).
  -- 2. MeromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin
  --    (Meromorphic/IsolatedZeros.lean:99) with hxU, hacc, h gives f =ᶠ[𝓝[≠] x] g.
  -- 3. `.frequently` turns that into ∃ᶠ z in 𝓝[≠] x, f z = g z. The [NeBot (𝓝[≠] x)]
  --    that Filter.Eventually.frequently (Order/Filter/Basic.lean:756) demands is
  --    supplied by instance search from NormedField.nhdsNE_neBot
  --    (Normed/Field/Basic.lean:242, @[instance], [NontriviallyNormedField 𝕜]).
  -- 4. (hf.frequently_eq_iff_eventually_eq hg).mp (Analytic/IsolatedZeros.lean:141)
  --    upgrades it to ∀ᶠ z in 𝓝 x, f z = g z, which is the goal.
  --
  -- i.e. the whole proof is
  --   (hf.frequently_eq_iff_eventually_eq hg).mp
  --     ((hf.meromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin
  --         hg.meromorphicAt hxU hacc h).frequently)
  -- modulo whatever `EventuallyEq`-vs-`∀ᶠ … =` unfolding the elaborator wants.

  -- RECORDED FALLBACK (the v1.1 primary route — kept in full, since nothing here has
  -- been elaborated and the route above could stumble on an unfolding):
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

Primary route (all added v1.2):
`MeromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin` —
Analysis/Meromorphic/IsolatedZeros.lean:99 (verbatim signature quoted in §0; the
zero-valued form at :59, the identity principle at :88 and the `Preperfect`
variants at :109/:118 are the neighbouring family);
`AnalyticAt.meromorphicAt` — Analysis/Meromorphic/Basic.lean:40;
`NormedField.nhdsNE_neBot` — Analysis/Normed/Field/Basic.lean:242 (`@[instance]`);
`Filter.Eventually.frequently` — Order/Filter/Basic.lean:756;
`AnalyticAt.frequently_eq_iff_eventually_eq` —
Analysis/Analytic/IsolatedZeros.lean:141 (verbatim signature quoted in §0).

Fallback route: `mem_codiscreteWithin_accPt` — Topology/DiscreteSubset.lean:217
(and the `codiscreteWithin` def at :201, `mem_codiscreteWithin` at :203 as
fallback); `accPt_sup` — Topology/ClusterPt.lean:190;
`accPt_iff_frequently_nhdsNE` — Topology/ClusterPt.lean:217.

#### Obligations (A1)

- **S1AP-BRIDGE** (**LOW** — downgraded from HIGH in v1.2). The punctured →
  unpunctured step. Discharge, in two lines: `.frequently` on the conclusion of
  Meromorphic/IsolatedZeros.lean:99 (fed by `AnalyticAt.meromorphicAt`, Basic:40),
  then `AnalyticAt.frequently_eq_iff_eventually_eq` (Analytic/IsolatedZeros.lean:141).
  The `NeBot (𝓝[≠] x)` instance is `NormedField.nhdsNE_neBot` (Normed/Field/Basic.lean:242)
  and needs no argument. **This obligation no longer gates A2–A4**; the v1.1
  claim that it did was the consequence of not citing :99. Residual risk is
  ordinary elaboration friction: whether `f =ᶠ[𝓝[≠] x] g` unfolds to
  `∀ᶠ z in 𝓝[≠] x, f z = g z` where `.frequently` wants it, and whether the
  `Filter`/`Topology` namespaces are open enough for `𝓝[≠]` to parse under the
  proposed preamble. Fallbacks, in order: (i) the full v1.1 filter-algebra route
  displayed above, whose every link is also pinned; (ii) within that route,
  replace step 2 by `AccPt.mono` (ClusterPt.lean:230, pinned — Annex A F5)
  through `U ⊆ (U ∩ S) ∪ (U \ S)` with `sup_principal`; (iii) work from
  `mem_codiscreteWithin` (:203) directly: `Disjoint (𝓝[≠] x) (𝓟 (U \ S))` plus
  `NeBot (𝓝[≠] x ⊓ 𝓟 U)` forces `NeBot (𝓝[≠] x ⊓ 𝓟 (U ∩ S))` by
  `inf_sup_left`-type lattice reasoning in `Filter`; (iv) if the generic form
  resists, specialize A1 to `𝕜 = ℂ`, `U = closedBall c R` and inline it into
  A2 — the generic statement is then dropped, A2–A4 survive unchanged, and the
  drop is recorded. **Do not** weaken A2 by *assuming* the factorization
  pointwise (death condition 6).
- **S1AP-A1b** (LOW, informational, added v1.2). A1 is a near-duplicate of pinned
  material under a different name, which the name-only collision scan could not
  see. If any of this is offered upstream, expect a maintainer to ask why A1 is not
  simply stated as a two-line `AnalyticAt` corollary in
  `Mathlib/Analysis/Meromorphic/IsolatedZeros.lean` next to :99, and be ready to
  either agree or justify the separate home. This is a review-negotiation item, not
  a proof risk. The acceptance record additionally proposed **renaming** A1 to match
  the pinned family (e.g. `AnalyticAt.eventuallyEq_nhds_of_eventuallyEq_codiscreteWithin`);
  a declaration name is part of a public signature, so **that rename is NOT made in
  this pass** and would return the surface to contract review (§5.4).
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

**`hR : 0 < R` IS REQUIRED FOR TRUTH, NOT FOR CONVENIENCE (v1.2, acceptance
record truth lens finding 3).** This is the package-wide statement of the
negative-radius trap; v1.1 framed the trap as W1-specific and that framing is
wrong. Weakening `0 < R` to `0 ≤ R`, to `R ≠ 0`, or to nothing makes **A2
false**, by a witness entirely inside the pin:

> Take `f = id`, `c = 0`, `R = -1`. Then `closedBall (0:ℂ) (-1) = ∅`
> (`Metric.closedBall_eq_empty`, Pseudo/Defs.lean:468) so `hf` holds vacuously;
> `sphere (0:ℂ) (-1) = ∅` (`Metric.sphere_eq_empty_of_neg`, :442) so `hf₀` holds
> vacuously; `ball (0:ℂ) (-1) = ∅` (`Metric.ball_eq_empty`, :387) so
> `MeromorphicOn.divisor f (ball 0 (-1))` is identically `0` — its `toFun` guards
> on `z ∈ U` (Divisor.lean:39–:41) — and the RHS is `2πI · 0 = 0`. But the LHS is
> `∮ z in C(0,-1), (z - 0)⁻¹ = 2 * π * I ≠ 0`, by the pinned
> `circleIntegral.integral_sub_center_inv` (CircleIntegral.lean:532, whose
> hypothesis is exactly `R ≠ 0`). `0 = 2πI` is false.

This is the same witness §5.2 already runs against the pool's W1 premise-form.
The trap is **package-wide**: see the identical notes under A3 and A4, §5.2, and
death condition 8.

*Why the split with W1's `|R|` is deliberate and not an oversight.* W1 is stated
on `|R|` and A2–A4 on `0 < R`, whereas the pin's own family here (`:538`, `:557`,
JensenFormula.lean:307) uses `R ≠ 0` with `|R|` throughout. The split is kept
because the two statements are doing different jobs: W1 closes a documented
library gap and should therefore be as general as the pinned API around it
(uniform in the sign of `R`), while A2–A4 assert an equality between an integral
and a count over `ball c R`, where the negative-radius branch is not merely
awkward but **empty on one side and nonzero on the other**. Adopting `R ≠ 0` +
`|R|` for A2–A4 would require restating the divisor sum over `ball c |R|` and the
hypotheses over `closedBall c |R|`/`sphere c |R|` — a change to three public
signatures, which this pass does not make (§5.4). A future reviewer who prefers
the uniform convention should raise it as a contract-review item.

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
  (including its differentiability binders as displayed at :54–:56 — **and note
  that its first argument `(x : 𝕜)` is EXPLICIT and precedes `hf`**, see the
  verbatim quote now in §0), `logDeriv_prod`'s per-factor nonvanishing, and
  `logDeriv_fun_zpow`'s `(f · ^ n)` lambda shape versus the `(· - u) ^ D u`
  factor shape.

  **Lambda shapes at all three levels, not just the innermost (v1.2, acceptance
  record pin lens finding 2).** v1.1 recorded the lambda hazard only for
  `logDeriv_fun_zpow`. It is present one level up as well, and step 7 walks into
  it: at the pin `logDeriv_mul` concludes on `logDeriv (fun z => f z * g z) x`
  (:56) and `logDeriv_prod` on `logDeriv (∏ i ∈ s, f i ·) x` (:75) — both LAMBDA
  spellings — while step 7 computes with `logDeriv (φ * g) z`, a **Pi-level
  product of two functions**. These are defeq but not syntactically equal, so
  `rw` will not fire on them and `exact` needs a `show`. Discharge: `Pi.mul_apply`
  (Algebra/Notation/Pi/Defs.lean:70, `@[simp]`, `namespace Pi` :29–:165) or an
  explicit `show`, applied at each of the three shapes — `logDeriv_mul` :56,
  `logDeriv_prod` :75, `logDeriv_fun_zpow` :87 — alongside the `Pi.smul_apply`
  already recorded under S1AP-SMUL (that one is the `to_additive` twin of
  `Pi.pow_apply`, Notation/Pi/Defs.lean:136, and has no declaration line of its
  own; see the §0 note). Not a soundness problem, an unrecorded seam of exactly
  the kind this register exists for. Fallback:
  prove the expansion by `Finset.induction` on `h₃f.toFinset` using
  `FactorizedRational.extractFactor` (:107) instead of `logDeriv_prod` — the
  pool's route (b), re-proving less of `extract_zeros_poles` than the pool
  feared because only the sphere-side identity is needed.
- **S1AP-BRIDGE** (**LOW**, shared with A1 — downgraded from HIGH in v1.2).
  Step 6 consumes A1, which is now a short corollary of
  Meromorphic/IsolatedZeros.lean:99 rather than the package's gate; if A1 falls to
  its fallback (iv), step 6 inlines it. **S1AP-LOGD is now the package's only HIGH
  obligation**, and it lives in A2's step 7, not in A1.
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

**`hR : 0 < R` IS REQUIRED FOR TRUTH HERE TOO (v1.2).** The A2 witness refutes A3
directly: with `f = id`, `c = 0`, `R = -1` both hypotheses are vacuous
(`closedBall 0 (-1) = ∅`, `sphere 0 (-1) = ∅`), the right side is vacuously TRUE
(`ball 0 (-1) = ∅`, so "no zero in the ball" holds), and the left side is FALSE
(`∮ z in C(0,-1), (z-0)⁻¹ = 2πI ≠ 0` by CircleIntegral.lean:532). An `iff` with a
false left and a true right is false. See the fuller statement under A2, and §5.2.

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

**`hR : 0 < R` IS REQUIRED FOR TRUTH HERE TOO (v1.2 — and this sharpens the
acceptance record, which guessed the opposite).** The acceptance record's truth
lens tried the `f = id` and `f = (·)²` witnesses against A4, found `n = 1` and
`n = 2` respectively, and concluded that "A4's `0 < R` is convenience". **That
conclusion is wrong and is corrected here.** Those witnesses fail only because
they produce a *positive* count; A4's `∃ n : ℕ` also forbids a *negative* one,
and with the hypotheses vacuous at `R < 0` the function `f` is completely
arbitrary — nothing forces it to be analytic, so a pole is admissible:

> Take `f = fun z : ℂ => z⁻¹`, `c = 0`, `R = -1`. As above, `closedBall 0 (-1)`
> and `sphere 0 (-1)` are empty, so `hf` and `hf₀` hold vacuously. On the contour
> every point has `‖z‖ = 1`, so `z ≠ 0`, and there `deriv f z / f z =
> (-(z^2)⁻¹)/(z⁻¹) = -(z - 0)⁻¹` (`deriv_inv`, Deriv/Inv.lean:66). Hence the LHS
> is `-(2 * π * I)`, by `circleIntegral.integral_const_mul` (:527) and
> `circleIntegral.integral_sub_center_inv` (:532). Since `2πI ≠ 0`, solving
> `2πI · (n:ℂ) = -2πI` needs `n = -1`, which is not a natural number. No `n : ℕ`
> exists, so **A4 is FALSE at `R = -1`**.

So `0 < R` is soundness-load-bearing in all three of A2, A3 and A4, and the trap
is package-wide without exception. (Note what does the work: `0 < R` is what
makes `hf₀` non-vacuous, and `hf₀` on a nonempty sphere is what forces `f` to be
genuinely analytic and nonvanishing on the contour.)

#### Proof skeleton

```lean
  -- n := (∑ᶠ u, divisor f (ball c R) u).toNat. By A2 it suffices that the finsum is
  -- ≥ 0: divisor_nonneg (:177) on the ball + finite support (:104) +
  -- finsum_eq_sum_of_support_subset + Finset.sum_nonneg, then Int.toNat_of_nonneg.
```

#### Pinned dependencies (A4)

A2; Divisor.lean:104/:177 (consumed as
`MeromorphicOn.AnalyticOnNhd.divisor_nonneg`, fully qualified — see the §0
namespace note); Finprod.lean:354 (twin);
`Finset.sum_nonneg` — Algebra/Order/BigOperators/Group/Finset.lean:120, the
`to_additive` twin named on the attribute line at :119 over
`Finset.one_le_prod'`, inside `namespace Finset` :32–:602 (locator added v1.2;
v1.1 cited it as "core big-operators/order API, same files as A3's", which is a
locator-free hand-wave and is what pin lens finding 3 objected to);
`Int.cast_sum` — Algebra/BigOperators/Ring/Finset.lean:377;
`Int.toNat_of_nonneg` — **no locator is offered, deliberately.** It is used 33
times inside Mathlib at the pin but is DECLARED NOWHERE under `Mathlib/`; it is a
Lean-core `Int` lemma. Under this document's own rule a locator must be read
before it is written, and there is no `Mathlib/` file to read. A stage-two
drafter must confirm the exact name and argument order at elaboration time.

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

Severities re-priced in v1.2 where the acceptance record's findings, re-confirmed
at the pin, required it. **The package now has exactly one HIGH obligation, and
it is S1AP-LOGD in A2's step 7 — not A1.**

| ID | Statement | Severity | Content | Fallback recorded |
|---|---|---|---|---|
| **S1AP-LOGD** | A2 | **HIGH** | `logDeriv (φ * g)` expansion on the sphere: finprod→Finset seam, `logDeriv_mul/prod/fun_zpow` side conditions, the explicit `(x : 𝕜)` of :54, lambda shapes at all three levels (:56/:75/:87) | yes (induction via `extractFactor` :107 — pool route (b), sphere-side only; `Pi.mul_apply`/`show` for the shapes) |
| S1AP-BRIDGE | A1 (**no longer gates A2–A4**) | LOW *(was HIGH; v1.2)* | punctured→unpunctured only: `.frequently` on Meromorphic/IsolatedZeros:99 (via AnalyticAt.meromorphicAt, Basic:40; `NeBot` by instance, Normed/Field/Basic:242) then Analytic/IsolatedZeros:141 | yes (four routes, incl. the full v1.1 filter-algebra proof and inlining a ℂ-special case into A2) |
| S1AP-FIN | A2 | MEDIUM | `≠ ⊤` supply on the compact: Order:133 → :624 → Meromorphic/Order:279 + ENat:526; subtype binders | yes (Mult.lean S1M-FIN pattern) |
| S1AP-INT | A2 | MEDIUM | `integral_congr` EqOn shape + integrability before `integral_add`/`integral_fun_sum` | yes (unfold to `intervalIntegral.integral_finsetSum`, :461 proof copyable) |
| S1AP-SUPP | A2 | MEDIUM | support ⊆ ball and support ⊆ zeros; orientation of NormalForm:578 | yes (pointwise via :71 + :133/:137, bypassing :578 in A2) |
| S1AP-W1a | W1 | MEDIUM | chain-rule constant arithmetic for the log primitive (Comp:258 / Basic:681 / Add:403 / Mul:558, all with the explicitness noted); also: apply :538 by `refine … (f := …) ?_`, never a bare `apply` | yes (`mul_const` variant, Mul:305) |
| S1AP-W1b | W1 | MEDIUM | slitPlane membership from the norm bound (`Complex.abs_re_le_norm`, Complex/Norm:38) | yes (direct re-estimate) |
| S1AP-W1e | W1 | MEDIUM *(new, v1.2)* | the `∮`-level absolute-radius flip needed only by the Cauchy alternative route: derivable from CircleAverage:96 + :135 via :430 and :422, but not a named lemma at the pin | yes (reconstruct from `circleMap_neg_radius` :162 + periodicity, pattern at :292–:296) |
| S1AP-A3a | A3 | MEDIUM | `2πI·(n:ℂ) = 0 → n = 0` cast chain; ball-carrier `≠ ⊤` restriction | yes |
| S1AP-SEAM | A2 | LOW | CB-vs-ball divisor pointwise equality (Divisor:68 twice) | yes |
| S1AP-SMUL | A2 | LOW | `φ • g` vs `φ * g`: smul_eq_mul (Action/Defs:74, rfl) via Pi.smul_apply — Annex A F4 | yes (`show`/rewrite) |
| S1AP-CAST | A2 | LOW | `ℤ→ℂ` cast through the Finset sum | yes (`push_cast`) |
| S1AP-A1a | A1/A2 | LOW | `AccPt` at sphere points via `closure_ball` + ClusterPt:261 | yes |
| S1AP-A1b | A1 | LOW *(new, v1.2; informational)* | A1 is a semantic near-duplicate of Meromorphic/IsolatedZeros:99 under a different name; upstream will ask why it is not stated there | n/a (review-negotiation item) |
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
  (`∮ … C(c,R) = ∮ … C(c,|R|)`). **Restated in v1.2.** It is **absent as a named
  `∮` lemma** — re-verified this pass by grepping `neg_radius|abs_radius` over
  the whole of CircleIntegral.lean, which finds only `circleMap_neg_radius`
  (:162) and the integrand-level `circleIntegrable_neg_radius` (:292). It is
  **NOT absent as mathematics**: `Real.circleAverage_abs_radius`
  (CircleAverage.lean:135, `@[simp]`) already performs the flip, and
  `Real.circleAverage_eq_circleIntegral` (:96) bridges to `∮`. The v1.1 phrasing
  "does not exist at the pin" is withdrawn as misleading. Deriving the named `∮`
  form is short but not free — it must insert and cancel the `(z - c)⁻¹ •` weight
  of :96 and cannot use `integral_congr` (:425, `0 ≤ R`) to do it, which is why
  it is costed as **S1AP-W1e** (MEDIUM) rather than as "~3 lines". Not needed by
  W1's primary (log-primitive) route; needed by the recorded Cauchy alternative.
  Reconstruction pattern, if a general lemma is ever wanted:
  CircleIntegral.lean:292–:296.
- **DEFERRED-AP5** — the meromorphic-case argument principle (poles counted
  negatively; the pool's `MeromorphicOn.circleIntegral_logDeriv` sketch). The
  factorization engine (:291) already covers it, but the sphere-side `logDeriv`
  expansion gains a pole-factor case split. A future delta, not a redesign.
  *(v1.2, acceptance record claim-boundary finding 4: v1.1 ended this item with
  "and the analytic case is the one with consumers in sight" — the only sentence
  in the document asserting a downstream consumer, and it named none. In a
  document whose whole licence is route-neutrality, an unnamed "consumers in
  sight" invites the reader to supply one, and the natural supply inside
  `domains/riemann-hypothesis/` is an entire function, i.e. ξ — which is exactly
  the analytic-vs-meromorphic split the sentence turned on. The clause is
  deleted. For the record, the consumers actually in view are internal and
  route-neutral: DEFERRED-AP2, DEFERRED-AP3, and a possible upstream Mathlib
  submission. Nothing in this package has a ζ/ξ consumer, and supplying one is
  death condition 4.)*

---

## Claim boundary

- **This contract is an unbuilt statement surface.** Stage-one acceptance
  changes no barrier row, closes no queue task, and carries no kernel verdict.
- **No barrier is closed by building it either. It closes no barrier, advances
  no barrier, and partially closes no barrier of `MATHLIB_CAPABILITY_MAP.md` —
  its capability-map effect is INVENTORY ONLY.** Generic machinery lowers the
  cost of a future exit; it never retires a row. *(v1.2, acceptance record
  claim-boundary finding 2: v1.1 negated only the word "closes", leaving
  "advances", "partially closes" and "inventory only" to implication. The repo
  has a settled formula for exactly this situation and this contract now uses it
  verbatim — `domains/riemann-hypothesis/drafts/README.md:33` for HarnackDisc and
  `:34` for PolyLiouville, with the equivalent statement carried in the built
  headers, e.g. `ResearchOS/Analysis/HarnackDisc.lean:23–:30`.)* The barriers of
  `MATHLIB_CAPABILITY_MAP.md` are scoped to this repository's ζ/ξ layer; W1,
  A1–A4 quantify over arbitrary functions and mention no ζ, ξ, L-function, or
  strip. This is the finding-A4 discipline of `MULTIPLICITY_CONTRACT.md`,
  inherited here verbatim.
- **In particular, `S1-GLOBAL-ZEROS` is untouched and stays OPEN — but not for
  the reason v1.1 gave.** *(v1.2, acceptance record claim-boundary finding 1.
  v1.1 said that row "concerns zero *enumeration* for specific functions". It
  does not, and a reader checking the row would have found the paraphrase does
  not match it. The row, re-read this pass at `MATHLIB_CAPABILITY_MAP.md:387`,
  blocks on "no global enumeration, symmetric truncation, convergence, or
  counting API", and its exit-evidence column **leads with "finite divisor
  sums"** — and A2–A4 are finite divisor sums. The paraphrase is replaced by the
  row's real content and the real reason.)* A2–A4 sum a divisor over one disc,
  but of an **arbitrary `f`**, whereas the row is scoped to this repository's
  ζ/ξ layer and additionally requires symmetric truncation, weighted
  summability, star convergence of `Σ 1/ρ`, and the source-matched `|ρ| ≤ T`
  (Li) / `|Im ρ| < T` (Weil) limits with multiplicity. None of those is supplied
  here and none is approached. The row is untouched and stays OPEN; the effect is
  inventory only.
- **No route is selected, advanced, or implied.** The RH queue
  (`tasks/RIEMANN_HYPOTHESIS.md`) is the lane authority;
  `repo/ECDLP_DECISION_SUBSTRATE.json` governs the ECDLP lane and currently
  selects no route; neither authorizes work from this document, and this
  document requests none.
- **No RH-truth claim.** Nothing here proves, disproves, or supplies evidence
  about the Riemann Hypothesis, and no consequence of W1/A1–A4 does either.
- **Shape neutrality** *(added v1.2, acceptance record claim-boundary finding
  5)*. The route-neutrality argument above is lexical — no statement names ζ, ξ,
  an L-function, a strip, or a route — and lexical grounds do not by themselves
  answer a challenge about region SHAPE. The whole surface is disc-only: A2–A4
  count over `Metric.ball c R` with the contour `C(c, R)`, and the repo treats
  shape as a route-selection vector to be checked, not assumed (RH-011 required
  "the no-cutoff-shape neutrality property re-verified mechanically",
  `tasks/RIEMANN_HYPOTHESIS.md:844`; the ZERO_SET_SLICE surface is parameterized
  by "an arbitrary compact `K`, with no cutoff shape anywhere, because choosing a
  cutoff shape is a route selection and all routes remain PARKED", `:831–:832`).
  **The disc is not a cutoff choice in the RH-011 sense here**, for two
  independent reasons: no statement in this package truncates the zero set of any
  named function — the statements quantify over an arbitrary `f`, so there is
  nothing for a shape to select over — and the disc is **forced by the pin**,
  where `circleIntegral` is the only contour API present and general contours are
  Form B (death condition 5). The asymmetry is recorded rather than hidden:
  nothing here supplies a strip- or rectangle-shaped count, and the
  route-neutral compact-`K` form at the ξ level already exists separately in
  `ZERO_SET_SLICE_CONTRACT.md`. Anyone who later reads the disc as the Li-side
  `|ρ| ≤ T` shape should note that reading requires an instantiation at ξ, which
  is death condition 4.
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
8. **The negative-radius trap is reopened anywhere in the package.** This is
   **package-wide, not W1-local** (corrected in v1.2; §5.2 and the notes under
   A2, A3, A4). Two forms:
   (a) **W1 is restated with the unsigned-radius hypothesis.**
   `w ∉ Metric.closedBall c R` is a **false** premise-form at `R < 0` (§5.2,
   with a pinned counterexample witness); any draft carrying it must not
   proceed to elaboration.
   (b) **`hR : 0 < R` is weakened in A2, A3 or A4** — to `0 ≤ R`, to `R ≠ 0`, or
   dropped. All three statements become **FALSE**, not merely awkward, and each
   has a pinned witness: `f = id, c = 0, R = -1` refutes A2 and A3, and
   `f = (·)⁻¹, c = 0, R = -1` refutes A4. At `R < 0` the closed ball, the sphere
   and the ball are all empty, so `hf` and `hf₀` are vacuous, the divisor sum is
   `0`, and `f` is entirely unconstrained — while the contour `C(c, R)` is the
   perfectly good circle of geometric radius `|R|` and the integral is whatever
   that unconstrained `f` makes it. `0 < R` is what makes `hf₀` bite. Any draft
   that relaxes it must not proceed to elaboration.
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
  sphere) was called "confirmed as the right risk locus" in v1.1. **That
  confirmation is RETRACTED in v1.2 and moves to §5.3.** The codiscrete bridge is
  not the risk locus: its meromorphic, punctured form is a pinned theorem
  (Meromorphic/IsolatedZeros.lean:99), so A1 is a short corollary and
  `S1AP-BRIDGE` is LOW. v1.1 did establish, correctly, that every link of an
  independent discharge chain is individually pinned and named
  (DiscreteSubset:217, ClusterPt:190/:217/:261, Analytic/IsolatedZeros:141,
  Deriv/Basic:647) — that chain survives as A1's recorded fallback. The package's
  real risk locus is A2's step 7, `S1AP-LOGD`.

### 5.2 Correction to the pool (one defect found and fixed here)

`UPSTREAM_POOL.md` §7.1 proposes the warm-up as
`(hw : w ∉ Metric.closedBall c R) : (∮ z in C(c, R), (z - w)⁻¹) = 0`.
**This is false for `R < 0`.** Take `R = -1`, `w = c`: `Metric.closedBall c (-1)
= ∅`, so the hypothesis holds vacuously — yet the pinned
`circleIntegral.integral_sub_center_inv` (CircleIntegral.lean:532, hypothesis
only `R ≠ 0`) evaluates the integral to `2 * π * I ≠ 0`. The circle `C(c, R)`
has geometric radius `|R|`, and the file's own integrability lemmas are stated
on `sphere c |R|` (:538, :557). W1 therefore carries the hypothesis
`w ∉ Metric.closedBall c |R|`. Consequently the pool's "few-line addition via
the Cauchy theorem" is
accurate for `0 ≤ R` only; the uniform statement uses the primitive route
(:538 + slitPlane log), which the docstring itself notes is possible — or the
Cauchy route plus the `|R|` flip, which v1.2 records in full as a costed
alternative (S1AP-W1e) after correcting the v1.1 claim that the flip is absent at
the pin. Neither reading changes the difficulty class; the signature had to
change.

**The trap is PACKAGE-WIDE, not W1-local (v1.2).** v1.1 recorded this witness
only against W1's premise-form. The same `R = -1` geometry refutes A2, A3 and A4
if their `hR : 0 < R` is weakened, because at `R < 0` **every region in the
statement is empty while the contour is not**:

| object at `R = -1`, `c = 0` | value | pinned lemma |
|---|---|---|
| `Metric.closedBall 0 (-1)` | `∅` | `closedBall_eq_empty`, Pseudo/Defs.lean:468 |
| `Metric.sphere 0 (-1)` | `∅` | `sphere_eq_empty_of_neg`, :442 |
| `Metric.ball 0 (-1)` | `∅` | `ball_eq_empty`, :387 |
| the contour `C(0, -1)` | the circle of geometric radius `1` | `circleIntegral` def, CircleIntegral.lean:385 |

So `hf` and `hf₀` are vacuous, the divisor finsum is `0`, and `f` is entirely
unconstrained — which is the whole problem, since the integral is then whatever
that unconstrained `f` makes it:

- **A2 and A3.** `f = id`: LHS `∮ z in C(0,-1), (z-0)⁻¹ = 2πI ≠ 0` (:532,
  hypothesis exactly `R ≠ 0`) against A2's RHS `2πI·0 = 0`, and against A3's
  vacuously-true right-hand side.
- **A4.** `f = fun z => z⁻¹`: on the contour `‖z‖ = 1` so `z ≠ 0`, and there
  `deriv f z / f z = (-(z^2)⁻¹)/(z⁻¹) = -(z-0)⁻¹` (`deriv_inv`, Deriv/Inv.lean:66),
  giving LHS `-(2πI)` by :527 and :532. `2πI·(n:ℂ) = -2πI` has no solution with
  `n : ℕ`. *(The acceptance record judged A4's `0 < R` to be mere convenience,
  having tried only `f = id` and `f = (·)²`, which produce nonnegative counts.
  That judgement is corrected here: `∃ n : ℕ` forbids negative counts too, and at
  `R < 0` nothing stops `f` from having a pole.)*

Death condition 8 is extended accordingly.

### 5.3 Not verified, and stated as such

Nothing in this contract was elaborated; no statement is known to typecheck and
no skeleton is known to close. "Pinned" means *the named declaration exists in
the tree with the quoted signature text at the quoted line*, re-read this
session — it does not mean the assembly works. Form B's difficulty assessment
is inherited from the pool, not re-verified. The two `sorry` markers inside
W1's skeleton are stage-one display holes in a non-built document, not
proposed build content; a built PR containing them would violate death
condition 1 and the one invariant.

Retracted in v1.2 and listed here so it is not quoted from v1.1: the claim that
the codiscreteness bridge is this package's hardest step, and the claim that the
`∮`-level `|R|` flip does not exist at the pin. Both were inherited or asserted
without the counter-evidence being looked for, and both are corrected in §5.4.

### 5.4 v1.2 editorial pass (RH-015, 2026-08-09) — what was applied and what was not

This section records the application of the editorial fixes enumerated by
`notes/reviews/ARG_PRINCIPLE_ACCEPTANCE_2026_08_08.md` (stage-one acceptance,
three lenses, zero blocking findings, no lens asking for a signature change).

**Method.** That record states in terms that its findings are *claims with
locators*, produced by one lens each with no adversarial verifier, and that
cost-reducing findings in particular must be confirmed before use. Accordingly
every locator written or corrected in v1.2 was **re-opened at the pin
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`** (re-confirmed by
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`) and its
signature text read, and the two re-pricing findings were re-derived from the
source rather than accepted on report. Nothing was elaborated; there is still no
Lean toolchain here and no statement is known to typecheck.

**The two re-pricing findings, both CONFIRMED at the pin, one with its cost
estimate corrected.**

1. *A1 is not the hard step.* CONFIRMED.
   `MeromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin` reads at
   Meromorphic/IsolatedZeros.lean:99 as quoted in §0, inside `namespace
   MeromorphicAt` (:31–:130), with section variables at :24–:27 identical to A1's
   binder context. Its conclusion is punctured (`𝓝[≠] x`) where A1's is
   unpunctured (`𝓝 x`) — the shape difference is the entire delta — and the
   bridge across it is `AnalyticAt.meromorphicAt` (Meromorphic/Basic.lean:40) +
   `Filter.Eventually.frequently` (Order/Filter/Basic.lean:756, whose `[NeBot f]`
   is discharged by the `@[instance]` `NormedField.nhdsNE_neBot`,
   Normed/Field/Basic.lean:242, stated for `[NontriviallyNormedField α]` = A1's
   typeclass) + `AnalyticAt.frequently_eq_iff_eventually_eq`
   (Analytic/IsolatedZeros.lean:141). **Applied:** locators into §0; `S1AP-BRIDGE`
   HIGH → LOW and no longer gating; the "single genuinely new move" and "the
   pool's named hardest step" prose rewritten in §Candidate fields, §Grounding,
   §2 A1 and §5.1; the two-line discharge recorded as A1's primary skeleton with
   the v1.1 filter-algebra proof kept as fallback; the name-collision scan's
   limitation stated where the scan is.
2. *The `|R|` flip.* CONFIRMED as to existence; **cost estimate not confirmed.**
   `Real.circleAverage_abs_radius` is at CircleAverage.lean:135, `@[simp]`,
   inside `namespace Real` (:42–:382), on `circleAverage_neg_radius` (:129) and
   `circleAverage_eq_integral_add` (:117); and a full grep of
   `neg_radius|abs_radius` over CircleIntegral.lean confirms no `∮`-level flip is
   named there. **Applied:** the CircleAverage locators into §0; the v1.1 "does
   not exist at the pin" claim replaced by the accurate present-as-mathematics /
   absent-as-a-named-lemma statement, in W1's alternative-route paragraph and in
   DEFERRED-AP4; the Cauchy+flip route written out in full with its ingredients.
   **Partially declined:** the finding's "~3 lines" and its proposal to promote
   Cauchy+flip to primary and *retire* `S1AP-W1a`/`W1b`/`W1c`. The only bridge at
   the pin from `circleAverage` to `circleIntegral`
   (`circleAverage_eq_circleIntegral`, :96) carries a `(z - c)⁻¹ •` weight, and
   cancelling that weight cannot use `circleIntegral.integral_congr` (:425)
   because its `0 ≤ R` excludes precisely the negative-radius case the flip
   exists for; the derivation therefore needs :430 (or an unfold), a `smul`/`mul`
   step and an `R = 0` split. Promoting the route substitutes a new MEDIUM
   obligation (**S1AP-W1e**, added) for two existing ones rather than retiring
   them, so the log-primitive route stays primary and W1a/W1b/W1c stay live.
   Demoting them on an unconfirmed cost claim is exactly the "invites a drafter
   to skip preparation" failure the acceptance record warned about.

**The soundness finding, applied package-wide and SHARPENED.** `0 < R` is
required for TRUTH in A2, A3 **and A4**, and death condition 8 now says so. The
acceptance record judged A4's `0 < R` to be convenience after trying `f = id` and
`f = (·)²`; that is corrected in §5.2 with `f = (·)⁻¹`, `c = 0`, `R = -1`, which
gives `∮ = -2πI` and leaves `∃ n : ℕ` unsatisfiable. All four empty-region
lemmas and `deriv_inv` behind these witnesses are now in §0.

**The remaining fixes, all applied:** the FactorizedRational "open set" docstring
warning (span corrected to :285–:290); the verbatim `logDeriv_mul` :54–:56 and
`logDeriv_prod` :73–:75 quotes, whose v1.1 elisions hid an explicit positional
argument; the three-level lambda-shape hazard in `S1AP-LOGD` with
`Pi.mul_apply`/`Pi.smul_apply` resolved to real declaration sites; the
locator-free auxiliaries of the W1 and A3/A4 dependency lines; the rewritten
Divisor.lean namespace note, which v1.1 stated in a way that inverted the risk;
the `refine … (f := …) ?_` in W1's skeleton; the full
`domains/riemann-hypothesis/drafts/` path; the `S1-GLOBAL-ZEROS` paraphrase
replaced by the row's real text at `MATHLIB_CAPABILITY_MAP.md:387`; the settled
closes/advances/partially-closes/inventory-only formula; the stage-two shelf and
prefix; the unnamed "consumers in sight" clause of DEFERRED-AP5, deleted; the
shape-neutrality statement; and the W1 effort claim in §Expected information
gain.

**Locator corrections made while applying, relative to the acceptance record's
own citations** (each re-read this pass): the FactorizedRational docstring is at
:285–:290, not :284–:290; `logDeriv_mul` spans :54–:56 with its proof at :57;
the shape-neutrality precedent in the RH queue is at
`tasks/RIEMANN_HYPOTHESIS.md:831–:832` and `:844`, not `:790–:792`;
`PREFIX_DOMAINS` is at `scripts/gen_researchos_registry.py:46–:54` with
`DOMAIN_SUBTREES` at `:60–:63` and the governing comment at `:56–:59`;
`Real.circleAverage_eq_circleIntegral` is at CircleAverage.lean:96;
`Pi.smul_apply` and `Finset.sum_nonneg` have **no declaration lines** — they are
`to_additive` twins generated at Notation/Pi/Defs.lean:135 and
Order/BigOperators/Group/Finset.lean:119 respectively; and `Int.toNat_of_nonneg`
has **no `Mathlib/` declaration site at all**, so no locator is given for it.

**NOT DONE, because each requires a public signature change.** Two enumerated
fixes stop here rather than proceed. Under the two-stage gate the acceptance is
valid only for the surface as it stands, so applying either would silently
invalidate the acceptance it claims to implement; both return the surface to
contract review if a reviewer still wants them.

- *Rename A1* to match the pinned family, e.g.
  `AnalyticAt.eventuallyEq_nhds_of_eventuallyEq_codiscreteWithin` (acceptance
  record, truth lens finding 1). A declaration name is part of its signature. The
  substance of the finding — that A1 is a corollary, not a new move — is applied
  in full; only the rename is withheld. Recorded as S1AP-A1b.
- *Rename W1* to `..._of_notMem_closedBall_abs` or `..._of_abs_lt_dist`
  (acceptance record, truth lens finding 4). Same reason. The finding offered a
  second, non-signature repair — require a docstring on the built declaration
  stating the ball is `closedBall c |R|` — and **that one is applied**, under W1's
  statement.
- Related, and also withheld: adopting the pin's `R ≠ 0` + `|R|` convention across
  A2–A4 (truth lens finding 3's second half) would restate three conclusions and
  six hypotheses. The finding's alternative — one sentence justifying the
  deliberate split — **is applied**, under A2.

**Standing of v1.2.** This pass carries **no kernel verdict**, adds no ledger
row, creates no drafts-lane file, changes no barrier row, and selects no route.
All five public signatures are byte-identical to v1.0 and v1.1.

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

**Destination shelf and ledger lane, named here so the promotion PR does not
have to guess (added v1.2, acceptance record claim-boundary finding 3).** *This
package is domain-neutral.* Its built form belongs on the domain-neutral shelf
`ResearchOS/Analysis/ArgPrinciple.lean`, **NOT** under
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`. Three repo facts make that
placement mandatory rather than stylistic:

1. The ledger prefix map is a **closed machine whitelist**, not a convention:
   `scripts/gen_researchos_registry.py:46–:54` (`PREFIX_DOMAINS`) maps exactly
   `nt-`, `RH-`, `MB-`, `HK-`, `PL-`, `TC-`, `GO-` and nothing else, and
   `DOMAIN_SUBTREES` at `:60–:63` forces `riemann-hypothesis` rows under
   `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/` and `analysis-generic`
   rows under `ResearchOS/Analysis/`.
2. The in-file comment at `:56–:59` states the rule this package falls under:
   "domain-neutral lemmas may not be filed inside a conjecture program's subtree,
   where they would read as that program's content." (`VERIFIED_RESEARCHOS.md:22–25`
   restates it.)
3. The drafts-lane promotion invariant at
   `domains/riemann-hypothesis/drafts/README.md:40–:45` says a promoted draft
   moves "only together with its `RH-*` ledger rows" — **and that `RH-*` default
   does not apply here.** It is the RH-lane default; the four generic packages
   already on the domain-neutral shelf (MellinBound, HarnackDisc, PolyLiouville,
   ThreeCircles — `domains/riemann-hypothesis/drafts/README.md:32–:35`) each carry their own
   `analysis-generic` prefix instead.

So a stage-two promotion of this package needs **a newly registered prefix**
(e.g. `AP-`) added to `PREFIX_DOMAINS` mapping to `analysis-generic`, in the same
PR, following the MellinBound/Harnack/PolyLiouville/ThreeCircles pattern.
Registering that prefix is part of the promotion change; **this document
registers nothing and adds no ledger row of any status.**

### What current CI does and does not say about the draft

`domains/riemann-hypothesis/drafts/ArgPrinciple.lean`, if created, lies outside
every lake target (`lakefile.toml:2`), exactly as recorded for the drafts lane at
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
