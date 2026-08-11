import Ecdlp.Proved.FrozenProjectiveSecpChainSemantics
import Ecdlp.Proved.M16DirectSystemRootBridge
import Ecdlp.Proved.M16FrobeniusPointSplit

/-!
# Exact point semantics of the direct M16 root equation

This file composes the complete projective chart cover with the recursively
iterated secp256k1 Kummer fiber over the algebraic closure.  It proves that a
root of the source-field `S17At` equation is exactly a choice of sixteen
closure points above the prescribed source coordinates whose sum lies above
the prescribed target coordinate.

All internal affine and infinity charts remain present through the existing
`FrozenChartPolynomialCover ↔ FrozenChartCover` theorem.  No point witness is
claimed to descend to the base field, and no uniqueness, factor-base,
recovery, solver, rank, yield, cost, or discrete-log claim is made.
-/

namespace Ecdlp.M16DirectPointSemantics

open scoped BigOperators

open WeierstrassCurve.Affine
open Ecdlp.Curve
open Ecdlp.FrozenProjectiveSemaev
open Ecdlp.FrozenProjectiveSecpLocalFiber
open Ecdlp.FrozenProjectiveSecpChainSemantics
open Ecdlp.M16DirectSystemRootBridge
open Ecdlp.M16FrobeniusPointSplit
open Ecdlp.SemaevLeftFoldAffine

noncomputable section

abbrev Fp := ZMod Secp256k1.p
abbrev FpBar := AlgebraicClosure Fp
abbrev BarCurve := secp256k1 ⁄ FpBar
abbrev BarPoint := BarCurve.Point

local instance : DecidableEq FpBar := Classical.decEq _

private instance barCurve_isElliptic : BarCurve.IsElliptic :=
  inferInstanceAs
    ((secp256k1.map (algebraMap Fp FpBar)).IsElliptic)

private theorem projectivePair_eq_of_u_v_eq
    {A B : ProjectivePair FpBar}
    (hu : A.u = B.u) (hv : A.v = B.v) : A = B := by
  rcases A with ⟨au, av, ha⟩
  rcases B with ⟨bu, bv, hb⟩
  simp only at hu hv
  subst bu
  subst bv
  rfl

private theorem barCurve_equation_of_sq
    {x y : FpBar} (h : y ^ 2 = x ^ 3 + 7) :
    BarCurve.Equation x y := by
  rw [WeierstrassCurve.Affine.equation_iff]
  simp only [BarCurve, WeierstrassCurve.baseChange, WeierstrassCurve.map,
    secp256k1, map_zero, map_ofNat]
  linear_combination h

