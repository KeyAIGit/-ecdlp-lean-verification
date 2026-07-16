import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial
import Ecdlp.Proved.ThreeTorsionCard
import Ecdlp.Proved.ThreeTorsionBridge
import Ecdlp.Proved.FiveTorsionBridge
import Ecdlp.Proved.MultiplicationFormula
import Ecdlp.Proved.CoprimePsi2Psi3

/-!
# N7@3: the multiplication-by-3 `x`-coordinate formula — `x(3•P) = Φ₃(x)/ΨSq₃(x)`

The point-level `n = 3` case of the division-polynomial multiplication formula
`x([n]P) = Φₙ(x)/ΨSqₙ(x)` for secp256k1 — node **N7@3** of the `ψₙ ↔ E[n]` bridge
(`notes/DIVISION_POLY_TORSION_MAP.md`), extending the `n = 2` base case
(`MultiplicationFormula.lean`, `secp256k1_double_x_eq_Φ₂_div_Ψ₂Sq`) one rung up the
ladder toward the general formula (the missing Mathlib rung).

**Main theorem** (`secp256k1_triple_x_eq_Φ₃_div_ΨSq₃`): whenever `3 • P` is an affine
point `(X, Y)`, its `x`-coordinate is
`X = Φ₃(x)/ΨSq₃(x) = (x⁹ − 672x⁶ + 2352x³ + 21952)/(9x⁸ + 504x⁵ + 7056x²)` —
with **no side conditions** beyond `3 • P ≠ O` (encoded by the hypothesis itself):
* in the generic branch, `3P = 2P + P` is computed through the tangent-then-chord
  construction (the same point algebra as `FiveTorsionBridge.lean`), and the core
  identity `triple_x_core` — a `linear_combination` certificate designed symbolically
  and re-checked by the kernel — turns the chord `x`-coordinate into `Φ₃/ΨSq₃`;
* in the 2-torsion branch (`y = 0`), `3P = P` and the formula *still* holds:
  `Ψ₂Sq(x) = 4y² = 0` collapses `Φ₃ = X·Ψ₃² − preΨ₄·Ψ₂Sq` to `x·ΨSq₃`, and the
  denominator is nonzero because `Ψ₂Sq ⊥ Ψ₃` (`CoprimePsi2Psi3.lean`) forbids a
  common root.

Every `linear_combination` certificate and the final formula are symbolically and
numerically cross-checked in `scripts/certs/triple_mult_formula_check.py` (`CERT_OK`);
nothing from the script enters the proofs. The explicit `Φ₃`/`ΨSq₃` evaluations are
kept `private` (public canonical forms live in `TripleDivisionPolynomial.lean` on a
sibling branch; this file stays self-contained whichever lands first). No
`native_decide`, no new axioms.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- `Φ 3` evaluated: the degree-`9 = 3²` numerator of `x(3•P)`. -/
private theorem Φ₃_eval (x : ZMod Secp256k1.p) :
    (secp256k1.Φ 3).eval x = x ^ 9 - 672 * x ^ 6 + 2352 * x ^ 3 + 21952 := by
  rw [secp256k1.Φ_three]
  simp only [eval_sub, eval_mul, eval_pow, eval_X]
  rw [secp256k1_Ψ₃_eval, secp256k1_preΨ₄_eval, secp256k1_Ψ₂Sq_eval]
  ring

