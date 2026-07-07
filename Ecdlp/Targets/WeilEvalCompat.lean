import Mathlib
import Ecdlp.Proved.PointEvaluation

/-!
# Weil layer B — evaluation compatibility

`evalRatAt` **extends** `evalAt`: for a *regular* function `r ∈ F[E]`, its value as a rational
function regular at `P` (image under the localization map, then `evalRatAt`) equals its direct value
`evalAt h r`. The correctness certificate for `evalRatAt` before it is used to evaluate the Miller
function `f_P`; self-contained (no divisor-support machinery).

Proof shape: both sides are *definitionally* `(quotientXYIdealEquiv h).toRingEquiv (…)` — unfolding
the `.comp` / `.toRingHom` / `.trans` structure is cheap. The two `rfl` steps `e1`, `e2` pin that
form so the outer equiv matches on both sides; `congr 1` then peels it, and the residue-vs-quotient
crux (`residue` of the localization = quotient by the point's maximal ideal, definitional) closes it.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- `evalRatAt` extends `evalAt`: evaluating the image of a regular function `r` in the local ring
`F[E]_P` equals evaluating `r` directly at `P`. -/
theorem evalRatAt_algebraMap {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] (r : W.CoordinateRing) :
    evalRatAt h (algebraMap W.CoordinateRing
        (Localization.AtPrime (XYIdeal W x (C y))) r) = evalAt h r := by
  haveI := xyIdeal_isMaximal h
  have e1 : evalRatAt h (algebraMap W.CoordinateRing
        (Localization.AtPrime (XYIdeal W x (C y))) r)
      = (quotientXYIdealEquiv h).toRingEquiv
          ((RingEquiv.ofBijective _
            (Ideal.bijective_algebraMap_quotient_residueField (XYIdeal W x (C y)))).symm
            (IsLocalRing.residue (Localization.AtPrime (XYIdeal W x (C y)))
              (algebraMap W.CoordinateRing (Localization.AtPrime (XYIdeal W x (C y))) r))) := rfl
  have e2 : evalAt h r
      = (quotientXYIdealEquiv h).toRingEquiv (Ideal.Quotient.mk (XYIdeal W x (C y)) r) := rfl
  rw [e1, e2]
  congr 1
  rw [RingEquiv.symm_apply_eq, RingEquiv.ofBijective_apply]
  rfl

end Ecdlp.Weil
