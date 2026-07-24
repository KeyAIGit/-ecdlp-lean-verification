import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialSeparable
import Ecdlp.Proved.CoprimePsi2PrePsi4
import Ecdlp.Proved.DivisionResultantTransport
import Ecdlp.Proved.FourTorsionBridgeBar
import Ecdlp.Proved.TwoTorsionStructure
import Ecdlp.Proved.FourTorsionClassification

/-!
# `#E[4](𝔽̄_p) = 16` and `E[4](𝔽̄_p) ≅ ℤ/4 × ℤ/4`

This is the first composite-index member of the exact closure torsion family. The count
splits the 4-torsion into two disjoint pieces:

* the already-counted 2-torsion, with `4` points;
* the primitive 4-torsion `{P | 4 • P = 0 ∧ 2 • P ≠ 0}`.

The mapped primitive division polynomial `preΨ₄` has six distinct roots. Coprimality of
`Ψ₂Sq` and `preΨ₄` ensures that the chosen square root above each root is nonzero, so every
root contributes the two distinct points `(x, y)` and `(x, -y)`. The closure bridge
identifies these twelve points with the primitive 4-torsion, giving `4 + 12 = 16`.

For the structure theorem, the internal 2-torsion of the group `E[4]` is identified
explicitly with ambient `E[2]`. The composite-order classification theorem then applies
to a group killed by four, of cardinality sixteen, with four elements killed by two.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

open scoped Classical

/-- The base-change hom `𝔽_p →+* 𝔽̄_p`. -/
private noncomputable abbrev φcl :
    ZMod Secp256k1.p →+* AlgebraicClosure (ZMod Secp256k1.p) :=
  algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p))

private theorem φcl_ne_zero {c : ZMod Secp256k1.p} (hc : c ≠ 0) : φcl c ≠ 0 := by
  intro h0
  exact hc (RingHom.injective φcl (by rw [map_zero]; exact h0))

private theorem two_ne_zero_bar :
    (2 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
  have h2p : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]
      decide
    simpa using h
  have hφ := φcl_ne_zero h2p
  rwa [map_ofNat] at hφ

/-- File-local registration of ellipticity for the mapped curve. -/
private instance secp256k1Bar_isElliptic_four : secp256k1Bar.IsElliptic :=
  inferInstanceAs ((secp256k1.map φcl).IsElliptic)

/-! ## Lifting roots to closure points -/

