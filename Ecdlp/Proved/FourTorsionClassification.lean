import Ecdlp.Proved.TorsionStructure

/-!
# Classification of finite abelian groups with four-torsion profile

The prime-exponent classification in `TorsionStructure.lean` does not apply to exponent
four. This module closes the first composite case constructively: a finite abelian group
killed by four, with 16 elements and exactly four elements killed by two, is additively
equivalent to `(ZMod 4)^2`.
-/

namespace Ecdlp.Torsion

open AddSubgroup

/-- A finite abelian group killed by four, of order 16, whose two-torsion has order four,
is additively equivalent to `(ZMod 4)^2`. -/
theorem nonempty_addEquiv_zmod_four_prod_of_card_and_two_torsion
    {A : Type*} [acg : AddCommGroup A]
    (hkill : ∀ a : A, (4 : ℕ) • a = 0)
    (hcard : Nat.card A = 16)
    (hcardTwo :
      Nat.card
        ↥(AddSubgroup.torsionBy A ((2 : ℕ) : ℤ)) = 4) :
    Nonempty (A ≃+ ZMod 4 × ZMod 4) := by
  have hpos : 0 < Nat.card A := hcard ▸ by norm_num
  haveI hfiniteA : Finite A := (Nat.card_pos_iff.mp hpos).2
  let B : AddSubgroup A := AddSubgroup.torsionBy A ((2 : ℕ) : ℤ)
  have hcardB : Nat.card B = 4 := by
    simpa [B] using hcardTwo
  haveI hfiniteB : Finite B := inferInstance
  haveI : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩
  obtain ⟨eTwo⟩ :
      Nonempty (B ≃+ ZMod 2 × ZMod 2) :=
    nonempty_addEquiv_zmod_prod_of_card_eq_sq
      (fun b => AddSubgroup.torsionBy.nsmul b)
      (hcardB.trans (by norm_num))
  let d : A →+ A := nsmulAddMonoidHom 2
  have hker : d.ker = B := by
    ext a
    simp only [AddMonoidHom.mem_ker, d, nsmulAddMonoidHom_apply, B,
      AddSubgroup.torsionBy.nsmul_iff]
  have hrangeCard : Nat.card d.range = 4 := by
    have hmul : Nat.card d.ker * Nat.card d.range = Nat.card A := by
      simpa only [AddSubgroup.index_ker] using d.ker.card_mul_index
    rw [hker, hcardB, hcard] at hmul
    omega
  have hrangeLe : d.range ≤ B := by
    rintro _ ⟨a, rfl⟩
    simp only [B, AddSubgroup.torsionBy.nsmul_iff]
    rw [show d a = (2 : ℕ) • a by simp [d]]
    rw [← mul_nsmul]
    norm_num
    exact hkill a
  have hrangeEq : d.range = B :=
    AddSubgroup.eq_of_le_of_card_ge hrangeLe (by omega)
  let u : B := eTwo.symm (1, 0)
  let v : B := eTwo.symm (0, 1)
  obtain ⟨x, hx⟩ : ∃ x : A, d x = u := by
    have hu : (u : A) ∈ d.range := by
      rw [hrangeEq]
      exact u.property
    simpa only [AddMonoidHom.mem_range] using hu
  obtain ⟨y, hy⟩ : ∃ y : A, d y = v := by
    have hv : (v : A) ∈ d.range := by
      rw [hrangeEq]
      exact v.property
    simpa only [AddMonoidHom.mem_range] using hv
  have hxTwo : (2 : ℕ) • x = (u : A) := by
    simpa [d] using hx
  have hyTwo : (2 : ℕ) • y = (v : A) := by
    simpa [d] using hy
  have hu_ne : (u : A) ≠ 0 := by
    intro hu
    have hu' : u = 0 := Subtype.ext hu
    have := congrArg eTwo hu'
    simpa [u] using this
  have hv_ne : (v : A) ≠ 0 := by
    intro hv
    have hv' : v = 0 := Subtype.ext hv
    have := congrArg eTwo hv'
    simpa [v] using this
  have huv_ne : (u : A) + (v : A) ≠ 0 := by
    intro huv
    have huv' : u + v = 0 := by
      apply Subtype.ext
      simpa using huv
    have := congrArg eTwo huv'
    simpa [u, v] using this
  let delta : A →+ B :=
    d.codRestrict B fun a => hrangeLe ⟨a, rfl⟩
  let q : A →+ ZMod 2 × ZMod 2 :=
    eTwo.toAddMonoidHom.comp delta
  have hdeltaX : delta x = u := by
    apply Subtype.ext
    exact hx
  have hdeltaY : delta y = v := by
    apply Subtype.ext
    exact hy
  have hqx : q x = (1, 0) := by
    change eTwo (delta x) = (1, 0)
    rw [hdeltaX]
    simpa [u]
  have hqy : q y = (0, 1) := by
    change eTwo (delta y) = (0, 1)
    rw [hdeltaY]
    simpa [v]
  have huTwo : (2 : ℕ) • (u : A) = 0 := by
    simpa using congrArg (fun b : B => (b : A)) (AddSubgroup.torsionBy.nsmul u)
  have hvTwo : (2 : ℕ) • (v : A) = 0 := by
    simpa using congrArg (fun b : B => (b : A)) (AddSubgroup.torsionBy.nsmul v)
  have hdeltaU : delta (u : A) = 0 := by
    apply Subtype.ext
    simpa [delta, d] using huTwo
  have hdeltaV : delta (v : A) = 0 := by
    apply Subtype.ext
    simpa [delta, d] using hvTwo
  have hqu : q (u : A) = 0 := by
    change eTwo (delta (u : A)) = 0
    rw [hdeltaU, map_zero]
  have hqv : q (v : A) = 0 := by
    change eTwo (delta (v : A)) = 0
    rw [hdeltaV, map_zero]
  have hthreeModTwo : (3 : ZMod 2) = 1 := by
    calc
      (3 : ZMod 2) = 1 + (2 : ZMod 2) := by ring
      _ = 1 := by
        have htwo : (2 : ZMod 2) = 0 :=
          CharP.ofNat_eq_zero' (R := ZMod 2) 2 2 dvd_rfl
        rw [htwo, add_zero]
  let zx : ZMod 4 →+ A :=
    ZMod.lift 4
      ⟨zmultiplesHom A x, by
        simpa only [zmultiplesHom_apply, Int.ofNat_eq_coe, natCast_zsmul] using hkill x⟩
  let zy : ZMod 4 →+ A :=
    ZMod.lift 4
      ⟨zmultiplesHom A y, by
        simpa only [zmultiplesHom_apply, Int.ofNat_eq_coe, natCast_zsmul] using hkill y⟩
  have hzx (m : ℤ) : zx (m : ZMod 4) = m • x := by
    simp [zx, zmultiplesHom_apply]
  have hzy (m : ℤ) : zy (m : ZMod 4) = m • y := by
    simp [zy, zmultiplesHom_apply]
  have hzxOne : zx (1 : ZMod 4) = x := by
    simpa using hzx 1
  have hzyOne : zy (1 : ZMod 4) = y := by
    simpa using hzy 1
  have hzxNat (m : ℕ) : zx (m : ZMod 4) = m • x := by
    simpa [hzxOne] using zx.map_nsmul m (1 : ZMod 4)
  have hzyNat (m : ℕ) : zy (m : ZMod 4) = m • y := by
    simpa [hzyOne] using zy.map_nsmul m (1 : ZMod 4)
  have hzxZero : zx (0 : ZMod 4) = 0 := by simpa using hzxNat 0
  have hzyZero : zy (0 : ZMod 4) = 0 := by simpa using hzyNat 0
  have hzxTwo : zx (2 : ZMod 4) = (2 : ℕ) • x := by simpa using hzxNat 2
  have hzyTwo : zy (2 : ZMod 4) = (2 : ℕ) • y := by simpa using hzyNat 2
  have hzxThree : zx (3 : ZMod 4) = (3 : ℕ) • x := by simpa using hzxNat 3
  have hzyThree : zy (3 : ZMod 4) = (3 : ℕ) • y := by simpa using hzyNat 3
  let f : ZMod 4 × ZMod 4 →+ A :=
    (zx.comp (AddMonoidHom.fst (ZMod 4) (ZMod 4))) +
      zy.comp (AddMonoidHom.snd (ZMod 4) (ZMod 4))
  have hf_ker : ∀ z, f z = 0 → z = 0 := by
    rintro ⟨a, b⟩ hz
    have hqz : q (f (a, b)) = 0 := by rw [hz, map_zero]
    have haLt : a.val < 4 := ZMod.val_lt a
    have hbLt : b.val < 4 := ZMod.val_lt b
    rw [← ZMod.natCast_zmod_val a, ← ZMod.natCast_zmod_val b] at hz hqz ⊢
    interval_cases ha : a.val <;> interval_cases hb : b.val <;>
      simp [f, hzxZero, hzyZero, hzxOne, hzyOne, hzxTwo, hzyTwo,
        hzxThree, hzyThree, hqx, hqy, hqu, hqv, hthreeModTwo,
        hxTwo, hyTwo, hu_ne, hv_ne, huv_ne] at hqz hz ⊢ <;>
      norm_num at hqz
  have hf_injective : Function.Injective f := by
    intro z w hzw
    rw [← sub_eq_zero]
    apply hf_ker
    rw [map_sub, hzw, sub_self]
  letI : Fintype A := Fintype.ofFinite A
  have hf_bijective : Function.Bijective f := by
    rw [Fintype.bijective_iff_injective_and_card]
    refine ⟨hf_injective, ?_⟩
    simpa [← Nat.card_eq_fintype_card, hcard]
  exact ⟨(AddEquiv.ofBijective f hf_bijective).symm⟩

end Ecdlp.Torsion
