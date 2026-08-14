import Mathlib

/-!
# Transposed kernel evaluation boundary

This file formalizes the elementary algebraic core of
`UORC056-TRANSPOSED-KERNEL-EVALUATION-B6`.

Canonical parity on an odd cycle has one wrap defect. In the regular
translation algebra, inverting `1 + T` gives the full alternating geometric
sum of all `n` translation powers.

The file does not formalize elliptic curves, Kummer algebras, transposed
multipoint evaluation, secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Finite alternating geometric-series identity over a commutative ring. -/
theorem one_add_mul_alternating_sum
    {R : Type*} [CommRing R] (X : R) (n : ℕ) :
    (1 + X) * Finset.sum (Finset.range n) (fun j => (-X) ^ j)
      = 1 - (-X) ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Finset.sum_range_succ, mul_add, ih, pow_succ]
      ring

/-- Away from the unique odd-cycle wrap, consecutive canonical parity values
cancel. -/
theorem canonicalParity_nonwrap (k : ℕ) :
    (-1 : ℤ) ^ (k + 1) + (-1 : ℤ) ^ k = 0 := by
  rw [pow_succ]
  ring

/-- On an odd cycle the final canonical representative is even, so the wrap
sum is two. -/
theorem canonicalParity_oddWrap (m : ℕ) :
    (-1 : ℤ) ^ 0 + (-1 : ℤ) ^ (2 * m) = 2 := by
  simp

end Ecdlp.ParityLift
