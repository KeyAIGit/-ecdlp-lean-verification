import Mathlib
import Ecdlp.Proved.WeilDivisorClass

/-!
# Weil-pairing rung W3 (representative-independence) — OPEN TARGET

The Weil pairing `eₙ(P,Q)` is built from the Miller function `f_P` (rung W2,
`secp256k1_miller_function_exists`): a generator of the principal fractional ideal
`(XYIdeal' h)ⁿ`. For the pairing to be **well defined**, its value must not depend on *which*
generator is chosen — so we need: any two Miller functions for the same `(P, n)` differ by a
**unit** of the coordinate ring `F[secp256k1]`.

This is the representative-independence half of W3. (The other half — evaluating `f_P` at a
divisor — needs a rational-function evaluation API that Mathlib v4.31 lacks.)

**This file is an open target (one `sorry`); it is NOT imported from `Ecdlp.lean` and NOT gated.**
-/

namespace Ecdlp.Weil

open WeierstrassCurve.Affine WeierstrassCurve.Affine.Point

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **W3 (representative-independence): the Miller function is unique up to a unit.** If `f` and
`g` both generate the principal fractional ideal `(XYIdeal' h)ⁿ` (as submodules of the function
field), then they differ by a unit of the coordinate ring: `∃ u : F[secp256k1]ˣ, u • f = g`. -/
theorem secp256k1_miller_function_unique
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
    ∃ u : (Ecdlp.Curve.secp256k1.toAffine.CoordinateRing)ˣ, u • f = g := by
  exact Submodule.span_singleton_eq_span_singleton.mp (hf.symm.trans hg)

end Ecdlp.Weil
