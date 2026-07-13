import Mathlib
import Ecdlp.Proved.CurveCardinalityExact
import Ecdlp.Proved.SubgroupOrder
import Ecdlp.Proved.GlvEigenvalue

/-!
# The whole point group of secp256k1 equals its base-point subgroup

The subgroup files established the structure of the *crypto subgroup* `⟨G⟩ = zmultiples G`:
it has exactly `n` elements (`secp256k1_grp_card`) and is cyclic (`secp256k1_grp_isAddCyclic`).
The exact cardinality keystone `secp256k1_card_point_eq_n` says the *whole* group of rational
points also has exactly `n` elements. Since a subgroup with the same finite cardinality as the
ambient group is the whole group (`AddSubgroup.eq_top_of_card_eq`), the two coincide:
`⟨G⟩ = ⊤` (cofactor 1).

Consequences promoted here from the subgroup to the entire point group:

* `secp256k1_point_isAddCyclic` — the *whole* group `E(𝔽_p)` is cyclic, as an instance,
  transported across `⟨G⟩ = ⊤` via `AddSubgroup.topEquiv`.
* `secp256k1_mem_zmultiples` — every rational point is an integer multiple of `G`.
* `secp256k1_glvHom_eq_zsmul_unconditional` — the GLV eigenvalue property with the
  `[IsAddCyclic …]` hypothesis of `secp256k1_glvHom_eq_zsmul` now discharged by the new
  instance, so it holds unconditionally.

No new axioms; everything rests on `secp256k1_card_point_eq_n` and the subgroup structure.
-/

open WeierstrassCurve.Affine

namespace Ecdlp.Curve

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **The base-point subgroup is the whole group: `⟨G⟩ = ⊤`.** The crypto subgroup `⟨G⟩` has
`n` elements (`secp256k1_grp_card`) and so does the whole point group (`secp256k1_card_point_eq_n`);
a finite subgroup of full cardinality is everything (`AddSubgroup.eq_top_of_card_eq`). This is
exactly the cofactor-`1` statement for secp256k1. -/
theorem secp256k1_grp_eq_top : secp256k1Grp = ⊤ :=
  AddSubgroup.eq_top_of_card_eq secp256k1Grp
    (secp256k1_grp_card.trans secp256k1_card_point_eq_n.symm)

/-- **The whole secp256k1 point group is cyclic.** Registered as an instance so downstream
results needing `[IsAddCyclic secp256k1.toAffine.Point]` are discharged automatically. Proved
by transporting cyclicity of `⟨G⟩` across the isomorphism `(⊤ : AddSubgroup _) ≃+ _` supplied by
`AddSubgroup.topEquiv`, using `secp256k1_grp_eq_top`. -/
instance secp256k1_point_isAddCyclic : IsAddCyclic secp256k1.toAffine.Point := by
  have h : IsAddCyclic ↥secp256k1Grp := secp256k1_grp_isAddCyclic
  rw [secp256k1_grp_eq_top] at h
  exact AddSubgroup.topEquiv.isAddCyclic.mp h

/-- **Every rational point is a multiple of `G`.** Since `⟨G⟩ = ⊤`, every point of
`E(𝔽_p)` lies in the base-point subgroup `zmultiples G`. -/
theorem secp256k1_mem_zmultiples (P : secp256k1.toAffine.Point) : P ∈ secp256k1Grp := by
  rw [secp256k1_grp_eq_top]
  exact AddSubgroup.mem_top P

/-- **GLV eigenvalue property, unconditional.** The cyclicity hypothesis of
`secp256k1_glvHom_eq_zsmul` is now an available instance (`secp256k1_point_isAddCyclic`), so the
GLV endomorphism `glvHom` is multiplication by a fixed integer `k` with `k² + k + 1` annihilating
every point — with no remaining hypotheses. -/
theorem secp256k1_glvHom_eq_zsmul_unconditional :
    ∃ k : ℤ, (∀ P : secp256k1.toAffine.Point, glvHom P = k • P)
      ∧ ∀ P : secp256k1.toAffine.Point, (k ^ 2 + k + 1) • P = 0 :=
  secp256k1_glvHom_eq_zsmul

end Ecdlp.Curve