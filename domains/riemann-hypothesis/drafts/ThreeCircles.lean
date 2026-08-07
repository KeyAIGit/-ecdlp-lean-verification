/-
NON-BUILT DRAFT — Hadamard three-circles package (upstream pool item 3), TC1-TC11.

This file is the drafts-lane Lean draft of
`domains/riemann-hypothesis/THREE_CIRCLES_CONTRACT.md` (DRAFT v1, 2026-08-07;
adversarial review Annex A, verdict SOUND_WITH_FIXES, findings B1-B2 applied in
place — the POST-fix skeletons are the ones followed below). It is NOT part of
any lake target (`lakefile.toml` declares `defaultTargets = ["Ecdlp",
"ResearchOS"]`; nothing under `domains/` is built), it is outside the CI
proof-completeness gate's scan surface, and the Lean kernel has NOT checked
it. No CI run on any
acceptance PR is evidence of anything about this file (contract §Two-stage
gate). The kernel's verdict is delivered only by a separate stage-two built
promotion PR.

Statement surface: TC1-TC11, exactly 11 public signatures (1 `def` + 10
theorems), each CHARACTER-IDENTICAL to its contract `lean` block. Complete
proof bodies throughout: no proof placeholder of any kind and no new axiom
(death condition 1). No repo prerequisite: every
import below is pinned Mathlib; nothing here mentions ζ, ξ, zero counting,
growth order, or any route obligation. This draft closes no barrier row,
selects no route, and carries no claim about the truth of RH (contract §Claim
boundary; RH-queue authority `tasks/RIEMANN_HYPOTHESIS.md`, sole ACTIVE task
RH-011).

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0), toolchain
`leanprover/lean4:v4.31.0` — re-verified this session via
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`. Every lemma
named in a proof or fallback below was grep-verified against that tree this
session (locators in the contract's §0 / pinned API table).
-/
import Mathlib.Analysis.Complex.Hadamard                 -- three-lines, verticalStrip, sSupNormIm
import Mathlib.Analysis.SpecialFunctions.Complex.Arg    -- norm_mul_exp_arg_mul_I
import Mathlib.Analysis.SpecialFunctions.ExpDeriv       -- Complex.differentiable_exp
import Mathlib.Analysis.SpecialFunctions.Log.Basic      -- Real.exp_log, log_le_log, log_div
import Mathlib.Analysis.Complex.ReImTopology            -- Complex.closure_preimage_re
import Mathlib.Analysis.Complex.Trigonometric           -- Complex.norm_exp
import Mathlib.Analysis.SpecialFunctions.Pow.Real       -- Real.rpow_add', rpow_one, rpow_nonneg

open Complex Complex.HadamardThreeLines Metric Set
open scoped Real
-- Preamble carried verbatim from the contract (its import-closure sufficiency
-- was the Annex A front-5 check: the public-import closure of these seven
-- imports contains every cited module, including RCLike/Real.lean's
-- `sphere_nonempty`, Topology/Order/Compact.lean's `bddAbove_image`, and
-- Archimedean/Real/Basic.lean's `Real.sSup_le`). `open Complex.HadamardThreeLines`
-- is load-bearing: `verticalStrip` / `verticalClosedStrip` resolve bare only
-- under it (contract §0 naming trap), and the three-lines input is the PRIMED
-- `norm_le_interp_of_mem_verticalClosedStrip'` (Hadamard.lean:607) — the
-- unprimed name does not exist at the pin.

/-! ## Block A — circle-sup helper (the only `def`)

The annulus is the inline set-builder `{w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}` (resp.
strict) at every use site — no annulus `Set` object exists at the pin and none
is introduced (contract decision 1, death condition 4). -/

/-! ### TC1. Circle sup of the norm `[GEN]` `[PIN]` — the `def`

Circle twin of the pinned `sSupNormIm` (Hadamard.lean:77): a bare `sSup`,
meaningful when the image is nonempty and bounded above, junk `0` otherwise —
the conditionally-complete-lattice convention of the file being extended
(contract decision 2). -/

