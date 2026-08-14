import Mathlib

/-!
# Polynomial-Pell sign-seed boundary

This file formalizes the elementary quadratic-conjugation algebra behind
`UORC056-POLYNOMIAL-PELL-SIGN-SEED-B17`.

The symmetric norm is unchanged by conjugation, the marked one-point seed
transforms covariantly when the generator/y-coordinate is negated, and the
rational selector changes sign when the conjugate factor is chosen.

The file does not formalize polynomial Pell equations, half-gcd, elliptic
curves, Kummer algebras, secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Quadratic Pell norm is invariant under `A -> -A`. -/
theorem pellNorm_negA
    {R : Type*} [CommRing R] (A B F : R) :
    (-A) ^ 2 - F * B ^ 2 = A ^ 2 - F * B ^ 2 := by
  ring

/-- A marked seed `A = y B` transforms covariantly when both `A` and `y` are
negated. -/
theorem markedSeed_negation
    {R : Type*} [Ring R] (A B y : R)
    (hseed : A = y * B) :
    -A = (-y) * B := by
  simpa [hseed]

/-- The oriented rational selector changes sign under quadratic conjugation. -/
theorem pellSelector_negA
    {K : Type*} [Field K] (A B y : K) (_hA : A ≠ 0) :
    (-y * B) / (-A) = -((-y * B) / A) := by
  simp only [neg_mul, neg_div, div_neg, neg_neg]

end Ecdlp.ParityLift
