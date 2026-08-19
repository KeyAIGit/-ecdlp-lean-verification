import Mathlib

namespace Ecdlp.Proved.Uorc056HrpcxLinearShiftBarrierV1

/-- The alternating geometric polynomial, written recursively so that the
    proof does not depend on a concrete group order. -/
def alternatingGeometric {R : Type*} [Ring R] (x : R) : Nat → R
  | 0 => 0
  | n + 1 => alternatingGeometric x n + (-x) ^ n

/-- Algebraic core of the odd-cycle parity barrier:
    `(1+x) * (1-x+...+(-x)^(n-1)) = 1-(-x)^n`. -/
theorem alternatingGeometric_identity {R : Type*} [CommRing R] (x : R) :
    ∀ n : Nat,
      (1 + x) * alternatingGeometric x n = 1 - (-x) ^ n := by
  intro n
  induction n with
  | zero =>
      simp [alternatingGeometric]
  | succ n ih =>
      simp only [alternatingGeometric, mul_add, ih, pow_succ]
      ring

/-- Once the cyclic relation makes `(-x)^n = -1`, the alternating
    convolution has the explicit inverse `(1+x)/2`. -/
theorem alternatingGeometric_explicit_inverse
    {F : Type*} [Field F]
    (x : F) (n : Nat)
    (hcycle : (-x) ^ n = -1)
    (htwo : (2 : F) ≠ 0) :
    ((2 : F)⁻¹ * (1 + x)) * alternatingGeometric x n = 1 := by
  have hid := alternatingGeometric_identity x n
  have hmain : (1 + x) * alternatingGeometric x n = (2 : F) := by
    rw [hid, hcycle]
    ring
  calc
    ((2 : F)⁻¹ * (1 + x)) * alternatingGeometric x n =
        (2 : F)⁻¹ * ((1 + x) * alternatingGeometric x n) := by ring
    _ = (2 : F)⁻¹ * 2 := by rw [hmain]
    _ = 1 := inv_mul_cancel₀ htwo

/-- The general logical step used after constructing the explicit inverse. -/
theorem explicitLeftInverseForcesInjective
    {α β : Type*} (forward : α → β) (backward : β → α)
    (h : Function.LeftInverse backward forward) :
    Function.Injective forward :=
  h.injective

end Ecdlp.Proved.Uorc056HrpcxLinearShiftBarrierV1
