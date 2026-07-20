/-
# Division-polynomial doubling: `ψₙ ∣ ψ₂ₙ` (the ω prerequisite, N7-uniform S2 brick)

Mathlib's division-polynomial file states, as the **explicit first step** toward the
(still-`TODO`) bivariate `y`-coordinate division polynomials `ωₙ`, that

> it can be shown by induction that `ψₙ` always divides `ψ₂ₙ` in `R[X, Y]`, so that
> `ψ₂ₙ / ψₙ` is always well-defined as a polynomial

(`Mathlib/AlgebraicGeometry/EllipticCurve/DivisionPolynomial/Basic.lean`, module
docstring; `ωₙ := (ψ₂ₙ/ψₙ − ψₙ·(a₁φₙ + a₃ψₙ²))/2`). This module discharges that
prerequisite at the bivariate `ψ`-level, over an **arbitrary** Weierstrass curve `W`
over any `CommRing R`, for all `k : ℤ`:

* `ψ_two_mul`: `ψ₂ₖ = ψₖ · complEDS₂ …` — the explicit complementary factor `ψ₂ₖ/ψₖ`,
* `ψ_dvd_ψ_two_mul`: `ψₖ ∣ ψ₂ₖ`.

Because Mathlib now carries the scalar EDS 2-complement `complEDS₂` (with
`normEDS_mul_complEDS₂` / `normEDS_dvd_normEDS_two_mul`) and `W.ψ` is definitionally
`normEDS W.ψ₂ (C W.Ψ₃) (C W.preΨ₄)`, the "induction" the docstring anticipated is now a
direct specialization — no new recursion needed.

**Honest scope.** This is the `ψₙ ∣ ψ₂ₙ` prerequisite only. The bivariate `ωₙ` is **not**
defined here (that needs the further `÷2` well-definedness step, Mathlib's open `TODO`),
and nothing about `Point`-level `[n]`-arithmetic is claimed. This is the S2 substrate the
`ω` construction — and, past it, the group-law coordinate map (S3) — will consume.
-/
import Mathlib

namespace Ecdlp.Curve

open Polynomial

variable {R : Type*} [CommRing R] (W : WeierstrassCurve R)

/-- The doubling factorisation of the bivariate `n`-division polynomial: `ψ₂ₖ = ψₖ · (ψ₂ₖ/ψₖ)`,
with the complementary factor given explicitly by the scalar EDS 2-complement `complEDS₂`
applied to `W`'s normalised-EDS parameters `(ψ₂, C Ψ₃, C preΨ₄)`. -/
theorem ψ_two_mul (k : ℤ) :
    W.ψ (2 * k) = W.ψ k * complEDS₂ W.ψ₂ (C W.Ψ₃) (C W.preΨ₄) k :=
  (normEDS_mul_complEDS₂ W.ψ₂ (C W.Ψ₃) (C W.preΨ₄) k).symm

/-- `ψₖ` divides `ψ₂ₖ` in `R[X][Y]` — the Mathlib-`TODO` `ω` prerequisite, so that `ψ₂ₖ/ψₖ`
is a genuine polynomial. -/
theorem ψ_dvd_ψ_two_mul (k : ℤ) : W.ψ k ∣ W.ψ (2 * k) :=
  normEDS_dvd_normEDS_two_mul W.ψ₂ (C W.Ψ₃) (C W.preΨ₄) k

end Ecdlp.Curve
