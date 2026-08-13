import Mathlib

/-!
# Prime-norm CM factorization boundary

This file formalizes the elementary degree arithmetic used by the
`UNIFORM-ORIENTED-ROOT-CIRCUIT-056` Kummer/CM track.

For a CM endomorphism of prime norm `n`, multiplicativity of degree would force
any two-stage endomorphism factorization to have positive integer degrees whose
product is `n`.  Primality therefore makes one stage a degree-one unit.

The file does not formalize elliptic curves, endomorphism rings, isogenies,
secp256k1, or an oriented-root evaluator.
-/

namespace Ecdlp.ParityLift

/-- A positive factorization of a prime integer has a unit factor. -/
theorem primeNorm_noNontrivialTwoFactor
    (n left right : ℕ)
    (hn : n.Prime)
    (hleft : 0 < left)
    (hright : 0 < right)
    (hfactor : left * right = n) :
    left = 1 ∨ right = 1 := by
  have hdiv : left ∣ n := ⟨right, hfactor⟩
  rcases (hn.eq_one_or_self_of_dvd left hdiv) with hleftOne | hleftN
  · exact Or.inl hleftOne
  · right
    rw [hleftN] at hfactor
    have hnpos : 0 < n := hn.pos
    nlinarith

/-- If both proposed stages have degree greater than one, their product cannot
be a prime norm. -/
theorem primeNorm_rejectsProperTwoStageChain
    (n left right : ℕ)
    (hn : n.Prime)
    (hleft : 1 < left)
    (hright : 1 < right) :
    left * right ≠ n := by
  intro hfactor
  rcases primeNorm_noNontrivialTwoFactor n left right hn
      (Nat.zero_lt_of_lt hleft) (Nat.zero_lt_of_lt hright) hfactor with h | h
  · omega
  · omega

end Ecdlp.ParityLift
