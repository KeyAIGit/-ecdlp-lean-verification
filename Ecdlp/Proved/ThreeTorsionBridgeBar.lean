import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialEvalBridge

/-!
# The 3-torsion bridge over the algebraic closure `𝔽̄_p`

The point-level `n = 3` division-polynomial ↔ torsion bridge for `secp256k1Bar`, the
base change of secp256k1 to `K := AlgebraicClosure (ZMod Secp256k1.p)`: for a nonzero
affine point `P = (x, y)` of the closure curve, `3 • P = 0 ⟺ ψ₃(P) = 0 ⟺ 3x⁴ + 84x = 0`.

This is the port of `Ecdlp/Proved/ThreeTorsionBridge.lean` from `𝔽_p` to `𝔽̄_p`, and it is
**the missing link for the count `#E[3](𝔽̄_p) = 9`** (node N11 at `n = 3` of
`notes/DIVISION_POLY_TORSION_MAP.md`). Over `𝔽_p` itself the bridge is vacuous for
counting: the secp256k1 point group has prime order `n ≠ 3`, so `E[3](𝔽_p) = {O}` and
the four roots of `Ψ₃` simply do not lie on `𝔽_p`-rational points. The genuine content
lives over the closure, where `Ψ₃` has exactly `4` distinct roots
(`secp256k1_Ψ₃_roots_card_bar` / `secp256k1_Ψ₃_roots_nodup_bar` in
`DivisionPolynomialSeparable.lean`); each root `x₀` carries two points `(x₀, ±y₀)`
(distinct since `y₀ ≠ 0` there), so this bridge turns the root count `4` into the point
count `#E[3](𝔽̄_p) = 2·4 + 1 = 9 = 3²` — which
`Ecdlp.Torsion.nonempty_addEquiv_zmod_prod_of_card_eq_sq` (`TorsionStructure.lean`)
then upgrades to `E[3] ≅ ℤ/3 × ℤ/3`.

The proof body is the field-generic template proof (group-law case split on
`y = negY`, the slope identity `ℓ·2y = 3x²`, and the rational identity
`addX(P,P) − x = −(3x⁴+84x)/(4y²)`), with the three constant-nonzero facts
(`2, 7, 63 ≠ 0`) transported from `𝔽_p` along the injective base-change hom, and the
curve-equation / `negY` extraction recomputed through the mapped coefficients of
`secp256k1Bar = secp256k1.map (algebraMap 𝔽_p 𝔽̄_p)`. No `native_decide`, no new axioms;
the only `decide`s are the template's own `p ∤ 2, 7, 63` facts over `ℕ`.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- The base-change hom `𝔽_p →+* 𝔽̄_p` (same map as `secp256k1Bar` is built from). -/
private noncomputable abbrev φK :
    ZMod Secp256k1.p →+* AlgebraicClosure (ZMod Secp256k1.p) :=
  algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p))

/-- A nonzero constant of `𝔽_p` stays nonzero in `𝔽̄_p` (the base change is injective). -/
private theorem φK_ne_zero {c : ZMod Secp256k1.p} (hc : c ≠ 0) : φK c ≠ 0 := by
  intro h0
  exact hc (RingHom.injective φK (by rw [map_zero]; exact h0))

/-- **The closure 3-division polynomial in closed form: `Ψ₃ = 3X⁴ + 3·28·X`.**
The base change of `secp256k1_Ψ₃` (`DivisionPolynomial.lean`) along
`WeierstrassCurve.map_Ψ₃`; the coefficients are numerals, hence fixed by the map. -/
private theorem secp256k1Bar_Ψ₃ :
    secp256k1Bar.Ψ₃ = 3 * X ^ 4 + 3 * C 28 * X := by
  have h : (secp256k1.Ψ₃).map φK
      = 3 * X ^ 4 + 3 * C 28 * X := by
    rw [secp256k1_Ψ₃]
    simp only [Polynomial.map_add, Polynomial.map_mul, Polynomial.map_pow,
      Polynomial.map_ofNat, Polynomial.map_C, Polynomial.map_X, map_ofNat]
  simpa only [secp256k1Bar, WeierstrassCurve.map_Ψ₃] using h

