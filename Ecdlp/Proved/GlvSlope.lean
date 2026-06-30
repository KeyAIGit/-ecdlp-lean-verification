import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# GLV slope-scaling identity (secant branch)

The secp256k1 GLV endomorphism acts on affine points by `(x, y) ↦ (β·x, y)`, where
`β` is the cube root of unity in `𝔽_p` (`β² + β + 1 = 0`, equivalently `β³ = 1`;
`Secp256k1.beta`). This lemma records how that map scales the *secant slope* between
two points with distinct `X`-coordinates: replacing `x₁, x₂` by `β·x₁, β·x₂` (and
keeping `y₁, y₂`) multiplies the slope by `β²`.

Algebraically, `slope = (y₁ - y₂)/(x₁ - x₂)`, so the new slope is
`(y₁ - y₂)/(β·x₁ - β·x₂) = β⁻¹·(y₁ - y₂)/(x₁ - x₂)`, and `β⁻¹ = β²` because `β³ = 1`.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

/-- **GLV slope scaling, secant branch.** For two points with `x₁ ≠ x₂`, applying the
GLV endomorphism `x ↦ β·x` to the `X`-coordinates multiplies the secant slope by `β²`.

NOTE on the statement: `slope` lives in the `WeierstrassCurve.Affine` namespace, so it
is accessed through `secp256k1.toAffine.slope` (Lean's dot notation resolves through the
`toAffine` coercion, exactly as every other `Affine`-namespace predicate is used across
this repository, e.g. `secp256k1.toAffine.Equation` / `.Nonsingular`). `toAffine` is the
reducible identity `W ↦ W`, so this is the intended statement; `secp256k1.slope` alone
does not elaborate because `WeierstrassCurve.slope` does not exist. -/
theorem secp256k1_glv_slope_of_X_ne [Fact (Nat.Prime Secp256k1.p)]
    (x₁ x₂ y₁ y₂ : ZMod Secp256k1.p) (hx : x₁ ≠ x₂) :
    secp256k1.toAffine.slope ((Secp256k1.beta : ZMod Secp256k1.p) * x₁)
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₂) y₁ y₂
      = (Secp256k1.beta : ZMod Secp256k1.p) ^ 2
          * secp256k1.toAffine.slope x₁ x₂ y₁ y₂ := by
  -- β-facts (verbatim pattern from `Ecdlp/Proved/GlvEndomorphism.lean`).
  have hβeig : (Secp256k1.beta : ZMod Secp256k1.p) ^ 2
      + (Secp256k1.beta : ZMod Secp256k1.p) + 1 = 0 := by
    have h0 : ((Secp256k1.beta ^ 2 + Secp256k1.beta + 1 : ℕ) : ZMod Secp256k1.p) = 0 := by
      rw [ZMod.natCast_eq_zero_iff]
      exact Nat.dvd_of_mod_eq_zero Secp256k1.beta_field_eigenvalue
    push_cast at h0
    linear_combination h0
  have hβ3 : (Secp256k1.beta : ZMod Secp256k1.p) ^ 3 = 1 := by
    linear_combination ((Secp256k1.beta : ZMod Secp256k1.p) - 1) * hβeig
  have hβ0 : (Secp256k1.beta : ZMod Secp256k1.p) ≠ 0 := by
    intro hb; rw [hb] at hβeig; norm_num at hβeig
  -- `β·x₁ ≠ β·x₂` from `x₁ ≠ x₂` by left-cancelling the nonzero `β`.
  have hxβ : (Secp256k1.beta : ZMod Secp256k1.p) * x₁
      ≠ (Secp256k1.beta : ZMod Secp256k1.p) * x₂ :=
    fun h => hx (mul_left_cancel₀ hβ0 h)
  -- Unfold both secant slopes.
  rw [slope_of_X_ne hxβ, slope_of_X_ne hx]
  -- Goal: (y₁ - y₂)/(β·x₁ - β·x₂) = β² * ((y₁ - y₂)/(x₁ - x₂)).
  -- Nonzero denominators.
  have hd1 : (Secp256k1.beta : ZMod Secp256k1.p) * x₁
      - (Secp256k1.beta : ZMod Secp256k1.p) * x₂ ≠ 0 := sub_ne_zero.mpr hxβ
  have hd2 : x₁ - x₂ ≠ 0 := sub_ne_zero.mpr hx
  -- Put the RHS as a single fraction, then cross-multiply (fixed orientation `a*d = c*b`).
  rw [mul_div_assoc', div_eq_div_iff hd1 hd2]
  -- Goal: (y₁ - y₂)*(x₁ - x₂) = β²*(y₁ - y₂)*(β·x₁ - β·x₂).
  -- Residual is (1 - β³)*(y₁ - y₂)*(x₁ - x₂); close with hβ3.
  linear_combination (-((y₁ - y₂) * (x₁ - x₂))) * hβ3

end Ecdlp.Curve
