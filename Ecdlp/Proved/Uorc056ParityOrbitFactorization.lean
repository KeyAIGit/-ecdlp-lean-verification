import Mathlib

/-!
# UORC-056 C39 parity orbit factorization

This file kernel-checks the algebraic core of the orbit decoder:

* the canonical even/odd quotient returns the correct sign at either factor;
* the difference of the two factors is a square root of the public
  discriminant expression;
* swapping the ordered factors negates the decoder;
* every degree-minimal decoder satisfying the two divisibility identities is
  a constant recombination of the orbit factors;
* the secp256k1 half-size is strictly between `2^254` and `2^255`.

It does not formalize the half-index Miller function, the norm/resultant
construction, finite-field interpolation ranks, coefficient density, or an
arithmetic-circuit lower bound. Those are scoped to the mathematical note and
exact executable replay.
-/

namespace Ecdlp.Uorc056ParityOrbitFactorization

/-- The canonical decoder from ordered odd/even orbit factors. -/
def orbitDecoder {K : Type*} [Field K] (pEven pOdd : K) : K :=
  (pOdd - pEven) / (pOdd + pEven)

/-- At an even root, the canonical orbit decoder is `+1`. -/
theorem orbitDecoder_even
    {K : Type*} [Field K]
    (pEven pOdd : K)
    (hEven : pEven = 0)
    (hOdd : pOdd ≠ 0) :
    orbitDecoder pEven pOdd = 1 := by
  simp [orbitDecoder, hEven, hOdd]

/-- At an odd root, the canonical orbit decoder is `-1`. -/
theorem orbitDecoder_odd
    {K : Type*} [Field K]
    (pEven pOdd : K)
    (hOdd : pOdd = 0)
    (hEven : pEven ≠ 0) :
    orbitDecoder pEven pOdd = -1 := by
  simp [orbitDecoder, hOdd, hEven]

/-- The ordered difference is a square root of the unordered discriminant. -/
theorem orbitDiscriminant
    {K : Type*} [CommRing K]
    (pEven pOdd : K) :
    (pOdd - pEven) ^ 2 =
      (pOdd + pEven) ^ 2 - 4 * (pOdd * pEven) := by
  ring

/-- Swapping the ordered factors negates the decoder. -/
theorem orbitDecoder_swap
    {K : Type*} [Field K]
    (pEven pOdd : K)
    (hden : pOdd + pEven ≠ 0) :
    orbitDecoder pOdd pEven = -orbitDecoder pEven pOdd := by
  unfold orbitDecoder
  field_simp
  ring

/-- Algebraic classification of a degree-minimal decoder after the root-count
    argument supplies the two constant-multiple identities. -/
theorem minimalDecoderRecombination
    {K : Type*} [CommRing K]
    (A B c d pEven pOdd : K)
    (hMinus : A - B = c * pEven)
    (hPlus : A + B = d * pOdd) :
    2 * A = c * pEven + d * pOdd ∧
      2 * B = d * pOdd - c * pEven := by
  constructor
  · calc
      2 * A = (A - B) + (A + B) := by ring
      _ = c * pEven + d * pOdd := by rw [hMinus, hPlus]
  · calc
      2 * B = (A + B) - (A - B) := by ring
      _ = d * pOdd - c * pEven := by rw [hPlus, hMinus]

/-- The recombined decoder gives `+1` on the even factor when the odd factor
    and its coefficient are nonzero. -/
theorem recombinedDecoder_even
    {K : Type*} [Field K]
    (c d pEven pOdd : K)
    (hEven : pEven = 0)
    (hd : d ≠ 0)
    (hOdd : pOdd ≠ 0) :
    (c * pEven + d * pOdd) / (d * pOdd - c * pEven) = 1 := by
  simp [hEven, hd, hOdd]

/-- The recombined decoder gives `-1` on the odd factor when the even factor
    and its coefficient are nonzero. -/
theorem recombinedDecoder_odd
    {K : Type*} [Field K]
    (c d pEven pOdd : K)
    (hOdd : pOdd = 0)
    (hc : c ≠ 0)
    (hEven : pEven ≠ 0) :
    (c * pEven + d * pOdd) / (d * pOdd - c * pEven) = -1 := by
  simp [hOdd, hc, hEven]


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpHalf : Nat :=
  (secpN - 1) / 2


theorem secpHalfDegreeBoundary :
    2 ^ 254 < secpHalf ∧ secpHalf < 2 ^ 255 := by
  native_decide

end Ecdlp.Uorc056ParityOrbitFactorization
