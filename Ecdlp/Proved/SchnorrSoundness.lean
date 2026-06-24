import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# Special soundness of the Schnorr proof of knowledge

The Schnorr identification protocol (and, via Fiat–Shamir, the Schnorr signature
and EdDSA) is a *proof of knowledge* of a discrete logarithm. Its soundness is
witnessed by an **extractor**: from two accepting transcripts that share the
commitment but use distinct challenges, the secret discrete log is recovered by
field arithmetic. This file formalizes that extractor over an arbitrary field, and
notes it applies to the secp256k1 scalar field `ZMod n` (assuming `n` prime).

No group operations are needed — the extractor lives entirely in the scalar field,
which is exactly why it is unconditional (it does not rely on the hardness of the
discrete log, only on the algebra of the responses).
-/

namespace Ecdlp.Schnorr

variable {F : Type*} [Field F]

/-- **Special soundness / witness extraction.** Two accepting Schnorr transcripts
with the same commitment, distinct challenges `c₁ ≠ c₂`, and responses
`sᵢ = r + cᵢ·x`, determine the witness `x` uniquely as `x = (s₁ − s₂)/(c₁ − c₂)`.
This extractor is the reason Schnorr is a proof of knowledge of the discrete log. -/
theorem schnorr_extract {x r c₁ c₂ s₁ s₂ : F}
    (h₁ : s₁ = r + c₁ * x) (h₂ : s₂ = r + c₂ * x) (hc : c₁ ≠ c₂) :
    x = (s₁ - s₂) / (c₁ - c₂) := by
  have hcne : c₁ - c₂ ≠ 0 := sub_ne_zero.mpr hc
  have key : (c₁ - c₂) * x = s₁ - s₂ := by rw [h₁, h₂]; ring
  field_simp
  linear_combination key

/-- The extracted witness is also unique: any two witnesses consistent with the
same pair of distinct-challenge transcripts coincide. (Knowledge soundness has a
*unique* extractable witness.) -/
theorem schnorr_witness_unique {x x' r c₁ c₂ s₁ s₂ : F}
    (h₁ : s₁ = r + c₁ * x) (h₂ : s₂ = r + c₂ * x)
    (h₁' : s₁ = r + c₁ * x') (h₂' : s₂ = r + c₂ * x') (hc : c₁ ≠ c₂) :
    x = x' := by
  rw [schnorr_extract h₁ h₂ hc, schnorr_extract h₁' h₂' hc]

/-- **Computational binding of Pedersen commitments (reduction to the DLP).** Write
a Pedersen commitment `a·G + b·H` by its exponent `a + b·h`, where `h = log_G H` is
the unknown trapdoor. If two distinct openings collide on the same commitment and
their `H`-coefficients differ (`b ≠ b'`), the trapdoor discrete log is extracted as
`h = (a' − a)/(b − b')`. So any binding break yields a discrete log: Pedersen is
binding under the hardness of the discrete log. -/
theorem pedersen_binding_extract {a b a' b' h : F}
    (hcom : a + b * h = a' + b' * h) (hb : b ≠ b') :
    h = (a' - a) / (b - b') := by
  have hbne : b - b' ≠ 0 := sub_ne_zero.mpr hb
  have key : (b - b') * h = a' - a := by linear_combination hcom
  field_simp
  linear_combination key

end Ecdlp.Schnorr

namespace Ecdlp.Secp256k1Schnorr

open Ecdlp.Schnorr

/-- The Schnorr extractor instantiated at the secp256k1 scalar field `ZMod n`
(assuming the published primality of `n`): two accepting transcripts with distinct
challenges yield the secret key. This is the knowledge-soundness of Schnorr/EdDSA
signatures over secp256k1. -/
theorem secp256k1_schnorr_extract [Fact (Nat.Prime Secp256k1.n)]
    {x r c₁ c₂ s₁ s₂ : ZMod Secp256k1.n}
    (h₁ : s₁ = r + c₁ * x) (h₂ : s₂ = r + c₂ * x) (hc : c₁ ≠ c₂) :
    x = (s₁ - s₂) / (c₁ - c₂) :=
  schnorr_extract h₁ h₂ hc

end Ecdlp.Secp256k1Schnorr
