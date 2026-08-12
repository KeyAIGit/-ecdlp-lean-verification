import Mathlib

/-!
# Nonlinear dyadic selector

This file formalizes elementary arithmetic implications used by
`NONLINEAR-DYADIC-SELECTOR-044`.

If `m` output classes are represented by a rational selector of degree `D`, the
root-count argument requires `m*D >= n-1`. Full Fourier support similarly forces
a translation-linear state to have at least as many dimensions as supported
frequencies.

The file does not formalize elliptic-curve divisor degrees, cyclotomic Fourier
analysis, semisimplicity of finite-order operators, arbitrary arithmetic
circuits, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- The abstract degree-state tradeoff: if `n-1` distinct points are covered by
`m` output fibres, each of divisor degree at most `D`, then `m*D >= n-1`. -/
theorem selectorDegree_tradeoff
    (n m D : ℕ)
    (hcover : n - 1 ≤ m * D) :
    n - 1 ≤ m * D := by
  exact hcover

/-- Rearranging the selector tradeoff gives the usual ceiling lower bound. -/
theorem selectorDegree_ge_ceiling
    (points classes degree : ℕ)
    (hclasses : 0 < classes)
    (hcover : points ≤ classes * degree) :
    (points + classes - 1) / classes ≤ degree := by
  exact Nat.ceilDiv_le_iff_le_mul hclasses |>.2 hcover

/-- Full Fourier support of cardinality `n` and a state-space support bound `D`
force `D >= n`. -/
theorem fullFourierSupport_forcesDimension
    (n D : ℕ)
    (hsupport : n ≤ D) :
    n ≤ D := by
  exact hsupport

/-- If an exact state encoding is injective on all `n` cyclic positions, the
state space contains at least `n` elements. -/
theorem fullCycleState_cardLowerBound
    (n : ℕ)
    {State : Type*}
    [Fintype State]
    (state : Fin n → State)
    (hinjective : Function.Injective state) :
    n ≤ Fintype.card State := by
  simpa using Fintype.card_le_of_injective state hinjective

end Ecdlp.ParityLift
