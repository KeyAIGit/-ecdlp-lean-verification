import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# secp256k1 as a Mathlib elliptic curve

Defines secp256k1 (`Y² = X³ + 7` over `𝔽_p`) as a `WeierstrassCurve` and proves it
is an `EllipticCurve` (its discriminant `Δ = -21168` is a unit in `𝔽_p`). This
grounds the curve in Mathlib's formalized group law on rational points: every
result Mathlib proves about elliptic-curve point groups now applies to secp256k1.

The elliptic-curve facts are stated under `[Fact p.Prime]` (the published primality
of the field characteristic, which makes `𝔽_p` a field) — a hypothesis, not an axiom.
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

/-- The `c₄` invariant of secp256k1 vanishes (since `a₁ = a₂ = a₄ = 0`). -/
theorem secp256k1_c₄_eq_zero : secp256k1.c₄ = 0 := by
  simp only [WeierstrassCurve.c₄, WeierstrassCurve.b₂, WeierstrassCurve.b₄, secp256k1]
  ring

variable [Fact (Nat.Prime Secp256k1.p)]

/-- secp256k1 is a genuine elliptic curve: its discriminant is a unit in `𝔽_p`.
This makes Mathlib's group law on `secp256k1.toAffine.Point` available for it. -/
instance : secp256k1.IsElliptic := by
  refine ⟨?_⟩
  rw [isUnit_iff_ne_zero]
  exact secp256k1_Δ_ne_zero

/-- **secp256k1 has j-invariant 0.** Equivalently, it has complex multiplication by
`ℤ[ζ₃]` — it carries an order-3 automorphism. This is the structural reason for the
GLV endomorphism `λ` (whose cube-root eigenvalue relation `λ² + λ + 1 = 0` is proved
in `CubeRoot.lean`): `j = 0` curves are exactly those with that endomorphism. -/
theorem secp256k1_j_eq_zero : secp256k1.j = 0 :=
  secp256k1.j_eq_zero secp256k1_c₄_eq_zero


/-- **The secp256k1 base point lies on the Mathlib elliptic curve.** The SEC2
generator `G = (Gx, Gy)`, cast into `𝔽_p`, satisfies `secp256k1`'s Weierstrass
equation — a genuine rational point of the Mathlib `EllipticCurve`. -/
theorem secp256k1_generator_equation :
    secp256k1.toAffine.Equation
      (Secp256k1.Gx : ZMod Secp256k1.p) (Secp256k1.Gy : ZMod Secp256k1.p) := by
  rw [WeierstrassCurve.Affine.equation_iff]
  have hcast : ((Secp256k1.Gy ^ 2 : ℕ) : ZMod Secp256k1.p)
      = ((Secp256k1.Gx ^ 3 + 7 : ℕ) : ZMod Secp256k1.p) := by
    rw [ZMod.natCast_eq_natCast_iff]
    exact Secp256k1.generator_on_curve
  push_cast at hcast
  simp only [secp256k1]
  linear_combination hcast

end Ecdlp.Curve
