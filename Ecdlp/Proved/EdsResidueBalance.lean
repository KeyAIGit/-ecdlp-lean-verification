import Mathlib

/-!
# Fixed-index EDS residue balance

This file formalizes the quadratic-exponent cancellation behind the bounded
`PARITY-LIFT-000` structured-character screen.

For a hidden scalar `k`, evaluating a fixed division-polynomial index `m` at
`[k]G` introduces the same quadratic scaling `m² k²` that appears after
transport to the base EDS. Any fixed product or ratio therefore has zero
quadratic defect term by term and after finite summation.

These are arithmetic identities only. They do not formalize the analytic EDS
Residue hardness result, construct a parity oracle, or authorize any target
computation.
-/

namespace Ecdlp.EdsResidue

open scoped BigOperators

/-- One fixed index has no residual quadratic exponent after the transported
`m² k²` term is compared with its base-scaling contribution. -/
theorem fixedIndexTermQuadraticBalance (e m k : ℤ) :
    e * (m * k) ^ 2 = (e * m ^ 2) * k ^ 2 := by
  ring

/-- A finite product or ratio of fixed-index observables remains quadratically
balanced. Integer coefficients model positive product powers and negative ratio
powers uniformly. -/
theorem fixedIndexQuadraticBalance
    {ι : Type*} [Fintype ι] (e m : ι → ℤ) (k : ℤ) :
    (∑ i, e i * (m i * k) ^ 2)
      = (∑ i, e i * (m i) ^ 2) * k ^ 2 := by
  calc
    (∑ i, e i * (m i * k) ^ 2)
        = ∑ i, (e i * (m i) ^ 2) * k ^ 2 := by
            apply Finset.sum_congr rfl
            intro i hi
            ring
    _ = (∑ i, e i * (m i) ^ 2) * k ^ 2 := by
          rw [Finset.sum_mul]

/-- Equivalent zero-defect form used by the EDS-residue mechanism screen. -/
theorem fixedIndexQuadraticDefect_zero
    {ι : Type*} [Fintype ι] (e m : ι → ℤ) (k : ℤ) :
    (∑ i, e i * (m i * k) ^ 2)
        - (∑ i, e i * (m i) ^ 2) * k ^ 2 = 0 := by
  rw [fixedIndexQuadraticBalance]
  ring

end Ecdlp.EdsResidue
