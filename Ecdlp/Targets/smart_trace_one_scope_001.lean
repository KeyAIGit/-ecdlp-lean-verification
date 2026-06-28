import Mathlib

namespace Ecdlp.Targets.SmartTraceOneScope

/-- [smart-trace-one-scope-001] **Anomalous-curve scope (Smart/SSSA attack).**
An elliptic curve over `𝔽_p` is *anomalous* — `#E(𝔽_p) = p` — exactly when its trace
of Frobenius `a_p` equals `1`, because `#E(𝔽_p) = p + 1 - a_p`. This is the boundary
condition that the Smart/SSSA `p`-adic-logarithm attack requires; secp256k1 is proved
NOT anomalous in `Ecdlp/Proved/TraceOfFrobenius.lean`. Open conjecture stem (the
arithmetic equivalence given the trace identity). -/
theorem smart_trace_one_scope (p N : ℕ) (a_p : ℤ)
    (htr : (N : ℤ) = (p : ℤ) + 1 - a_p) :
    (N : ℤ) = (p : ℤ) ↔ a_p = 1 := by
  sorry

end Ecdlp.Targets.SmartTraceOneScope
