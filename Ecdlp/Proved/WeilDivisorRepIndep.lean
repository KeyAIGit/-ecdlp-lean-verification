import Mathlib
import Ecdlp.Proved.WeilDivisorEval

/-!
# Weil ladder rung W3e-2: representative-independence of divisor evaluation `divEval`

The Miller function `f_P` of the Weil pairing is only determined **up to a unit** of the
coordinate ring: two functions generating the same power `(XYIdeal' h)ⁿ` differ by some
`u : F[E]ˣ` (`secp256k1_miller_function_unique`, rung W3, representative-independence half). For
the pairing value `eₙ` to be well defined, the divisor evaluation `divEval f_P (Q)−(O)` built in
W3e-1 (`WeilDivisorEval.lean`) must not depend on which representative is chosen. This file
quantifies exactly how the representative enters:

* `evalReg_smul_unit` — **pointwise scaling law**: if `u • f = g` for a unit `u` of `F[E]` and
  both `f, g` are regular at `P`, then `evalReg g = u(P) · evalReg f`. The unit contributes the
  single (nonzero, by `evalAt_unit_ne_zero`) factor `evalAt h u`;
* `divEval_smul_unit` — **divisor scaling law (unconditional)**: consequently
  `divEval g (Q)−(O) = (u(Q)/u(O)) · divEval f (Q)−(O)`. The unit ambiguity enters `divEval`
  through the single ratio `u(Q)/u(O)` of its values at the two points — nothing else;
* `divEval_smul_unit_eq` — **representative-independence, conditional**: if additionally the unit
  takes equal values at `Q` and `O` (`u(Q) = u(O)`), the ratio is `1` and
  `divEval g = divEval f`. The two evaluations agree exactly.

**Honest scope — the one remaining gap.** Full unconditional representative-independence would
follow from the fact that *every unit of the affine coordinate ring `F[E]` of an elliptic curve
is a nonzero constant of `F`* (so `u(Q) = u(O)` automatically). That "units are constants"
statement — equivalently, that `evalAt hQ (↑u) = evalAt hO (↑u)` for every `u : F[E]ˣ` — is **not
in the landed API** (Mathlib v4.31 has no lemma computing the unit group of
`WeierstrassCurve.Affine.CoordinateRing`), so it is carried here as an explicit hypothesis rather
than proved. `secp256k1_miller_eval_scaling` (`FunctionFieldEval.lean`) supplies only nonvanishing
`u(P) ≠ 0` at each point, not equality across points. The scaling laws above are the strongest
statements that follow unconditionally from the landed lemmas; `divEval_smul_unit_eq` and its
secp256k1 form isolate the missing "units-are-constants" input as a named hypothesis.

Curve-agnostic except the final secp256k1 theorems. No `native_decide`; no new axioms; fully
kernel-checked on top of `evalReg`/`divEval` and the presentation calculus of `FunctionFieldEval`.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- **Pointwise scaling law for `evalReg`.** If `g = u • f` for a unit `u` of the coordinate ring
and both `f` and `g` are regular at `P`, then the value of `g` at `P` is the value of `f` scaled
by the unit's value `u(P) = evalAt h u`:
`evalReg h hg = evalAt h u · evalReg h hf`. Proof: from a presentation `f = a/b` (`b(P) ≠ 0`),
`g = u • f = (u·a)/b` is a presentation of `g` with the **same** denominator, so both values are
computed by `evalReg_eq`, and the numerator scaling is exactly `evalFracAt_unit_mul`. -/
theorem evalReg_smul_unit {x y : F} (h : W.Equation x y) (u : (W.CoordinateRing)ˣ)
    {f g : W.FunctionField} (hug : u • f = g)
    (hf : RegularAt h f) (hg : RegularAt h g) :
    evalReg h hg = evalAt h (u : W.CoordinateRing) * evalReg h hf := by
  obtain ⟨a, b, hb, hab⟩ := id hf
  have hgf : g = algebraMap W.CoordinateRing W.FunctionField (u : W.CoordinateRing) * f := by
    rw [← hug]
    simp only [Units.smul_def, Algebra.smul_def]
  have hg_pres : g = algebraMap W.CoordinateRing W.FunctionField ((u : W.CoordinateRing) * a)
      / algebraMap W.CoordinateRing W.FunctionField b := by
    rw [hgf, hab, map_mul, mul_div_assoc]
  rw [evalReg_eq h hg hb hg_pres, evalReg_eq h hf hb hab]
  exact evalFracAt_unit_mul h u a b

