import Mathlib

/-!
# Multi-cell net cancellation

This file formalizes the algebraic elimination used by
`MULTI-CELL-NET-CANCELLATION-048`.

Two Ward recurrence cells with a common coefficient may be written abstractly as

  A_r = U * R2 - V_r * M2
  A_s = U * S2 - V_s * M2.

Eliminating `U` from the two cells gives

  A_r * S2 - A_s * R2 = M2 * (V_s * R2 - V_r * S2).

For an elliptic divisibility sequence, the bracket on the right is itself the
Ward product `W(r+s) * W(s-r)`, so the natural two-cell determinant collapses
to one multiplicative EDS monomial.

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

end Ecdlp.ParityLift
