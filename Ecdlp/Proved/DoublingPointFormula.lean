/-
# Point-level doubling in division-polynomial form for secp256k1 (N7-uniform S3a base)

Combines the two landed coordinate formulas — the `x`-doubling
`x(2•P) = Φ₂(x)/Ψ₂Sq(x)` (`MultiplicationFormula.lean`) and the `y`-doubling
`y(2•P) = ω₂/(2y)³` (`MultiplicationYFormula.lean`) — into a statement about the **actual
group operation** `2 • P` on `secp256k1.toAffine.Point`, not just the raw `addX`/`addY`
coordinates.

This is the **`n = 2` Point-level instance** of the registered open target
`n7_uniform_secp256k1_x` (the uniform `x(n•P) = Φₙ/ΨSqₙ`): the base case of node S3a of the
N7-uniform build (`BARRIERS.md §B3`), now connected to `Point`. Given a non-2-torsion `P`
whose double is the affine point `(X, Y)`, it pins **both** coordinates to their
division-polynomial values.

**Honest scope.** Fixed `n = 2` only; the uniform statement for all `n` remains the open
target. This does not define a general bivariate `ωₙ`.
-/
import Mathlib
import Ecdlp.Proved.MultiplicationFormula
import Ecdlp.Proved.MultiplicationYFormula

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Point-level doubling for secp256k1 in division-polynomial form (`n = 2`).**
For a nonsingular `P = (x,y)` on `y² = x³ + 7` that is not 2-torsion (`y ≠ negY x y`), if the
double `2 • P` is the affine point `(X, Y)` then `X = Φ₂(x)/Ψ₂Sq(x)` and `Y = ω₂/(2y)³` with
`ω₂ = x⁶ + 140x³ − 392`. The `n = 2` Point-level base of node S3a and the base case of the
open target `n7_uniform_secp256k1_x`. -/
theorem secp256k1_two_nsmul_coords
    (x y X Y : ZMod Secp256k1.p) (hc : y ^ 2 = x ^ 3 + 7)
    (h : secp256k1.toAffine.Nonsingular x y)
    (h' : secp256k1.toAffine.Nonsingular X Y)
    (hy : y ≠ secp256k1.toAffine.negY x y)
    (hP : (2 : ℕ) • Point.some x y h = Point.some X Y h') :
    X = (secp256k1.Φ 2).eval x / secp256k1.Ψ₂Sq.eval x
      ∧ Y = (x ^ 6 + 140 * x ^ 3 - 392) / (2 * y) ^ 3 := by
  rw [two_nsmul, Point.add_self_of_Y_ne hy] at hP
  injection hP with hX hY
  refine ⟨?_, ?_⟩
  · rw [← hX]; exact secp256k1_double_x_eq_Φ₂_div_Ψ₂Sq x y hc hy
  · rw [← hY]; exact secp256k1_double_y_eq_ω₂ x y hc hy

end Ecdlp.Curve
