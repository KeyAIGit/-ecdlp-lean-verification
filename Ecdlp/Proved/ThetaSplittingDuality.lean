import Mathlib

/-!
# Theta splitting duality

This file formalizes the elementary algebraic core used by
`THETA-SPLITTING-DUALITY-028`.

If two multiplicative phase normalizations take values in a commutative phase
group, their pointwise ratio is again a multiplicative homomorphism. In a
geometric central extension this ratio is the character relating two
splittings of the same projection.

For an odd cyclic source, a phase which is simultaneously n-torsion and binary
is trivial. For a prime-order source represented by `ZMod p`, every nonzero
character exponent acts injectively, so a nontrivial character is faithful.

The file does not formalize theta groups, central extensions, line bundles,
sigma functions, or the geometric premise that a chosen linearization gives a
multiplicative splitting.
-/

namespace Ecdlp.ParityLift

/-- Pointwise ratio of two multiplicative phase homomorphisms. In a central
phase extension this is the character relating two splittings. -/
def phaseHomRatio
    {G M : Type*} [Group G] [CommGroup M]
    (s₁ s₂ : G →* M) : G →* M where
  toFun q := s₁ q / s₂ q
  map_one' := by simp
  map_mul' x y := by
    simp [div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm]

@[simp]
theorem phaseHomRatio_apply
    {G M : Type*} [Group G] [CommGroup M]
    (s₁ s₂ : G →* M) (q : G) :
    phaseHomRatio s₁ s₂ q = s₁ q / s₂ q := rfl

/-- An element whose order divides both an odd number `2*m+1` and two is
trivial. This is the generator-level obstruction to a nontrivial binary
character of an odd-order cyclic group. -/
theorem oddTorsion_binaryPhase_trivial
    {M : Type*} [Group M]
    (x : M) (m : ℕ)
    (hodd : x ^ (2 * m + 1) = 1)
    (hbinary : x ^ 2 = 1) :
    x = 1 := by
  calc
    x = (x ^ 2) ^ m * x := by simp [hbinary]
    _ = x ^ (2 * m) * x := by rw [pow_mul]
    _ = x ^ (2 * m + 1) := by rw [pow_succ]
    _ = 1 := hodd

/-- A nonzero exponent on a prime-order cyclic group is faithful. Under an
identification of the dual group with `ZMod p`, this says that every nontrivial
character has full prime order rather than a smaller nontrivial image. -/
theorem primeExponentMap_injective
    (p : ℕ) [Fact p.Prime]
    (a : ZMod p) (ha : a ≠ 0) :
    Function.Injective (fun k : ZMod p => a * k) := by
  intro x y hxy
  have h := congrArg (fun z : ZMod p => a⁻¹ * z) hxy
  simpa [mul_assoc, ha] using h

/-- A nonzero character exponent permutes the prime-order scalar labels. -/
theorem primeExponentMap_surjective
    (p : ℕ) [Fact p.Prime]
    (a : ZMod p) (ha : a ≠ 0) :
    Function.Surjective (fun k : ZMod p => a * k) := by
  intro y
  refine ⟨a⁻¹ * y, ?_⟩
  simp [mul_assoc, ha]

end Ecdlp.ParityLift
