import Mathlib

/-!
# CM ray-class torus orientation

This file formalizes elementary algebraic identities used by
`CM-RAY-CLASS-TORUS-ORIENTATION-040`.

A quadratic character that is trivial on the CM unit subgroup descends through
the unit quotient. A generator-oriented ray-class resolvent scales by the
quadratic character, while its square and every character-balanced trace lose
the orientation.

The file does not formalize ray class groups, Weber functions, Shimura
reciprocity, elliptic units, CM class fields, secp256k1 nonvanishing, divisor
degrees, or arithmetic-circuit complexity.
-/

namespace Ecdlp.ParityLift

/-- Multiplying by a unit on which the character is trivial does not change the
character value, which is the elementary descent through the CM-unit quotient. -/
theorem character_mul_trivialUnit
    {K : Type*} [CommRing K]
    (character scalarCharacter unitCharacter : K)
    (hcharacter : character = scalarCharacter * unitCharacter)
    (hunit : unitCharacter = 1) :
    character = scalarCharacter := by
  rw [hcharacter, hunit, mul_one]

/-- Normalizing a nonzero ray-class eigenresolvent recovers its quadratic
character multiplier. -/
theorem normalizedRayResolvent_recoversCharacter
    {K : Type*} [Field K]
    (projected base character : K)
    (hprojected : projected = character * base)
    (hbase : base ≠ 0) :
    projected / base = character := by
  rw [hprojected]
  field_simp [hbase]

/-- Opposite quadratic orientations have the same invariant square. -/
theorem rayResolvent_square_generatorBlind
    {K : Type*} [CommRing K]
    (projected base character : K)
    (hprojected : projected = character * base)
    (hcharacter : character ^ 2 = 1) :
    projected ^ 2 = base ^ 2 := by
  rw [hprojected, mul_pow, hcharacter, one_mul]

/-- A character-balanced factor removes the generator-relative orientation. -/
theorem balancedRayFactor_isInvariant
    {K : Type*} [Field K]
    (oriented invariant character : K)
    (horiented : oriented = character * invariant)
    (hcharacter : character ≠ 0) :
    oriented / character = invariant := by
  rw [horiented]
  field_simp [hcharacter]

/-- A generator-independent trace remains unchanged under any relabeling whose
only effect is multiplication by the trivial character. -/
theorem invariantRayTrace_unchanged
    {K : Type*} [CommRing K]
    (projected base trivialCharacter : K)
    (hprojected : projected = trivialCharacter * base)
    (htrivial : trivialCharacter = 1) :
    projected = base := by
  rw [hprojected, htrivial, one_mul]

end Ecdlp.ParityLift
