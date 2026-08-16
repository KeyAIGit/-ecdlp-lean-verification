# UORC-056 C42 contract: oriented transposed resultant

Date: 2026-08-16

Status: active research contract. No parity evaluator is claimed.

## 1. Input inherited from C39 to C41

The compact public state is

\[
F_G(Q)=M_{(n-1)/2}(G,Q,S).
\]

C39 gives the exact decoder

\[
(-1)^k=
\frac{\Delta(F_G(Q))}{\Sigma(F_G(Q))},
\]

where

\[
\Sigma=P_{\rm odd}+P_{\rm even},
\qquad
\Delta=P_{\rm odd}-P_{\rm even}.
\]

The explicit factors have degree `(n-1)/2`. C40 excludes ordinary full-kernel isogeny norms and subgroup-norm towers. C41 excludes, on the frozen corpus, ordinary polynomial composition, short linear coefficient recurrence, and low-degree single-state transitions.

## 2. Exact C42 target

Construct an evaluator

```text
State = TransposedOrientedNorm(E,G,Q,S),
Output = Decode(E,G,Q,S,State),
```

such that

\[
Output=(-1)^k,
\qquad Q=[k]G,
\]

without materializing any of

```text
P_even,
P_odd,
Sigma,
Delta,
K_H,
Y_G on all half-kernel roots,
an O(sqrt(n))-width block table.
```

The full charged cost must satisfy

\[
C_{preprocessing}+C_{advice}+C_{memory}+C_{representation}+C_{online}
=O(n^{1/2-\varepsilon})
\]

for one fixed `epsilon>0`.

## 3. First candidate representations

C42 may use one of the following only if it gives a literal on-demand value algorithm:

1. a transposed resultant that computes `Delta(F_G(Q))` without constructing the resultant polynomial;
2. a structured determinant with displacement rank `o(sqrt(n))`;
3. a target-dependent modular-composition circuit whose relation matrices are generated in sub-root cost;
4. an elliptic-net incomplete norm with a proved marked-half recurrence;
5. a transfer matrix carrying the ordered square-root branch from the public anchor.

A generic degree-`m` resultant or modular-composition call is not a positive result. Its input representation already has size `Theta(m)` unless a special compiler is supplied.

## 4. Mandatory tests

Every candidate must expose:

```text
where the generator marking enters,
why G -> -G negates the oriented output,
why no unknown scalar digit controls the circuit,
why no dense degree-m object is hidden in advice,
all-point correctness on frozen curves,
held-out curve validation,
a complete cost ledger.
```

## 5. Negative gate

A negative C42 package must name an exact grammar, for example:

```text
bounded-displacement determinant,
bounded relation-matrix modular composition,
fixed-depth elliptic-net resultant,
fixed-width transfer matrix,
canonical square-root selector family.
```

It must prove a rank, width, representation, collision, or reduction boundary for that grammar. No unrestricted resultant, circuit, or ECDLP lower bound may be claimed.

## 6. First attack order

```text
1. derive the direct evaluation functional for Delta at z=F_G(Q);
2. search for low-displacement multiplication matrices in the half-kernel algebra;
3. test whether GLV block decomposition reduces the oriented determinant dimension;
4. test canonical square-root selectors with held-out curves;
5. compare any surviving compiler against the exact 129-bit interpolation frontier from C41.
```
