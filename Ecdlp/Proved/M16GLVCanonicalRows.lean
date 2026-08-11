import Ecdlp.Proved.CurveFullGroup
import Ecdlp.Proved.GlvSubgroupEigenvalue
import Ecdlp.Proved.M16CanonicalRecoveryRows

/-!
# Exact GLV compression of canonical M16 recovery rows

The liftable M16 factor base is the disjoint union of `94509` explicit
three-coordinate GLV orbits.  This module reorders the census layers as
`P, phi(P), phi^2(P)`, proves that the lower-residue reference points transform
by the published secp256k1 eigenvalue `lambda`, and folds integral recovery
rows to one coefficient per GLV orbit without changing their exact elliptic-
curve evaluation.

The corresponding map over `ZMod n` is a surjection from `283527` raw columns
to `94509` orbit columns.  Its kernel has dimension `189018`; in particular,
GLV compression is deliberately not injective.  These are dimensions of the
ambient coefficient spaces, not the rank of any collected relation matrix.

This module does not implement root finding or recovery, prove `AllRoots`
completeness, charge PFPO work, establish relation yield or independence, run
sparse linear algebra, or provide a runtime, memory, cost, discrete-log, or
ECDLP-shortcut result.  The representative is the reproducible census orbit
representative with the lower-residue point sign.  No claim is made that it is
byte-for-byte the separate experimental convention based on a minimum point
encoding, and no comparison theorem between those two conventions is asserted
here.
-/

namespace Ecdlp.M16GLVCanonicalRows

open scoped BigOperators

open WeierstrassCurve.Affine
open Ecdlp.Curve
open Ecdlp.M16BaseRecoveryFiber
open Ecdlp.M16CanonicalRecoveryRows
open Ecdlp.M16FactorBaseLiftable

noncomputable section

abbrev Fp := ZMod Secp256k1.p
abbrev BasePoint := Ecdlp.Curve.secp256k1.toAffine.Point

/-! ## Orbit phases and lower-residue reference points -/

/-- Reorder the census layers `representative, beta^2, beta` into the GLV
phase order `representative, beta, beta^2`. -/
def glvPhaseToLayer : Equiv.Perm (Fin 3) :=
  Equiv.swap 1 2

@[simp] theorem glvPhaseToLayer_zero : glvPhaseToLayer 0 = 0 := by
  decide

@[simp] theorem glvPhaseToLayer_one : glvPhaseToLayer 1 = 2 := by
  decide

@[simp] theorem glvPhaseToLayer_two : glvPhaseToLayer 2 = 1 := by
  decide

/-- Every liftable factor-base coordinate has a unique GLV phase and liftable
orbit representative. -/
noncomputable def liftableGLVPhaseEquiv :
    Fin 3 × LiftableGLVOrbitRep ≃ LiftableFactorBaseX :=
  (Equiv.prodCongr glvPhaseToLayer (Equiv.refl _)).trans
    liftableOrbitEquiv

@[simp] theorem liftableGLVPhaseEquiv_apply_fst
    (j : Fin 3) (i : LiftableGLVOrbitRep) :
    (liftableGLVPhaseEquiv (j, i)).1 =
      glvOrbitLayer (glvPhaseToLayer j) i.1 := by
  simp [liftableGLVPhaseEquiv]

@[simp] theorem liftableGLVPhaseEquiv_zero_fst
    (i : LiftableGLVOrbitRep) :
    (liftableGLVPhaseEquiv (0, i)).1 = orbitRepresentative i.1 := by
  rw [liftableGLVPhaseEquiv_apply_fst, glvPhaseToLayer_zero]
  rfl

theorem liftableGLVPhaseEquiv_one_val
    (i : LiftableGLVOrbitRep) :
    (liftableGLVPhaseEquiv (1, i)).1.1 =
      (Secp256k1.beta : Fp) *
        (liftableGLVPhaseEquiv (0, i)).1.1 := by
  rw [liftableGLVPhaseEquiv_apply_fst, glvPhaseToLayer_one,
    glvOrbitLayer_two, liftableGLVPhaseEquiv_zero_fst]

