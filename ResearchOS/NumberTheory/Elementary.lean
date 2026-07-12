import Mathlib

/-!
# Elementary number theory — a NON-ECC domain instance of the Research OS

This module is the first **non-elliptic-curve** domain to flow through the same verifier
slot as the ECDLP substrate. Its whole purpose is to demonstrate that the pipeline is
*domain-agnostic*: a claim corpus (`domains/number-theory/corpus.md`) whose facts are
discharged by the Lean kernel, under the same no-`sorry` / no-axiom guarantees enforced on
the ECDLP base. The verifier does not know or care that these are number-theory facts
rather than curve facts — which is exactly the reusable-engine claim, now demonstrated on a
second, unrelated subject.

All results are elementary and kernel-checked by `norm_num` (no `native_decide`, so they
stay strictly inside the standard axiom base {propext, Classical.choice, Quot.sound} — the
`#print axioms` lines in `Ecdlp/AxiomAudit.lean` enforce this).
-/

namespace ResearchOS.NumberTheory

/-- 2017 is prime. -/
theorem prime_2017 : Nat.Prime 2017 := by norm_num

/-- The Mersenne number `M₁₃ = 2¹³ − 1 = 8191` is prime (the fifth Mersenne prime, with
exponents 2, 3, 5, 7, 13). -/
theorem mersenne_M13_prime : Nat.Prime 8191 := by norm_num

/-- 561 is **not** prime — it is the smallest Carmichael number (a composite that is a
Fermat pseudoprime to every base coprime to it). -/
theorem carmichael_561_not_prime : ¬ Nat.Prime 561 := by norm_num

/-- Its factorization `561 = 3 · 11 · 17`: squarefree with three distinct prime factors —
the Korselt structure every Carmichael number has. -/
theorem carmichael_561_factorization : (561 : ℕ) = 3 * 11 * 17 := by norm_num

end ResearchOS.NumberTheory
