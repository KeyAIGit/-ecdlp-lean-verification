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

open Finset in
/-- **Aggregate Schnorr verification (MuSig / FROST / Taproot multisig).** If each
party `i` holds key `Pᵢ = xᵢ·G`, nonce `Rᵢ = rᵢ·G`, and forms partial response
`sᵢ = rᵢ + c·xᵢ` under a shared challenge `c`, then the aggregate response verifies
against the aggregate key and nonce: `(∑ sᵢ)·G = (∑ Rᵢ) + c·(∑ Pᵢ)`. This is the
correctness of Schnorr multisignatures (deployed in Bitcoin Taproot). -/
theorem threshold_schnorr_aggregate {ι : Type*} (t : Finset ι) (g : G)
    (P R : ι → G) (x r : ι → ZMod n) (c : ZMod n)
    (hP : ∀ i, P i = x i • g) (hR : ∀ i, R i = r i • g) :
    (∑ i ∈ t, (r i + c * x i)) • g = (∑ i ∈ t, R i) + c • ∑ i ∈ t, P i := by
  simp only [hP, hR, Finset.sum_add_distrib, add_smul, Finset.sum_smul,
    Finset.smul_sum, mul_smul]

open Finset in
/-- **Feldman verifiable secret sharing (VSS) — share verification.** With sharing
polynomial `f(X) = ∑ⱼ aⱼ·Xʲ` and public coefficient commitments `Cⱼ = aⱼ·G`, the
share `s = f(i)` verifies against the commitments: `s·G = ∑ⱼ (iʲ)·Cⱼ`. This lets
each party check its share without the dealer's secret — the basis of distributed
key generation (DKG). -/
theorem feldman_vss_verify (g : G) (a : ℕ → ZMod n) (deg : ℕ) (i : ZMod n) :
    (∑ j ∈ range (deg + 1), a j * i ^ j) • g
      = ∑ j ∈ range (deg + 1), (i ^ j) • (a j • g) := by
  rw [Finset.sum_smul]
  exact Finset.sum_congr rfl (fun j _ => by rw [mul_comm, mul_smul])

end Ecdlp.Schnorr
