import Mathlib
import Ecdlp.Proved.PointEvaluation

/-!
# Weil-pairing rung W3 (evaluation half): the nonvanishing criterion at a point

The Weil pairing evaluates a Miller function `f_P` at points of a divisor `D_Q`, and needs to know
*where `f_P` is regular and nonzero* — the points where the value is a genuine element of `𝔽_p` and
not `0`/`∞`. `PointEvaluation.lean` built `evalRatAt : F[E]_P →+* F`, the value at `P` of a
rational function regular there (localization at the maximal ideal `⟨X−x, Y−y⟩`). This file pins
down its **zero locus**, the last algebraic fact the evaluation step needs:

* `evalRatAt_eq_zero_iff` — a rational function regular at `P` **vanishes at `P` iff it lies in the
  maximal ideal** of the local ring `F[E]_P` (the functions with a zero at `P`).
* `evalRatAt_ne_zero_iff_isUnit` — equivalently, it is **nonzero at `P` iff it is a unit** of
  `F[E]_P`. This is the nonvanishing criterion: `f_P` may be evaluated to a nonzero value exactly at
  the points where it is a unit of the local ring — i.e. off its zero/pole support.

Both are immediate from `evalRatAt = residueFieldEquiv ∘ residue`: the residue map's kernel is the
maximal ideal, the residue-field iso is injective, and a local ring's non-units are exactly its
maximal ideal. Curve-agnostic (any Weierstrass curve over a field, any rational point).

**Honest scope.** This completes the *evaluation-at-a-point* half of rung W3 — the value and its
zero locus. It does **not** build `f_P(D_Q)` (evaluation at a whole divisor) or Weil reciprocity
`f(div g) = g(div f)` (rung W4), which remain genuine Mathlib gaps (`notes/FOUNDATIONS.md`). It is,
however, an independently reusable piece of the missing rational-function-evaluation API and is
PR-able toward Mathlib on its own. No new axioms; fully kernel-checked.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- **Zero locus of point-evaluation.** A rational function regular at `P = (x,y)` vanishes at `P`
iff it lies in the maximal ideal of the local ring `F[E]_P` — i.e. iff it is a non-unit with a
genuine zero at `P`. Immediate from `evalRatAt = residueFieldEquiv ∘ residue`: the residue-field
iso is injective, so `evalRatAt r = 0 ↔ residue r = 0 ↔ r ∈ 𝔪`. -/
theorem evalRatAt_eq_zero_iff {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime]
    (r : Localization.AtPrime (XYIdeal W x (C y))) :
    evalRatAt h r = 0 ↔
      r ∈ IsLocalRing.maximalIdeal (Localization.AtPrime (XYIdeal W x (C y))) := by
  have hcomp : evalRatAt h r
      = residueFieldEquiv h (IsLocalRing.residue (Localization.AtPrime (XYIdeal W x (C y))) r) :=
    rfl
  rw [hcomp, map_eq_zero_iff _ (residueFieldEquiv h).injective]
  exact Ideal.Quotient.eq_zero_iff_mem

/-- **Nonvanishing criterion.** A rational function regular at `P` is **nonzero at `P` iff it is a
unit** of the local ring `F[E]_P`. This is exactly the condition under which a Miller function may
be evaluated at `P` to a nonzero value in `𝔽_p` — the points off its zero/pole support. From
`evalRatAt_eq_zero_iff` and the local-ring fact that non-units are precisely the maximal ideal. -/
theorem evalRatAt_ne_zero_iff_isUnit {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime]
    (r : Localization.AtPrime (XYIdeal W x (C y))) :
    evalRatAt h r ≠ 0 ↔ IsUnit r := by
  rw [ne_eq, evalRatAt_eq_zero_iff]
  exact IsLocalRing.not_mem_maximalIdeal

end Ecdlp.Weil
