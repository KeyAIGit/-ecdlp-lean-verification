import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# secp256k1 as a Mathlib elliptic curve

Defines secp256k1 (`Y² = X³ + 7` over `𝔽_p`) as a `WeierstrassCurve` and proves it
is an `EllipticCurve` (its discriminant `Δ = -21168` is a unit in `𝔽_p`). This
grounds the curve in Mathlib's formalized group law on rational points: every
result Mathlib proves about elliptic-curve point groups now applies to secp256k1.
-/

namespace Ecdlp.Curve

/-- secp256k1 as a short Weierstrass curve `Y² = X³ + 7` over `𝔽_p`. -/
def secp256k1 : WeierstrassCurve (ZMod Secp256k1.p) where
  a₁ := 0
  a₂ := 0
  a₃ := 0
  a₄ := 0
  a₆ := 7

/-- The secp256k1 discriminant is nonzero in `𝔽_p` (`Δ = -21168`, machine-checked). -/
theorem secp256k1_Δ_ne_zero : secp256k1.Δ ≠ 0 := by native_decide

/-- secp256k1 is a genuine elliptic curve: its discriminant is a unit in `𝔽_p`.
This makes Mathlib's group law on `secp256k1.toAffine.Point` available for it. -/
instance : secp256k1.IsElliptic :=
  ⟨isUnit_iff_ne_zero.mpr secp256k1_Δ_ne_zero⟩

end Ecdlp.Curve
