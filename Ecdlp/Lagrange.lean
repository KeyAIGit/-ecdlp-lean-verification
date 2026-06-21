import Mathlib.GroupTheory.OrderOfElement

theorem order_dvd_card {G : Type*} [Group G] [Fintype G] (g : G) :
    orderOf g ∣ Fintype.card G :=
  orderOf_dvd_card
