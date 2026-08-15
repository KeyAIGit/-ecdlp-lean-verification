import Mathlib

/-!
# UORC-056 C33 oriented addition carry cocycle

This file kernel-checks the algebraic core of the lifted-addition obstruction:

* the carry factor reconstructs the oriented target after addition;
* the carry factor satisfies the normalized 2-cocycle identity;
* a diagonal carry at a public half point is the target sign itself;
* a gauge propagated by the same successor rule is unique once its anchor is
  fixed;
* an involution cannot carry nontrivial odd-order homomorphic phase;
* fixed secp256k1 arithmetic used by the C33 boundary.

It does not formalize elliptic curves, canonical integer representatives,
the carry-matrix determinant, divisor-degree transfer, or the classification of
all extension-field characters. Those inputs are stated explicitly in the
accompanying note and replayed by exact Python certificates.
-/

namespace Ecdlp.Uorc056OrientedAdditionCocycle

/-- The sign-valued addition carry attached to an oriented sign function. -/
def carry
    {A R : Type*} [Add A] [Mul R]
    (sigma : A -> R) (P Q : A) : R :=
  sigma P * sigma Q * sigma (P + Q)

/-- The carry restores the oriented value at the sum when every sign squares
    to one. -/
theorem carry_reconstruct
    {A R : Type*} [Add A] [CommMonoid R]
    (sigma : A -> R)
    (hsq : forall P, sigma P * sigma P = 1)
    (P Q : A) :
    carry sigma P Q * sigma P * sigma Q = sigma (P + Q) := by
  unfold carry
  calc
    (sigma P * sigma Q * sigma (P + Q)) * sigma P * sigma Q =
        (sigma P * sigma P) * (sigma Q * sigma Q) * sigma (P + Q) := by
      ac_rfl
    _ = sigma (P + Q) := by
      rw [hsq P, hsq Q]
      simp

/-- Carry is symmetric on a commutative input law. -/
theorem carry_symmetric
    {A R : Type*} [AddCommSemigroup A] [CommMonoid R]
    (sigma : A -> R) (P Q : A) :
    carry sigma P Q = carry sigma Q P := by
  simp [carry, add_comm, mul_comm]

/-- The carry is an exact normalized 2-cocycle. -/
theorem carry_cocycle
    {A R : Type*} [AddSemigroup A] [CommMonoid R]
    (sigma : A -> R)
    (hsq : forall P, sigma P * sigma P = 1)
    (P Q T : A) :
    carry sigma P Q * carry sigma (P + Q) T =
      carry sigma Q T * carry sigma P (Q + T) := by
  unfold carry
  rw [add_assoc]
  calc
    (sigma P * sigma Q * sigma (P + Q)) *
        (sigma (P + Q) * sigma T * sigma (P + (Q + T))) =
      (sigma (P + Q) * sigma (P + Q)) *
        (sigma P * sigma Q * sigma T * sigma (P + (Q + T))) := by
      ac_rfl
    _ = sigma P * sigma Q * sigma T * sigma (P + (Q + T)) := by
      rw [hsq (P + Q)]
      simp
    _ = (sigma (Q + T) * sigma (Q + T)) *
        (sigma P * sigma Q * sigma T * sigma (P + (Q + T))) := by
      rw [hsq (Q + T)]
      simp
    _ = (sigma Q * sigma T * sigma (Q + T)) *
        (sigma P * sigma (Q + T) * sigma (P + (Q + T))) := by
      ac_rfl

/-- A diagonal carry at any public half point is already the target sign. -/
theorem diagonal_carry_is_target
    {A R : Type*} [Add A] [CommMonoid R]
    (sigma : A -> R)
    (hsq : forall P, sigma P * sigma P = 1)
    (half target : A)
    (hhalf : half + half = target) :
    carry sigma half half = sigma target := by
  simp [carry, hhalf, hsq half]

/-- Two state sequences obeying the same anchored successor law are identical.
    This is the finite successor form of carry-gauge uniqueness. -/
theorem anchored_successor_unique
    {R : Type*} [Mul R]
    (edge left right : Nat -> R)
    (hzero : left 0 = right 0)
    (hone : left 1 = right 1)
    (hleft : forall k, left (k + 1) = edge k * left k * left 1)
    (hright : forall k, right (k + 1) = edge k * right k * right 1) :
    forall k, left k = right k := by
  intro k
  induction k with
  | zero => exact hzero
  | succ k ih =>
      rw [hleft k, hright k, ih, hone]

/-- An element that is both an involution and of odd order is trivial. This is
    the scalar algebra behind the absence of a nontrivial binary homomorphic
    phase on an odd cyclic group. -/
theorem odd_order_involution_trivial
    {R : Type*} [Monoid R]
    (x : R) (m : Nat)
    (h2 : x ^ 2 = 1)
    (hodd : x ^ (2 * m + 1) = 1) :
    x = 1 := by
  calc
    x = 1 * x := by simp
    _ = (x ^ 2) ^ m * x := by rw [h2, one_pow]
    _ = x ^ (2 * m) * x := by rw [pow_mul]
    _ = x ^ (2 * m + 1) := by rw [pow_add, pow_one]
    _ = 1 := hodd

/-- A public additive recoding preserves the same scalar multiplier. -/
theorem additive_recoding_keeps_scalar
    {G H : Type*} [AddMonoid G] [AddMonoid H]
    (phi : G →+ H)
    (k : Nat)
    (P : G) :
    phi (k • P) = k • phi P := by
  exact map_nsmul phi k P


def secpP : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpHalf : Nat :=
  (secpN - 1) / 2


def secpInverseTwo : Nat :=
  (secpN + 1) / 2


theorem secpOrderIsOdd :
    secpN % 2 = 1 := by
  native_decide


theorem secpInverseTwoCertificate :
    (2 * secpInverseTwo) % secpN = 1 := by
  native_decide


theorem secpNegativeHalfCertificate :
    2 * secpHalf = secpN - 1 := by
  native_decide


theorem secpNoBaseFieldOrderNCharacter :
    Nat.gcd secpN (secpP - 1) = 1 := by
  native_decide


theorem secpFixedCarryFibrePoleLowerBoundIs256Bit :
    2 ^ 255 < secpN - 1 ∧ secpN - 1 < 2 ^ 256 := by
  native_decide


theorem secpNonzeroCarryRankIs256Bit :
    2 ^ 255 < secpN - 1 ∧ secpN - 1 < 2 ^ 256 := by
  native_decide

end Ecdlp.Uorc056OrientedAdditionCocycle
