import Mathlib

/-!
# Hilbert-90 displacement boundary

This file formalizes the elementary multiplicative algebra behind
`UORC056-HILBERT90-DISPLACEMENT-BOUNDARY-B16`.

Every nonzero potential admits a first-order local cocycle. Hence the existence
of a sparse recurrence does not by itself restrict or compress the global
projective potential. Equal cocycles determine potentials only up to an
invariant ratio.

The file does not formalize elliptic curves, Miller functions, quotient fields,
Berlekamp-Massey, secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- The local multiplicative cocycle of a nonzero potential along one step. -/
def localCocycle
    {X K : Type*} [CommGroup K]
    (potential : X → K) (step : X → X) (point : X) : K :=
  potential (step point) / potential point

/-- Every potential satisfies its defining first-order recurrence. -/
theorem localCocycle_recurrence
    {X K : Type*} [CommGroup K]
    (potential : X → K) (step : X → X) (point : X) :
    localCocycle potential step point * potential point
      = potential (step point) := by
  simp [localCocycle]

/-- Thus every nonzero projective potential admits some first-order cocycle. -/
theorem everyPotential_has_firstOrderCocycle
    {X K : Type*} [CommGroup K]
    (potential : X → K) (step : X → X) :
    ∃ cocycle : X → K,
      ∀ point,
        cocycle point * potential point = potential (step point) := by
  refine ⟨localCocycle potential step, ?_⟩
  intro point
  exact localCocycle_recurrence potential step point

/-- Multiplying a potential by one global scalar leaves its local cocycle
unchanged. -/
theorem localCocycle_constantGauge
    {X K : Type*} [CommGroup K]
    (potential : X → K) (step : X → X) (constant : K) (point : X) :
    localCocycle (fun x => constant * potential x) step point
      = localCocycle potential step point := by
  simp only [localCocycle, div_eq_mul_inv, mul_inv_rev]
  calc
    (constant * potential (step point))
        * ((potential point)⁻¹ * constant⁻¹)
        = (constant * constant⁻¹)
            * (potential (step point) * (potential point)⁻¹) := by
              ac_rfl
    _ = potential (step point) * (potential point)⁻¹ := by
          simp

/-- Potentials with the same cocycle have a step-invariant pointwise ratio. -/
theorem equalCocycles_ratioInvariant
    {X K : Type*} [CommGroup K]
    (first second : X → K) (step : X → X) (point : X)
    (h : localCocycle first step point = localCocycle second step point) :
    first (step point) / second (step point)
      = first point / second point := by
  have hfirst := localCocycle_recurrence first step point
  have hsecond := localCocycle_recurrence second step point
  calc
    first (step point) / second (step point)
        = (localCocycle first step point * first point)
            / (localCocycle second step point * second point) := by
              rw [hfirst, hsecond]
    _ = (localCocycle second step point * first point)
            / (localCocycle second step point * second point) := by
          rw [h]
    _ = first point / second point := by
          simp only [div_eq_mul_inv, mul_inv_rev]
          calc
            (localCocycle second step point * first point)
                * ((second point)⁻¹
                    * (localCocycle second step point)⁻¹)
                = (localCocycle second step point
                    * (localCocycle second step point)⁻¹)
                    * (first point * (second point)⁻¹) := by
                      ac_rfl
            _ = first point * (second point)⁻¹ := by
                  simp

end Ecdlp.ParityLift