noncomputable def sSupNormCircle {E : Type*} [NormedAddCommGroup E]
    (f : ℂ → E) (r : ℝ) : ℝ :=
  sSup ((norm ∘ f) '' Metric.sphere (0 : ℂ) r)

/-! ### TC2. Nonnegativity `[GEN]` `[PIN]`

Mirror of the pinned `sSupNormIm_nonneg` (Hadamard.lean:99-102) verbatim. The
junk case is included: for `r < 0` the sphere is empty, the image is empty,
`sSup ∅ = 0`, and the statement still holds — no side condition. -/

lemma sSupNormCircle_nonneg {E : Type*} [NormedAddCommGroup E]
    (f : ℂ → E) (r : ℝ) : 0 ≤ sSupNormCircle f r := by
  apply Real.sSup_nonneg
  -- `apply` unfolds the `def` at default transparency; if unification balks,
  -- fallback: prepend
  --   show 0 ≤ sSup ((norm ∘ f) '' Metric.sphere (0 : ℂ) r)
  rintro y ⟨w, _, hw⟩
  simp only [← hw, Function.comp, norm_nonneg]

/-! ### TC3. Bounded above on a sphere `[GEN]` `[PIN]` -/

lemma bddAbove_image_norm_sphere {E : Type*} [NormedAddCommGroup E]
    {f : ℂ → E} {r : ℝ} (hc : ContinuousOn f (Metric.sphere (0 : ℂ) r)) :
    BddAbove ((norm ∘ f) '' Metric.sphere (0 : ℂ) r) := by
  exact (isCompact_sphere (0 : ℂ) r).bddAbove_image hc.norm
  -- OBLIG TC-COMP (LOW): `hc.norm : ContinuousOn (fun x => ‖f x‖) _` vs the
  -- goal's `norm ∘ f` — definitionally equal, matched by unification here.
  -- Fallback (contract-recorded):
  --   simpa [Function.comp] using (isCompact_sphere (0 : ℂ) r).bddAbove_image hc.norm

/-! ### TC4. Pointwise bound by the circle sup `[GEN]` `[PIN]`

Circles enter as `‖w‖ = r` binders from here on; `Metric.sphere` never leaks
into the main statements (bridge: `mem_sphere_zero_iff_norm`, TC-SPH). -/

lemma le_sSupNormCircle {E : Type*} [NormedAddCommGroup E]
    {f : ℂ → E} {r : ℝ} {w : ℂ}
    (hc : ContinuousOn f (Metric.sphere (0 : ℂ) r)) (hw : ‖w‖ = r) :
    ‖f w‖ ≤ sSupNormCircle f r := by
  exact le_csSup (bddAbove_image_norm_sphere hc)
    (Set.mem_image_of_mem _ (mem_sphere_zero_iff_norm.mpr hw))
  -- OBLIG TC-COMP (LOW): the membership produced is `(norm ∘ f) w ∈ …` with
  -- `(norm ∘ f) w` needing to be seen as `‖f w‖` (defeq). Fallback
  -- (contract-recorded): `Function.comp_apply` in a `simpa`:
  --   simpa [Function.comp_apply] using le_csSup (bddAbove_image_norm_sphere hc)
  --     (Set.mem_image_of_mem (norm ∘ f) (mem_sphere_zero_iff_norm.mpr hw))
  -- OBLIG TC-SPH (LOW) fallback: unfold `Metric.sphere` to `dist w 0 = r` and
  -- close with the `dist_zero_right`/`dist_eq_norm` simp set.

/-! ## Block B — exp-transport bookkeeping (strip ↔ annulus) -/

/-! ### TC5. `exp` carries the closed strip into the closed annulus `[GEN]` `[PIN]` -/