private noncomputable def liftY (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    AlgebraicClosure (ZMod Secp256k1.p) :=
  (exists_nonsingular_y secp256k1Bar x).choose

private theorem liftY_nonsingular (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.Nonsingular x (liftY x) :=
  (exists_nonsingular_y secp256k1Bar x).choose_spec

private noncomputable def liftP (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.Point :=
  Point.some x (liftY x) (liftY_nonsingular x)

private theorem liftP_def (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    liftP x = Point.some x (liftY x) (liftY_nonsingular x) := rfl

private theorem secp256k1Bar_curve_of_nonsingular
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) :
    y ^ 2 = x ^ 3 + 7 := by
  have he : secp256k1Bar.toAffine.Equation x y := h.1
  rw [WeierstrassCurve.Affine.equation_iff] at he
  simp only [secp256k1Bar, WeierstrassCurve.map, WeierstrassCurve.map_a₁,
    WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄,
    WeierstrassCurve.map_a₆, secp256k1, map_zero, map_ofNat] at he
  linear_combination he

private theorem secp256k1Bar_negY
    (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.negY x y = -y := by
  simp [WeierstrassCurve.Affine.negY, secp256k1Bar, WeierstrassCurve.map, secp256k1]

private theorem liftY_sq (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    (liftY x) ^ 2 = x ^ 3 + 7 :=
  secp256k1Bar_curve_of_nonsingular x (liftY x) (liftY_nonsingular x)

/-! ## The six roots of the primitive 4-division polynomial -/

private theorem secp256k1Bar_preΨ₄_map :
    secp256k1Bar.preΨ₄ = (secp256k1.preΨ₄).map φcl := by
  simp only [secp256k1Bar, WeierstrassCurve.map_preΨ₄]

private theorem preΨ₄bar_roots_card :
    ((secp256k1.preΨ₄).map φcl).roots.card = 6 :=
  secp256k1_preΨ₄_roots_card_bar

private theorem preΨ₄bar_roots_nodup :
    ((secp256k1.preΨ₄).map φcl).roots.Nodup :=
  secp256k1_preΨ₄_roots_nodup_bar

private theorem preΨ₄bar_ne_zero : (secp256k1.preΨ₄).map φcl ≠ 0 := by
  intro h0
  have hc := preΨ₄bar_roots_card
  rw [h0, Polynomial.roots_zero] at hc
  simp at hc

private theorem preΨ₄bar_roots_toFinset_card :
    ((secp256k1.preΨ₄).map φcl).roots.toFinset.card = 6 := by
  have h := Multiset.toFinset_card_of_nodup preΨ₄bar_roots_nodup
  rw [preΨ₄bar_roots_card] at h
  exact h

private theorem eval_of_mem_preΨ₄bar_roots
    {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : a ∈ ((secp256k1.preΨ₄).map φcl).roots.toFinset) :
    ((secp256k1.preΨ₄).map φcl).eval a = 0 :=
  (mem_roots'.mp (Multiset.mem_toFinset.mp ha)).2

private theorem mem_preΨ₄bar_roots_of_eval
    {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ₄).map φcl).eval a = 0) :
    a ∈ ((secp256k1.preΨ₄).map φcl).roots.toFinset :=
  Multiset.mem_toFinset.mpr (mem_roots'.mpr ⟨preΨ₄bar_ne_zero, ha⟩)

/-! ## Nonzero fibres from `Ψ₂Sq ⊥ preΨ₄` -/

private theorem no_common_root {K : Type*} [Field K] {F G : K[X]} (h : IsCoprime F G)
    {x₀ : K} (hF : F.eval x₀ = 0) (hG : G.eval x₀ = 0) : False := by
  obtain ⟨u, v, huv⟩ := h
  have h1 := congrArg (Polynomial.eval x₀) huv
  simp [hF, hG] at h1

private theorem preΨ₄bar_isCoprime_Ψ₂Sq :
    IsCoprime ((secp256k1.Ψ₂Sq).map φcl) ((secp256k1.preΨ₄).map φcl) := by
  have h := secp256k1_isCoprime_Ψ₂Sq_preΨ₄.map (Polynomial.mapRingHom φcl)
  simpa only [Polynomial.coe_mapRingHom] using h

private theorem Ψ₂Sqbar_eval (a : AlgebraicClosure (ZMod Secp256k1.p)) :
    ((secp256k1.Ψ₂Sq).map φcl).eval a = 4 * (a ^ 3 + 7) := by
  rw [secp256k1_Ψ₂Sq]
  simp only [Polynomial.map_add, Polynomial.map_mul, Polynomial.map_pow,
    Polynomial.map_C, Polynomial.map_X, Polynomial.map_ofNat, map_ofNat, eval_add,
    eval_mul, eval_pow, eval_C, eval_X, Polynomial.eval_ofNat]
  ring

private theorem x_cube_add_seven_ne_zero_of_root
    {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ₄).map φcl).eval a = 0) :
    a ^ 3 + 7 ≠ 0 := by
  intro h7
  have hΨ2 : ((secp256k1.Ψ₂Sq).map φcl).eval a = 0 := by
    rw [Ψ₂Sqbar_eval]
    linear_combination 4 * h7
  exact no_common_root preΨ₄bar_isCoprime_Ψ₂Sq hΨ2 ha

private theorem liftY_ne_zero
    {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ₄).map φcl).eval a = 0) :
    liftY a ≠ 0 := by
  intro h0
  have hsq := liftY_sq a
  rw [h0] at hsq
  exact x_cube_add_seven_ne_zero_of_root ha (by linear_combination -hsq)

private theorem liftY_ne_neg
    {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ₄).map φcl).eval a = 0) :
    liftY a ≠ -liftY a := by
  intro h
  have h2 : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * liftY a = 0 := by
    linear_combination h
  rcases mul_eq_zero.mp h2 with h2' | hy0
  · exact two_ne_zero_bar h2'
  · exact liftY_ne_zero ha hy0

