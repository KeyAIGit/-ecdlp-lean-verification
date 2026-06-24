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

end Ecdlp.Schnorr
