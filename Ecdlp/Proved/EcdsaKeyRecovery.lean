import Mathlib

/-!
# ECDSA private-key recovery — signature algebra

ECDSA signatures satisfy the scalar identity

  `s · k = z + r · x`

where

* `s` is the signature scalar (second component of the signature),
* `k` is the per-signature nonce,
* `z` is the (truncated) hash of the message,
* `r` is the `x`-coordinate of the nonce point `k·G` (first component), and
* `x` is the signer's private key.

This file records two classical private-key recovery facts as **pure field
identities** over an abstract `[Field F]`. As with `schnorr_extract` in
`Ecdlp/Proved/SchnorrSoundness.lean`, these are equational/linear-algebra
statements: there is **no adversary, no hash / random oracle, no probability
space, and no reduction to discrete-log hardness** — consistent with the scope
recorded in `ABSTRACT_SCOPE.md`. They capture exactly the arithmetic step by
which a leaked or reused nonce lets one solve the signing equation(s) for the
private key `x`.
-/

namespace Ecdlp.Schnorr

variable {F : Type*} [Field F]

/-- **ECDSA nonce-reuse key recovery.** If a signer produces two signatures
`(r, s₁)` and `(r, s₂)` on messages with hashes `z₁, z₂` using the **same nonce**
`k` (hence the same `r`, since `r` depends only on `k·G`), then subtracting the two
signing equations `sᵢ·k = zᵢ + r·x` eliminates `r·x` and pins down the nonce
`k = (z₁ − z₂)/(s₁ − s₂)`; back-substitution then recovers the private key
`x = (s₁·k − z₁)/r`. This is the exact algebra behind the real-world key thefts
caused by nonce reuse — the Sony PlayStation 3 firmware-signing key extraction and
the 2013 Android `SecureRandom` Bitcoin-wallet key thefts. -/
theorem ecdsa_nonce_reuse_recovers {k x r z₁ z₂ s₁ s₂ : F}
    (h₁ : s₁ * k = z₁ + r * x) (h₂ : s₂ * k = z₂ + r * x)
    (hs : s₁ ≠ s₂) (hr : r ≠ 0) :
    k = (z₁ - z₂) / (s₁ - s₂) ∧ x = (s₁ * k - z₁) / r := by
  have hsne : s₁ - s₂ ≠ 0 := sub_ne_zero.mpr hs
  refine ⟨?_, ?_⟩
  · have key : (s₁ - s₂) * k = z₁ - z₂ := by linear_combination h₁ - h₂
    field_simp
    linear_combination key
  · have key : r * x = s₁ * k - z₁ := by linear_combination -h₁
    field_simp
    linear_combination key

/-- **ECDSA known/leaked-nonce key recovery.** If the nonce `k` used for a single
signature `(r, s)` is known to the attacker — e.g. it was leaked, or was biased /
partially predictable as in a hidden-number-problem (HNP) lattice attack that first
reconstructs `k` — then the signing equation `s·k = z + r·x` is linear in the private
key `x`, which is recovered directly as `x = (s·k − z)/r`. -/
theorem ecdsa_known_nonce_recovers_key {k x r z s : F}
    (h : s * k = z + r * x) (hr : r ≠ 0) : x = (s * k - z) / r := by
  field_simp
  linear_combination -h

end Ecdlp.Schnorr
