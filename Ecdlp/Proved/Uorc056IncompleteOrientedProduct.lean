import Mathlib

/-!
# UORC-056 C41 incomplete oriented-product boundary

This file kernel-checks the exact secp256k1 dimension arithmetic used by C41.
The frozen finite-field ranks, polynomial-decomposition screens, and
Berlekamp-Massey calculations are independently replayed by Python and are not
mislabelled as general Lean theorems.
-/

namespace Ecdlp.Uorc056IncompleteOrientedProduct

/-- Number of bivariate monomials of total degree at most `d`. -/
def totalMonomials (d : Nat) : Nat :=
  (d + 1) * (d + 2) / 2

/-- Number of diagonal monomials fixed by swapping two variables. -/
def diagonalMonomials (d : Nat) : Nat :=
  d / 2 + 1

/-- Dimension of the swap-symmetric total-degree subspace. -/
def symmetricMonomials (d : Nat) : Nat :=
  (totalMonomials d + diagonalMonomials d) / 2

/-- Dimension of the swap-antisymmetric total-degree subspace. -/
def antisymmetricMonomials (d : Nat) : Nat :=
  (totalMonomials d - diagonalMonomials d) / 2


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpRows : Nat :=
  secpN - 1


def secpPairs : Nat :=
  secpRows / 2


def secpInterpolationDegree : Nat :=
  481231938336009023090067544955250113852

/-- `secpInterpolationDegree` is the first total degree whose complete
    bivariate monomial count exceeds the `n-1` sampled rows. -/
theorem secpGeneralBivariateThreshold :
    totalMonomials (secpInterpolationDegree - 1) ≤ secpRows ∧
      secpRows < totalMonomials secpInterpolationDegree := by
  native_decide

/-- The same exact degree is the first one whose swap-symmetric monomial
    subspace exceeds the `(n-1)/2` unordered negation pairs. -/
theorem secpSwapSymmetricThreshold :
    symmetricMonomials (secpInterpolationDegree - 1) ≤ secpPairs ∧
      secpPairs < symmetricMonomials secpInterpolationDegree := by
  native_decide

/-- The ordinary rational-graph interpolation threshold has degree
    `(n-1)/2`: at that degree the two polynomial sides have two more columns
    than the sampled rows. -/
theorem secpRationalTransitionThreshold :
    2 * secpPairs = secpRows ∧
      2 * (secpPairs + 1) = secpRows + 2 := by
  native_decide

/-- The first bivariate dimension threshold is a 129-bit number. -/
theorem secpInterpolationDegreeBitBoundary :
    2 ^ 128 < secpInterpolationDegree ∧
      secpInterpolationDegree < 2 ^ 129 := by
  native_decide

/-- The one-variable rational-transition threshold remains at the 255-bit
    half-order scale. -/
theorem secpRationalDegreeBitBoundary :
    2 ^ 254 < secpPairs ∧ secpPairs < 2 ^ 255 := by
  native_decide

end Ecdlp.Uorc056IncompleteOrientedProduct
