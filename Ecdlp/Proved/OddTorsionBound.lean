import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
# A uniform odd-torsion bound for secp256k1

The per-level torsion nodes (`Ψ₃` → `#E[3]`, `ψ₅` → `#E[5]`) are instances of a single
parametric fact. For **every odd `n` coprime to `p`** (`n ≠ 0` in `𝔽_p`), the `n`-division
polynomial `ψₙ = preΨ' n` — odd index, so no `ψ₂` factor — has degree exactly `(n² − 1)/2`,
hence at most `(n² − 1)/2` roots. Those roots are the `x`-coordinates of the order-`n`
points, so secp256k1 has at most `(n² − 1)/2` nontrivial `n`-torsion `x`-coordinates, i.e.
`#E[n] ≤ n²` — the ceiling reached exactly by the classical structure `E[n] ≅ (ℤ/n)²`.

This is the general statement the concrete `ThreeTorsion` / `FiveTorsion` nodes instantiate;
it needs only the machine-checked non-vanishing `n ≢ 0 (mod p)`. Pure degree/root facts over
`𝔽_p`; no `[Fact p.Prime]` variable, no axioms.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **`deg(ψₙ) = (n² − 1)/2` for odd `n` coprime to `p`.** For odd `n`, Mathlib's
`Ψₙ = preΨₙ` (no `ψ₂` factor), and the general degree formula `natDegree_preΨ'` collapses
to `(n² − 1)/2`. The only hypotheses: `n` is odd and `n ≠ 0` in `𝔽_p`. -/
theorem secp256k1_odd_preΨ_natDegree {n : ℕ} (hodd : ¬ Even n)
    (hn : ((n : ℕ) : ZMod Secp256k1.p) ≠ 0) :
    (secp256k1.preΨ' n).natDegree = (n ^ 2 - 1) / 2 := by
  rw [secp256k1.natDegree_preΨ' hn, if_neg hodd]

/-- **At most `(n² − 1)/2` nontrivial `n`-torsion `x`-coordinates for odd `n` coprime to
`p`** (`#E[n] ≤ n²`). Since `ψₙ = preΨ' n` has degree `(n² − 1)/2`, it has at most that many
roots in `𝔽_p`; for odd `n` these are exactly the `x`-coordinates of the order-`n` points.
The uniform statement behind `secp256k1_three_torsion_x_card_le` /
`secp256k1_five_torsion_x_card_le`. -/
theorem secp256k1_odd_torsion_x_card_le {n : ℕ} (hodd : ¬ Even n)
    (hn : ((n : ℕ) : ZMod Secp256k1.p) ≠ 0) :
    Multiset.card (secp256k1.preΨ' n).roots ≤ (n ^ 2 - 1) / 2 :=
  (Polynomial.card_roots' _).trans (secp256k1_odd_preΨ_natDegree hodd hn).le

end Ecdlp.Curve
