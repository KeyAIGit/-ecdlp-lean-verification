/-
# The complementary doubling factor `ψ₂ₘ/ψₘ`, expanded, uniformly in `m`

`Ecdlp/Proved/DivisionPolynomialDoubling.lean` records the doubling *factorisation*
`ψ₂ₖ = ψₖ · complEDS₂ …`. This module records the complementary *expansion*: multiplying that
factor by `ψ₂` gives a four-term expression in the neighbours `ψ_{m-2}, ψ_{m-1}, ψ_{m+1},
ψ_{m+2}`, uniformly in `m : ℤ`, over an arbitrary Weierstrass curve `W` over any `CommRing R`.

It is a direct specialisation of Mathlib's scalar-EDS lemma `complEDS₂_mul_b`
(`Mathlib/NumberTheory/EllipticDivisibilitySequence.lean:329`), available because `W.ψ` is
definitionally `normEDS W.ψ₂ (C W.Ψ₃) (C W.preΨ₄)`. Mathlib's `WeierstrassCurve` layer has
`ψ_even` and `ψ_odd` but **no** `complEDS₂` lemma at all — grep
`Mathlib/AlgebraicGeometry/EllipticCurve/` for `complEDS` and it is empty — so this is the
`W`-level statement of a fact that exists only in scalar form upstream.

**What this module deliberately does NOT contain.** An earlier version of this file also stated
`ψ₂ₘ · ψ₂ = ψ_{m-1}² ψ_m ψ_{m+2} − ψ_{m-2} ψ_m ψ_{m+1}²` under the name `ψ_two_mul_mul_ψ₂`.
That statement is **character-for-character Mathlib's `WeierstrassCurve.ψ_even`**
(`DivisionPolynomial/Basic.lean:430`) — both are `normEDS_even ..` at the same arguments — and
this repository already used `ψ_even` in two places
(`Ecdlp/Proved/DivisionPolynomialPointDoubling.lean`, which gives its point-level form, and
`Ecdlp/Proved/OmegaRecurrenceAnchors.lean`, which applies it at `m = 3`). It was a duplicate
under a new name and has been removed. Use `W.ψ_even` directly.

**Why the surviving statement is worth naming.** `complEDS₂ (m) · ψ₂` is exactly the numerator
of Silverman's `ωₘ` up to the ordering of factors — see
`Ecdlp/Proved/OmegaNumeratorUniform.lean`, which is built on this lemma and which identifies the
per-index anchors of `OmegaRecurrenceAnchors.lean` as instances of one uniform equation.

**Honest scope.** This is a polynomial identity in `R[X][Y]`. It defines no `ωₙ` — the bivariate
`y`-coordinate division polynomials remain Mathlib's open `TODO`, since the `÷2`
well-definedness step is untouched here. It states nothing about `Point`-level `[n]`-arithmetic,
nothing about torsion, and nothing about secp256k1 in particular. It is substrate for the `ω`
construction, not a step past it.
-/
import Mathlib

namespace Ecdlp.Curve

open Polynomial

variable {R : Type*} [CommRing R] (W : WeierstrassCurve R)

/-- The complementary doubling factor `ψ₂ₘ/ψₘ`, expanded: multiplying it by `ψ₂` gives a
four-term expression in the neighbours `ψ_{m-2}, ψ_{m-1}, ψ_{m+1}, ψ_{m+2}`.

Mathlib states this only in scalar-EDS form (`complEDS₂_mul_b`); there is no `complEDS₂` lemma
anywhere under `Mathlib/AlgebraicGeometry/EllipticCurve/`. -/
theorem complEDS₂_mul_ψ₂ (m : ℤ) :
    complEDS₂ W.ψ₂ (C W.Ψ₃) (C W.preΨ₄) m * W.ψ₂ =
      W.ψ (m - 1) ^ 2 * W.ψ (m + 2) - W.ψ (m - 2) * W.ψ (m + 1) ^ 2 :=
  complEDS₂_mul_b W.ψ₂ (C W.Ψ₃) (C W.preΨ₄) m

end Ecdlp.Curve
