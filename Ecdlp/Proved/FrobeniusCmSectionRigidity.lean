import Mathlib

/-!
# Character collapse for GLV-invariant Frobenius/CM sections

This file formalizes the binary bookkeeping isolated in
`FROBENIUS-CM-SECTION-RIGIDITY-010`.

The geometric input is a generalized division section `A_α` attached to an
endomorphism `α` which commutes with the order-three GLV automorphism. Let
`a` be the scalar by which `α` acts on the chosen prime-order subgroup and let
`δ` be the parity of `deg α`. The generalized chain rule and the ordinary
multiplication formula reduce the character of the section to

    public_ψa(Q)
      * rho(Q)^(a+δ)
      * phase^(k).

GLV invariance at the even secp256k1 eigenvalue and ordinary GLV covariance
force the phase bit to be the same bit `a+δ`. Consequently the entire hidden
part is

    (rho(Q) * (-1)^k)^(a+δ),

which is either trivial or the already-public perfectly-periodic point
character. No independent `R3` or carry equation remains.

Lean proves only this exact binary implication. It does not formalize
Frobenius, arbitrary-isogeny division polynomials, the generalized chain rule,
or the geometric admission of an external section into the stated class.
-/

namespace Ecdlp.ParityLift

/-- Binary coefficient controlling both the residual EDS character and the
canonical scalar-parity phase of a GLV-invariant generalized division section. -/
def frobeniusCmHiddenWeight (actionParity degreeParity : ZMod 2) : ZMod 2 :=
  actionParity + degreeParity

/-- The chain-rule expression collapses to the public point character raised
to the single weight `actionParity + degreeParity`.

Here `rhoBit` is the bit of the residual EDS character, `scalarParity` is the
bit of `(-1)^k`, and `publicBit` is the character of the ordinary fixed-index
section `psi_a(Q)`. -/
theorem frobeniusCmSection_character_collapse
    (actionParity degreeParity rhoBit scalarParity publicBit : ZMod 2) :
    publicBit
        + frobeniusCmHiddenWeight actionParity degreeParity * rhoBit
        + frobeniusCmHiddenWeight actionParity degreeParity * scalarParity
      = publicBit
        + frobeniusCmHiddenWeight actionParity degreeParity
            * (rhoBit + scalarParity) := by
  simp only [frobeniusCmHiddenWeight]
  ring

/-- If action parity and degree parity agree, the generalized section character
is exactly the ordinary public fixed-index character. -/
theorem frobeniusCmSection_equalParity_isPublic
    (actionParity degreeParity rhoBit scalarParity publicBit : ZMod 2)
    (h : actionParity = degreeParity) :
    publicBit
        + frobeniusCmHiddenWeight actionParity degreeParity * rhoBit
        + frobeniusCmHiddenWeight actionParity degreeParity * scalarParity
      = publicBit := by
  subst degreeParity
  fin_cases actionParity <;> simp [frobeniusCmHiddenWeight] <;> ring

/-- If action parity and degree parity differ, the only extra character is the
already-public perfectly-periodic point character `rhoBit + scalarParity`. -/
theorem frobeniusCmSection_differentParity_isPointCharacter
    (actionParity degreeParity rhoBit scalarParity publicBit : ZMod 2)
    (h : actionParity ≠ degreeParity) :
    publicBit
        + frobeniusCmHiddenWeight actionParity degreeParity * rhoBit
        + frobeniusCmHiddenWeight actionParity degreeParity * scalarParity
      = publicBit + rhoBit + scalarParity := by
  fin_cases actionParity <;> fin_cases degreeParity <;>
    simp_all [frobeniusCmHiddenWeight] <;> ring

/-- Taking a C3 orbit norm cannot manufacture an independent equation: the
extra term is still only the orbit norm of the public point character. -/
theorem frobeniusCmC3Norm_character_collapse
    (weight rho0 rho1 rho2 parity0 parity1 parity2 publicNorm : ZMod 2) :
    publicNorm
        + weight * (rho0 + parity0)
        + weight * (rho1 + parity1)
        + weight * (rho2 + parity2)
      = publicNorm
        + weight * ((rho0 + rho1 + rho2)
          + (parity0 + parity1 + parity2)) := by
  ring

end Ecdlp.ParityLift
