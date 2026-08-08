/-
NON-BUILT DRAFT — growth-order definitional surface (`S1-GROWTH` definitional
pillar), G0-G2 + L1-L6.

This file is the drafts-lane Lean transcription of
`domains/riemann-hypothesis/ENTIRE_ORDER_CONTRACT.md` (DRAFT v1, 2026-08-07;
red-team audit Annex A applied in place; stage-one INDEPENDENT ACCEPTANCE
2026-08-07, record `notes/reviews/ENTIRE_ORDER_ACCEPTANCE_2026_08_07.md` —
"ACCEPT WITH APPLIED EDITORIAL FIXES", zero signature changes; that record,
per the contract's death condition 1, is what unlocks exactly this
transcription and nothing downstream). The POST-fix statement blocks are the
ones transcribed below. It is NOT part of any lake target (`lakefile.toml`
declares `defaultTargets = ["Ecdlp", "ResearchOS"]`; nothing under `domains/`
is built), it is outside the CI proof-completeness gate's scan surface, and
the Lean kernel has NOT checked it. No CI run on any acceptance PR is
evidence of anything about this file (contract §Two-stage gate). The kernel's
verdict is delivered only by a separate stage-two built promotion PR.

Statement surface: G0-G2 + L1-L6, exactly 9 public signatures (3 `def` +
6 theorems), each CHARACTER-IDENTICAL (docstrings included) to its contract
`lean` block. Complete proof bodies throughout: no proof placeholder of any
kind and no new axiom (contract death condition 2). Every junk convention is
kept symmetric between G1 and G2 (death condition 4); L4 is proved
unconditionally as stated (death condition 5); no statement evaluates
`growthType` outside its documented gate (death condition 6). Nothing here
mentions ζ, ξ, zero counting, Hadamard factorization, or any route
obligation; `S1-GROWTH` (MATHLIB_CAPABILITY_MAP.md:388) remains OPEN — a
definition supplies zero quantitative bounds — and this file closes no
barrier row, selects no route, and carries no claim about the truth of RH
(contract §Claim boundary; RH-queue authority `tasks/RIEMANN_HYPOTHESIS.md`).

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0), toolchain
`leanprover/lean4:v4.31.0` — re-verified this session via
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`. Every lemma
named in a proof below was grep-verified against that tree this session
(locators in the contract's §0 / pinned API table, plus the additional
proof-side locators recorded inline below). No Lean toolchain exists in this
environment; source reading only.

Obligation register carried from the contract (severities unchanged):
S1G-0 LOW, S1G-1 LOW, S1G-2 LOW, S1G-L1 LOW (Annex A F2), S1G-L2 **HIGH**,
S1G-L3 LOW-MED, S1G-L4 MEDIUM, S1G-L5 **HIGH**, S1G-L6 LOW. The two HIGH
obligations receive full best-effort bodies below with their routes and
fallbacks documented inline at the declaration; neither statement is
weakened (contract: L2 must not become `≤ ε` or `natDegree = 0`; an L5 with
statement-level `+ ε` slack is a pre-labeled FAILED design gate — the ε used
inside L5's proof is proof-internal only and never reaches the statement).

Registered proof-shape notes (statements untouched):
* L1 — the contract skeleton's two constant-branches are subsumed into one
  `Tendsto` route: `Filter.Tendsto.const_div_atTop` (Field.lean:222) needs no
  sign hypothesis on the constant, so both branches close through the same
  `limsup_congr` + `Tendsto.limsup_eq` pair the skeleton already cites.
* L2 Step 1 uses `Asymptotics.IsBigO.bound` (Asymptotics/Defs.lean:157)
  rather than `exists_pos`: the inner clamp makes positivity of the
  polynomial constant unnecessary (it is clamped through `max C 1`).
* L4 uses `div_le_div_of_nonneg_right` with only `0 ≤ c`, exactly as Annex
  A.1 sharpened it.
* L5 Step 4's "ENNReal ε-induction" is realized by
  `ENNReal.le_of_forall_pos_le_add` (Data/ENNReal/Basic.lean:605) plus
  constant-translation-commutes-with-limsup via
  `Monotone.map_limsup_of_continuousAt` (Topology/Order/LiminfLimsup.lean:588,
  autoParams free in ℝ≥0∞) with `continuous_add_const` and the pinned
  `instance : ContinuousAdd ℝ≥0∞` (Topology/Algebra/Ring/Real.lean:118),
  then `limsup_max` (Order/LiminfLimsup.lean:1141). The two traps the
  contract records are avoided: `ENNReal.limsup_add_le` (needs
  `[CountableInterFilter]`, which `atTop : Filter ℝ` is not) is never used,
  and `ENNReal.limsup_mul_le'` is never applied to the quotients.

Preamble note: the import block is carried character-identical from the
contract §2 ("name-resolution review only"). Proof-side constants
(`comap_norm_atTop`, `IsLittleO.tendsto_div_nhds_zero`,
`Monotone.map_limsup_of_continuousAt`, `Tendsto.const_div_atTop`,
`NormedSpace.sphere_nonempty`, `isCompact_sphere`) are expected in the
public-import closure of these five imports; if stage-two elaboration
reports an unknown constant, the fix is an added import line, never a
statement change.
-/
import Mathlib.Analysis.Complex.Trigonometric      -- Complex.norm_exp
import Mathlib.Analysis.Polynomial.Basic           -- Polynomial.isBigO_cobounded_of_degree_le
import Mathlib.Analysis.SpecialFunctions.Pow.Real  -- rpow for growthType
import Mathlib.Topology.Instances.ENNReal.Lemmas   -- ENNReal limsup API, continuous_ofReal
import Mathlib.Analysis.Complex.Hadamard           -- sSupNormIm precedent (comment-cited only)

open Filter Metric
open scoped ENNReal Topology

namespace Complex
variable {E : Type*} [NormedAddCommGroup E]

