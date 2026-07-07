import Mathlib
import Ecdlp.Proved.PointEvaluation

/-!
# Weil layer B — distinct points are distinct closed points

`xyIdeal_ne_of_x_ne`: rational points on a Weierstrass curve with **different x-coordinates** give
**different maximal ideals** `⟨X−x, Y−y⟩` of the coordinate ring `F[E]` — i.e. they are different
closed points of the affine curve. This is the divisor-support **separation** the Weil pairing needs:
the points in a divisor `D_Q` chosen to compute `f_P(D_Q)` must avoid `P` and `O`, which requires
knowing distinct points are genuinely distinct closed points.

Proof: `XClass x₁ - XClass x₂ = algebraMap F F[E] (x₂ - x₁)` (both `XClass`es are the images of the
coordinate function `X − ·`, so their difference is the constant `x₂ − x₁`). When `x₁ ≠ x₂` that
constant is a **unit** of `F[E]`. If the two ideals coincided, both `XClass`es — hence their
difference — would lie in that ideal, forcing a unit into a maximal (proper) ideal: contradiction.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- **Distinct x-coordinates ⇒ distinct closed points.** For rational points `(x₁,y₁)` and
`(x₂,y₂)` on `W` with `x₁ ≠ x₂`, the maximal ideals `⟨X−x₁, Y−y₁⟩` and `⟨X−x₂, Y−y₂⟩` of `F[E]`
differ. -/
theorem xyIdeal_ne_of_x_ne {x₁ y₁ x₂ y₂ : F}
    (h₂ : W.Equation x₂ y₂) (hx : x₁ ≠ x₂) :
    XYIdeal W x₁ (C y₁) ≠ XYIdeal W x₂ (C y₂) := by
  intro heq
  have halg : algebraMap F W.CoordinateRing (x₂ - x₁) = mk W (C (C (x₂ - x₁))) := rfl
  have hdiff : XClass W x₁ - XClass W x₂ = algebraMap F W.CoordinateRing (x₂ - x₁) := by
    rw [halg]
    simp only [XClass, ← map_sub]
    congr 1
    simp only [map_sub]
    ring
  have hmem : algebraMap F W.CoordinateRing (x₂ - x₁) ∈ XYIdeal W x₂ (C y₂) := by
    rw [← hdiff]
    refine Ideal.sub_mem _ ?_ (Ideal.subset_span (Set.mem_insert _ _))
    rw [← heq]
    exact Ideal.subset_span (Set.mem_insert _ _)
  have hunit : IsUnit (algebraMap F W.CoordinateRing (x₂ - x₁)) :=
    (isUnit_iff_ne_zero.mpr (sub_ne_zero.mpr (Ne.symm hx))).map _
  exact (xyIdeal_isMaximal h₂).ne_top (Ideal.eq_top_of_isUnit_mem _ hmem hunit)

end Ecdlp.Weil
