import Mathlib

namespace Ecdlp.ParityLift

/-- The negative sign cannot have odd multiplicative order. -/
theorem negOne_not_oddOrder (m : ℕ) :
    (-1 : ℤ) ^ (2 * m + 1) ≠ 1 := by
  rw [pow_add, pow_mul]
  norm_num

/-- A sign whose odd power is one is the positive sign. -/
theorem oddOrder_sign_is_trivial
    (m : ℕ) (s : ℤ)
    (hs : s = 1 ∨ s = -1)
    (hpow : s ^ (2 * m + 1) = 1) :
    s = 1 := by
  rcases hs with rfl | rfl
  · rfl
  · exact False.elim ((negOne_not_oddOrder m) hpow)

/-- Alternating canonical labels fail a multiplicative law at the odd wrap. -/
theorem canonicalParity_wrap_not_character (m : ℕ) :
    (-1 : ℤ) ^ 0 ≠ (-1 : ℤ) ^ (2 * m) * (-1 : ℤ) ^ 1 := by
  simp

end Ecdlp.ParityLift
