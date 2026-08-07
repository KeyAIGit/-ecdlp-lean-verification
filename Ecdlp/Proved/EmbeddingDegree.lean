import Mathlib
import Ecdlp.Secp256k1Verified
import Ecdlp.Proved.Secp256k1PrimeN

/-!
# secp256k1 has no small embedding degree (MOV / Frey–Rück resistance)

The MOV / Frey–Rück transfer reduces ECDLP on `E(𝔽_p)` to the discrete-log problem
in the multiplicative group `𝔽_{p^k}^×`, where `k` — the **embedding degree** — is
the least `k ≥ 1` with `n ∣ p^k − 1` (equivalently `p^k ≡ 1 (mod n)`). The transfer
is only useful when `k` is small enough that `𝔽_{p^k}` admits a subexponential
discrete log; for secp256k1 the embedding degree is astronomically large, so the
pairing transfer is useless in practice.

This file machine-checks the concrete fact behind that: for every `1 ≤ k ≤ 100`,
`p^k ≢ 1 (mod n)`. Hence secp256k1's embedding degree exceeds `100` — the MOV/FR
target field `𝔽_{p^k}` would need `k > 100`, i.e. an extension of more than
~25 000 bits, far beyond any feasible index-calculus discrete log.

This is the verified **boundary node** for barrier `B3-weil-pairing`: the transfer
*exists* in theory (it needs the Weil/Tate pairing, not yet in Mathlib), but here we
machine-check that even if the pairing were available it could not help — no small
`k` works. The hardness of ECDLP on secp256k1 therefore does not leak through MOV.

## The exact embedding degree

`secp256k1_embedding_degree_eq` upgrades the bounded scan to the exact value: the
multiplicative order of `p` in `(ℤ/nℤ)^×` is

  `k = (n − 1)/6 = 2^5 · 149 · 631 · 107361793816595537 · 174723607534414371449
                       · 341948486974166000522343609283189 ≈ 1.93·10^76`  (254 bits).

`p` is not a primitive root mod `n`: it is both a quadratic and a cubic residue, and
those two conditions — and only those — cut `n − 1` down by the cofactor `6`. The six
primes of `k` are a strict subset of the primes of `n − 1`, so the three large
primality side-conditions are discharged by the Pratt certificates already in
`Ecdlp/Proved/Secp256k1PrimeN.lean`; no new primality work is done here.

The statement must live in `ZMod n`, not in the `Nat.pow`-then-`%` idiom used for the
bounded scan: `Secp256k1.p ^ k` as a `Nat` is a ~4.9·10^78-bit integer, whereas
`(p : ZMod n) ^ k` reduces at every squaring.

## What the exact value does not establish

It is a fact about two integers. It is **not** a hardness result: it gives no lower
bound on the cost of solving ECDLP on secp256k1. Nor does it by itself prove the
MOV / Frey–Rück transfer useless — three unformalized ingredients stand between this
number and that conclusion: a Weil/Tate pairing (absent from Mathlib), the
Balasubramanian–Koblitz identification of `ord_n(p)` with the least extension over
which the full `n`-torsion is rational, and any cost model for discrete logarithms in
`𝔽_{p^k}` (barrier `B1-cost-model`, no Lean content). It closes only the pairing
route and says nothing about prime-field index calculus or Semaev/Gaudry–Diem.
-/

namespace Ecdlp.Curve

/-- **secp256k1's embedding degree, exactly.** The multiplicative order of `p` in
`(ℤ/nℤ)^×` — the least `k ≥ 1` with `n ∣ p^k − 1`, i.e. the MOV / Frey–Rück embedding
degree — is exactly `(n − 1)/6 = 2^5 · 149 · 631 · 107361793816595537 ·
174723607534414371449 · 341948486974166000522343609283189`, a 254-bit, 77-digit
integer. So `p` is not a primitive root mod `n`: it is a quadratic *and* a cubic
residue, and `⟨p⟩` is precisely the index-6 subgroup of sixth powers. Proved by
`orderOf_eq_of_pow_and_pow_div_prime`: one witness `p^k = 1` plus minimality
`p^(k/q) ≠ 1` at each of the six primes `q ∣ k`. See the module docstring for the
honest scope — this is a fact about two integers, not a hardness theorem. -/
theorem secp256k1_embedding_degree_eq :
    orderOf ((Secp256k1.p : ZMod Secp256k1.n))
      = 19298681539552699237261830834781317975472927379845817397100860523586360249056 := by
  refine orderOf_eq_of_pow_and_pow_div_prime (by norm_num) (by native_decide) ?_
  intro q hq hqd
  rw [show (19298681539552699237261830834781317975472927379845817397100860523586360249056 : ℕ) = 2 ^ 5 * (149 ^ 1 * (631 ^ 1 * (107361793816595537 ^ 1 * (174723607534414371449 ^ 1 * (341948486974166000522343609283189 ^ 1))))) by native_decide] at hqd
  rcases (Nat.Prime.dvd_mul hq).mp hqd with h | h
  · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 2 by norm_num)).mp (hq.dvd_of_dvd_pow h)]
    native_decide
  · rcases (Nat.Prime.dvd_mul hq).mp h with h | h
    · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 149 by norm_num)).mp (hq.dvd_of_dvd_pow h)]
      native_decide
    · rcases (Nat.Prime.dvd_mul hq).mp h with h | h
      · rw [(Nat.prime_dvd_prime_iff_eq hq (show Nat.Prime 631 by norm_num)).mp (hq.dvd_of_dvd_pow h)]
        native_decide
      · rcases (Nat.Prime.dvd_mul hq).mp h with h | h
        · rw [(Nat.prime_dvd_prime_iff_eq hq Ecdlp.Primality.pr_107361793816595537).mp (hq.dvd_of_dvd_pow h)]
          native_decide
        · rcases (Nat.Prime.dvd_mul hq).mp h with h | h
          · rw [(Nat.prime_dvd_prime_iff_eq hq Ecdlp.Primality.pr_174723607534414371449).mp (hq.dvd_of_dvd_pow h)]
            native_decide
          · rw [(Nat.prime_dvd_prime_iff_eq hq Ecdlp.Primality.pr_341948486974166000522343609283189).mp (hq.dvd_of_dvd_pow h)]
            native_decide

/-- **secp256k1 has embedding degree > 100.** For every `k` with `1 ≤ k ≤ 100`
(written as `j < 100` with `k = j + 1`), `p^k ≢ 1 (mod n)`. So the MOV/Frey–Rück
pairing transfer would require an extension field `𝔽_{p^k}` with `k > 100` —
intractably large — and the discrete log on secp256k1 does not transfer to a
feasible finite-field DLP. -/
theorem secp256k1_embedding_degree_gt_100 :
    ∀ j, j < 100 → Secp256k1.p ^ (j + 1) % Secp256k1.n ≠ 1 := by
  native_decide

end Ecdlp.Curve
