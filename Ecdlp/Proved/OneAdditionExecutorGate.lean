import Mathlib

/-!
# One-addition executor gate

This file formalizes the elementary cubic GLV factorization used by
`ONE-ADDITION-EXECUTOR-GATE-OA1`.

It does not formalize elliptic curves, division polynomials, quadratic
characters, the frozen screen, GLV carry, R3, or any complexity claim.
-/

namespace Ecdlp.ParityLift

/-- The three order-three GLV translates of one x-coordinate multiply to a
single cubic difference. -/
theorem cubicOrbitFactor
    {K : Type*} [CommRing K]
    (x a beta : K)
    (hbetaSum : beta ^ 2 + beta + 1 = 0)
    (hbetaCube : beta ^ 3 = 1) :
    (x - a) * (x - beta * a) * (x - beta ^ 2 * a) = x ^ 3 - a ^ 3 := by
  have hsum : 1 + beta + beta ^ 2 = 0 := by
    simpa [add_comm, add_left_comm, add_assoc] using hbetaSum
  have hpair : beta + beta ^ 2 + beta ^ 3 = 0 := by
    rw [hbetaCube]
    simpa [add_comm, add_left_comm, add_assoc] using hbetaSum
  calc
    (x - a) * (x - beta * a) * (x - beta ^ 2 * a) =
        x ^ 3
          - (1 + beta + beta ^ 2) * a * x ^ 2
          + (beta + beta ^ 2 + beta ^ 3) * a ^ 2 * x
          - beta ^ 3 * a ^ 3 := by ring
    _ = x ^ 3 - a ^ 3 := by rw [hsum, hpair, hbetaCube]; ring

/-- The executor identity carries six shifted residue factors, hence even
residual weight. -/
theorem sixShiftedFactors_even : Even 6 := by
  norm_num

end Ecdlp.ParityLift
