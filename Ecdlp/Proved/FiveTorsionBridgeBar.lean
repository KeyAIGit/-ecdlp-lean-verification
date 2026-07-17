import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial
import Ecdlp.Proved.CoprimePsi3Psi5
import Ecdlp.Proved.DivisionPolynomialEvalBridge
import Ecdlp.Proved.ThreeTorsionBridgeBar

/-!
# The 5-torsion bridge over the algebraic closure `𝔽̄_p`

The point-level `n = 5` division-polynomial ↔ torsion bridge for `secp256k1Bar`, the
base change of secp256k1 to `K := AlgebraicClosure (ZMod Secp256k1.p)`: for a nonzero
affine point `P = (x, y)` of the closure curve, `5 • P = 0 ⟺ ψ₅(P) = 0 ⟺
5x¹² + 2660x⁹ − 11760x⁶ − 548800x³ − 614656 = 0`. That per-point equivalence is exactly
the headline theorem `secp256k1Bar_five_nsmul_eq_zero_iff`, and is all this file proves.

This is the port of `Ecdlp/Proved/FiveTorsionBridge.lean` from `𝔽_p` to `𝔽̄_p`, exactly
as `ThreeTorsionBridgeBar.lean` ported `ThreeTorsionBridge.lean`. Over `𝔽_p` itself the
bridge is vacuous for counting: the secp256k1 point group has prime order `n ≠ 5`, so
`E[5](𝔽_p) = {O}` and the twelve roots of `preΨ₅` do not lie on `𝔽_p`-rational points;
the genuine counting content lives over the closure.

*Motivation / downstream (not proved in this file).* Combining this per-point bridge with
the closure root-count — `preΨ₅` has exactly `12` distinct roots
(`secp256k1_preΨ₅_roots_card_bar` / `secp256k1_preΨ₅_roots_nodup_bar` in
`DivisionPolynomialSeparable.lean`) — and the `±y`-pairing (each nonzero root `x₀`
carrying two points `(x₀, ±y₀)`) is what would turn the root count `12` into a point count
`#E[5](𝔽̄_p) = 2·12 + 1 = 25 = 5²` (node N11 at `n = 5` of
`notes/DIVISION_POLY_TORSION_MAP.md`). That assembly — including surjectivity onto the
root set and the `y₀ ≠ 0` input — is done in `FiveTorsionStructure.lean`, not here.

The route mirrors the odd-`n` pattern of the `𝔽_p` template:
`5 • P = 0 ⟺ 2 • P = -(3 • P) ⟺ x(2P) = x(3P) ⟺ ψ₅(P) = 0`. Stage 1
(`secp256k1Bar_psi5_evalEval`) reduces the bivariate `ψ 5` on the curve to the concrete
degree-12 univariate; the heart is `five_core_bar`, the template's field-generic
`linear_combination` certificate ported token-identically (re-verified by sympy in
transcription, re-checked by the Lean kernel). The 3-torsion branch of the case split
routes through the already-ported closure bridge `secp256k1Bar_three_nsmul_eq_zero_iff`
(`ThreeTorsionBridgeBar.lean`); the 2-torsion criterion `2 • P = 0 ⟺ y = 0` is
re-proved over the closure inline (port of `TwoTorsionPoint.lean`).

The constant-nonzero facts (`2, 3, 64, 1750329, 614656, 49787136 ≠ 0` in `𝔽̄_p`) are
the template's own `p ∤ c` facts over `ℕ` (`decide`, as in the `𝔽_p` file), transported
along the injective base-change hom `φ : 𝔽_p →+* 𝔽̄_p`; concrete polynomial evaluations
over the closure (`Ψ₃`, `preΨ₄`, `preΨ₅`) are derived via the `map` route with
`Polynomial.map_ofNat` / `Polynomial.eval_ofNat` (the `E[3]` lesson). No
`native_decide`, no new axioms.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

open scoped Classical

/-- The base-change hom `𝔽_p →+* 𝔽̄_p` (same map as `secp256k1Bar` is built from). -/
private noncomputable abbrev φK :
    ZMod Secp256k1.p →+* AlgebraicClosure (ZMod Secp256k1.p) :=
  algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p))

