import Mathlib
import Ecdlp.Proved.DivisionPolynomial

/-!
# The multiplication-by-`n` `x`-coordinate formula — base case `n = 2` for secp256k1

The **division-polynomial multiplication formula** `x([n]P) = Φₙ(x) / ΨSqₙ(x)` is the engine
behind the *general* `ψₙ`-vanishing ⟺ `n`-torsion bridge (`notes/FOUNDATIONS.md`, rung 4): a
nonzero point `P` is `n`-torsion exactly when `[n]P = O`, i.e. exactly when the denominator
`ΨSqₙ(x(P))` vanishes. Mathlib formalizes the polynomials `Φₙ` (`Φ`) and `ΨSqₙ` (`ΨSq`)
themselves (`Mathlib.AlgebraicGeometry.EllipticCurve.DivisionPolynomial.Basic`) but **not** the
formula linking them to `[n]P` on the point group — that link (for all `n`, by induction on the
division-polynomial recurrence) is the missing rung, absent from Mathlib v4.31 (it lives only in
a stalled upstream PR; see `notes/UPSTREAM_SCAN.md`).

This file proves the **base case `n = 2`** of that formula for secp256k1, in Mathlib's *canonical*
`Φ`/`ΨSq` vocabulary (the earlier per-`n` torsion bridges used ad-hoc reduced polynomials like
`3x⁴+84x`; this states the general `Φₙ/ΨSqₙ` shape). For secp256k1 (`b₄ = 0`, `b₆ = 28`,
`b₈ = 0`):
* `Φ 2 = X⁴ − 56X`,
* `Ψ₂Sq = 4X³ + 28 = 4(X³ + 7) = 4y²` on the curve,
so `x(2•P) = (x⁴ − 56x)/(4y²)` — the standard chord-tangent doubling `x`-coordinate, now shown to
equal Mathlib's `Φ 2 / Ψ₂Sq`. Everything is a ring identity over `𝔽_p`; the only hypotheses are
the curve equation and that `P` is not 2-torsion (`2y ≠ 0`, so the tangent is defined).
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- **`Φ 2 = X⁴ − 56X` for secp256k1** (`b₄ = 0`, `2·b₆ = 56`, `b₈ = 0`). The numerator of the
doubled point's `x`-coordinate, in Mathlib's canonical division-polynomial `Φ`. -/
theorem secp256k1_Φ₂ : secp256k1.Φ 2 = X ^ 4 - C 56 * X := by
  rw [WeierstrassCurve.Φ_two, secp256k1_b₄, secp256k1_b₆, secp256k1_b₈]
  simp only [C_0, zero_mul, sub_zero]
  norm_num

/-- `Φ 2` evaluated at `x` is `x⁴ − 56x`. -/
theorem secp256k1_Φ₂_eval (x : ZMod Secp256k1.p) : (secp256k1.Φ 2).eval x = x ^ 4 - 56 * x := by
  rw [secp256k1_Φ₂]
  simp only [eval_sub, eval_pow, eval_mul, eval_C, eval_X]

/-- `Ψ₂Sq` evaluated at `x` is `4x³ + 28`. -/
theorem secp256k1_Ψ₂Sq_eval (x : ZMod Secp256k1.p) : secp256k1.Ψ₂Sq.eval x = 4 * x ^ 3 + 28 := by
  rw [secp256k1_Ψ₂Sq]
  simp only [eval_add, eval_mul, eval_pow, eval_C, eval_X]

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Multiplication-by-2 `x`-coordinate formula for secp256k1 — `x(2•P) = Φ₂(x)/Ψ₂Sq(x)`.**
For a nonzero point `P = (x,y)` on `y² = x³ + 7` that is *not* 2-torsion (`y ≠ negY x y`, i.e.
`2y ≠ 0`, so the tangent slope is defined), the `x`-coordinate of the doubled point
`addX x x (slope x x y y)` equals `(Φ 2)(x) / (Ψ₂Sq)(x)` with Mathlib's canonical division
polynomials. This is the **base case `n = 2`** of the general multiplication formula
`x([n]P) = Φₙ/ΨSqₙ` — the engine of the `ψₙ`-vanishing ⟺ `n`-torsion bridge whose general form
is the missing Mathlib rung (`notes/FOUNDATIONS.md`). Proof: `Ψ₂Sq(x) = 4y²` on the curve, the
doubling slope satisfies `2y·ℓ = 3x²`, and a single certified `linear_combination` closes the
cleared identity `addX·(4x³+28) = x⁴ − 56x`. -/
theorem secp256k1_double_x_eq_Φ₂_div_Ψ₂Sq
    (x y : ZMod Secp256k1.p) (hc : y ^ 2 = x ^ 3 + 7)
    (hy : y ≠ secp256k1.toAffine.negY x y) :
    secp256k1.toAffine.addX x x (secp256k1.toAffine.slope x x y y)
      = (secp256k1.Φ 2).eval x / secp256k1.Ψ₂Sq.eval x := by
  rw [secp256k1_Φ₂_eval, secp256k1_Ψ₂Sq_eval]
  have hnegY : secp256k1.toAffine.negY x y = -y := by
    simp [WeierstrassCurve.Affine.negY, secp256k1]
  have hd : y - secp256k1.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy
  have h2y : (2 : ZMod Secp256k1.p) * y ≠ 0 := by
    intro h; exact hy (by rw [hnegY]; linear_combination h)
  have hden : (4 : ZMod Secp256k1.p) * x ^ 3 + 28 = 4 * y ^ 2 := by linear_combination -4 * hc
  have hden_ne : (4 : ZMod Secp256k1.p) * x ^ 3 + 28 ≠ 0 := by
    rw [hden]; intro h
    exact h2y (mul_self_eq_zero.mp (by linear_combination h))
  set ℓ := secp256k1.toAffine.slope x x y y with hℓ
  have hslope : ℓ * (2 * y) = 3 * x ^ 2 := by
    rw [hℓ, WeierstrassCurve.Affine.slope_of_Y_ne rfl hy, div_mul_eq_mul_div, div_eq_iff hd]
    simp only [secp256k1, WeierstrassCurve.Affine.negY]
    ring
  rw [eq_div_iff hden_ne]
  simp only [WeierstrassCurve.Affine.addX, secp256k1]
  linear_combination (2 * y * ℓ + 3 * x ^ 2) * hslope - 4 * ℓ ^ 2 * hc

end Ecdlp.Curve
