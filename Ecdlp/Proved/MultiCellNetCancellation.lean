import Mathlib

/-!
# Multi-cell net cancellation

This file formalizes algebraic eliminations used by
`MULTI-CELL-NET-CANCELLATION-048`.

Write abstract Ward data as

  A(a,b) = V(a) * R(b) - V(b) * R(a).

Then every `A(a,b)` is a 2x2 minor of the two-column vectors `(V(a), R(a))`.
This yields the shared-middle two-cell collapse, vanishing natural 3x3
determinants, and the four-index Grassmann-Pluecker relation.

The file does not formalize elliptic curves, elliptic divisibility sequences,
net polynomials, secp256k1, parity, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Elimination of the common coefficient from two Ward-shaped recurrence cells. -/
theorem twoWardCells_eliminateCommonCoefficient
    {K : Type*} [CommRing K]
    (Ar As U R2 S2 Vr Vs M2 : K)
    (hr : Ar = U * R2 - Vr * M2)
    (hs : As = U * S2 - Vs * M2) :
    Ar * S2 - As * R2 = M2 * (Vs * R2 - Vr * S2) := by
  rw [hr, hs]
  ring

/-- If the remaining cross-difference is itself a known recurrence product,
then the entire two-cell determinant is one multiplicative monomial. -/
theorem twoWardCells_determinantCollapse
    {K : Type*} [CommRing K]
    (Ar As U R2 S2 Vr Vs M2 T : K)
    (hr : Ar = U * R2 - Vr * M2)
    (hs : As = U * S2 - Vs * M2)
    (ht : T = Vs * R2 - Vr * S2) :
    Ar * S2 - As * R2 = M2 * T := by
  rw [hr, hs, ht]
  ring

/-- Adjacent shifts are the specialization where the secondary Ward product is
the odd-index term (up to the normalized factor W(1)=1). -/
theorem adjacentTwoWardCells_collapse
    {K : Type*} [CommRing K]
    (Ar As U R2 S2 Vr Vs M2 OddTerm : K)
    (hr : Ar = U * R2 - Vr * M2)
    (hs : As = U * S2 - Vs * M2)
    (hodd : OddTerm = Vs * R2 - Vr * S2) :
    Ar * S2 - As * R2 = M2 * OddTerm := by
  exact twoWardCells_determinantCollapse Ar As U R2 S2 Vr Vs M2 OddTerm hr hs hodd

/-- Three Ward rows with a common middle coefficient lie in a two-dimensional
column span, so their natural 3x3 determinant vanishes. -/
theorem threeWardRows_rankTwoDeterminant_zero
    {K : Type*} [CommRing K]
    (A1 A2 A3 U R1 R2 R3 V1 V2 V3 M : K)
    (h1 : A1 = U * R1 - V1 * M)
    (h2 : A2 = U * R2 - V2 * M)
    (h3 : A3 = U * R3 - V3 * M) :
    A1 * (R2 * V3 - R3 * V2)
      - R1 * (A2 * V3 - A3 * V2)
      + V1 * (A2 * R3 - A3 * R2) = 0 := by
  rw [h1, h2, h3]
  ring

/-- Four 2x2 Ward minors satisfy the Grassmann-Pluecker relation. -/
theorem wardMinors_pluecker
    {K : Type*} [CommRing K]
    (Pab Pac Pad Pbc Pbd Pcd Va Vb Vc Vd Ra Rb Rc Rd : K)
    (hab : Pab = Va * Rb - Vb * Ra)
    (hac : Pac = Va * Rc - Vc * Ra)
    (had : Pad = Va * Rd - Vd * Ra)
    (hbc : Pbc = Vb * Rc - Vc * Rb)
    (hbd : Pbd = Vb * Rd - Vd * Rb)
    (hcd : Pcd = Vc * Rd - Vd * Rc) :
    Pab * Pcd - Pac * Pbd + Pad * Pbc = 0 := by
  rw [hab, hac, had, hbc, hbd, hcd]
  ring

end Ecdlp.ParityLift
