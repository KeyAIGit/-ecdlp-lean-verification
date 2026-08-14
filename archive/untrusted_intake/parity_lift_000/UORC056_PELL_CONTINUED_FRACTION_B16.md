# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track B16: standard Pell continued-fraction and half-gcd boundary

Date: 2026-08-14

Status: **the distinguished generator-oriented Pell factor admits the ordinary
polynomial Euclidean and continued-fraction representation, but that standard
representation is not compact. The quotient-degree sum is exactly the reduced
input degree. Therefore an explicit quotient list, continuant, or materialized
half-gcd transformation has linear field-word size. On secp256k1 the reduced
degree is at least `2^253`. Frozen B7A factors also exhibit almost entirely
linear quotients and a quotient count close to the degree. This does not close
an implicit transposed algorithm that evaluates only `A(x(Q)):B(x(Q))` without
materializing the Euclidean state.**

No external point, key, wallet, unknown scalar, or production-sized DLP target
is accepted. The replay uses only the ten frozen B7A toy curves and public
secp256k1 integers.

## 1. Input from B7A and B13-B15

The B track has isolated a generator-oriented principal function

```text
f_G(P)=A(x(P))+y(P)B(x(P))
```

whose quadratic norm satisfies

```text
A(X)^2-(X^3+7)B(X)^2
 =c_G K_H(X)(X-x(S_G)).                         (B16.1)
```

Away from the two public exceptional points, its exact selector is

```text
-y(Q)B(x(Q))/A(x(Q))=(-1)^k,
Q=[k]G.                                           (B16.2)
```

B13-B15 identify alternating Miller integration, the cyclic elliptic factorial,
and the Hilbert-90 lift with the same distinguished global factor. The next
possible compression candidate is a polynomial continued fraction or half-gcd
program for `A/B`.

## 2. Exact Euclidean telescoping

Run the ordinary polynomial Euclidean algorithm on `A` and `B`, swapping them
if necessary:

```text
R_(-1)=A,
R_0=B,
R_(i-1)=q_i R_i+R_(i+1),
deg R_(i+1)<deg R_i.
```

For every nonterminal step,

```text
deg q_i=deg R_(i-1)-deg R_i.                    (B16.3)
```

If the terminal remainder is the gcd `g`, summation telescopes:

```text
boxed:
sum_i deg q_i=max(deg A,deg B)-deg g.            (B16.4)
```

This identity is independent of how many quotients have degree one or how the
Euclidean tree is balanced.

An explicit polynomial quotient of degree `d` contains `d+1` field
coefficients. Hence a materialized quotient list uses at least

```text
sum_i deg q_i
```

field words. By `(B16.4)`, its representation size is at least the reduced
input degree.

## 3. Consequence for continuants and half-gcd

The continued fraction of `A/B` is the quotient list

```text
[q_0;q_1,...,q_r].                              (B16.5)
```

Its convergents are produced by products of the standard two-by-two matrices

```text
M(q_i)=((q_i,1),(1,0)).                          (B16.6)
```

Balancing these products with half-gcd can reduce arithmetic time from a
quadratic polynomial algorithm to quasi-linear time in the input degree. It
does not make the represented transformation constant-size. At least one of
the following remains materialized in the standard architecture:

```text
the quotient polynomials,
the continuant numerators and denominators,
a half-gcd transformation matrix with polynomial entries,
or an equivalent product/remainder tree.
```

Their total coefficient representation is `Omega(D)`, where

```text
D=max(deg A,deg B)-deg gcd(A,B).                 (B16.7)
```

Therefore quasi-linear in `D` is still linear in `n` for the declared Pell
factor. Faster polynomial arithmetic is not an exponent improvement for the
056 cost gate.

This is a representation-class boundary. It is not a lower bound against an
algorithm that never materializes these polynomials and directly evaluates one
functional at `x(Q)`.

## 4. Exact secp256k1 degree certificate

For secp256k1,

```text
n=1 mod 8,
h=(n-1)/4,
M=(n-1)/2=2h.
```

The principal divisor has pole order

```text
M+1=2h+1.                                        (B16.8)
```

In the Riemann-Roch basis

```text
1,x,...,x^h,
y,xy,...,x^(h-1)y,
```

the only term with pole order exactly `2h+1` is `x^(h-1)y`. Thus the
distinguished factor must satisfy

```text
boxed:
deg B=h-1.                                       (B16.9)
```

The norm in `(B16.1)` is squarefree except at the one public anchor root
`x(S_G)`, already present in `K_H`. Consequently a common factor of `A` and `B`
can have degree at most one in this declared divisor model. Therefore

```text
D >= h-2=(n-1)/4-2.                              (B16.10)
```

The exact public integer certificate gives

```text
boxed:
D >= 2^253.                                      (B16.11)
```

So explicit continued-fraction or half-gcd state is enormously above both the
`2^128` Pollard frontier and the required `O(n^(1/2-epsilon))` budget.

## 5. Frozen exact replay

The executable

```text
experiments/parity_lift_000/uorc056_pell_continued_fraction.py
```

reconstructs the B7A principal factors on ten frozen cofactor-one prime-order
toy curves. It then computes the complete polynomial Euclidean quotient list.

Exact aggregate results:

```text
frozen cases                                      10
total principal numerator degree                 277
total terminal gcd degree                          3
total Euclidean quotients                         261
total quotient degree                             274
materialized quotient coefficient slots           535
degree-one quotients                              248
largest toy order                                 313
largest quotient count                             76
all telescoping identities                       true
```

The toy data show that the standard quotient sequence is not only linear in
total degree by theorem, but also close to linear in quotient count for these
instances. The latter is bounded evidence, not an asymptotic theorem for
secp256k1.

## 6. Formalization boundary

`Ecdlp/Proved/PellContinuedFractionBoundary.lean` kernel-checks:

1. explicit quotient coefficient slots dominate quotient-degree sum;
2. abstract Euclidean degree telescoping;
3. explicit slots dominate reduced degree;
4. the secp256k1 reduced-degree lower bound is at least `2^253`.

Lean does not formalize the elliptic curve, the B7A divisor, Riemann-Roch,
polynomial Euclidean correctness, half-gcd, the common-factor classification,
or parity extraction. These are explicit premises of this scoped package.

## 7. Decision

```text
Ordinary polynomial continued fraction exists             yes
Quotient-degree sum                                        reduced input degree
Explicit quotient/continuant representation                Omega(n) field words
Materialized half-gcd matrix                               Omega(n) field words
Exact secp reduced-degree lower bound                      at least 2^253
Does fast polynomial arithmetic meet sub-sqrt?             no
Implicit transposed single-value evaluation                open
Public parity oracle                                       absent
Classical sub-square-root ECDLP                             absent
```

## 8. Next admitted target

The only continued-fraction escape that remains is genuinely transposed and
single-value:

```text
Given public E,G,Q, evaluate A(x(Q)):B(x(Q))
without constructing A, B, their quotient list, a half-gcd matrix,
K_H, or an equivalent degree-D state.
```

A positive proposal must provide an application algorithm whose represented
state and arithmetic work are both below `n^(1/2-epsilon)`. Merely naming
half-gcd, subresultants, continuants, or fast polynomial multiplication is not
sufficient because their standard input and output representations are already
linear in `D`.
