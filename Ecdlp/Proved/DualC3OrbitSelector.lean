import Mathlib

/-!
# Dual C3 orbit selector: elementary obstruction core

This file formalizes two abstract facts used by
`DUAL-C3-ORBIT-SELECTOR-033`.

* A vector in a field cannot be fixed by multiplication by a nontrivial scalar
  unless it is zero.
* A predicate invariant under an involution cannot equal a target that flips
  under that involution on both members of a pair.

The file does not formalize elliptic curves, Frobenius eigenspaces, CM, Weil
pairings, field-of-definition degrees, or secp256k1 arithmetic.
-/

namespace Ecdlp.ParityLift

/-- A nontrivial scalar eigenaction has no nonzero fixed vector over a field. -/
theorem nontrivialScalar_fixed_forces_zero
    {K : Type*} [Field K]
    (a x : K)
    (ha : a ≠ 1)
    (hfix : a * x = x) :
    x = 0 := by
  have hmul : (a - 1) * x = 0 := by
    calc
      (a - 1) * x = a * x - x := by ring
      _ = 0 := sub_eq_zero.mpr hfix
  rcases mul_eq_zero.mp hmul with hscalar | hx
  · exact False.elim (ha (sub_eq_zero.mp hscalar))
  · exact hx

/-- The same statement for a scalar power. In the Frobenius application the
scalar is `p^m mod n`. -/
theorem nontrivialScalarPower_fixed_forces_zero
    {K : Type*} [Field K]
    (a x : K) (m : ℕ)
    (ha : a ^ m ≠ 1)
    (hfix : (a ^ m) * x = x) :
    x = 0 :=
  nontrivialScalar_fixed_forces_zero (a ^ m) x ha hfix

/-- An invariant decoder cannot equal a target which is complemented by the
same symmetry on both points of a pair. -/
theorem invariantDecoder_cannot_decode_flippingTarget
    {A : Type*}
    (sigma : A → A)
    (decode target : A → Bool)
    (x : A)
    (hinvariant : decode (sigma x) = decode x)
    (hflip : target (sigma x) = !(target x))
    (hcorrectX : decode x = target x)
    (hcorrectSigma : decode (sigma x) = target (sigma x)) :
    False := by
  have h : target x = !(target x) := by
    calc
      target x = decode x := hcorrectX.symm
      _ = decode (sigma x) := hinvariant.symm
      _ = target (sigma x) := hcorrectSigma
      _ = !(target x) := hflip
  cases htarget : target x <;> simp [htarget] at h

end Ecdlp.ParityLift
