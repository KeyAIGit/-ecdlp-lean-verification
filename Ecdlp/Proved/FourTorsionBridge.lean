/-
# Division-polynomial 4-torsion bridge for secp256k1 (both directions)

The `n = 4` case of the division-polynomial ↔ torsion bridge, filling the even-index gap in the
landed `{2,3,5,7}` family (`TwoTorsionPoint`, `ThreeTorsionBridge`, `FiveTorsionBridge`,
`SevenTorsionBridge`). For a nonzero affine point `P = (x, y)` of secp256k1,

  `4 • P = 0  ⟺  ψ₄(P) = 0`.

Unlike the odd bridges (which square a chord/secant relation), `n = 4` runs by **doubling of
doubling**: `4•P = 2•(2•P)`, so `4•P = 0` iff `2•P` is 2-torsion. The 2-torsion criterion
`secp256k1_two_nsmul_eq_zero_iff` (`2•Q = 0 ⟺ Y_Q = 0`) reduces this to `Y(2•P) = 0`, and the
landed doubling `y`-coordinate `Y(2•P) = ω₂/(2y)³` (`secp256k1_two_nsmul_coords`,
`DoublingPointFormula`) evaluates `Y(2•P) = 0 ⟺ ω₂(x) = 0`. Since
`ψ₄(P) = 4y·ω₂(x)` with `ω₂ = x⁶+140x³−392`, both sides coincide.

This is the `n = 4` non-degeneracy leaf of the uniform carrier (`BARRIERS.md §B3`): the
strengthened `Carrier` predicate carries `n•P affine ⟺ ψₙ(P) ≠ 0`, and this supplies its `n = 4`
instance. No `native_decide` beyond the shared `2 ≠ 0` fact; no new axioms.
-/
import Mathlib
import Ecdlp.Proved.DoublingPointFormula
import Ecdlp.Proved.TwoTorsionPoint
import Ecdlp.Proved.FiveTorsionBridge

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Point-level 4-torsion criterion: `4 • P = 0 ⟺ ψ₄(P) = 0`.** For a nonzero affine point
`P = (x, y)` of secp256k1, its order divides 4 iff the 4-division polynomial vanishes at `P`.
Runs by doubling-of-doubling: `4•P = 2•(2•P)`, so `4•P = 0 ⟺ Y(2•P) = 0` (2-torsion of the
double), and `Y(2•P) = ω₂/(2y)³` gives `Y(2•P) = 0 ⟺ ω₂(x) = 0 ⟺ ψ₄(P) = 4y·ω₂ = 0`. Fills the
even-index gap in the `{2,3,5,7}` torsion-bridge family. -/
theorem secp256k1_four_nsmul_eq_zero_iff (x y : ZMod Secp256k1.p)
    (h : secp256k1.toAffine.Nonsingular x y) :
    (4 : ℕ) • (Point.some x y h) = 0 ↔ (secp256k1.ψ 4).evalEval x y = 0 := by
  have h2ne : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
    simpa using this
  have hcurve : y ^ 2 = x ^ 3 + 7 := by
    have he : secp256k1.toAffine.Equation x y := h.1
    rw [WeierstrassCurve.Affine.equation_iff] at he
    simp only [secp256k1] at he
    linear_combination he
  have hnegY : secp256k1.toAffine.negY x y = -y := by
    simp [WeierstrassCurve.Affine.negY, secp256k1]
  have hψ4 : (secp256k1.ψ 4).evalEval x y = 4 * y * (x ^ 6 + 140 * x ^ 3 - 392) := by
    rw [secp256k1.ψ_four]
    simp only [evalEval_mul, evalEval_C]
    rw [secp256k1_preΨ₄_eval, secp256k1_psi2_evalEval]
    ring
  rw [hψ4, show (4 : ℕ) = 2 + 2 from rfl, add_nsmul]
  by_cases hy0 : y = secp256k1.toAffine.negY x y
  · -- `P` is 2-torsion: `2•P = 0`, so `2•P + 2•P = 0`; RHS `4y·ω₂ = 0` since `y = 0`.
    have hyeq : y = 0 := by
      have h2y : (2 : ZMod Secp256k1.p) * y = 0 := by rw [hnegY] at hy0; linear_combination hy0
      rcases mul_eq_zero.mp h2y with h2 | hy
      · exact absurd h2 h2ne
      · exact hy
    have h2P : (2 : ℕ) • Point.some x y h = 0 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_eq hy0
    rw [h2P, add_zero]
    exact iff_of_true rfl (by rw [hyeq]; ring)
  · -- `P` not 2-torsion: `2•P = some X2 Y2`; `4•P = 2•(2•P) = 0 ⟺ Y2 = 0 ⟺ ω₂(x) = 0`.
    have hy : y ≠ 0 := fun h0 => hy0 (by rw [hnegY, h0]; ring)
    have h2yne : (2 : ZMod Secp256k1.p) * y ≠ 0 := mul_ne_zero h2ne hy
    have hns2 : secp256k1.toAffine.Nonsingular
        (secp256k1.toAffine.addX x x (secp256k1.toAffine.slope x x y y))
        (secp256k1.toAffine.addY x x y (secp256k1.toAffine.slope x x y y)) :=
      nonsingular_add h h (fun hxy => hy0 hxy.2)
    set X2 := secp256k1.toAffine.addX x x (secp256k1.toAffine.slope x x y y) with hX2
    set Y2 := secp256k1.toAffine.addY x x y (secp256k1.toAffine.slope x x y y) with hY2
    have hP2 : (2 : ℕ) • Point.some x y h = Point.some X2 Y2 hns2 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_ne hy0
    obtain ⟨-, hY2val⟩ := secp256k1_two_nsmul_coords x y X2 Y2 hcurve h hns2 hy0 hP2
    rw [hP2, ← two_nsmul, secp256k1_two_nsmul_eq_zero_iff X2 Y2 hns2, hY2val,
      div_eq_zero_iff, or_iff_left (pow_ne_zero 3 h2yne)]
    have h4yne : (4 : ZMod Secp256k1.p) * y ≠ 0 := by
      rw [show (4 : ZMod Secp256k1.p) = 2 * 2 by norm_num]
      exact mul_ne_zero (mul_ne_zero h2ne h2ne) hy
    constructor
    · intro hω; rw [hω]; ring
    · intro h4ω
      rcases mul_eq_zero.mp h4ω with hc | hc
      · exact absurd hc h4yne
      · exact hc

end Ecdlp.Curve
