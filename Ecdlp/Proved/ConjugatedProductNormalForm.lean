import Mathlib

namespace Ecdlp.ConjugatedProduct

variable {M : Type*} [Group M]

def step (constant : M) (basis : ℕ → M) (index : ℕ) : M :=
  basis (index + 1) * constant * (basis index)⁻¹

def productFrom
    (constant : M) (basis : ℕ → M) (start : ℕ) : ℕ → M
  | 0 => 1
  | length + 1 =>
      step constant basis (start + length)
        * productFrom constant basis start length

@[simp]
theorem productFrom_zero
    (constant : M) (basis : ℕ → M) (start : ℕ) :
    productFrom constant basis start 0 = 1 := rfl

@[simp]
theorem productFrom_succ
    (constant : M) (basis : ℕ → M) (start length : ℕ) :
    productFrom constant basis start (length + 1)
      = step constant basis (start + length)
        * productFrom constant basis start length := rfl

theorem productFrom_normalForm
    (constant : M) (basis : ℕ → M) (start length : ℕ) :
    productFrom constant basis start length
      = basis (start + length)
        * constant ^ length
        * (basis start)⁻¹ := by
  induction length with
  | zero => simp [productFrom]
  | succ length ih =>
      rw [productFrom_succ, ih]
      simp [step, pow_succ', Nat.add_assoc, mul_assoc]

theorem normalized_productFrom
    (constant : M) (basis : ℕ → M) (start length : ℕ) :
    (basis (start + length))⁻¹
        * productFrom constant basis start length
        * basis start
      = constant ^ length := by
  rw [productFrom_normalForm]
  group

end Ecdlp.ConjugatedProduct
