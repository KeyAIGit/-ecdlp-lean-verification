import Mathlib
import Ecdlp.Proved.GlvEndomorphism
import Ecdlp.Proved.GlvHom

/-!
# The GLV endomorphism as a bundled `AddMonoidHom`

`glvPoint` preserves the point at infinity (`glvPoint_zero`) and is additive
(`glvPoint_add`), so it is a bona-fide additive-monoid homomorphism of the secp256k1
point group. This file bundles it as a first-class Mathlib `AddMonoidHom`
(`secp256k1.toAffine.Point →+ secp256k1.toAffine.Point`), so it composes with Mathlib's
homomorphism API (kernels, images, `AddMonoidHom.comp`, iterates).

**Scope, stated honestly.** This bundles the *homomorphism* structure only. The
cryptographically load-bearing fact — that `glvHom` acts as scalar multiplication by the
GLV eigenvalue `λ` on the base-point subgroup (`glvHom G = λ • G`) — is **not** proved
here and remains open; bundling does not establish it. See `notes/GLV_HOMOMORPHISM.md`
and the open stem `Ecdlp/Targets/glv_root_mod_n_condition_008.lean`.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **The GLV endomorphism, bundled as an `AddMonoidHom`.** `AddMonoidHom.mk'` derives
`map_zero` from additivity (the codomain is an additive group), so `glvPoint_add` alone
suffices. This is the homomorphism object; it does **not** assert the `[λ]`-action. -/
def glvHom : secp256k1.toAffine.Point →+ secp256k1.toAffine.Point :=
  AddMonoidHom.mk' glvPoint glvPoint_add

@[simp] theorem glvHom_apply (P : secp256k1.toAffine.Point) : glvHom P = glvPoint P := rfl

/-- The bundled hom sends the point at infinity to itself (`map_zero`, for the record). -/
theorem glvHom_zero : glvHom (0 : secp256k1.toAffine.Point) = 0 := map_zero glvHom

/-- The bundled hom is additive (`map_add`, for the record). -/
theorem glvHom_add (P Q : secp256k1.toAffine.Point) :
    glvHom (P + Q) = glvHom P + glvHom Q := map_add glvHom P Q

end Ecdlp.Curve