lemma exp_mem_annulus_of_mem_verticalClosedStrip {r₁ r₃ : ℝ}
    (h₁ : 0 < r₁) (h₃ : 0 < r₃) {w : ℂ}
    (hw : w ∈ verticalClosedStrip (Real.log r₁) (Real.log r₃)) :
    Complex.exp w ∈ {z : ℂ | r₁ ≤ ‖z‖ ∧ ‖z‖ ≤ r₃} := by
  simp only [verticalClosedStrip, Set.mem_preimage, Set.mem_Icc] at hw
  simp only [Set.mem_setOf_eq, Complex.norm_exp]
  exact ⟨by calc r₁ = Real.exp (Real.log r₁) := (Real.exp_log h₁).symm
              _ ≤ Real.exp w.re := Real.exp_le_exp.mpr hw.1,
         by calc Real.exp w.re ≤ Real.exp (Real.log r₃) := Real.exp_le_exp.mpr hw.2
              _ = r₃ := Real.exp_log h₃⟩
  -- OBLIG TC-EXP-MONO (LOW): `Real.exp_le_exp` is an iff; `.mpr` is the
  -- direction used. Fallback (contract-recorded): `gcongr` — both `Real.exp`
  -- monotonicity and `Real.log_le_log` carry `@[gcongr]`/`@[bound]` at the pin
  -- (Log/Basic.lean:149/:153 attribute lines).

/-! ### TC6. `exp` carries the open strip into the open annulus `[GEN]` `[PIN]` -/

lemma exp_mem_annulus_of_mem_verticalStrip {r₁ r₃ : ℝ}
    (h₁ : 0 < r₁) (h₃ : 0 < r₃) {w : ℂ}
    (hw : w ∈ verticalStrip (Real.log r₁) (Real.log r₃)) :
    Complex.exp w ∈ {z : ℂ | r₁ < ‖z‖ ∧ ‖z‖ < r₃} := by
  -- TC5 verbatim with `mem_Ioo` for `mem_Icc`, `exp_lt_exp` for `exp_le_exp`,
  -- strict calc steps (contract TC6 skeleton).
  simp only [verticalStrip, Set.mem_preimage, Set.mem_Ioo] at hw
  simp only [Set.mem_setOf_eq, Complex.norm_exp]
  exact ⟨by calc r₁ = Real.exp (Real.log r₁) := (Real.exp_log h₁).symm
              _ < Real.exp w.re := Real.exp_lt_exp.mpr hw.1,
         by calc Real.exp w.re < Real.exp (Real.log r₃) := Real.exp_lt_exp.mpr hw.2
              _ = r₃ := Real.exp_log h₃⟩
  -- OBLIG TC-EXP-MONO (LOW): as TC5; fallback `gcongr`.

/-! ### TC7. `exp`-surjectivity onto a circle, with real part pinned `[GEN]` `[PIN]`
— the surjectivity leg (TC-SURJ)

The witness is explicit; NO logarithm of `z` is chosen — `Complex.arg` is
total, and `norm_mul_exp_arg_mul_I` (Arg.lean:56) is stated for ALL `x` (at
`x = 0` both sides are `0`), so no branch of `log` enters anywhere (death
condition 3 guards the drift). -/

lemma exists_exp_eq_of_norm_eq {r : ℝ} (hr : 0 < r) {z : ℂ} (hz : ‖z‖ = r) :
    ∃ w : ℂ, w.re = Real.log r ∧ Complex.exp w = z := by
  refine ⟨Real.log r + z.arg * I, ?_, ?_⟩
  · simp [Complex.add_re, Complex.ofReal_re, Complex.mul_I_re, Complex.ofReal_im]
    -- OBLIG TC-SURJ (MEDIUM), friction (ii): the real-part goal must close to
    -- `Real.log r + -0 = Real.log r` (or already be closed); if the simp set
    -- leaves `-(↑z.arg).im`, `Complex.ofReal_im` is already in the listed set.
  · rw [Complex.exp_add, ← Complex.ofReal_exp, Real.exp_log hr, ← hz]
    exact Complex.norm_mul_exp_arg_mul_I z
    -- OBLIG TC-SURJ (MEDIUM), friction (i): the `rw` chain passes through
    -- `exp_add`, converts `exp ↑(Real.log r)` to `↑(Real.exp (Real.log r))`
    -- AGAINST the `@[simp]` normal form (`← ofReal_exp`), rewrites under the
    -- coercion (`Real.exp_log hr`), then folds `↑r` to `↑‖z‖` (`← hz`).
    -- Fallback (contract-recorded), if `← hz` fails to rewrite under the
    -- coercion:
    --   have hrz : (r : ℂ) = (‖z‖ : ℂ) := congrArg _ hz.symm
    --   rw [Complex.exp_add, ← Complex.ofReal_exp, Real.exp_log hr, hrz]
    --   exact Complex.norm_mul_exp_arg_mul_I z
    -- Whole-leg fallback (contract-recorded):
    --   simp [Complex.exp_add, ← Complex.ofReal_exp, Real.exp_log hr, hz,
    --     Complex.norm_mul_exp_arg_mul_I]

