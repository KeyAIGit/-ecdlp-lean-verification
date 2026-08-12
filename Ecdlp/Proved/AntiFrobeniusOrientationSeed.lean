import Mathlib

/-!
# Anti-Frobenius orientation seed

This file formalizes the elementary algebraic core of
`ANTI-FROBENIUS-ORIENTATION-SEED-031`.

For a field automorphism `sigma`, an anti-invariant element satisfies
`sigma x = -x`. Once a nonzero anti-invariant seed `tau` is fixed, the ratio of
any other anti-invariant element by `tau` is fixed by `sigma`. Conversely,
multiplying `tau` by a fixed element remains anti-invariant. Thus the
anti-invariant line is one-dimensional over the fixed field.

The file does not formalize finite fields, Frobenius, Gaussian periods,
elliptic curves, or the complex sign used to read the GLV carry.
-/

namespace Ecdlp.ParityLift

/-- An element fixed by a field automorphism. -/
def IsFixedBy
    {K : Type*} [Field K]
    (sigma : K ≃+* K) (x : K) : Prop :=
  sigma x = x

/-- An element negated by a field automorphism. -/
def IsAntiFixedBy
    {K : Type*} [Field K]
    (sigma : K ≃+* K) (x : K) : Prop :=
  sigma x = -x

/-- The ratio of two anti-invariant elements is fixed. -/
theorem antiFixed_div_antiFixed_isFixed
    {K : Type*} [Field K]
    (sigma : K ≃+* K)
    (x tau : K)
    (hx : IsAntiFixedBy sigma x)
    (htau : IsAntiFixedBy sigma tau) :
    IsFixedBy sigma (x / tau) := by
  change sigma (x / tau) = x / tau
  change sigma x = -x at hx
  change sigma tau = -tau at htau
  simp [div_eq_mul_inv, hx, htau]

/-- A fixed scalar times an anti-invariant seed is anti-invariant. -/
theorem fixed_mul_antiFixed_isAntiFixed
    {K : Type*} [Field K]
    (sigma : K ≃+* K)
    (c tau : K)
    (hc : IsFixedBy sigma c)
    (htau : IsAntiFixedBy sigma tau) :
    IsAntiFixedBy sigma (c * tau) := by
  change sigma (c * tau) = -(c * tau)
  rw [map_mul, hc, htau]
  ring

/-- A nonzero anti-invariant seed spans every anti-invariant element over the
fixed field. -/
theorem antiFixed_eq_fixedRatio_mul_seed
    {K : Type*} [Field K]
    (sigma : K ≃+* K)
    (x tau : K)
    (hx : IsAntiFixedBy sigma x)
    (htau : IsAntiFixedBy sigma tau)
    (htau0 : tau ≠ 0) :
    IsFixedBy sigma (x / tau) ∧
      x = (x / tau) * tau := by
  constructor
  · exact antiFixed_div_antiFixed_isFixed sigma x tau hx htau
  · field_simp

/-- Two nonzero anti-invariant seeds differ by a unique fixed-field ratio. -/
theorem antiFixed_seed_ratio
    {K : Type*} [Field K]
    (sigma : K ≃+* K)
    (tau₁ tau₂ : K)
    (h₁ : IsAntiFixedBy sigma tau₁)
    (h₂ : IsAntiFixedBy sigma tau₂)
    (h₂0 : tau₂ ≠ 0) :
    IsFixedBy sigma (tau₁ / tau₂) ∧
      tau₁ = (tau₁ / tau₂) * tau₂ :=
  antiFixed_eq_fixedRatio_mul_seed sigma tau₁ tau₂ h₁ h₂ h₂0

end Ecdlp.ParityLift
