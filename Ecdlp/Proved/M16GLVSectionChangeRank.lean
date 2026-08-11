import Ecdlp.Proved.M16CancellationRelationRank

/-!
# Rank invariance under a certified GLV section change

This module isolates the linear algebra behind changing the chosen column in
each liftable GLV orbit.  A `MonomialRebase α β` consists of a uniform
column equivalence `β ≃ α` and one unit of `ZMod n` for each new column.
The new basis vector is the corresponding unit multiple of the old basis
vector, so the transported coefficient is multiplied by the inverse unit.

The target column in an augmented relation is fixed, including its coefficient
`-1`.  Consequently coefficient and augmented matrix ranks, labelled synthesis
kernels, and the cardinalities of the deduplicated row sets are invariant.

`SignedGLVSection` is deliberately conditional: it records a supplied orbit
permutation, GLV phase, sign choice, and proof that the resulting scalar is the
declared unit.  It does not define or certify the separate experimental
minimum-point-encoding convention.  No achieved rank, relation yield,
independence, PFPO or `AllRoots` result, root-solving result, runtime, memory,
cost, discrete-log recovery, or ECDLP shortcut is proved here.
-/

namespace Ecdlp.M16GLVSectionChangeRank

open Ecdlp.Curve
open Ecdlp.M16CancellationRelationRank
open Ecdlp.M16FactorBaseLiftable
open Ecdlp.M16FiniteGLVRelationRank
open Ecdlp.M16GLVCanonicalRows

noncomputable section

abbrev K := ZMod Secp256k1.n
abbrev BasePoint := Ecdlp.Curve.secp256k1.toAffine.Point
abbrev PointN := ↥Ecdlp.Curve.secp256k1Grp
abbrev Rep := Ecdlp.M16FactorBaseLiftable.LiftableGLVOrbitRep

/-! ## Generic monomial column changes -/

/-- A uniform column permutation followed by multiplication of every new
column by a unit.  `columnEquiv j` is the old column represented by new column
`j`; coefficients therefore transform by the inverse of `scale j`. -/
structure MonomialRebase (α β : Type*) where
  columnEquiv : β ≃ α
  scale : β → Kˣ

namespace MonomialRebase

/-- Extend a column change by one distinguished target column.  The target is
fixed and has scale one. -/
def withFixedTarget {α β : Type*} (T : MonomialRebase α β) :
    MonomialRebase (Option α) (Option β) where
  columnEquiv := T.columnEquiv.optionCongr
  scale
    | none => 1
    | some j => T.scale j

/-- The coefficient-space equivalence induced by a monomial column change. -/
def rowEquiv {α β : Type*} (T : MonomialRebase α β) :
    (α → K) ≃ₗ[K] (β → K) :=
  (LinearEquiv.funCongrLeft K K T.columnEquiv).trans
    (LinearEquiv.piCongrRight fun j ↦
      LinearEquiv.smulOfUnit (T.scale j)⁻¹)

@[simp] theorem rowEquiv_apply {α β : Type*}
    (T : MonomialRebase α β) (row : α → K) (j : β) :
    T.rowEquiv row j =
      (T.scale j)⁻¹ • row (T.columnEquiv j) := by
  rfl

@[simp] theorem withFixedTarget_rowEquiv_none {α β : Type*}
    (T : MonomialRebase α β) (row : Option α → K) :
    T.withFixedTarget.rowEquiv row none = row none := by
  rw [rowEquiv_apply]
  change (1 : Kˣ)⁻¹ • row none = row none
  rw [inv_one, one_smul]

@[simp] theorem withFixedTarget_rowEquiv_some {α β : Type*}
    (T : MonomialRebase α β) (row : Option α → K) (j : β) :
    T.withFixedTarget.rowEquiv row (some j) =
      (T.scale j)⁻¹ • row (some (T.columnEquiv j)) := by
  rfl

/-- Finitely supported form of `rowEquiv`.  Finiteness is used only to pass
through the canonical equivalence between a `Finsupp` and its function space. -/
noncomputable def finsuppEquiv {α β : Type*} [Finite α] [Finite β]
    (T : MonomialRebase α β) :
    (α →₀ K) ≃ₗ[K] (β →₀ K) :=
  (Finsupp.linearEquivFunOnFinite K K α).trans <|
    T.rowEquiv.trans
      (Finsupp.linearEquivFunOnFinite K K β).symm

