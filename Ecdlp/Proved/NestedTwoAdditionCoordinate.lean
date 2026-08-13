import Mathlib
import Ecdlp.Proved.SquareClassCircuitFrontier

/-!
# Nested two-addition coordinate boundary

This file formalizes the elementary algebraic collapse behind the rejection of
the naive same-feature GLV orbit product.  It does not formalize elliptic
curves, quadratic characters, the exhaustive toy screens, carry correctness,
or circuit complexity.
-/

namespace Ecdlp.ParityLift

/-- A binomial multiplied over the three weights of a nontrivial cubic orbit
collapses to one binomial in the cube. -/
theorem cubicOrbitBinomialProduct
    {K : Type*} [CommRing K]
    (beta u : K)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    (1 + u) * (1 + beta * u) * (1 + beta ^ 2 * u) = 1 + u ^ 3 := by
  calc
    (1 + u) * (1 + beta * u) * (1 + beta ^ 2 * u) =
        1 + u ^ 3 +
          (beta ^ 2 + beta + 1) *
            (u + beta * u ^ 2 + (beta - 1) * u ^ 3) := by ring
    _ = 1 + u ^ 3 := by rw [hbeta]; ring

/-- The cubic-orbit product has exactly the square class of the resulting
one-addition factor. -/
theorem cubicOrbitBinomialProduct_squareEquivalent
    {K : Type*} [CommRing K]
    (beta u : K)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    SquareEquivalent
      ((1 + u) * (1 + beta * u) * (1 + beta ^ 2 * u))
      (1 + u ^ 3) := by
  rw [cubicOrbitBinomialProduct beta u hbeta]
  exact squareEquivalent_refl _

/-- If the monomial has trivial cubic weight, the three equal orbit factors
also retain only the original binomial square class. -/
theorem repeatedBinomialCube_squareEquivalent
    {K : Type*} [CommRing K]
    (u : K) :
    SquareEquivalent ((1 + u) ^ 3) (1 + u) := by
  simpa using oddPower_squareEquivalent_self (1 + u) 1

/-- The `t=-1, epsilon=1` nested expression is just a trinomial before taking
square class. -/
theorem inverseNestedTrinomial
    {K : Type*} [Field K]
    (H M c : K)
    (hH : H ≠ 0) :
    H * (1 + c * M / H) = H + c * M := by
  field_simp [hH]

end Ecdlp.ParityLift