theorem liftableGLVPhaseEquiv_two_val
    (i : LiftableGLVOrbitRep) :
    (liftableGLVPhaseEquiv (2, i)).1.1 =
      (Secp256k1.beta : Fp) ^ 2 *
        (liftableGLVPhaseEquiv (0, i)).1.1 := by
  rw [liftableGLVPhaseEquiv_apply_fst, glvPhaseToLayer_two,
    glvOrbitLayer_one, liftableGLVPhaseEquiv_zero_fst]

/-- All three phase coordinates have the same secp256k1 curve right-hand
side, hence the same two possible y-coordinates. -/
theorem rhs_liftableGLVPhaseEquiv
    (j : Fin 3) (i : LiftableGLVOrbitRep) :
    rhs (liftableGLVPhaseEquiv (j, i)).1.1 =
      rhs (liftableGLVPhaseEquiv (0, i)).1.1 := by
  by_cases hzero : j = 0
  · subst j
    rfl
  by_cases hone : j = 1
  · subst j
    rw [liftableGLVPhaseEquiv_one_val, rhs_beta_mul]
  have htwo : j = 2 := by
    apply Fin.ext
    omega
  subst j
  rw [liftableGLVPhaseEquiv_two_val]
  simp only [pow_two, mul_assoc, rhs_beta_mul]

/-- The lower-residue convention chooses the same y-coordinate in every GLV
phase, because the phase transformation changes only x. -/
theorem referenceLift_val_glvPhase
    (j : Fin 3) (i : LiftableGLVOrbitRep) :
    (referenceLift (liftableGLVPhaseEquiv (j, i))).1 =
      (referenceLift (liftableGLVPhaseEquiv (0, i))).1 := by
  let y : LiftAt (liftableGLVPhaseEquiv (j, i)).1.1 :=
    ⟨(referenceLift (liftableGLVPhaseEquiv (0, i))).1,
      (referenceLift (liftableGLVPhaseEquiv (0, i))).2.trans
        (rhs_liftableGLVPhaseEquiv j i).symm⟩
  have hy : IsLowerResidueLift (liftableGLVPhaseEquiv (j, i)) y := by
    simpa [IsLowerResidueLift, y] using
      referenceLift_isLowerResidue (liftableGLVPhaseEquiv (0, i))
  exact (congrArg Subtype.val
    (lowerResidueLift_unique (liftableGLVPhaseEquiv (j, i)) hy)).symm

/-- The chosen point in phase one is the GLV image of the phase-zero point. -/
theorem referencePoint_glvPhase_one (i : LiftableGLVOrbitRep) :
    referencePoint (liftableGLVPhaseEquiv (1, i)) =
      glvPoint (referencePoint (liftableGLVPhaseEquiv (0, i))) := by
  simp only [referencePoint, liftPoint, glvPoint_some, Point.some.injEq]
  exact ⟨liftableGLVPhaseEquiv_one_val i,
    referenceLift_val_glvPhase 1 i⟩

/-- The chosen point in phase two is the second GLV image of the phase-zero
point. -/
theorem referencePoint_glvPhase_two (i : LiftableGLVOrbitRep) :
    referencePoint (liftableGLVPhaseEquiv (2, i)) =
      glvPoint (glvPoint
        (referencePoint (liftableGLVPhaseEquiv (0, i)))) := by
  simp only [referencePoint, liftPoint, glvPoint_some, Point.some.injEq]
  exact ⟨by
      simpa only [pow_two, mul_assoc] using
        liftableGLVPhaseEquiv_two_val i,
    referenceLift_val_glvPhase 2 i⟩

/-- On the full secp256k1 base-field point group, the GLV map is multiplication
by the published integer eigenvalue. -/
theorem glvPoint_eq_lam (P : BasePoint) :
    glvPoint P = (Secp256k1.lam : ℤ) • P :=
  secp256k1_glvPoint_eq_lam_on_zmultiples P
    (secp256k1_mem_zmultiples P)

