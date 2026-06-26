import Mathlib

/-!
# The collision equation — the "solve" step of Pollard rho / BSGS

Generic square-root DLP algorithms (baby-step giant-step, Pollard rho/kangaroo,
van Oorschot–Wiener) all reduce to the same final step: a **collision** between two
group expressions `g^a · h^b = g^c · h^d` (with `h = g^x` the unknown) yields a
*linear congruence* for the discrete log `x`. This file proves that step.

`PollardRho.lean` proves a collision must *exist* (pigeonhole); `BabyStepGiantStep.
lean` bounds the *cost* of finding one. This is the algebraic identity that turns a
found collision into the answer: from the collision,

  `a + x·b ≡ c + x·d  (mod n)`,   `n = orderOf g`,

so `(a − c) ≡ x·(d − b) (mod n)`, and whenever `d − b` is invertible mod `n`
(e.g. `n` prime and `d ≢ b`), `x` is recovered uniquely. Formalizes corpus claim
`pollard-rho-collision-equation-002`.
-/

namespace Ecdlp.GenericGroup

variable {G : Type*} [Group G]

/-- **Collision equation.** If `h = g^x` and a generic walk produces a collision
`g^a · h^b = g^c · h^d`, then the exponents satisfy `a + x·b ≡ c + x·d (mod orderOf g)`.
This is the linear congruence from which the discrete log `x` is solved. -/
theorem collision_modEq (g h : G) (x a b c d : ℕ) (hx : h = g ^ x)
    (hcol : g ^ a * h ^ b = g ^ c * h ^ d) :
    a + x * b ≡ c + x * d [MOD orderOf g] := by
  subst hx
  rw [← pow_mul, ← pow_mul, ← pow_add, ← pow_add] at hcol
  exact pow_eq_pow_iff_modEq.mp hcol

/-- The collision equation in subtractive form over `ℤ/n`: `(a − c) = x·(d − b)` in
`ZMod (orderOf g)`. When `d − b` is a unit (e.g. `orderOf g` prime and `d ≢ b`),
this determines `x`. -/
theorem collision_zmod (g h : G) (x a b c d : ℕ) (hx : h = g ^ x)
    (hcol : g ^ a * h ^ b = g ^ c * h ^ d) :
    ((a : ZMod (orderOf g)) - c) = (x : ZMod (orderOf g)) * ((d : ZMod (orderOf g)) - b) := by
  have hmod := collision_modEq g h x a b c d hx hcol
  have hcast : ((a + x * b : ℕ) : ZMod (orderOf g)) = ((c + x * d : ℕ) : ZMod (orderOf g)) :=
    (ZMod.natCast_eq_natCast_iff _ _ _).mpr hmod
  push_cast at hcast
  linear_combination hcast

/-- **Discrete-log recovery.** When the collision coefficient `d − b` is a unit mod
`n` (e.g. `n` prime and `d ≢ b`), the collision determines the discrete log:
`x = (a − c)·(d − b)⁻¹` in `ZMod n`. This closes the rho/BSGS solve step — a found
collision yields the answer outright. -/
theorem collision_recovers_log (g h : G) (x a b c d : ℕ) (hx : h = g ^ x)
    (hcol : g ^ a * h ^ b = g ^ c * h ^ d)
    (hu : IsUnit ((d : ZMod (orderOf g)) - b)) :
    (x : ZMod (orderOf g))
      = ((a : ZMod (orderOf g)) - c) * Ring.inverse ((d : ZMod (orderOf g)) - b) := by
  have hz := collision_zmod g h x a b c d hx hcol
  rw [hz, mul_assoc, Ring.mul_inverse_cancel _ hu, mul_one]

/-- **The discrete log is well-defined mod `n`.** If `g^x = g^y` then
`x ≡ y (mod orderOf g)`: the DLP has a unique solution modulo the group order. -/
theorem dlog_unique (g : G) {x y : ℕ} (hxy : g ^ x = g ^ y) :
    x ≡ y [MOD orderOf g] :=
  pow_eq_pow_iff_modEq.mp hxy

end Ecdlp.GenericGroup
