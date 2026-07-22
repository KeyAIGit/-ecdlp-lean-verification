/-
# Point-evaluated ψ index-doubling recurrences (N7-uniform, index-reduction bricks)

Mathlib's division-polynomial index-doubling recurrences `ψ_even` and `ψ_odd` express `ψ` at an
even/odd index `2m`, `2m+1` in terms of `ψ` at the neighbouring indices `m-2 … m+2`. They are the
tool the N7-uniform carrier's step lemmas use to relate `ψ` at `2k, 2k±1, 2k±2` (the indices the
even/odd steps produce) back to `ψ` at `k, k±1, k±2` (the indices the induction hypothesis
constrains). This file transports both to an arbitrary point `(x, y)` by the `evalEval` ring
homomorphism — the scalar (point-level) forms the step assemblies consume.

Curve-generic over any `CommRing`; pure `congrArg (evalEval x y)` + `simp` distribution over the
Mathlib polynomial identities `ψ_even`/`ψ_odd`, the exact idiom of the point-evaluated transport trio
in `DivisionPolynomialPointDiff.lean`. No `native_decide`, no new axioms. (Together with
`φ_ψ_diff_evalEval`, `ψ_isEllSequence_evalEval`, `ψ_succ_mul_ψ_pred_evalEval` and the bridges
`ΨSq_eval_eq_ψ_evalEval_sq`, `Φ_eval_eq_φ_evalEval`, this completes the point-evaluated
division-polynomial recurrence toolkit for the N7-uniform build.)
-/
import Mathlib
import Ecdlp.Proved.DivisionPolynomialEllSequence

namespace Ecdlp.Curve

open Polynomial

variable {R : Type*} [CommRing R] (W : WeierstrassCurve R)

/-- **`ψ_even` evaluated at a point `(x, y)`.** For all `m : ℤ`,
`ψ(2m)(P)·ψ₂(P) = ψ(m−1)(P)²·ψm(P)·ψ(m+2)(P) − ψ(m−2)(P)·ψm(P)·ψ(m+1)(P)²`, with `·(P) = evalEval x y`.
The point-level form of Mathlib's even index-doubling recurrence `ψ_even`. The `ψ₂` factor on the
left becomes `2y` at a point of secp256k1 (`secp256k1_psi2_evalEval`). The even-step index reduction
`2k ↦ k, k±1, k±2` the N7-uniform carrier consumes. Follows from `ψ_even` by applying the `evalEval`
ring hom (`congrArg` + `evalEval_mul/sub/pow`). -/
theorem ψ_even_evalEval (x y : R) (m : ℤ) :
    (W.ψ (2 * m)).evalEval x y * W.ψ₂.evalEval x y
      = (W.ψ (m - 1)).evalEval x y ^ 2 * (W.ψ m).evalEval x y * (W.ψ (m + 2)).evalEval x y
        - (W.ψ (m - 2)).evalEval x y * (W.ψ m).evalEval x y * (W.ψ (m + 1)).evalEval x y ^ 2 := by
  have h := congrArg (Polynomial.evalEval x y) (W.ψ_even m)
  simpa only [evalEval_mul, evalEval_sub, evalEval_pow] using h

/-- **`ψ_odd` evaluated at a point `(x, y)`.** For all `m : ℤ`,
`ψ(2m+1)(P) = ψ(m+2)(P)·ψm(P)³ − ψ(m−1)(P)·ψ(m+1)(P)³`, with `·(P) = evalEval x y`. The point-level
form of Mathlib's odd index-doubling recurrence `ψ_odd`. The odd-step index reduction
`2k+1 ↦ k, k±1, k+2` the N7-uniform carrier consumes. Follows from `ψ_odd` by applying the `evalEval`
ring hom (`congrArg` + `evalEval_mul/sub/pow`). -/
theorem ψ_odd_evalEval (x y : R) (m : ℤ) :
    (W.ψ (2 * m + 1)).evalEval x y
      = (W.ψ (m + 2)).evalEval x y * (W.ψ m).evalEval x y ^ 3
        - (W.ψ (m - 1)).evalEval x y * (W.ψ (m + 1)).evalEval x y ^ 3 := by
  have h := congrArg (Polynomial.evalEval x y) (W.ψ_odd m)
  simpa only [evalEval_mul, evalEval_sub, evalEval_pow] using h

end Ecdlp.Curve
