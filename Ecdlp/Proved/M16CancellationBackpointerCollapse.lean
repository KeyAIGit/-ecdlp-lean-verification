import Ecdlp.Proved.M16CanonicalRecoveryRows
import Ecdlp.Proved.M16CancellationRootLowerBound

/-!
# A large explicit M16 backpointer family on one canonical row

Fix a liftable factor-base coordinate `a` and use its lower-residue reference
lift.  The two anchor slots contribute the same reference point `A`, while
seven freely chosen labelled coordinates contribute pairs `B_j, -B_j`.  For
the nonidentity target `R = -(A + A)`, this gives an explicit compatible
base-field recovery witness and hence a liftable reduced root.

Although the labelled roots remember all seven choices, the displayed
recovery witnesses have the same canonical coefficient row:
`Finsupp.single a (-2)`.  This equality is insensitive to repeated pair
coordinates, including the case in which a pair coordinate equals the
anchor.  It therefore gives an injection of `283527^7` labelled choices into
the root-plus-recovery backpointers lying above that one row.

This is an explicit witness-family and output/backpointer-cardinality result
only.  It does not say that every recovery of one of the constructed roots has
this row, that the row or recovery is unique, or that row evaluation is
injective.  The chosen target coordinate and the reference square roots are
noncomputable mathematical conventions.  Nothing here implements `Recover`,
PFPO, `AllRoots`, enumeration, square-root extraction, point decompression,
relation filtering, rank computation, sparse linear algebra, or any runtime,
memory, solver-node, total-cost, scalar-recovery, or ECDLP claim.
-/

namespace Ecdlp.M16CancellationBackpointerCollapse

open scoped BigOperators

open WeierstrassCurve.Affine
open Ecdlp.Curve
open Ecdlp.M16BaseRecoveryFiber
open Ecdlp.M16CanonicalRecoveryRows
open Ecdlp.M16CancellationRootLowerBound
open Ecdlp.M16DirectPointSemantics
open Ecdlp.M16FactorBaseLiftable
open Ecdlp.M16FrobeniusPointSplit
open Ecdlp.M16SolverGate

noncomputable section

abbrev Fp := ZMod Secp256k1.p
abbrev BasePoint := Ecdlp.Curve.secp256k1.toAffine.Point

/-! ## Anchor target and its affine coordinate -/

/-- The point represented by the lower-residue reference lift at `a`. -/
abbrev anchorPoint (a : LiftableFactorBaseX) : BasePoint :=
  referencePoint a

theorem anchorPoint_ne_zero (a : LiftableFactorBaseX) :
    anchorPoint a ≠ 0 :=
  liftPoint_ne_zero a.1.1 (referenceLift a)

/-- The target canceled by two positive anchor slots. -/
def anchorTarget (a : LiftableFactorBaseX) : BasePoint :=
  -(anchorPoint a + anchorPoint a)

theorem anchorTarget_ne_zero (a : LiftableFactorBaseX) :
    anchorTarget a ≠ 0 := by
  intro hzero
  have htwo : (2 : ℕ) • anchorPoint a = 0 := by
    simpa only [anchorTarget, two_nsmul] using neg_eq_zero.mp hzero
  exact anchorPoint_ne_zero a
    (secp256k1_no_nonzero_two_torsion (anchorPoint a) htwo)

private theorem exists_liesOver_include_of_ne_zero
    (R : BasePoint) (hR : R ≠ 0) :
    ∃ X : Fp, LiesOver X (includePoint R) := by
  rcases R with _ | ⟨x, y, h⟩
  · exact (hR rfl).elim
  · refine ⟨x, ?_⟩
    apply (liesOver_iff_barKummer_eq _ _).mpr
    rw [includePoint_some]
    rfl

/-- A mathematically chosen affine coordinate of the nonidentity anchor
target.  This choice is not a recovery or decompression algorithm. -/
noncomputable def anchorX (a : LiftableFactorBaseX) : Fp :=
  Classical.choose
    (exists_liesOver_include_of_ne_zero
      (anchorTarget a) (anchorTarget_ne_zero a))

theorem anchorTarget_liesOver (a : LiftableFactorBaseX) :
    LiesOver (anchorX a) (includePoint (anchorTarget a)) :=
  Classical.choose_spec
    (exists_liesOver_include_of_ne_zero
      (anchorTarget a) (anchorTarget_ne_zero a))

/-! ## The explicit labelled cancellation witness -/

/-- The first two source slots are the anchor.  Each of the seven freely
chosen coordinates then occupies one fixed labelled pair. -/
def cancellationTuple (a : LiftableFactorBaseX)
    (B : Fin 7 → LiftableFactorBaseX) : FactorBaseTuple :=
  ![a, a,
    B 0, B 0, B 1, B 1, B 2, B 2, B 3, B 3,
    B 4, B 4, B 5, B 5, B 6, B 6]

