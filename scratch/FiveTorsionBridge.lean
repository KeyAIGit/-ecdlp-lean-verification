import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.TwoTorsionPoint
import Ecdlp.Proved.ThreeTorsionBridge

/-!
# Division-polynomial 5-torsion bridge for secp256k1 (scratch / server verification)

Stage-1 reduction `secp256k1_psi5_evalEval` and the point-level `n = 5` equivalence
`5•P = 0 ↔ ψ 5 vanishes at P`.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- Concrete evaluation of the univariate `preΨ₄` for secp256k1:
`preΨ₄(x) = 2x⁶ + 280x³ − 784`. -/
theorem secp256k1_preΨ₄_eval (x : ZMod Secp256k1.p) :
    secp256k1.preΨ₄.eval x = 2 * x ^ 6 + 280 * x ^ 3 - 784 := by
  rw [WeierstrassCurve.preΨ₄, secp256k1_b₂, secp256k1_b₄, secp256k1_b₆, secp256k1_b₈]
  simp only [eval_add, eval_mul, eval_pow, eval_X, eval_C, eval_ofNat]
  ring

/-- Concrete evaluation of `Ψ₃` for secp256k1: `Ψ₃(x) = 3x⁴ + 84x`. -/
theorem secp256k1_Ψ₃_eval (x : ZMod Secp256k1.p) :
    secp256k1.Ψ₃.eval x = 3 * x ^ 4 + 84 * x := by
  rw [secp256k1_Ψ₃]
  simp only [eval_add, eval_mul, eval_pow, eval_X, eval_C, eval_ofNat]
  ring

/-- The bivariate 2-division polynomial `ψ₂` evaluated at `(x,y)` on secp256k1 is `2y`. -/
theorem secp256k1_psi2_evalEval (x y : ZMod Secp256k1.p) :
    secp256k1.ψ₂.evalEval x y = 2 * y := by
  rw [WeierstrassCurve.ψ₂, evalEval_polynomialY]
  simp [secp256k1]

