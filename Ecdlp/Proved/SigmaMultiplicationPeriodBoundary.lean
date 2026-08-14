import Mathlib

/-!
# Sigma multiplication period boundary

This file formalizes elementary arithmetic behind
`UORC056-SIGMA-MULTIPLICATION-PERIOD-B10`.

A prime cycle has no proper nontrivial period, and the canonical half-size
`M` in `n=2M+1` lies strictly between zero and `n` when `M` is positive.

The file does not formalize sigma functions, subgroups, elliptic curves,
secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Every divisor of a prime order is trivial or the full order. -/
theorem primePeriod_eq_one_or_order
    {n d : ℕ} (hn : n.Prime) (hd : d ∣ n) :
    d = 1 ∨ d = n := by
  exact (Nat.dvd_prime hn).mp hd

/-- A declared nontrivial period of a prime cycle is the full cycle. -/
theorem nontrivialPrimePeriod_eq_order
    {n d : ℕ} (hn : n.Prime) (hd : d ∣ n) (hd1 : d ≠ 1) :
    d = n := by
  exact ((primePeriod_eq_one_or_order hn hd).resolve_left hd1)

/-- The canonical half-size is strictly smaller than the odd cycle order. -/
theorem canonicalHalf_lt_oddOrder (M : ℕ) :
    M < 2 * M + 1 := by
  omega

/-- A positive canonical half has cardinality strictly between zero and the
odd cycle order. -/
theorem canonicalHalf_intermediate (M : ℕ) (hM : 0 < M) :
    0 < M ∧ M < 2 * M + 1 := by
  exact ⟨hM, canonicalHalf_lt_oddOrder M⟩

end Ecdlp.ParityLift
