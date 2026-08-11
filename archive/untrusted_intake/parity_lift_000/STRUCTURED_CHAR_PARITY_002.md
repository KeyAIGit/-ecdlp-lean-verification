# STRUCTURED-CHAR-PARITY-002: high-degree / low-evaluation-cost observables

Date: 2026-08-11

Status: **untrusted research note**. This note records a next-stage analysis stacked conceptually on `CHAR-PARITY-001`. It is not canonical evidence, does not authorize production-sized computation, and claims no ECDLP improvement.

## Central question

Can an exact generator-relative parity decoder

```text
D(Q) = (-1)^k,   Q=[k]G, 0<=k<n,
```

be realized by a structured observable whose algebraic degree / geometric conductor is square-root scale or larger, while its online evaluation cost remains sub-square-root (possibly polylogarithmic)?

## 1. Degree alone cannot lower-bound evaluation cost

The answer to the abstract degree-vs-cost question is **yes**: structured high-degree functions can be evaluated cheaply.

Examples:

- repeated squaring evaluates `x^(2^t)` with `t` squarings although the degree is `2^t`;
- the multiplication-by-`m` map `[m]` on an elliptic curve has degree `m^2` but is evaluated by an addition chain in `O(log m)` group operations;
- division-polynomial / EDS recurrences evaluate indexed terms without expanding their degree-Theta(m^2) polynomial representation.

Therefore the degree/conductor lower bound from `CHAR-PARITY-001` cannot by itself imply an online-time lower bound.

For a secp256k1-scale field, an index `m` near `q^(1/4)` already gives formal degree near `sqrt(q)` while `log2(m)` is only about 64. This is the principal structured loophole.

## 2. A composition loophole that does *not* help

A superficially dangerous family is

```text
f(Q) = g([m]Q),
```

with `g` low-degree and `m` invertible modulo the prime subgroup order `n`. Although the rational-map degree of `f` is multiplied by about `m^2`, the map `[m]` merely permutes the cyclic subgroup.

If

```text
chi(g([m][k]G)) = (-1)^k
```

for all canonical `k`, set `t = m*k mod n`. Then the trace sequence of `g` on `[t]G` is just parity composed with a permutation of the cyclic index. Its discrete Fourier coefficients are correspondingly permuted, so the large Fourier demand used by `CHAR-PARITY-001` remains. The character-sum bound can be applied to the low-degree core `g`, rather than to the expanded degree of `g o [m]`.

**Disposition:** precomposition by scalar multiplication does not by itself evade the low-conductor obstruction.

## 3. Division-polynomial family

The genuinely interesting family is a fixed-index division-polynomial character

```text
Q |-> chi(psi_m(Q)),
```

or products/ratios of a bounded number of such terms. Here degree grows as Theta(m^2), while EDS/division-polynomial recurrences can evaluate the value using an addition-chain style computation.

### Immediate sign obstruction

For odd `m`, `psi_m` is x-only on a short Weierstrass model, hence

```text
psi_m(-Q) = psi_m(Q).
```

Canonical parity on an odd prime-order cycle is anti-invariant under `Q -> -Q` away from the identity. Thus an odd-index single `chi(psi_m(Q))` cannot be an exact parity decoder.

For even `m`, `psi_m` carries one `y` factor, so

```text
psi_m(-Q) = -psi_m(Q).
```

On secp256k1, `p = 3 mod 4`, hence the quadratic character satisfies `chi(-1)=-1`. Therefore the even-index family has the *correct* negation covariance and is not eliminated by the sign test.

**Principal surviving elementary candidate:** even-index division-polynomial / EDS characters, and structured products or ratios with overall sign-sensitive parity.

## 4. Why a fast exact member would be a major result

An exact parity oracle can be recursively bit-peeled to recover the full canonical scalar in `O(log n)` oracle calls (formalized in `Ecdlp/Proved/ScalarParity.lean`). Therefore if one member of the structured family were evaluable in time `T(n)=o(sqrt(n)/log n)`, it would imply a sub-square-root DLP algorithm through that reduction.

This is why a completely general proof that *all* structured low-circuit observables fail is likely to require a lower-bound model substantially stronger than the current conductor argument. Generic-group lower bounds do not automatically apply to coordinate-sensitive rational/EDS/theta computations.

## 5. Bounded local screen (non-canonical)

A local recurrence-based toy screen was performed on the frozen prime-order curves

```text
y^2 = x^3 + 7 over F_43, F_67, F_79, F_127, F_163
```

using one generator on each prime-order group.

Screened family:

```text
chi(psi_m([k]G)),  1 <= m < n, 1 <= k < n,
```

with either global sign, plus XOR/product combinations of up to four distinct observed character sequences.

Observed result:

- no single `chi(psi_m)` matched exact canonical parity on any of the five curves;
- no product of up to four screened division-polynomial character sequences matched exact parity on any of the five curves;
- the recurrence implementation was cross-checked against the standard `x([m]P)` division-polynomial identity on the smaller frozen curves.

This is only bounded negative evidence. It does not rule out larger indices, structured ratios/products outside the screened set, theta recurrences, preprocessing, or another fast high-degree family.

## 6. Current answer

| question | current answer |
|---|---|
| Can high algebraic degree coexist with cheap evaluation? | **Yes, definitively.** |
| Does scalar-multiplication precomposition of a low-degree core evade `CHAR-PARITY-001`? | **No; subgroup reindexing preserves the Fourier obstruction.** |
| Can an odd-index single division-polynomial character give parity? | **No; it is sign-erasing.** |
| Can an even-index division-polynomial character give parity on secp256k1? | **Not ruled out structurally; bounded toy evidence is negative.** |
| Is there a known polylog/sub-sqrt exact structured parity observable? | **No evidence in this analysis.** |
| Can we currently prove no such structured observable exists in full generality? | **No.** A general time lower bound would go well beyond the conductor theorem and would be close in spirit to proving a strong non-generic ECDLP lower bound. |

## 7. Highest-value next theorem

The next target should not be another degree bound. It should exploit the *recurrence/straight-line structure* directly.

A useful restricted theorem target is:

```text
DIVPOLY-PARITY-003
```

> For the secp256k1 prime-order subgroup, classify or exclude exact parity for
> `chi(psi_m(Q))` (especially even `m`) and then for bounded products/ratios of
> division-polynomial terms, using their translation, torsion-divisor, and
> recurrence symmetries rather than expanded degree.

A second target is a circuit-model statement:

```text
RECURRENCE-PARITY-004
```

> Define a restricted arithmetic/EDS/theta straight-line model and prove that
> exact canonical parity requires square-root-scale resources *inside that
> model*, or produce an explicit counterexample.

The restricted-model formulation is essential: an unconditional lower bound for arbitrary coordinate-sensitive polynomial-size circuits would be far stronger than what `CHAR-PARITY-001` establishes.