/-! ## Primitive 4-torsion membership -/

private theorem secp256k1Bar_psi_four_eval
    (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    (secp256k1Bar.ψ 4).evalEval x y =
      2 * y * secp256k1Bar.preΨ₄.eval x := by
  rw [secp256k1Bar.ψ_four]
  simp only [evalEval_mul, evalEval_C]
  rw [secp256k1Bar_psi2_evalEval]
  ring

private theorem liftP_four_nsmul
    {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ₄).map φcl).eval a = 0) :
    (4 : ℕ) • liftP a = 0 := by
  rw [liftP_def]
  apply (secp256k1Bar_four_nsmul_eq_zero_iff
    a (liftY a) (liftY_nonsingular a)).mpr
  rw [secp256k1Bar_psi_four_eval, secp256k1Bar_preΨ₄_map, ha]
  ring

private theorem liftP_two_nsmul_ne_zero
    {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ₄).map φcl).eval a = 0) :
    (2 : ℕ) • liftP a ≠ 0 := by
  intro h2
  rw [liftP_def] at h2
  exact liftY_ne_zero ha
    ((secp256k1Bar_two_nsmul_eq_zero_iff
      a (liftY a) (liftY_nonsingular a)).mp h2)

private theorem four_nsmul_neg {P : secp256k1Bar.toAffine.Point}
    (hP : (4 : ℕ) • P = 0) :
    (4 : ℕ) • (-P) = 0 := by
  have hmem :
      P ∈ AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((4 : ℕ) : ℤ) :=
    AddSubgroup.torsionBy.nsmul_iff.mpr hP
  exact AddSubgroup.torsionBy.nsmul_iff.mp (neg_mem hmem)

private theorem two_nsmul_neg_ne_zero {P : secp256k1Bar.toAffine.Point}
    (hP : (2 : ℕ) • P ≠ 0) :
    (2 : ℕ) • (-P) ≠ 0 := by
  intro hneg
  have hmemNeg :
      -P ∈ AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((2 : ℕ) : ℤ) :=
    AddSubgroup.torsionBy.nsmul_iff.mpr hneg
  have hmem :
      P ∈ AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((2 : ℕ) : ℤ) := by
    simpa using (neg_mem hmemNeg)
  exact hP (AddSubgroup.torsionBy.nsmul_iff.mp hmem)

/-! ## Exact enumeration of the twelve primitive points -/

