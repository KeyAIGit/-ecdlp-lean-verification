import Mathlib
import Ecdlp.Proved.GlvEndomorphism
import Ecdlp.Proved.GlvHom
import Ecdlp.Proved.GlvMonoidHom
import Ecdlp.Proved.GlvCubeRelation

/-!
# The GLV endomorphism satisfies its minimal polynomial as an *operator* identity

`secp256k1_glv_cube_relation` (`Ecdlp/Proved/GlvCubeRelation.lean`) proves the primitive
cube-root-of-unity relation **pointwise**:

  `glvPoint (glvPoint P) + glvPoint P + P = 0`   for every point `P`.

Here we upgrade that pointwise fact to a single **operator identity** between bundled
additive endomorphisms of the secp256k1 point group:

  `glvHom ∘ glvHom + glvHom + id = 0`   in `End(E)`.

This is the honest "`φ² + φ + 1 = 0` in the endomorphism ring" statement: the GLV
endomorphism `φ = glvHom` is annihilated by its minimal polynomial `X² + X + 1`, so it is
a primitive cube root of unity in `End(E)` — the complex-multiplication-by-`ℤ[ζ₃]`
structure of the `j = 0` curve, now expressed as an equation between first-class Mathlib
`AddMonoidHom`s (it composes with the kernel/image/iterate API, unlike a pointwise `∀`).

**Scope, unchanged.** This is a statement in `End(E)`; it does **not** assert that `glvHom`
acts as scalar multiplication by the GLV eigenvalue `λ` on `⟨G⟩` (`glvHom G = λ • G`),
which stays gated on point counting (`notes/GLV_LAMBDA.md`, `notes/GLV_HOMOMORPHISM.md`).
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **`φ² + φ + 1 = 0` in `End(E)` (operator form).** The GLV endomorphism `glvHom`
satisfies its minimal polynomial `X² + X + 1` as an identity of additive endomorphisms:
`glvHom.comp glvHom + glvHom + AddMonoidHom.id = 0`. Bundles the pointwise cube relation
`secp256k1_glv_cube_relation` into a single equation of `AddMonoidHom`s, so `glvHom` is a
primitive cube root of unity in the endomorphism ring of the secp256k1 point group. -/
theorem glvHom_minpoly :
    glvHom.comp glvHom + glvHom + AddMonoidHom.id secp256k1.toAffine.Point
      = (0 : secp256k1.toAffine.Point →+ secp256k1.toAffine.Point) := by
  ext P
  simp only [AddMonoidHom.add_apply, AddMonoidHom.comp_apply, AddMonoidHom.id_apply,
    AddMonoidHom.zero_apply, glvHom_apply]
  exact secp256k1_glv_cube_relation P

end Ecdlp.Curve
