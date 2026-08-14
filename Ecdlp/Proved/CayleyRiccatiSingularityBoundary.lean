import Mathlib

/-!
# Cayley-Riccati singularity boundary

Elementary projective algebra for the B19 package of
`UNIFORM-ORIENTED-ROOT-CIRCUIT-056`.

The projective selector update induced by multiplying the conjugate-factor
ratio is a Möbius/Riccati map. In Cayley coordinates it is merely diagonal
multiplication. Both selector boundary points `+1` and `-1` are fixed by every
regular multiplier, so a branch flip requires a degenerate step.

This file does not formalize elliptic curves, polynomial Pell factors, divisors,
secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Numerator of the Cayley coordinate `z=(1+r)/(1-r)`. -/
def cayleyNumerator {R : Type*} [One R] [Add R] (r : R) : R := 1 + r

/-- Denominator of the Cayley coordinate `z=(1+r)/(1-r)`. -/
def cayleyDenominator {R : Type*} [One R] [Sub R] (r : R) : R := 1 - r

/-- Numerator of the selector after multiplying the Cayley coordinate by `c`. -/
def riccatiNumerator {R : Type*} [Ring R] (c r : R) : R :=
  (c - 1) + (c + 1) * r

/-- Denominator of the selector after multiplying the Cayley coordinate by `c`. -/
def riccatiDenominator {R : Type*} [Ring R] (c r : R) : R :=
  (c + 1) + (c - 1) * r

/-- The inverse-Cayley numerator after diagonal multiplication. -/
theorem cayleyDiagonal_numerator
    {R : Type*} [CommRing R] (c r : R) :
    c * cayleyNumerator r - cayleyDenominator r =
      riccatiNumerator c r := by
  simp only [cayleyNumerator, cayleyDenominator, riccatiNumerator]
  ring

/-- The inverse-Cayley denominator after diagonal multiplication. -/
theorem cayleyDiagonal_denominator
    {R : Type*} [CommRing R] (c r : R) :
    c * cayleyNumerator r + cayleyDenominator r =
      riccatiDenominator c r := by
  simp only [cayleyNumerator, cayleyDenominator, riccatiDenominator]
  ring

/-- The `+1` selector branch is projectively fixed by every regular diagonal
multiplier: numerator and denominator remain equal. -/
theorem riccati_fixed_one
    {R : Type*} [CommRing R] (c : R) :
    riccatiNumerator c 1 = riccatiDenominator c 1 := by
  simp [riccatiNumerator, riccatiDenominator]

/-- The `-1` selector branch is projectively fixed: the updated numerator is the
negative of the updated denominator. -/
theorem riccati_fixed_negOne
    {R : Type*} [CommRing R] (c : R) :
    riccatiNumerator c (-1) = -riccatiDenominator c (-1) := by
  simp [riccatiNumerator, riccatiDenominator]

/-- A finite nonzero multiplier keeps the `+1` pair nonzero in characteristic
not two. -/
theorem riccati_one_pair_nonzero
    {K : Type*} [Field K] (c : K)
    (hc : c ≠ 0) (htwo : (2 : K) ≠ 0) :
    riccatiNumerator c 1 ≠ 0 ∧ riccatiDenominator c 1 ≠ 0 := by
  have hnum : riccatiNumerator c 1 = (2 : K) * c := by
    simp only [riccatiNumerator]
    ring
  have hden : riccatiDenominator c 1 = (2 : K) * c := by
    simp only [riccatiDenominator]
    ring
  constructor
  · rw [hnum]
    exact mul_ne_zero htwo hc
  · rw [hden]
    exact mul_ne_zero htwo hc

/-- The `-1` projective pair is nonzero in characteristic not two. -/
theorem riccati_negOne_pair_nonzero
    {K : Type*} [Field K] (c : K)
    (htwo : (2 : K) ≠ 0) :
    riccatiNumerator c (-1) ≠ 0 ∧
      riccatiDenominator c (-1) ≠ 0 := by
  have hnum : riccatiNumerator c (-1) = -(2 : K) := by
    simp only [riccatiNumerator]
    ring
  have hden : riccatiDenominator c (-1) = (2 : K) := by
    simp only [riccatiDenominator]
    ring
  constructor
  · rw [hnum]
    exact neg_ne_zero.mpr htwo
  · rw [hden]
    exact htwo

end Ecdlp.ParityLift
