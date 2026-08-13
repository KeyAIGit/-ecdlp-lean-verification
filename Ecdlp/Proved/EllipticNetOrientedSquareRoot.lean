import Mathlib

/-!
# Elliptic-net oriented square-root boundary

This file formalizes the elementary additive identities used by
`ELLIPTIC-NET-ORIENTED-SQUARE-ROOT-047`.

A three-term net recurrence makes the sum of any two recurrence cells equal to
the negative of the third.  The first normalized rank-two determinant is a
specialization: its apparent additive cancellation is exactly one
multiplicative net monomial.

The file does not formalize elliptic nets, division polynomials, coordinate
formulas, matrix pullbacks, character sums, secp256k1, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- In any additive commutative group, two cells of a three-term recurrence
collapse to the negative of the remaining cell. -/
theorem threeTermRecurrence_twoCellCollapse
    {R : Type*} [AddCommGroup R]
    (first second third : R)
    (hrecurrence : first + second + third = 0) :
    first + second = -third := by
  calc
    first + second = first + second + third - third := by abel
    _ = 0 - third := by rw [hrecurrence]
    _ = -third := by simp

/-- The normalized rank-two determinant relation used in package 047. -/
theorem normalizedRankTwoDeterminant_collapse
    {R : Type*} [CommRing R]
    (w02 w21 w20 w12 w22 w1m1 : R)
    (hnet : w22 * w1m1 + w20 * w12 - w02 * w21 = 0) :
    w02 * w21 - w20 * w12 = w22 * w1m1 := by
  have hsum : w22 * w1m1 + w20 * w12 = w02 * w21 :=
    sub_eq_zero.mp hnet
  calc
    w02 * w21 - w20 * w12 =
        (w22 * w1m1 + w20 * w12) - w20 * w12 := by rw [hsum]
    _ = w22 * w1m1 := by ring

/-- A determinant already equal to a product remains in the multiplicative
algebra after applying any multiplicative character. -/
theorem multiplicativeCharacter_ofCollapsedDeterminant
    {R S : Type*} [CommMonoid R] [CommMonoid S]
    (character : R →* S)
    (determinant left right : R)
    (hcollapse : determinant = left * right) :
    character determinant = character left * character right := by
  rw [hcollapse, map_mul]

end Ecdlp.ParityLift
