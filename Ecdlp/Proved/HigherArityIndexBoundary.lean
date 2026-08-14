import Mathlib

/-!
# Explicit higher-arity index/resultant boundary

This file formalizes the arithmetic core of
`UORC056-HIGHER-ARITY-INDEX-B5`.

At the root of an explicit binary resultant tree, let `A` and `B` be the two
represented child degrees, `c` the number of explicitly evaluated leftovers,
and `C` a common upper bound. Coverage `M <= A*B+c` implies `M <= C^2+C`.

The file does not formalize elliptic curves, resultants, theta functions,
secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- An explicit binary-resultant root cannot cover more than `C^2+C` target
factors when both child degrees and the residual list are bounded by `C`. -/
theorem explicitResultantRoot_squareBoundary
    (A B c C M : ℤ)
    (hA0 : 0 ≤ A)
    (hB0 : 0 ≤ B)
    (hc0 : 0 ≤ c)
    (hC0 : 0 ≤ C)
    (hAC : A ≤ C)
    (hBC : B ≤ C)
    (hcC : c ≤ C)
    (hcover : M ≤ A * B + c) :
    M ≤ C ^ 2 + C := by
  have hproduct : A * B ≤ C * C := by
    exact mul_le_mul hAC hBC hB0 hC0
  nlinarith

/-- With no explicit residual list, the same model forces the target size below
the square of the maximum child degree. -/
theorem explicitResultantRoot_noResidual
    (A B C M : ℤ)
    (hA0 : 0 ≤ A)
    (hB0 : 0 ≤ B)
    (hC0 : 0 ≤ C)
    (hAC : A ≤ C)
    (hBC : B ≤ C)
    (hcover : M ≤ A * B) :
    M ≤ C ^ 2 := by
  have hproduct : A * B ≤ C * C := by
    exact mul_le_mul hAC hBC hB0 hC0
  nlinarith

/-- The three-set iterated construction is the special case where the two root
input degrees multiply to the ideal signed coverage. -/
theorem threeSetIntermediate_squareBoundary
    (A B C M : ℤ)
    (hA0 : 0 ≤ A)
    (hB0 : 0 ≤ B)
    (hC0 : 0 ≤ C)
    (hAC : A ≤ C)
    (hBC : B ≤ C)
    (hcover : M ≤ A * B) :
    M ≤ C ^ 2 := by
  exact explicitResultantRoot_noResidual A B C M hA0 hB0 hC0 hAC hBC hcover

end Ecdlp.ParityLift
