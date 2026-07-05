import Mathlib
import Ecdlp.Proved.SevenTorsionBridge
import Ecdlp.Proved.ThreeTorsionCard

/-!
# Point-cardinality bound for secp256k1 n-torsion (n = 3, 5, 7)

Upgrades the x-coordinate count bounds to genuine POINT counts:
`Nat.card {P // n • P = 0} ≤ n²` for n ∈ {3,5,7}, via a ≤2-to-1 fiber argument
(at most two y per x on the curve) combined with the division-polynomial x-coordinate
bounds from the merged torsion bridges.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- x-coordinate projection of an affine point (0 ↦ 0). -/
def px : secp256k1.toAffine.Point → ZMod Secp256k1.p
  | .zero => 0
  | .some x _ _ => x

/-- y-coordinate projection of an affine point (0 ↦ 0). -/
def py : secp256k1.toAffine.Point → ZMod Secp256k1.p
  | .zero => 0
  | .some _ y _ => y

/-- The curve equation `y² = x³ + 7` holds at any nonsingular affine point of secp256k1. -/
theorem secp256k1_curve_of_nonsingular (x y : ZMod Secp256k1.p)
    (h : secp256k1.toAffine.Nonsingular x y) : y ^ 2 = x ^ 3 + 7 := by
  have he : secp256k1.toAffine.Equation x y := h.1
  rw [WeierstrassCurve.Affine.equation_iff] at he
  simp only [secp256k1] at he
  linear_combination he

/-! ### Concrete univariate torsion polynomials for n = 5, 7 -/

/-- The degree-12 univariate 5-torsion polynomial `Q₅(x)`. -/
noncomputable def Q5 : (ZMod Secp256k1.p)[X] :=
  5 * X ^ 12 + 2660 * X ^ 9 - 11760 * X ^ 6 - 548800 * X ^ 3 - 614656

theorem Q5_eval (x : ZMod Secp256k1.p) :
    Q5.eval x = 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656 := by
  simp only [Q5, eval_add, eval_sub, eval_mul, eval_pow, eval_X, eval_ofNat]

theorem Q5_natDegree_le : Q5.natDegree ≤ 12 := by
  unfold Q5; compute_degree

