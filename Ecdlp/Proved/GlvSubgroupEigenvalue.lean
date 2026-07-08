import Ecdlp.Proved.GeneratorOrder
import Ecdlp.Proved.GlvMonoidHom

/-!
# GLV eigenvalue on the whole base-point subgroup `⟨G⟩`

`secp256k1_glvPoint_generator` (in `GeneratorOrder.lean`) gives the eigenvalue identity
`glvPoint G = λ·G` **at the generator**. Combined with the additivity of the bundled
endomorphism `glvHom` (`glvHom_apply` + `map_zsmul`), it propagates to **every** point of
the cyclic subgroup `⟨G⟩`: the GLV endomorphism acts as the scalar `[λ]` on all of `⟨G⟩`.

This is the full GLV eigenvalue property on the cryptographic subgroup — **unconditionally**.
It does *not* assume whole-group cyclicity / point counting, unlike
`secp256k1_glvHom_eq_zsmul` (which is stated `[IsAddCyclic secp256k1.toAffine.Point]`). The
scalar is the published `Secp256k1.lam`, cast to `ℤ`. Together with `addOrderOf G = n` this
completes the GLV `[λ]` object on `⟨G⟩` (the cryptographically load-bearing subgroup), a fact
the notes had billed as blocked behind `#E(𝔽_p) = n`.
-/

open WeierstrassCurve.Affine

namespace Ecdlp.Curve

/-- **GLV eigenvalue on `⟨G⟩`:** for every `P` in the base-point subgroup,
`glvPoint P = λ·P`. The GLV endomorphism restricts to multiplication by the published `λ`
on the whole cyclic crypto subgroup — no point-counting / whole-group-cyclicity assumption. -/
theorem secp256k1_glvPoint_eq_lam_on_zmultiples
    (P : secp256k1.toAffine.Point) (hP : P ∈ AddSubgroup.zmultiples secp256k1G) :
    glvPoint P = (Secp256k1.lam : ℤ) • P := by
  obtain ⟨k, hk⟩ := AddSubgroup.mem_zmultiples_iff.mp hP
  have hgen : glvHom secp256k1G = (Secp256k1.lam : ℤ) • secp256k1G := by
    rw [glvHom_apply, secp256k1_glvPoint_generator, natCast_zsmul]
  rw [← hk, ← glvHom_apply, map_zsmul, hgen, smul_smul, smul_smul, mul_comm]

end Ecdlp.Curve