/-! ### G0. The maximum-modulus carrier `[GEN]` `[PIN]` — obligation S1G-0 (LOW) -/

/-- `M(f, r) = sup {‖f z‖ : ‖z‖ = r}`, as a bare real `sSup` in the style of
`Complex.HadamardThreeLines.sSupNormIm` (Hadamard.lean:77). Total: junk value `0`
when the sphere is empty (`r < 0`, `Real.sSup_empty`) or the image is unbounded
(`Real.sSup_of_not_bddAbove`); nonnegative always (`Real.sSup_nonneg` — norms). -/
noncomputable def maxModulus (f : ℂ → E) (r : ℝ) : ℝ :=
  sSup ((norm ∘ f) '' Metric.sphere (0 : ℂ) r)

/-! ### G1. The growth order `[GEN]` `[PIN]` — THE definition under review —
obligation S1G-1 (LOW) -/

/-- The growth order of `f : ℂ → E`, valued in `ℝ≥0∞`:
`limsup_{r→∞} log log (max (M(f,r)) 1) / log r`, clamped into `[0,∞]`.

Degenerate-case conventions, stated exactly and shared verbatim with `growthType`:
* inner clamp `max … 1`: the argument of the inner `Real.log` is `≥ 1`, so the
  `Real.log = log |·|` junk on negatives (Log/Basic.lean:44) is never reached and
  the inner log is `≥ 0`; without this clamp a modulus decaying like `exp (-r)`
  would receive order 1 (see contract §1.1);
* outer clamp `ENNReal.ofReal`: transient negative quotients (outer log of a value
  in `(0,1)`, i.e. `1 < maxModulus f r < e`; endpoints give quotient exactly `0` —
  at `M ≤ 1` the outer-log argument is `0` and `log 0 = 0`, at `M = e` it is `1`)
  collapse to `0`;
* classical footing: `Real.log (max x 1)` is exactly `log⁺ x`, so with the outer
  clamp this definition is the textbook `log⁺ log⁺` formulation of order (see §1.1);
* `maxModulus` junk (empty sphere at `r < 0`, `Real.sSup_empty`; unbounded
  norm-image at some `r`, `Real.sSup_of_not_bddAbove` — impossible for entire `f`
  but the definition is total): the junk value `0` is lifted to `1` by the inner
  clamp and contributes `0`; identical in `growthType` through the common `G0`
  carrier, so this junk convention is symmetric by construction;
* consequences: `growthOrder f = 0` for `f = 0`, for constants, and for every `f`
  with `maxModulus f · ≤ 1` eventually — the textbook convention for bounded
  entire functions;
* for nonconstant entire `f` the clamps are eventually inactive and the value is
  the classical order. That fact is NOT asserted by this definition and no lemma
  below depends on it. -/
noncomputable def growthOrder (f : ℂ → E) : ℝ≥0∞ :=
  Filter.limsup
    (fun r : ℝ =>
      ENNReal.ofReal (Real.log (Real.log (max (maxModulus f r) 1)) / Real.log r))
    Filter.atTop

/-! ### G2. The growth type, gated on finite positive order `[GEN]` `[PIN]` —
obligation S1G-2 (LOW; `r ^ p` must elaborate via the `Pow ℝ ℝ` rpow instance,
Pow/Real.lean:38, not `Monoid.npow`) -/

/-- The type of `f` relative to exponent `p`:
`limsup_{r→∞} log (max (M(f,r)) 1) / r ^ p`, with the SAME two clamps as
`growthOrder` (inner `max … 1`, outer `ENNReal.ofReal`) so the degenerate-case
conventions of order and type are identical.

GATE (design-bearing, enforced by documentation and by death condition 6, not by a
hypothesis binder): `growthType f p` is meaningful only when
`0 < p` and `growthOrder f = ENNReal.ofReal p` — i.e. finite positive order. The
definition is total (repo totalization convention; junk documented):
* `p ≤ 0`: junk (the gate excludes it; no lemma below is stated there);
* `r ^ p` is `Real.rpow` (Pow/Real.lean:35, instance :38); its own junk at
  negative bases is invisible under `atTop`;
* bounded `f`, `0 < p`: inner log eventually `0`, so `growthType f p = 0`. -/
noncomputable def growthType (f : ℂ → E) (p : ℝ) : ℝ≥0∞ :=
  Filter.limsup
    (fun r : ℝ => ENNReal.ofReal (Real.log (max (maxModulus f r) 1) / r ^ p))
    Filter.atTop

/-! ### L1. Order of a constant is zero `[GEN]` `[PIN]` — the smoke test —
obligation S1G-L1 (LOW, Annex A F2: closer instances pinned at
Topology/Order/Real.lean:53/:55).

Route note (registered in the header): the skeleton's two branches
(`log K ≤ 1` / `1 < log K`) are subsumed — `Tendsto.const_div_atTop`
(Topology/Algebra/Order/Field.lean:222) sends `log (log K) / log r` to `0`
for EVERY sign of the constant numerator, and `ENNReal.continuous_ofReal`
(Topology/Instances/ENNReal/Lemmas.lean:70) pushes the limit through the
clamp; both skeleton closers (`limsup_congr` :265 and `Tendsto.limsup_eq`,
Topology/Order/LiminfLimsup.lean:191, `[NeBot atTop]` satisfied) are used. -/

