import Mathlib

/-!
# Oriented principal Pell boundary

This file formalizes elementary algebraic and combinatorial statements used by
`UNIFORM-ORIENTED-ROOT-CIRCUIT-056`, Track B7A.

It does not formalize elliptic curves, divisors, Riemann-Roch, polynomial-Pell
factorization, secp256k1, parity evaluation, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- If `n = 2m+1`, then the sum `2(1+...+m)=m(m+1)` has the
quarter-residue identity used by the canonical even half. -/
theorem evenHalfQuarterIdentity (m : ℤ) :
    4 * (m * (m + 1)) = (2 * m + 1) ^ 2 - 1 := by
  ring

/-- Multiplying a quadratic factor by its involutive conjugate gives the norm
form used by the polynomial-Pell identity. -/
theorem quadraticConjugateNorm
    {R : Type*} [CommRing R] (a b y : R) :
    (a + y * b) * (a - y * b) = a ^ 2 - y ^ 2 * b ^ 2 := by
  ring

/-- If the right factor vanishes and the left factor is nonzero, the normalized
difference-over-sum selector is `+1`. -/
theorem selectorRightZero
    {K : Type*} [Field K] (u : K) (hu : u ≠ 0) :
    (u - 0) / (u + 0) = 1 := by
  simp [hu]

/-- If the left factor vanishes and the right factor is nonzero, the normalized
difference-over-sum selector is `-1`. -/
theorem selectorLeftZero
    {K : Type*} [Field K] (u : K) (hu : u ≠ 0) :
    (0 - u) / (0 + u) = -1 := by
  simp [hu]

/-- A binary merge tree records only the combinatorics of a generalized Miller
product. -/
inductive MergeTree where
  | leaf
  | merge (left right : MergeTree)

namespace MergeTree

/-- Number of input leaves. -/
def leaves : MergeTree → ℕ
  | .leaf => 1
  | .merge left right => leaves left + leaves right

/-- Number of binary merge nodes. -/
def merges : MergeTree → ℕ
  | .leaf => 0
  | .merge left right => merges left + merges right + 1

/-- Every nonempty binary merge tree has exactly one fewer merge than leaves. -/
theorem merges_add_one_eq_leaves (tree : MergeTree) :
    merges tree + 1 = leaves tree := by
  induction tree with
  | leaf => rfl
  | merge left right ihLeft ihRight =>
      simp only [merges, leaves]
      omega

end MergeTree

/-- A one-level plus/minus index system covering at most `2ab+k` targets has
square-root charged width. This is a statement about the declared explicit
index grammar, not a lower bound for arbitrary arithmetic circuits. -/
theorem oneLevelIndexWidthBoundary
    (m a b k : ℝ)
    (ha : 0 ≤ a)
    (hb : 0 ≤ b)
    (hk : 0 ≤ k)
    (hcover : m ≤ 2 * a * b + k) :
    2 * m ≤ (a + b + k) * (a + b + k + 2) := by
  have hab : 0 ≤ a + b := add_nonneg ha hb
  have hkab : 0 ≤ k * (a + b) := mul_nonneg hk hab
  nlinarith [sq_nonneg (a - b), sq_nonneg k]

end Ecdlp.ParityLift
