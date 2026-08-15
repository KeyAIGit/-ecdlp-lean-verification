import Mathlib
import Ecdlp.Proved.Uorc056OrientedAdditionCocycle

/-!
# UORC-056 C34 dynamic carry aggregation

This file kernel-checks the algebraic core of C34:

* an addition gate combines two compiled aggregates by one carry factor;
* the resulting aggregate depends only on the terminal weight;
* three suitably related carry factors multiply to the original sign;
* equal generator-blind public data cannot decode opposite marked targets;
* fixed secp256k1 multiplier arithmetic for the three-carry identity.

It does not formalize the Python addition-DAG compiler, the finite exhaustive
single-carry classification, Miller functions, elliptic nets or a public
carry evaluator.
-/

namespace Ecdlp.Uorc056DynamicCarryAggregation

/-- Scalar form of the compiled aggregate A_m. -/
def scalarAggregate
    {R : Type*} [Monoid R]
    (base terminal : R) (m : Nat) : R :=
  base ^ m * terminal

/-- One addition gate preserves the aggregate normal form. -/
theorem aggregate_gate
    {R : Type*} [CommMonoid R]
    (base left right terminal : R)
    (a b : Nat)
    (hleft : left * left = 1)
    (hright : right * right = 1) :
    (left * right * terminal) *
        scalarAggregate base left a *
        scalarAggregate base right b =
      scalarAggregate base terminal (a + b) := by
  unfold scalarAggregate
  calc
    (left * right * terminal) * (base ^ a * left) * (base ^ b * right) =
        (base ^ a * base ^ b) *
          (left * left) * (right * right) * terminal := by
      ac_rfl
    _ = base ^ (a + b) * terminal := by
      rw [hleft, hright, pow_add]
      simp

/-- Abstract three-carry compression. The variables correspond to the signs at
    Q, A, B, T, U=Q+A, -T and -B. -/
theorem three_carry_compression
    {R : Type*} [CommRing R]
    (sQ sA sB sT sU sNegT sNegB : R)
    (hA : sA * sA = 1)
    (hU : sU * sU = 1)
    (hB : sB * sNegB = -1)
    (hT : sT * sNegT = -1) :
    (sQ * sA * sU) *
        (sA * sB * sT) *
        (sNegT * sNegB * sU) = sQ := by
  calc
    (sQ * sA * sU) * (sA * sB * sT) * (sNegT * sNegB * sU) =
        sQ * (sA * sA) * (sU * sU) *
          (sB * sNegB) * (sT * sNegT) := by
      ring
    _ = sQ := by
      rw [hA, hU, hB, hT]
      ring

/-- A state generated from identical public data cannot decode two separated
    generator-relative targets. -/
theorem generator_blind_decoder_obstruction
    {Input State Output : Type*}
    (state : Input -> State)
    (decoder : State -> Output)
    (left right : Input)
    (hpublic : state left = state right)
    (targetLeft targetRight : Output)
    (hleft : decoder (state left) = targetLeft)
    (hright : decoder (state right) = targetRight)
    (hsep : targetLeft ≠ targetRight) :
    False := by
  apply hsep
  calc
    targetLeft = decoder (state left) := hleft.symm
    _ = decoder (state right) := congrArg decoder hpublic
    _ = targetRight := hright

/-- If two compiled carry products both satisfy the same aggregate normal form,
    then they agree pointwise. -/
theorem chain_independent_of_common_aggregate
    {R : Type*}
    (first second aggregate : R)
    (hfirst : first = aggregate)
    (hsecond : second = aggregate) :
    first = second := by
  exact hfirst.trans hsecond.symm


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpHalf : Nat :=
  (secpN - 1) / 2


def secpInverseTwo : Nat :=
  (secpN + 1) / 2


def secpThreeCarryA : Nat := 2


def secpThreeCarryT : Nat := secpHalf


def secpThreeCarryB : Nat := secpThreeCarryT - secpThreeCarryA


theorem secpThreeCarrySumCertificate :
    secpThreeCarryA + secpThreeCarryB = secpThreeCarryT := by
  native_decide


theorem secpThreeCarryDoubleTCertificate :
    (2 * secpThreeCarryT) % secpN = secpN - 1 := by
  native_decide


theorem secpThreeCarryThirdSumCertificate :
    (secpInverseTwo + (secpInverseTwo + secpThreeCarryA)) % secpN =
      (1 + secpThreeCarryA) % secpN := by
  native_decide


theorem secpThreeCarryMultipliersNonzero :
    secpThreeCarryA ≠ 0 ∧
    secpThreeCarryB ≠ 0 ∧
    secpThreeCarryT ≠ 0 ∧
    secpInverseTwo ≠ 0 := by
  native_decide

end Ecdlp.Uorc056DynamicCarryAggregation
