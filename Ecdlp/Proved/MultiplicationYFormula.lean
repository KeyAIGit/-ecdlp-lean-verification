/-
# The multiplication-by-`n` `y`-coordinate formula — base case `n = 2` for secp256k1

Companion to `MultiplicationFormula.lean` (which proves the `x`-coordinate doubling
`x(2•P) = Φ₂(x)/Ψ₂Sq(x) = (x⁴−56x)/(2y)²`). This file proves the **`y`-coordinate** of the
doubled point:
```
y(2•P) = (x⁶ + 140x³ − 392) / (2y)³.
```
In division-polynomial terms this is `y(2•P) = ω₂/ψ₂³` with `ψ₂ = 2y` and the `n = 2`
`y`-coordinate ("omega") division polynomial `ω₂ = x⁶ + 140x³ − 392` for secp256k1
(`y² = x³ + 7`, `a₁ = a₃ = 0`). It is the **base case of node S3a** of the N7-uniform build
(`BARRIERS.md §B3`, proof DAG in `targets/n7_uniform_secp256k1_x.json`): the general
`y([n]P) = ωₙ(P)/ψₙ(P)³` on points, the `y`-analogue of the `x`-formula and the first
`y`-coordinate division-polynomial value in the repo.

Mathlib has **no** `ω` (y-coordinate) division polynomial (open `TODO`); the value here is
derived directly from the group law's doubling `y`-coordinate `addY` and certified by a single
`linear_combination` against the curve equation and the doubling-slope relation.

**Honest scope.** Fixed `n = 2` only, and it is a coordinate identity about `addY`/`slope` —
it is `y(2•P)` written as a rational function; the *uniform* `y([n]P) = ωₙ/ψₙ³` and its
connection to a general bivariate `ωₙ` remain the open target.
-/
import Mathlib
import Ecdlp.Proved.DivisionPolynomial

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Multiplication-by-2 `y`-coordinate formula for secp256k1 — `y(2•P) = ω₂/(2y)³`.**
For a nonzero point `P = (x,y)` on `y² = x³ + 7` that is not 2-torsion (`y ≠ negY x y`, i.e.
`2y ≠ 0`), the `y`-coordinate of the doubled point `addY x x y (slope x x y y)` equals
`(x⁶ + 140x³ − 392)/(2y)³` — the `n = 2` `y`-coordinate division-polynomial value `ω₂/ψ₂³`
(base case of node S3a of the N7-uniform build). Proof: the doubling slope satisfies
`2y·ℓ = 3x²`, and a single certified `linear_combination` closes the cleared identity
`addY·(2y)³ = x⁶ + 140x³ − 392` modulo the curve equation. -/
theorem secp256k1_double_y_eq_ω₂
    (x y : ZMod Secp256k1.p) (hc : y ^ 2 = x ^ 3 + 7)
    (hy : y ≠ secp256k1.toAffine.negY x y) :
    secp256k1.toAffine.addY x x y (secp256k1.toAffine.slope x x y y)
      = (x ^ 6 + 140 * x ^ 3 - 392) / (2 * y) ^ 3 := by
  have hnegY : secp256k1.toAffine.negY x y = -y := by
    simp [WeierstrassCurve.Affine.negY, secp256k1]
  have hd : y - secp256k1.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy
  have h2y : (2 : ZMod Secp256k1.p) * y ≠ 0 := by
    intro h; exact hy (by rw [hnegY]; linear_combination h)
  have hden_ne : ((2 : ZMod Secp256k1.p) * y) ^ 3 ≠ 0 := pow_ne_zero 3 h2y
  set ℓ := secp256k1.toAffine.slope x x y y with hℓ
  have hslope : ℓ * (2 * y) = 3 * x ^ 2 := by
    rw [hℓ, WeierstrassCurve.Affine.slope_of_Y_ne rfl hy, div_mul_eq_mul_div, div_eq_iff hd]
    simp only [secp256k1, WeierstrassCurve.Affine.negY]
    ring
  rw [eq_div_iff hden_ne]
  simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
    WeierstrassCurve.Affine.addX, WeierstrassCurve.Affine.negY, secp256k1]
  linear_combination (-4 * y ^ 2 * ℓ ^ 2 - 6 * x ^ 2 * y * ℓ - 9 * x ^ 4 + 12 * x * y ^ 2) * hslope
    + (28 * x ^ 3 - 8 * y ^ 2 - 56) * hc

end Ecdlp.Curve
