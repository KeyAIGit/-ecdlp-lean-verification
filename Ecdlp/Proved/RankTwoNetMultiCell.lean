import Mathlib

/-!
# Rank-two net multi-cell determinant boundary

This file formalizes the commutative-ring cancellation used by
`RANK-TWO-NET-MULTI-CELL-049`.

The geometric input consists of:

* three coordinate-difference identities, each cross-multiplied to avoid
  division;
* one matrix-pullback identity for the rank-three net value
  `Omega_(1,1,1)`;
* the statement that the coordinate determinant is `omega` times the three
  coordinate differences.

After substitution, the three-point determinant is one multiplicative net
monomial after cross multiplication.  If the total-index factor vanishes and
the three base net values are nonzero, the determinant vanishes.

The file does not formalize elliptic curves, elliptic nets, net polynomials,
coordinate formulas, secp256k1, parity, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Cross-multiplied form of the rank-two three-point determinant factorization.

The hypotheses abstract the identities

`dAB * Wa^2 * Wb^2 = -Sab * Dab`,

and their two companions, together with

`omega * Sab * Sac * Sbc = Stot * Wa * Wb * Wc`.
-/
theorem rankTwoThreePointDeterminant_crossMultiply
    {K : Type*} [CommRing K]
    (determinant omega dAB dAC dBC : K)
    (Wa Wb Wc Sab Sac Sbc Dab Dac Dbc Stot : K)
    (hdet : determinant = omega * dAB * dAC * dBC)
    (hAB : dAB * Wa ^ 2 * Wb ^ 2 = -Sab * Dab)
    (hAC : dAC * Wa ^ 2 * Wc ^ 2 = -Sac * Dac)
    (hBC : dBC * Wb ^ 2 * Wc ^ 2 = -Sbc * Dbc)
    (homega : omega * Sab * Sac * Sbc = Stot * Wa * Wb * Wc) :
    determinant * Wa ^ 4 * Wb ^ 4 * Wc ^ 4 =
      -(Stot * Wa * Wb * Wc * Dab * Dac * Dbc) := by
  calc
    determinant * Wa ^ 4 * Wb ^ 4 * Wc ^ 4 =
        omega
          * (dAB * Wa ^ 2 * Wb ^ 2)
          * (dAC * Wa ^ 2 * Wc ^ 2)
          * (dBC * Wb ^ 2 * Wc ^ 2) := by
            rw [hdet]
            ring
    _ = omega * (-Sab * Dab) * (-Sac * Dac) * (-Sbc * Dbc) := by
          rw [hAB, hAC, hBC]
    _ = -(omega * Sab * Sac * Sbc) * Dab * Dac * Dbc := by ring
    _ = -(Stot * Wa * Wb * Wc) * Dab * Dac * Dbc := by rw [homega]
    _ = -(Stot * Wa * Wb * Wc * Dab * Dac * Dbc) := by ring

/-- If the total-index net factor vanishes, then the three-point determinant
vanishes on a chart where the three base net values are nonzero. -/
theorem rankTwoThreePointDeterminant_zero_of_totalFactor_zero
    {K : Type*} [Field K]
    (determinant omega dAB dAC dBC : K)
    (Wa Wb Wc Sab Sac Sbc Dab Dac Dbc Stot : K)
    (hWa : Wa ≠ 0)
    (hWb : Wb ≠ 0)
    (hWc : Wc ≠ 0)
    (hdet : determinant = omega * dAB * dAC * dBC)
    (hAB : dAB * Wa ^ 2 * Wb ^ 2 = -Sab * Dab)
    (hAC : dAC * Wa ^ 2 * Wc ^ 2 = -Sac * Dac)
    (hBC : dBC * Wb ^ 2 * Wc ^ 2 = -Sbc * Dbc)
    (homega : omega * Sab * Sac * Sbc = Stot * Wa * Wb * Wc)
    (hStot : Stot = 0) :
    determinant = 0 := by
  have hcross := rankTwoThreePointDeterminant_crossMultiply
    determinant omega dAB dAC dBC
    Wa Wb Wc Sab Sac Sbc Dab Dac Dbc Stot
    hdet hAB hAC hBC homega
  rw [hStot] at hcross
  have hzero : determinant * (Wa ^ 4 * Wb ^ 4 * Wc ^ 4) = 0 := by
    simpa [mul_assoc] using hcross
  have hproduct : Wa ^ 4 * Wb ^ 4 * Wc ^ 4 ≠ 0 := by
    exact mul_ne_zero (mul_ne_zero (pow_ne_zero 4 hWa) (pow_ne_zero 4 hWb))
      (pow_ne_zero 4 hWc)
  exact (mul_eq_zero.mp hzero).resolve_right hproduct

end Ecdlp.ParityLift
