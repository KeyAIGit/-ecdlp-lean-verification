import Mathlib
import Ecdlp.Proved.DivisionPolynomial

/-!
# Division-polynomial 3-torsion bridge for secp256k1

The point-level `n = 3` case of the division-polynomial ↔ torsion bridge: it upgrades the
forward-only "a 3-torsion point is a root of `Ψ₃`" fact to a full **equivalence** between the
group condition `3 • P = 0` and the vanishing of the 3-division polynomial `ψ 3` at `P`.

This is the `n = 3` analogue of the `n = 2` bridge in `Ecdlp/Proved/TwoTorsionPoint.lean`, and
it is an original elementary proof on the Mathlib master API (the general-`n` bridge routes
through the universal-curve / function-field machinery, which is not in Mathlib v4.31; see
`notes/UPSTREAM_SCAN.md`). The crux is the rational identity
`addX(P,P) - x = -(3x⁴+84x)/(4y²)`, so the doubled point returns to `x(-P)` exactly when
`3x⁴ + 84x = 0`; the `y`-coordinate then agrees automatically.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

/-- **The bivariate 3-division polynomial `ψ 3` evaluated at any point `(x,y)` of secp256k1
equals the concrete univariate `3x⁴ + 84x`.** (`ψ 3` is odd, hence univariate in `x`.) -/
theorem secp256k1_psi3_evalEval (x y : ZMod Secp256k1.p) :
    (secp256k1.ψ 3).evalEval x y = 3 * x ^ 4 + 84 * x := by
  rw [WeierstrassCurve.ψ_three, secp256k1_Ψ₃, Polynomial.evalEval_C]
  simp only [Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_ofNat,
    Polynomial.eval_pow, Polynomial.eval_C, Polynomial.eval_X]
  ring

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Point-level 3-torsion criterion for secp256k1: `3 • P = 0 ⟺ ψ 3` vanishes at `P`.**
For a nonzero affine point `P = (x, y)`, the group relation `3 • P = 0` holds iff the
3-division polynomial vanishes at `P` (equivalently `3x⁴ + 84x = 0`). Upgrades the forward-only
`secp256k1_Ψ₃`-root fact to a full equivalence — the `ψ₃ ↔ E[3]` bridge. -/
theorem secp256k1_three_nsmul_eq_zero_iff
    (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y) :
    (3 : ℕ) • (Point.some x y h) = 0 ↔ (secp256k1.ψ 3).evalEval x y = 0 := by
  rw [secp256k1_psi3_evalEval]
  have h2ne : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  have hp7 : (7 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((7 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  have hp63 : (63 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((63 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  have hcurve : y ^ 2 = x ^ 3 + 7 := by
    have he : secp256k1.toAffine.Equation x y := h.1
    rw [WeierstrassCurve.Affine.equation_iff] at he
    simp only [secp256k1] at he
    linear_combination he
  have hnegY : secp256k1.toAffine.negY x y = -y := by
    simp [WeierstrassCurve.Affine.negY, secp256k1]
  have key : (3 : ℕ) • Point.some x y h
      = Point.some x y h + Point.some x y h + Point.some x y h := by
    rw [show (3 : ℕ) = 2 + 1 from rfl, add_nsmul, two_nsmul, one_nsmul]
  rw [key, add_eq_zero_iff_eq_neg]
  by_cases hy0 : y = secp256k1.toAffine.negY x y
  · rw [Point.add_self_of_Y_eq hy0]
    refine iff_of_false ?_ ?_
    · rw [eq_comm, neg_eq_zero]; exact Point.some_ne_zero h
    · intro hpoly
      have hy00 : y = 0 := by
        have h2y0 : (2 : ZMod Secp256k1.p) * y = 0 := by
          rw [hnegY] at hy0; linear_combination hy0
        rcases mul_eq_zero.mp h2y0 with h2 | hy
        · exact absurd h2 h2ne
        · exact hy
      have hx3 : x ^ 3 = -7 := by
        have hc0 := hcurve; rw [hy00] at hc0; linear_combination -hc0
      have hxne : x ≠ 0 := by
        intro hx0; rw [hx0] at hx3; exact hp7 (by linear_combination hx3)
      have h63x : (63 : ZMod Secp256k1.p) * x = 0 := by
        linear_combination hpoly - 3 * x * hx3
      rcases mul_eq_zero.mp h63x with h63 | hx0
      · exact hp63 h63
      · exact hxne hx0
  · have h2y : (2 : ZMod Secp256k1.p) * y ≠ 0 := by
      intro hc; exact hy0 (by rw [hnegY]; linear_combination hc)
    have hd : y - secp256k1.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy0
    have h4 : (4 : ZMod Secp256k1.p) * y ^ 2 ≠ 0 := by
      have hmm := mul_ne_zero h2y h2y
      intro hc; exact hmm (by linear_combination hc)
    rw [Point.add_of_Y_ne hy0, Point.neg_some, Point.some.injEq]
    set ℓ := secp256k1.toAffine.slope x x y y with hℓ
    have hsl' : ℓ * (2 * y) = 3 * x ^ 2 := by
      rw [hℓ, WeierstrassCurve.Affine.slope_of_Y_ne rfl hy0,
        div_mul_eq_mul_div, div_eq_iff hd]
      simp only [secp256k1, WeierstrassCurve.Affine.negY]
      ring
    have hAid : secp256k1.toAffine.addX x x ℓ - x
        = (-(3 * x ^ 4 + 84 * x)) / (4 * y ^ 2) := by
      rw [eq_div_iff h4]
      simp only [WeierstrassCurve.Affine.addX, secp256k1]
      linear_combination (2 * y * ℓ + 3 * x ^ 2) * hsl' - 12 * x * hcurve
    have hA : secp256k1.toAffine.addX x x ℓ = x ↔ 3 * x ^ 4 + 84 * x = 0 := by
      constructor
      · intro hh
        have hz : secp256k1.toAffine.addX x x ℓ - x = 0 := sub_eq_zero.mpr hh
        rw [hAid, div_eq_zero_iff] at hz
        rcases hz with h1 | h2
        · exact neg_eq_zero.mp h1
        · exact absurd h2 h4
      · intro hh
        have hz : secp256k1.toAffine.addX x x ℓ - x = 0 := by
          rw [hAid]; simp only [hh, neg_zero, zero_div]
        exact sub_eq_zero.mp hz
    have hB : secp256k1.toAffine.addX x x ℓ = x →
        secp256k1.toAffine.addY x x y ℓ = secp256k1.toAffine.negY x y := by
      intro hx
      simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
        WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1] at hx ⊢
      linear_combination (-ℓ) * hx
    constructor
    · rintro ⟨ha, _⟩; exact hA.mp ha
    · intro hpoly
      have ha := hA.mpr hpoly
      exact ⟨ha, hB ha⟩

end Ecdlp.Curve
