import Mathlib
import Ecdlp.Proved.FunctionFieldRegular

/-!
# OPEN TARGET — Weil ladder rung W3e-1: divisor evaluation `f(D)` for `D = (Q) − (O)`

The first evaluation-half rung of the Weil pairing (`notes/WEIL_LADDER.md`, W3e-1). Building
on the landed `evalReg` (the value at a point of a function regular there), define the value
of a function `f` at a degree-0 divisor `D = (Q) − (O)` as the ratio of point values, and
prove it is multiplicative in `f`. Multiplicativity is what makes `f_P(D_Q)` a homomorphism
`E → μₙ` in the eventual pairing.

This is an **open stem** (one `sorry`, excluded from the built base). Proof shape: unfold
`divEval` to `evalReg _ hf / evalReg _ hf`; the crux sub-lemma is `evalReg` multiplicativity
at a point — `evalReg h (f*g) = evalReg h f * evalReg h g` for `f, g` regular at `P` — which
follows from `evalReg_eq` + `evalFracAt_mul` (pick presentations `f=a₁/b₁`, `g=a₂/b₂` with
`bᵢ(P)≠0`, so `f*g = (a₁a₂)/(b₁b₂)` with `(b₁b₂)(P)≠0`). Then the two ratios recombine.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- Value of a function `f` at the degree-0 divisor `(Q) − (O)`: the ratio of the two point
values, defined when `f` is regular at both points (given by their curve equations). -/
noncomputable def divEval {xQ yQ xO yO : F}
    (hQ : W.Equation xQ yQ) (hO : W.Equation xO yO)
    {f : W.FunctionField} (hfQ : RegularAt hQ f) (hfO : RegularAt hO f) : F :=
  evalReg hQ hfQ / evalReg hO hfO

/-- **W3e-1: divisor evaluation is multiplicative in the function.** For `f, g` regular at
both `Q` and `O`, `divEval (f·g) = divEval f · divEval g`. -/
theorem divEval_mul {xQ yQ xO yO : F}
    (hQ : W.Equation xQ yQ) (hO : W.Equation xO yO)
    {f g : W.FunctionField}
    (hfQ : RegularAt hQ f) (hfO : RegularAt hO f)
    (hgQ : RegularAt hQ g) (hgO : RegularAt hO g)
    (hfgQ : RegularAt hQ (f * g)) (hfgO : RegularAt hO (f * g)) :
    divEval hQ hO hfgQ hfgO
      = divEval hQ hO hfQ hfO * divEval hQ hO hgQ hgO := by
  sorry

end Ecdlp.Weil
