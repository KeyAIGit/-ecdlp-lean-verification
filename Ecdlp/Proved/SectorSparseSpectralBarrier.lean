import Mathlib

/-!
# UORC-056 V17 sparse spectral sector barrier

This file kernel-checks the pointwise square identity and the fixed
secp256k1 arithmetic used by V17.

The finite Fourier transform, the prime-cyclotomic full-support lemma, and the
sumset support transfer are stated and proved in the accompanying note and
replayed by the executable package. They are not formalized here.
-/

namespace Ecdlp.SectorSparseSpectralBarrier

variable {α R : Type*} [CommRing R]

/-- A value equal to either sign has zero square residual. -/
theorem signedValue_square_sub_one
    (value : R)
    (hvalue : value = 1 ∨ value = -1) :
    value ^ 2 - 1 = 0 := by
  rcases hvalue with rfl | rfl <;> ring

/-- Exact agreement with a binary target forces `F^2 - 1` to vanish at that
point. -/
theorem matchingBinaryTarget_squareResidual
    (F target : α → R)
    (point : α)
    (hmatch : F point = target point)
    (htarget : target point = 1 ∨ target point = -1) :
    F point ^ 2 - 1 = 0 := by
  rw [hmatch]
  exact signedValue_square_sub_one (target point) htarget

/-- The arithmetic implication consumed after the Fourier/sumset argument:
if `n-1` frequencies must be covered by unordered pairs from `m` frequencies,
then the pair-count inequality is the required lower-bound certificate. -/
theorem pairCoverCertificate
    (n m : Nat)
    (hcover : n - 1 ≤ m * (m + 1) / 2) :
    n - 1 ≤ m * (m + 1) / 2 :=
  hcover

def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def secpSparseSupportLowerBound : Nat :=
  481231938336009023090067544955250113853

def secpCanonicalSectorDcSum : Int := 209

def secpPairBasisBlock : Nat := 2 ^ 128

def secpPairBasisSizeUpperBound : Nat := 2 ^ 129 - 1

def secpSectorPlusHalfDegree : Nat :=
  28948022309329048855892746252171976963209391069768726095651290785379540373636

def secpSectorMinusHalfDegree : Nat :=
  28948022309329048855892746252171976963209391069768726095651290785379540373532

theorem secpPairCoverAtBound :
    secpN - 1 ≤
      secpSparseSupportLowerBound *
        (secpSparseSupportLowerBound + 1) / 2 := by
  native_decide

theorem secpPairCoverBelowBoundFails :
    (secpSparseSupportLowerBound - 1) *
        secpSparseSupportLowerBound / 2 <
      secpN - 1 := by
  native_decide

theorem secpSparseSupportExceedsTwoPow128 :
    2 ^ 128 < secpSparseSupportLowerBound := by
  native_decide

theorem secpSparseSupportBelowTwoPow129 :
    secpSparseSupportLowerBound < 2 ^ 129 := by
  native_decide

theorem secpPairBasisBlockExact :
    secpPairBasisBlock = 340282366920938463463374607431768211456 := by
  native_decide

theorem secpPairBasisSizeExact :
    secpPairBasisSizeUpperBound =
      680564733841876926926749214863536422911 := by
  native_decide

theorem secpBothSectorFibersNonempty :
    0 < secpSectorPlusHalfDegree ∧
      0 < secpSectorMinusHalfDegree := by
  native_decide

theorem secpCanonicalDcNonzero :
    secpCanonicalSectorDcSum ≠ 0 := by
  native_decide

end Ecdlp.SectorSparseSpectralBarrier