/-- **Stage-1: `ψ 5` at a point `(x,y)` of secp256k1 reduces to the concrete degree-12
univariate polynomial** `5x¹² + 2660x⁹ − 11760x⁶ − 548800x³ − 614656`. -/
theorem secp256k1_psi5_evalEval (x y : ZMod Secp256k1.p) (hcurve : y ^ 2 = x ^ 3 + 7) :
    (secp256k1.ψ 5).evalEval x y
      = 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656 := by
  have h5 := secp256k1.ψ_odd 2
  rw [show (2 * 2 + 1 : ℤ) = 5 by ring, show (2 + 2 : ℤ) = 4 by ring,
      show (2 - 1 : ℤ) = 1 by ring, show (2 + 1 : ℤ) = 3 by ring,
      secp256k1.ψ_four, secp256k1.ψ_two, secp256k1.ψ_one, secp256k1.ψ_three] at h5
  rw [h5]
  simp only [evalEval_sub, evalEval_mul, evalEval_pow, evalEval_C, evalEval_one]
  rw [secp256k1_psi2_evalEval, secp256k1_preΨ₄_eval, secp256k1_Ψ₃_eval]
  linear_combination (16 * (2 * x ^ 6 + 280 * x ^ 3 - 784) * (y ^ 2 + x ^ 3 + 7)) * hcurve

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Core algebraic identity for the 5-torsion bridge.** With `ℓ₂` the tangent slope at `P`
(so `2yℓ₂ = 3x²`) and `ℓ₃` the secant slope between `2P` and `P`, the `x`-coordinate of `3P`
equals that of `2P` iff `ψ₅(x) = 0`. Pure field algebra, machine-certified by a
`linear_combination` of the curve equation and the slope relation. -/
theorem five_core (x y ℓ₂ ℓ₃ : ZMod Secp256k1.p)
    (h64 : (64 : ZMod Secp256k1.p) ≠ 0)
    (hcurve : y ^ 2 = x ^ 3 + 7)
    (hy : y ≠ 0)
    (hℓ2 : 2 * y * ℓ₂ = 3 * x ^ 2)
    (hd : ℓ₂ ^ 2 - 3 * x ≠ 0)
    (hℓ3 : (ℓ₂ ^ 2 - 3 * x) * ℓ₃ = -(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y) :
    ℓ₃ ^ 2 - (ℓ₂ ^ 2 - 2 * x) - x = ℓ₂ ^ 2 - 2 * x
      ↔ 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656 = 0 := by
  have hd2 : (ℓ₂ ^ 2 - 3 * x) ^ 2 ≠ 0 := pow_ne_zero 2 hd
  have h64y6 : (64 : ZMod Secp256k1.p) * y ^ 6 ≠ 0 := mul_ne_zero h64 (pow_ne_zero 6 hy)
  have hmaster : ((-(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y) ^ 2
        - (2 * (ℓ₂ ^ 2 - 2 * x) + x) * (ℓ₂ ^ 2 - 3 * x) ^ 2) * (64 * y ^ 6)
      = -(5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656) := by
    linear_combination
      (-32 * ℓ₂ ^ 5 * y ^ 5 - 48 * ℓ₂ ^ 4 * x ^ 2 * y ^ 4 - 72 * ℓ₂ ^ 3 * x ^ 4 * y ^ 3
        + 288 * ℓ₂ ^ 3 * x * y ^ 5 - 108 * ℓ₂ ^ 2 * x ^ 6 * y ^ 2 + 432 * ℓ₂ ^ 2 * x ^ 3 * y ^ 4
        + 128 * ℓ₂ ^ 2 * y ^ 6 - 162 * ℓ₂ * x ^ 8 * y + 648 * ℓ₂ * x ^ 5 * y ^ 3
        - 672 * ℓ₂ * x ^ 2 * y ^ 5 - 243 * x ^ 10 + 972 * x ^ 7 * y ^ 2 - 1008 * x ^ 4 * y ^ 4
        - 384 * x * y ^ 6) * hℓ2
      + (724 * x ^ 9 - 2192 * x ^ 6 * y ^ 2 - 7728 * x ^ 6 + 832 * x ^ 3 * y ^ 4
        + 7616 * x ^ 3 * y ^ 2 + 65856 * x ^ 3 + 256 * y ^ 6 + 1792 * y ^ 4 + 12544 * y ^ 2
        + 87808) * hcurve
  have hBF : (ℓ₃ ^ 2 - (2 * (ℓ₂ ^ 2 - 2 * x) + x)) * (ℓ₂ ^ 2 - 3 * x) ^ 2
      = (-(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y) ^ 2
        - (2 * (ℓ₂ ^ 2 - 2 * x) + x) * (ℓ₂ ^ 2 - 3 * x) ^ 2 := by
    linear_combination
      ((ℓ₂ ^ 2 - 3 * x) * ℓ₃ + (-(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y)) * hℓ3
  set F := (-(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y) ^ 2
      - (2 * (ℓ₂ ^ 2 - 2 * x) + x) * (ℓ₂ ^ 2 - 3 * x) ^ 2 with hFdef
  rw [show (ℓ₃ ^ 2 - (ℓ₂ ^ 2 - 2 * x) - x = ℓ₂ ^ 2 - 2 * x)
        ↔ (ℓ₃ ^ 2 - (2 * (ℓ₂ ^ 2 - 2 * x) + x) = 0)
      from by constructor <;> intro h <;> linear_combination h]
  constructor
  · intro hB
    have hFz : F = 0 := by rw [← hBF, hB, zero_mul]
    have := hmaster
    rw [hFz, zero_mul] at this
    linear_combination -this
  · intro hp
    have hFz : F = 0 := by
      have := hmaster
      rw [hp, neg_zero] at this
      exact (mul_eq_zero.mp this).resolve_right h64y6
    have hBz : (ℓ₃ ^ 2 - (2 * (ℓ₂ ^ 2 - 2 * x) + x)) * (ℓ₂ ^ 2 - 3 * x) ^ 2 = 0 := by
      rw [hBF, hFz]
    exact (mul_eq_zero.mp hBz).resolve_right hd2

/-- Helper: a small natural-number constant is nonzero in `𝔽_p`. -/
private theorem const_ne (n : ℕ) (hn : ¬ Secp256k1.p ∣ n) : (n : ZMod Secp256k1.p) ≠ 0 := by
  rw [Ne, ZMod.natCast_eq_zero_iff]; exact hn

/-- **Point-level 5-torsion criterion for secp256k1: `5 • P = 0 ⟺ ψ 5` vanishes at `P`.** -/
theorem secp256k1_five_nsmul_eq_zero_iff
    (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y) :
    (5 : ℕ) • (Point.some x y h) = 0 ↔ (secp256k1.ψ 5).evalEval x y = 0 := by
  have h2 : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have := const_ne 2 (by decide); exact_mod_cast this
  have h3ne : (3 : ZMod Secp256k1.p) ≠ 0 := by
    have := const_ne 3 (by decide); exact_mod_cast this
  have h64 : (64 : ZMod Secp256k1.p) ≠ 0 := by
    have := const_ne 64 (by decide); exact_mod_cast this
  have hcurve : y ^ 2 = x ^ 3 + 7 := by
    have he : secp256k1.toAffine.Equation x y := h.1
    rw [WeierstrassCurve.Affine.equation_iff] at he
    simp only [secp256k1] at he
    linear_combination he
  have hnegY : secp256k1.toAffine.negY x y = -y := by
    simp [WeierstrassCurve.Affine.negY, secp256k1]
  rw [secp256k1_psi5_evalEval x y hcurve]
  by_cases hy0 : y = secp256k1.toAffine.negY x y
  · -- 2-torsion branch: y = 0
    have hy00 : y = 0 := by
      rw [hnegY] at hy0
      have h2y : (2 : ZMod Secp256k1.p) * y = 0 := by linear_combination hy0
      rcases mul_eq_zero.mp h2y with hc | hc
      · exact absurd hc h2
      · exact hc
    have h2P : (2 : ℕ) • (Point.some x y h) = 0 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_eq hy0
    have h5P : (5 : ℕ) • (Point.some x y h) = Point.some x y h := by
      rw [show (5 : ℕ) = 1 + 2 + 2 from rfl, add_nsmul, add_nsmul, one_nsmul, h2P,
        add_zero, add_zero]
    refine iff_of_false ?_ ?_
    · rw [h5P]; exact Point.some_ne_zero h
    · have hx3 : x ^ 3 = -7 := by rw [hy00] at hcurve; linear_combination -hcurve
      have hval : 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656
          = 1750329 := by
        linear_combination (5 * x ^ 9 + 2625 * x ^ 6 - 30135 * x ^ 3 - 337855) * hx3
      rw [hval]
      have := const_ne 1750329 (by decide); exact_mod_cast this
  · -- y ≠ negY, so y ≠ 0
    have hy : y ≠ 0 := by
      intro h0; exact hy0 (by rw [hnegY, h0]; ring)
    by_cases h3 : (3 : ℕ) • (Point.some x y h) = 0
    · -- 3-torsion branch
      have h34 : 3 * x ^ 4 + 84 * x = 0 := by
        have := (secp256k1_three_nsmul_eq_zero_iff x y h).mp h3
        rwa [secp256k1_psi3_evalEval] at this
      have h5P2 : (5 : ℕ) • (Point.some x y h) = (2 : ℕ) • (Point.some x y h) := by
        rw [show (5 : ℕ) = 2 + 3 from rfl, add_nsmul, h3, add_zero]
      have h2ne : (2 : ℕ) • (Point.some x y h) ≠ 0 :=
        fun hc => hy ((secp256k1_two_nsmul_eq_zero_iff x y h).mp hc)
      refine iff_of_false ?_ ?_
      · rw [h5P2]; exact h2ne
      · intro hc
        have hfac : 3 * x * (x ^ 3 + 28) = 0 := by linear_combination h34
        rcases mul_eq_zero.mp hfac with h3x | hx328
        · rcases mul_eq_zero.mp h3x with hc3 | hx0
          · exact h3ne hc3
          · have hpv : 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656
                = -614656 := by rw [hx0]; ring
            rw [hpv] at hc
            exact (const_ne 614656 (by decide)) (by exact_mod_cast (by linear_combination -hc :
              (614656 : ZMod Secp256k1.p) = 0))
        · have hx3 : x ^ 3 = -28 := by linear_combination hx328
          have hpv : 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656
              = -49787136 := by
            linear_combination (5 * x ^ 9 + 2520 * x ^ 6 - 82320 * x ^ 3 + 1756160) * hx3
          rw [hpv] at hc
          exact (const_ne 49787136 (by decide)) (by exact_mod_cast (by linear_combination -hc :
            (49787136 : ZMod Secp256k1.p) = 0))
    · -- main branch: y ≠ 0 and 3P ≠ 0
      have hYd : y - secp256k1.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy0
      have hΨ3ne : 3 * x ^ 4 + 84 * x ≠ 0 := fun hc =>
        h3 ((secp256k1_three_nsmul_eq_zero_iff x y h).mpr (by rw [secp256k1_psi3_evalEval]; exact hc))
      set s2 := secp256k1.toAffine.slope x x y y with hs2def
      set X2 := secp256k1.toAffine.addX x x s2 with hX2def
      set Y2 := secp256k1.toAffine.addY x x y s2 with hY2def
      have hsl2 : s2 * (2 * y) = 3 * x ^ 2 := by
        rw [hs2def, slope_of_Y_ne rfl hy0, div_mul_eq_mul_div, div_eq_iff hYd]
        simp only [secp256k1, WeierstrassCurve.Affine.negY]
        ring
      have hId : (s2 ^ 2 - 3 * x) * (4 * y ^ 2) = -(3 * x ^ 4 + 84 * x) := by
        linear_combination (2 * s2 * y + 3 * x ^ 2) * hsl2 + (-12 * x) * hcurve
      have hd : s2 ^ 2 - 3 * x ≠ 0 := by
        intro hc
        apply hΨ3ne
        have := hId
        rw [hc, zero_mul] at this
        linear_combination -this
      have hx2val : X2 = s2 ^ 2 - 2 * x := by
        rw [hX2def]; simp only [WeierstrassCurve.Affine.addX, secp256k1]; ring
      have hx2x : X2 - x = s2 ^ 2 - 3 * x := by rw [hx2val]; ring
      have hx2ne : X2 ≠ x := by rw [← sub_ne_zero, hx2x]; exact hd
      have hy2val : Y2 = -(s2 * (s2 ^ 2 - 3 * x) + y) := by
        rw [hY2def]
        simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
          WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1]
        ring
      have hns2 : secp256k1.toAffine.Nonsingular X2 Y2 := by
        rw [hX2def, hY2def, hs2def]; exact nonsingular_add h h (fun hxy => hy0 hxy.2)
      have hP2 : (2 : ℕ) • (Point.some x y h) = Point.some X2 Y2 hns2 := by
        rw [two_nsmul, hX2def, hY2def, hs2def]; exact Point.add_self_of_Y_ne hy0
      set s3 := secp256k1.toAffine.slope X2 x Y2 y with hs3def
      set X3 := secp256k1.toAffine.addX X2 x s3 with hX3def
      set Y3 := secp256k1.toAffine.addY X2 x Y2 s3 with hY3def
      have hx3val : X3 = s3 ^ 2 - (s2 ^ 2 - 2 * x) - x := by
        rw [hX3def]
        simp only [WeierstrassCurve.Affine.addX, secp256k1]
        rw [hx2val]; ring
      have hns3 : secp256k1.toAffine.Nonsingular X3 Y3 := by
        rw [hX3def, hY3def, hs3def]; exact nonsingular_add hns2 h (fun hxy => hx2ne hxy.1)
      have hP3 : (3 : ℕ) • (Point.some x y h) = Point.some X3 Y3 hns3 := by
        rw [show (3 : ℕ) = 2 + 1 from rfl, add_nsmul, one_nsmul, hP2, hX3def, hY3def, hs3def]
        exact Point.add_some (fun hxy => hx2ne hxy.1)
      have hsl3s : s3 * (X2 - x) = Y2 - y := by
        rw [hs3def, slope_of_X_ne hx2ne]
        exact div_mul_cancel₀ _ (sub_ne_zero.mpr hx2ne)
      have hℓ3 : (s2 ^ 2 - 3 * x) * s3 = -(s2 * (s2 ^ 2 - 3 * x) + y) - y := by
        have hstep := hsl3s
        rw [hy2val, hx2x] at hstep
        linear_combination hstep
      have hxiff : X2 = X3 ↔ 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3
          - 614656 = 0 := by
        rw [hx3val, hx2val, eq_comm]
        exact five_core x y s2 s3 h64 hcurve hy (by linear_combination hsl2) hd hℓ3
      have hyimp : X2 = X3 → Y2 = secp256k1.toAffine.negY X3 Y3 := by
        intro hx
        rcases Y_eq_of_X_eq hns2.1 hns3.1 hx with hyy | hyn
        · exfalso
          have e23 : (2 : ℕ) • (Point.some x y h) = (3 : ℕ) • (Point.some x y h) := by
            rw [hP2, hP3, Point.some.injEq]; exact ⟨hx, hyy⟩
          rw [show (3 : ℕ) = 2 + 1 from rfl, add_nsmul, one_nsmul] at e23
          exact (Point.some_ne_zero h) (self_eq_add_right.mp e23)
        · exact hyn
      rw [show (5 : ℕ) = 2 + 3 from rfl, add_nsmul, hP2, hP3, add_eq_zero_iff_eq_neg,
        Point.neg_some, Point.some.injEq]
      constructor
      · rintro ⟨hx, _⟩; exact hxiff.mp hx
      · intro hp
        exact ⟨hxiff.mpr hp, hyimp (hxiff.mpr hp)⟩

end Ecdlp.Curve
