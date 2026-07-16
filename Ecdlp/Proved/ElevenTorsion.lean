import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
# 11-torsion point count for secp256k1 via the 11-division polynomial

Next concrete rung of the torsion tower above `ψ₇` (deg 24): the `11`-division polynomial
`ψ₁₁ = Ψ₁₁`. Because `11` is **odd**, Mathlib's factorisation `Ψₙ = preΨₙ` (no `ψ₂` factor)
means `preΨ' 11` *is* the genuine 11-division polynomial, so its roots are exactly the
`x`-coordinates of the order-11 points.

Its degree is `(11² − 1)/2 = 60` — obtained by instantiating Mathlib's general degree
formula `natDegree_preΨ'` at `n = 11` over `𝔽_p`, needing only `11 ≠ 0` in `𝔽_p`. Hence
secp256k1 has at most 60 nontrivial 11-torsion `x`-coordinates, i.e. `#E[11] ≤ 121` —
consistent with the classical structure `E[11] ≅ (ℤ/11)²` (120 nontrivial points, `±y` per
`x` ⇒ 60 `x`-coords). A concrete named level of the uniform
`secp256k1_odd_torsion_x_card_le` (`#E[n] ≤ n²`), in the same spirit as the 3-, 5- and
7-torsion nodes; closes the `eleven_torsion_degree` prover-loop target. All
polynomial/degree facts over `𝔽_p`; no axioms.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **`deg (preΨ' 11) = 60`** (11-torsion bound). The secp256k1 11-division polynomial
`ψ₁₁ = preΨ' 11` (odd index ⇒ no `ψ₂` factor) has degree `(11² − 1)/2 = 60`, instantiating
Mathlib's general `natDegree_preΨ'` at `n = 11`; the only hypothesis is `11 ≠ 0` in `𝔽_p`
(machine-checked: `p ∤ 11`). One rung above `secp256k1_preΨ₇_natDegree`. -/
theorem secp256k1_preΨ₁₁_natDegree : (secp256k1.preΨ' 11).natDegree = 60 := by
  have h11 : ((11 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
  rw [secp256k1.natDegree_preΨ' h11]
  decide

/-- The 11-division polynomial is nonzero (degree 60), so the 11-torsion `x`-coordinates
form a proper finite set. Mirrors `secp256k1_preΨ₇_ne_zero`. -/
theorem secp256k1_preΨ₁₁_ne_zero : secp256k1.preΨ' 11 ≠ 0 := by
  intro h
  have h60 : (secp256k1.preΨ' 11).natDegree = 60 := secp256k1_preΨ₁₁_natDegree
  rw [h, natDegree_zero] at h60
  exact absurd h60 (by norm_num)

/-- **At most 60 eleven-torsion `x`-coordinates.** Since `ψ₁₁ = preΨ' 11` has degree 60, it
has at most 60 roots in `𝔽_p`; these are exactly the `x`-coordinates of the order-11 points,
so secp256k1 has at most 60 nontrivial 11-torsion `x`-coordinates (`#E[11] ≤ 121`,
consistent with `E[11] ≅ (ℤ/11)²`). Mirrors `secp256k1_seven_torsion_x_card_le` one rung
up. -/
theorem secp256k1_eleven_torsion_x_card_le :
    Multiset.card (secp256k1.preΨ' 11).roots ≤ 60 :=
  (Polynomial.card_roots' _).trans secp256k1_preΨ₁₁_natDegree.le

end Ecdlp.Curve
