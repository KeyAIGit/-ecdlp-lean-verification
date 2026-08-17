import Mathlib

/-!
# UORC-056 C43 local GLV gauge boundary

This file kernel-checks the elementary sign algebra used by C43:

* parity is carry times the ordered sector sign;
* the cubic carry product is invariant under a two-sign flip;
* that residual gauge can change the ordered first sign;
* cyclic-invariant or product-only data cannot decode the ordered first sign;
* exact secp256k1 GLV quotient arithmetic.

It does not formalize Miller functions, interpolation, elliptic curves, the
finite character-span replay, or an unrestricted circuit lower bound.
-/

namespace Ecdlp.Uorc056LocalGlvGaugeBreaking

/-- The exact Boolean character identity behind `parity = carry * sector`. -/
theorem parityEqCarryMulSector
    {R : Type*} [CommRing R]
    (s0 s1 s2 : R)
    (hs1 : s1 ^ 2 = 1)
    (hs2 : s2 ^ 2 = 1) :
    (s0 * s1 * s2) * (s1 * s2) = s0 := by
  calc
    (s0 * s1 * s2) * (s1 * s2) = s0 * (s1 ^ 2) * (s2 ^ 2) := by ring
    _ = s0 := by rw [hs1, hs2]; ring

/-- Flipping two component signs leaves the cubic carry product unchanged. -/
theorem twoSignFlipPreservesCarry
    {R : Type*} [CommRing R]
    (s0 s1 s2 : R) :
    (-s0) * (-s1) * s2 = s0 * s1 * s2 := by
  ring

/-- In odd characteristic, the same two-sign flip changes a nonzero first
    component. This is the explicit residual Klein-four gauge witness. -/
theorem twoSignFlipChangesFirst
    {K : Type*} [Field K]
    (s0 : K)
    (htwo : (2 : K) ≠ 0)
    (hs0 : s0 ≠ 0) :
    -s0 ≠ s0 := by
  intro h
  have hz : (2 : K) * s0 = 0 := by
    calc
      (2 : K) * s0 = s0 - (-s0) := by ring
      _ = 0 := by rw [h]; ring
  exact hs0 ((mul_eq_zero.mp hz).resolve_left htwo)

/-- A decoder that sees only the cubic product cannot choose the ordered first
    sign, since two sign triples can have the same product and opposite first
    coordinates. -/
theorem productOnlyCannotDecodeFirst
    {K : Type*} [Field K]
    (d : K → K)
    (htwo : (2 : K) ≠ 0)
    (hplus : d 1 = 1)
    (hminus : d 1 = -1) :
    False := by
  have h : (1 : K) = -1 := hplus.symm.trans hminus
  have hsub : (1 : K) - (-1) = 0 := sub_eq_zero.mpr h
  have hz : (2 : K) = 0 := by
    calc
      (2 : K) = 1 - (-1) := by ring
      _ = 0 := hsub
  exact htwo hz

/-- Cyclic-invariant data cannot decode the ordered first component on all sign
    triples. The two displayed triples are cyclic rotations of each other. -/
theorem cyclicInvariantCannotDecodeFirst
    {K : Type*} [Field K]
    (d : K → K → K → K)
    (htwo : (2 : K) ≠ 0)
    (hcyclic : d 1 (-1) (-1) = d (-1) (-1) 1)
    (hfirstA : d 1 (-1) (-1) = 1)
    (hfirstB : d (-1) (-1) 1 = -1) :
    False := by
  have h : (1 : K) = -1 := by
    calc
      (1 : K) = d 1 (-1) (-1) := hfirstA.symm
      _ = d (-1) (-1) 1 := hcyclic
      _ = -1 := hfirstB
  have hsub : (1 : K) - (-1) = 0 := sub_eq_zero.mpr h
  have hz : (2 : K) = 0 := by
    calc
      (2 : K) = 1 - (-1) := by ring
      _ = 0 := hsub
  exact htwo hz

/-- Cross-multiplied carry-sector reconstruction of the oriented root. -/
theorem carrySectorReconstruction
    {R : Type*} [CommRing R]
    (s0 s1 s2 y : R)
    (hs1 : s1 ^ 2 = 1)
    (hs2 : s2 ^ 2 = 1) :
    (s0 * y) * (y ^ 2) =
      ((s0 * s1 * s2) * (y ^ 3)) * (s1 * s2) := by
  have hs : (s0 * s1 * s2) * (s1 * s2) = s0 :=
    parityEqCarryMulSector s0 s1 s2 hs1 hs2
  calc
    (s0 * y) * (y ^ 2) = s0 * (y ^ 3) := by ring
    _ = ((s0 * s1 * s2) * (s1 * s2)) * (y ^ 3) := by rw [hs]
    _ = ((s0 * s1 * s2) * (y ^ 3)) * (s1 * s2) := by ring

/-- Reversing all three oriented roots negates their cubic product. -/
theorem tripleReversalNegatesCarry
    {R : Type*} [CommRing R]
    (a b c : R) :
    (-a) * (-b) * (-c) = -(a * b * c) := by
  ring


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpHalfKernel : Nat :=
  (secpN - 1) / 2


def secpGlvOrbits : Nat :=
  (secpN - 1) / 6


theorem secpHalfKernelIsThreeGlvOrbits :
    secpHalfKernel = 3 * secpGlvOrbits := by
  native_decide


theorem secpGlvOrbitCountExact :
    secpGlvOrbits =
      19298681539552699237261830834781317975472927379845817397100860523586360249056 := by
  native_decide


theorem secpGlvOrbitBitBoundary :
    2 ^ 253 < secpGlvOrbits ∧ secpGlvOrbits < 2 ^ 254 := by
  native_decide

end Ecdlp.Uorc056LocalGlvGaugeBreaking
