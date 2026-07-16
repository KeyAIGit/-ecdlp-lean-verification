import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialEvalBridge
import Ecdlp.Proved.CoprimePsi3Psi7
import Ecdlp.Proved.ThreeTorsionBridgeBar
import Ecdlp.Proved.FiveTorsionBridgeBar

/-!
# The 7-torsion bridge over the algebraic closure `𝔽̄_p`

The point-level `n = 7` division-polynomial ↔ torsion bridge for `secp256k1Bar`, the base
change of secp256k1 to `K := AlgebraicClosure (ZMod Secp256k1.p)`: for a nonzero affine
point `P = (x, y)` of the closure curve, `7 • P = 0 ⟺ ψ₇(P) = 0 ⟺` the concrete degree-24
univariate `7x²⁴ + 27608x²¹ − ⋯ + 377801998336` vanishes at `x`.

This is the port of `Ecdlp/Proved/SevenTorsionBridge.lean` from `𝔽_p` to `𝔽̄_p` — the `n = 7`
analogue of `ThreeTorsionBridgeBar.lean`, and the missing link for the count
`#E[7](𝔽̄_p) = 49` (node N11 at `n = 7` over the closure): the mapped `preΨ' 7` has exactly
`24` distinct roots in `𝔽̄_p` (`secp256k1_preΨ₇_roots_card_bar` / `…_nodup_bar`,
`DivisionPolynomialSeparable.lean`), each root carries two points `(x₀, ±y₀)`, so this
bridge turns the root count `24` into the point count `2·24 + 1 = 49 = 7²`
(`SevenTorsionStructure.lean`).

The route is the field-generic template of the `𝔽_p` proof:
`7 • P = 0 ⟺ 3 • P = -(4 • P) ⟺ x(3P) = x(4P) ⟺ ψ₇(x) = 0`, with the sympy-designed
`linear_combination` master certificate ported token-identically (its coefficients are
integer numerals, valid over any commutative ring), the mapped-coefficient `simp` sets of
`ThreeTorsionBridgeBar.lean` for the group-law extraction, and the constant-nonzero facts
(`2, 3, 3063651608241, 377801998336, 2478758911082496 ≠ 0`) transported from `𝔽_p` along
the injective base-change hom. Stage 1 consumes the closure five-bridge evaluation lemmas
`secp256k1Bar_psi5_evalEval` / `secp256k1Bar_psi2_evalEval` / `secp256k1Bar_preΨ₄_eval`
(`FiveTorsionBridgeBar.lean`), exactly as the `𝔽_p` seven-bridge consumes the `𝔽_p`
five-bridge. No `native_decide`, no new axioms; the only `decide`s are `p ∤ n` facts over
`ℕ`, token-identical to the `𝔽_p` file's.
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

/-! ## Constant-nonzero facts, transported from `𝔽_p`

Each is the `𝔽_p` `decide` fact `p ∤ n` pushed through the injective base change, the
`ThreeTorsionBridgeBar` idiom verbatim. -/

