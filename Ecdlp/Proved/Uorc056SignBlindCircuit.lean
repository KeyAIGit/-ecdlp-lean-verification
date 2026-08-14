import Mathlib

/-!
# UORC056 C23 sign-blind additive circuit boundary

This file formalizes a two-world indistinguishability theorem for arithmetic
circuits. The two worlds represent the two global branches `R` and `-R`.
If every public leaf has the same value in both worlds, then every rational
circuit assembled with addition, subtraction, multiplication, division,
inversion, powers, and constants also has the same value in both worlds.

The same statement applies entrywise to matrices, so a determinant cannot
create branch sensitivity when all of its entries are sign-blind circuits.
A Sylvester resultant is a determinant and is therefore covered whenever all
of its coefficients are sign-blind.

This is a scoped algebraic theorem. It does not rule out a circuit supplied
with a genuinely branch-sensitive public leaf.
-/

namespace Ecdlp.UORC056

/-- A finite rational arithmetic circuit over indexed atoms. -/
inductive RationalCircuit (ι K : Type*) where
  | const (c : K)
  | atom (i : ι)
  | neg (a : RationalCircuit ι K)
  | add (a b : RationalCircuit ι K)
  | sub (a b : RationalCircuit ι K)
  | mul (a b : RationalCircuit ι K)
  | inv (a : RationalCircuit ι K)
  | div (a b : RationalCircuit ι K)
  | pow (a : RationalCircuit ι K) (n : ℕ)

namespace RationalCircuit

variable {ι K : Type*} [Field K]

/-- Evaluate a rational circuit under an assignment of its atoms. -/
def eval (assignment : ι → K) : RationalCircuit ι K → K
  | .const c => c
  | .atom i => assignment i
  | .neg a => -eval assignment a
  | .add a b => eval assignment a + eval assignment b
  | .sub a b => eval assignment a - eval assignment b
  | .mul a b => eval assignment a * eval assignment b
  | .inv a => (eval assignment a)⁻¹
  | .div a b => eval assignment a / eval assignment b
  | .pow a n => eval assignment a ^ n

/-- Two assignments agreeing on every atom give identical circuit output. -/
theorem eval_eq_of_atom_eq
    (left right : ι → K)
    (hAtoms : ∀ i, left i = right i)
    (e : RationalCircuit ι K) :
    eval left e = eval right e := by
  induction e with
  | const c => rfl
  | atom i => exact hAtoms i
  | neg a ih => simpa [eval] using congrArg Neg.neg ih
  | add a b ihA ihB => simp [eval, ihA, ihB]
  | sub a b ihA ihB => simp [eval, ihA, ihB]
  | mul a b ihA ihB => simp [eval, ihA, ihB]
  | inv a ih => simp [eval, ih]
  | div a b ihA ihB => simp [eval, ihA, ihB]
  | pow a n ih => simp [eval, ih]

/-- A family of atoms is sign-blind when replacing the hidden branch parameter
`z` by `-z` leaves every atom unchanged. -/
def SignBlindAtoms (atoms : ι → K → K) : Prop :=
  ∀ i z, atoms i (-z) = atoms i z

/-- Evaluate a circuit whose atoms depend on a hidden branch parameter. -/
def evalAt
    (atoms : ι → K → K)
    (e : RationalCircuit ι K)
    (z : K) : K :=
  eval (fun i => atoms i z) e

/-- Arbitrary rational arithmetic preserves sign-blindness of the leaves. -/
theorem evalAt_neg_eq
    (atoms : ι → K → K)
    (hAtoms : SignBlindAtoms atoms)
    (e : RationalCircuit ι K)
    (z : K) :
    evalAt atoms e (-z) = evalAt atoms e z := by
  unfold evalAt
  apply eval_eq_of_atom_eq
  intro i
  exact hAtoms i z

/-- An even output cannot equal a target that takes two distinct values on a
sign pair. -/
theorem signBlind_cannot_match_separated_target
    (output target : K → K)
    (hOutput : ∀ z, output (-z) = output z)
    (z : K)
    (hSeparated : target z ≠ target (-z)) :
    ¬ (output z = target z ∧ output (-z) = target (-z)) := by
  rintro ⟨hPos, hNeg⟩
  apply hSeparated
  calc
    target z = output z := hPos.symm
    _ = output (-z) := (hOutput z).symm
    _ = target (-z) := hNeg

/-- In particular, a sign-blind output cannot recover both `z` and `-z` when
they are distinct. -/
theorem signBlind_cannot_select_sign_pair
    (output : K → K)
    (hOutput : ∀ z, output (-z) = output z)
    (z : K)
    (hSeparated : z ≠ -z) :
    ¬ (output z = z ∧ output (-z) = -z) := by
  exact signBlind_cannot_match_separated_target
    output (fun w => w) hOutput z hSeparated

section Determinant

variable {m : Type*} [Fintype m] [DecidableEq m]

/-- Evaluate a matrix whose entries are rational circuits. -/
def evalMatrix
    (atoms : ι → K → K)
    (matrix : Matrix m m (RationalCircuit ι K))
    (z : K) : Matrix m m K :=
  fun i j => evalAt atoms (matrix i j) z

/-- Entrywise sign-blindness gives equality of the two evaluated matrices. -/
theorem evalMatrix_neg_eq
    (atoms : ι → K → K)
    (hAtoms : SignBlindAtoms atoms)
    (matrix : Matrix m m (RationalCircuit ι K))
    (z : K) :
    evalMatrix atoms matrix (-z) = evalMatrix atoms matrix z := by
  ext i j
  exact evalAt_neg_eq atoms hAtoms (matrix i j) z

/-- A determinant of sign-blind arithmetic entries is sign-blind. -/
theorem determinant_neg_eq
    (atoms : ι → K → K)
    (hAtoms : SignBlindAtoms atoms)
    (matrix : Matrix m m (RationalCircuit ι K))
    (z : K) :
    Matrix.det (evalMatrix atoms matrix (-z)) =
      Matrix.det (evalMatrix atoms matrix z) := by
  rw [evalMatrix_neg_eq atoms hAtoms matrix z]

/-- Consequently, a sign-blind determinant cannot select two separated target
branches. This applies directly to Sylvester determinants whose coefficients
are sign-blind circuits. -/
theorem determinant_cannot_match_separated_target
    (atoms : ι → K → K)
    (hAtoms : SignBlindAtoms atoms)
    (matrix : Matrix m m (RationalCircuit ι K))
    (target : K → K)
    (z : K)
    (hSeparated : target z ≠ target (-z)) :
    ¬ (Matrix.det (evalMatrix atoms matrix z) = target z ∧
       Matrix.det (evalMatrix atoms matrix (-z)) = target (-z)) := by
  apply signBlind_cannot_match_separated_target
    (output := fun w => Matrix.det (evalMatrix atoms matrix w))
    (target := target)
    (z := z)
  · intro w
    exact determinant_neg_eq atoms hAtoms matrix w
  · exact hSeparated

end Determinant

end RationalCircuit

end Ecdlp.UORC056
