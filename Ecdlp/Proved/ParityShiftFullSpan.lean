import Mathlib

/-!
# Exact parity has full cyclic shift span on odd cycles

The exact canonical parity word on an odd cycle has one wrap-around seam.  Adding the
word to its one-step cyclic shift cancels everywhere except at that seam.  Consequently,
any linear space containing all cyclic shifts also contains every standard basis vector.

The concrete cyclic indexing is recorded by `parity_seam`; the linear-algebraic kernel is
recorded by `span_eq_top_of_two_shift_delta` and
`submodule_eq_top_of_two_shift_delta_mem`.
-/

namespace Ecdlp.Proved.ParityShiftFullSpan

/-- The predecessor used by the canonical representatives `0, ..., n-1`.
At the wrap-around point `0`, the predecessor is `n-1`. -/
def cyclicPrev (n k : ℕ) : ℕ :=
  if k = 0 then n - 1 else k - 1

/-- On an odd cycle, the alternating parity signs cancel against their predecessors
at every nonzero index and leave the value `2` at the unique wrap-around seam. -/
theorem parity_seam {n k : ℕ} (hn : Odd n) :
    (-1 : ℚ) ^ k + (-1 : ℚ) ^ cyclicPrev n k = if k = 0 then 2 else 0 := by
  by_cases hk : k = 0
  · subst k
    rcases hn with ⟨m, hm⟩
    subst n
    norm_num [cyclicPrev, pow_add, pow_mul]
  · have hsucc : k = (k - 1) + 1 := by omega
    have hpow : (-1 : ℚ) ^ k = (-1 : ℚ) ^ ((k - 1) + 1) :=
      congrArg (fun t : ℕ => (-1 : ℚ) ^ t) hsucc
    simp only [cyclicPrev, hk, if_false]
    rw [hpow, pow_succ]
    ring

/-- If every standard basis vector is a scalar multiple of the sum of two members of a
family `u`, then the family spans the complete function space.  In the parity
application, `u j` is the `j`-th cyclic shift of the parity word and the scalar is `1/2`.
-/
theorem span_eq_top_of_two_shift_delta
    {R ι : Type*} [Semiring R] [Fintype ι] [DecidableEq ι]
    (u : ι → (ι → R)) (next : ι → ι) (c : R)
    (hdelta : ∀ j, (Pi.basisFun R ι) j = c • (u j + u (next j))) :
    Submodule.span R (Set.range u) = ⊤ := by
  refine (Submodule.eq_top_iff_forall_basis_mem (Pi.basisFun R ι)).2 ?_
  intro j
  rw [hdelta j]
  exact (Submodule.span R (Set.range u)).smul_mem c
    ((Submodule.span R (Set.range u)).add_mem
      (Submodule.subset_span (Set.mem_range_self j))
      (Submodule.subset_span (Set.mem_range_self (next j))))

/-- A linear subspace containing the relevant two-shift combinations must be the whole
function space.  Applied to a translation-invariant subspace containing exact parity,
this rules out any proper low-dimensional linear translation-stable compression. -/
theorem submodule_eq_top_of_two_shift_delta_mem
    {R ι : Type*} [Semiring R] [Fintype ι] [DecidableEq ι]
    (V : Submodule R (ι → R))
    (u : ι → (ι → R)) (next : ι → ι) (c : R)
    (hu : ∀ j, u j ∈ V)
    (hdelta : ∀ j, (Pi.basisFun R ι) j = c • (u j + u (next j))) :
    V = ⊤ := by
  refine (Submodule.eq_top_iff_forall_basis_mem (Pi.basisFun R ι)).2 ?_
  intro j
  rw [hdelta j]
  exact V.smul_mem c (V.add_mem (hu j) (hu (next j)))

end Ecdlp.Proved.ParityShiftFullSpan
