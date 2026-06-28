import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
# 3-torsion point count for secp256k1 via the 3-division polynomial

The 3-division polynomial `Ψ₃ = 3X⁴ + 84X` has **degree 4** over `𝔽_p`
(`secp256k1_Ψ₃_natDegree`), so it has at most 4 roots — hence secp256k1 has at most
4 nontrivial 3-torsion `x`-coordinates (`#E[3] ≤ 9`, the order-3 points plus `O`).
This mirrors the 2-torsion count (`secp256k1_two_torsion_x_card_le`) one rung up the
torsion tower. The 3-torsion is the GLV/CM-relevant torsion: the curve's complex
multiplication by `ℤ[ζ₃]` (source of the GLV endomorphism `λ`) acts on `E[3]`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- The 3-division polynomial is nonzero (it has degree 4), so the 3-torsion
`x`-coordinates form a proper finite set, not all of `𝔽_p`. Mirrors
`secp256k1_Ψ₂Sq_ne_zero`. -/
theorem secp256k1_Ψ₃_ne_zero : secp256k1.Ψ₃ ≠ 0 := by
  intro h
  have h4 : secp256k1.Ψ₃.natDegree = 4 := secp256k1_Ψ₃_natDegree
  rw [h, natDegree_zero] at h4
  exact absurd h4 (by norm_num)

/-- **At most 4 three-torsion `x`-coordinates.** Since `Ψ₃` has degree 4, it has at
most 4 roots in `𝔽_p`; these are exactly the `x`-coordinates of the order-3 points,
so secp256k1 has at most 4 nontrivial 3-torsion points (`#E[3] ≤ 9` with `O`).
Mirrors `secp256k1_two_torsion_x_card_le`. -/
theorem secp256k1_three_torsion_x_card_le :
    Multiset.card secp256k1.Ψ₃.roots ≤ 4 :=
  (Polynomial.card_roots' _).trans secp256k1_Ψ₃_natDegree.le

end Ecdlp.Curve
