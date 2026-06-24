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


/-- A root of `x² + x + 1` in a field of characteristic `≠ 3` is a **primitive** cube
root of unity: it has multiplicative order exactly `3`. This strengthens
`cube_root_of_eigenvalue` (which gives only `x³ = 1`) and is the precise sense in
which the secp256k1 GLV eigenvalue `λ` (and field factor `β`) generate the order-3
automorphism / complex multiplication. -/
theorem orderOf_eigenvalue_eq_three {F : Type*} [Field F] (x : F)
    (h : x ^ 2 + x + 1 = 0) (hchar : (3 : F) ≠ 0) : orderOf x = 3 := by
  haveI : Fact (Nat.Prime 3) := ⟨by norm_num⟩
  apply orderOf_eq_prime
  · linear_combination (x - 1) * h
  · intro hx1
    subst hx1
    exact hchar (by linear_combination h)

end Ecdlp.Proved
