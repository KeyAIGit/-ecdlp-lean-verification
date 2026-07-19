/-
# General ωₙ foundation: the Silverman ω-recurrence reproduces the group-law anchors (N7-uniform)

Toward the **uniform** `y([n]•P) = ωₙ/ψₙ³` (node S3a-uniform of the N7 build, `BARRIERS.md §B3`;
target `n7_uniform_secp256k1_x`), the general `y`-coordinate ("omega") division polynomial is
`ωₙ = (ψ_{n+2}·ψ_{n-1}² − ψ_{n-2}·ψ_{n+1}²)/(4y)` (Silverman). Mathlib has the `ψ` recurrence but
**no** `ω` (open `TODO`). This file validates that recurrence numerator against the two
**independently kernel-verified**, group-law-derived anchors already in the ledger:
`ω₂ = x⁶+140x³−392` (`MultiplicationYFormula`) and `ω₃ = y·(x¹²+1540x⁹−87024x⁶−109760x³−1229312)`
(`MultiplicationYTripleFormula`). Concretely it proves `4y·ωₙ = ψ_{n+2}ψ_{n-1}² − ψ_{n-2}ψ_{n+1}²`
evaluated on a curve point, for `n = 2, 3` — cross-checking two independent constructions — and
extends to `n = 4` (`ω₄`, degree 24) via a freshly-derived `ψ₆` brick.

Uses the existing `secp256k1_psi5_evalEval`, `secp256k1_psi2_evalEval`, `secp256k1_preΨ₄_eval`
(all in `FiveTorsionBridge.lean`) plus Mathlib's `ψ_zero/one/two/three/four` and `ψ_even`. The
`n = 4` step first reduces the even-index `ψ 6` (`secp256k1_psi6_evalEval`) via `ψ_even 3`, then
anchors `ω₄`. No `native_decide`.

**Scope.** Anchor validation at `n = 2, 3, 4` — grounding the general `ωₙ` object against the
verified group-law values (and, at `n = 4`, against the recurrence-derived `ψ₆`); the uniform
statement for all `n` remains the open target.
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

/-- **`ψ 6` at a point `(x,y)` of secp256k1 reduces to `2y` times a concrete degree-16 univariate.**
The even index makes this the genuine gap in the `ψ₂,ψ₃,ψ₅,ψ₇` brick family. Route: the even
recurrence `ψ_even 3` (`ψ₆·ψ₂ = ψ₂²ψ₃ψ₅ − ψ₁ψ₃ψ₄²`) reduces on the curve — via the five-bridge
`ψ₅` value and `ψ₂ = 2y`, `ψ₄ = preΨ₄·2y` — to `ψ₆·(2y) = (2y)·(2y·ψ₃·(ψ₅−preΨ₄²))`; cancelling the
`ψ₂ = 2y` factor (`2y ≠ 0`, i.e. `P` is not 2-torsion) leaves the stated value. Here
`ψ₆/(2y) = ψ₃·(ψ₅−preΨ₄²) = 3x¹⁶+4704x¹³−131712x¹⁰−7639296x⁷−12907776x⁴−103262208x`. No
`native_decide`. -/
theorem secp256k1_psi6_evalEval (x y : ZMod Secp256k1.p) (hcurve : y ^ 2 = x ^ 3 + 7)
    (h2y : (2 : ZMod Secp256k1.p) * y ≠ 0) :
    (secp256k1.ψ 6).evalEval x y
      = 2 * y * (3 * x ^ 16 + 4704 * x ^ 13 - 131712 * x ^ 10 - 7639296 * x ^ 7
          - 12907776 * x ^ 4 - 103262208 * x) := by
  have h6 := secp256k1.ψ_even 3
  rw [show (2 * 3 : ℤ) = 6 by ring, show (3 - 1 : ℤ) = 2 by ring, show (3 + 2 : ℤ) = 5 by ring,
      show (3 - 2 : ℤ) = 1 by ring, show (3 + 1 : ℤ) = 4 by ring,
      secp256k1.ψ_two, secp256k1.ψ_four, secp256k1.ψ_three, secp256k1.ψ_one] at h6
  have h6e := congrArg (Polynomial.evalEval x y) h6
  simp only [evalEval_mul, evalEval_sub, evalEval_pow, evalEval_C, evalEval_one] at h6e
  rw [secp256k1_psi2_evalEval, secp256k1_psi5_evalEval x y hcurve, secp256k1_preΨ₄_eval,
      secp256k1_Ψ₃_eval] at h6e
  refine mul_right_cancel₀ h2y ?_
  rw [h6e]; ring

/-- **ω-recurrence anchor at `n = 4`:** `ψ₆·ψ₃² − ψ₂·ψ₅² = 4y·ω₄` on a secp256k1 point, with
`ω₄ = x²⁴+8624x²¹−2875712x¹⁸−16946944x¹⁵−1054135040x¹²−35487778816x⁹−229379784704x⁶
−701632282624x³−188900999168`. Extends the `n = 2, 3` anchors to the first even step needing the
`ψ₆` brick, feeding the `carrier_four` `y`-conjunct of the uniform induction. -/
theorem secp256k1_omega_recurrence_four (x y : ZMod Secp256k1.p) (hcurve : y ^ 2 = x ^ 3 + 7)
    (h2y : (2 : ZMod Secp256k1.p) * y ≠ 0) :
    (secp256k1.ψ 6).evalEval x y * (secp256k1.ψ 3).evalEval x y ^ 2
      - (secp256k1.ψ 2).evalEval x y * (secp256k1.ψ 5).evalEval x y ^ 2
    = 4 * y * (x ^ 24 + 8624 * x ^ 21 - 2875712 * x ^ 18 - 16946944 * x ^ 15
        - 1054135040 * x ^ 12 - 35487778816 * x ^ 9 - 229379784704 * x ^ 6
        - 701632282624 * x ^ 3 - 188900999168) := by
  rw [secp256k1_psi6_evalEval x y hcurve h2y, secp256k1.ψ_three, secp256k1.ψ_two,
      secp256k1_psi5_evalEval x y hcurve, evalEval_C, secp256k1_Ψ₃_eval,
      secp256k1_psi2_evalEval]
  ring

end Ecdlp.Curve
