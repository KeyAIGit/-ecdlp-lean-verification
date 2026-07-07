import Mathlib
import Ecdlp.Proved.PointEvaluation

/-!
# Weil layer B — distinct points are distinct closed points (iteration/scratch)

`x₁ ≠ x₂ → XYIdeal W x₁ (C y₁) ≠ XYIdeal W x₂ (C y₂)`: rational points with different x-coordinates
give **different maximal ideals** of `F[E]`. This is the divisor-support separation the Weil pairing
needs (points of `D_Q` must avoid `P`, `O`).

Idea: `XClass x₁ - XClass x₂ = algebraMap F F[E] (x₂ - x₁)` is a unit when `x₁ ≠ x₂`; if the two
ideals coincided, both `XClass`es (hence their difference) would lie in that ideal, forcing a unit
into a maximal (proper) ideal — contradiction.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

theorem xyIdeal_ne_of_x_ne {x₁ y₁ x₂ y₂ : F}
    (h₂ : W.Equation x₂ y₂) (hx : x₁ ≠ x₂) :
    XYIdeal W x₁ (C y₁) ≠ XYIdeal W x₂ (C y₂) := by
  intro heq
  have hdiff : XClass W x₁ - XClass W x₂ = algebraMap F W.CoordinateRing (x₂ - x₁) := by
    simp only [XClass, ← map_sub]
    congr 1
    C_simp
    ring1
  have hmem : algebraMap F W.CoordinateRing (x₂ - x₁) ∈ XYIdeal W x₂ (C y₂) := by
    rw [← hdiff]
    refine Ideal.sub_mem _ ?_ (Ideal.subset_span (Set.mem_insert _ _))
    rw [← heq]
    exact Ideal.subset_span (Set.mem_insert _ _)
  have hunit : IsUnit (algebraMap F W.CoordinateRing (x₂ - x₁)) :=
    (isUnit_iff_ne_zero.mpr (sub_ne_zero.mpr (Ne.symm hx))).map _
  exact (xyIdeal_isMaximal h₂).ne_top (Ideal.eq_top_of_isUnit_mem _ hmem hunit)

end Ecdlp.Weil
