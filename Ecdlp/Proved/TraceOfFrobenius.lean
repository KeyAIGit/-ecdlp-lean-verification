import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# secp256k1: arithmetic of `p + 1 − n` (the Frobenius trace `t`)

**Now unconditional.** What is machine-checked below are properties of the **integer**
`t := p + 1 − n` over `ℤ`. This integer *is* the curve's **trace of Frobenius**, because
`#E(𝔽_p) = n` is now a **theorem** (`Ecdlp.Curve.secp256k1_card_point_eq_n`,
`CurveCardinalityExact.lean`) — proved *curve-specifically* without the general Hasse bound or
Schoof (`#E ≤ 2p+1 < 3n` plus `E[2] = {O}`; see `notes/HASSE_RECON.md`). So the labels
"ordinary", "non-anomalous", and "Hasse-consistent" below hold **for the curve unconditionally**;
the proved content here is the arithmetic of `p + 1 − n` = `t`, and the CM data it satisfies is in
`FrobeniusCM.lean` (`N(π)=p`, `Tr(π)=t`, `4p=t²+3b²`).

For the secp256k1 curve `E/𝔽_p`, with the proved group order `#E = n` (`secp256k1_card_point_eq_n`;
cofactor 1), the **trace of Frobenius** is `t = p + 1 − n`. Two classical "transfer"
attacks are governed entirely by `t`:

* `t = 0` ⟺ `E` is **supersingular** ⟺ embedding degree ≤ 6, so the MOV/Frey–Rück
  pairing transfer to `𝔽_{p^k}` is feasible.
* `t = 1` ⟺ `#E = p`, i.e. `E` is **anomalous** ⟺ the Smart / Semaev–Satoh–Araki
  (SSSA) attack solves the ECDLP in linear time via the `p`-adic elliptic logarithm.

This file machine-checks (over `ℤ`, from the proved order `#E = n`) that secp256k1
avoids both, and is consistent with the Hasse bound:

* `t ≠ 0` — **ordinary**, not supersingular (no supersingular MOV).
* `t ≠ 1` — **not anomalous** (Smart/SSSA inapplicable).
* `t² ≤ 4p` — the **Hasse** bound `|t| ≤ 2√p` (sanity: `#E = n` is in the valid range).

Together with `EmbeddingDegree.lean` (no small embedding degree even in the ordinary
case), these are the verified boundary nodes for the pairing/transfer barriers: the
hardness of ECDLP on secp256k1 does not leak through MOV/FR or Smart/SSSA.
-/

namespace Ecdlp.Curve

/-- **secp256k1 is ordinary, non-anomalous, and Hasse-consistent.** Since `#E = n` (proved),
the trace `t = p + 1 − n` satisfies `t ≠ 0` (not supersingular), `t ≠ 1` (not
anomalous — Smart/SSSA does not apply), and `t² ≤ 4p` (the Hasse bound). -/
theorem secp256k1_trace_ordinary_nonanomalous :
    ((Secp256k1.p : ℤ) + 1 - Secp256k1.n) ≠ 0 ∧
    ((Secp256k1.p : ℤ) + 1 - Secp256k1.n) ≠ 1 ∧
    ((Secp256k1.p : ℤ) + 1 - Secp256k1.n) ^ 2 ≤ 4 * (Secp256k1.p : ℤ) := by
  native_decide

end Ecdlp.Curve