theorem growthOrder_const (c : E) : growthOrder (fun _ : ℂ => c) = 0 := by
  unfold growthOrder
  -- Step 1 (contract): for 0 ≤ r the carrier is the constant ‖c‖:
  -- nonempty sphere (NormedSpace.sphere_nonempty, RCLike/Real.lean:128), constant
  -- image (Set.Nonempty.image_const, Data/Set/Image.lean:276), csSup_singleton
  -- (ConditionallyCompletePartialOrder/Basic.lean:120).
  have hM : ∀ r : ℝ, 0 ≤ r → maxModulus (fun _ : ℂ => c) r = ‖c‖ := by
    intro r hr
    unfold maxModulus
    have himg : (norm ∘ fun _ : ℂ => c) = fun _ : ℂ => ‖c‖ := rfl
    rw [himg, Set.Nonempty.image_const (NormedSpace.sphere_nonempty.mpr hr) ‖c‖]
    exact csSup_singleton _
  -- Step 2: the integrand is eventually the r-family of one fixed constant quotient.
  have hcongr : ∀ᶠ r : ℝ in Filter.atTop,
      ENNReal.ofReal
          (Real.log (Real.log (max (maxModulus (fun _ : ℂ => c) r) 1)) / Real.log r)
        = ENNReal.ofReal (Real.log (Real.log (max ‖c‖ 1)) / Real.log r) := by
    filter_upwards [eventually_ge_atTop (0 : ℝ)] with r hr
    rw [hM r hr]
  -- Step 3: constant / log r → 0 (any sign of the constant), pushed through ofReal.
  have htendsto : Filter.Tendsto
      (fun r : ℝ => ENNReal.ofReal (Real.log (Real.log (max ‖c‖ 1)) / Real.log r))
      Filter.atTop (𝓝 0) := by
    have h1 : Filter.Tendsto
        (fun r : ℝ => Real.log (Real.log (max ‖c‖ 1)) / Real.log r)
        Filter.atTop (𝓝 0) :=
      Real.tendsto_log_atTop.const_div_atTop _
    simpa [Function.comp_def] using (ENNReal.continuous_ofReal.tendsto 0).comp h1
  rw [Filter.limsup_congr hcongr]
  exact htendsto.limsup_eq

/-! ### L2. Order of a polynomial is zero `[GEN]` `[ASM]` — the required test,
honestly costed — obligation S1G-L2 (**HIGH**).

This is the first of the two HIGH bodies. The named hard step (contract Step
3, the unassembled `log log (C·rⁿ) / log r → 0` asymptotic — no assembled
lemma exists at the pin, re-confirmed by Annex A.5 and by the acceptance
panel) is assembled here from pinned pieces only:

  clamp majorization   max (M P r) 1 ≤ max C 1 * r ^ n            (Step 2 + clamp)
  log-algebra          log (max C 1 * rⁿ) = log (max C 1) + n·log r
                                            (Real.log_mul :132, Real.log_pow :287)
  linear absorption    log (max C 1) + n·log r ≤ D·log r  for log r ≥ 1,
                       D := max (log (max C 1) + n) 1     (le_mul_of_one_le_right)
  outer log            log log (max (M P r) 1) ≤ log D + log log r  (Real.log_le_log :150)
  vanishing bound      (log D + log log r)/log r → 0
                       (Tendsto.const_div_atTop Field.lean:222;
                        Real.isLittleO_log_id_atTop :449 →
                        IsLittleO.tendsto_div_nhds_zero, Asymptotics/Lemmas.lean:362,
                        composed with tendsto_log_atTop :350)
  closer               limsup_le_limsup (:198, autoParams free in ℝ≥0∞) against
                       Tendsto.limsup_eq, plus le_antisymm with zero_le.

The degenerate branch (inner `log⁺` still `≤ 1`) collapses through
`ENNReal.ofReal_eq_zero` exactly as in L4.

FALLBACK (honest, per contract): if any seam above resists elaboration at
stage two, L2 splits into its own stage-two PR (the contract explicitly
allows landing L1/L3-L6 first); the statement must NOT be weakened to an
`≤ ε` phrasing or to a `natDegree = 0` special case. -/

