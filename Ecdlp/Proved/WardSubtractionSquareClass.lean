import Mathlib

/-!
# Square-class information is not closed under subtraction

The Ward recurrence for an elliptic sequence contains a subtraction of two
field-valued products. This file records a finite-field obstruction to replacing
that subtraction by a transition on the two quadratic-residue bits alone.

The statement is deliberately scoped: it does not exclude a field-valued state
that retains a ratio, an additive cancellation parameter, or other coordinate
data.
-/

namespace Ecdlp.WardSubtraction

/-- Boolean square-class indicator over the fixed field `ZMod 7`. -/
def squareBit (value : ZMod 7) : Bool :=
  decide (IsSquare value)

@[simp]
theorem squareBit_one : squareBit (1 : ZMod 7) = true := by
  native_decide

@[simp]
theorem squareBit_two : squareBit (2 : ZMod 7) = true := by
  native_decide

@[simp]
theorem squareBit_four : squareBit (4 : ZMod 7) = true := by
  native_decide

@[simp]
theorem squareBit_one_sub_two :
    squareBit ((1 : ZMod 7) - 2) = false := by
  native_decide

@[simp]
theorem squareBit_one_sub_four :
    squareBit ((1 : ZMod 7) - 4) = true := by
  native_decide

/-- No function of the two input square-class bits can recover the square class
of every nonzero subtraction. The witnesses `(1,2)` and `(1,4)` have the same
input bits but opposite output bits. -/
theorem no_squareBit_subtraction_map :
    ¬ ∃ outputMap : Bool → Bool → Bool,
      ∀ left right : ZMod 7,
        left ≠ 0 → right ≠ 0 → left - right ≠ 0 →
          outputMap (squareBit left) (squareBit right)
            = squareBit (left - right) := by
  rintro ⟨outputMap, hmap⟩
  have h12 := hmap (1 : ZMod 7) 2 (by native_decide) (by native_decide)
    (by native_decide)
  have h14 := hmap (1 : ZMod 7) 4 (by native_decide) (by native_decide)
    (by native_decide)
  simp only [squareBit_one, squareBit_two, squareBit_four,
    squareBit_one_sub_two, squareBit_one_sub_four] at h12 h14
  exact Bool.false_ne_true (h12.symm.trans h14)

end Ecdlp.WardSubtraction
