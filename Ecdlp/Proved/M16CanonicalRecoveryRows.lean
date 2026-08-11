import Ecdlp.Proved.M16BaseRecoveryFiber
import Ecdlp.Proved.M16FactorBaseLiftable

/-!
# Canonical coefficient rows for factor-base M16 recovery witnesses

This module specializes the exact base-field recovery fiber to sixteen labelled
liftable factor-base coordinates.  Each coordinate is given the uniquely
specified square root whose canonical `ZMod.val` representative is smaller
than that of its negative.  Relative to these reference lifts, a recovery
witness determines an integral `Finsupp` row.  Repeated factor-base coordinates
are deliberately aggregated in that row.

The target-sign normalization is exact: if `tau` is `1` for the retained
`false` target label and `-1` for `true`, the canonical row is `(-tau)` times
the raw source row.  Consequently it evaluates to the supplied target point
and is unchanged by simultaneous global source negation and target-label
flipping.  These statements remain valid for target `R = 0`; in that case the
two Boolean labels are still distinct labelled recovery data even though they
name the same geometric target point.

The final finite sets are mathematical image and fiber specifications.  They
do not assert uniqueness of rows or recoveries, injectivity of row evaluation,
or efficient enumeration; they do not implement `Recover`, PFPO, `AllRoots`,
a square-root or recovery algorithm, or any runtime, memory, solver-node,
relation-rank, relation-yield, cost, or ECDLP-shortcut claim.
-/

namespace Ecdlp.M16CanonicalRecoveryRows

open scoped BigOperators

open Ecdlp.M16BaseRecoveryFiber
open Ecdlp.M16FactorBaseLiftable

noncomputable section

abbrev Fp := ZMod Secp256k1.p
abbrev BasePoint := Ecdlp.Curve.secp256k1.toAffine.Point

/-! ## Factor-base recovery data -/

/-- Sixteen labelled liftable factor-base coordinates. -/
abbrev FactorBaseTuple := Fin 16 → LiftableFactorBaseX

/-- Forget the factor-base and liftability proofs, retaining the field
coordinate in every labelled slot. -/
def sourceCoordinates (x : FactorBaseTuple) : Fin 16 → Fp :=
  fun i ↦ (x i).1.1

/-- The underlying labelled lift tuple and retained target-sign label. -/
abbrev RecoveryData (x : FactorBaseTuple) :=
  LiftTuple (sourceCoordinates x) × Bool

/-- Integral coefficient rows indexed by liftable factor-base coordinates. -/
abbrev Row := LiftableFactorBaseX →₀ ℤ

/-! ## A uniquely specified reference lift -/

/-- An arbitrary temporary lift used only to construct the uniquely
characterized lower-residue lift. -/
private noncomputable def someLift (a : LiftableFactorBaseX) :
    LiftAt a.1.1 :=
  Classical.choice
    ((nonempty_liftAt_iff_isLiftable a.1.1).mpr a.2)

private theorem two_ne_zero_fp : (2 : Fp) ≠ 0 := by
  change ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0
  rw [Ne, ZMod.natCast_eq_zero_iff]
  exact Nat.not_dvd_of_pos_of_lt (by norm_num)
    (by norm_num [Secp256k1.p])

theorem liftAt_value_ne_zero (a : LiftableFactorBaseX)
    (y : LiftAt a.1.1) : y.1 ≠ 0 := by
  intro hy
  apply secp256k1_rhs_ne_zero a.1.1
  rw [← y.2, hy]
  norm_num

theorem liftAt_value_ne_neg (a : LiftableFactorBaseX)
    (y : LiftAt a.1.1) : y.1 ≠ -y.1 := by
  intro hneg
  have hadd : y.1 + y.1 = 0 := by
    calc
      y.1 + y.1 = y.1 + (-y.1) :=
        congrArg (fun z : Fp ↦ y.1 + z) hneg
      _ = 0 := add_neg_cancel y.1
  have hmul : (2 : Fp) * y.1 = 0 := by
    simpa only [two_mul] using hadd
  rcases mul_eq_zero.mp hmul with htwo | hy
  · exact two_ne_zero_fp htwo
  · exact liftAt_value_ne_zero a y hy

