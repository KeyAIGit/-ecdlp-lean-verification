import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.ThreeTorsionBridge

/-!
# Division-polynomial 5-torsion bridge for secp256k1 (scratch / server verification)

Stage-1 reduction `secp256k1_psi5_evalEval` and (attempt) the point-level `n = 5`
equivalence `5•P = 0 ↔ ψ 5 vanishes at P`.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- Concrete evaluation of the univariate `preΨ₄` for secp256k1:
`preΨ₄(x) = 2x⁶ + 280x³ − 784`. -/
theorem secp256k1_preΨ₄_eval (x : ZMod Secp256k1.p) :
    secp256k1.preΨ₄.eval x = 2 * x ^ 6 + 280 * x ^ 3 - 784 := by
  rw [WeierstrassCurve.preΨ₄, secp256k1_b₂, secp256k1_b₄, secp256k1_b₆, secp256k1_b₈]
  simp only [eval_add, eval_sub, eval_mul, eval_pow, eval_X, eval_C, eval_ofNat]
  ring

/-- Concrete evaluation of `Ψ₃` for secp256k1: `Ψ₃(x) = 3x⁴ + 84x`. -/
theorem secp256k1_Ψ₃_eval (x : ZMod Secp256k1.p) :
    secp256k1.Ψ₃.eval x = 3 * x ^ 4 + 84 * x := by
  rw [secp256k1_Ψ₃]
  simp only [eval_add, eval_mul, eval_pow, eval_X, eval_C, eval_ofNat]
  ring

/-- The bivariate 2-division polynomial `ψ₂` evaluated at `(x,y)` on secp256k1 is `2y`
(since `a₁ = a₃ = 0`). -/
theorem secp256k1_psi2_evalEval (x y : ZMod Secp256k1.p) :
    secp256k1.ψ₂.evalEval x y = 2 * y := by
  rw [WeierstrassCurve.ψ₂, evalEval_polynomialY]
  simp [secp256k1]

/-- **Stage-1: the bivariate 5-division polynomial `ψ 5` evaluated at a point `(x,y)` of
secp256k1 (`y² = x³ + 7`) reduces to the concrete degree-12 univariate polynomial in `x`**
`5x¹² + 2660x⁹ − 11760x⁶ − 548800x³ − 614656`. (`ψ 5` is odd, hence univariate on the curve.) -/
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

end Ecdlp.Curve
