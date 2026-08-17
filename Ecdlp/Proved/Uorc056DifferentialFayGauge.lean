import Mathlib

/-!
# UORC-056 C51 differential/Fay gauge boundary

This file kernel-checks the elementary integer algebra behind the C51
quasiperiod cancellation.  The analytic sigma/zeta identities, elliptic curves,
division-polynomial recurrences, finite-field replay, and complexity statements
remain outside this Lean file.
-/

namespace Ecdlp.Uorc056DifferentialFayGauge

/-- Coefficient of `H(k)` in the period-shift differential normal form. -/
def firstCoefficient (a b r s n : ℤ) : ℤ :=
  2 * b * s - a * s - r * b + n * (s ^ 2 - r * s)

/-- Coefficient of `H(k+1)` in the period-shift differential normal form. -/
def secondCoefficient (a b r s n : ℤ) : ℤ :=
  a * s + r * b + n * r * s

/-- The coefficient of the naked quasiperiod after rewriting the shifted
    logarithmic derivative in terms of periodic torsion jets. -/
def etaCoefficient (a b r s n k : ℤ) : ℤ :=
  s * (a + b * k)
    - firstCoefficient a b r s n * k
    - secondCoefficient a b r s n * (k + 1)
    + (b + s * n) * (r + s * k)

/-- The quasiperiod coefficient cancels identically for every period shift. -/
theorem etaCoefficient_eq_zero (a b r s n k : ℤ) :
    etaCoefficient a b r s n k = 0 := by
  simp [etaCoefficient, firstCoefficient, secondCoefficient]
  ring

/-- The high-index specialization `(a,b,r,s)=(1,0,0,1)` has coefficients
    `n-1` and `1`. -/
theorem highIndexCoefficients (n : ℤ) :
    firstCoefficient 1 0 0 1 n = n - 1 ∧
      secondCoefficient 1 0 0 1 n = 1 := by
  constructor
  · simp [firstCoefficient]
    ring
  · simp [secondCoefficient]

/-- The same specialization has no residual quasiperiod for any scalar `k`. -/
theorem highIndexEtaCancels (n k : ℤ) :
    etaCoefficient 1 0 0 1 n k = 0 := by
  exact etaCoefficient_eq_zero 1 0 0 1 n k

/-- Coefficients in the public second-logarithmic-derivative formula sum to
    zero, as required for invariance under a common additive coordinate shift. -/
theorem secondDerivativeCoefficientSum (n : ℤ) :
    -(n ^ 2) + (n ^ 2 - n) + n = 0 := by
  ring

/-- The first-order high-index normal form is exactly the declared linear
    combination once the two coefficient identities are substituted. -/
theorem highIndexLinearCombination
    {R : Type*} [CommRing R]
    (n hAnchor hQuery hNext : R) :
    -hAnchor + (n - 1) * hQuery + hNext
      = -(1 : R) * hAnchor
        + (n - 1) * hQuery
        + (1 : R) * hNext := by
  ring

end Ecdlp.Uorc056DifferentialFayGauge
