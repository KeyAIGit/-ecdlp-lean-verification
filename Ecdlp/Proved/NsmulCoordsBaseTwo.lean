/-
# Uniform N7 induction — base rung `n = 2` of the ω-free joint carrier (grind, not merged)

Second leaf of the `normEDSRec'` (even/odd strong) induction toward the uniform
`x(n•P)=Φₙ/ΨSqₙ` on secp256k1 points (node S3b, `BARRIERS.md §B3`; target
`n7_uniform_secp256k1_x`). The carrier holds **both** coordinates jointly, with the `y`-conjunct
stated **ω-free** — via the EDS omega-relation `4y·ωₙ = ψ(n+2)ψ(n-1)² − ψ(n-2)ψ(n+1)²` using only
Mathlib's `ψ` (there is no `ω` division polynomial in Mathlib).

Where `NsmulCoordsBaseOne` discharged the odd leaf `n = 1`, this file discharges the **even leaf
`n = 2`**, reshaping the two already-merged group-law facts into the joint ω-free format:

* `secp256k1_two_nsmul_coords` (`DoublingPointFormula`, PR #205) — Point-level `2•P=(Φ₂/Ψ₂Sq,
  ω₂/(2y)³)`;
* `secp256k1_omega_recurrence_two` (`OmegaRecurrenceAnchors`) — `ψ₄ψ₁² − ψ₀ψ₃² = 4y·ω₂`.

The `x`-conjunct is `secp256k1.ΨSq_two : ΨSq 2 = Ψ₂Sq` away from the doubling value; the
`y`-conjunct clears `Y = ω₂/(2y)³` against `ψ₂ = 2y` (so `ψ₂³ = (2y)³`) and the ω-recurrence
numerator `4y·ω₂`, using `2y ≠ 0` (from the non-2-torsion hypothesis). Kernel-checked, no
`native_decide`.

The uniform induction itself stays an open target (`Ecdlp/Targets/n7_uniform_carrier_induction.lean`),
excluded from the built base; this base rung is a standalone closed result.
-/
import Mathlib
import Ecdlp.Proved.DoublingPointFormula
import Ecdlp.Proved.OmegaRecurrenceAnchors

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Base rung `n = 2`** (even leaf) of the uniform joint `(x,y)` carrier: for a nonsingular
non-2-torsion `P=(x,y)` on secp256k1 whose double is the affine point `(X,Y)`, its coordinates
satisfy `X = Φ₂(x)/ΨSq₂(x)` and the ω-free `y`-relation
`Y·(4y)·ψ₂³ = ψ₄ψ₁² − ψ₀ψ₃²` (`= 4y·ω₂`, with `ω₂ = x⁶+140x³−392`). Reshapes the merged
`secp256k1_two_nsmul_coords` and `secp256k1_omega_recurrence_two` into the induction's joint
format. -/
theorem secp256k1_two_nsmul_coords_ωfree
    (x y X Y : ZMod Secp256k1.p) (hc : y ^ 2 = x ^ 3 + 7)
    (h : secp256k1.toAffine.Nonsingular x y)
    (h' : secp256k1.toAffine.Nonsingular X Y)
    (hy : y ≠ secp256k1.toAffine.negY x y)
    (hn : (2 : ℕ) • (Point.some x y h) = Point.some X Y h') :
    X = (secp256k1.Φ 2).eval x / (secp256k1.ΨSq 2).eval x
      ∧ Y * (4 * y) * ((secp256k1.ψ (2 : ℤ)).evalEval x y) ^ 3
          = (secp256k1.ψ 4).evalEval x y * ((secp256k1.ψ 1).evalEval x y) ^ 2
            - (secp256k1.ψ 0).evalEval x y * ((secp256k1.ψ 3).evalEval x y) ^ 2 := by
  obtain ⟨hX, hY⟩ := secp256k1_two_nsmul_coords x y X Y hc h h' hy hn
  refine ⟨?_, ?_⟩
  · rw [secp256k1.ΨSq_two]; exact hX
  · rw [hY, secp256k1.ψ_two, secp256k1_psi2_evalEval, secp256k1_omega_recurrence_two]
    have hnegY : secp256k1.toAffine.negY x y = -y := by
      simp [WeierstrassCurve.Affine.negY, secp256k1]
    have h2y : (2 : ZMod Secp256k1.p) * y ≠ 0 := by
      intro hh; exact hy (by rw [hnegY]; linear_combination hh)
    rw [div_mul_eq_mul_div, div_mul_eq_mul_div, div_eq_iff (pow_ne_zero 3 h2y)]
    ring

end Ecdlp.Curve
