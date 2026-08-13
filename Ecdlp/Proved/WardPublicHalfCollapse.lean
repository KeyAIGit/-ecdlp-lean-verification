import Mathlib

/-!
# Public odd-cycle halves and the lifted index

For a canonical scalar `k` in an odd cycle, the two group halves of the points
indexed by `k+1` and `k-1` have canonical scalar representatives whose sum is
`k` when `k` is odd and `k+n` when `k` is even.

The file formalizes only this arithmetic and a `ZMod 2` consequence under a
declared period-shift law.
-/

namespace Ecdlp.WardPublicHalf

def oddHalfRep (order scalar : ℕ) : ℕ :=
  (scalar + (scalar % 2) * order) / 2

def liftedIndex (order scalar : ℕ) : ℕ :=
  if scalar % 2 = 0 then scalar + order else scalar

theorem mod_two_cases (scalar : ℕ) :
    scalar % 2 = 0 ∨ scalar % 2 = 1 := by
  omega

theorem zmodTwo_add_self (value : ZMod 2) : value + value = 0 := by
  fin_cases value <;> native_decide

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

theorem oddHalfRep_succ_sub_pred
    {order scalar : ℕ}
    (horderOdd : order % 2 = 1)
    (hscalar : 1 ≤ scalar) :
    oddHalfRep order (scalar + 1) - oddHalfRep order (scalar - 1) = 1 := by
  rcases mod_two_cases scalar with heven | hodd
  · have hsucc : (scalar + 1) % 2 = 1 := by omega
    have hpred : (scalar - 1) % 2 = 1 := by omega
    simp [oddHalfRep, hsucc, hpred]
    omega
  · have hsucc : (scalar + 1) % 2 = 0 := by omega
    have hpred : (scalar - 1) % 2 = 0 := by omega
    simp [oddHalfRep, hsucc, hpred]
    omega

def publicPhase
    (defect : ZMod 2) (residue : ℕ → ZMod 2) (scalar : ℕ) : ZMod 2 :=
  if scalar % 2 = 0 then residue scalar else defect + residue scalar

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
    simp only [publicPhase, hleft, hright, if_false, hdiff, if_true, add_zero]
    calc
      defect + residue left + (defect + residue right)
          = (defect + defect) + (residue left + residue right) := by abel
      _ = residue left + residue right := by
        rw [zmodTwo_add_self, zero_add]

theorem residue_liftedIndex_eq_defect_add_publicPhase
    (order : ℕ)
    (defect : ZMod 2)
    (residue : ℕ → ZMod 2)
    (hshift : ∀ scalar, residue (scalar + order) = residue scalar + defect)
    (scalar : ℕ) :
    residue (liftedIndex order scalar)
      = defect + publicPhase defect residue scalar := by
  by_cases heven : scalar % 2 = 0
  · simp only [liftedIndex, publicPhase, heven, if_true]
    rw [Nat.add_comm order scalar, hshift scalar]
    abel
  · simp only [liftedIndex, publicPhase, heven, if_false]
    rw [← add_assoc, zmodTwo_add_self, zero_add]

end Ecdlp.WardPublicHalf
