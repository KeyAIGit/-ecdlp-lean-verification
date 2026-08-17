import Mathlib

/-!
# Arithmetic envelope for mixed-y hybrid Fourier transfer

This file records the finite-sum bookkeeping used by
`MIXED-Y-HYBRID-TRANSFER-016`.

After field Fourier inversion, a scalar-domain Fourier coefficient is bounded
by a sum of the form

`sum_i coefficientNorm(i) * hybridSumNorm(i)`.

If every complete hybrid sum has a common square-root bound `M`, the whole
coefficient is at most `M` times the field Fourier `L1` norm.  For products of
independent field observables, the two-dimensional Fourier `L1` norm factors.

Lean proves only these finite arithmetic implications.  It does not formalize
Artin-Schreier sheaves, Kummer sheaves, Weil-Deligne bounds, or the claim that
the relevant elliptic hybrid sums are `O(sqrt p)`.
-/

namespace Ecdlp.ParityLift

/-- A common envelope for all complete hybrid sums transfers through the
nonnegative field-Fourier coefficient norms. -/
theorem finiteWeightedTransfer_envelope
    {ι : Type*} [Fintype ι]
    (coefficientNorm hybridSumNorm : ι → ℝ)
    (M : ℝ)
    (hcoeff : ∀ i, 0 ≤ coefficientNorm i)
    (hhybrid : ∀ i, hybridSumNorm i ≤ M) :
    (∑ i, coefficientNorm i * hybridSumNorm i) ≤
      M * ∑ i, coefficientNorm i := by
  calc
    (∑ i, coefficientNorm i * hybridSumNorm i) ≤
        ∑ i, coefficientNorm i * M := by
      apply Finset.sum_le_sum
      intro i hi
      exact mul_le_mul_of_nonneg_left (hhybrid i) (hcoeff i)
    _ = (∑ i, coefficientNorm i) * M := by
      rw [Finset.sum_mul]
    _ = M * ∑ i, coefficientNorm i := by
      ring

/-- The `L1` norm of a tensor-product Fourier coefficient array factors into
the product of the two one-dimensional `L1` norms. -/
theorem tensorFourierL1_factor
    {ι κ : Type*} [Fintype ι] [Fintype κ]
    (a : ι → ℝ) (b : κ → ℝ) :
    (∑ i, ∑ k, |a i * b k|) =
      (∑ i, |a i|) * ∑ k, |b k| := by
  calc
    (∑ i, ∑ k, |a i * b k|) =
        ∑ i, ∑ k, |a i| * |b k| := by
      simp only [abs_mul]
    _ = ∑ i, |a i| * ∑ k, |b k| := by
      apply Finset.sum_congr rfl
      intro i hi
      rw [Finset.mul_sum]
    _ = (∑ i, |a i|) * ∑ k, |b k| := by
      rw [Finset.sum_mul]

/-- If two nonnegative field-Fourier `L1` bounds are known separately, their
product observable has the product bound. -/
theorem tensorFourierL1_bound
    (actualA actualB boundA boundB : ℝ)
    (hactualA : 0 ≤ actualA)
    (hactualB : 0 ≤ actualB)
    (hA : actualA ≤ boundA)
    (hB : actualB ≤ boundB) :
    actualA * actualB ≤ boundA * boundB := by
  exact mul_le_mul hA hB hactualB (le_trans hactualA hA)

/-- Multiplying an inverse-square-root coefficient by a logarithmic field `L1`
bound preserves a square-root denominator.  This theorem is intentionally an
algebraic rewrite, not an asymptotic claim. -/
theorem logarithmicL1_over_sqrt_rewrite
    (C L p : ℝ) :
    C * p⁻¹ * L = C * L * p⁻¹ := by
  ring

end Ecdlp.ParityLift
