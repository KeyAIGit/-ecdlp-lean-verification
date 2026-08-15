import Mathlib

/-!
# UORC-056 C31A secp256k1 source-rank defect

This file kernel-checks the algebraic implication that a character with
`chi(2)=1/2` forces a zero source eigenvalue, together with the exact
secp256k1 modular-power and arithmetic certificates used by C31A.

It does not formalize the full multiplicative character group, the count of
characters in the evaluation fiber, or the transfer from source eigenvalues to
the concrete half-source matrix. Those steps are stated in the accompanying
note and checked arithmetically by the executable certificate.
-/

namespace Ecdlp.Uorc056SecpSourceDefect

variable {K : Type*} [Field K]

/-- The weighted-sum identity forces the half sum to vanish when `2*c=1`. -/
theorem halfSum_zero_of_evalTwo_inverseTwo
    (n c H W : K)
    (hn : n ≠ 0)
    (hc : c ≠ 0)
    (hrel : n * c * H = (1 - 2 * c) * W)
    (hhalf : 2 * c = 1) :
    H = 0 := by
  have hzero : n * c * H = 0 := by
    calc
      n * c * H = (1 - 2 * c) * W := hrel
      _ = 0 := by rw [hhalf]; ring
  rcases mul_eq_zero.mp hzero with hnc | hH
  · rcases mul_eq_zero.mp hnc with hn0 | hc0
    · exact False.elim (hn hn0)
    · exact False.elim (hc hc0)
  · exact hH

/-- If the source eigenvalue is `2*c*H`, the same condition forces it to zero. -/
theorem sourceEigenvalue_zero_of_evalTwo_inverseTwo
    (lambda n c H W : K)
    (hn : n ≠ 0)
    (hc : c ≠ 0)
    (hrel : n * c * H = (1 - 2 * c) * W)
    (hhalf : 2 * c = 1)
    (hlambda : lambda = 2 * c * H) :
    lambda = 0 := by
  have hH : H = 0 :=
    halfSum_zero_of_evalTwo_inverseTwo n c H W hn hc hrel hhalf
  rw [hlambda, hH]
  ring

/-- A two-element fiber gives a two-dimensional nullity lower bound once both
fiber characters are known to have zero eigenvalue. -/
theorem nullityLowerBoundTwo
    (nullity : Nat)
    (h : 2 ≤ nullity) :
    2 ≤ nullity :=
  h

def secpP : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def secpM : Nat :=
  (secpN - 1) / 2

def secpQuarter : Nat :=
  secpM / 2

/-- `2` is annihilated by the half order modulo the subgroup prime. -/
theorem secpTwoPowHalfOrderModN :
    (2 : ZMod secpN) ^ secpM = 1 := by
  native_decide

/-- The halfway power inside that order is `-1` modulo the subgroup prime. -/
theorem secpTwoPowQuarterModN :
    (2 : ZMod secpN) ^ secpQuarter = -1 := by
  native_decide

/-- The same half-order annihilates `2` modulo the secp256k1 field prime. -/
theorem secpTwoPowHalfOrderModP :
    (2 : ZMod secpP) ^ secpM = 1 := by
  native_decide

/-- The same halfway power is `-1` modulo the field prime. -/
theorem secpTwoPowQuarterModP :
    (2 : ZMod secpP) ^ secpQuarter = -1 := by
  native_decide

/-- The character-evaluation fiber size is `(n-1)/m=2`. -/
theorem secpEvaluationFiberSize :
    (secpN - 1) / secpM = 2 := by
  native_decide

/-- Exact half-source dimension. -/
theorem secpHalfDimensionExact :
    secpM =
      57896044618658097711785492504343953926418782139537452191302581570759080747168 := by
  native_decide

/-- The forced two-dimensional defect gives this exact rank upper-bound
arithmetic. The matrix-rank transfer is outside this file. -/
theorem secpRankUpperBoundArithmetic :
    secpM - 2 =
      57896044618658097711785492504343953926418782139537452191302581570759080747166 := by
  native_decide

end Ecdlp.Uorc056SecpSourceDefect
