import Mathlib

/-!
# Compact cocycle and Hilbert-90 boundary

This file formalizes only elementary algebraic statements used by
`UNIFORM-ORIENTED-ROOT-CIRCUIT-056`, Track B13.

It does not formalize elliptic curves, divisors, Miller functions, quotient
function fields, cyclic Galois extensions, secp256k1, parity, or ECDLP.
-/

namespace Ecdlp.ParityLift

open scoped BigOperators

/-- The integer identity behind `N(-T)=-G` when `N=(n+1)/2` and `T=2G`. -/
theorem halfPlusOne_double (m : ℤ) :
    2 * (m + 1) = (2 * m + 1) + 1 := by
  ring

/-- A finite product of consecutive multiplicative coboundaries telescopes. -/
theorem telescopingDivProduct
    {K : Type*} [CommGroup K] (a : ℕ → K) (m : ℕ) :
    (Finset.range m).prod (fun i => a (i + 1) / a i) = a m / a 0 := by
  induction m with
  | zero => simp
  | succ m ih =>
      rw [Finset.prod_range_succ, ih]
      simpa [Nat.add_comm, div_eq_mul_inv, mul_comm, mul_left_comm, mul_assoc]

/-- A cyclic multiplicative coboundary has norm one. -/
theorem cyclicCoboundaryNorm
    {K : Type*} [CommGroup K] (a : ℕ → K) (n : ℕ)
    (hcycle : a n = a 0) :
    (Finset.range n).prod (fun i => a (i + 1) / a i) = 1 := by
  rw [telescopingDivProduct, hcycle]
  simp

/-- The reciprocal local relation used by the explicit Hilbert-90 lift. -/
theorem hilbert90ReciprocalStep
    {K : Type*} [Field K] (trace f₀ f₁ : K)
    (hf₀ : f₀ ≠ 0) (hf₁ : f₁ ≠ 0) :
    trace / f₁ = (trace / f₀) / (f₁ / f₀) := by
  field_simp

/-- The standard explicit cyclic lift is indexed by exactly `n` terms. -/
theorem standardHilbert90IndexCardinality (n : ℕ) :
    (Finset.range n).card = n := by
  simp

end Ecdlp.ParityLift
