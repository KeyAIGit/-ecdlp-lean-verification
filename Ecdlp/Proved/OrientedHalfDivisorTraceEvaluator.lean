import Mathlib

/-!
# Oriented half-divisor trace evaluator

This file formalizes the field-algebra core used by
`UNIFORM-ORIENTED-ROOT-CIRCUIT-056`, track C3.

A translated quarter-kernel factor has two conjugate numerators
`A + y * B` and `A - y * B`. Their product is a polynomial norm. On a
Kummer root where that norm vanishes, the ratio `-(y * B) / A` is square-one;
the vanishing conjugate determines whether the ratio is `1` or `-1`.

The file does not formalize elliptic curves, divisor classes, quarter-kernel
polynomials, translation by a half-generator, secp256k1, a circuit-size bound,
or a sub-square-root ECDLP algorithm.
-/

namespace Ecdlp.ParityLift

def tracePairEvaluator
    {K : Type*} [Field K]
    (A B y : K) : K :=
  -(y * B) / A

theorem conjugateNumerator_product
    {K : Type*} [CommRing K]
    (A B y : K) :
    (A + y * B) * (A - y * B) = A ^ 2 - y ^ 2 * B ^ 2 := by
  ring

theorem pellIdentity_atKernelRoot
    {K : Type*} [CommRing K]
    (A B y curve kernel factor constant : K)
    (hy : y ^ 2 = curve)
    (hidentity : A ^ 2 - curve * B ^ 2 = constant * kernel * factor)
    (hkernel : kernel = 0) :
    A ^ 2 = (y * B) ^ 2 := by
  have hzero : A ^ 2 - curve * B ^ 2 = 0 := by
    simpa [hkernel] using hidentity
  calc
    A ^ 2 = curve * B ^ 2 := by linear_combination hzero
    _ = y ^ 2 * B ^ 2 := by rw [hy]
    _ = (y * B) ^ 2 := by ring

theorem tracePairEvaluator_sq_eq_one
    {K : Type*} [Field K]
    (A B y curve : K)
    (hA : A ≠ 0)
    (hy : y ^ 2 = curve)
    (hnorm : A ^ 2 = curve * B ^ 2) :
    tracePairEvaluator A B y ^ 2 = 1 := by
  unfold tracePairEvaluator
  field_simp [hA]
  calc
    (-(y * B)) ^ 2 = (y * B) ^ 2 := by ring
    _ = y ^ 2 * B ^ 2 := by ring
    _ = curve * B ^ 2 := by rw [hy]
    _ = A ^ 2 := hnorm.symm

theorem tracePairEvaluator_eq_one_of_leftBranch
    {K : Type*} [Field K]
    (A B y : K)
    (hA : A ≠ 0)
    (hbranch : A = -(y * B)) :
    tracePairEvaluator A B y = 1 := by
  have hnonzero : -(y * B) ≠ 0 := by
    simpa [hbranch] using hA
  simp [tracePairEvaluator, hbranch, hnonzero]

theorem tracePairEvaluator_eq_negOne_of_rightBranch
    {K : Type*} [Field K]
    (A B y : K)
    (hA : A ≠ 0)
    (hbranch : A = y * B) :
    tracePairEvaluator A B y = -1 := by
  have hnonzero : y * B ≠ 0 := by
    simpa [hbranch] using hA
  simp [tracePairEvaluator, hbranch, hnonzero]

theorem tracePairEvaluator_neg_oddPart
    {K : Type*} [Field K]
    (A B y : K) :
    tracePairEvaluator A (-B) y = -tracePairEvaluator A B y := by
  unfold tracePairEvaluator
  ring

theorem orientedRootRatio_eq_tracePairEvaluator
    {K : Type*} [Field K]
    (Y A B y curve : K)
    (hy : y ^ 2 = curve)
    (hy0 : y ≠ 0)
    (hA : A ≠ 0)
    (hbridge : Y * A + curve * B = 0) :
    Y / y = tracePairEvaluator A B y := by
  have hbridge' := hbridge
  rw [← hy] at hbridge'
  unfold tracePairEvaluator
  field_simp [hy0, hA]
  linear_combination hbridge'

end Ecdlp.ParityLift