/-- `ΨSq 3` evaluated: the degree-8 denominator of `x(3•P)`. -/
private theorem ΨSq₃_eval (x : ZMod Secp256k1.p) :
    (secp256k1.ΨSq 3).eval x = 9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2 := by
  rw [secp256k1.ΨSq_three]
  simp only [eval_pow]
  rw [secp256k1_Ψ₃_eval]
  ring

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Core certificate for N7@3.** With `l2` the tangent slope at `P = (x, y)`
(`2y·l2 = 3x²`), `l3` the chord slope from `2P` to `P` (in its cleared form), and
`x(2P) − x = l2² − 3x ≠ 0`, the chord `x`-coordinate `x(3P) = l3² − x(2P) − x` equals
`Φ₃(x)/ΨSq₃(x)`. The heart is `hmaster`, a symbolically designed `linear_combination`
certificate (`scripts/certs/triple_mult_formula_check.py`), re-verified by the kernel. -/
theorem triple_x_core (x y l2 l3 : ZMod Secp256k1.p)
    (hcurve : y ^ 2 = x ^ 3 + 7) (hy : y ≠ 0)
    (h2 : (2 : ZMod Secp256k1.p) ≠ 0)
    (hl2 : l2 * (2 * y) = 3 * x ^ 2)
    (hd : l2 ^ 2 - 3 * x ≠ 0)
    (hl3 : (l2 ^ 2 - 3 * x) * l3 = -(l2 * (l2 ^ 2 - 3 * x) + y) - y) :
    l3 ^ 2 - (l2 ^ 2 - 2 * x) - x
      = (x ^ 9 - 672 * x ^ 6 + 2352 * x ^ 3 + 21952)
        / (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2) := by
  have h2y : (2 : ZMod Secp256k1.p) * y ≠ 0 := mul_ne_zero h2 hy
  have h4y2 : (4 : ZMod Secp256k1.p) * y ^ 2 ≠ 0 := by
    intro hc
    exact mul_ne_zero h2y h2y (by linear_combination hc)
  -- `(x(2P) − x) · 4y² = −Ψ₃(x)` — the repo's standard doubling identity.
  have hId : (l2 ^ 2 - 3 * x) * (4 * y ^ 2) = -(3 * x ^ 4 + 84 * x) := by
    linear_combination (l2 * (2 * y) + 3 * x ^ 2) * hl2 - 12 * x * hcurve
  have hΨne : (3 : ZMod Secp256k1.p) * x ^ 4 + 84 * x ≠ 0 := by
    intro hc
    rw [hc, neg_zero] at hId
    exact mul_ne_zero hd h4y2 hId
  have hdenne : (9 : ZMod Secp256k1.p) * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2 ≠ 0 := by
    rw [show (9 : ZMod Secp256k1.p) * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2
        = (3 * x ^ 4 + 84 * x) ^ 2 by ring]
    exact pow_ne_zero 2 hΨne
  rw [eq_div_iff hdenne]
  -- eliminate the chord slope: `x(3P)·(l2²−3x)²` in terms of `x, y, l2` only
  have hBF : (l3 ^ 2 - (l2 ^ 2 - 2 * x) - x) * (l2 ^ 2 - 3 * x) ^ 2
      = (l2 * (l2 ^ 2 - 3 * x) + 2 * y) ^ 2
        - (l2 ^ 2 - x) * (l2 ^ 2 - 3 * x) ^ 2 := by
    linear_combination
      ((l2 ^ 2 - 3 * x) * l3 - (l2 * (l2 ^ 2 - 3 * x) + 2 * y)) * hl3
  -- the master certificate (sympy-designed cofactors, kernel-verified)
  have hmaster :
      ((l2 * (l2 ^ 2 - 3 * x) + 2 * y) ^ 2 - (l2 ^ 2 - x) * (l2 ^ 2 - 3 * x) ^ 2)
          * (64 * y ^ 6)
        = (x ^ 9 - 672 * x ^ 6 + 2352 * x ^ 3 + 21952) * (4 * x ^ 3 + 28) := by
    linear_combination
      (32 * l2 ^ 3 * x * y ^ 5 + 48 * l2 ^ 2 * x ^ 3 * y ^ 4 + 128 * l2 ^ 2 * y ^ 6
          + 72 * l2 * x ^ 5 * y ^ 3 + 108 * x ^ 7 * y ^ 2 - 384 * x * y ^ 6) * hl2
      + (4 * x ^ 9 - 320 * x ^ 6 * y ^ 2 - 2688 * x ^ 6 - 320 * x ^ 3 * y ^ 4
          - 448 * x ^ 3 * y ^ 2 + 9408 * x ^ 3 + 256 * y ^ 6 + 1792 * y ^ 4
          + 12544 * y ^ 2 + 87808) * hcurve
  -- square of hId, to trade `(l2²−3x)²·16y⁴` for `Ψ₃(x)²`
  have hIdsq : (l2 ^ 2 - 3 * x) ^ 2 * (16 * y ^ 4) = (3 * x ^ 4 + 84 * x) ^ 2 := by
    linear_combination ((l2 ^ 2 - 3 * x) * (4 * y ^ 2) - (3 * x ^ 4 + 84 * x)) * hId
  -- assemble, then cancel the auxiliary `4y² ≠ 0`
  have hkey : (l3 ^ 2 - (l2 ^ 2 - 2 * x) - x)
        * (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2) * (4 * y ^ 2)
      = (x ^ 9 - 672 * x ^ 6 + 2352 * x ^ 3 + 21952) * (4 * y ^ 2) := by
    linear_combination
      (-(l3 ^ 2 - (l2 ^ 2 - 2 * x) - x) * (4 * y ^ 2)) * hIdsq
      + (64 * y ^ 6) * hBF
      + hmaster
      + (-4 * (x ^ 9 - 672 * x ^ 6 + 2352 * x ^ 3 + 21952)) * hcurve
  exact mul_right_cancel₀ h4y2 hkey

