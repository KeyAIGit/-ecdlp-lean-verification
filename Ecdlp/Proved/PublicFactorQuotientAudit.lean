import Mathlib
import Ecdlp.Proved.R3PointScaleDichotomy

/-!
# Public-factor quotient classification

This file records the theorem-only bookkeeping used by
`PUBLIC-FACTOR-QUOTIENT-AUDIT-021`.

Candidate signs are represented as bits in `ZMod 2`; quotienting multiplicative
signs is therefore bit addition.  A candidate equal to a public factor has zero
residual.  For the normalized C3 orbit, the residual of raw `R3` is zero in the
trivial point-scale branch and is exactly the carry bit in the nontrivial
point-scale branch.

Lean does not formalize the finite Python screens, statistical admission rules,
or construction of the public point-function character.
-/

namespace Ecdlp.ParityLift

/-- Quotient of multiplicative binary signs, written additively in `ZMod 2`. -/
def publicFactorQuotientBit
    (candidateBit publicFactorBit : ZMod 2) : ZMod 2 :=
  candidateBit + publicFactorBit

/-- Rediscovering an already-public sign leaves the trivial quotient. -/
theorem publicFactorQuotient_self_zero (publicBit : ZMod 2) :
    publicFactorQuotientBit publicBit publicBit = 0 := by
  fin_cases publicBit <;> native_decide

/-- In the trivial point-scale branch, quotienting `R3` by the public C3 norm
leaves no hidden bit. -/
theorem r3PublicBranch_quotient_zero
    (gammaBit r3Bit : ZMod 2) :
    publicFactorQuotientBit r3Bit
      (r3PublicOrbitNormBit 0 gammaBit r3Bit) = 0 := by
  exact r3_trivialPointScale_exposesNoCarry gammaBit r3Bit

/-- In the nontrivial point-scale branch, quotienting `R3` by the public C3
norm leaves exactly the GLV carry bit. -/
theorem r3HardBranch_quotient_eq_carry
    (gammaBit r3Bit : ZMod 2) :
    publicFactorQuotientBit r3Bit
      (r3PublicOrbitNormBit 1 gammaBit r3Bit) = gammaBit := by
  exact r3_nontrivialPointScale_recoversCarry gammaBit r3Bit

/-- The two point-scale branches are exhaustive for a binary scale bit. -/
theorem publicFactorQuotient_dichotomy
    (pointScaleBit gammaBit r3Bit : ZMod 2) :
    publicFactorQuotientBit r3Bit
        (r3PublicOrbitNormBit pointScaleBit gammaBit r3Bit) = 0 ∨
      publicFactorQuotientBit r3Bit
        (r3PublicOrbitNormBit pointScaleBit gammaBit r3Bit) = gammaBit := by
  fin_cases pointScaleBit
  · exact Or.inl (r3PublicBranch_quotient_zero gammaBit r3Bit)
  · exact Or.inr (r3HardBranch_quotient_eq_carry gammaBit r3Bit)

end Ecdlp.ParityLift
