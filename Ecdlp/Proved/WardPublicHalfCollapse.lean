import Mathlib

/-!
# Public odd-cycle halves and the Ward lifted index

For a canonical scalar `k` in an odd cycle, the two publicly computable group
halves of the points indexed by `k+1` and `k-1` have canonical scalar
representatives whose sum is

```text
k       when k is odd,
k + n   when k is even.
```

Thus the Ward midpoint construction evaluates the residue at a lifted index,
not uniformly at the canonical index `k`. In a binary residue model whose
period shift contributes one constant defect, the lifted residue simplifies to
that defect plus the public point phase.

The file formalizes only this arithmetic and `ZMod 2` consequence. It assumes
the declared period-shift law; it does not construct that law for division
polynomials or claim a parity evaluator.
-/

namespace Ecdlp.WardPublicHalf

/-- Canonical scalar representative of the public half of `[scalar]G` in an
odd-order cycle, for a canonical input scalar. -/
def oddHalfRep (order scalar : ℕ) : ℕ :=
  (scalar + (scalar % 2) * order) / 2

/-- Index reached by summing the two public half representatives used in the
Ward midpoint construction. -/
def liftedIndex (order scalar : ℕ) : ℕ :=
  if scalar % 2 = 0 then scalar + order else scalar

/-- Every natural number has one of the two binary residues. -/
theorem mod_two_cases (scalar : ℕ) :
    scalar % 2 = 0 ∨ scalar % 2 = 1 := by
  omega

/-- The public halves of the successor and predecessor indices sum to the
canonical index in the odd branch and to one period lift in the even branch. -/
theorem oddHalfRep_succ_add_pred
    {order scalar : ℕ}
    (horderOdd : order % 2 = 1)
    (hscalar : 1 ≤ scalar) :
    oddHalfRep order (scalar + 1) + oddHalfRep order (scalar - 1)
      = liftedIndex order scalar := by
  rcases mod_two_cases scalar with heven | hodd
  · have hsucc : (scalar + 1) % 2 = 1 := by omega
    have hpred : (scalar - 1) % 2 = 1 := by omega
    simp [oddHalfRep, liftedIndex, heven, hsucc, hpred]
    omega
  · have hsucc : (scalar + 1) % 2 = 0 := by omega
    have hpred : (scalar - 1) % 2 = 0 := by omega
    simp [oddHalfRep, liftedIndex, hodd, hsucc, hpred]
    omega

/-- The same two public half representatives differ by one, so the second Ward
index is the fixed anchor `1`. -/
theorem oddHalfRep_succ_sub_pred
    {order scalar : ℕ}
    (horderOdd : order % 2 = 1)
    (hscalar : 1 ≤ scalar) :
    oddHalfRep order (scalar + 1) - oddHalfRep order (scalar - 1) = 1 := by
  rcases mod_two_cases scalar with heven | hodd
  · have hsucc : (scalar + 1) % 2 = 1 := by omega
    have hpred : (scalar - 1) % 2 = 1 := by omega
    simp [oddHalfRep, heven, hsucc, hpred]
    omega
  · have hsucc : (scalar + 1) % 2 = 0 := by omega
    have hpred : (scalar - 1) % 2 = 0 := by omega
    simp [oddHalfRep, hodd, hsucc, hpred]
    omega

/-- Binary public phase: an odd index includes one copy of the constant defect,
while an even index does not. -/
def publicPhase
    (defect : ZMod 2) (residue : ℕ → ZMod 2) (scalar : ℕ) : ZMod 2 :=
  if scalar % 2 = 0 then residue scalar else defect + residue scalar

/-- The product of two public phases has the exact endpoint normal form: the
sum of the two residue bits plus the parity character of the segment length. -/
theorem publicPhase_pair_normalForm
    (defect : ZMod 2)
    (residue : ℕ → ZMod 2)
    {left right : ℕ}
    (hle : left ≤ right) :
    publicPhase defect residue left + publicPhase defect residue right
      = residue left + residue right
        + (if (right - left) % 2 = 0 then 0 else defect) := by
  rcases mod_two_cases left with hleft | hleft <;>
    rcases mod_two_cases right with hright | hright
  · have hdiff : (right - left) % 2 = 0 := by omega
    simp [publicPhase, hleft, hright, hdiff]
  · have hdiff : (right - left) % 2 = 1 := by omega
    simp [publicPhase, hleft, hright, hdiff]
    ring
  · have hdiff : (right - left) % 2 = 1 := by omega
    simp [publicPhase, hleft, hright, hdiff]
    ring
  · have hdiff : (right - left) % 2 = 0 := by omega
    simp [publicPhase, hleft, hright, hdiff]
    ring

/-- If shifting the residue index by one odd period adds the constant defect,
then the residue selected by the public-half Ward construction is exactly the
defect plus the public phase. The putative nonconstant midpoint observable has
therefore collapsed to already public endpoint data under these assumptions. -/
theorem residue_liftedIndex_eq_defect_add_publicPhase
    (order : ℕ)
    (defect : ZMod 2)
    (residue : ℕ → ZMod 2)
    (hshift : ∀ scalar, residue (scalar + order) = residue scalar + defect)
    (scalar : ℕ) :
    residue (liftedIndex order scalar)
      = defect + publicPhase defect residue scalar := by
  by_cases heven : scalar % 2 = 0
  · simp [liftedIndex, publicPhase, heven, hshift, add_comm]
  · simp [liftedIndex, publicPhase, heven]
    ring

end Ecdlp.WardPublicHalf
