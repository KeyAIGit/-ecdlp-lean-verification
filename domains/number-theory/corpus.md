# Elementary number theory domain corpus (atomic claims + status)

Starter claim corpus for the **elementary number theory** domain — the first **non-elliptic-curve**
instance of the Research OS, and the machine-checked evidence that the pipeline is not ECC-only.
Small and honest: each claim is **verified** by the Lean kernel in the separate `ResearchOS`
library (`ResearchOS/NumberTheory/Elementary.lean`), under the same no-`sorry` / no-axiom gates as
the ECDLP base. No claim is asserted before the kernel accepts it. These facts are deliberately
unrelated to elliptic curves — the verifier slot is identical; only the subject changed.

Provenance: standard elementary number theory (primality, Mersenne primes, Carmichael numbers /
Korselt's criterion). All proofs are `norm_num`, so they stay strictly inside the standard axiom
base {propext, Classical.choice, Quot.sound} — no `native_decide` (see `Ecdlp/AxiomAudit.lean`).

| id | claim | status | evidence |
|---|---|---|---|
| nt-prime-2017 | 2017 is prime | **verified** | `ResearchOS/NumberTheory/Elementary.lean` (`prime_2017`) |
| nt-mersenne-m13 | the Mersenne number `M₁₃ = 2¹³ − 1 = 8191` is prime (the 5th Mersenne prime) | **verified** | `ResearchOS/NumberTheory/Elementary.lean` (`mersenne_M13_prime`) |
| nt-carmichael-561-composite | 561, the smallest Carmichael number, is **not** prime | **verified** | `ResearchOS/NumberTheory/Elementary.lean` (`carmichael_561_not_prime`) |
| nt-carmichael-561-korselt | `561 = 3 · 11 · 17` — squarefree, three distinct prime factors (Korselt structure) | **verified** | `ResearchOS/NumberTheory/Elementary.lean` (`carmichael_561_factorization`) |
| nt-mersenne-m17 | the Mersenne number `M₁₇ = 2¹⁷ − 1 = 131071` is prime | **verified** | `ResearchOS/NumberTheory/MoreFacts.lean` (`mersenne_M17_prime`) |
| nt-mersenne-m19 | the Mersenne number `M₁₉ = 2¹⁹ − 1 = 524287` is prime | **verified** | `ResearchOS/NumberTheory/MoreFacts.lean` (`mersenne_M19_prime`) |
| nt-carmichael-1105-composite | 1105 (2nd Carmichael number) is **not** prime | **verified** | `ResearchOS/NumberTheory/MoreFacts.lean` (`carmichael_1105_not_prime`) |
| nt-carmichael-1105-korselt | `1105 = 5 · 13 · 17` — squarefree, three distinct prime factors | **verified** | `ResearchOS/NumberTheory/MoreFacts.lean` (`carmichael_1105_factorization`) |
| nt-carmichael-1729-composite | 1729 (3rd Carmichael number; Hardy–Ramanujan taxicab number) is **not** prime | **verified** | `ResearchOS/NumberTheory/MoreFacts.lean` (`carmichael_1729_not_prime`) |
| nt-carmichael-1729-korselt | `1729 = 7 · 13 · 19` — squarefree, three distinct prime factors | **verified** | `ResearchOS/NumberTheory/MoreFacts.lean` (`carmichael_1729_factorization`) |
| nt-twin-10007-10009 | `(10007, 10009)` is a twin-prime pair (both prime) | **verified** | `ResearchOS/NumberTheory/MoreFacts.lean` (`prime_10007`, `prime_10009`) |

**Why this domain exists.** It reserves nothing and proves the reusable-engine claim on a second,
unrelated subject: the same corpus → verifier → truth-graph slots that carry secp256k1 facts also
carry number-theory facts, verified by the same kernel with the same trust guarantees. It is
intentionally minimal — a proof of portability, not a research program in number theory.
