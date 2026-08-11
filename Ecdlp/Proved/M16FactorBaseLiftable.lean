import Mathlib
import Mathlib.NumberTheory.LegendreSymbol.Basic
import Ecdlp.Proved.CurveCardinalityExact
import Ecdlp.Proved.M16FactorBaseLiftableCountCertificate
import Ecdlp.Proved.Secp256k1Params
import Ecdlp.Proved.SevenNonResidue

/-!
# Exact liftable M16 factor-base census for secp256k1

The M16 coordinate factor base is the subgroup cut out by
`x ^ 564522 = 1` in the secp256k1 base field.  This file separates the
coordinate count from the curve-lift count and proves the exact census:

* `564522` subgroup coordinates in total (reused from
  `M16FactorBaseFinite.lean`);
* `188174` free three-element coordinate orbits for the GLV action;
* `94509` liftable and `93665` nonliftable GLV orbit representatives;
* `283527` liftable and `280995` nonliftable coordinates;
* `567054` signed affine factor-base points;
* quadratic-character sum `2532` over the coordinate factor base.

The finite computation follows the checked desk artifact
`experiments/engine/pkc_smooth_m16_regime_assurance_desk/artifact.json`.
It uses the artifact's exact-order generator and enumerates one representative
from each three-element GLV orbit.  A constant-stack tail-recursive accumulator
certifies all `188174` representatives in one isolated native leaf; a second
isolated native leaf certifies the generator.  This facade contains no native
command and derives the public counts by ordinary kernel proofs.

This is a finite-field and affine-point census only.  It proves no relation
yield, rank, solver, recovery, cost, or ECDLP shortcut.
-/

namespace Ecdlp.M16FactorBaseLiftable

open scoped Count
open Ecdlp.M16FactorBaseFinite
open WeierstrassCurve.Affine
open Certificates

/-! ## No zero right-hand side and the Euler liftability test -/

/-- No base-field coordinate has `x³ + 7 = 0`: that equation would make `-7`
a cube, contradicting the already-certified cubic-residue witness. -/
theorem secp256k1_rhs_ne_zero (x : Fp) : rhs x ≠ 0 := by
  intro hzero
  have hx3 : x ^ 3 = -7 := by
    dsimp only [rhs] at hzero
    linear_combination hzero
  have hxne : x ≠ 0 := by
    intro hx0
    rw [hx0] at hx3
    exact Ecdlp.Curve.secp256k1_seven_ne_zero (by linear_combination hx3)
  have h3dvd : 3 ∣ Secp256k1.p - 1 :=
    Nat.dvd_of_mod_eq_zero Ecdlp.Curve.three_dvd_p_sub_one
  have hexp : 3 * ((Secp256k1.p - 1) / 3) = Secp256k1.p - 1 :=
    Nat.mul_div_cancel' h3dvd
  have hpow :
      (-7 : Fp) ^ ((Secp256k1.p - 1) / 3) = 1 := by
    rw [← hx3, ← pow_mul, hexp]
    exact ZMod.pow_card_sub_one_eq_one hxne
  exact Ecdlp.Curve.secp256k1_neg7_pow_ne_one hpow

/-- On secp256k1, liftability is exactly the nonzero Euler-criterion test. -/
theorem isLiftable_iff_eulerCriterion (x : Fp) :
    IsLiftable x ↔ rhs x ^ (Secp256k1.p / 2) = 1 := by
  exact ZMod.euler_criterion Secp256k1.p (secp256k1_rhs_ne_zero x)

/-! ## Exact-order generator and factor-base enumeration -/

private theorem prime_dvd_factorBaseDegree {q : ℕ} (hq : q.Prime)
    (hqd : q ∣ 564522) : q = 2 ∨ q = 3 ∨ q = 7 ∨ q = 13441 := by
  change q ∣ 2 * (3 * (7 * 13441)) at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h2 | hrest
  · rcases (Nat.dvd_prime (by norm_num : Nat.Prime 2)).mp h2 with hq1 | hq2
    · exact absurd hq1 hq.ne_one
    · exact Or.inl hq2
  · rcases (Nat.Prime.dvd_mul hq).mp hrest with h3 | hrest
    · rcases (Nat.dvd_prime (by norm_num : Nat.Prime 3)).mp h3 with hq1 | hq3
      · exact absurd hq1 hq.ne_one
      · exact Or.inr (Or.inl hq3)
    · rcases (Nat.Prime.dvd_mul hq).mp hrest with h7 | h13441
      · rcases (Nat.dvd_prime (by norm_num : Nat.Prime 7)).mp h7 with hq1 | hq7
        · exact absurd hq1 hq.ne_one
        · exact Or.inr (Or.inr (Or.inl hq7))
      · rcases (Nat.dvd_prime (by norm_num : Nat.Prime 13441)).mp h13441 with hq1 | hq13441
        · exact absurd hq1 hq.ne_one
        · exact Or.inr (Or.inr (Or.inr hq13441))

