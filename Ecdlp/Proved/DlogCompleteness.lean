import Mathlib

/-!
# Completeness of discrete-log protocols

Soundness extractors for Schnorr and Pedersen live in `SchnorrSoundness.lean`
(pure scalar-field algebra). This file proves the *completeness* side — honest
executions verify — in the cyclic group itself, modelled as a `ZMod n`-module `G`
(a finite abelian group of exponent dividing `n`; `s • g` is the scalar
multiplication `g ↦ s·g`).
-/

namespace Ecdlp.Schnorr

variable {G : Type*} [AddCommGroup G] {n : ℕ} [Module (ZMod n) G]

/-- **Schnorr / EdDSA signature correctness (completeness).** An honestly produced
signature verifies: with public key `P = x·G`, commitment `R = r·G`, and response
`s = r + c·x` (scalars in `ZMod n`), the verification equation `s·G = R + c·P`
holds. With `schnorr_extract` (soundness) this gives both directions of the Schnorr
proof of knowledge. -/
theorem schnorr_verify (g p R : G) (x r c s : ZMod n)
    (hp : p = x • g) (hR : R = r • g) (hs : s = r + c * x) :
    s • g = R + c • p := by
  subst hp hR hs
  rw [add_smul, mul_smul]

/-- **Diffie–Hellman key agreement correctness.** Both parties derive the same
shared secret: Alice computes `a • (b • g)` from Bob's public `b • g`, Bob computes
`b • (a • g)` from Alice's public `a • g`, and these agree. -/
theorem dh_agree (g : G) (a b : ZMod n) : a • (b • g) = b • (a • g) := by
  rw [← mul_smul, ← mul_smul, mul_comm]

end Ecdlp.Schnorr