private theorem bar_two_ne_zero : (2 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
  have hp : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  have hφ := φK_ne_zero hp
  rwa [map_ofNat] at hφ

private theorem bar_three_ne_zero : (3 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
  have hp : (3 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((3 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  have hφ := φK_ne_zero hp
  rwa [map_ofNat] at hφ

/-- `ψ₇` at the `y = 0` locus: the value `3063651608241 = 3¹²·7⁸` is a unit of `𝔽̄_p`. -/
private theorem bar_c3063651608241_ne_zero :
    (3063651608241 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
  have hp : (3063651608241 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((3063651608241 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  have hφ := φK_ne_zero hp
  rwa [map_ofNat] at hφ

/-- `ψ₇(0) = 377801998336 = 2¹⁶·7⁸` is a unit of `𝔽̄_p`. -/
private theorem bar_c377801998336_ne_zero :
    (377801998336 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
  have hp : (377801998336 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((377801998336 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  have hφ := φK_ne_zero hp
  rwa [map_ofNat] at hφ

/-- `ψ₇` at the `x³ = −28` locus: `2478758911082496 = 2¹⁶·3⁸·7⁸` is a unit of `𝔽̄_p`. -/
private theorem bar_c2478758911082496_ne_zero :
    (2478758911082496 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
  have hp : (2478758911082496 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((2478758911082496 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  have hφ := φK_ne_zero hp
  rwa [map_ofNat] at hφ

/-! ## Mapped-coefficient extraction for `secp256k1Bar`

Fresh private copies of the (private) `ThreeTorsionBridgeBar` / `ThreeTorsionStructure`
lemmas; any CI failure of the mapped-coefficient computation localizes here. -/

/-- The closure `Ψ₃` in closed form: `Ψ₃ = 3X⁴ + 3·28·X` (coefficients are numerals,
hence fixed by the base change). -/
private theorem bar_Ψ₃_closed :
    secp256k1Bar.Ψ₃ = 3 * X ^ 4 + 3 * C 28 * X := by
  have h : (secp256k1.Ψ₃).map φK
      = 3 * X ^ 4 + 3 * C 28 * X := by
    rw [secp256k1_Ψ₃]
    simp only [Polynomial.map_add, Polynomial.map_mul, Polynomial.map_pow,
      Polynomial.map_ofNat, Polynomial.map_C, Polynomial.map_X, map_ofNat]
  simpa only [secp256k1Bar, WeierstrassCurve.map_Ψ₃] using h

/-- The closure `Ψ₃` evaluates to `3x⁴ + 84x` — the `𝔽̄_p` analogue of `secp256k1_Ψ₃_eval`. -/
private theorem bar_Ψ₃_eval (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.Ψ₃.eval x = 3 * x ^ 4 + 84 * x := by
  rw [bar_Ψ₃_closed]
  simp only [eval_add, eval_mul, eval_pow, eval_X, eval_C, eval_ofNat]
  ring

/-- The curve equation of `secp256k1Bar` at a nonsingular point: `y² = x³ + 7`. -/
private theorem bar_curve_of_nonsingular
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) : y ^ 2 = x ^ 3 + 7 := by
  have he : secp256k1Bar.toAffine.Equation x y := h.1
  rw [WeierstrassCurve.Affine.equation_iff] at he
  simp only [secp256k1Bar, WeierstrassCurve.map, WeierstrassCurve.map_a₁,
    WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄,
    WeierstrassCurve.map_a₆, secp256k1, map_zero, map_ofNat] at he
  linear_combination he

/-- Negation on `secp256k1Bar` is `y ↦ -y` (`a₁ = a₃ = 0` survive the base change). -/
private theorem bar_negY (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.negY x y = -y := by
  simp [WeierstrassCurve.Affine.negY, secp256k1Bar, WeierstrassCurve.map,
    WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃,
    WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆, secp256k1]

/-- **Stage-1: `ψ 7` at `(x,y)` on `secp256k1Bar` reduces to a concrete degree-24
univariate.** Port of `secp256k1_psi7_evalEval`, consuming the closure five-bridge
evaluation lemmas (`FiveTorsionBridgeBar.lean`) exactly as the `𝔽_p` original consumes
the `𝔽_p` five-bridge. -/
theorem secp256k1Bar_psi7_evalEval (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (hcurve : y ^ 2 = x ^ 3 + 7) :
    (secp256k1Bar.ψ 7).evalEval x y = (7*x^24 + 27608*x^21 - 2101904*x^18 - 284585728*x^15 - 2228742656*x^12 - 26142548992*x^9 - 330576748544*x^6 - 661153497088*x^3 + 377801998336) := by
  have h7 := secp256k1Bar.ψ_odd 3
  rw [show (2 * 3 + 1 : ℤ) = 7 by ring, show (3 + 2 : ℤ) = 5 by ring,
      show (3 - 1 : ℤ) = 2 by ring, show (3 + 1 : ℤ) = 4 by ring,
      secp256k1Bar.ψ_four, secp256k1Bar.ψ_two, secp256k1Bar.ψ_three] at h7
  rw [h7]
  simp only [evalEval_sub, evalEval_mul, evalEval_pow, evalEval_C]
  rw [secp256k1Bar_psi5_evalEval x y hcurve, secp256k1Bar_psi2_evalEval,
    secp256k1Bar_preΨ₄_eval, bar_Ψ₃_eval]
  linear_combination (-16 * (2 * x ^ 6 + 280 * x ^ 3 - 784) ^ 3 * (y ^ 2 + x ^ 3 + 7)) * hcurve

/-- **Master identity over `𝔽̄_p`.** With `ℓ₂` the tangent slope at `P` and `ℓ₃` the secant
slope for `2P + P`, the bracket `G` (numerator of `x(4P) − x(3P)` up to the `ℓ₄`-secant)
reduces, after clearing `(ℓ₂²−3x)⁶·(2y)¹²`, to `−4(x³+7)·ψ₇(x)`. Token-identical port of
`seven_master` (`SevenTorsionBridge.lean`): the certificate's coefficients are integer
numerals, so the sympy-designed `linear_combination` is valid verbatim over `𝔽̄_p`. -/
private theorem seven_master_bar (x y ℓ₂ ℓ₃ : AlgebraicClosure (ZMod Secp256k1.p))
    (hcurve : y ^ 2 = x ^ 3 + 7)
    (hℓ2 : 2 * y * ℓ₂ = 3 * x ^ 2)
    (hℓ3 : (ℓ₂ ^ 2 - 3 * x) * ℓ₃ = -(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y) :
    ((3*ℓ₂^6 + 4*ℓ₂^5*ℓ₃ - 2*ℓ₂^4*ℓ₃^2 - 9*ℓ₂^4*x - 2*ℓ₂^3*ℓ₃^3 - 18*ℓ₂^3*ℓ₃*x + 2*ℓ₂^2*ℓ₃^4 - 6*ℓ₂^2*ℓ₃^2*x + 9*ℓ₂^2*x^2 + 6*ℓ₂*ℓ₃^3*x + 18*ℓ₂*ℓ₃*x^2 - ℓ₃^6 + 3*ℓ₃^4*x + 9*ℓ₃^2*x^2)) * (ℓ₂ ^ 2 - 3 * x) ^ 6 * (2 * y) ^ 12 = -4 * (x ^ 3 + 7) * ((7*x^24 + 27608*x^21 - 2101904*x^18 - 284585728*x^15 - 2228742656*x^12 - 26142548992*x^9 - 330576748544*x^6 - 661153497088*x^3 + 377801998336)) := by
  linear_combination ((2 * y) ^ 12 * ((3*ℓ₂^15 + ℓ₂^14*ℓ₃ - 3*ℓ₂^13*ℓ₃^2 - 54*ℓ₂^13*x + ℓ₂^12*ℓ₃^3 - 24*ℓ₂^12*ℓ₃*x - 6*ℓ₂^12*y + ℓ₂^11*ℓ₃^4 + 48*ℓ₂^11*ℓ₃^2*x + 4*ℓ₂^11*ℓ₃*y + 414*ℓ₂^11*x^2 - ℓ₂^10*ℓ₃^5 - 12*ℓ₂^10*ℓ₃^3*x + 2*ℓ₂^10*ℓ₃^2*y + 234*ℓ₂^10*ℓ₃*x^2 + 90*ℓ₂^10*x*y - 15*ℓ₂^9*ℓ₃^4*x - 4*ℓ₂^9*ℓ₃^3*y - 315*ℓ₂^9*ℓ₃^2*x^2 - 48*ℓ₂^9*ℓ₃*x*y - 1755*ℓ₂^9*x^3 + 8*ℓ₂^9*y^2 + 15*ℓ₂^8*ℓ₃^5*x + 2*ℓ₂^8*ℓ₃^4*y + 45*ℓ₂^8*ℓ₃^3*x^2 - 30*ℓ₂^8*ℓ₃^2*x*y - 1215*ℓ₂^8*ℓ₃*x^3 - 16*ℓ₂^8*ℓ₃*y^2 - 558*ℓ₂^8*x^2*y + 90*ℓ₂^7*ℓ₃^4*x^2 + 48*ℓ₂^7*ℓ₃^3*x*y + 1080*ℓ₂^7*ℓ₃^2*x^3 + 12*ℓ₂^7*ℓ₃^2*y^2 + 216*ℓ₂^7*ℓ₃*x^2*y + 4455*ℓ₂^7*x^4 - 84*ℓ₂^7*x*y^2 - 90*ℓ₂^6*ℓ₃^5*x^2 - 24*ℓ₂^6*ℓ₃^4*x*y - 4*ℓ₂^6*ℓ₃^3*y^2 + 180*ℓ₂^6*ℓ₃^2*x^2*y + 3645*ℓ₂^6*ℓ₃*x^4 + 156*ℓ₂^6*ℓ₃*x*y^2 + 1836*ℓ₂^6*x^3*y + 64*ℓ₂^6*y^3 - 270*ℓ₂^5*ℓ₃^4*x^3 - 216*ℓ₂^5*ℓ₃^3*x^2*y - 2025*ℓ₂^5*ℓ₃^2*x^4 - 108*ℓ₂^5*ℓ₃^2*x*y^2 - 432*ℓ₂^5*ℓ₃*x^3*y - 32*ℓ₂^5*ℓ₃*y^3 - 6804*ℓ₂^5*x^5 + 324*ℓ₂^5*x^2*y^2 + 270*ℓ₂^4*ℓ₃^5*x^3 + 108*ℓ₂^4*ℓ₃^4*x^2*y - 405*ℓ₂^4*ℓ₃^3*x^4 + 36*ℓ₂^4*ℓ₃^3*x*y^2 - 540*ℓ₂^4*ℓ₃^2*x^3*y + 8*ℓ₂^4*ℓ₃^2*y^3 - 6318*ℓ₂^4*ℓ₃*x^5 - 540*ℓ₂^4*ℓ₃*x^2*y^2 - 3402*ℓ₂^4*x^4*y - 408*ℓ₂^4*x*y^3 + 405*ℓ₂^3*ℓ₃^4*x^4 + 432*ℓ₂^3*ℓ₃^3*x^3*y + 1944*ℓ₂^3*ℓ₃^2*x^5 + 324*ℓ₂^3*ℓ₃^2*x^2*y^2 + 324*ℓ₂^3*ℓ₃*x^4*y + 192*ℓ₂^3*ℓ₃*x*y^3 + 5832*ℓ₂^3*x^6 - 540*ℓ₂^3*x^3*y^2 + 80*ℓ₂^3*y^4 - 405*ℓ₂^2*ℓ₃^5*x^4 - 216*ℓ₂^2*ℓ₃^4*x^3*y + 972*ℓ₂^2*ℓ₃^3*x^5 - 108*ℓ₂^2*ℓ₃^3*x^2*y^2 + 810*ℓ₂^2*ℓ₃^2*x^4*y - 48*ℓ₂^2*ℓ₃^2*x*y^3 + 5832*ℓ₂^2*ℓ₃*x^6 + 756*ℓ₂^2*ℓ₃*x^3*y^2 - 16*ℓ₂^2*ℓ₃*y^4 + 3402*ℓ₂^2*x^5*y + 720*ℓ₂^2*x^2*y^3 - 243*ℓ₂*ℓ₃^4*x^5 - 324*ℓ₂*ℓ₃^3*x^4*y - 729*ℓ₂*ℓ₃^2*x^6 - 324*ℓ₂*ℓ₃^2*x^3*y^2 - 288*ℓ₂*ℓ₃*x^2*y^3 - 2187*ℓ₂*x^7 + 324*ℓ₂*x^4*y^2 - 240*ℓ₂*x*y^4 + 243*ℓ₃^5*x^5 + 162*ℓ₃^4*x^4*y - 729*ℓ₃^3*x^6 + 108*ℓ₃^3*x^3*y^2 - 486*ℓ₃^2*x^5*y + 72*ℓ₃^2*x^2*y^3 - 2187*ℓ₃*x^7 - 324*ℓ₃*x^4*y^2 + 48*ℓ₃*x*y^4 - 1458*x^6*y - 216*x^3*y^3 + 32*y^5))) * hℓ3 + ((8192*ℓ₂^11*y^13 + 12288*ℓ₂^10*x^2*y^12 + 18432*ℓ₂^9*x^4*y^11 - 147456*ℓ₂^9*x*y^13 + 27648*ℓ₂^8*x^6*y^10 - 221184*ℓ₂^8*x^3*y^12 - 163840*ℓ₂^8*y^14 + 41472*ℓ₂^7*x^8*y^9 - 331776*ℓ₂^7*x^5*y^11 + 860160*ℓ₂^7*x^2*y^13 + 62208*ℓ₂^6*x^10*y^8 - 497664*ℓ₂^6*x^7*y^10 + 1290240*ℓ₂^6*x^4*y^12 + 1572864*ℓ₂^6*x*y^14 + 93312*ℓ₂^5*x^12*y^7 - 746496*ℓ₂^5*x^9*y^9 + 1935360*ℓ₂^5*x^6*y^11 - 2064384*ℓ₂^5*x^3*y^13 - 425984*ℓ₂^5*y^15 + 139968*ℓ₂^4*x^14*y^6 - 1119744*ℓ₂^4*x^11*y^8 + 2903040*ℓ₂^4*x^8*y^10 - 3096576*ℓ₂^4*x^5*y^12 - 5947392*ℓ₂^4*x^2*y^14 + 209952*ℓ₂^3*x^16*y^5 - 1679616*ℓ₂^3*x^13*y^7 + 4354560*ℓ₂^3*x^10*y^9 - 4644864*ℓ₂^3*x^7*y^11 + 1032192*ℓ₂^3*x^4*y^13 + 2654208*ℓ₂^3*x*y^15 + 314928*ℓ₂^2*x^18*y^4 - 2519424*ℓ₂^2*x^15*y^6 + 6531840*ℓ₂^2*x^12*y^8 - 6967296*ℓ₂^2*x^9*y^10 + 1548288*ℓ₂^2*x^6*y^12 + 11059200*ℓ₂^2*x^3*y^14 - 393216*ℓ₂^2*y^16 + 472392*ℓ₂*x^20*y^3 - 3779136*ℓ₂*x^17*y^5 + 9797760*ℓ₂*x^14*y^7 - 10450944*ℓ₂*x^11*y^9 + 2322432*ℓ₂*x^8*y^11 + 4644864*ℓ₂*x^5*y^13 - 5013504*ℓ₂*x^2*y^15 + 708588*x^22*y^2 - 5668704*x^19*y^4 + 14696640*x^16*y^6 - 15676416*x^13*y^8 + 3483648*x^10*y^10 + 6967296*x^7*y^12 - 10174464*x^4*y^14 + 1179648*x*y^16)) * hℓ2 + ((-28*x^24 - 2125792*x^21*y^2 - 110432*x^21 + 14880320*x^18*y^4 + 14770112*x^18*y^2 + 8407616*x^18 - 29209600*x^15*y^6 - 89392128*x^15*y^4 - 94983168*x^15*y^2 + 1138342912*x^15 + 17819648*x^12*y^8 + 115075072*x^12*y^6 + 530761728*x^12*y^4 + 1803225088*x^12*y^2 + 8914970624*x^12 + 7368704*x^9*y^10 - 9662464*x^9*y^8 - 274763776*x^9*y^6 - 1912107008*x^9*y^4 - 3707604992*x^9*y^2 + 104570195968*x^9 - 13533184*x^6*y^12 - 61243392*x^6*y^10 - 207126528*x^6*y^8 + 11239424*x^6*y^6 + 9677144064*x^6*y^4 + 130523430912*x^6*y^2 + 1322306994176*x^6 + 5046272*x^3*y^14 + 33488896*x^3*y^12 + 221577216*x^3*y^10 + 1461125120*x^3*y^8 + 9598468096*x^3*y^6 + 62783422464*x^3*y^4 + 408642977792*x^3*y^2 + 2644613988352*x^3 - 262144*y^16 - 1835008*y^14 - 12845056*y^12 - 89915392*y^10 - 629407744*y^8 - 4405854208*y^6 - 30840979456*y^4 - 215886856192*y^2 - 1511207993344)) * hcurve

/-- **Core algebraic identity for the 7-torsion bridge over `𝔽̄_p`.**
`x(3P) = x(4P) ⟺ ψ₇(x) = 0`. Token-identical port of `seven_core`. -/
private theorem seven_core_bar (x y ℓ₂ ℓ₃ ℓ₄ : AlgebraicClosure (ZMod Secp256k1.p))
    (h2 : (2 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0)
    (hcurve : y ^ 2 = x ^ 3 + 7) (hy : y ≠ 0)
    (hℓ2 : 2 * y * ℓ₂ = 3 * x ^ 2)
    (hd2 : ℓ₂ ^ 2 - 3 * x ≠ 0)
    (hℓ3 : (ℓ₂ ^ 2 - 3 * x) * ℓ₃ = -(ℓ₂ * (ℓ₂ ^ 2 - 3 * x) + y) - y)
    (hd3 : ℓ₃ ^ 2 - ℓ₂ ^ 2 ≠ 0)
    (hℓ4 : (ℓ₃ ^ 2 - ℓ₂ ^ 2) * ℓ₄ = (ℓ₂^3 + 2*ℓ₂^2*ℓ₃ - 3*ℓ₂*x - ℓ₃^3 - 3*ℓ₃*x)) :
    ℓ₃ ^ 2 - (ℓ₂ ^ 2 - 2 * x) - x = ℓ₄ ^ 2 - (ℓ₃ ^ 2 - (ℓ₂ ^ 2 - 2 * x) - x) - x
      ↔ ((7*x^24 + 27608*x^21 - 2101904*x^18 - 284585728*x^15 - 2228742656*x^12 - 26142548992*x^9 - 330576748544*x^6 - 661153497088*x^3 + 377801998336)) = 0 := by
  have hgoal : (ℓ₃ ^ 2 - (ℓ₂ ^ 2 - 2 * x) - x = ℓ₄ ^ 2 - (ℓ₃ ^ 2 - (ℓ₂ ^ 2 - 2 * x) - x) - x)
      ↔ (ℓ₄ ^ 2 - (2 * (ℓ₃ ^ 2 - ℓ₂ ^ 2) + 3 * x) = 0) := by
    constructor <;> intro h <;> linear_combination -h
  rw [hgoal]
  have hbf4 : (ℓ₄ ^ 2 - (2 * (ℓ₃ ^ 2 - ℓ₂ ^ 2) + 3 * x)) * (ℓ₃ ^ 2 - ℓ₂ ^ 2) ^ 2 = ((3*ℓ₂^6 + 4*ℓ₂^5*ℓ₃ - 2*ℓ₂^4*ℓ₃^2 - 9*ℓ₂^4*x - 2*ℓ₂^3*ℓ₃^3 - 18*ℓ₂^3*ℓ₃*x + 2*ℓ₂^2*ℓ₃^4 - 6*ℓ₂^2*ℓ₃^2*x + 9*ℓ₂^2*x^2 + 6*ℓ₂*ℓ₃^3*x + 18*ℓ₂*ℓ₃*x^2 - ℓ₃^6 + 3*ℓ₃^4*x + 9*ℓ₃^2*x^2)) := by
    linear_combination ((ℓ₂^3 + 2*ℓ₂^2*ℓ₃ - ℓ₂^2*ℓ₄ - 3*ℓ₂*x - ℓ₃^3 + ℓ₃^2*ℓ₄ - 3*ℓ₃*x)) * hℓ4
  have hmaster := seven_master_bar x y ℓ₂ ℓ₃ hcurve hℓ2 hℓ3
  have hd3sq : (ℓ₃ ^ 2 - ℓ₂ ^ 2) ^ 2 ≠ 0 := pow_ne_zero 2 hd3
  have hd2p : (ℓ₂ ^ 2 - 3 * x) ^ 6 ≠ 0 := pow_ne_zero 6 hd2
  have h2y : (2 * y) ^ 12 ≠ 0 := pow_ne_zero 12 (mul_ne_zero h2 hy)
  have hc7 : (-4 * (x ^ 3 + 7) : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
    rw [hcurve.symm]
    have h2y2 : (2 * y) ^ 2 ≠ 0 := pow_ne_zero 2 (mul_ne_zero h2 hy)
    intro hcon; exact h2y2 (by linear_combination -hcon)
  constructor
  · intro hz
    have hG0 : ((3*ℓ₂^6 + 4*ℓ₂^5*ℓ₃ - 2*ℓ₂^4*ℓ₃^2 - 9*ℓ₂^4*x - 2*ℓ₂^3*ℓ₃^3 - 18*ℓ₂^3*ℓ₃*x + 2*ℓ₂^2*ℓ₃^4 - 6*ℓ₂^2*ℓ₃^2*x + 9*ℓ₂^2*x^2 + 6*ℓ₂*ℓ₃^3*x + 18*ℓ₂*ℓ₃*x^2 - ℓ₃^6 + 3*ℓ₃^4*x + 9*ℓ₃^2*x^2)) = 0 := by
      have := hbf4; rw [hz, zero_mul] at this; linear_combination -this
    have hz2 : -4 * (x ^ 3 + 7) * ((7*x^24 + 27608*x^21 - 2101904*x^18 - 284585728*x^15 - 2228742656*x^12 - 26142548992*x^9 - 330576748544*x^6 - 661153497088*x^3 + 377801998336)) = 0 := by rw [← hmaster, hG0]; ring
    exact (mul_eq_zero.mp hz2).resolve_left hc7
  · intro hp
    have hM0 : ((3*ℓ₂^6 + 4*ℓ₂^5*ℓ₃ - 2*ℓ₂^4*ℓ₃^2 - 9*ℓ₂^4*x - 2*ℓ₂^3*ℓ₃^3 - 18*ℓ₂^3*ℓ₃*x + 2*ℓ₂^2*ℓ₃^4 - 6*ℓ₂^2*ℓ₃^2*x + 9*ℓ₂^2*x^2 + 6*ℓ₂*ℓ₃^3*x + 18*ℓ₂*ℓ₃*x^2 - ℓ₃^6 + 3*ℓ₃^4*x + 9*ℓ₃^2*x^2)) * (ℓ₂ ^ 2 - 3 * x) ^ 6 * (2 * y) ^ 12 = 0 := by rw [hmaster, hp]; ring
    have hG0 : ((3*ℓ₂^6 + 4*ℓ₂^5*ℓ₃ - 2*ℓ₂^4*ℓ₃^2 - 9*ℓ₂^4*x - 2*ℓ₂^3*ℓ₃^3 - 18*ℓ₂^3*ℓ₃*x + 2*ℓ₂^2*ℓ₃^4 - 6*ℓ₂^2*ℓ₃^2*x + 9*ℓ₂^2*x^2 + 6*ℓ₂*ℓ₃^3*x + 18*ℓ₂*ℓ₃*x^2 - ℓ₃^6 + 3*ℓ₃^4*x + 9*ℓ₃^2*x^2)) = 0 := by
      have h1 : ((3*ℓ₂^6 + 4*ℓ₂^5*ℓ₃ - 2*ℓ₂^4*ℓ₃^2 - 9*ℓ₂^4*x - 2*ℓ₂^3*ℓ₃^3 - 18*ℓ₂^3*ℓ₃*x + 2*ℓ₂^2*ℓ₃^4 - 6*ℓ₂^2*ℓ₃^2*x + 9*ℓ₂^2*x^2 + 6*ℓ₂*ℓ₃^3*x + 18*ℓ₂*ℓ₃*x^2 - ℓ₃^6 + 3*ℓ₃^4*x + 9*ℓ₃^2*x^2)) * (ℓ₂ ^ 2 - 3 * x) ^ 6 = 0 := (mul_eq_zero.mp hM0).resolve_right h2y
      exact (mul_eq_zero.mp h1).resolve_right hd2p
    have hbz : (ℓ₄ ^ 2 - (2 * (ℓ₃ ^ 2 - ℓ₂ ^ 2) + 3 * x)) * (ℓ₃ ^ 2 - ℓ₂ ^ 2) ^ 2 = 0 := by
      rw [hbf4, hG0]
    exact (mul_eq_zero.mp hbz).resolve_right hd3sq

/-- **Point-level 7-torsion criterion over `𝔽̄_p`: `7 • P = 0 ⟺ ψ 7` vanishes at `P`.**
This is where the `ψ₇ ↔ E[7]` bridge has its real content: over `𝔽̄_p` the `24` roots of
the mapped `preΨ' 7` are realized by actual curve points, giving `#E[7](𝔽̄_p) = 49` once
paired with `±y` (`SevenTorsionStructure.lean`). -/
theorem secp256k1Bar_seven_nsmul_eq_zero_iff
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) :
    (7 : ℕ) • (Point.some x y h) = 0 ↔ (secp256k1Bar.ψ 7).evalEval x y = 0 := by
  have h2 : (2 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := bar_two_ne_zero
  have h3ne : (3 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := bar_three_ne_zero
  have hcurve : y ^ 2 = x ^ 3 + 7 := bar_curve_of_nonsingular x y h
  have hnegY : secp256k1Bar.toAffine.negY x y = -y := bar_negY x y
  rw [secp256k1Bar_psi7_evalEval x y hcurve]
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
    have h7P : (7 : ℕ) • (Point.some x y h) = Point.some x y h := by
      rw [show (7 : ℕ) = 1 + 2 + 2 + 2 from rfl, add_nsmul, add_nsmul, add_nsmul, one_nsmul,
        h2P, add_zero, add_zero, add_zero]
    have hx3 : x ^ 3 = -7 := by rw [hy00] at hcurve; linear_combination -hcurve
    refine iff_of_false ?_ ?_
    · rw [h7P]; exact Point.some_ne_zero h
    · intro hc
      exact bar_c3063651608241_ne_zero
        (by linear_combination -hc + ((7*x^21 + 27559*x^18 - 2294817*x^15 - 268522009*x^12 - 349088593*x^9 - 23698928841*x^6 - 164684246657*x^3 + 491636229511)) * hx3)
  · -- y ≠ negY, so y ≠ 0
    have hy : y ≠ 0 := by intro h0; exact hy0 (by rw [hnegY, h0]; ring)
    have hYd : y - secp256k1Bar.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy0
    set s2 := secp256k1Bar.toAffine.slope x x y y with hs2def
    set X2 := secp256k1Bar.toAffine.addX x x s2 with hX2def
    set Y2 := secp256k1Bar.toAffine.addY x x y s2 with hY2def
    have hsl2 : s2 * (2 * y) = 3 * x ^ 2 := by
      rw [hs2def, slope_of_Y_ne rfl hy0, div_mul_eq_mul_div, div_eq_iff hYd]
      simp only [secp256k1Bar, WeierstrassCurve.map, WeierstrassCurve.map_a₁,
        WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄,
        WeierstrassCurve.map_a₆, secp256k1, map_zero, WeierstrassCurve.Affine.negY]
      ring
    have hℓ2 : 2 * y * s2 = 3 * x ^ 2 := by linear_combination hsl2
    have hx2val : X2 = s2 ^ 2 - 2 * x := by
      rw [hX2def]
      simp only [WeierstrassCurve.Affine.addX, secp256k1Bar, WeierstrassCurve.map,
        WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃,
        WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆, secp256k1, map_zero]
      ring
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
    -- `2 • P ≠ 0` directly from `hP2` (an affine point is not `O`); this replaces the
    -- `𝔽_p` file's appeal to the two-torsion criterion, avoiding a `TwoTorsionPointBar`.
    have h2ne : (2 : ℕ) • (Point.some x y h) ≠ 0 := by
      rw [hP2]; exact Point.some_ne_zero hns2
    by_cases h3 : (3 : ℕ) • (Point.some x y h) = 0
    · -- 3-torsion branch: gcd(3,7)=1 so 7P = P ≠ 0
      have h34 : 3 * x ^ 4 + 84 * x = 0 := by
        have := (secp256k1Bar_three_nsmul_eq_zero_iff x y h).mp h3
        rwa [secp256k1Bar_psi3_evalEval] at this
      have h7P : (7 : ℕ) • (Point.some x y h) = Point.some x y h := by
        rw [show (7 : ℕ) = 1 + 3 + 3 from rfl, add_nsmul, add_nsmul, one_nsmul, h3,
          add_zero, add_zero]
      refine iff_of_false ?_ ?_
      · rw [h7P]; exact Point.some_ne_zero h
      · intro hc
        have hfac : 3 * x * (x ^ 3 + 28) = 0 := by linear_combination h34
        rcases mul_eq_zero.mp hfac with h3x | hx328
        · rcases mul_eq_zero.mp h3x with hc3 | hx0
          · exact h3ne hc3
          · exact bar_c377801998336_ne_zero
              (by linear_combination hc - ((7*x^23 + 27608*x^20 - 2101904*x^17 - 284585728*x^14 - 2228742656*x^11 - 26142548992*x^8 - 330576748544*x^5 - 661153497088*x^2)) * hx0)
        · have hx3 : x ^ 3 = -28 := by linear_combination hx328
          exact bar_c2478758911082496_ne_zero
            (by linear_combination hc - ((7*x^21 + 27412*x^18 - 2869440*x^15 - 204241408*x^12 + 3490016768*x^9 - 123863018496*x^6 + 3137587769344*x^3 - 88513611038720)) * hx3)
    · -- 3P ≠ 0
      have hΨ3ne : 3 * x ^ 4 + 84 * x ≠ 0 := fun hc =>
        h3 ((secp256k1Bar_three_nsmul_eq_zero_iff x y h).mpr
          (by rw [secp256k1Bar_psi3_evalEval]; exact hc))
      have hId : (s2 ^ 2 - 3 * x) * (4 * y ^ 2) = -(3 * x ^ 4 + 84 * x) := by
        linear_combination (2 * s2 * y + 3 * x ^ 2) * hℓ2 + (-12 * x) * hcurve
      have hd2 : s2 ^ 2 - 3 * x ≠ 0 := by
        intro hc; apply hΨ3ne
        have := hId; rw [hc, zero_mul] at this; linear_combination this
      have hx2x : X2 - x = s2 ^ 2 - 3 * x := by rw [hx2val]; ring
      have hx2ne : X2 ≠ x := by rw [← sub_ne_zero, hx2x]; exact hd2
      set s3 := secp256k1Bar.toAffine.slope X2 x Y2 y with hs3def
      set X3 := secp256k1Bar.toAffine.addX X2 x s3 with hX3def
      set Y3 := secp256k1Bar.toAffine.addY X2 x Y2 s3 with hY3def
      have hx3val : X3 = s3 ^ 2 - (s2 ^ 2 - 2 * x) - x := by
        rw [hX3def]
        simp only [WeierstrassCurve.Affine.addX, secp256k1Bar, WeierstrassCurve.map,
          WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃,
          WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆, secp256k1, map_zero]
        rw [hx2val]; ring
      have hy3val : Y3 = -(s3 * (X3 - X2) + Y2) := by
        rw [hY3def]
        simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
          WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1Bar,
          WeierstrassCurve.map, WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂,
          WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆,
          secp256k1, map_zero]
        rw [hX3def]
        simp only [WeierstrassCurve.Affine.addX, secp256k1Bar, WeierstrassCurve.map,
          WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃,
          WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆, secp256k1, map_zero]
        ring
      have hns3 : secp256k1Bar.toAffine.Nonsingular X3 Y3 :=
        nonsingular_add hns2 h (fun hxy => hx2ne hxy.1)
      have hP3 : (3 : ℕ) • (Point.some x y h) = Point.some X3 Y3 hns3 := by
        rw [show (3 : ℕ) = 2 + 1 from rfl, add_nsmul, one_nsmul, hP2]
        exact Point.add_some (fun hxy => hx2ne hxy.1)
      have hsl3s : s3 * (X2 - x) = Y2 - y := by
        rw [hs3def, slope_of_X_ne hx2ne]
        exact div_mul_cancel₀ _ (sub_ne_zero.mpr hx2ne)
      have hℓ3 : (s2 ^ 2 - 3 * x) * s3 = -(s2 * (s2 ^ 2 - 3 * x) + y) - y := by
        have hstep := hsl3s; rw [hy2val, hx2x] at hstep; linear_combination hstep
      have hS4Y : Y3 - y = (s2^3 + 2*s2^2*s3 - 3*s2*x - s3^3 - 3*s3*x) := by
        rw [hy3val, hy2val, hx3val, hx2val]; ring
      by_cases hX3 : X3 = x
      · -- order-4 branch: 4P = 0 ⇒ 7P = 3P ≠ 0
        have hX3red : s3 ^ 2 - s2 ^ 2 = 0 := by
          have hh := hX3; rw [hx3val] at hh; linear_combination hh
        rcases Y_eq_of_X_eq hns3.1 h.1 hX3 with hYeq | hYneg
        · exfalso
          have e3P : (3 : ℕ) • (Point.some x y h) = Point.some x y h := by
            rw [hP3, Point.some.injEq]; exact ⟨hX3, hYeq⟩
          rw [show (3 : ℕ) = 2 + 1 from rfl, add_nsmul, one_nsmul] at e3P
          exact h2ne (add_right_cancel (show (2 : ℕ) • (Point.some x y h) + Point.some x y h
              = (0 : secp256k1Bar.toAffine.Point) + Point.some x y h by
                rw [zero_add]; exact e3P))
        · have hY3neg : Y3 = -y := by rw [hYneg, hnegY]
          have h3PnegP : (3 : ℕ) • (Point.some x y h) = -(Point.some x y h) := by
            rw [hP3, Point.neg_some, Point.some.injEq]; exact ⟨hX3, by rw [hY3neg, hnegY]⟩
          have h4P : (4 : ℕ) • (Point.some x y h) = 0 := by
            rw [show (4 : ℕ) = 3 + 1 from rfl, add_nsmul, one_nsmul, h3PnegP, neg_add_cancel]
          have h7P : (7 : ℕ) • (Point.some x y h) = (3 : ℕ) • (Point.some x y h) := by
            rw [show (7 : ℕ) = 4 + 3 from rfl, add_nsmul, h4P, zero_add]
          have hS4val : ((s2^3 + 2*s2^2*s3 - 3*s2*x - s3^3 - 3*s3*x)) = -2 * y := by
            rw [← hS4Y, hY3neg]; ring
          refine iff_of_false ?_ ?_
          · rw [h7P, hP3]; exact Point.some_ne_zero hns3
          · intro hc
            have hmaster := seven_master_bar x y s2 s3 hcurve hℓ2 hℓ3
            rw [hc, mul_zero] at hmaster
            have hd2p : (s2 ^ 2 - 3 * x) ^ 6 ≠ 0 := pow_ne_zero 6 hd2
            have h2y : (2 * y) ^ 12 ≠ 0 := pow_ne_zero 12 (mul_ne_zero h2 hy)
            have hGval : ((3*s2^6 + 4*s2^5*s3 - 2*s2^4*s3^2 - 9*s2^4*x - 2*s2^3*s3^3 - 18*s2^3*s3*x + 2*s2^2*s3^4 - 6*s2^2*s3^2*x + 9*s2^2*x^2 + 6*s2*s3^3*x + 18*s2*s3*x^2 - s3^6 + 3*s3^4*x + 9*s3^2*x^2)) = ((s2^3 + 2*s2^2*s3 - 3*s2*x - s3^3 - 3*s3*x)) ^ 2 := by
              linear_combination (-(2 * (s3 ^ 2 - s2 ^ 2 + x) + x) * (s3 ^ 2 - s2 ^ 2)) * hX3red
            rw [hGval] at hmaster
            have hS40 : ((s2^3 + 2*s2^2*s3 - 3*s2*x - s3^3 - 3*s3*x)) ^ 2 = 0 := by
              have h1 : ((s2^3 + 2*s2^2*s3 - 3*s2*x - s3^3 - 3*s3*x)) ^ 2 * (s2 ^ 2 - 3 * x) ^ 6 = 0 :=
                (mul_eq_zero.mp hmaster).resolve_right h2y
              exact (mul_eq_zero.mp h1).resolve_right hd2p
            have hS4z : ((s2^3 + 2*s2^2*s3 - 3*s2*x - s3^3 - 3*s3*x)) = 0 := sq_eq_zero_iff.mp hS40
            rw [hS4val] at hS4z
            have h2y0 : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * y = 0 := by
              linear_combination -hS4z
            exact hy ((mul_eq_zero.mp h2y0).resolve_left h2)
      · -- main branch: 3P ≠ 0 and 4P ≠ 0
        have hd3 : s3 ^ 2 - s2 ^ 2 ≠ 0 := by
          intro hc; apply hX3; rw [hx3val]; linear_combination hc
        set s4 := secp256k1Bar.toAffine.slope X3 x Y3 y with hs4def
        set X4 := secp256k1Bar.toAffine.addX X3 x s4 with hX4def
        set Y4 := secp256k1Bar.toAffine.addY X3 x Y3 s4 with hY4def
        have hx4val : X4 = s4 ^ 2 - X3 - x := by
          rw [hX4def]
          simp only [WeierstrassCurve.Affine.addX, secp256k1Bar, WeierstrassCurve.map,
            WeierstrassCurve.map_a₁, WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃,
            WeierstrassCurve.map_a₄, WeierstrassCurve.map_a₆, secp256k1, map_zero]
          ring
        have hns4 : secp256k1Bar.toAffine.Nonsingular X4 Y4 :=
          nonsingular_add hns3 h (fun hxy => hX3 hxy.1)
        have hP4 : (4 : ℕ) • (Point.some x y h) = Point.some X4 Y4 hns4 := by
          rw [show (4 : ℕ) = 3 + 1 from rfl, add_nsmul, one_nsmul, hP3]
          exact Point.add_some (fun hxy => hX3 hxy.1)
        have hsl4s : s4 * (X3 - x) = Y3 - y := by
          rw [hs4def, slope_of_X_ne hX3]
          exact div_mul_cancel₀ _ (sub_ne_zero.mpr hX3)
        have hℓ4 : (s3 ^ 2 - s2 ^ 2) * s4 = (s2^3 + 2*s2^2*s3 - 3*s2*x - s3^3 - 3*s3*x) := by
          have hX3mx : X3 - x = s3 ^ 2 - s2 ^ 2 := by rw [hx3val]; ring
          have hst := hsl4s; rw [hX3mx] at hst
          linear_combination hst + hS4Y
        have hxiff : X3 = X4 ↔ ((7*x^24 + 27608*x^21 - 2101904*x^18 - 284585728*x^15 - 2228742656*x^12 - 26142548992*x^9 - 330576748544*x^6 - 661153497088*x^3 + 377801998336)) = 0 := by
          rw [hx4val, hx3val]
          exact seven_core_bar x y s2 s3 s4 h2 hcurve hy hℓ2 hd2 hℓ3 hd3 hℓ4
        have hyimp : X3 = X4 → Y3 = secp256k1Bar.toAffine.negY X4 Y4 := by
          intro hx
          rcases Y_eq_of_X_eq hns3.1 hns4.1 hx with hyy | hyn
          · exfalso
            have e34 : (3 : ℕ) • (Point.some x y h) = (4 : ℕ) • (Point.some x y h) := by
              rw [hP3, hP4, Point.some.injEq]; exact ⟨hx, hyy⟩
            rw [show (4 : ℕ) = 3 + 1 from rfl, add_nsmul, one_nsmul] at e34
            have hP0 : (0 : secp256k1Bar.toAffine.Point) = Point.some x y h :=
              add_left_cancel (show (3 : ℕ) • (Point.some x y h) + 0
                = (3 : ℕ) • (Point.some x y h) + Point.some x y h by
                  rw [add_zero]; exact e34)
            exact Point.some_ne_zero h hP0.symm
          · exact hyn
        rw [show (7 : ℕ) = 3 + 4 from rfl, add_nsmul, hP3, hP4, add_eq_zero_iff_eq_neg,
          Point.neg_some, Point.some.injEq]
        constructor
        · rintro ⟨hx, _⟩; exact hxiff.mp hx
        · intro hp; exact ⟨hxiff.mpr hp, hyimp (hxiff.mpr hp)⟩

/-- **Reconciliation with the root-count vocabulary of `DivisionPolynomialSeparable.lean`:**
`7 • P = 0` iff the `x`-coordinate of `P` is a root of the mapped univariate `preΨ' 7`,
i.e. of `((secp256k1.preΨ' 7).map φ) ∈ 𝔽̄_p[X]` — the polynomial whose roots were counted
(`24`, all distinct) by `secp256k1_preΨ₇_roots_card_bar`/`…_nodup_bar`. Together they say:
the 7-torsion `x`-locus of `secp256k1Bar` is exactly that 24-element root set. -/
theorem secp256k1Bar_seven_torsion_iff_root
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) :
    (7 : ℕ) • Point.some x y h = 0 ↔ ((secp256k1.preΨ' 7).map φK).eval x = 0 := by
  have hcurve : y ^ 2 = x ^ 3 + 7 := bar_curve_of_nonsingular x y h
  rw [secp256k1Bar_seven_nsmul_eq_zero_iff x y h, secp256k1Bar_psi7_evalEval x y hcurve]
  have hmap : ((secp256k1.preΨ' 7).map φK).eval x = (7*x^24 + 27608*x^21 - 2101904*x^18 - 284585728*x^15 - 2228742656*x^12 - 26142548992*x^9 - 330576748544*x^6 - 661153497088*x^3 + 377801998336) := by
    rw [secp256k1_preΨ₇]
    simp only [Polynomial.map_add, Polynomial.map_sub, Polynomial.map_mul,
      Polynomial.map_pow, Polynomial.map_ofNat, Polynomial.map_X, eval_add, eval_sub,
      eval_mul, eval_pow, Polynomial.eval_ofNat, eval_X]
  rw [hmap]

end Ecdlp.Curve
