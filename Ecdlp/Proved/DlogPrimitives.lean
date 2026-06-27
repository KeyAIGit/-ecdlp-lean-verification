import Mathlib

/-!
# More verified discrete-log primitives

Correctness/structure facts for further deployed discrete-log primitives, in the
cyclic group modelled as a `ZMod n`-module `G` (scalar multiplication `s • g`).
Complements the soundness (`SchnorrSoundness.lean`) and completeness
(`DlogCompleteness.lean`) results.
-/

namespace Ecdlp.Schnorr

variable {G : Type*} [AddCommGroup G] {n : ℕ} [Module (ZMod n) G]

/-- **ElGamal decryption correctness.** With public key `P = x·G`, an additive
ElGamal ciphertext `(r·G, m + r·P)` decrypts to the message:
`(m + r·P) − x·(r·G) = m`. -/
theorem elgamal_decrypt (g m : G) (x r : ZMod n) :
    (m + r • (x • g)) - x • (r • g) = m := by
  rw [← mul_smul, ← mul_smul, mul_comm r x]; abel

/-- **Pedersen commitments are additively homomorphic.** The commitment to the sum
of messages is the sum of commitments: `Com(a,b) + Com(a',b') = Com(a+a', b+b')`.
This is what lets Pedersen commitments add up in range proofs and MPC. -/
theorem pedersen_homomorphic (g h : G) (a b a' b' : ZMod n) :
    (a • g + b • h) + (a' • g + b' • h) = (a + a') • g + (b + b') • h := by
  rw [add_smul, add_smul]; abel

/-- **ElGamal ciphertext re-randomization.** Anyone (without the secret key) can
re-randomize a ciphertext `(r·G, m + r·P)` by adding `(r'·G, r'·P)`; the result
still decrypts to the same `m`. This is the unlinkability primitive behind mixnets
and re-encryption. -/
theorem elgamal_rerandomize_decrypt (g m : G) (x r r' : ZMod n) :
    ((m + r • (x • g)) + r' • (x • g)) - x • (r • g + r' • g) = m := by
  simp only [smul_add, ← mul_smul]
  rw [mul_comm r x, mul_comm r' x]; abel

/-- **ElGamal is additively homomorphic.** The componentwise sum of two ciphertexts
of `m₁, m₂` (under public key `P`) is a ciphertext of `m₁ + m₂`: `Enc(m₁;r₁) +
Enc(m₂;r₂) = Enc(m₁+m₂; r₁+r₂)`. This is what enables homomorphic tallying in
verifiable e-voting. -/
theorem elgamal_additively_homomorphic (g P m₁ m₂ : G) (r₁ r₂ : ZMod n) :
    (r₁ • g + r₂ • g, (m₁ + r₁ • P) + (m₂ + r₂ • P))
      = ((r₁ + r₂) • g, (m₁ + m₂) + (r₁ + r₂) • P) := by
  rw [Prod.mk.injEq]
  refine ⟨by rw [add_smul], ?_⟩
  rw [add_smul]; abel

end Ecdlp.Schnorr
