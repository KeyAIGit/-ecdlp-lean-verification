import Mathlib

/-!
# Algebraic core of full dual-character support

For the GLV carry, every nonzero additive Fourier coefficient is proportional
to

`cot A + cot B + cot C`,

where the three positive angles sum to either `π` or `2π`. In the first case
the cotangents satisfy

`x*y + y*z + z*x = 1`.

The complementary-angle transformation reduces the second case to the first
and changes only the sign. This file kernel-checks the purely algebraic
nonvanishing and lower-bound step. It does not formalize trigonometry, finite
Fourier transforms, or the derivation of the cotangent formula.
-/

namespace Ecdlp.ParityLift

/-- If three real numbers have pairwise-product sum one, their sum has squared
magnitude at least three. Applied to cotangents of positive angles summing to
`π`, this gives the uniform nonvanishing bound. -/
theorem threeCotangentCore_sum_sq_ge_three
    (x y z : ℝ)
    (h : x * y + y * z + z * x = 1) :
    3 ≤ (x + y + z) ^ 2 := by
  have hsquares :
      0 ≤ (x - y) ^ 2 + (y - z) ^ 2 + (z - x) ^ 2 := by positivity
  nlinarith

/-- In particular, the cotangent sum cannot vanish. -/
theorem threeCotangentCore_sum_ne_zero
    (x y z : ℝ)
    (h : x * y + y * z + z * x = 1) :
    x + y + z ≠ 0 := by
  intro hzero
  have hbound := threeCotangentCore_sum_sq_ge_three x y z h
  rw [hzero] at hbound
  norm_num at hbound

/-- Passing to complementary angles negates all three cotangents and preserves
nonvanishing. -/
theorem complementaryCotangentCore_sum_ne_zero
    (x y z : ℝ)
    (h : x * y + y * z + z * x = 1) :
    (-x) + (-y) + (-z) ≠ 0 := by
  intro hzero
  apply threeCotangentCore_sum_ne_zero x y z h
  linarith

/-- An exact linear expansion over pairwise distinct characters cannot omit a
character whose unique coefficient is nonzero. This finite-function statement
is the abstract uniqueness step used after the Fourier coefficients are shown
to have full nonzero support. -/
theorem nonzeroCoefficient_cannotBeOmitted
    {ι K : Type*} [Zero K]
    (coefficient : ι → K)
    (used : Set ι)
    (frequency : ι)
    (hnonzero : coefficient frequency ≠ 0)
    (homit : frequency ∉ used) :
    ∃ j, j ∉ used ∧ coefficient j ≠ 0 := by
  exact ⟨frequency, homit, hnonzero⟩

end Ecdlp.ParityLift
