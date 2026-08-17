import Mathlib

/-!
# Elliptic Gauss projector

This file formalizes the elementary sign and square identities used by
`ELLIPTIC-GAUSS-PROJECTOR-035`.

A quadratic-character eigenprojector changes by a sign under generator change,
while its square is generator-blind.  Recovering the character requires an
oriented value, not only its invariant square.

The file does not formalize elliptic Gauss sums, modular functions, divisor
degrees, secp256k1 nonvanishing, or complexity.
-/

namespace Ecdlp.ParityLift

/-- A projector scaled by a quadratic character has generator-blind square. -/
theorem quadraticProjector_square_eq_baseSquare
    {K : Type*} [Field K]
    (projected base character : K)
    (hprojected : projected = character * base)
    (hcharacter : character ^ 2 = 1) :
    projected ^ 2 = base ^ 2 := by
  rw [hprojected]
  calc
    (character * base) ^ 2 = character ^ 2 * base ^ 2 := by ring
    _ = base ^ 2 := by rw [hcharacter, one_mul]

/-- Once a nonzero oriented base value is supplied, normalization recovers the
quadratic character. -/
theorem orientedProjectorRatio_recoversCharacter
    {K : Type*} [Field K]
    (projected base character : K)
    (hprojected : projected = character * base)
    (hbase : base ≠ 0) :
    projected / base = character := by
  rw [hprojected]
  field_simp

/-- Opposite orientations have the same square. -/
theorem neg_orientation_sameSquare
    {K : Type*} [Ring K]
    (value : K) :
    (-value) ^ 2 = value ^ 2 := by
  simp [pow_two]

end Ecdlp.ParityLift