theorem Q5_ne_zero : Q5 ≠ 0 := by
  intro hz
  have h0 : Q5.eval 0 = 0 := by rw [hz, eval_zero]
  rw [Q5_eval] at h0
  have hval : (614656 : ZMod Secp256k1.p) = 0 := by linear_combination -h0
  have hc : ((614656 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]; decide
  exact hc (by exact_mod_cast hval)

/-- The degree-24 univariate 7-torsion polynomial `Q₇(x)`. -/
noncomputable def Q7 : (ZMod Secp256k1.p)[X] :=
  7 * X ^ 24 + 27608 * X ^ 21 - 2101904 * X ^ 18 - 284585728 * X ^ 15
    - 2228742656 * X ^ 12 - 26142548992 * X ^ 9 - 330576748544 * X ^ 6
    - 661153497088 * X ^ 3 + 377801998336

theorem Q7_eval (x : ZMod Secp256k1.p) :
    Q7.eval x = 7 * x ^ 24 + 27608 * x ^ 21 - 2101904 * x ^ 18 - 284585728 * x ^ 15
      - 2228742656 * x ^ 12 - 26142548992 * x ^ 9 - 330576748544 * x ^ 6
      - 661153497088 * x ^ 3 + 377801998336 := by
  simp only [Q7, eval_add, eval_sub, eval_mul, eval_pow, eval_X, eval_ofNat]

theorem Q7_natDegree_le : Q7.natDegree ≤ 24 := by
  unfold Q7; compute_degree

theorem Q7_ne_zero : Q7 ≠ 0 := by
  intro hz
  have h0 : Q7.eval 0 = 0 := by rw [hz, eval_zero]
  rw [Q7_eval] at h0
  have hval : (377801998336 : ZMod Secp256k1.p) = 0 := by linear_combination h0
  have hc : ((377801998336 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]; decide
  exact hc (by exact_mod_cast hval)

variable [Fact (Nat.Prime Secp256k1.p)]

/-! ### x-coordinate membership for n = 5, 7 -/

theorem secp256k1_five_torsion_x_mem (x y : ZMod Secp256k1.p)
    (h : secp256k1.toAffine.Nonsingular x y) (ht : (5 : ℕ) • Point.some x y h = 0) :
    x ∈ Q5.roots.toFinset := by
  have hcurve : y ^ 2 = x ^ 3 + 7 := secp256k1_curve_of_nonsingular x y h
  have hev := (secp256k1_five_nsmul_eq_zero_iff x y h).mp ht
  rw [secp256k1_psi5_evalEval x y hcurve] at hev
  rw [Multiset.mem_toFinset, mem_roots']
  refine ⟨Q5_ne_zero, ?_⟩
  rw [IsRoot.def, Q5_eval]
  exact hev

theorem secp256k1_seven_torsion_x_mem (x y : ZMod Secp256k1.p)
    (h : secp256k1.toAffine.Nonsingular x y) (ht : (7 : ℕ) • Point.some x y h = 0) :
    x ∈ Q7.roots.toFinset := by
  have hcurve : y ^ 2 = x ^ 3 + 7 := secp256k1_curve_of_nonsingular x y h
  have hev := (secp256k1_seven_nsmul_eq_zero_iff x y h).mp ht
  rw [secp256k1_psi7_evalEval x y hcurve] at hev
  rw [Multiset.mem_toFinset, mem_roots']
  refine ⟨Q7_ne_zero, ?_⟩
  rw [IsRoot.def, Q7_eval]
  exact hev

/-! ### General ≤2-to-1 counting lemma -/

/-- **Fiber ≤ 2 counting bound.** If every nonzero `n`-torsion point of secp256k1 has its
`x`-coordinate in a finite set `Xf` of size `≤ m`, then the set of all `n`-torsion POINTS has
`ncard ≤ 2·m + 1`: each `x` has at most two `y` on the curve, plus the identity `0`. -/
theorem secp256k1_torsion_ncard_le (n m : ℕ) (Xf : Finset (ZMod Secp256k1.p))
    (hXcard : Xf.card ≤ m)
    (hmem : ∀ (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y),
        n • Point.some x y h = 0 → x ∈ Xf) :
    Set.ncard {P : secp256k1.toAffine.Point | n • P = 0} ≤ 2 * m + 1 := by
  classical
  haveI : NeZero Secp256k1.p := ⟨(Fact.out : Nat.Prime Secp256k1.p).pos.ne'⟩
  set T := {P : secp256k1.toAffine.Point | n • P = 0} with hT
  set N := {P : secp256k1.toAffine.Point | n • P = 0 ∧ P ≠ 0} with hN
  -- Injectivity of the (x,y) map on N.
  have hpair_inj : Set.InjOn (fun P => (px P, py P)) N := by
    rintro P hP Q hQ hPQ
    rcases P with _ | ⟨x1, y1, h1⟩
    · exact absurd rfl hP.2
    rcases Q with _ | ⟨x2, y2, h2⟩
    · exact absurd rfl hQ.2
    · simp only [px, py, Prod.mk.injEq] at hPQ
      obtain ⟨hx, hy⟩ := hPQ
      subst hx; subst hy; rfl
  -- Finiteness of N.
  have hNfin : N.Finite := Set.Finite.of_finite_image (Set.toFinite _) hpair_inj
  haveI : Fintype ↥N := hNfin.fintype
  -- N.ncard equals the Finset card.
  have hNcard : N.ncard = N.toFinset.card := Set.ncard_eq_toFinset_card' N
  -- The x-image lands in Xf.
  have himg_sub : N.toFinset.image px ⊆ Xf := by
    intro a ha
    rw [Finset.mem_image] at ha
    obtain ⟨P, hPsN, hPa⟩ := ha
    rw [Set.mem_toFinset] at hPsN
    rcases P with _ | ⟨x, y, h⟩
    · exact absurd rfl hPsN.2
    · simp only [px] at hPa
      rw [← hPa]
      exact hmem x y h hPsN.1
  -- Each x-fiber has at most 2 points.
  have hfib : ∀ a ∈ N.toFinset.image px,
      (N.toFinset.filter (fun P => px P = a)).card ≤ 2 := by
    intro a _
    have hpoly_ne : (X ^ 2 - C (a ^ 3 + 7) : (ZMod Secp256k1.p)[X]) ≠ 0 :=
      X_pow_sub_C_ne_zero (by norm_num) (a ^ 3 + 7)
    have hpoly_deg : (X ^ 2 - C (a ^ 3 + 7) : (ZMod Secp256k1.p)[X]).natDegree ≤ 2 := by
      compute_degree
    have hroots_card :
        (X ^ 2 - C (a ^ 3 + 7) : (ZMod Secp256k1.p)[X]).roots.toFinset.card ≤ 2 :=
      (Multiset.toFinset_card_le _).trans ((card_roots' _).trans hpoly_deg)
    refine le_trans ?_ hroots_card
    apply Finset.card_le_card_of_injOn py
    · intro P hP
      rw [Finset.mem_coe, Finset.mem_filter, Set.mem_toFinset] at hP
      obtain ⟨hPN, hPa⟩ := hP
      rcases P with _ | ⟨x, y, h⟩
      · exact absurd rfl hPN.2
      · simp only [px] at hPa
        subst hPa
        have hcurve : y ^ 2 = x ^ 3 + 7 := secp256k1_curve_of_nonsingular x y h
        simp only [py, Finset.mem_coe, Multiset.mem_toFinset, mem_roots', IsRoot.def, eval_sub,
          eval_pow, eval_X, eval_C]
        exact ⟨hpoly_ne, by linear_combination hcurve⟩
    · intro P hP Q hQ hPQ
      rw [Finset.mem_coe, Finset.mem_filter, Set.mem_toFinset] at hP hQ
      rcases P with _ | ⟨x1, y1, h1⟩
      · exact absurd rfl hP.1.2
      rcases Q with _ | ⟨x2, y2, h2⟩
      · exact absurd rfl hQ.1.2
      · simp only [px] at hP hQ
        simp only [py] at hPQ
        have hxx : x1 = x2 := hP.2.trans hQ.2.symm
        subst hxx; subst hPQ; rfl
  -- Bound N.ncard ≤ 2*m.
  have hN_le : N.ncard ≤ 2 * m := by
    rw [hNcard]
    calc N.toFinset.card
        ≤ 2 * (N.toFinset.image px).card := by
          apply Finset.card_le_mul_card_image
          exact hfib
      _ ≤ 2 * Xf.card := Nat.mul_le_mul_left 2 (Finset.card_le_card himg_sub)
      _ ≤ 2 * m := Nat.mul_le_mul_left 2 hXcard
  -- T = insert 0 N.
  have hTins : T = insert 0 N := by
    ext P
    simp only [hT, hN, Set.mem_setOf_eq, Set.mem_insert_iff]
    constructor
    · intro hP0
      by_cases h : P = 0
      · exact Or.inl h
      · exact Or.inr ⟨hP0, h⟩
    · rintro (rfl | ⟨hP0, _⟩)
      · simp
      · exact hP0
  calc T.ncard = (insert 0 N).ncard := by rw [hTins]
    _ ≤ N.ncard + 1 := Set.ncard_insert_le 0 N
    _ ≤ 2 * m + 1 := Nat.add_le_add_right hN_le 1

/-! ### Point-count corollaries: #E[n] ≤ n² for n = 3, 5, 7 -/

/-- **#E[3] ≤ 9** (set form). secp256k1 has at most 9 three-torsion points. -/
theorem secp256k1_three_torsion_ncard_le :
    Set.ncard {P : secp256k1.toAffine.Point | (3 : ℕ) • P = 0} ≤ 9 := by
  have h := secp256k1_torsion_ncard_le 3 4 secp256k1.Ψ₃.roots.toFinset
    secp256k1_Ψ₃_roots_toFinset_card_le
    (fun x y hns ht => Multiset.mem_toFinset.mpr
      (secp256k1_three_torsion_x_mem_Ψ₃_roots x y hns ht))
  simpa using h

/-- **#E[5] ≤ 25** (set form). secp256k1 has at most 25 five-torsion points. -/
theorem secp256k1_five_torsion_ncard_le :
    Set.ncard {P : secp256k1.toAffine.Point | (5 : ℕ) • P = 0} ≤ 25 := by
  have hcard : Q5.roots.toFinset.card ≤ 12 :=
    (Multiset.toFinset_card_le _).trans ((card_roots' _).trans Q5_natDegree_le)
  have h := secp256k1_torsion_ncard_le 5 12 Q5.roots.toFinset hcard
    secp256k1_five_torsion_x_mem
  simpa using h

/-- **#E[7] ≤ 49** (set form). secp256k1 has at most 49 seven-torsion points. -/
theorem secp256k1_seven_torsion_ncard_le :
    Set.ncard {P : secp256k1.toAffine.Point | (7 : ℕ) • P = 0} ≤ 49 := by
  have hcard : Q7.roots.toFinset.card ≤ 24 :=
    (Multiset.toFinset_card_le _).trans ((card_roots' _).trans Q7_natDegree_le)
  have h := secp256k1_torsion_ncard_le 7 24 Q7.roots.toFinset hcard
    secp256k1_seven_torsion_x_mem
  simpa using h

/-- **#E[3] ≤ 9** (`Nat.card` subtype form). -/
theorem secp256k1_three_torsion_card_le :
    Nat.card {P : secp256k1.toAffine.Point // (3 : ℕ) • P = 0} ≤ 9 :=
  secp256k1_three_torsion_ncard_le

/-- **#E[5] ≤ 25** (`Nat.card` subtype form). -/
theorem secp256k1_five_torsion_card_le :
    Nat.card {P : secp256k1.toAffine.Point // (5 : ℕ) • P = 0} ≤ 25 :=
  secp256k1_five_torsion_ncard_le

/-- **#E[7] ≤ 49** (`Nat.card` subtype form). -/
theorem secp256k1_seven_torsion_card_le :
    Nat.card {P : secp256k1.toAffine.Point // (7 : ℕ) • P = 0} ≤ 49 :=
  secp256k1_seven_torsion_ncard_le

end Ecdlp.Curve
