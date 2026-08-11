import Ecdlp.Proved.M16GLVSectionChangeRank

/-!
# Fixed-fiber rank accounting

This module records two effects that were deliberately left distinct in the
earlier finite relation-matrix package.

First, for a nonzero target, the constant target column adds no rank to any
finite sample of certified recoveries.  The general statement is sharper:
the augmented synthesis kernel is the intersection of the coefficient
synthesis kernel with the kernel of the sum of the label coefficients.  A
nonzero target forces every coefficient dependency to have label sum zero.
At target zero only the intersection theorem is supplied here; no equality of
the two kernels or ranks is claimed.  The nonzero-target conclusion is
transported through every supplied signed GLV section.

Second, for one fixed factor-base tuple, the complete semantic recovery fiber
is the normalized fiber times the retained Boolean target label.  Global
source negation and target-label flipping do not change the canonical row.
Thus passing from the normalized fiber to the full labelled fiber preserves
both coefficient and augmented rank, while adding exactly one normalized-
fiber cardinality to each labelled synthesis-kernel dimension.

Raw integral-row and GLV-compressed mod-`n` multiplicity/coarsening theorems
are intentionally deferred: they need a smaller elaboration interface for
the nested finite semantic fibers.  In particular, this module makes no
multiplicity or row-partition claim.  Any later fixed-fiber multiplicity must
count target-labelled semantic witnesses, not algebraic root multiplicity.

No minimum-point-encoding convention is defined or compared here.  Nothing
in this module proves an achieved rank, independence, relation yield, PFPO or
`AllRoots` result, root-solving result, runtime, memory, cost, discrete-log
recovery, or ECDLP shortcut.
-/

namespace Ecdlp.M16FixedFiberMultiplicityRank

open scoped BigOperators

open Ecdlp.Curve
open Ecdlp.M16BaseRecoveryFiber
open Ecdlp.M16CanonicalRecoveryRows
open Ecdlp.M16FactorBaseLiftable
open Ecdlp.M16FiniteGLVRelationRank
open Ecdlp.M16GLVCanonicalRows
open Ecdlp.M16GLVSectionChangeRank

noncomputable section

abbrev K := ZMod Secp256k1.n
abbrev BasePoint := Ecdlp.Curve.secp256k1.toAffine.Point
abbrev PointN := ↥Ecdlp.Curve.secp256k1Grp
abbrev Rep := LiftableGLVOrbitRep

/-! ## The exact augmented-kernel boundary -/

/-- Sum of the coefficients of a finitely supported labelled combination. -/
noncomputable def labelSum {ι : Type*} : (ι →₀ K) →ₗ[K] K :=
  Finsupp.linearCombination K (fun _ ↦ 1)

@[simp] theorem labelSum_single {ι : Type*} (i : ι) (c : K) :
    labelSum (Finsupp.single i c) = c := by
  simp [labelSum]

/-- Restrict a coefficient function to its canonical finite-support
presentation and evaluate it in the concrete prime-order subgroup. -/
noncomputable def evalCoefficientFunctionModN :
    (Rep → K) →ₗ[K] PointN :=
  evalGLVRowModN.comp
    (Finsupp.linearEquivFunOnFinite K K Rep).symm.toLinearMap

theorem evalCoefficientFunctionModN_coefficientRow
    {R : BasePoint} (w : CertifiedRecovery R) :
    evalCoefficientFunctionModN (coefficientRow w) = asPointN R := by
  rw [evalCoefficientFunctionModN, LinearMap.comp_apply]
  change evalGLVRowModN
      ((Finsupp.linearEquivFunOnFinite K K Rep).symm
        (certifiedRowModN w : Rep → K)) = asPointN R
  rw [Finsupp.linearEquivFunOnFinite_symm_coe]
  exact evalGLVRowModN_certifiedRowModN w

theorem evalCoefficientFunctionModN_coefficientMatrix_row
    {R : BasePoint} {ι : Type*} (sample : ι → CertifiedRecovery R)
    (i : ι) :
    evalCoefficientFunctionModN ((coefficientMatrix sample).row i) =
      asPointN R := by
  exact evalCoefficientFunctionModN_coefficientRow (sample i)