/-- **The Weierstrass equation of `secp256k1Bar` is still `y² = x³ + 7`.** All the
`aᵢ` of the mapped curve are images of `0` (resp. `7`) under the base-change hom.
Kept as one lemma so any CI failure of the coefficient computation localizes here. -/
private theorem secp256k1Bar_equation_iff
    (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.Equation x y ↔ y ^ 2 = x ^ 3 + 7 := by
  rw [WeierstrassCurve.Affine.equation_iff]
  simp only [secp256k1Bar, WeierstrassCurve.map, secp256k1, map_zero, map_ofNat]
  constructor <;> intro he <;> linear_combination he

/-- Negation on `secp256k1Bar` is `y ↦ -y` (`a₁ = a₃ = 0` survive the base change). -/
private theorem secp256k1Bar_negY (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.negY x y = -y := by
  simp [WeierstrassCurve.Affine.negY, secp256k1Bar, WeierstrassCurve.map, secp256k1]

/-- **The bivariate 3-division polynomial `ψ 3` of `secp256k1Bar` evaluated at any point
`(x,y)` equals the concrete univariate `3x⁴ + 84x`.** (`ψ 3` is odd, hence univariate
in `x`.) Closure analogue of `secp256k1_psi3_evalEval`. -/
theorem secp256k1Bar_psi3_evalEval (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    (secp256k1Bar.ψ 3).evalEval x y = 3 * x ^ 4 + 84 * x := by
  rw [WeierstrassCurve.ψ_three, secp256k1Bar_Ψ₃, Polynomial.evalEval_C]
  simp only [Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_ofNat,
    Polynomial.eval_pow, Polynomial.eval_C, Polynomial.eval_X]
  ring

/-- **Point-level 3-torsion criterion over `𝔽̄_p`: `3 • P = 0 ⟺ ψ 3` vanishes at `P`.**
For a nonzero affine point `P = (x, y)` of `secp256k1Bar`, the group relation
`3 • P = 0` holds iff the 3-division polynomial vanishes at `P` (equivalently
`3x⁴ + 84x = 0`). This is where the `ψ₃ ↔ E[3]` bridge has its real content: over
`𝔽̄_p` the four roots of `Ψ₃` are realized by actual curve points, giving
`#E[3](𝔽̄_p) = 9` once paired with `±y`. -/
theorem secp256k1Bar_three_nsmul_eq_zero_iff
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) :
    (3 : ℕ) • (Point.some x y h) = 0 ↔ (secp256k1Bar.ψ 3).evalEval x y = 0 := by
  rw [secp256k1Bar_psi3_evalEval]
  have h2ne : (2 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
    have h2p : (2 : ZMod Secp256k1.p) ≠ 0 := by
      have : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
        rw [Ne, ZMod.natCast_eq_zero_iff]; decide
      simpa using this
    have hφ := φK_ne_zero h2p
    rwa [map_ofNat] at hφ
  have hp7 : (7 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
    have h7p : (7 : ZMod Secp256k1.p) ≠ 0 := by
      have : ((7 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
        rw [Ne, ZMod.natCast_eq_zero_iff]; decide
      simpa using this
    have hφ := φK_ne_zero h7p
    rwa [map_ofNat] at hφ
  have hp63 : (63 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
    have h63p : (63 : ZMod Secp256k1.p) ≠ 0 := by
      have : ((63 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
        rw [Ne, ZMod.natCast_eq_zero_iff]; decide
      simpa using this
    have hφ := φK_ne_zero h63p
    rwa [map_ofNat] at hφ
  have hcurve : y ^ 2 = x ^ 3 + 7 := (secp256k1Bar_equation_iff x y).mp h.1
  have hnegY : secp256k1Bar.toAffine.negY x y = -y := secp256k1Bar_negY x y
  have key : (3 : ℕ) • Point.some x y h
      = Point.some x y h + Point.some x y h + Point.some x y h := by
    rw [show (3 : ℕ) = 2 + 1 from rfl, add_nsmul, two_nsmul, one_nsmul]
  rw [key, add_eq_zero_iff_eq_neg]
  by_cases hy0 : y = secp256k1Bar.toAffine.negY x y
  · rw [Point.add_self_of_Y_eq hy0]
    refine iff_of_false ?_ ?_
    · rw [eq_comm, neg_eq_zero]; exact Point.some_ne_zero h
    · intro hpoly
      have hy00 : y = 0 := by
        have h2y0 : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * y = 0 := by
          rw [hnegY] at hy0; linear_combination hy0
        rcases mul_eq_zero.mp h2y0 with h2 | hy
        · exact absurd h2 h2ne
        · exact hy
      have hx3 : x ^ 3 = -7 := by
        have hc0 := hcurve; rw [hy00] at hc0; linear_combination -hc0
      have hxne : x ≠ 0 := by
        intro hx0; rw [hx0] at hx3; exact hp7 (by linear_combination hx3)
      have h63x : (63 : AlgebraicClosure (ZMod Secp256k1.p)) * x = 0 := by
        linear_combination hpoly - 3 * x * hx3
      rcases mul_eq_zero.mp h63x with h63 | hx0
      · exact hp63 h63
      · exact hxne hx0
  · have h2y : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * y ≠ 0 := by
      intro hc; exact hy0 (by rw [hnegY]; linear_combination hc)
    have hd : y - secp256k1Bar.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy0
    have h4 : (4 : AlgebraicClosure (ZMod Secp256k1.p)) * y ^ 2 ≠ 0 := by
      have hmm := mul_ne_zero h2y h2y
      intro hc; exact hmm (by linear_combination hc)
    rw [Point.add_of_Y_ne hy0, Point.neg_some, Point.some.injEq]
    set ℓ := secp256k1Bar.toAffine.slope x x y y with hℓ
    have hsl' : ℓ * (2 * y) = 3 * x ^ 2 := by
      rw [hℓ, WeierstrassCurve.Affine.slope_of_Y_ne rfl hy0,
        div_mul_eq_mul_div, div_eq_iff hd]
      simp only [secp256k1Bar, WeierstrassCurve.map, secp256k1, map_zero,
        WeierstrassCurve.Affine.negY]
      ring
    have hAid : secp256k1Bar.toAffine.addX x x ℓ - x
        = (-(3 * x ^ 4 + 84 * x)) / (4 * y ^ 2) := by
      rw [eq_div_iff h4]
      simp only [WeierstrassCurve.Affine.addX, secp256k1Bar, WeierstrassCurve.map,
        secp256k1, map_zero]
      linear_combination (2 * y * ℓ + 3 * x ^ 2) * hsl' - 12 * x * hcurve
    have hA : secp256k1Bar.toAffine.addX x x ℓ = x ↔ 3 * x ^ 4 + 84 * x = 0 := by
      constructor
      · intro hh
        have hz : secp256k1Bar.toAffine.addX x x ℓ - x = 0 := sub_eq_zero.mpr hh
        rw [hAid, div_eq_zero_iff] at hz
        rcases hz with h1 | h2
        · exact neg_eq_zero.mp h1
        · exact absurd h2 h4
      · intro hh
        have hz : secp256k1Bar.toAffine.addX x x ℓ - x = 0 := by
          rw [hAid]; simp only [hh, neg_zero, zero_div]
        exact sub_eq_zero.mp hz
    have hB : secp256k1Bar.toAffine.addX x x ℓ = x →
        secp256k1Bar.toAffine.addY x x y ℓ = secp256k1Bar.toAffine.negY x y := by
      intro hx
      simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
        WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1Bar,
        WeierstrassCurve.map, secp256k1, map_zero] at hx ⊢
      linear_combination (-ℓ) * hx
    constructor
    · rintro ⟨ha, _⟩; exact hA.mp ha
    · intro hpoly
      have ha := hA.mpr hpoly
      exact ⟨ha, hB ha⟩

/-- **Reconciliation with the root-count vocabulary of `DivisionPolynomialSeparable.lean`:**
`3 • P = 0` iff the `x`-coordinate of `P` is a root of the mapped univariate `Ψ₃`,
i.e. of `((secp256k1.Ψ₃).map φ) ∈ 𝔽̄_p[X]` — the polynomial whose roots were counted
(`4`, all distinct) by `secp256k1_Ψ₃_roots_card_bar`/`…_nodup_bar`. Together they say:
the 3-torsion `x`-locus of `secp256k1Bar` is exactly that 4-element root set. -/
theorem secp256k1Bar_three_torsion_iff_root
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) :
    (3 : ℕ) • Point.some x y h = 0 ↔ ((secp256k1.Ψ₃).map φK).eval x = 0 := by
  rw [secp256k1Bar_three_nsmul_eq_zero_iff, secp256k1Bar_psi3_evalEval]
  have h3 : (secp256k1.Ψ₃).map φK = 3 * X ^ 4 + 3 * C 28 * X := by
    have hb := secp256k1Bar_Ψ₃
    simpa only [secp256k1Bar, WeierstrassCurve.map_Ψ₃] using hb
  have hmap : ((secp256k1.Ψ₃).map φK).eval x = 3 * x ^ 4 + 84 * x := by
    rw [h3]
    simp only [Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_ofNat,
      Polynomial.eval_pow, Polynomial.eval_C, Polynomial.eval_X]
    ring
  rw [hmap]

end Ecdlp.Curve
