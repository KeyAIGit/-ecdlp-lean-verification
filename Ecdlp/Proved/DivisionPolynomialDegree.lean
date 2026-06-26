import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.Secp256k1PrimeP

/-!
# Degree of the secp256k1 2-division polynomial (torsion point count)

The 2-division polynomial `Ψ₂Sq = 4X³ + 28` has **degree 3** over `𝔽_p`, so it has
at most 3 roots — hence secp256k1 has at most 3 nontrivial 2-torsion `x`-coordinates,
i.e. `#E[2] ≤ 4` (the three order-2 points plus `O`). This is the first concrete
*torsion-count* fact, the degree side of the division-polynomial picture (Mathlib's
`DivisionPolynomial.Degree`). Uses the machine-checked primality of `p` (so `𝔽_p`
is a field / has no zero divisors and the leading coefficient `4 ≠ 0`).
-/

namespace Ecdlp.Curve

open Polynomial

/-- **`Ψ₂Sq` has degree 3.** The secp256k1 2-division polynomial `4X³ + 28` has
`natDegree = 3`, so at most 3 two-torsion `x`-coordinates exist (`#E[2] ≤ 4`). -/
theorem secp256k1_Ψ₂Sq_natDegree : secp256k1.Ψ₂Sq.natDegree = 3 := by
  have h4 : (4 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((4 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
    simpa using h
  rw [secp256k1_Ψ₂Sq, natDegree_add_eq_left_of_natDegree_lt]
  · rw [natDegree_C_mul h4, natDegree_X_pow]
  · rw [natDegree_C_mul h4, natDegree_X_pow, natDegree_C]; norm_num

end Ecdlp.Curve