theorem liftAt_ne_negLiftAt (a : LiftableFactorBaseX)
    (y : LiftAt a.1.1) : y ≠ negLiftAt y := by
  intro h
  exact liftAt_value_ne_neg a y (congrArg Subtype.val h)

private theorem liftAt_val_ne_neg_val (a : LiftableFactorBaseX)
    (y : LiftAt a.1.1) : y.1.val ≠ (-y.1).val := by
  intro h
  exact liftAt_value_ne_neg a y
    ((ZMod.val_injective Secp256k1.p) h)

/-- `ZMod` has no field order.  "Lower residue" refers only to the canonical
natural-number representatives returned by `ZMod.val`. -/
def IsLowerResidueLift (a : LiftableFactorBaseX)
    (y : LiftAt a.1.1) : Prop :=
  y.1.val < (-y.1).val

/-- The reference lift is the member of the pair `{y, -y}` with the smaller
canonical residue representative.  Its characterization below is independent
of the temporary choice in `someLift`. -/
noncomputable def referenceLift (a : LiftableFactorBaseX) :
    LiftAt a.1.1 :=
  if (someLift a).1.val < (-(someLift a).1).val then
    someLift a
  else
    negLiftAt (someLift a)

theorem referenceLift_isLowerResidue (a : LiftableFactorBaseX) :
    IsLowerResidueLift a (referenceLift a) := by
  classical
  by_cases h : (someLift a).1.val < (-(someLift a).1).val
  · simp [referenceLift, IsLowerResidueLift, h]
  · have hrev : (-(someLift a).1).val < (someLift a).1.val :=
      lt_of_le_of_ne (Nat.le_of_not_gt h)
        (liftAt_val_ne_neg_val a (someLift a)).symm
    simpa [referenceLift, IsLowerResidueLift, negLiftAt, h] using hrev

/-- Every lift above a liftable factor-base coordinate is either the fixed
reference lift or its negative. -/
theorem liftAt_eq_reference_or_neg_reference
    (a : LiftableFactorBaseX) (y : LiftAt a.1.1) :
    y = referenceLift a ∨ y = negLiftAt (referenceLift a) := by
  rcases eq_or_eq_neg_of_sq_eq_sq y.1 (referenceLift a).1
      (y.2.trans (referenceLift a).2.symm) with h | h
  · exact Or.inl (Subtype.ext h)
  · right
    apply Subtype.ext
    simpa [negLiftAt] using h

theorem lowerResidueLift_unique (a : LiftableFactorBaseX)
    {y : LiftAt a.1.1} (hy : IsLowerResidueLift a y) :
    y = referenceLift a := by
  rcases liftAt_eq_reference_or_neg_reference a y with h | h
  · exact h
  · subst y
    have href : (referenceLift a).1.val <
        (-(referenceLift a).1).val :=
      referenceLift_isLowerResidue a
    have hneg : (-(referenceLift a).1).val <
        (referenceLift a).1.val := by
      simpa [IsLowerResidueLift, negLiftAt] using hy
    exact (Nat.lt_asymm href hneg).elim

/-- The lower-residue lift exists uniquely.  This is the reproducible
characterization of `referenceLift`, rather than a positivity assertion in
the finite field. -/
theorem existsUnique_lowerResidueLift (a : LiftableFactorBaseX) :
    ∃! y : LiftAt a.1.1, IsLowerResidueLift a y :=
  ⟨referenceLift a, referenceLift_isLowerResidue a,
    fun _ hy ↦ lowerResidueLift_unique a hy⟩

/-- The unique sign of a lift relative to the lower-residue reference.
`false` is the reference and `true` its negative. -/
noncomputable def referenceSignEquiv (a : LiftableFactorBaseX) :
    Bool ≃ LiftAt a.1.1 := by
  classical
  refine
    { toFun := fun
        | false => referenceLift a
        | true => negLiftAt (referenceLift a)
      invFun := fun y => if y = referenceLift a then false else true
      left_inv := ?_
      right_inv := ?_ }
  · intro sign
    cases sign
    · simp
    · have hne : negLiftAt (referenceLift a) ≠ referenceLift a :=
        Ne.symm (liftAt_ne_negLiftAt a (referenceLift a))
      simp [hne]
  · intro y
    rcases liftAt_eq_reference_or_neg_reference a y with h | h
    · subst y
      simp
    · subst y
      have hne : negLiftAt (referenceLift a) ≠ referenceLift a :=
        Ne.symm (liftAt_ne_negLiftAt a (referenceLift a))
      simp [hne]

