import Mathlib

/-!
# Uniform oriented-root generic boundary

This file formalizes only the arithmetic cost transfer used by the
`UNIFORM-ORIENTED-ROOT-CIRCUIT-056` research target.

If an exact oriented-root evaluator supplies one scalar-parity bit per query,
the standard bit-peeling reduction solves the full discrete logarithm with a
logarithmic number of evaluator calls plus public group arithmetic. Therefore
any lower bound for full discrete logarithm in a declared computation model
transfers to the evaluator after the reduction overhead is charged.

The file does not formalize the generic-group model, Shoup's theorem,
preprocessing lower bounds, elliptic curves, secp256k1, or an evaluator.
-/

namespace Ecdlp.ParityLift

/-- A lower bound for a full discrete-log computation transfers through an
explicit upper bound on the cost of the parity-based reduction. -/
theorem orientedRootCost_transfer
    (lowerBound dlpCost oracleCalls oracleCost overhead : ℕ)
    (hlower : lowerBound ≤ dlpCost)
    (hreduction : dlpCost ≤ oracleCalls * oracleCost + overhead) :
    lowerBound ≤ oracleCalls * oracleCost + overhead :=
  hlower.trans hreduction

/-- The preprocessing time-space lower-bound expression transfers after
substituting the charged parity-reduction cost. -/
theorem orientedRootPreprocessingTradeoff_transfer
    (successWeight order advice dlpCost oracleCalls oracleCost overhead : ℕ)
    (hlower : successWeight * order ≤ advice * dlpCost ^ 2)
    (hreduction : dlpCost ≤ oracleCalls * oracleCost + overhead) :
    successWeight * order
      ≤ advice * (oracleCalls * oracleCost + overhead) ^ 2 := by
  calc
    successWeight * order ≤ advice * dlpCost ^ 2 := hlower
    _ ≤ advice * (oracleCalls * oracleCost + overhead) ^ 2 := by
      gcongr

/-- If the reduction overhead has already been separated, the remaining lower
bound must be covered by the oracle calls. -/
theorem orientedRootCost_afterOverhead
    (lowerBound oracleCalls oracleCost overhead : ℕ)
    (hbound : lowerBound ≤ oracleCalls * oracleCost + overhead) :
    lowerBound - overhead ≤ oracleCalls * oracleCost := by
  omega

end Ecdlp.ParityLift
