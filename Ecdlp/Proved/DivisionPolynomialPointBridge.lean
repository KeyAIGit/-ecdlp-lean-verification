/-
# Point-evaluated univariate↔bivariate division-polynomial bridge (N7-uniform keystone)

The multiplication-by-`n` x-coordinate on the group is `x([n]•P) = Φₙ(x)/ΨSqₙ(x)`, stated with the
**univariate** `Φ, ΨSq : R[X]` (the objects whose degrees/leading coefficients Mathlib computes).
But the ω-free division-polynomial identities that drive the N7-uniform carrier
(`φ_ψ_diff_evalEval`, `ψ_isEllSequence_evalEval`, …) live in the **bivariate** `φ, ψ : R[X][Y]`
evaluated at a point. To connect the two — the keystone every algebra wall of
`Ecdlp/Targets/n7_uniform_carrier_induction.lean` reduces to — one needs, for a point `(x,y)` on
the curve,

  `(ΨSq n).eval x = (ψ n).evalEval x y ^ 2`   and   `(Φ n).eval x = (φ n).evalEval x y`.

Mathlib records these identities only in the **affine coordinate ring** `W.CoordinateRing`
(`mk_ψ_sq : mk W (ψ n)² = mk W (C (ΨSq n))`, `mk_φ`), and only as a **scalar `normEDS`** sequence
(`eval_ΨSq_eq_normEDS_sq`) — neither is the point-evaluated form. This file supplies it, by pushing
the coordinate-ring identities through Mathlib's ring homomorphism
`AdjoinRoot.evalEval h : W.CoordinateRing →+* R`, which is built **directly** from a proof
`h : W.polynomial.evalEval x y = 0` (definitionally `W.Equation x y`) and satisfies
`AdjoinRoot.evalEval h (mk W g) = g.evalEval x y`. A ring hom respects `^2`, `*`, and `C`, so
applying it to `mk_ψ_sq` / `mk_φ` collapses each to the scalar bridge in a few `simp` steps — no
`AdjoinRoot.mk_eq_mk`, no denominator-nonvanishing hypotheses. Curve-generic over any `CommRing`;
no `native_decide`, no new axioms.
-/
import Mathlib
import Ecdlp.Proved.MultiplicationXCoordinateRing

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {R : Type*} [CommRing R] (W : WeierstrassCurve R)

/-- **`ΨSqₙ.eval x = (ψₙ.evalEval x y)²` at a curve point.** The univariate `ΨSq n` (whose square
root is the bivariate `ψ n`) evaluated at `x` equals the square of `ψ n` evaluated at the point
`(x,y)` on the curve. The point-level form of the coordinate-ring identity `mk_ψ_sq`
(`MultiplicationXCoordinateRing.lean`), obtained by applying the point-evaluation ring hom
`AdjoinRoot.evalEval h` (a ring hom, so it commutes with `_ ^ 2` and `C`). The keystone the
N7-uniform carrier's x-conjuncts consume to move between `ΨSq`/`Φ` and `ψ`/`φ`. -/
theorem ΨSq_eval_eq_ψ_evalEval_sq {x y : R} (h : W.toAffine.Equation x y) (n : ℤ) :
    (W.ΨSq n).eval x = (W.ψ n).evalEval x y ^ 2 := by
  have h0 : W.toAffine.polynomial.evalEval x y = 0 := h
  have hbridge := congrArg (AdjoinRoot.evalEval h0) (mk_ψ_sq W n)
  simp only [map_pow, AdjoinRoot.evalEval_mk, Polynomial.evalEval_C] at hbridge
  exact hbridge.symm

/-- **`Φₙ.eval x = (φₙ.evalEval x y)` at a curve point.** The univariate numerator `Φ n` evaluated
at `x` equals the bivariate `φ n` evaluated at the point `(x,y)` on the curve. The point-level form
of Mathlib's coordinate-ring identity `mk_φ` (`mk W (φ n) = mk W (C (Φ n))`), obtained by applying
the point-evaluation ring hom `AdjoinRoot.evalEval h`. Together with `ΨSq_eval_eq_ψ_evalEval_sq`
this gives `x([n]•P) = Φₙ/ΨSqₙ = φₙ(P)/ψₙ(P)²`, the bridge the N7-uniform x-walls consume. -/
theorem Φ_eval_eq_φ_evalEval {x y : R} (h : W.toAffine.Equation x y) (n : ℤ) :
    (W.Φ n).eval x = (W.φ n).evalEval x y := by
  have h0 : W.toAffine.polynomial.evalEval x y = 0 := h
  have hbridge := congrArg (AdjoinRoot.evalEval h0) (mk_φ W n)
  simp only [AdjoinRoot.evalEval_mk, Polynomial.evalEval_C] at hbridge
  exact hbridge.symm

end Ecdlp.Curve
