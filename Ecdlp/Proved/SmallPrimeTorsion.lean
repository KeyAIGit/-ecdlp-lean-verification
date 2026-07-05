import Mathlib
import Ecdlp.Proved.SevenTorsionBridge

/-!
# Exact-order small-prime torsion classification for secp256k1

Combines the merged division-polynomial torsion bridges (`n = 2, 3, 5, 7`) with a
reusable order-upgrade lemma to characterize *exact* additive order `ℓ` of an affine
point `P = (x, y)` of secp256k1 as vanishing of the `ℓ`-division polynomial at `P`,
for each prime `ℓ ∈ {2, 3, 5, 7}`.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Order-upgrade lemma.** For a nonzero affine point `P = (x, y)` and a *prime* `ℓ`,
`addOrderOf P = ℓ` iff `ℓ • P = 0`. (The only proper divisor of a prime is `1`, and
`addOrderOf P = 1` would force `P = 0`, contradicting `Point.some_ne_zero`.) -/
theorem addOrderOf_eq_of_prime_nsmul {ℓ : ℕ} (hℓ : ℓ.Prime)
    (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y) :
    addOrderOf (Point.some x y h) = ℓ ↔ (ℓ : ℕ) • Point.some x y h = 0 := by
  rw [← addOrderOf_dvd_iff_nsmul_eq_zero]
  constructor
  · rintro rfl; exact dvd_refl _
  · intro hdvd
    rcases (Nat.dvd_prime hℓ).mp hdvd with h1 | hself
    · exact absurd (AddMonoid.addOrderOf_eq_one_iff.mp h1) (Point.some_ne_zero h)
    · exact hself

/-- **Small-prime exact-order torsion classification for secp256k1.** For an affine
point `P = (x, y)` and each prime `ℓ ∈ {2, 3, 5, 7}`, the additive order of `P` equals
`ℓ` iff the `ℓ`-division polynomial `ψ ℓ` vanishes at `P`. -/
theorem secp256k1_smallprime_addOrderOf
    (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y) :
    (addOrderOf (Point.some x y h) = 2 ↔ (secp256k1.ψ 2).evalEval x y = 0) ∧
    (addOrderOf (Point.some x y h) = 3 ↔ (secp256k1.ψ 3).evalEval x y = 0) ∧
    (addOrderOf (Point.some x y h) = 5 ↔ (secp256k1.ψ 5).evalEval x y = 0) ∧
    (addOrderOf (Point.some x y h) = 7 ↔ (secp256k1.ψ 7).evalEval x y = 0) := by
  have h2ne : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  refine ⟨?_, ?_, ?_, ?_⟩
  · -- ℓ = 2 : `ψ 2 = ψ₂` evaluates to `2y`, and `2 ≠ 0`, so `ψ 2 = 0 ↔ y = 0`.
    rw [addOrderOf_eq_of_prime_nsmul Nat.prime_two, secp256k1_two_nsmul_eq_zero_iff,
        secp256k1.ψ_two, secp256k1_psi2_evalEval]
    constructor
    · intro hy; rw [hy]; ring
    · intro h2y
      rcases mul_eq_zero.mp h2y with hc | hc
      · exact absurd hc h2ne
      · exact hc
  · rw [addOrderOf_eq_of_prime_nsmul (ℓ := 3) (by norm_num),
        secp256k1_three_nsmul_eq_zero_iff]
  · rw [addOrderOf_eq_of_prime_nsmul (ℓ := 5) (by norm_num),
        secp256k1_five_nsmul_eq_zero_iff]
  · rw [addOrderOf_eq_of_prime_nsmul (ℓ := 7) (by norm_num),
        secp256k1_seven_nsmul_eq_zero_iff]

/-- Concrete-polynomial corollary for `ℓ = 3`: exact order 3 iff `3x⁴ + 84x = 0`. -/
theorem secp256k1_addOrderOf_three_iff_poly
    (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y) :
    addOrderOf (Point.some x y h) = 3 ↔ 3 * x ^ 4 + 84 * x = 0 := by
  rw [(secp256k1_smallprime_addOrderOf x y h).2.1, secp256k1_psi3_evalEval]

/-- Concrete-polynomial corollary for `ℓ = 5`: exact order 5 iff the degree-12
5-division polynomial vanishes at `x` (valid on the curve). -/
theorem secp256k1_addOrderOf_five_iff_poly
    (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y) :
    addOrderOf (Point.some x y h) = 5 ↔
      5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656 = 0 := by
  have hcurve : y ^ 2 = x ^ 3 + 7 := by
    have he : secp256k1.toAffine.Equation x y := h.1
    rw [WeierstrassCurve.Affine.equation_iff] at he
    simp only [secp256k1] at he
    linear_combination he
  rw [(secp256k1_smallprime_addOrderOf x y h).2.2.1, secp256k1_psi5_evalEval x y hcurve]

end Ecdlp.Curve
