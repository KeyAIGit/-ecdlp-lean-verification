import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# secp256k1: arithmetic of `p + 1 − n` (the Frobenius trace *conditional on* `#E = n`)

**Conditionality (read first).** What is machine-checked below are properties of the **integer**
`t := p + 1 − n` over `ℤ`. This integer *is* the curve's **trace of Frobenius only once
`#E(𝔽_p) = n` is proved** — which this repo does **not** prove: `#E = n` needs the Hasse bound
(absent from Mathlib v4.31; see `notes/HASSE_RECON.md`), and is currently a *pinned hypothesis*
(the published cofactor-1 order), not a theorem. So the labels "ordinary", "non-anomalous", and
"Hasse-consistent" below hold **for the curve** exactly under the assumption `#E = n`; the proved
content is the arithmetic of `p + 1 − n`. (`n ∣ #E` is now proved — `CurveCardinality.lean` — so
`#E ∈ {n, 2n, …}`; pinning `#E = n` still awaits Hasse.)

For the secp256k1 curve `E/𝔽_p`, *assuming* group order `#E = n` (the published, machine-checked
prime order; cofactor 1), the **trace of Frobenius** is `t = p + 1 − n`. Two classical "transfer"
attacks are governed entirely by `t`:

* `t = 0` ⟺ `E` is **supersingular** ⟺ embedding degree ≤ 6, so the MOV/Frey–Rück
  pairing transfer to `𝔽_{p^k}` is feasible.
* `t = 1` ⟺ `#E = p`, i.e. `E` is **anomalous** ⟺ the Smart / Semaev–Satoh–Araki
  (SSSA) attack solves the ECDLP in linear time via the `p`-adic elliptic logarithm.

This file machine-checks (over `ℤ`, from the pinned order `#E = n`) that secp256k1
avoids both, and is consistent with the Hasse bound:

* `t ≠ 0` — **ordinary**, not supersingular (no supersingular MOV).
* `t ≠ 1` — **not anomalous** (Smart/SSSA inapplicable).
* `t² ≤ 4p` — the **Hasse** bound `|t| ≤ 2√p` (sanity: `#E = n` is in the valid range).

Together with `EmbeddingDegree.lean` (no small embedding degree even in the ordinary
case), these are the verified boundary nodes for the pairing/transfer barriers: the
hardness of ECDLP on secp256k1 does not leak through MOV/FR or Smart/SSSA.
-/

namespace Ecdlp.Curve

/-- **secp256k1 is ordinary, non-anomalous, and Hasse-consistent.** With `#E = n`,
the trace `t = p + 1 − n` satisfies `t ≠ 0` (not supersingular), `t ≠ 1` (not
anomalous — Smart/SSSA does not apply), and `t² ≤ 4p` (the Hasse bound). -/
theorem secp256k1_trace_ordinary_nonanomalous :
    ((Secp256k1.p : ℤ) + 1 - Secp256k1.n) ≠ 0 ∧
    ((Secp256k1.p : ℤ) + 1 - Secp256k1.n) ≠ 1 ∧
    ((Secp256k1.p : ℤ) + 1 - Secp256k1.n) ^ 2 ≤ 4 * (Secp256k1.p : ℤ) := by
  native_decide

end Ecdlp.Curve