/-! ## Block C — the workhorse -/

/-! ### TC8. Three-circles, pointwise endpoint-bound form `[GEN]` `[PIN]`
— the exp-transport of the pinned three-lines

`^` is `Real.rpow`. The exponents are exactly what Hadamard.lean:607 emits at
`l := Real.log r₁`, `u := Real.log r₃` after the witness's real part is
rewritten to `Real.log r₂` (contract decision 3: raw strip exponents here,
zero log-algebra; the textbook ratio form is corollary TC10). -/

theorem norm_le_interp_of_norm_eq {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] {f : ℂ → E} {r₁ r₂ r₃ M₁ M₃ : ℝ} {z : ℂ}
    (h₁ : 0 < r₁) (h₁₂ : r₁ ≤ r₂) (h₂₃ : r₂ ≤ r₃) (h₁₃ : r₁ < r₃)
    (hd : DifferentiableOn ℂ f {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃})
    (hc : ContinuousOn f {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃})
    (hM₁ : ∀ w : ℂ, ‖w‖ = r₁ → ‖f w‖ ≤ M₁)
    (hM₃ : ∀ w : ℂ, ‖w‖ = r₃ → ‖f w‖ ≤ M₃)
    (hz : ‖z‖ = r₂) :
    ‖f z‖ ≤ M₁ ^ (1 - (Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁))
          * M₃ ^ ((Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁)) := by
  have h₂ : 0 < r₂ := h₁.trans_le h₁₂
  have h₃ : 0 < r₃ := h₁.trans h₁₃
  have hul : Real.log r₁ < Real.log r₃ := Real.log_lt_log h₁ h₁₃
  -- (TC-SURJ) the evaluation point upstairs: surjectivity of `exp` is needed
  -- at exactly ONE point — this one — and TC7's explicit witness supplies it.
  obtain ⟨w, hwre, hwexp⟩ := exists_exp_eq_of_norm_eq h₂ hz
  have hw : w ∈ verticalClosedStrip (Real.log r₁) (Real.log r₃) := by
    simp only [verticalClosedStrip, Set.mem_preimage, Set.mem_Icc, hwre]
    exact ⟨Real.log_le_log h₁ h₁₂, Real.log_le_log h₂ h₂₃⟩
  -- (TC-CL, MEDIUM) closure of the open strip is the closed strip — assembled,
  -- not pinned: `closure_preimage_re` (ReImTopology.lean:70) + `closure_Ioo`
  -- (DenselyOrdered.lean:72, needs `l ≠ u`, supplied by `hul.ne` — this is why
  -- `r₁ < r₃` is a hypothesis and not `r₁ ≤ r₃`).
  have hcl : closure (verticalStrip (Real.log r₁) (Real.log r₃))
      = verticalClosedStrip (Real.log r₁) (Real.log r₃) := by
    rw [verticalStrip, verticalClosedStrip, Complex.closure_preimage_re,
        closure_Ioo hul.ne]
    -- Fallback (contract-recorded), if `rw [verticalStrip]` misfires on the
    -- definitional unfold:
    --   simp only [verticalStrip, verticalClosedStrip]
    --   rw [Complex.closure_preimage_re, closure_Ioo hul.ne]
  -- MapsTo, open and closed (TC5/TC6)
  have hmapsO : Set.MapsTo Complex.exp (verticalStrip (Real.log r₁) (Real.log r₃))
      {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃} :=
    fun _ hw => exp_mem_annulus_of_mem_verticalStrip h₁ h₃ hw
  have hmapsC : Set.MapsTo Complex.exp (verticalClosedStrip (Real.log r₁) (Real.log r₃))
      {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃} :=
    fun _ hw => exp_mem_annulus_of_mem_verticalClosedStrip h₁ h₃ hw
  -- (TC-DCOC, LOW) DiffContOnCl of the composite; both fields are `protected`
  -- (DiffContOnCl.lean:33), so the anonymous constructor is forced; the
  -- `rw [hcl]` happens INSIDE the second component, not on the outer goal.
  -- Fallback (contract-recorded): the `DifferentiableOn.diffContOnCl` route
  -- via DiffContOnCl.lean:39 if the constructor fights.
  have hd' : DiffContOnCl ℂ (f ∘ Complex.exp) (verticalStrip (Real.log r₁) (Real.log r₃)) :=
    ⟨hd.comp Complex.differentiable_exp.differentiableOn hmapsO,
     by rw [hcl]; exact hc.comp Complex.continuous_exp.continuousOn hmapsC⟩
  -- (TC-BB, HIGH — the riskiest step of the package) boundedness upstairs,
  -- transported from the compact annulus. The strip is NOT compact; any
  -- "direct" boundedness on it is death condition 7. Three stacked syntactic
  -- hazards: (i) `norm ∘ (f ∘ exp)` vs `(norm ∘ f) ∘ exp` is defeq but not
  -- syntactic; (ii) `Set.image_comp` orientation (`f ∘ g '' a = f '' g '' a`,
  -- Image.lean:224) applied left-to-right with `f := norm ∘ f`, `g := exp`;
  -- (iii) `mem_closedBall_zero_iff` threaded through a set-builder membership.
  have hann : IsCompact {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃} :=
    (isCompact_closedBall (0 : ℂ) r₃).of_isClosed_subset
      ((isClosed_le continuous_const continuous_norm).inter
        (isClosed_le continuous_norm continuous_const))
      (fun w hw => mem_closedBall_zero_iff.mpr hw.2)
  have hB : BddAbove ((norm ∘ (f ∘ Complex.exp)) ''
      verticalClosedStrip (Real.log r₁) (Real.log r₃)) := by
    have hbig : BddAbove ((norm ∘ f) '' {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}) :=
      hann.bddAbove_image hc.norm
    refine hbig.mono ?_
    calc (norm ∘ (f ∘ Complex.exp)) '' verticalClosedStrip _ _
        = (norm ∘ f) '' (Complex.exp '' verticalClosedStrip _ _) :=
          Set.image_comp (norm ∘ f) Complex.exp _
      _ ⊆ (norm ∘ f) '' {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃} :=
          Set.image_mono hmapsC.image_subset
    -- Fallback (TC-BB route (a), contract-recorded): drop `Set.image_comp`
    -- entirely and chase upper bounds through the membership — replace the
    -- `refine hbig.mono ?_` and the `calc` by:
    --   obtain ⟨b, hb'⟩ := hbig
    --   refine ⟨b, ?_⟩
    --   rintro x ⟨y, hy, rfl⟩
    --   exact hb' (Set.mem_image_of_mem (norm ∘ f) (hmapsC hy))
    -- The "bound on the strip directly" route is pre-rejected in design
    -- (death condition 7): the strip is unbounded and no pinned lemma bounds
    -- a continuous image of an unbounded set; the annulus transport is forced.
  -- (TC-PERIOD, MEDIUM) boundary bounds upstairs: :607's `ha`/`hb` quantify
  -- over the WHOLE vertical line, which `exp` wraps onto the circle
  -- infinitely-many-to-one (period `2πI`). The discharge runs line → circle,
  -- pointwise: every line point LANDS ON the circle by `norm_exp` + `exp_log`,
  -- so the circle-wide bound applies at every one of the infinitely many
  -- preimages alike. NO section of `exp` is chosen — choosing preimages
  -- (circle → line) is death condition 3.
  have ha : ∀ y ∈ Complex.re ⁻¹' {Real.log r₁}, ‖(f ∘ Complex.exp) y‖ ≤ M₁ := by
    intro y hy
    refine hM₁ _ ?_
    rw [Complex.norm_exp, show y.re = Real.log r₁ from hy, Real.exp_log h₁]
    -- Fallback (TC-PERIOD, contract-recorded), if the `show … from hy` fails
    -- on `Set.mem_singleton_iff` unfolding: first run
    --   simp only [Set.mem_preimage, Set.mem_singleton_iff] at hy
    -- and then `rw [Complex.norm_exp, hy, Real.exp_log h₁]`.
  have hb : ∀ y ∈ Complex.re ⁻¹' {Real.log r₃}, ‖(f ∘ Complex.exp) y‖ ≤ M₃ := by
    intro y hy
    refine hM₃ _ ?_
    rw [Complex.norm_exp, show y.re = Real.log r₃ from hy, Real.exp_log h₃]
    -- Fallback (TC-PERIOD): as `ha` —
    --   simp only [Set.mem_preimage, Set.mem_singleton_iff] at hy
    --   rw [Complex.norm_exp, hy, Real.exp_log h₃]
  -- the pinned three-lines, endpoint form (Hadamard.lean:607; note the PRIME —
  -- the unprimed name does not exist at the pin; hypothesis order hul hz hd hB ha hb)
  have key := Complex.HadamardThreeLines.norm_le_interp_of_mem_verticalClosedStrip'
    hul hw hd' hB ha hb
  -- (TC-EVAL, MEDIUM) rewrite evaluation point and exponent; no log-algebra.
  -- Order matters: `hwexp` fires before `w` disappears from the norm; `hwre`
  -- clears BOTH exponent occurrences of `w.re` (`rw` rewrites all
  -- occurrences). Occurrence audit (contract-recorded): after the first two
  -- rewrites `w` occurs only as `w.re` (twice); the result is literally the
  -- goal. Fallback if `Function.comp_apply` fails syntactically:
  --   simp only [Function.comp_apply] at key
  --   rw [hwexp, hwre] at key
  rw [Function.comp_apply, hwexp, hwre] at key
  exact key