/-- The artifact generator has exact multiplicative order `564522`. -/
theorem factorBaseGenerator_order : orderOf factorBaseGenerator = 564522 := by
  apply orderOf_eq_of_pow_and_pow_div_prime (by norm_num)
  · exact factorBaseGenerator_certificate.1
  · intro q hq hqd
    rcases prime_dvd_factorBaseDegree hq hqd with rfl | rfl | rfl | rfl
    · simpa using factorBaseGenerator_certificate.2.1
    · simpa using factorBaseGenerator_certificate.2.2.1
    · simpa using factorBaseGenerator_certificate.2.2.2.1
    · simpa using factorBaseGenerator_certificate.2.2.2.2.1

/-- The first order-three power of the census generator is `β²`. -/
theorem factorBaseGenerator_glv_square :
    factorBaseGenerator ^ factorBaseOrbitCount =
      (Secp256k1.beta : Fp) ^ 2 := by
  exact factorBaseGenerator_certificate.2.2.2.2.2.1

/-- The second order-three power of the census generator is `β`. -/
theorem factorBaseGenerator_glv :
    factorBaseGenerator ^ (2 * factorBaseOrbitCount) =
      (Secp256k1.beta : Fp) := by
  exact factorBaseGenerator_certificate.2.2.2.2.2.2

private def enumerateFactorBase (i : Fin 564522) : FactorBaseX :=
  ⟨factorBaseGenerator ^ (i : ℕ), by
    change (factorBaseGenerator ^ (i : ℕ)) ^ 564522 = 1
    rw [← pow_mul, Nat.mul_comm, pow_mul,
      factorBaseGenerator_certificate.1, one_pow]⟩

private theorem enumerateFactorBase_injective :
    Function.Injective enumerateFactorBase := by
  intro i j hij
  apply Fin.ext
  have hpow : factorBaseGenerator ^ (i : ℕ) =
      factorBaseGenerator ^ (j : ℕ) := congrArg Subtype.val hij
  have hfinite : IsOfFinOrder factorBaseGenerator :=
    orderOf_pos_iff.mp (by rw [factorBaseGenerator_order]; norm_num)
  have hmod := hfinite.pow_inj_mod.mp hpow
  rw [factorBaseGenerator_order] at hmod
  simpa [Nat.mod_eq_of_lt i.isLt, Nat.mod_eq_of_lt j.isLt] using hmod

private theorem enumerateFactorBase_bijective :
    Function.Bijective enumerateFactorBase := by
  apply (Fintype.bijective_iff_injective_and_card enumerateFactorBase).2
  refine ⟨enumerateFactorBase_injective, ?_⟩
  simpa using card_factorBaseX.symm

private noncomputable def indexEquivFactorBase :
    Fin 564522 ≃ FactorBaseX :=
  Equiv.ofBijective enumerateFactorBase enumerateFactorBase_bijective

private def glvOrbitFinEquiv :
    Fin 3 × Fin factorBaseOrbitCount ≃ Fin 564522 :=
  finProdFinEquiv.trans <| finCongr (by norm_num [factorBaseOrbitCount])

private noncomputable def glvOrbitIndexEquiv :
    Fin 3 × Fin factorBaseOrbitCount ≃ FactorBaseX :=
  glvOrbitFinEquiv.trans indexEquivFactorBase

/-- The factor-base coordinate in layer `j` of the orbit represented by `i`.
Layer `0` is the representative, layer `1` is its `β²` image, and layer `2`
is its `β` image. -/
noncomputable def glvOrbitLayer (j : Fin 3) (i : GLVOrbitRep) : FactorBaseX :=
  glvOrbitIndexEquiv (j, i)

