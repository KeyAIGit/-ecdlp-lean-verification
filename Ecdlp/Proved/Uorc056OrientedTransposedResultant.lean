import Mathlib

/-!
# UORC-056 C42 oriented transposed resultant

This file kernel-checks the elementary algebraic core used by C42:

* target-root localization of the two oriented branches;
* the cubic relative-norm determinant for `X^3 = T`;
* exact secp256k1 degree arithmetic after the GLV block decomposition.

It does not formalize Miller functions, the elliptic-curve divisor identities,
finite-field interpolation, coefficient density, resultants, or an unrestricted
complexity lower bound. Those claims remain in the mathematical note and exact
executable replay.
-/

namespace Ecdlp.Uorc056OrientedTransposedResultant

/-- At a query value `z = a + y*b`, the difference-over-sum of the two
    plus-or-minus `Y*b` branches returns the relative orientation `s` when
    `Y=s*y`. -/
theorem localizedBranchDecoder
    {K : Type*} [Field K]
    (a b y s : K)
    (htwo : (2 : K) ≠ 0)
    (hy : y ≠ 0)
    (hb : b ≠ 0) :
    (((a + y * b - a + s * y * b) - (a + y * b - a - s * y * b)) /
      ((a + y * b - a + s * y * b) + (a + y * b - a - s * y * b))) = s := by
  have hyb : y * b ≠ 0 := mul_ne_zero hy hb
  have hden : (2 : K) * (y * b) ≠ 0 := mul_ne_zero htwo hyb
  rw [show
      (a + y * b - a + s * y * b) + (a + y * b - a - s * y * b)
        = (2 : K) * (y * b) by ring]
  apply (div_eq_iff hden).2
  ring

/-- Relative cubic norm of `c0 + X*c1 + X^2*c2` under `X^3=T`. -/
def cubicNorm {R : Type*} [CommRing R] (t c0 c1 c2 : R) : R :=
  c0 ^ 3 + t * c1 ^ 3 + t ^ 2 * c2 ^ 3 - 3 * t * c0 * c1 * c2

/-- The determinant of the multiplication matrix in the basis
    `[1, X, X^2]`, with `X^3=T`, is the cubic relative norm. -/
theorem cubicMultiplicationDeterminant
    {R : Type*} [CommRing R]
    (t c0 c1 c2 : R) :
    c0 * (c0 * c0 - (t * c2) * c1)
      - (t * c2) * (c1 * c0 - (t * c2) * c2)
      + (t * c1) * (c1 * c1 - c0 * c2)
      = cubicNorm t c0 c1 c2 := by
  unfold cubicNorm
  ring


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpHalfDegree : Nat :=
  (secpN - 1) / 2


def secpGlvBlockDegree : Nat :=
  (secpN - 1) / 6


def secpGlvBlockSqrtCeil : Nat :=
  138919694570470098040331481282401564370


def secpTwoLevelBaby : Nat :=
  138919694570470098040331481282401564369


def secpTwoLevelGiant : Nat :=
  138919694570470098040331481282401564370


theorem secpOrderModSix : secpN % 6 = 1 := by
  native_decide


theorem secpHalfIsThreeGlvBlocks :
    secpHalfDegree = 3 * secpGlvBlockDegree := by
  native_decide


theorem secpGlvBlockExact :
    secpGlvBlockDegree =
      19298681539552699237261830834781317975472927379845817397100860523586360249056 := by
  native_decide


theorem secpGlvBlockBitBoundary :
    2 ^ 253 < secpGlvBlockDegree ∧ secpGlvBlockDegree < 2 ^ 254 := by
  native_decide


theorem secpGlvBlockSqrtCertificate :
    (secpGlvBlockSqrtCeil - 1) ^ 2 < secpGlvBlockDegree ∧
      secpGlvBlockDegree ≤ secpGlvBlockSqrtCeil ^ 2 := by
  native_decide


theorem secpTwoLevelWitness :
    secpGlvBlockDegree ≤ secpTwoLevelBaby * secpTwoLevelGiant ∧
      secpTwoLevelBaby + secpTwoLevelGiant =
        277839389140940196080662962564803128739 := by
  native_decide

end Ecdlp.Uorc056OrientedTransposedResultant
