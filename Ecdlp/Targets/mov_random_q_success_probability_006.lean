import Mathlib

namespace Ecdlp.Targets.MovRandomQSuccessProbability

open Finset

/-- [mov-random-q-success-probability-006] **MOV random-`Q` success probability.**
In the MOV/Frey–Rück reduction one needs an `n`-torsion point `Q` for which the Weil
pairing `e_n(P,Q)` has full order `n`. In a cyclic group of order `n` the number of
elements of order exactly `n` is Euler's totient `φ(n)`, so a uniformly random choice
succeeds with probability `φ(n)/n`. Open conjecture stem (the counting identity). -/
theorem mov_random_q_success_probability {G : Type*} [Group G] [Fintype G] [IsCyclic G]
    (n : ℕ) (hn : Fintype.card G = n) :
    (univ.filter (fun g : G => orderOf g = n)).card = Nat.totient n := by
  sorry

end Ecdlp.Targets.MovRandomQSuccessProbability
