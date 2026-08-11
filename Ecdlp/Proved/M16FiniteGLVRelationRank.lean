import Mathlib.LinearAlgebra.Matrix.Rank
import Ecdlp.Proved.M16GLVCanonicalRows
import Ecdlp.Proved.ProtocolInstantiation

/-!
# Finite GLV relation matrices and honest rank accounting

This module turns exact, GLV-compressed M16 recovery witnesses into finite
labelled relation matrices over `ZMod n`.  A labelled sample is a function from
a finite type `ι`; equal recovered rows at different labels remain distinct
observations.  The associated synthesis maps identify matrix rank with the
dimension of the span of the sampled rows, and rank-nullity records the linear
dependencies among the labels.

Two ranks are kept deliberately separate:

* the **coefficient rank** uses the `94509` GLV factor-base columns and treats
  the fixed target as the right-hand side;
* the **augmented rank** adds one target column, with coefficient `-1`, and
  treats each observation as a homogeneous relation.

The coefficient matrix is a submatrix of the augmented matrix, while the
extra target column can increase rank by at most one.  Deduplicating sampled
rows gives only an upper bound on rank; no independence follows from
distinctness.

This is a structural accounting package.  It does not construct or enumerate
recovery witnesses, implement root finding or a minimum-encoding convention,
prove `AllRoots` completeness, charge PFPO work, establish an achieved rank or
relation yield, run sparse linear algebra, or provide runtime, memory, cost,
discrete-log, or ECDLP-shortcut claims.
-/

namespace Ecdlp.M16FiniteGLVRelationRank

open Ecdlp.Curve
open Ecdlp.M16BaseRecoveryFiber
open Ecdlp.M16CanonicalRecoveryRows
open Ecdlp.M16FactorBaseLiftable
open Ecdlp.M16GLVCanonicalRows

noncomputable section

abbrev K := ZMod Secp256k1.n
abbrev BasePoint := Ecdlp.Curve.secp256k1.toAffine.Point
abbrev PointN := ↥Ecdlp.Curve.secp256k1Grp
abbrev Rep := LiftableGLVOrbitRep

/-! ## Evaluation modulo the group order -/

/-- A curve point, viewed in the concrete prime-order subgroup.  Membership in
`⟨G⟩` is supplied by the full-group theorem. -/
noncomputable def asPointN (P : BasePoint) : PointN :=
  ⟨P, secp256k1_mem_zmultiples P⟩

@[simp] theorem coe_asPointN (P : BasePoint) :
    (asPointN P : BasePoint) = P :=
  rfl

/-- The phase-zero GLV representative as an element of the concrete
prime-order subgroup. -/
noncomputable def glvRepresentativePointN (i : Rep) : PointN :=
  asPointN (glvRepresentativePoint i)

@[simp] theorem coe_glvRepresentativePointN (i : Rep) :
    (glvRepresentativePointN i : BasePoint) = glvRepresentativePoint i :=
  rfl

/-- Evaluate a GLV-compressed coefficient row over the prime-order scalar
field in the concrete secp256k1 subgroup. -/
noncomputable def evalGLVRowModN : GLVRowModN →ₗ[K] PointN :=
  Finsupp.linearCombination K glvRepresentativePointN

/-- Reducing an integral GLV row modulo `n` preserves its exact curve-point
evaluation.  The equality is stated after coercing the subgroup result to the
ambient affine-point group. -/
theorem coe_evalGLVRowModN_reduceModN (row : GLVRow) :
    ((evalGLVRowModN (reduceModN row) : PointN) : BasePoint) =
      evalGLVRow row := by
  classical
  induction row using Finsupp.induction_linear with
  | zero => simp [evalGLVRowModN, evalGLVRow]
  | add f g hf hg =>
      simp only [map_add, AddSubgroup.coe_add, hf, hg]
  | single i c =>
      have hreduce :
          reduceModN (Finsupp.single i c) =
            Finsupp.single i (c : K) := by
        ext j
        by_cases hij : i = j <;>
          simp [reduceModN_apply, hij]
      rw [hreduce]
      simp only [evalGLVRowModN, evalGLVRow,
        Finsupp.linearCombination_single]
      change (((c : K) • glvRepresentativePointN i : PointN) : BasePoint) =
        c • glvRepresentativePoint i
      rw [Int.cast_smul_eq_zsmul, AddSubgroup.coe_zsmul]
      rfl

