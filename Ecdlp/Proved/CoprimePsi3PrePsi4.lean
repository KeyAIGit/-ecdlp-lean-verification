import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial

/-!
# `Ψ₃` and `preΨ₄` are coprime for secp256k1 (node L6 of B1)

Companion to L5 (`CoprimePsi2Psi3.lean`): the 3- and 4-division polynomials share no root —
"no point is both 3- and 4-torsion", the **second** place `Δ ≠ 0` enters the division-polynomial
coprimality argument (node **L6** of `notes/B1_COPRIMALITY_PLAN.md`). Proved by an explicit
Bézout certificate `u·Ψ₃ + v·preΨ₄ = 1` with cofactors from extended-Euclid over `𝔽_p` (CAS);
the sparse cofactors (`u = U₅X⁵+U₂X²`, `v = V₃X³+V₀`) collapse the identity to four residue
equations in `ZMod p`, discharged by `native_decide`. `Ψ₃ = 3X⁴+84X` and `preΨ₄ = 2X⁶+280X³−784`
are the concrete secp256k1 forms (`DivisionPolynomial.lean`, `FourDivisionPolynomial.lean`).
-/

namespace Ecdlp.Curve

open Polynomial

private def U₅ : ZMod Secp256k1.p :=
  4066664185772280807851901832855603285744094861515991086689728884415543513331
private def U₂ : ZMod Secp256k1.p :=
  62501909090399416520678480475683486164562681632162182762416966878040738140515
private def V₃ : ZMod Secp256k1.p :=
  51796048339999676500007639755060548998018850040546295389694198677331102065835
private def V₀ : ZMod Secp256k1.p :=
  68382318006221171532032354667120537418448983291060690242689874229160447006352

/-- **`Ψ₃` and `preΨ₄` are coprime** (L6). Their only possible common root would be a point that
is simultaneously 3- and 4-torsion, forbidden by nonsingularity (`Δ ≠ 0`); realized by an
explicit Bézout certificate over `𝔽_p`. The second reachable leaf of the Route-B coprimality
node B1. -/
theorem secp256k1_isCoprime_Ψ₃_preΨ₄ :
    IsCoprime secp256k1.Ψ₃ secp256k1.preΨ₄ := by
  refine ⟨C U₅ * X ^ 5 + C U₂ * X ^ 2, C V₃ * X ^ 3 + C V₀, ?_⟩
  rw [secp256k1_Ψ₃, secp256k1_preΨ₄]
  have e9 : (3 * U₅ + 2 * V₃ : ZMod Secp256k1.p) = 0 := by native_decide
  have e6 : (84 * U₅ + 3 * U₂ + 280 * V₃ + 2 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e3 : (84 * U₂ - 784 * V₃ + 280 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e0 : (-784 * V₀ : ZMod Secp256k1.p) = 1 := by native_decide
  have key : (C U₅ * X ^ 5 + C U₂ * X ^ 2) * (3 * X ^ 4 + 3 * C 28 * X)
      + (C V₃ * X ^ 3 + C V₀) * (2 * X ^ 6 + 280 * X ^ 3 - 784)
      = C (3 * U₅ + 2 * V₃) * X ^ 9
        + C (84 * U₅ + 3 * U₂ + 280 * V₃ + 2 * V₀) * X ^ 6
        + C (84 * U₂ - 784 * V₃ + 280 * V₀) * X ^ 3
        + C (-784 * V₀) := by
    simp only [map_add, map_sub, map_mul, map_neg, map_ofNat]; ring
  rw [key, e9, e6, e3, e0]
  simp

end Ecdlp.Curve
