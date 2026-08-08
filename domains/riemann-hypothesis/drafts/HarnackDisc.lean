/-
DRAFTS-LANE MIRROR — Harnack double inequality on a disc (UPSTREAM-POOL §5),
H1-H5.

This file is the drafts-lane copy of the built module
`ResearchOS/Analysis/HarnackDisc.lean`, implementing
`domains/riemann-hypothesis/HARNACK_CONTRACT.md` (statement surface
independently accepted 2026-08-07, `notes/reviews/HARNACK_ACCEPTANCE_2026_08_07.md`;
promotion record `notes/reviews/HARNACK_PROMOTION_2026_08_08.md`). From the
first `import` below through end of file it is byte-identical to the built
module; only this leading header differs. It is NOT part of any lake target
and is not itself kernel-checked: the kernel's verdict applies to the built
copy, and any proof-only repair must be applied to both copies before a new
CI run. A statement change stops promotion and returns to contract review.

The package is generic complex analysis: it closes no barrier row, selects no
route, and says nothing about the Riemann Hypothesis.

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0).
-/
import Mathlib.Analysis.Complex.Harmonic.Poisson
-- The contract's proposed preamble, verbatim. A single import suffices: at the
-- pin, `Analysis/Complex/Harmonic/Poisson.lean` has
-- `public import Mathlib.Analysis.Complex.Harmonic.MeanValue` and
-- `public import Mathlib.Analysis.Complex.Poisson` (its lines :8-:9), and the
-- pin uses the Lean module system (`module` / `public import`), so visibility
-- is a closure property: Harmonic/MeanValue, Complex/Poisson, CircleAverage,
-- CircleIntegral, the InnerProductSpace harmonic API, and all order/norm glue
-- named below are in the transitive public-import closure. This drafts-lane
-- file uses plain `import` (contract §0b: not the pin's `module`/`public
-- import` idiom), so the whole closure is visible.

open Complex InnerProductSpace Metric Real
-- Contract preamble, verbatim. `InnerProductSpace` is load-bearing for the
-- bare spelling `HarmonicOnNhd` inside the H3-H5 statements; `Real` for
-- `circleAverage`'s namespace (primary spellings below are nevertheless
-- qualified `Real.circleAverage`, so a lost `open` degrades, not breaks);
-- `Metric` mirrors `Harmonic/Poisson.lean:24` house style (primary spellings
-- of `sphere`/`ball`/`closedBall` below are qualified `Metric.…` because the
-- contract statements spell them so).

/-! ## Block A — kernel glue (pinned bounds re-expressed on `poissonKernel`)

## H1. Two-sided kernel bound on the sphere `[GEN]` `[PIN]`

Repackages the two pinned sharp bounds `le_re_herglotzRieszKernel` /
`re_herglotzRieszKernel_le` (Analysis/Complex/Poisson.lean:134/:101, both
re-read verbatim at the pin this session, hypothesis order `(hz) (hw)`) from
the expanded quotient `((z - c + (w - c)) / ((z - c) - (w - c))).re` onto
`poissonKernel` via the function-level bridge
`poissonKernel_eq_re_herglotzRieszKernel` (Poisson.lean:73) and
`herglotzRieszKernel_def` (Poisson.lean:39). The private aux
`poissonKernel_eq_re_herglotzRieszKernel_aux` (Poisson.lean:60) is not usable
and is not used. -/

theorem poissonKernel_mem_Icc {c w z : ℂ} {R : ℝ}
    (hz : z ∈ Metric.sphere c R) (hw : w ∈ Metric.ball c R) :
    poissonKernel c w z ∈
      Set.Icc ((R - ‖w - c‖) / (R + ‖w - c‖)) ((R + ‖w - c‖) / (R - ‖w - c‖)) := by
  have hkey : poissonKernel c w z = ((z - c + (w - c)) / ((z - c) - (w - c))).re := by
    simp only [poissonKernel_eq_re_herglotzRieszKernel, Function.comp_apply,
      herglotzRieszKernel_def]                       -- Poisson.lean:73, :39
    -- OBLIG H-1a (LOW): the syntactic seam. `simp only` must rewrite the applied
    -- head `poissonKernel c w z` with the FUNCTION-LEVEL equality :73, then
    -- `Function.comp_apply`-reduce `(Complex.re ∘ herglotzRieszKernel c w) z`,
    -- then unfold :39 to exactly the quotient the bound theorems are stated on
    -- (`z - c + (w - c)` and `(z - c) + (w - c)` are the same parse: `-`/`+`
    -- are both infixl:65).
    -- Fallback (contract-recorded, avoids head-rewrite under application):
    --   have := congrFun (poissonKernel_eq_re_herglotzRieszKernel (c := c) (w := w)) z
    --   simpa [herglotzRieszKernel_def] using this
  exact ⟨hkey ▸ le_re_herglotzRieszKernel hz hw,     -- Poisson.lean:134
         hkey ▸ re_herglotzRieszKernel_le hz hw⟩     -- Poisson.lean:101
  -- OBLIG H-1a cont. (LOW): the anonymous constructor relies on `∈ Set.Icc`
  -- unfolding to the conjunction, and `hkey ▸` on the rewrite-direction
  -- heuristic of `▸` against a known expected type.
  -- Fallback (contract-recorded, direction-explicit):
  --   refine Set.mem_Icc.mpr ?_
  --   constructor <;> rw [hkey]
  --   · exact le_re_herglotzRieszKernel hz hw
  --   · exact re_herglotzRieszKernel_le hz hw

/-! ## H2. Continuity of the Poisson kernel on the sphere `[GEN]` `[PIN]`

The in-tree analogue `continuousOn_herglotz_riesz`
(Analysis/Complex/Harmonic/Poisson.lean:30-35) is `private lemma` and cannot be
cited (contract §0a item 4, obligation H-2a — the largest single obligation of
the package); this re-proves the (easier) `poissonKernel` form by the same
pattern: nonvanishing `have` in the local context, then `fun_prop`. -/

theorem continuousOn_poissonKernel {c w : ℂ} {R : ℝ} (hw : w ∈ Metric.ball c R) :
    ContinuousOn (poissonKernel c w) (Metric.sphere c R) := by
  have hne : ∀ z ∈ Metric.sphere c R, (z - c) - (w - c) ≠ 0 := by
    intro z hz h
    rw [sub_eq_zero] at h                            -- z - c = w - c
    have h₁ : ‖w - c‖ < R := mem_ball_iff_norm.1 hw
      -- to_additive twin of mem_ball_iff_norm'', Analysis/Normed/Group/Basic.lean:869
    have h₂ : ‖z - c‖ = R := mem_sphere_iff_norm.1 hz
      -- to_additive twin of mem_sphere_iff_norm', Basic.lean:886 (attr :885)
    rw [h] at h₂
    linarith
  have hne' : ∀ z ∈ Metric.sphere c R, ‖(z - c) - (w - c)‖ ^ 2 ≠ 0 :=
    fun z hz => pow_ne_zero 2 (norm_ne_zero_iff.mpr (hne z hz))
    -- pow_ne_zero: Algebra/GroupWithZero/Basic.lean:258;
    -- norm_ne_zero_iff: to_additive twin at Analysis/Normed/Group/Basic.lean:999.
    -- Materializes the side condition the skeleton's comment names, so that
    -- both the `fun_prop` discharger and `aesop` can close it by assumption.
  unfold poissonKernel
  fun_prop (disch := aesop)
  -- OBLIG H-2a (MEDIUM): `fun_prop` must prove ContinuousOn of the real
  -- quotient with side goal (shape) ∀ z ∈ sphere c R, ‖(z - c) - (w - c)‖ ^ 2 ≠ 0,
  -- available verbatim as hne'. In-tree precedent for the exact pattern
  -- (nonvanishing `have` + fun_prop on a ContinuousOn-of-quotient goal):
  -- the private Harmonic/Poisson.lean:30-35.
  -- NOISE NOTE (CI on PR #318): this line was ACCEPTED by the kernel, but it
  -- emitted two "aesop failed to prove the goal after exhaustive search"
  -- warnings. Diagnosis: `fun_prop`'s discharger is
  -- `first | with_reducible assumption | (tac)` (Tactic/FunProp/Elab.lean:87-96).
  -- The side goal that is actually needed is `ContinuousOn.div₀`'s
  -- `∀ x ∈ s, g x ≠ 0` (Topology/Algebra/GroupWithZero.lean:233-236) — hne'
  -- verbatim — so it is closed by `with_reducible assumption` and never reaches
  -- the discharger at all. The two aesop calls were spent on the UNPROVABLE side
  -- goals of the competing candidates `Continuous.div₀` / `ContinuousAt.div₀`
  -- (same file :224-:232), whose conditions `∀ x, g x ≠ 0` / `g a ≠ 0` are false
  -- off the sphere. The warnings are therefore cosmetic, not a latent defect.
  -- `(disch := assumption)` would silence them on that reading, but it is a
  -- change to a line the kernel has already accepted, and this round is a repair
  -- of three genuine rejections; it is deliberately NOT made here. If the noise
  -- is ever worth removing, it is a separate change with its own CI round.
  -- Fallback 1 (Annex A6 shape — the in-tree private proof uses a PLAIN
  --   `fun_prop`, no disch argument, with the nonvanishing fact as a `have` in
  --   the local context): fun_prop
  -- Fallback 2 (fully explicit, contract-recorded):
  --   apply ContinuousOn.div
  --   · exact ((continuous_norm.comp (continuous_id.sub continuous_const)).pow 2
  --       |>.sub continuous_const).continuousOn
  --   · exact ((continuous_norm.comp ((continuous_id.sub continuous_const).sub
  --       continuous_const)).pow 2).continuousOn
  --   · exact fun z hz => pow_ne_zero 2 (norm_ne_zero_iff.mpr (hne z hz))
  -- Fallback 3 (contract-recorded): prove continuity on the larger set
  --   {z | ‖z - c‖ ∈ Set.Ioc ‖w - c‖ R} mimicking Harmonic/Poisson.lean:30-35
  --   verbatim, then `.mono` down to the sphere.
  -- If all routes fail: contract death condition 3 — stop, do not weaken the
  -- integrability side conditions downstream.

/-! ## Block B — the deliverable

## H3. Harnack double inequality on a disc, explicit constants `[GEN]` `[PIN]`

Load-bearing pinned inputs, all re-read verbatim at the pin this session:
the Poisson representation
`InnerProductSpace.HarmonicOnNhd.circleAverage_poissonKernel_smul`
(Analysis/Complex/Harmonic/Poisson.lean:91 — hypothesis on `closedBall c R`,
NOT `|R|`), the mean value `HarmonicOnNhd.circleAverage_eq`
(Analysis/Complex/Harmonic/MeanValue.lean:27 — ROOT-LEVEL name, the file has
`open InnerProductSpace` and no `namespace` command (contract Annex A2), so
bare-name calls only; its hypothesis is on `closedBall c |R|`), and
`Real.circleAverage_mono` (MeasureTheory/Integral/CircleAverage.lean:271 —
BOTH integrability arguments are mandatory; `Real.circleAverage` of a
non-integrable function is `0` by definition, so dropping them would make the
chain unsound, contract claim boundary "junk-value honesty").

Delta vs `UPSTREAM_POOL.md:490-497`: `hR : 0 < R` dropped as redundant —
`Metric.pos_of_mem_ball hw` recovers it (contract §0a item 5). The constants
are the sharp classical ones; sharpness itself is NOT claimed as a statement. -/

theorem InnerProductSpace.HarmonicOnNhd.harnack {f : ℂ → ℝ} {c w : ℂ} {R : ℝ}
    (hf : HarmonicOnNhd f (Metric.closedBall c R))
    (h₀ : ∀ z ∈ Metric.closedBall c R, 0 ≤ f z)
    (hw : w ∈ Metric.ball c R) :
    (R - ‖w - c‖) / (R + ‖w - c‖) * f c ≤ f w ∧
      f w ≤ (R + ‖w - c‖) / (R - ‖w - c‖) * f c := by
  have hR : 0 < R := Metric.pos_of_mem_ball hw       -- Pseudo/Defs.lean:376
  have habs : |R| = R := abs_of_pos hR
    -- to_additive twin of mabs_of_one_lt, Algebra/Order/Group/Unbundled/Abs.lean:93
  -- pinned representation (the load-bearing input):
  have hrep : Real.circleAverage (poissonKernel c w • f) c R = f w :=
    hf.circleAverage_poissonKernel_smul hw           -- Harmonic/Poisson.lean:91
    -- dot notation resolves: the representation lives in namespace
    -- InnerProductSpace (Harmonic/Poisson.lean:28), same as `hf`'s head.
  -- pinned mean value at the center (|R| plumbing, OBLIG H-3b site 1):
  have hmean : Real.circleAverage f c R = f c :=
    HarmonicOnNhd.circleAverage_eq (by rwa [habs])   -- MeanValue.lean:27, ROOT-LEVEL
    -- Only the root-level name exists, so this resolves unambiguously even
    -- under `open InnerProductSpace`; dot notation `hf.circleAverage_eq` would
    -- NOT resolve (Annex A2) and is not used.
    -- Fallback (fully explicit root anchor):
    --   _root_.HarmonicOnNhd.circleAverage_eq (show HarmonicOnNhd f
    --     (Metric.closedBall c |R|) by rwa [habs])
  -- integrability:
  have hfc : ContinuousOn f (Metric.sphere c R) :=
    hf.contDiffOn.continuousOn.mono Metric.sphere_subset_closedBall
      -- InnerProductSpace/Harmonic/Basic.lean:51; ContDiff/Defs.lean:551;
      -- Pseudo/Defs.lean:480
  have hintf : CircleIntegrable f c R := hfc.circleIntegrable hR.le
      -- CircleIntegral.lean:337
  have hint : CircleIntegrable (poissonKernel c w • f) c R :=
    hintf.smul_of_continuousOn
      (show ContinuousOn (poissonKernel c w) (Metric.sphere c |R|) by
        rw [habs]; exact continuousOn_poissonKernel hw)
      -- CircleIntegral.lean:247 (its `g` wants `sphere c |R|`, hence the
      -- explicit `show` + `rw [habs]`; 𝕜 := ℝ, F := ℝ, instances
      -- NormedRing/Module/NormSMulClass all pinned). OBLIG H-3b site 2,
      -- discharged by the contract-recorded fallback.
      -- KERNEL NOTE (CI on PR #318): the earlier spelling
      --   hintf.smul_of_continuousOn (habs ▸ continuousOn_poissonKernel hw)
      -- is rejected. With an expected type present, `h ▸ e` rewrites the
      -- EXPECTED TYPE by `h.symm`, i.e. it replaces every `R` in
      -- `ContinuousOn (poissonKernel c w) (sphere c |R|)` by `|R|`, yielding
      -- `sphere c |(|R|)|` and forcing `hw : w ∈ ball c |(|R|)|` — the
      -- reported application type mismatch. Rewriting the goal forward with
      -- `rw [habs]` under a `show` fixes the direction: it turns the demanded
      -- `sphere c |R|` into `sphere c R`, which is exactly H2's carrier.
      -- Do NOT reintroduce `habs ▸` here (nor `(habs ▸ ·)` variants): the
      -- direction, not the lemma, was wrong.
  -- pointwise comparison on the sphere (H1 × nonnegativity), OBLIG H-3a:
  have hlow : ∀ z ∈ Metric.sphere c |R|,
      (((R - ‖w - c‖) / (R + ‖w - c‖)) • f) z ≤ (poissonKernel c w • f) z := by
    intro z hz
    rw [habs] at hz                                  -- OBLIG H-3b site 3
    simpa only [Pi.smul_apply', Pi.smul_apply, smul_eq_mul] using
      mul_le_mul_of_nonneg_right (poissonKernel_mem_Icc hz hw).1
        (h₀ z (Metric.sphere_subset_closedBall hz))
    -- OBLIG H-3a (MEDIUM): `poissonKernel c w • f` is function-on-function smul
    -- (Pi.smul_apply' shape, Algebra/Group/Action/Pi.lean:41: (s • x) i = s i • x i)
    -- while the quotient smul is scalar-on-function (Pi.smul_apply, to_additive
    -- twin of Pi.pow_apply, Algebra/Notation/Pi/Defs.lean:135-136: (a • f) i = a • f i);
    -- both must land on `_ * f z` via smul_eq_mul (Algebra/Group/Action/Defs.lean:74)
    -- before mul_le_mul_of_nonneg_right (Algebra/Order/GroupWithZero/Defs.lean:230,
    -- shape b ≤ c → 0 ≤ a → b * a ≤ c * a) applies.
    -- Fallback (contract-recorded, defeq route): replace the `simpa only` with
    --   show ((R - ‖w - c‖) / (R + ‖w - c‖)) * f z ≤ poissonKernel c w z * f z
    --   exact mul_le_mul_of_nonneg_right (poissonKernel_mem_Icc hz hw).1
    --     (h₀ z (Metric.sphere_subset_closedBall hz))
  have hhigh : ∀ z ∈ Metric.sphere c |R|,
      (poissonKernel c w • f) z ≤ (((R + ‖w - c‖) / (R - ‖w - c‖)) • f) z := by
    intro z hz
    rw [habs] at hz
    simpa only [Pi.smul_apply', Pi.smul_apply, smul_eq_mul] using
      mul_le_mul_of_nonneg_right (poissonKernel_mem_Icc hz hw).2
        (h₀ z (Metric.sphere_subset_closedBall hz))
    -- OBLIG H-3a, same seam as hlow; same defeq fallback with the inequality
    -- reversed:
    --   show poissonKernel c w z * f z ≤ ((R + ‖w - c‖) / (R - ‖w - c‖)) * f z
    --   exact mul_le_mul_of_nonneg_right (poissonKernel_mem_Icc hz hw).2
    --     (h₀ z (Metric.sphere_subset_closedBall hz))
  refine ⟨?_, ?_⟩
  · calc (R - ‖w - c‖) / (R + ‖w - c‖) * f c
        = Real.circleAverage (((R - ‖w - c‖) / (R + ‖w - c‖)) • f) c R := by
          rw [Real.circleAverage_smul, hmean, smul_eq_mul]
          -- CircleAverage.lean:331. OBLIG H-3c (LOW): instance search at
          -- 𝕜 = E = ℝ (NormedDivisionRing ℝ, Module ℝ ℝ, NormSMulClass ℝ ℝ,
          -- SMulCommClass ℝ ℝ ℝ — all pinned, variable block :36-:40).
          -- Fallback: rw [show (((R - ‖w - c‖) / (R + ‖w - c‖)) • f)
          --     = fun z => ((R - ‖w - c‖) / (R + ‖w - c‖)) • f z from rfl,
          --   Real.circleAverage_fun_smul, hmean, smul_eq_mul]
          --   (CircleAverage.lean:339)
      _ ≤ Real.circleAverage (poissonKernel c w • f) c R :=
          Real.circleAverage_mono hintf.const_smul hint hlow
          -- CircleAverage.lean:271; const_smul: CircleIntegral.lean:233 (A := ℝ).
          -- OBLIG H-3d (LOW): if `hintf.const_smul` fails to elaborate at the
          -- Pi-smul, the lambda-form fallback is
          --   Real.circleAverage_mono hintf.const_fun_smul hint hlow
          --   (CircleIntegral.lean:237) with hlow reshaped by `show`.
      _ = f w := hrep
  · calc f w
        = Real.circleAverage (poissonKernel c w • f) c R := hrep.symm
      _ ≤ Real.circleAverage (((R + ‖w - c‖) / (R - ‖w - c‖)) • f) c R :=
          Real.circleAverage_mono hint hintf.const_smul hhigh
      _ = (R + ‖w - c‖) / (R - ‖w - c‖) * f c := by
          rw [Real.circleAverage_smul, hmean, smul_eq_mul]
          -- same OBLIG H-3c fallback as the lower half.

/-! ## Block C — corollaries (the forms consumed downstream)

## H4. Harnack at the center: factor 3 on the half-radius ball `[GEN]` `[PIN]`

`hR : 0 < R` is genuinely needed here (contract §1 note at H4 and death
condition 5): a closed ball is nonempty at radius 0, so membership does not
force `0 < R` the way H3's open-ball hypothesis does, and both the `hw'` and
`hc` steps below consume it. -/

theorem InnerProductSpace.HarmonicOnNhd.harnack_half {f : ℂ → ℝ} {c w : ℂ} {R : ℝ}
    (hf : HarmonicOnNhd f (Metric.closedBall c R))
    (h₀ : ∀ z ∈ Metric.closedBall c R, 0 ≤ f z)
    (hR : 0 < R) (hw : w ∈ Metric.closedBall c (R / 2)) :
    f c / 3 ≤ f w ∧ f w ≤ 3 * f c := by
  have hr : ‖w - c‖ ≤ R / 2 := mem_closedBall_iff_norm.1 hw
    -- to_additive twin of mem_closedBall_iff_norm'', Normed/Group/Basic.lean:877
  have hw' : w ∈ Metric.ball c R := mem_ball_iff_norm.2 (by linarith)
  obtain ⟨h₁, h₂⟩ := hf.harnack h₀ hw'               -- H3
  have hc : 0 ≤ f c := h₀ c (Metric.mem_closedBall_self hR.le)  -- Pseudo/Defs.lean:460
  have hd₁ : 0 < R + ‖w - c‖ := by positivity
    -- OBLIG (H-4a adjunct, same scope note as H-5a): positivity must close the
    -- atom `R` from hypothesis hR. Fallback: linarith [norm_nonneg (w - c)]
  have hd₂ : 0 < R - ‖w - c‖ := by linarith [norm_nonneg (w - c)]
  constructor
  · calc f c / 3 = 1 / 3 * f c := by ring
      _ ≤ (R - ‖w - c‖) / (R + ‖w - c‖) * f c := by
          gcongr ?_ * f c
          -- OBLIG H-4a (LOW): gcongr must produce the bare fraction-comparison
          -- side goal, discharging `0 ≤ f c` from hc.
          -- Fallback (contract-recorded): replace `gcongr ?_ * f c` with
          --   apply mul_le_mul_of_nonneg_right _ hc
          rw [div_le_div_iff₀ (by norm_num) hd₁]
            -- Algebra/Order/GroupWithZero/Basic.lean:1430:
            -- a / b ≤ c / d ↔ a * d ≤ c * b
          linarith    -- 1 * (R + r) ≤ (R - r) * 3  ⟺  4r ≤ 2R  ⟸  r ≤ R/2
      _ ≤ f w := h₁
  · calc f w ≤ (R + ‖w - c‖) / (R - ‖w - c‖) * f c := h₂
      _ ≤ 3 * f c := by
          gcongr ?_ * f c
          -- same OBLIG H-4a fallback: apply mul_le_mul_of_nonneg_right _ hc
          rw [div_le_iff₀ hd₂]
            -- GroupWithZero/Basic.lean:1138 (re-verified, Annex A7):
            -- b / c ≤ a ↔ b ≤ a * c. Retired contingency, still recorded:
            -- div_le_div_iff₀ hd₂ (by norm_num : (0:ℝ) < 1) after `3 = 3 / 1`.
          linarith    -- R + r ≤ 3 * (R - r)  ⟺  4r ≤ 2R

/-! ## H5. Positivity propagation from the center `[GEN]` `[PIN]` -/

theorem InnerProductSpace.HarmonicOnNhd.pos_of_pos_center {f : ℂ → ℝ} {c w : ℂ} {R : ℝ}
    (hf : HarmonicOnNhd f (Metric.closedBall c R))
    (h₀ : ∀ z ∈ Metric.closedBall c R, 0 ≤ f z)
    (hc : 0 < f c) (hw : w ∈ Metric.ball c R) :
    0 < f w := by
  have hR : 0 < R := Metric.pos_of_mem_ball hw       -- Pseudo/Defs.lean:376
  have hrR : ‖w - c‖ < R := mem_ball_iff_norm.1 hw
  have hpos : 0 < (R - ‖w - c‖) / (R + ‖w - c‖) :=
    div_pos (by linarith) (by positivity)
    -- div_pos: GroupWithZero/Basic.lean:880.
    -- OBLIG H-5a (LOW): positivity on `R + ‖w - c‖` must close the atom `R`
    -- from hypothesis hR. Fallback: (by linarith [norm_nonneg (w - c)])
  exact lt_of_lt_of_le (mul_pos hpos hc) (hf.harnack h₀ hw).1   -- H3, lower half
