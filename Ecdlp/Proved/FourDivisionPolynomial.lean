import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
# The secp256k1 4-division polynomial (next rung of the torsion tower)

The 4-division polynomial `ψ₄ = Ψ₄ = preΨ₄·ψ₂` governs the 4-torsion `E[4]`.
Mathlib factors it through the univariate auxiliary `preΨ₄ ∈ R[X]`
(`WeierstrassCurve.preΨ₄`), the genuine `X`-polynomial of the tower (mirroring
`Ψ₂Sq` and `Ψ₃`). For secp256k1 (`b₂=b₄=b₈=0`, `b₆=28`) it collapses to
`2X⁶ + 280X³ − 784`, degree 6 — extending the `Ψ₂Sq` (deg 3) → `Ψ₃` (deg 4) chain
to `preΨ₄` (deg 6).

Note: `preΨ₄ = ψ₄/ψ₂`, so its roots are *not* literally the 4-torsion
`x`-coordinates (the `ψ₂` factor carries the 2-torsion roots) — hence we record the
closed form, degree and nonvanishing, but not a "4-torsion x-coord count" claim.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **The secp256k1 4-division polynomial auxiliary is `preΨ₄ = 2X⁶ + 280X³ − 784`.**
With `ψ₄ = preΨ₄·ψ₂`, this is the univariate heart of the 4-torsion polynomial:
substituting secp256k1's `b₂=b₄=b₈=0`, `b₆=28` into Mathlib's
`2X⁶ + b₂X⁵ + 5b₄X⁴ + 10b₆X³ + 10b₈X² + (b₂b₈−b₄b₆)X + (b₄b₈−b₆²)` gives
`2X⁶ + 280X³ − 784`. Extends `secp256k1_Ψ₂Sq` / `secp256k1_Ψ₃` one rung up. -/
theorem secp256k1_preΨ₄ :
    secp256k1.preΨ₄ = C 2 * X ^ 6 + C 280 * X ^ 3 + C (-784) := by
  rw [WeierstrassCurve.preΨ₄, secp256k1_b₂, secp256k1_b₄, secp256k1_b₆, secp256k1_b₈]
  C_simp
  ring1

/-- **`deg preΨ₄ = 6`** (4-torsion bound). The secp256k1 4-division auxiliary
`2X⁶ + 280X³ − 784` has degree 6, so it has at most 6 roots in `𝔽_p`. Uses the
machine-checked primality of `p` (leading coefficient `2 ≠ 0` in `𝔽_p`). Mirrors
`secp256k1_Ψ₃_natDegree`. -/
theorem secp256k1_preΨ₄_natDegree : secp256k1.preΨ₄.natDegree = 6 := by
  have h2 : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
    simpa using h
  rw [secp256k1_preΨ₄]
  compute_degree! <;> first | exact h2 | norm_num

/-- The 4-division auxiliary is nonzero (it has degree 6). Mirrors
`secp256k1_Ψ₃_ne_zero`. -/
theorem secp256k1_preΨ₄_ne_zero : secp256k1.preΨ₄ ≠ 0 := by
  intro h
  have h6 : secp256k1.preΨ₄.natDegree = 6 := secp256k1_preΨ₄_natDegree
  rw [h, natDegree_zero] at h6
  exact absurd h6 (by norm_num)

end Ecdlp.Curve
