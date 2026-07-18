import Mathlib
import Ecdlp.Proved.FunctionFieldRegular

/-!
# Weil ladder rung W3e-1: divisor evaluation `f(D)` for `D = (Q) − (O)`

The first evaluation-half rung of the Weil pairing (`notes/WEIL_LADDER.md`, W3e-1). On top of
the landed `evalReg` (the value at a point of a function regular there, `FunctionFieldRegular.lean`),
this file:

* proves **`evalReg` is multiplicative at a point** — `evalReg h (f*g) = evalReg h f · evalReg h g`
  for `f, g` regular at `P` — the pointwise homomorphism property;
* defines **`divEval`**, the value of `f` at the degree-0 divisor `(Q) − (O)` as the ratio of the
  two point values, and proves it is **multiplicative in the function**
  (`divEval (f·g) = divEval f · divEval g`).

Multiplicativity in `f` is exactly what makes `f_P(D_Q)` a homomorphism `E → μₙ` in the eventual
pairing `eₙ`. Pure-kernel: no `native_decide`; the arithmetic is ring/field algebra over the
coordinate-ring evaluation hom `evalAt : W.CoordinateRing →+* F` and the fraction field
`W.FunctionField`.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- **`evalReg` is multiplicative at a point.** For `f, g` regular at `P` (with `f·g` regular
there too), the value of the product is the product of the values. Proof: pick presentations
`f = a₁/b₁`, `g = a₂/b₂` with `bᵢ(P) ≠ 0`; then `f·g = (a₁a₂)/(b₁b₂)` with `(b₁b₂)(P) ≠ 0`, and
`evalReg` of each is the presented value (`evalReg_eq`), so the claim is `evalFracAt_mul`. -/
theorem evalReg_mul {x y : F} (h : W.Equation x y) {f g : W.FunctionField}
    (hf : RegularAt h f) (hg : RegularAt h g) (hfg : RegularAt h (f * g)) :
    evalReg h hfg = evalReg h hf * evalReg h hg := by
  have hf' := hf
  have hg' := hg
  obtain ⟨a₁, b₁, hb₁, hab₁⟩ := hf'
  obtain ⟨a₂, b₂, hb₂, hab₂⟩ := hg'
  have hbmul : evalAt h (b₁ * b₂) ≠ 0 := by rw [map_mul]; exact mul_ne_zero hb₁ hb₂
  have habmul : f * g = algebraMap W.CoordinateRing W.FunctionField (a₁ * a₂)
      / algebraMap W.CoordinateRing W.FunctionField (b₁ * b₂) := by
    rw [hab₁, hab₂, map_mul, map_mul]; ring
  rw [evalReg_eq h hf hb₁ hab₁, evalReg_eq h hg hb₂ hab₂,
      evalReg_eq h hfg hbmul habmul]
  exact evalFracAt_mul h a₁ b₁ a₂ b₂

/-- Value of a function `f` at the degree-0 divisor `(Q) − (O)`: the ratio of the two point
values, defined when `f` is regular at both points. -/
noncomputable def divEval {xQ yQ xO yO : F}
    (hQ : W.Equation xQ yQ) (hO : W.Equation xO yO)
    {f : W.FunctionField} (hfQ : RegularAt hQ f) (hfO : RegularAt hO f) : F :=
  evalReg hQ hfQ / evalReg hO hfO

/-- **W3e-1: divisor evaluation is multiplicative in the function.** For `f, g` regular at both
`Q` and `O`, `divEval (f·g) = divEval f · divEval g`. -/
theorem divEval_mul {xQ yQ xO yO : F}
    (hQ : W.Equation xQ yQ) (hO : W.Equation xO yO)
    {f g : W.FunctionField}
    (hfQ : RegularAt hQ f) (hfO : RegularAt hO f)
    (hgQ : RegularAt hQ g) (hgO : RegularAt hO g)
    (hfgQ : RegularAt hQ (f * g)) (hfgO : RegularAt hO (f * g)) :
    divEval hQ hO hfgQ hfgO
      = divEval hQ hO hfQ hfO * divEval hQ hO hgQ hgO := by
  simp only [divEval]
  rw [evalReg_mul hQ hfQ hgQ hfgQ, evalReg_mul hO hfO hgO hfgO]
  ring

end Ecdlp.Weil
