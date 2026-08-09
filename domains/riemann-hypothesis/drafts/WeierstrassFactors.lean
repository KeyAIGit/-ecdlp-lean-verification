/-
NON-BUILT DRAFT — generic Weierstrass elementary factors and canonical products,
W1–W12.

This file transcribes the stage-one accepted surface in
`domains/riemann-hypothesis/WEIERSTRASS_FACTORS_CONTRACT.md` under RH-019.
It is deliberately outside every Lake target and is not imported by
`ResearchOS.lean`.  Repository CI therefore does not elaborate it, and this
file carries no kernel verdict.  A built promotion, if later authorized, is a
separate task.

The package is generic: it concerns a fixed finite genus and an arbitrary
family in `ℂ`.  It contains no zeta or xi input, supplies no global zero count
or growth theorem, selects no route, and moves no barrier.  In the capstone,
`Nat.card` is only the multiplicity of one finite fibre.

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0).
-/
import Mathlib.Analysis.SpecialFunctions.Complex.LogBounds
import Mathlib.Analysis.Complex.Exponential
import Mathlib.Analysis.SpecialFunctions.Complex.Log
import Mathlib.Analysis.SpecialFunctions.Log.Summable
import Mathlib.Analysis.Normed.Module.MultipliableUniformlyOn
import Mathlib.Topology.Algebra.InfiniteSum.UniformOn
import Mathlib.Analysis.Complex.LocallyUniformLimit
import Mathlib.Analysis.Analytic.Order
import Mathlib.Analysis.Complex.CauchyIntegral

open Complex Filter Function Set
open scoped Topology

/-! ## W1. Elementary factor: definition and evaluation -/

/-- The **Weierstrass elementary factor** of genus `p`:
`E p z = (1 - z) * exp (z + z ^ 2 / 2 + ⋯ + z ^ p / p)`. -/
noncomputable def weierstrassFactor (p : ℕ) (z : ℂ) : ℂ :=
  (1 - z) * Complex.exp (∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1))

@[simp] lemma weierstrassFactor_apply_zero (p : ℕ) : weierstrassFactor p 0 = 1 := by
  simp [weierstrassFactor]

@[simp] lemma weierstrassFactor_genus_zero (z : ℂ) : weierstrassFactor 0 z = 1 - z := by
  simp [weierstrassFactor]

lemma weierstrassFactor_succ (p : ℕ) (z : ℂ) :
    weierstrassFactor (p + 1) z
      = weierstrassFactor p z * Complex.exp (z ^ (p + 1) / (p + 1)) := by
  simp only [weierstrassFactor, Finset.sum_range_succ, Complex.exp_add]
  ring

/-! ## W2. Differentiability and analyticity -/

lemma differentiable_weierstrassFactor (p : ℕ) :
    Differentiable ℂ (weierstrassFactor p) := by
  unfold weierstrassFactor
  fun_prop

lemma analyticAt_weierstrassFactor (p : ℕ) (z : ℂ) :
    AnalyticAt ℂ (weierstrassFactor p) z := by
  exact (Complex.analyticOnNhd_univ_iff_differentiable.mpr
    (differentiable_weierstrassFactor p)) z (Set.mem_univ z)

/-! ## W3. The only zero of an elementary factor -/

@[simp] lemma weierstrassFactor_eq_zero_iff {p : ℕ} {z : ℂ} :
    weierstrassFactor p z = 0 ↔ z = 1 := by
  simp only [weierstrassFactor, mul_eq_zero, Complex.exp_ne_zero, or_false]
  rw [sub_eq_zero, eq_comm]

lemma weierstrassFactor_ne_zero {p : ℕ} {z : ℂ} (hz : z ≠ 1) :
    weierstrassFactor p z ≠ 0 := by
  exact fun h => hz (weierstrassFactor_eq_zero_iff.mp h)

/-! ## W4. Algebraic bridge to the pinned logarithmic Taylor polynomial -/

