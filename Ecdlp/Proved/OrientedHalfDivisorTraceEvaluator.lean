import Mathlib

namespace Ecdlp.ParityLift

variable {K : Type*} [Field K]

private def ratio (a b c : K) : K := -(c * b) / a

private theorem ratio_square
    (a b c d : K)
    (ha : a ≠ 0)
    (hc : c ^ 2 = d)
    (hn : a ^ 2 = d * b ^ 2) :
    ratio a b c ^ 2 = 1 := by
  unfold ratio
  field_simp [ha]
  calc
    c ^ 2 * b ^ 2 = d * b ^ 2 := by rw [hc]
    _ = a ^ 2 := hn.symm

end Ecdlp.ParityLift
