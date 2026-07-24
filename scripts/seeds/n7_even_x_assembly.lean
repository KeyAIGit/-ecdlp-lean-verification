import Ecdlp.Proved.DivisionPolynomialPsiSqDoubling
import Ecdlp.Proved.DivisionPolynomialPhiDoubling

namespace Ecdlp.Curve.N7Uniform

open Polynomial WeierstrassCurve WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]
variable {x : ZMod Secp256k1.p}

/-- Tangent doubling transports the division-polynomial x-coordinate ratio
from index `k` to index `2k`. -/
theorem even_x_algebra (k : ℕ) (Xk Yk sk : ZMod Secp256k1.p)
    (hXk : Xk = (secp256k1.Φ (k : ℤ)).eval x / (secp256k1.ΨSq (k : ℤ)).eval x)
    (hden : (secp256k1.ΨSq (k : ℤ)).eval x ≠ 0)
    (hslope : sk * (2 * Yk) = 3 * Xk ^ 2)
    (hcurvek : Yk ^ 2 = Xk ^ 3 + 7) :
    secp256k1.toAffine.addX Xk Xk sk
      = (secp256k1.Φ ((2 * k : ℕ) : ℤ)).eval x /
          (secp256k1.ΨSq ((2 * k : ℕ) : ℤ)).eval x := by
  let A : ZMod Secp256k1.p := (secp256k1.Φ (k : ℤ)).eval x
  let B : ZMod Secp256k1.p := (secp256k1.ΨSq (k : ℤ)).eval x
  have hXk' : Xk = A / B := by
    simpa [A, B] using hXk
  have hB : B ≠ 0 := by
    simpa [B] using hden
  have hAB : Xk * B = A := by
    rw [hXk']
    exact div_mul_cancel₀ A hB

  have h3 : (3 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((3 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]
      native_decide
    simpa using h
  have h4 : (4 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((4 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]
      native_decide
    simpa using h
  have h7 : (7 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((7 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]
      native_decide
    simpa using h

  have hXcurve : Xk ^ 3 + 7 ≠ 0 := by
    intro hzero
    have hYsq : Yk ^ 2 = 0 := by
      rw [hcurvek, hzero]
    have hY : Yk = 0 :=
      (pow_eq_zero_iff (by norm_num : (2 : ℕ) ≠ 0)).mp hYsq
    have hslope' := hslope
    rw [hY] at hslope'
    have h3Xsq : (3 : ZMod Secp256k1.p) * Xk ^ 2 = 0 := by
      linear_combination hslope'
    have hXsq : Xk ^ 2 = 0 :=
      (mul_eq_zero.mp h3Xsq).resolve_left h3
    have hX : Xk = 0 :=
      (pow_eq_zero_iff (by norm_num : (2 : ℕ) ≠ 0)).mp hXsq
    apply h7
    simpa [hX] using hzero

  have hD : A ^ 3 + 7 * B ^ 3 ≠ 0 := by
    intro hD0
    have hD0' := hD0
    rw [← hAB] at hD0'
    apply hXcurve
    have hfactor : B ^ 3 * (Xk ^ 3 + 7) = 0 := by
      linear_combination hD0'
    exact (mul_eq_zero.mp hfactor).resolve_left (pow_ne_zero 3 hB)

  have hΨ :
      (secp256k1.ΨSq (2 * (k : ℤ))).eval x =
        4 * B * (A ^ 3 + 7 * B ^ 3) := by
    simpa [A, B] using secp256k1_ΨSq_two_mul_eval (k : ℤ) x
  have hΦ :
      (secp256k1.Φ (2 * (k : ℤ))).eval x =
        A ^ 4 - 56 * A * B ^ 3 := by
    simpa [A, B] using secp256k1_Φ_two_mul_eval (k : ℤ) x
  have hden2 : 4 * B * (A ^ 3 + 7 * B ^ 3) ≠ 0 :=
    mul_ne_zero (mul_ne_zero h4 hB) hD
  have hindex : ((2 * k : ℕ) : ℤ) = 2 * (k : ℤ) := by
    norm_num

  rw [hindex, hΦ, hΨ, eq_div_iff hden2]
  simp only [WeierstrassCurve.Affine.addX, secp256k1]
  rw [← hAB]
  linear_combination
    B ^ 4 * (2 * Yk * sk + 3 * Xk ^ 2) * hslope
      - 4 * B ^ 4 * sk ^ 2 * hcurvek

end Ecdlp.Curve.N7Uniform