theorem growthOrder_polynomial (P : Polynomial ℂ) :
    growthOrder (fun z : ℂ => P.eval z) = 0 := by
  unfold growthOrder
  -- Step 1 (pinned): Polynomial.isBigO_cobounded_of_degree_le
  -- (Analysis/Polynomial/Basic.lean:362; section variables :341, ℂ qualifies)
  -- against Q := X ^ P.natDegree (degree_X_pow, degree_le_natDegree), extracted
  -- by IsBigO.bound (Asymptotics/Defs.lean:157).
  obtain ⟨C, hC⟩ :=
    (Polynomial.isBigO_cobounded_of_degree_le (P := P) (Q := Polynomial.X ^ P.natDegree)
      (by rw [Polynomial.degree_X_pow]; exact Polynomial.degree_le_natDegree)).bound
  have hcb : ∀ᶠ z : ℂ in Bornology.cobounded ℂ,
      ‖P.eval z‖ ≤ C * ‖z‖ ^ P.natDegree := by
    filter_upwards [hC] with z hz
    simpa only [Polynomial.eval_pow, Polynomial.eval_X, norm_pow] using hz
  -- Step 2 (pinned): transfer to spheres through comap_norm_atTop
  -- (Analysis/Normed/Group/Bounded.lean:32, `comap norm atTop = cobounded ℂ`)
  -- and Filter.eventually_comap (Order/Filter/Map.lean:121); then csSup_le (:202)
  -- over the nonempty norm-image (sphere_nonempty, RCLike/Real.lean:128).
  rw [← comap_norm_atTop, Filter.eventually_comap] at hcb
  have hM : ∀ᶠ r : ℝ in Filter.atTop,
      maxModulus (fun z : ℂ => P.eval z) r ≤ C * r ^ P.natDegree := by
    filter_upwards [hcb, eventually_ge_atTop (0 : ℝ)] with r hr hr0
    unfold maxModulus
    refine csSup_le ((NormedSpace.sphere_nonempty.mpr hr0).image _) ?_
    rintro y ⟨z, hz, rfl⟩
    have hzr : ‖z‖ = r := mem_sphere_zero_iff_norm.mp hz
    have hb2 := hr z hzr
    rw [hzr] at hb2
    exact hb2
  -- Step 3 (the S1G-L2 HIGH step, assembled): pointwise majorization by
  -- (log D + log log r) / log r with a single constant D ≥ 1.
  set D : ℝ := max (Real.log (max C 1) + (P.natDegree : ℝ)) 1 with hDdef
  have arith2 : ∀ x r : ℝ, 1 < r → 1 ≤ Real.log r → x ≤ C * r ^ P.natDegree →
      ENNReal.ofReal (Real.log (Real.log (max x 1)) / Real.log r)
        ≤ ENNReal.ofReal ((Real.log D + Real.log (Real.log r)) / Real.log r) := by
    intro x r hr1 hlogr1 hx
    have hr0 : (0 : ℝ) < r := lt_trans zero_lt_one hr1
    have hlogr0 : (0 : ℝ) < Real.log r := lt_of_lt_of_le zero_lt_one hlogr1
    rcases le_or_lt (Real.log (max x 1)) 1 with hL1 | hL1
    · -- degenerate branch: outer log nonpositive, ofReal-collapse (Real.lean:181).
      have hq : Real.log (Real.log (max x 1)) / Real.log r ≤ 0 :=
        div_nonpos_of_nonpos_of_nonneg
          (Real.log_nonpos (Real.log_nonneg (le_max_right _ _)) hL1) hlogr0.le
      calc ENNReal.ofReal (Real.log (Real.log (max x 1)) / Real.log r) = 0 :=
            ENNReal.ofReal_eq_zero.mpr hq
        _ ≤ _ := zero_le _
    · -- main branch: 1 < log (max x 1).
      have hM1 : (0 : ℝ) < max x 1 := lt_of_lt_of_le zero_lt_one (le_max_right _ _)
      have hrpow0 : (0 : ℝ) < r ^ P.natDegree := pow_pos hr0 _
      have h11 : (1 : ℝ) * 1 ≤ max C 1 * r ^ P.natDegree :=
        mul_le_mul (le_max_right _ _) (one_le_pow₀ hr1.le) zero_le_one
          (le_trans zero_le_one (le_max_right _ _))
      rw [one_mul] at h11
      have h1 : max x 1 ≤ max C 1 * r ^ P.natDegree :=
        max_le (hx.trans (mul_le_mul_of_nonneg_right (le_max_left _ _) hrpow0.le)) h11
      have hLD : Real.log (max x 1) ≤ D * Real.log r := by
        calc Real.log (max x 1)
            ≤ Real.log (max C 1 * r ^ P.natDegree) := Real.log_le_log hM1 h1
          _ = Real.log (max C 1) + Real.log (r ^ P.natDegree) :=
              Real.log_mul (ne_of_gt (lt_of_lt_of_le zero_lt_one (le_max_right _ _)))
                (ne_of_gt hrpow0)
          _ = Real.log (max C 1) + (P.natDegree : ℝ) * Real.log r := by
              rw [Real.log_pow]
          _ ≤ (Real.log (max C 1) + (P.natDegree : ℝ)) * Real.log r := by
              rw [add_mul]
              exact add_le_add
                (le_mul_of_one_le_right (Real.log_nonneg (le_max_right _ _)) hlogr1)
                le_rfl
          _ ≤ D * Real.log r := by
              refine mul_le_mul_of_nonneg_right ?_ hlogr0.le
              rw [hDdef]
              exact le_max_left _ _
      have hlogL :
          Real.log (Real.log (max x 1)) ≤ Real.log D + Real.log (Real.log r) := by
        calc Real.log (Real.log (max x 1))
            ≤ Real.log (D * Real.log r) :=
              Real.log_le_log (lt_trans zero_lt_one hL1) hLD
          _ = Real.log D + Real.log (Real.log r) := by
              refine Real.log_mul (ne_of_gt ?_) (ne_of_gt hlogr0)
              rw [hDdef]
              exact lt_of_lt_of_le zero_lt_one (le_max_right _ _)
      exact ENNReal.ofReal_le_ofReal (div_le_div_of_nonneg_right hlogL hlogr0.le)
  have hbound : ∀ᶠ r : ℝ in Filter.atTop,
      ENNReal.ofReal
          (Real.log (Real.log (max (maxModulus (fun z : ℂ => P.eval z) r) 1))
            / Real.log r)
        ≤ ENNReal.ofReal ((Real.log D + Real.log (Real.log r)) / Real.log r) := by
    filter_upwards [hM, eventually_gt_atTop (1 : ℝ), eventually_ge_atTop (Real.exp 1)]
      with r hMr hr1 hre
    have hlogr1 : (1 : ℝ) ≤ Real.log r := by
      have h := Real.log_le_log (Real.exp_pos 1) hre
      rwa [Real.log_exp] at h
    exact arith2 _ r hr1 hlogr1 hMr
  -- Step 4: the majorant vanishes — this is the previously-unassembled asymptotic.
  have hb : Filter.Tendsto
      (fun r : ℝ => (Real.log D + Real.log (Real.log r)) / Real.log r)
      Filter.atTop (𝓝 0) := by
    have h1 : Filter.Tendsto (fun r : ℝ => Real.log D / Real.log r)
        Filter.atTop (𝓝 0) :=
      Real.tendsto_log_atTop.const_div_atTop _
    have h2 : Filter.Tendsto (fun r : ℝ => Real.log (Real.log r) / Real.log r)
        Filter.atTop (𝓝 0) := by
      simpa [Function.comp_def] using
        Real.isLittleO_log_id_atTop.tendsto_div_nhds_zero.comp Real.tendsto_log_atTop
    have h3 := h1.add h2
    rw [add_zero] at h3
    exact h3.congr fun r => (add_div _ _ _).symm
  have hb' : Filter.Tendsto
      (fun r : ℝ => ENNReal.ofReal ((Real.log D + Real.log (Real.log r)) / Real.log r))
      Filter.atTop (𝓝 0) := by
    simpa [Function.comp_def] using (ENNReal.continuous_ofReal.tendsto 0).comp hb
  refine le_antisymm ?_ (zero_le _)
  calc Filter.limsup
        (fun r : ℝ =>
          ENNReal.ofReal
            (Real.log (Real.log (max (maxModulus (fun z : ℂ => P.eval z) r) 1))
              / Real.log r))
        Filter.atTop
      ≤ Filter.limsup
          (fun r : ℝ =>
            ENNReal.ofReal ((Real.log D + Real.log (Real.log r)) / Real.log r))
          Filter.atTop := Filter.limsup_le_limsup hbound
    _ = 0 := hb'.limsup_eq

