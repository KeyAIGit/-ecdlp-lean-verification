import Mathlib

/-!
# Oriented parity divisor circuit boundary

This file formalizes elementary componentwise identities used by
`ORIENTED-PARITY-DIVISOR-CIRCUIT-046`.

In a split Kummer algebra, multiplying each nonzero square root component by an
independent sign preserves its square.  The sign action is injective when every
root component is nonzero.  Once an oriented root is selected, division by the
public y-coordinate returns either `1` or `-1`.  The file also records the
binary product-tree gate arithmetic.

The file does not formalize elliptic curves, Kummer kernel polynomials,
interpolation, branch cardinalities, divisor degrees, determinant complexity,
secp256k1, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Componentwise multiplication by square-one signs preserves the symmetric
square data. -/
theorem signAction_preservesSquare
    {ι K : Type*} [CommRing K]
    (root sign : ι → K)
    (hsign : ∀ index, sign index ^ 2 = 1) :
    (fun index => (sign index * root index) ^ 2) =
      (fun index => root index ^ 2) := by
  funext index
  calc
    (sign index * root index) ^ 2 =
        sign index ^ 2 * root index ^ 2 := by
          simp [mul_pow]
    _ = root index ^ 2 := by rw [hsign index, one_mul]

/-- At nonzero root components, two sign vectors producing the same oriented
root are equal. -/
theorem signAction_injective
    {ι K : Type*} [Field K]
    (root : ι → K)
    (hroot : ∀ index, root index ≠ 0) :
    Function.Injective
      (fun sign : ι → K => fun index => sign index * root index) := by
  intro left right hequal
  funext index
  have hcomponent : left index * root index = right index * root index :=
    congrFun hequal index
  exact (mul_right_cancel₀ (hroot index)) hcomponent

/-- Global negation is one of the square-root branches. -/
theorem negOrientation_sameSquare
    {K : Type*} [CommRing K]
    (root : K) :
    (-root) ^ 2 = root ^ 2 := by
  ring

/-- Selecting the positive y-branch makes the oriented ratio equal to one. -/
theorem orientedRatio_eq_one
    {K : Type*} [Field K]
    (oriented y : K)
    (hy : y ≠ 0)
    (horiented : oriented = y) :
    oriented / y = 1 := by
  rw [horiented, div_self hy]

/-- Selecting the negative y-branch makes the oriented ratio equal to minus
one. -/
theorem orientedRatio_eq_negOne
    {K : Type*} [Field K]
    (oriented y : K)
    (hy : y ≠ 0)
    (horiented : oriented = -y) :
    oriented / y = -1 := by
  simp [horiented, hy]

/-- A binary product tree with `leaves` inputs and at most one new component per
multiplication needs at least `leaves - 1` gates.  The structural premise is
recorded as `leaves ≤ gates + 1`. -/
theorem binaryProduct_gate_lower_bound
    (leaves gates : ℕ)
    (hcoverage : leaves ≤ gates + 1) :
    leaves - 1 ≤ gates := by
  omega

end Ecdlp.ParityLift
