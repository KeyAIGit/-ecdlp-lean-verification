import Mathlib

/-!
# R3 point-scale dichotomy

This file records the binary bookkeeping behind
`R3-POINT-SCALE-DICHOTOMY-018`.

Write multiplicative signs as bits in `ZMod 2`.  If the public normalized point
character is

`C(k) = s^k * rho(k)`,

and the three canonical GLV representatives sum to `gamma*n` with odd `n`, the
public C3 orbit norm has bit

`publicNormBit = gamma * pointScaleBit + r3Bit`.

Therefore a trivial point-scale bit makes `R3` itself public, while the
nontrivial point-scale bit makes the difference between `R3` and the public
norm exactly the GLV carry bit.

Lean proves only this binary implication.  It does not formalize division
polynomials, perfectly periodic EDS normalization, or public evaluation of the
point-function character.
-/

namespace Ecdlp.ParityLift

/-- Bit of the public C3 orbit norm after point-scale normalization. -/
def r3PublicOrbitNormBit
    (pointScaleBit gammaBit r3Bit : ZMod 2) : ZMod 2 :=
  gammaBit * pointScaleBit + r3Bit

/-- With trivial point-scale character, the raw `R3` bit is already public. -/
theorem r3_trivialPointScale_isPublic
    (gammaBit r3Bit : ZMod 2) :
    r3PublicOrbitNormBit 0 gammaBit r3Bit = r3Bit := by
  simp [r3PublicOrbitNormBit]

/-- With nontrivial point-scale character, the public norm differs from `R3`
by exactly the carry bit. -/
theorem r3_nontrivialPointScale_differsByCarry
    (gammaBit r3Bit : ZMod 2) :
    r3PublicOrbitNormBit 1 gammaBit r3Bit = gammaBit + r3Bit := by
  simp [r3PublicOrbitNormBit]

/-- In the nontrivial point-scale case, an `R3` decoder and the public orbit
norm recover the carry bit. -/
theorem r3_nontrivialPointScale_recoversCarry
    (gammaBit r3Bit : ZMod 2) :
    r3Bit + r3PublicOrbitNormBit 1 gammaBit r3Bit = gammaBit := by
  fin_cases gammaBit <;> fin_cases r3Bit <;>
    norm_num [r3PublicOrbitNormBit]

/-- In the trivial point-scale case, comparing `R3` with the public orbit norm
returns zero and therefore exposes no carry bit. -/
theorem r3_trivialPointScale_exposesNoCarry
    (gammaBit r3Bit : ZMod 2) :
    r3Bit + r3PublicOrbitNormBit 0 gammaBit r3Bit = 0 := by
  fin_cases gammaBit <;> fin_cases r3Bit <;>
    norm_num [r3PublicOrbitNormBit]

end Ecdlp.ParityLift
