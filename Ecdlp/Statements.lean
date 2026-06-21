import Mathlib

namespace Ecdlp.Targets

variable {G : Type*} [Group G] [Fintype G]

theorem order_dvd_card (g : G) : orderOf g ∣ Fintype.card G :=
  orderOf_dvd_card

theorem glv_eigenvalue_zmod (n lam : ℕ)
    (h : (lam^2 + lam + 1) % n = 0) :
    ((lam : ZMod n)^2 + (lam : ZMod n) + 1) = 0 := by
  sorry

end Ecdlp.Targets
