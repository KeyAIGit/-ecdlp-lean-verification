import Mathlib

/-!
# Hilbert-90 displacement boundary

This file formalizes elementary algebra behind the statement that a first-order
cyclic multiplicative recurrence is universal for nonzero projective vectors.

It does not formalize elliptic curves, Miller functions, Berlekamp-Massey,
quotient fields, secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Local multiplicative cocycle attached to a nonzero potential. -/
def localCocycle
    {X K : Type*} [CommGroup K]
    (potential : X → K) (step : X → X) (point : X) : K :=
  potential (step point) / potential point

/-- Every nonzero potential satisfies the induced first-order recurrence. -/
theorem localCocycle_recurrence
    {X K : Type*} [CommGroup K]
    (potential : X → K) (step : X → X) (point : X) :
    potential (step point) =
      localCocycle potential step point * potential point := by
  simp [localCocycle]

/-- Multiplying the potential by a global nonzero scalar leaves the cocycle
unchanged. -/
theorem localCocycle_constantGauge
    {X K : Type*} [CommGroup K]
    (potential : X → K) (step : X → X) (constant : K) (point : X) :
    localCocycle (fun x => constant * potential x) step point =
      localCocycle potential step point := by
  simp only [localCocycle, div_eq_mul_inv, mul_inv_rev]
  calc
    (constant * potential (step point)) *
        (potential point)⁻¹ * constant⁻¹ =
      (constant * constant⁻¹) *
        (potential (step point) * (potential point)⁻¹) := by
          ac_rfl
    _ = potential (step point) * (potential point)⁻¹ := by simp

/-- Equal local cocycles imply that the pointwise ratio is invariant under the
step map. -/
theorem equalCocycles_ratioInvariant
    {X K : Type*} [CommGroup K]
    (first second : X → K) (step : X → X)
    (point : X)
    (h : localCocycle first step point =
      localCocycle second step point) :
    first (step point) / second (step point) =
      first point / second point := by
  simp only [localCocycle, div_eq_mul_inv] at h ⊢
  calc
    first (step point) * (second (step point))⁻¹ =
      (first (step point) * (first point)⁻¹) *
        (first point * (second (step point))⁻¹) := by
          calc
            first (step point) * (second (step point))⁻¹ =
              (first (step point) * (second (step point))⁻¹) * 1 := by simp
            _ = (first (step point) * (second (step point))⁻¹) *
                ((first point)⁻¹ * first point) := by simp
            _ = (first (step point) * (first point)⁻¹) *
                (first point * (second (step point))⁻¹) := by ac_rfl
    _ = (second (step point) * (second point)⁻¹) *
        (first point * (second (step point))⁻¹) := by rw [h]
    _ = first point * (second point)⁻¹ := by
      calc
        (second (step point) * (second point)⁻¹) *
            (first point * (second (step point))⁻¹) =
          (second (step point) * (second (step point))⁻¹) *
            (first point * (second point)⁻¹) := by ac_rfl
        _ = first point * (second point)⁻¹ := by simp

end Ecdlp.ParityLift
