import Mathlib
import Ecdlp.Proved.SquareClassCircuitFrontier

/-!
# Additive square-class conductor frontier

This file formalizes the elementary algebraic core of
`ADDITIVE-SQUARE-CLASS-CONDUCTOR-039`.

An addition factors as one new square-class innovation, while repeated
squaring builds the explicit one-subtraction family `x^(2^m)-x` with only a
linear number of arithmetic gates.

The file does not formalize elliptic curves, valuations, divisors, conductor,
Riemann-Hurwitz, separability, secp256k1 polynomial gcds, carry correctness, or
arithmetic-circuit lower bounds.
-/

namespace Ecdlp.ParityLift

/-- An addition gate consists of the left square class and one innovation
`1 + b/a`. -/
theorem addition_as_single_innovation
    {K : Type*} [Field K]
    (a b : K)
    (ha : a ≠ 0) :
    a + b = a * (1 + b / a) := by
  field_simp [ha]

/-- The same factorization expressed through the repository's explicit
square-equivalence relation. -/
theorem addition_squareEquivalent_innovation
    {K : Type*} [Field K]
    (a b : K)
    (ha : a ≠ 0) :
    SquareEquivalent (a + b) (a * (1 + b / a)) := by
  rw [addition_as_single_innovation a b ha]
  exact squareEquivalent_refl _

/-- The value produced after repeatedly squaring the same input. -/
def squareTower {K : Type*} [Monoid K] (x : K) : ℕ → K
  | 0 => x
  | m + 1 => squareTower x m * squareTower x m

@[simp]
theorem squareTower_zero
    {K : Type*} [Monoid K]
    (x : K) :
    squareTower x 0 = x := rfl

@[simp]
theorem squareTower_succ
    {K : Type*} [Monoid K]
    (x : K) (m : ℕ) :
    squareTower x (m + 1) = squareTower x m * squareTower x m := rfl

/-- `m` squarings produce the exponent `2^m`. -/
theorem squareTower_eq_pow_two
    {K : Type*} [Monoid K]
    (x : K) (m : ℕ) :
    squareTower x m = x ^ (2 ^ m) := by
  induction m with
  | zero => simp [squareTower]
  | succ m ih =>
      rw [squareTower_succ, ih]
      rw [pow_succ, pow_mul]
      simp [pow_two]

/-- The uniform counterfamily uses one subtraction after the squaring tower. -/
def oneAdditionTower
    {K : Type*} [Ring K]
    (x : K) (m : ℕ) : K :=
  squareTower x m - x

/-- Exact algebraic form of the one-addition counterfamily. -/
theorem oneAdditionTower_eq
    {K : Type*} [Ring K]
    (x : K) (m : ℕ) :
    oneAdditionTower x m = x ^ (2 ^ m) - x := by
  rw [oneAdditionTower, squareTower_eq_pow_two]

end Ecdlp.ParityLift
