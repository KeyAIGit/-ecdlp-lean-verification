import Mathlib
import Ecdlp.Proved.TorsionPointCount
import Ecdlp.Proved.TwoTorsionPoint
import Ecdlp.Proved.CurveTorsion

/-!
# Two secp256k1 torsion facts

* `secp256k1_two_torsion_ncard_le` — the **tight** point count `#E[2] ≤ 4`. The generic
  fiber lemma `secp256k1_torsion_ncard_le` gives only `2·3 + 1 = 7` because it allows two
  `y` per `x`; but 2-torsion is the special `y = 0` fiber, which is 1-to-1, so nonzero
  2-torsion injects into the ≤ 3 roots of `X³ + 7`, giving ≤ 3 nonzero points plus `O`.

* `secp256k1_torsionBy_inf_eq_gcd` — `E[m] ⊓ E[n] = E[gcd m n]`, generalizing the
  coprime-disjoint leaf, via the order characterization `P ∈ E[k] ↔ addOrderOf P ∣ k`.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Tight `#E[2] ≤ 4`.** secp256k1 has at most 4 two-torsion points. A nonzero 2-torsion
point is `some x y h` with `2 • P = 0`, hence `y = 0` (`secp256k1_two_nsmul_eq_zero_iff`),
hence `x³ + 7 = 0` by the curve equation. The map `some x 0 h ↦ x` is injective on nonzero
2-torsion (the `y = 0` fiber is 1-to-1), so nonzero 2-torsion injects into the ≤ 3 roots of
`X³ + C 7`; adding the identity gives ≤ 4. -/
theorem secp256k1_two_torsion_ncard_le :
    Set.ncard {P : secp256k1.toAffine.Point | (2 : ℕ) • P = 0} ≤ 4 := by
  classical
  haveI : NeZero Secp256k1.p := ⟨(Fact.out : Nat.Prime Secp256k1.p).pos.ne'⟩
  have h7 : (7 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((7 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
    simpa using h
  -- The cubic `X³ + 7`: nonzero, degree ≤ 3, so ≤ 3 roots.
  set f : (ZMod Secp256k1.p)[X] := X ^ 3 + C 7 with hf
  have hf_ne : f ≠ 0 := by
    intro hz
    have h0 : f.eval 0 = 0 := by rw [hz, eval_zero]
    rw [hf] at h0
    simp only [eval_add, eval_pow, eval_X, eval_C] at h0
    exact h7 (by linear_combination h0)
  have hf_deg : f.natDegree ≤ 3 := by rw [hf]; compute_degree
  have hroots_card : f.roots.toFinset.card ≤ 3 :=
    (Multiset.toFinset_card_le _).trans ((card_roots' _).trans hf_deg)
  set T := {P : secp256k1.toAffine.Point | (2 : ℕ) • P = 0} with hT
  set N := {P : secp256k1.toAffine.Point | (2 : ℕ) • P = 0 ∧ P ≠ 0} with hN
  -- The x-projection sends nonzero 2-torsion into the roots of `X³ + 7`.
  have hmem : ∀ P ∈ N, px P ∈ f.roots.toFinset := by
    intro P hP
    rcases P with _ | ⟨x, y, h⟩
    · exact absurd rfl hP.2
    · have hy : y = 0 := (secp256k1_two_nsmul_eq_zero_iff x y h).mp hP.1
      have hcurve : y ^ 2 = x ^ 3 + 7 := secp256k1_curve_of_nonsingular x y h
      simp only [px]
      rw [Multiset.mem_toFinset, mem_roots']
      refine ⟨hf_ne, ?_⟩
      simp only [hf, IsRoot.def, eval_add, eval_pow, eval_X, eval_C]
      rw [hy] at hcurve
      linear_combination -hcurve
  -- The x-projection is injective on nonzero 2-torsion (`y` is forced to `0`).
  have hpx_inj : Set.InjOn px N := by
    rintro P hP Q hQ hPQ
    rcases P with _ | ⟨x1, y1, h1⟩
    · exact absurd rfl hP.2
    rcases Q with _ | ⟨x2, y2, h2⟩
    · exact absurd rfl hQ.2
    · simp only [px] at hPQ
      have hy1 : y1 = 0 := (secp256k1_two_nsmul_eq_zero_iff x1 y1 h1).mp hP.1
      have hy2 : y2 = 0 := (secp256k1_two_nsmul_eq_zero_iff x2 y2 h2).mp hQ.1
      subst hPQ; subst hy1; subst hy2; rfl
  -- Hence `N` is finite and `N.ncard ≤ 3`.
  have himg_sub : px '' N ⊆ ↑(f.roots.toFinset) := by
    rintro a ⟨P, hP, rfl⟩
    exact hmem P hP
  have hNfin : N.Finite :=
    Set.Finite.of_finite_image
      (Set.Finite.subset (f.roots.toFinset).finite_toSet himg_sub) hpx_inj
  haveI : Fintype ↥N := hNfin.fintype
  have hNcard : N.ncard = N.toFinset.card := Set.ncard_eq_toFinset_card' N
  have hN_le : N.ncard ≤ 3 := by
    rw [hNcard]
    refine le_trans ?_ hroots_card
    apply Finset.card_le_card_of_injOn px
    · intro P hP
      rw [Finset.mem_coe, Set.mem_toFinset] at hP
      exact hmem P hP
    · intro P hP Q hQ hPQ
      rw [Finset.mem_coe, Set.mem_toFinset] at hP hQ
      exact hpx_inj hP hQ hPQ
  -- `T = insert 0 N`, so `T.ncard ≤ N.ncard + 1 ≤ 4`.
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
    _ ≤ 3 + 1 := Nat.add_le_add_right hN_le 1
    _ = 4 := rfl

/-- **Torsion intersection is the gcd: `E[m] ⊓ E[n] = E[gcd m n]`.** Generalizes the
coprime-disjoint leaf. `P ∈ E[m] ⊓ E[n] ↔ addOrderOf P ∣ m ∧ addOrderOf P ∣ n ↔
addOrderOf P ∣ gcd m n ↔ P ∈ E[gcd m n]`. -/
theorem secp256k1_torsionBy_inf_eq_gcd (m n : ℕ) :
    AddSubgroup.torsionBy secp256k1.toAffine.Point (m : ℤ) ⊓
      AddSubgroup.torsionBy secp256k1.toAffine.Point (n : ℤ)
      = AddSubgroup.torsionBy secp256k1.toAffine.Point (Nat.gcd m n : ℤ) := by
  ext P
  simp only [AddSubgroup.mem_inf, secp256k1_mem_torsionBy_iff_addOrderOf_dvd]
  exact ⟨fun ⟨hm, hn⟩ => Nat.dvd_gcd hm hn,
         fun h => ⟨h.trans (Nat.gcd_dvd_left m n), h.trans (Nat.gcd_dvd_right m n)⟩⟩

end Ecdlp.Curve
