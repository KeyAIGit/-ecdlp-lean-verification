import Mathlib

/-!
# Canonical midpoint circularity on an odd cycle

This file formalizes the arithmetic core of
`CANONICAL-MIDPOINT-CIRCULARITY-005`.

For a canonical scalar `k`, the canonical path midpoint is `k / 2`, and the
correction in the binary decomposition

```text
k = 2 * (k / 2) + (k % 2)
```

is exactly the parity bit. In an odd cyclic group, the unique public group half
of `[k]G` has canonical representative

```text
(k + (k % 2) * n) / 2,
```

which differs from the canonical path midpoint by

```text
(k % 2) * ((n + 1) / 2).
```

Thus a divide-and-conquer construction that assumes the canonical midpoint has
already selected the target parity branch.

These are arithmetic and ordinary scalar-action identities only. They do not
rule out a midpoint-independent theta, EDS, analytic, or coordinate circuit.
-/

namespace Ecdlp.CocycleIntegration

/-- A natural number has one of the two possible residues modulo two. -/
theorem mod_two_cases (k : ℕ) : k % 2 = 0 ∨ k % 2 = 1 := by
  omega

/-- The canonical binary decomposition of a natural scalar. -/
theorem canonical_binary_split (k : ℕ) :
    k = 2 * (k / 2) + k % 2 := by
  omega

/-- In any proposed binary split with a one-bit correction, that correction is
exactly the canonical parity bit. -/
theorem binary_split_bit_eq_parity
    {k midpoint bit : ℕ}
    (hbit : bit < 2)
    (hsplit : k = 2 * midpoint + bit) :
    bit = k % 2 := by
  omega

/-- The midpoint in a valid binary split is the canonical floor midpoint. -/
theorem binary_split_midpoint_eq_div_two
    {k midpoint bit : ℕ}
    (hbit : bit < 2)
    (hsplit : k = 2 * midpoint + bit) :
    midpoint = k / 2 := by
  omega

/-- Returning the canonical midpoint also returns parity through the residual. -/
theorem canonical_midpoint_residual_eq_parity (k : ℕ) :
    k - 2 * (k / 2) = k % 2 := by
  omega

/-- Canonical scalar splitting transported to any additive monoid. -/
theorem point_canonical_binary_split
    {A : Type*} [AddMonoid A] (G : A) (k : ℕ) :
    k • G = (k / 2) • G + (k / 2) • G + (k % 2) • G := by
  calc
    k • G = (2 * (k / 2) + k % 2) • G :=
      congrArg (fun m : ℕ => m • G) (canonical_binary_split k)
    _ = (k / 2) • G + (k / 2) • G + (k % 2) • G := by
      rw [two_mul]
      simp [add_nsmul, add_assoc]

/-- Canonical representative of the public group half on an odd cycle. -/
def oddCyclePublicHalf (n k : ℕ) : ℕ :=
  (k + (k % 2) * n) / 2

/-- The public odd-cycle half is the canonical path midpoint plus a parity-sized
half-order correction. -/
theorem oddCyclePublicHalf_eq_canonical_add_correction
    {n k : ℕ} (hnOdd : n % 2 = 1) :
    oddCyclePublicHalf n k
      = k / 2 + (k % 2) * ((n + 1) / 2) := by
  rcases mod_two_cases k with hk | hk
  · simp [oddCyclePublicHalf, hk]
  · simp [oddCyclePublicHalf, hk]
    omega

/-- Doubling the public half representative returns the original scalar plus
exactly one full-order wrap when the scalar is odd. -/
theorem two_mul_oddCyclePublicHalf
    {n k : ℕ} (hnOdd : n % 2 = 1) :
    2 * oddCyclePublicHalf n k = k + (k % 2) * n := by
  rcases mod_two_cases k with hk | hk
  · simp [oddCyclePublicHalf, hk]
    omega
  · simp [oddCyclePublicHalf, hk]
    omega

/-- For a canonical scalar below the odd order, the public half representative
is itself canonical. -/
theorem oddCyclePublicHalf_lt_order
    {n k : ℕ} (hnOdd : n % 2 = 1) (hk : k < n) :
    oddCyclePublicHalf n k < n := by
  rcases mod_two_cases k with hpar | hpar
  · simp [oddCyclePublicHalf, hpar]
    omega
  · simp [oddCyclePublicHalf, hpar]
    omega

/-- The public group half equals the canonical path midpoint exactly in the even
branch. Selecting whether a correction is needed is therefore parity. -/
theorem oddCyclePublicHalf_eq_canonical_iff_even
    {n k : ℕ} (hnOdd : n % 2 = 1) :
    oddCyclePublicHalf n k = k / 2 ↔ k % 2 = 0 := by
  rw [oddCyclePublicHalf_eq_canonical_add_correction hnOdd]
  constructor
  · intro h
    rcases mod_two_cases k with hk | hk
    · exact hk
    · rw [hk] at h
      simp at h
      omega
  · intro hk
    simp [hk]

end Ecdlp.CocycleIntegration