/-! ### L3. Order of `exp` is one `[GEN]` `[PIN]` — pinned ingredients SUFFICE —
obligation S1G-L3 (LOW-MED: the `IsGreatest` pair is assembled in image form;
`mem_sphere_zero_iff_norm` is `to_additive`-GENERATED from
`mem_sphere_one_iff_norm`, Analysis/Normed/Group/Basic.lean:302-303 — a
declaration-grep finds nothing, generation site is the citation). No limsup
asymptotic is consumed anywhere: the integrand is eventually EXACTLY 1. -/

theorem growthOrder_exp : growthOrder Complex.exp = 1 := by
  unfold growthOrder
  -- Step 1: maxModulus exp r = Real.exp r for 0 ≤ r, by IsGreatest.csSup_eq
  -- (ConditionallyCompletePartialOrder/Basic.lean:72): membership via
  -- Complex.norm_of_nonneg (Norm.lean:106) + Complex.norm_exp
  -- (Trigonometric.lean:995, Complex span :954-:1002) + Complex.ofReal_re
  -- (Data/Complex/Basic.lean:88); upper bound via re_le_norm (Norm.lean:43) +
  -- Real.exp_le_exp (Analysis/Complex/Exponential.lean:315).
  have hM : ∀ r : ℝ, 0 ≤ r → maxModulus Complex.exp r = Real.exp r := by
    intro r hr
    unfold maxModulus
    refine IsGreatest.csSup_eq ⟨⟨(r : ℂ), ?_, ?_⟩, ?_⟩
    · rw [mem_sphere_zero_iff_norm]
      exact Complex.norm_of_nonneg hr
    · show ‖Complex.exp (r : ℂ)‖ = Real.exp r
      rw [Complex.norm_exp, Complex.ofReal_re]
    · rintro y ⟨z, hz, rfl⟩
      have hzr : ‖z‖ = r := mem_sphere_zero_iff_norm.mp hz
      calc (norm ∘ Complex.exp) z = Real.exp z.re := Complex.norm_exp z
        _ ≤ Real.exp r := Real.exp_le_exp.mpr (le_trans (Complex.re_le_norm z) hzr.le)
  -- Steps 2-4: clamp inactive (one_le_exp, Exponential.lean:279; max_eq_left),
  -- log_exp (:74) twice-nested collapses the double log, div_self with
  -- log_pos (:187); eventually-constant, closed by limsup_congr (:265) +
  -- limsup_const (:284) + ofReal_one (Data/ENNReal/Basic.lean:291).
  have hcongr : ∀ᶠ r : ℝ in Filter.atTop,
      ENNReal.ofReal
          (Real.log (Real.log (max (maxModulus Complex.exp r) 1)) / Real.log r)
        = (1 : ℝ≥0∞) := by
    filter_upwards [eventually_gt_atTop (1 : ℝ)] with r hr1
    have hr0 : (0 : ℝ) ≤ r := (lt_trans zero_lt_one hr1).le
    rw [hM r hr0, max_eq_left (Real.one_le_exp hr0), Real.log_exp,
      div_self (ne_of_gt (Real.log_pos hr1)), ENNReal.ofReal_one]
  rw [Filter.limsup_congr hcongr]
  exact Filter.limsup_const 1

/-! ### L4. Comparison/monotonicity `[GEN]` `[PIN]` — true BECAUSE of the clamps —
obligation S1G-L4 (MEDIUM: pure case-assembly, no unassembled asymptotics).
Unconditional as stated — death condition 5 protects this signature. The
`e`-threshold is phrased as `1 < Real.log (max … 1)` and the constant `e` is
never introduced, exactly as the contract requires. -/

theorem growthOrder_le_of_eventually_le {f : ℂ → E} {g : ℂ → E}
    (h : ∀ᶠ r in Filter.atTop, maxModulus f r ≤ maxModulus g r) :
    growthOrder f ≤ growthOrder g := by
  unfold growthOrder
  -- The two-branch clamp case split of the skeleton, abstracted over the two
  -- clamped carriers x ≤ y (1 ≤ x) and the positive denominator lr:
  -- • outer log ≤ 0: quotient ≤ 0, ofReal-collapse (ofReal_eq_zero, Real.lean:181);
  -- • otherwise 1 < log x is forced (log_nonpos :221 / log_nonneg :212 argue by
  --   contradiction), and the chain log_le_log (:150) → log_le_log again →
  --   div_le_div_of_nonneg_right (GroupWithZero/Basic.lean:1199, needs only 0 ≤ c,
  --   Annex A.1) → ofReal_le_ofReal (Real.lean:137) closes.
  have mono_step : ∀ x y lr : ℝ, 0 < lr → 1 ≤ x → x ≤ y →
      ENNReal.ofReal (Real.log (Real.log x) / lr)
        ≤ ENNReal.ofReal (Real.log (Real.log y) / lr) := by
    intro x y lr hlr hx hxy
    rcases le_or_lt (Real.log (Real.log x)) 0 with hc | hc
    · calc ENNReal.ofReal (Real.log (Real.log x) / lr) = 0 :=
            ENNReal.ofReal_eq_zero.mpr (div_nonpos_of_nonpos_of_nonneg hc hlr.le)
        _ ≤ _ := zero_le _
    · have hlx1 : 1 < Real.log x := by
        by_contra hle
        push_neg at hle
        exact absurd (Real.log_nonpos (Real.log_nonneg hx) hle) (not_le.mpr hc)
      have h1 : Real.log x ≤ Real.log y :=
        Real.log_le_log (lt_of_lt_of_le zero_lt_one hx) hxy
      have h2 : Real.log (Real.log x) ≤ Real.log (Real.log y) :=
        Real.log_le_log (lt_trans zero_lt_one hlx1) h1
      exact ENNReal.ofReal_le_ofReal (div_le_div_of_nonneg_right h2 hlr.le)
  -- limsup_le_limsup (:198; autoParams discharged by isBoundedDefault in ℝ≥0∞)
  -- reduces to the eventual pointwise bound; max_le_max (Order/MinMax.lean:54)
  -- transports the carrier bound through the inner clamp.
  refine Filter.limsup_le_limsup ?_
  filter_upwards [h, eventually_gt_atTop (1 : ℝ)] with r hfg hr
  exact mono_step _ _ _ (Real.log_pos hr) (le_max_right _ _) (max_le_max hfg le_rfl)

