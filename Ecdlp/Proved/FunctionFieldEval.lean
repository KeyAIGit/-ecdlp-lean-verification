import Mathlib
import Ecdlp.Proved.PointEvaluation
import Ecdlp.Proved.EvalRatAtCompat
import Ecdlp.Proved.WeilDivisorClass

/-!
# Weil rung W3, evaluation half (completion): evaluating presented fractions at a point

The Weil pairing evaluates the Miller function `f_P` — an element of the **function field**
`F(E) = Frac F[E]` (`WeilDivisorClass`, rung 2) — at rational points. The evaluation layers built
so far are `evalAt : F[E] →+* F` (regular functions, `PointEvaluation`), its localized extension
`evalRatAt : F[E]_P →+* F` with kernel/nonvanishing control (`EvalRatAtNonvanishing`), and the
compatibility `evalRatAt ∘ algebraMap = evalAt` (`EvalRatAtCompat`). What was missing is the form
evaluation actually takes in Miller's algorithm: a rational function is *presented* as a quotient
`a/b` of two regular functions with `b(P) ≠ 0`, and its value at `P` is `a(P)/b(P)`. This file
builds that calculus **on the presentation side**:

* `evalFracAt h a b := evalAt h a / evalAt h b` — total, with the standard Mathlib junk value
  `0` when `b(P) = 0`; every substantive lemma carries the explicit nonvanishing hypothesis;
* `evalFracAt_well_defined` — **independence of the presentation**: if `a₁ * b₂ = a₂ * b₁` in
  `F[E]` (the two fractions are equal in the function field) and both denominators are nonzero at
  `P`, the two values agree. Cross-multiplication happens in `F` through the ring hom `evalAt`;
* `evalFracAt_one` — agreement with `evalAt` on regular functions (denominator `1`);
* `evalFracAt_mul` — multiplicativity in numerator and denominator simultaneously, the identity
  Miller-loop products of line functions consume;
* `evalAt_unit_ne_zero` / `evalFracAt_unit_mul` — a unit of `F[E]` is nonzero at **every**
  rational point, and scales `evalFracAt` multiplicatively;
* `evalRatAt_eq_evalFracAt` — the weld to the localization layer: whenever `r ∈ F[E]_P` satisfies
  `(algebraMap b) * r = algebraMap a` with `b(P) ≠ 0`, the residue-map value `evalRatAt h r`
  equals the presented value `a(P)/b(P)`. So the two evaluation routes agree on their common
  domain, with no fraction-field surjectivity API needed;
* `secp256k1_miller_eval_scaling` — the Miller-layer connection: two Miller functions `f, g` for
  the same torsion data differ by a unit `u` of the coordinate ring (`WeilDivisorClass`, rung 3)
  **and** `u` evaluates to a nonzero constant at every rational point of secp256k1. The
  representative ambiguity of `f_P` is a globally nonvanishing factor — the well-definedness seed
  for the pairing value `eₙ`.

**Honest scope.** This completes the evaluation half of rung W3 at the level of *presented*
fractions. It does **not** prove that every element of `FunctionField` admits an `a/b`
presentation (fraction-ring surjectivity — `IsFractionRing`/`IsLocalization.mk'` API with no
compiled precedent in this repository; that extraction is the next rung), nor evaluation at whole
divisors `f_P(D_Q)`, nor Weil reciprocity (rung W4, `notes/FOUNDATIONS.md`). Curve-agnostic except
the final secp256k1 theorem. No new axioms; fully kernel-checked.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- **Value at `P` of a presented fraction `a/b` of regular functions**: `a(P)/b(P)`. Total, with
the standard Mathlib junk value `0` when the denominator vanishes at `P` — lemmas about it carry
the explicit hypothesis `evalAt h b ≠ 0`. This is the shape in which Miller's algorithm evaluates
the function `f_P`: as a product of line-function quotients, never as an abstract fraction-field
element. -/
noncomputable def evalFracAt {x y : F} (h : W.Equation x y) (a b : W.CoordinateRing) : F :=
  evalAt h a / evalAt h b

/-- Definitional unfolding of `evalFracAt`. -/
theorem evalFracAt_def {x y : F} (h : W.Equation x y) (a b : W.CoordinateRing) :
    evalFracAt h a b = evalAt h a / evalAt h b :=
  rfl

/-- **`evalFracAt` agrees with `evalAt` on regular functions**: a fraction with denominator `1`
evaluates to the numerator's value. Correctness certificate on the regular locus. -/
theorem evalFracAt_one {x y : F} (h : W.Equation x y) (a : W.CoordinateRing) :
    evalFracAt h a 1 = evalAt h a := by
  rw [evalFracAt_def, map_one, div_one]

/-- **Well-definedness: the value is independent of the presentation.** If two fractions
`a₁/b₁ = a₂/b₂` agree in the function field — witnessed by cross-multiplication
`a₁ * b₂ = a₂ * b₁` in the coordinate ring — and both denominators are nonzero at `P`, then the
presented values at `P` agree. The check happens entirely in `F`, transported through the ring
homomorphism `evalAt`; no domain hypothesis on `F[E]` is needed. This is the core lemma making
"evaluate `f_P` via any regular presentation" a well-posed operation. -/
theorem evalFracAt_well_defined {x y : F} (h : W.Equation x y)
    {a₁ b₁ a₂ b₂ : W.CoordinateRing} (hcross : a₁ * b₂ = a₂ * b₁)
    (hb₁ : evalAt h b₁ ≠ 0) (hb₂ : evalAt h b₂ ≠ 0) :
    evalFracAt h a₁ b₁ = evalFracAt h a₂ b₂ := by
  rw [evalFracAt_def, evalFracAt_def, div_eq_div_iff hb₁ hb₂, ← map_mul, ← map_mul, hcross]

