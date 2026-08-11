import Ecdlp.Proved.M16DirectPointSemantics

/-!
# Exact base-field recovery fibers for direct M16 roots

This module packages the finite base-field square-root choices above sixteen
prescribed source coordinates.  A recovery witness consists of those sixteen
choices together with either orientation of a supplied target point.  Global
negation exchanges the two orientations, giving an exact equivalence between
the full fiber and one normalized orientation times `Bool`.

The main theorem is a semantic finite-specification result: relative to a
base-field target point above `X`, the recovery fiber is inhabited exactly
when `S17At x X = 0` and every source coordinate is liftable over the base
field.  It is not an efficient square-root or recovery algorithm and makes no
PFPO, `AllRoots`, runtime, memory, solver-node, relation-rank, yield, cost, or
discrete-log claim.
-/

namespace Ecdlp.M16BaseRecoveryFiber

open scoped BigOperators

open WeierstrassCurve.Affine
open Ecdlp.Curve
open Ecdlp.M16DirectPointSemantics
open Ecdlp.M16DirectSystemRootBridge
open Ecdlp.M16FactorBaseLiftable
open Ecdlp.M16FrobeniusPointSplit
open Ecdlp.SemaevLeftFoldAffine

noncomputable section

abbrev Fp := ZMod Secp256k1.p
abbrev FpBar := AlgebraicClosure Fp
abbrev BasePoint := secp256k1.toAffine.Point
abbrev BarCurve := secp256k1 ⁄ FpBar
abbrev BarPoint := BarCurve.Point

local instance : DecidableEq FpBar := Classical.decEq _

private instance barCurve_isElliptic : BarCurve.IsElliptic :=
  inferInstanceAs
    ((secp256k1.map (algebraMap Fp FpBar)).IsElliptic)

/-! ## One-coordinate base-field lifts -/