/-- **Divisor scaling law (unconditional).** For `g = u • f` with `u` a unit of `F[E]`, and `f, g`
both regular at `Q` and at `O`, the divisor evaluation over `(Q) − (O)` scales by the **ratio** of
the unit's values at the two points:
`divEval g (Q)−(O) = (u(Q)/u(O)) · divEval f (Q)−(O)`. So the entire dependence of `divEval` on the
Miller representative is the single scalar `u(Q)/u(O)`. -/
theorem divEval_smul_unit {xQ yQ xO yO : F}
    (hQ : W.Equation xQ yQ) (hO : W.Equation xO yO)
    (u : (W.CoordinateRing)ˣ) {f g : W.FunctionField} (hug : u • f = g)
    (hfQ : RegularAt hQ f) (hfO : RegularAt hO f)
    (hgQ : RegularAt hQ g) (hgO : RegularAt hO g) :
    divEval hQ hO hgQ hgO
      = (evalAt hQ (u : W.CoordinateRing) / evalAt hO (u : W.CoordinateRing))
        * divEval hQ hO hfQ hfO := by
  simp only [divEval]
  rw [evalReg_smul_unit hQ u hug hfQ hgQ, evalReg_smul_unit hO u hug hfO hgO]
  ring

/-- **Representative-independence of `divEval` (conditional on the unit being constant).** If, in
addition to `g = u • f`, the unit takes the **same value at `Q` and at `O`**
(`u(Q) = u(O)` — the property that holds because units of the affine coordinate ring of an
elliptic curve are nonzero constants; see the honest-scope note), then the scaling ratio is `1`
and the two divisor evaluations agree: `divEval g (Q)−(O) = divEval f (Q)−(O)`. This is the
well-definedness statement the Weil pairing value `eₙ` requires of its Miller function. -/
theorem divEval_smul_unit_eq {xQ yQ xO yO : F}
    (hQ : W.Equation xQ yQ) (hO : W.Equation xO yO)
    (u : (W.CoordinateRing)ˣ) {f g : W.FunctionField} (hug : u • f = g)
    (hfQ : RegularAt hQ f) (hfO : RegularAt hO f)
    (hgQ : RegularAt hQ g) (hgO : RegularAt hO g)
    (hval : evalAt hQ (u : W.CoordinateRing) = evalAt hO (u : W.CoordinateRing)) :
    divEval hQ hO hgQ hgO = divEval hQ hO hfQ hfO := by
  rw [divEval_smul_unit hQ hO u hug hfQ hfO hgQ hgO, hval,
    div_self (evalAt_unit_ne_zero hO u), one_mul]

