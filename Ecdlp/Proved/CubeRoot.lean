import Mathlib

/-!
# Cube-root structure of the GLV endomorphism

The secp256k1 GLV endomorphism scalar `λ` (and field factor `β`) satisfy
`x² + x + 1 = 0`, hence are primitive cube roots of unity: `x³ = 1`. This is the
ring-level reason behind the concrete `native_decide` facts
`Secp256k1.lambda_is_cube_root` and `beta_is_cube_root`.
-/

namespace Ecdlp.Proved

/-- In a commutative ring, a root of `x² + x + 1` is a cube root of unity. -/
theorem cube_root_of_eigenvalue {R : Type*} [CommRing R] (x : R)
    (h : x ^ 2 + x + 1 = 0) : x ^ 3 = 1 := by
  linear_combination (x - 1) * h

end Ecdlp.Proved
