import Mathlib

/-!
# The `r`-general elliptic-sequence identity reduces to its `r = 1` case

`isEllSequence_of_rec_one`: if `W : ℤ → R` satisfies the two-index recurrence
`W(m+n)·W(m−n) = W(m+1)·W(m−1)·W(n)² − W(n+1)·W(n−1)·W(m)²` for all `m, n`, then `W` is an elliptic
sequence in Mathlib's sense (`IsEllSequence W`, the three-index identity with a free `r`). Proved by
pure algebra: three instances of the hypothesis combine under a single `linear_combination`; no
induction, no field, and — notably — **no `W 1 = 1` / non-vanishing hypothesis** (the reduction is
more general than the roadmap anticipated). This isolates the entire remaining content of the open
Mathlib TODO "`normEDS` is an elliptic sequence"
(`Mathlib/NumberTheory/EllipticDivisibilitySequence.lean`) into the single `r = 1` master
recurrence — the first, self-contained upstream stepping stone toward that contribution. See
`notes/B1_TRACTABILITY_MAP.md`. No new axioms.
-/

namespace Ecdlp.EDS

/-- **The `r`-general elliptic-sequence identity is a pure consequence of its `r = 1` case.**
If `W : ℤ → R` (over any commutative ring) satisfies the two-index recurrence, then `IsEllSequence W`.
No non-vanishing / `W 1 = 1` hypothesis is needed. -/
theorem isEllSequence_of_rec_one {R : Type*} [CommRing R] {W : ℤ → R}
    (hrec : ∀ m n : ℤ,
      W (m + n) * W (m - n) = W (m + 1) * W (m - 1) * W n ^ 2 - W (n + 1) * W (n - 1) * W m ^ 2) :
    IsEllSequence W := by
  intro m n r
  linear_combination W r ^ 2 * hrec m n - W n ^ 2 * hrec m r + W m ^ 2 * hrec n r

end Ecdlp.EDS
