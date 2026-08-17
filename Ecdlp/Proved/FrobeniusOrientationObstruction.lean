import Mathlib

/-!
# Frobenius orientation obstruction

This file formalizes the elementary logical core of
`FROBENIUS-ORIENTATION-OBSTRUCTION-030`.

If a decoder is invariant under a map, then it is invariant under every finite
iterate of that map. If one iterate sends a query to its negative while the
target is complemented by negation, the decoder cannot be correct on both
points.

In the intended application, the map is Frobenius on a cyclotomic period,
half of its multiplicative-order cycle acts as conjugation/negation, and the
target is the generator-relative GLV carry.

The file does not formalize finite fields, cyclotomic periods, elliptic curves,
or the secp256k1 order certificate.
-/

namespace Ecdlp.ParityLift

/-- Forward iteration with the convention used in this file. -/
def iterateForward
    {A : Type*} (f : A → A) : ℕ → A → A
  | 0, x => x
  | m + 1, x => f (iterateForward f m x)

@[simp]
theorem iterateForward_zero
    {A : Type*} (f : A → A) (x : A) :
    iterateForward f 0 x = x := rfl

@[simp]
theorem iterateForward_succ
    {A : Type*} (f : A → A) (m : ℕ) (x : A) :
    iterateForward f (m + 1) x = f (iterateForward f m x) := rfl

/-- Invariance under one application implies invariance under every finite
forward iterate. -/
theorem invariant_under_iterateForward
    {A B : Type*}
    (f : A → A) (decode : A → B)
    (hinvariant : ∀ x, decode (f x) = decode x) :
    ∀ m x, decode (iterateForward f m x) = decode x := by
  intro m
  induction m with
  | zero =>
      intro x
      rfl
  | succ m ih =>
      intro x
      rw [iterateForward_succ, hinvariant]
      exact ih x

/-- A map-invariant decoder cannot decode an anti-invariant target when one
iterate of the map equals negation. -/
theorem invariantDecoder_cannot_decode_iterateNegation
    {A : Type*} [Neg A]
    (f : A → A)
    (decode target : A → Bool)
    (m : ℕ) (q : A)
    (hinvariant : ∀ x, decode (f x) = decode x)
    (hhalf : iterateForward f m q = -q)
    (hflip : target (-q) = !(target q))
    (hcorrectQ : decode q = target q)
    (hcorrectNegQ : decode (-q) = target (-q)) :
    False := by
  have hiter := invariant_under_iterateForward f decode hinvariant m q
  have hsame : decode (-q) = decode q := by
    rw [← hhalf]
    exact hiter
  have h : target q = !(target q) := by
    calc
      target q = decode q := hcorrectQ.symm
      _ = decode (-q) := hsame.symm
      _ = target (-q) := hcorrectNegQ
      _ = !(target q) := hflip
  cases htarget : target q <;> simp [htarget] at h

/-- Contrapositive form: any decoder correct on both members of an
anti-invariant pair must break invariance somewhere before the iterate reaches
negation. -/
theorem correctAntiInvariantTarget_forces_noninvariance
    {A : Type*} [Neg A]
    (f : A → A)
    (decode target : A → Bool)
    (m : ℕ) (q : A)
    (hhalf : iterateForward f m q = -q)
    (hflip : target (-q) = !(target q))
    (hcorrectQ : decode q = target q)
    (hcorrectNegQ : decode (-q) = target (-q)) :
    ¬(∀ x, decode (f x) = decode x) := by
  intro hinvariant
  exact invariantDecoder_cannot_decode_iterateNegation
    f decode target m q hinvariant hhalf hflip hcorrectQ hcorrectNegQ

end Ecdlp.ParityLift
