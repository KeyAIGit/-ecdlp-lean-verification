import Mathlib

open scoped BigOperators

namespace Ecdlp.EndpointSegment

variable {A : Type*} [AddCommGroup A]

def edgeCocycle (defect : A) (potential : ℕ → A) (index : ℕ) : A :=
  defect + potential (index + 1) - potential index

def segmentSum
    (defect : A) (potential : ℕ → A) (start length : ℕ) : A :=
  ∑ i ∈ Finset.range length,
    edgeCocycle defect potential (start + i)

@[simp]
theorem segmentSum_zero
    (defect : A) (potential : ℕ → A) (start : ℕ) :
    segmentSum defect potential start 0 = 0 := by
  simp [segmentSum]

theorem segmentSum_succ
    (defect : A) (potential : ℕ → A) (start length : ℕ) :
    segmentSum defect potential start (length + 1)
      = segmentSum defect potential start length
        + edgeCocycle defect potential (start + length) := by
  simp [segmentSum]

theorem segmentSum_normalForm
    (defect : A) (potential : ℕ → A) (start length : ℕ) :
    segmentSum defect potential start length
      = length • defect
        + potential (start + length)
        - potential start := by
  induction length with
  | zero => simp [segmentSum]
  | succ length ih =>
      rw [segmentSum_succ, ih]
      simp [edgeCocycle, add_nsmul, Nat.add_assoc] <;> abel

theorem segmentSum_add
    (defect : A) (potential : ℕ → A)
    (start leftLength rightLength : ℕ) :
    segmentSum defect potential start (leftLength + rightLength)
      = segmentSum defect potential start leftLength
        + segmentSum defect potential (start + leftLength) rightLength := by
  simp only [segmentSum_normalForm]
  simp [add_nsmul, Nat.add_assoc] <;> abel

def endpointResidual
    (defect : A) (potential : ℕ → A) (start length : ℕ) : A :=
  segmentSum defect potential start length
    - (potential (start + length) - potential start)

theorem endpointResidual_eq_length_smul
    (defect : A) (potential : ℕ → A) (start length : ℕ) :
    endpointResidual defect potential start length = length • defect := by
  unfold endpointResidual
  rw [segmentSum_normalForm]
  abel

end Ecdlp.EndpointSegment
