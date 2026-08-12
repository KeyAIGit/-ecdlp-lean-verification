import Mathlib
import Ecdlp.Proved.GlvGaussianPeriodCut

/-!
# Normalized Gaussian-period blackbox identities

This file formalizes elementary algebraic identities used by
`NORMALIZED-PERIOD-BLACKBOX-032`.

The normalized three-factor resolvent is a product of three normalized factors.
Cyclic permutation does not change it, simultaneous inversion of the two
product-one triples does not change it, and a full product ratio is one once a
permutation argument identifies numerator and denominator.

The file does not formalize Weil pairings, cyclotomic fields, CM kernels,
Galois orbit counts, or a public evaluator from elliptic-curve coordinates.
-/

namespace Ecdlp.ParityLift

/-- A normalized product of three factors equals the product of their three
normalized ratios. -/
theorem normalizedTripleProduct_eq_productRatios
    {K : Type*} [Field K]
    (a b c A B C : K)
    (hA : 1 - A ≠ 0) (hB : 1 - B ≠ 0) (hC : 1 - C ≠ 0) :
    ((1 - a) * (1 - b) * (1 - c)) /
        ((1 - A) * (1 - B) * (1 - C)) =
      ((1 - a) / (1 - A)) *
        ((1 - b) / (1 - B)) *
        ((1 - c) / (1 - C)) := by
  field_simp
  ring

/-- Cyclically permuting both triples leaves the normalized resolvent
unchanged. -/
theorem normalizedTripleProduct_cycle
    {K : Type*} [Field K]
    (a b c A B C : K) :
    ((1 - a) * (1 - b) * (1 - c)) /
        ((1 - A) * (1 - B) * (1 - C)) =
      ((1 - b) * (1 - c) * (1 - a)) /
        ((1 - B) * (1 - C) * (1 - A)) := by
  ring

/-- If both phase triples have product one, inverting every phase entry in
both numerator and denominator leaves the normalized value unchanged. This is
the algebraic core of the `a -> -a` dual-orbit covariance. -/
theorem normalizedTripleProduct_inversion
    {K : Type*} [Field K]
    (a b c A B C : K)
    (ha : a ≠ 0) (hb : b ≠ 0) (hc : c ≠ 0)
    (hA : A ≠ 0) (hB : B ≠ 0) (hC : C ≠ 0)
    (habc : a * b * c = 1)
    (hABC : A * B * C = 1) :
    ((1 - a⁻¹) * (1 - b⁻¹) * (1 - c⁻¹)) /
        ((1 - A⁻¹) * (1 - B⁻¹) * (1 - C⁻¹)) =
      ((1 - a) * (1 - b) * (1 - c)) /
        ((1 - A) * (1 - B) * (1 - C)) := by
  rw [tripleProduct_inversion_neg a b c ha hb hc habc,
      tripleProduct_inversion_neg A B C hA hB hC hABC]
  simp

/-- Once an exact permutation argument shows that the numerator full product
is the denominator full product, their normalized ratio is one. -/
theorem normalizedFullProduct_eq_one
    {K : Type*} [Field K]
    (numerator denominator : K)
    (hperm : numerator = denominator)
    (hden : denominator ≠ 0) :
    numerator / denominator = 1 := by
  rw [hperm]
  exact div_self denominator hden

end Ecdlp.ParityLift
