import Mathlib

/-!
# Rational-character degree barrier: arithmetic core

This file formalizes only the elementary real-arithmetic implication used by
`RATIONAL-CHARACTER-DEGREE-BARRIER-033`.

The analytic premises are external to this file:

* the exact heavy Fourier coefficient of the scalar GLV carry;
* the Kummer-covering character-sum estimate
  `|sum omega(P) * chi(f(P))| <= 2 * degree(f) * sqrt(p)`;
* the bridge from an exact public decoder to the twisted sum.

No elliptic curves, rational functions, characters, trigonometry or
secp256k1 constants are formalized here.
-/

namespace Ecdlp.ParityLift

/-- Rearrangement of the twisted-character upper bound into a degree lower
bound. The variable `rootP` stands for `sqrt(p)` and is assumed positive. -/
theorem rationalCharacter_degree_lower_bound
    (n coefficient degree rootP : ℝ)
    (hroot : 0 < rootP)
    (hbound : n * coefficient ≤ 2 * degree * rootP + 1) :
    (n * coefficient - 1) / (2 * rootP) ≤ degree := by
  apply (div_le_iff₀ (mul_pos (by norm_num) hroot)).2
  nlinarith

/-- A public lower bound on the Fourier coefficient may be substituted before
rearranging the character-sum inequality. -/
theorem rationalCharacter_degree_lower_bound_of_heavy
    (n coefficient heavy degree rootP : ℝ)
    (hn : 0 ≤ n)
    (hroot : 0 < rootP)
    (hheavy : heavy ≤ coefficient)
    (hbound : n * coefficient ≤ 2 * degree * rootP + 1) :
    (n * heavy - 1) / (2 * rootP) ≤ degree := by
  have hscaled : n * heavy ≤ n * coefficient :=
    mul_le_mul_of_nonneg_left hheavy hn
  apply (div_le_iff₀ (mul_pos (by norm_num) hroot)).2
  nlinarith

/-- If a quotient-coordinate rational map of degree `r` produces an elliptic
function of degree at most `6*r+3`, every lower bound on the elliptic function
transfers to that quotient degree. -/
theorem quotientDegree_transfer
    (lower ellipticDegree quotientDegree : ℝ)
    (hlower : lower ≤ ellipticDegree)
    (hupper : ellipticDegree ≤ 6 * quotientDegree + 3) :
    (lower - 3) / 6 ≤ quotientDegree := by
  linarith

end Ecdlp.ParityLift