/-- The phase-zero lower-residue point used as the orbit column. -/
noncomputable def glvRepresentativePoint
    (i : LiftableGLVOrbitRep) : BasePoint :=
  referencePoint (liftableGLVPhaseEquiv (0, i))

/-- Exact covariance of the reproducible reference points under all three GLV
phases. -/
theorem referencePoint_glvPhase
    (j : Fin 3) (i : LiftableGLVOrbitRep) :
    referencePoint (liftableGLVPhaseEquiv (j, i)) =
      ((Secp256k1.lam : ℤ) ^ (j : ℕ)) •
        glvRepresentativePoint i := by
  by_cases hzero : j = 0
  · subst j
    simp [glvRepresentativePoint]
  by_cases hone : j = 1
  · subst j
    calc
        referencePoint (liftableGLVPhaseEquiv (1, i)) =
            glvPoint (glvRepresentativePoint i) := by
          simpa [glvRepresentativePoint] using referencePoint_glvPhase_one i
        _ = (Secp256k1.lam : ℤ) • glvRepresentativePoint i :=
          glvPoint_eq_lam _
        _ = ((Secp256k1.lam : ℤ) ^ (1 : ℕ)) •
            glvRepresentativePoint i := by simp
  have htwo : j = 2 := by
    apply Fin.ext
    omega
  subst j
  calc
      referencePoint (liftableGLVPhaseEquiv (2, i)) =
          glvPoint (glvPoint (glvRepresentativePoint i)) := by
        simpa [glvRepresentativePoint] using referencePoint_glvPhase_two i
      _ = (Secp256k1.lam : ℤ) •
          glvPoint (glvRepresentativePoint i) := glvPoint_eq_lam _
      _ = (Secp256k1.lam : ℤ) •
          ((Secp256k1.lam : ℤ) • glvRepresentativePoint i) := by
        rw [glvPoint_eq_lam]
      _ = ((Secp256k1.lam : ℤ) ^ (2 : ℕ)) •
          glvRepresentativePoint i := by
        simp only [pow_two, smul_smul]

/-! ## Integral GLV row compression and exact evaluation -/

/-- Integral coefficient rows with one column per liftable GLV orbit. -/
abbrev GLVRow := LiftableGLVOrbitRep →₀ ℤ

private noncomputable def glvCoordinateSum :
    Row →ₗ[ℤ] (LiftableGLVOrbitRep → ℤ) where
  toFun row i :=
    ∑ j : Fin 3, ((Secp256k1.lam : ℤ) ^ (j : ℕ)) *
      row (liftableGLVPhaseEquiv (j, i))
  map_add' row₁ row₂ := by
    funext i
    simp [mul_add, Finset.sum_add_distrib]
  map_smul' c row := by
    funext i
    simp only [Finsupp.smul_apply, Pi.smul_apply, smul_eq_mul,
      RingHom.id_apply]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro j _
    ring

/-- Fold each raw factor-base column into its GLV orbit, multiplying phase `j`
by `lambda^j`. -/
noncomputable def glvCompress : Row →ₗ[ℤ] GLVRow :=
  (Finsupp.linearEquivFunOnFinite ℤ ℤ LiftableGLVOrbitRep).symm.toLinearMap.comp
    glvCoordinateSum

@[simp] theorem glvCompress_apply
    (row : Row) (i : LiftableGLVOrbitRep) :
    glvCompress row i =
      ∑ j : Fin 3, ((Secp256k1.lam : ℤ) ^ (j : ℕ)) *
        row (liftableGLVPhaseEquiv (j, i)) := by
  rfl

