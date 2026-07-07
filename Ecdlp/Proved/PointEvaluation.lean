import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# Function evaluation at a rational point (Weil-pairing infrastructure, layer B)

The Weil pairing evaluates a rational function (the Miller function `f_P`) at points of the curve.
Mathlib v4.31 has **no** rational-function evaluation API — the coordinate ring `F[E]` is not even
known to be a Dedekind domain there, so the `HeightOneSpectrum` valuation/divisor apparatus does
not apply out of the box. This file builds the **first rungs** of that missing infrastructure: the
evaluation of a **regular** function (an element of the affine coordinate ring `F[E]`) at a
rational point `P = (x,y) ∈ E`, as a genuine ring homomorphism `F[E] →+* F`, and its extension to
**rational** functions regular at `P` via localization.

The construction rides on Mathlib's `CoordinateRing.quotientXYIdealEquiv`, the `F`-algebra
isomorphism `F[E] / ⟨X−x, Y−y⟩ ≃ F` (evaluation modulo the maximal ideal at `P`). Composing the
quotient map with that isomorphism gives point-evaluation. Structural facts proved: it is
**surjective** (every value in `F` is attained, so `P` is an `F`-rational point), its **kernel
is exactly the maximal ideal `⟨X−x, Y−y⟩`** of `P`, that ideal is **maximal** (`P` is a closed
point), the **residue field at `P` is `F`**, and the rational-function evaluation
`Localization.AtPrime ⟨X−x,Y−y⟩ →+* F` (rational functions regular at `P` → their value at `P`).

See `notes/FOUNDATIONS.md` (Weil sub-ladder, W3 evaluation half).
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

/-- **The ideal of a rational point is maximal** — `P` is a *closed point*. For `(x,y)` on the
curve, `⟨X−x, Y−y⟩` is a maximal ideal of `F[E]`, immediate from `F[E]/⟨X−x,Y−y⟩ ≃ F`
(`quotientXYIdealEquiv`) being a field. This is the prerequisite for localizing at `P` (the local
ring `F[E]_P`) to evaluate rational functions regular at `P`. -/
theorem xyIdeal_isMaximal {x y : F} (h : W.Equation x y) :
    (XYIdeal W x (C y)).IsMaximal :=
  Ideal.Quotient.maximal_of_isField _
    ((quotientXYIdealEquiv (W' := W) (x := x) (y := C y) h).toMulEquiv.isField (Field.toIsField F))

/-- **The residue field at a rational point `(x,y)` is `F`.** Composing Mathlib's bijection
`F[E]/⟨X−x,Y−y⟩ ≃ ResidueField ⟨X−x,Y−y⟩` (valid as the ideal is maximal) with `F[E]/⟨X−x,Y−y⟩ ≃ F`
(`quotientXYIdealEquiv`) identifies the residue field at `P` with the base field. This is the
**value field** of point-evaluation of rational functions. -/
noncomputable def residueFieldEquiv {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] :
    (XYIdeal W x (C y)).ResidueField ≃+* F := by
  haveI := xyIdeal_isMaximal h
  exact (RingEquiv.ofBijective _
      (Ideal.bijective_algebraMap_quotient_residueField (XYIdeal W x (C y)))).symm.trans
    (quotientXYIdealEquiv (W' := W) h).toRingEquiv

/-- **Evaluation of a rational function regular at `P`.** The local ring
`Localization.AtPrime ⟨X−x,Y−y⟩` is the ring of rational functions **regular at `P`**; this ring
hom sends such a function to its value at `P` in `F` (the residue map, followed by the residue
field `≃ F`). Extends `evalAt` from regular functions to rational functions regular at `P` — the
form the Weil pairing's Miller function `f_P` (which has zeros and poles) needs to be evaluated in.
-/
noncomputable def evalRatAt {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] :
    Localization.AtPrime (XYIdeal W x (C y)) →+* F :=
  (residueFieldEquiv h).toRingHom.comp
    (IsLocalRing.residue (Localization.AtPrime (XYIdeal W x (C y))))

/-- Evaluation of a rational function regular at `P` is **surjective** (every value in `F` is
attained: constants are regular everywhere). -/
theorem evalRatAt_surjective {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] :
    Function.Surjective (evalRatAt h) :=
  (residueFieldEquiv h).surjective.comp
    (IsLocalRing.residue_surjective (R := Localization.AtPrime (XYIdeal W x (C y))))

end Ecdlp.Weil
