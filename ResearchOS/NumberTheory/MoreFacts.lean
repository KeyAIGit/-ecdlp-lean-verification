import Mathlib

/-!
# More elementary number-theory facts

Additional elementary number-theory facts in the non-elliptic-curve domain,
extending `ResearchOS.NumberTheory.Elementary`. Every statement here is
kernel-checked by `norm_num`, stays inside the standard axiom base
(no `native_decide`), and is kernel-complete with no placeholders.

Contents:

* Two further Mersenne primes: M17 = 2^17 - 1 = 131071 and
  M19 = 2^19 - 1 = 524287.
* Two further Carmichael numbers, 1105 and 1729, each shown composite
  together with its squarefree factorization into three distinct primes.
* The twin-prime pair (10007, 10009), stated as two primality facts.
-/

namespace ResearchOS.NumberTheory

/-- The Mersenne number M17 = 2^17 - 1 = 131071 is prime. -/
theorem mersenne_M17_prime : Nat.Prime 131071 := by norm_num

/-- The Mersenne number M19 = 2^19 - 1 = 524287 is prime. -/
theorem mersenne_M19_prime : Nat.Prime 524287 := by norm_num

/-- The Carmichael number 1105 is composite. -/
theorem carmichael_1105_not_prime : ¬ Nat.Prime 1105 := by norm_num

/-- Squarefree factorization of the Carmichael number 1105 into three
distinct primes: 1105 = 5 * 13 * 17. -/
theorem carmichael_1105_factorization : (1105 : ℕ) = 5 * 13 * 17 := by norm_num

/-- The Carmichael number 1729 (also the Hardy–Ramanujan taxicab number,
the smallest number expressible as a sum of two positive cubes in two
different ways) is composite. -/
theorem carmichael_1729_not_prime : ¬ Nat.Prime 1729 := by norm_num

/-- Squarefree factorization of the Carmichael number 1729 into three
distinct primes: 1729 = 7 * 13 * 19. -/
theorem carmichael_1729_factorization : (1729 : ℕ) = 7 * 13 * 19 := by norm_num

/-- 10007 is prime; together with 10009 it forms a twin-prime pair. -/
theorem prime_10007 : Nat.Prime 10007 := by norm_num

/-- 10009 is prime; together with 10007 it forms a twin-prime pair. -/
theorem prime_10009 : Nat.Prime 10009 := by norm_num

end ResearchOS.NumberTheory
