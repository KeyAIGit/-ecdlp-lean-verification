import Mathlib

/-!
# Baby-step giant-step: the `O(√n)` upper bound

The generic discrete logarithm in a cyclic group of order `n` is solved
deterministically in `O(√n)` group operations by the baby-step giant-step
algorithm. Its correctness rests on one arithmetic fact: with `m = ⌈√n⌉`, every
exponent `x < n` can be written `x = i·m + j` with `i, j < m`. The algorithm
precomputes the `m` baby steps `g^j` and walks the `m` giant steps `(g^m)^i`,
matching a collision in `O(√n)` work.

Together with `Ecdlp.GenericGroup.generic_dlog_query_bound` these give the two `√n`
**arithmetic relations** — the lower relation `p ≤ q·q` and the upper `n ≤ ⌈√n⌉²` — that
*motivate* the `Θ(√n)` generic complexity. This is **not** a formal proof of `Θ(√n)` running
time: there is no executable algorithm, lookup table, cost/step semantics, or (for Pollard-rho)
birthday-time analysis here. The claim "generic DLP is `Θ(√n)`" is the standard result these
relations point to, not something this file establishes as a complexity theorem.
-/

namespace Ecdlp.GenericGroup

/-- **Baby-step giant-step decomposition.** With `m = ⌈√n⌉ = Nat.sqrt n + 1`, every
`x < n` is `x = i·m + j` with `i, j < m` — the `O(√n)` covering of all exponents
that makes the baby-step giant-step algorithm correct. -/
theorem bsgs_decomp (n x : ℕ) (hx : x < n) :
    ∃ i j, i < Nat.sqrt n + 1 ∧ j < Nat.sqrt n + 1 ∧
      x = i * (Nat.sqrt n + 1) + j := by
  have hmpos : 0 < Nat.sqrt n + 1 := Nat.succ_pos _
  have hmm : n < (Nat.sqrt n + 1) * (Nat.sqrt n + 1) := Nat.lt_succ_sqrt n
  refine ⟨x / (Nat.sqrt n + 1), x % (Nat.sqrt n + 1), ?_, Nat.mod_lt x hmpos, ?_⟩
  · exact Nat.div_lt_of_lt_mul (lt_trans hx hmm)
  · exact (Nat.div_add_mod' x (Nat.sqrt n + 1)).symm

/-- The number of baby/giant steps `m = ⌈√n⌉` is `O(√n)`: `m·m` only just exceeds
`n`, so the algorithm uses `Θ(√n)` group operations — matching the `Ω(√p)` lower
bound `generic_dlog_query_bound`. -/
theorem bsgs_steps_sq_ge (n : ℕ) : n ≤ (Nat.sqrt n + 1) * (Nat.sqrt n + 1) :=
  le_of_lt (Nat.lt_succ_sqrt n)

end Ecdlp.GenericGroup
