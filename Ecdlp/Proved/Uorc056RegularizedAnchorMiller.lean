import Mathlib

/-!
# UORC-056 C36 regularized anchor-Miller translation

This file kernel-checks the algebraic core used by C36:

* a shifted Miller quotient reduces to an `n`-th power once the
  same-subgroup commutator phase is one;
* ratios of two shifts and Frobenius norm-one quotients remain `n`-th
  powers of explicit gauges;
* the half-centered formula clears to a fractional-linear expression;
* exact secp256k1 arithmetic makes `n` coprime to `p^2-1`.

It does not formalize elliptic curves, Miller divisors, Weil reciprocity,
or the identification of the residual commutator with the Weil pairing.
Those geometric inputs are stated in the accompanying note and replayed
by exact executable finite-field calculations.
-/

namespace Ecdlp.Uorc056RegularizedAnchorMiller

/-- A normalized shifted value is the declared gauge power once its
    residual same-subgroup phase is one. -/
theorem shiftedValue_eq_gaugePow
    {K : Type*} [CommGroup K]
    (base shifted gauge : K) (n : Nat)
    (hshifted : shifted = base * gauge ^ n) :
    shifted / base = gauge ^ n := by
  rw [hshifted]
  simp

/-- Two regular shifts differ by the corresponding public gauge ratio
    raised to the same power. -/
theorem twoShiftRatio_eq_gaugeRatioPow
    {K : Type*} [CommGroup K]
    (first second hFirst hSecond : K) (n : Nat)
    (h1 : first = hFirst ^ n)
    (h2 : second = hSecond ^ n) :
    first / second = (hFirst / hSecond) ^ n := by
  rw [h1, h2, div_pow]

/-- The Frobenius norm-one quotient has exactly the same power form. -/
theorem normOneQuotient_eq_ratioPow
    {K : Type*} [CommGroup K]
    (h hConj : K) (n : Nat) :
    h ^ n / hConj ^ n = (h / hConj) ^ n := by
  exact (div_pow h hConj n).symm

/-- Constant products of same-subgroup shifted channels remain one
    explicit `n`-th power. -/
theorem productOfTwoGaugePowers
    {K : Type*} [CommMonoid K]
    (left right : K) (n : Nat) :
    left ^ n * right ^ n = (left * right) ^ n := by
  simpa using (mul_pow left right n).symm

/-- A bilinear alternating phase is trivial on two multiples of one
    generator. This is the abstract same-cyclic-subgroup pairing
    degeneracy used by C36. -/
theorem alternatingPhase_sameGenerator
    {A K : Type*} [AddCommMonoid A] [CommMonoid K]
    (phase : A → A → K)
    (hleft : ∀ (m : Nat) (x y : A),
      phase (m • x) y = phase x y ^ m)
    (hright : ∀ (m : Nat) (x y : A),
      phase x (m • y) = phase x y ^ m)
    (generator : A)
    (halt : phase generator generator = 1)
    (a b : Nat) :
    phase (a • generator) (b • generator) = 1 := by
  rw [hleft, hright, halt, one_pow, one_pow]

/-- Clearing the half-centered slope denominator yields a linear
    numerator in the Kummer coordinate `z`. -/
theorem mobiusNumerator_clear
    {K : Type*} [Field K]
    (yS yP mu c yH z xH : K)
    (hz : z - xH ≠ 0) :
    (yS + yP - (mu + 2 * yH / (z - xH)) * c) * (z - xH) =
      (yS + yP - mu * c) * (z - xH) - 2 * yH * c := by
  field_simp [hz]
  ring

/-- The same clearing identity for the denominator. -/
theorem mobiusDenominator_clear
    {K : Type*} [Field K]
    (yS yP mu c yH z xH : K)
    (hz : z - xH ≠ 0) :
    (-yS + yP - (mu + 2 * yH / (z - xH)) * c) * (z - xH) =
      (-yS + yP - mu * c) * (z - xH) - 2 * yH * c := by
  field_simp [hz]
  ring

def secpP : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def secpP2Minus1 : Nat := secpP * secpP - 1

theorem secpQuadraticPowerMapCoprime :
    Nat.gcd secpN secpP2Minus1 = 1 := by
  native_decide

theorem secpOrderOdd :
    secpN % 2 = 1 := by
  native_decide

theorem secpQuadraticExtensionOrderPositive :
    0 < secpP2Minus1 := by
  native_decide

end Ecdlp.Uorc056RegularizedAnchorMiller
