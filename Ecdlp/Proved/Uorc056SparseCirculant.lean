import Mathlib
import Ecdlp.Proved.ScalarParity
import Ecdlp.Proved.Uorc056BranchSensitiveLeaf

/-!
# UORC056 C25 sparse-circulant parity symmetry core

This file formalizes the arithmetic collision principles used by the C25
classification of

  det (a I + b T + c T^k)

and its sparse resultant. The determinant and resultant identities themselves
remain in the exact executable replay. The Lean theorems record the parity
behavior of the relevant canonical exponent transforms and show that any
observable collision at opposite parity blocks a universal parity decoder.
-/

namespace Ecdlp.UORC056

open Ecdlp.ParityLift

/-- The canonical representative of `1-k mod n` is `n+1-k` for `1<k<n`.
For odd `n`, this transformation preserves parity. Thus the `a=b` coefficient
stabilizer does not by itself yield an opposite-parity collision. -/
theorem one_sub_canonical_preserves_scalarParity
    {n k : ℕ}
    (hnOdd : n % 2 = 1)
    (hkLower : 1 < k)
    (hkUpper : k < n) :
    scalarParity (n + 1 - k) = scalarParity k := by
  unfold scalarParity
  omega

/-- When `n=1 mod 4`, the canonical inverse of `2` has odd representative
`(n+1)/2`, whereas `2` is even. -/
theorem two_and_half_succ_have_opposite_parity
    {n : ℕ} (hnMod4 : n % 4 = 1) :
    scalarParity 2 ≠ scalarParity ((n + 1) / 2) := by
  unfold scalarParity
  omega

/-- For the transposition `k -> k/(k-1)`, the image of `k=3` is represented by
`(n+3)/2`. When `n=1 mod 4`, this has parity opposite to `3`. -/
theorem three_and_half_add_three_have_opposite_parity
    {n : ℕ} (hnMod4 : n % 4 = 1) :
    scalarParity 3 ≠ scalarParity ((n + 3) / 2) := by
  unfold scalarParity
  omega

/-- Any collision of an observable at two opposite-parity indices rules out a
single decoder that is correct at both indices. -/
theorem observable_collision_blocks_parity_decoder
    {X : Type*} (observable : ℕ → X) (left right : ℕ)
    (hCollision : observable left = observable right)
    (hParity : scalarParity left ≠ scalarParity right) :
    ¬ ∃ decode : X → ℕ,
        decode (observable left) = scalarParity left ∧
        decode (observable right) = scalarParity right := by
  exact twoWorld_branch_sensitive_target_not_publicly_decodable
    (publicPlus := observable left)
    (publicMinus := observable right)
    (targetPlus := scalarParity left)
    (targetMinus := scalarParity right)
    hCollision hParity

/-- The explicit `k=2` inversion collision blocks a decoder on every
`n=1 mod 4` instance where the observable has that symmetry. -/
theorem inverse_two_collision_blocks_parity_decoder
    {X : Type*} {n : ℕ} (observable : ℕ → X)
    (hnMod4 : n % 4 = 1)
    (hCollision : observable 2 = observable ((n + 1) / 2)) :
    ¬ ∃ decode : X → ℕ,
        decode (observable 2) = scalarParity 2 ∧
        decode (observable ((n + 1) / 2)) =
          scalarParity ((n + 1) / 2) := by
  exact observable_collision_blocks_parity_decoder
    observable 2 ((n + 1) / 2) hCollision
    (two_and_half_succ_have_opposite_parity hnMod4)

/-- The explicit `k=3` collision for `k -> k/(k-1)` blocks a decoder on every
`n=1 mod 4` instance where the observable has that symmetry. -/
theorem three_mobius_collision_blocks_parity_decoder
    {X : Type*} {n : ℕ} (observable : ℕ → X)
    (hnMod4 : n % 4 = 1)
    (hCollision : observable 3 = observable ((n + 3) / 2)) :
    ¬ ∃ decode : X → ℕ,
        decode (observable 3) = scalarParity 3 ∧
        decode (observable ((n + 3) / 2)) =
          scalarParity ((n + 3) / 2) := by
  exact observable_collision_blocks_parity_decoder
    observable 3 ((n + 3) / 2) hCollision
    (three_and_half_add_three_have_opposite_parity hnMod4)

/-- An observable constant on the nonzero canonical indices cannot decode
parity, already because indices `1` and `2` have different parity. This is the
abstract consequence used for every zero-coefficient two-term determinant
stratum. -/
theorem constant_observable_blocks_parity_decoder
    {X : Type*} (observable : ℕ → X)
    (hConstant : ∀ left right, observable left = observable right) :
    ¬ ∃ decode : X → ℕ,
        decode (observable 1) = scalarParity 1 ∧
        decode (observable 2) = scalarParity 2 := by
  apply observable_collision_blocks_parity_decoder observable 1 2
  · exact hConstant 1 2
  · norm_num [scalarParity]

/-- If a coefficient-symmetric extraction is constant on a full Möbius orbit
and that orbit contains opposite parity, it cannot be an exact parity decoder.
The executable C25 certificate supplies such an orbit collision for every
prime order greater than eleven. -/
theorem mobius_orbit_collision_blocks_parity_decoder
    {X : Type*} (extraction : ℕ → X) (left right : ℕ)
    (hSameOrbitValue : extraction left = extraction right)
    (hOppositeParity : scalarParity left ≠ scalarParity right) :
    ¬ ∃ decode : X → ℕ,
        decode (extraction left) = scalarParity left ∧
        decode (extraction right) = scalarParity right :=
  observable_collision_blocks_parity_decoder
    extraction left right hSameOrbitValue hOppositeParity

end Ecdlp.UORC056