section Secp256k1

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Secp256k1: the Miller representative enters `divEval` only through `u(Q)/u(O)`.** For two
Miller functions `f, g` for the same torsion data — both generating the fractional ideal
`(XYIdeal' h)ⁿ` — regular at `Q` and `O`, there is a unit `u` of the coordinate ring with
`u • f = g` (`secp256k1_miller_function_unique`, rung W3) such that
`divEval g (Q)−(O) = (u(Q)/u(O)) · divEval f (Q)−(O)`. The unit is globally nonvanishing
(`evalAt_unit_ne_zero`), so the ratio is a well-defined nonzero scalar: switching Miller
representative rescales `divEval` by exactly this constant. -/
theorem secp256k1_divEval_miller_rep_scaling
    {xQ yQ xO yO : ZMod Secp256k1.p}
    (hQ : Ecdlp.Curve.secp256k1.toAffine.Equation xQ yQ)
    (hO : Ecdlp.Curve.secp256k1.toAffine.Equation xO yO)
    {x y : ZMod Secp256k1.p} (h : Ecdlp.Curve.secp256k1.toAffine.Nonsingular x y) (n : ℕ)
    (f g : Ecdlp.Curve.secp256k1.toAffine.FunctionField)
    (hf : (↑(CoordinateRing.XYIdeal' h ^ n) :
        Submodule Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
          Ecdlp.Curve.secp256k1.toAffine.FunctionField)
        = Submodule.span Ecdlp.Curve.secp256k1.toAffine.CoordinateRing {f})
    (hg : (↑(CoordinateRing.XYIdeal' h ^ n) :
        Submodule Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
          Ecdlp.Curve.secp256k1.toAffine.FunctionField)
        = Submodule.span Ecdlp.Curve.secp256k1.toAffine.CoordinateRing {g})
    (hfQ : RegularAt hQ f) (hfO : RegularAt hO f)
    (hgQ : RegularAt hQ g) (hgO : RegularAt hO g) :
    ∃ u : (Ecdlp.Curve.secp256k1.toAffine.CoordinateRing)ˣ, u • f = g ∧
      divEval hQ hO hgQ hgO
        = (evalAt hQ (u : Ecdlp.Curve.secp256k1.toAffine.CoordinateRing)
            / evalAt hO (u : Ecdlp.Curve.secp256k1.toAffine.CoordinateRing))
          * divEval hQ hO hfQ hfO := by
  obtain ⟨u, hu⟩ := secp256k1_miller_function_unique h n f g hf hg
  exact ⟨u, hu, divEval_smul_unit hQ hO u hu hfQ hfO hgQ hgO⟩

/-- **Secp256k1: representative-independence of `divEval` for Miller functions**, conditional on
the units-are-constants input. If every unit of the coordinate ring takes equal values at `Q` and
`O` (`hunit` — true because such units are nonzero constants, but not yet in the landed API), then
any two Miller functions `f, g` for the same torsion data, regular at `Q` and `O`, give the same
divisor evaluation: `divEval g (Q)−(O) = divEval f (Q)−(O)`. This is the exact well-definedness the
Weil pairing `eₙ` needs; the single remaining input `hunit` is the open "units of `F[E]` are
constants" sub-lemma, isolated here as a hypothesis. -/
theorem secp256k1_divEval_miller_rep_indep
    {xQ yQ xO yO : ZMod Secp256k1.p}
    (hQ : Ecdlp.Curve.secp256k1.toAffine.Equation xQ yQ)
    (hO : Ecdlp.Curve.secp256k1.toAffine.Equation xO yO)
    {x y : ZMod Secp256k1.p} (h : Ecdlp.Curve.secp256k1.toAffine.Nonsingular x y) (n : ℕ)
    (f g : Ecdlp.Curve.secp256k1.toAffine.FunctionField)
    (hf : (↑(CoordinateRing.XYIdeal' h ^ n) :
        Submodule Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
          Ecdlp.Curve.secp256k1.toAffine.FunctionField)
        = Submodule.span Ecdlp.Curve.secp256k1.toAffine.CoordinateRing {f})
    (hg : (↑(CoordinateRing.XYIdeal' h ^ n) :
        Submodule Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
          Ecdlp.Curve.secp256k1.toAffine.FunctionField)
        = Submodule.span Ecdlp.Curve.secp256k1.toAffine.CoordinateRing {g})
    (hfQ : RegularAt hQ f) (hfO : RegularAt hO f)
    (hgQ : RegularAt hQ g) (hgO : RegularAt hO g)
    (hunit : ∀ v : (Ecdlp.Curve.secp256k1.toAffine.CoordinateRing)ˣ,
        evalAt hQ (v : Ecdlp.Curve.secp256k1.toAffine.CoordinateRing)
          = evalAt hO (v : Ecdlp.Curve.secp256k1.toAffine.CoordinateRing)) :
    divEval hQ hO hgQ hgO = divEval hQ hO hfQ hfO := by
  obtain ⟨u, hu⟩ := secp256k1_miller_function_unique h n f g hf hg
  exact divEval_smul_unit_eq hQ hO u hu hfQ hfO hgQ hgO (hunit u)

end Secp256k1

end Ecdlp.Weil
