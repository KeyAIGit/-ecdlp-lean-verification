import Mathlib
import Ecdlp.Proved.M16FactorBaseFinite
import Ecdlp.Proved.M16SolverGate

/-!
# Exact unordered tuple counts for the M16 factor base

`Sym FactorBaseX k` is the type of size-`k` multisets, so it retains repeated
x-coordinates while quotienting only by permutation.  Stars-and-bars gives its
exact cardinality.  At the desk ceiling recorded by `M16SolverGate`, width six
fits and width seven does not.

These are representation counts only.  They do not show that the coordinates
lift to curve points, that a target relation exists, or that any solver runs
within the stated ceiling.
-/

namespace Ecdlp.M16FactorBaseSymmetricGate

open Ecdlp.M16FactorBaseFinite
open Ecdlp.M16SolverGate

/-- Exact number of size-six multisets from the full root-based factor base. -/
theorem card_sym_factorBaseX_six :
    Fintype.card (Sym FactorBaseX 6) =
      44953578811715702293911690083685 := by
  rw [Sym.card_sym_eq_choose, card_factorBaseX]
  norm_num [Nat.choose_eq_descFactorial_div_factorial,
    Nat.descFactorial, Nat.factorial]

/-- The size-six multiset representation fits below the desk ceiling. -/
theorem card_sym_factorBaseX_six_le_budget :
    Fintype.card (Sym FactorBaseX 6) ≤ maxRelationTermBudget := by
  rw [card_sym_factorBaseX_six]
  norm_num [maxRelationTermBudget]

/-- Exact number of size-seven multisets from the full root-based factor base. -/
theorem card_sym_factorBaseX_seven :
    Fintype.card (Sym FactorBaseX 7) =
      3625364848488605997796768368508932240 := by
  rw [Sym.card_sym_eq_choose, card_factorBaseX]
  norm_num [Nat.choose_eq_descFactorial_div_factorial,
    Nat.descFactorial, Nat.factorial]

/-- The desk ceiling is strictly below the size-seven multiset count. -/
theorem budget_lt_card_sym_factorBaseX_seven :
    maxRelationTermBudget < Fintype.card (Sym FactorBaseX 7) := by
  rw [card_sym_factorBaseX_seven]
  norm_num [maxRelationTermBudget]

end Ecdlp.M16FactorBaseSymmetricGate
