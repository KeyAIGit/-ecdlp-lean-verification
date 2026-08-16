# UORC-056 C39: parity orbit factorization of the half-index Miller state

Date: 2026-08-16

Status: exact structural reduction plus scoped decoder closures. No parity oracle or sub-square-root ECDLP algorithm is claimed.

## 1. Target and surviving state

Let

\[
Q=[k]G,\qquad h=\frac{n-1}{2},
\]

and fix a public regular trace-zero shift `S` over `F_(p^2)`. The surviving compact state is

\[
F_G(Q)=M_h(G,Q,S)=\frac{f_{h,G}(S+Q)}{f_{h,G}(S)}.
\]

It is public and has a binary Miller-chain evaluator of cost `O(log n)`. C39 investigates whether parity

\[
\sigma_G(Q)=(-1)^k
\]

has a short decoder from this state.

## 2. Exact orbit polynomials

Put

\[
m=\frac{n-1}{2}.
\]

Define

\[
P_{\rm even}(Z)=\prod_{1\le k<n,\ k\ {m even}}(Z-F_G([k]G)),
\]

\[
P_{\rm odd}(Z)=\prod_{1\le k<n,\ k\ {m odd}}(Z-F_G([k]G)).
\]

Both are monic of degree `m`. If their root sets are disjoint, then

\[
\boxed{
D_{\rm orb}(Z)=
\frac{P_{\rm odd}(Z)-P_{\rm even}(Z)}
     {P_{\rm odd}(Z)+P_{\rm even}(Z)}
}
\]

is regular at every sampled state and satisfies

\[
\boxed{D_{\rm orb}(F_G([k]G))=(-1)^k.}
\]

This gives an exact decoder, but not a cheap one: its explicit factors have degree `m`.

## 3. Optimality among explicit rational decoders

Let `E` and `O` be disjoint sets of state values with `r_E` and `r_O` distinct elements. Suppose

\[
D(Z)=\frac{A(Z)}{B(Z)}
\]

is regular on both sets and returns `+1` on `E` and `-1` on `O`. Then `A-B` vanishes on every even state and `A+B` vanishes on every odd state. Therefore

\[
\boxed{\max(\deg A,\deg B)\ge\max(r_E,r_O).}
\]

When both classes contain `m` distinct values, every rational parity decoder has degree at least `m`. The orbit decoder reaches this lower bound exactly.

At degree at most `m`, constants `c,d` satisfy

\[
A-B=cP_{\rm even},\qquad A+B=dP_{\rm odd},
\]

hence

\[
2A=cP_{\rm even}+dP_{\rm odd},\qquad
2B=dP_{\rm odd}-cP_{\rm even}.
\]

Thus every degree-minimal explicit rational decoder is a constant recombination of the same two orbit factors.

Frozen results:

| p | n | m | distinct states | optimal rational degree | direct polynomial degree |
|---:|---:|---:|---:|---:|---:|
| 43 | 31 | 15 | 29 | 15 | 28 |
| 67 | 79 | 39 | 78 | 39 | 77 |
| 79 | 67 | 33 | 66 | 33 | 65 |
| 127 | 127 | 63 | 126 | 63 | 125 |
| 163 | 139 | 69 | 138 | 69 | 137 |

## 4. Oriented norm normal form

Choose

\[
P_j=[j]G=(x_j,y_j),\qquad 1\le j\le m,
\]

and define

\[
K_H(X)=\prod_{j=1}^{m}(X-x_j).
\]

Let `Y_G` be the oriented square root in the half-kernel algebra:

\[
Y_G(x_j)=(-1)^j y_j,\qquad
Y_G^2=X^3+7\pmod {K_H}.
\]

Write the half-index state on the two points over each `x_j` as

\[
F_G(P)=A(x(P))+y(P)B(x(P)),
\]

where

\[
A(x_j)=\frac{F_G(P_j)+F_G(-P_j)}2,
\qquad
B(x_j)=\frac{F_G(P_j)-F_G(-P_j)}{2y_j}.
\]

The even point above `x_j` has `y=Y_G(x_j)` and the odd point has `y=-Y_G(x_j)`. Consequently

\[
\boxed{P_{\rm even}(Z)=\operatorname{Norm}_{K_H}(Z-A-Y_GB),}
\]

\[
\boxed{P_{\rm odd}(Z)=\operatorname{Norm}_{K_H}(Z-A+Y_GB).}
\]