/-! ### L5. Order of a product is at most the max `[GEN]` `[ASM]` —
obligation S1G-L5 (**HIGH**).

This is the second HIGH body. Route, step by step (contract Steps 1-4):
Step 1 — carrier submultiplicativity on nonempty spheres: csSup_le (:202) /
le_csSup (:198), BddAbove from isCompact_sphere (ProperSpace.lean:45) +
IsCompact.image + IsCompact.bddAbove (Topology/Order/Compact.lean:322) — this
is where the load-bearing continuity hypotheses earn their keep.
Step 2 — clamp submultiplicativity max (ab) 1 ≤ max a 1 * max b 1 (the small
unpinned private fact, an inline `have`).
Step 3 — Real.log_mul (:132) on the clamped factors (both ≥ 1 > 0).
Step 4 — the ε-absorption (previously unassembled): pointwise
  log⁺log⁺(prod) ≤ log 2 / log r + max of the two quotients
(two-case: WLOG-ordered halves through an inline `main`, degenerate branch
ofReal-collapsed as in L4), then ENNReal.ofReal_add_le (Real.lean:57),
Tendsto.eventually_le_const (dual of OrderClosed.lean:242) to trade the
vanishing log 2 / log r term for a proof-internal ε,
ENNReal.le_of_forall_pos_le_add (Basic.lean:605) to discharge ε, constant
translation through the limsup by Monotone.map_limsup_of_continuousAt
(Topology/Order/LiminfLimsup.lean:588; continuous_add_const with the pinned
ContinuousAdd ℝ≥0∞, Topology/Algebra/Ring/Real.lean:118), and finally
limsup_max (Order/LiminfLimsup.lean:1141, root-level name, autoParams free).

Traps avoided (contract §0): ENNReal.limsup_add_le
(Order/Filter/ENNReal.lean:231) is NEVER used — `atTop : Filter ℝ` is not a
CountableInterFilter; ENNReal.limsup_mul_le' is NEVER applied to the
quotients (the quotient of a product is not the product of quotients).

FALLBACK (honest, per contract): if the Step-4 assembly resists at stage
two, the only sanctioned retreat is a statement-level `+ ε` slack, and the
contract pre-labels that a FAILED design gate — record it as such and stop;
do not silently reshape the statement. The ε below is proof-internal only. -/

