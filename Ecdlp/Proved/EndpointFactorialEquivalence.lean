import Mathlib

/-!
# Endpoint segment and cyclic-factorial equivalence

This file formalizes the elementary multiplicative algebra behind
`UORC056-ENDPOINT-FACTORIAL-EQUIVALENCE-B14`.

It does not formalize elliptic curves, Miller functions, Hilbert 90,
secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- The endpoint ratio attached to a nonzero multiplicative potential. -/
def endpointRatio
    {X K : Type*} [CommGroup K]
    (potential : X → K) (source target : X) : K :=
  potential target / potential source

/-- Endpoint ratios are one on the diagonal. -/
theorem endpointRatio_refl
    {X K : Type*} [CommGroup K]
    (potential : X → K) (point : X) :
    endpointRatio potential point point = 1 := by
  simp [endpointRatio]

/-- Endpoint ratios satisfy the pair-groupoid composition law. -/
theorem endpointRatio_compose
    {X K : Type*} [CommGroup K]
    (potential : X → K) (first middle last : X) :
    endpointRatio potential first middle
      * endpointRatio potential middle last
      = endpointRatio potential first last := by
  simp [endpointRatio, div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm]

/-- A composable endpoint function is recovered from one anchor row. -/
theorem endpoint_eq_anchor_ratio
    {X K : Type*} [CommGroup K]
    (endpoint : X → X → K)
    (anchor source target : X)
    (hcompose :
      ∀ first middle last,
        endpoint first middle * endpoint middle last
          = endpoint first last) :
    endpoint source target
      = endpoint anchor target / endpoint anchor source := by
  calc
    endpoint source target
        = (endpoint anchor source)⁻¹
            * (endpoint anchor source * endpoint source target) := by
              simp
    _ = (endpoint anchor source)⁻¹ * endpoint anchor target := by
          rw [hcompose anchor source target]
    _ = endpoint anchor target / endpoint anchor source := by
          simp [div_eq_mul_inv, mul_comm]

/-- Multiplying a potential by one global scalar leaves every endpoint ratio
unchanged. -/
theorem endpointRatio_constantGauge
    {X K : Type*} [CommGroup K]
    (potential : X → K) (constant : K) (source target : X) :
    endpointRatio (fun point => constant * potential point) source target
      = endpointRatio potential source target := by
  simp [endpointRatio, div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm]

/-- Any two-level product cover `m ≤ b*g`, charged by `b+g`, lies on the
square-root frontier. -/
theorem twoLevelProduct_squareBound
    (m b g : ℤ)
    (hcover : m ≤ b * g) :
    4 * m ≤ (b + g) ^ 2 := by
  nlinarith [sq_nonneg (b - g)]

end Ecdlp.ParityLift
