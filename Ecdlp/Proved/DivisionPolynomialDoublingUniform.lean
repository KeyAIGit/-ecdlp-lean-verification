/-
# Uniform doubling identity for `ψ₂ₙ` (the ω-free `y`-conjunct, all `n` at once)

`Ecdlp/Proved/DivisionPolynomialDoubling.lean` records the doubling *factorisation*
`ψ₂ₖ = ψₖ · complEDS₂ …`. This module records the complementary *expansion*: the closed
form of `ψ₂ₘ · ψ₂` in terms of five neighbouring division polynomials, uniformly in
`m : ℤ`, over an arbitrary Weierstrass curve `W` over any `CommRing R`:

* `complEDS₂_mul_ψ₂` — the complementary factor, expanded,
* `ψ_two_mul_mul_ψ₂` — the doubling identity itself.

Both are direct specialisations of Mathlib's scalar-EDS lemmas `complEDS₂_mul_b` and
`normEDS_even` (`Mathlib/NumberTheory/EllipticDivisibilitySequence.lean`), available
because `W.ψ` is definitionally `normEDS W.ψ₂ (C W.Ψ₃) (C W.preΨ₄)`. Neither lemma was
previously used anywhere in this repository.

**Why it is worth naming.** The right-hand side of `ψ_two_mul_mul_ψ₂` is the shape the
`ω`-free `y`-conjunct of the N7 uniform carrier takes. The existing anchors
`secp256k1_omega_recurrence_{two,three,four}` (`Ecdlp/Proved/OmegaRecurrenceAnchors.lean`)
each establish one index by hand; this statement covers every index simultaneously, and
does so curve-generically rather than for secp256k1 only.

**Honest scope.** This is a polynomial identity in `R[X][Y]`. It defines no `ωₙ` — the
bivariate `y`-coordinate division polynomials remain Mathlib's open `TODO`, since the
`÷2` well-definedness step is untouched here. It states nothing about `Point`-level
`[n]`-arithmetic, nothing about torsion, and nothing about secp256k1 in particular. It is
substrate for the `ω` construction, not a step past it.
-/
import Mathlib

namespace Ecdlp.Curve

open Polynomial

variable {R : Type*} [CommRing R] (W : WeierstrassCurve R)

/-- The complementary doubling factor `ψ₂ₘ/ψₘ`, expanded: multiplying it by `ψ₂` gives a
four-term expression in the neighbours `ψ_{m-2}, ψ_{m-1}, ψ_{m+1}, ψ_{m+2}`. -/
theorem complEDS₂_mul_ψ₂ (m : ℤ) :
    complEDS₂ W.ψ₂ (C W.Ψ₃) (C W.preΨ₄) m * W.ψ₂ =
      W.ψ (m - 1) ^ 2 * W.ψ (m + 2) - W.ψ (m - 2) * W.ψ (m + 1) ^ 2 :=
  complEDS₂_mul_b W.ψ₂ (C W.Ψ₃) (C W.preΨ₄) m

/-- **Uniform doubling identity.** For every `m : ℤ`,
`ψ₂ₘ · ψ₂ = ψ_{m-1}² ψ_m ψ_{m+2} − ψ_{m-2} ψ_m ψ_{m+1}²`.

This is the single statement behind the per-index `ω`-recurrence anchors: it holds for all
`m` at once, and over an arbitrary curve. -/
theorem ψ_two_mul_mul_ψ₂ (m : ℤ) :
    W.ψ (2 * m) * W.ψ₂ =
      W.ψ (m - 1) ^ 2 * W.ψ m * W.ψ (m + 2) -
        W.ψ (m - 2) * W.ψ m * W.ψ (m + 1) ^ 2 :=
  normEDS_even W.ψ₂ (C W.Ψ₃) (C W.preΨ₄) m

end Ecdlp.Curve
