import Ecdlp.Proved.M16CancellationBackpointerCollapse
import Ecdlp.Proved.M16FiniteGLVRelationRank

/-!
# Rank one for the explicit M16 cancellation family

This module feeds the seven-parameter cancellation backpointer family into the
finite GLV relation-rank accounting package.  The labels remain distinct
certified recoveries, but every coefficient row is the same nonzero
GLV-compressed row and every augmented row is consequently the same nonzero
homogeneous relation.  Thus both matrix ranks are exactly one, while both
labelled synthesis kernels have dimension `283527^7 - 1`.

The result applies only to the explicit cancellation family constructed in
`M16CancellationBackpointerCollapse`.  It does not enumerate other roots or
recoveries, prove `AllRoots` completeness, model PFPO work, establish a
relation yield or an achieved rank for any algorithm, run sparse linear
algebra, define a minimum encoding, charge time or memory, recover a scalar,
or give an ECDLP shortcut.
-/

namespace Ecdlp.M16CancellationRelationRank

open Ecdlp.Curve
open Ecdlp.M16CancellationBackpointerCollapse
open Ecdlp.M16FactorBaseLiftable
open Ecdlp.M16FiniteGLVRelationRank
open Ecdlp.M16GLVCanonicalRows

noncomputable section

abbrev K := ZMod Secp256k1.n
abbrev Rep := LiftableGLVOrbitRep

/-! ## The labelled sample and its constant rows -/

/-- The seven freely selected labelled factor-base coordinates. -/
abbrev CancellationLabel := Fin 7 → LiftableFactorBaseX

/-- The displayed cancellation recovery, packaged as a certified recovery for
the fixed anchor target. -/
noncomputable def cancellationRankSample (a : LiftableFactorBaseX) :
    CancellationLabel → CertifiedRecovery (anchorTarget a) :=
  fun B ↦ ⟨cancellationTuple a B, cancellationRecovery a B⟩

/-- Distinct labels remain distinct certified recovery observations. -/
theorem cancellationRankSample_injective (a : LiftableFactorBaseX) :
    Function.Injective (cancellationRankSample a) := by
  intro B C h
  have htuple : cancellationTuple a B = cancellationTuple a C := by
    simpa [cancellationRankSample] using
      congrArg
        (fun w : CertifiedRecovery (anchorTarget a) ↦ w.1) h
  funext j
  fin_cases j
  · simpa [cancellationTuple] using congrFun htuple (2 : Fin 16)
  · simpa [cancellationTuple] using congrFun htuple (4 : Fin 16)
  · simpa [cancellationTuple] using congrFun htuple (6 : Fin 16)
  · simpa [cancellationTuple] using congrFun htuple (8 : Fin 16)
  · simpa [cancellationTuple] using congrFun htuple (10 : Fin 16)
  · simpa [cancellationTuple] using congrFun htuple (12 : Fin 16)
  · simpa [cancellationTuple] using congrFun htuple (14 : Fin 16)

/-- The common GLV-compressed mod-`n` coefficient row. -/
noncomputable def cancellationRowModN
    (a : LiftableFactorBaseX) : GLVRowModN :=
  glvCompressModN (reduceModN (Finsupp.single a (-2)))

/-- Every displayed cancellation recovery compresses to the same mod-`n`
row. -/
theorem certifiedRowModN_cancellationRankSample
    (a : LiftableFactorBaseX) (B : CancellationLabel) :
    certifiedRowModN (cancellationRankSample a B) =
      cancellationRowModN a := by
  simp [certifiedRowModN, cancellationRankSample, cancellationRowModN,
    canonicalGLVRowModN, canonicalRow_cancellationRecovery]

/-- The common compressed row is nonzero because it evaluates to the nonzero
anchor target.  No separate unit calculation for `lambda` is needed. -/
theorem cancellationRowModN_ne_zero (a : LiftableFactorBaseX) :
    cancellationRowModN a ≠ 0 := by
  have h := certifiedRowModN_ne_zero (anchorTarget_ne_zero a)
    (cancellationRankSample a (fun _ ↦ a))
  rwa [certifiedRowModN_cancellationRankSample] at h

/-- The common coefficient row in the matrix's function-space presentation. -/
noncomputable def cancellationCoefficientRow
    (a : LiftableFactorBaseX) : Rep → K :=
  fun i ↦ cancellationRowModN a i

/-- The common augmented row, including target coefficient `-1`. -/
noncomputable def cancellationAugmentedRow
    (a : LiftableFactorBaseX) : Option Rep → K
  | none => -1
  | some i => cancellationRowModN a i

theorem cancellationCoefficientRow_ne_zero (a : LiftableFactorBaseX) :
    cancellationCoefficientRow a ≠ 0 := by
  intro hzero
  apply cancellationRowModN_ne_zero a
  ext i
  have hi := congrFun hzero i
  simpa [cancellationCoefficientRow] using hi

theorem cancellationAugmentedRow_ne_zero (a : LiftableFactorBaseX) :
    cancellationAugmentedRow a ≠ 0 := by
  intro hzero
  apply cancellationCoefficientRow_ne_zero a
  funext i
  have hi := congrFun hzero (some i)
  simpa [cancellationCoefficientRow, cancellationAugmentedRow] using hi

