import Mathlib

namespace Ecdlp.Targets.FrontierOrderofDvdCard

/-- [frontier:frontier_orderOf_dvd_card] Lagrange: every element's order divides the group order (finite group). -/
theorem frontier_orderOf_dvd_card {G : Type*} [Group G] [Fintype G] (g : G) :
    orderOf g ∣ Fintype.card G := by
  apply orderOf_dvd_card

end Ecdlp.Targets.FrontierOrderofDvdCard