/-- **N7@3 — the multiplication-by-3 `x`-coordinate formula for secp256k1.**
Whenever `3 • P` is an affine point `(X, Y)`, its `x`-coordinate equals Mathlib's
`Φ₃/ΨSq₃` evaluated at `x(P)` — with no side conditions: the generic case goes through
the tangent-then-chord construction and `triple_x_core`; the 2-torsion case (`3P = P`)
holds because `Ψ₂Sq(x) = 0` collapses `Φ₃` to `x·ΨSq₃`, with `ΨSq₃(x) ≠ 0` from the
`Ψ₂Sq ⊥ Ψ₃` Bézout certificate. -/
theorem secp256k1_triple_x_eq_Φ₃_div_ΨSq₃
    {x y X Y : ZMod Secp256k1.p} (h : secp256k1.toAffine.Nonsingular x y)
    {h' : secp256k1.toAffine.Nonsingular X Y}
    (hEq : (3 : ℕ) • (Point.some x y h) = Point.some X Y h') :
    X = (secp256k1.Φ 3).eval x / (secp256k1.ΨSq 3).eval x := by
  rw [Φ₃_eval, ΨSq₃_eval]
  have h2 : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  have hcurve : y ^ 2 = x ^ 3 + 7 := by
    have he : secp256k1.toAffine.Equation x y := h.1
    rw [WeierstrassCurve.Affine.equation_iff] at he
    simp only [secp256k1] at he
    linear_combination he
  have hnegY : secp256k1.toAffine.negY x y = -y := by
    simp [WeierstrassCurve.Affine.negY, secp256k1]
  by_cases hy0 : y = secp256k1.toAffine.negY x y
  · -- 2-torsion branch: `2P = O`, so `3P = P` and `X = x`.
    have h2P : (2 : ℕ) • (Point.some x y h) = 0 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_eq hy0
    have h3P : (3 : ℕ) • (Point.some x y h) = Point.some x y h := by
      rw [show (3 : ℕ) = 1 + 2 from rfl, add_nsmul, one_nsmul, h2P, add_zero]
    rw [h3P, Point.some.injEq] at hEq
    rw [← hEq.1]
    -- on 2-torsion, `y = 0` hence `Ψ₂Sq(x) = 4x³ + 28 = 0`
    have hy00 : y = 0 := by
      rw [hnegY] at hy0
      have h2y0 : (2 : ZMod Secp256k1.p) * y = 0 := by linear_combination hy0
      rcases mul_eq_zero.mp h2y0 with hc | hc
      · exact absurd hc h2
      · exact hc
    have hΨ2z : (4 : ZMod Secp256k1.p) * x ^ 3 + 28 = 0 := by
      rw [hy00] at hcurve
      linear_combination -4 * hcurve
    -- `Ψ₃(x) ≠ 0`: a common root of `Ψ₂Sq` and `Ψ₃` would contradict the Bézout certificate
    have hΨ3ne : (3 : ZMod Secp256k1.p) * x ^ 4 + 84 * x ≠ 0 := by
      intro hc
      obtain ⟨u, v, huv⟩ := secp256k1_isCoprime_Ψ₂Sq_Ψ₃
      have hev := congrArg (Polynomial.eval x) huv
      simp only [Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_one] at hev
      rw [secp256k1_Ψ₂Sq_eval, secp256k1_Ψ₃_eval, hΨ2z, hc] at hev
      simp at hev
    have hdenne : (9 : ZMod Secp256k1.p) * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2 ≠ 0 := by
      rw [show (9 : ZMod Secp256k1.p) * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2
          = (3 * x ^ 4 + 84 * x) ^ 2 by ring]
      exact pow_ne_zero 2 hΨ3ne
    rw [eq_div_iff hdenne]
    linear_combination (2 * x ^ 6 + 280 * x ^ 3 - 784) * hΨ2z
  · -- generic branch: `3P = 2P + P` through tangent-then-chord, then the core.
    have hy : y ≠ 0 := fun h0 => hy0 (by rw [hnegY, h0]; ring)
    have h3Pne : (3 : ℕ) • (Point.some x y h) ≠ 0 := by
      rw [hEq]; exact Point.some_ne_zero h'
    have hΨ3ne : 3 * x ^ 4 + 84 * x ≠ 0 := by
      intro hc
      exact h3Pne ((secp256k1_three_nsmul_eq_zero_iff x y h).mpr
        (by rw [secp256k1_psi3_evalEval]; exact hc))
    have hYd : y - secp256k1.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy0
    set s2 := secp256k1.toAffine.slope x x y y with hs2def
    set X2 := secp256k1.toAffine.addX x x s2 with hX2def
    set Y2 := secp256k1.toAffine.addY x x y s2 with hY2def
    have hsl2 : s2 * (2 * y) = 3 * x ^ 2 := by
      rw [hs2def, slope_of_Y_ne rfl hy0, div_mul_eq_mul_div, div_eq_iff hYd]
      simp only [secp256k1, WeierstrassCurve.Affine.negY]
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
      rw [hX2def]; simp only [WeierstrassCurve.Affine.addX, secp256k1]; ring
    have hx2x : X2 - x = s2 ^ 2 - 3 * x := by rw [hx2val]; ring
    have hx2ne : X2 ≠ x := by rw [← sub_ne_zero, hx2x]; exact hd
    have hy2val : Y2 = -(s2 * (s2 ^ 2 - 3 * x) + y) := by
      rw [hY2def]
      simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
        WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1]
      ring
    have hns2 : secp256k1.toAffine.Nonsingular X2 Y2 :=
      nonsingular_add h h (fun hxy => hy0 hxy.2)
    have hP2 : (2 : ℕ) • (Point.some x y h) = Point.some X2 Y2 hns2 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_ne hy0
    set s3 := secp256k1.toAffine.slope X2 x Y2 y with hs3def
    set X3 := secp256k1.toAffine.addX X2 x s3 with hX3def
    set Y3 := secp256k1.toAffine.addY X2 x Y2 s3 with hY3def
    have hx3val : X3 = s3 ^ 2 - (s2 ^ 2 - 2 * x) - x := by
      rw [hX3def]
      simp only [WeierstrassCurve.Affine.addX, secp256k1]
      rw [hx2val]; ring
    have hns3 : secp256k1.toAffine.Nonsingular X3 Y3 :=
      nonsingular_add hns2 h (fun hxy => hx2ne hxy.1)
    have hP3 : (3 : ℕ) • (Point.some x y h) = Point.some X3 Y3 hns3 := by
      rw [show (3 : ℕ) = 2 + 1 from rfl, add_nsmul, one_nsmul, hP2]
      exact Point.add_some (fun hxy => hx2ne hxy.1)
    have hsl3s : s3 * (X2 - x) = Y2 - y := by
      rw [hs3def, slope_of_X_ne hx2ne]
      exact div_mul_cancel₀ _ (sub_ne_zero.mpr hx2ne)
    have hl3 : (s2 ^ 2 - 3 * x) * s3 = -(s2 * (s2 ^ 2 - 3 * x) + y) - y := by
      have hstep := hsl3s
      rw [hy2val, hx2x] at hstep
      linear_combination hstep
    rw [hP3, Point.some.injEq] at hEq
    rw [← hEq.1, hx3val]
    exact triple_x_core x y s2 s3 hcurve hy h2 (by linear_combination hsl2) hd hl3

end Ecdlp.Curve
