import Mathlib

/-!
# Normalized period blackbox

This file formalizes the elementary algebraic core of
`NORMALIZED-PERIOD-BLACKBOX-032`.

For the six characteristic roots

`r₁, r₂, r₃, r₁⁻¹, r₂⁻¹, r₃⁻¹`, with `r₁*r₂*r₃ = 1`, the normalized
Gaussian-period resolvent has the reciprocal degree-six characteristic
polynomial

`(X^3-sX^2+tX-1)(X^3-tX^2+sX-1)`.

The second part records the arithmetic form of the extension-degree versus
state-rank tradeoff. It does not formalize finite fields, Frobenius orbits,
Gaussian periods, elliptic curves, or the bridge from a public point to the
normalized resolvent.
-/

namespace Ecdlp.ParityLift

/-- Expansion of the reciprocal pair of cubic characteristic factors. -/
theorem reciprocalCubic_product
    {K : Type*} [CommRing K]
    (x s t : K) :
    (x ^ 3 - s * x ^ 2 + t * x - 1) *
        (x ^ 3 - t * x ^ 2 + s * x - 1)
      = x ^ 6
        - (s + t) * x ^ 5
        + (s * t + s + t) * x ^ 4
        - (s ^ 2 + t ^ 2 + 2) * x ^ 3
        + (s * t + s + t) * x ^ 2
        - (s + t) * x
        + 1 := by
  ring

/-- If `d = g*m`, the extension degree dominates `g`, and a state rank
dominates the Frobenius orbit length `m`, then the base-field state size
`e*r` is at least `d`. -/
theorem extensionOrbit_product_lower_bound
    (d e g m r : ℕ)
    (hfactor : d = g * m)
    (hdegree : g ≤ e)
    (hrank : m ≤ r) :
    d ≤ e * r := by
  rw [hfactor]
  exact Nat.mul_le_mul hdegree hrank

/-- In the secp256k1 six-root linear-output case, the exact recurrence rank is
at least three times the Frobenius orbit length. The resulting base-field
coefficient/state product is at least `3*d`. -/
theorem extensionSixRoot_product_lower_bound
    (d e g m r : ℕ)
    (hfactor : d = g * m)
    (hdegree : g ≤ e)
    (hrank : 3 * m ≤ r) :
    3 * d ≤ e * r := by
  rw [hfactor]
  calc
    3 * (g * m) = g * (3 * m) := by ring
    _ ≤ e * r := Nat.mul_le_mul hdegree hrank

/-- A rank-six recurrence over an extension of degree `d/2` still occupies
`3*d` base-field words. -/
theorem rankSix_halfExtension_product
    (d e : ℕ)
    (hhalf : d = 2 * e) :
    e * 6 = 3 * d := by
  omega

end Ecdlp.ParityLift
