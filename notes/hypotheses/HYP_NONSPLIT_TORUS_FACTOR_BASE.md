# HYP-TORUS-001 — The nonsplit-torus factor base

**Status:** proposed hypothesis. Non-executable. No experiment authorized, no route promoted.
**Threat model:** classical, single target, plain. No oracle, no precomputation amortized across
targets, no chosen inputs, no quantum.
**Baseline:** Pollard rho on secp256k1 = `2^127.8257`; with `|Aut| = 6`, `2^126.5333`.
**Date:** 2026-07-29. Branch cut from `main` @ `731b11d`.

---

## 0. Provenance and honesty ledger — read first

This was produced by one model in one session: an orchestrator plus thirteen subagents (five
generation lenses, five adversarial killers, three judges). **It is not source-independent
review.** Twenty-eight candidates were generated; twenty-six had their own pre-registered kill
condition fire during the session.

**One of the three judges returned `NONE`** — it argued the correct output was zero hypotheses and
that the pool was "a closed post-mortem ledger, not a hypothesis list". That verdict is recorded
because it is partly right: it is overridden here only because it judged the *candidate pool* and
never saw the repaired candidate below, which is a gap in the orchestration, not a refutation.

**Three claims were corrected mid-flight, all of them the orchestrator's own:**

1. An exact Eisenstein decomposition of Frobenius was computed and presented as new. **It is not
   new** — `Ecdlp/Proved/FrobeniusCM.lean` already proves `secp256k1_frobenius_norm`,
   `secp256k1_frobenius_trace` and `secp256k1_four_p_eq_trace_sq` with the same integers. The
   computation stands only as a consistency check.
2. The first pass maximized the factor-base size `D` inside a viability window. **That is the
   wrong criterion** — `D = deg L`, and a larger `L` makes every Gröbner solve harder. The
   criterion is to *minimize* `D` subject to the relation-yield balance. This changed the headline
   from "m = 6 vs m = 16" to what is stated below.
3. The first pass ignored that the torus trace is **2-to-1**, so `deg L = |H|/2`, not `|H|`. This
   removed `m ∈ {11,12,13}` from the viable window entirely and reduced the `m = 6` margin to
   `+0.12` bits.

No novelty is claimed. Absence of this construction from the literature and from this repository
is **not** treated as evidence that it is new — it has not been searched for exhaustively.

---

## 1. The classification that makes the sector complete

Petit–Kosters–Messeng (PKC 2016) instance (i) builds its factor base from a subgroup of
`F_p^* = G_m(F_p)`, of order `p - 1`. The natural question nobody in this project asked is:
**which other algebraic groups over `F_p` could supply a factor base?**

The answer is a classification, and it is short. The connected one-dimensional algebraic groups
over `F_p` are exactly:

| group | order | status |
|---|---|---|
| `G_a` (additive) | `p` | **empty cell** — `F_p` as an additive group is a 1-dimensional `F_p`-vector space, so it has *no proper subgroups at all*. Nothing to build a factor base from. |
| `G_m` (split torus) | `p - 1` | **This is PKC instance (i).** Closed on secp256k1 — see §3. |
| `T_2` (nonsplit torus) | `p + 1` | **Never examined.** This hypothesis. |

There is no fourth. So the sector is finite and this hypothesis exhausts it.

`T_2(F_p) = {α ∈ F_{p²} : α^(p+1) = 1}`, cyclic of order `p + 1`.

---

## 2. The technical bridge, verified

`T_2` does not live inside `F_p`, so "`x(P)` lies in a subgroup of `T_2`" does not immediately
type-check. The bridge is the trace `Tr(α) = α + α^p ∈ F_p`, which is **2-to-1**.

For `H ≤ T_2` of order `d`, the set `Tr(H) ⊆ F_p` has size `≈ d/2` and is the root set of a
polynomial over `F_p` of that degree. So

    F = { P ∈ E(F_p) : x(P) ∈ Tr(H) }

is a well-defined algebraic factor base, cut out by `L(x) = 0` exactly as in PKC, with
**`deg L ≈ |H| / 2`**.

Verified by exhaustive enumeration this session at `p = 23, 31, 47, 59, 71, 83`: in every case
`|Tr(H)|` equalled the predicted `⌊d/2⌋ + 1` and the interpolated polynomial had exactly that
degree.

---

## 3. The decisive computation — already executed

```
p - 1 = 2 · 3 · 7 · 13441 · P₂₃₇
p + 1 = 2⁴ · 7322137 · 45422601869677 · P₁₈₃
        P₁₈₃ = 21759506893163426790183529804034058295931507131047955271
```

Divisors avoiding the huge prime: `p - 1` has 16, maximum `2^19.1067`; `p + 1` has 20, maximum
`2^72.1723`.

Viability of an arity `m` requires two things simultaneously:

- **yield** — `deg L ≥ (m!·p)^(1/m)`, the PKC §3.2 balance point;
- **linear algebra** — `(deg L)² ≤ 2^126.5333`, i.e. `deg L ≤ 2^63.2666`.

Applying both, with the 2-to-1 trace loss:

| `m` | `\|H\|` | `deg L = \|H\|/2` | threshold `(m!p)^(1/m)` | margin | verdict |
|---|---|---|---|---|---|
| 4 | 2^68.172 | 2^67.172 | 2^65.146 | +2.03 | fails linear algebra (`2^134.3` > rho) |
| **6** | **2^45.368** | **2^44.368** | **2^44.2486** | **+0.1198** | **passes, on a knife edge** |
| **7** | **2^45.368** | **2^44.368** | **2^38.3285** | **+6.0400** | **passes comfortably** |
| 11 | 2^24.804 | 2^23.804 | 2^25.5682 | −1.7644 | fails yield |
| 12 | 2^23.804 | 2^22.804 | 2^23.7363 | −0.9325 | fails yield |
| 13 | 2^22.804 | 2^21.804 | 2^22.1951 | −0.3912 | fails yield |

