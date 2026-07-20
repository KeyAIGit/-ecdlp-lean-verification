/-
# Point-evaluated ω-free x-coordinate difference identity (N7-uniform, odd-step brick)

The Silverman x-difference identity `φ_ψ_diff : φₙ·ψₘ² − φₘ·ψₙ² = ψ(m+n)·ψ(m−n)`
(`DivisionPolynomialEllSequence.lean`) is an identity in the bivariate ring `R[X][Y]`. This file
transports it to an arbitrary point `(x, y)` by the `evalEval` ring homomorphism, giving the
scalar form the **odd step** of the uniform multiplication-by-`n` carrier reduces to.

Concretely, for consecutive multiples `k•P, (k+1)•P` the secant `x`-coordinate `x((2k+1)•P)`
clears to Silverman's `x((2k+1)P) − x(P) = −ψ(2k+1)ψ₁/(ψ_{k+1}²ψ_k²)`, i.e. `φ_ψ_diff` at
`(m, n) = (k+1, k)` **evaluated at `P`** — exactly this lemma. It is the scalar identity the
open target's `odd_x_algebra` wall (`Ecdlp/Targets/n7_uniform_carrier_induction.lean`) consumes
once the `Carrier` y-coupling pins the two `y`-coordinates.

Curve-generic over any `CommRing`; pure `congrArg (evalEval x y)` + `simp` distribution over the
proved polynomial identity. No `native_decide`, no new axioms.
-/
import Mathlib
import Ecdlp.Proved.DivisionPolynomialEllSequence

namespace Ecdlp.Curve

open Polynomial

variable {R : Type*} [CommRing R] (W : WeierstrassCurve R)

/-- **`φ_ψ_diff` evaluated at a point `(x, y)`.** For all `m n : ℤ`,
`φₙ(P)·ψₘ(P)² − φₘ(P)·ψₙ(P)² = ψ(m+n)(P)·ψ(m−n)(P)`, where `·(P) = evalEval x y`. The scalar
(point-level) form of the ω-free x-coordinate difference identity — the odd-step reduction
target of the N7-uniform multiplication-by-`n` carrier. Follows from the `R[X][Y]` identity
`φ_ψ_diff` by applying the `evalEval` ring hom (`congrArg` + `evalEval_mul/sub/pow`). -/
theorem φ_ψ_diff_evalEval (x y : R) (m n : ℤ) :
    (W.φ n).evalEval x y * (W.ψ m).evalEval x y ^ 2
      - (W.φ m).evalEval x y * (W.ψ n).evalEval x y ^ 2
    = (W.ψ (m + n)).evalEval x y * (W.ψ (m - n)).evalEval x y := by
  have h := congrArg (Polynomial.evalEval x y) (φ_ψ_diff W m n)
  simpa only [evalEval_mul, evalEval_sub, evalEval_pow] using h

/-- **The three-term elliptic-net relation `ψ_isEllSequence` evaluated at a point `(x, y)`.**
For all `m n r : ℤ`,
`ψ(m+n)(P)·ψ(m−n)(P)·ψr(P)² = ψ(m+r)(P)·ψ(m−r)(P)·ψn(P)² − ψ(n+r)(P)·ψ(n−r)(P)·ψm(P)²`,
with `·(P) = evalEval x y`. The point-level form of the ω-free net relation (`ψ_isEllSequence`,
`DivisionPolynomialEllSequence.lean`) — the general index-arithmetic tool the even/odd steps of
the N7-uniform carrier use to relate `ψ` at `2k, 2k±1, 2k±2` to `ψ` at `k, k±1` (its `r = 1`
specialisation is `φ_ψ_diff_evalEval`). Same `congrArg (evalEval x y)` + `evalEval_mul`/`sub`/`pow`
distribution over the proved `R[X][Y]` identity. No `native_decide`, no new axioms. -/
theorem ψ_isEllSequence_evalEval (x y : R) (m n r : ℤ) :
    (W.ψ (m + n)).evalEval x y * (W.ψ (m - n)).evalEval x y * (W.ψ r).evalEval x y ^ 2
      = (W.ψ (m + r)).evalEval x y * (W.ψ (m - r)).evalEval x y * (W.ψ n).evalEval x y ^ 2
        - (W.ψ (n + r)).evalEval x y * (W.ψ (n - r)).evalEval x y * (W.ψ m).evalEval x y ^ 2 := by
  have h := congrArg (Polynomial.evalEval x y) (ψ_isEllSequence W m n r)
  simpa only [evalEval_mul, evalEval_sub, evalEval_pow] using h

end Ecdlp.Curve