/-- Every source-field coordinate has an affine secp256k1 point above it in
the chosen algebraic closure. -/
theorem exists_liesOver (x : Fp) :
    ∃ P : BarPoint, LiesOver x P := by
  let xb : FpBar := algebraMap Fp FpBar x
  obtain ⟨y, hy⟩ := IsAlgClosed.exists_eq_mul_self (xb ^ 3 + 7)
  have hy' : y ^ 2 = xb ^ 3 + 7 := by
    simpa [pow_two] using hy.symm
  have hcurve : BarCurve.Nonsingular xb y :=
    BarCurve.equation_iff_nonsingular.mp (barCurve_equation_of_sq hy')
  exact ⟨Point.some xb y hcurve, y, hcurve, rfl⟩

/-- A fixed, noncomputable affine closure point above a source-field
coordinate.  It is used only to choose witnesses; no descent or preferred
square-root property is attached to this choice. -/
noncomputable def closureLift (x : Fp) : BarPoint :=
  Classical.choose (exists_liesOver x)

theorem liesOver_closureLift (x : Fp) :
    LiesOver x (closureLift x) :=
  Classical.choose_spec (exists_liesOver x)

/-- `LiesOver` is exactly equality with the canonical affine Kummer
coordinate. -/
theorem liesOver_iff_barKummer_eq (x : Fp) (P : BarPoint) :
    LiesOver x P ↔
      barKummer P = ProjectivePair.affine (algebraMap Fp FpBar x) := by
  constructor
  · rintro ⟨y, hcurve, rfl⟩
    rfl
  · rcases P with _ | ⟨px, py, hcurve⟩
    · intro h
      have hv := congrArg ProjectivePair.v h
      exact (zero_ne_one hv).elim
    · intro h
      have hx := congrArg ProjectivePair.u h
      change px = algebraMap Fp FpBar x at hx
      subst px
      exact ⟨py, hcurve, rfl⟩

/-- Negating a point does not change the source-field coordinate above which
it lies. -/
@[simp] theorem liesOver_neg_iff (x : Fp) (P : BarPoint) :
    LiesOver x (-P) ↔ LiesOver x P := by
  rw [liesOver_iff_barKummer_eq, liesOver_iff_barKummer_eq,
    barKummer_neg]

private theorem mapProjectivePair_affine
    (x : Fp) :
    mapProjectivePair (algebraMap Fp FpBar)
        (algebraMap Fp FpBar).injective (ProjectivePair.affine x) =
      ProjectivePair.affine (algebraMap Fp FpBar x) := by
  apply projectivePair_eq_of_u_v_eq <;>
    simp [mapProjectivePair, ProjectivePair.affine]

private theorem mapped_projectiveLeaves_eq_barKummer
    (x : Fin 16 → Fp) (seed : ℕ → BarPoint)
    (hseed : ∀ i, LiesOver (externalValue x i) (seed i)) :
    (fun i =>
        mapProjectivePair (algebraMap Fp FpBar)
          (algebraMap Fp FpBar).injective (projectiveLeaves x i)) =
      fun i => barKummer (seed i) := by
  funext i
  rw [projectiveLeaves, mapProjectivePair_affine]
  exact (liesOver_iff_barKummer_eq (externalValue x i) (seed i)).mp
    (hseed i) |>.symm

/-! ## Exact direct-root point semantics -/

/-- The direct target-specialized `S17At` equation vanishes exactly when the
sixteen prescribed source coordinates can be lifted to closure points whose
finite sum has the prescribed target coordinate.

The reverse direction uses the complete chart cover, so intermediate
identity sums and every associated infinity chart are retained. -/
theorem S17At_eq_zero_iff_exists_point_sum_liesOver
    (x : Fin 16 → Fp) (X : Fp) :
    S17At x X = 0 ↔
      ∃ P : Fin 16 → BarPoint,
        (∀ i, LiesOver (x i) (P i)) ∧
        LiesOver X (∑ i, P i) := by
  constructor
  · intro hroot
    let seed : ℕ → BarPoint :=
      fun i => closureLift (externalValue x i)
    have hseed : ∀ i, LiesOver (externalValue x i) (seed i) := by
      intro i
      exact liesOver_closureLift (externalValue x i)
    have hpoly :=
      (S17At_eq_zero_iff_chartPolynomialCover_over
        (algebraMap Fp FpBar) (algebraMap Fp FpBar).injective x X).mp hroot
    have hchartMapped :=
      (frozenChartPolynomialCover_iff_chartCover _ _).mp hpoly
    have hleaves := mapped_projectiveLeaves_eq_barKummer x seed hseed
    have htarget := mapProjectivePair_affine X
    rw [hleaves, htarget] at hchartMapped
    rcases
        (frozenChartCover_barKummer_iff_signedPrefixSum seed
          (ProjectivePair.affine (algebraMap Fp FpBar X))).mp
          hchartMapped with
      ⟨lift, hsigned, hend⟩
    let P : Fin 16 → BarPoint := fun i => lift i
    refine ⟨P, ?_, ?_⟩
    · intro i
      have hbase : LiesOver (x i) (seed i) := by
        simpa [seed, externalValue, i.isLt] using hseed i
      rcases hsigned i i.isLt with hpos | hneg
      · simpa [P, hpos] using hbase
      · have hbaseNeg : LiesOver (x i) (-seed i) :=
          (liesOver_neg_iff (x i) (seed i)).mpr hbase
        simpa [P, hneg] using hbaseNeg
    · apply (liesOver_iff_barKummer_eq X (∑ i, P i)).mpr
      rw [Fin.sum_univ_eq_sum_range]
      simpa [P, signedPrefixSum, normalizeProjectivePair,
        ProjectivePair.affine] using hend.symm
  · rintro ⟨P, hP, hsum⟩
    let seed : ℕ → BarPoint := fun i =>
      if hi : i < 16 then P ⟨i, hi⟩ else closureLift 0
    have hseed : ∀ i, LiesOver (externalValue x i) (seed i) := by
      intro i
      by_cases hi : i < 16
      · simpa [seed, externalValue, hi] using hP ⟨i, hi⟩
      · simpa [seed, externalValue, hi] using liesOver_closureLift (0 : Fp)
    have hsumSeed :
        signedPrefixSum seed 16 = ∑ i, P i := by
      rw [signedPrefixSum]
      calc
        ∑ i ∈ Finset.range 16, seed i =
            ∑ i : Fin 16, seed i :=
          (Fin.sum_univ_eq_sum_range seed 16).symm
        _ = ∑ i, P i := by
          apply Finset.sum_congr rfl
          intro i _
          simp [seed, i.isLt]
    have hchain :
        FrozenChartCover (fun i => barKummer (seed i))
          (ProjectivePair.affine (algebraMap Fp FpBar X)) := by
      apply
        (frozenChartCover_barKummer_iff_signedPrefixSum seed
          (ProjectivePair.affine (algebraMap Fp FpBar X))).mpr
      refine ⟨seed, ?_, ?_⟩
      · intro i hi
        exact Or.inl rfl
      · have hk := (liesOver_iff_barKummer_eq X (∑ i, P i)).mp hsum
        simpa [hsumSeed, normalizeProjectivePair,
          ProjectivePair.affine] using hk.symm
    have hleaves := mapped_projectiveLeaves_eq_barKummer x seed hseed
    have htarget := mapProjectivePair_affine X
    have hchartMapped :
        FrozenChartCover
          (fun i =>
            mapProjectivePair (algebraMap Fp FpBar)
              (algebraMap Fp FpBar).injective (projectiveLeaves x i))
          (mapProjectivePair (algebraMap Fp FpBar)
            (algebraMap Fp FpBar).injective (ProjectivePair.affine X)) := by
      rw [hleaves, htarget]
      exact hchain
    have hpoly :=
      (frozenChartPolynomialCover_iff_chartCover _ _).mpr hchartMapped
    exact
      (S17At_eq_zero_iff_chartPolynomialCover_over
        (algebraMap Fp FpBar) (algebraMap Fp FpBar).injective x X).mpr hpoly

/-- Relative to any supplied closure point above the target coordinate, a
root is exactly a family of source lifts whose sum is that target point or
its inverse.  This is the precise sign ambiguity of an `x`-coordinate
target; neither branch is privileged. -/
theorem S17At_eq_zero_iff_exists_point_sum_eq_target_or_neg
    (x : Fin 16 → Fp) (X : Fp) (T : BarPoint)
    (hT : LiesOver X T) :
    S17At x X = 0 ↔
      ∃ P : Fin 16 → BarPoint,
        (∀ i, LiesOver (x i) (P i)) ∧
        ((∑ i, P i) = T ∨ (∑ i, P i) = -T) := by
  rw [S17At_eq_zero_iff_exists_point_sum_liesOver]
  constructor
  · rintro ⟨P, hP, hsum⟩
    refine ⟨P, hP, ?_⟩
    apply (barKummer_eq_iff (∑ i, P i) T).mp
    exact
      ((liesOver_iff_barKummer_eq X (∑ i, P i)).mp hsum).trans
        ((liesOver_iff_barKummer_eq X T).mp hT).symm
  · rintro ⟨P, hP, hsum | hsum⟩
    · exact ⟨P, hP, hsum ▸ hT⟩
    · refine ⟨P, hP, ?_⟩
      rw [hsum]
      exact (liesOver_neg_iff X T).mpr hT

/-- A fixed zero-sum spelling for a supplied target lift.  In the branch
where the subtotal initially equals `T`, all sixteen source witnesses are
negated simultaneously; `LiesOver` is unchanged and their subtotal becomes
`-T`. -/
theorem S17At_eq_zero_iff_exists_point_sum_add_target_eq_zero
    (x : Fin 16 → Fp) (X : Fp) (T : BarPoint)
    (hT : LiesOver X T) :
    S17At x X = 0 ↔
      ∃ P : Fin 16 → BarPoint,
        (∀ i, LiesOver (x i) (P i)) ∧
        (∑ i, P i) + T = 0 := by
  rw [S17At_eq_zero_iff_exists_point_sum_eq_target_or_neg x X T hT]
  constructor
  · rintro ⟨P, hP, hsum | hsum⟩
    · refine ⟨fun i => -P i, ?_, ?_⟩
      · intro i
        exact (liesOver_neg_iff (x i) (P i)).mpr (hP i)
      · rw [Finset.sum_neg_distrib, hsum]
        exact neg_add_cancel T
    · exact ⟨P, hP, (add_eq_zero_iff_eq_neg).mpr hsum⟩
  · rintro ⟨P, hP, hzero⟩
    exact ⟨P, hP, Or.inr ((add_eq_zero_iff_eq_neg).mp hzero)⟩

/-- Equivalent zero-sum spelling with a separately named point above the
target coordinate.  The target point is necessarily the inverse of the
sixteen-point subtotal; no sign of a target lift is privileged. -/
theorem S17At_eq_zero_iff_exists_point_relation
    (x : Fin 16 → Fp) (X : Fp) :
    S17At x X = 0 ↔
      ∃ (P : Fin 16 → BarPoint) (T : BarPoint),
        (∀ i, LiesOver (x i) (P i)) ∧
        LiesOver X T ∧
        (∑ i, P i) + T = 0 := by
  rw [S17At_eq_zero_iff_exists_point_sum_liesOver]
  constructor
  · rintro ⟨P, hP, hsum⟩
    refine ⟨P, -(∑ i, P i), hP, ?_, add_neg_cancel _⟩
    exact (liesOver_neg_iff X (∑ i, P i)).mpr hsum
  · rintro ⟨P, T, hP, hT, hzero⟩
    refine ⟨P, hP, ?_⟩
    rw [(add_eq_zero_iff_eq_neg).mp hzero]
    exact (liesOver_neg_iff X T).mpr hT

end

end Ecdlp.M16DirectPointSemantics
