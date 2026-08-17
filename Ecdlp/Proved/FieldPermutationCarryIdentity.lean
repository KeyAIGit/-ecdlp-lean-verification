import Mathlib

/-!
# Field permutation orientation is a scaled GLV carry

This file records the elementary arithmetic core of
`FIELD-PERMUTATION-CARRY-IDENTITY-017`.

For three distinct canonical representatives `x₀,x₁,x₂`, their positive
directed gaps have total `p` in one cyclic orientation and `2*p` in the reverse
orientation.  Hence the permutation-orientation sign is the negative of the
binary carry sign of the directed-gap orbit.

If `x₁ = β*x₀` and `x₂ = β²*x₀` modulo `p`, the directed differences form the
order-three orbit of `(β-1)*x₀`:

`(β-1)*x, β*(β-1)*x, β²*(β-1)*x`.

Lean proves these order and ring identities.  It does not formalize canonical
residues in a finite field, discrete Fourier transforms, or asymptotic character
sum estimates.
-/

namespace Ecdlp.ParityLift

/-- Positive directed distance from `a` to `b` in canonical representatives
modulo the positive circumference `p`. -/
def directedGap (p a b : ℤ) : ℤ :=
  if a < b then b - a else p + b - a

/-- Sign of the cyclic ordering `(a,b,c)`.  The three listed linear orders are
the positive cyclic permutations; the other three are negative. -/
def fieldPermutationOrientation (a b c : ℤ) : ℤ :=
  if (a < b ∧ b < c) ∨ (b < c ∧ c < a) ∨ (c < a ∧ a < b) then
    1
  else
    -1

/-- The directed-gap total is `p` for positive cyclic orientation and `2*p`
for negative orientation.  The displayed equation packages both cases without
division by `p`. -/
theorem directedGap_cyclicOrientation_identity
    (p a b c : ℤ)
    (_hab : a ≠ b) (_hbc : b ≠ c) (hca : c ≠ a) :
    fieldPermutationOrientation a b c * p =
      3 * p - 2 *
        (directedGap p a b + directedGap p b c + directedGap p c a) := by
  unfold fieldPermutationOrientation directedGap
  by_cases hablt : a < b <;>
    by_cases hbclt : b < c <;>
      by_cases hcalt : c < a <;>
        simp [hablt, hbclt, hcalt] <;> omega

/-- The second directed-difference coefficient is `β` times the first. -/
theorem glvDifferenceOrbit_second
    {R : Type*} [CommRing R] (β x : R) :
    β * ((β - 1) * x) = (β ^ 2 - β) * x := by
  ring

/-- If `β³=1`, the third directed-difference coefficient is `β²` times the
first. -/
theorem glvDifferenceOrbit_third
    {R : Type*} [CommRing R] (β x : R)
    (hβ : β ^ 3 = 1) :
    β ^ 2 * ((β - 1) * x) = (1 - β ^ 2) * x := by
  calc
    β ^ 2 * ((β - 1) * x) = (β ^ 3 - β ^ 2) * x := by ring
    _ = (1 - β ^ 2) * x := by rw [hβ]

/-- The three directed-difference coefficients telescope to zero. -/
theorem glvDifferenceCoefficients_sum_zero
    {R : Type*} [CommRing R] (β x : R) :
    (β - 1) * x + (β ^ 2 - β) * x + (1 - β ^ 2) * x = 0 := by
  ring

/-- Binary carry sign with the convention `-1` at one wrap and `+1` at two
wraps. -/
def fieldBinaryCarrySign (γ : ℤ) : ℤ :=
  2 * γ - 3

/-- Cyclic orientation sign with the convention `+1` at one directed wrap and
`-1` at two directed wraps. -/
def fieldCyclicOrientationSign (γ : ℤ) : ℤ :=
  3 - 2 * γ

/-- The cyclic orientation of the directed-gap orbit is exactly the negative
of its binary carry sign. -/
theorem fieldCyclicOrientation_eq_neg_carry (γ : ℤ) :
    fieldCyclicOrientationSign γ = -fieldBinaryCarrySign γ := by
  simp [fieldCyclicOrientationSign, fieldBinaryCarrySign]

/-- On the two canonical wrap counts, the orientation is genuinely binary. -/
theorem fieldCyclicOrientation_sign_dichotomy
    (γ : ℤ) (hγ : γ = 1 ∨ γ = 2) :
    fieldCyclicOrientationSign γ = 1 ∨
      fieldCyclicOrientationSign γ = -1 := by
  rcases hγ with hγ | hγ
  · subst γ
    exact Or.inl (by norm_num [fieldCyclicOrientationSign])
  · subst γ
    exact Or.inr (by norm_num [fieldCyclicOrientationSign])

end Ecdlp.ParityLift