/-- Evaluating a synthesized coefficient dependency gives its label sum times
the fixed target. -/
theorem evalCoefficientFunctionModN_coefficientSynthesis
    {R : BasePoint} {ι : Type*} (sample : ι → CertifiedRecovery R)
    (c : ι →₀ K) :
    evalCoefficientFunctionModN (coefficientSynthesis sample c) =
      labelSum c • asPointN R := by
  have hmaps :
      evalCoefficientFunctionModN.comp (coefficientSynthesis sample) =
        (labelSum (ι := ι)).smulRight (asPointN R) := by
    apply Finsupp.lhom_ext (σ₁₂ := RingHom.id K)
    intro i a
    simp only [LinearMap.comp_apply, coefficientSynthesis,
      Finsupp.linearCombination_single, map_smul,
      LinearMap.smulRight_apply, labelSum_single]
    rw [evalCoefficientFunctionModN_coefficientMatrix_row]
  exact LinearMap.congr_fun hmaps c

/-- The factor-base coordinates of the two synthesis maps agree. -/
@[simp] theorem augmentedSynthesis_some
    {R : BasePoint} {ι : Type*} (sample : ι → CertifiedRecovery R)
    (c : ι →₀ K) (i : Rep) :
    augmentedSynthesis sample c (some i) =
      coefficientSynthesis sample c i := by
  induction c using Finsupp.induction_linear with
  | zero => simp
  | add f g hf hg => simp only [map_add, Pi.add_apply, hf, hg]
  | single k a => simp [coefficientSynthesis, augmentedSynthesis]

/-- The distinguished target coordinate is minus the sum of the label
coefficients. -/
@[simp] theorem augmentedSynthesis_none
    {R : BasePoint} {ι : Type*} (sample : ι → CertifiedRecovery R)
    (c : ι →₀ K) :
    augmentedSynthesis sample c none = -labelSum c := by
  induction c using Finsupp.induction_linear with
  | zero => simp
  | add f g hf hg =>
      simp only [map_add, Pi.add_apply, hf, hg]
      abel
  | single k a => simp [augmentedSynthesis]

/-- For every target, including zero, an augmented dependency is exactly a
coefficient dependency whose label coefficients sum to zero. -/
theorem ker_augmentedSynthesis_eq_inf_ker_coefficientSynthesis_ker_labelSum
    {R : BasePoint} {ι : Type*} (sample : ι → CertifiedRecovery R) :
    LinearMap.ker (augmentedSynthesis sample) =
      LinearMap.ker (coefficientSynthesis sample) ⊓
        LinearMap.ker (labelSum (ι := ι)) := by
  ext c
  simp only [LinearMap.mem_ker, Submodule.mem_inf]
  constructor
  · intro haug
    constructor
    · funext i
      have hi := congrFun haug (some i)
      simpa using hi
    · have hnone := congrFun haug none
      simpa using hnone
  · rintro ⟨hcoeff, hsum⟩
    funext j
    cases j with
    | none => simp [hsum]
    | some i => simp [hcoeff]

/-- For a nonzero target, every coefficient dependency has label sum zero. -/
theorem ker_coefficientSynthesis_le_ker_labelSum_of_target_ne_zero
    {R : BasePoint} (hR : R ≠ 0) {ι : Type*}
    (sample : ι → CertifiedRecovery R) :
    LinearMap.ker (coefficientSynthesis sample) ≤
      LinearMap.ker (labelSum (ι := ι)) := by
  intro c hc
  rw [LinearMap.mem_ker] at hc ⊢
  have hsmul : labelSum c • asPointN R = 0 := by
    rw [← evalCoefficientFunctionModN_coefficientSynthesis sample c,
      hc, map_zero]
  have hpoint : asPointN R ≠ 0 := by
    intro hzero
    apply hR
    simpa [asPointN] using
      congrArg (fun P : PointN ↦ (P : BasePoint)) hzero
  exact (smul_eq_zero.mp hsmul).resolve_right hpoint

/-- The target column is rank-redundant for every certified sample whose fixed
target is nonzero.  At target zero this module supplies only the preceding
intersection formula and makes no kernel- or rank-equality claim. -/
theorem ker_augmentedSynthesis_eq_ker_coefficientSynthesis_of_target_ne_zero
    {R : BasePoint} (hR : R ≠ 0) {ι : Type*}
    (sample : ι → CertifiedRecovery R) :
    LinearMap.ker (augmentedSynthesis sample) =
      LinearMap.ker (coefficientSynthesis sample) := by
  rw [ker_augmentedSynthesis_eq_inf_ker_coefficientSynthesis_ker_labelSum]
  exact inf_eq_left.mpr
    (ker_coefficientSynthesis_le_ker_labelSum_of_target_ne_zero hR sample)