Equivalently these are resultants against `K_H`. On all five frozen curves `B` is nonzero on every root of `K_H`, and all 438 parity evaluations pass.

## 5. A new oriented square-root branch

Define

\[
\Sigma=P_{\rm odd}+P_{\rm even},\qquad
\Delta=P_{\rm odd}-P_{\rm even},\qquad
\Pi=P_{\rm odd}P_{\rm even}.
\]

Then

\[
\boxed{\Delta^2=\Sigma^2-4\Pi,}
\]

and

\[
\boxed{(-1)^k=\frac{\Delta(F_G(Q))}{\Sigma(F_G(Q))}.}
\]

Under the covariant reversal `(G,S) -> (-G,-S)` at a fixed physical query, the even and odd factors swap. Therefore `Sigma` and `Pi` are fixed while `Delta` changes sign.

The exact orbit decoder therefore repackages the original orientation into the ordered polynomial square-root branch `Delta`. Materializing a degree-`m` polynomial costs `Theta(m)` field elements. For secp256k1,

\[
m=57896044618658097711785492504343953926418782139537452191302581570759080747168,
\]

which is a 255-bit degree. A non-materializing circuit for `Delta(F_G(Q))` remains open.

## 6. Density and paired-negation boundary

On the frozen corpus:

* `P_even` and `P_odd` have every coefficient nonzero except one zero coefficient in one `P_odd` instance;
* `Sigma`, `Delta`, `A`, `B`, and `Y_G` are dense;
* every support has step one;
* the rational map from the state at the even point above `x_j` to the state at the odd point first appears at the ordinary interpolation dimension threshold.

| p | m | first paired-negation rational degree |
|---:|---:|---:|
| 43 | 15 | 7 |
| 67 | 39 | 19 |
| 79 | 33 | 16 |
| 127 | 63 | 31 |
| 163 | 69 | 34 |

One degree below each threshold the evaluation matrix has full column rank. No unexpectedly low-degree Möbius or quadratic transition is present on the frozen corpus.

## 7. Arbitrary products of trace-linear power characters

For every

\[
e\in\mathbb Z/(p^2-1)\mathbb Z
\]

and every

\[
(A:B)\in\mathbf P^1(\mathbb F_p),
\]

define, when everywhere nonzero,

\[
X_{e,A:B}(Q)=
\chi_p\!\left(A\operatorname{Re}(F_G(Q)^e)+B\operatorname{Im}(F_G(Q)^e)\right).
\]

An arbitrary product of any number of these atoms is an `F_2`-linear combination of their normalized sign vectors. Exact span computation gives:

| p | n | declared atoms | valid atoms | span rank | parity in span |
|---:|---:|---:|---:|---:|:---:|
| 43 | 31 | 81,312 | 49,770 | 22 | no |
| 67 | 79 | 305,184 | 166,122 | 44 | no |
| 79 | 67 | 499,200 | 318,318 | 43 | no |
| 127 | 127 | 2,064,384 | 1,113,462 | 80 | no |
| 163 | 139 | 4,357,152 | 2,540,970 | 89 | no |

Totals:

```text
7,307,232 declared atoms
4,188,642 everywhere-nonzero atoms
0 parity spans
```

Thus no decoder formed as an arbitrary product of these trace-linear power-character atoms equals parity on any frozen screen. This is a scoped finite-corpus result, not an unrestricted circuit lower bound.

## 8. Decision

C39 establishes:

```text
exact parity orbit decoder                         found
optimal explicit rational degree                  proved
oriented norm/resultant normal form                found
orientation moved to polynomial square root Delta proved
explicit coefficient compression                  not found
non-materializing resultant/net decoder           not found
all trace-linear power-character products         closed on frozen corpus
parity oracle                                      not found
sub-square-root ECDLP                              not found
```

The next positive frontier is:

```text
ON-DEMAND-ORIENTED-NORM-EVALUATION-C40
```

It must evaluate `Delta(F_G(Q))` without producing `Theta(n)` coefficients. Candidate mechanisms include a recursive elliptic-net norm, a target-dependent transposed resultant, a polynomial-square-root continuation seeded by the public anchor, or a transfer matrix of dimension `o(sqrt(n))`. Any construction that materializes the full orbit factors or half-kernel algebra fails the cost gate by representation size.
