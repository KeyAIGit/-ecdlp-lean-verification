import Mathlib

/-!
# Quadratic Weil orientation

This file formalizes the elementary algebraic identities used by
`QUADRATIC-WEIL-ORIENTATION-038`.

A quadratic Weil/Gauss value scaled by a dual-line character has a normalized
ratio equal to the hidden quadratic character. The ratio is independent of the
nonzero dual scale. A bilinear contraction over all dual scales preserves the
character, whereas the unweighted full-dual sum cancels when the reference sum
vanishes.

The file does not formalize elliptic curves, Weil pairings, quadratic Gauss
sums, Heisenberg or Weil representations, Stone-von Neumann theory,
secp256k1 embedding degrees, or complexity.
-/

namespace Ecdlp.ParityLift

/-- A nonzero dual scale cancels from a normalized quadratic Weil ratio. -/
theorem normalizedQuadraticWeilRatio_recoversCharacter
    {K : Type*} [Field K]
    (projected base dualScale character gaussBase : K)
    (hprojected : projected = dualScale * character * gaussBase)
    (hbase : base = dualScale * gaussBase)
    (hdualScale : dualScale ≠ 0)
    (hgaussBase : gaussBase ≠ 0) :
    projected / base = character := by
  rw [hprojected, hbase]
  field_simp [hdualScale, hgaussBase]
  ring

/-- A quadratic character disappears after squaring the oriented Weil value. -/
theorem quadraticWeilSquare_generatorBlind
    {K : Type*} [CommRing K]
    (projected base character : K)
    (hprojected : projected = character * base)
    (hcharacter : character ^ 2 = 1) :
    projected ^ 2 = base ^ 2 := by
  rw [hprojected, mul_pow, hcharacter, one_mul]

/-- If every dual component differs by one common character, the bilinear
selector-free contraction factors by that character. -/
theorem selectorFreeContraction_factor
    {K : Type*} {ι : Type*} [CommRing K]
    (s : Finset ι)
    (projected base : ι → K)
    (character : K)
    (hprojected : ∀ index ∈ s, projected index = character * base index) :
    (∑ index ∈ s, projected index * base index) =
      character * ∑ index ∈ s, base index * base index := by
  calc
    (∑ index ∈ s, projected index * base index) =
        ∑ index ∈ s, (character * base index) * base index := by
          apply Finset.sum_congr rfl
          intro index hindex
          rw [hprojected index hindex]
    _ = ∑ index ∈ s, character * (base index * base index) := by
          apply Finset.sum_congr rfl
          intro index hindex
          ring
    _ = character * ∑ index ∈ s, base index * base index := by
          rw [Finset.mul_sum]

/-- A nonzero selector-free reference contraction recovers the common
quadratic character by normalization. -/
theorem selectorFreeContractionRatio_recoversCharacter
    {K : Type*} {ι : Type*} [Field K]
    (s : Finset ι)
    (projected base : ι → K)
    (character : K)
    (hprojected : ∀ index ∈ s, projected index = character * base index)
    (hbase : (∑ index ∈ s, base index * base index) ≠ 0) :
    (∑ index ∈ s, projected index * base index) /
        (∑ index ∈ s, base index * base index) = character := by
  rw [selectorFreeContraction_factor s projected base character hprojected]
  field_simp [hbase]

/-- By contrast, an unweighted full-dual sum cancels whenever the reference
sum is zero. -/
theorem unweightedFullDualSum_cancels
    {K : Type*} {ι : Type*} [CommRing K]
    (s : Finset ι)
    (projected base : ι → K)
    (character : K)
    (hprojected : ∀ index ∈ s, projected index = character * base index)
    (hbase : (∑ index ∈ s, base index) = 0) :
    (∑ index ∈ s, projected index) = 0 := by
  calc
    (∑ index ∈ s, projected index) =
        ∑ index ∈ s, character * base index := by
          apply Finset.sum_congr rfl
          intro index hindex
          rw [hprojected index hindex]
    _ = character * ∑ index ∈ s, base index := by
          rw [Finset.mul_sum]
    _ = 0 := by rw [hbase, mul_zero]

end Ecdlp.ParityLift
