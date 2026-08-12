import Mathlib
import Ecdlp.Proved.M16FactorBaseSymmetricGate
import Ecdlp.Proved.CurveCardinalityExact
import Ecdlp.Proved.Secp256k1GenericSecurity

/-!
# A narrow six-width coverage obstruction for the secp256k1 M16 factor base

This module counts only a deliberately fixed, target-independent translated-image
model.  A table stores one arbitrary secp256k1 point for every unordered six-element
factor-base multiset and every choice of six lift signs.  A target-independent list
of `q` residual points may then be added to a table entry, followed by one global
sign.  The resulting set has at most twice the product of the two index-set sizes.

For the exact secp256k1 M16 factor base, the signed six-index type has fewer than
`2^112` elements.  Since the full point group has more than `2^255` elements, a
fixed residual list with `q <= 2^141` cannot cover at least half of the group.

The theorem is intentionally not a lower bound for M16, ECDLP, or any calibrated
runtime model.  It does not cover target-adaptive or implicit residual generation,
streaming tables, multilevel joins, Wagner-style methods, non-translation filters,
Groebner solving, recovery, rank, or sparse linear algebra.  Here `q` counts literal
residual slots in this exact oblivious translated-image model, not field operations,
group operations, PFPO cost, time, or memory.
-/

namespace Ecdlp.M16SixWidthNoGo

open Ecdlp.M16FactorBaseFinite

/-- The complete secp256k1 affine point group used as the coverage universe. -/
abbrev SecpPoint := Ecdlp.Curve.secp256k1.toAffine.Point

/-- An unordered six-coordinate M16 table index together with all six lift signs.

Repeated coordinates are retained because `Sym FactorBaseX 6` is the type of
multisets of cardinality six, not the type of six-element subsets. -/
abbrev SignedSixIndex := Sym FactorBaseX 6 × (Fin 6 → Bool)

/-- Targets emitted by one arbitrary table payload, one entry of a fixed residual
list, and one final global sign.  Neither `emit` nor `residual` receives a target as
an argument; this target independence is the defining restriction of the model. -/
def coveredTargets {I : Type} {q : ℕ}
    (emit : I → SecpPoint) (residual : Fin q → SecpPoint) : Set SecpPoint :=
  Set.range fun z : I × (Fin q × Bool) =>
    if z.2.2 then emit z.1 + residual z.2.1
    else -(emit z.1 + residual z.2.1)

/-- The translated-image model covers at most two targets per table/residual pair.

This statement is completely generic in the finite table-index type.  Collisions
between emitted points, residuals, or signs can only decrease the range size. -/
theorem ncard_coveredTargets_le {I : Type} [Finite I] {q : ℕ}
    (emit : I → SecpPoint) (residual : Fin q → SecpPoint) :
    (coveredTargets emit residual).ncard ≤ 2 * Nat.card I * q := by
  rw [← Nat.card_coe_set_eq]
  calc
    Nat.card ↑(coveredTargets emit residual)
        ≤ Nat.card (I × (Fin q × Bool)) := by
          exact Finite.card_range_le _
    _ = 2 * Nat.card I * q := by
          simp [Nat.card_prod]
          ring

/-- The unordered six-multiset part of the exact M16 factor base has fewer than
`2^106` possible values.  The only new compiler-evaluated leaf in this module is
the final closed comparison after rewriting by the exact symmetric-cardinality
theorem. -/
theorem card_sym_factorBaseX_six_lt_two_pow_106 :
    Fintype.card (Sym FactorBaseX 6) < 2 ^ 106 := by
  rw [Ecdlp.M16FactorBaseSymmetricGate.card_sym_factorBaseX_six]
  native_decide

/-- Adding the `2^6` independent lift-sign masks leaves the complete signed
six-index type below `2^112`. -/
theorem natCard_signedSixIndex_lt_two_pow_112 :
    Nat.card SignedSixIndex < 2 ^ 112 := by
  have hsym := card_sym_factorBaseX_six_lt_two_pow_106
  calc
    Nat.card SignedSixIndex
        = Fintype.card (Sym FactorBaseX 6) * 2 ^ 6 := by
            simp [SignedSixIndex, Nat.card_eq_fintype_card]
    _ < 2 ^ 106 * 2 ^ 6 :=
          Nat.mul_lt_mul_of_pos_right hsym (by positivity)
    _ = 2 ^ 112 := by norm_num [pow_add]

/-- If the fixed residual list has at most `2^141` slots, the covered set is
strictly smaller than half of the full secp256k1 point group. -/
theorem no_half_coverage_of_two_pow_141_probe_bound
    {q : ℕ} (hq : q ≤ 2 ^ 141)
    (emit : SignedSixIndex → SecpPoint)
    (residual : Fin q → SecpPoint) :
    2 * (coveredTargets emit residual).ncard < Nat.card SecpPoint := by
  have hcover :
      (coveredTargets emit residual).ncard ≤ 2 * Nat.card SignedSixIndex * q :=
    ncard_coveredTargets_le emit residual
  have hindex : Nat.card SignedSixIndex < 2 ^ 112 :=
    natCard_signedSixIndex_lt_two_pow_112
  have hsmall :
      2 * (coveredTargets emit residual).ncard < 2 ^ 255 := by
    calc
      2 * (coveredTargets emit residual).ncard
          ≤ 2 * (2 * Nat.card SignedSixIndex * q) :=
            Nat.mul_le_mul_left 2 hcover
      _ = 4 * Nat.card SignedSixIndex * q := by ring
      _ ≤ 4 * Nat.card SignedSixIndex * 2 ^ 141 :=
            Nat.mul_le_mul_left (4 * Nat.card SignedSixIndex) hq
      _ < 4 * 2 ^ 112 * 2 ^ 141 := by
            exact Nat.mul_lt_mul_of_pos_right
              (Nat.mul_lt_mul_of_pos_left hindex (by norm_num))
              (by positivity)
      _ = 2 ^ 255 := by norm_num [pow_add]
  calc
    2 * (coveredTargets emit residual).ncard
        < 2 ^ 255 := hsmall
    _ < Secp256k1.n := Ecdlp.GenericGroup.two_pow_255_lt_secp256k1_n
    _ = Nat.card SecpPoint := Ecdlp.Curve.secp256k1_card_point_eq_n.symm

/-- Consequently, covering at least half of secp256k1 in this exact fixed-list
translated-image model requires strictly more than `2^141` residual slots. -/
theorem half_coverage_requires_more_than_two_pow_141_probes
    {q : ℕ}
    (emit : SignedSixIndex → SecpPoint)
    (residual : Fin q → SecpPoint)
    (hhalf : Nat.card SecpPoint ≤ 2 * (coveredTargets emit residual).ncard) :
    2 ^ 141 < q := by
  by_contra hq
  have hq' : q ≤ 2 ^ 141 := by omega
  have hno := no_half_coverage_of_two_pow_141_probe_bound hq' emit residual
  omega

end Ecdlp.M16SixWidthNoGo
