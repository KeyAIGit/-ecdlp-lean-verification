import Mathlib
import Ecdlp.Proved.DoublingPointFormulaBar
import Ecdlp.Proved.TwoTorsionStructure
import Ecdlp.Proved.FiveTorsionBridgeBar

/-!
# The 4-torsion bridge over the algebraic closure

For an affine point of `secp256k1Bar`, multiplication by four vanishes exactly when the
fourth division polynomial vanishes. The proof is the closure port of
`FourTorsionBridge.lean`: split off the two-torsion case, then identify four-torsion with
two-torsion of the double through the closure doubling `y`-coordinate formula.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine
open scoped Classical

private noncomputable abbrev φK :
    ZMod Secp256k1.p →+* AlgebraicClosure (ZMod Secp256k1.p) :=
  algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p))

private theorem φK_ne_zero {c : ZMod Secp256k1.p} (hc : c ≠ 0) : φK c ≠ 0 := by
  intro h0
  exact hc (RingHom.injective φK (by rw [map_zero]; exact h0))

private theorem two_ne_zero_bar :
    (2 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
  have h2p : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]
      decide
    simpa using h
  have hφ := φK_ne_zero h2p
  rwa [map_ofNat] at hφ

private theorem secp256k1Bar_curve_of_nonsingular
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) :
    y ^ 2 = x ^ 3 + 7 := by
  have he : secp256k1Bar.toAffine.Equation x y := h.1
  rw [WeierstrassCurve.Affine.equation_iff] at he
  simp only [secp256k1Bar, WeierstrassCurve.map, WeierstrassCurve.map_a₁,
    WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄,
    WeierstrassCurve.map_a₆, secp256k1, map_zero, map_ofNat] at he
  linear_combination he

private theorem secp256k1Bar_negY
    (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.negY x y = -y := by
  simp [WeierstrassCurve.Affine.negY, secp256k1Bar, WeierstrassCurve.map, secp256k1]

/-- An affine point of `secp256k1Bar` is killed by four iff `ψ₄` vanishes there. -/
theorem secp256k1Bar_four_nsmul_eq_zero_iff
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) :
    (4 : ℕ) • Point.some x y h = 0 ↔
      (secp256k1Bar.ψ 4).evalEval x y = 0 := by
  have h2ne := two_ne_zero_bar
  have hcurve := secp256k1Bar_curve_of_nonsingular x y h
  have hnegY := secp256k1Bar_negY x y
  have hψ4 :
      (secp256k1Bar.ψ 4).evalEval x y =
        4 * y * (x ^ 6 + 140 * x ^ 3 - 392) := by
    rw [secp256k1Bar.ψ_four]
    simp only [evalEval_mul, evalEval_C]
    rw [secp256k1Bar_preΨ₄_eval, secp256k1Bar_psi2_evalEval]
    ring
  rw [hψ4, show (4 : ℕ) = 2 + 2 from rfl, add_nsmul]
  by_cases hy0 : y = secp256k1Bar.toAffine.negY x y
  · have hyeq : y = 0 := by
      have h2y : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * y = 0 := by
        rw [hnegY] at hy0
        linear_combination hy0
      rcases mul_eq_zero.mp h2y with h2 | hy
      · exact absurd h2 h2ne
      · exact hy
    have h2P : (2 : ℕ) • Point.some x y h = 0 := by
      rw [two_nsmul]
      exact Point.add_self_of_Y_eq hy0
    rw [h2P, add_zero]
    exact iff_of_true rfl (by rw [hyeq]; ring)
  · have hy : y ≠ 0 := fun h0 => hy0 (by rw [hnegY, h0]; ring)
    have h2yne :
        (2 : AlgebraicClosure (ZMod Secp256k1.p)) * y ≠ 0 :=
      mul_ne_zero h2ne hy
    have hns2 : secp256k1Bar.toAffine.Nonsingular
        (secp256k1Bar.toAffine.addX x x (secp256k1Bar.toAffine.slope x x y y))
        (secp256k1Bar.toAffine.addY x x y (secp256k1Bar.toAffine.slope x x y y)) :=
      nonsingular_add h h (fun hxy => hy0 hxy.2)
    set X2 := secp256k1Bar.toAffine.addX x x
      (secp256k1Bar.toAffine.slope x x y y) with hX2
    set Y2 := secp256k1Bar.toAffine.addY x x y
      (secp256k1Bar.toAffine.slope x x y y) with hY2
    have hP2 :
        (2 : ℕ) • Point.some x y h = Point.some X2 Y2 hns2 := by
      rw [two_nsmul]
      exact Point.add_self_of_Y_ne hy0
    obtain ⟨-, hY2val⟩ :=
      secp256k1Bar_two_nsmul_coords x y X2 Y2 hcurve h hns2 hy0 hP2
    rw [hP2, ← two_nsmul,
      secp256k1Bar_two_nsmul_eq_zero_iff X2 Y2 hns2, hY2val,
      div_eq_zero_iff, or_iff_left (pow_ne_zero 3 h2yne)]
    have h4yne :
        (4 : AlgebraicClosure (ZMod Secp256k1.p)) * y ≠ 0 := by
      rw [show (4 : AlgebraicClosure (ZMod Secp256k1.p)) = 2 * 2 by norm_num]
      exact mul_ne_zero (mul_ne_zero h2ne h2ne) hy
    constructor
    · intro hω
      rw [hω]
      ring
    · intro h4ω
      rcases mul_eq_zero.mp h4ω with hc | hc
      · exact absurd hc h4yne
      · exact hc

end Ecdlp.Curve
