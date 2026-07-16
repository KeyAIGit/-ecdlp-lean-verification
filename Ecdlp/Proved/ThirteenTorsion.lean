import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
# 13-torsion point count for secp256k1 via the 13-division polynomial

Torsion-tower rung above `ψ₁₁` (deg 60): the `13`-division polynomial `ψ₁₃ = Ψ₁₃`.
Because `13` is **odd**, Mathlib's factorisation `Ψₙ = preΨₙ` (no `ψ₂` factor) means
`preΨ' 13` *is* the genuine 13-division polynomial, so its roots are exactly the
`x`-coordinates of the order-13 points.

Its degree is `(13² − 1)/2 = 84` — obtained by instantiating Mathlib's general degree
formula `natDegree_preΨ'` at `n = 13` over `𝔽_p`, needing only `13 ≠ 0` in `𝔽_p`. Hence
secp256k1 has at most 84 nontrivial 13-torsion `x`-coordinates, i.e. `#E[13] ≤ 169` —
consistent with the classical structure `E[13] ≅ (ℤ/13)²` (168 nontrivial points, `±y` per
`x` ⇒ 84 `x`-coords). A concrete named level of the uniform
`secp256k1_odd_torsion_x_card_le` (`#E[n] ≤ n²`), in the same spirit as the 3-, 5-, 7- and
11-torsion nodes; closes the `thirteen_torsion_degree` prover-loop target. All
polynomial/degree facts over `𝔽_p`; no axioms.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **`deg (preΨ' 13) = 84`** (13-torsion bound). The secp256k1 13-division polynomial
`ψ₁₃ = preΨ' 13` (odd index ⇒ no `ψ₂` factor) has degree `(13² − 1)/2 = 84`, instantiating
Mathlib's general `natDegree_preΨ'` at `n = 13`; the only hypothesis is `13 ≠ 0` in `𝔽_p`
(machine-checked: `p ∤ 13`). One rung above `secp256k1_preΨ₁₁_natDegree`. -/
theorem secp256k1_preΨ₁₃_natDegree : (secp256k1.preΨ' 13).natDegree = 84 := by
  have h13 : ((13 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
  rw [secp256k1.natDegree_preΨ' h13]
  decide

/-- The 13-division polynomial is nonzero (degree 84), so the 13-torsion `x`-coordinates
form a proper finite set. Mirrors `secp256k1_preΨ₁₁_ne_zero`. -/
theorem secp256k1_preΨ₁₃_ne_zero : secp256k1.preΨ' 13 ≠ 0 := by
  intro h
  have h84 : (secp256k1.preΨ' 13).natDegree = 84 := secp256k1_preΨ₁₃_natDegree
  rw [h, natDegree_zero] at h84
  exact absurd h84 (by norm_num)

/-- **At most 84 thirteen-torsion `x`-coordinates.** Since `ψ₁₃ = preΨ' 13` has degree 84,
it has at most 84 roots in `𝔽_p`; these are exactly the `x`-coordinates of the order-13
points, so secp256k1 has at most 84 nontrivial 13-torsion `x`-coordinates (`#E[13] ≤ 169`,
consistent with `E[13] ≅ (ℤ/13)²`). Mirrors `secp256k1_eleven_torsion_x_card_le` one rung
up. -/
theorem secp256k1_thirteen_torsion_x_card_le :
    Multiset.card (secp256k1.preΨ' 13).roots ≤ 84 :=
  (Polynomial.card_roots' _).trans secp256k1_preΨ₁₃_natDegree.le

end Ecdlp.Curve
