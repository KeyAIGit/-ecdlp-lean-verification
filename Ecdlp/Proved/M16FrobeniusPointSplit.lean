import Mathlib.FieldTheory.Finite.Basic
import Ecdlp.Proved.M16FactorBaseLiftable

/-!
# Conditional point-level Frobenius split for the M16 lane

This is a conditional point-witness layer only.  It deliberately starts with
actual curve points and an actual point-sum relation.  It proves no
`S17At`/direct-root/frozen-root/chart-root-to-point existence theorem, no
factor-base membership or recovery completeness, and no solver, yield, rank,
cost, or ECDLP shortcut claim.
-/

namespace Ecdlp.M16FrobeniusPointSplit

open WeierstrassCurve.Affine
open Ecdlp.Curve

noncomputable section

/-- The secp256k1 base field. -/
abbrev Fp := ZMod Secp256k1.p

/-- A fixed algebraic closure containing the canonical quadratic subfield. -/
abbrev FpBar := AlgebraicClosure Fp

local instance : DecidableEq FpBar := Classical.decEq _

/-- Base-field secp256k1 points. -/
abbrev BasePoint := secp256k1.toAffine.Point

/-- secp256k1 base-changed to the chosen algebraic closure. -/
abbrev BarCurve := secp256k1 ⁄ FpBar

/-- secp256k1 points over the chosen algebraic closure. -/
abbrev BarPoint := BarCurve.Point

private instance barCurve_isElliptic : BarCurve.IsElliptic :=
  inferInstanceAs
    ((secp256k1.map (algebraMap Fp FpBar)).IsElliptic)

/-- Arithmetic Frobenius of the algebraic closure over `Fp`. -/
noncomputable def frobeniusField : FpBar ≃ₐ[Fp] FpBar :=
  FiniteField.frobeniusAlgEquivOfAlgebraic Fp FpBar

