import Mathlib

/-!
# Direct generic parity collision boundary

Elementary algebraic and arithmetic core for the adversarial-integration track
of `UNIFORM-ORIENTED-ROOT-CIRCUIT-056`.

This file does not formalize generic-group oracle machines, elliptic curves,
coordinate algorithms, secp256k1 encodings, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Distinct affine functions with different slopes collide at at most one
field element. -/
theorem affineCollision_atMostOne
    {K : Type*} [Field K]
    (a b c d k₁ k₂ : K)
    (hslope : a ≠ c)
    (h₁ : a * k₁ + b = c * k₁ + d)
    (h₂ : a * k₂ + b = c * k₂ + d) :
    k₁ = k₂ := by
  have e₁ : (a - c) * k₁ = d - b := by
    linear_combination h₁
  have e₂ : (a - c) * k₂ = d - b := by
    linear_combination h₂
  have hprod : (a - c) * (k₁ - k₂) = 0 := by
    rw [mul_sub, e₁, e₂, sub_self]
  have hcoeff : a - c ≠ 0 := sub_ne_zero.mpr hslope
  have hdiff : k₁ - k₂ = 0 :=
    (mul_eq_zero.mp hprod).resolve_left hcoeff
  exact sub_eq_zero.mp hdiff

/-- Pair-collision coverage of a balanced half-domain forces square-root total
label capacity. -/
theorem collisionCoverage_implies_square
    (half labels : ℕ)
    (hcover : 2 * half ≤ labels * (labels - 1)) :
    2 * half ≤ labels ^ 2 := by
  calc
    2 * half ≤ labels * (labels - 1) := hcover
    _ ≤ labels * labels :=
      Nat.mul_le_mul_left labels (Nat.sub_le labels 1)
    _ = labels ^ 2 := by simp [pow_two]

/-- With `stored` preprocessing labels and `online` query-dependent labels,
only pairs containing an online label can depend on the hidden scalar. If those
pairs cover a balanced half-domain, the total charged label count is still at
the square-root scale. -/
theorem preprocessingOnlineCoverage_implies_totalSquare
    (half stored online : ℕ)
    (hcover :
      2 * half ≤ 2 * stored * online + online * (online - 1)) :
    2 * half ≤ (stored + online) ^ 2 := by
  have hOnline : online * (online - 1) ≤ online * online :=
    Nat.mul_le_mul_left online (Nat.sub_le online 1)
  calc
    2 * half ≤ 2 * stored * online + online * (online - 1) := hcover
    _ ≤ 2 * stored * online + online * online :=
      Nat.add_le_add_left hOnline (2 * stored * online)
    _ ≤ stored * stored + (2 * stored * online + online * online) := by
      omega
    _ = (stored + online) ^ 2 := by ring

/-- Odd-order specialization. -/
theorem oddOrderCollisionCoverage_implies_square
    (n half labels : ℕ)
    (hn : n = 2 * half + 1)
    (hcover : 2 * half ≤ labels * (labels - 1)) :
    n - 1 ≤ labels ^ 2 := by
  subst n
  simpa using collisionCoverage_implies_square half labels hcover

/-- Public secp256k1 subgroup order. -/
def secp256k1Order : ℕ :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

/-- Candidate exact generic-label threshold. -/
def secp256k1GenericParityThreshold : ℕ := 2 ^ 128

/-- `2^128` has enough pair-collision capacity. -/
theorem secp256k1_threshold_sufficient :
    secp256k1Order - 1 ≤
      secp256k1GenericParityThreshold *
        (secp256k1GenericParityThreshold - 1) := by
  native_decide

/-- One fewer label has insufficient pair-collision capacity. -/
theorem secp256k1_previous_threshold_insufficient :
    (secp256k1GenericParityThreshold - 1) *
        (secp256k1GenericParityThreshold - 2) <
      secp256k1Order - 1 := by
  native_decide

end Ecdlp.ParityLift
