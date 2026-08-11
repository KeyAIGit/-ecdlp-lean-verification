import Ecdlp.Proved.SemaevLeftFoldAffine
import Ecdlp.Proved.M16FactorBaseFinite

/-!
# Direct M16 System (4): exact set-level root bridge

This file states the literal four-coordinate row equations from direct M16
System (4), proves that a canonical row is equivalent to the exact
`x ^ 564522 = 1` factor-base predicate, and removes the three transition
coordinates in every row by an explicit equivalence of solution subtypes.

This is only an equivalence of sets of distinct solutions.  It makes no claim
about ideals, radicals, multiplicities, solver behavior, solving cost,
recovery, relation yield, rank, descent, or a discrete-log shortcut.  External
source values and the fixed target are affine, while the final chart-cover
result keeps every internal infinity mask over the algebraic closure.
-/

namespace Ecdlp.M16DirectSystemRootBridge

open Ecdlp.M16FactorBaseFinite
open Ecdlp.SemaevLeftFoldAffine

/-- The secp256k1 source field. -/
abbrev Fp := ZMod Secp256k1.p

/-- The four scalar coordinates in one literal System-(4) row. -/
structure ChainVars where
  x₁ : Fp
  x₂ : Fp
  x₃ : Fp
  x₄ : Fp
  deriving DecidableEq

/-- The three transition equations and terminal factor-base equation in one
literal System-(4) row.  This predicate is intentionally not defined through
`FactorBaseX` or `extendLeaf`. -/
def ChainEquations (u : ChainVars) : Prop :=
  u.x₂ = u.x₁ ^ 2 ∧
  u.x₃ = u.x₂ ^ 3 ∧
  u.x₄ = u.x₃ ^ 7 ∧
  1 - u.x₄ ^ 13441 = 0

/-- The unique transition-coordinate extension of a source coordinate. -/
def extendLeaf (a : Fp) : ChainVars :=
  ⟨a, a ^ 2, (a ^ 2) ^ 3, ((a ^ 2) ^ 3) ^ 7⟩

/-- One literal row is canonical exactly when its source coordinate satisfies
the factor-base root equation. -/
theorem chainEquations_iff (u : ChainVars) :
    ChainEquations u ↔
      u = extendLeaf u.x₁ ∧ u.x₁ ^ 564522 = 1 := by
  constructor
  · rintro ⟨h₂, h₃, h₄, hterminal⟩
    have hterminal' : u.x₄ ^ 13441 = 1 :=
      (sub_eq_zero.mp hterminal).symm
    have hpow : u.x₁ ^ 564522 = 1 := by
      rw [h₄, h₃, h₂] at hterminal'
      simpa only [← pow_mul] using hterminal'
    have hu : u = extendLeaf u.x₁ := by
      cases u with
      | mk x₁ x₂ x₃ x₄ =>
          simp only [extendLeaf] at h₂ h₃ h₄ ⊢
          subst x₂
          subst x₃
          subst x₄
          rfl
    exact ⟨hu, hpow⟩
  · rintro ⟨hu, hpow⟩
    have hcanonical : ChainEquations (extendLeaf u.x₁) := by
      refine ⟨rfl, rfl, rfl, ?_⟩
      rw [sub_eq_zero]
      change 1 = ((((u.x₁ ^ 2) ^ 3) ^ 7) ^ 13441)
      rw [← pow_mul, ← pow_mul, ← pow_mul]
      exact hpow.symm
    exact Eq.mpr (congrArg ChainEquations hu) hcanonical

/-- The literal sixteen-row direct System (4), including its target-bound
Semaev-2004 left-fold `f17` equation.  It is intentionally not defined through
the reduced factor-base subtype. -/
def DirectSystem4 (X : Fp) (u : Fin 16 → ChainVars) : Prop :=
  S17At (fun i => (u i).x₁) X = 0 ∧
  ∀ i, ChainEquations (u i)

/-- Exact elimination of all 48 transition coordinates at the level of
distinct solution sets. -/
noncomputable def directSolEquivReduced (X : Fp) :
    {u : Fin 16 → ChainVars // DirectSystem4 X u} ≃
      {x : Fin 16 → FactorBaseX //
        S17At (fun i => (x i).1) X = 0} where
  toFun u :=
    ⟨fun i =>
        ⟨(u.1 i).x₁,
          ((chainEquations_iff (u.1 i)).mp (u.2.2 i)).2⟩,
      u.2.1⟩
  invFun x :=
    ⟨fun i => extendLeaf (x.1 i).1,
      ⟨by simpa [extendLeaf] using x.2,
        fun i =>
          (chainEquations_iff (extendLeaf (x.1 i).1)).mpr
            ⟨rfl, (x.1 i).2⟩⟩⟩
  left_inv u := by
    apply Subtype.ext
    funext i
    exact ((chainEquations_iff (u.1 i)).mp (u.2.2 i)).1.symm
  right_inv x := by
    apply Subtype.ext
    funext i
    apply Subtype.ext
    rfl

/-! ## All internal projective branches remain present -/

/-- The independently transcribed target-specialized left-fold representative
vanishes exactly when the repository's complete stage-14 chart-polynomial
cover has a solution after injective base change to an algebraically closed
field.

Only the sixteen external values and target are fixed to affine charts.  The
fourteen internal witnesses still range over every affine/infinity mask, so
degree-drop and infinity branches are not discarded. -/
theorem S17At_eq_zero_iff_chartPolynomialCover_over
    {K : Type*} [Field K] [IsAlgClosed K]
    (phi : Fp →+* K) (hphi : Function.Injective phi)
    (x : Fin 16 → Fp) (X : Fp) :
    S17At x X = 0 ↔
      Ecdlp.FrozenProjectiveSemaev.FrozenChartPolynomialCover
        (fun i =>
          Ecdlp.FrozenProjectiveSemaev.mapProjectivePair
            phi hphi (projectiveLeaves x i))
        (Ecdlp.FrozenProjectiveSemaev.mapProjectivePair
          phi hphi (.affine X)) := by
  rw [S17At_eq_frozenSpecialize]
  exact
    Ecdlp.FrozenProjectiveSemaev.frozenRecS17_iff_chartPolynomialCover_over
      phi hphi (projectiveLeaves x) (.affine X)

end Ecdlp.M16DirectSystemRootBridge
