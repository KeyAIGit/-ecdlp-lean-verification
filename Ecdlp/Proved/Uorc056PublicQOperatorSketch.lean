import Mathlib
import Ecdlp.Proved.Uorc056AsymmetricResultant

/-!
# UORC056 C27 public-Q operator-state barriers

This file kernel-checks the information-transfer core used by C27 and the
fixed secp256k1 integer certificates.

The executable companion proves two exact operator identities and replays their
finite consequences:

* a fixed sparse trace atom `Tr(T_G^a T_Q^b)` differs from its baseline at
  most one nonzero scalar;
* a coordinate-sparse bilinear probe can differ from zero only on its charged
  support-difference set.

The full finite-field representation theorem

`nontrivial F_p-representation of C_n has dimension at least ord_n(p)`

and the exact Lucas/multiplicative-order certificates are verified by the
deterministic Python replay. They are not smuggled into this file under a
kernel-checked label.
-/

namespace Ecdlp.UORC056

section InformationTransfer

variable {α X Y : Type*}

/-- Equal observable values cannot be decoded to two different target values. -/
theorem equalObservable_blocks_twoTarget_decoder
    (observable : α → X) (target : α → Y)
    (left right : α)
    (hObservable : observable left = observable right)
    (hTarget : target left ≠ target right) :
    ¬ ∃ decode : X → Y,
        decode (observable left) = target left ∧
        decode (observable right) = target right := by
  intro h
  rcases h with ⟨decode, hLeft, hRight⟩
  apply hTarget
  calc
    target left = decode (observable left) := hLeft.symm
    _ = decode (observable right) := congrArg decode hObservable
    _ = target right := hRight

variable [DecidableEq α]

/-- If an observable is constant away from a charged exceptional set, any two
outside points with different target labels block an exact decoder. -/
theorem constantOutside_blocks_twoTarget_decoder
    (observable : α → X) (target : α → Y)
    (exceptional : Finset α) (base : X)
    (left right : α)
    (hLeft : left ∉ exceptional)
    (hRight : right ∉ exceptional)
    (hConstant : ∀ point, point ∉ exceptional → observable point = base)
    (hTarget : target left ≠ target right) :
    ¬ ∃ decode : X → Y,
        decode (observable left) = target left ∧
        decode (observable right) = target right := by
  apply equalObservable_blocks_twoTarget_decoder
    observable target left right
  · calc
      observable left = base := hConstant left hLeft
      _ = observable right := (hConstant right hRight).symm
  · exact hTarget

/-- Covering one full target fibre by exceptional points costs at least the
cardinality of that fibre. -/
theorem fibreCard_le_exceptionalCard
    (fibre exceptional : Finset α)
    (hSubset : fibre ⊆ exceptional) :
    fibre.card ≤ exceptional.card :=
  Finset.card_le_card hSubset

/-- The same transfer when the charged cost is only known to dominate the
exceptional-set cardinality. -/
theorem fibreCard_le_cost
    (fibre exceptional : Finset α) (cost : ℕ)
    (hSubset : fibre ⊆ exceptional)
    (hExceptional : exceptional.card ≤ cost) :
    fibre.card ≤ cost := by
  exact le_trans (fibreCard_le_exceptionalCard fibre exceptional hSubset)
    hExceptional

end InformationTransfer

section FixedArithmetic

def secpN : ℕ :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def secpHalfParityFibre : ℕ :=
  57896044618658097711785492504343953926418782139537452191302581570759080747168

def secpLinearRepresentationDegree : ℕ :=
  19298681539552699237261830834781317975472927379845817397100860523586360249056

def secpMomentDepth : ℕ :=
  70296448064902889502766530

/-- Exact half-fibre arithmetic for the nonzero canonical scalar domain. -/
theorem secpHalfParityFibre_certificate :
    2 * secpHalfParityFibre = secpN - 1 := by
  native_decide

/-- Exact arithmetic behind the claimed extension/representation degree. -/
theorem secpLinearDegree_certificate :
    6 * secpLinearRepresentationDegree = secpN - 1 := by
  native_decide

/-- The trace/Krylov exceptional-set bound is three times the minimum
nontrivial base-field linear representation degree. -/
theorem secpHalf_eq_three_mul_linearDegree :
    secpHalfParityFibre = 3 * secpLinearRepresentationDegree := by
  native_decide

/-- The exact factorization whose prime factors and order witnesses are checked
by the companion Lucas-certificate replay. -/
theorem secpLinearDegree_factorization :
    secpLinearRepresentationDegree =
      2^5 * 149 * 631 *
      107361793816595537 *
      174723607534414371449 *
      341948486974166000522343609283189 := by
  native_decide

theorem secpLinearDegree_gt_twoPow253 :
    2^253 < secpLinearRepresentationDegree := by
  native_decide

theorem secpLinearDegree_lt_twoPow254 :
    secpLinearRepresentationDegree < 2^254 := by
  native_decide

theorem secpHalf_gt_twoPow254 :
    2^254 < secpHalfParityFibre := by
  native_decide

theorem secpHalf_lt_twoPow255 :
    secpHalfParityFibre < 2^255 := by
  native_decide

/-- Minimality of the full expanded Newton-moment depth recorded by C27. -/
theorem secpMomentDepth_predecessor_fails :
    (secpMomentDepth - 1) * secpMomentDepth *
        (secpMomentDepth + 1) / 6 <
      secpHalfParityFibre := by
  native_decide

theorem secpMomentDepth_succeeds :
    secpHalfParityFibre ≤
      secpMomentDepth * (secpMomentDepth + 1) *
        (secpMomentDepth + 2) / 6 := by
  native_decide

end FixedArithmetic

end Ecdlp.UORC056
