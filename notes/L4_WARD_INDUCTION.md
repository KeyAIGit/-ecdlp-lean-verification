# L4 — proving `normEDS_rec_one` (Ward's theorem): scoping + machinery

The flagship deep contribution: close the open Mathlib TODO
(`EllipticDivisibilitySequence.lean`: "prove that `normEDS` satisfies `IsEllDivSequence`"). With
`isEllSequence_of_rec_one` **already proved** (merged, `Ecdlp/Proved/EllSequenceRecOne.lean`), the
*entire* remaining content of `IsEllSequence (normEDS b c d)` is the single `r = 1` master recurrence:

```
normEDS_rec_one :  ∀ m n : ℤ,
  W (m+n) * W (m-n) = W (m+1) * W (m-1) * W n ^ 2 - W (n+1) * W (n-1) * W m ^ 2      (★₁)
  where W = normEDS b c d
```
Then `IsEllSequence (normEDS b c d) := isEllSequence_of_rec_one normEDS_rec_one`, and
`IsEllDivSequence` follows once `IsDivSequence` (a separate, smaller induction) is added.

This is Ward's theorem (1948) — the known-hard core, ~400–800 lines of the parity-case induction.

## Mathlib machinery available (v4.31, all PROVEN — verified on the server)

Base values: `normEDS_zero = 0`, `_one = 1`, `_two = b`, `_three = c`, `_four = d * b`;
`normEDS_neg n : normEDS b c d (-n) = -normEDS b c d n`.

Doubling recurrences:
- `normEDS_even m : normEDS b c d (2*m) * b = normEDS(m-1)^2 * normEDS m * normEDS(m+2)
                                            - normEDS(m-2) * normEDS m * normEDS(m+1)^2`
- `normEDS_odd  m : normEDS b c d (2*m+1) = normEDS(m+2) * normEDS m ^3
                                          - normEDS(m-1) * normEDS(m+1)^3`
- `complEDS₂_mul_b k : complEDS₂ b c d k * b = normEDS(k-1)^2 * normEDS(k+2) - normEDS(k-2) * normEDS(k+1)^2`
- `normEDS_mul_complEDS₂ k : normEDS k * complEDS₂ k = normEDS (2*k)`

Induction engine:
- `normEDSRec' {P : ℕ → Sort u}` — strong recursion: bases `P 0..P 4`, an even step
  `∀ m, (∀ k < 2*(m+3), P k) → P (2*(m+3))`, an odd step `∀ m, (∀ k < 2*(m+2)+1, P k) → P (2*(m+2)+1)`.
- `normEDSRec` — the `ℤ` analogue (via `Int.negInduction` + the ℕ version), the one to use for `(★₁)`.

## Proof plan (Ward, adapted to the Mathlib API)

1. **Universal base ring.** Prove `(★₁)` for `b, c, d` the three generators of `R₀ := MvPolynomial (Fin 3) ℤ`
   (an integral domain), then transport to arbitrary `CommRing R` by the evaluation hom `+ map_normEDS`.
   ("prove generically, specialise" — cheap, removes any `R`-specific reasoning.)
2. **Invert `b` only.** Work in `Frac R₀` (or `R₀[b⁻¹]`) so the `* b` on the LHS of `normEDS_even` can be
   cleared. `b = normEDS … 2` is a nonzero element of a domain, so this is unconditional; the divisions
   never touch a general `normEDS n`, and `(★₁)` is denominator-free as a statement, so it descends to `R₀`.
3. **Reduce the index range.** By `normEDS_neg` (oddness) and the `m ↔ n` antisymmetry of `(★₁)`, reduce to
   `m ≥ n ≥ 0`; dispatch `n = 0` (`normEDS 0 = 0`), `n = 1` (both sides equal by `normEDS_one`), `m = n`.
4. **Double induction.** Strong-induct on `m + n` via `normEDSRec`, splitting on parities of `m, n`. In each
   parity branch rewrite the top-index factors through `normEDS_even`/`normEDS_odd` (halving the indices),
   then close the resulting polynomial goal by `linear_combination`/`ring` against *lower* instances of `(★₁)`.

**Where the cost concentrates (honest):**
1. **Certificate discovery** — for each parity case the reduced goal is a large polynomial in ~10–15
   `normEDS`-values equal to an explicit combination of smaller `(★₁)` instances + the two recurrences.
   The identity is true; finding the exact `linear_combination` witnesses is the multi-page part.
2. **IH strengthening** — `(★₁)` alone is often not self-reducing; expect to carry a companion identity
   simultaneously. The prime candidate is the **Somos-4 slice** (below).
3. **`ℤ` well-founded / parity bookkeeping** — steady boilerplate via `normEDSRec` + `Int.even`/`odd` lemmas.

## First milestone — the Somos-4 slice `(★₁)(·, 2)`
```
normEDS(m+2) * normEDS(m-2) = b^2 * normEDS(m+1) * normEDS(m-1) - c * normEDS(m)^2
```
(the `n = 2` case, using `normEDS 1 = 1`, `normEDS 2 = b`, `normEDS 3 = c`). A *single-variable*
induction on `m` via `normEDSRec` — the scoped warm-up that tests the induction machinery and is the
likely companion identity for the full `(★₁)`. **Prove this first**, then generalise.

## Status
- `isEllSequence_of_rec_one` (the `r`-general ← `r = 1` reduction): **DONE**, merged.
- `normEDS_rec_one` (`(★₁)`): **scoped, not yet proved** — the weeks-scale Ward induction; the machinery
  above is confirmed present. Next concrete step: the Somos-4 slice.
- On completion: `IsEllSequence (normEDS)` (the TODO's elliptic half) is a one-liner; then optionally
  `IsDivSequence` (~150–300 further lines) for the full `IsEllDivSequence`.

*Provenance: machinery read off the pinned Mathlib v4.31 on the server; plan is Ward's classical argument
adapted to that API. Nothing here is kernel-verified beyond the already-merged reduction lemma.*
