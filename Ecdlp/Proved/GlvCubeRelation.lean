import Mathlib
import Ecdlp.Proved.Secp256k1Curve
import Ecdlp.Proved.GlvEndomorphism
import Ecdlp.Proved.GlvHom

/-!
# The GLV endomorphism is a primitive cube root of unity: `φ² + φ + 1 = 0`

The capstone CM fact: `glvPoint` satisfies its minimal polynomial `x² + x + 1` on the
whole secp256k1 point group,

  `glvPoint (glvPoint P) + glvPoint P + P = 0`   for every `P`.

This says `glvPoint` is a primitive cube root of unity in `End(E)` — the
complex-multiplication-by-`ℤ[ζ₃]` structure of the `j = 0` curve, and the algebraic
heart of GLV (it does NOT need the scalar `λ` or point counting; see `notes/GLV_LAMBDA.md`).

**Why it holds.** For `P = (x, y)`, the three points `P = (x,y)`, `φP = (βx, y)`,
`φ²P = (β²x, y)` share the `Y`-coordinate `y`, so they are collinear on the horizontal
line `Y = y` (whose three intersections with `Y² = X³ + 7` are exactly `x, βx, β²x`,
the roots of `X³ = y² − 7`). Three collinear points sum to `O`. Concretely the first two
already sum to `−P`: the secant/tangent slope is `0` (equal `Y`'s), giving new
`X = −(β² + β)x = x` (using `β² + β = −1`) and `Y = −y`, i.e. `φ²P + φP = −P`.

The proof splits on `x = 0` (the three points coincide at a 3-torsion point `(0, ±√7)`,
handled by the doubling formula) vs `x ≠ 0` (`β²x ≠ βx`, the secant formula). In both
cases the sum of the first two points plus `P` is closed to `0` by `add_of_Y_eq`.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **`φ² + φ + 1 = 0`: the GLV endomorphism is a primitive cube root of unity.** -/
theorem secp256k1_glv_cube_relation (P : secp256k1.toAffine.Point) :
    glvPoint (glvPoint P) + glvPoint P + P = 0 := by
  -- β eigenvalue facts.
  have hbeig : (Secp256k1.beta : ZMod Secp256k1.p) ^ 2
      + (Secp256k1.beta : ZMod Secp256k1.p) + 1 = 0 := by
    have h0 : ((Secp256k1.beta ^ 2 + Secp256k1.beta + 1 : ℕ) : ZMod Secp256k1.p) = 0 := by
      rw [ZMod.natCast_eq_zero_iff]
      exact Nat.dvd_of_mod_eq_zero Secp256k1.beta_field_eigenvalue
    push_cast at h0; linear_combination h0
  have hb0 : (Secp256k1.beta : ZMod Secp256k1.p) ≠ 0 := by
    intro hb; rw [hb] at hbeig; norm_num at hbeig
  have hb1 : (Secp256k1.beta : ZMod Secp256k1.p) ≠ 1 := by
    intro hb; rw [hb] at hbeig
    have h3 : (3 : ZMod Secp256k1.p) = 0 := by linear_combination hbeig
    have hne3 : ((3 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
    exact hne3 (by exact_mod_cast h3)
  -- `negY _ y = -y` for secp256k1.
  have hnegY : ∀ a w : ZMod Secp256k1.p, secp256k1.toAffine.negY a w = -w := by
    intro a w; simp [WeierstrassCurve.Affine.negY, secp256k1]
  cases P with
  | zero => simp only [glvPoint_zero, add_zero, zero_add]
  | some x y h =>
    simp only [glvPoint_some]
    set b : ZMod Secp256k1.p := (Secp256k1.beta : ZMod Secp256k1.p) with hbdef
    -- goal: some (b*(b*x)) y _ + some (b*x) y _ + some x y h = 0
    by_cases hx0 : x = 0
    · -- Coincident / 3-torsion case: the three points are all `(0, y)`.
      subst hx0
      -- `(0,y)` on the curve forces `y² = 7`, so `y ≠ 0`.
      have hy0 : y ≠ 0 := by
        intro hy
        have heq : secp256k1.toAffine.Equation 0 y :=
          ((WeierstrassCurve.Affine.nonsingular_iff 0 y).mp h).1
        rw [WeierstrassCurve.Affine.equation_iff] at heq
        rw [hy] at heq
        simp only [secp256k1] at heq
        revert heq; native_decide
      have hyne : y ≠ secp256k1.toAffine.negY (b * 0) y := by
        rw [hnegY]; intro hc; exact hy0 (by linear_combination hc / 2)
      rw [add_of_Y_ne hyne]
      have hxe : (b * (b * 0) : ZMod Secp256k1.p) = b * 0 := by ring
      refine add_of_Y_eq ?_ ?_
      · rw [slope_of_Y_ne hxe hyne]
        simp only [WeierstrassCurve.Affine.addX, WeierstrassCurve.Affine.negY, secp256k1]
        ring
      · rw [slope_of_Y_ne hxe hyne]
        simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negY,
          WeierstrassCurve.Affine.negAddY, WeierstrassCurve.Affine.addX, secp256k1]
        ring
    · -- Generic case: `β²x ≠ βx`, the secant formula.
      have hne : (b * (b * x) : ZMod Secp256k1.p) ≠ b * x := by
        intro hc
        apply hx0
        have h1 : (b * x) * (b - 1) = 0 := by linear_combination hc
        rcases mul_eq_zero.mp h1 with h2 | h3
        · rcases mul_eq_zero.mp h2 with h4 | h5
          · exact absurd h4 hb0
          · exact h5
        · exact absurd (sub_eq_zero.mp h3) hb1
      rw [add_of_X_ne hne]
      refine add_of_Y_eq ?_ ?_
      · -- new X-coordinate `= x`, using `β² + β + 1 = 0`.
        rw [slope_of_X_ne hne]
        simp only [sub_self, zero_div, WeierstrassCurve.Affine.addX, secp256k1]
        linear_combination (-x) * hbeig
      · -- new Y-coordinate `= negY x y = -y`.
        rw [slope_of_X_ne hne]
        simp only [sub_self, zero_div, WeierstrassCurve.Affine.addY,
          WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.negAddY,
          WeierstrassCurve.Affine.addX, secp256k1]
        ring

end Ecdlp.Curve
