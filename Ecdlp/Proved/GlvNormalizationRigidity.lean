import Mathlib

/-!
# Scoped GLV normalization rigidity

This file formalizes the parity algebra behind `GLV-NORMALIZATION-RIGIDITY-008`.
It does not construct an EDS-residue oracle and makes no asymptotic claim.

For the canonical scalar representatives `k₀,k₁,k₂` of an order-three GLV
orbit, one has

`k₀ + k₁ + k₂ = γ n`, with `γ ∈ {1,2}` and odd subgroup order `n`.

Every homogeneous net/theta section in the scoped algebraic category has a
quadratic normalization exponent

`q(k) = a*k^2 + b*k + c`.

Modulo two, the C3-orbit sum of this exponent is

`q(k₀)+q(k₁)+q(k₂) = (a+b)*γ+c`.

Thus the binary GLV carry coefficient is exactly the parity of the section's
quadratic normalization weight `a+b`.  Odd-gauge sections inherit the same carry
as the perfectly periodic point function; even-gauge sections cannot contain an
odd number of EDS-residue factors.
-/

namespace Ecdlp.ParityLift

/-- A convenient polynomial model for the normalization exponent of a
homogeneous net/theta section. -/
def quadraticNormalizationExponent (a b c k : ℤ) : ℤ :=
  a * k ^ 2 + b * k + c

/-- Every integer square has the same parity as the integer itself. -/
theorem square_sub_self_even (z : ℤ) : Even (z ^ 2 - z) := by
  rw [show z ^ 2 - z = z * (z - 1) by ring, Int.even_mul]
  by_cases hz : Even z
  · exact Or.inl hz
  · exact Or.inr ((Int.even_sub_one).2 hz)

/-- The sum of the three square representatives differs from the GLV carry
`γ` by an even integer whenever the subgroup order is odd. -/
theorem glvOrbitSquareCarryParity
    (n k₀ k₁ k₂ γ : ℤ)
    (hn : Even (n - 1))
    (hsum : k₀ + k₁ + k₂ = γ * n) :
    Even (k₀ ^ 2 + k₁ ^ 2 + k₂ ^ 2 - γ) := by
  rcases square_sub_self_even k₀ with ⟨r₀, hr₀⟩
  rcases square_sub_self_even k₁ with ⟨r₁, hr₁⟩
  rcases square_sub_self_even k₂ with ⟨r₂, hr₂⟩
  rcases hn with ⟨rn, hrn⟩
  refine ⟨r₀ + r₁ + r₂ + γ * rn, ?_⟩
  calc
    k₀ ^ 2 + k₁ ^ 2 + k₂ ^ 2 - γ =
        (k₀ ^ 2 - k₀) + (k₁ ^ 2 - k₁) + (k₂ ^ 2 - k₂)
          + γ * (n - 1) := by
            linear_combination hsum
    _ = (r₀ + r₁ + r₂ + γ * rn) + (r₀ + r₁ + r₂ + γ * rn) := by
      rw [hr₀, hr₁, hr₂, hrn]
      ring

/-- The linear GLV-orbit sum differs from `γ` by an even integer. -/
theorem glvOrbitLinearCarryParity
    (n k₀ k₁ k₂ γ : ℤ)
    (hn : Even (n - 1))
    (hsum : k₀ + k₁ + k₂ = γ * n) :
    Even (k₀ + k₁ + k₂ - γ) := by
  rcases hn with ⟨rn, hrn⟩
  refine ⟨γ * rn, ?_⟩
  calc
    k₀ + k₁ + k₂ - γ = γ * (n - 1) := by
      linear_combination hsum
    _ = (γ * rn) + (γ * rn) := by
      rw [hrn]
      ring

/-- **Quadratic orbit rigidity.**  A quadratic normalization exponent has C3
carry coefficient `a+b`; all remaining dependence is an even integer and a
fixed constant `c`. -/
theorem quadraticNormalizationOrbitParity
    (a b c n k₀ k₁ k₂ γ : ℤ)
    (hn : Even (n - 1))
    (hsum : k₀ + k₁ + k₂ = γ * n) :
    Even
      (quadraticNormalizationExponent a b c k₀
        + quadraticNormalizationExponent a b c k₁
        + quadraticNormalizationExponent a b c k₂
        - ((a + b) * γ + c)) := by
  rcases glvOrbitSquareCarryParity n k₀ k₁ k₂ γ hn hsum with ⟨rs, hrs⟩
  rcases glvOrbitLinearCarryParity n k₀ k₁ k₂ γ hn hsum with ⟨rl, hrl⟩
  refine ⟨a * rs + b * rl + c, ?_⟩
  calc
    quadraticNormalizationExponent a b c k₀
        + quadraticNormalizationExponent a b c k₁
        + quadraticNormalizationExponent a b c k₂
        - ((a + b) * γ + c) =
      a * (k₀ ^ 2 + k₁ ^ 2 + k₂ ^ 2 - γ)
        + b * (k₀ + k₁ + k₂ - γ) + 2 * c := by
          simp only [quadraticNormalizationExponent]
          ring
    _ = (a * rs + b * rl + c) + (a * rs + b * rl + c) := by
      rw [hrs, hrl]
      ring

/-- If the carry weight `w` is odd (`w-1` is even), then its multiplier is the
same as the basic carry multiplier, up to a fixed constant. -/
theorem oddCarryWeight_forces_basicCarry
    (w γ c : ℤ) (hw : Even (w - 1)) :
    Even ((w * γ + c) - (γ + c)) := by
  rcases hw with ⟨r, hr⟩
  refine ⟨r * γ, ?_⟩
  calc
    (w * γ + c) - (γ + c) = (w - 1) * γ := by ring
    _ = (r * γ) + (r * γ) := by
      rw [hr]
      ring

/-- If the carry weight is even, its carry contribution is binary-trivial. -/
theorem evenCarryWeight_killsCarry
    (w γ c : ℤ) (hw : Even w) :
    Even ((w * γ + c) - c) := by
  rcases hw with ⟨r, hr⟩
  refine ⟨r * γ, ?_⟩
  calc
    (w * γ + c) - c = w * γ := by ring
    _ = (r * γ) + (r * γ) := by
      rw [hr]
      ring

/-- Fixed affine pullback changes a quadratic weight by `b^2`, which has the
same parity as `b`.  It cannot manufacture a new binary carry class. -/
theorem affinePullbackWeightParity (w b : ℤ) :
    Even (w * b ^ 2 - w * b) := by
  rcases square_sub_self_even b with ⟨r, hr⟩
  refine ⟨w * r, ?_⟩
  calc
    w * b ^ 2 - w * b = w * (b ^ 2 - b) := by ring
    _ = (w * r) + (w * r) := by
      rw [hr]
      ring

/-- Any order-three linearization scalar is already a square.  Consequently a
quadratic character cannot see a separate binary phase coming only from the
GLV eigenvalue. -/
theorem cubeRootLinearization_isSquare
    {K : Type*} [CommRing K] (z : K) (hz : z ^ 3 = 1) : IsSquare z := by
  refine ⟨z ^ 2, ?_⟩
  calc
    z = z * 1 := by ring
    _ = z * z ^ 3 := by rw [hz]
    _ = (z ^ 2) * (z ^ 2) := by ring

end Ecdlp.ParityLift
