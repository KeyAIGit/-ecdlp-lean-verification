# UORC-056 C41: incomplete oriented-product compression boundary

Date: 2026-08-16

Status: exact frozen-corpus boundary for three declared compression mechanisms. No parity oracle, unrestricted arithmetic-circuit lower bound, or sub-square-root ECDLP algorithm is claimed.

## 1. Problem inherited from C39 and C40

C39 found the exact degree-optimal explicit decoder for the half-index Miller state

\[
F_G(Q)=M_{(n-1)/2}(G,Q,S).
\]

It uses the two orbit factors

\[
P_{\rm even}(Z)=\prod_{k\ {m even}}(Z-F_G([k]G)),
\qquad
P_{\rm odd}(Z)=\prod_{k\ {m odd}}(Z-F_G([k]G)),
\]

and returns

\[
(-1)^k=
\frac{P_{\rm odd}(F_G(Q))-P_{\rm even}(F_G(Q))}
     {P_{\rm odd}(F_G(Q))+P_{\rm even}(F_G(Q))}.
\]

C40 then proved that a complete Frobenius or isogeny norm cannot select one marked parity half, because the subgroup has prime order and the two halves are neither subgroups nor subgroup cosets.

C41 asks whether the incomplete marked product can nevertheless be compressed by one of three standard mechanisms:

1. a nontrivial functional composition of the orbit polynomial;
2. a short linear recurrence in its coefficients;
3. a low-degree transition law for the compact state under public group operations.

The package complements the earlier endpoint/factorial boundary. B14 identifies endpoint-segment evaluation with the global cyclic factorial and places standard two-level block products at the square-root frontier. B15 proves density and full linearized Fourier support in the closest root-of-unity model. C41 performs the corresponding exact tests directly on the half-index Miller-state orbit factors.

## 2. Functional decomposition screen

The declared polynomial set is

\[
P_{\rm even},\quad P_{\rm odd},\quad
\Sigma=P_{\rm even}+P_{\rm odd},\quad
\Delta=P_{\rm odd}-P_{\rm even},\quad
\Pi=P_{\rm even}P_{\rm odd}.
\]

For every proper divisor `r` of the degree, the replay tests whether a monic polynomial `f` has a normalized decomposition

\[
f=g\circ h,
\qquad
\deg h=r,
\qquad
h\text{ monic},
\qquad
h(0)=0.
\]

This normalization is complete for polynomial decompositions when the characteristic does not divide the outer degree, which holds in every declared frozen case.

Across five curves and five polynomials per curve:

```text
25 polynomials tested
0 nontrivial decompositions
```

Thus the explicit orbit factors do not arise from a smaller polynomial through ordinary functional composition on the frozen corpus.

This does not exclude rational decomposition, multivariate composition, or a short circuit unrelated to functional decomposition.

## 3. Coefficient recurrence complexity

For every declared polynomial, Berlekamp-Massey is run on the coefficient list in both ascending and descending order.

For a finite sequence of length `L`, the generic maximum observable linear recurrence order is

\[
\left\lceil\frac L2\right\rceil.
\]

Every one of the fifty tested coefficient directions reaches exactly that maximum.

Examples:

| `n` | polynomial coefficient count | recurrence order |
|---:|---:|---:|
| 31 | 16 for each half factor | 8 |
| 79 | 40 for each half factor | 20 |
| 67 | 34 for each half factor | 17 |
| 127 | 64 for each half factor | 32 |
| 139 | 70 for each half factor | 35 |

The product factor `Pi`, whose coefficient count is `n`, likewise has recurrence order `(n+1)/2` on the finite window.

Therefore no short constant-coefficient linear recurrence is visible in either coefficient direction.

This is a finite-window linear-complexity statement, not a theorem against nonlinear or nonconstant recurrences.

## 4. Public state transitions

Let

\[
F_k=F_G([k]G).
\]

The replay studies the four public transformations