/-- The finite fiber of base-field square roots above an arbitrary source
coordinate.  Unlike the factor-base-specific `LiftFiber`, this definition
and its proofs remain valid in the formal `rhs a = 0` singleton edge case;
no claim is made that this edge occurs for the fixed secp256k1 field. -/
def LiftAt (a : Fp) :=
  {y : Fp // y ^ 2 = rhs a}

noncomputable instance liftAtFintype (a : Fp) : Fintype (LiftAt a) :=
  by
    classical
    exact Subtype.fintype _

private theorem liftAt_equation (a : Fp) (y : LiftAt a) :
    secp256k1.toAffine.Equation a y.1 := by
  rw [WeierstrassCurve.Affine.equation_iff]
  simpa only [secp256k1, rhs, zero_mul, add_zero] using y.2

private theorem liftAt_nonsingular (a : Fp) (y : LiftAt a) :
    secp256k1.toAffine.Nonsingular a y.1 :=
  WeierstrassCurve.Affine.equation_iff_nonsingular.mp
    (liftAt_equation a y)

/-- Interpret a square-root choice as the corresponding affine base-field
secp256k1 point. -/
noncomputable def liftPoint (a : Fp) (y : LiftAt a) : BasePoint :=
  Point.some a y.1 (liftAt_nonsingular a y)

theorem liftPoint_ne_zero (a : Fp) (y : LiftAt a) :
    liftPoint a y ≠ 0 :=
  Point.some_ne_zero _

theorem liftPoint_injective (a : Fp) :
    Function.Injective (liftPoint a) := by
  intro y z h
  apply Subtype.ext
  exact (Point.some.inj h).right

/-- Actual base-field curve points whose closure inclusions lie above `a`.
The predicate rules out the point at infinity and records the intended
coordinate independently of the concrete `Point.some` representation. -/
def ActualLiftAt (a : Fp) :=
  {P : BasePoint // LiesOver a (includePoint P)}

theorem liesOver_include_liftPoint (a : Fp) (y : LiftAt a) :
    LiesOver a (includePoint (liftPoint a y)) := by
  apply (liesOver_iff_barKummer_eq _ _).mpr
  rw [liftPoint, includePoint_some]
  rfl

private theorem actualLiftAt_exists_lift (a : Fp) (P : ActualLiftAt a) :
    ∃ y : LiftAt a, P.1 = liftPoint a y := by
  rcases P with ⟨P, hP⟩
  rcases P with _ | ⟨px, py, hcurve⟩
  · rcases hP with ⟨yb, hb, hEq⟩
    change (0 : BarPoint) =
      Point.some (algebraMap Fp FpBar a) yb hb at hEq
    exact (Point.some_ne_zero hb hEq.symm).elim
  · rcases hP with ⟨yb, hb, hEq⟩
    rw [includePoint_some] at hEq
    have hxmap := (Point.some.inj hEq).left
    have hx : px = a := (algebraMap Fp FpBar).injective hxmap
    subst px
    have hy : py ^ 2 = rhs a := by
      have he := hcurve.1
      rw [WeierstrassCurve.Affine.equation_iff] at he
      simpa only [secp256k1, rhs, zero_mul, add_zero] using he
    exact ⟨⟨py, hy⟩, rfl⟩

/-- Square-root choices and actual base-field affine points above the same
coordinate are equivalent, including when the fiber has only the root zero. -/
noncomputable def liftAtEquivActualLiftAt (a : Fp) :
    LiftAt a ≃ ActualLiftAt a where
  toFun y := ⟨liftPoint a y, liesOver_include_liftPoint a y⟩
  invFun P := Classical.choose (actualLiftAt_exists_lift a P)
  left_inv y := by
    apply liftPoint_injective a
    exact (Classical.choose_spec
      (actualLiftAt_exists_lift a
        ⟨liftPoint a y, liesOver_include_liftPoint a y⟩)).symm
  right_inv P := by
    apply Subtype.ext
    exact (Classical.choose_spec (actualLiftAt_exists_lift a P)).symm

theorem nonempty_liftAt_iff_isLiftable (a : Fp) :
    Nonempty (LiftAt a) ↔ IsLiftable a := by
  rw [IsLiftable, isSquare_iff_exists_sq]
  constructor
  · rintro ⟨y⟩
    exact ⟨y.1, y.2.symm⟩
  · rintro ⟨y, hy⟩
    exact ⟨⟨y, hy.symm⟩⟩

/-- Negate a square-root choice without changing its prescribed coordinate. -/
def negLiftAt {a : Fp} (y : LiftAt a) : LiftAt a :=
  ⟨-y.1, by simpa using y.2⟩

@[simp] theorem negLiftAt_involutive {a : Fp} (y : LiftAt a) :
    negLiftAt (negLiftAt y) = y := by
  apply Subtype.ext
  simp [negLiftAt]

@[simp] theorem liftPoint_negLiftAt {a : Fp} (y : LiftAt a) :
    liftPoint a (negLiftAt y) = -liftPoint a y := by
  rw [liftPoint, liftPoint, Point.neg_some]
  simp only [Point.some.injEq]
  refine ⟨trivial, ?_⟩
  simp [negLiftAt, WeierstrassCurve.Affine.negY, secp256k1,
    WeierstrassCurve.toAffine]

/-! ## Sixteen-coordinate recovery fibers -/

/-- One base-field square-root choice in every labelled source slot. -/
abbrev LiftTuple (x : Fin 16 → Fp) :=
  ∀ i, LiftAt (x i)

theorem nonempty_liftTuple_iff (x : Fin 16 → Fp) :
    Nonempty (LiftTuple x) ↔ ∀ i, IsLiftable (x i) := by
  constructor
  · rintro ⟨L⟩ i
    exact (nonempty_liftAt_iff_isLiftable (x i)).mp ⟨L i⟩
  · intro h
    exact ⟨fun i ↦ Classical.choice
      ((nonempty_liftAt_iff_isLiftable (x i)).mpr (h i))⟩

/-- The base-field point tuple determined by a square-root tuple. -/
noncomputable def liftTuplePoints {x : Fin 16 → Fp}
    (L : LiftTuple x) : Fin 16 → BasePoint :=
  fun i ↦ liftPoint (x i) (L i)

/-- The two target orientations.  `false` is the normalized orientation
`R`; `true` is `-R`. -/
def signedTarget (sign : Bool) (R : BasePoint) : BasePoint :=
  if sign then -R else R

@[simp] theorem signedTarget_false (R : BasePoint) :
    signedTarget false R = R := rfl

@[simp] theorem signedTarget_true (R : BasePoint) :
    signedTarget true R = -R := rfl

@[simp] theorem signedTarget_not (sign : Bool) (R : BasePoint) :
    signedTarget (!sign) R = -signedTarget sign R := by
  cases sign <;> simp [signedTarget]

/-- A square-root tuple is compatible with one chosen target orientation
when the corresponding seventeen base-field points sum to zero. -/
def Compatible (x : Fin 16 → Fp) (R : BasePoint)
    (L : LiftTuple x) (sign : Bool) : Prop :=
  (∑ i, liftTuplePoints L i) + signedTarget sign R = 0

/-- The complete semantic recovery fiber, retaining both target signs. -/
def RecoveryFiber (x : Fin 16 → Fp) (R : BasePoint) :=
  {z : LiftTuple x × Bool // Compatible x R z.1 z.2}

/-- The same semantic fiber with the target orientation fixed to `R`. -/
def NormalizedFiber (x : Fin 16 → Fp) (R : BasePoint) :=
  {L : LiftTuple x // Compatible x R L false}

/-- Negate every labelled square-root choice. -/
def globalNegate {x : Fin 16 → Fp} (L : LiftTuple x) : LiftTuple x :=
  fun i ↦ negLiftAt (L i)

@[simp] theorem globalNegate_involutive {x : Fin 16 → Fp}
    (L : LiftTuple x) :
    globalNegate (globalNegate L) = L := by
  funext i
  exact negLiftAt_involutive (L i)

theorem sum_liftTuplePoints_globalNegate {x : Fin 16 → Fp}
    (L : LiftTuple x) :
    (∑ i, liftTuplePoints (globalNegate L) i) =
      -(∑ i, liftTuplePoints L i) := by
  simp [liftTuplePoints, globalNegate, Finset.sum_neg_distrib]

/-- Simultaneously negating every source point and flipping the target sign
preserves compatibility. -/
theorem compatible_globalNegate_iff {x : Fin 16 → Fp}
    {R : BasePoint} {L : LiftTuple x} {sign : Bool} :
    Compatible x R (globalNegate L) (!sign) ↔
      Compatible x R L sign := by
  rw [Compatible, Compatible, sum_liftTuplePoints_globalNegate,
    signedTarget_not, ← neg_add, neg_eq_zero]

/-- The fixed-point-free involution on the full recovery fiber.  Its lack of
fixed points comes from the retained Boolean target label, even if a
particular square root is its own negative. -/
noncomputable def recoveryGlobalNegate {x : Fin 16 → Fp}
    {R : BasePoint} (w : RecoveryFiber x R) : RecoveryFiber x R :=
  ⟨(globalNegate w.1.1, !w.1.2),
    compatible_globalNegate_iff.mpr w.2⟩

@[simp] theorem recoveryGlobalNegate_involutive {x : Fin 16 → Fp}
    {R : BasePoint} (w : RecoveryFiber x R) :
    recoveryGlobalNegate (recoveryGlobalNegate w) = w := by
  rcases w with ⟨⟨L, sign⟩, h⟩
  apply Subtype.ext
  cases sign <;>
    simp [recoveryGlobalNegate, globalNegate_involutive]

theorem recoveryGlobalNegate_ne {x : Fin 16 → Fp}
    {R : BasePoint} (w : RecoveryFiber x R) :
    recoveryGlobalNegate w ≠ w := by
  intro h
  have hsign := congrArg (fun z : RecoveryFiber x R ↦ z.1.2) h
  rcases w with ⟨⟨L, sign⟩, hw⟩
  cases sign <;> simp [recoveryGlobalNegate] at hsign

private def normalizeTuple {x : Fin 16 → Fp}
    (L : LiftTuple x) (sign : Bool) : LiftTuple x :=
  if sign then globalNegate L else L

private theorem compatible_normalizeTuple {x : Fin 16 → Fp}
    {R : BasePoint} {L : LiftTuple x} {sign : Bool}
    (h : Compatible x R L sign) :
    Compatible x R (normalizeTuple L sign) false := by
  cases sign with
  | false => simpa [normalizeTuple] using h
  | true =>
      simpa [normalizeTuple] using
        (compatible_globalNegate_iff
          (x := x) (R := R) (L := L) (sign := true)).mpr h

private theorem compatible_denormalizeTuple {x : Fin 16 → Fp}
    {R : BasePoint} {L : LiftTuple x}
    (h : Compatible x R L false) (sign : Bool) :
    Compatible x R (normalizeTuple L sign) sign := by
  cases sign with
  | false => simpa [normalizeTuple] using h
  | true =>
      simpa [normalizeTuple] using
        (compatible_globalNegate_iff
          (x := x) (R := R) (L := L) (sign := false)).mpr h

/-- Exact separation of target-sign ambiguity from the normalized fiber. -/
noncomputable def recoveryFiberEquivNormalizedFiberProdBool
    (x : Fin 16 → Fp) (R : BasePoint) :
    RecoveryFiber x R ≃ NormalizedFiber x R × Bool where
  toFun w :=
    (⟨normalizeTuple w.1.1 w.1.2, compatible_normalizeTuple w.2⟩,
      w.1.2)
  invFun z :=
    ⟨(normalizeTuple z.1.1 z.2, z.2),
      compatible_denormalizeTuple z.1.2 z.2⟩
  left_inv w := by
    apply Subtype.ext
    rcases w with ⟨⟨L, sign⟩, h⟩
    cases sign <;>
      simp [normalizeTuple, globalNegate_involutive]
  right_inv z := by
    rcases z with ⟨⟨L, h⟩, sign⟩
    cases sign <;>
      simp [normalizeTuple, globalNegate_involutive]

noncomputable instance normalizedFiberFintype
    (x : Fin 16 → Fp) (R : BasePoint) : Fintype (NormalizedFiber x R) := by
  classical
  exact Subtype.fintype _

noncomputable instance recoveryFiberFintype
    (x : Fin 16 → Fp) (R : BasePoint) : Fintype (RecoveryFiber x R) := by
  classical
  exact Subtype.fintype _

/-- The retained Boolean target label doubles the normalized semantic fiber
exactly, including degenerate cases in which pointwise negation fixes some
lifts.  This counts labelled orientations, not unlabelled recoveries. -/
theorem card_recoveryFiber_eq_two_mul_card_normalizedFiber
    (x : Fin 16 → Fp) (R : BasePoint) :
    Fintype.card (RecoveryFiber x R) =
      2 * Fintype.card (NormalizedFiber x R) := by
  calc
    Fintype.card (RecoveryFiber x R) =
        Fintype.card (NormalizedFiber x R × Bool) :=
      Fintype.card_congr
        (recoveryFiberEquivNormalizedFiberProdBool x R)
    _ = 2 * Fintype.card (NormalizedFiber x R) := by
      simp [Nat.mul_comm]

@[simp] theorem recoveryFiberEquiv_sign
    (x : Fin 16 → Fp) (R : BasePoint) (w : RecoveryFiber x R) :
    (recoveryFiberEquivNormalizedFiberProdBool x R w).2 = w.1.2 :=
  rfl

/-- Under the normalization equivalence, global negation fixes the normalized
witness and flips precisely the Boolean target label. -/
theorem recoveryFiberEquiv_globalNegate
    (x : Fin 16 → Fp) (R : BasePoint) (w : RecoveryFiber x R) :
    recoveryFiberEquivNormalizedFiberProdBool x R
        (recoveryGlobalNegate w) =
      ((recoveryFiberEquivNormalizedFiberProdBool x R w).1,
        !(recoveryFiberEquivNormalizedFiberProdBool x R w).2) := by
  rcases w with ⟨⟨L, sign⟩, h⟩
  cases sign
  apply Prod.ext
  · apply Subtype.ext
    simp [recoveryFiberEquivNormalizedFiberProdBool,
      recoveryGlobalNegate, normalizeTuple]
  · rfl
  apply Prod.ext
  · apply Subtype.ext
    simp [recoveryFiberEquivNormalizedFiberProdBool,
      recoveryGlobalNegate, normalizeTuple]
  · rfl

/-! ## Canonical finite specification -/

/-- The canonical duplicate-free finite specification obtained by filtering
all finite square-root tuples and both Boolean target labels.  This is a
mathematical enumeration specification, not an efficiency claim. -/
noncomputable def recoveryFinset (x : Fin 16 → Fp) (R : BasePoint) :
    Finset (LiftTuple x × Bool) := by
  classical
  exact Finset.univ.filter (fun z ↦ Compatible x R z.1 z.2)

@[simp] theorem mem_recoveryFinset_iff
    {x : Fin 16 → Fp} {R : BasePoint} {z : LiftTuple x × Bool} :
    z ∈ recoveryFinset x R ↔ Compatible x R z.1 z.2 := by
  classical
  simp [recoveryFinset]

/-- The filtered specification contains exactly the underlying witnesses of
`RecoveryFiber`; `Finset` supplies duplicate-freeness by construction. -/
noncomputable def recoveryFiberEquivRecoveryFinsetSubtype
    (x : Fin 16 → Fp) (R : BasePoint) :
    RecoveryFiber x R ≃
      {z : LiftTuple x × Bool // z ∈ recoveryFinset x R} := by
  apply Equiv.subtypeEquivProp
  funext z
  exact propext mem_recoveryFinset_iff.symm

theorem card_recoveryFinset (x : Fin 16 → Fp) (R : BasePoint) :
    (recoveryFinset x R).card = Fintype.card (RecoveryFiber x R) := by
  rw [← Fintype.card_coe]
  exact (Fintype.card_congr
    (recoveryFiberEquivRecoveryFinsetSubtype x R)).symm

/-! ## Exact nonemptiness criterion -/

theorem recoveryFiber_all_isLiftable
    {x : Fin 16 → Fp} {R : BasePoint} (w : RecoveryFiber x R) (i : Fin 16) :
    IsLiftable (x i) :=
  (nonempty_liftAt_iff_isLiftable (x i)).mp ⟨w.1.1 i⟩

private theorem S17At_eq_zero_of_normalizedFiber
    {x : Fin 16 → Fp} {X : Fp} {R : BasePoint}
    (hR : LiesOver X (includePoint R)) (w : NormalizedFiber x R) :
    S17At x X = 0 := by
  apply
    (S17At_eq_zero_iff_exists_point_sum_add_target_eq_zero
      x X (includePoint R) hR).mpr
  refine ⟨fun i ↦ includePoint (liftTuplePoints w.1 i), ?_, ?_⟩
  · intro i
    exact liesOver_include_liftPoint (x i) (w.1 i)
  · have hmap := congrArg includePoint w.2
    simpa only [Compatible, signedTarget_false, map_add, map_zero,
      map_sum] using hmap

theorem S17At_eq_zero_of_recoveryFiber
    {x : Fin 16 → Fp} {X : Fp} {R : BasePoint}
    (hR : LiesOver X (includePoint R)) (w : RecoveryFiber x R) :
    S17At x X = 0 := by
  exact S17At_eq_zero_of_normalizedFiber hR
    (recoveryFiberEquivNormalizedFiberProdBool x R w).1

private theorem nonempty_normalizedFiber_of_S17At_eq_zero_of_all_isLiftable
    {x : Fin 16 → Fp} {X : Fp} {R : BasePoint}
    (hR : LiesOver X (includePoint R))
    (hroot : S17At x X = 0) (hlift : ∀ i, IsLiftable (x i)) :
    Nonempty (NormalizedFiber x R) := by
  rcases
      (S17At_eq_zero_iff_exists_point_sum_add_target_eq_zero
        x X (includePoint R) hR).mp hroot with
    ⟨P, hover, hsum⟩
  have hQexist : ∀ i, ∃ Q : BasePoint, includePoint Q = P i := by
    intro i
    exact exists_includePoint_eq_of_liesOver_of_isLiftable
      (hover i) (hlift i)
  choose Q hQ using hQexist
  have hQover : ∀ i, LiesOver (x i) (includePoint (Q i)) := by
    intro i
    rw [hQ i]
    exact hover i
  let A : ∀ i, ActualLiftAt (x i) :=
    fun i ↦ ⟨Q i, hQover i⟩
  let L : LiftTuple x :=
    fun i ↦ (liftAtEquivActualLiftAt (x i)).symm (A i)
  have hpoint : ∀ i, liftPoint (x i) (L i) = Q i := by
    intro i
    change liftPoint (x i)
        ((liftAtEquivActualLiftAt (x i)).symm (A i)) = Q i
    exact congrArg Subtype.val
      ((liftAtEquivActualLiftAt (x i)).apply_symm_apply (A i))
  have hsumBar :
      (∑ i, includePoint (Q i)) + includePoint R = 0 := by
    simpa only [← hQ] using hsum
  have hsumBase : (∑ i, Q i) + R = 0 := by
    apply includePoint_injective
    simpa only [map_add, map_zero, map_sum] using hsumBar
  refine ⟨⟨L, ?_⟩⟩
  change (∑ i, liftPoint (x i) (L i)) + R = 0
  simpa only [hpoint] using hsumBase

/-- Keystone semantic contract: for a supplied affine base-field target point
above `X`, the exact recovery fiber is inhabited precisely by a direct M16
root whose sixteen coordinates all lift over the base field. -/
theorem nonempty_recoveryFiber_iff_S17At_eq_zero_and_all_isLiftable
    (x : Fin 16 → Fp) (X : Fp) (R : BasePoint)
    (hR : LiesOver X (includePoint R)) :
    Nonempty (RecoveryFiber x R) ↔
      S17At x X = 0 ∧ ∀ i, IsLiftable (x i) := by
  constructor
  · rintro ⟨w⟩
    exact ⟨S17At_eq_zero_of_recoveryFiber hR w,
      recoveryFiber_all_isLiftable w⟩
  · rintro ⟨hroot, hlift⟩
    rcases
        nonempty_normalizedFiber_of_S17At_eq_zero_of_all_isLiftable
          hR hroot hlift with
      ⟨w⟩
    exact ⟨(recoveryFiberEquivNormalizedFiberProdBool x R).symm
      (w, false)⟩

/-- Any prescribed nonliftable slot makes the recovery fiber empty,
independently of the target. -/
theorem not_nonempty_recoveryFiber_of_not_isLiftable
    {x : Fin 16 → Fp} (R : BasePoint) (i : Fin 16)
    (hi : ¬ IsLiftable (x i)) :
    ¬ Nonempty (RecoveryFiber x R) := by
  rintro ⟨w⟩
  exact hi (recoveryFiber_all_isLiftable w i)

/-- Thin specialization for a literal direct System-(4) solution.  It adds
no recovery algorithm: once the system hypothesis supplies the root
equation, fiber inhabitation is exactly pointwise liftability. -/
theorem nonempty_recoveryFiber_of_directSystem4_iff_all_isLiftable
    (u : Fin 16 → ChainVars) (X : Fp) (R : BasePoint)
    (hR : LiesOver X (includePoint R)) (hsystem : DirectSystem4 X u) :
    Nonempty (RecoveryFiber (fun i ↦ (u i).x₁) R) ↔
      ∀ i, IsLiftable ((u i).x₁) := by
  rw [nonempty_recoveryFiber_iff_S17At_eq_zero_and_all_isLiftable
    (fun i ↦ (u i).x₁) X R hR]
  simp only [hsystem.1, true_and]

end

end Ecdlp.M16BaseRecoveryFiber
