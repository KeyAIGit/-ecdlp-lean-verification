import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
# 5-torsion point count for secp256k1 via the 5-division polynomial

Next rung of the torsion tower, above `Ψ₂Sq` (deg 3) → `Ψ₃` (deg 4) → `preΨ₄` (deg 6).
The `5`-division polynomial `ψ₅ = Ψ₅` governs the 5-torsion `E[5]`. Because `5` is **odd**,
Mathlib's factorisation `Ψₙ = preΨₙ` (no `ψ₂` factor) means `preΨ' 5` *is* the genuine
5-division polynomial, so its roots are exactly the `x`-coordinates of the order-5 points.

Its degree is `(5² − 1)/2 = 12` — obtained here by instantiating Mathlib's **general**
degree formula `natDegree_preΨ'` (`(preΨ' n).natDegree = (n² − [Even n] · 3 − 1)/2`) at
`n = 5` over `𝔽_p`, needing only `5 ≠ 0` in `𝔽_p`. Hence secp256k1 has at most 12
nontrivial 5-torsion `x`-coordinates, i.e. `#E[5] ≤ 25` — consistent with the classical
structure `E[5] ≅ (ℤ/5)²` (24 nontrivial points, `±y` per `x` ⇒ 12 `x`-coordinates).
Everything is a polynomial/degree fact over `𝔽_p`; no `[Fact p.Prime]`, no axioms.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **`deg (preΨ' 5) = 12`** (5-torsion bound). The secp256k1 5-division polynomial
`ψ₅ = preΨ' 5` (odd index ⇒ no `ψ₂` factor) has degree `(5² − 1)/2 = 12`, instantiating
Mathlib's general `natDegree_preΨ'` at `n = 5`; the only hypothesis is `5 ≠ 0` in `𝔽_p`
(machine-checked: `p ∤ 5`). Extends `secp256k1_Ψ₃_natDegree` / `secp256k1_preΨ₄_natDegree`
one rung up the tower. -/
theorem secp256k1_preΨ₅_natDegree : (secp256k1.preΨ' 5).natDegree = 12 := by
  have h5 : ((5 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
  rw [secp256k1.natDegree_preΨ' h5]
  decide

/-- The 5-division polynomial is nonzero (it has degree 12), so the 5-torsion
`x`-coordinates form a proper finite set, not all of `𝔽_p`. Mirrors
`secp256k1_Ψ₃_ne_zero`. -/
theorem secp256k1_preΨ₅_ne_zero : secp256k1.preΨ' 5 ≠ 0 := by
  intro h
  have h12 : (secp256k1.preΨ' 5).natDegree = 12 := secp256k1_preΨ₅_natDegree
  rw [h, natDegree_zero] at h12
  exact absurd h12 (by norm_num)

/-- **At most 12 five-torsion `x`-coordinates.** Since `ψ₅ = preΨ' 5` has degree 12, it has
at most 12 roots in `𝔽_p`; these are exactly the `x`-coordinates of the order-5 points, so
secp256k1 has at most 12 nontrivial 5-torsion `x`-coordinates (`#E[5] ≤ 25`, consistent with
`E[5] ≅ (ℤ/5)²`). Mirrors `secp256k1_three_torsion_x_card_le` one rung up. -/
theorem secp256k1_five_torsion_x_card_le :
    Multiset.card (secp256k1.preΨ' 5).roots ≤ 12 :=
  (Polynomial.card_roots' _).trans secp256k1_preΨ₅_natDegree.le

end Ecdlp.Curve