\[
F_k\longmapsto F_{k+1},
\qquad
F_k\longmapsto F_{2k},
\qquad
F_k\longmapsto F_{-k},
\qquad
F_k\longmapsto F_{\lambda k}.
\]

### 4.1 Bivariate algebraic relations

A bivariate relation of total degree at most `d` has

\[
N(d)=\binom{d+2}{2}
\]

monomial columns.

For successor, doubling, and GLV, the first relation appears exactly at the smallest `d` satisfying

\[
N(d)>n-1.
\]

One degree earlier the evaluation matrix has full column rank. The observed first degrees are:

| `n` | first degree |
|---:|---:|
| 31 | 7 |
| 79 | 12 |
| 67 | 11 |
| 127 | 15 |
| 139 | 16 |

These are ordinary interpolation thresholds, not exceptional group-law identities.

### 4.2 Negation and the swap involution

Negation appears one degree earlier than a generic ordered transition because the sample set consists of `m=(n-1)/2` unordered pairs

\[
\{(F_k,F_{-k}),(F_{-k},F_k)\}.
\]

For total degree `d`, the numbers of symmetric and antisymmetric monomials are

\[
S(d)=\frac{N(d)+\lfloor d/2\rfloor+1}{2},
\qquad
A(d)=\frac{N(d)-\lfloor d/2\rfloor-1}{2}.
\]

The observed rank is exactly

\[
\min(S(d),m)+\min(A(d),m).
\]

The first relation occurs precisely when

\[
S(d)>m,
\]

with full rank at the previous degree. Therefore the earlier negation relation is completely explained by the public swap involution and does not reveal an unexpectedly short transition law.

### 4.3 One-variable rational transitions

A rational graph relation

\[
A(F_k)-F_{uk}B(F_k)=0,
\qquad
\deg A,\deg B\le d,
\]

has `2(d+1)` columns.

For all four transformations, the first relation occurs at

\[
\boxed{d=m=\frac{n-1}{2}},
\]

exactly when the number of columns exceeds the `n-1` rows. At degree `m-1` the matrix has full rank `n-1`.

Thus the state does not admit a low-degree rational successor, doubling, negation, or GLV map on the frozen corpus.

## 5. secp256k1 dimension frontier

For secp256k1, the first degree at which a completely generic bivariate interpolation relation is forced is

\[
\boxed{
481231938336009023090067544955250113852
}.
\]

The same value is the first degree at which the symmetric negation subspace exceeds the number of unordered pairs. It has 129 bits and is asymptotic to `sqrt(2n)`.

The first dimension-forced one-variable rational transition degree is

\[
\boxed{
\frac{n-1}{2}
=
57896044618658097711785492504343953926418782139537452191302581570759080747168,
}
\]

which has 255 bits.

These are exact dimension thresholds. They do not prove that the production secp256k1 state has no lower-degree relation. The frozen results show that no exceptional relation appears in the declared corpus before the thresholds.

## 6. Decision

C41 closes on the frozen corpus:

```text
ordinary polynomial functional decomposition,
short constant-coefficient recurrence of orbit-factor coefficients,
low-degree bivariate successor, doubling and GLV relations,
low-degree rational successor, doubling, negation and GLV maps,
negation relations beyond those forced by the swap involution.
```

C41 does not close:

```text
rational or multivariate functional decomposition,
nonlinear recurrences with changing coefficients,
target-dependent transposed resultants,
elliptic-net or determinant circuits not mediated by F_k alone,
incomplete-product algorithms using additional curve coordinates,
unrestricted arithmetic circuits.
```

No cheap decoder has been found. The remaining positive route must bypass both explicit orbit coefficients and a low-degree transition law in the single Miller-state coordinate.

## 7. Successor

The next scoped package is

```text
ORIENTED-TRANSPOSED-RESULTANT-C42.
```

It should ask whether the value

\[
\Delta(F_G(Q))
\]

can be evaluated directly by transposed modular composition, structured determinant displacement, or an elliptic-net resultant without constructing `P_even`, `P_odd`, `K_H`, or a square-root-width block table.
