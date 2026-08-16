import Mathlib
import Ecdlp.Proved.Uorc056AnchorMixedMiller

/-!
# UORC-056 C36 multi-argument Miller defect decoder

This file kernel-checks the algebraic core of C36:

* the multiplicative defect of a nonzero field-valued state is a normalized
  2-cocycle;
* a scaled n-th-power gauge changes the defect by the corresponding explicit
  n-th-power coboundary and one common scalar;
* the exact monomial-dimension thresholds used in the frozen polynomial and
  rational rank screens.

It does not formalize the elliptic curve, the shifted Miller section, the 520
quadratic-extension shifts, or the finite evaluation-matrix ranks. Those are
stated in the accompanying note and replayed by exact Python.
-/

namespace Ecdlp.Uorc056MultiArgumentMillerDecoder

/-- Multiplicative addition defect of a field-valued state. The accompanying
results assume that every evaluated state value is nonzero. -/
def defect
    {A K : Type*} [Add A] [Field K]
    (state : A -> K) (P Q : A) : K :=
  state (P + Q) / (state P * state Q)

/-- Every multiplicative defect of a nonzero field-valued state is an exact
normalized 2-cocycle. -/
theorem defect_cocycle
    {A K : Type*} [AddSemigroup A] [Field K]
    (state : A -> K)
    (hstate : forall X, state X ≠ 0)
    (P Q T : A) :
    defect state P Q * defect state (P + Q) T =
      defect state Q T * defect state P (Q + T) := by
  unfold defect
  rw [add_assoc]
  field_simp [hstate]
  ring

/-- Algebraic normal form of a defect after a common scalar and an inverse
n-th-power gauge are inserted into a nonzero field-valued state.

The variables stand for values at `P`, `Q`, and `P+Q`. -/
theorem defect_of_scaled_power_gauge
    {K : Type*} [Field K]
    (c fP fQ fPQ hP hQ hPQ : K)
    (n : Nat)
    (hc : c ≠ 0)
    (hfP : fP ≠ 0)
    (hfQ : fQ ≠ 0)
    (hfPQ : fPQ ≠ 0)
    (hhP : hP ≠ 0)
    (hhQ : hQ ≠ 0)
    (hhPQ : hPQ ≠ 0) :
    (c * fPQ * (hPQ ^ n)⁻¹) /
        ((c * fP * (hP ^ n)⁻¹) * (c * fQ * (hQ ^ n)⁻¹)) =
      c⁻¹ * (fPQ / (fP * fQ)) * ((hP * hQ / hPQ) ^ n) := by
  field_simp [hc, hfP, hfQ, hfPQ, hhP, hhQ, hhPQ]
  ring

/-- Number of monomials in two variables of total degree at most `d`. -/
def pairMonomials (d : Nat) : Nat :=
  (d + 1) * (d + 2) / 2

/-- Number of monomials in three variables of total degree at most `d`. -/
def tripleMonomials (d : Nat) : Nat :=
  (d + 1) * (d + 2) * (d + 3) / 6

/-- Frozen polynomial interpolation thresholds for the two-defect grammar. -/
theorem pairPolynomialThresholds :
    pairMonomials 6 < 30 ∧ 30 ≤ pairMonomials 7 ∧
    pairMonomials 10 < 78 ∧ 78 ≤ pairMonomials 11 ∧
    pairMonomials 9 < 66 ∧ 66 ≤ pairMonomials 10 ∧
    pairMonomials 14 < 126 ∧ 126 ≤ pairMonomials 15 ∧
    pairMonomials 15 < 138 ∧ 138 ≤ pairMonomials 16 := by
  native_decide

/-- Frozen polynomial interpolation thresholds for the three-defect grammar. -/
theorem triplePolynomialThresholds :
    tripleMonomials 3 < 30 ∧ 30 ≤ tripleMonomials 4 ∧
    tripleMonomials 5 < 78 ∧ 78 ≤ tripleMonomials 6 ∧
    tripleMonomials 5 < 66 ∧ 66 ≤ tripleMonomials 6 ∧
    tripleMonomials 7 < 126 ∧ 126 ≤ tripleMonomials 8 ∧
    tripleMonomials 7 < 138 ∧ 138 ≤ tripleMonomials 8 := by
  native_decide

/-- Dimension-forced thresholds for a numerator/denominator pair in two
variables. These arithmetic facts do not assert that the resulting relation
has a denominator nonzero on every sample. -/
theorem pairRationalDimensionThresholds :
    2 * pairMonomials 4 ≤ 30 ∧ 30 < 2 * pairMonomials 5 ∧
    2 * pairMonomials 7 ≤ 78 ∧ 78 < 2 * pairMonomials 8 ∧
    2 * pairMonomials 6 ≤ 66 ∧ 66 < 2 * pairMonomials 7 ∧
    2 * pairMonomials 9 ≤ 126 ∧ 126 < 2 * pairMonomials 10 ∧
    2 * pairMonomials 10 ≤ 138 ∧ 138 < 2 * pairMonomials 11 := by
  native_decide

/-- Dimension-forced thresholds for a numerator/denominator pair in three
variables. -/
theorem tripleRationalDimensionThresholds :
    2 * tripleMonomials 2 ≤ 30 ∧ 30 < 2 * tripleMonomials 3 ∧
    2 * tripleMonomials 4 ≤ 78 ∧ 78 < 2 * tripleMonomials 5 ∧
    2 * tripleMonomials 3 ≤ 66 ∧ 66 < 2 * tripleMonomials 4 ∧
    2 * tripleMonomials 5 ≤ 126 ∧ 126 < 2 * tripleMonomials 6 ∧
    2 * tripleMonomials 5 ≤ 138 ∧ 138 < 2 * tripleMonomials 6 := by
  native_decide

end Ecdlp.Uorc056MultiArgumentMillerDecoder
