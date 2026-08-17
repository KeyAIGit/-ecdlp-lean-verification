import Mathlib

/-!
# Dyadic branch compression

This file formalizes elementary algebraic and cardinality identities used by
`DYADIC-BRANCH-COMPRESSION-043`.

After a public inverse-dyadic scaling, the canonical quotient is recovered by
subtracting a correction indexed by the low-bit residue. Nonzero scaling keeps
all correction labels distinct, so any explicit exact branch encoding needs at
least one state for every residue.

The file does not formalize elliptic curves, canonical integer representatives
modulo a group order, arbitrary shared circuits, secp256k1 point arithmetic, or
ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Inverse scaling of `scalar = twoPower * quotient + residue`, followed by the
residue correction, recovers the quotient. -/
theorem dyadicCorrection_identity
    {K : Type*} [Field K]
    (inverse twoPower scalar quotient residue : K)
    (hinverse : inverse * twoPower = 1)
    (hscalar : scalar = twoPower * quotient + residue) :
    inverse * scalar - inverse * residue = quotient := by
  calc
    inverse * scalar - inverse * residue =
        inverse * (twoPower * quotient + residue) - inverse * residue := by
          rw [hscalar]
    _ = (inverse * twoPower) * quotient := by ring
    _ = quotient := by rw [hinverse, one_mul]

/-- Multiplication by a nonzero field element is injective, so distinct low-bit
residues give distinct affine corrections. -/
theorem nonzeroScaling_injective
    {K : Type*} [Field K]
    (inverse : K)
    (hinverse : inverse ≠ 0) :
    Function.Injective (fun residue : K => inverse * residue) := by
  intro left right hequal
  exact mul_left_cancel₀ hinverse hequal

/-- An explicit branch-state encoding that distinguishes every depth-`d`
residue needs at least `2^d` states. -/
theorem dyadicBranchState_card_lower_bound
    (depth : ℕ)
    {State : Type*}
    [Fintype State]
    (encode : Fin (2 ^ depth) → State)
    (hinjective : Function.Injective encode) :
    2 ^ depth ≤ Fintype.card State := by
  simpa using Fintype.card_le_of_injective encode hinjective

/-- If an exact decoder assigns one state to each residue and equal states have
equal corrections, pairwise-distinct corrections force the state map to be
injective. -/
theorem distinctCorrections_forceInjectiveStates
    {Residue State Correction : Type*}
    (state : Residue → State)
    (correction : Residue → Correction)
    (hstate : ∀ left right, state left = state right → correction left = correction right)
    (hcorrection : Function.Injective correction) :
    Function.Injective state := by
  intro left right hequal
  exact hcorrection (hstate left right hequal)

end Ecdlp.ParityLift
