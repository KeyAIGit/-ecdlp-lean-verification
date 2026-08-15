import Mathlib
import Ecdlp.Proved.Uorc056SparseCirculant

/-!
# UORC056 C26 asymmetric sparse-resultant core

This file formalizes two scoped principles used by C26.

First, if two determinant values differ by a known scale factor and an
extraction is invariant under that scale, then an opposite-parity orbit
collision blocks an exact parity decoder. This is the abstract theorem applied
to the projectively cyclic coefficient triple `(1, omega, omega^2)` and to
quadratic-character extraction after the executable certificate verifies that
`omega` is a square.

Second, six small preimage sets cannot cover a larger finite domain. This is
the counting core behind the worst-case linear reduced-degree boundary for a
single S3/Mobius reparameterization of the sparse trinomial resultant. The
concrete identification of the six preimages and the exact secp256k1 bound are
kept in the deterministic replay.

No unrestricted sparse-resultant or arithmetic-circuit lower bound is claimed.
-/

namespace Ecdlp.UORC056

open Ecdlp.ParityLift

/-- If two observable values differ by a fixed multiplier and the extraction
ignores that multiplier, then the extracted values collide. Opposite scalar
parity therefore rules out one decoder correct at both indices. -/
theorem scaleInvariant_extraction_collision_blocks_parity_decoder
    {K X : Type*} [Mul K]
    (value : ℕ → K) (extract : K → X) (mu : K)
    (left right : ℕ)
    (hScale : value right = mu * value left)
    (hInvariant : ∀ z, extract (mu * z) = extract z)
    (hParity : scalarParity left ≠ scalarParity right) :
    ¬ ∃ decode : X → ℕ,
        decode (extract (value left)) = scalarParity left ∧
        decode (extract (value right)) = scalarParity right := by
  apply observable_collision_blocks_parity_decoder
    (observable := fun index => extract (value index))
    (left := left) (right := right)
  · calc
      extract (value left) = extract (mu * value left) :=
        (hInvariant (value left)).symm
      _ = extract (value right) := by rw [hScale]
  · exact hParity

/-- A scale-invariant extraction is constant along any finite chain whose
successive values differ by the same scale. -/
theorem scaleInvariant_three_cycle
    {K X : Type*} [Mul K]
    (extract : K → X) (mu z : K)
    (hInvariant : ∀ value, extract (mu * value) = extract value) :
    extract (mu * (mu * z)) = extract z := by
  calc
    extract (mu * (mu * z)) = extract (mu * z) := hInvariant (mu * z)
    _ = extract z := hInvariant z

section SixCover

variable {α : Type*} [DecidableEq α]

/-- The cardinality of a finite set covered by six finite sets is at most the
sum of their cardinalities. -/
theorem card_le_sum_six_of_subset_union
    (U A0 A1 A2 A3 A4 A5 : Finset α)
    (hCover : U ⊆ (((((A0 ∪ A1) ∪ A2) ∪ A3) ∪ A4) ∪ A5)) :
    U.card ≤ A0.card + A1.card + A2.card + A3.card + A4.card + A5.card := by
  have h01 := Finset.card_union_le A0 A1
  have h012 := Finset.card_union_le (A0 ∪ A1) A2
  have h0123 := Finset.card_union_le ((A0 ∪ A1) ∪ A2) A3
  have h01234 := Finset.card_union_le (((A0 ∪ A1) ∪ A2) ∪ A3) A4
  have h012345 :=
    Finset.card_union_le ((((A0 ∪ A1) ∪ A2) ∪ A3) ∪ A4) A5
  have hCard :
      U.card ≤ (((((A0 ∪ A1) ∪ A2) ∪ A3) ∪ A4) ∪ A5).card :=
    Finset.card_le_card hCover
  omega

/-- If each of six covering sets has cardinality at most `b`, then the covered
set has cardinality at most `6*b`. -/
theorem card_le_six_mul_of_small_cover
    (U A0 A1 A2 A3 A4 A5 : Finset α) (b : ℕ)
    (hCover : U ⊆ (((((A0 ∪ A1) ∪ A2) ∪ A3) ∪ A4) ∪ A5))
    (h0 : A0.card ≤ b) (h1 : A1.card ≤ b)
    (h2 : A2.card ≤ b) (h3 : A3.card ≤ b)
    (h4 : A4.card ≤ b) (h5 : A5.card ≤ b) :
    U.card ≤ 6 * b := by
  have hSum := card_le_sum_six_of_subset_union
    U A0 A1 A2 A3 A4 A5 hCover
  omega

/-- Contrapositive form: six sets of size at most `b` cannot cover a domain
with more than `6*b` elements. -/
theorem six_small_sets_do_not_cover
    (U A0 A1 A2 A3 A4 A5 : Finset α) (b : ℕ)
    (h0 : A0.card ≤ b) (h1 : A1.card ≤ b)
    (h2 : A2.card ≤ b) (h3 : A3.card ≤ b)
    (h4 : A4.card ≤ b) (h5 : A5.card ≤ b)
    (hLarge : 6 * b < U.card) :
    ¬ U ⊆ (((((A0 ∪ A1) ∪ A2) ∪ A3) ∪ A4) ∪ A5) := by
  intro hCover
  have hBound := card_le_six_mul_of_small_cover
    U A0 A1 A2 A3 A4 A5 b hCover h0 h1 h2 h3 h4 h5
  omega

end SixCover

end Ecdlp.UORC056
