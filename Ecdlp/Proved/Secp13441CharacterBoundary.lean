import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# The order-13441 field character on secp256k1

This file records the exact arithmetic boundary used by
`SECP-13441-CHARACTER-HELDOUT-022`.

The secp256k1 field satisfies

`p - 1 = 2 * 3 * 7 * 13441 * q`.

Consequently an order-13441 multiplicative character exists in the base field,
and its exponent `(p-1)/13441` is divisible by three.  Any order-three GLV
field multiplier therefore disappears after raising to that exponent.

Lean proves only these finite arithmetic and group identities.  It does not
formalize the public perfectly-periodic point function, the toy held-out
screen, or any universal lookup-table decoder.
-/

namespace Ecdlp.ParityLift

/-- The medium-size prime factor of the secp256k1 base-field multiplicative
order used by this package. -/
def secp13441CharacterOrder : ℕ := 13441

/-- The corresponding power-residue exponent. -/
def secp13441CharacterExponent : ℕ :=
  (Secp256k1.p - 1) / secp13441CharacterOrder

/-- The remaining exact cofactor after removing `2 * 3 * 7 * 13441`. -/
def secp13441RemainingCofactor : ℕ :=
  205115282021455665897114700593932402728804164701536103180137503955397371

/-- `13441` is prime. -/
theorem secp13441CharacterOrder_prime :
    Nat.Prime secp13441CharacterOrder := by
  native_decide

/-- Exact factorization used by the experiment.  No primality claim for the
remaining cofactor is needed by the character argument. -/
theorem secp256k1FieldOrder_factorization_13441 :
    Secp256k1.p - 1 =
      2 * 3 * 7 * secp13441CharacterOrder * secp13441RemainingCofactor := by
  native_decide

/-- The order `13441` divides the base-field multiplicative order. -/
theorem secp13441CharacterOrder_dvd_fieldOrder :
    secp13441CharacterOrder ∣ Secp256k1.p - 1 := by
  native_decide

/-- The character exponent is divisible by three, so an order-three field
multiplier is invisible to the character. -/
theorem three_dvd_secp13441CharacterExponent :
    3 ∣ secp13441CharacterExponent := by
  native_decide

/-- The same exponent is even, so negation is also invisible. -/
theorem two_dvd_secp13441CharacterExponent :
    2 ∣ secp13441CharacterExponent := by
  native_decide

/-- An element of order dividing three is killed by every exponent divisible
by three. -/
theorem orderThree_pow_eq_one_of_three_dvd
    {K : Type*} [Monoid K]
    (β : K) (e : ℕ)
    (hβ : β ^ 3 = 1)
    (he : 3 ∣ e) :
    β ^ e = 1 := by
  rcases he with ⟨m, rfl⟩
  rw [pow_mul, hβ, one_pow]

/-- Raising a publicly scaled value to such an exponent removes the
order-three scale factor. -/
theorem orderThreeCharacterPhase_invariant
    {K : Type*} [CommMonoid K]
    (β x : K) (e : ℕ)
    (hβ : β ^ 3 = 1)
    (he : 3 ∣ e) :
    (β * x) ^ e = x ^ e := by
  rw [mul_pow, orderThree_pow_eq_one_of_three_dvd β e hβ he, one_mul]

/-- An even exponent also removes multiplication by a binary sign. -/
theorem evenCharacterPhase_negationInvariant
    {K : Type*} [CommGroup K]
    (s x : K) (e : ℕ)
    (hs : s ^ 2 = 1)
    (he : 2 ∣ e) :
    (s * x) ^ e = x ^ e := by
  rcases he with ⟨m, rfl⟩
  rw [mul_pow, pow_mul, hs, one_pow, one_mul]

end Ecdlp.ParityLift
