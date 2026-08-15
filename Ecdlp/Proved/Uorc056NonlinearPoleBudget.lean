import Mathlib

/-!
# UORC056 C28 nonlinear rational-state pole-budget boundary

This file kernel-checks the finite pole-budget compiler, the abstract integer
transfers consumed after the algebraic zero-count arguments, and the exact
secp256k1 thresholds.

It does not formalize divisors on elliptic curves, the theorem that a nonzero
rational function has equal zero and pole degree, or the transfer from the
marked subgroup evaluations to a divisor. Those obligations are stated and
proved mathematically in the accompanying note and replayed on finite rational
controls.
-/

namespace Ecdlp.UORC056

/-- A representation grammar for the degree-only pole-budget compiler. -/
inductive PoleExpr where
  | const
  | leaf (budget : ℕ)
  | neg (value : PoleExpr)
  | add (left right : PoleExpr)
  | mul (left right : PoleExpr)
  | inv (value : PoleExpr)
  | pow (value : PoleExpr) (exponent : ℕ)
  deriving Repr

namespace PoleExpr

/-- The safe total pole-degree budget assigned to an expression. -/
def budget : PoleExpr → ℕ
  | const => 0
  | leaf value => value
  | neg value => budget value
  | add left right => budget left + budget right
  | mul left right => budget left + budget right
  | inv value => budget value
  | pow value exponent => exponent * budget value

@[simp] theorem budget_const : budget const = 0 := rfl
@[simp] theorem budget_leaf (value : ℕ) : budget (leaf value) = value := rfl
@[simp] theorem budget_neg (value : PoleExpr) :
    budget (neg value) = budget value := rfl
@[simp] theorem budget_add (left right : PoleExpr) :
    budget (add left right) = budget left + budget right := rfl
@[simp] theorem budget_mul (left right : PoleExpr) :
    budget (mul left right) = budget left + budget right := rfl
@[simp] theorem budget_inv (value : PoleExpr) :
    budget (inv value) = budget value := rfl
@[simp] theorem budget_pow (value : PoleExpr) (exponent : ℕ) :
    budget (pow value exponent) = exponent * budget value := rfl

/-- The direct CM `A/B` parity decoder compiled in the safe degree-only grammar. -/
def abDecoder (aBudget bBudget : ℕ) : PoleExpr :=
  let A := leaf aBudget
  let B := leaf bBudget
  let X := leaf 2
  let Y := leaf 3
  let numerator :=
    add
      (add (pow A 2) (mul (mul A X) B))
      (mul (pow X 2) (pow B 2))
  let denominator := mul Y A
  mul numerator (inv denominator)

/-- Exact output of the compiler for the direct `A/B` decoder. -/
theorem budget_abDecoder (aBudget bBudget : ℕ) :
    budget (abDecoder aBudget bBudget) =
      4 * aBudget + 3 * bBudget + 9 := by
  simp [abDecoder, budget]
  omega

/-- Equal coordinate budgets give the uniform `7*delta+9` bound. -/
theorem budget_abDecoder_le_equal
    (aBudget bBudget delta : ℕ)
    (ha : aBudget ≤ delta) (hb : bBudget ≤ delta) :
    budget (abDecoder aBudget bBudget) ≤ 7 * delta + 9 := by
  rw [budget_abDecoder]
  omega

end PoleExpr

section ZeroCountTransfers

/-- Integer transfer consumed after `f^2-1` supplies `2*m` marked zeros and
has pole degree at most `2*D`. -/
theorem squareResidual_zeroCount_to_poleLower
    (m D : ℕ) (h : 2 * m ≤ 2 * D) :
    m ≤ D := by
  omega

/-- Integer transfer consumed after the translation defect supplies `2*m-1`
marked zeros and has pole degree at most `2*D`. -/
theorem translationDefect_zeroCount_to_poleLower
    (m D : ℕ) (hm : 0 < m)
    (h : 2 * m - 1 ≤ 2 * D) :
    m ≤ D := by
  omega

end ZeroCountTransfers

section FixedArithmetic

def secpN_C28 : ℕ :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def secpHalf_C28 : ℕ :=
  57896044618658097711785492504343953926418782139537452191302581570759080747168

def secpABStatePoleLower : ℕ :=
  8270863516951156815969356072049136275202683162791064598757511652965582963880

def secpABPolynomialDegreeLower : ℕ :=
  1378477252825192802661559345341522712533780527131844099792918608827597160647

theorem secpHalf_C28_certificate :
    2 * secpHalf_C28 = secpN_C28 - 1 := by
  native_decide

/-- The preceding equal-coordinate pole budget is insufficient. -/
theorem secpABStatePole_predecessor_fails :
    7 * (secpABStatePoleLower - 1) + 9 < secpHalf_C28 := by
  native_decide

/-- The recorded equal-coordinate pole budget reaches the necessary half-order. -/
theorem secpABStatePole_bound_succeeds :
    secpHalf_C28 ≤ 7 * secpABStatePoleLower + 9 := by
  native_decide

theorem secpABStatePole_bits_lower :
    2 ^ 252 < secpABStatePoleLower := by
  native_decide

theorem secpABStatePole_bits_upper :
    secpABStatePoleLower < 2 ^ 253 := by
  native_decide

/-- If both CM components are polynomials in `T=x^3` of degree at most `d`,
the compiler gives the safe bound `42*d+9`. -/
theorem secpABPolynomialDegree_predecessor_fails :
    42 * (secpABPolynomialDegreeLower - 1) + 9 < secpHalf_C28 := by
  native_decide

theorem secpABPolynomialDegree_bound_succeeds :
    secpHalf_C28 ≤ 42 * secpABPolynomialDegreeLower + 9 := by
  native_decide

theorem secpABPolynomialDegree_bits_lower :
    2 ^ 249 < secpABPolynomialDegreeLower := by
  native_decide

theorem secpABPolynomialDegree_bits_upper :
    secpABPolynomialDegreeLower < 2 ^ 250 := by
  native_decide

/-- Degree-only circuit growth from one unit pole-budget leaf needs 255 binary
doublings to reach the secp half-order. -/
theorem secpUnitBudget_gate_predecessor_fails :
    2 ^ 254 < secpHalf_C28 := by
  native_decide

theorem secpUnitBudget_gate_bound_succeeds :
    secpHalf_C28 ≤ 2 ^ 255 := by
  native_decide

/-- With total initial budget five, the degree-only compiler needs 253 binary
doublings. This is logarithmic and therefore is not a useful unrestricted
circuit lower bound. -/
theorem secpFiveBudget_gate_predecessor_fails :
    2 ^ 252 * 5 < secpHalf_C28 := by
  native_decide

theorem secpFiveBudget_gate_bound_succeeds :
    secpHalf_C28 ≤ 2 ^ 253 * 5 := by
  native_decide

end FixedArithmetic

end Ecdlp.UORC056
