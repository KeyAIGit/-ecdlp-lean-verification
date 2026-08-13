import Mathlib

/-!
# Independent theta row normalization

This file formalizes the linear-algebra core of
`INDEPENDENT-THETA-ROW-NORMALIZATION-051`.

For one common section basis, independent local trivializations multiply the
evaluation matrix on the left by a diagonal matrix.  A common basis change
multiplies on the right by one matrix.  The determinant therefore factors as
the product of row scalars, the original determinant, and the basis-change
determinant.

The file does not formalize line bundles, theta functions, elliptic curves,
secp256k1, parity, or ECDLP.
-/

open scoped BigOperators

namespace Ecdlp.ParityLift

/-- Independent scalar row trivializations and one common basis change factor
completely out of the determinant. -/
theorem det_diagonal_mul_commonBasis
    {ι R : Type*}
    [Fintype ι] [DecidableEq ι] [CommRing R]
    (rowScale : ι → R)
    (evaluation basisChange : Matrix ι ι R) :
    Matrix.det (Matrix.diagonal rowScale * evaluation * basisChange)
      = (∏ index, rowScale index)
          * Matrix.det evaluation
          * Matrix.det basisChange := by
  rw [Matrix.det_mul, Matrix.det_mul, Matrix.det_diagonal]

/-- If the product of row scalars is one, diagonal row rescaling leaves the
determinant unchanged. -/
theorem det_diagonal_mul_eq_of_product_eq_one
    {ι R : Type*}
    [Fintype ι] [DecidableEq ι] [CommRing R]
    (rowScale : ι → R)
    (evaluation : Matrix ι ι R)
    (hproduct : ∏ index, rowScale index = 1) :
    Matrix.det (Matrix.diagonal rowScale * evaluation)
      = Matrix.det evaluation := by
  rw [Matrix.det_mul, Matrix.det_diagonal, hproduct, one_mul]

/-- After dividing out a nonzero common determinant and basis constant, the
entire residual of a row-trivialized determinant is the product of row scales. -/
theorem rowTrivialization_residual
    {K : Type*} [Field K]
    (transformed common basisConstant rowProduct : K)
    (hcommon : common ≠ 0)
    (hbasis : basisConstant ≠ 0)
    (hfactor : transformed = rowProduct * common * basisConstant) :
    transformed / (common * basisConstant) = rowProduct := by
  rw [hfactor]
  field_simp

end Ecdlp.ParityLift
