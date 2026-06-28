import Mathlib

namespace Ecdlp.Targets.GlvRootModNCondition

/-- [glv-root-mod-n-condition-008] **GLV eigenvalue acts as scalar `[λ]`.**
If an endomorphism `φ` of the (cyclic) prime-order-`n` subgroup has the generator `g`
as a `λ`-eigenvector (`φ g = λ • g`), then `φ` acts on the whole subgroup as the scalar
multiplication map `[λ]`: `φ x = λ • x` for every `x`. This is the algebraic core of the
GLV endomorphism speed-up exploited in `Ecdlp/Proved/CubeRoot.lean` (where secp256k1's
`λ` satisfies `λ² + λ + 1 ≡ 0`). Open conjecture stem. -/
theorem glv_root_mod_n_condition {G : Type*} [AddCommGroup G] (φ : G →+ G) (g : G)
    (lam : ℤ) (hgen : ∀ x : G, ∃ k : ℤ, x = k • g) (heig : φ g = lam • g) :
    ∀ x : G, φ x = lam • x := by
  sorry

end Ecdlp.Targets.GlvRootModNCondition
