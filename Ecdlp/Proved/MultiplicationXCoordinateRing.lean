/-
# Coordinate-ring translation for the multiplication-by-`n` x-coordinate

This is the first foundational brick of the general-`n` multiplication-formula
build (the "N7-uniform" wall, `BARRIERS.md §B3`). It records — over an arbitrary
Weierstrass curve — the purely-algebraic identity in the affine coordinate ring
`W.CoordinateRing` that links the *bivariate* division polynomials `W.φ n`,
`W.ψ n` (which actually compute `x([n]•P)` on points) to the *univariate*
polynomials `W.Φ n`, `W.ΨSq n` (whose degrees/leading-coefficients are the
computable data Mathlib provides in `DivisionPolynomial/Degree.lean`).

Concretely: in `W.CoordinateRing`, `mk W (W.ψ n) ^ 2 = mk W (C (W.ΨSq n))` and
hence `φₙ · ΨSqₙ = Φₙ · ψₙ²`. Both facts are two-step rewrites over Mathlib's own
`mk_ψ`, `mk_Ψ_sq`, `mk_φ` congruences.

**Honest scope.** This is *only* the coordinate-ring translation layer (node
"S1"/N7-substrate). It says nothing yet about `Point` arithmetic: the hard step
— that `x([n]•P) = φₙ(P)/ψₙ(P)²` as a map on the group `E(k)` — needs the
multiplication-by-`n` coordinate map, which is absent from Mathlib. This brick is
the algebra that step will consume, not that step itself.
-/
import Mathlib

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {R : Type*} [CommRing R] (W : WeierstrassCurve R)

/-- In the affine coordinate ring, the square of the bivariate division polynomial
`ψₙ` collapses to the (constant-embedded) univariate `ΨSqₙ`. -/
theorem mk_ψ_sq (n : ℤ) : mk W (W.ψ n) ^ 2 = mk W (C (W.ΨSq n)) := by
  rw [mk_ψ, mk_Ψ_sq]

/-- The coordinate-ring cross-multiplied form of `x([n]•P) = Φₙ/ΨSqₙ`:
`φₙ · ΨSqₙ = Φₙ · ψₙ²` in `W.CoordinateRing`. -/
theorem mk_φ_mul_ΨSq (n : ℤ) :
    mk W (W.φ n) * mk W (C (W.ΨSq n)) = mk W (C (W.Φ n)) * mk W (W.ψ n) ^ 2 := by
  rw [mk_φ, mk_ψ_sq W]

end Ecdlp.Curve
