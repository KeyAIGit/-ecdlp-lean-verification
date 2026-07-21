/-
# Secant `x`-coordinate cleared identity for secp256k1 (N7-uniform odd-step geometry brick)

The group-law secant `x`-coordinate `addX X₁ X₂ ℓ = ℓ² − X₁ − X₂` (secp256k1 has `a₁=a₂=0`),
cleared by `(X₁−X₂)²` against the two curve equations and the secant slope relation
`ℓ·(X₁−X₂) = Y₁−Y₂`, is

  `addX X₁ X₂ ℓ · (X₁−X₂)² = X₁³ + X₂³ + 14 − 2·Y₁Y₂ − (X₁+X₂)(X₁−X₂)²`.

This exposes the cross term **`Y₁Y₂`** — the one quantity the abstract `odd_x_algebra` wall of the
open N7-uniform carrier (`Ecdlp/Targets/n7_uniform_carrier_induction.lean`) leaves sign-ambiguous.
For a genuine pair of consecutive multiples `kP, (k+1)P` the `Carrier` y-coupling pins `Y₁Y₂` via
the `ψ` products, so this identity is the geometry half of that wall's closure (the arithmetic half
is `φ_ψ_diff_evalEval`). Pure `linear_combination` over `h₁, h₂` (curve equations) and `hℓ` (slope);
no `native_decide`, no new axioms.
-/
import Mathlib
import Ecdlp.Proved.Secp256k1Curve

namespace Ecdlp.Curve

/-- **Secant `addX` cleared by `(X₁−X₂)²` for secp256k1 `y²=x³+7`.** With a secant slope `ℓ`
(`ℓ·(X₁−X₂) = Y₁−Y₂`) and both endpoints on the curve, the group-law `addX` satisfies
`addX X₁ X₂ ℓ · (X₁−X₂)² = X₁³ + X₂³ + 14 − 2·Y₁·Y₂ − (X₁+X₂)(X₁−X₂)²`. Exposes the `Y₁Y₂` cross
term pinned by the N7-uniform `Carrier` y-coupling. -/
theorem secp256k1_secant_addX_cleared (X₁ X₂ Y₁ Y₂ ℓ : ZMod Secp256k1.p)
    (hℓ : ℓ * (X₁ - X₂) = Y₁ - Y₂)
    (h₁ : Y₁ ^ 2 = X₁ ^ 3 + 7) (h₂ : Y₂ ^ 2 = X₂ ^ 3 + 7) :
    secp256k1.toAffine.addX X₁ X₂ ℓ * (X₁ - X₂) ^ 2
      = X₁ ^ 3 + X₂ ^ 3 + 14 - 2 * Y₁ * Y₂ - (X₁ + X₂) * (X₁ - X₂) ^ 2 := by
  simp only [WeierstrassCurve.Affine.addX, secp256k1]
  linear_combination h₁ + h₂ + (ℓ * (X₁ - X₂) + (Y₁ - Y₂)) * hℓ

end Ecdlp.Curve
