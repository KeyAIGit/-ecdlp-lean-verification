import Mathlib

namespace Ecdlp.Targets.FrontierTorsionbyOneBot

/-- [frontier:frontier_torsionBy_one_bot] Only the identity is 1-torsion: the 1-torsion subgroup is trivial. -/
theorem frontier_torsionBy_one_bot {A : Type*} [AddCommGroup A] :
    AddSubgroup.torsionBy A (1 : ℤ) = ⊥ := by
  sorry

end Ecdlp.Targets.FrontierTorsionbyOneBot
