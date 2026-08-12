import Mathlib

/-!
# Parity divisor symmetry

This file formalizes elementary field identities used by
`PARITY-DIVISOR-SYMMETRY-045`.

A subset with nonzero sum has trivial scalar stabilizer when multiplication
preserves the subset sum, and its opposite has only the multiplier `-1` as a
scalar swap. These identities underlie the exact canonical-parity stabilizer
calculation.

The file does not formalize canonical parity subsets of finite fields, C6 orbit
balance, elliptic-curve divisor degrees, arithmetic circuits, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- A nonzero subset sum forces any scalar multiplier preserving that sum to be
one. -/
theorem preservingNonzeroSum_multiplier_eq_one
    {K : Type*} [Field K]
    (multiplier subsetSum : K)
    (hsum : subsetSum ≠ 0)
    (hpreserve : multiplier * subsetSum = subsetSum) :
    multiplier = 1 := by
  apply (mul_right_cancel₀ hsum)
  simpa using hpreserve

/-- If a nonzero subset sum is sent to its negative, the multiplier is exactly
minus one. -/
theorem swappingNonzeroSum_multiplier_eq_negOne
    {K : Type*} [Field K]
    (multiplier subsetSum : K)
    (hsum : subsetSum ≠ 0)
    (hswap : multiplier * subsetSum = -subsetSum) :
    multiplier = -1 := by
  apply (mul_right_cancel₀ hsum)
  calc
    multiplier * subsetSum = -subsetSum := hswap
    _ = (-1 : K) * subsetSum := by ring

/-- A scalar cannot simultaneously preserve and negate a nonzero oriented sum
in characteristic different from two. -/
theorem preserveAndSwap_incompatible
    {K : Type*} [Field K]
    (subsetSum : K)
    (hsum : subsetSum ≠ 0)
    (htwo : (2 : K) ≠ 0)
    (hpreserve : subsetSum = -subsetSum) :
    False := by
  have hsumSelf : subsetSum + subsetSum = 0 := by
    calc
      subsetSum + subsetSum = -subsetSum + subsetSum := by rw [hpreserve]
      _ = 0 := neg_add_cancel subsetSum
  have hdouble : (2 : K) * subsetSum = 0 := by
    calc
      (2 : K) * subsetSum = subsetSum + subsetSum := by ring
      _ = 0 := hsumSelf
  rcases mul_eq_zero.mp hdouble with htwoZero | hsumZero
  · exact htwo htwoZero
  · exact hsum hsumZero

end Ecdlp.ParityLift