/-! ## Block D — the log-convexity headline and corollaries -/

/-! ### TC9. Hadamard three-circles: log-convexity of the circle sup `[GEN]` `[PIN]`
— the headline

This IS the statement "`log (sSupNormCircle f (Real.exp x))` is convex in `x`"
in inequality form at three points, without mentioning `ConvexOn` — the pin's
own three-lines development makes the same presentational choice
(Hadamard.lean:582-607); no new convexity API is introduced (TC-DEFERRED-2). -/

theorem sSupNormCircle_le_interp {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] {f : ℂ → E} {r₁ r₂ r₃ : ℝ}
    (h₁ : 0 < r₁) (h₁₂ : r₁ ≤ r₂) (h₂₃ : r₂ ≤ r₃) (h₁₃ : r₁ < r₃)
    (hd : DifferentiableOn ℂ f {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃})
    (hc : ContinuousOn f {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}) :
    sSupNormCircle f r₂ ≤
      sSupNormCircle f r₁
        ^ (1 - (Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁))
      * sSupNormCircle f r₃
        ^ ((Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁)) := by
  have h₂ : 0 < r₂ := h₁.trans_le h₁₂
  have h₃ : 0 < r₃ := h₁.trans h₁₃
  -- circles sit inside the closed annulus
  have hsub : ∀ {r : ℝ}, r₁ ≤ r → r ≤ r₃ →
      Metric.sphere (0 : ℂ) r ⊆ {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃} := by
    intro r hr₁ hr₃ w hw
    have hwn := mem_sphere_zero_iff_norm.mp hw
    exact ⟨hwn ▸ hr₁, hwn ▸ hr₃⟩
    -- OBLIG TC-SUP (MEDIUM), hazard (ii): `hwn ▸ hr₁` transports `r₁ ≤ r`
    -- along `‖w‖ = r` backwards. Fallback (contract-recorded), if the `▸`
    -- direction misfires:
    --   exact ⟨hwn.symm ▸ hr₁, hwn.symm ▸ hr₃⟩
    -- or: constructor <;> rw [hwn] <;> assumption
  -- sSup over the middle circle, against a nonneg RHS (junk-safety of the
  -- bare-sSup convention: `Real.sSup_le` demands `0 ≤ a` — TC-SUP hazard).
  refine Real.sSup_le ?_ (mul_nonneg
    (Real.rpow_nonneg (sSupNormCircle_nonneg f r₁) _)
    (Real.rpow_nonneg (sSupNormCircle_nonneg f r₃) _))
  rintro y ⟨z, hz, rfl⟩
  exact norm_le_interp_of_norm_eq h₁ h₁₂ h₂₃ h₁₃ hd hc
    (fun w hw => le_sSupNormCircle (hc.mono (hsub le_rfl h₁₃.le)) hw)
    (fun w hw => le_sSupNormCircle (hc.mono (hsub h₁₃.le le_rfl)) hw)
    (mem_sphere_zero_iff_norm.mp hz)
  -- OBLIG TC-SUP (MEDIUM), hazard (i): after `rintro y ⟨z, hz, rfl⟩` the goal
  -- head is `(norm ∘ f) z ≤ …` (defeq to `‖f z‖ ≤ …`). Fallback
  -- (contract-recorded): prepend
  --   simp only [Function.comp_apply]
  -- before the final `exact`. Hazard (iii) audit: inner circle takes
  -- `hsub le_rfl h₁₃.le`, outer takes `hsub h₁₃.le le_rfl` — as written.

