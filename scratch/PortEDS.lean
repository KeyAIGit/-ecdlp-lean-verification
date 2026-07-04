/-
Copyright (c) 2024 David Kurniadi Angdinata. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: David Kurniadi Angdinata
-/
import Mathlib

/-!
# Port of the net-relation proof that `normEDS` is an elliptic sequence

This file ports the "net-relation" machinery of the elliptic-divisibility-sequence
development from **mathlib4 PR #13155**
(`Mathlib/NumberTheory/EllipticDivisibilitySequence.lean` at that PR's head),
authored by **Junyan Xu (`alreadydone`)** and **David Angdinata**. The mathematical
content, the proof strategy, and every certificate below are THEIR work; this file
only transcribes their `namespace EllSequence` block onto this repository's pinned
Mathlib v4.31.0 (adapting for 2024 → v4.31 API drift) and is *not* original work of
this repository.

Mathlib v4.31.0 already provides `IsEllSequence`, `normEDS`, `preNormEDS`,
`normEDS_odd`, `normEDS_even`, `normEDS_neg`, `map_normEDS`, etc., but leaves open the
TODO that `normEDS` satisfies `IsEllSequence`. The ported block is wrapped in a fresh
`namespace EDSPort` so that its local `IsEllSequence` / `Rel₃` definitions do not clash
with Mathlib's top-level `IsEllSequence` (to which they are definitionally equal).

The block is self-contained over a free sequence `W : ℤ → R` and culminates in
`EDSPort.of_oddRec_evenRec`. The final theorem `normEDS_isEllSequence` instantiates it
over the integral domain `MvPolynomial (Fin 3) ℤ` and transports to an arbitrary
`CommRing` via the evaluation homomorphism and `map_normEDS`, mirroring the transport
idiom used elsewhere in this repository.
-/

universe u v w

variable {R : Type u} [CommRing R] (W : ℤ → R)

open scoped nonZeroDivisors

namespace EDSPort

/-- The expression `W((m+n)/2) * W((m-n)/2)` is the basic building block of elliptic relations,
where integers `m` and `n` should have the same parity. -/
private def addMulSub (m n : ℤ) : R := W ((m + n).tdiv 2) * W ((m - n).tdiv 2)
/- Implementation note: we use `Int.tdiv _ 2` instead of `_ / 2` so that `(-m).tdiv 2 = -(m.tdiv 2)`
and lemmas like `addMulSub_neg_left` hold unconditionally, even though in the case we care about
(`m` and `n` both even or both odd) both are equal. -/

/-- The four-index elliptic relation, defined in terms of `addMulSub`,
featuring the three partitions of four indices into two pairs.
Intended to apply to four integers of the same parity. -/
private def rel₄ (a b c d : ℤ) : R :=
  addMulSub W a b * addMulSub W c d
    - addMulSub W a c * addMulSub W b d
    + addMulSub W a d * addMulSub W b c

/-- The defining property of elliptic nets in [Stange2011],
equivalent to a suitable valid (same-parity indices) `rel₄` relation,
but here only the first three indices enjoy symmetry under permutation,
while in `rel₄` all four indices can be freely permuted.

The order of the last two terms are changed and two signs are swapped compared to Stange's
paper to make the equivalence with elliptic relations unconditional (indepedent of W
being an odd function). This should also avoid peculiarities in characteristic 3. -/
def net (p q r s : ℤ) : R :=
  W (p + q + s) * W (p - q) * W (r + s) * W r
    - W (p + r + s) * W (p - r) * W (q + s) * W q
    + W (q + r + s) * W (q - r) * W (p + s) * W p

variable {W} in
private lemma net_eq_rel₄ {p q r s : ℤ} :
    net W p q r s = rel₄ W (2 * p + s) (2 * q + s) (2 * r + s) s := by
  simp_rw [net, rel₄, addMulSub, add_add_add_comm _ s, add_sub_add_comm, sub_self, add_zero,
    add_assoc, ← two_mul, add_sub_cancel_right, ← left_distrib, ← mul_sub_left_distrib,
    Int.mul_tdiv_cancel_left _ two_ne_zero]
  ring

/-- The three-index elliptic relation, obtained by
specializing to `d = 0` in the four-index relation. -/
def Rel₃ (m n r : ℤ) : Prop :=
  W (m + n) * W (m - n) * W r ^ 2 =
    W (m + r) * W (m - r) * W n ^ 2 - W (n + r) * W (n - r) * W m ^ 2

/-- The proposition that a sequence indexed by integers is an elliptic sequence. -/
def IsEllSequence : Prop :=
  ∀ m n r : ℤ, Rel₃ W m n r

/-- The numerator of an invariant of an elliptic sequence, such that for each `s`,
`invarNum s n / invarDenom s n` is a constant independent of `n`. -/
def invarNum (s n : ℤ) : R :=
  (W (n + 2 * s) * W (n - s) ^ 2 + W (n + s) ^ 2 * W (n - 2 * s)) * W s ^ 2
    + W n ^ 3 * W (2 * s) ^ 2

/-- The denominator of an invariant of an elliptic sequence. -/
def invarDenom (s n : ℤ) : R := W (n + s) * W n * W (n - s)

theorem invarNum_mul_invarDenom_of_net (net_eq_zero : ∀ p q r s, net W p q r s = 0) (s m n : ℤ) :
    invarNum W s m * invarDenom W s n = invarNum W s n * invarDenom W s m := by
  linear_combination (norm := (simp_rw [invarNum, invarDenom, net]; ring_nf))
    net_eq_zero m n s 0 * W m * W n * W (2 * s) ^ 2
      - (net_eq_zero m n s s * W (m - s) * W (n - s)
        + net_eq_zero (m - s) (n - s) s s * W (m + s) * W (n + s)
        - net_eq_zero (n + s) n (n - s) (m - n) * W (m - n) * W (2 * s)) * W s ^ 2

lemma net_add_sub_iff (m n : ℤ) :
    net W (m + n) m (m - n) n = 0 ↔
      W (2 * (m + n)) * W (m - n) * W m * W n =
        (W (2 * m + n) * W (2 * n) * W m - W (m + 2 * n) * W (2 * m) * W n) * W (m + n) := by
  rw [net]
  conv_rhs => rw [← sub_eq_zero]
  ring_nf


private lemma addMulSub_even (m n : ℤ) : addMulSub W (2 * m) (2 * n) = W (m + n) * W (m - n) := by
  simp_rw [addMulSub, ← left_distrib, ← mul_sub_left_distrib, Int.mul_tdiv_cancel_left _ two_ne_zero]

private lemma addMulSub_odd (m n : ℤ) :
    addMulSub W (2 * m + 1) (2 * n + 1) = W (m + n + 1) * W (m - n) := by
  have h k := Int.mul_tdiv_cancel_left k two_ne_zero
  rw [addMulSub, ← h (m + n + 1), ← h (m - n)]; congr <;> ring

private lemma addMulSub_self (zero : W 0 = 0) (m : ℤ) : addMulSub W m m = 0 := by
  rw [addMulSub, sub_self, Int.zero_tdiv, zero, mul_zero]

private lemma addMulSub_neg_left (neg : ∀ k, W (-k) = -W k) (m n : ℤ) :
    addMulSub W (-m) n = addMulSub W m n := by
  simp_rw [addMulSub, ← neg_add', neg_add_eq_sub, ← neg_sub m, Int.neg_tdiv, neg]; ring

private lemma addMulSub_neg_right (m n : ℤ) : addMulSub W m (-n) = addMulSub W m n := by
  rw [addMulSub, addMulSub, mul_comm]; abel_nf

private lemma addMulSub_abs_left (neg : ∀ k, W (-k) = -W k) (m n : ℤ) :
    addMulSub W |m| n = addMulSub W m n := by
  obtain h | h := abs_choice m <;> simp only [h, addMulSub_neg_left W neg]

private lemma addMulSub_abs_right (m n : ℤ) : addMulSub W m |n| = addMulSub W m n := by
  obtain h | h := abs_choice n <;> simp only [h, addMulSub_neg_right]

private lemma addMulSub_swap (neg : ∀ k, W (-k) = -W k) (m n : ℤ) :
    addMulSub W m n = - addMulSub W n m := by
  rw [addMulSub, addMulSub, ← neg_sub, Int.neg_tdiv, neg]; ring_nf

private lemma rel₃_iff_rel₄_eq_zero (m n r : ℤ) :
    Rel₃ W m n r ↔ rel₄ W (2 * m) (2 * n) (2 * r) 0 = 0 := by
  rw [rel₄, ← mul_zero 2, Rel₃]
  simp_rw [addMulSub_even, add_zero, sub_zero]
  convert sub_eq_zero.symm using 2; ring

section transf

variable (a b c d : ℤ)

/-- The proposition that the four indices are all nonnegative and strictly decreasing. -/
def StrictAnti₄ : Prop := 0 ≤ d ∧ d < c ∧ c < b ∧ b < a

/-- The proposition that the four indices are of the same parity. -/
def HaveSameParity₄ : Prop :=
  a.negOnePow = b.negOnePow ∧ b.negOnePow = c.negOnePow ∧ c.negOnePow = d.negOnePow

/-- The average of four indices. -/
def avg₄ : ℤ := (a + b + c + d) / 2

namespace HaveSameParity₄
open Int Equiv

variable {W a b c d} (same : HaveSameParity₄ a b c d)

include same in
private lemma rel₄_eq_net : rel₄ W a b c d = net W ((a - d) / 2) ((b - d) / 2) ((c - d) / 2) d := by
  have h := @Int.two_mul_ediv_two_of_even
  rw [net_eq_rel₄, h, h, h]; · simp_rw [sub_add_cancel]
  all_goals simp only [← negOnePow_eq_iff, same.1, same.2.1, same.2.2]

include same in
lemma even_sum : Even (a + b + c + d) := by
  simp_rw [← negOnePow_eq_one_iff, negOnePow_add,
    same.1, same.2.1, same.2.2, units_mul_self, one_mul, units_mul_self]

include same in
lemma avg₄_add_avg₄ : avg₄ a b c d + avg₄ a b c d = a + b + c + d := by
  rw [← two_mul]; exact Int.mul_ediv_cancel' same.even_sum.two_dvd

include same in
lemma same₀₃ : a.negOnePow = d.negOnePow := by rw [same.1, same.2.1, same.2.2]

include same in
protected lemma abs : HaveSameParity₄ |a| |b| |c| |d| := by
  simpa only [HaveSameParity₄, negOnePow_abs] using same

lemma perm (σ : Perm (Fin 4)) :
    ∀ t : Fin 4 → ℤ, HaveSameParity₄ (t 0) (t 1) (t 2) (t 3) →
      HaveSameParity₄ (t (σ 0)) (t (σ 1)) (t (σ 2)) (t (σ 3)) := by
  have h := (Perm.mclosure_swap_castSucc_succ 3).symm ▸ Submonoid.mem_top σ
  induction h using Submonoid.closure_induction with
  | mem x hx =>
    obtain ⟨i, rfl⟩ := hx
    rintro t ⟨h₀₁, h₁₂, h₂₃⟩; fin_cases i
    exacts [⟨h₀₁.symm, h₀₁ ▸ h₁₂, h₂₃⟩, ⟨h₀₁ ▸ h₁₂, h₁₂.symm, h₁₂ ▸ h₂₃⟩,
      ⟨h₀₁, h₁₂ ▸ h₂₃, h₂₃.symm⟩]
  | one => exact fun _ ↦ id
  | mul σ τ _ _ ihσ ihτ =>
    intro t same; simp_rw [Perm.mul_apply]; exact ihτ (t ∘ σ) (ihσ _ same)

include same in
lemma six_le_of_strictAnti₄ (anti : StrictAnti₄ a b c d) : 6 ≤ a := by
  simp_rw [HaveSameParity₄, negOnePow_eq_iff] at same
  obtain ⟨hd, hdc, hcb, hba⟩ := anti
  rw [← add_two_le_iff_lt_of_even_sub] at hdc hcb hba
  · linarith
  exacts [same.1, same.2.1, same.2.2]

variable (W) in
/-- A hybrid product formed by one factor from an `addMulSub` and one from another `addMulSub`. -/
private def addMulSub₄ (a b c d : ℤ) : R := W ((a + b).tdiv 2) * W ((c - d).tdiv 2)

private lemma addMulSub₄_mul_addMulSub₄ :
    addMulSub₄ W a b c d * addMulSub₄ W c d a b = addMulSub W a b * addMulSub W c d := by
  simp_rw [addMulSub₄, addMulSub]; ring

/-! Preservation of `rel₄`, `HaveSameParity₄`, and `strictAnti₄` under the transformation
  `(a,b,c,d) ↦ (avg₄ a b c d - d, avg₄ a b c d - c, avg₄ a b c d - b, |avg₄ a b c d - a|)`. -/

include same in
private lemma addMulSub_transf :
    addMulSub W (avg₄ a b c d - d) (avg₄ a b c d - c) = addMulSub₄ W a b c d ∧
      addMulSub W (avg₄ a b c d - d) (avg₄ a b c d - b) = addMulSub₄ W a c b d ∧
      addMulSub W (avg₄ a b c d - d) |avg₄ a b c d - a| = addMulSub₄ W b c a d ∧
      addMulSub W (avg₄ a b c d - c) (avg₄ a b c d - b) = addMulSub₄ W a d b c ∧
      addMulSub W (avg₄ a b c d - c) |avg₄ a b c d - a| = addMulSub₄ W b d a c ∧
      addMulSub W (avg₄ a b c d - b) |avg₄ a b c d - a| = addMulSub₄ W c d a b := by
  simp_rw [addMulSub_abs_right, addMulSub, addMulSub₄, sub_add_sub_comm, same.avg₄_add_avg₄]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩ <;> ring_nf

include same in
private theorem rel₄_transf :
    rel₄ W (avg₄ a b c d - d) (avg₄ a b c d - c) (avg₄ a b c d - b) |avg₄ a b c d - a| =
      rel₄ W a b c d := by
  obtain ⟨h₁, h₂, h₃, h₄, h₅, h₆⟩ := same.addMulSub_transf (W := W)
  simp_rw [rel₄, h₁, h₂, h₃, h₄, h₅, h₆, addMulSub₄_mul_addMulSub₄, mul_comm]

include same in
theorem transf : HaveSameParity₄
    (avg₄ a b c d - d) (avg₄ a b c d - c) (avg₄ a b c d - b) |avg₄ a b c d - a| := by
  simp_rw [HaveSameParity₄, negOnePow_abs, negOnePow_sub, same.1, same.2.1, same.2.2, true_and]

include same in
theorem strictAnti₄_transf (anti : StrictAnti₄ a b c d) :
    StrictAnti₄ (avg₄ a b c d - d) (avg₄ a b c d - c) (avg₄ a b c d - b) |avg₄ a b c d - a| := by
  obtain ⟨hd, hdc, hcb, hba⟩ := anti
  refine ⟨abs_nonneg _, abs_lt.mpr ⟨?_, ?_⟩, ?_, ?_⟩ <;> rw [← sub_pos]
  · rw [sub_neg_eq_add, sub_add_sub_comm, same.avg₄_add_avg₄]; linarith only [hd, hdc]
  all_goals linarith only [hdc, hcb, hba]

end HaveSameParity₄

end transf

/-- The four-index elliptic relation multiplied by a two-index "coefficient". -/
def rel₆ (k l a b c d : ℤ) : R := addMulSub W k l * rel₄ W a b c d

/-! In the following three key lemmas we use `m`, `n`, `r`, `s` to denote "free" indices and
`c`, `d` to denote "fixed" indices. -/

/-- A `rel₄` with a fixed index and three free indices can be expressed in terms of
three `rel₄`s with two fixed indices and two free indices that share one fixed index
(the larger one) and two free indices with the first `rel₄`.
The coefficient before the first `rel₄` is `addMulSub` applied to the two fixed indices. -/
private lemma rel₆_eq₃ (c d m n r : ℤ) :
    rel₆ W c d m n r c = rel₆ W m c n r c d - rel₆ W n c m r c d + rel₆ W r c m n c d := by
  simp_rw [rel₆, rel₄]; ring

/-- A `rel₄` with a fixed index and three free indices can be expressed in terms of
three `rel₄`s with two fixed indices and two free indices that share one fixed index
(the smaller one) and two free indices with the first `rel₄`.
The coefficient before the first `rel₄` is `addMulSub` applied to the two fixed indices. -/
private lemma rel₆_eq₃' (c d m n r : ℤ) :
    rel₆ W c d m n r d = rel₆ W m d n r c d - rel₆ W n d m r c d + rel₆ W r d m n c d := by
  simp_rw [rel₆, rel₄]; ring

/-- A `rel₄` with four free indices can be expressed in terms of ten `rel₄`s
with one or two indices chosen from two possibilities (fixed indices) and
the other indices chosen from the indices of the first `rel₄`.
The coefficient before the first `rel₄` is `addMulSub` applied to the two fixed indices. -/
private theorem rel₆_eq₁₀ (c d m n r s : ℤ) :
    rel₆ W c d m n r s =
      rel₆ W n d m r s c - rel₆ W r d m n s c + rel₆ W s d m n r c
      + rel₆ W n c m r s d - rel₆ W r c m n s d + rel₆ W s c m n r d
      + rel₆ W n r m s c d - rel₆ W n s m r c d + rel₆ W r s m n c d
      - 2 * rel₆ W m d n r s c := by
  simp_rw [rel₆, rel₄]; ring

/-- It is also possible to directly express an arbitrary `rel₄`
in terms of `rel₄`s with the last two indices fixed. -/
private theorem addMulSub_sq_mul_rel₄_eq₉ (c d m n r s : ℤ) :
    (addMulSub W c d) ^ 2 * rel₄ W m n r s =
      addMulSub W m c * (rel₆ W n d r s c d - rel₆ W r d n s c d + rel₆ W s d n r c d)
                    -- = rel₆ W c d n r s d ↑ by rel₆_eq₃'   = rel₆ W c d n r s c ↓ by rel₆_eq₃
      - addMulSub W m d * (rel₆ W n c r s c d - rel₆ W r c n s c d + rel₆ W s c n r c d)
      + addMulSub W c d * (rel₆ W n r m s c d - rel₆ W n s m r c d + rel₆ W r s m n c d) := by
                         -- the third row in RHS of rel₆_eq₁₀
  simp_rw [rel₆, rel₄]; ring

/-- The recurrence defining odd terms of an elliptic sequence,
a particular case of the elliptic relation according to `rel₃_iff_oddRec`. -/
def OddRec (m : ℤ) : Prop :=
  W (2 * m + 1) * W 1 ^ 3 = W (m + 2) * W m ^ 3 - W (m - 1) * W (m + 1) ^ 3

/-- The recurrence defining even terms of an elliptic sequence, a particular case
of the elliptic relation according to `rel₃_iff_evenRec` and `rel₄_iff_evenRec`. -/
def EvenRec (m : ℤ) : Prop :=
  W (2 * m) * W 2 * W 1 ^ 2 = W m * (W (m - 1) ^ 2 * W (m + 2) - W (m - 2) * W (m + 1) ^ 2)

private lemma rel₃_iff_oddRec (m : ℤ) : Rel₃ W (m + 1) m 1 ↔ OddRec W m := by
  rw [Rel₃, OddRec]; ring_nf

private lemma rel₃_iff_evenRec (m : ℤ) : Rel₃ W (m + 1) (m - 1) 1 ↔ EvenRec W m := by
  rw [Rel₃, EvenRec]; ring_nf

private lemma rel₄_iff_evenRec (m : ℤ) : rel₄ W (2 * m + 1) (2 * m - 1) 3 1 = 0 ↔ EvenRec W m := by
  rw [iff_comm, EvenRec, ← sub_eq_zero, show 2 * m - 1 = 2 * (m - 1) + 1 by ring]
  convert_to _ ↔ rel₄ W _ _ (2 * 1 + 1) (2 * 0 + 1) = 0
  simp_rw [rel₄, addMulSub_odd]; ring_nf

/-- The minimal possible fourth index in the four-index elliptic relation given the first index. -/
def dMin (a : ℤ) : ℤ := if Even a then 0 else 1
/-- The minimal possible third index in the four-index elliptic relation given the first index. -/
def cMin (a : ℤ) : ℤ := dMin a + 2

lemma dMin_nonneg (a : ℤ) : 0 ≤ dMin a := by rw [dMin]; split_ifs <;> decide

lemma dMin_lt_cMin (a : ℤ) : dMin a < cMin a := lt_add_of_pos_right _ zero_lt_two

lemma negOnePow_cMin_eq_dMin (a : ℤ) : (cMin a).negOnePow = (dMin a).negOnePow := by
  rw [cMin, Int.negOnePow_add]; exact mul_one _

lemma negOnePow_dMin (a : ℤ) : (dMin a).negOnePow = a.negOnePow := by
  rw [dMin]
  split_ifs with h
  · rw [Int.negOnePow_even _ h, Int.negOnePow_even _ even_zero]
  · rw [Int.negOnePow_odd _ (Int.not_even_iff_odd.mp h), Int.negOnePow_odd _ odd_one]

lemma negOnePow_cMin (a : ℤ) : (cMin a).negOnePow = a.negOnePow := by
  rw [negOnePow_cMin_eq_dMin, negOnePow_dMin]

variable {W}
private lemma addMulSub_mem_nonZeroDivisors (one : W 1 ∈ R⁰) (two : W 2 ∈ R⁰) (a : ℤ) :
    addMulSub W (cMin a) (dMin a) ∈ R⁰ := by
  rw [cMin, dMin]; split_ifs; exacts [mul_mem one one, mul_mem two one]

lemma dMin_le {a b : ℤ} (same : a.negOnePow = b.negOnePow) (h : 0 ≤ b) : dMin a ≤ b := by
  rw [dMin]; split_ifs with odd
  exacts [h, h.lt_of_ne (by rintro rfl; exact odd (a.negOnePow_eq_one_iff.mp same))]

open Int

section Rel₄OfValid

variable (W) in
/-- The four-index elliptic relation restricted to the case where the four indices are
nonnegative, have the same parity and are strictly decreasing. -/
private def Rel₄OfValid (a b c d : ℤ) : Prop :=
  HaveSameParity₄ a b c d → StrictAnti₄ a b c d → rel₄ W a b c d = 0

variable {a c₀ d₀ : ℤ} (par : c₀.negOnePow = d₀.negOnePow) (le : 0 ≤ d₀) (lt : d₀ < c₀)
  (rel : ∀ {a' b}, a' ≤ a → Rel₄OfValid W a' b c₀ d₀) (mem : addMulSub W c₀ d₀ ∈ R⁰)

include par le lt rel mem in
/-- If `rel₄` holds for all quadruples of the form `(a', b, c₀, d₀)` for arbitrary `b` and
`a' < a`, then it holds for `(a, b, c, c₀)` and `(a, b, c, d₀)` for arbitrary `b` and `c`
(subject to some technical conditions). -/
private lemma rel₄_fix₁_of_fix₂ (b c : ℤ) :
    Rel₄OfValid W a b c c₀ ∧ (c₀ < c → Rel₄OfValid W a b c d₀) := by
  refine ⟨fun same anti ↦ mem.2 _ ?_, fun _hc same anti ↦ mem.2 _ ?_⟩ <;> rw [mul_comm, ← rel₆]
  on_goal 1 => rw [rel₆_eq₃]; have _hc := trivial
  on_goal 2 => rw [rel₆_eq₃']
  all_goals simp_rw [rel₆]; rw [rel le_rfl, rel le_rfl, rel anti.2.2.2.le]
  iterate 2
    simp_rw [mul_zero, add_zero, sub_zero]
    iterate 3
      simp only [HaveSameParity₄, par, same.1, same.2.1, same.2.2, true_and]
      refine ⟨le, lt, ?_, ?_⟩ <;> linarith only [_hc, anti.2.1, anti.2.2.1, anti.2.2.2]

include par le lt rel mem in
/-- If `rel₄` holds for all quadruples of the form `(a', b, c₀, d₀)` for arbitrary `b` and
`a' < a`, then it holds for `(a, b, c, d)` for arbitrary `b`, `c` and `d`
(subject to some technical conditions). -/
private lemma rel₄_of_fix₂ (b c d : ℤ) (hc : c₀ < d) (par' : d.negOnePow = d₀.negOnePow) :
    Rel₄OfValid W a b c d := fun same ⟨_, hdc, hcb, hba⟩ ↦ mem.2 _ <| by
  rw [mul_comm, ← rel₆, rel₆_eq₁₀]; simp_rw [rel₆]
  have fix₁ b c := (rel₄_fix₁_of_fix₂ par le lt rel mem b c).1
  have fix₂ {b c} := (rel₄_fix₁_of_fix₂ par le lt rel mem b c).2
  rw [fix₁, fix₁, fix₁, fix₂ hc, fix₂ hc, fix₂ (hc.trans hdc), rel le_rfl, rel le_rfl,
    rel le_rfl, (rel₄_fix₁_of_fix₂ par le lt (fun h ↦ rel <| h.trans hba.le) mem _ _).1]
  · simp_rw [mul_zero, add_zero, sub_zero]
  iterate 10
    simp only [HaveSameParity₄, par, par', same.1, same.2.1, same.2.2, true_and]
    refine ⟨?_, ?_, ?_, ?_⟩ <;> linarith only [hc, le, lt, hdc, hcb, hba]

/-- Specialize previous lemmas to the case `c₀ = cMin a` and `d₀ = dMin a`,
and combine them to remove technical conditions about the relative order of the indices. -/
private theorem rel₄_of_min₂ (one : W 1 ∈ R⁰) (two : W 2 ∈ R⁰)
    (rel : ∀ {a' b}, a' ≤ a → Rel₄OfValid W a' b (cMin a) (dMin a)) (b c d : ℤ) :
    Rel₄OfValid W a b c d := fun same anti ↦ by
  obtain hc|hc := lt_or_ge (cMin a) d
  · refine rel₄_of_fix₂ (negOnePow_cMin_eq_dMin a) (dMin_nonneg a) (dMin_lt_cMin a) rel
      (addMulSub_mem_nonZeroDivisors one two a) _ _ _ hc ?_ same anti
    rw [negOnePow_dMin, same.1, same.2.1, same.2.2]
  have fix := rel₄_fix₁_of_fix₂ (negOnePow_cMin_eq_dMin a) (dMin_nonneg a) (dMin_lt_cMin a) rel
    (addMulSub_mem_nonZeroDivisors one two a) b c
  obtain rfl|hc := hc.eq_or_lt
  · exact fix.1 same anti
  obtain rfl : dMin a = d := (dMin_le same.same₀₃ anti.1).antisymm <| by
    rwa [← add_two_le_iff_lt_of_even_sub, cMin, add_le_add_iff_right] at hc
    rw [← negOnePow_eq_iff, negOnePow_cMin, same.same₀₃]
  obtain rfl|hc : cMin a = c ∨ _ := ((add_two_le_iff_lt_of_even_sub <| by
    rw [← negOnePow_eq_iff, negOnePow_dMin, same.1, same.2.1]).mpr anti.2.1).eq_or_lt
  exacts [rel le_rfl same anti, fix.2 hc same anti]

-- The main inductive argument.
private theorem rel₄_of_anti_oddRec_evenRec (one : W 1 ∈ R⁰) (two : W 2 ∈ R⁰)
    (oddRec : ∀ m ≥ 2, OddRec W m) (evenRec : ∀ m ≥ 3, EvenRec W m) :
    ∀ ⦃a b c d : ℤ⦄, Rel₄OfValid W a b c d :=
  -- apply induction on `a`
  Int.strongRec (m := 6) -- if `a < 6` the conclusion holds vacuously
    (fun a ha b c d same anti ↦ absurd (same.six_le_of_strictAnti₄ anti) (by omega))
    -- otherwise, it suffices to deal with the "minimal" case `c = cMin a` and `d = dMin a`
    fun a h6 ih ↦ rel₄_of_min₂ one two fun {a' b} haa same anti ↦ by
  obtain ha'|ha' := haa.lt_or_eq
  · -- if `a' < a`, apply the inductive hypothesis
    exact ih _ ha' same anti
  obtain hba|rfl := lt_or_eq_of_le <| show b + 2 ≤ a' from
    (add_two_le_iff_lt_of_even_sub <| (negOnePow_eq_iff _ _).1 same.1).mpr anti.2.2.2
  · -- if `b + 2 < a'`, apply `transf` and then the inductive hypothesis is applicable
    rw [← same.rel₄_transf]
    refine ih _ ?_ same.transf (same.strictAnti₄_transf anti)
    rw [avg₄, sub_lt_iff_lt_add, Int.ediv_lt_iff_lt_mul zero_lt_two, ← ha', cMin]
    linarith only [hba]
  obtain ⟨m, rfl|rfl⟩ := b.even_or_odd'
  -- the `b + 2 = a'` case is handled by oddRec or evenRec depending on the parity of `b`
  · have ea : Even a := by rw [← ha']; exact (even_two_mul _).add even_two
    have hm2 : m ≥ 2 := by linarith only [h6, ha']
    simp_rw [cMin, dMin, if_pos ea]
    convert (rel₃_iff_rel₄_eq_zero W (m + 1) m 1).mp
      ((rel₃_iff_oddRec W m).mpr <| oddRec _ hm2) using 2 <;> ring
  · have nea : ¬ Even a := by
      rw [← ha', Int.not_even_iff_odd]; convert odd_two_mul_add_one (m + 1) using 1; ring
    have hm3 : m + 1 ≥ 3 := by linarith only [h6, ha']
    simp_rw [cMin, dMin, if_neg nea]
    convert (rel₄_iff_evenRec W (m + 1)).mpr (evenRec _ hm3) using 2 <;> ring

end Rel₄OfValid

section Perm

variable (neg : ∀ k, W (-k) = -W k)

include neg in
private lemma rel₄_abs {m n r s : ℤ} : rel₄ W |m| |n| |r| |s| = rel₄ W m n r s := by
  simp_rw [rel₄, addMulSub_abs_left W neg, addMulSub_abs_right]

include neg in
private lemma rel₄_swap₀₁ {m n r s : ℤ} : rel₄ W m n r s = - rel₄ W n m r s := by
  simp_rw [rel₄, addMulSub_swap W neg n m]; ring

include neg in
private lemma rel₄_swap₁₂ {m n r s : ℤ} : rel₄ W m n r s = - rel₄ W m r n s := by
  simp_rw [rel₄, addMulSub_swap W neg r n]; ring

include neg in
private lemma rel₄_swap₂₃ {m n r s : ℤ} : rel₄ W m n r s = - rel₄ W m n s r := by
  simp_rw [rel₄, addMulSub_swap W neg s r]; ring

open Equiv

variable (W) in
/-- The four-index elliptic relation with a tuple as input. -/
private def rel₄Fin4 (t : Fin 4 → ℤ) : R := rel₄ W (t 0) (t 1) (t 2) (t 3)

include neg in
/-- `rel₄` is invariant (up to sign) under permutation of the four indices. -/
private theorem rel₄Fin4_perm (σ : Perm (Fin 4)) :
    ∀ t, rel₄Fin4 W (t ∘ σ) = Perm.sign σ • rel₄Fin4 W t := by
  have h := (Perm.mclosure_swap_castSucc_succ 3).symm ▸ Submonoid.mem_top σ
  induction h using Submonoid.closure_induction with
  | mem x hx =>
    obtain ⟨i, rfl⟩ := hx
    intro t; fin_cases i <;>
      rw [Perm.sign_swap Fin.castSucc_lt_succ.ne, Units.neg_smul, one_smul]
    exacts [rel₄_swap₀₁ neg, rel₄_swap₁₂ neg, rel₄_swap₂₃ neg]
  | one => simp
  | mul σ τ _ _ ihσ ihτ =>
    intro t
    rw [Perm.coe_mul, ← Function.comp_assoc, ihτ, ihσ, map_mul, mul_comm, mul_smul]

include neg in
private lemma rel₄Fin4_perm' (σ : Perm (Fin 4)) (t) :
    Perm.sign σ • rel₄Fin4 W (t ∘ σ) = rel₄Fin4 W t := by
  rw [rel₄Fin4_perm neg, ← mul_smul, Int.units_mul_self, one_smul]

variable (zero : W 0 = 0)

/-! `rel₄` is trivial when two indices are equal. -/

include zero in
private lemma rel₄_same₀₁ (m r s : ℤ) : rel₄ W m m r s = 0 := by
  simp_rw [rel₄, addMulSub_self W zero]; ring

include zero in
private lemma rel₄_same₁₂ (m n s : ℤ) : rel₄ W m n n s = 0 := by
  simp_rw [rel₄, addMulSub_self W zero]; ring

include zero in
private lemma rel₄_same₂₃ (m n r : ℤ) : rel₄ W m n r r = 0 := by
  simp_rw [rel₄, addMulSub_self W zero]; ring

variable (one : W 1 ∈ R⁰) (two : W 2 ∈ R⁰)
  (oddRec : ∀ m ≥ 2, OddRec W m) (evenRec : ∀ m ≥ 3, EvenRec W m)

include neg zero one two oddRec evenRec in
/-- The four-index `rel₄` relations follow from
the single-index `oddRec` and `evenRec` recursive relations. -/
private theorem rel₄_of_oddRec_evenRec {a b c d : ℤ} (same : HaveSameParity₄ a b c d) :
    rel₄ W a b c d = 0 := by
  let t := ![|a|, |b|, |c|, |d|]
  have nonneg i : 0 ≤ t i := by fin_cases i <;> exact abs_nonneg _
  let σ := Fin.revPerm.trans (Tuple.sort t)
  have anti : Antitone (t ∘ σ) := by
    simp_rw [σ, coe_trans, ← Function.comp_assoc]
    exact (Tuple.monotone_sort t).comp_antitone fun _ _ ↦ Fin.rev_le_rev.mpr
  clear_value σ -- otherwise, unifying `t (σ i)` with `(t ∘ σ) i` is extremely slow
  rw [← rel₄_abs neg]; change rel₄Fin4 W t = 0
  rw [← rel₄Fin4_perm' neg σ, rel₄Fin4]; simp_rw [Function.comp]
  by_cases h₃₂ : t (σ 3) = t (σ 2); · rw [h₃₂, rel₄_same₂₃ zero, smul_zero]
  by_cases h₂₁ : t (σ 2) = t (σ 1); · rw [h₂₁, rel₄_same₁₂ zero, smul_zero]
  by_cases h₁₀ : t (σ 1) = t (σ 0); · rw [h₁₀, rel₄_same₀₁ zero, smul_zero]
  rw [rel₄_of_anti_oddRec_evenRec one two oddRec evenRec (same.abs.perm _ _), smul_zero]
  exact ⟨nonneg _, (anti <| by decide).lt_of_ne h₃₂,
    (anti <| by decide).lt_of_ne h₂₁, (anti <| by decide).lt_of_ne h₁₀⟩

include neg zero one two oddRec evenRec in
/-- An ℕ-indexed sequence defined recursively by the even-odd recurrence, after extension to
all integers by symmetry (to make an odd function), is an elliptic sequence, provided its
first two terms are not zero divisors. -/
theorem of_oddRec_evenRec : IsEllSequence W := fun m n r ↦ by
  rw [rel₃_iff_rel₄_eq_zero, rel₄_of_oddRec_evenRec neg zero one two oddRec evenRec]
  refine ⟨?_, ?_, ?_⟩ <;> simp only [negOnePow_two_mul, negOnePow_zero]

end Perm

end EDSPort

/-- **`normEDS` is an elliptic sequence** (Mathlib's `IsEllSequence`), the open Mathlib
TODO, obtained by instantiating the ported net-relation proof of Junyan Xu and David
Angdinata over the integral domain `MvPolynomial (Fin 3) ℤ` and transporting to an
arbitrary `CommRing` via the evaluation homomorphism. -/
theorem normEDS_isEllSequence {R : Type*} [CommRing R] (b c d : R) :
    IsEllSequence (normEDS b c d) := by
  have hne : (MvPolynomial.X 0 : MvPolynomial (Fin 3) ℤ) ≠ 0 := MvPolynomial.X_ne_zero 0
  have hell0 : IsEllSequence
      (normEDS (MvPolynomial.X 0 : MvPolynomial (Fin 3) ℤ)
        (MvPolynomial.X 1) (MvPolynomial.X 2)) :=
    EDSPort.of_oddRec_evenRec
      (W := normEDS (MvPolynomial.X 0) (MvPolynomial.X 1) (MvPolynomial.X 2))
      (fun k => normEDS_neg _ _ _ k)
      (normEDS_zero _ _ _)
      (by rw [normEDS_one]; exact one_mem _)
      (by rw [normEDS_two]; exact mem_nonZeroDivisors_of_ne_zero hne)
      (fun m _ => by
        unfold EDSPort.OddRec
        rw [normEDS_one, normEDS_odd]; ring)
      (fun m _ => by
        unfold EDSPort.EvenRec
        rw [normEDS_one, normEDS_two]
        linear_combination
          normEDS_even (MvPolynomial.X 0 : MvPolynomial (Fin 3) ℤ)
            (MvPolynomial.X 1) (MvPolynomial.X 2) m)
  let f : MvPolynomial (Fin 3) ℤ →+* R :=
    MvPolynomial.eval₂Hom (Int.castRingHom R) ![b, c, d]
  intro m n r
  have h := congrArg f (hell0 m n r)
  simp only [map_mul, map_sub, map_pow, map_normEDS] at h
  have hB : f (MvPolynomial.X 0) = b := by simp [f]
  have hC : f (MvPolynomial.X 1) = c := by simp [f]
  have hD : f (MvPolynomial.X 2) = d := by simp [f]
  rw [hB, hC, hD] at h
  exact h
