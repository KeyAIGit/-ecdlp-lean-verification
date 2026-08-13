import Mathlib

/-!
# Mixed-weight GLV resolvent algebra

This file formalizes the elementary C3 Fourier product and odd-part
factorization used by `MIXED-WEIGHT-GLV-RESOLVENT-C042`.

It does not formalize elliptic curves, finite-field characters, the explicit
R4/S5 formulas, carry correctness, exhaustive search, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Product of the three C3 Fourier components of a circulant row. -/
theorem cubicDftProduct
    {K : Type*} [CommRing K]
    (beta a₀ a₁ a₂ : K)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    (a₀ + a₁ + a₂)
        * (a₀ + beta * a₁ + beta ^ 2 * a₂)
        * (a₀ + beta ^ 2 * a₁ + beta * a₂)
      = a₀ ^ 3 + a₁ ^ 3 + a₂ ^ 3 - 3 * a₀ * a₁ * a₂ := by
  calc
    (a₀ + a₁ + a₂)
          * (a₀ + beta * a₁ + beta ^ 2 * a₂)
          * (a₀ + beta ^ 2 * a₁ + beta * a₂)
        = a₀ ^ 3 + a₁ ^ 3 + a₂ ^ 3 - 3 * a₀ * a₁ * a₂
          + (a₀ + a₁ + a₂) * (beta ^ 2 + beta + 1)
            * (a₀ * a₁ + a₀ * a₂ + a₁ ^ 2 * beta - a₁ ^ 2
              + a₁ * beta ^ 2 * a₂ - a₁ * beta * a₂ + a₁ * a₂
              + beta * a₂ ^ 2 - a₂ ^ 2) := by ring
    _ = a₀ ^ 3 + a₁ ^ 3 + a₂ ^ 3 - 3 * a₀ * a₁ * a₂ := by
      rw [hbeta]
      ring

/-- The difference between the two conjugate products is always divisible by
`W`; this is the abstract anti-characteristic factorization behind the explicit
translated determinant formula. -/
theorem conjugateLinearProduct_odd
    {K : Type*} [CommRing K]
    (l a₀ a₁ c₀ c₁ W : K) :
    (l - 2 * W) * (a₀ + a₁ * W) * (c₀ + c₁ * W)
      - (l + 2 * W) * (a₀ - a₁ * W) * (c₀ - c₁ * W)
      = -2 * W *
          (2 * W ^ 2 * a₁ * c₁ + 2 * a₀ * c₀
            - a₀ * c₁ * l - a₁ * c₀ * l) := by
  ring

end Ecdlp.ParityLift
