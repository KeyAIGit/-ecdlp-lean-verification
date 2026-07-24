import Mathlib
import Ecdlp.Proved.Secp256k1PrimeP
import Ecdlp.Proved.TorsionPointCount

/-!
# `7` is a quadratic non-residue mod `p`: secp256k1 has no affine point with `x = 0`

A small arithmetic fact about secp256k1 with a disproportionately useful consequence.

Since `p ≡ 1 (mod 7)` and `p ≡ 3 (mod 4)`, quadratic reciprocity gives
`(7 | p) = −(p | 7) = −1`, i.e. **`7` is not a square in `𝔽_p`** (equivalently, the Euler
witness `7^((p−1)/2) ≠ 1`, discharged here by `native_decide`). Substituting `x = 0` into the
curve equation `y² = x³ + 7` would force `y² = 7`, so:

  **no affine point of secp256k1 has `x`-coordinate `0`** (`secp256k1_x_ne_zero`).

## Why this is worth its own module

It converts Lean's junk-value convention `a / 0 = 0` from a nuisance into a *tool*. The
division-polynomial coordinate certificates state the `x`-coordinate of `n • P` in the divided
form `X = Φₙ(x) / ΨSqₙ(x)`. Ordinarily such a statement carries no information when the
denominator vanishes — `a / 0 = 0` makes it vacuously true rather than contradictory, which is
why the denominator hypothesis `ΨSqₙ(x) ≠ 0` normally has to be supplied from outside (in the
N7-uniform development it was supplied by the *torsion bridge* `n • P = O ↔ ψₙ(P) = 0`, an
upstream-gated wall).

Here the implication runs the other way: if `ΨSqₙ(x) = 0` then the divided form collapses to
`X = 0`, and `secp256k1_x_ne_zero` says that is impossible for an affine point. So the
denominator is nonzero **for free** — see `secp256k1_psiSq_ne_zero_of_x_eq_div`, which derives
`ΨSqₙ(x) ≠ 0` from nothing but the divided form itself plus nonsingularity of `n • P`. No
torsion theory, no multiplication-by-`n` coordinate map, and in particular no dependence on
Mathlib's unmerged division-polynomial `zsmul` development.

Stated for a general index `m : ℤ` and, in `secp256k1_den_ne_zero_of_x_eq_div`, for a general
quotient — the argument never inspects the numerator, so it applies verbatim to any coordinate
certificate written in divided form.

`native_decide` (allowed in this repo's trusted base as `Lean.ofReduceBool`) is used only for
the two closed 256-bit literal facts `7 ≠ 0` and `7^(p/2) ≠ 1`. This module declares no
`[Fact (Nat.Prime Secp256k1.p)]` section variable, so those goals are closed terms over the
global instance (`Secp256k1PrimeP.lean`) and `native_decide` can evaluate them — the discipline
recorded in `secp256k1_neg7_pow_ne_one` (`CurveCardinalityExact.lean`), which states its
cubic-residue witness outside that file's `Fact` section for the same reason.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- **`7 ≠ 0` in `𝔽_p`.** Closed literal fact; `native_decide`. -/
theorem secp256k1_seven_ne_zero : (7 : ZMod Secp256k1.p) ≠ 0 := by native_decide

/-- **Euler witness: `7^(p/2) ≠ 1` in `𝔽_p`** (for odd `p`, `p / 2 = (p−1)/2`, which is the
exponent `ZMod.euler_criterion` uses). The goal is a closed term over the global `Fact`
instance, so `native_decide` discharges the 256-bit modular exponentiation — exactly as
`secp256k1_neg7_pow_ne_one` (`CurveCardinalityExact.lean`) does for the cubic witness. -/
theorem secp256k1_seven_pow_ne_one :
    (7 : ZMod Secp256k1.p) ^ (Secp256k1.p / 2) ≠ 1 := by native_decide

/-- **`7` is not a square in `𝔽_p`.** Euler's criterion against the witness
`secp256k1_seven_pow_ne_one`. (Reciprocity cross-check: `p ≡ 1 mod 7` gives `(p|7) = +1`, and
`p ≡ 3 mod 4` with `7 ≡ 3 mod 4` flips the sign, so `(7|p) = −1`.) -/
theorem secp256k1_seven_not_isSquare : ¬ IsSquare (7 : ZMod Secp256k1.p) := fun hsq =>
  secp256k1_seven_pow_ne_one
    ((ZMod.euler_criterion Secp256k1.p secp256k1_seven_ne_zero).mp hsq)

/-- **No affine point of secp256k1 has `x`-coordinate `0`.** At `x = 0` the curve equation
`y² = x³ + 7` reads `y² = 7`, exhibiting `7` as a square — contradicting
`secp256k1_seven_not_isSquare`. -/
theorem secp256k1_x_ne_zero {x y : ZMod Secp256k1.p}
    (h : secp256k1.toAffine.Nonsingular x y) : x ≠ 0 := by
  intro hx0
  refine secp256k1_seven_not_isSquare ⟨y, ?_⟩
  have hc : y ^ 2 = x ^ 3 + 7 := secp256k1_curve_of_nonsingular x y h
  rw [hx0] at hc
  linear_combination -hc

/-- **A divided coordinate certificate forces its own denominator nonzero.** If the
`x`-coordinate of an affine point is presented as a quotient `a / b`, then `b ≠ 0`: otherwise
`a / b = a / 0 = 0` by Lean's junk-value convention, and no affine point has `x = 0`.

The numerator is never inspected, so this applies to any coordinate certificate in divided
form. -/
theorem secp256k1_den_ne_zero_of_x_eq_div {X Y a b : ZMod Secp256k1.p}
    (h : secp256k1.toAffine.Nonsingular X Y) (hX : X = a / b) : b ≠ 0 := fun hb0 =>
  secp256k1_x_ne_zero h (by rw [hX, hb0, div_zero])

/-- **`ΨSqₘ(x) ≠ 0` from the divided `x`-coordinate certificate alone.** The
division-polynomial specialization of `secp256k1_den_ne_zero_of_x_eq_div`: whenever `n • P` is
an affine point whose `x`-coordinate is certified in the canonical divided form
`Φₘ(x) / ΨSqₘ(x)`, the denominator cannot vanish.

This is exactly the non-degeneracy hypothesis that the N7-uniform carrier induction needs at
every step, obtained here **without** the torsion bridge `n • P = O ↔ ψₙ(P) = 0` — so it
breaks the circularity in which that non-degeneracy was previously derived from the bridge and
the bridge itself remained open. -/
theorem secp256k1_psiSq_ne_zero_of_x_eq_div {m : ℤ} {X Y x : ZMod Secp256k1.p}
    (h : secp256k1.toAffine.Nonsingular X Y)
    (hX : X = (secp256k1.Φ m).eval x / (secp256k1.ΨSq m).eval x) :
    (secp256k1.ΨSq m).eval x ≠ 0 :=
  secp256k1_den_ne_zero_of_x_eq_div h hX

end Ecdlp.Curve
