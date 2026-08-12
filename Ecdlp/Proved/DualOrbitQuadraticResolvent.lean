import Mathlib

/-!
# Dual-orbit quadratic resolvent

This file formalizes the elementary algebraic core of
`DUAL-ORBIT-QUADRATIC-RESOLVENT-034`.

If a character-weighted projector satisfies

```text
projected = character * base,
```

then normalization by a nonzero base recovers the character.  It also records
the elementary fact that an eigen-sum with a nontrivial scalar eigenvalue must
vanish.

The file does not formalize finite-field quadratic characters, elliptic curves,
torsion sums, cyclotomic products, nonvanishing on secp256k1, or complexity.
-/

namespace Ecdlp.ParityLift

/-- Normalizing a nonzero character eigenprojector recovers its eigenvalue. -/
theorem normalizedProjector_recoversCharacter
    {K : Type*} [Field K]
    (projected base character : K)
    (hprojected : projected = character * base)
    (hbase : base ≠ 0) :
    projected / base = character := by
  rw [hprojected]
  field_simp

/-- A sum satisfying `S = c*S` for a nontrivial scalar `c` must vanish.  This
is the abstract cancellation used to explain why the `x` and `x^2` weighted
projectors vanish under the order-three GLV action. -/
theorem nontrivialEigenvalue_forcesZero
    {K : Type*} [Field K]
    (c S : K)
    (hfixed : S = c * S)
    (hc : c ≠ 1) :
    S = 0 := by
  have hmul : (c - 1) * S = 0 := by
    calc
      (c - 1) * S = c * S - S := by ring
      _ = 0 := by rw [← hfixed]; ring
  rcases mul_eq_zero.mp hmul with hc0 | hS0
  · exact (hc (sub_eq_zero.mp hc0)).elim
  · exact hS0

/-- Abstract two-value classification once the quadratic character is known to
be `+1` or `-1`. -/
theorem quadraticOrbit_twoValues
    {K : Type*} [Field K]
    (character value nonresidueConstant : K)
    (hcharacter : character = 1 ∨ character = -1)
    (hresidue : character = 1 → value = 1)
    (hnonresidue : character = -1 → value = nonresidueConstant) :
    (character = 1 ∧ value = 1) ∨
      (character = -1 ∧ value = nonresidueConstant) := by
  rcases hcharacter with hplus | hminus
  · exact Or.inl ⟨hplus, hresidue hplus⟩
  · exact Or.inr ⟨hminus, hnonresidue hminus⟩

end Ecdlp.ParityLift
