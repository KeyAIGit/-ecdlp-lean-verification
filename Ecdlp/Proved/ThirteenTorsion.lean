import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
# The secp256k1 13-division polynomial: degree and root bound (polynomial layer only)

Division-polynomial tower rung above `preΨ' 11` (deg 60): the degree of `preΨ' 13` is
`(13² − 1)/2 = 84`, by instantiating Mathlib's general degree formula `natDegree_preΨ'`
at `n = 13` over `𝔽_p` (only hypothesis: `13 ≠ 0` in `𝔽_p`, machine-checked `p ∤ 13`).
Hence `preΨ' 13 ≠ 0` and its root multiset **in `𝔽_p`** has at most 84 elements.

**Scope (what is NOT proved here).** These are polynomial-layer facts only. Unlike
`ℓ ∈ {2, 3, 5, 7}`, the point-level bridge `13•P = O ⟺ ψ₁₃(P) = 0` is **not**
formalized for `ℓ = 13`, so no statement about `E[13]`, its cardinality, or the
geometric reading of these roots is made or implied — neither over `𝔽_p` nor over
`𝔽̄_p`. The classical expectation `E[13] ≅ (ℤ/13)²` (⇒ ≤ 84 torsion `x`-coordinates)
is the unproved *motivation* for this rung, recorded here only as context. Instances of
the proved uniform bound `secp256k1_odd_preΨ_natDegree` /
`secp256k1_odd_torsion_x_card_le` (`OddTorsionBound.lean`) at `n = 13`. No axioms.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **`deg (preΨ' 13) = 84`.** The secp256k1 13-division polynomial `preΨ' 13` (odd
index ⇒ no `ψ₂` factor) has degree `(13² − 1)/2 = 84`, instantiating Mathlib's general
`natDegree_preΨ'` at `n = 13`; the only hypothesis is `13 ≠ 0` in `𝔽_p`
(machine-checked: `p ∤ 13`). One rung above `secp256k1_preΨ₁₁_natDegree`. Polynomial
degree fact only — see the module docstring for what this does *not* claim. -/
theorem secp256k1_preΨ₁₃_natDegree : (secp256k1.preΨ' 13).natDegree = 84 := by
  have h13 : ((13 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
  rw [secp256k1.natDegree_preΨ' h13]
  decide

/-- The 13-division polynomial is nonzero (it has degree 84), so its root multiset in
`𝔽_p` is well-defined and finite. Mirrors `secp256k1_preΨ₁₁_ne_zero`. -/
theorem secp256k1_preΨ₁₃_ne_zero : secp256k1.preΨ' 13 ≠ 0 := by
  intro h
  have h84 : (secp256k1.preΨ' 13).natDegree = 84 := secp256k1_preΨ₁₃_natDegree
  rw [h, natDegree_zero] at h84
  exact absurd h84 (by norm_num)

/-- **`preΨ' 13` has at most 84 roots in `𝔽_p`** (counted with multiplicity): a degree-84
polynomial has at most 84 roots. A polynomial-layer bound only — the root ↔ 13-torsion
correspondence is *not* formalized (no `ℓ = 13` bridge), so this carries no statement
about `E[13]`. Instance of `secp256k1_odd_torsion_x_card_le` at `n = 13`. -/
theorem secp256k1_preΨ₁₃_roots_card_le :
    Multiset.card (secp256k1.preΨ' 13).roots ≤ 84 :=
  (Polynomial.card_roots' _).trans secp256k1_preΨ₁₃_natDegree.le

end Ecdlp.Curve