/-- The chosen coordinate representative of a GLV orbit. -/
noncomputable def orbitRepresentative (i : GLVOrbitRep) : FactorBaseX :=
  glvOrbitLayer 0 i

private theorem glvOrbitLayer_val (j : Fin 3) (i : GLVOrbitRep) :
    (glvOrbitLayer j i).1 =
      factorBaseGenerator ^ ((i : ℕ) + factorBaseOrbitCount * (j : ℕ)) := by
  rfl

private theorem orbitRepresentative_val (i : GLVOrbitRep) :
    (orbitRepresentative i).1 = factorBaseGenerator ^ (i : ℕ) := by
  rw [orbitRepresentative, glvOrbitLayer_val]
  simp

/-- Layer one is the `β²` image of the chosen representative. -/
theorem glvOrbitLayer_one (i : GLVOrbitRep) :
    (glvOrbitLayer 1 i).1 =
      (Secp256k1.beta : Fp) ^ 2 * (orbitRepresentative i).1 := by
  rw [glvOrbitLayer_val, orbitRepresentative_val]
  simp only [Fin.val_one]
  rw [mul_one, pow_add, factorBaseGenerator_glv_square, mul_comm]

/-- Layer two is the `β` image of the chosen representative. -/
theorem glvOrbitLayer_two (i : GLVOrbitRep) :
    (glvOrbitLayer 2 i).1 =
      (Secp256k1.beta : Fp) * (orbitRepresentative i).1 := by
  rw [glvOrbitLayer_val, orbitRepresentative_val]
  change factorBaseGenerator ^ ((i : ℕ) + factorBaseOrbitCount * 2) =
    (Secp256k1.beta : Fp) * factorBaseGenerator ^ (i : ℕ)
  rw [Nat.mul_comm factorBaseOrbitCount 2, pow_add,
    factorBaseGenerator_glv, mul_comm]

/-- The three coordinates in every enumerated GLV orbit are distinct. -/
theorem glvOrbitLayer_injective (i : GLVOrbitRep) :
    Function.Injective (fun j : Fin 3 ↦ glvOrbitLayer j i) := by
  intro j k hjk
  have hpairs : (j, i) = (k, i) := glvOrbitIndexEquiv.injective hjk
  exact congrArg Prod.fst hpairs

private theorem beta_cube : (Secp256k1.beta : Fp) ^ 3 = 1 := by
  have hbeta : (Secp256k1.beta : Fp) ^ 2 +
      (Secp256k1.beta : Fp) + 1 = 0 := by
    have h0 : ((Secp256k1.beta ^ 2 + Secp256k1.beta + 1 : ℕ) : Fp) = 0 := by
      rw [ZMod.natCast_eq_zero_iff]
      exact Nat.dvd_of_mod_eq_zero Secp256k1.beta_field_eigenvalue
    push_cast at h0
    linear_combination h0
  linear_combination ((Secp256k1.beta : Fp) - 1) * hbeta

private theorem rhs_beta_mul (x : Fp) :
    rhs ((Secp256k1.beta : Fp) * x) = rhs x := by
  simp only [rhs, mul_pow, beta_cube, one_mul]

private theorem isLiftable_beta_mul (x : Fp) :
    IsLiftable ((Secp256k1.beta : Fp) * x) ↔ IsLiftable x := by
  simp only [IsLiftable, rhs_beta_mul]

private theorem glvOrbitLayer_isLiftable (j : Fin 3) (i : GLVOrbitRep) :
    IsLiftable (glvOrbitLayer j i).1 ↔
      IsLiftable (orbitRepresentative i).1 := by
  by_cases hzero : j = 0
  · subst j
    rfl
  by_cases hone : j = 1
  · subst j
    rw [glvOrbitLayer_one]
    simpa only [pow_two, mul_assoc] using
      (isLiftable_beta_mul ((Secp256k1.beta : Fp) * (orbitRepresentative i).1)).trans
        (isLiftable_beta_mul (orbitRepresentative i).1)
  have htwo : j = 2 := by
    apply Fin.ext
    omega
  subst j
  rw [glvOrbitLayer_two]
  exact isLiftable_beta_mul (orbitRepresentative i).1

/-! ## Resource-bounded orbit-representative census -/