/-! ## Certified recovery rows -/

/-- One factor-base tuple together with an exact recovery-fiber witness for
the fixed target `R`. -/
abbrev CertifiedRecovery (R : BasePoint) :=
  Σ x : FactorBaseTuple, RecoveryFiber (sourceCoordinates x) R

/-- The integral GLV-compressed row carried by a certified recovery. -/
noncomputable def certifiedRowZ {R : BasePoint}
    (w : CertifiedRecovery R) : GLVRow :=
  canonicalGLVRow w.1 w.2.1

/-- The mod-`n` GLV-compressed row carried by a certified recovery. -/
noncomputable def certifiedRowModN {R : BasePoint}
    (w : CertifiedRecovery R) : GLVRowModN :=
  canonicalGLVRowModN w.1 w.2.1

/-- The certified mod-`n` row is coefficientwise reduction of the certified
integral row. -/
theorem certifiedRowModN_eq_reduceModN {R : BasePoint}
    (w : CertifiedRecovery R) :
    certifiedRowModN w = reduceModN (certifiedRowZ w) := by
  simpa [certifiedRowModN, certifiedRowZ, canonicalGLVRowModN,
    canonicalGLVRow] using
      glvCompressModN_reduceModN (canonicalRow w.1 w.2.1)

/-- Integral certified rows evaluate exactly to their fixed target. -/
theorem evalGLVRow_certifiedRowZ {R : BasePoint}
    (w : CertifiedRecovery R) :
    evalGLVRow (certifiedRowZ w) = R := by
  exact evalGLVRow_canonicalGLVRow w.1 R w.2

/-- Mod-`n` certified rows evaluate exactly to their fixed target in the
concrete prime-order subgroup. -/
theorem evalGLVRowModN_certifiedRowModN {R : BasePoint}
    (w : CertifiedRecovery R) :
    evalGLVRowModN (certifiedRowModN w) = asPointN R := by
  apply Subtype.ext
  rw [certifiedRowModN_eq_reduceModN,
    coe_evalGLVRowModN_reduceModN]
  exact evalGLVRow_certifiedRowZ w

/-- A certified integral row for a nonzero target cannot be the zero row. -/
theorem certifiedRowZ_ne_zero {R : BasePoint} (hR : R ≠ 0)
    (w : CertifiedRecovery R) : certifiedRowZ w ≠ 0 := by
  intro hrow
  apply hR
  rw [← evalGLVRow_certifiedRowZ w, hrow, map_zero]

/-- A certified mod-`n` row for a nonzero target cannot be the zero row. -/
theorem certifiedRowModN_ne_zero {R : BasePoint} (hR : R ≠ 0)
    (w : CertifiedRecovery R) : certifiedRowModN w ≠ 0 := by
  intro hrow
  have hzero : asPointN R = 0 := by
    rw [← evalGLVRowModN_certifiedRowModN w, hrow, map_zero]
  apply hR
  simpa [asPointN] using
    congrArg (fun P : PointN ↦ (P : BasePoint)) hzero

/-- With target coefficient `-1`, every certified row is an exact homogeneous
relation in the concrete prime-order subgroup. -/
theorem certifiedRelation_closes {R : BasePoint}
    (w : CertifiedRecovery R) :
    evalGLVRowModN (certifiedRowModN w) +
      (-1 : K) • asPointN R = 0 := by
  rw [evalGLVRowModN_certifiedRowModN]
  simp