/-- `logTaylor (p+1)` at `-z` is minus the exponent sum of `weierstrassFactor p`.
Pure algebra; this is the whole seam between W6 and the pinned log bound. -/
lemma logTaylor_neg_eq (p : ℕ) (z : ℂ) :
    Complex.logTaylor (p + 1) (-z) = -∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1) := by
  simp only [Complex.logTaylor, Finset.sum_range_succ']
  simp only [pow_one, Nat.cast_zero, div_zero, zero_add, add_zero]
  rw [← Finset.sum_neg_distrib]
  apply Finset.sum_congr rfl
  intro k hk
  have hsign :
      (-1 : ℂ) ^ (k + 2) * (-z) ^ (k + 1) = -z ^ (k + 1) := by
    calc
      (-1 : ℂ) ^ (k + 2) * (-z) ^ (k + 1)
          = ((-1 : ℂ) ^ k * (-z) ^ k) * (-z) := by
              rw [show k + 2 = (k + 1) + 1 by omega, pow_succ, pow_succ,
                pow_succ]
              ring
      _ = z ^ k * (-z) := by
            rw [← mul_pow]
            ring
      _ = -z ^ (k + 1) := by rw [pow_succ]; ring
  rw [hsign]
  push_cast
  ring

/-- Branch-free exponential form: avoids `log_mul` and all argument bookkeeping. -/
lemma weierstrassFactor_eq_exp {p : ℕ} {z : ℂ} (hz : z ≠ 1) :
    weierstrassFactor p z
      = Complex.exp (Complex.log (1 - z) + ∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1)) := by
  rw [Complex.exp_add, Complex.exp_log (sub_ne_zero.mpr (Ne.symm hz))]
  rfl

/-! ## W5. Consumption of the pinned logarithmic estimate -/

/-- The pinned estimate `LogBounds.lean:231`, restated on the exponent sum of
`weierstrassFactor`. Everything here except the statement shape is already a
result at the pin. -/
theorem norm_log_one_sub_add_sum_le (p : ℕ) {z : ℂ} (hz : ‖z‖ < 1) :
    ‖Complex.log (1 - z) + ∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1)‖
      ≤ ‖z‖ ^ (p + 1) * (1 - ‖z‖)⁻¹ / (p + 1) := by
  have h := Complex.norm_log_one_sub_inv_add_logTaylor_neg_le p hz
  have hsp : (1 : ℂ) - z ∈ Complex.slitPlane := by
    rw [sub_eq_add_neg]
    exact Complex.mem_slitPlane_of_norm_lt_one (by rwa [norm_neg])
  rw [Complex.log_inv _ (Complex.slitPlane_arg_ne_pi hsp), logTaylor_neg_eq] at h
  have heq :
      -Complex.log (1 - z) + -∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1) =
        -(Complex.log (1 - z) + ∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1)) := by
    ring
  rw [heq, norm_neg] at h
  exact h

/-! ## W6. A uniform elementary-factor estimate on the half-disc -/

/-- The sole input to the convergence criterion: `‖E p z - 1‖ ≤ 4/(p+1) · ‖z‖^(p+1)`
on `‖z‖ ≤ 1/2`. Deliberately NOT the sharp Rudin 15.8 bound on the closed unit
disc (see DEFERRED-W3). -/
theorem norm_weierstrassFactor_sub_one_le {p : ℕ} {z : ℂ} (hz : ‖z‖ ≤ 1 / 2) :
    ‖weierstrassFactor p z - 1‖ ≤ 4 / (p + 1) * ‖z‖ ^ (p + 1) := by
  let L : ℂ :=
    Complex.log (1 - z) + ∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1)
  have hzlt : ‖z‖ < 1 := lt_of_le_of_lt hz (by norm_num)
  have hzne : z ≠ 1 := by
    intro h
    subst z
    norm_num at hz
  have hform : weierstrassFactor p z = Complex.exp L := by
    exact weierstrassFactor_eq_exp hzne
  have hL : ‖L‖ ≤ ‖z‖ ^ (p + 1) * (1 - ‖z‖)⁻¹ / (p + 1) :=
    norm_log_one_sub_add_sum_le p hzlt
  have hinv : (1 - ‖z‖)⁻¹ ≤ (2 : ℝ) := by
    rw [inv_eq_one_div, div_le_iff₀]
    · linarith
    · linarith [norm_nonneg z]
  -- Pre-combine the logarithmic estimate and the inverse bound.  In particular,
  -- do not ask one congruence step to invent this transitivity.
  have hL2 : ‖L‖ ≤ ‖z‖ ^ (p + 1) * 2 / (p + 1) := by
    refine hL.trans ?_
    exact div_le_div_of_nonneg_right
      (mul_le_mul_of_nonneg_left hinv (pow_nonneg (norm_nonneg z) _)) (by positivity)
  have hzleone : ‖z‖ ≤ 1 := hz.trans (by norm_num)
  have hpow : ‖z‖ ^ (p + 1) ≤ ‖z‖ :=
    pow_le_of_le_one (norm_nonneg z) hzleone (by omega)
  have hpone : (1 : ℝ) ≤ p + 1 := by norm_num
  have hmajor : ‖z‖ ^ (p + 1) * 2 / (p + 1) ≤ 1 := by
    rw [div_le_iff₀ (by positivity : (0 : ℝ) < p + 1)]
    nlinarith
  have hL1 : ‖L‖ ≤ 1 := hL2.trans hmajor
  calc
    ‖weierstrassFactor p z - 1‖ = ‖Complex.exp L - 1‖ := by rw [hform]
    _ ≤ 2 * ‖L‖ := Complex.norm_exp_sub_one_le hL1
    _ ≤ 2 * (‖z‖ ^ (p + 1) * 2 / (p + 1)) :=
      mul_le_mul_of_nonneg_left hL2 (by norm_num)
    _ = 4 / (p + 1) * ‖z‖ ^ (p + 1) := by ring

