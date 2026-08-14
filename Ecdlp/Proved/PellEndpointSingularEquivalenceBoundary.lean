import Mathlib

/-!
# Pell endpoint singular equivalence boundary

Elementary algebra for the B20 package of
`UNIFORM-ORIENTED-ROOT-CIRCUIT-056`.

For a Pell pair `A ± yB`, the selector relation `-yB/A = ±1` forces exactly
one conjugate factor to vanish. The exceptional common-root pair is the only
place where both conjugates can vanish simultaneously.

This file does not formalize elliptic curves, endpoint products, divisors,
secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- On the `+1` selector branch, `yB=-A`, so the plus factor vanishes. -/
theorem pellPlus_zero_of_evenRelation
    {R : Type*} [CommRing R] (A y B : R)
    (h : y * B = -A) :
    A + y * B = 0 := by
  rw [h]
  ring

/-- On the `+1` selector branch, the conjugate factor is `2A`. -/
theorem pellMinus_eq_two_mul_of_evenRelation
    {R : Type*} [CommRing R] (A y B : R)
    (h : y * B = -A) :
    A - y * B = 2 * A := by
  rw [h]
  ring

/-- On the `-1` selector branch, `yB=A`, so the minus factor vanishes. -/
theorem pellMinus_zero_of_oddRelation
    {R : Type*} [CommRing R] (A y B : R)
    (h : y * B = A) :
    A - y * B = 0 := by
  rw [h]
  ring

/-- On the `-1` selector branch, the plus factor is `2A`. -/
theorem pellPlus_eq_two_mul_of_oddRelation
    {R : Type*} [CommRing R] (A y B : R)
    (h : y * B = A) :
    A + y * B = 2 * A := by
  rw [h]
  ring

/-- In odd characteristic, away from a common root `A=0`, the two Pell
conjugates cannot vanish simultaneously on either selector branch. -/
theorem pellConjugates_not_both_zero_of_evenRelation
    {K : Type*} [Field K] (A y B : K)
    (hA : A ≠ 0) (htwo : (2 : K) ≠ 0)
    (h : y * B = -A) :
    A + y * B = 0 ∧ A - y * B ≠ 0 := by
  constructor
  · exact pellPlus_zero_of_evenRelation A y B h
  · rw [pellMinus_eq_two_mul_of_evenRelation A y B h]
    exact mul_ne_zero htwo hA

/-- Odd-branch analogue. -/
theorem pellConjugates_not_both_zero_of_oddRelation
    {K : Type*} [Field K] (A y B : K)
    (hA : A ≠ 0) (htwo : (2 : K) ≠ 0)
    (h : y * B = A) :
    A - y * B = 0 ∧ A + y * B ≠ 0 := by
  constructor
  · exact pellMinus_zero_of_oddRelation A y B h
  · rw [pellPlus_eq_two_mul_of_oddRelation A y B h]
    exact mul_ne_zero htwo hA

end Ecdlp.ParityLift