/-- Liftable representatives for the explicit free GLV coordinate orbits. -/
abbrev LiftableGLVOrbitRep :=
  {i : GLVOrbitRep // IsLiftable (orbitRepresentative i).1}

/-- Nonliftable representatives for the explicit free GLV coordinate orbits. -/
abbrev NonliftableGLVOrbitRep :=
  {i : GLVOrbitRep // ¬ IsLiftable (orbitRepresentative i).1}

noncomputable instance : Fintype LiftableGLVOrbitRep :=
  Fintype.ofFinite LiftableGLVOrbitRep

noncomputable instance : Fintype NonliftableGLVOrbitRep :=
  Fintype.ofFinite NonliftableGLVOrbitRep

private noncomputable def liftableRepEquivCountSet :
    LiftableGLVOrbitRep ≃
      {k : ℕ // k < factorBaseOrbitCount ∧
        representativeEulerPositive k = true} where
  toFun i :=
    ⟨i.1.1, i.1.isLt, by
      simpa only [representativeEulerPositive, decide_eq_true_eq,
        orbitRepresentative_val] using
        (isLiftable_iff_eulerCriterion _).mp i.2⟩
  invFun k :=
    ⟨⟨k.1, k.2.1⟩, by
      apply (isLiftable_iff_eulerCriterion _).mpr
      simpa only [representativeEulerPositive, decide_eq_true_eq,
        orbitRepresentative_val] using k.2.2⟩
  left_inv i := by
    apply Subtype.ext
    rfl
  right_inv k := by
    apply Subtype.ext
    rfl

/-- There are exactly `188174` three-element coordinate GLV orbits. -/
theorem card_glvOrbitRep : Fintype.card GLVOrbitRep = 188174 := by
  change Fintype.card (Fin factorBaseOrbitCount) = 188174
  rw [Fintype.card_fin]
  rfl

/-- Exactly `94509` GLV coordinate orbits lift to affine points. -/
theorem card_liftableGLVOrbitRep :
    Fintype.card LiftableGLVOrbitRep = 94509 := by
  calc
    Fintype.card LiftableGLVOrbitRep =
        Fintype.card
          {k : ℕ // k < factorBaseOrbitCount ∧
            representativeEulerPositive k = true} :=
      Fintype.card_congr liftableRepEquivCountSet
    _ = Nat.count (fun k ↦ representativeEulerPositive k = true)
        factorBaseOrbitCount :=
      (Nat.count_eq_card_fintype
        (fun k ↦ representativeEulerPositive k = true)
        factorBaseOrbitCount).symm
    _ = 94509 := representativeEulerPositive_count

/-- Exactly `93665` GLV coordinate orbits do not lift. -/
theorem card_nonliftableGLVOrbitRep :
    Fintype.card NonliftableGLVOrbitRep = 93665 := by
  rw [Fintype.card_subtype_compl, card_glvOrbitRep,
    card_liftableGLVOrbitRep]

private noncomputable def layerLiftableEquiv :
    Fin 3 × LiftableGLVOrbitRep ≃
      {z : Fin 3 × GLVOrbitRep //
        IsLiftable (glvOrbitLayer z.1 z.2).1} where
  toFun z := ⟨(z.1, z.2.1), (glvOrbitLayer_isLiftable z.1 z.2.1).mpr z.2.2⟩
  invFun z :=
    (z.1.1, ⟨z.1.2, (glvOrbitLayer_isLiftable z.1.1 z.1.2).mp z.2⟩)
  left_inv z := by
    rfl
  right_inv z := by
    apply Subtype.ext
    rfl

private noncomputable def indexedLiftableEquiv :
    {z : Fin 3 × GLVOrbitRep //
      IsLiftable (glvOrbitLayer z.1 z.2).1} ≃ LiftableFactorBaseX :=
  glvOrbitIndexEquiv.subtypeEquiv (fun _ ↦ Iff.rfl)

private noncomputable def liftableOrbitEquiv :
    Fin 3 × LiftableGLVOrbitRep ≃ LiftableFactorBaseX :=
  layerLiftableEquiv.trans indexedLiftableEquiv

/-- Exactly `283527` of the `564522` factor-base coordinates lift. -/
theorem card_liftableFactorBaseX :
    Fintype.card LiftableFactorBaseX = 283527 := by
  calc
    Fintype.card LiftableFactorBaseX =
        Fintype.card (Fin 3 × LiftableGLVOrbitRep) :=
      (Fintype.card_congr liftableOrbitEquiv).symm
    _ = 283527 := by
      rw [Fintype.card_prod, Fintype.card_fin, card_liftableGLVOrbitRep]

/-- Exactly `280995` factor-base coordinates do not lift. -/
theorem card_nonliftableFactorBaseX :
    Fintype.card NonliftableFactorBaseX = 280995 := by
  rw [Fintype.card_subtype_compl, card_factorBaseX,
    card_liftableFactorBaseX]

/-! ## Character sum and signed affine points -/

/-- The quadratic-character sum over the factor base.  The zero branch is
absent by `secp256k1_rhs_ne_zero`, so this is `+1` on liftable coordinates and
`-1` on nonliftable coordinates. -/
noncomputable def factorBaseCharacterSum : ℤ :=
  by
    classical
    exact ∑ x : FactorBaseX, if IsLiftable x.1 then (1 : ℤ) else -1

/-- The exact quadratic-character sum over the coordinate factor base is
`2532`. -/
theorem factorBaseCharacterSum_eq : factorBaseCharacterSum = 2532 := by
  classical
  let liftGlobal : Fintype LiftableFactorBaseX := inferInstance
  let nonliftGlobal : Fintype NonliftableFactorBaseX := inferInstance
  letI : Fintype LiftableFactorBaseX :=
    Subtype.fintype (fun x : FactorBaseX ↦ IsLiftable x.1)
  letI : Fintype NonliftableFactorBaseX :=
    Subtype.fintype (fun x : FactorBaseX ↦ ¬IsLiftable x.1)
  have hcardLift :
      Fintype.card LiftableFactorBaseX =
        @Fintype.card LiftableFactorBaseX liftGlobal :=
    @Fintype.card_congr LiftableFactorBaseX LiftableFactorBaseX
      inferInstance liftGlobal (Equiv.refl _)
  have hcardNonlift :
      Fintype.card NonliftableFactorBaseX =
        @Fintype.card NonliftableFactorBaseX nonliftGlobal :=
    @Fintype.card_congr NonliftableFactorBaseX NonliftableFactorBaseX
      inferInstance nonliftGlobal (Equiv.refl _)
  have hlift :
      (∑ x : LiftableFactorBaseX,
        if IsLiftable x.1.1 then (1 : ℤ) else -1) =
        (Fintype.card LiftableFactorBaseX : ℤ) := by
    calc
      _ = ∑ _x : LiftableFactorBaseX, (1 : ℤ) := by
        apply Finset.sum_congr rfl
        intro x _
        rw [if_pos x.2]
      _ = (Fintype.card LiftableFactorBaseX : ℤ) := by simp
  have hnonlift :
      (∑ x : NonliftableFactorBaseX,
        if IsLiftable x.1.1 then (1 : ℤ) else -1) =
        -(Fintype.card NonliftableFactorBaseX : ℤ) := by
    calc
      _ = ∑ _x : NonliftableFactorBaseX, (-1 : ℤ) := by
        apply Finset.sum_congr rfl
        intro x _
        rw [if_neg x.2]
      _ = -(Fintype.card NonliftableFactorBaseX : ℤ) := by simp
  rw [factorBaseCharacterSum,
    ← Fintype.sum_subtype_add_sum_subtype
      (p := fun x : FactorBaseX ↦ IsLiftable x.1)]
  rw [hlift, hnonlift, hcardLift, hcardNonlift]
  rw [card_liftableFactorBaseX, card_nonliftableFactorBaseX]
  norm_num

/-- The two affine `y`-coordinates above a liftable factor-base coordinate. -/
abbrev LiftFiber (x : LiftableFactorBaseX) :=
  {y : Fp // y ^ 2 = rhs x.1.1}

/-- Signed affine factor-base points, retaining both square-root signs. -/
abbrev SignedAffineFactorBasePoint :=
  Σ x : LiftableFactorBaseX, LiftFiber x

noncomputable def liftY (x : LiftableFactorBaseX) : Fp :=
  Classical.choose x.2.exists_mul_self

private theorem liftY_mul_self (x : LiftableFactorBaseX) :
    liftY x * liftY x = rhs x.1.1 :=
  (Classical.choose_spec x.2.exists_mul_self).symm

private theorem liftY_sq (x : LiftableFactorBaseX) :
    liftY x ^ 2 = rhs x.1.1 := by
  simpa only [pow_two] using liftY_mul_self x

private theorem liftY_ne_zero (x : LiftableFactorBaseX) : liftY x ≠ 0 := by
  intro hzero
  have hsquare := liftY_sq x
  rw [hzero, zero_pow (by norm_num : 2 ≠ 0)] at hsquare
  exact secp256k1_rhs_ne_zero x.1.1 hsquare.symm

private theorem two_ne_zero_fp : (2 : Fp) ≠ 0 := by
  change ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0
  rw [Ne, ZMod.natCast_eq_zero_iff]
  exact Nat.not_dvd_of_pos_of_lt (by norm_num)
    (by norm_num [Secp256k1.p])

private theorem neg_liftY_ne_liftY (x : LiftableFactorBaseX) :
    -liftY x ≠ liftY x := by
  intro hneg
  have hadd : liftY x + liftY x = 0 := by
    calc
      liftY x + liftY x = -liftY x + liftY x :=
        congrArg (fun z : Fp ↦ z + liftY x) hneg.symm
      _ = 0 := neg_add_cancel (liftY x)
  have hmul : (2 : Fp) * liftY x = 0 := by
    simpa only [two_mul] using hadd
  rcases mul_eq_zero.mp hmul with htwo | hy
  · exact two_ne_zero_fp htwo
  · exact liftY_ne_zero x hy

private noncomputable def boolEquivLiftFiber (x : LiftableFactorBaseX) :
    Bool ≃ LiftFiber x where
  toFun
    | false => ⟨liftY x, liftY_sq x⟩
    | true => ⟨-liftY x, by simpa using liftY_sq x⟩
  invFun y := if y.1 = liftY x then false else true
  left_inv b := by
    cases b <;> simp [neg_liftY_ne_liftY]
  right_inv y := by
    apply Subtype.ext
    rcases eq_or_eq_neg_of_sq_eq_sq y.1 (liftY x)
        (y.2.trans (liftY_sq x).symm) with h | h
    · simp [h]
    · simp [h, neg_liftY_ne_liftY]

/-- Every liftable coordinate has exactly two affine square-root signs. -/
theorem card_liftFiber (x : LiftableFactorBaseX) :
    Fintype.card (LiftFiber x) = 2 := by
  calc
    Fintype.card (LiftFiber x) = Fintype.card Bool :=
      Fintype.card_congr (boolEquivLiftFiber x).symm
    _ = 2 := Fintype.card_bool

/-- The liftable factor base contains exactly `567054` signed affine points. -/
theorem card_signedAffineFactorBasePoint :
    Fintype.card SignedAffineFactorBasePoint = 567054 := by
  rw [Fintype.card_sigma]
  simp_rw [card_liftFiber]
  rw [Finset.sum_const, Finset.card_univ, card_liftableFactorBaseX]
  norm_num [nsmul_eq_mul]

private theorem liftFiber_equation (x : LiftableFactorBaseX) (y : LiftFiber x) :
    Ecdlp.Curve.secp256k1.toAffine.Equation x.1.1 y.1 := by
  rw [WeierstrassCurve.Affine.equation_iff]
  simpa only [Ecdlp.Curve.secp256k1, rhs, zero_mul, add_zero] using y.2

private theorem liftFiber_nonsingular (x : LiftableFactorBaseX) (y : LiftFiber x) :
    Ecdlp.Curve.secp256k1.toAffine.Nonsingular x.1.1 y.1 :=
  WeierstrassCurve.Affine.equation_iff_nonsingular.mp (liftFiber_equation x y)

/-- Interpret a signed affine factor-base pair as a genuine nonidentity point of
the Mathlib secp256k1 point group. -/
noncomputable def toPoint (z : SignedAffineFactorBasePoint) :
    Ecdlp.Curve.secp256k1.toAffine.Point :=
  .some z.1.1.1 z.2.1 (liftFiber_nonsingular z.1 z.2)

/-- Every signed affine factor-base pair maps to a nonidentity curve point. -/
theorem toPoint_ne_zero (z : SignedAffineFactorBasePoint) : toPoint z ≠ 0 :=
  WeierstrassCurve.Affine.Point.some_ne_zero _

end Ecdlp.M16FactorBaseLiftable