@[simp] theorem referenceSignEquiv_false (a : LiftableFactorBaseX) :
    referenceSignEquiv a false = referenceLift a :=
  rfl

@[simp] theorem referenceSignEquiv_true (a : LiftableFactorBaseX) :
    referenceSignEquiv a true = negLiftAt (referenceLift a) :=
  rfl

theorem existsUnique_referenceSign (a : LiftableFactorBaseX)
    (y : LiftAt a.1.1) :
    ∃! sign : Bool, y = referenceSignEquiv a sign := by
  refine ⟨(referenceSignEquiv a).symm y, ?_, ?_⟩
  · exact ((referenceSignEquiv a).apply_symm_apply y).symm
  · intro sign hsign
    rw [hsign]
    exact ((referenceSignEquiv a).symm_apply_apply sign).symm

/-! ## Source coefficients and row evaluation -/

def boolCoefficient : Bool → ℤ
  | false => 1
  | true => -1

@[simp] theorem boolCoefficient_false : boolCoefficient false = 1 := rfl
@[simp] theorem boolCoefficient_true : boolCoefficient true = -1 := rfl

@[simp] theorem boolCoefficient_not (sign : Bool) :
    boolCoefficient (!sign) = -boolCoefficient sign := by
  cases sign <;> norm_num [boolCoefficient]

/-- The coefficient `+1` or `-1` of a lift relative to its reference. -/
noncomputable def liftCoefficient (a : LiftableFactorBaseX)
    (y : LiftAt a.1.1) : ℤ :=
  boolCoefficient ((referenceSignEquiv a).symm y)

@[simp] theorem liftCoefficient_referenceLift (a : LiftableFactorBaseX) :
    liftCoefficient a (referenceLift a) = 1 := by
  change boolCoefficient
    ((referenceSignEquiv a).symm (referenceLift a)) = 1
  have hsign : (referenceSignEquiv a).symm (referenceLift a) = false := by
    apply (referenceSignEquiv a).symm_apply_eq.mpr
    rfl
  rw [hsign]
  rfl

@[simp] theorem liftCoefficient_neg_referenceLift
    (a : LiftableFactorBaseX) :
    liftCoefficient a (negLiftAt (referenceLift a)) = -1 := by
  change boolCoefficient
    ((referenceSignEquiv a).symm
      (negLiftAt (referenceLift a))) = -1
  have hsign : (referenceSignEquiv a).symm
      (negLiftAt (referenceLift a)) = true := by
    apply (referenceSignEquiv a).symm_apply_eq.mpr
    rfl
  rw [hsign]
  rfl

@[simp] theorem liftCoefficient_negLiftAt (a : LiftableFactorBaseX)
    (y : LiftAt a.1.1) :
    liftCoefficient a (negLiftAt y) = -liftCoefficient a y := by
  rcases liftAt_eq_reference_or_neg_reference a y with h | h
  · subst y
    simp
  · subst y
    simp

/-- The point attached to the lower-residue reference lift. -/
noncomputable def referencePoint (a : LiftableFactorBaseX) : BasePoint :=
  liftPoint a.1.1 (referenceLift a)

theorem liftPoint_eq_liftCoefficient_smul_referencePoint
    (a : LiftableFactorBaseX) (y : LiftAt a.1.1) :
    liftPoint a.1.1 y = liftCoefficient a y • referencePoint a := by
  rcases liftAt_eq_reference_or_neg_reference a y with h | h
  · subst y
    simp [referencePoint]
  · subst y
    simp [referencePoint]

/-- The raw source row.  The sum over labelled slots intentionally aggregates
repeated factor-base coordinates, so an individual coefficient need not be
`+1` or `-1` and may cancel to zero. -/
noncomputable def coefficientVector (x : FactorBaseTuple)
    (L : LiftTuple (sourceCoordinates x)) : Row :=
  ∑ i, Finsupp.single (x i) (liftCoefficient (x i) (L i))

theorem coefficientVector_apply (x : FactorBaseTuple)
    (L : LiftTuple (sourceCoordinates x)) (a : LiftableFactorBaseX) :
    coefficientVector x L a =
      ∑ i, if x i = a then liftCoefficient (x i) (L i) else 0 := by
  classical
  simp [coefficientVector, Finsupp.single_apply]

