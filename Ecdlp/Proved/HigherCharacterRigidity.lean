import Mathlib

/-!
# Higher-character rigidity under the order-three GLV action

For the raw point function on the secp256k1 `j=0` curve, the GLV automorphism
scales the value by a fixed primitive cube root.  Hence a sextic phase `z`
travels through the orbit

```text
z, omega*z, omega^2*z.
```

The orbit product is `z^3`, and cubing is unchanged by the cube-root twist.
Thus the canonical C3-invariant component of a sextic phase is its quadratic
component.  Cubic information can label the three positions inside a GLV
orbit, but it does not provide an independent C3-invariant binary separator.

This file formalizes the group/ring algebra only.  It does not formalize the
raw point-function transformation law or claim a universal theorem for every
possible use of higher characters.
-/

namespace Ecdlp.ParityLift

/-- Cubing removes multiplication by a cube root of unity. -/
theorem cubeRootTwist_cube_invariant
    {K : Type*} [CommMonoid K]
    (omega z : K) (homega : omega ^ 3 = 1) :
    (omega * z) ^ 3 = z ^ 3 := by
  rw [mul_pow, homega, one_mul]

/-- The product over an order-three twisted orbit is the cube of the original
phase. -/
theorem cubeRootTwist_orbitProduct
    {K : Type*} [CommRing K]
    (omega z : K) (homega : omega ^ 3 = 1) :
    z * (omega * z) * (omega ^ 2 * z) = z ^ 3 := by
  calc
    z * (omega * z) * (omega ^ 2 * z) = omega ^ 3 * z ^ 3 := by ring
    _ = z ^ 3 := by rw [homega, one_mul]

/-- The cube of a sextic phase has order dividing two. -/
theorem sexticPhase_cube_isBinary
    {K : Type*} [CommMonoid K]
    (z : K) (hz : z ^ 6 = 1) :
    (z ^ 3) ^ 2 = 1 := by
  simpa [pow_mul] using hz

/-- The two phases in the same cube-root coset have the same binary cube. -/
theorem sameCubeRootCoset_sameBinaryPhase
    {K : Type*} [CommMonoid K]
    (omega z : K) (homega : omega ^ 3 = 1) :
    (omega * z) ^ 3 = z ^ 3 :=
  cubeRootTwist_cube_invariant omega z homega

end Ecdlp.ParityLift
