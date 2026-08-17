import Mathlib

/-!
# UORC-056 C45 full-field Ward collapse

This file kernel-checks the elementary algebraic consequences used by C45:

* if every near-period channel is one power of one public raw state, then the
  offset family has a single multiplicative transition;
* all offsets are generated from the first channel by that one transition;
* the exact fixed secp256k1 parity and power-map arithmetic.

The elliptic-curve division-polynomial composition law, Ward quasi-period law,
and fixed finite-field evaluations are checked by the companion executable
replay. This file does not claim a nonlinear decoder of the raw state, a parity
oracle, or an unrestricted arithmetic-circuit lower bound.
-/

namespace Ecdlp.Uorc056FullFieldWardCollapseC45


def collapsedChannel
    {G : Type*} [CommGroup G]
    (raw : G) (n offset : Nat) : G :=
  (raw ^ (n * (n + 2 * offset)))⁻¹


theorem channelExponentStep (n offset : Nat) :
    n * (n + 2 * (offset + 1)) =
      2 * n + n * (n + 2 * offset) := by
  ring


/-- Consecutive Ward offsets differ by one fixed public multiplier. -/
theorem collapsedChannel_step
    {G : Type*} [CommGroup G]
    (raw : G) (n offset : Nat) :
    collapsedChannel raw n (offset + 1) =
      (raw ^ (2 * n))⁻¹ * collapsedChannel raw n offset := by
  unfold collapsedChannel
  rw [channelExponentStep, pow_add]
  simp only [mul_inv_rev]
  ac_rfl


/-- Starting from offset one, the complete family is a geometric progression. -/
theorem collapsedChannel_from_first
    {G : Type*} [CommGroup G]
    (raw : G) (n offset : Nat) :
    collapsedChannel raw n (offset + 1) =
      ((raw ^ (2 * n))⁻¹) ^ offset * collapsedChannel raw n 1 := by
  induction offset with
  | zero => simp
  | succ offset ih =>
      rw [collapsedChannel_step, ih, pow_succ]
      ac_rfl


/-- Abstract algebra behind the full-field collapse. The elliptic replay
supplies `raw = w*c^q`, the Ward coefficient relation, and the channel formula. -/
theorem fullFieldCollapse
    {G : Type*} [CommGroup G]
    (raw w c coefficient channel : G)
    (q exponent : Nat)
    (hraw : raw = w * c ^ q)
    (hcoefficient : coefficient = (c ^ exponent)⁻¹)
    (hchannel : channel = coefficient ^ q * (w ^ exponent)⁻¹) :
    channel = (raw ^ exponent)⁻¹ := by
  rw [hchannel, hcoefficient, hraw]
  simp only [mul_pow, inv_pow, pow_mul, mul_inv_rev]
  rw [Nat.mul_comm exponent q]
  ac_rfl


def secpP : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


theorem secpFieldModFour : secpP % 4 = 3 := by
  native_decide


theorem secpOrderOdd : secpN % 2 = 1 := by
  native_decide


theorem secpPowerMapCoprime : Nat.gcd (secpN * secpN) (secpP - 1) = 1 := by
  native_decide


theorem declaredChannelCount : 294 * 8 = 2352 := by
  native_decide


theorem declaredRecurrenceCount : 294 * 7 = 2058 := by
  native_decide

end Ecdlp.Uorc056FullFieldWardCollapseC45
