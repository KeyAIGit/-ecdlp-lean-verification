import Mathlib

/-!
# UORC-056 C55 cycle label and open-translation boundary

This file kernel-checks the elementary algebra behind the exact doubling-cycle
labels and the arbitrary-decoder collision. It does not formalize rational
functions on elliptic curves, the pole-degree argument, the finite-field replay,
or an unrestricted complexity lower bound.
-/

namespace Ecdlp.Uorc056CycleLabelOpenTranslation

/-- If `two^m=1`, the power label `k^m` is invariant under multiplication by
    `two`. -/
theorem cycleLabelInvariant
    {R : Type*} [CommMonoid R]
    (two k : R) (m : Nat)
    (horder : two ^ m = 1) :
    (two * k) ^ m = k ^ m := by
  rw [mul_pow, horder, one_mul]

/-- If the exponent sends `-1` to `-1`, the full cycle label changes sign under
    negation. -/
theorem cycleLabelNegation
    {R : Type*} [CommRing R]
    (k : R) (m : Nat)
    (hodd : (-1 : R) ^ m = -1) :
    (-k) ^ m = -(k ^ m) := by
  calc
    (-k) ^ m = ((-1 : R) * k) ^ m := by ring_nf
    _ = (-1 : R) ^ m * k ^ m := by rw [mul_pow]
    _ = -(k ^ m) := by rw [hodd]; ring

/-- Squaring the exponent removes the sign of the cycle label. -/
theorem pairCycleLabelNegation
    {R : Type*} [CommRing R]
    (k : R) (m : Nat) :
    (-k) ^ (2 * m) = k ^ (2 * m) := by
  calc
    (-k) ^ (2 * m) = ((-k) ^ 2) ^ m := by rw [pow_mul]
    _ = (k ^ 2) ^ m := by congr 1 <;> ring
    _ = k ^ (2 * m) := by rw [pow_mul]

/-- A cycle-invariant state shared by opposite target signs cannot decode point
    parity in characteristic different from two. -/
theorem cycleInvariantCannotDecodeOpposite
    {S K : Type*} [Field K]
    (decode : S → K) (evenPoint oddPoint : S)
    (hsame : evenPoint = oddPoint)
    (heven : decode evenPoint = 1)
    (hodd : decode oddPoint = -1)
    (htwo : (2 : K) ≠ 0) :
    False := by
  have hone : (1 : K) = -1 := by
    calc
      (1 : K) = decode evenPoint := heven.symm
      _ = decode oddPoint := by rw [hsame]
      _ = -1 := hodd
  have hz : (2 : K) = 0 := by
    calc
      (2 : K) = 1 - (-1) := by ring
      _ = 0 := sub_eq_zero.mpr hone
  exact htwo hz

/-- The arithmetic implication used by the scoped pole-degree boundary. -/
theorem poleDegreeBoundary
    (n d : Nat)
    (h : n - 1 ≤ 5 * d) :
    (n - 1 + 4) / 5 ≤ d := by
  omega


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpOrdTwo : Nat :=
  (secpN - 1) / 64


def secpCycleInvariantDegreeLowerBound : Nat :=
  (secpN - 1 + 4) / 5


def secpGenericWithinCycleBsgs : Nat :=
  42535295865117307932921825928971026432


theorem secpDoublingOrderOdd : secpOrdTwo % 2 = 1 := by
  native_decide


theorem secpFullCycleCount : (secpN - 1) / secpOrdTwo = 64 := by
  native_decide


theorem secpPairCycleCount : (secpN - 1) / (2 * secpOrdTwo) = 32 := by
  native_decide


theorem secpDegreeLowerBoundValue :
    secpCycleInvariantDegreeLowerBound =
      23158417847463239084714197001737581570567512855814980876521032628303632298868 := by
  native_decide


theorem secpBsgsSquareCoversCycle :
    secpOrdTwo ≤ secpGenericWithinCycleBsgs ^ 2 := by
  native_decide

end Ecdlp.Uorc056CycleLabelOpenTranslation
