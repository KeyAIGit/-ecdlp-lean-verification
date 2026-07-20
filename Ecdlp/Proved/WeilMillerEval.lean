import Mathlib
import Ecdlp.Proved.WeilDivisorEval

/-!
# Weil ladder rung W3e-3: the domain of the raw pairing value + the `divEval` unit law

The raw Weil-pairing evaluation is `divEval f_P ((A) − (B))` for a Miller function `f_P` and two
points `A, B` **off the support of `div f_P`**. This file closes the still-reachable part of the
W3-evaluation scaffolding — the *domain* on which that value is defined, and the last basic-algebra
law of `divEval`:

* `regularAt_one` / `evalReg_one` / `divEval_one` — the **unit law**: `divEval 1 ((A)−(B)) = 1`.
  Together with `divEval_mul` (W3e-1) this makes `divEval` a monoid homomorphism on the functions
  regular at both `A` and `B`;
* `secp256k1_miller_jointly_regular` — the **support-disjointness bridge**: a Miller function `f`
  for `(P, n)` has a fixed presentation `a/b`, and at **any two** points `A, B` where the single
  denominator `b` does not vanish (i.e. `A, B` off the zero locus of `b`, hence off `supp(div f)`),
  `f` is regular at *both*. This is exactly the joint-regularity hypothesis `divEval hA hB` consumes,
  produced from one geometric condition — so on such `A, B` the raw evaluation is defined, is
  multiplicative in `f` (`divEval_mul`), and is independent of the Miller representative
  (`divEval_smul_unit_eq` / `secp256k1_divEval_miller_rep_indep`, W3e-2, under the units-are-constants
  hypothesis).

**Honest scope.** This packages the *domain and algebra* of the raw evaluation; it does **not**
assemble the Weil pairing `eₙ(P, Q)` itself. That assembly evaluates `f_P` at a divisor equivalent to
`(Q) − (O)` supported away from `{P, O}` (the base point `O` lies in `supp(div f_P)`, so `f_P` is not
regular at `O`), and relating the shifted evaluation back to `(Q) − (O)` requires **Weil reciprocity
(rung W4)** — a frozen Mathlib no-go (`BARRIERS.md` §B3). W3e-4/W4/W5 stay parked behind it.

Curve-agnostic except the final secp256k1 bridge. No `native_decide`; no new axioms; fully
kernel-checked on top of the `evalReg`/`divEval` layer.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- The constant `1` is regular at every point (presentation `1 = 1/1`, denominator `1 ≠ 0`). -/
theorem regularAt_one {x y : F} (h : W.Equation x y) :
    RegularAt h (1 : W.FunctionField) :=
  ⟨1, 1, by rw [map_one]; exact one_ne_zero, by simp only [map_one, div_one]⟩

/-- **The value of the constant `1` at a point is `1`.** Independent of the regularity witness, via
`evalReg_eq` on the presentation `1 = 1/1`. -/
theorem evalReg_one {x y : F} (h : W.Equation x y) (h1 : RegularAt h (1 : W.FunctionField)) :
    evalReg h h1 = 1 := by
  have hb : evalAt h (1 : W.CoordinateRing) ≠ 0 := by rw [map_one]; exact one_ne_zero
  have hab : (1 : W.FunctionField)
      = algebraMap W.CoordinateRing W.FunctionField 1
        / algebraMap W.CoordinateRing W.FunctionField 1 := by
    simp only [map_one, div_one]
  rw [evalReg_eq h h1 hb hab, evalFracAt_one, map_one]

/-- **The unit law for divisor evaluation:** `divEval 1 ((A)−(B)) = 1`. With `divEval_mul` (W3e-1),
`divEval` is a monoid homomorphism on the functions regular at both `A` and `B`. -/
theorem divEval_one {xA yA xB yB : F}
    (hA : W.Equation xA yA) (hB : W.Equation xB yB)
    (h1A : RegularAt hA (1 : W.FunctionField)) (h1B : RegularAt hB (1 : W.FunctionField)) :
    divEval hA hB h1A h1B = 1 := by
  simp only [divEval]
  rw [evalReg_one hA h1A, evalReg_one hB h1B, div_one]

section Secp256k1

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **W3e-3: support-disjointness ⇒ the Miller function is jointly regular at the evaluation
points.** A Miller function `f` for the torsion data `(P, n)` on secp256k1 — a generator of
`(XYIdeal' h)ⁿ`, as produced by rung W2 — has a fixed presentation `a/b`
(`secp256k1_miller_function_regularAt`). At **any two** rational points `A = (xA, yA)`,
`B = (xB, yB)` where the single denominator `b` does not vanish (equivalently: `A, B` lie off the
zero locus of `b`, hence off `supp(div f)`), `f` is regular at both. This is precisely the
joint-regularity hypothesis the raw evaluation `divEval hA hB` consumes — obtained from one
geometric condition — so on such `A, B` the raw pairing value `divEval f ((A)−(B))` is defined,
multiplicative (`divEval_mul`) and Miller-representative-independent
(`secp256k1_divEval_miller_rep_indep`). -/
theorem secp256k1_miller_jointly_regular
    {x y : ZMod Secp256k1.p} (h : Ecdlp.Curve.secp256k1.toAffine.Nonsingular x y) (n : ℕ)
    (f : Ecdlp.Curve.secp256k1.toAffine.FunctionField)
    (hf : (↑(CoordinateRing.XYIdeal' h ^ n) :
        Submodule Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
          Ecdlp.Curve.secp256k1.toAffine.FunctionField)
        = Submodule.span Ecdlp.Curve.secp256k1.toAffine.CoordinateRing {f}) :
    ∃ a b : Ecdlp.Curve.secp256k1.toAffine.CoordinateRing, b ≠ 0 ∧
      f = algebraMap Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
            Ecdlp.Curve.secp256k1.toAffine.FunctionField a
        / algebraMap Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
            Ecdlp.Curve.secp256k1.toAffine.FunctionField b ∧
      ∀ {xA yA xB yB : ZMod Secp256k1.p}
        (hA : Ecdlp.Curve.secp256k1.toAffine.Equation xA yA)
        (hB : Ecdlp.Curve.secp256k1.toAffine.Equation xB yB),
        evalAt hA b ≠ 0 → evalAt hB b ≠ 0 →
        RegularAt hA f ∧ RegularAt hB f := by
  obtain ⟨a, b, hb, hab, hreg⟩ := secp256k1_miller_function_regularAt h n f hf
  exact ⟨a, b, hb, hab, fun hA hB hbA hbB => ⟨hreg hA hbA, hreg hB hbB⟩⟩

end Secp256k1

end Ecdlp.Weil