theorem coefficientVector_globalNegate (x : FactorBaseTuple)
    (L : LiftTuple (sourceCoordinates x)) :
    coefficientVector x (globalNegate L) = -coefficientVector x L := by
  classical
  ext a
  simp only [coefficientVector_apply, globalNegate,
    Finsupp.neg_apply]
  rw [← Finset.sum_neg_distrib]
  apply Finset.sum_congr rfl
  intro i _
  by_cases h : x i = a
  · simp only [h, if_pos]
    exact liftCoefficient_negLiftAt (x i) (L i)
  · simp [h]

/-- Evaluate a coefficient row as an integral linear combination of the
reference factor-base points. -/
noncomputable def evalRow : Row →ₗ[ℤ] BasePoint :=
  Finsupp.linearCombination ℤ referencePoint

theorem evalRow_coefficientVector (x : FactorBaseTuple)
    (L : LiftTuple (sourceCoordinates x)) :
    evalRow (coefficientVector x L) =
      ∑ i, liftTuplePoints L i := by
  classical
  rw [coefficientVector, map_sum]
  simp only [evalRow, Finsupp.linearCombination_single]
  apply Finset.sum_congr rfl
  intro i _
  exact
    (liftPoint_eq_liftCoefficient_smul_referencePoint (x i) (L i)).symm

/-! ## Target normalization and canonical rows -/

/-- The coefficient of the target in `Compatible`: `false` contributes `R`
and `true` contributes `-R`. -/
def targetCoefficient : Bool → ℤ
  | false => 1
  | true => -1

@[simp] theorem targetCoefficient_false : targetCoefficient false = 1 := rfl
@[simp] theorem targetCoefficient_true : targetCoefficient true = -1 := rfl

@[simp] theorem targetCoefficient_not (sign : Bool) :
    targetCoefficient (!sign) = -targetCoefficient sign := by
  cases sign <;> norm_num [targetCoefficient]

theorem signedTarget_eq_targetCoefficient_smul
    (sign : Bool) (R : BasePoint) :
    signedTarget sign R = targetCoefficient sign • R := by
  cases sign <;> simp [signedTarget, targetCoefficient]

/-- Normalize a raw source row so that its evaluation is the supplied target.
If `tau` is the target coefficient in compatibility, this is `(-tau)` times
the raw row. -/
noncomputable def canonicalRow (x : FactorBaseTuple)
    (z : RecoveryData x) : Row :=
  (-targetCoefficient z.2) • coefficientVector x z.1

theorem canonicalRow_globalNegate (x : FactorBaseTuple)
    (L : LiftTuple (sourceCoordinates x)) (sign : Bool) :
    canonicalRow x (globalNegate L, !sign) =
      canonicalRow x (L, sign) := by
  cases sign <;>
    simp [canonicalRow, targetCoefficient,
      coefficientVector_globalNegate]

theorem evalRow_canonicalRow_of_compatible
    (x : FactorBaseTuple) (R : BasePoint) (z : RecoveryData x)
    (hz : Compatible (sourceCoordinates x) R z.1 z.2) :
    evalRow (canonicalRow x z) = R := by
  rcases z with ⟨L, sign⟩
  cases sign with
  | false =>
      change (∑ i, liftTuplePoints L i) + R = 0 at hz
      have hsum : (∑ i, liftTuplePoints L i) = -R :=
        (add_eq_zero_iff_eq_neg).mp hz
      simp [canonicalRow, targetCoefficient,
        evalRow_coefficientVector, hsum]
  | true =>
      change (∑ i, liftTuplePoints L i) + (-R) = 0 at hz
      have hsum0 : (∑ i, liftTuplePoints L i) = -(-R) :=
        (add_eq_zero_iff_eq_neg).mp hz
      have hsum : (∑ i, liftTuplePoints L i) = R := by
        simpa using hsum0
      simp [canonicalRow, targetCoefficient,
        evalRow_coefficientVector, hsum]

theorem evalRow_canonicalRow (x : FactorBaseTuple) (R : BasePoint)
    (w : RecoveryFiber (sourceCoordinates x) R) :
    evalRow (canonicalRow x w.1) = R :=
  evalRow_canonicalRow_of_compatible x R w.1 w.2

