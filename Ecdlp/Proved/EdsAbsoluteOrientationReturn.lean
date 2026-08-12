import Mathlib

/-!
# EDS absolute orientation return

This file formalizes elementary binary identities used by
`EDS-ABSOLUTE-ORIENTATION-RETURN-042`.

In additive `ZMod 2` notation, the public local EDS cocycle is a public
coboundary plus one constant bit. Summing a segment telescopes every internal
public value, leaving exactly the endpoint values and the constant bit times
the segment length. On the secp-like branch where the constant is nonzero, the
remaining absolute orientation is canonical scalar parity.

The file does not formalize division polynomials, the raw point-function source
normalization, secp256k1 arithmetic, circuit lower bounds, or ECDLP.
-/

open scoped BigOperators

namespace Ecdlp.ParityLift

private theorem two_eq_zero_mod2 : (2 : ZMod 2) = 0 := by
  norm_num

/-- A binary coboundary plus a constant bit telescopes over a finite segment. -/
theorem binaryCocycle_sum_range
    (constant : ZMod 2)
    (publicBit : ℕ → ZMod 2) :
    ∀ length : ℕ,
      (∑ index ∈ Finset.range length,
          (constant + publicBit (index + 1) + publicBit index)) =
        (length : ZMod 2) * constant + publicBit length + publicBit 0 := by
  intro length
  induction length with
  | zero =>
      simp [two_eq_zero_mod2]
  | succ length ih =>
      rw [Finset.sum_range_succ, ih]
      push_cast
      ring_nf
      simp [two_eq_zero_mod2]

/-- If the public point-function bit is the residue plus a constant times the
canonical scalar, the residue is recovered from the public bit and that scalar
bit. -/
theorem residue_eq_public_add_scalarBit
    (residue publicBit constant scalarBit : ZMod 2)
    (hpublic : publicBit = constant * scalarBit + residue) :
    residue = publicBit + constant * scalarBit := by
  rw [hpublic]
  ring_nf
  simp [two_eq_zero_mod2]

/-- In the secp-like branch where the constant bit is one, absolute EDS residue
and scalar parity differ only by the public point-function bit. -/
theorem secpLike_residue_parity_equivalence
    (residue publicBit parity : ZMod 2)
    (hpublic : publicBit = parity + residue) :
    residue = publicBit + parity := by
  rw [hpublic]
  ring_nf
  simp [two_eq_zero_mod2]

/-- Any decoder for one of two bits related by a public xor immediately gives a
decoder for the other. -/
theorem publicXor_transfersDecoder
    (publicBit hidden output : ZMod 2)
    (houtput : output = publicBit + hidden) :
    hidden = publicBit + output := by
  rw [houtput]
  ring_nf
  simp [two_eq_zero_mod2]

end Ecdlp.ParityLift
