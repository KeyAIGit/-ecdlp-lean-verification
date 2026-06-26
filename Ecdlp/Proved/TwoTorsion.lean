import Mathlib
import Ecdlp.Proved.DivisionPolynomial

/-!
# secp256k1 2-torsion via the division polynomial (rung 4, easy direction)

The first connection between Mathlib's division polynomials and actual torsion
points, specialised to the 2-torsion of secp256k1 and proved unconditionally.

A point `(x, 0)` lies on `Y² = X³ + 7` exactly when `x³ + 7 = 0`; and the
2-division polynomial is `Ψ₂Sq = 4X³ + 28 = 4(X³ + 7)` (`DivisionPolynomial.lean`).
So any order-2 `x`-coordinate is a root of `Ψ₂Sq` — the forward direction of the
general criterion `ψₙ(x_P) = 0 ⟺ [n]P = O`. The general statement (all `n`, both
directions, tied to point order) is the open rung toward the Weil pairing; see
`notes/FOUNDATIONS.md`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **An order-2 `x`-coordinate is a root of the 2-division polynomial.** If `(x, 0)`
satisfies the secp256k1 Weierstrass equation (a 2-torsion point), then `Ψ₂Sq`
vanishes at `x`. Unconditional (no `[Fact p.Prime]`): the forward direction needs
only the ring identity `Ψ₂Sq = 4(X³ + 7)`. -/
theorem secp256k1_Ψ₂Sq_root_of_two_torsion (x : ZMod Secp256k1.p)
    (hx : secp256k1.toAffine.Equation x 0) :
    secp256k1.Ψ₂Sq.eval x = 0 := by
  rw [WeierstrassCurve.Affine.equation_iff] at hx
  rw [secp256k1_Ψ₂Sq]
  simp only [secp256k1, eval_add, eval_mul, eval_pow, eval_C, eval_X] at hx ⊢
  first
    | linear_combination 4 * hx
    | linear_combination -4 * hx

end Ecdlp.Curve
