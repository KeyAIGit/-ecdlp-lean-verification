import Mathlib

/-!
# A narrow arithmetic gate for the M16 solver cost placeholder

The symbolic M16 desk calculation records the uncalibrated optimistic ceiling

`B = 26470005625446268964608938870039985`.

This file exposes a Boolean gate for an externally supplied relation-solver
term count and proves exact numeric boundary facts.  It does not estimate that
term count, calibrate field operations against group operations, establish a
solving degree, or prove an ECDLP complexity bound.
-/

namespace Ecdlp.M16SolverGate

/-- The exact smooth-subgroup x-coordinate degree used by the M16 route. -/
def factorBaseDegree : ℕ := 564522

/-- The desk calculation's uncalibrated optimistic per-system term ceiling. -/
def maxRelationTermBudget : ℕ :=
  26470005625446268964608938870039985

/-- Accept an externally supplied term count exactly when it fits the ceiling. -/
def relationTermGate (relationTerms : ℕ) : Bool :=
  decide (relationTerms ≤ maxRelationTermBudget)

/-- The Boolean gate is only the decidable form of the stated inequality. -/
theorem relationTermGate_spec (relationTerms : ℕ) :
    relationTermGate relationTerms = decide (relationTerms ≤ maxRelationTermBudget) := rfl

/-- The exact ceiling is accepted. -/
theorem relationTermGate_at_max :
    relationTermGate maxRelationTermBudget = true := by
  native_decide

/-- The successor of the exact ceiling is rejected. -/
theorem relationTermGate_succ_max_fails :
    relationTermGate (maxRelationTermBudget + 1) = false := by
  native_decide

/-- Logical interface to the named ceiling. -/
theorem relationTermGate_iff_le_max (relationTerms : ℕ) :
    relationTermGate relationTerms = true ↔
      relationTerms ≤ maxRelationTermBudget := by
  simp [relationTermGate]

/-- Logical interface with the ceiling expanded to its exact integer value. -/
theorem relationTermGate_iff_le_exact (relationTerms : ℕ) :
    relationTermGate relationTerms = true ↔
      relationTerms ≤ 26470005625446268964608938870039985 := by
  simpa [maxRelationTermBudget] using relationTermGate_iff_le_max relationTerms

/-- The ceiling is at least `2^114`. -/
theorem two_pow_114_le_maxRelationTermBudget :
    2 ^ 114 ≤ maxRelationTermBudget := by
  native_decide

/-- The ceiling is below `2^115`. -/
theorem maxRelationTermBudget_lt_two_pow_115 :
    maxRelationTermBudget < 2 ^ 115 := by
  native_decide

/-- The exact binary-size window for the ceiling. -/
theorem maxRelationTermBudget_bit_window :
    2 ^ 114 ≤ maxRelationTermBudget ∧
      maxRelationTermBudget < 2 ^ 115 :=
  ⟨two_pow_114_le_maxRelationTermBudget,
    maxRelationTermBudget_lt_two_pow_115⟩

/-- A fifth power of the factor-base degree fits below the ceiling. -/
theorem factorBaseDegree_pow_five_le_maxRelationTermBudget :
    factorBaseDegree ^ 5 ≤ maxRelationTermBudget := by
  native_decide

/-- A sixth power of the factor-base degree already exceeds the ceiling. -/
theorem maxRelationTermBudget_lt_factorBaseDegree_pow_six :
    maxRelationTermBudget < factorBaseDegree ^ 6 := by
  native_decide

/-- The exact factor-base-degree window for the ceiling. -/
theorem maxRelationTermBudget_degree_window :
    factorBaseDegree ^ 5 ≤ maxRelationTermBudget ∧
      maxRelationTermBudget < factorBaseDegree ^ 6 :=
  ⟨factorBaseDegree_pow_five_le_maxRelationTermBudget,
    maxRelationTermBudget_lt_factorBaseDegree_pow_six⟩

/-- Any supplied term count bounded below by `D^6` necessarily fails this
narrow arithmetic gate. -/
theorem relationTermGate_fails_of_degree_six_lower_bound
    {relationTerms : ℕ}
    (h : factorBaseDegree ^ 6 ≤ relationTerms) :
    relationTermGate relationTerms = false := by
  rw [Bool.eq_false_iff]
  intro htrue
  have hle := (relationTermGate_iff_le_max relationTerms).mp htrue
  exact (not_lt_of_ge hle)
    (lt_of_lt_of_le maxRelationTermBudget_lt_factorBaseDegree_pow_six h)

end Ecdlp.M16SolverGate
