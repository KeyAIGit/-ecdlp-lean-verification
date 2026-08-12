import Mathlib
import Ecdlp.Proved.M16FactorBaseLiftable
import Ecdlp.Proved.M16SixWidthNoGo
import Ecdlp.Proved.M16SolverGate

/-!
# A liftability-aware six-width coverage obstruction for secp256k1 M16

After restricting the M16 coordinate factor base to the exact `283527`
coordinates that lift to secp256k1, the unordered width-six representation has
exactly `721534357111870307687559424092` entries.  Adding six independent lift
signs gives `46178198855159699692003803141888` signed table indices.

This module reuses the fixed translated-image model from
`M16SixWidthNoGo.lean`: a table stores one arbitrary secp256k1 point for each
signed index, and a fixed, target-independent list of `q` residual points is
added to those table entries, followed by one global sign.  Exact arithmetic
then shows that `q <= 2^148` cannot cover half of the full point group.

This is deliberately not a lower bound for M16, ECDLP, or a calibrated runtime
model.  It does not cover target-adaptive or implicit residual generation,
streaming tables, multilevel joins, Wagner-style methods, non-translation
filters, Groebner solving, recovery, rank, or sparse linear algebra.  Here `q`
counts literal residual slots in this exact oblivious translated-image model,
not field operations, group operations, PFPO cost, time, or memory.
-/

namespace Ecdlp.M16LiftableSixWidthNoGo

open Ecdlp.M16FactorBaseLiftable
open Ecdlp.M16SixWidthNoGo
open Ecdlp.M16SolverGate

/-! ## Exact liftable symmetric-power counts -/

/-- Exact number of size-six multisets from the liftable M16 factor base. -/
theorem card_sym_liftableFactorBaseX_six :
    Fintype.card (Sym LiftableFactorBaseX 6) =
      721534357111870307687559424092 := by
  rw [Sym.card_sym_eq_choose, card_liftableFactorBaseX]
  norm_num [Nat.choose_eq_descFactorial_div_factorial,
    Nat.descFactorial, Nat.factorial]

/-- The liftable size-six multiset representation fits below the desk ceiling. -/
theorem card_sym_liftableFactorBaseX_six_le_budget :
    Fintype.card (Sym LiftableFactorBaseX 6) ≤ maxRelationTermBudget := by
  rw [card_sym_liftableFactorBaseX_six]
  norm_num [maxRelationTermBudget]

/-- Exact number of size-seven multisets from the liftable M16 factor base. -/
theorem card_sym_liftableFactorBaseX_seven :
    Fintype.card (Sym LiftableFactorBaseX 7) =
      29225542982142846278510969455868148 := by
  rw [Sym.card_sym_eq_choose, card_liftableFactorBaseX]
  norm_num [Nat.choose_eq_descFactorial_div_factorial,
    Nat.descFactorial, Nat.factorial]

/-- The desk ceiling is already below the liftable size-seven multiset count. -/
theorem budget_lt_card_sym_liftableFactorBaseX_seven :
    maxRelationTermBudget < Fintype.card (Sym LiftableFactorBaseX 7) := by
  rw [card_sym_liftableFactorBaseX_seven]
  norm_num [maxRelationTermBudget]

/-! ## Fixed-oblivious translated-image coverage -/

/-- A liftability-aware unordered six-coordinate table index together with all
six independent affine lift signs.  Repeated coordinates are retained. -/
abbrev LiftableSignedSixIndex :=
  Sym LiftableFactorBaseX 6 × (Fin 6 → Bool)

/-- Exact number of signed liftable width-six table indices. -/
theorem natCard_liftableSignedSixIndex :
    Nat.card LiftableSignedSixIndex =
      46178198855159699692003803141888 := by
  calc
    Nat.card LiftableSignedSixIndex =
        Fintype.card (Sym LiftableFactorBaseX 6) * 2 ^ 6 := by
      simp [LiftableSignedSixIndex, Nat.card_eq_fintype_card]
    _ = 46178198855159699692003803141888 := by
      rw [card_sym_liftableFactorBaseX_six]
      norm_num

/-- Closed arithmetic at the exact signed-index size.  This is the only new
compiler-evaluated leaf in this module. -/
private theorem closed_two_pow_148_half_bound :
    4 * 46178198855159699692003803141888 * 2 ^ 148 < Secp256k1.n := by
  native_decide

/-- If the fixed residual list has at most `2^148` slots, the covered set is
strictly smaller than half of the full secp256k1 point group. -/
theorem no_half_coverage_of_two_pow_148_probe_bound
    {q : ℕ} (hq : q ≤ 2 ^ 148)
    (emit : LiftableSignedSixIndex → SecpPoint)
    (residual : Fin q → SecpPoint) :
    2 * (coveredTargets emit residual).ncard < Nat.card SecpPoint := by
  have hcover :
      (coveredTargets emit residual).ncard ≤
        2 * Nat.card LiftableSignedSixIndex * q :=
    ncard_coveredTargets_le emit residual
  calc
    2 * (coveredTargets emit residual).ncard
        ≤ 2 * (2 * Nat.card LiftableSignedSixIndex * q) :=
      Nat.mul_le_mul_left 2 hcover
    _ = 4 * Nat.card LiftableSignedSixIndex * q := by ring
    _ ≤ 4 * Nat.card LiftableSignedSixIndex * 2 ^ 148 :=
      Nat.mul_le_mul_left (4 * Nat.card LiftableSignedSixIndex) hq
    _ < Secp256k1.n := by
      rw [natCard_liftableSignedSixIndex]
      exact closed_two_pow_148_half_bound
    _ = Nat.card SecpPoint :=
      Ecdlp.Curve.secp256k1_card_point_eq_n.symm

/-- Consequently, covering at least half of secp256k1 in this exact fixed-list
translated-image model requires strictly more than `2^148` residual slots. -/
theorem half_coverage_requires_more_than_two_pow_148_probes
    {q : ℕ}
    (emit : LiftableSignedSixIndex → SecpPoint)
    (residual : Fin q → SecpPoint)
    (hhalf : Nat.card SecpPoint ≤ 2 * (coveredTargets emit residual).ncard) :
    2 ^ 148 < q := by
  by_contra hq
  have hq' : q ≤ 2 ^ 148 := by omega
  have hno :=
    no_half_coverage_of_two_pow_148_probe_bound hq' emit residual
  omega

end Ecdlp.M16LiftableSixWidthNoGo
