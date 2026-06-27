import Mathlib

namespace Ecdlp.Targets.FeatherlessTest

/-- Live test target for the Featherless model tier. `n < 2^n` needs induction, so
the Tier-0 tactic ladder (rfl/decide/native_decide/simp/omega/ring/aesop) should
NOT close it — forcing escalation to the Featherless prover models. Temporary;
removed after the test. -/
theorem lt_two_pow_test (n : ℕ) : n < 2 ^ n := by
  sorry

end Ecdlp.Targets.FeatherlessTest
