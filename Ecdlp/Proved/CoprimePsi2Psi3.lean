import Mathlib
import Ecdlp.Proved.DivisionPolynomial

/-!
# `Ψ₂Sq` and `Ψ₃` are coprime for secp256k1 (node L5 of B1)

First hand-built sub-lemma of **B1** (`gcd(Φₙ,ψₙ²)=1`, see `notes/B1_COPRIMALITY_PLAN.md`):
the 2- and 3-division polynomials share no root — "no point is both 2- and 3-torsion". This is
one of the two places `Δ ≠ 0` (nonsingularity) enters the division-polynomial coprimality
argument. We prove it constructively with an explicit **Bézout certificate**
`u·Ψ₂Sq + v·Ψ₃ = 1` whose cofactors were computed by extended-Euclid over `𝔽_p` (CAS); the
resulting identity reduces to three residue equations in `ZMod p`, discharged by `native_decide`.
`Ψ₂Sq = 4X³+28` and `Ψ₃ = 3X⁴+84X` are the concrete secp256k1 forms (`DivisionPolynomial.lean`).
No new axioms beyond the compiler trust of `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- Bézout cofactor coefficients (from extended-Euclid over `𝔽_p`): `u = U₃X³+U₀`, `v = V₂X²`
with `u·Ψ₂Sq + v·Ψ₃ = 1`. -/
private def U₃ : ZMod Secp256k1.p :=
  24615665229021300047527845452527191295338006944226310382537751702361571996527
private def U₀ : ZMod Secp256k1.p :=
  53760612860182519303800814468319385789018207166190261875462449717957673240415
private def V₂ : ZMod Secp256k1.p :=
  5776476107076998411153201066193047557305985629578440836435525732820848895185

/-- **`Ψ₂Sq` and `Ψ₃` are coprime** (L5). Their only possible common root would be a point that
is simultaneously 2- and 3-torsion, which nonsingularity (`Δ ≠ 0`) forbids; here realized by an
explicit Bézout certificate over `𝔽_p`. A reachable leaf of the Route-B coprimality node B1. -/
theorem secp256k1_isCoprime_Ψ₂Sq_Ψ₃ :
    IsCoprime secp256k1.Ψ₂Sq secp256k1.Ψ₃ := by
  refine ⟨C U₃ * X ^ 3 + C U₀, C V₂ * X ^ 2, ?_⟩
  rw [secp256k1_Ψ₂Sq, secp256k1_Ψ₃]
  have e6 : (4 * U₃ + 3 * V₂ : ZMod Secp256k1.p) = 0 := by native_decide
  have e3 : (28 * U₃ + 4 * U₀ + 84 * V₂ : ZMod Secp256k1.p) = 0 := by native_decide
  have e0 : (28 * U₀ : ZMod Secp256k1.p) = 1 := by native_decide
  -- collapse the Bézout product to one `C` per power of `X`, then use the residue facts.
  have key : (C U₃ * X ^ 3 + C U₀) * (C 4 * X ^ 3 + C 28)
      + C V₂ * X ^ 2 * (3 * X ^ 4 + 3 * C 28 * X)
      = C (4 * U₃ + 3 * V₂) * X ^ 6 + C (28 * U₃ + 4 * U₀ + 84 * V₂) * X ^ 3
        + C (28 * U₀) := by
    simp only [map_add, map_mul, map_ofNat]; ring
  rw [key, e6, e3, e0]
  simp

end Ecdlp.Curve
