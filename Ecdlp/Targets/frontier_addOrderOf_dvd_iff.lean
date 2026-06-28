import Mathlib

namespace Ecdlp.Targets.FrontierAddorderofDvdIff

/-- [frontier:frontier_addOrderOf_dvd_iff] Order divides n iff n-smul is zero (torsion ↔ order characterization). -/
theorem frontier_addOrderOf_dvd_iff {A : Type*} [AddGroup A] (a : A) (n : ℕ) :
    addOrderOf a ∣ n ↔ n • a = 0 := by
  sorry

end Ecdlp.Targets.FrontierAddorderofDvdIff
