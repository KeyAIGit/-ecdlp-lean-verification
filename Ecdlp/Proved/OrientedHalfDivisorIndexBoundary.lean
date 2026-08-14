import Mathlib

/-!
# Oriented half-divisor and two-set index boundary

This file formalizes the arithmetic core of
`UORC056-ORIENTED-HALF-DIVISOR-INDEX-B4`.

The parity-oriented divisor has scalar class

  M(M+1) - M^2 = M.

For a two-set square-root-Velu-style index system with cardinalities `a`, `b`
and leftovers `c`, coverage of `M` representatives gives `M <= 2ab+c`.
Writing `n=2M+1` and `W=a+b+c`, this implies

  n <= (W+1)^2.

The file does not formalize elliptic curves, Picard groups, isogenies,
resultants, secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- The scalar class of the even-minus-odd canonical half-divisor. -/
theorem parityHalfDivisor_scalarClass (M : ℤ) :
    M * (M + 1) - M * M = M := by
  ring

/-- Cardinality coverage in a standard two-set index system already forces a
square-root work boundary. The hypotheses are stated over integers to keep the
algebraic core independent of finite-set encodings. -/
theorem twoSetIndexCoverage_squareBoundary
    (a b c M n : ℤ)
    (ha : 0 ≤ a)
    (hb : 0 ≤ b)
    (hc : 0 ≤ c)
    (hcover : M ≤ 2 * a * b + c)
    (hn : n = 2 * M + 1) :
    n ≤ (a + b + c + 1) ^ 2 := by
  have habSquare : 0 ≤ (a - b) ^ 2 := sq_nonneg (a - b)
  have hcSquare : 0 ≤ c ^ 2 := sq_nonneg c
  have hcCross : 0 ≤ 2 * c * (a + b) := by positivity
  have hlinear : 0 ≤ 2 * a + 2 * b := by positivity
  nlinarith

/-- The marked class changes sign when the marked generator is negated. -/
theorem markedClass_neg
    {A : Type*} [AddCommGroup A]
    (M : ℤ) (G : A) :
    M • (-G) = -(M • G) := by
  simp

end Ecdlp.ParityLift
