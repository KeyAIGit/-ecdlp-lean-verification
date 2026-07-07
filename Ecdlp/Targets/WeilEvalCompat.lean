import Mathlib
import Ecdlp.Proved.PointEvaluation

/-!
# Weil layer B — evaluation compatibility (iteration/scratch, not yet promoted)

`evalRatAt` genuinely **extends** `evalAt`: for a *regular* function `r ∈ F[E]`, its value as a
rational function regular at `P` (image under the localization map, then `evalRatAt`) equals its
direct value `evalAt h r`. This is the correctness certificate for `evalRatAt` before it is used to
evaluate the Miller function; it is self-contained (no divisor-support machinery).

Iteration file under `Targets/` (gate-excluded) while the proof is developed on the warm server
loop. Promote to `Proved/` only once the kernel accepts it with no `sorry`.
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
  sorry

end Ecdlp.Weil
