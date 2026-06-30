import Mathlib
import Ecdlp.Proved.GlvSlope
import Ecdlp.Proved.GlvSlopeTangent

/-!
# GLV slope-scaling identity (all branches)

Assembles the secant branch (`secp256k1_glv_slope_of_X_ne`) and the tangent branch
(`secp256k1_glv_slope_of_Y_ne`) with the remaining vertical branch into a single
**unconditional** statement: for *any* `x₁, x₂, y₁, y₂`, the secp256k1 GLV map
`x ↦ β·x` scales the addition slope by exactly `β²`.

This is the scalar identity that drives the whole homomorphism: Mathlib's affine
addition computes `P + Q` from the single slope `ℓ`, and `β²·ℓ` is what makes
`(x, y) ↦ (β·x, y)` respect `addX`/`addY` (see `notes/GLV_HOMOMORPHISM.md`). The
vertical branch (`y₁ = negY x₂ y₂`) is the degenerate case where both slopes are `0`,
so the identity holds as `0 = β²·0`.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

/-- **GLV slope scaling (all branches).** Applying the secp256k1 GLV endomorphism
`x ↦ β·x` to both `X`-coordinates multiplies the addition slope by `β²`, for every
choice of coordinates — no `x₁ ≠ x₂` or tangent side condition required. Dispatches to
the secant lemma (`secp256k1_glv_slope_of_X_ne`), the tangent lemma
(`secp256k1_glv_slope_of_Y_ne`), or the vertical case (both slopes `0`). -/
theorem secp256k1_glv_slope [Fact (Nat.Prime Secp256k1.p)]
    (x₁ x₂ y₁ y₂ : ZMod Secp256k1.p) :
    secp256k1.toAffine.slope ((Secp256k1.beta : ZMod Secp256k1.p) * x₁)
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₂) y₁ y₂
      = (Secp256k1.beta : ZMod Secp256k1.p) ^ 2
          * secp256k1.toAffine.slope x₁ x₂ y₁ y₂ := by
  by_cases hx : x₁ = x₂
  · by_cases hy : y₁ = secp256k1.toAffine.negY x₂ y₂
    · -- Vertical branch: `y₁ = negY x₂ y₂`, so both slopes are `0`.
      have hnegYeq : secp256k1.toAffine.negY
          ((Secp256k1.beta : ZMod Secp256k1.p) * x₂) y₂
          = secp256k1.toAffine.negY x₂ y₂ := by
        simp [WeierstrassCurve.Affine.negY, secp256k1]
      have hxβ : (Secp256k1.beta : ZMod Secp256k1.p) * x₁
          = (Secp256k1.beta : ZMod Secp256k1.p) * x₂ := by rw [hx]
      have hyβ : y₁ = secp256k1.toAffine.negY
          ((Secp256k1.beta : ZMod Secp256k1.p) * x₂) y₂ := by rw [hnegYeq]; exact hy
      rw [slope_of_Y_eq hxβ hyβ, slope_of_Y_eq hx hy, mul_zero]
    · -- Tangent / doubling branch.
      exact secp256k1_glv_slope_of_Y_ne x₁ x₂ y₁ y₂ hx hy
  · -- Secant branch.
    exact secp256k1_glv_slope_of_X_ne x₁ x₂ y₁ y₂ hx

end Ecdlp.Curve