**For `p - 1` the window is empty at every `m`** — which independently reproduces the closure of
PKC instance (i) reached in the OPUS-001 audit (PR #255) by a different argument.

**For `p + 1` the window is non-empty at `m ∈ {6, 7}`**, with `|H| = 45422601869677` and
`deg L = 2^44.368`. Linear algebra there costs `2^88.74`, comfortably under the baseline.

---

## 4. The hypothesis

> **HYP-TORUS-001.** The nonsplit torus `T_2(F_p)` of order `p + 1` supplies an algebraic factor
> base for the PKC 2016 prime-field decomposition method at arities `m ∈ {6, 7}` on secp256k1,
> where the split torus `F_p^*` supplies none at any arity. The required summation polynomial is
> therefore `S_7` or `S_8` with per-variable degree `2^5 = 32` or `2^6 = 64`, rather than the
> `S_17` with per-variable degree `2^15` that the `p - 1` construction would demand.

**What makes this the interesting arity.** `S_7` and `S_8` sit exactly at the frontier of the
computed literature: Faugère–Huot–Joux–Renault–Vitse (2014) computed the 8th **symmetrized**
summation polynomial, and their Table 1 records that the **classical** `S_7` and `S_8` were *not*
computed. So this construction lands the size leg precisely where the polynomial leg becomes a
real question rather than an impossible one.

### Curve/field-specific fact consumed

The prime factorization of `p + 1` for `p = 2^256 − 2^32 − 977`, specifically the 45-bit prime
factor `45422601869677`. This is a fact about *this* field, and the factor base reads the
*x-coordinate representation* — which matters, because an earlier measurement in this project
established that any attack drawing only on the abstract group structure cannot be curve-specific
(the near-orthogonality constant computed on the real curve group is identical to the one computed
in `Z_n` with no curve, in 9 pairs from 11 to 19 bits).

### Nearest atlas mechanism, and the structural difference

Nearest is PKC 2016 instance (i), the `p − 1` smooth-subgroup factor base. The difference is not
wording: instance (i) draws its factor base from a *split* torus whose subgroup orders divide
`p − 1`, and secp256k1's `p − 1` is arithmetically hostile (largest usable divisor `2^19.11`, and
a hard gap with no divisor strictly between 43 and 13440). The nonsplit torus is a **different
algebraic group** with a different order, and the classification in §1 shows it is the only other
candidate in the sector.

---

## 5. What this does NOT claim

- **It is not an attack, and it does not lower the cost of ECDLP on secp256k1.** It clears one
  leg — the factor-base size leg — and says nothing about the total.
- **The Gröbner cost `T(E, m, L)` remains completely unbounded**, exactly as it is for PKC
  instance (ii). A naive Yokoyama-shaped proxy `m · (deg L)^(m−1)` evaluates to `2^229.4` at
  `m = 6`, far above the baseline — but Yokoyama's Prop. 9 is scoped to a **random** `V` and does
  not bound a structured one, so that proxy is indicative, not decisive. Whether it transfers is
  precisely the open question.
- It does not claim `S_7` or `S_8` is computable, only that it is nearer the frontier than `S_17`.
- It does not claim the recovery semantics, exceptional loci, saturation, denominators or
  distinct-`x` conditions have been checked. They have not.
- The `m = 6` margin of `+0.1198` bits is **within the noise of how the yield condition is
  stated**. If the correct constant carries any factor above `2^0.12`, `m = 6` drops out and only
  `m = 7` survives. Nothing should rest on `m = 6` alone.
- No novelty is claimed. This construction may exist in the literature under another name; it was
  not exhaustively searched for.

---

## 6. Pre-registered next decisive quantity

The size leg is decided. The next leg has a decisive quantity that is measurable **at toy scale
only**, with no secp256k1 computation of any kind:

> **Q:** For the torus-trace system — `S_{m+1}(x_1..x_m, x_R) = 0` together with `L(x_i) = 0`
> where `L` cuts out `Tr(H)` for `H` a subgroup of the nonsplit torus — is the first-fall degree
> (equivalently the observed solving degree) **lower** than for a random `V` of the same size, at
> matched small parameters?

- **SUPPORT:** the structured `V` shows a solving degree strictly below the random-`V` control at
  three or more consecutive toy sizes, with the gap growing in `m`.
- **KILL:** the solving degree matches the random-`V` control within noise. Then Yokoyama's naive
  bound is the right shape after all, the `2^229.4` proxy stands, and HYP-TORUS-001 closes as
  `bounded_negative` — the size leg cleared, the cost leg fatal.

Both branches are reachable. The measurement is on primes of 10–20 bits with a matched random-`V`
control and a planted-structure positive control, and it requires no Gröbner engine beyond what
the measurement itself defines.

**This measurement is not authorized by this document.** It is stated so that whoever picks it up
inherits a pre-registered prediction rather than writing one after seeing the data.

---

## 7. Reproduction

Every number above was computed from `p` and `n` alone with plain Python and `sympy`, in this
session. No Sage, msolve, F4/F5 or Gröbner computation was run. No secp256k1 discrete-log
computation of any kind was performed, and `secp256k1` remains a forbidden target.
