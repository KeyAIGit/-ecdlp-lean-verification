import Mathlib

/-!
# CM Weil trace compression

This file formalizes elementary algebraic identities used by
`CM-WEIL-TRACE-COMPRESSION-039`.

The selector-free quadratic-Weil contraction compresses abstractly to the
character of a hidden split-torus element `diag(k,k⁻¹)`.  The file records the
determinant square-class identity, the uniqueness ingredients for the
Frobenius-diagonal completion, normalization of a scaled character value, and
the fact that two distinct affine generic-group labels collide at at most one
hidden scalar.

It does not formalize finite Weil representations, Maslov indices, generic-group
probability spaces, complex multiplication, ray class fields, secp256k1
coordinates, or arithmetic-circuit lower bounds.
-/

namespace Ecdlp.ParityLift

/-- The determinant of `diag(k,k⁻¹) - I` is a square times `-k⁻¹`. -/
theorem splitTorus_det_sub_one
    {K : Type*} [Field K]
    (k : K) (hk : k ≠ 0) :
    (k - 1) * (k⁻¹ - 1) = -(k - 1) ^ 2 * k⁻¹ := by
  field_simp [hk]
  ring

/-- If a matrix commutes with a diagonal Frobenius operator with distinct
entries, both off-diagonal coefficients vanish. -/
theorem frobeniusCommuting_offDiagonal_zero
    {K : Type*} [Field K]
    (r b c : K)
    (hr : r ≠ 1)
    (hb : b * r = b)
    (hc : r * c = c) :
    b = 0 ∧ c = 0 := by
  constructor
  · have hproduct : b * (r - 1) = 0 := by
      calc
        b * (r - 1) = b * r - b := by ring
        _ = 0 := sub_eq_zero.mpr hb
    exact (mul_eq_zero.mp hproduct).resolve_right (sub_ne_zero.mpr hr)
  · have hproduct : (r - 1) * c = 0 := by
      calc
        (r - 1) * c = r * c - c := by ring
        _ = 0 := sub_eq_zero.mpr hc
    exact (mul_eq_zero.mp hproduct).resolve_left (sub_ne_zero.mpr hr)

/-- Once the primal eigenvalue and determinant one are fixed, the dual
eigenvalue is uniquely the inverse. -/
theorem uniqueSplitTorusDiagonal
    {K : Type*} [Field K]
    (a d k : K)
    (hk : k ≠ 0)
    (ha : a = k)
    (hdet : a * d = 1) :
    d = k⁻¹ := by
  subst a
  apply (mul_left_cancel₀ hk)
  rw [hdet]
  simp [hk]

/-- Two affine labels with different slopes can collide at at most one hidden
scalar. -/
theorem affineCollision_atMostOne
    {K : Type*} [Field K]
    (a₁ a₂ b₁ b₂ x y : K)
    (ha : a₁ ≠ a₂)
    (hx : a₁ * x + b₁ = a₂ * x + b₂)
    (hy : a₁ * y + b₁ = a₂ * y + b₂) :
    x = y := by
  have hslope : a₁ - a₂ ≠ 0 := sub_ne_zero.mpr ha
  have hproduct : (a₁ - a₂) * (x - y) = 0 := by
    calc
      (a₁ - a₂) * (x - y) =
          (a₁ * x + b₁ - (a₂ * x + b₂)) -
          (a₁ * y + b₁ - (a₂ * y + b₂)) := by ring
      _ = 0 := by rw [hx, hy]; ring
  have hxy : x - y = 0 := (mul_eq_zero.mp hproduct).resolve_left hslope
  exact sub_eq_zero.mp hxy

/-- Normalizing a nonzero scaled trace or contraction recovers its character
factor. -/
theorem normalizedTraceCompression_recoversCharacter
    {K : Type*} [Field K]
    (compressed scale character : K)
    (hscale : scale ≠ 0)
    (hcompressed : compressed = scale * character) :
    compressed / scale = character := by
  rw [hcompressed]
  field_simp [hscale]

end Ecdlp.ParityLift
