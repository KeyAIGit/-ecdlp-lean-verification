import Mathlib

/-!
# UORC-056 V19 direct shared parity Cauchy barrier

This file kernel-checks the point-defect decomposition and the fixed natural-
number arithmetic used by V19.

It does not formalize finite Fourier transforms, support convolution, the
Cauchy double-alternant determinant, or the transfer from Cauchy full spark to
spectral support. Those obligations are stated explicitly in the accompanying
note and replayed over exact finite fields.
-/

namespace Ecdlp.SharedParityCauchyBarrier

variable {ι R : Type*} [DecidableEq ι] [CommRing R]

/-- The one-point defect between `A` and the pointwise product `sigma * B`. -/
def pointDefect (anchor : ι) (A B sigma : ι → R) : ι → R :=
  fun k =>
    if k = anchor then
      A anchor - sigma anchor * B anchor
    else
      0

/-- Agreement away from one anchor is exactly a pointwise product plus a
one-point defect. This is the algebraic input to the V19 Fourier system. -/
theorem agreementOffAnchor_decomposition
    (anchor : ι)
    (A B sigma : ι → R)
    (h : ∀ k, k ≠ anchor → A k = sigma k * B k) :
    A = fun k => sigma k * B k + pointDefect anchor A B sigma k := by
  funext k
  by_cases hk : k = anchor
  · subst k
    simp [pointDefect] <;> ring
  · simp [pointDefect, hk, h k hk]

/-- If two separately counted supports lie in one dictionary of size `t`, a
lower bound on their sum transfers to twice the dictionary size. -/
theorem sharedDictionaryTransfer
    (a b t n : Nat)
    (ha : a ≤ t)
    (hb : b ≤ t)
    (hsum : n ≤ a + b) :
    n ≤ 2 * t := by
  omega

/-- Arithmetic certificate consumed after the one-bilinear-gate support
transfer. -/
theorem bilinearProductCertificate
    (target a b : Nat)
    (h : target ≤ a * b) :
    target ≤ a * b :=
  h

/-- Arithmetic certificate consumed after the shared-dictionary sumset
transfer. -/
theorem pairCoverCertificate
    (target t : Nat)
    (h : target ≤ t * (t + 1) / 2) :
    target ≤ t * (t + 1) / 2 :=
  h

/-- Arithmetic certificate consumed after the Cauchy full-spark argument. -/
theorem rationalSeparateSupportCertificate
    (n a b : Nat)
    (h : n ≤ a + b) :
    n ≤ a + b :=
  h

def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def secpFreeIdentityParitySupport : Nat :=
  secpN - 1

def secpRationalSeparateSupportLowerBound : Nat :=
  secpN

def secpRationalCanonicalSupportLowerBound : Nat :=
  secpN + 1

def secpRationalSharedUnionLowerBound : Nat :=
  57896044618658097711785492504343953926418782139537452191302581570759080747169

def secpBilinearLeftSupport : Nat :=
  340282366920938463463374607431768211455

def secpBilinearRightSupport : Nat :=
  340282366920938463463374607431768211456

def secpBilinearLeafSumLowerBound : Nat :=
  680564733841876926926749214863536422911

def secpBilinearDictionaryLowerBound : Nat :=
  481231938336009023090067544955250113853

theorem secpFreeIdentitySupportArithmetic :
    secpFreeIdentityParitySupport =
      115792089237316195423570985008687907852837564279074904382605163141518161494336 := by
  native_decide

theorem secpRationalSeparateSupportArithmetic :
    secpRationalSeparateSupportLowerBound =
      115792089237316195423570985008687907852837564279074904382605163141518161494337 := by
  native_decide

theorem secpRationalCanonicalSupportArithmetic :
    secpRationalCanonicalSupportLowerBound =
      115792089237316195423570985008687907852837564279074904382605163141518161494338 := by
  native_decide

theorem secpRationalUnionAtBound :
    secpN ≤ 2 * secpRationalSharedUnionLowerBound := by
  native_decide

theorem secpRationalUnionBelowBoundFails :
    2 * (secpRationalSharedUnionLowerBound - 1) < secpN := by
  native_decide

theorem secpRationalUnionExceedsTwoPow254 :
    2 ^ 254 < secpRationalSharedUnionLowerBound := by
  native_decide

theorem secpRationalUnionBelowTwoPow255 :
    secpRationalSharedUnionLowerBound < 2 ^ 255 := by
  native_decide

theorem secpRationalSeparateExceedsTwoPow255 :
    2 ^ 255 < secpRationalSeparateSupportLowerBound := by
  native_decide

theorem secpRationalSeparateBelowTwoPow256 :
    secpRationalSeparateSupportLowerBound < 2 ^ 256 := by
  native_decide

theorem secpBilinearLeafSumArithmetic :
    secpBilinearLeftSupport + secpBilinearRightSupport =
      secpBilinearLeafSumLowerBound := by
  native_decide

theorem secpBilinearProductAtBound :
    secpN - 1 ≤ secpBilinearLeftSupport * secpBilinearRightSupport := by
  native_decide

theorem secpBilinearPreviousSumFails :
    secpBilinearLeftSupport * secpBilinearLeftSupport < secpN - 1 := by
  native_decide

theorem secpBilinearLeafSumIsTwoPow129MinusOne :
    secpBilinearLeafSumLowerBound = 2 ^ 129 - 1 := by
  native_decide

theorem secpBilinearDictionaryAtBound :
    secpN - 1 ≤
      secpBilinearDictionaryLowerBound *
        (secpBilinearDictionaryLowerBound + 1) / 2 := by
  native_decide

theorem secpBilinearDictionaryBelowBoundFails :
    (secpBilinearDictionaryLowerBound - 1) *
        secpBilinearDictionaryLowerBound / 2 <
      secpN - 1 := by
  native_decide

theorem secpBilinearDictionaryExceedsTwoPow128 :
    2 ^ 128 < secpBilinearDictionaryLowerBound := by
  native_decide

theorem secpBilinearDictionaryBelowTwoPow129 :
    secpBilinearDictionaryLowerBound < 2 ^ 129 := by
  native_decide

end Ecdlp.SharedParityCauchyBarrier