/-! ## Labelled finite samples and their matrices -/

/-- A coefficient row as a vector in the `94509`-column function space. -/
noncomputable def coefficientRow {R : BasePoint}
    (w : CertifiedRecovery R) : Rep → K :=
  fun i ↦ certifiedRowModN w i

/-- An augmented row.  `none` is the fixed target column and every `some i`
is a GLV factor-base coefficient column. -/
noncomputable def augmentedRow {R : BasePoint}
    (w : CertifiedRecovery R) : Option Rep → K
  | none => -1
  | some i => certifiedRowModN w i

@[simp] theorem augmentedRow_none {R : BasePoint}
    (w : CertifiedRecovery R) : augmentedRow w none = -1 :=
  rfl

@[simp] theorem augmentedRow_some {R : BasePoint}
    (w : CertifiedRecovery R) (i : Rep) :
    augmentedRow w (some i) = coefficientRow w i :=
  rfl

/-- The coefficient matrix of a finite labelled sample.  Equal rows at
different labels are intentionally retained. -/
noncomputable def coefficientMatrix {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) : Matrix ι Rep K :=
  fun k i ↦ coefficientRow (sample k) i

/-- The augmented homogeneous relation matrix, with target column `-1`. -/
noncomputable def augmentedMatrix {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) : Matrix ι (Option Rep) K :=
  fun k i ↦ augmentedRow (sample k) i

@[simp] theorem coefficientMatrix_apply {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) (k : ι) (i : Rep) :
    coefficientMatrix sample k i = certifiedRowModN (sample k) i :=
  rfl

@[simp] theorem augmentedMatrix_none {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) (k : ι) :
    augmentedMatrix sample k none = -1 :=
  rfl

@[simp] theorem augmentedMatrix_some {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) (k : ι) (i : Rep) :
    augmentedMatrix sample k (some i) = coefficientMatrix sample k i :=
  rfl

/-- Every labelled augmented matrix row is an exact homogeneous relation for
the fixed target. -/
theorem augmentedMatrix_row_closes {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) (k : ι) :
    evalGLVRowModN (certifiedRowModN (sample k)) +
      augmentedMatrix sample k none • asPointN R = 0 := by
  simpa using certifiedRelation_closes (sample k)

/-! ## Synthesis maps, spans, and rank-nullity -/

/-- Synthesis of linear combinations of the labelled coefficient rows. -/
noncomputable def coefficientSynthesis {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) :
    (ι →₀ K) →ₗ[K] (Rep → K) :=
  Finsupp.linearCombination K (coefficientMatrix sample).row

/-- Synthesis of linear combinations of the labelled augmented rows. -/
noncomputable def augmentedSynthesis {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) :
    (ι →₀ K) →ₗ[K] (Option Rep → K) :=
  Finsupp.linearCombination K (augmentedMatrix sample).row

theorem range_coefficientSynthesis {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) :
    LinearMap.range (coefficientSynthesis sample) =
      Submodule.span K (Set.range (coefficientMatrix sample).row) := by
  simpa [coefficientSynthesis] using
    (Finsupp.range_linearCombination
      (R := K) (v := (coefficientMatrix sample).row))

theorem range_augmentedSynthesis {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) :
    LinearMap.range (augmentedSynthesis sample) =
      Submodule.span K (Set.range (augmentedMatrix sample).row) := by
  simpa [augmentedSynthesis] using
    (Finsupp.range_linearCombination
      (R := K) (v := (augmentedMatrix sample).row))

/-- Dimension of the span of the sampled coefficient rows. -/
noncomputable def coefficientRank {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) : ℕ :=
  Module.finrank K (LinearMap.range (coefficientSynthesis sample))

/-- Dimension of the span of the sampled augmented rows. -/
noncomputable def augmentedRank {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) : ℕ :=
  Module.finrank K (LinearMap.range (augmentedSynthesis sample))

