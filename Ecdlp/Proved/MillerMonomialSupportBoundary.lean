import Mathlib

/-!
# Miller monomial support boundary

This file formalizes the arithmetic core of
`UORC056-MILLER-MONOMIAL-SUPPORT-B11`.

If a corrected oriented divisor has at least `M+1` support points and each
ordinary atom contributes at most four, then any covering monomial requires
`M+1 <= 4r`.

The file does not formalize divisors, Miller functions, elliptic curves,
secp256k1, parity recovery, or ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Support coverage by bounded-support atoms forces the corresponding atom
count inequality. -/
theorem fourSupportAtoms_cover
    (M support atoms : ℕ)
    (hlower : M + 1 ≤ support)
    (hupper : support ≤ 4 * atoms) :
    M + 1 ≤ 4 * atoms := by
  omega

/-- The ceiling-style lower bound is encoded without division: fewer than `r`
atoms cannot cover when `4r < M+1`. -/
theorem tooFewFourSupportAtoms
    (M atoms : ℕ)
    (hsmall : 4 * atoms < M + 1) :
    ¬ M + 1 ≤ 4 * atoms := by
  omega

end Ecdlp.ParityLift
