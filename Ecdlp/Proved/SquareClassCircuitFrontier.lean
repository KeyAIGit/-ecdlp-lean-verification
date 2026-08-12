import Mathlib

/-!
# Square-class circuit frontier

This file formalizes elementary identities behind the square-class audit of
nonlinear carry decoders.

A quadratic-character output depends on a function only modulo squares.  The
lemmas show that multiplication combines square classes, inversion does not
create a new class, even powers are squares, and odd powers differ from the
original value by a square.

The file does not formalize elliptic curves, function-field divisors, addition
gates, quadratic characters, conductor growth, or a circuit lower bound.
-/

namespace Ecdlp.ParityLift

/-- Two values are square-equivalent when one is the other multiplied by an
explicit square. -/
def SquareEquivalent {K : Type*} [CommRing K] (x y : K) : Prop :=
  ∃ u : K, x = y * u ^ 2

/-- Reflexivity of explicit square equivalence. -/
theorem squareEquivalent_refl
    {K : Type*} [CommRing K] (x : K) :
    SquareEquivalent x x := by
  refine ⟨1, ?_⟩
  simp [SquareEquivalent]

/-- Multiplication combines two square-equivalence witnesses. -/
theorem squareEquivalent_mul
    {K : Type*} [CommRing K]
    {a b c d : K}
    (hab : SquareEquivalent a b)
    (hcd : SquareEquivalent c d) :
    SquareEquivalent (a * c) (b * d) := by
  rcases hab with ⟨u, rfl⟩
  rcases hcd with ⟨v, rfl⟩
  refine ⟨u * v, ?_⟩
  ring

/-- Every even power is square-equivalent to one. -/
theorem evenPower_squareEquivalent_one
    {K : Type*} [CommRing K]
    (x : K) (m : ℕ) :
    SquareEquivalent (x ^ (2 * m)) 1 := by
  refine ⟨x ^ m, ?_⟩
  simp [SquareEquivalent, pow_mul]

/-- Every odd power is square-equivalent to the original value. -/
theorem oddPower_squareEquivalent_self
    {K : Type*} [CommRing K]
    (x : K) (m : ℕ) :
    SquareEquivalent (x ^ (2 * m + 1)) x := by
  refine ⟨x ^ m, ?_⟩
  rw [pow_add, pow_one, pow_mul]
  ring

/-- In a field, inversion preserves square class for nonzero values. -/
theorem inverse_squareEquivalent_self
    {K : Type*} [Field K]
    (x : K) (hx : x ≠ 0) :
    SquareEquivalent x⁻¹ x := by
  refine ⟨x⁻¹, ?_⟩
  field_simp

/-- Raising to any odd natural exponent preserves square class. -/
theorem oddExponent_squareEquivalent_self
    {K : Type*} [CommRing K]
    (x : K) (e : ℕ)
    (he : Odd e) :
    SquareEquivalent (x ^ e) x := by
  rcases he with ⟨m, rfl⟩
  simpa [Nat.two_mul] using oddPower_squareEquivalent_self x m

end Ecdlp.ParityLift
