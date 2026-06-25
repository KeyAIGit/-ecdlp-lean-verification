# Primality certificates for secp256k1 p and n

Goal: prove `Nat.Prime Secp256k1.p` and `Nat.Prime Secp256k1.n` in Lean via
`Nat.lucas_primality`, to remove the `[Fact p.Prime] / [Fact n.Prime]` hypotheses
and make the conditional theorems unconditional.

`lucas_primality (p) (a : ZMod p) (ha : a^(p-1) = 1)
  (hd : ∀ q, q.Prime → q ∣ (p-1) → a^((p-1)/q) ≠ 1) : p.Prime`

Needs: a witness `a` (primitive root), the full factorization of `p-1`, and a
primality proof for EACH prime factor (recursive Pratt for the large ones; norm_num
for the small ones).

## Factorizations (computed with sympy; all factors verified prime, product checked)

p − 1 = 2 · 3 · 7 · 13441
        · 205115282021455665897114700593932402728804164701536103180137503955397371

n − 1 = 2^6 · 3 · 149 · 631
        · 107361793816595537
        · 174723607534414371449
        · 341948486974166000522343609283189

## Recursion needed (large factors → their own certificates)
- p-1: the 70-digit (~233-bit) factor needs its own lucas_primality cert.
- n-1: the 18-, 21-, and 33-digit factors each need their own cert.
(Recurse: factor (q-1) for each large prime q, repeat. sympy factorint handles it.)

## Status: planned. Best executed on the server (local Lean) — many native_decide
## modular exponentiations + recursion; slow under CI-only.
