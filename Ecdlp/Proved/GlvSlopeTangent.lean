import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# GLV slope-scaling identity (tangent / doubling branch)

Companion to `Ecdlp/Proved/GlvSlope.lean` (secant branch). The secp256k1 GLV
endomorphism acts on affine points by `(x, y) ↦ (β·x, y)`. This lemma records how
that map scales the *tangent slope* at a point being doubled (`x₁ = x₂`, `y₁ ≠ -y₂`):
replacing `x₁, x₂` by `β·x₁, β·x₂` multiplies the slope by `β²`.

Unlike the secant branch, the cube-root relation `β³ = 1` is **not** needed here: the
tangent slope is `3x₁²/(2y₁)` (since for secp256k1 `negY x y = -y` is independent of
`x`, as `a₁ = a₃ = 0`), and `3·(β·x₁)²/(2y₁) = β²·3x₁²/(2y₁)` is immediate. The only
structural input is that `negY` does not see the `x`-coordinate, so the tangent-branch
side condition `y₁ ≠ negY x₂ y₂` transfers verbatim to `y₁ ≠ negY (β·x₂) y₂`.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

/-- **GLV slope scaling, tangent branch.** For a point being doubled (`x₁ = x₂` and
`y₁ ≠ negY x₂ y₂`), applying the GLV endomorphism `x ↦ β·x` to the `X`-coordinates
multiplies the tangent slope by `β²`. See `secp256k1_glv_slope_of_X_ne` for the secant
branch and the namespace note there about `secp256k1.toAffine.slope`. -/
theorem secp256k1_glv_slope_of_Y_ne [Fact (Nat.Prime Secp256k1.p)]
    (x₁ x₂ y₁ y₂ : ZMod Secp256k1.p) (hx : x₁ = x₂)
    (hy : y₁ ≠ secp256k1.toAffine.negY x₂ y₂) :
    secp256k1.toAffine.slope ((Secp256k1.beta : ZMod Secp256k1.p) * x₁)
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₂) y₁ y₂
      = (Secp256k1.beta : ZMod Secp256k1.p) ^ 2
          * secp256k1.toAffine.slope x₁ x₂ y₁ y₂ := by
  -- `negY` is `x`-independent for secp256k1 (`a₁ = a₃ = 0`): `negY _ y = -y`.
  have hnegYeq : secp256k1.toAffine.negY ((Secp256k1.beta : ZMod Secp256k1.p) * x₂) y₂
      = secp256k1.toAffine.negY x₂ y₂ := by
    simp [WeierstrassCurve.Affine.negY, secp256k1]
  -- `β·x₁ = β·x₂` from `x₁ = x₂`.
  have hxβ : (Secp256k1.beta : ZMod Secp256k1.p) * x₁
      = (Secp256k1.beta : ZMod Secp256k1.p) * x₂ := by rw [hx]
  -- The tangent-branch side condition transfers (negY independent of `x`).
  have hyβ : y₁ ≠ secp256k1.toAffine.negY
      ((Secp256k1.beta : ZMod Secp256k1.p) * x₂) y₂ := by
    rw [hnegYeq]; exact hy
  -- Unfold both tangent slopes.
  rw [slope_of_Y_ne hxβ hyβ, slope_of_Y_ne hx hy]
  -- Reduce `negY` and the vanishing `a`-coefficients, then close by field arithmetic.
  simp only [WeierstrassCurve.Affine.negY, secp256k1,
    mul_zero, zero_mul, add_zero, sub_zero, zero_add]
  ring

end Ecdlp.Curve
