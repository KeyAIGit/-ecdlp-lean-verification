import Mathlib
import Ecdlp.Proved.SchnorrSoundness

/-!
# Advanced discrete-log protocols: Okamoto and Chaum–Pedersen

Soundness/completeness of two further deployed Σ-protocols, built from the Schnorr
extractor and verification identity. Neither protocol is present in Mathlib.
-/

namespace Ecdlp.Schnorr

variable {F : Type*} [Field F]

/-- **Okamoto identification — special soundness (2-witness extraction).** For the
relation `P = x₁·G + x₂·H`, two accepting transcripts with distinct challenges
extract *both* witnesses: from `sₖ = rₖ + c·xₖ` and `sₖ' = rₖ + c'·xₖ`,
`x₁ = (s₁−s₁')/(c−c')` and `x₂ = (s₂−s₂')/(c−c')`. -/
theorem okamoto_extract {x₁ x₂ r₁ r₂ c c' s₁ s₂ s₁' s₂' : F}
    (h1 : s₁ = r₁ + c * x₁) (h2 : s₂ = r₂ + c * x₂)
    (h1' : s₁' = r₁ + c' * x₁) (h2' : s₂' = r₂ + c' * x₂) (hc : c ≠ c') :
    x₁ = (s₁ - s₁') / (c - c') ∧ x₂ = (s₂ - s₂') / (c - c') :=
  ⟨schnorr_extract h1 h1' hc, schnorr_extract h2 h2' hc⟩

end Ecdlp.Schnorr

namespace Ecdlp.DLEQ

variable {G : Type*} [AddCommGroup G] {n : ℕ} [Module (ZMod n) G]

/-- **Chaum–Pedersen DLEQ — completeness.** An honest proof that two group elements
share a discrete log (`a = x·G`, `b = x·H`) satisfies both verification equations:
`s·G = R₁ + c·a` and `s·H = R₂ + c·b`, where `R₁ = r·G`, `R₂ = r·H`, `s = r + c·x`.
This is the proof of *equality of discrete logs* used in verifiable random
functions and mix-nets. -/
theorem chaum_pedersen_verify (g h a b R₁ R₂ : G) (x r c s : ZMod n)
    (ha : a = x • g) (hb : b = x • h) (hR₁ : R₁ = r • g) (hR₂ : R₂ = r • h)
    (hs : s = r + c * x) :
    s • g = R₁ + c • a ∧ s • h = R₂ + c • b := by
  subst ha hb hR₁ hR₂ hs
  constructor <;> rw [add_smul, mul_smul]

end Ecdlp.DLEQ