/-! ## W7–W11. The canonical product -/

section CanonicalProduct

variable {ι : Type*} {p : ℕ} {a : ι → ℂ}

/-- The **Weierstrass canonical product** of genus `p` over the zero family `a`. -/
noncomputable def weierstrassProduct (p : ℕ) (a : ι → ℂ) (z : ℂ) : ℂ :=
  ∏' i, weierstrassFactor p (z / a i)

/-- The zero family escapes every ball, cofinitely. Derived from `hsum`, not assumed. -/
lemma eventually_cofinite_le_norm (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (R : ℝ) :
    ∀ᶠ i in Filter.cofinite, R ≤ ‖a i‖ := by
  let B : ℝ := max R 1
  have hBpos : 0 < B := by
    exact zero_lt_one.trans_le (by dsimp [B]; exact le_max_right R 1)
  have heps : 0 < B⁻¹ ^ (p + 1) := pow_pos (inv_pos.mpr hBpos) _
  have hsmall :
      ∀ᶠ i in Filter.cofinite, ‖a i‖⁻¹ ^ (p + 1) < B⁻¹ ^ (p + 1) :=
    (tendsto_order.1 hsum.tendsto_cofinite_zero).2 _ heps
  filter_upwards [hsmall] with i hi
  by_contra hRi
  have haiPos : 0 < ‖a i‖ := norm_pos_iff.mpr (hane i)
  have haiB : ‖a i‖ < B :=
    (lt_of_not_ge hRi).trans_le (by dsimp [B]; exact le_max_left R 1)
  have hinv : B⁻¹ < ‖a i‖⁻¹ := (inv_lt_inv₀ hBpos haiPos).2 haiB
  have hpow : B⁻¹ ^ (p + 1) < ‖a i‖⁻¹ ^ (p + 1) :=
    (pow_lt_pow_iff_left₀ (inv_nonneg.mpr hBpos.le) (inv_nonneg.mpr haiPos.le)
      (by omega)).2 hinv
  exact (not_lt_of_ge hpow.le) hi

/-- Every fiber of the zero family is finite. -/
lemma finite_setOf_apply_eq (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (w : ℂ) :
    {i | a i = w}.Finite := by
  have hlarge := eventually_cofinite_le_norm hane hsum (‖w‖ + 1)
  have hfinite : {i | ¬ (‖w‖ + 1 ≤ ‖a i‖)}.Finite :=
    Filter.eventually_cofinite.mp hlarge
  refine hfinite.subset ?_
  intro i hi
  simp only [Set.mem_setOf_eq] at hi ⊢
  intro hcontra
  rw [hi] at hcontra
  linarith

/-! ## W8. Absolute and locally uniform convergence on the whole plane -/

/-- Pointwise absolute convergence of the factor tails, every `z`. -/
lemma summable_norm_weierstrassFactor_sub_one (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (z : ℂ) :
    Summable fun i ↦ ‖weierstrassFactor p (z / a i) - 1‖ := by
  let C : ℝ := 4 / (p + 1) * ‖z‖ ^ (p + 1)
  have hmaj : Summable fun i => C * ‖a i‖⁻¹ ^ (p + 1) := hsum.mul_left C
  refine Summable.of_norm_bounded_eventually hmaj ?_
  filter_upwards [eventually_cofinite_le_norm hane hsum (2 * ‖z‖ + 1)] with i hi
  have haiPos : 0 < ‖a i‖ := norm_pos_iff.mpr (hane i)
  have hhalf : ‖z / a i‖ ≤ (1 : ℝ) / 2 := by
    rw [norm_div, div_le_iff₀ haiPos]
    nlinarith [norm_nonneg z]
  have hnormalize :
      ‖z / a i‖ ^ (p + 1) = ‖z‖ ^ (p + 1) * ‖a i‖⁻¹ ^ (p + 1) := by
    rw [norm_div, div_pow, div_eq_mul_inv, ← inv_pow]
  calc
    ‖‖weierstrassFactor p (z / a i) - 1‖‖
        = ‖weierstrassFactor p (z / a i) - 1‖ := by simp
    _ ≤ 4 / (p + 1) * ‖z / a i‖ ^ (p + 1) :=
      norm_weierstrassFactor_sub_one_le hhalf
    _ = C * ‖a i‖⁻¹ ^ (p + 1) := by
      rw [hnormalize]
      dsimp [C]
      ring

/-- The canonical product converges locally uniformly on the whole plane —
`Set.univ`, not a zero-avoiding subdomain (contrast the Euler sine development). -/
theorem hasProdLocallyUniformlyOn_weierstrassProduct (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) :
    HasProdLocallyUniformlyOn (fun i z ↦ weierstrassFactor p (z / a i))
      (weierstrassProduct p a) Set.univ := by
  refine hasProdLocallyUniformlyOn_of_forall_compact isOpen_univ ?_
  intro K hKuniv hK
  obtain ⟨r, hKr⟩ := hK.isBounded.subset_closedBall (0 : ℂ)
  let R : ℝ := max r 0
  have hR0 : 0 ≤ R := by dsimp [R]; exact le_max_right r 0
  have hKR : K ⊆ Metric.closedBall 0 R := by
    intro x hx
    exact Metric.mem_closedBall.mpr
      ((Metric.mem_closedBall.mp (hKr hx)).trans (by dsimp [R]; exact le_max_left r 0))
  let u : ι → ℝ := fun i => 4 / (p + 1) * (R ^ (p + 1) / ‖a i‖ ^ (p + 1))
  have hu : Summable u := by
    have hRscaled : Summable fun i => R ^ (p + 1) * ‖a i‖⁻¹ ^ (p + 1) :=
      hsum.mul_left (R ^ (p + 1))
    have hscaled :
        Summable fun i => 4 / (p + 1) * (R ^ (p + 1) * ‖a i‖⁻¹ ^ (p + 1)) :=
      hRscaled.mul_left ((4 : ℝ) / (p + 1))
    simpa only [u, div_eq_mul_inv, ← inv_pow, mul_assoc] using hscaled
  have htail :
      ∀ᶠ i in Filter.cofinite, ∀ x ∈ K,
        ‖weierstrassFactor p (x / a i) - 1‖ ≤ u i := by
    filter_upwards [eventually_cofinite_le_norm hane hsum (2 * R + 1)] with i hi
    intro x hx
    have haiPos : 0 < ‖a i‖ := norm_pos_iff.mpr (hane i)
    -- This named step is required before the normalized comparison below.
    have hxR : ‖x‖ ≤ R := by
      simpa [dist_eq_norm] using (Metric.mem_closedBall.mp (hKR hx))
    have hhalf : ‖x / a i‖ ≤ (1 : ℝ) / 2 := by
      rw [norm_div, div_le_iff₀ haiPos]
      nlinarith
    have hpow :
        ‖x / a i‖ ^ (p + 1) ≤ R ^ (p + 1) / ‖a i‖ ^ (p + 1) := by
      rw [norm_div, div_pow]
      exact div_le_div_of_nonneg_right
        ((pow_le_pow_iff_left₀ (norm_nonneg x) hR0 (by omega)).2 hxR) (by positivity)
    calc
      ‖weierstrassFactor p (x / a i) - 1‖
          ≤ 4 / (p + 1) * ‖x / a i‖ ^ (p + 1) :=
            norm_weierstrassFactor_sub_one_le hhalf
      _ ≤ 4 / (p + 1) * (R ^ (p + 1) / ‖a i‖ ^ (p + 1)) :=
        mul_le_mul_of_nonneg_left hpow (by positivity)
      _ = u i := rfl
  have hraw :
      HasProdUniformlyOn
        (fun i x => 1 + (weierstrassFactor p (x / a i) - 1))
        (fun x => ∏' i, (1 + (weierstrassFactor p (x / a i) - 1))) K := by
    apply hu.hasProdUniformlyOn_one_add hK htail
    intro i
    have hc : Continuous (fun x : ℂ => weierstrassFactor p (x / a i)) := by
      simpa only [Function.comp_def] using
        (differentiable_weierstrassFactor p).continuous.comp
          (by fun_prop : Continuous fun x : ℂ => x / a i)
    exact (hc.sub continuous_const).continuousOn
  have hfamily :
      ∀ᶠ s : Finset ι in atTop,
        K.EqOn
          (fun x => s.prod fun i => 1 + (weierstrassFactor p (x / a i) - 1))
          (fun x => s.prod fun i => weierstrassFactor p (x / a i)) := by
    filter_upwards with s
    intro x hx
    simp
  have hconverted :
      HasProdUniformlyOn (fun i x => weierstrassFactor p (x / a i))
        (fun x => ∏' i, (1 + (weierstrassFactor p (x / a i) - 1))) K :=
    hraw.congr hfamily
  refine hconverted.congr_right ?_
  intro x hx
  unfold weierstrassProduct
  exact tprod_congr fun i => by simp

/-! ## W9. The locally uniform limit is entire -/

theorem differentiable_weierstrassProduct (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) :
    Differentiable ℂ (weierstrassProduct p a) := by
  have h := hasProdLocallyUniformlyOn_weierstrassProduct hane hsum
  have hd : DifferentiableOn ℂ (weierstrassProduct p a) Set.univ :=
    h.differentiableOn
      (.of_forall fun s => by
        simpa [Finset.prod_fn] using
          DifferentiableOn.finsetProd
            (fun i _ => ((differentiable_weierstrassFactor p).comp
              (by fun_prop)).differentiableOn))
      isOpen_univ
  exact differentiableOn_univ.mp hd

lemma analyticAt_weierstrassProduct (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (z : ℂ) :
    AnalyticAt ℂ (weierstrassProduct p a) z := by
  exact (Complex.analyticOnNhd_univ_iff_differentiable.mpr
    (differentiable_weierstrassProduct hane hsum)) z (Set.mem_univ z)

/-! ## W10. Pointwise complement split and the analytic nonzero tail -/

/-- Pointwise-global complement split of the product: for ANY index set `S` and
EVERY `z`. This is the re-derived replacement for the pool's missing
`HasProdLocallyUniformlyOn.mul_compl` (§1.4): no uniform content is needed for a
function identity. -/
theorem weierstrassProduct_eq_tprod_mul_tprod_compl (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (S : Set ι) (z : ℂ) :
    weierstrassProduct p a z
      = (∏' i : S, weierstrassFactor p (z / a i))
          * ∏' i : ↥Sᶜ, weierstrassFactor p (z / a i) := by
  have hnorm := summable_norm_weierstrassFactor_sub_one hane hsum z
  have hS : Multipliable
      ((fun i => weierstrassFactor p (z / a i)) ∘ ((↑) : S → ι)) := by
    refine Multipliable.congr
      (g := (fun i => weierstrassFactor p (z / a i)) ∘ ((↑) : S → ι))
      (multipliable_one_add_of_summable (hnorm.subtype (· ∈ S))) ?_
    intro i
    simp only [Function.comp_apply, ← add_sub_assoc, add_sub_cancel_left]
  have hSc : Multipliable
      ((fun i => weierstrassFactor p (z / a i)) ∘ ((↑) : ↥Sᶜ → ι)) := by
    refine Multipliable.congr
      (g := (fun i => weierstrassFactor p (z / a i)) ∘ ((↑) : ↥Sᶜ → ι))
      (multipliable_one_add_of_summable (hnorm.subtype (· ∈ Sᶜ))) ?_
    intro i
    simp only [Function.comp_apply, ← add_sub_assoc, add_sub_cancel_left]
  unfold weierstrassProduct
  exact (Multipliable.tprod_mul_tprod_compl
    (f := fun i => weierstrassFactor p (z / a i)) (s := S) hS hSc).symm

/-- The complement tail is an entire function of `z` — a subfamily instantiation
of W9, not a new convergence argument. -/
lemma analyticAt_tprod_compl (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (S : Set ι) (z : ℂ) :
    AnalyticAt ℂ (fun w ↦ ∏' i : ↥Sᶜ, weierstrassFactor p (w / a i)) z := by
  have hane' : ∀ i : ↥Sᶜ, a i ≠ 0 := fun i => hane i
  have hsum' : Summable fun i : ↥Sᶜ => ‖a i‖⁻¹ ^ (p + 1) :=
    hsum.subtype (· ∈ Sᶜ)
  change AnalyticAt ℂ (weierstrassProduct p (fun i : ↥Sᶜ => a i)) z
  exact analyticAt_weierstrassProduct hane' hsum' z

/-- If no zero sits at `w`, the whole product is nonzero at `w`. Applied to the
complement of the fiber, this is the tail-nonvanishing input to W12. -/
lemma weierstrassProduct_ne_zero_of_forall_ne (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) {w : ℂ} (h : ∀ i, a i ≠ w) :
    weierstrassProduct p a w ≠ 0 := by
  have hnorm := summable_norm_weierstrassFactor_sub_one hane hsum w
  have hfac : ∀ i, 1 + (weierstrassFactor p (w / a i) - 1) ≠ 0 := by
    intro i
    rw [← add_sub_assoc, add_sub_cancel_left]
    apply weierstrassFactor_ne_zero
    intro hi
    have hwa : w = a i := (div_eq_one_iff_eq (hane i)).mp hi
    exact h i hwa.symm
  have ht := tprod_one_add_ne_zero_of_summable hfac hnorm
  simpa only [weierstrassProduct, ← add_sub_assoc, add_sub_cancel_left] using ht

/-! ## W11. Exact zero set -/

/-- The zero set of the canonical product is exactly the zero family — on all
of ℂ. This is the statement the Euler sine development structurally avoids by
working on the complement of its zeros. -/
theorem weierstrassProduct_eq_zero_iff (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) {z : ℂ} :
    weierstrassProduct p a z = 0 ↔ ∃ i, a i = z := by
  classical
  constructor
  · intro hz
    by_contra hnone
    push Not at hnone
    exact (weierstrassProduct_ne_zero_of_forall_ne hane hsum hnone) hz
  · rintro ⟨i, rfl⟩
    rw [weierstrassProduct_eq_tprod_mul_tprod_compl hane hsum ({i} : Set ι) (a i)]
    have hhead :
        (∏' j : ({i} : Set ι), weierstrassFactor p (a i / a j)) = 0 := by
      rw [tprod_fintype]
      let j : ({i} : Set ι) := ⟨i, by simp⟩
      apply Finset.prod_eq_zero (Finset.mem_univ j)
      apply weierstrassFactor_eq_zero_iff.mpr
      simpa [j] using div_self (hane i)
    rw [hhead, zero_mul]

end CanonicalProduct

/-! ## W12. Local analytic order -/

/-- The elementary factor has a SIMPLE zero at `1`. -/
lemma analyticOrderAt_weierstrassFactor_one (p : ℕ) :
    analyticOrderAt (weierstrassFactor p) 1 = 1 := by
  let g : ℂ → ℂ := fun z =>
    Complex.exp (∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1))
  have hf : AnalyticAt ℂ (fun z : ℂ => 1 - z) 1 := by fun_prop
  have hg : AnalyticAt ℂ g 1 := by
    dsimp [g]
    fun_prop
  have hleft : analyticOrderAt (fun z : ℂ => 1 - z) 1 = 1 := by
    apply hf.analyticOrderAt_eq_one_of_zero_deriv_ne_zero
    · simp
    · rw [deriv_const_sub_id]
      norm_num
  have hright : analyticOrderAt g 1 = 0 := by
    apply hg.analyticOrderAt_eq_zero.mpr
    exact Complex.exp_ne_zero _
  rw [show weierstrassFactor p = (fun z : ℂ => 1 - z) * g by rfl,
    analyticOrderAt_mul hf hg, hleft, hright]
  simp

/-- Transported along `z ↦ z / c`: the factor `E_p(· / c)` has a simple zero at `c`. -/
lemma analyticOrderAt_weierstrassFactor_div {p : ℕ} {c : ℂ} (hc : c ≠ 0) :
    analyticOrderAt (fun z ↦ weierstrassFactor p (z / c)) c = 1 := by
  have hg : AnalyticAt ℂ (fun z : ℂ => z / c) c := by fun_prop
  have hg' : deriv (fun z : ℂ => z / c) c ≠ 0 := by
    rw [deriv_div_const]
    simp [hc]
  have hcomp := analyticOrderAt_comp_of_deriv_ne_zero
    (f := weierstrassFactor p) hg hg'
  simpa [Function.comp_def, div_self hc, analyticOrderAt_weierstrassFactor_one p] using hcomp

section FiniteProductOrder

/-- `[GEN]` Order is additive over finite products of analytic functions. Absent at
the pin AS A NAME in the analytic carrier (only the binary `analyticOrderAt_mul`,
Order.lean:497, exists there); a routine `Finset.cons_induction`. NOTE (Annex B
item 1): the MEROMORPHIC twin `meromorphicOrderAt_prod` IS pinned
(Meromorphic/Order.lean:437, with `meromorphicOrderAt_fun_prod` at :456 already
handling the `Finset.prod_apply` seam), and the carrier bridge
`AnalyticAt.meromorphicOrderAt_eq` (:279) transfers it — so this lemma is
derivable by transfer instead of fresh induction. Natural Mathlib upstream
either way. -/
lemma analyticOrderAt_finsetProd {ι : Type*} (s : Finset ι) {f : ι → ℂ → ℂ} {z₀ : ℂ}
    (hf : ∀ i ∈ s, AnalyticAt ℂ (f i) z₀) :
    analyticOrderAt (∏ i ∈ s, f i) z₀ = ∑ i ∈ s, analyticOrderAt (f i) z₀ := by
  classical
  revert hf
  refine Finset.induction_on s ?_ ?_
  · intro hf
    have hone : AnalyticAt ℂ (1 : ℂ → ℂ) z₀ := analyticAt_const
    simpa using hone.analyticOrderAt_eq_zero.mpr (one_ne_zero : (1 : ℂ) ≠ 0)
  · intro i s his ih hf
    have hfi : AnalyticAt ℂ (f i) z₀ := hf i (Finset.mem_insert_self i s)
    have hfs : ∀ j ∈ s, AnalyticAt ℂ (f j) z₀ :=
      fun j hj => hf j (Finset.mem_insert_of_mem hj)
    rw [Finset.prod_insert his, Finset.sum_insert his,
      analyticOrderAt_mul hfi (Finset.analyticAt_prod s hfs), ih hfs]

end FiniteProductOrder

section CanonicalProductOrder

variable {ι : Type*} {p : ℕ} {a : ι → ℂ}

/-- **Zero set with multiplicity, at every point of ℂ.** The local analytic order
of the canonical product at `w` is the number of indices sitting at `w`. This is
the statement whose absence the Euler sine development routes around; it is
stated with NO domain restriction and NO nontriviality side condition. -/
theorem analyticOrderAt_weierstrassProduct (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (w : ℂ) :
    analyticOrderAt (weierstrassProduct p a) w = (Nat.card {i | a i = w} : ℕ∞) := by
  classical
  let S : Set ι := {i | a i = w}
  have hS : S.Finite := by
    simpa only [S] using finite_setOf_apply_eq hane hsum w
  letI := hS.fintype
  let f : S → ℂ → ℂ := fun i z => weierstrassFactor p (z / a i)
  let F : ℂ → ℂ := ∏ i : S, f i
  let T : ℂ → ℂ := fun z => ∏' i : ↥Sᶜ, weierstrassFactor p (z / a i)
  have hsplit : weierstrassProduct p a = F * T := by
    funext z
    rw [weierstrassProduct_eq_tprod_mul_tprod_compl hane hsum S z, tprod_fintype]
    simp only [F, f, T, Finset.prod_apply, Pi.mul_apply]
  have hfactorAnalytic : ∀ i : S, AnalyticAt ℂ (f i) w := by
    intro i
    dsimp [f]
    have hdiv : AnalyticAt ℂ (fun z : ℂ => z / a i) w := by
      simpa only [id_eq] using
        (analyticAt_id (𝕜 := ℂ) (z := w)).div_const (c := a i)
    simpa only [Function.comp_def] using
      AnalyticAt.comp (f := fun z : ℂ => z / a i) (x := w)
        (analyticAt_weierstrassFactor p (w / a i)) hdiv
  have hFa : AnalyticAt ℂ F w := by
    dsimp [F]
    exact Finset.analyticAt_prod Finset.univ
      (fun i hi => hfactorAnalytic i)
  have hTa : AnalyticAt ℂ T w := by
    dsimp [T]
    exact analyticAt_tprod_compl hane hsum S w
  have hfactorOrder : ∀ i : S, analyticOrderAt (f i) w = 1 := by
    intro i
    have hiw : a i = w := by simpa only [S, Set.mem_setOf_eq] using i.property
    dsimp [f]
    simpa only [hiw] using
      (analyticOrderAt_weierstrassFactor_div (p := p) (c := a i) (hane i))
  have hFord : analyticOrderAt F w = (Nat.card S : ℕ∞) := by
    calc
      analyticOrderAt F w
          = ∑ i : S, analyticOrderAt (f i) w := by
              simpa only [F] using
                (analyticOrderAt_finsetProd (Finset.univ : Finset S)
                  (fun i hi => hfactorAnalytic i))
      _ = ∑ i : S, (1 : ℕ∞) := by
            apply Finset.sum_congr rfl
            intro i hi
            exact hfactorOrder i
      _ = (Nat.card S : ℕ∞) := by
            simp [Set.fintypeCard_eq_ncard]
  have hane' : ∀ i : ↥Sᶜ, a i ≠ 0 := fun i => hane i
  have hsum' : Summable fun i : ↥Sᶜ => ‖a i‖⁻¹ ^ (p + 1) :=
    hsum.subtype (· ∈ Sᶜ)
  have htailAvoids : ∀ i : ↥Sᶜ, a i ≠ w := by
    intro i hi
    exact i.property (by simpa only [S, Set.mem_setOf_eq] using hi)
  have hTne : T w ≠ 0 := by
    have ht := weierstrassProduct_ne_zero_of_forall_ne
      (p := p) (a := fun i : ↥Sᶜ => a i) hane' hsum' htailAvoids
    simpa only [T, weierstrassProduct] using ht
  have hTord : analyticOrderAt T w = 0 :=
    hTa.analyticOrderAt_eq_zero.mpr hTne
  calc
    analyticOrderAt (weierstrassProduct p a) w
        = analyticOrderAt (F * T) w := by rw [hsplit]
    _ = analyticOrderAt F w + analyticOrderAt T w := analyticOrderAt_mul hFa hTa
    _ = (Nat.card S : ℕ∞) + 0 := by rw [hFord, hTord]
    _ = (Nat.card {i | a i = w} : ℕ∞) := by simp [S]

/-- Non-degeneracy, explicit: the product is nowhere locally identically zero.
Makes the `⊤`-case impossibility a named fact instead of `untop₀` junk. -/
lemma analyticOrderAt_weierstrassProduct_ne_top (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (w : ℂ) :
    analyticOrderAt (weierstrassProduct p a) w ≠ ⊤ := by
  rw [analyticOrderAt_weierstrassProduct hane hsum w]
  simp

end CanonicalProductOrder
