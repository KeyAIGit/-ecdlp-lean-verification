import Mathlib

/-!
# GLV Gaussian-period cut

This file formalizes the elementary algebraic identity behind
`GLV-GAUSSIAN-PERIOD-CUT-029`.

For three nonzero phase elements `a,b,c` with product one, the product

```text
(1-a)(1-b)(1-c)
```

is the inverse-orbit sum minus the forward-orbit sum. On the complex unit
circle this is `conjugate(eta)-eta` for `eta=a+b+c`, so its imaginary sign is
the orientation of the corresponding Gaussian period.

The file does not formalize cyclotomic fields, complex positivity, Galois orbit
degrees, elliptic curves, or a public evaluator from point coordinates.
-/

namespace Ecdlp.ParityLift

/-- The zero-sum triple product is the inverse-orbit resolvent. -/
theorem tripleProduct_eq_inverseSum_sub_sum
    {K : Type*} [Field K]
    (a b c : K)
    (ha : a ≠ 0) (hb : b ≠ 0) (hc : c ≠ 0)
    (hprod : a * b * c = 1) :
    (1 - a) * (1 - b) * (1 - c) =
      (a⁻¹ + b⁻¹ + c⁻¹) - (a + b + c) := by
  have hab : a * b = c⁻¹ := by
    calc
      a * b = (a * b * c) * c⁻¹ := by simp [mul_assoc, hc]
      _ = c⁻¹ := by rw [hprod]; simp
  have hac : a * c = b⁻¹ := by
    calc
      a * c = (a * c * b) * b⁻¹ := by simp [mul_assoc, hb]
      _ = (a * b * c) * b⁻¹ := by ring
      _ = b⁻¹ := by rw [hprod]; simp
  have hbc : b * c = a⁻¹ := by
    calc
      b * c = (b * c * a) * a⁻¹ := by simp [mul_assoc, ha]
      _ = (a * b * c) * a⁻¹ := by ring
      _ = a⁻¹ := by rw [hprod]; simp
  calc
    (1 - a) * (1 - b) * (1 - c) =
        1 - a - b - c + a * b + a * c + b * c - a * b * c := by ring
    _ = (a⁻¹ + b⁻¹ + c⁻¹) - (a + b + c) := by
      rw [hab, hac, hbc, hprod]
      ring

/-- Cyclically permuting the three GLV phase entries does not change the
resolvent. -/
theorem tripleProduct_cycle
    {K : Type*} [CommRing K]
    (a b c : K) :
    (1 - a) * (1 - b) * (1 - c) =
      (1 - b) * (1 - c) * (1 - a) := by
  ring

/-- Inverting every phase element negates the zero-sum triple resolvent. On the
unit circle this is the algebraic form of conjugation anti-invariance. -/
theorem tripleProduct_inversion_neg
    {K : Type*} [Field K]
    (a b c : K)
    (ha : a ≠ 0) (hb : b ≠ 0) (hc : c ≠ 0)
    (hprod : a * b * c = 1) :
    (1 - a⁻¹) * (1 - b⁻¹) * (1 - c⁻¹) =
      -((1 - a) * (1 - b) * (1 - c)) := by
  have hprodInv : a⁻¹ * b⁻¹ * c⁻¹ = 1 := by
    calc
      a⁻¹ * b⁻¹ * c⁻¹ = (a * b * c)⁻¹ := by
        simp [mul_assoc, mul_left_comm, mul_comm]
      _ = 1 := by rw [hprod]; simp
  rw [tripleProduct_eq_inverseSum_sub_sum
        a⁻¹ b⁻¹ c⁻¹ (inv_ne_zero ha) (inv_ne_zero hb) (inv_ne_zero hc) hprodInv,
      tripleProduct_eq_inverseSum_sub_sum a b c ha hb hc hprod]
  simp [ha, hb, hc]
  ring

end Ecdlp.ParityLift
