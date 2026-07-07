import Mathlib
import Ecdlp.Proved.PointEvaluation

/-!
# Weil layer B — `evalRatAt` extends `evalAt`

`evalRatAt` (evaluation of a rational function regular at `P`, via the local ring `F[E]_P`) genuinely
**extends** `evalAt` (evaluation of a regular function): for a regular `r ∈ F[E]`, the value of its
image in `F[E]_P` equals its direct value at `P`. This is the correctness certificate for `evalRatAt`
before it is used to evaluate the Weil pairing's Miller function `f_P`, and it is self-contained
(no divisor-support machinery).

Proof: both sides are definitionally `(quotientXYIdealEquiv h).toRingEquiv (…)` — unfolding the
`.comp` / `.toRingHom` / `.trans` structure is cheap (`e1`, `e2`). After pinning that shared outer
equiv, `congr 1` peels it and the residue-vs-quotient crux closes it: the residue of the localization
at `P` coincides *definitionally* with the quotient by `P`'s maximal ideal.

See `notes/FOUNDATIONS.md` (Weil sub-ladder, evaluation layer).
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- **`evalRatAt` extends `evalAt`.** Evaluating the image of a regular function `r` in the local
ring `F[E]_P` equals evaluating `r` directly at `P`. -/
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
