import Mathlib

/-!
# Frobenius-Stickelberger determinant scale cancellation

This file formalizes the elementary four-point quadratic identities used by
`FROBENIUS-STICKELBERGER-DETERMINANT-050`.

For a quadratic exponent q, the Frobenius-Stickelberger sigma product contains

  q(sum_i u_i) + sum_(i<j) q(u_i-u_j) - 4 sum_i q(u_i).

This vanishes.  The file checks the square and bilinear identities and then the
three rank-two preferred-basis exponent forms

  a^2-a*b,  b^2-a*b,  a*b.

It does not formalize sigma functions, the classical determinant theorem,
elliptic curves, elliptic nets, arbitrary numbers of points, secp256k1, parity,
or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Four-point polarization identity for a square quadratic form. -/
theorem fourPoint_squareBalance
    {R : Type*} [CommRing R]
    (a b c d : R) :
    (a + b + c + d) ^ 2
      + (a - b) ^ 2 + (a - c) ^ 2 + (a - d) ^ 2
      + (b - c) ^ 2 + (b - d) ^ 2 + (c - d) ^ 2
      = (4 : R) * (a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2) := by
  ring

/-- Four-point polarization identity for the bilinear monomial `a*b`. -/
theorem fourPoint_bilinearBalance
    {R : Type*} [CommRing R]
    (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : R) :
    (a₁ + a₂ + a₃ + a₄) * (b₁ + b₂ + b₃ + b₄)
      + (a₁ - a₂) * (b₁ - b₂)
      + (a₁ - a₃) * (b₁ - b₃)
      + (a₁ - a₄) * (b₁ - b₄)
      + (a₂ - a₃) * (b₂ - b₃)
      + (a₂ - a₄) * (b₂ - b₄)
      + (a₃ - a₄) * (b₃ - b₄)
      = (4 : R) * (a₁ * b₁ + a₂ * b₂ + a₃ * b₃ + a₄ * b₄) := by
  ring

/-- The exponent of the preferred sigma value at the first marked point. -/
def rankTwoFirstScale
    {R : Type*} [Ring R]
    (a b : R) : R :=
  a ^ 2 - a * b

/-- The exponent of the preferred sigma value at the second marked point. -/
def rankTwoSecondScale
    {R : Type*} [Ring R]
    (a b : R) : R :=
  b ^ 2 - a * b

/-- The exponent of the preferred sigma value at the point sum. -/
def rankTwoMixedScale
    {R : Type*} [Ring R]
    (a b : R) : R :=
  a * b

/-- Four-point cancellation for `a^2-a*b`. -/
theorem fourPoint_rankTwoFirstScaleBalance
    {R : Type*} [CommRing R]
    (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : R) :
    rankTwoFirstScale (a₁ + a₂ + a₃ + a₄) (b₁ + b₂ + b₃ + b₄)
      + rankTwoFirstScale (a₁ - a₂) (b₁ - b₂)
      + rankTwoFirstScale (a₁ - a₃) (b₁ - b₃)
      + rankTwoFirstScale (a₁ - a₄) (b₁ - b₄)
      + rankTwoFirstScale (a₂ - a₃) (b₂ - b₃)
      + rankTwoFirstScale (a₂ - a₄) (b₂ - b₄)
      + rankTwoFirstScale (a₃ - a₄) (b₃ - b₄)
      = (4 : R) *
          (rankTwoFirstScale a₁ b₁ + rankTwoFirstScale a₂ b₂
            + rankTwoFirstScale a₃ b₃ + rankTwoFirstScale a₄ b₄) := by
  simp [rankTwoFirstScale]
  ring

/-- Four-point cancellation for `b^2-a*b`. -/
theorem fourPoint_rankTwoSecondScaleBalance
    {R : Type*} [CommRing R]
    (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : R) :
    rankTwoSecondScale (a₁ + a₂ + a₃ + a₄) (b₁ + b₂ + b₃ + b₄)
      + rankTwoSecondScale (a₁ - a₂) (b₁ - b₂)
      + rankTwoSecondScale (a₁ - a₃) (b₁ - b₃)
      + rankTwoSecondScale (a₁ - a₄) (b₁ - b₄)
      + rankTwoSecondScale (a₂ - a₃) (b₂ - b₃)
      + rankTwoSecondScale (a₂ - a₄) (b₂ - b₄)
      + rankTwoSecondScale (a₃ - a₄) (b₃ - b₄)
      = (4 : R) *
          (rankTwoSecondScale a₁ b₁ + rankTwoSecondScale a₂ b₂
            + rankTwoSecondScale a₃ b₃ + rankTwoSecondScale a₄ b₄) := by
  simp [rankTwoSecondScale]
  ring

/-- Four-point cancellation for the mixed exponent `a*b`. -/
theorem fourPoint_rankTwoMixedScaleBalance
    {R : Type*} [CommRing R]
    (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : R) :
    rankTwoMixedScale (a₁ + a₂ + a₃ + a₄) (b₁ + b₂ + b₃ + b₄)
      + rankTwoMixedScale (a₁ - a₂) (b₁ - b₂)
      + rankTwoMixedScale (a₁ - a₃) (b₁ - b₃)
      + rankTwoMixedScale (a₁ - a₄) (b₁ - b₄)
      + rankTwoMixedScale (a₂ - a₃) (b₂ - b₃)
      + rankTwoMixedScale (a₂ - a₄) (b₂ - b₄)
      + rankTwoMixedScale (a₃ - a₄) (b₃ - b₄)
      = (4 : R) *
          (rankTwoMixedScale a₁ b₁ + rankTwoMixedScale a₂ b₂
            + rankTwoMixedScale a₃ b₃ + rankTwoMixedScale a₄ b₄) := by
  simp [rankTwoMixedScale]
  ring

/-- If the total net factor vanishes, a cross-multiplied determinant
factorization forces the determinant to vanish when its denominator is nonzero. -/
theorem zeroTotalFactor_forcesDeterminantZero
    {K : Type*} [Field K]
    (det denominator constant pairFactor : K)
    (hdenominator : denominator ≠ 0)
    (hfactor : det * denominator = constant * 0 * pairFactor) :
    det = 0 := by
  have hproduct : det * denominator = 0 := by simpa using hfactor
  exact (mul_eq_zero.mp hproduct).resolve_right hdenominator

end Ecdlp.ParityLift
