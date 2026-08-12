import Mathlib
import Mathlib.NumberTheory.LegendreSymbol.Basic
import Ecdlp.Proved.M16FactorBaseFinite

/-!
# Shared definitions for the exact M16 liftable census

This module contains the public factor-base definitions and the small
computable interface shared by the isolated native certificate leaves.
It contains no native proof itself.
-/

namespace Ecdlp.M16FactorBaseLiftable

open Ecdlp.M16FactorBaseFinite

/-- The secp256k1 base field. -/
abbrev Fp := ZMod Secp256k1.p

/-- The right-hand side of the affine secp256k1 equation. -/
def rhs (x : Fp) : Fp := x ^ 3 + 7

/-- A coordinate lifts precisely when the curve right-hand side is a square. -/
def IsLiftable (x : Fp) : Prop := IsSquare (rhs x)

/-- Factor-base coordinates that lift to affine secp256k1 points. -/
abbrev LiftableFactorBaseX :=
  {x : FactorBaseX // IsLiftable x.1}

/-- Factor-base coordinates that do not lift to affine secp256k1 points. -/
abbrev NonliftableFactorBaseX :=
  {x : FactorBaseX // ¬ IsLiftable x.1}

noncomputable instance : Fintype LiftableFactorBaseX :=
  Fintype.ofFinite LiftableFactorBaseX

noncomputable instance : Fintype NonliftableFactorBaseX :=
  Fintype.ofFinite NonliftableFactorBaseX

/-- The exact-order subgroup generator used by the checked census artifact. -/
def factorBaseGenerator : Fp :=
  82848990384721873837542085774364474839392473759419163642662585798722904926012

/-- The number of three-element GLV coordinate orbits in the factor base. -/
def factorBaseOrbitCount : ℕ := 188174

/-- Indices of the explicit GLV orbit representatives. -/
abbrev GLVOrbitRep := Fin factorBaseOrbitCount

namespace Certificates

/-- The computable Euler predicate for the explicit orbit representatives. -/
@[noinline] def representativeEulerPositive (k : ℕ) : Bool :=
  decide (rhs (factorBaseGenerator ^ k) ^ (Secp256k1.p / 2) = 1)

/-- Generic tail-recursive Boolean counter used by the isolated census
certificate.

Keeping the accumulator tail recursive is important here: the native
evaluation traverses all `188174` representatives in constant stack space. -/
@[noinline] def boolCountAcc (p : ℕ → Bool) (start : ℕ) : ℕ → ℕ → ℕ
  | 0, acc => acc
  | remaining + 1, acc =>
      boolCountAcc p start remaining (acc + (p (start + remaining)).toNat)

/-- The generic tail-recursive computation agrees with `Nat.count`.

The predicate stays abstract throughout this proof, so no tactic sees or
normalizes the closed secp256k1 field computation. -/
theorem boolCountAcc_eq (p : ℕ → Bool) (start remaining acc : ℕ) :
    boolCountAcc p start remaining acc =
      acc + Nat.count
        (fun k ↦ p (start + k) = true) remaining := by
  induction remaining generalizing acc with
  | zero => rfl
  | succ remaining ih =>
    rw [boolCountAcc, ih, Nat.count_succ]
    by_cases h : p (start + remaining) = true
    · simp only [h, Bool.toNat_true, if_pos]
      ac_rfl
    · have hb : p (start + remaining) = false :=
        Bool.eq_false_of_not_eq_true h
      simp only [hb, Bool.toNat_false, Bool.false_eq_true, if_false,
        Nat.add_zero]

end Certificates

end Ecdlp.M16FactorBaseLiftable
