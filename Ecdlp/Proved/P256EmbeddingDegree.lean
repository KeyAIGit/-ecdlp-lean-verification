import Mathlib
import Ecdlp.Proved.P256Curve

/-!
# NIST P-256 has no small embedding degree (MOV / Frey–Rück resistance)

The second live domain's first attack-boundary rung, mirroring secp256k1's
`Ecdlp/Proved/EmbeddingDegree.lean`. The MOV / Frey–Rück transfer reduces ECDLP on
`E(𝔽_p)` to the discrete log in `𝔽_{p^k}^×`, where `k` — the **embedding degree** — is the
least `k ≥ 1` with `n ∣ p^k − 1` (i.e. `p^k ≡ 1 (mod n)`). It is only useful when `k` is
small enough that `𝔽_{p^k}` admits a subexponential discrete log.

This file machine-checks that for P-256, `p^k ≢ 1 (mod n)` for every `1 ≤ k ≤ 100`, so the
embedding degree exceeds `100` — the target field `𝔽_{p^k}` would need `k > 100` (an
extension of more than ~25 000 bits), far beyond any feasible index-calculus discrete log.
As for secp256k1, the pairing transfer — even were the Weil/Tate pairing available in
Mathlib — could not help; ECDLP on P-256 does not leak through MOV. Pure modular arithmetic
on the (now kernel-verified prime) `p` and `n`; no point-counting / `#E` required.
-/

namespace Ecdlp.P256

/-- **NIST P-256 has embedding degree > 100.** For every `k` with `1 ≤ k ≤ 100` (written as
`j < 100`, `k = j + 1`), `p^k ≢ 1 (mod n)`. So the MOV / Frey–Rück transfer would require an
intractably large extension field `𝔽_{p^k}` with `k > 100` — the discrete log on P-256 does
not transfer to a feasible finite-field DLP. -/
theorem p256_embedding_degree_gt_100 :
    ∀ j, j < 100 → p ^ (j + 1) % n ≠ 1 := by
  native_decide

end Ecdlp.P256
