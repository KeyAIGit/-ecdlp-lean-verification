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
  simp [localCocycle, div_eq_mul_inv]
  group

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
  dsimp [localCocycle] at h
  calc
    first (step point) / second (step point) =
        (first (step point) / first point) *
          (first point / second (step point)) := by group
    _ = (second (step point) / second point) *
          (first point / second (step point)) := by rw [h]
    _ = first point / second point := by group

end Ecdlp.ParityLift
