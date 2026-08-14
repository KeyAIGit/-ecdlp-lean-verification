import Mathlib

/-!
# UORC-056 CM threefold root decomposition algebra

This file kernel-checks two denominator-free algebraic consequences used by
V14 after the central oriented root has been split into its three C3 weights.
It does not formalize elliptic curves, the kernel quotient, or the parity
projectors themselves.
-/

namespace Ecdlp.CmThreefoldRoot

variable {R : Type*} [CommRing R]

/-- From the weight-1 and weight-2 square equations

  2AB + T C^2 = 0,
  B^2 + 2AC = 0,

one obtains the denominator-free four-branch selector equation

  B (T B^3 + 8 A^3) = 0.
-/
theorem selector_denominator_free
    (A B C T : R)
    (h1 : 2 * A * B + T * C ^ 2 = 0)
    (h2 : B ^ 2 + 2 * A * C = 0) :
    B * (T * B ^ 3 + 8 * A ^ 3) = 0 := by
  linear_combination
    T * (B ^ 2 - 2 * A * C) * h2 +
    4 * A ^ 2 * h1

/-- The weight-2 equation eliminates `C` from the point-value expression
without division.  If `2A` is invertible, this is exactly the V14 direct
reconstruction formula using only `A` and `B`. -/
theorem eliminate_weight_two_component
    (A B C x : R)
    (h2 : B ^ 2 + 2 * A * C = 0) :
    2 * A * (A + x * B + x ^ 2 * C)
      = 2 * A ^ 2 + 2 * A * x * B - x ^ 2 * B ^ 2 := by
  linear_combination x ^ 2 * h2

/-- A lightweight consistency form: if `B=0`, the selector polynomial
vanishes identically. -/
theorem selector_uniform_branch
    (A T : R) :
    (0 : R) * (T * (0 : R) ^ 3 + 8 * A ^ 3) = 0 := by
  ring

end Ecdlp.CmThreefoldRoot
