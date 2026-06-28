import Mathlib

namespace Ecdlp.Targets.FrontierZeroMemTorsionby

/-- [frontier:frontier_zero_mem_torsionBy] The identity is n-torsion for every n. -/
theorem frontier_zero_mem_torsionBy {A : Type*} [AddCommGroup A] (n : ℤ) :
    (0 : A) ∈ AddSubgroup.torsionBy A n := by
  sorry

end Ecdlp.Targets.FrontierZeroMemTorsionby