private theorem primitive_four_torsion_finset_card :
    (((((secp256k1.preΨ₄).map φcl).roots.toFinset.image liftP)
      ∪ (((secp256k1.preΨ₄).map φcl).roots.toFinset.image fun a => -liftP a))).card
      = 12 := by
  have hinj1 :
      Set.InjOn liftP ↑(((secp256k1.preΨ₄).map φcl).roots.toFinset) := by
    intro a _ b _ hab
    simp only [liftP_def, Point.some.injEq] at hab
    exact hab.1
  have hinj2 :
      Set.InjOn (fun a => -liftP a)
        ↑(((secp256k1.preΨ₄).map φcl).roots.toFinset) := by
    intro a ha b hb hab
    have h' : -liftP a = -liftP b := hab
    exact hinj1 ha hb (neg_inj.mp h')
  have hdisj :
      Disjoint (((secp256k1.preΨ₄).map φcl).roots.toFinset.image liftP)
        (((secp256k1.preΨ₄).map φcl).roots.toFinset.image fun a => -liftP a) := by
    rw [Finset.disjoint_left]
    intro P hP hQ
    rw [Finset.mem_image] at hP hQ
    obtain ⟨a, haR, rfl⟩ := hP
    obtain ⟨b, -, hEq⟩ := hQ
    have hEq' : -liftP b = liftP a := hEq
    simp only [liftP_def] at hEq'
    rw [Point.neg_some, Point.some.injEq] at hEq'
    obtain ⟨hba, hyy⟩ := hEq'
    subst hba
    rw [secp256k1Bar_negY] at hyy
    exact liftY_ne_neg (eval_of_mem_preΨ₄bar_roots haR) hyy.symm
  have h1 := Finset.card_union_of_disjoint hdisj
  have h2 :
      ((((secp256k1.preΨ₄).map φcl).roots.toFinset.image liftP).card = 6) :=
    (Finset.card_image_of_injOn hinj1).trans preΨ₄bar_roots_toFinset_card
  have h3 :
      ((((secp256k1.preΨ₄).map φcl).roots.toFinset.image fun a => -liftP a).card = 6) :=
    (Finset.card_image_of_injOn hinj2).trans preΨ₄bar_roots_toFinset_card
  omega

private theorem primitive_four_torsion_set_eq :
    {P : secp256k1Bar.toAffine.Point |
      (4 : ℕ) • P = 0 ∧ (2 : ℕ) • P ≠ 0}
      =
      ↑((((secp256k1.preΨ₄).map φcl).roots.toFinset.image liftP)
        ∪ (((secp256k1.preΨ₄).map φcl).roots.toFinset.image fun a => -liftP a)) := by
  ext P
  simp only [Set.mem_setOf_eq, Finset.mem_coe]
  constructor
  · intro hP
    rcases P with _ | ⟨x, y, h⟩
    · exact (hP.2 (by simp)).elim
    · have hy : y ≠ 0 := fun hy0 =>
        hP.2 ((secp256k1Bar_two_nsmul_eq_zero_iff x y h).mpr hy0)
      have hψ :
          (secp256k1Bar.ψ 4).evalEval x y = 0 :=
        (secp256k1Bar_four_nsmul_eq_zero_iff x y h).mp hP.1
      rw [secp256k1Bar_psi_four_eval] at hψ
      have hpre : secp256k1Bar.preΨ₄.eval x = 0 := by
        rcases mul_eq_zero.mp hψ with h2y | hpre
        · rcases mul_eq_zero.mp h2y with h2 | hy0
          · exact (two_ne_zero_bar h2).elim
          · exact (hy hy0).elim
        · exact hpre
      have hroot : ((secp256k1.preΨ₄).map φcl).eval x = 0 := by
        rw [← secp256k1Bar_preΨ₄_map]
        exact hpre
      have hxR : x ∈ ((secp256k1.preΨ₄).map φcl).roots.toFinset :=
        mem_preΨ₄bar_roots_of_eval hroot
      have hy2 : y ^ 2 = x ^ 3 + 7 :=
        secp256k1Bar_curve_of_nonsingular x y h
      have hz2 : (liftY x) ^ 2 = x ^ 3 + 7 := liftY_sq x
      have hyz : (y - liftY x) * (y + liftY x) = 0 := by
        linear_combination hy2 - hz2
      rcases mul_eq_zero.mp hyz with h1 | h2
      · have hyEq : y = liftY x := sub_eq_zero.mp h1
        subst hyEq
        exact Finset.mem_union_left _ (Finset.mem_image.mpr ⟨x, hxR, rfl⟩)
      · have hyEq : y = -liftY x := by
          linear_combination h2
        refine Finset.mem_union_right _ (Finset.mem_image.mpr ⟨x, hxR, ?_⟩)
        show -liftP x = Point.some x y h
        rw [liftP_def, Point.neg_some, Point.some.injEq]
        exact ⟨rfl, by rw [secp256k1Bar_negY]; exact hyEq.symm⟩
  · intro hP
    rw [Finset.mem_union] at hP
    rcases hP with hP | hP <;> rw [Finset.mem_image] at hP <;>
      obtain ⟨a, haR, rfl⟩ := hP
    · have ha := eval_of_mem_preΨ₄bar_roots haR
      exact ⟨liftP_four_nsmul ha, liftP_two_nsmul_ne_zero ha⟩
    · have ha := eval_of_mem_preΨ₄bar_roots haR
      exact ⟨four_nsmul_neg (liftP_four_nsmul ha),
        two_nsmul_neg_ne_zero (liftP_two_nsmul_ne_zero ha)⟩

private theorem primitive_four_torsion_ncard :
    Set.ncard
      {P : secp256k1Bar.toAffine.Point |
        (4 : ℕ) • P = 0 ∧ (2 : ℕ) • P ≠ 0} = 12 := by
  rw [primitive_four_torsion_set_eq, Set.ncard_coe_finset]
  exact primitive_four_torsion_finset_card

private theorem primitive_four_torsion_finite :
    Set.Finite
      {P : secp256k1Bar.toAffine.Point |
        (4 : ℕ) • P = 0 ∧ (2 : ℕ) • P ≠ 0} := by
  rw [primitive_four_torsion_set_eq]
  exact Finset.finite_toSet _

private theorem two_torsion_finite :
    Set.Finite
      {P : secp256k1Bar.toAffine.Point | (2 : ℕ) • P = 0} := by
  apply Set.finite_of_ncard_pos
  rw [secp256k1Bar_two_torsion_ncard]
  norm_num

private theorem two_primitive_four_disjoint :
    Disjoint
      {P : secp256k1Bar.toAffine.Point | (2 : ℕ) • P = 0}
      {P : secp256k1Bar.toAffine.Point |
        (4 : ℕ) • P = 0 ∧ (2 : ℕ) • P ≠ 0} := by
  rw [Set.disjoint_left]
  intro P h2 h4
  exact h4.2 h2

private theorem four_torsion_set_eq :
    {P : secp256k1Bar.toAffine.Point | (4 : ℕ) • P = 0}
      =
      {P : secp256k1Bar.toAffine.Point | (2 : ℕ) • P = 0}
        ∪
      {P : secp256k1Bar.toAffine.Point |
        (4 : ℕ) • P = 0 ∧ (2 : ℕ) • P ≠ 0} := by
  ext P
  simp only [Set.mem_setOf_eq, Set.mem_union]
  constructor
  · intro h4
    by_cases h2 : (2 : ℕ) • P = 0
    · exact Or.inl h2
    · exact Or.inr ⟨h4, h2⟩
  · rintro (h2 | h4)
    · calc
        (4 : ℕ) • P = (2 : ℕ) • P + (2 : ℕ) • P := by
          rw [show (4 : ℕ) = 2 + 2 from rfl, add_nsmul]
        _ = 0 := by simp [h2]
    · exact h4.1

/-! ## Exact cardinality -/

/-- **`#E[4](𝔽̄_p) = 16`** (set form). -/
theorem secp256k1Bar_four_torsion_ncard :
    Set.ncard
      {P : secp256k1Bar.toAffine.Point | (4 : ℕ) • P = 0} = 16 := by
  calc
    Set.ncard {P : secp256k1Bar.toAffine.Point | (4 : ℕ) • P = 0}
        =
        Set.ncard
          ({P : secp256k1Bar.toAffine.Point | (2 : ℕ) • P = 0}
            ∪
          {P : secp256k1Bar.toAffine.Point |
            (4 : ℕ) • P = 0 ∧ (2 : ℕ) • P ≠ 0}) := by
              rw [four_torsion_set_eq]
    _ =
        Set.ncard
            {P : secp256k1Bar.toAffine.Point | (2 : ℕ) • P = 0}
          +
        Set.ncard
            {P : secp256k1Bar.toAffine.Point |
              (4 : ℕ) • P = 0 ∧ (2 : ℕ) • P ≠ 0} :=
      Set.ncard_union_eq two_primitive_four_disjoint
        two_torsion_finite primitive_four_torsion_finite
    _ = 4 + 12 := by
      rw [secp256k1Bar_two_torsion_ncard, primitive_four_torsion_ncard]
    _ = 16 := by norm_num

/-- **`#E[4](𝔽̄_p) = 16`** (`Nat.card` subtype form). -/
theorem secp256k1Bar_four_torsion_card :
    Nat.card
      {P : secp256k1Bar.toAffine.Point // (4 : ℕ) • P = 0} = 16 :=
  secp256k1Bar_four_torsion_ncard

/-- **`#E[4](𝔽̄_p) = 16`** (`torsionBy` subgroup form). -/
theorem secp256k1Bar_torsionBy_four_card :
    Nat.card
      ↥(AddSubgroup.torsionBy
        secp256k1Bar.toAffine.Point ((4 : ℕ) : ℤ)) = 16 := by
  have he :
      ↥(AddSubgroup.torsionBy
          secp256k1Bar.toAffine.Point ((4 : ℕ) : ℤ))
        ≃
      {P : secp256k1Bar.toAffine.Point // (4 : ℕ) • P = 0} :=
    Equiv.subtypeEquivRight fun _ => AddSubgroup.torsionBy.nsmul_iff
  rw [Nat.card_congr he]
  exact secp256k1Bar_four_torsion_card

/-! ## Identifying the internal two-torsion of `E[4]` with ambient `E[2]` -/

private abbrev BarPoint := secp256k1Bar.toAffine.Point

private abbrev BarFourTorsion :=
  ↥(AddSubgroup.torsionBy BarPoint ((4 : ℕ) : ℤ))

private abbrev BarFourTwoTorsion :=
  ↥(AddSubgroup.torsionBy BarFourTorsion ((2 : ℕ) : ℤ))

private abbrev BarTwoTorsion :=
  ↥(AddSubgroup.torsionBy BarPoint ((2 : ℕ) : ℤ))

/-- Forgetting the `E[4]` wrapper identifies its internal 2-torsion with ambient `E[2]`. -/
private noncomputable def fourTwoTorsionEquiv : BarFourTwoTorsion ≃ BarTwoTorsion where
  toFun a :=
    ⟨a.1.1, AddSubgroup.torsionBy.nsmul_iff.mpr (by
      have h := congrArg
        (fun b : BarFourTwoTorsion => (b.1.1 : BarPoint))
        (AddSubgroup.torsionBy.nsmul a)
      simpa using h)⟩
  invFun q := by
    have h2 : (2 : ℕ) • (q.1 : BarPoint) = 0 := by
      have h := congrArg
        (fun b : BarTwoTorsion => (b.1 : BarPoint))
        (AddSubgroup.torsionBy.nsmul q)
      simpa using h
    have h4 : (4 : ℕ) • (q.1 : BarPoint) = 0 := by
      calc
        (4 : ℕ) • (q.1 : BarPoint)
            = (2 : ℕ) • (q.1 : BarPoint) + (2 : ℕ) • (q.1 : BarPoint) := by
                rw [show (4 : ℕ) = 2 + 2 from rfl, add_nsmul]
        _ = 0 := by simp [h2]
    let q4 : BarFourTorsion :=
      ⟨q.1, AddSubgroup.torsionBy.nsmul_iff.mpr h4⟩
    refine ⟨q4, AddSubgroup.torsionBy.nsmul_iff.mpr ?_⟩
    apply Subtype.ext
    simpa [q4] using h2
  left_inv a := by
    apply Subtype.ext
    apply Subtype.ext
    rfl
  right_inv q := by
    apply Subtype.ext
    rfl

/-! ## Composite-order structure -/

/-- **`E[4](𝔽̄_p) ≅ ℤ/4 × ℤ/4`.** -/
theorem secp256k1Bar_four_torsion_structure :
    Nonempty
      (↥(AddSubgroup.torsionBy
          secp256k1Bar.toAffine.Point ((4 : ℕ) : ℤ))
        ≃+ ZMod 4 × ZMod 4) := by
  have hcardTwo : Nat.card BarFourTwoTorsion = 4 := by
    calc
      Nat.card BarFourTwoTorsion = Nat.card BarTwoTorsion :=
        Nat.card_congr fourTwoTorsionEquiv
      _ = 4 := secp256k1Bar_torsionBy_two_card
  exact Ecdlp.Torsion.nonempty_addEquiv_zmod_four_prod_of_card_and_two_torsion
    (fun a => AddSubgroup.torsionBy.nsmul a)
    secp256k1Bar_torsionBy_four_card
    hcardTwo

end Ecdlp.Curve
