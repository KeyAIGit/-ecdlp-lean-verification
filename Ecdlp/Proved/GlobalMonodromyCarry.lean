import Mathlib
import Ecdlp.Secp256k1Verified
import Ecdlp.Proved.GlvNormalizationRigidity
import Ecdlp.Proved.GlobalMonodromyBoundary

/-!
# Global monodromy carry boundary

This file records the theorem-only arithmetic core of the cyclotomic carry
identity in `GLOBAL-MONODROMY-SECTION-009`.

The analytic package constructs, on the cyclotomic cover, the phase

`M(k) = ∏_{j=0}^2 (1 - ζ_n^(λ^j k))`.

For canonical representatives `k₀,k₁,k₂` with
`k₀+k₁+k₂=γ*n`, `γ ∈ {1,2}`, the half-angle factorization gives

`M(k) = 8*i*(-1)^γ*∏ sin(π*k_j/n)`.

Thus the sign of the imaginary part is exactly the GLV carry. Lean below
formalizes the integer parity, sign complement, dependent-pairing, odd-order
binary-character, anti-conjugate descent, and standard theta-degree boundaries.
It does not formalize complex positivity, Weil pairings, theta groups, or a
public carry oracle.
-/

namespace Ecdlp.ParityLift

/-- The half-angle exponent has the parity of the canonical GLV carry. -/
theorem cyclotomicHalfAngleCarryParity
    (n k₀ k₁ k₂ γ : ℤ)
    (hn : Even (n - 1))
    (hsum : k₀ + k₁ + k₂ = γ * n) :
    Even (k₀ + k₁ + k₂ - γ) :=
  glvOrbitLinearCarryParity n k₀ k₁ k₂ γ hn hsum

/-- Complementary canonical lifts have opposite binary carry signs. -/
theorem complementaryCarry_difference_odd
    (γ γneg : ℤ) (hsum : γ + γneg = 3) :
    ¬ Even (γneg - γ) := by
  intro h
  rcases h with ⟨r, hr⟩
  omega

/-- A multiplicative binary phase cannot be a nontrivial character of an odd
cyclic group. If its order divides both `2` and `2*m+1`, it is the identity. -/
theorem oddOrderBinaryPairingPhase_trivial
    {K : Type*} [CommGroup K]
    (u : K) (m : ℕ)
    (h₂ : u ^ 2 = 1)
    (hodd : u ^ (2 * m + 1) = 1) :
    u = 1 := by
  calc
    u = (u ^ 2) ^ m * u := by simp [h₂]
    _ = u ^ (2 * m + 1) := by
      rw [pow_mul, pow_add, pow_one]
    _ = 1 := hodd

/-- An alternating bilinear pairing is trivial when its second input is a
known scalar multiple of the first. This is the abstract obstruction behind
`e_n(Q, φ(Q)) = 1` when `φ(Q) = [λ]Q`. -/
theorem dependentPairing_trivial
    {A K : Type*} [AddCommMonoid A] [CommMonoid K]
    (pairing : A → A → K)
    (hsmul : ∀ (P R : A) (m : ℕ), pairing P (m • R) = pairing P R ^ m)
    (halt : ∀ P : A, pairing P P = 1)
    (P : A) (m : ℕ) :
    pairing P (m • P) = 1 := by
  rw [hsmul, halt, one_pow]

/-- Pairing an anti-conjugate element with its conjugate loses the sign. -/
theorem antiConjugatePairNorm_signInvariant
    {R : Type*} [CommRing R] (x : R) :
    x * (-x) = (-x) * (-(-x)) := by
  ring

/-- The trace of an anti-conjugate pair vanishes. -/
theorem antiConjugateTracePair_zero
    {R : Type*} [AddCommGroup R] (x : R) :
    x + (-x) = 0 := by
  simp

/-- Conditional standard-theta dimension boundary: if an order-`n`
translation stabilizes a positive-degree line bundle whose degree is `d`, and
the geometric theta-group argument supplies `n ∣ d`, then `d ≥ n`. -/
theorem standardThetaDegree_atLeastOrder
    (n d : ℕ) (hd : 0 < d) (hdiv : n ∣ d) :
    n ≤ d :=
  Nat.le_of_dvd hd hdiv

/-- The exact monodromy embedding degree already exceeds `2^253`. -/
theorem secp256k1MonodromyEmbeddingDegree_gt_twoPow253 :
    2 ^ 253 < secp256k1MonodromyEmbeddingDegree := by
  native_decide

end Ecdlp.ParityLift
