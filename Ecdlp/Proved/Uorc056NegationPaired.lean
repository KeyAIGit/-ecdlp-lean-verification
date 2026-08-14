import Mathlib

/-!
# UORC056 C20 algebraic core

This file formalizes the ring- and field-theoretic identities used by the
negation-paired quadratic and Hilbert-90 reductions. It deliberately does not
claim to formalize the geometric nine-point divisor theorem or the odd-prism
Laurent-support lower bound; those receive separate scoped certificates.
-/

namespace Ecdlp.UORC056

section CommRing

variable {R : Type*} [CommRing R]

/-- The paired sum/difference identity `S²-D²=4K`. -/
theorem paired_difference_of_squares (z w : R) :
    (z + w) ^ 2 - (z - w) ^ 2 = 4 * (z * w) := by
  ring

/-- The power sums of two quadratic roots satisfy the Dickson recurrence. -/
theorem paired_power_sum_recurrence (z w : R) (j : ℕ) :
    z ^ (j + 2) + w ^ (j + 2) =
      (z + w) * (z ^ (j + 1) + w ^ (j + 1)) -
        (z * w) * (z ^ j + w ^ j) := by
  simp only [pow_succ]
  ring

/-- Simultaneously changing both quadratic roots by a sign multiplies the
`j`-th power sum by `(-1)^j`. -/
theorem paired_power_sum_global_sign (z w : R) (j : ℕ) :
    (-z) ^ j + (-w) ^ j =
      (-1 : R) ^ j * (z ^ j + w ^ j) := by
  rw [show -z = (-1 : R) * z by ring,
      show -w = (-1 : R) * w by ring,
      mul_pow, mul_pow]
  ring

end CommRing

section Field

variable {K : Type*} [Field K] [CharZero K]

/-- Recover the first root from paired sum and paired difference. -/
theorem recover_first_from_sum_difference (z w : K) :
    ((z + w) + (z - w)) / 2 = z := by
  field_simp
  ring

/-- Recover the second root from paired sum and paired difference. -/
theorem recover_second_from_sum_difference (z w : K) :
    ((z + w) - (z - w)) / 2 = w := by
  field_simp
  ring

variable (τ : K ≃+* K) (hτ : Function.Involutive τ)

/-- A Hilbert-90 coboundary has norm one under an involution. -/
theorem hilbert90_coboundary_norm_one (h : K) (hh : h ≠ 0) :
    (h / τ h) * τ (h / τ h) = 1 := by
  have hτh : τ h ≠ 0 := (map_ne_zero τ).2 hh
  have hττ : τ (τ h) = h := hτ h
  calc
    (h / τ h) * τ (h / τ h) =
        (h / τ h) * (τ h / τ (τ h)) := by simp only [map_div]
    _ = (h / τ h) * (τ h / h) := by rw [hττ]
    _ = 1 := by field_simp [hh, hτh]

/-- The tautological Hilbert-90 representative `1+r` is valid, but already
requires the norm-one element `r`. -/
theorem hilbert90_tautological (r : K)
    (hNorm : r * τ r = 1) (hDen : 1 + τ r ≠ 0) :
    (1 + r) / (1 + τ r) = r := by
  apply (div_eq_iff hDen).2
  calc
    1 + r = r + 1 := by ring
    _ = r + r * τ r := by rw [hNorm]
    _ = r * (1 + τ r) := by ring

/-- Multiplication by an element of the fixed field does not change a
Hilbert-90 quotient. -/
theorem hilbert90_fixed_gauge
    (c h : K) (hc : τ c = c) (hc0 : c ≠ 0) (hh : h ≠ 0) :
    (c * h) / τ (c * h) = h / τ h := by
  have hτh : τ h ≠ 0 := (map_ne_zero τ).2 hh
  rw [map_mul, hc]
  field_simp [hc0, hh, hτh]

/-- Fixed elements are closed under addition. -/
theorem fixed_add {a b : K} (ha : τ a = a) (hb : τ b = b) :
    τ (a + b) = a + b := by
  simp [ha, hb]

/-- Fixed elements are closed under multiplication. -/
theorem fixed_mul {a b : K} (ha : τ a = a) (hb : τ b = b) :
    τ (a * b) = a * b := by
  simp [ha, hb]

/-- Fixed elements are closed under inversion. -/
theorem fixed_inv {a : K} (ha : τ a = a) :
    τ a⁻¹ = a⁻¹ := by
  simp [ha]

/-- Fixed elements are closed under division. -/
theorem fixed_div {a b : K} (ha : τ a = a) (hb : τ b = b) :
    τ (a / b) = a / b := by
  simp [ha, hb]

/-- In characteristic zero, a simultaneously fixed and anti-fixed element is
zero. This is the algebraic core of the branch-even grammar obstruction. -/
theorem fixed_and_antifixed_eq_zero {a : K}
    (hFixed : τ a = a) (hAnti : τ a = -a) : a = 0 := by
  have hEq : a = -a := by
    calc
      a = τ a := hFixed.symm
      _ = -a := hAnti
  have h2a : (2 : K) * a = 0 := by
    calc
      (2 : K) * a = a + a := by ring
      _ = a + (-a) := by rw [hEq]
      _ = 0 := by ring
  exact (mul_eq_zero.mp h2a).resolve_left (by norm_num)

/-- Hence a nonzero anti-fixed target cannot equal a fixed expression. -/
theorem fixed_ne_nonzero_antifixed {a b : K}
    (ha : τ a = a) (hb : τ b = -b) (hb0 : b ≠ 0) : a ≠ b := by
  intro hab
  subst a
  exact hb0 (fixed_and_antifixed_eq_zero τ ha hb)

end Field

end Ecdlp.UORC056
