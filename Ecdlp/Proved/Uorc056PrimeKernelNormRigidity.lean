import Mathlib

/-!
# UORC-056 C40 prime-kernel norm rigidity

This file checks the elementary algebraic and exact secp256k1 boundary used by
C40. The elliptic-curve Frobenius fibre and finite frozen replay remain in the
accompanying executable certificate.
-/

namespace Ecdlp.Uorc056PrimeKernelNormRigidity

/-- The unordered product is invariant under swapping the two marked factors. -/
theorem unorderedProduct_swap
    {R : Type*} [CommMonoid R] (even odd : R) :
    odd * even = even * odd := by
  rw [mul_comm]

/-- The ordered difference changes sign when the two factors are swapped. -/
theorem orderedDifference_swap
    {R : Type*} [Ring R] (even odd : R) :
    even - odd = -(odd - even) := by
  ring

/-- Symmetric data cannot simultaneously equal the two opposite ordered
    differences when two is nonzero and the factors are distinct. -/
theorem symmetricData_cannotChooseOrderedDifference
    {K : Type*} [Field K]
    (even odd : K)
    (two_ne_zero : (2 : K) ≠ 0)
    (hneq : even ≠ odd)
    (decoder : K → K → K)
    (hsym : decoder even odd = decoder odd even)
    (hforward : decoder even odd = odd - even)
    (hreverse : decoder odd even = even - odd) :
    False := by
  have h : odd - even = even - odd := by
    calc
      odd - even = decoder even odd := hforward.symm
      _ = decoder odd even := hsym
      _ = even - odd := hreverse
  have hzero : 2 * (odd - even) = 0 := by
    calc
      2 * (odd - even) = (odd - even) - (even - odd) := by ring
      _ = 0 := by rw [h]; ring
  have hdiff : odd - even = 0 := by
    exact (mul_eq_zero.mp hzero).resolve_left two_ne_zero
  have hoe : odd = even := sub_eq_zero.mp hdiff
  exact hneq hoe.symm


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpHalf : Nat :=
  (secpN - 1) / 2


theorem secpHalfNontrivial :
    1 < secpHalf ∧ secpHalf < secpN := by
  native_decide


theorem secpHalfNotDvdOrder :
    ¬ secpHalf ∣ secpN := by
  native_decide


theorem secpHalfTwice :
    2 * secpHalf = secpN - 1 := by
  native_decide

end Ecdlp.Uorc056PrimeKernelNormRigidity
