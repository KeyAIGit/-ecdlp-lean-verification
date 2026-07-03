import Mathlib

/-!
# GLV eigenvalue acts as the scalar `[λ]` on a cyclic subgroup

Promoted from the open stem `glv_root_mod_n_condition_008`. If an additive endomorphism `φ` of a
group `G` fixes a generator `g` as a `λ`-eigenvector (`φ g = λ • g`) and every element of `G` is an
integer multiple of `g` (cyclic), then `φ` is the scalar map `[λ]` on all of `G`: `φ x = λ • x`.
This is the algebraic core of the GLV endomorphism speed-up on secp256k1 (`Ecdlp/Proved/CubeRoot.lean`,
`GlvEndomorphism.lean`), where `λ` satisfies `λ² + λ + 1 ≡ 0 (mod n)`. Proof: expand `x = k • g`,
push `φ` through the `ℤ`-action (`map_zsmul`), rewrite the eigen-relation, and commute the two
scalar actions (`smul_comm`). Verified kernel-clean (no incomplete obligations, no new axioms).
-/

namespace Ecdlp.Curve

/-- **GLV eigenvalue ⇒ scalar action.** An endomorphism with the generator as a `λ`-eigenvector acts
as `[λ]` on the whole cyclic subgroup. -/
theorem glv_root_mod_n_condition {G : Type*} [AddCommGroup G] (φ : G →+ G) (g : G)
    (lam : ℤ) (hgen : ∀ x : G, ∃ k : ℤ, x = k • g) (heig : φ g = lam • g) :
    ∀ x : G, φ x = lam • x := by
  intro x
  obtain ⟨k, rfl⟩ := hgen x
  rw [map_zsmul, heig]
  exact smul_comm k lam g

end Ecdlp.Curve
