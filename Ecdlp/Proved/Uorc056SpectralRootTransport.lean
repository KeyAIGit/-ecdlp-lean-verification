import Mathlib

/-!
# UORC-056 C39 spectral-root transport

This file kernel-checks the algebraic core of the C39 reduction:

* inversion changes the sign of `w - w⁻¹` and fixes `w + w⁻¹`;
* `(w + w⁻¹)^2 - 4 = (w - w⁻¹)^2`;
* an exact sign decoder `sigma = a * r` transports to the quotient-root
  equation `(z^2 - 4) * r^2 = 1`;
* a split `r`-component binary root choice space has cardinality `2^r`;
* exact secp256k1 size arithmetic used by the C39 boundary.

It does not formalize Miller functions, the finite frozen interpolation, the
pair-kernel splitting theorem, or an unrestricted arithmetic-circuit lower
bound. Those parts are isolated in the mathematical note and exact replay.
-/

namespace Ecdlp.Uorc056SpectralRootTransport

/-- Inversion fixes the symmetric coordinate. -/
theorem inversion_fixes_sum
    {F : Type*} [Field F] (w : F) :
    w⁻¹ + (w⁻¹)⁻¹ = w + w⁻¹ := by
  rw [inv_inv]
  ac_rfl

/-- Inversion negates the antisymmetric coordinate. -/
theorem inversion_negates_difference
    {F : Type*} [Field F] (w : F) :
    w⁻¹ - (w⁻¹)⁻¹ = -(w - w⁻¹) := by
  rw [inv_inv]
  ring

/-- The symmetric and antisymmetric coordinates satisfy the hyperbola identity. -/
theorem symmetric_minus_four_eq_antisymmetric_square
    {F : Type*} [Field F] (w : F) :
    (w + w⁻¹) ^ 2 - 4 = (w - w⁻¹) ^ 2 := by
  ring

/-- If a sign is written as an antisymmetric coordinate times a correction,
then the correction is an oriented square root of the inverse public radicand. -/
theorem oriented_decoder_transports_to_square_root
    {F : Type*} [CommRing F]
    (sigma a r z : F)
    (hdecode : sigma = a * r)
    (hsigma : sigma * sigma = 1)
    (hrad : a * a = z * z - 4) :
    (z * z - 4) * (r * r) = 1 := by
  calc
    (z * z - 4) * (r * r) = (a * a) * (r * r) := by rw [hrad]
    _ = (a * r) * (a * r) := by ring
    _ = sigma * sigma := by rw [hdecode]
    _ = 1 := hsigma

/-- Conversely, a chosen square root gives a sign whenever the antisymmetric
coordinate is the corresponding radicand root. -/
theorem square_root_gives_sign_square
    {F : Type*} [CommRing F]
    (a r z : F)
    (hrad : a * a = z * z - 4)
    (hroot : (z * z - 4) * (r * r) = 1) :
    (a * r) * (a * r) = 1 := by
  calc
    (a * r) * (a * r) = (a * a) * (r * r) := by ring
    _ = (z * z - 4) * (r * r) := by rw [hrad]
    _ = 1 := hroot

/-- One independent binary sign choice in each of `r` split components gives
exactly `2^r` root vectors. -/
theorem binary_component_choices_card (r : Nat) :
    Fintype.card (Fin r → Bool) = 2 ^ r := by
  simp


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpPairComponents : Nat :=
  (secpN - 1) / 2


theorem secpPairComponentsIs255Bit :
    2 ^ 254 < secpPairComponents ∧ secpPairComponents < 2 ^ 255 := by
  native_decide


theorem secpPairKernelDegree :
    2 * secpPairComponents = secpN - 1 := by
  native_decide

end Ecdlp.Uorc056SpectralRootTransport