/-- Rank-nullity for the labelled coefficient-row synthesis map. -/
theorem coefficientRank_add_finrank_ker {R : BasePoint} {ι : Type*}
    [Fintype ι] (sample : ι → CertifiedRecovery R) :
    coefficientRank sample +
        Module.finrank K (LinearMap.ker (coefficientSynthesis sample)) =
      Fintype.card ι := by
  simpa [coefficientRank] using
    LinearMap.finrank_range_add_finrank_ker
      (coefficientSynthesis sample)

/-- Rank-nullity for the labelled augmented-row synthesis map. -/
theorem augmentedRank_add_finrank_ker {R : BasePoint} {ι : Type*}
    [Fintype ι] (sample : ι → CertifiedRecovery R) :
    augmentedRank sample +
        Module.finrank K (LinearMap.ker (augmentedSynthesis sample)) =
      Fintype.card ι := by
  simpa [augmentedRank] using
    LinearMap.finrank_range_add_finrank_ker
      (augmentedSynthesis sample)

/-! ## Equality with matrix rank -/

theorem coefficientMatrix_rank_eq_finrank_span_rows
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    (coefficientMatrix sample).rank =
      Module.finrank K
        (Submodule.span K (Set.range (coefficientMatrix sample).row)) :=
  Matrix.rank_eq_finrank_span_row _

theorem augmentedMatrix_rank_eq_finrank_span_rows
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    (augmentedMatrix sample).rank =
      Module.finrank K
        (Submodule.span K (Set.range (augmentedMatrix sample).row)) :=
  Matrix.rank_eq_finrank_span_row _

/-- The abstract coefficient-row span dimension is exactly matrix rank. -/
theorem coefficientMatrix_rank_eq_coefficientRank
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    (coefficientMatrix sample).rank = coefficientRank sample := by
  rw [coefficientMatrix_rank_eq_finrank_span_rows,
    ← range_coefficientSynthesis]
  rfl

/-- The abstract augmented-row span dimension is exactly matrix rank. -/
theorem augmentedMatrix_rank_eq_augmentedRank
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    (augmentedMatrix sample).rank = augmentedRank sample := by
  rw [augmentedMatrix_rank_eq_finrank_span_rows,
    ← range_augmentedSynthesis]
  rfl

/-! ## Coefficient rank versus augmented rank -/

/-- The coefficient matrix is the submatrix obtained by retaining the
`some` factor-base columns of the augmented matrix. -/
theorem coefficientMatrix_eq_augmented_submatrix
    {R : BasePoint} {ι : Type*} (sample : ι → CertifiedRecovery R) :
    coefficientMatrix sample =
      (augmentedMatrix sample).submatrix id Option.some := by
  rfl

/-- Adding the fixed target column cannot lower rank. -/
theorem coefficientRank_le_augmentedRank
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    coefficientRank sample ≤ augmentedRank sample := by
  rw [← coefficientMatrix_rank_eq_coefficientRank,
    ← augmentedMatrix_rank_eq_augmentedRank,
    coefficientMatrix_eq_augmented_submatrix]
  exact Matrix.rank_submatrix_le (augmentedMatrix sample) id Option.some

/-- The constant `-1` target column in the labelled row space. -/
def targetColumn {ι : Type*} : ι → K :=
  fun _ ↦ -1

/-- The augmented column family is exactly the coefficient column family
plus the singleton target column. -/
theorem range_augmentedMatrix_col {R : BasePoint} {ι : Type*}
    (sample : ι → CertifiedRecovery R) :
    Set.range (augmentedMatrix sample).col =
      Set.range (coefficientMatrix sample).col ∪
        {targetColumn (ι := ι)} := by
  ext v
  constructor
  · rintro ⟨j, rfl⟩
    cases j with
    | none => exact Or.inr rfl
    | some j => exact Or.inl ⟨j, rfl⟩
  · rintro (hv | hv)
    · rcases hv with ⟨j, rfl⟩
      exact ⟨some j, rfl⟩
    · have hv' : v = targetColumn (ι := ι) :=
        Set.mem_singleton_iff.mp hv
      subst v
      exact ⟨none, rfl⟩