theorem canonicalRow_recoveryGlobalNegate
    (x : FactorBaseTuple) (R : BasePoint)
    (w : RecoveryFiber (sourceCoordinates x) R) :
    canonicalRow x (recoveryGlobalNegate w).1 =
      canonicalRow x w.1 := by
  rcases w with ⟨⟨L, sign⟩, hw⟩
  simpa [recoveryGlobalNegate] using
    canonicalRow_globalNegate x L sign

/-! ## Finite row image and exact backpointer partition -/

/-- The duplicate-free image of all compatible labelled recovery data under
`canonicalRow`.  This is a finite mathematical specification, not an efficient
enumeration procedure. -/
noncomputable def canonicalRows (x : FactorBaseTuple) (R : BasePoint) :
    Finset Row := by
  classical
  exact (recoveryFinset (sourceCoordinates x) R).image (canonicalRow x)

/-- Compatible labelled recovery data mapping to one prescribed row. -/
noncomputable def rowBackpointers (x : FactorBaseTuple) (R : BasePoint)
    (row : Row) : Finset (RecoveryData x) := by
  classical
  exact (recoveryFinset (sourceCoordinates x) R).filter
    (fun z ↦ canonicalRow x z = row)

/-- The number of labelled recovery witnesses mapping to a row.  This is not
a rank, independence, or relation-yield measure. -/
noncomputable def rowMultiplicity (x : FactorBaseTuple) (R : BasePoint)
    (row : Row) : ℕ :=
  (rowBackpointers x R row).card

@[simp] theorem mem_rowBackpointers_iff
    {x : FactorBaseTuple} {R : BasePoint} {row : Row}
    {z : RecoveryData x} :
    z ∈ rowBackpointers x R row ↔
      Compatible (sourceCoordinates x) R z.1 z.2 ∧
        canonicalRow x z = row := by
  classical
  simp [rowBackpointers, mem_recoveryFinset_iff]

theorem mem_canonicalRows_iff_backpointers_nonempty
    (x : FactorBaseTuple) (R : BasePoint) (row : Row) :
    row ∈ canonicalRows x R ↔
      (rowBackpointers x R row).Nonempty := by
  classical
  simpa [canonicalRows, rowBackpointers] using
    (Finset.fiber_nonempty_iff_mem_image
      (s := recoveryFinset (sourceCoordinates x) R)
      (f := canonicalRow x) (y := row)).symm

theorem rowMultiplicity_pos_iff_mem_canonicalRows
    (x : FactorBaseTuple) (R : BasePoint) (row : Row) :
    0 < rowMultiplicity x R row ↔ row ∈ canonicalRows x R := by
  rw [rowMultiplicity, Finset.card_pos]
  exact (mem_canonicalRows_iff_backpointers_nonempty x R row).symm

set_option linter.constructorNameAsVariable false in
theorem evalRow_eq_target_of_mem_canonicalRows
    (x : FactorBaseTuple) (R : BasePoint) (row : Row)
    (hrow : row ∈ canonicalRows x R) :
    evalRow row = R := by
  classical
  simp only [canonicalRows, Finset.mem_image,
    mem_recoveryFinset_iff] at hrow
  rcases hrow with ⟨z, hz, hzr⟩
  rw [← hzr]
  exact evalRow_canonicalRow_of_compatible x R z hz

/-- Exact partition of the labelled recovery fiber by canonical row.  Global
sign pairs and any further collisions remain counted as distinct
backpointers. -/
theorem card_recoveryFiber_eq_sum_rowMultiplicity
    (x : FactorBaseTuple) (R : BasePoint) :
    Fintype.card (RecoveryFiber (sourceCoordinates x) R) =
      ∑ row ∈ canonicalRows x R, rowMultiplicity x R row := by
  classical
  rw [← card_recoveryFinset]
  change (recoveryFinset (sourceCoordinates x) R).card =
    ∑ row ∈ (recoveryFinset (sourceCoordinates x) R).image
        (canonicalRow x),
      ((recoveryFinset (sourceCoordinates x) R).filter
        (fun z ↦ canonicalRow x z = row)).card
  exact Finset.card_eq_sum_card_image (canonicalRow x)
    (recoveryFinset (sourceCoordinates x) R)

end

end Ecdlp.M16CanonicalRecoveryRows
