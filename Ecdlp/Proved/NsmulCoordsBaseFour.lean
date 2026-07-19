/-
# Uniform N7 induction — base rung `n = 4` of the ω-free joint carrier

Fourth (even) leaf of the `normEDSRec'` induction toward the uniform `x(n•P)=Φₙ/ΨSqₙ` on
secp256k1 points (node S3b, `BARRIERS.md §B3`; target `n7_uniform_secp256k1_x`). The carrier holds
**both** coordinates jointly, with the `y`-conjunct stated **ω-free** — via the EDS omega-relation
`4y·ωₙ = ψ(n+2)ψ(n-1)² − ψ(n-2)ψ(n+1)²` using only Mathlib's `ψ`.

Where `NsmulCoordsBaseTwo` discharged the even leaf `n = 2`, this file discharges the **even leaf
`n = 4`**, the last missing base rung of `carrier_four`. It reshapes the two landed `n = 4`
coordinate results into the joint ω-free format:

* `secp256k1_quadruple_x_eq_Φ₄_div_ΨSq₄` (`QuadrupleMultiplicationFormula`) — `x(4•P)=Φ₄/ΨSq₄`;
* `secp256k1_quadruple_y` (`QuadrupleMultiplicationYFormula`) — `Y·ψ₄³ = ω₄` (`y(4•P)=ω₄/ψ₄³`);
* `secp256k1_omega_recurrence_four` (`OmegaRecurrenceAnchors`) — `ψ₆ψ₃² − ψ₂ψ₅² = 4y·ω₄`.

The `x`-conjunct is exactly the quadruple-`x` value. The `y`-conjunct rewrites the ω-recurrence
numerator to `4y·ω₄`, evaluates `ψ₄ = preΨ₄·ψ₂ = (2x⁶+280x³−784)·2y`, and closes against
`secp256k1_quadruple_y` scaled by `4y`. Kernel-checked, no `native_decide`.

The uniform induction itself stays an open target
(`Ecdlp/Targets/n7_uniform_carrier_induction.lean`), excluded from the built base; this base rung is
a standalone closed result.
-/
import Mathlib
import Ecdlp.Proved.QuadrupleMultiplicationYFormula
import Ecdlp.Proved.OmegaRecurrenceAnchors

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Base rung `n = 4`** (even leaf) of the uniform joint `(x,y)` carrier: for a nonsingular
non-2-torsion `P=(x,y)` on secp256k1 whose quadruple is the affine point `(X,Y)`, its coordinates
satisfy `X = Φ₄(x)/ΨSq₄(x)` and the ω-free `y`-relation
`Y·(4y)·ψ₄³ = ψ₆ψ₃² − ψ₂ψ₅²` (`= 4y·ω₄`, with `ω₄` of degree 24). Reshapes the landed
`secp256k1_quadruple_x_eq_Φ₄_div_ΨSq₄`, `secp256k1_quadruple_y`, and
`secp256k1_omega_recurrence_four` into the induction's joint format. -/
theorem secp256k1_four_nsmul_coords_ωfree
    (x y X Y : ZMod Secp256k1.p) (hc : y ^ 2 = x ^ 3 + 7)
    (h : secp256k1.toAffine.Nonsingular x y)
    (h' : secp256k1.toAffine.Nonsingular X Y)
    (hy : y ≠ secp256k1.toAffine.negY x y)
    (hn : (4 : ℕ) • (Point.some x y h) = Point.some X Y h') :
    X = (secp256k1.Φ 4).eval x / (secp256k1.ΨSq 4).eval x
      ∧ Y * (4 * y) * ((secp256k1.ψ (4 : ℤ)).evalEval x y) ^ 3
          = (secp256k1.ψ 6).evalEval x y * ((secp256k1.ψ 3).evalEval x y) ^ 2
            - (secp256k1.ψ 2).evalEval x y * ((secp256k1.ψ 5).evalEval x y) ^ 2 := by
  have hnegY : secp256k1.toAffine.negY x y = -y := by
    simp [WeierstrassCurve.Affine.negY, secp256k1]
  have h2y : (2 : ZMod Secp256k1.p) * y ≠ 0 := by
    intro hh; exact hy (by rw [hnegY]; linear_combination hh)
  refine ⟨secp256k1_quadruple_x_eq_Φ₄_div_ΨSq₄ h hn, ?_⟩
  rw [secp256k1_omega_recurrence_four x y hc h2y]
  have hψ4 : (secp256k1.ψ (4 : ℤ)).evalEval x y = (2 * x ^ 6 + 280 * x ^ 3 - 784) * (2 * y) := by
    rw [secp256k1.ψ_four]
    simp only [evalEval_mul, evalEval_C]
    rw [secp256k1_preΨ₄_eval, secp256k1_psi2_evalEval]
  rw [hψ4]
  linear_combination (4 * y) * secp256k1_quadruple_y h hn

end Ecdlp.Curve