/-- Arithmetic Frobenius on secp256k1 points, induced coordinatewise. -/
noncomputable def frobeniusPoint : BarPoint →+ BarPoint :=
  WeierstrassCurve.Affine.Point.map
    (W' := secp256k1) frobeniusField.toAlgHom

private noncomputable def mapPoint
    {F K : Type*} [Field F] [Field K]
    [DecidableEq F] [DecidableEq K]
    (W : WeierstrassCurve.Affine F) [W.IsElliptic]
    (f : F →+* K) : W.Point →+ (W.map f).Point where
  toFun P := match P with
    | 0 => 0
    | Point.some _ _ h =>
        Point.some _ _ <| (W.map_nonsingular f.injective ..).mpr h
  map_zero' := rfl
  map_add' := by
    rintro (_ | ⟨x₁, y₁, h₁⟩) (_ | ⟨x₂, y₂, h₂⟩)
    any_goals rfl
    by_cases hxy : x₁ = x₂ ∧ y₁ = W.negY x₂ y₂
    · rw [Point.add_of_Y_eq hxy.left hxy.right,
        Point.add_of_Y_eq (congrArg _ hxy.left) <| by
          rw [hxy.right, W.map_negY]]
    · simpa only [Point.add_some hxy, ← W.map_addX,
        ← W.map_addY, ← W.map_slope] using!
        (Point.add_some fun h ↦ hxy ⟨f.injective h.1,
          f.injective (W.map_negY f .. ▸ h).2⟩).symm

/-- The base-change inclusion on secp256k1 points. -/
noncomputable def includePoint : BasePoint →+ BarPoint :=
  mapPoint secp256k1.toAffine (algebraMap Fp FpBar)

@[simp]
theorem includePoint_zero : includePoint (0 : BasePoint) = 0 := rfl

@[simp]
theorem includePoint_some {x y : Fp}
    (h : secp256k1.toAffine.Nonsingular x y) :
    includePoint (Point.some x y h) =
      Point.some (algebraMap Fp FpBar x) (algebraMap Fp FpBar y)
        ((secp256k1.toAffine.map_nonsingular
          (algebraMap Fp FpBar).injective x y).mpr h) := rfl

/-- Arithmetic Frobenius is the `p`-th-power map on the chosen closure. -/
theorem frobeniusField_apply (z : FpBar) :
    frobeniusField z = z ^ Secp256k1.p := by
  change z ^ Fintype.card Fp = z ^ Secp256k1.p
  rw [ZMod.card]

/-- Frobenius fixes the embedded base field pointwise. -/
@[simp]
theorem frobeniusField_algebraMap (z : Fp) :
    frobeniusField (algebraMap Fp FpBar z) = algebraMap Fp FpBar z :=
  frobeniusField.commutes z

private theorem barCurve_curve_of_nonsingular
    (x y : FpBar) (h : BarCurve.Nonsingular x y) :
    y ^ 2 = x ^ 3 + 7 := by
  have he : BarCurve.Equation x y := h.1
  rw [WeierstrassCurve.Affine.equation_iff] at he
  simp only [BarCurve, WeierstrassCurve.baseChange, WeierstrassCurve.map,
    secp256k1, map_zero, map_ofNat] at he
  linear_combination he

private theorem barCurve_negY (x y : FpBar) :
    BarCurve.negY x y = -y := by
  simp [WeierstrassCurve.Affine.negY, BarCurve,
    WeierstrassCurve.baseChange, WeierstrassCurve.map, secp256k1]

private theorem frobeniusPoint_some_of_fixed
    {x y : FpBar} (h : BarCurve.Nonsingular x y)
    (hx : frobeniusField x = x) (hy : frobeniusField y = y) :
    frobeniusPoint (Point.some x y h) = Point.some x y h := by
  rw [frobeniusPoint, Point.map_some]
  simp only [Point.some.injEq]
  exact ⟨hx, hy⟩

private theorem frobeniusPoint_some_of_antifixed
    {x y : FpBar} (h : BarCurve.Nonsingular x y)
    (hx : frobeniusField x = x) (hy : frobeniusField y = -y) :
    frobeniusPoint (Point.some x y h) = -(Point.some x y h) := by
  rw [frobeniusPoint, Point.map_some, Point.neg_some]
  simp only [Point.some.injEq]
  exact ⟨hx, hy.trans (barCurve_negY x y).symm⟩

/-- `P` is an affine closure point whose `x`-coordinate is the canonical image of `x`. -/
def LiesOver (x : Fp) (P : BarPoint) : Prop :=
  ∃ (y : FpBar) (h : BarCurve.Nonsingular
      (algebraMap Fp FpBar x) y),
    P = Point.some (algebraMap Fp FpBar x) y h

/-- A point is `Fp²`-rational when the square of arithmetic Frobenius fixes it. -/
def IsFp2Point (P : BarPoint) : Prop :=
  frobeniusPoint (frobeniusPoint P) = P

/-- The additive subgroup of `Fp²`-rational points in the chosen algebraic closure. -/
noncomputable def fp2Points : AddSubgroup BarPoint where
  carrier := {P | IsFp2Point P}
  zero_mem' := by simp [IsFp2Point]
  add_mem' := by
    intro P Q hP hQ
    simp only [Set.mem_setOf_eq, IsFp2Point] at hP hQ ⊢
    simp [map_add, hP, hQ]
  neg_mem' := by
    intro P hP
    simp only [Set.mem_setOf_eq, IsFp2Point] at hP ⊢
    simp [hP]

/-- Base change on points is injective. -/
theorem includePoint_injective : Function.Injective includePoint := by
  rintro (_ | _) (_ | _) h
  any_goals contradiction
  · rfl
  · simpa only [includePoint, mapPoint, Point.some.injEq] using
      ⟨(algebraMap Fp FpBar).injective (Point.some.inj h).left,
        (algebraMap Fp FpBar).injective (Point.some.inj h).right⟩

/-- Arithmetic Frobenius fixes every explicitly base-changed point. -/
@[simp]
theorem frobeniusPoint_includePoint (P : BasePoint) :
    frobeniusPoint (includePoint P) = includePoint P := by
  rcases P with _ | ⟨x, y, h⟩
  · rfl
  · rw [includePoint_some]
    exact frobeniusPoint_some_of_fixed _ (by simp) (by simp)

/-- A point over a liftable base coordinate is not merely Frobenius-fixed:
it is the base change of an actual secp256k1 point over `Fp`. -/
theorem exists_includePoint_eq_of_liesOver_of_isLiftable
    {x : Fp} {P : BarPoint} (hP : LiesOver x P)
    (hx : Ecdlp.M16FactorBaseLiftable.IsLiftable x) :
    ∃ Q : BasePoint, includePoint Q = P := by
  rcases hP with ⟨y, hcurve, rfl⟩
  rw [Ecdlp.M16FactorBaseLiftable.IsLiftable,
    isSquare_iff_exists_sq] at hx
  rcases hx with ⟨r, hr⟩
  have hy2 : y ^ 2 = (algebraMap Fp FpBar r) ^ 2 := by
    calc
      y ^ 2 = (algebraMap Fp FpBar x) ^ 3 + 7 :=
        barCurve_curve_of_nonsingular _ _ hcurve
      _ = algebraMap Fp FpBar
          (Ecdlp.M16FactorBaseLiftable.rhs x) := by
        rw [Ecdlp.M16FactorBaseLiftable.rhs, map_add, map_pow]
        rw [map_ofNat]
      _ = algebraMap Fp FpBar (r ^ 2) := congrArg _ hr
      _ = (algebraMap Fp FpBar r) ^ 2 := by rw [map_pow]
  have hyr : ∃ r₀ : Fp, y = algebraMap Fp FpBar r₀ := by
    rcases eq_or_eq_neg_of_sq_eq_sq y (algebraMap Fp FpBar r) hy2 with hy | hy
    · exact ⟨r, hy⟩
    · exact ⟨-r, by simpa using hy⟩
  rcases hyr with ⟨r₀, hr₀⟩
  subst y
  have hbase : secp256k1.toAffine.Nonsingular x r₀ :=
    (secp256k1.toAffine.baseChange_nonsingular
      (Algebra.ofId Fp FpBar).injective x r₀).mp hcurve
  refine ⟨Point.some x r₀ hbase, ?_⟩
  rw [includePoint_some]
  rfl

/-- A liftable base coordinate makes every closure point above it Frobenius-fixed.
This includes the `rhs x = 0` edge case: then the sole square root is `0`. -/
theorem frobeniusPoint_eq_of_liesOver_of_isLiftable
    {x : Fp} {P : BarPoint} (hP : LiesOver x P)
    (hx : Ecdlp.M16FactorBaseLiftable.IsLiftable x) :
    frobeniusPoint P = P := by
  rcases exists_includePoint_eq_of_liesOver_of_isLiftable hP hx with ⟨Q, hQ⟩
  rw [← hQ]
  exact frobeniusPoint_includePoint Q

/-- A nonliftable base coordinate makes every closure point above it
Frobenius-antifixed.  The proof is Euler's criterion applied to the actual
square root, rather than a descent assertion about all closure fixed points. -/
theorem frobeniusPoint_eq_neg_of_liesOver_of_not_isLiftable
    {x : Fp} {P : BarPoint} (hP : LiesOver x P)
    (hx : ¬ Ecdlp.M16FactorBaseLiftable.IsLiftable x) :
    frobeniusPoint P = -P := by
  rcases hP with ⟨y, hcurve, rfl⟩
  let a : Fp := Ecdlp.M16FactorBaseLiftable.rhs x
  have ha : a ≠ 0 := by
    intro ha0
    apply hx
    simp [Ecdlp.M16FactorBaseLiftable.IsLiftable, a, ha0]
  have heuler_ne : a ^ (Secp256k1.p / 2) ≠ 1 := by
    intro heuler
    apply hx
    exact (ZMod.euler_criterion Secp256k1.p ha).mpr heuler
  have heuler : a ^ (Secp256k1.p / 2) = -1 :=
    (ZMod.pow_div_two_eq_neg_one_or_one Secp256k1.p ha).resolve_left heuler_ne
  have hp_ne_two : Secp256k1.p ≠ 2 := by
    norm_num [Secp256k1.p]
  have hp_odd : Odd Secp256k1.p :=
    (Fact.out : Nat.Prime Secp256k1.p).odd_of_ne_two hp_ne_two
  have hp_split : 2 * (Secp256k1.p / 2) + 1 = Secp256k1.p :=
    Nat.two_mul_div_two_add_one_of_odd hp_odd
  have hy2 : y ^ 2 = algebraMap Fp FpBar a := by
    calc
      y ^ 2 = (algebraMap Fp FpBar x) ^ 3 + 7 :=
        barCurve_curve_of_nonsingular _ _ hcurve
      _ = algebraMap Fp FpBar
          (Ecdlp.M16FactorBaseLiftable.rhs x) := by
        rw [Ecdlp.M16FactorBaseLiftable.rhs, map_add, map_pow]
        rw [map_ofNat]
      _ = algebraMap Fp FpBar a := rfl
  have hy_frob : frobeniusField y = -y := by
    calc
      frobeniusField y = y ^ Secp256k1.p := frobeniusField_apply y
      _ = y ^ (2 * (Secp256k1.p / 2) + 1) := by rw [hp_split]
      _ = (y ^ 2) ^ (Secp256k1.p / 2) * y := by
        rw [pow_add, pow_mul, pow_one]
      _ = algebraMap Fp FpBar (a ^ (Secp256k1.p / 2)) * y := by
        rw [hy2, map_pow]
      _ = -y := by rw [heuler]; simp
  exact frobeniusPoint_some_of_antifixed hcurve (by simp) hy_frob

/-- Every closure point above a base-field `x`-coordinate is `Fp²`-rational.
The liftable branch is fixed and the nonliftable branch is antifixed. -/
theorem isFp2Point_of_liesOver {x : Fp} {P : BarPoint}
    (hP : LiesOver x P) : IsFp2Point P := by
  by_cases hx : Ecdlp.M16FactorBaseLiftable.IsLiftable x
  · have hfix := frobeniusPoint_eq_of_liesOver_of_isLiftable hP hx
    simp [IsFp2Point, hfix]
  · have hanti :=
      frobeniusPoint_eq_neg_of_liesOver_of_not_isLiftable hP hx
    simp [IsFp2Point, hanti]

/-! ## Subtotals and the point-level split -/

/-- A finite sum of points which individually descend to `Fp` also descends
as one literal base-changed subtotal. -/
theorem exists_includePoint_eq_sum_of_pointwise_descent
    {I : Type*} (s : Finset I) (P : I → BarPoint)
    (hP : ∀ i ∈ s, ∃ Q : BasePoint, includePoint Q = P i) :
    ∃ Q : BasePoint, includePoint Q = ∑ i ∈ s, P i := by
  classical
  induction s using Finset.induction_on with
  | empty =>
      exact ⟨0, by simp⟩
  | @insert a s ha ih =>
      rcases hP a (Finset.mem_insert_self a s) with ⟨Qa, hQa⟩
      rcases ih (fun i hi ↦ hP i (Finset.mem_insert_of_mem hi)) with ⟨Qs, hQs⟩
      refine ⟨Qa + Qs, ?_⟩
      simp [ha, hQa, hQs]

/-- A finite subtotal of point witnesses above liftable coordinates is
literally in the range of `includePoint`.  This is the descent input needed
before any use of the base-field two-torsion theorem. -/
theorem exists_includePoint_eq_sum_of_liftable_liesOver
    {I : Type*} (s : Finset I) (x : I → Fp) (P : I → BarPoint)
    (hover : ∀ i ∈ s, LiesOver (x i) (P i))
    (hlift : ∀ i ∈ s,
      Ecdlp.M16FactorBaseLiftable.IsLiftable (x i)) :
    ∃ Q : BasePoint, includePoint Q = ∑ i ∈ s, P i := by
  apply exists_includePoint_eq_sum_of_pointwise_descent s P
  intro i hi
  exact exists_includePoint_eq_of_liesOver_of_isLiftable
    (hover i hi) (hlift i hi)

/-- A finite subtotal of point witnesses above nonliftable coordinates is
Frobenius-antifixed. -/
theorem frobeniusPoint_sum_eq_neg_of_nonliftable_liesOver
    {I : Type*} (s : Finset I) (x : I → Fp) (P : I → BarPoint)
    (hover : ∀ i ∈ s, LiesOver (x i) (P i))
    (hnon : ∀ i ∈ s,
      ¬ Ecdlp.M16FactorBaseLiftable.IsLiftable (x i)) :
    frobeniusPoint (∑ i ∈ s, P i) = -(∑ i ∈ s, P i) := by
  classical
  simp_rw [map_sum]
  calc
    ∑ i ∈ s, frobeniusPoint (P i) = ∑ i ∈ s, -P i := by
      apply Finset.sum_congr rfl
      intro i hi
      rw [frobeniusPoint_eq_neg_of_liesOver_of_not_isLiftable
        (hover i hi) (hnon i hi)]
    _ = -(∑ i ∈ s, P i) := by rw [Finset.sum_neg_distrib]

/-- Diagnostic split before eliminating two-torsion.  Conjugating a relation
whose three parts are respectively fixed, antifixed, and fixed shows that the
antifixed subtotal and the fixed subtotal agree and are both killed by `2`.
No assertion about closure-field two-torsion is made here. -/
theorem frobenius_split_before_two_torsion
    {S N T : BarPoint}
    (hS : frobeniusPoint S = S)
    (hN : frobeniusPoint N = -N)
    (hT : frobeniusPoint T = T)
    (hsum : S + N + T = 0) :
    S + (-N) + T = 0 ∧
      (2 : ℕ) • N = 0 ∧
      (2 : ℕ) • (S + T) = 0 ∧
      S + T = N := by
  have hconj : S + (-N) + T = 0 := by
    have h := congrArg frobeniusPoint hsum
    simpa only [map_add, map_zero, hS, hN, hT] using h
  have hplus : (S + T) + N = 0 := by
    calc
      (S + T) + N = S + N + T := by abel
      _ = 0 := hsum
  have hminus : (S + T) + (-N) = 0 := by
    calc
      (S + T) + (-N) = S + (-N) + T := by abel
      _ = 0 := hconj
  have hfixed_eq_neg : S + T = -N :=
    (add_eq_zero_iff_eq_neg).mp hplus
  have hfixed_eq : S + T = N := by
    have h := (add_eq_zero_iff_eq_neg).mp hminus
    simpa using h
  have hself : N = -N := hfixed_eq.symm.trans hfixed_eq_neg
  have htwoN : (2 : ℕ) • N = 0 := by
    rw [two_nsmul, add_eq_zero_iff_eq_neg]
    exact hself
  have htwoFixed : (2 : ℕ) • (S + T) = 0 := by
    calc
      (2 : ℕ) • (S + T) = (2 : ℕ) • N := congrArg _ hfixed_eq
      _ = 0 := htwoN
  exact ⟨hconj, htwoN, htwoFixed, hfixed_eq⟩

/-- Final base/antifixed split.  Here `C` is the descended liftable subtotal and
`T` is an arbitrary base-field correction (in particular either sign of a
target point).  The fixed subtotal is pulled back through the injective point
inclusion before `secp256k1_no_nonzero_two_torsion` is invoked. -/
theorem frobenius_split_of_base_subtotal
    (C T : BasePoint) (N : BarPoint)
    (hN : frobeniusPoint N = -N)
    (hsum : includePoint C + N + includePoint T = 0) :
    includePoint C + includePoint T = 0 ∧ N = 0 := by
  rcases frobenius_split_before_two_torsion
      (frobeniusPoint_includePoint C) hN
      (frobeniusPoint_includePoint T) hsum with
    ⟨_, _, htwoFixed, hfixed_eq⟩
  have hmap : includePoint C + includePoint T = includePoint (C + T) := by
    exact (map_add includePoint C T).symm
  rw [hmap] at htwoFixed
  have htwoBase : (2 : ℕ) • (C + T) = 0 := by
    apply includePoint_injective
    simpa only [map_nsmul, map_zero] using htwoFixed
  have hbase : C + T = 0 :=
    Ecdlp.Curve.secp256k1_no_nonzero_two_torsion (C + T) htwoBase
  have hfixed_zero : includePoint C + includePoint T = 0 := by
    rw [hmap, hbase, map_zero]
  exact ⟨hfixed_zero, hfixed_eq.symm.trans hfixed_zero⟩

/-- Signed-target wrapper.  Taking `τ = 1` or `τ = -1` records the two
possible target signs while retaining an arbitrary descended liftable
subtotal `C`. -/
theorem frobenius_split_with_signed_target
    (C R : BasePoint) (N : BarPoint) (τ : ℤ)
    (hN : frobeniusPoint N = -N)
    (hsum : includePoint C + N + τ • includePoint R = 0) :
    includePoint C + τ • includePoint R = 0 ∧ N = 0 := by
  simpa only [map_zsmul] using
    frobenius_split_of_base_subtotal C (τ • R) N hN (by
      simpa only [map_zsmul] using hsum)

/-- End-to-end conditional point-witness split for two finite indexed families.
It assumes the point relation itself and never manufactures point witnesses
from polynomial roots.  The liftable subtotal descends to `C`; the
nonliftable subtotal vanishes; and the remaining base relation holds. -/
theorem split_partitioned_point_witnesses
    {IL IN : Type*}
    (sL : Finset IL) (sN : Finset IN)
    (xL : IL → Fp) (xN : IN → Fp)
    (PL : IL → BarPoint) (PN : IN → BarPoint)
    (T : BasePoint)
    (hoverL : ∀ i ∈ sL, LiesOver (xL i) (PL i))
    (hlift : ∀ i ∈ sL,
      Ecdlp.M16FactorBaseLiftable.IsLiftable (xL i))
    (hoverN : ∀ i ∈ sN, LiesOver (xN i) (PN i))
    (hnon : ∀ i ∈ sN,
      ¬ Ecdlp.M16FactorBaseLiftable.IsLiftable (xN i))
    (hsum : (∑ i ∈ sL, PL i) + (∑ i ∈ sN, PN i) +
      includePoint T = 0) :
    ∃ C : BasePoint,
      includePoint C = ∑ i ∈ sL, PL i ∧
      includePoint C + includePoint T = 0 ∧
      (∑ i ∈ sN, PN i) = 0 := by
  classical
  rcases exists_includePoint_eq_sum_of_liftable_liesOver
      sL xL PL hoverL hlift with ⟨C, hC⟩
  have hanti := frobeniusPoint_sum_eq_neg_of_nonliftable_liesOver
    sN xN PN hoverN hnon
  have hsum' : includePoint C + (∑ i ∈ sN, PN i) +
      includePoint T = 0 := by
    rw [hC]
    exact hsum
  rcases frobenius_split_of_base_subtotal C T
      (∑ i ∈ sN, PN i) hanti hsum' with ⟨hbase, hzero⟩
  exact ⟨C, hC, hbase, hzero⟩

end

end Ecdlp.M16FrobeniusPointSplit
