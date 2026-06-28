import Mathlib

/-!
# Anomalous-curve scope (Smart/SSSA attack boundary)

An elliptic curve over `𝔽_p` is *anomalous* when `#E(𝔽_p) = p`. Via the
point-count identity `#E(𝔽_p) = p + 1 - a_p` (Hasse), this is equivalent to the
trace of Frobenius `a_p` being `1`. The anomalous case is exactly where the
Smart/SSSA `p`-adic-elliptic-logarithm attack applies (it solves ECDLP in
polynomial time there). secp256k1 is proved **not** anomalous in
`Ecdlp/Proved/TraceOfFrobenius.lean`, so the attack does not apply to it.

Provenance: this is the first corpus-derived target (`smart-trace-one-scope-001`,
`Ecdlp/Targets/`) closed end-to-end by the **warm-server Tier-0 prover sweep**
(`omega`), then re-verified by the CI kernel gate.
-/

namespace Ecdlp.Curve

/-- **Anomalous ⟺ trace one.** With the Hasse point-count identity
`#E(𝔽_p) = p + 1 - a_p` (hypothesis `htr`), the curve is anomalous (`#E = p`) exactly
when the trace of Frobenius `a_p = 1`. -/
theorem anomalous_iff_trace_one (p N : ℕ) (a_p : ℤ)
    (htr : (N : ℤ) = (p : ℤ) + 1 - a_p) :
    (N : ℤ) = (p : ℤ) ↔ a_p = 1 := by
  omega

end Ecdlp.Curve
