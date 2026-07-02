import Mathlib

namespace Ecdlp.Targets.FrontierOrderofOne

/-- [frontier:frontier_orderOf_one] The identity has order 1. -/
theorem frontier_orderOf_one {G : Type*} [Group G] : orderOf (1 : G) = 1 := by
  simp

end Ecdlp.Targets.FrontierOrderofOne
