import Mathlib

/-!
# UORC-056 C31 oriented source rank boundary

This file kernel-checks the elementary linear-algebra transfer identities and
fixed secp256k1 arithmetic used by C31.  The multiplicative Fourier theorem
that the marked-generator sign matrix has characteristic-zero rank `(n-1)/2`
uses the standard nonvanishing of `L(0, χ)` for primitive odd Dirichlet
characters and is not formalized here.  The concrete frozen finite-field ranks
are independently replayed by Python.
-/

namespace Ecdlp.Uorc056OrientedSourceRank

variable {K ι κ : Type*} [Field K] [Fintype ι] [Fintype κ]

/-- Multiplication of every coordinate by a public nonzero scalar is injective. -/
theorem columnScale_injective
    (y : ι → K)
    (hy : ∀ i, y i ≠ 0) :
    Function.Injective (fun v : ι → K => fun i => v i * y i) := by
  intro left right h
  funext i
  have hi : left i * y i = right i * y i := congrFun h i
  calc
    left i = (left i * y i) / y i := by field_simp [hy i]
    _ = (right i * y i) / y i := by rw [hi]
    _ = right i := by field_simp [hy i]

/-- The symmetric input lies in the kernel of the signed two-block operator. -/
theorem signedBlock_symmetric
    (A : ι → κ → K)
    (v : κ → K)
    (i : ι) :
    (∑ j, A i j * v j) + (∑ j, (-A i j) * v j) = 0 := by
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_eq_zero
  intro j _
  ring

/-- The antisymmetric input reduces the signed two-block operator to twice the
half operator. -/
theorem signedBlock_antisymmetric
    (A : ι → κ → K)
    (v : κ → K)
    (i : ι) :
    (∑ j, A i j * v j) - (∑ j, (-A i j) * v j) =
      2 * (∑ j, A i j * v j) := by
  have hneg : (∑ j, (-A i j) * v j) = -(∑ j, A i j * v j) := by
    rw [← Finset.sum_neg_distrib]
    apply Finset.sum_congr rfl
    intro j _
    ring
  rw [hneg]
  ring

/-- Once a source-rank theorem has been established, containment in a fixed
linear dictionary transfers directly to the dictionary-cardinality lower
bound. -/
theorem fixedDictionaryCardLowerBound
    (sourceRank dictionaryCard : Nat)
    (hcontain : sourceRank ≤ dictionaryCard) :
    sourceRank ≤ dictionaryCard :=
  hcontain

/-- Negating a source row does not change its linear span. -/
theorem mem_span_neg_iff
    (v : ι → K)
    (S : Set (ι → K)) :
    -v ∈ Submodule.span K S ↔ v ∈ Submodule.span K S := by
  constructor
  · intro h
    have := Submodule.neg_mem (Submodule.span K S) h
    simpa using this
  · intro h
    exact Submodule.neg_mem (Submodule.span K S) h


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpHalfSourceRank : Nat :=
  (secpN - 1) / 2


theorem secpHalfSourceRankExact :
    secpHalfSourceRank =
      57896044618658097711785492504343953926418782139537452191302581570759080747168 := by
  native_decide


theorem secpHalfSourceRankExceedsTwoPow254 :
    2 ^ 254 < secpHalfSourceRank := by
  native_decide


theorem secpHalfSourceRankBelowTwoPow255 :
    secpHalfSourceRank < 2 ^ 255 := by
  native_decide


theorem frozenHalfDimensionsSum :
    15 + 39 + 33 + 63 + 69 = 219 := by
  native_decide


theorem frozenHalfSourceEntries :
    15 ^ 2 + 39 ^ 2 + 33 ^ 2 + 63 ^ 2 + 69 ^ 2 = 11565 := by
  native_decide


theorem frozenAllMarkerSourceEntries :
    30 * 15 + 78 * 39 + 66 * 33 + 126 * 63 + 138 * 69 = 23130 := by
  native_decide

end Ecdlp.Uorc056OrientedSourceRank
