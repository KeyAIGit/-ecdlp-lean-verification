import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
# 7-torsion point count for secp256k1 via the 7-division polynomial

Next concrete rung of the torsion tower above `ψ₅` (deg 12): the `7`-division polynomial
`ψ₇ = Ψ₇`. Because `7` is **odd**, Mathlib's factorisation `Ψₙ = preΨₙ` (no `ψ₂` factor)
means `preΨ' 7` *is* the genuine 7-division polynomial, so its roots are exactly the
`x`-coordinates of the order-7 points.

Its degree is `(7² − 1)/2 = 24` — obtained by instantiating Mathlib's general degree formula
`natDegree_preΨ'` at `n = 7` over `𝔽_p`, needing only `7 ≠ 0` in `𝔽_p`. Hence secp256k1 has
at most 24 nontrivial 7-torsion `x`-coordinates, i.e. `#E[7] ≤ 49` — consistent with the
classical structure `E[7] ≅ (ℤ/7)²` (48 nontrivial points, `±y` per `x` ⇒ 24 `x`-coords).
A concrete named level of the uniform `secp256k1_odd_torsion_x_card_le` (`#E[n] ≤ n²`), in
the same spirit as the 3- and 5-torsion nodes. All polynomial/degree facts over `𝔽_p`; no axioms.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **`deg (preΨ' 7) = 24`** (7-torsion bound). The secp256k1 7-division polynomial
`ψ₇ = preΨ' 7` (odd index ⇒ no `ψ₂` factor) has degree `(7² − 1)/2 = 24`, instantiating
Mathlib's general `natDegree_preΨ'` at `n = 7`; the only hypothesis is `7 ≠ 0` in `𝔽_p`
(machine-checked: `p ∤ 7`). One rung above `secp256k1_preΨ₅_natDegree`. -/
theorem secp256k1_preΨ₇_natDegree : (secp256k1.preΨ' 7).natDegree = 24 := by
  have h7 : ((7 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
  rw [secp256k1.natDegree_preΨ' h7]
  decide

/-- The 7-division polynomial is nonzero (degree 24), so the 7-torsion `x`-coordinates form
a proper finite set. Mirrors `secp256k1_preΨ₅_ne_zero`. -/
theorem secp256k1_preΨ₇_ne_zero : secp256k1.preΨ' 7 ≠ 0 := by
  intro h
  have h24 : (secp256k1.preΨ' 7).natDegree = 24 := secp256k1_preΨ₇_natDegree
  rw [h, natDegree_zero] at h24
  exact absurd h24 (by norm_num)

/-- **At most 24 seven-torsion `x`-coordinates.** Since `ψ₇ = preΨ' 7` has degree 24, it has
at most 24 roots in `𝔽_p`; these are exactly the `x`-coordinates of the order-7 points, so
secp256k1 has at most 24 nontrivial 7-torsion `x`-coordinates (`#E[7] ≤ 49`, consistent with
`E[7] ≅ (ℤ/7)²`). Mirrors `secp256k1_five_torsion_x_card_le` one rung up. -/
theorem secp256k1_seven_torsion_x_card_le :
    Multiset.card (secp256k1.preΨ' 7).roots ≤ 24 :=
  (Polynomial.card_roots' _).trans secp256k1_preΨ₇_natDegree.le

end Ecdlp.Curve
