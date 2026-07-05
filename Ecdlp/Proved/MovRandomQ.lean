import Mathlib

namespace Ecdlp.MovReduction

open Finset

/-- [mov-random-q-success-probability-006] **MOV random-`Q` success probability.**
In the MOV/Frey–Rück reduction one needs an `n`-torsion point `Q` for which the Weil
pairing `e_n(P,Q)` has full order `n`. In a cyclic group of order `n` the number of
elements of order exactly `n` is Euler's totient `φ(n)`, so a uniformly random choice
succeeds with probability `φ(n)/n`. Proved: the counting identity is exactly
`IsCyclic.card_orderOf_eq_totient` at `d = Fintype.card G`. -/
theorem mov_random_q_success_probability {G : Type*} [Group G] [Fintype G] [IsCyclic G]
    (n : ℕ) (hn : Fintype.card G = n) :
    (univ.filter (fun g : G => orderOf g = n)).card = Nat.totient n := by
  subst hn
  exact IsCyclic.card_orderOf_eq_totient dvd_rfl

end Ecdlp.MovReduction
