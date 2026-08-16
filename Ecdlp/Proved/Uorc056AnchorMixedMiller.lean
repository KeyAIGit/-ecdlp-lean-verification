import Mathlib

/-!
# UORC-056 C35 shifted Miller gauge boundary

This file kernel-checks the algebraic core used by C35:

* two evaluations of one shifted Miller gauge eliminate their unknown common
  normalization by cross multiplication;
* two evaluations of the torus/Kummer relation eliminate their unknown common
  normalization in the same way;
* an n-th-power map can be inverted on an element of order dividing m once
  `n * r = 1 mod m` is supplied;
* the concrete secp256k1 coprimality and inverse-exponent certificates for
  `p-1`, `p+1`, and `p^2-1`.

The divisor calculations, local Miller-section construction, quadratic-
extension replay, character histograms, and rational-decoder root counts are
proved in the accompanying note and checked by exact Python. They are not
silently labeled as Lean theorems here.
-/

namespace Ecdlp.Uorc056AnchorMixedMiller

/-- Cross-multiplied normalized shift-gauge identity. The hypotheses model
`m(P) g(P)^n = c f(P)` at two public points. The unknown common scalar `c`
cancels. -/
theorem normalized_shift_gauge_cross
    {R : Type*} [CommMonoid R]
    (mP m0 fP f0 gP g0 c : R)
    (n : Nat)
    (hP : mP * gP ^ n = c * fP)
    (h0 : m0 * g0 ^ n = c * f0) :
    mP * f0 * gP ^ n = m0 * fP * g0 ^ n := by
  calc
    mP * f0 * gP ^ n = f0 * (mP * gP ^ n) := by ac_rfl
    _ = f0 * (c * fP) := by rw [hP]
    _ = fP * (c * f0) := by ac_rfl
    _ = fP * (m0 * g0 ^ n) := by rw [h0]
    _ = m0 * fP * g0 ^ n := by ac_rfl

/-- Cross-multiplied normalized torus/Kummer identity. If two torus values have
one common scalar normalization times an n-th power, the normalization
cancels. -/
theorem normalized_torus_cross
    {R : Type*} [CommMonoid R]
    (tP t0 rP r0 lambda : R)
    (n : Nat)
    (hP : tP = lambda * rP ^ n)
    (h0 : t0 = lambda * r0 ^ n) :
    tP * r0 ^ n = t0 * rP ^ n := by
  rw [hP, h0]
  ac_rfl

/-- If `z^m = 1` and `n*r = 1 + q*m`, exponentiation by `r` recovers `z`
from `z^n`. This is the abstract algebra behind the public inverse exponent on
`F_p^*`, the norm-one torus, and `F_(p^2)^*`. -/
theorem recover_from_coprime_power
    {R : Type*} [Monoid R]
    (z : R)
    (n r m q : Nat)
    (hexponent : n * r = 1 + q * m)
    (horder : z ^ m = 1) :
    (z ^ n) ^ r = z := by
  calc
    (z ^ n) ^ r = z ^ (n * r) := by
      simpa using (pow_mul z n r).symm
    _ = z ^ (1 + q * m) := by rw [hexponent]
    _ = z * z ^ (q * m) := by rw [pow_add, pow_one]
    _ = z * z ^ (m * q) := by rw [Nat.mul_comm q m]
    _ = z * (z ^ m) ^ q := by rw [pow_mul]
    _ = z := by rw [horder, one_pow, mul_one]


def secpP : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpP2MinusOne : Nat := secpP ^ 2 - 1


def secpInverseNModPMinusOne : Nat :=
  32393677620855434490503476718741331181544936338401395921493940466534500759435


def secpInverseNModPPlusOne : Nat :=
  79207552422331657165126911011852759371753461673363963763919063432758971963937


def secpInverseNModP2MinusOne : Nat :=
  3993565780692757165664246821601600670194293395206194842632201512277833189089668065828959777066409387784695222179016361079589771916642201863092356595241057


theorem secpCoprimePMinusOne :
    Nat.gcd secpN (secpP - 1) = 1 := by
  native_decide


theorem secpCoprimePPlusOne :
    Nat.gcd secpN (secpP + 1) = 1 := by
  native_decide


theorem secpCoprimeP2MinusOne :
    Nat.gcd secpN secpP2MinusOne = 1 := by
  native_decide


theorem secpInverseNModPMinusOneCertificate :
    (secpN * secpInverseNModPMinusOne) % (secpP - 1) = 1 := by
  native_decide


theorem secpInverseNModPPlusOneCertificate :
    (secpN * secpInverseNModPPlusOne) % (secpP + 1) = 1 := by
  native_decide


theorem secpInverseNModP2MinusOneCertificate :
    (secpN * secpInverseNModP2MinusOne) % secpP2MinusOne = 1 := by
  native_decide

end Ecdlp.Uorc056AnchorMixedMiller