theorem growthOrder_mul_le {f g : ℂ → ℂ} (hf : Continuous f) (hg : Continuous g) :
    growthOrder (f * g) ≤ max (growthOrder f) (growthOrder g) := by
  unfold growthOrder
  -- carrier nonnegativity (Real.sSup_nonneg, Archimedean/Real/Basic.lean:294 —
  -- norms; junk values included).
  have hMnn : ∀ (k : ℂ → ℂ) (r : ℝ), 0 ≤ maxModulus k r := by
    intro k r
    unfold maxModulus
    refine Real.sSup_nonneg ?_
    rintro y ⟨z, _, rfl⟩
    exact norm_nonneg _
  -- Step 1: submultiplicativity of the carrier for 0 ≤ r.
  have hsub : ∀ r : ℝ, 0 ≤ r →
      maxModulus (f * g) r ≤ maxModulus f r * maxModulus g r := by
    intro r hr
    have hbf : BddAbove ((norm ∘ f) '' Metric.sphere (0 : ℂ) r) :=
      ((isCompact_sphere (0 : ℂ) r).image (continuous_norm.comp hf)).bddAbove
    have hbg : BddAbove ((norm ∘ g) '' Metric.sphere (0 : ℂ) r) :=
      ((isCompact_sphere (0 : ℂ) r).image (continuous_norm.comp hg)).bddAbove
    unfold maxModulus
    refine csSup_le ((NormedSpace.sphere_nonempty.mpr hr).image _) ?_
    rintro y ⟨z, hz, rfl⟩
    have h1 : ‖f z‖ ≤ sSup ((norm ∘ f) '' Metric.sphere (0 : ℂ) r) :=
      le_csSup hbf ⟨z, hz, rfl⟩
    have h2 : ‖g z‖ ≤ sSup ((norm ∘ g) '' Metric.sphere (0 : ℂ) r) :=
      le_csSup hbg ⟨z, hz, rfl⟩
    calc (norm ∘ (f * g)) z = ‖f z‖ * ‖g z‖ := by
          simp [Function.comp_apply, Pi.mul_apply, norm_mul]
      _ ≤ sSup ((norm ∘ f) '' Metric.sphere (0 : ℂ) r)
            * sSup ((norm ∘ g) '' Metric.sphere (0 : ℂ) r) :=
          mul_le_mul h1 h2 (norm_nonneg _) (le_trans (norm_nonneg _) h1)
  -- Step 2: clamp submultiplicativity (the small unpinned private fact).
  have hclamp : ∀ a b : ℝ, 0 ≤ a → 0 ≤ b → max (a * b) 1 ≤ max a 1 * max b 1 := by
    intro a b _ hb
    refine max_le ?_ ?_
    · exact mul_le_mul (le_max_left _ _) (le_max_left _ _) hb
        (le_trans zero_le_one (le_max_right _ _))
    · have h11 : (1 : ℝ) * 1 ≤ max a 1 * max b 1 :=
        mul_le_mul (le_max_right _ _) (le_max_right _ _) zero_le_one
          (le_trans zero_le_one (le_max_right _ _))
      rwa [one_mul] at h11
  -- Steps 3-4a: the pointwise log⁺log⁺ subadditivity, over abstract clamped
  -- values 1 ≤ x, y, z with z ≤ x*y and a positive denominator lr.
  have arith : ∀ x y z lr : ℝ, 0 < lr → 1 ≤ x → 1 ≤ y → 1 ≤ z → z ≤ x * y →
      ENNReal.ofReal (Real.log (Real.log z) / lr)
        ≤ ENNReal.ofReal (Real.log 2 / lr)
            + max (ENNReal.ofReal (Real.log (Real.log x) / lr))
                  (ENNReal.ofReal (Real.log (Real.log y) / lr)) := by
    intro x y z lr hlr hx hy hz hzxy
    have hLz : Real.log z ≤ Real.log x + Real.log y := by
      calc Real.log z ≤ Real.log (x * y) :=
            Real.log_le_log (lt_of_lt_of_le zero_lt_one hz) hzxy
        _ = Real.log x + Real.log y :=
            Real.log_mul (ne_of_gt (lt_of_lt_of_le zero_lt_one hx))
              (ne_of_gt (lt_of_lt_of_le zero_lt_one hy))
    rcases le_or_lt (Real.log z) 1 with h1 | h1
    · -- degenerate branch collapses through the ofReal clamp as in L4.
      have hq : Real.log (Real.log z) / lr ≤ 0 :=
        div_nonpos_of_nonpos_of_nonneg (Real.log_nonpos (Real.log_nonneg hz) h1) hlr.le
      calc ENNReal.ofReal (Real.log (Real.log z) / lr) = 0 :=
            ENNReal.ofReal_eq_zero.mpr hq
        _ ≤ _ := zero_le _
    · -- main branch: Lz ≤ Lu + Lv ≤ 2·(the larger), log 2 splits off (log_mul).
      have main : ∀ u v : ℝ, v ≤ u → Real.log z ≤ u + v →
          ENNReal.ofReal (Real.log (Real.log z) / lr)
            ≤ ENNReal.ofReal (Real.log 2 / lr) + ENNReal.ofReal (Real.log u / lr) := by
        intro u v hvu hsum
        have hu2 : Real.log z ≤ 2 * u := by linarith
        have hupos : (0 : ℝ) < u := by linarith
        have hlogle : Real.log (Real.log z) ≤ Real.log 2 + Real.log u := by
          calc Real.log (Real.log z) ≤ Real.log (2 * u) :=
                Real.log_le_log (lt_trans zero_lt_one h1) hu2
            _ = Real.log 2 + Real.log u :=
                Real.log_mul (by norm_num) (ne_of_gt hupos)
        calc ENNReal.ofReal (Real.log (Real.log z) / lr)
            ≤ ENNReal.ofReal ((Real.log 2 + Real.log u) / lr) :=
              ENNReal.ofReal_le_ofReal (div_le_div_of_nonneg_right hlogle hlr.le)
          _ = ENNReal.ofReal (Real.log 2 / lr + Real.log u / lr) := by rw [add_div]
          _ ≤ ENNReal.ofReal (Real.log 2 / lr) + ENNReal.ofReal (Real.log u / lr) :=
              ENNReal.ofReal_add_le
      rcases le_total (Real.log y) (Real.log x) with hle | hle
      · exact (main (Real.log x) (Real.log y) hle hLz).trans
          (add_le_add_left (le_max_left _ _) _)
      · exact (main (Real.log y) (Real.log x) hle (by linarith)).trans
          (add_le_add_left (le_max_right _ _) _)
  -- The eventual pointwise bound, instantiated at the three clamped carriers.
  have key : ∀ᶠ r : ℝ in Filter.atTop,
      ENNReal.ofReal (Real.log (Real.log (max (maxModulus (f * g) r) 1)) / Real.log r)
        ≤ ENNReal.ofReal (Real.log 2 / Real.log r)
            + max (ENNReal.ofReal
                    (Real.log (Real.log (max (maxModulus f r) 1)) / Real.log r))
                  (ENNReal.ofReal
                    (Real.log (Real.log (max (maxModulus g r) 1)) / Real.log r)) := by
    filter_upwards [eventually_gt_atTop (1 : ℝ)] with r hr1
    have hr0 : (0 : ℝ) ≤ r := (lt_trans zero_lt_one hr1).le
    refine arith (max (maxModulus f r) 1) (max (maxModulus g r) 1)
      (max (maxModulus (f * g) r) 1) (Real.log r) (Real.log_pos hr1)
      (le_max_right _ _) (le_max_right _ _) (le_max_right _ _) ?_
    exact (max_le_max (hsub r hr0) le_rfl).trans (hclamp _ _ (hMnn f r) (hMnn g r))
  -- Step 4b: ε-absorption of the vanishing log 2 / log r term.
  refine ENNReal.le_of_forall_pos_le_add fun ε hε _ => ?_
  have hev : ∀ᶠ r : ℝ in Filter.atTop, Real.log 2 / Real.log r ≤ (ε : ℝ) :=
    (Real.tendsto_log_atTop.const_div_atTop (Real.log 2)).eventually_le_const
      (NNReal.coe_pos.mpr hε)
  have hkey2 : ∀ᶠ r : ℝ in Filter.atTop,
      ENNReal.ofReal (Real.log (Real.log (max (maxModulus (f * g) r) 1)) / Real.log r)
        ≤ max (ENNReal.ofReal
                (Real.log (Real.log (max (maxModulus f r) 1)) / Real.log r))
              (ENNReal.ofReal
                (Real.log (Real.log (max (maxModulus g r) 1)) / Real.log r))
            + (ε : ℝ≥0∞) := by
    filter_upwards [key, hev] with r h1 h2
    refine h1.trans ?_
    rw [add_comm]
    refine add_le_add_left ?_ _
    calc ENNReal.ofReal (Real.log 2 / Real.log r)
        ≤ ENNReal.ofReal ((ε : ℝ)) := ENNReal.ofReal_le_ofReal h2
      _ = (ε : ℝ≥0∞) := ENNReal.ofReal_coe_nnreal
  have hmono : Monotone fun x : ℝ≥0∞ => x + (ε : ℝ≥0∞) :=
    fun _ _ h => add_le_add_right h _
  calc Filter.limsup
        (fun r : ℝ =>
          ENNReal.ofReal
            (Real.log (Real.log (max (maxModulus (f * g) r) 1)) / Real.log r))
        Filter.atTop
      ≤ Filter.limsup
          (fun r : ℝ =>
            max (ENNReal.ofReal
                  (Real.log (Real.log (max (maxModulus f r) 1)) / Real.log r))
                (ENNReal.ofReal
                  (Real.log (Real.log (max (maxModulus g r) 1)) / Real.log r))
              + (ε : ℝ≥0∞))
          Filter.atTop := Filter.limsup_le_limsup hkey2
    _ = Filter.limsup
          (fun r : ℝ =>
            max (ENNReal.ofReal
                  (Real.log (Real.log (max (maxModulus f r) 1)) / Real.log r))
                (ENNReal.ofReal
                  (Real.log (Real.log (max (maxModulus g r) 1)) / Real.log r)))
          Filter.atTop + (ε : ℝ≥0∞) :=
        -- REVIEW NOTE (2026-08-07): the pinned lemma's RHS is `F.limsup (f ∘ a)`
        -- (Topology/Order/LiminfLimsup.lean:592); matching it against the
        -- beta-reduced lambda in this calc step is definitional (comp + beta,
        -- default transparency). If stage-two elaboration balks at the seam,
        -- the fix is a `show`/`simp only [Function.comp_def]` normalization in
        -- this body — never a statement change.
        (hmono.map_limsup_of_continuousAt
          (fun r : ℝ =>
            max (ENNReal.ofReal
                  (Real.log (Real.log (max (maxModulus f r) 1)) / Real.log r))
                (ENNReal.ofReal
                  (Real.log (Real.log (max (maxModulus g r) 1)) / Real.log r)))
          ((continuous_add_const _).continuousAt)).symm
    _ = max
          (Filter.limsup
            (fun r : ℝ =>
              ENNReal.ofReal
                (Real.log (Real.log (max (maxModulus f r) 1)) / Real.log r))
            Filter.atTop)
          (Filter.limsup
            (fun r : ℝ =>
              ENNReal.ofReal
                (Real.log (Real.log (max (maxModulus g r) 1)) / Real.log r))
            Filter.atTop) + (ε : ℝ≥0∞) := by
        rw [limsup_max
          (u := fun r : ℝ =>
            ENNReal.ofReal (Real.log (Real.log (max (maxModulus f r) 1)) / Real.log r))
          (v := fun r : ℝ =>
            ENNReal.ofReal (Real.log (Real.log (max (maxModulus g r) 1)) / Real.log r))]

