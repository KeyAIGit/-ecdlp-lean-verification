import Mathlib

namespace Ecdlp.Targets.FrontierPowCardEqOne

/-- [frontier:frontier_pow_card_eq_one] Euler/Lagrange: g ^ |G| = 1 in a finite group. -/
theorem frontier_pow_card_eq_one {G : Type*} [Group G] [Fintype G] (g : G) :
    g ^ Fintype.card G = 1 := by
  sorry

end Ecdlp.Targets.FrontierPowCardEqOne
