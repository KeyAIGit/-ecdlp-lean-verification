import Mathlib

/-!
# Relative EDS-residue gauge identities

This file records the arithmetic core of `RELATIVE-RESIDUE-GAUGE-001`.
It does not construct an EDS-residue oracle or make an asymptotic claim.

For a hidden integer index `k`, the rank-two elliptic-net transport from
`(G, [k]G)` at a fixed vector `(a,b)` involves the indices

* `a + b*k`,
* `k`, with exponent `b^2 - a*b`, and
* `k+1`, with exponent `a*b`.

The quadratic normalization defect is independent of `k`. Consequently a
quadratic rescaling of the underlying rank-one net cancels from the transport
identity up to a public constant depending only on `(a,b)`. This is the exact
algebra behind the fact that fixed rank-two net relations provide relative
residue labels but do not fix the remaining global sign gauge.
-/

namespace Ecdlp.ParityLift

/-- The rank-two elliptic-net transport has no hidden `k`-dependent quadratic
normalization defect. -/
theorem rankTwoNetQuadraticDefect (a b k : ℤ) :
    (a + b * k) ^ 2
        - (b ^ 2 - a * b) * k ^ 2
        - (a * b) * (k + 1) ^ 2
      = a * (a - b) := by
  ring

/-- Rearranged form: every `k`-dependent quadratic exponent in the transported
net is accounted for by the two source indices, leaving only a fixed constant. -/
theorem rankTwoNetQuadraticBalance (a b k : ℤ) :
    (a + b * k) ^ 2
      = (b ^ 2 - a * b) * k ^ 2
        + (a * b) * (k + 1) ^ 2
        + a * (a - b) := by
  ring

/-- Pairwise relative sign labels are invariant under one simultaneous global
sign flip. Thus a connected collection of such labels can determine a sign
assignment only up to the remaining global gauge unless an absolute anchor is
supplied. -/
theorem pairLabel_invariant_under_globalNegation
    {α : Type*} (ρ : α → ℤ) (u v : α) :
    (-ρ u) * (-ρ v) = ρ u * ρ v := by
  ring

end Ecdlp.ParityLift
