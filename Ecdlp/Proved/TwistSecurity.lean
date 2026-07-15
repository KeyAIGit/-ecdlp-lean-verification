import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# secp256k1 quadratic-twist security certificate

The classical attack-resistance capstone (`ClassicalSecurityProfile.lean`) certifies that
every known shortcut against the discrete log **on the curve `E`** is blocked. It says nothing
about the **quadratic twist** `Ẽ / 𝔽_p`, and that omission is exactly where secp256k1 is
weakest.

A single-coordinate (`x`-only) scalar multiplication — a Montgomery ladder that ignores the
`y`-coordinate — cannot tell whether its input `x` lies on `E` or on the twist `Ẽ`: both share
the same `x`-line. So an implementation that skips point validation and receives a twist point
is doing arithmetic in `Ẽ(𝔽_p)` instead of `E(𝔽_p)`. The security it then has is the security
of the **twist**, not of the curve.

For secp256k1 the twist order is
`#Ẽ(𝔽_p) = p + 1 + t = 2p + 2 − n`  (where `t = p + 1 − n` is the Frobenius trace, and
`#E = n` is the proved cofactor-1 point count `secp256k1_card_point_eq_n`). Its exact
factorization is
```
#Ẽ = 3² · 13² · 3319 · 22639 · Q,     Q a 220-bit prime.
```
Two honest consequences, both certified below:

* **The twist is not prime-order.** It carries a nontrivial cofactor `3²·13²·3319·22639 =
  114286177161 ≈ 2³⁷`, i.e. genuine small-order subgroups. A twist point can be *confined* to
  one of them (a small-subgroup / invalid-curve confinement), unlike on `E` where the point
  group is simple (`secp256k1_point_group_no_proper_subgroup`).
* **Twist security is below the curve's.** The largest prime factor `Q` satisfies
  `2²¹⁹ < Q < 2²²⁰`, so generic discrete log in the twist's big subgroup costs `≈ √Q < 2¹¹⁰`
  — strictly under the curve's `≈ 2¹²⁸` (`secp256k1_generic_security`).

This is a **limitation certificate**, not a strength claim: it is *why* correct secp256k1
implementations MUST validate that a received point is on `E` (or carry a `y`-coordinate and
check the curve equation) before scalar multiplication. `Q`'s primality is a full recursive
Pratt certificate (`scripts/pratt_certificate.py`, witness `a = 7`, 10 nodes); the order and
its factorization are `native_decide` arithmetic. No new axioms beyond the compiler-trusted
`Lean.ofReduceBool` the `native_decide` facts already carry.
-/

namespace Ecdlp.Curve.TwistPrimality
open Nat

