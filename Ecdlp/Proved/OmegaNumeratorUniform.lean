/-
# The ω-recurrence numerator, uniformly in `n`

`Ecdlp/Proved/OmegaRecurrenceAnchors.lean` validates Silverman's `y`-coordinate division
polynomial `ωₙ = (ψ_{n+2}ψ_{n-1}² − ψ_{n-2}ψ_{n+1}²)/(4y)` against the independently
kernel-verified group-law values at `n = 2, 3, 4`, one index at a time, each by an
explicit rewrite chain ending in `ring`. Mathlib has no `ωₙ`; the numerator is all that is
available, so pinning it down uniformly is the substrate step.

This module names the numerator **once, for every `n : ℤ` at once**:

* `psi_omega_numerator` (curve-generic, `CommRing R`) —
  `ψ_{n+2}·ψ_{n-1}² − ψ_{n-2}·ψ_{n+1}² = complEDS₂(n) · ψ₂`.

That is: the ω numerator is not a fresh object per index, it is Mathlib's *2-complement
sequence* `complEDS₂` (`Mathlib/NumberTheory/EllipticDivisibilitySequence.lean`) times
`ψ₂`. It follows immediately from `complEDS₂_mul_ψ₂` in
`Ecdlp/Proved/DivisionPolynomialDoublingUniform.lean`, which is itself Mathlib's
`complEDS₂_mul_b` at `(b, c, d) = (ψ₂, C Ψ₃, C preΨ₄)`.

Two consequences are recorded for secp256k1:

* `secp256k1_omega_numerator_evalEval` — the point-level form. Since `ψ₂` evaluates to
  `2y` on secp256k1 (`secp256k1_psi2_evalEval`; `a₁ = a₃ = 0`), the numerator at any
  affine `(x, y)` is `complEDS₂(n)(x, y) · 2y`, **with no curve hypothesis** — the identity
  is one between polynomials, so it holds at every pair `(x, y)`, on the curve or off it.
  Consequently, wherever `2y ≠ 0`, `ωₙ = complEDS₂(n)/2` — the division by `4y` in
  Silverman's formula is a division by `2·ψ₂`, and the `y`-dependence of `ωₙ` is entirely
  the `y`-dependence of `complEDS₂(n)`.

* `secp256k1_omega_recurrence_two_of_uniform` — the `n = 2` anchor, **re-derived from the
  uniform statement** rather than from the group law. Its proof is `complEDS₂_two`
  (`complEDS₂(2) = d = C preΨ₄`) plus `secp256k1_preΨ₄_eval`, so it exhibits
  `ω₂ = preΨ₄/2 = x⁶+140x³−392` as an instance rather than a coincidence. The
  group-law-derived `secp256k1_omega_recurrence_two` is left untouched: the two proofs are
  independent routes to the same equation, and that is exactly their value as a
  cross-check.

**Honest scope.** This defines no `ωₙ`. Silverman's `ωₙ` is the quotient of the numerator
by `4y`, and the `÷ 4y` well-definedness step — the reason Mathlib's bivariate `y`-division
polynomials are still an open `TODO` — is untouched here; nothing below divides by
anything. Nor is anything asserted about `Point`-level `[n]`-arithmetic, about torsion, or
about `y([n]•P)`. The content is exactly: *the object the anchors were validating against
is `complEDS₂ · ψ₂`, uniformly, over any curve.* The `n = 3, 4` anchors are not re-derived
here — they would need `complEDS₂_three`/`complEDS₂_four` unfolded through `preNormEDS 5`,
which is a longer computation and buys no new structure.
-/
import Mathlib
import Ecdlp.Proved.DivisionPolynomialDoublingUniform
import Ecdlp.Proved.FiveTorsionBridge

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable {R : Type*} [CommRing R] (W : WeierstrassCurve R)

/-- **The ω-recurrence numerator, uniformly in `n`.** For every `n : ℤ`, over an arbitrary
Weierstrass curve, the numerator of Silverman's `ωₙ` is Mathlib's 2-complement sequence
`complEDS₂` at `n`, times `ψ₂`:

`ψ_{n+2}·ψ_{n-1}² − ψ_{n-2}·ψ_{n+1}² = complEDS₂ ψ₂ (C Ψ₃) (C preΨ₄) n · ψ₂`.

Every per-index anchor in `OmegaRecurrenceAnchors.lean` is an instance of this one
equation. -/
theorem psi_omega_numerator (n : ℤ) :
    W.ψ (n + 2) * W.ψ (n - 1) ^ 2 - W.ψ (n - 2) * W.ψ (n + 1) ^ 2
      = complEDS₂ W.ψ₂ (C W.Ψ₃) (C W.preΨ₄) n * W.ψ₂ := by
  rw [complEDS₂_mul_ψ₂]
  ring

/-- **Point-level form for secp256k1, uniformly in `n`.** At any pair `(x, y)` — no curve
hypothesis, since this is an identity of polynomials — the ω numerator equals
`complEDS₂(n)(x, y) · 2y`. Wherever `2y ≠ 0` this exhibits `ωₙ = complEDS₂(n)/2`. -/
theorem secp256k1_omega_numerator_evalEval (n : ℤ) (x y : ZMod Secp256k1.p) :
    (secp256k1.ψ (n + 2)).evalEval x y * (secp256k1.ψ (n - 1)).evalEval x y ^ 2
      - (secp256k1.ψ (n - 2)).evalEval x y * (secp256k1.ψ (n + 1)).evalEval x y ^ 2
      = (complEDS₂ secp256k1.ψ₂ (C secp256k1.Ψ₃) (C secp256k1.preΨ₄) n).evalEval x y
          * (2 * y) := by
  have h := congrArg (Polynomial.evalEval x y) (psi_omega_numerator secp256k1 n)
  simp only [evalEval_sub, evalEval_mul, evalEval_pow] at h
  rw [secp256k1_psi2_evalEval] at h
  exact h

/-- **The `n = 2` anchor, re-derived from the uniform statement.** `complEDS₂(2) = preΨ₄`
and `preΨ₄(x) = 2x⁶ + 280x³ − 784`, so the numerator is `4y·(x⁶+140x³−392)`: the value
`ω₂ = x⁶+140x³−392` that `MultiplicationYFormula` obtains from the group law appears here
as `preΨ₄/2`, an instance of `psi_omega_numerator`.

`secp256k1_omega_recurrence_two` in `OmegaRecurrenceAnchors.lean` states the same equation
and is deliberately kept: it goes through the group-law-derived `ψ₄`/`ψ₃` values instead,
so the two together are an independent cross-check, not a duplication. -/
theorem secp256k1_omega_recurrence_two_of_uniform (x y : ZMod Secp256k1.p) :
    (secp256k1.ψ 4).evalEval x y * (secp256k1.ψ 1).evalEval x y ^ 2
      - (secp256k1.ψ 0).evalEval x y * (secp256k1.ψ 3).evalEval x y ^ 2
      = 4 * y * (x ^ 6 + 140 * x ^ 3 - 392) := by
  have h := secp256k1_omega_numerator_evalEval 2 x y
  rw [show (2 + 2 : ℤ) = 4 by norm_num, show (2 - 1 : ℤ) = 1 by norm_num,
      show (2 - 2 : ℤ) = 0 by norm_num, show (2 + 1 : ℤ) = 3 by norm_num,
      complEDS₂_two, evalEval_C, secp256k1_preΨ₄_eval] at h
  rw [h]
  ring

end Ecdlp.Curve
