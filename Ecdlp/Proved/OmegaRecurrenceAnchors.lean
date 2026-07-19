/-
# General ωₙ foundation: the Silverman ω-recurrence reproduces the group-law anchors (N7-uniform)

Toward the **uniform** `y([n]•P) = ωₙ/ψₙ³` (node S3a-uniform of the N7 build, `BARRIERS.md §B3`;
target `n7_uniform_secp256k1_x`), the general `y`-coordinate ("omega") division polynomial is
`ωₙ = (ψ_{n+2}·ψ_{n-1}² − ψ_{n-2}·ψ_{n+1}²)/(4y)` (Silverman). Mathlib has the `ψ` recurrence but
**no** `ω` (open `TODO`). This file validates that recurrence numerator against the two
**independently kernel-verified**, group-law-derived anchors already in the ledger:
`ω₂ = x⁶+140x³−392` (`MultiplicationYFormula`) and `ω₃ = y·(x¹²+1540x⁹−87024x⁶−109760x³−1229312)`
(`MultiplicationYTripleFormula`). Concretely it proves `4y·ωₙ = ψ_{n+2}ψ_{n-1}² − ψ_{n-2}ψ_{n+1}²`
evaluated on a curve point, for `n = 2, 3` — cross-checking two independent constructions.

Uses the existing `secp256k1_psi5_evalEval`, `secp256k1_psi2_evalEval`, `secp256k1_preΨ₄_eval`
(all in `FiveTorsionBridge.lean`) plus Mathlib's `ψ_zero/one/two/three/four`. No `native_decide`.

**Scope.** Anchor validation at `n = 2, 3` only — grounding the general `ωₙ` object against the
verified group-law values; the uniform statement for all `n` remains the open target.
-/
import Mathlib
import Ecdlp.Proved.FiveTorsionBridge

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- **ω-recurrence anchor at `n = 2`:** `ψ₄·ψ₁² − ψ₀·ψ₃² = 4y·ω₂` on a secp256k1 point, with
`ω₂ = x⁶+140x³−392` (the group-law-derived value of `MultiplicationYFormula`). -/
theorem secp256k1_omega_recurrence_two (x y : ZMod Secp256k1.p) :
    (secp256k1.ψ 4).evalEval x y * (secp256k1.ψ 1).evalEval x y ^ 2
      - (secp256k1.ψ 0).evalEval x y * (secp256k1.ψ 3).evalEval x y ^ 2
    = 4 * y * (x ^ 6 + 140 * x ^ 3 - 392) := by
  rw [secp256k1.ψ_four, secp256k1.ψ_one, secp256k1.ψ_zero, secp256k1.ψ_three]
  simp only [evalEval_mul, evalEval_C, evalEval_one, evalEval_zero, zero_mul, sub_zero]
  rw [secp256k1_psi2_evalEval, secp256k1_preΨ₄_eval]
  ring

/-- **ω-recurrence anchor at `n = 3`:** `ψ₅·ψ₂² − ψ₁·ψ₄² = 4y·ω₃` on a secp256k1 point, with
`ω₃ = y·(x¹²+1540x⁹−87024x⁶−109760x³−1229312)` (the group-law-derived value of
`MultiplicationYTripleFormula`). -/
theorem secp256k1_omega_recurrence_three (x y : ZMod Secp256k1.p) (hcurve : y ^ 2 = x ^ 3 + 7) :
    (secp256k1.ψ 5).evalEval x y * (secp256k1.ψ 2).evalEval x y ^ 2
      - (secp256k1.ψ 1).evalEval x y * (secp256k1.ψ 4).evalEval x y ^ 2
    = 4 * y * (y * (x ^ 12 + 1540 * x ^ 9 - 87024 * x ^ 6 - 109760 * x ^ 3 - 1229312)) := by
  rw [secp256k1_psi5_evalEval x y hcurve, secp256k1.ψ_two, secp256k1.ψ_one, secp256k1.ψ_four]
  simp only [evalEval_mul, evalEval_C, evalEval_one]
  rw [secp256k1_psi2_evalEval, secp256k1_preΨ₄_eval]
  ring

end Ecdlp.Curve