@[simp] theorem glvCompress_single_phase
    (j : Fin 3) (i : LiftableGLVOrbitRep) (c : ℤ) :
    glvCompress (Finsupp.single (liftableGLVPhaseEquiv (j, i)) c) =
      Finsupp.single i (((Secp256k1.lam : ℤ) ^ (j : ℕ)) * c) := by
  classical
  ext k
  rw [glvCompress_apply]
  by_cases hik : i = k
  · subst k
    rw [Fintype.sum_eq_single j]
    · simp
    · intro j' hj'
      have hphase :
          liftableGLVPhaseEquiv (j, i) ≠
            liftableGLVPhaseEquiv (j', i) := by
        intro h
        have hpairs := liftableGLVPhaseEquiv.injective h
        exact hj' (congrArg Prod.fst hpairs).symm
      simp [hphase]
  · have hphase : ∀ j' : Fin 3,
        liftableGLVPhaseEquiv (j, i) ≠
          liftableGLVPhaseEquiv (j', k) := by
      intro j' h
      have hpairs := liftableGLVPhaseEquiv.injective h
      exact hik (congrArg Prod.snd hpairs)
    simp [hik, hphase]

/-- Evaluate an orbit row as an integral linear combination of phase-zero
reference points. -/
noncomputable def evalGLVRow : GLVRow →ₗ[ℤ] BasePoint :=
  Finsupp.linearCombination ℤ glvRepresentativePoint

/-- GLV compression preserves the exact elliptic-curve evaluation as an
identity of linear maps. -/
theorem evalGLVRow_comp_glvCompress :
    evalGLVRow.comp glvCompress = evalRow := by
  apply Finsupp.lhom_ext
  intro a c
  rcases liftableGLVPhaseEquiv.surjective a with ⟨⟨j, i⟩, rfl⟩
  simp only [LinearMap.comp_apply]
  rw [glvCompress_single_phase]
  simp only [evalGLVRow, evalRow, Finsupp.linearCombination_single,
    referencePoint_glvPhase, smul_smul]
  rw [mul_comm]

/-- Pointwise form of exact evaluation preservation. -/
theorem evalGLVRow_glvCompress (row : Row) :
    evalGLVRow (glvCompress row) = evalRow row := by
  simpa using LinearMap.congr_fun evalGLVRow_comp_glvCompress row

/-! ## Canonical recovered rows -/

/-- The GLV-compressed form of a target-normalized canonical recovery row. -/
noncomputable def canonicalGLVRow
    (x : FactorBaseTuple) (z : RecoveryData x) : GLVRow :=
  glvCompress (canonicalRow x z)

theorem canonicalGLVRow_globalNegate
    (x : FactorBaseTuple) (L : LiftTuple (sourceCoordinates x))
    (sign : Bool) :
    canonicalGLVRow x (globalNegate L, !sign) =
      canonicalGLVRow x (L, sign) := by
  rw [canonicalGLVRow, canonicalGLVRow,
    canonicalRow_globalNegate]

/-- A compatible recovery witness still evaluates exactly to the supplied
target after GLV compression. -/
theorem evalGLVRow_canonicalGLVRow_of_compatible
    (x : FactorBaseTuple) (R : BasePoint) (z : RecoveryData x)
    (hz : Compatible (sourceCoordinates x) R z.1 z.2) :
    evalGLVRow (canonicalGLVRow x z) = R := by
  rw [canonicalGLVRow, evalGLVRow_glvCompress]
  exact evalRow_canonicalRow_of_compatible x R z hz

theorem evalGLVRow_canonicalGLVRow
    (x : FactorBaseTuple) (R : BasePoint)
    (w : RecoveryFiber (sourceCoordinates x) R) :
    evalGLVRow (canonicalGLVRow x w.1) = R :=
  evalGLVRow_canonicalGLVRow_of_compatible x R w.1 w.2

/-! ## An explicit noninjectivity boundary -/

/-- One raw GLV alias: phase one with coefficient `1` and phase zero with
coefficient `-lambda` represent the same orbit point. -/
noncomputable def glvAliasRow (i : LiftableGLVOrbitRep) : Row :=
  Finsupp.single (liftableGLVPhaseEquiv (1, i)) 1 -
    Finsupp.single (liftableGLVPhaseEquiv (0, i))
      (Secp256k1.lam : ℤ)

@[simp] theorem glvCompress_glvAliasRow (i : LiftableGLVOrbitRep) :
    glvCompress (glvAliasRow i) = 0 := by
  simp [glvAliasRow, glvCompress_single_phase]

theorem glvAliasRow_ne_zero (i : LiftableGLVOrbitRep) :
    glvAliasRow i ≠ 0 := by
  have hphase :
      liftableGLVPhaseEquiv (0, i) ≠
        liftableGLVPhaseEquiv (1, i) := by
    intro h
    have hpairs := liftableGLVPhaseEquiv.injective h
    have : (0 : Fin 3) = 1 := congrArg Prod.fst hpairs
    norm_num at this
  intro hzero
  have happ := DFunLike.congr_fun hzero
    (liftableGLVPhaseEquiv (1, i))
  simp [glvAliasRow, hphase.symm] at happ

/-- Raw-to-orbit compression is not injective.  Consequently, neither raw
root counts nor recovery multiplicities may be read as relation rank. -/
theorem glvCompress_not_injective :
    ¬Function.Injective glvCompress := by
  intro hinjective
  have hpos : 0 < Fintype.card LiftableGLVOrbitRep := by
    rw [card_liftableGLVOrbitRep]
    norm_num
  rcases Fintype.card_pos_iff.mp hpos with ⟨i⟩
  apply glvAliasRow_ne_zero i
  apply hinjective
  simp

/-! ## Coefficient compression modulo the prime group order -/

/-- Raw coefficient columns over the rank-accounting field `ZMod n`. -/
abbrev RawRowModN :=
  LiftableFactorBaseX →₀ ZMod Secp256k1.n

/-- One mod-`n` coefficient column per liftable GLV orbit. -/
abbrev GLVRowModN :=
  LiftableGLVOrbitRep →₀ ZMod Secp256k1.n

private noncomputable def glvCoordinateSumModN :
    RawRowModN →ₗ[ZMod Secp256k1.n]
      (LiftableGLVOrbitRep → ZMod Secp256k1.n) where
  toFun row i :=
    ∑ j : Fin 3,
      ((Secp256k1.lam : ZMod Secp256k1.n) ^ (j : ℕ)) *
        row (liftableGLVPhaseEquiv (j, i))
  map_add' row₁ row₂ := by
    funext i
    simp [mul_add, Finset.sum_add_distrib]
  map_smul' c row := by
    funext i
    simp only [Finsupp.smul_apply, Pi.smul_apply, smul_eq_mul,
      RingHom.id_apply]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro j _
    ring

/-- GLV coefficient compression over the prime-order scalar field. -/
noncomputable def glvCompressModN :
    RawRowModN →ₗ[ZMod Secp256k1.n] GLVRowModN :=
  (Finsupp.linearEquivFunOnFinite
    (ZMod Secp256k1.n) (ZMod Secp256k1.n)
    LiftableGLVOrbitRep).symm.toLinearMap.comp glvCoordinateSumModN

@[simp] theorem glvCompressModN_apply
    (row : RawRowModN) (i : LiftableGLVOrbitRep) :
    glvCompressModN row i =
      ∑ j : Fin 3,
        ((Secp256k1.lam : ZMod Secp256k1.n) ^ (j : ℕ)) *
          row (liftableGLVPhaseEquiv (j, i)) := by
  rfl

@[simp] theorem glvCompressModN_single_phase
    (j : Fin 3) (i : LiftableGLVOrbitRep)
    (c : ZMod Secp256k1.n) :
    glvCompressModN
        (Finsupp.single (liftableGLVPhaseEquiv (j, i)) c) =
      Finsupp.single i
        (((Secp256k1.lam : ZMod Secp256k1.n) ^ (j : ℕ)) * c) := by
  classical
  ext k
  rw [glvCompressModN_apply]
  by_cases hik : i = k
  · subst k
    rw [Fintype.sum_eq_single j]
    · simp
    · intro j' hj'
      have hphase :
          liftableGLVPhaseEquiv (j, i) ≠
            liftableGLVPhaseEquiv (j', i) := by
        intro h
        have hpairs := liftableGLVPhaseEquiv.injective h
        exact hj' (congrArg Prod.fst hpairs).symm
      simp [hphase]
  · have hphase : ∀ j' : Fin 3,
        liftableGLVPhaseEquiv (j, i) ≠
          liftableGLVPhaseEquiv (j', k) := by
      intro j' h
      have hpairs := liftableGLVPhaseEquiv.injective h
      exact hik (congrArg Prod.snd hpairs)
    simp [hik, hphase]

/-- Coefficientwise reduction of an integral finitely supported row modulo
the group order. -/
noncomputable def reduceModN {ι : Type*} :
    (ι →₀ ℤ) →ₗ[ℤ] (ι →₀ ZMod Secp256k1.n) :=
  Finsupp.mapRange.linearMap
    (Int.castAddHom (ZMod Secp256k1.n)).toIntLinearMap

@[simp] theorem reduceModN_apply {ι : Type*}
    (row : ι →₀ ℤ) (i : ι) :
    reduceModN row i = (row i : ZMod Secp256k1.n) := by
  simp [reduceModN]

/-- Integer compression and mod-`n` compression commute. -/
theorem glvCompressModN_reduceModN (row : Row) :
    glvCompressModN (reduceModN row) =
      reduceModN (glvCompress row) := by
  ext i
  simp only [glvCompressModN_apply, reduceModN_apply, glvCompress_apply]
  push_cast
  rfl

/-- The mod-`n` canonical row attached to one compatible recovery datum. -/
noncomputable def canonicalGLVRowModN
    (x : FactorBaseTuple) (z : RecoveryData x) : GLVRowModN :=
  glvCompressModN (reduceModN (canonicalRow x z))

/-- Embed an orbit row into the phase-zero raw columns. -/
noncomputable def glvPhaseZeroSectionModN :
    GLVRowModN →ₗ[ZMod Secp256k1.n] RawRowModN :=
  Finsupp.lmapDomain (ZMod Secp256k1.n) (ZMod Secp256k1.n)
    (fun i : LiftableGLVOrbitRep ↦ liftableGLVPhaseEquiv (0, i))

/-- Phase-zero embedding is a right inverse to GLV compression. -/
theorem glvCompressModN_comp_glvPhaseZeroSectionModN :
    glvCompressModN.comp glvPhaseZeroSectionModN = LinearMap.id := by
  apply Finsupp.lhom_ext
  intro i c
  simp [glvPhaseZeroSectionModN, glvCompressModN_single_phase]

/-- Every legal orbit coefficient row has a phase-zero raw representative. -/
theorem glvCompressModN_surjective :
    Function.Surjective glvCompressModN := by
  intro row
  refine ⟨glvPhaseZeroSectionModN row, ?_⟩
  have h := LinearMap.congr_fun
    glvCompressModN_comp_glvPhaseZeroSectionModN row
  simpa using h

/-- Exact number of raw liftable factor-base columns over `ZMod n`. -/
theorem finrank_rawRowModN :
    Module.finrank (ZMod Secp256k1.n) RawRowModN = 283527 := by
  rw [Module.finrank_finsupp_self, card_liftableFactorBaseX]

/-- Exact number of GLV-normalized orbit columns over `ZMod n`. -/
theorem finrank_glvRowModN :
    Module.finrank (ZMod Secp256k1.n) GLVRowModN = 94509 := by
  rw [Module.finrank_finsupp_self, card_liftableGLVOrbitRep]

/-- The kernel of structural GLV compression has dimension `189018`.
This is not a statement about the rank of collected relation rows. -/
theorem finrank_ker_glvCompressModN :
    Module.finrank (ZMod Secp256k1.n)
      (LinearMap.ker glvCompressModN) = 189018 := by
  have hrange : LinearMap.range glvCompressModN = ⊤ :=
    LinearMap.range_eq_top.mpr glvCompressModN_surjective
  have h := LinearMap.finrank_range_add_finrank_ker glvCompressModN
  rw [hrange, finrank_top, finrank_glvRowModN, finrank_rawRowModN] at h
  omega

end

end Ecdlp.M16GLVCanonicalRows
