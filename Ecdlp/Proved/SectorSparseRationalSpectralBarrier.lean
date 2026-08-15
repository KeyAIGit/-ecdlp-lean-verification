import Mathlib

/-!
# UORC-056 V18 sparse rational spectral sector barrier

This file kernel-checks the pointwise square-residual identities and the fixed
secp256k1 natural-number arithmetic used by V18.

It does not formalize the finite Fourier transform, convolution support,
cyclotomic divisibility, or the prime-order uncertainty theorem. Those
mathematical obligations are stated in the accompanying note and independently
replayed where finite arithmetic is available.
-/

namespace Ecdlp.SectorSparseRationalSpectralBarrier

variable {α R : Type*} [CommRing R]

/-- Exact quotient agreement with a sign forces the square residual
`A^2 - B^2` to vanish at that point. -/
theorem signedQuotient_squareResidual
    (A B J : R)
    (hA : A = J * B)
    (hJ : J ^ 2 = 1) :
    A ^ 2 - B ^ 2 = 0 := by
  rw [hA]
  calc
    (J * B) ^ 2 - B ^ 2 = (J ^ 2 - 1) * B ^ 2 := by ring
    _ = 0 := by rw [hJ]; ring

/-- On the positive sector, `A - B` vanishes. -/
theorem positiveSector_difference
    (A B : R)
    (h : A = B) :
    A - B = 0 := by
  rw [h]
  ring

/-- On the positive sector, `A + B` equals `2B`. -/
theorem positiveSector_sum
    (A B : R)
    (h : A = B) :
    A + B = 2 * B := by
  rw [h]
  ring

/-- On the negative sector, `A + B` vanishes. -/
theorem negativeSector_sum
    (A B : R)
    (h : A = -B) :
    A + B = 0 := by
  rw [h]
  ring

/-- On the negative sector, `A - B` equals `-2B`. -/
theorem negativeSector_difference
    (A B : R)
    (h : A = -B) :
    A - B = -(2 * B) := by
  rw [h]
  ring

/-- Arithmetic certificate consumed after the nonzero-residual sumset
argument. -/
theorem pairCoverCertificate
    (n t : Nat)
    (hcover : n ≤ t * (t + 1) / 2) :
    n ≤ t * (t + 1) / 2 :=
  hcover

/-- Arithmetic certificate consumed after applying prime-order uncertainty
to `A - B`. -/
theorem uncertaintyDifferenceCertificate
    (n negativeFiber support : Nat)
    (h : n - negativeFiber ≤ support) :
    n - negativeFiber ≤ support :=
  h

/-- Arithmetic certificate consumed after applying prime-order uncertainty
to `A + B`. -/
theorem uncertaintySumCertificate
    (n positiveFiber support : Nat)
    (h : n - positiveFiber ≤ support) :
    n - positiveFiber ≤ support :=
  h

def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def secpRootSupportLowerBound : Nat :=
  481231938336009023090067544955250113853

def secpNonzeroPlusScalars : Nat :=
  57896044618658097711785492504343953926418782139537452191302581570759080747272

def secpNonzeroMinusScalars : Nat :=
  57896044618658097711785492504343953926418782139537452191302581570759080747064

def secpDifferenceSupportLowerBound : Nat :=
  57896044618658097711785492504343953926418782139537452191302581570759080747273

def secpSumSupportLowerBound : Nat :=
  57896044618658097711785492504343953926418782139537452191302581570759080747065

def secpSquareExactSupportLowerBound : Nat :=
  secpDifferenceSupportLowerBound

theorem secpPairCoverAtBound :
    secpN ≤
      secpRootSupportLowerBound *
        (secpRootSupportLowerBound + 1) / 2 := by
  native_decide

theorem secpPairCoverBelowBoundFails :
    (secpRootSupportLowerBound - 1) *
        secpRootSupportLowerBound / 2 <
      secpN := by
  native_decide

theorem secpRootSupportExceedsTwoPow128 :
    2 ^ 128 < secpRootSupportLowerBound := by
  native_decide

theorem secpRootSupportBelowTwoPow129 :
    secpRootSupportLowerBound < 2 ^ 129 := by
  native_decide

theorem secpSectorFibersPartitionNonzero :
    secpNonzeroPlusScalars + secpNonzeroMinusScalars = secpN - 1 := by
  native_decide

theorem secpSectorFiberDifference :
    secpNonzeroPlusScalars - secpNonzeroMinusScalars = 208 := by
  native_decide

theorem secpDifferenceUncertaintyArithmetic :
    secpN - secpNonzeroMinusScalars =
      secpDifferenceSupportLowerBound := by
  native_decide

theorem secpSumUncertaintyArithmetic :
    secpN - secpNonzeroPlusScalars =
      secpSumSupportLowerBound := by
  native_decide

theorem secpSquareExactBoundIsDifferenceBound :
    secpSquareExactSupportLowerBound =
      secpNonzeroPlusScalars + 1 := by
  native_decide

theorem secpSquareExactStrongerThanRootBound :
    secpRootSupportLowerBound <
      secpSquareExactSupportLowerBound := by
  native_decide

theorem secpSquareExactExceedsTwoPow254 :
    2 ^ 254 < secpSquareExactSupportLowerBound := by
  native_decide

theorem secpSquareExactBelowTwoPow255 :
    secpSquareExactSupportLowerBound < 2 ^ 255 := by
  native_decide

end Ecdlp.SectorSparseRationalSpectralBarrier
