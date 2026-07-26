import Mathlib
import Ecdlp.Secp256k1Verified
import Ecdlp.Proved.Secp256k1PrimeP

/-!
# The `p - 1` smooth-divisor ceiling for secp256k1

A *target-property screen fact*: an exact, kernel-checked ceiling on how smooth a
divisor of `p - 1` can be.

The complete prime factorization of `p - 1` is already available in this
repository as a by-product of the Pratt certificate for `p`
(`Ecdlp/Proved/Secp256k1PrimeP.lean`), which had to factor `p - 1` in order to
apply `Nat.lucas_primality`:

```text
p - 1 = 2 · 3 · 7 · 13441 · C,      C = 2051152820…5397371   (237 bits, prime)
```

Every factor is proved prime there, `C` by
`Ecdlp.Primality.pr_205115282021455665897114700593932402728804164701536103180137503955397371`.
This module reuses those facts, adds nothing computational beyond one closed
arithmetic identity, and derives the statement a mechanism screen actually
consumes:

> every `13441`-smooth divisor of `p - 1` divides `564522`.

`564522 = 2 · 3 · 7 · 13441 ≈ 2 ^ 19.11`.

## What this is for

Published factor-base constructions that require `p - 1` to carry a large smooth
divisor are screened against this ceiling. The ceiling is a property of the
target, decidable in advance, and independent of any attack being run — so it
retires such a construction at zero experimental cost rather than after a sweep.

## What this is NOT

This is an arithmetic fact about `p - 1`. It is not a statement about ECDLP
difficulty, not a complexity bound, not a claim about any particular algorithm,
and not progress toward recovering a discrete logarithm. It says nothing about
the group order `n`, about extension fields, or about auxiliary curves.

The two `native_decide` uses are closed computations over literal constants and
contribute only `Lean.ofReduceBool`, already in the repository's allowed trust
base.
-/

namespace Ecdlp.Curve

open Nat

/-- The 237-bit prime cofactor of `p - 1`. -/
def pMinusOneCofactor : ℕ :=
  205115282021455665897114700593932402728804164701536103180137503955397371

/-- The `13441`-smooth part of `p - 1`, namely `2 * 3 * 7 * 13441`. -/
def pMinusOneSmoothPart : ℕ := 564522

theorem pMinusOneSmoothPart_eq : pMinusOneSmoothPart = 2 * 3 * 7 * 13441 := by
  norm_num [pMinusOneSmoothPart]

/-- The cofactor is prime, reusing the Pratt node already established for `p`. -/
theorem pMinusOneCofactor_prime : Nat.Prime pMinusOneCofactor :=
  Ecdlp.Primality.pr_205115282021455665897114700593932402728804164701536103180137503955397371

/-- `13441` is strictly below the cofactor. -/
theorem lt_pMinusOneCofactor : 13441 < pMinusOneCofactor := by
  norm_num [pMinusOneCofactor]

/-- **Complete factorization of `p - 1`.** -/
theorem secp256k1_p_sub_one_factorization :
    Secp256k1.p - 1 = pMinusOneSmoothPart * pMinusOneCofactor := by
  native_decide

/-- The smooth part is exactly `564522`. -/
theorem secp256k1_p_sub_one_smooth_part_value : pMinusOneSmoothPart = 564522 := rfl

/-- No prime at most `13441` divides the cofactor: the cofactor is prime and larger. -/
theorem pMinusOneCofactor_no_small_prime_factor
    {q : ℕ} (hq : Nat.Prime q) (hle : q ≤ 13441) : ¬ q ∣ pMinusOneCofactor := by
  intro hdvd
  have := (Nat.prime_dvd_prime_iff_eq hq pMinusOneCofactor_prime).mp hdvd
  subst this
  exact absurd (lt_of_lt_of_le lt_pMinusOneCofactor hle) (lt_irrefl _)

/-- **The screen fact.** Every `13441`-smooth divisor of `p - 1` divides `564522`.

`d` ranges over divisors of `p - 1` all of whose prime factors are at most
`13441`. Since the remaining cofactor is prime and strictly larger, `d` is
coprime to it, hence divides the smooth part. -/
theorem secp256k1_smooth_divisor_dvd_smooth_part
    {d : ℕ} (hdvd : d ∣ Secp256k1.p - 1)
    (hsmooth : ∀ q : ℕ, Nat.Prime q → q ∣ d → q ≤ 13441) :
    d ∣ pMinusOneSmoothPart := by
  have hcop : Nat.Coprime d pMinusOneCofactor := by
    by_contra hne
    obtain ⟨q, hq, hqd⟩ := Nat.exists_prime_and_dvd hne
    exact pMinusOneCofactor_no_small_prime_factor hq
      (hsmooth q hq (hqd.trans (Nat.gcd_dvd_left _ _)))
      (hqd.trans (Nat.gcd_dvd_right _ _))
  rw [secp256k1_p_sub_one_factorization] at hdvd
  exact (Nat.Coprime.dvd_of_dvd_mul_right hcop) hdvd

/-- **The ceiling in numeric form.** A nonzero `13441`-smooth divisor of `p - 1`
is at most `564522`. -/
theorem secp256k1_smooth_divisor_le
    {d : ℕ} (hdvd : d ∣ Secp256k1.p - 1)
    (hsmooth : ∀ q : ℕ, Nat.Prime q → q ∣ d → q ≤ 13441) :
    d ≤ 564522 :=
  Nat.le_of_dvd (by norm_num)
    (secp256k1_smooth_divisor_dvd_smooth_part hdvd hsmooth)

end Ecdlp.Curve
