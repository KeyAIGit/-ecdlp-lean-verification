import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial
import Ecdlp.Proved.ThreeTorsionCard
import Ecdlp.Proved.MultiplicationFormula
import Ecdlp.Proved.FiveTorsionBridge

/-!
# The `n = 3` division polynomials `Φ₃` and `ΨSq₃` for secp256k1 — concrete forms

Groundwork for node **N7@3** of the `ψₙ ↔ E[n]` bridge (`notes/DIVISION_POLY_TORSION_MAP.md`)
and for the degree half of node **N10(i)** (`deg [n] = n²`). Where `MultiplicationFormula.lean`
records the base case `n = 2` (`Φ 2 = X⁴ − 56X`, `x(2•P) = Φ₂/Ψ₂Sq`), this file records the
`n = 3` numerator/denominator of the multiplication-by-3 `x`-coordinate formula
`x(3•P) = Φ₃(x)/ΨSq₃(x)` in Mathlib's canonical division-polynomial vocabulary.

Mathlib gives the canonical shapes `Φ 3 = X·Ψ₃² − preΨ₄·Ψ₂Sq` (`WeierstrassCurve.Φ_three`)
and `ΨSq 3 = Ψ₃²` (`WeierstrassCurve.ΨSq_three`). Substituting the secp256k1 forms
`Ψ₃ = 3X⁴ + 84X`, `preΨ₄ = 2X⁶ + 280X³ − 784`, `Ψ₂Sq = 4X³ + 28` gives the explicit
univariate evaluations:

* `ΨSq₃(x) = (3x⁴ + 84x)² = 9x⁸ + 504x⁵ + 7056x²`  (degree `8 = 3² − 1`, the denominator),
* `Φ₃(x)  = x⁹ − 672x⁶ + 2352x³ + 21952`            (degree `9 = 3²`, the numerator).

The numerator degree `9 = 3²` is exactly what the general `deg [n] = n²` count predicts at
`n = 3` (cf. Mathlib's `natDegree_Φ`); together with `Ψ₃ ⊥ Φ₃` (coprimality, node N5 in
progress) this is the `n = 3` instance of the lowest-terms degree bookkeeping. Everything here
is a ring identity over `𝔽_p` — no `native_decide`, no curve hypothesis (the polynomials are
identities in `𝔽_p[X]`, evaluated formally).
-/

namespace Ecdlp.Curve

open Polynomial

/-- **`Φ 3 = X·Ψ₃² − preΨ₄·Ψ₂Sq` for secp256k1**, Mathlib's canonical `n = 3` numerator
(`WeierstrassCurve.Φ_three` specialised). -/
theorem secp256k1_Φ₃ :
    secp256k1.Φ 3 = X * secp256k1.Ψ₃ ^ 2 - secp256k1.preΨ₄ * secp256k1.Ψ₂Sq :=
  secp256k1.Φ_three

/-- **`ΨSq 3 = Ψ₃²` for secp256k1**, the `n = 3` denominator of the multiplication formula
(`WeierstrassCurve.ΨSq_three` specialised). -/
theorem secp256k1_ΨSq₃ : secp256k1.ΨSq 3 = secp256k1.Ψ₃ ^ 2 :=
  secp256k1.ΨSq_three

/-- **`ΨSq₃` evaluated: `(ΨSq 3)(x) = 9x⁸ + 504x⁵ + 7056x²`** — the explicit degree-8
denominator of `x(3•P)` for secp256k1. -/
theorem secp256k1_ΨSq₃_eval (x : ZMod Secp256k1.p) :
    (secp256k1.ΨSq 3).eval x = 9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2 := by
  rw [secp256k1_ΨSq₃]
  simp only [eval_pow]
  rw [secp256k1_Ψ₃_eval]
  ring

/-- **`Φ₃` evaluated: `(Φ 3)(x) = x⁹ − 672x⁶ + 2352x³ + 21952`** — the explicit degree-9
numerator of `x(3•P)` for secp256k1. Its degree `9 = 3²` matches the general `deg [n] = n²`
at `n = 3`. -/
theorem secp256k1_Φ₃_eval (x : ZMod Secp256k1.p) :
    (secp256k1.Φ 3).eval x = x ^ 9 - 672 * x ^ 6 + 2352 * x ^ 3 + 21952 := by
  rw [secp256k1_Φ₃]
  simp only [eval_sub, eval_mul, eval_pow, eval_X]
  rw [secp256k1_Ψ₃_eval, secp256k1_preΨ₄_eval, secp256k1_Ψ₂Sq_eval]
  ring

end Ecdlp.Curve
