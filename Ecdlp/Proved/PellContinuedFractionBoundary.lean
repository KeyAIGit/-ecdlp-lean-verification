import Mathlib

/-!
# Pell continued-fraction representation boundary

Elementary degree and representation accounting for the B16 package of
`UNIFORM-ORIENTED-ROOT-CIRCUIT-056`.

This file does not formalize elliptic curves, Riemann-Roch spaces, polynomial
Euclidean algorithms, half-gcd implementations, secp256k1 coordinate circuits,
parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Number of field coefficients in an explicitly materialized list of
polynomial quotients whose degrees are recorded by `degrees`. -/
def quotientCoefficientSlots : List ℕ → ℕ
  | [] => 0
  | degree :: tail => degree + 1 + quotientCoefficientSlots tail

/-- Materializing every quotient uses at least the sum of quotient degrees. -/
theorem quotientDegreeSum_le_coefficientSlots (degrees : List ℕ) :
    degrees.sum ≤ quotientCoefficientSlots degrees := by
  induction degrees with
  | nil => simp [quotientCoefficientSlots]
  | cons degree tail ih =>
      simp only [List.sum_cons, quotientCoefficientSlots]
      omega

/-- Abstract Euclidean degree telescoping. -/
theorem euclideanDegreeSum_eq_reducedDegree
    (initial terminal : ℕ) (degrees : List ℕ)
    (htelescope : initial = terminal + degrees.sum) :
    degrees.sum = initial - terminal := by
  omega

/-- Explicit quotient slots dominate the reduced Euclidean degree. -/
theorem explicitQuotientSlots_ge_reducedDegree
    (initial terminal : ℕ) (degrees : List ℕ)
    (htelescope : initial = terminal + degrees.sum) :
    initial - terminal ≤ quotientCoefficientSlots degrees := by
  rw [← euclideanDegreeSum_eq_reducedDegree initial terminal degrees htelescope]
  exact quotientDegreeSum_le_coefficientSlots degrees

/-- Public secp256k1 subgroup order. -/
def secp256k1OrderForPell : ℕ :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

/-- Quarter parameter `h=(n-1)/4`. -/
def secp256k1PellQuarter : ℕ := (secp256k1OrderForPell - 1) / 4

/-- Reduced-degree lower bound after allowing the one public exceptional common
factor in the declared Pell divisor model. -/
def secp256k1PellReducedDegreeLowerBound : ℕ :=
  secp256k1PellQuarter - 2

/-- The explicit representation lower bound is at least `2^253`. -/
theorem secp256k1_pellReducedDegree_ge_twoPow253 :
    2 ^ 253 ≤ secp256k1PellReducedDegreeLowerBound := by
  native_decide

end Ecdlp.ParityLift
