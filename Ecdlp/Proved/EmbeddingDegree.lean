import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# secp256k1 has no small embedding degree (MOV / Frey–Rück resistance)

The MOV / Frey–Rück transfer reduces ECDLP on `E(𝔽_p)` to the discrete-log problem
in the multiplicative group `𝔽_{p^k}^×`, where `k` — the **embedding degree** — is
the least `k ≥ 1` with `n ∣ p^k − 1` (equivalently `p^k ≡ 1 (mod n)`). The transfer
is only useful when `k` is small enough that `𝔽_{p^k}` admits a subexponential
discrete log; for secp256k1 the embedding degree is astronomically large, so the
pairing transfer is useless in practice.

This file machine-checks the concrete fact behind that: for every `1 ≤ k ≤ 100`,
`p^k ≢ 1 (mod n)`. Hence secp256k1's embedding degree exceeds `100` — the MOV/FR
target field `𝔽_{p^k}` would need `k > 100`, i.e. an extension of more than
~25 000 bits, far beyond any feasible index-calculus discrete log.

This is the verified **boundary node** for barrier `B3-weil-pairing`: the transfer
*exists* in theory (it needs the Weil/Tate pairing, not yet in Mathlib), but here we
machine-check that even if the pairing were available it could not help — no small
`k` works. The hardness of ECDLP on secp256k1 therefore does not leak through MOV.
-/

namespace Ecdlp.Curve

/-- **secp256k1 has embedding degree > 100.** For every `k` with `1 ≤ k ≤ 100`
(written as `j < 100` with `k = j + 1`), `p^k ≢ 1 (mod n)`. So the MOV/Frey–Rück
pairing transfer would require an extension field `𝔽_{p^k}` with `k > 100` —
intractably large — and the discrete log on secp256k1 does not transfer to a
feasible finite-field DLP. -/
theorem secp256k1_embedding_degree_gt_100 :
    ∀ j, j < 100 → Secp256k1.p ^ (j + 1) % Secp256k1.n ≠ 1 := by
  native_decide

end Ecdlp.Curve
