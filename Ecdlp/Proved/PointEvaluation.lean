import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# Function evaluation at a rational point (Weil-pairing infrastructure, layer B)

The Weil pairing evaluates a rational function (the Miller function `f_P`) at points of the curve.
Mathlib v4.31 has **no** rational-function evaluation API — the coordinate ring `F[E]` is not even
known to be a Dedekind domain there, so the `HeightOneSpectrum` valuation/divisor apparatus does
not apply out of the box. This file builds the **first rung** of that missing infrastructure: the
evaluation of a **regular** function (an element of the affine coordinate ring `F[E]`) at a
rational point `P = (x,y) ∈ E`, as a genuine ring homomorphism `F[E] →+* F`.

The construction rides on Mathlib's `CoordinateRing.quotientXYIdealEquiv`, the `F`-algebra
isomorphism `F[E] / ⟨X−x, Y−y⟩ ≃ F` (evaluation modulo the maximal ideal at `P`). Composing the
quotient map with that isomorphism gives point-evaluation. Two structural facts are proved: it is
**surjective** (every value in `F` is attained, so `P` is an `F`-rational point) and its **kernel
is exactly the maximal ideal `⟨X−x, Y−y⟩`** of `P` — the regular functions vanishing at `P`.

This is regular-function evaluation only; extending it to rational functions regular at `P`
(needed to evaluate `f_P`, which has zeros/poles) is the next rung, via localization at the maximal
ideal — see `notes/FOUNDATIONS.md` (Weil sub-ladder, W3 evaluation half).
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- **Evaluation at a rational point** `(x,y) ∈ E` as a ring homomorphism `F[E] →+* F`: reduce a
regular function modulo the maximal ideal `⟨X−x, Y−y⟩` at `P`, then apply Mathlib's isomorphism
`F[E]/⟨X−x,Y−y⟩ ≃ F` (`quotientXYIdealEquiv`). Sends a regular function to its value at `P`. -/
noncomputable def evalAt {x y : F} (h : W.Equation x y) : W.CoordinateRing →+* F :=
  (quotientXYIdealEquiv (W' := W) (x := x) (y := C y) h).toRingEquiv.toRingHom.comp
    (Ideal.Quotient.mk (XYIdeal W x (C y)))

/-- Evaluation at a rational point is **surjective**: every value in `F` is attained (`P` is
`F`-rational). Composition of the surjective quotient map with the isomorphism. -/
theorem evalAt_surjective {x y : F} (h : W.Equation x y) :
    Function.Surjective (evalAt h) :=
  (quotientXYIdealEquiv (W' := W) (x := x) (y := C y) h).surjective.comp
    Ideal.Quotient.mk_surjective

/-- **The kernel of evaluation at `(x,y)` is exactly the maximal ideal `⟨X−x, Y−y⟩`** of the
point — the regular functions vanishing at `P`. -/
theorem evalAt_ker {x y : F} (h : W.Equation x y) :
    RingHom.ker (evalAt h) = XYIdeal W x (C y) := by
  rw [evalAt, RingHom.ker_equiv_comp, Ideal.mk_ker]

end Ecdlp.Weil
