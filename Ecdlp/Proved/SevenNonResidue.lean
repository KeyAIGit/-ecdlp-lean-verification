import Mathlib.NumberTheory.LegendreSymbol.Basic
import Ecdlp.Proved.Secp256k1PrimeP
import Ecdlp.Proved.TorsionPointCount

/-!
# `7` is a quadratic non-residue modulo the secp256k1 field prime

The closed Euler-criterion witness below proves that `7` is not a square in
`ZMod Secp256k1.p`. Substituting `x = 0` in `y^2 = x^3 + 7` would make `7`
a square, so no affine secp256k1 point over the base field has zero
`x`-coordinate.

The two `native_decide` uses are closed computations over literal secp256k1
constants. They contribute only `Lean.ofReduceBool`, which is already in the
repository's allowed trust base.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

/-- `7` is nonzero in the secp256k1 base field. -/
theorem secp256k1_seven_ne_zero : (7 : ZMod Secp256k1.p) ≠ 0 := by
  native_decide

/-- Closed Euler-criterion witness for `7` in the secp256k1 base field. -/
theorem secp256k1_seven_pow_ne_one :
    (7 : ZMod Secp256k1.p) ^ (Secp256k1.p / 2) ≠ 1 := by
  native_decide

/-- `7` is not a square in the secp256k1 base field. -/
theorem secp256k1_seven_not_isSquare :
    ¬ IsSquare (7 : ZMod Secp256k1.p) := fun hsq =>
  secp256k1_seven_pow_ne_one
    ((ZMod.euler_criterion Secp256k1.p secp256k1_seven_ne_zero).mp hsq)

/-- No affine secp256k1 point over the base field has `x`-coordinate zero. -/
theorem secp256k1_x_ne_zero {x y : ZMod Secp256k1.p}
    (h : secp256k1.toAffine.Nonsingular x y) : x ≠ 0 := by
  intro hx0
  refine secp256k1_seven_not_isSquare ⟨y, ?_⟩
  have hc : y ^ 2 = x ^ 3 + 7 := secp256k1_curve_of_nonsingular x y h
  rw [hx0] at hc
  linear_combination -hc

end Ecdlp.Curve
