import Mathlib

/-!
# UORC-056 C54 charged moduli-tangent transfer

This file kernel-checks the elementary algebraic core of C54.  It does not
formalize elliptic curves, division-polynomial automatic differentiation, the
finite-field replay, orbit-factor density, or an unrestricted circuit lower
bound.
-/

namespace Ecdlp.Uorc056ChargedModuliTangentTransfer

/-- If the charged product is `n = a*b` and `b` is nonzero, the second charged
    coordinate generates the first over the neutral field. -/
theorem chargedRankOne
    {K : Type*} [Field K]
    (a b n : K) (hb : b ≠ 0) (hprod : a * b = n) :
    a = n / b := by
  exact (eq_div_iff hb).2 hprod

/-- Simultaneous endpoint negation preserves the charged product. -/
theorem chargedProductIsNeutral
    {R : Type*} [CommRing R] (a b : R) :
    (-a) * (-b) = a * b := by
  ring

/-- Simultaneous endpoint negation also preserves the charged ratio when the
    denominator is nonzero. -/
theorem chargedRatioIsNeutral
    {K : Type*} [Field K] (a b : K) :
    (-a) / (-b) = a / b := by
  simp

/-- The public endpoint cocycle reconstructs the normalized coordinate charge.

Here `B(P)=e(P)/e(G)` and
`C_B(P,Q)=e(G)e(P+Q)/(e(P)e(Q))`. -/
theorem endpointCocycleReconstructs
    {K : Type*} [Field K]
    (eG eP eQ eR : K)
    (hG : eG ≠ 0) (hP : eP ≠ 0) (hQ : eQ ≠ 0) :
    (eG * eR / (eP * eQ)) * (eP / eG) * (eQ / eG)
      = eR / eG := by
  field_simp [hG, hP, hQ] <;> ring

/-- One neutral collision with opposite desired outputs rules out every decoder
    that receives only that neutral state. -/
theorem equalNeutralStateCannotDecodeOpposite
    {S K : Type*} [Field K]
    (decode : S → K) (left right : S)
    (hsame : left = right)
    (hleft : decode left = 1)
    (hright : decode right = -1)
    (htwo : (2 : K) ≠ 0) :
    False := by
  have hone : (1 : K) = -1 := by
    calc
      (1 : K) = decode left := hleft.symm
      _ = decode right := by rw [hsame]
      _ = -1 := hright
  have hz : (2 : K) = 0 := by
    calc
      (2 : K) = 1 - (-1) := by ring
      _ = 0 := sub_eq_zero.mpr hone
  exact htwo hz

/-- Negating every root changes each linear orbit factor by one minus sign after
    replacing `X` with `-X`. -/
theorem negatedLinearFactor
    {R : Type*} [CommRing R] (X value : R) :
    X - (-value) = -((-X) - value) := by
  ring


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpOrdTwo : Nat :=
  (secpN - 1) / 64

/-- The certified doubling order is odd. -/
theorem secpDoublingOrderOdd : secpOrdTwo % 2 = 1 := by
  native_decide

/-- Adding negation to the odd doubling orbit leaves 32 pair-quotient cycles. -/
theorem secpPairCycleCount :
    (secpN - 1) / (2 * secpOrdTwo) = 32 := by
  native_decide

end Ecdlp.Uorc056ChargedModuliTangentTransfer