/-! ### TC10. Corollary: classical ratio-exponent form `[GEN]` `[PIN]`

Precisely the `UPSTREAM_POOL.md` §3.1 shape. All the log-algebra of the
package is quarantined here (contract decision 3, TC-ALG). -/

theorem norm_le_interp_of_norm_eq' {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] {f : ℂ → E} {r₁ r₂ r₃ M₁ M₃ : ℝ} {z : ℂ}
    (h₁ : 0 < r₁) (h₁₂ : r₁ ≤ r₂) (h₂₃ : r₂ ≤ r₃) (h₁₃ : r₁ < r₃)
    (hd : DifferentiableOn ℂ f {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃})
    (hc : ContinuousOn f {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃})
    (hM₁ : ∀ w : ℂ, ‖w‖ = r₁ → ‖f w‖ ≤ M₁)
    (hM₃ : ∀ w : ℂ, ‖w‖ = r₃ → ‖f w‖ ≤ M₃)
    (hz : ‖z‖ = r₂) :
    ‖f z‖ ≤ M₁ ^ (Real.log (r₃ / r₂) / Real.log (r₃ / r₁))
          * M₃ ^ (Real.log (r₂ / r₁) / Real.log (r₃ / r₁)) := by
  have h₂ : 0 < r₂ := h₁.trans_le h₁₂
  have h₃ : 0 < r₃ := h₁.trans h₁₃
  have hne : Real.log r₃ - Real.log r₁ ≠ 0 :=
    sub_ne_zero.mpr (Real.log_lt_log h₁ h₁₃).ne'
  have e₂ : Real.log (r₂ / r₁) / Real.log (r₃ / r₁)
      = (Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁) := by
    rw [Real.log_div h₂.ne' h₁.ne', Real.log_div h₃.ne' h₁.ne']
  have e₁ : Real.log (r₃ / r₂) / Real.log (r₃ / r₁)
      = 1 - (Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁) := by
    rw [Real.log_div h₃.ne' h₂.ne', Real.log_div h₃.ne' h₁.ne']
    field_simp
    -- OBLIG TC-ALG (LOW): the identity `(u - m)/(u - l) = 1 - (m - l)/(u - l)`
    -- needs `u - l ≠ 0` (`hne`, in context for `field_simp`). Fallback
    -- (contract-recorded): if `field_simp` leaves a `ring`-shaped residue,
    -- append `ring`:
    --   field_simp
    --   ring
  rw [e₁, e₂]
  exact norm_le_interp_of_norm_eq h₁ h₁₂ h₂₃ h₁₃ hd hc hM₁ hM₃ hz