theorem pr_26886215762884663 : Nat.Prime 26886215762884663 := by
  refine lucas_primality 26886215762884663 (3 : ZMod 26886215762884663) (by native_decide) ?_
  intro q hq hqd
  rw [show (26886215762884663 : ℕ) - 1 = 2 ^ 1 * (3 ^ 1 * (177481 ^ 1 * (152077 ^ 1 * (166021 ^ 1)))) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
  ·
    rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 3 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
    ·
      rcases (Nat.Prime.dvd_mul hq).mp h with h | h
      · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 177481 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
      ·
        rcases (Nat.Prime.dvd_mul hq).mp h with h | h
        · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 152077 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
        ·
          rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 166021 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide

theorem pr_25465723 : Nat.Prime 25465723 := by
  refine lucas_primality 25465723 (3 : ZMod 25465723) (by native_decide) ?_
  intro q hq hqd
  rw [show (25465723 : ℕ) - 1 = 2 ^ 1 * (3 ^ 1 * (1213 ^ 1 * (3499 ^ 1))) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
  ·
    rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 3 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
    ·
      rcases (Nat.Prime.dvd_mul hq).mp h with h | h
      · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 1213 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
      ·
        rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 3499 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide

theorem pr_2346158371 : Nat.Prime 2346158371 := by
  refine lucas_primality 2346158371 (2 : ZMod 2346158371) (by native_decide) ?_
  intro q hq hqd
  rw [show (2346158371 : ℕ) - 1 = 2 ^ 1 * (3 ^ 1 * (5 ^ 1 * (89 ^ 1 * (179 ^ 1 * (4909 ^ 1))))) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
  ·
    rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 3 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
    ·
      rcases (Nat.Prime.dvd_mul hq).mp h with h | h
      · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 5 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
      ·
        rcases (Nat.Prime.dvd_mul hq).mp h with h | h
        · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 89 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
        ·
          rcases (Nat.Prime.dvd_mul hq).mp h with h | h
          · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 179 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
          ·
            rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 4909 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide

theorem pr_453934566793 : Nat.Prime 453934566793 := by
  refine lucas_primality 453934566793 (5 : ZMod 453934566793) (by native_decide) ?_
  intro q hq hqd
  rw [show (453934566793 : ℕ) - 1 = 2 ^ 3 * (3 ^ 2 * (7 ^ 1 * (9781 ^ 1 * (92083 ^ 1)))) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
  ·
    rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 3 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
    ·
      rcases (Nat.Prime.dvd_mul hq).mp h with h | h
      · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 7 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
      ·
        rcases (Nat.Prime.dvd_mul hq).mp h with h | h
        · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 9781 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
        ·
          rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 92083 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide

theorem pr_4539345667931 : Nat.Prime 4539345667931 := by
  refine lucas_primality 4539345667931 (2 : ZMod 4539345667931) (by native_decide) ?_
  intro q hq hqd
  rw [show (4539345667931 : ℕ) - 1 = 2 ^ 1 * (5 ^ 1 * (453934566793 ^ 1)) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
  ·
    rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 5 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
    ·
      rw [(Nat.prime_dvd_prime_iff_eq hq pr_453934566793).mp (hq.dvd_of_dvd_pow h)]; native_decide

theorem pr_25910585072550149 : Nat.Prime 25910585072550149 := by
  refine lucas_primality 25910585072550149 (2 : ZMod 25910585072550149) (by native_decide) ?_
  intro q hq hqd
  rw [show (25910585072550149 : ℕ) - 1 = 2 ^ 2 * (1427 ^ 1 * (4539345667931 ^ 1)) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
  ·
    rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 1427 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
    ·
      rw [(Nat.prime_dvd_prime_iff_eq hq pr_4539345667931).mp (hq.dvd_of_dvd_pow h)]; native_decide

theorem pr_132401351950596217829363773663 : Nat.Prime 132401351950596217829363773663 := by
  refine lucas_primality 132401351950596217829363773663 (3 : ZMod 132401351950596217829363773663) (by native_decide) ?_
  intro q hq hqd
  rw [show (132401351950596217829363773663 : ℕ) - 1 = 2 ^ 1 * (3 ^ 2 * (11 ^ 2 * (2346158371 ^ 1 * (25910585072550149 ^ 1)))) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
  ·
    rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 3 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
    ·
      rcases (Nat.Prime.dvd_mul hq).mp h with h | h
      · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 11 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
      ·
        rcases (Nat.Prime.dvd_mul hq).mp h with h | h
        · rw [(Nat.prime_dvd_prime_iff_eq hq pr_2346158371).mp (hq.dvd_of_dvd_pow h)]; native_decide
        ·
          rw [(Nat.prime_dvd_prime_iff_eq hq pr_25910585072550149).mp (hq.dvd_of_dvd_pow h)]; native_decide

theorem pr_29235542524211150858901814862527031 : Nat.Prime 29235542524211150858901814862527031 := by
  refine lucas_primality 29235542524211150858901814862527031 (7 : ZMod 29235542524211150858901814862527031) (by native_decide) ?_
  intro q hq hqd
  rw [show (29235542524211150858901814862527031 : ℕ) - 1 = 2 ^ 1 * (5 ^ 1 * (71 ^ 1 * (311 ^ 1 * (132401351950596217829363773663 ^ 1)))) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
  ·
    rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 5 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
    ·
      rcases (Nat.Prime.dvd_mul hq).mp h with h | h
      · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 71 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
      ·
        rcases (Nat.Prime.dvd_mul hq).mp h with h | h
        · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 311 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
        ·
          rw [(Nat.prime_dvd_prime_iff_eq hq pr_132401351950596217829363773663).mp (hq.dvd_of_dvd_pow h)]; native_decide

theorem pr_1489008455352563922568011402972792902916827 : Nat.Prime 1489008455352563922568011402972792902916827 := by
  refine lucas_primality 1489008455352563922568011402972792902916827 (2 : ZMod 1489008455352563922568011402972792902916827) (by native_decide) ?_
  intro q hq hqd
  rw [show (1489008455352563922568011402972792902916827 : ℕ) - 1 = 2 ^ 1 * (25465723 ^ 1 * (29235542524211150858901814862527031 ^ 1)) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
  ·
    rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq pr_25465723).mp (hq.dvd_of_dvd_pow h)]; native_decide
    ·
      rw [(Nat.prime_dvd_prime_iff_eq hq pr_29235542524211150858901814862527031).mp (hq.dvd_of_dvd_pow h)]; native_decide

theorem pr_1013176677300131846900870239606035638738100997248092069256697437031 : Nat.Prime 1013176677300131846900870239606035638738100997248092069256697437031 := by
  refine lucas_primality 1013176677300131846900870239606035638738100997248092069256697437031 (7 : ZMod 1013176677300131846900870239606035638738100997248092069256697437031) (by native_decide) ?_
  intro q hq hqd
  rw [show (1013176677300131846900870239606035638738100997248092069256697437031 : ℕ) - 1 = 2 ^ 1 * (3 ^ 1 * (5 ^ 1 * (11 ^ 1 * (53 ^ 1 * (1447 ^ 1 * (26886215762884663 ^ 1 * (1489008455352563922568011402972792902916827 ^ 1))))))) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
  ·
    rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 3 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
    ·
      rcases (Nat.Prime.dvd_mul hq).mp h with h | h
      · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 5 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
      ·
        rcases (Nat.Prime.dvd_mul hq).mp h with h | h
        · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 11 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
        ·
          rcases (Nat.Prime.dvd_mul hq).mp h with h | h
          · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 53 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
          ·
            rcases (Nat.Prime.dvd_mul hq).mp h with h | h
            · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 1447 by norm_num)).mp (hq.dvd_of_dvd_pow h)]; native_decide
            ·
              rcases (Nat.Prime.dvd_mul hq).mp h with h | h
              · rw [(Nat.prime_dvd_prime_iff_eq hq pr_26886215762884663).mp (hq.dvd_of_dvd_pow h)]; native_decide
              ·
                rw [(Nat.prime_dvd_prime_iff_eq hq pr_1489008455352563922568011402972792902916827).mp (hq.dvd_of_dvd_pow h)]; native_decide
end Ecdlp.Curve.TwistPrimality

namespace Ecdlp.Curve
open Ecdlp.Curve.TwistPrimality

/-- The largest prime factor of the secp256k1 twist order is prime (full Pratt certificate). -/
theorem secp256k1_twist_maxprime_prime :
    Nat.Prime 1013176677300131846900870239606035638738100997248092069256697437031 :=
  pr_1013176677300131846900870239606035638738100997248092069256697437031

/-- **Exact factorization of the secp256k1 quadratic-twist order.**
`#Ẽ(𝔽_p) = 2p + 2 − n = 3² · 13² · 3319 · 22639 · Q`, exhibiting the `≈ 2³⁷` cofactor and the
220-bit large prime `Q`. (`#Ẽ = p + 1 + t` with `t = p+1−n`; `#E = n` is proved.) -/
theorem secp256k1_twist_order_factorization :
    2 * Secp256k1.p + 2 - Secp256k1.n
      = 3 ^ 2 * 13 ^ 2 * 3319 * 22639 * 1013176677300131846900870239606035638738100997248092069256697437031 := by
  native_decide

/-- **secp256k1 quadratic-twist security profile** (one certificate).
* twist order factors as `3² · 13² · 3319 · 22639 · Q` (`#Ẽ = 2p + 2 − n`);
* `Q` is prime and `2²¹⁹ < Q < 2²²⁰` (220-bit ⇒ generic twist-DLP `≈ √Q < 2¹¹⁰`, below the
  curve's `2¹²⁸`);
* the cofactor `3² · 13² · 3319 · 22639 = 114286177161 > 1` is nontrivial — the twist has
  small-order subgroups, so `x`-only arithmetic on a twist point can be confined.

Honest reading: a *limitation*. The twist is weaker than the curve; this is the machine-checked
reason single-coordinate secp256k1 code must validate points. Says nothing about non-generic
or quantum attacks. -/
theorem secp256k1_twist_security_profile :
    2 * Secp256k1.p + 2 - Secp256k1.n
        = 3 ^ 2 * 13 ^ 2 * 3319 * 22639 * 1013176677300131846900870239606035638738100997248092069256697437031
      ∧ Nat.Prime 1013176677300131846900870239606035638738100997248092069256697437031
      ∧ 2 ^ 219 < 1013176677300131846900870239606035638738100997248092069256697437031 ∧ 1013176677300131846900870239606035638738100997248092069256697437031 < 2 ^ 220
      ∧ 1 < 3 ^ 2 * 13 ^ 2 * 3319 * 22639 :=
  ⟨secp256k1_twist_order_factorization, secp256k1_twist_maxprime_prime,
    by native_decide, by native_decide, by native_decide⟩

end Ecdlp.Curve