theorem coefficientRank_eq_augmentedRank_of_target_ne_zero
    {R : BasePoint} (hR : R ≠ 0) {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    coefficientRank sample = augmentedRank sample := by
  have hcoeff := coefficientRank_add_finrank_ker sample
  have haug := augmentedRank_add_finrank_ker sample
  rw [ker_augmentedSynthesis_eq_ker_coefficientSynthesis_of_target_ne_zero
    hR sample] at haug
  omega

theorem coefficientMatrix_rank_eq_augmentedMatrix_rank_of_target_ne_zero
    {R : BasePoint} (hR : R ≠ 0) {ι : Type*} [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    (coefficientMatrix sample).rank = (augmentedMatrix sample).rank := by
  rw [coefficientMatrix_rank_eq_coefficientRank,
    augmentedMatrix_rank_eq_augmentedRank,
    coefficientRank_eq_augmentedRank_of_target_ne_zero hR]

/-! ## The same boundary after a supplied section change -/

theorem ker_rebasedAugmentedSynthesis_eq_ker_rebasedCoefficientSynthesis_of_target_ne_zero
    {κ ι : Type*} (S : SignedGLVSection κ)
    {R : BasePoint} (hR : R ≠ 0)
    (sample : ι → CertifiedRecovery R) :
    LinearMap.ker (rebasedAugmentedSynthesis S sample) =
      LinearMap.ker (rebasedCoefficientSynthesis S sample) := by
  rw [ker_rebasedAugmentedSynthesis,
    ker_rebasedCoefficientSynthesis,
    ker_augmentedSynthesis_eq_ker_coefficientSynthesis_of_target_ne_zero
      hR sample]

theorem rebasedCoefficientMatrix_rank_eq_rebasedAugmentedMatrix_rank_of_target_ne_zero
    {κ ι : Type*} [Fintype κ] (S : SignedGLVSection κ)
    {R : BasePoint} (hR : R ≠ 0) [Fintype ι]
    (sample : ι → CertifiedRecovery R) :
    (rebasedCoefficientMatrix S sample).rank =
      (rebasedAugmentedMatrix S sample).rank := by
  rw [rebasedCoefficientMatrix_rank_eq,
    rebasedAugmentedMatrix_rank_eq,
    coefficientMatrix_rank_eq_augmentedMatrix_rank_of_target_ne_zero hR]

/-! ## Fixed-fiber and normalized samples -/

/-- Labels in the complete target-labelled semantic fiber above one fixed
factor-base tuple. -/
abbrev FixedFiberLabel (x : FactorBaseTuple) (R : BasePoint) :=
  RecoveryFiber (sourceCoordinates x) R

/-- Regard every witness in one fixed semantic fiber as a certified recovery. -/
noncomputable def fixedFiberSample (x : FactorBaseTuple) (R : BasePoint) :
    FixedFiberLabel x R → CertifiedRecovery R :=
  fun w ↦ ⟨x, w⟩

/-- Regard every normalized witness as a certified recovery with the retained
target label fixed to `false`. -/
noncomputable def normalizedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    NormalizedFiber (sourceCoordinates x) R → CertifiedRecovery R :=
  fun w ↦ ⟨x, ⟨(w.1, false), w.2⟩⟩

/-- Forget only the Boolean target label, normalizing its source tuple by the
exact semantic fiber equivalence. -/
noncomputable def normalizeFixedFiber
    (x : FactorBaseTuple) (R : BasePoint) (w : FixedFiberLabel x R) :
    NormalizedFiber (sourceCoordinates x) R :=
  (recoveryFiberEquivNormalizedFiberProdBool
    (sourceCoordinates x) R w).1

theorem normalizeFixedFiber_surjective
    (x : FactorBaseTuple) (R : BasePoint) :
    Function.Surjective (normalizeFixedFiber x R) := by
  intro w
  refine ⟨(recoveryFiberEquivNormalizedFiberProdBool
    (sourceCoordinates x) R).symm (w, false), ?_⟩
  simp [normalizeFixedFiber]

/-- Target-label normalization preserves the raw integral canonical row. -/
theorem canonicalRow_normalizeFixedFiber
    (x : FactorBaseTuple) (R : BasePoint) (w : FixedFiberLabel x R) :
    canonicalRow x ((normalizeFixedFiber x R w).1, false) =
      canonicalRow x w.1 := by
  rcases w with ⟨⟨L, sign⟩, hw⟩
  cases sign with
  | false => rfl
  | true =>
      change canonicalRow x (globalNegate L, false) =
        canonicalRow x (L, true)
      exact canonicalRow_globalNegate x L true

/-- Target-label normalization also preserves the GLV-compressed mod-`n`
coefficient row used by the rank matrices. -/
theorem certifiedRowModN_normalizedFiberSample_normalizeFixedFiber
    (x : FactorBaseTuple) (R : BasePoint) (w : FixedFiberLabel x R) :
    certifiedRowModN
        (normalizedFiberSample x R (normalizeFixedFiber x R w)) =
      certifiedRowModN (fixedFiberSample x R w) := by
  simp only [certifiedRowModN, normalizedFiberSample, fixedFiberSample,
    canonicalGLVRowModN]
  rw [canonicalRow_normalizeFixedFiber]

theorem coefficientMatrix_row_normalizedFiberSample_normalizeFixedFiber
    (x : FactorBaseTuple) (R : BasePoint) (w : FixedFiberLabel x R) :
    (coefficientMatrix (normalizedFiberSample x R)).row
        (normalizeFixedFiber x R w) =
      (coefficientMatrix (fixedFiberSample x R)).row w := by
  funext i
  exact DFunLike.congr_fun
    (certifiedRowModN_normalizedFiberSample_normalizeFixedFiber x R w) i

theorem augmentedMatrix_row_normalizedFiberSample_normalizeFixedFiber
    (x : FactorBaseTuple) (R : BasePoint) (w : FixedFiberLabel x R) :
    (augmentedMatrix (normalizedFiberSample x R)).row
        (normalizeFixedFiber x R w) =
      (augmentedMatrix (fixedFiberSample x R)).row w := by
  funext j
  cases j with
  | none => rfl
  | some i =>
      exact congrFun
        (coefficientMatrix_row_normalizedFiberSample_normalizeFixedFiber
          x R w) i

theorem range_coefficientMatrix_row_fixedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    Set.range (coefficientMatrix (fixedFiberSample x R)).row =
      Set.range (coefficientMatrix (normalizedFiberSample x R)).row := by
  ext row
  constructor
  · rintro ⟨w, rfl⟩
    exact ⟨normalizeFixedFiber x R w,
      coefficientMatrix_row_normalizedFiberSample_normalizeFixedFiber
        x R w⟩
  · rintro ⟨w, rfl⟩
    rcases normalizeFixedFiber_surjective x R w with ⟨v, rfl⟩
    exact ⟨v,
      (coefficientMatrix_row_normalizedFiberSample_normalizeFixedFiber
        x R v).symm⟩

theorem range_augmentedMatrix_row_fixedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    Set.range (augmentedMatrix (fixedFiberSample x R)).row =
      Set.range (augmentedMatrix (normalizedFiberSample x R)).row := by
  ext row
  constructor
  · rintro ⟨w, rfl⟩
    exact ⟨normalizeFixedFiber x R w,
      augmentedMatrix_row_normalizedFiberSample_normalizeFixedFiber
        x R w⟩
  · rintro ⟨w, rfl⟩
    rcases normalizeFixedFiber_surjective x R w with ⟨v, rfl⟩
    exact ⟨v,
      (augmentedMatrix_row_normalizedFiberSample_normalizeFixedFiber
        x R v).symm⟩

/-- Retaining both target labels does not double coefficient rank. -/
theorem coefficientRank_fixedFiberSample_eq_normalizedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    coefficientRank (fixedFiberSample x R) =
      coefficientRank (normalizedFiberSample x R) := by
  rw [coefficientRank, coefficientRank,
    range_coefficientSynthesis, range_coefficientSynthesis,
    range_coefficientMatrix_row_fixedFiberSample]

/-- Retaining both target labels does not double augmented rank. -/
theorem augmentedRank_fixedFiberSample_eq_normalizedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    augmentedRank (fixedFiberSample x R) =
      augmentedRank (normalizedFiberSample x R) := by
  rw [augmentedRank, augmentedRank,
    range_augmentedSynthesis, range_augmentedSynthesis,
    range_augmentedMatrix_row_fixedFiberSample]

theorem coefficientMatrix_rank_fixedFiberSample_eq_normalizedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    (coefficientMatrix (fixedFiberSample x R)).rank =
      (coefficientMatrix (normalizedFiberSample x R)).rank := by
  rw [coefficientMatrix_rank_eq_coefficientRank,
    coefficientMatrix_rank_eq_coefficientRank,
    coefficientRank_fixedFiberSample_eq_normalizedFiberSample]

theorem augmentedMatrix_rank_fixedFiberSample_eq_normalizedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    (augmentedMatrix (fixedFiberSample x R)).rank =
      (augmentedMatrix (normalizedFiberSample x R)).rank := by
  rw [augmentedMatrix_rank_eq_augmentedRank,
    augmentedMatrix_rank_eq_augmentedRank,
    augmentedRank_fixedFiberSample_eq_normalizedFiberSample]

/-- The extra Boolean labels add exactly one normalized-fiber cardinality to
the coefficient dependency dimension. -/
theorem finrank_ker_coefficientSynthesis_fixedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    Module.finrank K
        (LinearMap.ker (coefficientSynthesis (fixedFiberSample x R))) =
      Fintype.card (NormalizedFiber (sourceCoordinates x) R) +
        Module.finrank K
          (LinearMap.ker
            (coefficientSynthesis (normalizedFiberSample x R))) := by
  have hfull :
      coefficientRank (fixedFiberSample x R) +
          Module.finrank K
            (LinearMap.ker (coefficientSynthesis (fixedFiberSample x R))) =
        Fintype.card (FixedFiberLabel x R) :=
    coefficientRank_add_finrank_ker (fixedFiberSample x R)
  have hnormalized :
      coefficientRank (normalizedFiberSample x R) +
          Module.finrank K
            (LinearMap.ker
              (coefficientSynthesis (normalizedFiberSample x R))) =
        Fintype.card (NormalizedFiber (sourceCoordinates x) R) :=
    coefficientRank_add_finrank_ker (normalizedFiberSample x R)
  rw [coefficientRank_fixedFiberSample_eq_normalizedFiberSample] at hfull
  rw [card_recoveryFiber_eq_two_mul_card_normalizedFiber] at hfull
  omega

/-- The same exact dependency increment holds for augmented rows. -/
theorem finrank_ker_augmentedSynthesis_fixedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    Module.finrank K
        (LinearMap.ker (augmentedSynthesis (fixedFiberSample x R))) =
      Fintype.card (NormalizedFiber (sourceCoordinates x) R) +
        Module.finrank K
          (LinearMap.ker
            (augmentedSynthesis (normalizedFiberSample x R))) := by
  have hfull :
      augmentedRank (fixedFiberSample x R) +
          Module.finrank K
            (LinearMap.ker (augmentedSynthesis (fixedFiberSample x R))) =
        Fintype.card (FixedFiberLabel x R) :=
    augmentedRank_add_finrank_ker (fixedFiberSample x R)
  have hnormalized :
      augmentedRank (normalizedFiberSample x R) +
          Module.finrank K
            (LinearMap.ker
              (augmentedSynthesis (normalizedFiberSample x R))) =
        Fintype.card (NormalizedFiber (sourceCoordinates x) R) :=
    augmentedRank_add_finrank_ker (normalizedFiberSample x R)
  rw [augmentedRank_fixedFiberSample_eq_normalizedFiberSample] at hfull
  rw [card_recoveryFiber_eq_two_mul_card_normalizedFiber] at hfull
  omega

theorem coefficientRank_fixedFiberSample_le_card_normalizedFiber
    (x : FactorBaseTuple) (R : BasePoint) :
    coefficientRank (fixedFiberSample x R) ≤
      Fintype.card (NormalizedFiber (sourceCoordinates x) R) := by
  rw [coefficientRank_fixedFiberSample_eq_normalizedFiberSample]
  have h := coefficientRank_add_finrank_ker (normalizedFiberSample x R)
  omega

theorem augmentedRank_fixedFiberSample_le_card_normalizedFiber
    (x : FactorBaseTuple) (R : BasePoint) :
    augmentedRank (fixedFiberSample x R) ≤
      Fintype.card (NormalizedFiber (sourceCoordinates x) R) := by
  rw [augmentedRank_fixedFiberSample_eq_normalizedFiberSample]
  have h := augmentedRank_add_finrank_ker (normalizedFiberSample x R)
  omega

theorem card_normalizedFiber_le_finrank_ker_coefficientSynthesis_fixedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    Fintype.card (NormalizedFiber (sourceCoordinates x) R) ≤
      Module.finrank K
        (LinearMap.ker (coefficientSynthesis (fixedFiberSample x R))) := by
  rw [finrank_ker_coefficientSynthesis_fixedFiberSample]
  exact Nat.le_add_right _ _

theorem card_normalizedFiber_le_finrank_ker_augmentedSynthesis_fixedFiberSample
    (x : FactorBaseTuple) (R : BasePoint) :
    Fintype.card (NormalizedFiber (sourceCoordinates x) R) ≤
      Module.finrank K
        (LinearMap.ker (augmentedSynthesis (fixedFiberSample x R))) := by
  rw [finrank_ker_augmentedSynthesis_fixedFiberSample]
  exact Nat.le_add_right _ _

/-! ## Deferred multiplicity layer

The exact raw and GLV/mod-`n` multiplicity/coarsening layer is left for a
separate module with a smaller finite-fiber elaboration interface.  No such
multiplicity or partition theorem is claimed here.
-/

end

end Ecdlp.M16FixedFiberMultiplicityRank
