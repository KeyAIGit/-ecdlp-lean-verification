import Mathlib
import Ecdlp.Proved.DivisionPolynomialEvalBridge
import Ecdlp.Proved.MultiplicationFormula
import Ecdlp.Proved.MultiplicationYFormula

/-!
# Point-level doubling over the algebraic closure

This is the algebraic-closure port of `DoublingPointFormula.lean`. It combines the
`x`- and `y`-coordinate doubling formulas for `secp256k1Bar`, the base change of
secp256k1 to `AlgebraicClosure (ZMod Secp256k1.p)`.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

private noncomputable abbrev φK :
    ZMod Secp256k1.p →+* AlgebraicClosure (ZMod Secp256k1.p) :=
  algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p))

private theorem secp256k1Bar_Φ₂_eval
    (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    (secp256k1Bar.Φ 2).eval x = x ^ 4 - 56 * x := by
  have hmap : secp256k1Bar.Φ 2 = (secp256k1.Φ 2).map φK := by
    simp only [secp256k1Bar, WeierstrassCurve.map_Φ]
  rw [hmap, secp256k1_Φ₂]
  simp only [Polynomial.map_sub, Polynomial.map_mul, Polynomial.map_pow,
    Polynomial.map_C, Polynomial.map_X, Polynomial.map_ofNat, map_ofNat,
    eval_sub, eval_mul, eval_pow, eval_C, eval_X, Polynomial.eval_ofNat]

private theorem secp256k1Bar_Ψ₂Sq_eval
    (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.Ψ₂Sq.eval x = 4 * x ^ 3 + 28 := by
  have hmap : secp256k1Bar.Ψ₂Sq = (secp256k1.Ψ₂Sq).map φK := by
    simp only [secp256k1Bar, WeierstrassCurve.map_Ψ₂Sq]
  rw [hmap, secp256k1_Ψ₂Sq]
  simp only [Polynomial.map_add, Polynomial.map_mul, Polynomial.map_pow,
    Polynomial.map_C, Polynomial.map_X, Polynomial.map_ofNat, map_ofNat,
    eval_add, eval_mul, eval_pow, eval_C, eval_X, Polynomial.eval_ofNat]

private theorem secp256k1Bar_negY
    (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.negY x y = -y := by
  simp [WeierstrassCurve.Affine.negY, secp256k1Bar, WeierstrassCurve.map, secp256k1]

private theorem secp256k1Bar_double_x_eq_Φ₂_div_Ψ₂Sq
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (hc : y ^ 2 = x ^ 3 + 7)
    (hy : y ≠ secp256k1Bar.toAffine.negY x y) :
    secp256k1Bar.toAffine.addX x x (secp256k1Bar.toAffine.slope x x y y)
      = (secp256k1Bar.Φ 2).eval x / secp256k1Bar.Ψ₂Sq.eval x := by
  rw [secp256k1Bar_Φ₂_eval, secp256k1Bar_Ψ₂Sq_eval]
  have hnegY : secp256k1Bar.toAffine.negY x y = -y := secp256k1Bar_negY x y
  have hd : y - secp256k1Bar.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy
  have h2y : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * y ≠ 0 := by
    intro h
    exact hy (by rw [hnegY]; linear_combination h)
  have hden : (4 : AlgebraicClosure (ZMod Secp256k1.p)) * x ^ 3 + 28
      = 4 * y ^ 2 := by
    linear_combination -4 * hc
  have hden_ne : (4 : AlgebraicClosure (ZMod Secp256k1.p)) * x ^ 3 + 28 ≠ 0 := by
    rw [hden]
    intro h
    exact h2y (mul_self_eq_zero.mp (by linear_combination h))
  set ℓ := secp256k1Bar.toAffine.slope x x y y with hℓ
  have hslope : ℓ * (2 * y) = 3 * x ^ 2 := by
    rw [hℓ, WeierstrassCurve.Affine.slope_of_Y_ne rfl hy,
      div_mul_eq_mul_div, div_eq_iff hd]
    simp only [secp256k1Bar, WeierstrassCurve.map, WeierstrassCurve.map_a₁,
      WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄,
      WeierstrassCurve.map_a₆, secp256k1, map_zero, map_ofNat,
      WeierstrassCurve.Affine.negY]
    ring
  rw [eq_div_iff hden_ne]
  simp only [WeierstrassCurve.Affine.addX, secp256k1Bar, WeierstrassCurve.map,
    WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃,
    WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆, secp256k1, map_zero, map_ofNat]
  linear_combination (2 * y * ℓ + 3 * x ^ 2) * hslope - 4 * ℓ ^ 2 * hc

private theorem secp256k1Bar_double_y_eq_ω₂
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (hc : y ^ 2 = x ^ 3 + 7)
    (hy : y ≠ secp256k1Bar.toAffine.negY x y) :
    secp256k1Bar.toAffine.addY x x y (secp256k1Bar.toAffine.slope x x y y)
      = (x ^ 6 + 140 * x ^ 3 - 392) / (2 * y) ^ 3 := by
  have hnegY : secp256k1Bar.toAffine.negY x y = -y := secp256k1Bar_negY x y
  have hd : y - secp256k1Bar.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy
  have h2y : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * y ≠ 0 := by
    intro h
    exact hy (by rw [hnegY]; linear_combination h)
  have hden_ne : ((2 : AlgebraicClosure (ZMod Secp256k1.p)) * y) ^ 3 ≠ 0 :=
    pow_ne_zero 3 h2y
  set ℓ := secp256k1Bar.toAffine.slope x x y y with hℓ
  have hslope : ℓ * (2 * y) = 3 * x ^ 2 := by
    rw [hℓ, WeierstrassCurve.Affine.slope_of_Y_ne rfl hy,
      div_mul_eq_mul_div, div_eq_iff hd]
    simp only [secp256k1Bar, WeierstrassCurve.map, WeierstrassCurve.map_a₁,
      WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄,
      WeierstrassCurve.map_a₆, secp256k1, map_zero, map_ofNat,
      WeierstrassCurve.Affine.negY]
    ring
  rw [eq_div_iff hden_ne]
  simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
    WeierstrassCurve.Affine.addX, WeierstrassCurve.Affine.negY, secp256k1Bar,
    WeierstrassCurve.map, WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂,
    WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆,
    secp256k1, map_zero, map_ofNat]
  linear_combination
    (-4 * y ^ 2 * ℓ ^ 2 - 6 * x ^ 2 * y * ℓ - 9 * x ^ 4
      + 12 * x * y ^ 2) * hslope
      + (28 * x ^ 3 - 8 * y ^ 2 - 56) * hc

/-- Point-level doubling for `secp256k1Bar` in division-polynomial coordinates. -/
theorem secp256k1Bar_two_nsmul_coords
    (x y X Y : AlgebraicClosure (ZMod Secp256k1.p))
    (hc : y ^ 2 = x ^ 3 + 7)
    (h : secp256k1Bar.toAffine.Nonsingular x y)
    (h' : secp256k1Bar.toAffine.Nonsingular X Y)
    (hy : y ≠ secp256k1Bar.toAffine.negY x y)
    (hP : (2 : ℕ) • Point.some x y h = Point.some X Y h') :
    X = (secp256k1Bar.Φ 2).eval x / secp256k1Bar.Ψ₂Sq.eval x
      ∧ Y = (x ^ 6 + 140 * x ^ 3 - 392) / (2 * y) ^ 3 := by
  rw [two_nsmul, Point.add_self_of_Y_ne hy] at hP
  injection hP with hX hY
  refine ⟨?_, ?_⟩
  · rw [← hX]
    exact secp256k1Bar_double_x_eq_Φ₂_div_Ψ₂Sq x y hc hy
  · rw [← hY]
    exact secp256k1Bar_double_y_eq_ω₂ x y hc hy

end Ecdlp.Curve
