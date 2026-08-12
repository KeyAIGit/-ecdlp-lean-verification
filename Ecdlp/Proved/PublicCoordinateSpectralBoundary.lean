import Mathlib

/-!
# Arithmetic core of the public coordinate spectral boundary

This file records the exact integer identities used by
`PUBLIC-COORDINATE-SPECTRAL-BARRIER-014`.

For nonzero field representatives `x₀`, `x₁`, `x₂` in a GLV orbit,

`x₀ + x₁ + x₂ = γ * p`, with `γ ∈ {1, 2}`.

The public field carry sign is `2*γ - 3`.  The same sign is obtained by
adding the three centered-sawtooth numerators `2*xᵢ - p`.

Lean does not formalize the analytic Fourier-L1 estimate or the external
elliptic Gaussian-sum theorem in this file.
-/

namespace Ecdlp.ParityLift

/-- The canonical field-orbit sum has signed numerator `(2*γ-3)*p`. -/
theorem fieldGlvCarry_numerator
    (p x₀ x₁ x₂ γ : ℤ)
    (hsum : x₀ + x₁ + x₂ = γ * p) :
    2 * (x₀ + x₁ + x₂) - 3 * p = (2 * γ - 3) * p := by
  rw [hsum]
  ring

/-- Adding the three centered-sawtooth numerators gives the field carry. -/
theorem centeredSawtoothNumerator_sum
    (p x₀ x₁ x₂ γ : ℤ)
    (hsum : x₀ + x₁ + x₂ = γ * p) :
    (2 * x₀ - p) + (2 * x₁ - p) + (2 * x₂ - p) =
      (2 * γ - 3) * p := by
  calc
    (2 * x₀ - p) + (2 * x₁ - p) + (2 * x₂ - p) =
        2 * (x₀ + x₁ + x₂) - 3 * p := by ring
    _ = (2 * γ - 3) * p :=
      fieldGlvCarry_numerator p x₀ x₁ x₂ γ hsum

/-- The only two canonical GLV field carries give signs `-1` and `+1`. -/
theorem fieldGlvCarry_sign_dichotomy
    (γ : ℤ) (hγ : γ = 1 ∨ γ = 2) :
    2 * γ - 3 = -1 ∨ 2 * γ - 3 = 1 := by
  rcases hγ with rfl | rfl <;> norm_num

/-- Complementary canonical lifts have opposite field carry signs. -/
theorem fieldGlvCarry_complement
    (γ γneg : ℤ) (hsum : γ + γneg = 3) :
    2 * γneg - 3 = -(2 * γ - 3) := by
  omega

end Ecdlp.ParityLift
