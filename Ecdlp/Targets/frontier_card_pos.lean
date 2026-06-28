import Mathlib

namespace Ecdlp.Targets.FrontierCardPos

/-- [frontier:frontier_card_pos] A finite group is nonempty: its cardinality is positive. -/
theorem frontier_card_pos {G : Type*} [Group G] [Fintype G] : 0 < Fintype.card G := by
  sorry

end Ecdlp.Targets.FrontierCardPos
