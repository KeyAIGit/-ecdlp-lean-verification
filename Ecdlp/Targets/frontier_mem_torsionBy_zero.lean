import Mathlib

namespace Ecdlp.Targets.FrontierMemTorsionbyZero

/-- [frontier:frontier_mem_torsionBy_zero] Membership in the 0-torsion is universal. -/
theorem frontier_mem_torsionBy_zero {A : Type*} [AddCommGroup A] (x : A) :
    x ∈ AddSubgroup.torsionBy A (0 : ℤ) := by
  sorry

end Ecdlp.Targets.FrontierMemTorsionbyZero