/-- The displayed lifts: two positive anchor references followed by seven
reference/negative-reference pairs. -/
def cancellationSigns : Fin 16 → Bool :=
  ![false, false,
    false, true, false, true, false, true, false, true,
    false, true, false, true, false, true]

noncomputable def cancellationLiftTuple (a : LiftableFactorBaseX)
    (B : Fin 7 → LiftableFactorBaseX) :
    LiftTuple (sourceCoordinates (cancellationTuple a B)) :=
  fun i ↦ if cancellationSigns i then
    negLiftAt (referenceLift (cancellationTuple a B i))
  else
    referenceLift (cancellationTuple a B i)

private theorem liftCoefficient_cancellationLiftTuple
    (a : LiftableFactorBaseX) (B : Fin 7 → LiftableFactorBaseX)
    (i : Fin 16) :
    liftCoefficient (cancellationTuple a B i)
        (cancellationLiftTuple a B i) =
      if cancellationSigns i then -1 else 1 := by
  by_cases hsign : cancellationSigns i = true
  · simp only [cancellationLiftTuple, hsign, if_pos]
    exact liftCoefficient_neg_referenceLift (cancellationTuple a B i)
  · simp only [cancellationLiftTuple, hsign]
    exact liftCoefficient_referenceLift (cancellationTuple a B i)

/-- All cancellation pairs disappear from the raw coefficient row.  The
proof does not assume that the `B j` are distinct or different from `a`. -/
theorem coefficientVector_cancellationLiftTuple
    (a : LiftableFactorBaseX) (B : Fin 7 → LiftableFactorBaseX) :
    coefficientVector (cancellationTuple a B)
        (cancellationLiftTuple a B) =
      Finsupp.single a 2 := by
  classical
  rw [coefficientVector]
  simp_rw [liftCoefficient_cancellationLiftTuple]
  rw [show (2 : ℤ) = 1 + 1 by norm_num, Finsupp.single_add]
  simp [cancellationTuple, cancellationSigns, Fin.sum_univ_succ]

private theorem sum_liftTuplePoints_cancellation
    (a : LiftableFactorBaseX) (B : Fin 7 → LiftableFactorBaseX) :
    (∑ i, liftTuplePoints (cancellationLiftTuple a B) i) =
      anchorPoint a + anchorPoint a := by
  simp [liftTuplePoints, cancellationLiftTuple, anchorPoint,
    cancellationSigns, cancellationTuple, sourceCoordinates,
    referencePoint, Fin.sum_univ_succ]

theorem cancellationCompatible (a : LiftableFactorBaseX)
    (B : Fin 7 → LiftableFactorBaseX) :
    Compatible (sourceCoordinates (cancellationTuple a B))
      (anchorTarget a) (cancellationLiftTuple a B) false := by
  change (∑ i, liftTuplePoints (cancellationLiftTuple a B) i) +
      anchorTarget a = 0
  rw [sum_liftTuplePoints_cancellation]
  simp [anchorTarget]

/-- The explicitly displayed labelled recovery witness. -/
noncomputable def cancellationRecovery (a : LiftableFactorBaseX)
    (B : Fin 7 → LiftableFactorBaseX) :
    RecoveryFiber (sourceCoordinates (cancellationTuple a B))
      (anchorTarget a) :=
  ⟨(cancellationLiftTuple a B, false), cancellationCompatible a B⟩

/-- The same witness, viewed as a liftable reduced root above the chosen
target coordinate. -/
noncomputable def cancellationRoot (a : LiftableFactorBaseX)
    (B : Fin 7 → LiftableFactorBaseX) :
    LiftableReducedRoot (anchorX a) :=
  ⟨cancellationTuple a B,
    S17At_eq_zero_of_recoveryFiber
      (anchorTarget_liesOver a) (cancellationRecovery a B)⟩

/-! ## Root-plus-recovery backpointers -/

/-- A liftable reduced root together with one compatible labelled recovery
backpointer for its exact source tuple. -/
abbrev RootWithRecovery (a : LiftableFactorBaseX) :=
  Σ root : LiftableReducedRoot (anchorX a),
    RecoveryFiber (sourceCoordinates root.1) (anchorTarget a)

/-- The canonical row attached to the retained recovery backpointer. -/
noncomputable def backpointerRow (a : LiftableFactorBaseX)
    (w : RootWithRecovery a) : Row :=
  canonicalRow w.1.1 w.2.1

/-- Package the displayed root and the displayed recovery together. -/
noncomputable def cancellationRootWithRecovery
    (a : LiftableFactorBaseX) (B : Fin 7 → LiftableFactorBaseX) :
    RootWithRecovery a :=
  ⟨cancellationRoot a B, cancellationRecovery a B⟩

