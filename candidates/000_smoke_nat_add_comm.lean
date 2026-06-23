import Mathlib

namespace Ecdlp.Targets.Smoke

/-- Smoke target for the autonomous loop: a trivially true Nat fact the
    zero-cost tactic ladder (Tier 0) should close without any API call.
    Not an ECDLP result; it only exercises the prover-loop mechanism. -/
example (a b : Nat) : a + b = b + a := by
  omega

end Ecdlp.Targets.Smoke