/-- A nonzero constant of `𝔽_p` stays nonzero in `𝔽̄_p` (the base change is injective). -/
private theorem φK_ne_zero {c : ZMod Secp256k1.p} (hc : c ≠ 0) : φK c ≠ 0 := by
  intro h0
  exact hc (RingHom.injective φK (by rw [map_zero]; exact h0))

/-- A natural constant not divisible by `p` is nonzero in `𝔽̄_p`: nonzero in `𝔽_p` by
`ZMod.natCast_eq_zero_iff` and the template's `decide`-checked `p ∤ c`, transported
along the injective base change (the `φK`-injectivity pattern; the `decide`s stay
over `ℕ`/`𝔽_p`, nothing is re-decided over `𝔽̄_p`). -/
private theorem const_ne_bar (n : ℕ) (hn : ¬ Secp256k1.p ∣ n) :
    (n : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
  have hp : ((n : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]; exact hn
  have hφ := φK_ne_zero hp
  rwa [map_natCast] at hφ

/-- The curve equation of `secp256k1Bar` at a nonsingular point: `y² = x³ + 7`. The
`aᵢ` of the mapped curve are images of `0` (resp. `7`) under the base-change hom. -/
private theorem secp256k1Bar_curve_of_nonsingular
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) : y ^ 2 = x ^ 3 + 7 := by
  have he : secp256k1Bar.toAffine.Equation x y := h.1
  rw [WeierstrassCurve.Affine.equation_iff] at he
  simp only [secp256k1Bar, WeierstrassCurve.map, WeierstrassCurve.map_a₁,
    WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄,
    WeierstrassCurve.map_a₆, secp256k1, map_zero, map_ofNat] at he
  linear_combination he

/-- Negation on `secp256k1Bar` is `y ↦ -y` (`a₁ = a₃ = 0` survive the base change). -/
private theorem secp256k1Bar_negY (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.negY x y = -y := by
  simp [WeierstrassCurve.Affine.negY, secp256k1Bar, WeierstrassCurve.map, secp256k1]

/-- Concrete evaluation of the univariate `preΨ₄` for `secp256k1Bar`:
`preΨ₄(x) = 2x⁶ + 280x³ − 784` — the base change of the compiled closed form
`secp256k1_preΨ₄`, mapped and evaluated coefficientwise. -/
theorem secp256k1Bar_preΨ₄_eval (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.preΨ₄.eval x = 2 * x ^ 6 + 280 * x ^ 3 - 784 := by
  have hmap : secp256k1Bar.preΨ₄ = (secp256k1.preΨ₄).map φK := by
    simp only [secp256k1Bar, WeierstrassCurve.map_preΨ₄]
  rw [hmap, secp256k1_preΨ₄]
  simp only [Polynomial.map_add, Polynomial.map_sub, Polynomial.map_mul,
    Polynomial.map_pow, Polynomial.map_ofNat, Polynomial.map_X, eval_add, eval_sub,
    eval_mul, eval_pow, eval_X, Polynomial.eval_ofNat]

/-- Concrete evaluation of the univariate `Ψ₃` for `secp256k1Bar`: `3x⁴ + 84x`
(base change of the compiled closed form `secp256k1_Ψ₃`). -/
private theorem secp256k1Bar_Ψ₃_eval (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.Ψ₃.eval x = 3 * x ^ 4 + 84 * x := by
  have hmap : secp256k1Bar.Ψ₃ = (secp256k1.Ψ₃).map φK := by
    simp only [secp256k1Bar, WeierstrassCurve.map_Ψ₃]
  rw [hmap, secp256k1_Ψ₃]
  simp only [Polynomial.map_add, Polynomial.map_mul, Polynomial.map_pow,
    Polynomial.map_ofNat, Polynomial.map_C, Polynomial.map_X, map_ofNat, eval_add,
    eval_mul, eval_pow, eval_C, eval_X, Polynomial.eval_ofNat]
  ring

/-- The bivariate 2-division polynomial `ψ₂` evaluated at `(x,y)` on `secp256k1Bar`
is `2y` (the mapped `a₁ = a₃ = 0` kill the linear terms). -/
theorem secp256k1Bar_psi2_evalEval (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.ψ₂.evalEval x y = 2 * y := by
  rw [WeierstrassCurve.ψ₂, evalEval_polynomialY]
  simp [secp256k1Bar, WeierstrassCurve.map, secp256k1]

/-- **Stage-1: `ψ 5` at a point `(x,y)` of `secp256k1Bar` reduces to the concrete
degree-12 univariate polynomial** `5x¹² + 2660x⁹ − 11760x⁶ − 548800x³ − 614656`.
Closure analogue of `secp256k1_psi5_evalEval`, same `linear_combination` certificate. -/
theorem secp256k1Bar_psi5_evalEval (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (hcurve : y ^ 2 = x ^ 3 + 7) :
    (secp256k1Bar.ψ 5).evalEval x y
      = 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656 := by
  have h5 := secp256k1Bar.ψ_odd 2
  rw [show (2 * 2 + 1 : ℤ) = 5 by ring, show (2 + 2 : ℤ) = 4 by ring,
      show (2 - 1 : ℤ) = 1 by ring, show (2 + 1 : ℤ) = 3 by ring,
      secp256k1Bar.ψ_four, secp256k1Bar.ψ_two, secp256k1Bar.ψ_one,
      secp256k1Bar.ψ_three] at h5
  rw [h5]
  simp only [evalEval_sub, evalEval_mul, evalEval_pow, evalEval_C, evalEval_one]
  rw [secp256k1Bar_psi2_evalEval, secp256k1Bar_preΨ₄_eval, secp256k1Bar_Ψ₃_eval]
  linear_combination (16 * (2 * x ^ 6 + 280 * x ^ 3 - 784) * (y ^ 2 + x ^ 3 + 7)) * hcurve

/-- **Core algebraic identity for the 5-torsion bridge over the closure.** With `ℓ₂` the
tangent slope at `P` (so `2yℓ₂ = 3x²`) and `ℓ₃` the secant slope between `2P` and `P`,
the `x`-coordinate of `3P` equals that of `2P` iff `ψ₅(x) = 0`. Pure field algebra —
the `𝔽_p` template's `five_core`, ported token-identically to `𝔽̄_p`; machine-certified
by the same `linear_combination` of the curve equation and the slope relation. -/
theorem five_core_bar (x y ℓ₂ ℓ₃ : AlgebraicClosure (ZMod Secp256k1.p))
    (h64 : (64 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0)
    (hcurve : y ^ 2 = x ^ 3 + 7)
    (hy : y ≠ 0)
    (hℓ2 : 2 * y * ℓ₂ = 3 * x ^ 2)
    (hd : ℓ₂ ^ 2 - 3 * x ≠ 0)
    (hℓ3 : (ℓ₂ ^ 2 - 3 * x) * ℓ₃ = -(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y) :
    ℓ₃ ^ 2 - (ℓ₂ ^ 2 - 2 * x) - x = ℓ₂ ^ 2 - 2 * x
      ↔ 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656 = 0 := by
  have hd2 : (ℓ₂ ^ 2 - 3 * x) ^ 2 ≠ 0 := pow_ne_zero 2 hd
  have h64y6 : (64 : AlgebraicClosure (ZMod Secp256k1.p)) * y ^ 6 ≠ 0 :=
    mul_ne_zero h64 (pow_ne_zero 6 hy)
  have hmaster : ((-(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y) ^ 2
        - (2 * (ℓ₂ ^ 2 - 2 * x) + x) * (ℓ₂ ^ 2 - 3 * x) ^ 2) * (64 * y ^ 6)
      = -(5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656) := by
    linear_combination
      (-32 * ℓ₂ ^ 5 * y ^ 5 - 48 * ℓ₂ ^ 4 * x ^ 2 * y ^ 4 - 72 * ℓ₂ ^ 3 * x ^ 4 * y ^ 3
        + 288 * ℓ₂ ^ 3 * x * y ^ 5 - 108 * ℓ₂ ^ 2 * x ^ 6 * y ^ 2 + 432 * ℓ₂ ^ 2 * x ^ 3 * y ^ 4
        + 128 * ℓ₂ ^ 2 * y ^ 6 - 162 * ℓ₂ * x ^ 8 * y + 648 * ℓ₂ * x ^ 5 * y ^ 3
        - 672 * ℓ₂ * x ^ 2 * y ^ 5 - 243 * x ^ 10 + 972 * x ^ 7 * y ^ 2 - 1008 * x ^ 4 * y ^ 4
        - 384 * x * y ^ 6) * hℓ2
      + (724 * x ^ 9 - 2192 * x ^ 6 * y ^ 2 - 7728 * x ^ 6 + 832 * x ^ 3 * y ^ 4
        + 7616 * x ^ 3 * y ^ 2 + 65856 * x ^ 3 + 256 * y ^ 6 + 1792 * y ^ 4 + 12544 * y ^ 2
        + 87808) * hcurve
  have hBF : (ℓ₃ ^ 2 - (2 * (ℓ₂ ^ 2 - 2 * x) + x)) * (ℓ₂ ^ 2 - 3 * x) ^ 2
      = (-(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y) ^ 2
        - (2 * (ℓ₂ ^ 2 - 2 * x) + x) * (ℓ₂ ^ 2 - 3 * x) ^ 2 := by
    linear_combination
      ((ℓ₂ ^ 2 - 3 * x) * ℓ₃ + (-(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y)) * hℓ3
  set F := (-(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y) ^ 2
      - (2 * (ℓ₂ ^ 2 - 2 * x) + x) * (ℓ₂ ^ 2 - 3 * x) ^ 2 with hFdef
  rw [show (ℓ₃ ^ 2 - (ℓ₂ ^ 2 - 2 * x) - x = ℓ₂ ^ 2 - 2 * x)
        ↔ (ℓ₃ ^ 2 - (2 * (ℓ₂ ^ 2 - 2 * x) + x) = 0)
      from by constructor <;> intro h <;> linear_combination h]
  constructor
  · intro hB
    have hFz : F = 0 := by rw [← hBF, hB, zero_mul]
    have := hmaster
    rw [hFz, zero_mul] at this
    linear_combination this
  · intro hp
    have hFz : F = 0 := by
      have := hmaster
      rw [hp, neg_zero] at this
      exact (mul_eq_zero.mp this).resolve_right h64y6
    have hBz : (ℓ₃ ^ 2 - (2 * (ℓ₂ ^ 2 - 2 * x) + x)) * (ℓ₂ ^ 2 - 3 * x) ^ 2 = 0 := by
      rw [hBF, hFz]
    exact (mul_eq_zero.mp hBz).resolve_right hd2

/-- **Point-level 2-torsion criterion over `𝔽̄_p`: `2 • P = 0 ⟺ y = 0`.** Port of
`secp256k1_two_nsmul_eq_zero_iff` (`TwoTorsionPoint.lean`) to the closure curve; needed
by the 3-torsion branch of the 5-torsion case split below. -/
theorem secp256k1Bar_two_nsmul_eq_zero_iff
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) :
    (2 : ℕ) • (Point.some x y h) = 0 ↔ y = 0 := by
  have h2ne : (2 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
    have := const_ne_bar 2 (by decide); exact_mod_cast this
  have hnegY : secp256k1Bar.toAffine.negY x y = -y := secp256k1Bar_negY x y
  rw [two_nsmul, add_eq_zero_iff_eq_neg, Point.neg_some, Point.some.injEq, hnegY]
  constructor
  · rintro ⟨-, hy⟩
    have h2y : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * y = 0 := by
      linear_combination hy
    rcases mul_eq_zero.mp h2y with h2 | hy0
    · exact absurd h2 h2ne
    · exact hy0
  · intro hy
    subst hy
    exact ⟨rfl, by ring⟩

/-- **Point-level 5-torsion criterion over `𝔽̄_p`: `5 • P = 0 ⟺ ψ 5` vanishes at `P`.**
For a nonzero affine point `P = (x, y)` of `secp256k1Bar`, the group relation
`5 • P = 0` holds iff the 5-division polynomial vanishes at `P` (equivalently
`5x¹² + 2660x⁹ − 11760x⁶ − 548800x³ − 614656 = 0`). This per-point equivalence is the
full content of the theorem. (Downstream, not proved here: that the twelve roots of
`preΨ₅` are each realized by an actual curve point and that, paired with `±y`, this yields
`#E[5](𝔽̄_p) = 25`.) -/
theorem secp256k1Bar_five_nsmul_eq_zero_iff
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) :
    (5 : ℕ) • (Point.some x y h) = 0 ↔ (secp256k1Bar.ψ 5).evalEval x y = 0 := by
  have h2 : (2 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
    have := const_ne_bar 2 (by decide); exact_mod_cast this
  have h3ne : (3 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
    have := const_ne_bar 3 (by decide); exact_mod_cast this
  have h64 : (64 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
    have := const_ne_bar 64 (by decide); exact_mod_cast this
  have hcurve : y ^ 2 = x ^ 3 + 7 := secp256k1Bar_curve_of_nonsingular x y h
  have hnegY : secp256k1Bar.toAffine.negY x y = -y := secp256k1Bar_negY x y
  rw [secp256k1Bar_psi5_evalEval x y hcurve]
  by_cases hy0 : y = secp256k1Bar.toAffine.negY x y
  · -- 2-torsion branch: y = 0
    have hy00 : y = 0 := by
      rw [hnegY] at hy0
      have h2y : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * y = 0 := by
        linear_combination hy0
      rcases mul_eq_zero.mp h2y with hc | hc
      · exact absurd hc h2
      · exact hc
    have h2P : (2 : ℕ) • (Point.some x y h) = 0 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_eq hy0
    have h5P : (5 : ℕ) • (Point.some x y h) = Point.some x y h := by
      rw [show (5 : ℕ) = 1 + 2 + 2 from rfl, add_nsmul, add_nsmul, one_nsmul, h2P,
        add_zero, add_zero]
    refine iff_of_false ?_ ?_
    · rw [h5P]; exact Point.some_ne_zero h
    · have hx3 : x ^ 3 = -7 := by rw [hy00] at hcurve; linear_combination -hcurve
      have hval : 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656
          = 1750329 := by
        linear_combination (5 * x ^ 9 + 2625 * x ^ 6 - 30135 * x ^ 3 - 337855) * hx3
      rw [hval]
      have := const_ne_bar 1750329 (by decide); exact_mod_cast this
  · -- y ≠ negY, so y ≠ 0
    have hy : y ≠ 0 := by
      intro h0; exact hy0 (by rw [hnegY, h0]; ring)
    by_cases h3 : (3 : ℕ) • (Point.some x y h) = 0
    · -- 3-torsion branch, via the ported closure 3-torsion bridge
      have h34 : 3 * x ^ 4 + 84 * x = 0 := by
        have := (secp256k1Bar_three_nsmul_eq_zero_iff x y h).mp h3
        rwa [secp256k1Bar_psi3_evalEval] at this
      have h5P2 : (5 : ℕ) • (Point.some x y h) = (2 : ℕ) • (Point.some x y h) := by
        rw [show (5 : ℕ) = 2 + 3 from rfl, add_nsmul, h3, add_zero]
      have h2ne : (2 : ℕ) • (Point.some x y h) ≠ 0 :=
        fun hc => hy ((secp256k1Bar_two_nsmul_eq_zero_iff x y h).mp hc)
      refine iff_of_false ?_ ?_
      · rw [h5P2]; exact h2ne
      · intro hc
        have hfac : 3 * x * (x ^ 3 + 28) = 0 := by linear_combination h34
        rcases mul_eq_zero.mp hfac with h3x | hx328
        · rcases mul_eq_zero.mp h3x with hc3 | hx0
          · exact h3ne hc3
          · have hpv : 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656
                = -614656 := by rw [hx0]; ring
            rw [hpv] at hc
            exact (const_ne_bar 614656 (by decide)) (by exact_mod_cast (by linear_combination -hc :
              (614656 : AlgebraicClosure (ZMod Secp256k1.p)) = 0))
        · have hx3 : x ^ 3 = -28 := by linear_combination hx328
          have hpv : 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656
              = -49787136 := by
            linear_combination (5 * x ^ 9 + 2520 * x ^ 6 - 82320 * x ^ 3 + 1756160) * hx3
          rw [hpv] at hc
          exact (const_ne_bar 49787136 (by decide)) (by exact_mod_cast (by linear_combination -hc :
            (49787136 : AlgebraicClosure (ZMod Secp256k1.p)) = 0))
    · -- main branch: y ≠ 0 and 3P ≠ 0
      have hYd : y - secp256k1Bar.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy0
      have hΨ3ne : 3 * x ^ 4 + 84 * x ≠ 0 := fun hc =>
        h3 ((secp256k1Bar_three_nsmul_eq_zero_iff x y h).mpr
          (by rw [secp256k1Bar_psi3_evalEval]; exact hc))
      set s2 := secp256k1Bar.toAffine.slope x x y y with hs2def
      set X2 := secp256k1Bar.toAffine.addX x x s2 with hX2def
      set Y2 := secp256k1Bar.toAffine.addY x x y s2 with hY2def
      have hsl2 : s2 * (2 * y) = 3 * x ^ 2 := by
        rw [hs2def, slope_of_Y_ne rfl hy0, div_mul_eq_mul_div, div_eq_iff hYd]
        simp only [secp256k1Bar, WeierstrassCurve.map, WeierstrassCurve.map_a₁,
          WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄,
          WeierstrassCurve.map_a₆, secp256k1, map_zero, WeierstrassCurve.Affine.negY]
        ring
      have hId : (s2 ^ 2 - 3 * x) * (4 * y ^ 2) = -(3 * x ^ 4 + 84 * x) := by
        linear_combination (2 * s2 * y + 3 * x ^ 2) * hsl2 + (-12 * x) * hcurve
      have hd : s2 ^ 2 - 3 * x ≠ 0 := by
        intro hc
        apply hΨ3ne
        have := hId
        rw [hc, zero_mul] at this
        linear_combination this
      have hx2val : X2 = s2 ^ 2 - 2 * x := by
        rw [hX2def]
        simp only [WeierstrassCurve.Affine.addX, secp256k1Bar, WeierstrassCurve.map,
          WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃,
          WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆, secp256k1, map_zero]
        ring
      have hx2x : X2 - x = s2 ^ 2 - 3 * x := by rw [hx2val]; ring
      have hx2ne : X2 ≠ x := by rw [← sub_ne_zero, hx2x]; exact hd
      have hy2val : Y2 = -(s2 * (s2 ^ 2 - 3 * x) + y) := by
        rw [hY2def]
        simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
          WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1Bar,
          WeierstrassCurve.map, WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂,
          WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆,
          secp256k1, map_zero]
        ring
      have hns2 : secp256k1Bar.toAffine.Nonsingular X2 Y2 :=
        nonsingular_add h h (fun hxy => hy0 hxy.2)
      have hP2 : (2 : ℕ) • (Point.some x y h) = Point.some X2 Y2 hns2 := by
        rw [two_nsmul]; exact Point.add_self_of_Y_ne hy0
      set s3 := secp256k1Bar.toAffine.slope X2 x Y2 y with hs3def
      set X3 := secp256k1Bar.toAffine.addX X2 x s3 with hX3def
      set Y3 := secp256k1Bar.toAffine.addY X2 x Y2 s3 with hY3def
      have hx3val : X3 = s3 ^ 2 - (s2 ^ 2 - 2 * x) - x := by
        rw [hX3def]
        simp only [WeierstrassCurve.Affine.addX, secp256k1Bar, WeierstrassCurve.map,
          WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃,
          WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆, secp256k1, map_zero]
        rw [hx2val]; ring
      have hns3 : secp256k1Bar.toAffine.Nonsingular X3 Y3 :=
        nonsingular_add hns2 h (fun hxy => hx2ne hxy.1)
      have hP3 : (3 : ℕ) • (Point.some x y h) = Point.some X3 Y3 hns3 := by
        rw [show (3 : ℕ) = 2 + 1 from rfl, add_nsmul, one_nsmul, hP2]
        exact Point.add_some (fun hxy => hx2ne hxy.1)
      have hsl3s : s3 * (X2 - x) = Y2 - y := by
        rw [hs3def, slope_of_X_ne hx2ne]
        exact div_mul_cancel₀ _ (sub_ne_zero.mpr hx2ne)
      have hℓ3 : (s2 ^ 2 - 3 * x) * s3 = -(s2 * (s2 ^ 2 - 3 * x) + y) - y := by
        have hstep := hsl3s
        rw [hy2val, hx2x] at hstep
        linear_combination hstep
      have hxiff : X2 = X3 ↔ 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3
          - 614656 = 0 := by
        rw [hx3val, hx2val, eq_comm]
        exact five_core_bar x y s2 s3 h64 hcurve hy (by linear_combination hsl2) hd hℓ3
      have hyimp : X2 = X3 → Y2 = secp256k1Bar.toAffine.negY X3 Y3 := by
        intro hx
        rcases Y_eq_of_X_eq hns2.1 hns3.1 hx with hyy | hyn
        · exfalso
          have e23 : (2 : ℕ) • (Point.some x y h) = (3 : ℕ) • (Point.some x y h) := by
            rw [hP2, hP3, Point.some.injEq]; exact ⟨hx, hyy⟩
          rw [show (3 : ℕ) = 2 + 1 from rfl, add_nsmul, one_nsmul] at e23
          have hP0 : (0 : secp256k1Bar.toAffine.Point) = Point.some x y h :=
            add_left_cancel (show (2 : ℕ) • (Point.some x y h) + 0
              = (2 : ℕ) • (Point.some x y h) + Point.some x y h by rw [add_zero]; exact e23)
          exact Point.some_ne_zero h hP0.symm
        · exact hyn
      rw [show (5 : ℕ) = 2 + 3 from rfl, add_nsmul, hP2, hP3, add_eq_zero_iff_eq_neg,
        Point.neg_some, Point.some.injEq]
      constructor
      · rintro ⟨hx, _⟩; exact hxiff.mp hx
      · intro hp
        exact ⟨hxiff.mpr hp, hyimp (hxiff.mpr hp)⟩

/-- **Reconciliation with the root-count vocabulary of `DivisionPolynomialSeparable.lean`:**
`5 • P = 0` iff the `x`-coordinate of `P` is a root of the mapped univariate `preΨ₅`,
i.e. of `((secp256k1.preΨ' 5).map φ) ∈ 𝔽̄_p[X]` — the polynomial whose roots were counted
(`12`, all distinct) by `secp256k1_preΨ₅_roots_card_bar`/`…_nodup_bar`. This equates the
`x`-coordinate of any 5-torsion point with a root of that polynomial. (Downstream, not
proved here: the reverse identification — that the 5-torsion `x`-locus is *exactly* that
12-element root set — additionally needs surjectivity, i.e. that every root is realized by
a nonsingular curve point.) -/
theorem secp256k1Bar_five_torsion_iff_root
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) :
    (5 : ℕ) • Point.some x y h = 0 ↔ ((secp256k1.preΨ' 5).map φK).eval x = 0 := by
  have hcurve : y ^ 2 = x ^ 3 + 7 := secp256k1Bar_curve_of_nonsingular x y h
  rw [secp256k1Bar_five_nsmul_eq_zero_iff, secp256k1Bar_psi5_evalEval x y hcurve]
  have h5m : (secp256k1.preΨ' 5).map φK
      = 5 * X ^ 12 + 2660 * X ^ 9 - 11760 * X ^ 6 - 548800 * X ^ 3 - 614656 := by
    rw [secp256k1_preΨ₅]
    simp only [Polynomial.map_add, Polynomial.map_sub, Polynomial.map_mul,
      Polynomial.map_pow, Polynomial.map_ofNat, Polynomial.map_X]
  have hmap : ((secp256k1.preΨ' 5).map φK).eval x
      = 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656 := by
    rw [h5m]
    simp only [eval_add, eval_sub, eval_mul, eval_pow, eval_X, Polynomial.eval_ofNat]
  rw [hmap]

end Ecdlp.Curve
