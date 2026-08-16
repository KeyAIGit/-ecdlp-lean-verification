import Mathlib

/-!
# UORC-056 C39 spectral-root transport

Kernel-checked algebraic core:

* inversion fixes `w + w⁻¹` and negates `w - w⁻¹`;
* for nonzero `w`, `(w + w⁻¹)^2 - 4 = (w - w⁻¹)^2`;
* an exact sign decoder transports to a quotient square-root equation;
* `r` independent binary component choices have cardinality `2^r`;
* exact secp256k1 size arithmetic.

Miller functions, frozen interpolation, quotient splitting, and unrestricted
circuit lower bounds are intentionally outside this file.
-/

namespace Ecdlp.Uorc056SpectralRootTransportC39

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

/-- The symmetric and antisymmetric coordinates satisfy the hyperbola identity
away from the zero element. -/
theorem symmetric_minus_four_eq_antisymmetric_square
    {F : Type*} [Field F] (w : F) (hw : w ≠ 0) :
    (w + w⁻¹) ^ 2 - 4 = (w - w⁻¹) ^ 2 := by
  field_simp [hw]
  <;> ring

/-- If a sign is represented by an antisymmetric coordinate times a correction,
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

/-- Conversely, a selected quotient square root yields a square-one sign. -/
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

/-- One binary sign choice in each of `r` split components gives `2^r` vectors. -/
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

end Ecdlp.Uorc056SpectralRootTransportC39
