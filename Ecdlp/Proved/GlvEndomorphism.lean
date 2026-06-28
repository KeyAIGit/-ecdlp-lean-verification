import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# The GLV endomorphism of secp256k1 — first building block

This file begins constructing a *missing object*: the GLV endomorphism of secp256k1,
the rational self-map `(x, y) ↦ (β·x, y)` where `β ∈ 𝔽_p` is the GLV cube-root factor
(`β² + β + 1 = 0`, equivalently `β³ = 1`; `Secp256k1.beta`). It is the endomorphism that
acts as scalar multiplication by `λ` on the base-point subgroup and powers the GLV
scalar-decomposition speed-up. On the abstract side `Ecdlp.Torsion.zmultiples_le_torsionBy`
and `Ecdlp/Targets/glv_root_mod_n_condition_008.lean` capture "`φ` acts as `[λ]`"; here we
start the concrete object on the actual curve.

**Rung 1 (this file): the map preserves the curve equation** — `(x,y)` on `Y²=X³+7`
implies `(β·x, y)` is too, because `(β·x)³ = β³·x³ = x³`. This is the `Equation` half of
turning `(x,y)↦(β·x,y)` into a genuine `WeierstrassCurve.Affine.Point → Point` map; the
remaining rungs (nonsingularity, then the additive-homomorphism property via the affine
addition formula) are the harder next steps toward the full endomorphism object.
-/

namespace Ecdlp.Curve

/-- **The GLV endomorphism preserves the secp256k1 curve equation.** If `(x, y)` solves
`Y² = X³ + 7`, so does `(β·x, y)`: since `β³ = 1`, `(β·x)³ = β³·x³ = x³`, leaving the
right-hand side unchanged. First step in building the GLV endomorphism as an object on
`secp256k1.toAffine.Point`. -/
theorem secp256k1_glv_preserves_equation
    (x y : ZMod Secp256k1.p)
    (h : secp256k1.toAffine.Equation x y) :
    secp256k1.toAffine.Equation ((Secp256k1.beta : ZMod Secp256k1.p) * x) y := by
  -- β² + β + 1 = 0 in 𝔽_p, lifted from the machine-checked Nat-level eigenvalue fact
  have hβeig : (Secp256k1.beta : ZMod Secp256k1.p) ^ 2
      + (Secp256k1.beta : ZMod Secp256k1.p) + 1 = 0 := by
    have h0 : ((Secp256k1.beta ^ 2 + Secp256k1.beta + 1 : ℕ) : ZMod Secp256k1.p) = 0 := by
      rw [ZMod.natCast_eq_zero_iff]
      exact Nat.dvd_of_mod_eq_zero Secp256k1.beta_field_eigenvalue
    push_cast at h0
    linear_combination h0
  -- hence β³ = 1  (β³ − 1 = (β − 1)(β² + β + 1))
  have hβ3 : (Secp256k1.beta : ZMod Secp256k1.p) ^ 3 = 1 := by
    linear_combination ((Secp256k1.beta : ZMod Secp256k1.p) - 1) * hβeig
  rw [WeierstrassCurve.Affine.equation_iff] at h ⊢
  simp only [secp256k1, zero_mul, mul_zero, add_zero, zero_add, mul_one] at h ⊢
  have hcube : ((Secp256k1.beta : ZMod Secp256k1.p) * x) ^ 3 = x ^ 3 := by
    rw [mul_pow, hβ3, one_mul]
  rw [hcube]
  exact h

end Ecdlp.Curve
