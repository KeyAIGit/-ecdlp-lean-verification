import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial

/-!
# `Ψ₂Sq` and `preΨ₄` are coprime for secp256k1 (node L6b of B1)

Completes the pairwise-disjointness triangle among the low division polynomials: with L5
(`Ψ₂Sq ⊥ Ψ₃`) and L6 (`Ψ₃ ⊥ preΨ₄`), this adds `Ψ₂Sq ⊥ preΨ₄` — "no nonidentity point is simultaneously
2-torsion and *primitive* 4-torsion" (order-2 points have order dividing 2, not exactly 4). A third
manifestation of nonsingularity (`Δ ≠ 0`) in the division-polynomial coprimality picture
(`notes/B1_COPRIMALITY_PLAN.md`). Proved by an explicit Bézout certificate `u·Ψ₂Sq + v·preΨ₄ = 1`
with cofactors from extended-Euclid over `𝔽_p` (CAS). Because both `Ψ₂Sq = 4X³+28` and
`preΨ₄ = 2X⁶+280X³−784` live in powers of `X³`, the cofactors are maximally sparse
(`u = aX³+b`, `v = c` constant); the identity collapses to three residue equations in `ZMod p`,
discharged by `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- Bézout cofactor coefficients (from extended-Euclid over `𝔽_p`): `u = aX³+b`, `v = c`
with `u·Ψ₂Sq + v·preΨ₄ = 1`. -/
private def a₃ : ZMod Secp256k1.p :=
  28466649300405965654963312829989223000208664030611937606828102190908804593317
private def b₀ : ZMod Secp256k1.p :=
  80717501359875178555849086110553607723112806770889652445494903137788301417945
private def c₀ : ZMod Secp256k1.p :=
  58858790636504264113644359348709461852852656604416688825801379626091225485029

/-- **`Ψ₂Sq` and `preΨ₄` are coprime** (L6b). Their only possible common root would be a point that
is a nonidentity point that is both 2-torsion and primitive-4-torsion, which nonsingularity (`Δ ≠ 0`) forbids; realized by an
explicit Bézout certificate over `𝔽_p`. Completes the pairwise low-torsion disjointness of B1. -/
theorem secp256k1_isCoprime_Ψ₂Sq_preΨ₄ :
    IsCoprime secp256k1.Ψ₂Sq secp256k1.preΨ₄ := by
  refine ⟨C a₃ * X ^ 3 + C b₀, C c₀, ?_⟩
  rw [secp256k1_Ψ₂Sq, secp256k1_preΨ₄]
  have e6 : (4 * a₃ + 2 * c₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e3 : (28 * a₃ + 4 * b₀ + 280 * c₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e0 : (28 * b₀ - 784 * c₀ : ZMod Secp256k1.p) = 1 := by native_decide
  have key : (C a₃ * X ^ 3 + C b₀) * (C 4 * X ^ 3 + C 28)
      + C c₀ * (2 * X ^ 6 + 280 * X ^ 3 - 784)
      = C (4 * a₃ + 2 * c₀) * X ^ 6 + C (28 * a₃ + 4 * b₀ + 280 * c₀) * X ^ 3
        + C (28 * b₀ - 784 * c₀) := by
    simp only [map_add, map_sub, map_mul, map_ofNat]; ring
  rw [key, e6, e3, e0]
  simp

end Ecdlp.Curve
