import Mathlib

/-!
# Within-curve phase lookup orientation boundary

This file records the exact binary symmetry bookkeeping used by
`SECP-13441-WITHIN-CURVE-CV-024`.

The order-13441 phase is invariant under scalar negation.  The GLV carry bit is
anti-invariant.  Therefore a prediction depending only on the phase makes the
same prediction on a negation pair while the two carry labels are opposite;
its two error bits are complementary.

Multiplying by a public anti-invariant orientation, such as a centered `y` sign
or a quadratic character of `y`, converts the carry into a negation-invariant
residual target.  A learned residual can then be converted back to carry using
the same public orientation.

Lean proves only these bit identities.  It does not formalize the phase,
C6-orbit cross-validation, or the statistical admission gate.
-/

namespace Ecdlp.ParityLift

/-- Prediction error for binary multiplicative signs represented additively in
`ZMod 2`. -/
def binaryPredictionError
    (prediction target : ZMod 2) : ZMod 2 :=
  prediction + target

/-- The same phase-only prediction on two opposite labels has complementary
error bits. -/
theorem invariantPrediction_antiInvariantTarget_pairErrors
    (prediction target : ZMod 2) :
    binaryPredictionError prediction target +
      binaryPredictionError prediction (target + 1) = 1 := by
  fin_cases prediction <;> fin_cases target <;> native_decide

/-- If both the target and a public orientation flip under negation, their
residual product is invariant. -/
theorem antiInvariantTarget_orientation_residualInvariant
    (target orientation : ZMod 2) :
    (target + 1) + (orientation + 1) = target + orientation := by
  fin_cases target <;> fin_cases orientation <;> native_decide

/-- A residual prediction is converted back to the original target by applying
the public orientation once more. -/
theorem orientedResidual_recoversTarget
    (target orientation : ZMod 2) :
    (target + orientation) + orientation = target := by
  fin_cases target <;> fin_cases orientation <;> native_decide

/-- Applying the public orientation to both a residual prediction and the true
residual preserves their error bit. -/
theorem orientedResidual_preservesPredictionError
    (prediction target orientation : ZMod 2) :
    binaryPredictionError
        (prediction + orientation)
        (target + orientation) =
      binaryPredictionError prediction target := by
  fin_cases prediction <;>
    fin_cases target <;>
      fin_cases orientation <;>
        native_decide

end Ecdlp.ParityLift