/-- **Multiplicativity** of presented-fraction evaluation, in numerator and denominator
simultaneously: `(a₁a₂)/(b₁b₂)` evaluates to the product of the values. This is the identity the
Miller loop consumes when accumulating products of line-function quotients. Holds unconditionally
(junk values multiply correctly in a field). -/
theorem evalFracAt_mul {x y : F} (h : W.Equation x y) (a₁ b₁ a₂ b₂ : W.CoordinateRing) :
    evalFracAt h (a₁ * a₂) (b₁ * b₂) = evalFracAt h a₁ b₁ * evalFracAt h a₂ b₂ := by
  simp only [evalFracAt_def, map_mul]
  rw [div_mul_div_comm]

/-- **A unit of the coordinate ring is nonzero at every rational point.** Ring homomorphisms send
units to units, and units of the field `F` are the nonzero elements. This is what makes the
Miller representative's unit ambiguity harmless for evaluation. -/
theorem evalAt_unit_ne_zero {x y : F} (h : W.Equation x y) (u : (W.CoordinateRing)ˣ) :
    evalAt h (u : W.CoordinateRing) ≠ 0 :=
  isUnit_iff_ne_zero.mp (u.isUnit.map (evalAt h))

/-- Scaling the numerator by a unit of `F[E]` scales the presented value by the unit's (nonzero,
by `evalAt_unit_ne_zero`) value at `P`. -/
theorem evalFracAt_unit_mul {x y : F} (h : W.Equation x y)
    (u : (W.CoordinateRing)ˣ) (a b : W.CoordinateRing) :
    evalFracAt h ((u : W.CoordinateRing) * a) b
      = evalAt h (u : W.CoordinateRing) * evalFracAt h a b := by
  rw [evalFracAt_def, evalFracAt_def, map_mul, mul_div_assoc]

/-- **The two evaluation routes agree.** If a rational function `r` regular at `P` (an element of
the local ring `F[E]_P`) admits a presentation by regular functions `a, b` — witnessed
multiplicatively by `(algebraMap b) * r = algebraMap a` in `F[E]_P` — and the denominator is
nonzero at `P`, then the residue-map value `evalRatAt h r` equals the presented value
`a(P)/b(P) = evalFracAt h a b`. Welds this file's presentation calculus to the localization layer
(`PointEvaluation`/`EvalRatAtCompat`) without any fraction-ring surjectivity API: the presentation
is taken as data, not extracted. -/
theorem evalRatAt_eq_evalFracAt {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] (a b : W.CoordinateRing) (hb : evalAt h b ≠ 0)
    (r : Localization.AtPrime (XYIdeal W x (C y)))
    (hr : algebraMap W.CoordinateRing (Localization.AtPrime (XYIdeal W x (C y))) b * r
        = algebraMap W.CoordinateRing (Localization.AtPrime (XYIdeal W x (C y))) a) :
    evalRatAt h r = evalFracAt h a b := by
  rw [evalFracAt_def, eq_div_iff hb, mul_comm (evalRatAt h r) (evalAt h b),
    ← evalRatAt_algebraMap h b, ← evalRatAt_algebraMap h a, ← map_mul, hr]

section Secp256k1

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Miller-layer connection: the representative ambiguity of the Miller function is a globally
nonvanishing factor.** If `f` and `g` both generate the fractional ideal `(XYIdeal' h)ⁿ` — i.e.
both are Miller functions for the same torsion data on secp256k1 — then they differ by a unit `u`
of the coordinate ring (`secp256k1_miller_function_unique`, rung 3) **whose value at every
rational point of the curve is nonzero** (`evalAt_unit_ne_zero`). Consequently any evaluation
recipe for `f_P` built from `evalFracAt`/`evalRatAt` changes only by the nonzero constants
`evalAt h' u` when the Miller representative changes — the well-definedness seed for the Weil
pairing value `eₙ` (which quotients exactly this ambiguity away). What remains for full W3 is
extracting an `a/b` presentation of the abstract generator `f` itself (fraction-ring
surjectivity), deliberately out of scope here. -/
theorem secp256k1_miller_eval_scaling
    {x y : ZMod Secp256k1.p} (h : Ecdlp.Curve.secp256k1.toAffine.Nonsingular x y) (n : ℕ)
    (f g : Ecdlp.Curve.secp256k1.toAffine.FunctionField)
    (hf : (↑(CoordinateRing.XYIdeal' h ^ n) :
        Submodule Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
          Ecdlp.Curve.secp256k1.toAffine.FunctionField)
        = Submodule.span Ecdlp.Curve.secp256k1.toAffine.CoordinateRing {f})
    (hg : (↑(CoordinateRing.XYIdeal' h ^ n) :
        Submodule Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
          Ecdlp.Curve.secp256k1.toAffine.FunctionField)
        = Submodule.span Ecdlp.Curve.secp256k1.toAffine.CoordinateRing {g}) :
    ∃ u : (Ecdlp.Curve.secp256k1.toAffine.CoordinateRing)ˣ,
      u • f = g ∧
        ∀ {x' y' : ZMod Secp256k1.p} (h' : Ecdlp.Curve.secp256k1.toAffine.Equation x' y'),
          evalAt h' (u : Ecdlp.Curve.secp256k1.toAffine.CoordinateRing) ≠ 0 := by
  obtain ⟨u, hu⟩ := secp256k1_miller_function_unique h n f g hf hg
  refine ⟨u, hu, ?_⟩
  intro x' y' h'
  exact evalAt_unit_ne_zero h' u

end Secp256k1

end Ecdlp.Weil
