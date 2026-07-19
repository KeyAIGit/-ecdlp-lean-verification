/-
# Uniform N7 induction — base rung `n = 1` of the ω-free joint carrier (grind, not merged)

Toward the uniform `x(n•P)=Φₙ/ΨSqₙ` on secp256k1 points (node S3b, `BARRIERS.md §B3`; target
`n7_uniform_secp256k1_x`). The multi-agent decomposition (ultracode) settled the induction on
`WeierstrassCurve.normEDSRec'` (even/odd strong recursion matching Mathlib's division-polynomial
recurrences), carrying **both** coordinates jointly, with the `y`-conjunct stated **ω-free** —
via the EDS omega-relation `4y·ωₙ = ψ(n+2)ψ(n-1)² − ψ(n-2)ψ(n+1)²` using only Mathlib's `ψ`
(there is no `ω` division polynomial in Mathlib).

This file discharges the **`n = 1` base rung** of that carrier — the first leaf `normEDSRec'`
demands — validating the ω-free `y`-conjunct format before the wall (`step_algebra`) is attacked.
Fully closed with existing API (kernel-checked); no `native_decide`.

Grind-in-progress: not imported into `Ecdlp.lean`, held on the feature branch per the "no merges
until the wall cracks or a final barrier" directive.
-/
import Mathlib
import Ecdlp.Proved.FiveTorsionBridge

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Base rung `n = 1`** of the uniform joint `(x,y)` carrier: for a nonsingular `P=(x,y)` on
secp256k1, since `1•P = P`, its coordinates satisfy `X = Φ₁(x)/ΨSq₁(x)` (`= x/1 = x`) and the
ω-free `y`-relation `Y·(4y)·ψ₁³ = ψ₃ψ₀² − ψ₋₁ψ₂²` (`= 4y²`). -/
theorem secp256k1_one_nsmul_coords
    (x y X Y : ZMod Secp256k1.p) (hc : y ^ 2 = x ^ 3 + 7)
    (h : secp256k1.toAffine.Nonsingular x y)
    (h' : secp256k1.toAffine.Nonsingular X Y)
    (hn : (1 : ℕ) • (Point.some x y h) = Point.some X Y h') :
    X = (secp256k1.Φ 1).eval x / (secp256k1.ΨSq 1).eval x
      ∧ Y * (4 * y) * ((secp256k1.ψ (1 : ℤ)).evalEval x y) ^ 3
          = (secp256k1.ψ 3).evalEval x y * ((secp256k1.ψ 0).evalEval x y) ^ 2
            - (secp256k1.ψ (-1)).evalEval x y * ((secp256k1.ψ 2).evalEval x y) ^ 2 := by
  rw [one_nsmul] at hn
  injection hn with hX hY
  subst hX hY
  refine ⟨?_, ?_⟩
  · rw [secp256k1.Φ_one, secp256k1.ΨSq_one, eval_X, eval_one, div_one]
  · rw [secp256k1.ψ_zero, secp256k1.ψ_one, show (-1 : ℤ) = -(1 : ℤ) from rfl, secp256k1.ψ_neg,
      secp256k1.ψ_one, secp256k1.ψ_two]
    rw [secp256k1_psi2_evalEval]
    simp only [evalEval_zero, evalEval_one, evalEval_neg]
    ring

end Ecdlp.Curve
