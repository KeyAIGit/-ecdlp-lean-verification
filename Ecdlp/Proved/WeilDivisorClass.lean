import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# Weil-pairing foundations, rung 1: torsion points ↔ principal divisors

The Weil pairing `eₙ : E[n] × E[n] → μₙ` is built on **divisors**: for `P ∈ E[n]` one takes a
rational function `f_P` with divisor `n·([P] − [O])`, which exists precisely because that
degree-0 divisor is **principal** — and principality of `n·([P] − [O])` is exactly `n • P = O`
(`P` is `n`-torsion). This file makes that first step precise and kernel-checked, on top of the
divisor-class machinery **already in Mathlib**.

Mathlib formalizes the elliptic-curve group law itself *through* the ideal class group of the
affine coordinate ring `F[W]` (`Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Point`,
`import …RingTheory.ClassGroup.Basic`): the **Abel–Jacobi map**
`toClass : W.Point →+ Additive (ClassGroup W.CoordinateRing)` sends `P` to the class of the ideal
`⟨X − x, Y − y⟩` — i.e. the class of the divisor `[P] − [O]` — and Mathlib proves it is an
**injective group homomorphism** (`toClass_injective`, `toClass_eq_zero`). This *is* the embedding
`E(F) ↪ Pic(F[W])`, the hard substrate the Weil construction sits on.

**What this rung proves.** Transporting `n`-torsion across that homomorphism:
`n • P = 0 ⟺ n • toClass P = 0`, i.e. `P` is `n`-torsion **iff its divisor class is `n`-torsion in
the class group** — iff `n·([P] − [O])` is principal. That principality is the existence
precondition for the Miller function `f_P` of the Weil pairing. The argument is curve-agnostic
(it uses only that `toClass` is an injective group hom, true for every elliptic curve); stated
here for secp256k1, whose `Point` carries the concrete `AddCommGroup` instance. **No new axioms;
fully kernel-checked.**

Honest scope: this is rung 1 of a long ladder (`notes/FOUNDATIONS.md`). The remaining rungs —
extracting `f_P` from principality, evaluating functions at divisors, Weil reciprocity, and
finally the bilinear non-degenerate `eₙ` into `μₙ` — are not yet built; some may meet genuine
Mathlib gaps. This node contributes the divisor-theoretic entry point and records that the
class-group substrate is already present upstream.
-/

namespace Ecdlp.Weil

open WeierstrassCurve.Affine WeierstrassCurve.Affine.Point

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Rung 1 — torsion ⟺ principal divisor class, for secp256k1.** A point `P` of secp256k1 is
`n`-torsion (`n • P = 0`) iff its Abel–Jacobi class `toClass P = [ [P] − [O] ]` is `n`-torsion in
the ideal class group of the coordinate ring `F[secp256k1]` — equivalently, iff the divisor
`n·([P] − [O])` is **principal** (its class is trivial). This is the divisor-theoretic
reformulation of `n`-torsion that the Weil pairing's Miller function requires, obtained by
transporting `n • (·)` across Mathlib's **injective** homomorphism `toClass` (`toClass_eq_zero` +
`map_nsmul`). The argument is curve-agnostic — it uses only that `toClass` is an injective group
hom, which Mathlib proves for every elliptic curve — but is stated here for secp256k1, whose
`Point` carries the required `AddCommGroup` instance concretely. -/
theorem secp256k1_torsion_iff_principal (P : Ecdlp.Curve.secp256k1.toAffine.Point) (n : ℕ) :
    n • P = 0 ↔ n • toClass P = 0 := by
  rw [← toClass_eq_zero (n • P), map_nsmul]

/-- **Rung 2 — the Miller function exists.** For a nonzero `n`-torsion point `P = (x,y)` of
secp256k1, there is a nonzero element `f_P` of the function field `F(secp256k1)` whose associated
fractional ideal is `(⟨X−x, Y−y⟩)ⁿ` — i.e. a **generator of the principal ideal** `(XYIdeal' h)ⁿ`.
This `f_P` is the **Miller function** of the Weil pairing: its divisor is `n·([P] − [O])`. It is
extracted from rung 1 (`secp256k1_torsion_iff_principal`): `n`-torsion makes the class
`(ClassGroup.mk (XYIdeal' h))ⁿ = ClassGroup.mk ((XYIdeal' h)ⁿ)` trivial, and Mathlib's
`ClassGroup.mk_eq_one_iff` turns a trivial class into a principal ideal, whose generator is `f_P`.
Rung W2 of the Weil-pairing sub-ladder (`notes/FOUNDATIONS.md`). -/
theorem secp256k1_miller_function_exists
    {x y : ZMod Secp256k1.p} (h : Ecdlp.Curve.secp256k1.toAffine.Nonsingular x y) (n : ℕ)
    (hn : n • Point.some x y h = 0) :
    ∃ f : Ecdlp.Curve.secp256k1.toAffine.FunctionField,
      (↑(CoordinateRing.XYIdeal' h ^ n) :
          Submodule Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
            Ecdlp.Curve.secp256k1.toAffine.FunctionField)
        = Submodule.span Ecdlp.Curve.secp256k1.toAffine.CoordinateRing {f} := by
  have hprin : (↑(CoordinateRing.XYIdeal' h ^ n) :
      Submodule Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
        Ecdlp.Curve.secp256k1.toAffine.FunctionField).IsPrincipal := by
    rw [← ClassGroup.mk_eq_one_iff, map_pow]
    have hcls : n • toClass (Point.some x y h) = 0 :=
      (secp256k1_torsion_iff_principal (Point.some x y h) n).mp hn
    have h2 := congrArg Additive.toMul hcls
    rwa [toMul_nsmul, toMul_zero] at h2
  exact hprin.principal

end Ecdlp.Weil