theorem coefficientMatrix_row_cancellationRankSample
    (a : LiftableFactorBaseX) (B : CancellationLabel) :
    (coefficientMatrix (cancellationRankSample a)).row B =
      cancellationCoefficientRow a := by
  funext i
  change certifiedRowModN (cancellationRankSample a B) i =
    cancellationRowModN a i
  rw [certifiedRowModN_cancellationRankSample]

theorem augmentedMatrix_row_cancellationRankSample
    (a : LiftableFactorBaseX) (B : CancellationLabel) :
    (augmentedMatrix (cancellationRankSample a)).row B =
      cancellationAugmentedRow a := by
  funext i
  cases i with
  | none => rfl
  | some i =>
      change certifiedRowModN (cancellationRankSample a B) i =
        cancellationRowModN a i
      rw [certifiedRowModN_cancellationRankSample]

/-! ## Singleton row ranges and exact rank -/

theorem range_coefficientMatrix_row_cancellationRankSample
    (a : LiftableFactorBaseX) :
    Set.range (coefficientMatrix (cancellationRankSample a)).row =
      {cancellationCoefficientRow a} := by
  ext row
  constructor
  · rintro ⟨B, rfl⟩
    exact Set.mem_singleton_iff.mpr
      (coefficientMatrix_row_cancellationRankSample a B)
  · intro hrow
    have hrow' : row = cancellationCoefficientRow a :=
      Set.mem_singleton_iff.mp hrow
    subst row
    exact ⟨fun _ ↦ a, coefficientMatrix_row_cancellationRankSample a _⟩

theorem range_augmentedMatrix_row_cancellationRankSample
    (a : LiftableFactorBaseX) :
    Set.range (augmentedMatrix (cancellationRankSample a)).row =
      {cancellationAugmentedRow a} := by
  ext row
  constructor
  · rintro ⟨B, rfl⟩
    exact Set.mem_singleton_iff.mpr
      (augmentedMatrix_row_cancellationRankSample a B)
  · intro hrow
    have hrow' : row = cancellationAugmentedRow a :=
      Set.mem_singleton_iff.mp hrow
    subst row
    exact ⟨fun _ ↦ a, augmentedMatrix_row_cancellationRankSample a _⟩

/-- The coefficient system has rank one: all labelled observations span one
nonzero compressed row. -/
theorem coefficientRank_cancellationRankSample
    (a : LiftableFactorBaseX) :
    coefficientRank (cancellationRankSample a) = 1 := by
  rw [coefficientRank, range_coefficientSynthesis,
    range_coefficientMatrix_row_cancellationRankSample]
  exact finrank_span_singleton (cancellationCoefficientRow_ne_zero a)

/-- The augmented homogeneous system also has rank one. -/
theorem augmentedRank_cancellationRankSample
    (a : LiftableFactorBaseX) :
    augmentedRank (cancellationRankSample a) = 1 := by
  rw [augmentedRank, range_augmentedSynthesis,
    range_augmentedMatrix_row_cancellationRankSample]
  exact finrank_span_singleton (cancellationAugmentedRow_ne_zero a)

theorem coefficientMatrix_rank_cancellationRankSample
    (a : LiftableFactorBaseX) :
    (coefficientMatrix (cancellationRankSample a)).rank = 1 := by
  rw [coefficientMatrix_rank_eq_coefficientRank,
    coefficientRank_cancellationRankSample]

theorem augmentedMatrix_rank_cancellationRankSample
    (a : LiftableFactorBaseX) :
    (augmentedMatrix (cancellationRankSample a)).rank = 1 := by
  rw [augmentedMatrix_rank_eq_augmentedRank,
    augmentedRank_cancellationRankSample]

/-! ## Label count and exact dependency dimensions -/

theorem card_cancellationLabel :
    Fintype.card CancellationLabel = 283527 ^ 7 := by
  rw [Fintype.card_fun, Fintype.card_fin, card_liftableFactorBaseX]

/-- All but one dimension of the labelled coefficient observations lies in
the synthesis kernel. -/
theorem finrank_ker_coefficientSynthesis_cancellationRankSample
    (a : LiftableFactorBaseX) :
    Module.finrank K
        (LinearMap.ker (coefficientSynthesis (cancellationRankSample a))) =
      283527 ^ 7 - 1 := by
  have h := coefficientRank_add_finrank_ker
    (cancellationRankSample a)
  rw [coefficientRank_cancellationRankSample,
    card_cancellationLabel] at h
  exact Nat.eq_sub_of_add_eq' h

/-- The augmented observations have the same exact dependency dimension. -/
theorem finrank_ker_augmentedSynthesis_cancellationRankSample
    (a : LiftableFactorBaseX) :
    Module.finrank K
        (LinearMap.ker (augmentedSynthesis (cancellationRankSample a))) =
      283527 ^ 7 - 1 := by
  have h := augmentedRank_add_finrank_ker
    (cancellationRankSample a)
  rw [augmentedRank_cancellationRankSample,
    card_cancellationLabel] at h
  exact Nat.eq_sub_of_add_eq' h

end

end Ecdlp.M16CancellationRelationRank
