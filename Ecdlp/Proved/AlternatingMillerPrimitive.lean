import Mathlib

/-!
# Alternating Miller primitive

This file formalizes integer arithmetic behind
`UORC056-ALTERNATING-MILLER-PRIMITIVE-B8`.

The two-step translation divisor has coefficients

  (M+2)(-G) - (M+1)(-2G) - M(G) + (M-1)(O).

Its total degree and scalar class are zero. The file does not formalize Miller
functions, elliptic curves, divisors, secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- The two parity edge sets partition the `2M` ordinary Miller edges. -/
theorem alternating_complement_edgeCount (M : ℕ) :
    M + M = 2 * M := by
  omega

/-- The compact two-step cocycle divisor has degree zero. -/
theorem twoStepMillerDivisor_degreeZero (M : ℤ) :
    (M + 2) - (M + 1) - M + (M - 1) = 0 := by
  ring

/-- The scalar-weighted point sum of the two-step divisor is zero. Here the
labels of `-G`, `-2G`, and `G` are represented by `-1`, `-2`, and `1`. -/
theorem twoStepMillerDivisor_scalarClassZero (M : ℤ) :
    (M + 2) * (-1) - (M + 1) * (-2) - M = 0 := by
  ring

/-- The correction relating the complementary product to the negated
alternating product has degree zero. -/
theorem involutionCorrection_degreeZero (M : ℤ) :
    (M + 1) - M - 1 = 0 := by
  ring

end Ecdlp.ParityLift
