import Mathlib
import Ecdlp.Proved.PointEvaluation

/-!
# Weil layer B — evaluation compatibility (OPEN TARGET, one `sorry`)

Next rung after the promoted point-evaluation layer (`Ecdlp/Proved/PointEvaluation.lean`):

  `evalRatAt` **extends** `evalAt` — for a *regular* function `r ∈ F[E]`, its value as a rational
  function regular at `P` (image under the localization map, then `evalRatAt`) equals its direct
  value `evalAt h r`.

This is the correctness certificate for `evalRatAt` before it is used to evaluate the Miller
function `f_P`; it is self-contained (no divisor-support machinery).

## Status — math done, Lean plumbing open (kernel-checked findings)

Established on the warm toolchain (`lake env lean`), so these are facts, not guesses:

* The **statement elaborates** cleanly — all types line up, the `[IsPrime]` instance is accepted.
* The **mathematical crux is definitional**:
    `IsLocalRing.residue (Localization.AtPrime I) (algebraMap F[E] (Localization.AtPrime I) r)`
      `= algebraMap (F[E] ⧸ I) I.ResidueField (Ideal.Quotient.mk I r)`   (`I = XYIdeal W x (C y)`)
  holds by `rfl` — the residue of the localization at the point coincides with the quotient by the
  point's maximal ideal (confirmed: `exact?` closes it, and `... := rfl` type-checks).
* Given that, the goal reduces (mathematically) to
    `quotientXYIdealEquiv h ((ofBij).symm (residue …)) = quotientXYIdealEquiv h (mk r)`,
  and `(ofBij).symm (residue …) = mk r` by `symm_apply_eq` + `ofBijective_apply` + the crux.

## The remaining obstacle (why this is parked, not promoted)

`residueFieldEquiv` (in `PointEvaluation.lean`) is **tactic-defined** (`by … exact …`). Two blind
finishes both fail on the *coercion / defeq* layer, not the math:

1. `congrArg _ (RingEquiv.symm_apply_apply _ _)` forces an `isDefEq` through the tactic-defined
   equiv that does **not** terminate even at `maxHeartbeats 1000000`.
2. `congr 1` splits into an ill-typed function-equality side goal
   `((I.ResidueField →+* F) = (F[E] ⧸ I →+* F))`, because `RingEquiv.coe_toRingHom` does not fire
   here (Mathlib-version coercion normal form), so `RingEquiv.trans_apply` cannot rewrite
   `(E.symm.trans Q).toRingHom` into `Q ∘ E.symm`.

**Likely fix** (for an interactive session, or a follow-up): restate `residueFieldEquiv` in
`PointEvaluation.lean` as a **term-mode** def (so its defeq is cheap/transparent), then the
`symm_apply_apply` finish should close in a few heartbeats; or add a `@[simp] residueFieldEquiv_apply`
lemma giving `residueFieldEquiv h z = quotientXYIdealEquiv h ((ofBij).symm z)` and rewrite with it.

Open stem lives under `Targets/` (gate-excluded); promote to `Proved/` only once the kernel accepts
it with no `sorry`.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- `evalRatAt` extends `evalAt`: evaluating the image of a regular function `r` in the local ring
`F[E]_P` equals evaluating `r` directly at `P`. (OPEN — see the module docstring for the
kernel-checked reduction and the remaining coercion/defeq obstacle.) -/
theorem evalRatAt_algebraMap {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] (r : W.CoordinateRing) :
    evalRatAt h (algebraMap W.CoordinateRing
        (Localization.AtPrime (XYIdeal W x (C y))) r) = evalAt h r := by
  sorry

end Ecdlp.Weil