@[simp] theorem finsuppEquiv_apply {α β : Type*} [Finite α] [Finite β]
    (T : MonomialRebase α β) (row : α →₀ K) (j : β) :
    T.finsuppEquiv row j =
      (T.scale j)⁻¹ • row (T.columnEquiv j) := by
  change T.rowEquiv row j = _
  exact T.rowEquiv_apply row j

@[simp] theorem finsuppEquiv_single {α β : Type*} [Finite α] [Finite β]
    (T : MonomialRebase α β) (i : α) (c : K) :
    T.finsuppEquiv (Finsupp.single i c) =
      Finsupp.single (T.columnEquiv.symm i)
        ((T.scale (T.columnEquiv.symm i))⁻¹ • c) := by
  classical
  ext j
  by_cases h : T.columnEquiv j = i
  · have hj : j = T.columnEquiv.symm i := by
      apply T.columnEquiv.injective
      simpa using h
    subst j
    rw [finsuppEquiv_apply]
    simp only [Equiv.apply_symm_apply, Finsupp.single_eq_same]
  · have hj : j ≠ T.columnEquiv.symm i := by
      intro hj
      subst j
      exact h (T.columnEquiv.apply_symm_apply i)
    have hi : i ≠ T.columnEquiv j := Ne.symm h
    have hj' : T.columnEquiv.symm i ≠ j := Ne.symm hj
    rw [finsuppEquiv_apply]
    simp only [Finsupp.single_apply, hi, hj', if_false, smul_zero]

end MonomialRebase

/-- Rebase every row of a matrix by the same permutation and unit diagonal. -/
noncomputable def rebaseMatrix {ι α β : Type*}
    (T : MonomialRebase α β) (M : Matrix ι α K) : Matrix ι β K :=
  fun i ↦ T.rowEquiv (M.row i)

@[simp] theorem rebaseMatrix_apply {ι α β : Type*}
    (T : MonomialRebase α β) (M : Matrix ι α K) (i : ι) (j : β) :
    rebaseMatrix T M i j =
      (T.scale j)⁻¹ • M i (T.columnEquiv j) := by
  exact T.rowEquiv_apply (M.row i) j

/-- A uniform permutation and nonzero column scaling preserve matrix rank. -/
theorem rank_rebaseMatrix {ι α β : Type*} [Fintype α] [Fintype β]
    (T : MonomialRebase α β) (M : Matrix ι α K) :
    (rebaseMatrix T M).rank = M.rank := by
  classical
  have hrebase :
      rebaseMatrix T M =
        M.submatrix id T.columnEquiv *
          Matrix.diagonal (fun j ↦ (((T.scale j)⁻¹ : Kˣ) : K)) := by
    ext i j
    rw [rebaseMatrix_apply, Matrix.mul_diagonal]
    simp only [Matrix.submatrix_apply, Units.smul_def, smul_eq_mul,
      id_eq, mul_comm]
  have hdet : IsUnit
      (Matrix.det
        (Matrix.diagonal (fun j ↦ (((T.scale j)⁻¹ : Kˣ) : K)))) := by
    rw [Matrix.det_diagonal]
    exact IsUnit.prod_univ_iff.mpr fun j ↦
      Units.isUnit ((T.scale j)⁻¹)
  rw [hrebase,
    Matrix.rank_mul_eq_left_of_isUnit_det
      (Matrix.diagonal (fun j ↦ (((T.scale j)⁻¹ : Kˣ) : K))) _ hdet]
  simpa using
    (Matrix.rank_submatrix M (Equiv.refl ι) T.columnEquiv)

/-! ## Supplied signed GLV sections -/

/-- A supplied signed GLV section.  The phase and sign are metadata certified
by `scale_spec`; no particular encoding convention is constructed here. -/
structure SignedGLVSection (κ : Type*) extends MonomialRebase Rep κ where
  phase : κ → Fin 3
  negated : κ → Bool
  scale_spec : ∀ j,
    (scale j : K) =
      (if negated j then (-1 : K) else 1) *
        (Secp256k1.lam : K) ^ (phase j : ℕ)

/-- The concrete subgroup basis point selected by a certified section. -/
noncomputable def sectionPointN {κ : Type*} (S : SignedGLVSection κ)
    (j : κ) : PointN :=
  S.scale j • glvRepresentativePointN (S.columnEquiv j)

/-- Expand the selected point into the supplied sign and GLV phase. -/
theorem sectionPointN_eq_signedPhase {κ : Type*}
    (S : SignedGLVSection κ) (j : κ) :
    sectionPointN S j =
      ((if S.negated j then (-1 : K) else 1) *
        (Secp256k1.lam : K) ^ (S.phase j : ℕ)) •
          glvRepresentativePointN (S.columnEquiv j) := by
  rw [sectionPointN, Units.smul_def, S.scale_spec]

/-- Evaluate coefficients in the basis supplied by the signed section. -/
noncomputable def evalSectionRowModN {κ : Type*}
    (S : SignedGLVSection κ) : (κ →₀ K) →ₗ[K] PointN :=
  Finsupp.linearCombination K (sectionPointN S)

private theorem inverseScale_cancel
    (u : Kˣ) (c : K) (P : PointN) :
    (u⁻¹ • c) • (u • P) = c • P := by
  rw [Units.smul_def, Units.smul_def, smul_smul, smul_eq_mul]
  congr 1
  rw [mul_comm ((u⁻¹ : Kˣ) : K) c, mul_assoc, Units.inv_mul, mul_one]

/-- Inverse coefficient scaling exactly compensates for the changed basis
point, so section evaluation agrees with the canonical GLV evaluation. -/
theorem evalSectionRowModN_rebase {κ : Type*} [Finite κ]
    (S : SignedGLVSection κ) (row : GLVRowModN) :
    evalSectionRowModN S (S.toMonomialRebase.finsuppEquiv row) =
      evalGLVRowModN row := by
  let lhs : GLVRowModN →ₗ[K] PointN :=
    (evalSectionRowModN S).comp
      S.toMonomialRebase.finsuppEquiv.toLinearMap
  have hmaps : lhs = evalGLVRowModN := by
    apply Finsupp.lhom_ext (σ₁₂ := RingHom.id K)
    intro i c
    change evalSectionRowModN S
        (S.toMonomialRebase.finsuppEquiv (Finsupp.single i c)) =
      evalGLVRowModN (Finsupp.single i c)
    rw [MonomialRebase.finsuppEquiv_single]
    simp only [evalSectionRowModN, evalGLVRowModN,
      Finsupp.linearCombination_single]
    rw [sectionPointN, S.columnEquiv.apply_symm_apply]
    exact inverseScale_cancel (S.scale (S.columnEquiv.symm i)) c
      (glvRepresentativePointN i)
  exact LinearMap.congr_fun hmaps row

/-! ## Certified recovery rows in a changed section -/

/-- The certified coefficient row transported to the supplied section. -/
noncomputable def rebasedCertifiedRowModN {κ : Type*} [Finite κ]
    (S : SignedGLVSection κ) {R : BasePoint}
    (w : CertifiedRecovery R) : κ →₀ K :=
  S.toMonomialRebase.finsuppEquiv (certifiedRowModN w)

/-- A rebased certified row still evaluates to its exact target. -/
theorem evalSectionRowModN_rebasedCertifiedRowModN
    {κ : Type*} [Finite κ] (S : SignedGLVSection κ)
    {R : BasePoint} (w : CertifiedRecovery R) :
    evalSectionRowModN S (rebasedCertifiedRowModN S w) = asPointN R := by
  calc
    evalSectionRowModN S (rebasedCertifiedRowModN S w) =
        evalGLVRowModN (certifiedRowModN w) := by
      exact evalSectionRowModN_rebase S (certifiedRowModN w)
    _ = asPointN R := evalGLVRowModN_certifiedRowModN w

/-- The fixed target coefficient `-1` closes the rebased homogeneous row. -/
theorem rebasedCertifiedRelation_closes
    {κ : Type*} [Finite κ] (S : SignedGLVSection κ)
    {R : BasePoint} (w : CertifiedRecovery R) :
    evalSectionRowModN S (rebasedCertifiedRowModN S w) +
      (-1 : K) • asPointN R = 0 := by
  rw [evalSectionRowModN_rebasedCertifiedRowModN]
  simp

/-! ## Rebased finite matrices -/

/-- Coefficient matrix in the supplied signed section. -/
noncomputable def rebasedCoefficientMatrix
    {κ ι : Type*} (S : SignedGLVSection κ) {R : BasePoint}
    (sample : ι → CertifiedRecovery R) : Matrix ι κ K :=
  rebaseMatrix S.toMonomialRebase (coefficientMatrix sample)

/-- Augmented matrix in the supplied signed section, with the target column
fixed rather than permuted or rescaled. -/
noncomputable def rebasedAugmentedMatrix
    {κ ι : Type*} (S : SignedGLVSection κ) {R : BasePoint}
    (sample : ι → CertifiedRecovery R) : Matrix ι (Option κ) K :=
  rebaseMatrix S.toMonomialRebase.withFixedTarget
    (augmentedMatrix sample)

@[simp] theorem rebasedCoefficientMatrix_apply
    {κ ι : Type*} [Finite κ] (S : SignedGLVSection κ)
    {R : BasePoint} (sample : ι → CertifiedRecovery R) (k : ι) (j : κ) :
    rebasedCoefficientMatrix S sample k j =
      rebasedCertifiedRowModN S (sample k) j := by
  simp [rebasedCoefficientMatrix, rebasedCertifiedRowModN]

@[simp] theorem rebasedAugmentedMatrix_none
    {κ ι : Type*} (S : SignedGLVSection κ)
    {R : BasePoint} (sample : ι → CertifiedRecovery R) (k : ι) :
    rebasedAugmentedMatrix S sample k none = -1 := by
  simp [rebasedAugmentedMatrix, MonomialRebase.withFixedTarget]

@[simp] theorem rebasedAugmentedMatrix_some
    {κ ι : Type*} [Finite κ] (S : SignedGLVSection κ)
    {R : BasePoint} (sample : ι → CertifiedRecovery R) (k : ι) (j : κ) :
    rebasedAugmentedMatrix S sample k (some j) =
      rebasedCoefficientMatrix S sample k j := by
  simp [rebasedAugmentedMatrix, rebasedCoefficientMatrix,
    MonomialRebase.withFixedTarget]

/-- Every augmented row in the changed section remains an exact homogeneous
relation for the same fixed target. -/
theorem rebasedAugmentedMatrix_row_closes
    {κ ι : Type*} [Finite κ] (S : SignedGLVSection κ)
    {R : BasePoint} (sample : ι → CertifiedRecovery R) (k : ι) :
    evalSectionRowModN S (rebasedCertifiedRowModN S (sample k)) +
      rebasedAugmentedMatrix S sample k none • asPointN R = 0 := by
  simpa using rebasedCertifiedRelation_closes S (sample k)

/-- Coefficient matrix rank is independent of the certified signed section. -/
theorem rebasedCoefficientMatrix_rank_eq
    {κ ι : Type*} [Fintype κ] (S : SignedGLVSection κ)
    {R : BasePoint} (sample : ι → CertifiedRecovery R) :
    (rebasedCoefficientMatrix S sample).rank =
      (coefficientMatrix sample).rank :=
  rank_rebaseMatrix S.toMonomialRebase (coefficientMatrix sample)

/-- Augmented matrix rank is independent of the certified signed section. -/
theorem rebasedAugmentedMatrix_rank_eq
    {κ ι : Type*} [Fintype κ] (S : SignedGLVSection κ)
    {R : BasePoint} (sample : ι → CertifiedRecovery R) :
    (rebasedAugmentedMatrix S sample).rank =
      (augmentedMatrix sample).rank :=
  rank_rebaseMatrix S.toMonomialRebase.withFixedTarget
    (augmentedMatrix sample)

/-! ## Labelled synthesis kernels -/

/-- Synthesis of labelled coefficient rows after the section change. -/
noncomputable def rebasedCoefficientSynthesis
    {κ ι : Type*} (S : SignedGLVSection κ) {R : BasePoint}
    (sample : ι → CertifiedRecovery R) :
    (ι →₀ K) →ₗ[K] (κ → K) :=
  Finsupp.linearCombination K (rebasedCoefficientMatrix S sample).row

/-- Synthesis of labelled augmented rows after the section change. -/
noncomputable def rebasedAugmentedSynthesis
    {κ ι : Type*} (S : SignedGLVSection κ) {R : BasePoint}
    (sample : ι → CertifiedRecovery R) :
    (ι →₀ K) →ₗ[K] (Option κ → K) :=
  Finsupp.linearCombination K (rebasedAugmentedMatrix S sample).row

theorem rebasedCoefficientSynthesis_eq_comp
    {κ ι : Type*} (S : SignedGLVSection κ) {R : BasePoint}
    (sample : ι → CertifiedRecovery R) :
    rebasedCoefficientSynthesis S sample =
      S.toMonomialRebase.rowEquiv.toLinearMap.comp
        (coefficientSynthesis sample) := by
  apply Finsupp.lhom_ext (σ₁₂ := RingHom.id K)
  intro k c
  simp only [rebasedCoefficientSynthesis, coefficientSynthesis,
    Finsupp.linearCombination_single, LinearMap.comp_apply]
  change c • S.toMonomialRebase.rowEquiv
      ((coefficientMatrix sample).row k) =
    S.toMonomialRebase.rowEquiv
      (c • (coefficientMatrix sample).row k)
  exact (S.toMonomialRebase.rowEquiv.map_smul c _).symm

theorem rebasedAugmentedSynthesis_eq_comp
    {κ ι : Type*} (S : SignedGLVSection κ) {R : BasePoint}
    (sample : ι → CertifiedRecovery R) :
    rebasedAugmentedSynthesis S sample =
      S.toMonomialRebase.withFixedTarget.rowEquiv.toLinearMap.comp
        (augmentedSynthesis sample) := by
  apply Finsupp.lhom_ext (σ₁₂ := RingHom.id K)
  intro k c
  simp only [rebasedAugmentedSynthesis, augmentedSynthesis,
    Finsupp.linearCombination_single, LinearMap.comp_apply]
  change c • S.toMonomialRebase.withFixedTarget.rowEquiv
      ((augmentedMatrix sample).row k) =
    S.toMonomialRebase.withFixedTarget.rowEquiv
      (c • (augmentedMatrix sample).row k)
  exact
    (S.toMonomialRebase.withFixedTarget.rowEquiv.map_smul c _).symm

/-- The labelled coefficient dependencies are exactly unchanged. -/
theorem ker_rebasedCoefficientSynthesis
    {κ ι : Type*} (S : SignedGLVSection κ) {R : BasePoint}
    (sample : ι → CertifiedRecovery R) :
    LinearMap.ker (rebasedCoefficientSynthesis S sample) =
      LinearMap.ker (coefficientSynthesis sample) := by
  rw [rebasedCoefficientSynthesis_eq_comp]
  exact LinearMap.ker_comp_of_ker_eq_bot _
    S.toMonomialRebase.rowEquiv.ker

/-- The labelled augmented dependencies are exactly unchanged. -/
theorem ker_rebasedAugmentedSynthesis
    {κ ι : Type*} (S : SignedGLVSection κ) {R : BasePoint}
    (sample : ι → CertifiedRecovery R) :
    LinearMap.ker (rebasedAugmentedSynthesis S sample) =
      LinearMap.ker (augmentedSynthesis sample) := by
  rw [rebasedAugmentedSynthesis_eq_comp]
  exact LinearMap.ker_comp_of_ker_eq_bot _
    S.toMonomialRebase.withFixedTarget.rowEquiv.ker

/-! ## Deduplicated rows -/

/-- Distinct coefficient rows after the section change. -/
noncomputable def rebasedDistinctCoefficientRows
    {κ ι : Type*} [Fintype ι] (S : SignedGLVSection κ)
    {R : BasePoint} (sample : ι → CertifiedRecovery R) : Finset (κ → K) := by
  classical
  exact Finset.univ.image (rebasedCoefficientMatrix S sample).row

/-- Distinct augmented rows after the section change. -/
noncomputable def rebasedDistinctAugmentedRows
    {κ ι : Type*} [Fintype ι] (S : SignedGLVSection κ)
    {R : BasePoint} (sample : ι → CertifiedRecovery R) :
    Finset (Option κ → K) := by
  classical
  exact Finset.univ.image (rebasedAugmentedMatrix S sample).row

/-- Deduplicating after a section change gives exactly the same number of
coefficient rows. -/
theorem card_rebasedDistinctCoefficientRows
    {κ ι : Type*} [Fintype ι] (S : SignedGLVSection κ)
    {R : BasePoint} (sample : ι → CertifiedRecovery R) :
    (rebasedDistinctCoefficientRows S sample).card =
      (distinctCoefficientRows sample).card := by
  classical
  have hrows :
      rebasedDistinctCoefficientRows S sample =
        (distinctCoefficientRows sample).image
          S.toMonomialRebase.rowEquiv := by
    ext row
    constructor
    · intro hrow
      rcases Finset.mem_image.mp hrow with ⟨k, _, hk⟩
      refine Finset.mem_image.mpr
        ⟨(coefficientMatrix sample).row k, ?_, ?_⟩
      · exact Finset.mem_image.mpr ⟨k, Finset.mem_univ k, rfl⟩
      · change S.toMonomialRebase.rowEquiv
          ((coefficientMatrix sample).row k) = row at hk
        exact hk
    · intro hrow
      rcases Finset.mem_image.mp hrow with ⟨oldRow, hold, hrow⟩
      rcases Finset.mem_image.mp hold with ⟨k, _, hk⟩
      subst oldRow
      refine Finset.mem_image.mpr ⟨k, Finset.mem_univ k, ?_⟩
      change S.toMonomialRebase.rowEquiv
        ((coefficientMatrix sample).row k) = row
      exact hrow
  rw [hrows,
    Finset.card_image_of_injective _ S.toMonomialRebase.rowEquiv.injective]

/-- Deduplicating after a section change gives exactly the same number of
augmented rows. -/
theorem card_rebasedDistinctAugmentedRows
    {κ ι : Type*} [Fintype ι] (S : SignedGLVSection κ)
    {R : BasePoint} (sample : ι → CertifiedRecovery R) :
    (rebasedDistinctAugmentedRows S sample).card =
      (distinctAugmentedRows sample).card := by
  classical
  have hrows :
      rebasedDistinctAugmentedRows S sample =
        (distinctAugmentedRows sample).image
          S.toMonomialRebase.withFixedTarget.rowEquiv := by
    ext row
    constructor
    · intro hrow
      rcases Finset.mem_image.mp hrow with ⟨k, _, hk⟩
      refine Finset.mem_image.mpr
        ⟨(augmentedMatrix sample).row k, ?_, ?_⟩
      · exact Finset.mem_image.mpr ⟨k, Finset.mem_univ k, rfl⟩
      · change S.toMonomialRebase.withFixedTarget.rowEquiv
          ((augmentedMatrix sample).row k) = row at hk
        exact hk
    · intro hrow
      rcases Finset.mem_image.mp hrow with ⟨oldRow, hold, hrow⟩
      rcases Finset.mem_image.mp hold with ⟨k, _, hk⟩
      subst oldRow
      refine Finset.mem_image.mpr ⟨k, Finset.mem_univ k, ?_⟩
      change S.toMonomialRebase.withFixedTarget.rowEquiv
        ((augmentedMatrix sample).row k) = row
      exact hrow
  rw [hrows,
    Finset.card_image_of_injective _
      S.toMonomialRebase.withFixedTarget.rowEquiv.injective]

/-! ## The explicit cancellation family remains rank one -/

theorem rebasedCoefficientMatrix_rank_cancellationRankSample
    {κ : Type*} [Fintype κ] (S : SignedGLVSection κ)
    (a : Ecdlp.M16FactorBaseLiftable.LiftableFactorBaseX) :
    (rebasedCoefficientMatrix S (cancellationRankSample a)).rank = 1 := by
  rw [rebasedCoefficientMatrix_rank_eq,
    coefficientMatrix_rank_cancellationRankSample]

theorem rebasedAugmentedMatrix_rank_cancellationRankSample
    {κ : Type*} [Fintype κ] (S : SignedGLVSection κ)
    (a : Ecdlp.M16FactorBaseLiftable.LiftableFactorBaseX) :
    (rebasedAugmentedMatrix S (cancellationRankSample a)).rank = 1 := by
  rw [rebasedAugmentedMatrix_rank_eq,
    augmentedMatrix_rank_cancellationRankSample]

theorem finrank_ker_rebasedCoefficientSynthesis_cancellationRankSample
    {κ : Type*} (S : SignedGLVSection κ)
    (a : Ecdlp.M16FactorBaseLiftable.LiftableFactorBaseX) :
    Module.finrank K
        (LinearMap.ker
          (rebasedCoefficientSynthesis S (cancellationRankSample a))) =
      283527 ^ 7 - 1 := by
  rw [ker_rebasedCoefficientSynthesis,
    finrank_ker_coefficientSynthesis_cancellationRankSample]

theorem finrank_ker_rebasedAugmentedSynthesis_cancellationRankSample
    {κ : Type*} (S : SignedGLVSection κ)
    (a : Ecdlp.M16FactorBaseLiftable.LiftableFactorBaseX) :
    Module.finrank K
        (LinearMap.ker
          (rebasedAugmentedSynthesis S (cancellationRankSample a))) =
      283527 ^ 7 - 1 := by
  rw [ker_rebasedAugmentedSynthesis,
    finrank_ker_augmentedSynthesis_cancellationRankSample]

end

end Ecdlp.M16GLVSectionChangeRank
