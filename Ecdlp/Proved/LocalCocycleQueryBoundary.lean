import Mathlib

/-!
# Local-cocycle query boundary

This file formalizes the elementary multiplicative gauge algebra behind
`UORC056-LOCAL-COCYCLE-QUERY-BOUNDARY-B18`.

A gauge that is constant across one queried edge preserves that local cocycle.
Gauge one preserves the anchor, while a nontrivial target gauge changes the
target value.

The file does not formalize graph connectivity, query complexity, elliptic
curves, Miller functions, secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Pointwise multiplication of a potential by a multiplicative gauge. -/
def gaugePotential
    {X K : Type*} [CommGroup K]
    (gauge potential : X → K) (point : X) : K :=
  gauge point * potential point

/-- Local multiplicative edge attached to a potential. -/
def edgeCocycle
    {X K : Type*} [CommGroup K]
    (potential : X → K) (step : X → X) (point : X) : K :=
  potential (step point) / potential point

/-- A gauge constant across one queried edge preserves that edge value. -/
theorem gauge_preservesQueriedEdge
    {X K : Type*} [CommGroup K]
    (gauge potential : X → K) (step : X → X) (point : X)
    (hconstant : gauge (step point) = gauge point) :
    edgeCocycle (gaugePotential gauge potential) step point
      = edgeCocycle potential step point := by
  simp only [edgeCocycle, gaugePotential, div_eq_mul_inv, mul_inv_rev]
  rw [hconstant]
  calc
    (gauge point * potential (step point))
        * ((potential point)⁻¹ * (gauge point)⁻¹)
        = (gauge point * (gauge point)⁻¹)
            * (potential (step point) * (potential point)⁻¹) := by
              ac_rfl
    _ = potential (step point) * (potential point)⁻¹ := by
          simp

/-- Gauge one leaves the anchor value unchanged. -/
theorem gauge_preservesAnchor
    {X K : Type*} [CommGroup K]
    (gauge potential : X → K) (anchor : X)
    (hanchor : gauge anchor = 1) :
    gaugePotential gauge potential anchor = potential anchor := by
  simp [gaugePotential, hanchor]

/-- A nontrivial target gauge changes the target value. -/
theorem nontrivialGauge_changesTarget
    {X K : Type*} [CommGroup K]
    (gauge potential : X → K) (target : X)
    (htarget : gauge target ≠ 1) :
    gaugePotential gauge potential target ≠ potential target := by
  intro heq
  have hscaled := congrArg (fun value => value * (potential target)⁻¹) heq
  have : gauge target = 1 := by
    simpa [gaugePotential, mul_assoc] using hscaled
  exact htarget this

end Ecdlp.ParityLift