private theorem cancellationTuple_injective (a : LiftableFactorBaseX) :
    Function.Injective (cancellationTuple a) := by
  intro B C h
  funext j
  fin_cases j
  · simpa [cancellationTuple] using congrFun h (2 : Fin 16)
  · simpa [cancellationTuple] using congrFun h (4 : Fin 16)
  · simpa [cancellationTuple] using congrFun h (6 : Fin 16)
  · simpa [cancellationTuple] using congrFun h (8 : Fin 16)
  · simpa [cancellationTuple] using congrFun h (10 : Fin 16)
  · simpa [cancellationTuple] using congrFun h (12 : Fin 16)
  · simpa [cancellationTuple] using congrFun h (14 : Fin 16)

theorem cancellationRootWithRecovery_injective
    (a : LiftableFactorBaseX) :
    Function.Injective (cancellationRootWithRecovery a) := by
  intro B C h
  apply cancellationTuple_injective a
  exact congrArg (fun w : RootWithRecovery a ↦ w.1.1) h

/-- Every displayed backpointer has exactly the same normalized row.  Pair
terms cancel before aggregation, so this remains true when pair coordinates
repeat, are permuted, or equal the anchor. -/
theorem canonicalRow_cancellationRecovery
    (a : LiftableFactorBaseX) (B : Fin 7 → LiftableFactorBaseX) :
    canonicalRow (cancellationTuple a B) (cancellationRecovery a B).1 =
      Finsupp.single a (-2) := by
  classical
  change (-targetCoefficient false) •
      coefficientVector (cancellationTuple a B)
        (cancellationLiftTuple a B) = Finsupp.single a (-2)
  rw [coefficientVector_cancellationLiftTuple]
  ext c
  by_cases h : a = c <;>
    simp [targetCoefficient, h]

theorem backpointerRow_cancellationRootWithRecovery
    (a : LiftableFactorBaseX) (B : Fin 7 → LiftableFactorBaseX) :
    backpointerRow a (cancellationRootWithRecovery a B) =
      Finsupp.single a (-2) := by
  exact canonicalRow_cancellationRecovery a B

/-! ## One constant-row preimage and its exact labelled lower bound -/

/-- Root-plus-recovery backpointers whose retained recovery has the displayed
constant row.  This is a subtype fiber, not a claim that all recoveries of any
root lie in it. -/
def ConstantRowPreimage (a : LiftableFactorBaseX) :=
  {w : RootWithRecovery a //
    backpointerRow a w = Finsupp.single a (-2)}

noncomputable instance rootWithRecoveryFintype
    (a : LiftableFactorBaseX) : Fintype (RootWithRecovery a) := by
  classical
  exact Fintype.ofFinite _

noncomputable instance constantRowPreimageFintype
    (a : LiftableFactorBaseX) : Fintype (ConstantRowPreimage a) := by
  classical
  exact Subtype.fintype _

/-- The seven labelled factor-base choices land in the constant-row
preimage. -/
noncomputable def constantRowFamily (a : LiftableFactorBaseX) :
    (Fin 7 → LiftableFactorBaseX) → ConstantRowPreimage a :=
  fun B ↦ ⟨cancellationRootWithRecovery a B,
    backpointerRow_cancellationRootWithRecovery a B⟩

theorem constantRowFamily_injective (a : LiftableFactorBaseX) :
    Function.Injective (constantRowFamily a) := by
  intro B C h
  apply cancellationRootWithRecovery_injective a
  exact congrArg Subtype.val h

/-- At least `283527^7` distinct labelled root-plus-recovery backpointers have
the single row `-2[a]`.  This is a cardinality statement about explicitly
constructed outputs, not an enumeration or work lower bound. -/
theorem card_constantRowPreimage_lower_bound
    (a : LiftableFactorBaseX) :
    283527 ^ 7 ≤ Fintype.card (ConstantRowPreimage a) := by
  calc
    283527 ^ 7 =
        Fintype.card (Fin 7 → LiftableFactorBaseX) := by
      rw [Fintype.card_fun, Fintype.card_fin,
        card_liftableFactorBaseX]
    _ ≤ Fintype.card (ConstantRowPreimage a) :=
      Fintype.card_le_of_injective (constantRowFamily a)
        (constantRowFamily_injective a)

/-- The existing optimistic desk ceiling is numerically below this explicit
constant-row backpointer family.  No PFPO, node-charge, runtime, memory, or
total-cost interpretation follows. -/
theorem maxRelationTermBudget_lt_constantRowPreimage_card
    (a : LiftableFactorBaseX) :
    maxRelationTermBudget < Fintype.card (ConstantRowPreimage a) :=
  maxRelationTermBudget_lt_liftable_cancellation_family.trans_le
    (card_constantRowPreimage_lower_bound a)

end

end Ecdlp.M16CancellationBackpointerCollapse
