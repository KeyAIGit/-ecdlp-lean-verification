import Mathlib

/-!
# Cyclic factorial standard boundary

This file formalizes two elementary algebraic facts used by
`UORC056-CYCLIC-FACTORIAL-STANDARD-BOUNDARY-B15`:

* the closed-form nonvanishing gate for the alternating Fourier coefficient;
* the two-level product square-root tradeoff.

It does not formalize q-binomial polynomials, elliptic shifted factorials,
secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- The closed-form alternating Fourier value is nonzero away from `1` and
`-1`. -/
theorem alternatingFourierValue_ne_zero
    {K : Type*} [Field K]
    (z : K) (hone : z ≠ 1) (hminus : z ≠ -1) :
    (z - 1) / (z + 1) ≠ 0 := by
  apply div_ne_zero
  · exact sub_ne_zero.mpr hone
  · intro hzero
    apply hminus
    calc
      z = (z + 1) - 1 := by ring
      _ = -1 := by rw [hzero]; ring

/-- A charged two-level block cover cannot beat the square-root frontier. -/
theorem cyclicFactorial_twoLevel_squareBound
    (length baby giant : ℤ)
    (hcover : length ≤ baby * giant) :
    4 * length ≤ (baby + giant) ^ 2 := by
  nlinarith [sq_nonneg (baby - giant)]

end Ecdlp.ParityLift
