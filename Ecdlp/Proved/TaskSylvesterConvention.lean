import Mathlib.Data.Fin.Rev
import Ecdlp.Proved.FixedDegreeProjectiveResultant

/-!
# The frozen TASK-018 Sylvester convention

This module records the exact matrix convention used by the TASK-018 producer.
For formal degrees `m` and `n`, the matrix has size `m + n`.  Its first `n`
rows are shifted descending coefficient vectors of `f`; its remaining `m`
rows are shifted descending coefficient vectors of `g`.  Columns are the
descending monomial slots.

Mathlib stores the same coefficients in the transpose convention, with the
opposite order on both axes.  Reversing both axes and transposing therefore
preserves the determinant exactly: the coefficient unit is `1`, not merely an
unspecified sign or unit.
-/

namespace Ecdlp.TaskSylvester

open Polynomial

variable {R : Type*}

/-- A descending coefficient row of formal degree `d`, shifted right by `s`. -/
def descendingShift [Semiring R] (p : R[X]) (d s j : ℕ) : R :=
  if j ∈ Set.Icc s (s + d) then p.coeff (d - (j - s)) else 0

/-- The literal TASK-018 Sylvester matrix.

The first `n` rows are the shifts `0, …, n-1` of the descending coefficients
of `f`; the last `m` rows are the shifts `0, …, m-1` of the descending
coefficients of `g`.
-/
def taskSylvester [Semiring R] (f g : R[X]) (m n : ℕ) :
    Matrix (Fin (m + n)) (Fin (m + n)) R :=
  Matrix.of fun i j ↦
    if (i : ℕ) < n then
      descendingShift f m i j
    else
      descendingShift g n (i - n) j

/-- The literal TASK-018 matrix is Mathlib's Sylvester matrix, transposed and
reversed simultaneously on both axes. -/
theorem taskSylvester_eq_reindex_transpose [Semiring R]
    (f g : R[X]) (m n : ℕ) :
    taskSylvester f g m n =
      Matrix.reindex Fin.revPerm Fin.revPerm
        (Matrix.transpose (Polynomial.sylvester f g m n)) := by
  ext i j
  have hiN : (i : ℕ) < m + n := i.isLt
  have hjN : (j : ℕ) < m + n := j.isLt
  simp only [taskSylvester, Matrix.of_apply, Matrix.reindex_apply,
    Matrix.submatrix_apply, Matrix.transpose_apply, Fin.revPerm_symm,
    Fin.revPerm_apply]
  split_ifs with hi
  · let k : Fin n := ⟨n - 1 - i, by omega⟩
    have hrev : i.rev = Fin.natAdd m k := by
      apply Fin.ext
      simp only [Fin.val_rev, Fin.val_natAdd, k]
      omega
    rw [hrev]
    simp only [Polynomial.sylvester, Matrix.of_apply, Fin.addCases_right]
    simp only [descendingShift, Set.mem_Icc, Fin.val_rev, k]
    split_ifs <;> congr 1 <;> omega
  · let k : Fin m := ⟨m + n - 1 - i, by omega⟩
    have hrev : i.rev = Fin.castAdd n k := by
      apply Fin.ext
      simp only [Fin.val_rev, Fin.val_castAdd, k]
      omega
    rw [hrev]
    simp only [Polynomial.sylvester, Matrix.of_apply, Fin.addCases_left]
    simp only [descendingShift, Set.mem_Icc, Fin.val_rev, k]
    split_ifs <;> congr 1 <;> omega

/-- Exact determinant bridge to Mathlib's fixed-formal-degree resultant.

The coefficient unit is exactly the ring unit `1`: transpose preserves
the determinant and simultaneous row/column reversal contributes no sign.
-/
theorem det_taskSylvester_eq_resultant [CommRing R]
    (f g : R[X]) (m n : ℕ) :
    (taskSylvester f g m n).det = Polynomial.resultant f g m n := by
  rw [taskSylvester_eq_reindex_transpose]
  simp only [Matrix.det_reindex_self, Matrix.det_transpose, Polynomial.resultant]

/-- End-to-end projective common-root theorem for the literal TASK-018
determinant convention.  The degree bounds retain zero leading coefficients,
and the projective root predicate excludes the irrelevant pair `[0:0]`.
-/
theorem det_taskSylvester_eq_zero_iff_common_projective_root
    {K : Type*} [Field K] [IsAlgClosed K]
    (f g : K[X]) {m n : ℕ}
    (hm : 0 < m) (hn : 0 < n)
    (hf : f.natDegree ≤ m) (hg : g.natDegree ≤ n) :
    (taskSylvester f g m n).det = 0 ↔
      Ecdlp.ProjectiveResultant.HasCommonProjectiveRoot f g m n := by
  rw [det_taskSylvester_eq_resultant]
  exact
    Ecdlp.ProjectiveResultant.fixedDegree_resultant_eq_zero_iff_common_projective_root
      f g hm hn hf hg

/-! ## Convention fixtures -/

/-- Cubic input for the `(3,2)` row/order fixture, in descending coefficients
`[3,1,4,1]`. -/
noncomputable def fixtureFThreeTwo : ℤ[X] :=
  C 3 * X ^ 3 + C 1 * X ^ 2 + C 4 * X + C 1

/-- Quadratic input for the `(3,2)` row/order fixture, in descending
coefficients `[5,9,2]`. -/
noncomputable def fixtureGThreeTwo : ℤ[X] :=
  C 5 * X ^ 2 + C 9 * X + C 2

/-- The frozen `(3,2)` coefficient, argument, row, and column convention has
determinant exactly `41`. -/
theorem taskSylvester_fixture_three_two_det :
    (taskSylvester fixtureFThreeTwo fixtureGThreeTwo 3 2).det = 41 := by
  have hmatrix :
      taskSylvester fixtureFThreeTwo fixtureGThreeTwo 3 2 =
        !![(3 : ℤ), 1, 4, 1, 0;
           0, 3, 1, 4, 1;
           5, 9, 2, 0, 0;
           0, 5, 9, 2, 0;
           0, 0, 5, 9, 2] := by
    ext i j
    fin_cases i <;> fin_cases j <;>
      norm_num [taskSylvester, descendingShift, fixtureFThreeTwo, fixtureGThreeTwo,
        Polynomial.coeff_X, Polynomial.coeff_one]
  rw [hmatrix]
  decide +kernel

end Ecdlp.TaskSylvester
