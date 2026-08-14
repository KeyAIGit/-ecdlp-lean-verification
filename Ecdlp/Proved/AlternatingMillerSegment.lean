import Mathlib

/-!
# Alternating Miller segment

This file formalizes the multiplicative algebra behind
`UORC056-ALTERNATING-MILLER-SEGMENT-B9`.

A segment ratio telescopes, adjacent segments compose, and the quotient of a
segment by its reflected partner is the corresponding norm ratio.

The file does not formalize Miller functions, elliptic curves, divisors,
secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Two adjacent multiplicative segment ratios telescope. -/
theorem segmentRatio_compose
    {K : Type*} [CommGroup K]
    (start middle finish : K) :
    (middle / start) * (finish / middle) = finish / start := by
  group

/-- The quotient of a segment and its reflected partner is the quotient of the
corresponding endpoint norms. -/
theorem segment_reflected_normQuotient
    {K : Type*} [CommGroup K]
    (start reflectedStart finish reflectedFinish : K) :
    (finish / start) / (reflectedStart / reflectedFinish)
      = (finish * reflectedFinish) / (start * reflectedStart) := by
  group

/-- A full closed segment has unit multiplicative ratio. -/
theorem closedSegment_ratio (value : α) [Group α] :
    value / value = 1 := by
  simp

end Ecdlp.ParityLift
