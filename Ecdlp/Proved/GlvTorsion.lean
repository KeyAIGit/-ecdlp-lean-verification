import Mathlib
import Ecdlp.Proved.Secp256k1Curve
import Ecdlp.Proved.GlvEndomorphism
import Ecdlp.Proved.GlvMonoidHom
import Ecdlp.Proved.Torsion

/-!
# The GLV endomorphism preserves the `n`-torsion: `glvPoint (E[n]) ⊆ E[n]`

Connective tissue between two verified objects in the environment: the GLV endomorphism
(`glvHom : Point →+ Point`, a verified additive endomorphism — indeed a primitive cube
root of unity in `End(E)`, `GlvCubeRelation.lean`) and the `n`-torsion subgroup `E[n]`
(`AddSubgroup.torsionBy`, `Torsion.lean`).

Because `glvHom` is a homomorphism, it cannot increase order: `addOrderOf (glvPoint P) ∣
addOrderOf P` (Mathlib `addOrderOf_map_dvd`), so if `P ∈ E[n]` (order divides `n`) then
`glvPoint P ∈ E[n]`. Hence `glvPoint` restricts to an endomorphism *of `E[n]`* — and on
`E[n]` it still satisfies `φ² + φ + 1 = 0` (`GlvCubeRelation.lean`). This is exactly the
setup in which the GLV eigenvalue `[λ]`-action lives (on the base-point subgroup
`⟨G⟩ ⊆ E[n]`); identifying the eigenvalue itself remains blocked on point counting
(`notes/GLV_LAMBDA.md`), but the endomorphism-*of-the-torsion* structure is now explicit.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **The GLV endomorphism preserves `n`-torsion.** If `P` lies in `E[n]` (its order
divides `n`), so does `glvPoint P`, because the homomorphism `glvHom` cannot increase
order. Thus `glvPoint` restricts to an endomorphism of `E[n]`. -/
theorem secp256k1_glv_preserves_torsion (n : ℕ) (P : secp256k1.toAffine.Point)
    (hP : P ∈ AddSubgroup.torsionBy secp256k1.toAffine.Point (n : ℤ)) :
    glvPoint P ∈ AddSubgroup.torsionBy secp256k1.toAffine.Point (n : ℤ) := by
  rw [Ecdlp.Torsion.mem_torsionBy_iff_addOrderOf_dvd] at hP ⊢
  calc addOrderOf (glvPoint P)
      = addOrderOf (glvHom P) := by rw [glvHom_apply]
    _ ∣ addOrderOf P := addOrderOf_map_dvd glvHom P
    _ ∣ n := hP

end Ecdlp.Curve
