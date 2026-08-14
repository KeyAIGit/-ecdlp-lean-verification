import Mathlib

/-!
# UORC056 C21-C22 Hilbert-90 divisor certificates

This file formalizes the combinatorial core of the half-divisor, fixed-field
gauge, and valuation-transparent multiplicative support lower bounds. A
`τ`-pair is represented by the two integral divisor coefficients `u i` and
`v i`; the anti-invariant coefficient is their difference. The geometric
identification of these coefficients with the specific endpoint-gauge divisor
remains in the executable replay.
-/

namespace Ecdlp.UORC056

/-- Adding the same fixed-field gauge coefficient to both members of a
`τ`-pair leaves the anti-invariant coefficient unchanged. -/
theorem pair_difference_gauge_invariant (u v c : ℤ) :
    (u + c) - (v + c) = u - v := by
  ring

/-- Pair differences add under multiplication of rational functions, at the
level of divisor coefficients. -/
theorem pair_difference_additive
    (u₁ v₁ u₂ v₂ : ℤ) :
    (u₁ + u₂) - (v₁ + v₂) = (u₁ - v₁) + (u₂ - v₂) := by
  ring

/-- Inversion negates the pair-difference vector. -/
theorem pair_difference_inverse (u v : ℤ) :
    (-u) - (-v) = -(u - v) := by
  ring

/-- A nonzero anti-invariant coefficient forces at least one nonzero
coefficient in every representing half-divisor. -/
theorem pair_difference_ne_zero_support (u v : ℤ)
    (h : u - v ≠ 0) : u ≠ 0 ∨ v ≠ 0 := by
  by_contra hZero
  push Not at hZero
  exact h (by simp [hZero.1, hZero.2])

section Support

variable {ι : Type*}

/-- The support of the anti-invariant difference is covered by the support of
any half-divisor representative. -/
theorem half_divisor_support_cover
    (u v s : ι → ℤ)
    (h : ∀ i, u i - v i = s i) :
    {i | s i ≠ 0} ⊆ {i | u i ≠ 0} ∪ {i | v i ≠ 0} := by
  intro i hi
  change s i ≠ 0 at hi
  change u i ≠ 0 ∨ v i ≠ 0
  apply pair_difference_ne_zero_support
  intro hdiff
  apply hi
  rw [← h i]
  exact hdiff

end Support

section FiniteSupport

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- Cardinal form of the half-divisor support lower bound. It counts
`τ`-pairs, not individual points. -/
theorem half_divisor_support_card_le
    (u v s : ι → ℤ)
    (h : ∀ i, u i - v i = s i) :
    Fintype.card {i // s i ≠ 0} ≤
      Fintype.card {i // u i ≠ 0 ∨ v i ≠ 0} := by
  let f : {i // s i ≠ 0} → {i // u i ≠ 0 ∨ v i ≠ 0} := fun i =>
    ⟨i.1, by
      apply pair_difference_ne_zero_support
      intro hdiff
      apply i.2
      rw [← h i.1]
      exact hdiff⟩
  exact Fintype.card_le_of_injective f (by
    intro a b hab
    apply Subtype.ext
    simpa [f] using congrArg
      (fun x : {i // u i ≠ 0 ∨ v i ≠ 0} => x.1) hab)

/-- The same card bound after an arbitrary fixed-field gauge, represented by a
common coefficient `c i` on both points of every pair. -/
theorem fixed_gauge_cannot_reduce_required_pair_count
    (u v s c : ι → ℤ)
    (h : ∀ i, u i - v i = s i) :
    Fintype.card {i // s i ≠ 0} ≤
      Fintype.card {i // (u i + c i) ≠ 0 ∨ (v i + c i) ≠ 0} := by
  apply half_divisor_support_card_le (u := fun i => u i + c i)
    (v := fun i => v i + c i) (s := s)
  intro i
  calc
    (u i + c i) - (v i + c i) = u i - v i :=
      pair_difference_gauge_invariant (u i) (v i) (c i)
    _ = s i := h i

end FiniteSupport

section MultiplicativeSupport

variable {ι κ : Type*} [Fintype κ]

/-- A nonzero finite integer sum has at least one nonzero summand. -/
theorem finite_sum_ne_zero_has_nonzero_term
    (g : κ → ℤ) (h : (∑ j, g j) ≠ 0) :
    ∃ j, g j ≠ 0 := by
  by_contra hNone
  push Not at hNone
  apply h
  simp [hNone]

/-- Support-union theorem for the declared valuation-transparent
multiplicative Hilbert-90 grammar. At divisor level, products, quotients,
powers, and pullbacks produce a finite integer sum of charged leaf vectors.
Every nonzero output coordinate therefore occurs in at least one charged leaf
support. -/
theorem multiplicative_pair_support_union
    (leaf : κ → ι → ℤ) (target : ι → ℤ)
    (hTarget : ∀ i, (∑ j, leaf j i) = target i) :
    ∀ i, target i ≠ 0 → ∃ j, leaf j i ≠ 0 := by
  intro i hi
  apply finite_sum_ne_zero_has_nonzero_term (g := fun j => leaf j i)
  intro hSum
  apply hi
  rw [← hTarget i]
  exact hSum

end MultiplicativeSupport

end Ecdlp.UORC056