/-! ### TC11. Corollary: two-boundary maximum principle on the annulus `[GEN]` `[PIN]`

The `M₁ = M₃` degeneration of TC8. `0 ≤ M` is DERIVED, not assumed
(TC-NONNEG): the inner circle is nonempty (`0 < r₁`), so `hM₁` at any witness
dominates a norm — do not "simplify" by adding a redundant `0 ≤ M` hypothesis. -/

theorem norm_le_of_mem_annulus {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] {f : ℂ → E} {r₁ r₃ M : ℝ} {z : ℂ}
    (h₁ : 0 < r₁) (h₁₃ : r₁ < r₃)
    (hd : DifferentiableOn ℂ f {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃})
    (hc : ContinuousOn f {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃})
    (hM₁ : ∀ w : ℂ, ‖w‖ = r₁ → ‖f w‖ ≤ M)
    (hM₃ : ∀ w : ℂ, ‖w‖ = r₃ → ‖f w‖ ≤ M)
    (hz : z ∈ {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}) :
    ‖f z‖ ≤ M := by
  obtain ⟨hz₁, hz₃⟩ := hz
  -- OBLIG TC-RPOW (LOW), friction (i): if `obtain` on `hz` fails
  -- syntactically on the set-builder, prepend
  --   simp only [Set.mem_setOf_eq] at hz
  -- 0 ≤ M, witnessed on the (nonempty) inner circle — this is where
  -- `NormedSpace.sphere_nonempty` earns its keep (TC-NONNEG).
  obtain ⟨w₀, hw₀⟩ := NormedSpace.sphere_nonempty (x := (0 : ℂ)) (r := r₁) |>.mpr h₁.le
  have hM : 0 ≤ M := (norm_nonneg _).trans (hM₁ w₀ (mem_sphere_zero_iff_norm.mp hw₀))
  -- TC8 at the middle radius ‖z‖: h₁₂ := hz₁, h₂₃ := hz₃, hz := rfl
  have key := norm_le_interp_of_norm_eq h₁ hz₁ hz₃ h₁₃ hd hc hM₁ hM₃ rfl
  set t := (Real.log ‖z‖ - Real.log r₁) / (Real.log r₃ - Real.log r₁) with ht
  calc ‖f z‖ ≤ M ^ (1 - t) * M ^ t := key
    _ = M ^ ((1 - t) + t) := (Real.rpow_add' hM (by rw [sub_add_cancel]; norm_num)).symm
    _ = M := by rw [sub_add_cancel, Real.rpow_one]
  -- OBLIG TC-RPOW (LOW), friction (ii): `rpow_add'` (Pow/Real.lean:210) is
  -- stated base-first and applied right-to-left (`.symm`); its side goal
  -- `(1 - t) + t ≠ 0` closes by `sub_add_cancel` (the `@[to_additive
  -- (attr := simp)]` twin of `div_mul_cancel`, Group/Defs.lean:1253) then
  -- `norm_num` on `(1 : ℝ) ≠ 0`. Fallback (contract-recorded): if the `set`
  -- abbreviation blocks the `sub_add_cancel` rewrite inside the side goal,
  -- inline `t` first (`rw [ht]`) or discharge the side goal as `by simp`
  -- (`sub_add_cancel` is `@[simp]` at the pin).