/-! ### L6. Type of `exp` at exponent one `[GEN]` `[PIN]` — the type's smoke test —
obligation S1G-L6 (LOW; the `r ^ (1 : ℝ)` rpow-vs-npow elaboration pitfall of
S1G-2 applies here concretely — `Real.rpow_one` (Pow/Real.lean:148) is the
matching rewrite). By L3, `growthOrder Complex.exp = 1 = ENNReal.ofReal 1`
with `0 < 1`, so this statement sits INSIDE G2's gate (death condition 6):
the pair (L3, L6) is the classical (order, type) = (1, 1) calibration. -/

theorem growthType_exp : growthType Complex.exp 1 = 1 := by
  unfold growthType
  -- Reuses L3's Step 1 verbatim (duplicated inline: the 9-signature surface
  -- admits no extra public helper declaration).
  have hM : ∀ r : ℝ, 0 ≤ r → maxModulus Complex.exp r = Real.exp r := by
    intro r hr
    unfold maxModulus
    refine IsGreatest.csSup_eq ⟨⟨(r : ℂ), ?_, ?_⟩, ?_⟩
    · rw [mem_sphere_zero_iff_norm]
      exact Complex.norm_of_nonneg hr
    · show ‖Complex.exp (r : ℂ)‖ = Real.exp r
      rw [Complex.norm_exp, Complex.ofReal_re]
    · rintro y ⟨z, hz, rfl⟩
      have hzr : ‖z‖ = r := mem_sphere_zero_iff_norm.mp hz
      calc (norm ∘ Complex.exp) z = Real.exp z.re := Complex.norm_exp z
        _ ≤ Real.exp r := Real.exp_le_exp.mpr (le_trans (Complex.re_le_norm z) hzr.le)
  -- For r > 1: clamp inactive, log_exp (:74), rpow_one (Pow/Real.lean:148),
  -- div_self; eventually-constant, limsup_congr (:265) + limsup_const (:284).
  have hcongr : ∀ᶠ r : ℝ in Filter.atTop,
      ENNReal.ofReal (Real.log (max (maxModulus Complex.exp r) 1) / r ^ (1 : ℝ))
        = (1 : ℝ≥0∞) := by
    filter_upwards [eventually_gt_atTop (1 : ℝ)] with r hr1
    have hr0 : (0 : ℝ) ≤ r := (lt_trans zero_lt_one hr1).le
    rw [hM r hr0, max_eq_left (Real.one_le_exp hr0), Real.log_exp, Real.rpow_one,
      div_self (ne_of_gt (lt_trans zero_lt_one hr1)), ENNReal.ofReal_one]
  rw [Filter.limsup_congr hcongr]
  exact Filter.limsup_const 1

end Complex