/-- One target column can increase rank by at most one. -/
theorem augmentedRank_le_coefficientRank_add_one
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    augmentedRank sample ≤ coefficientRank sample + 1 := by
  rw [← augmentedMatrix_rank_eq_augmentedRank,
    ← coefficientMatrix_rank_eq_coefficientRank,
    Matrix.rank_eq_finrank_span_cols,
    Matrix.rank_eq_finrank_span_cols,
    range_augmentedMatrix_col,
    Submodule.span_union]
  have htarget :
      Module.finrank K
          (Submodule.span K ({targetColumn (ι := ι)} : Set (ι → K))) ≤ 1 := by
    calc
      Module.finrank K
          (Submodule.span K ({targetColumn (ι := ι)} : Set (ι → K))) ≤
          Finset.card {targetColumn (ι := ι)} :=
        finrank_span_le_card
          ({targetColumn (ι := ι)} : Set (ι → K))
      _ = 1 := Finset.card_singleton _
  exact (Submodule.finrank_add_le_finrank_add_finrank
      (Submodule.span K (Set.range (coefficientMatrix sample).col))
      (Submodule.span K ({targetColumn (ι := ι)} : Set (ι → K)))).trans
    (Nat.add_le_add_left htarget _)

/-! ## Deduplicated row sets give upper bounds only -/

/-- The finite set of distinct coefficient rows occurring in the labelled
sample.  It forgets labels and multiplicities. -/
noncomputable def distinctCoefficientRows
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) : Finset (Rep → K) := by
  classical
  exact Finset.univ.image (coefficientMatrix sample).row

/-- The finite set of distinct augmented rows occurring in the labelled
sample.  It forgets labels and multiplicities. -/
noncomputable def distinctAugmentedRows
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) : Finset (Option Rep → K) := by
  classical
  exact Finset.univ.image (augmentedMatrix sample).row

theorem coe_distinctCoefficientRows
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    (↑(distinctCoefficientRows sample) : Set (Rep → K)) =
      Set.range (coefficientMatrix sample).row := by
  classical
  ext row
  simp [distinctCoefficientRows]

theorem coe_distinctAugmentedRows
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    (↑(distinctAugmentedRows sample) : Set (Option Rep → K)) =
      Set.range (augmentedMatrix sample).row := by
  classical
  ext row
  simp [distinctAugmentedRows]

/-- Coefficient rank is at most the number of distinct coefficient rows.
There is no converse without a linear-independence hypothesis. -/
theorem coefficientRank_le_distinctCoefficientRows_card
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    coefficientRank sample ≤ (distinctCoefficientRows sample).card := by
  rw [← coefficientMatrix_rank_eq_coefficientRank,
    coefficientMatrix_rank_eq_finrank_span_rows,
    ← coe_distinctCoefficientRows]
  simpa [Set.finrank] using
    (finrank_span_finset_le_card
      (R := K) (distinctCoefficientRows sample))

/-- Augmented rank is at most the number of distinct augmented rows.  Merely
being different rows does not make them linearly independent. -/
theorem augmentedRank_le_distinctAugmentedRows_card
    {R : BasePoint} {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    augmentedRank sample ≤ (distinctAugmentedRows sample).card := by
  rw [← augmentedMatrix_rank_eq_augmentedRank,
    augmentedMatrix_rank_eq_finrank_span_rows,
    ← coe_distinctAugmentedRows]
  simpa [Set.finrank] using
    (finrank_span_finset_le_card
      (R := K) (distinctAugmentedRows sample))

end

end Ecdlp.M16FiniteGLVRelationRank
