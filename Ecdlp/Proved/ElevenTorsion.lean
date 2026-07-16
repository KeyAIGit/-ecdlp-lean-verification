import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
# The secp256k1 11-division polynomial: degree and root bound (polynomial layer only)

Next odd rung of the division-polynomial tower above `preΨ' 7` (deg 24): the degree of
`preΨ' 11` is `(11² − 1)/2 = 60`, by instantiating Mathlib's general degree formula
`natDegree_preΨ'` at `n = 11` over `𝔽_p` (only hypothesis: `11 ≠ 0` in `𝔽_p`,
machine-checked `p ∤ 11`). Hence `preΨ' 11 ≠ 0` and its root multiset **in `𝔽_p`** has
at most 60 elements.

**Scope (what is NOT proved here).** These are polynomial-layer facts only. Unlike
`ℓ ∈ {2, 3, 5, 7}` (`TwoTorsion.lean`, `{Three,Five,Seven}TorsionBridge.lean`), the
point-level bridge `11•P = O ⟺ ψ₁₁(P) = 0` is **not** formalized for `ℓ = 11`, so no
statement about `E[11]`, its cardinality, or the geometric reading of these roots is
made or implied — neither over `𝔽_p` nor over `𝔽̄_p`. The classical expectation
`E[11] ≅ (ℤ/11)²` (⇒ ≤ 60 torsion `x`-coordinates) is the unproved *motivation* for
this rung, recorded here only as context. Instances of the proved uniform bound
`secp256k1_odd_preΨ_natDegree` / `secp256k1_odd_torsion_x_card_le`
(`OddTorsionBound.lean`) at `n = 11`, kept as a concrete named level. No axioms.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **`deg (preΨ' 11) = 60`.** The secp256k1 11-division polynomial `preΨ' 11` (odd
index ⇒ no `ψ₂` factor) has degree `(11² − 1)/2 = 60`, instantiating Mathlib's general
`natDegree_preΨ'` at `n = 11`; the only hypothesis is `11 ≠ 0` in `𝔽_p`
(machine-checked: `p ∤ 11`). One rung above `secp256k1_preΨ₇_natDegree`. Polynomial
degree fact only — see the module docstring for what this does *not* claim. -/
theorem secp256k1_preΨ₁₁_natDegree : (secp256k1.preΨ' 11).natDegree = 60 := by
  have h11 : ((11 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
  rw [secp256k1.natDegree_preΨ' h11]
  decide

/-- The 11-division polynomial is nonzero (it has degree 60), so its root multiset in
`𝔽_p` is well-defined and finite. Mirrors `secp256k1_preΨ₇_ne_zero`. -/
theorem secp256k1_preΨ₁₁_ne_zero : secp256k1.preΨ' 11 ≠ 0 := by
  intro h
  have h60 : (secp256k1.preΨ' 11).natDegree = 60 := secp256k1_preΨ₁₁_natDegree
  rw [h, natDegree_zero] at h60
  exact absurd h60 (by norm_num)

/-- **`preΨ' 11` has at most 60 roots in `𝔽_p`** (counted with multiplicity): a degree-60
polynomial has at most 60 roots. A polynomial-layer bound only — the root ↔ 11-torsion
correspondence is *not* formalized (no `ℓ = 11` bridge), so this carries no statement
about `E[11]`. Instance of `secp256k1_odd_torsion_x_card_le` at `n = 11`. -/
theorem secp256k1_preΨ₁₁_roots_card_le :
    Multiset.card (secp256k1.preΨ' 11).roots ≤ 60 :=
  (Polynomial.card_roots' _).trans secp256k1_preΨ₁₁_natDegree.le

end Ecdlp.Curve
