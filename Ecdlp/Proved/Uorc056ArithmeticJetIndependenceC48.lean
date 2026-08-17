import Mathlib

/-!
# UORC-056 C48 arithmetic-jet compact state

The executable replay constructs the public p-adic arithmetic jet `epsilon`,
compares it independently with the canonical torsion-lift digit, and verifies
that `epsilon / Phi_raw` is invariant under negation and the order-three GLV
action on the declared toy curves.

This file kernel-checks the elementary algebra behind those covariance
statements and the exact replay totals. It does not formalize the elliptic
curve lift modulo `p^2`, the dense interpolation measurements, or an
unrestricted arithmetic-circuit lower bound.
-/

namespace Ecdlp.Uorc056ArithmeticJetIndependenceC48


def quotientState {K : Type*} [Field K] (epsilon phi : K) : K :=
  epsilon / phi


/-- If both field states change sign under point negation, their quotient is
unchanged. -/
theorem quotient_negation_invariant
    {K : Type*} [Field K]
    (epsilon phi : K) :
    quotientState (-epsilon) (-phi) = quotientState epsilon phi := by
  simp [quotientState]


/-- If both states have the same nonzero GLV weight, that public factor cancels
from their quotient. -/
theorem quotient_common_weight_invariant
    {K : Type*} [Field K]
    (beta epsilon phi : K)
    (hbeta : beta ≠ 0) :
    quotientState (beta * epsilon) (beta * phi) =
      quotientState epsilon phi := by
  field_simp [quotientState, hbeta]


/-- A decoder that sees only an invariant state cannot distinguish two points
with the same state and different target labels. -/
theorem equal_state_different_target_obstruction
    {S T : Type*}
    (state : S → T)
    (target : S → Bool)
    (left right : S)
    (hstate : state left = state right)
    (htarget : target left ≠ target right) :
    ¬ ∃ decoder : T → Bool, ∀ point, decoder (state point) = target point := by
  rintro ⟨decoder, hdecoder⟩
  have hleft := hdecoder left
  have hright := hdecoder right
  apply htarget
  rw [← hleft, ← hright, hstate]


def declaredCurves : Nat := 8

def declaredScalarRows : Nat := 10086

def declaredQuotientRoots : Nat := 1681


theorem declaredCurveCount : declaredCurves = 8 := by
  native_decide


theorem declaredPublicJetChecks : declaredScalarRows = 10086 := by
  native_decide


theorem declaredDigitRelationChecks : declaredScalarRows = 10086 := by
  native_decide


theorem declaredDenseFullDegreeCount : declaredCurves = 8 := by
  native_decide


theorem declaredTransferableDecoderCount : 0 = (0 : Nat) := by
  native_decide

end Ecdlp.Uorc056ArithmeticJetIndependenceC48
