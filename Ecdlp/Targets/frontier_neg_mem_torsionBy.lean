import Mathlib

namespace Ecdlp.Targets.FrontierNegMemTorsionby

/-- [frontier:frontier_neg_mem_torsionBy] Torsion is closed under negation: -x is n-torsion when x is. -/
theorem frontier_neg_mem_torsionBy {A : Type*} [AddCommGroup A] (n : ℤ) (x : A)
    (hx : x ∈ AddSubgroup.torsionBy A n) : -x ∈ AddSubgroup.torsionBy A n := by
  sorry

end Ecdlp.Targets.FrontierNegMemTorsionby
