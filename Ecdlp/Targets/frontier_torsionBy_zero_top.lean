import Mathlib

namespace Ecdlp.Targets.FrontierTorsionbyZeroTop

/-- [frontier:frontier_torsionBy_zero_top] Every element is 0-torsion: the 0-torsion subgroup is the whole group. -/
theorem frontier_torsionBy_zero_top {A : Type*} [AddCommGroup A] :
    AddSubgroup.torsionBy A (0 : ℤ) = ⊤ := by
  sorry

end Ecdlp.Targets.FrontierTorsionbyZeroTop
