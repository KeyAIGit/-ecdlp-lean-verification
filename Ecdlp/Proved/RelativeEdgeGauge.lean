import Mathlib

/-!
# Relative edge gauge

A binary label attached to two endpoints is unchanged when the same global
binary offset is added at both endpoints. Finite sums of such labels retain
that invariance. This file contains only elementary `ZMod 2` algebra.
-/

namespace Ecdlp.ParityLift

def globalBinaryShift {I : Type*} (label : I → ZMod 2) : I → ZMod 2 :=
  fun index => label index + 1

def twoEndpointLabel {I : Type*}
    (label : I → ZMod 2) (left right : I) : ZMod 2 :=
  label left + label right

theorem twoEndpointLabel_shift_invariant
    {I : Type*} (label : I → ZMod 2) (left right : I) :
    twoEndpointLabel (globalBinaryShift label) left right =
      twoEndpointLabel label left right := by
  simp [twoEndpointLabel, globalBinaryShift]
  ring

theorem twoEndpointLabelSum_shift_invariant
    {I : Type*} (label : I → ZMod 2) (edges : List (I × I)) :
    (edges.map fun edge =>
      twoEndpointLabel (globalBinaryShift label) edge.1 edge.2).sum =
    (edges.map fun edge => twoEndpointLabel label edge.1 edge.2).sum := by
  induction edges with
  | nil => simp
  | cons edge tail ih =>
      simp [twoEndpointLabel_shift_invariant, ih]

theorem globalBinaryShift_ne_at
    {I : Type*} (label : I → ZMod 2) (target : I) :
    globalBinaryShift label target ≠ label target := by
  intro equality
  have one_eq_zero : (1 : ZMod 2) = 0 := by
    calc
      (1 : ZMod 2) = (label target + 1) - label target := by ring
      _ = 0 := by
        rw [← equality]
        simp [globalBinaryShift]
  norm_num at one_eq_zero

end Ecdlp.ParityLift
