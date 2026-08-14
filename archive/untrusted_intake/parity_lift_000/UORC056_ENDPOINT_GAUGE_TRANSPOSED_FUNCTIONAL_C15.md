# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C15: endpoint-gauge transposed functional and sparse anti-resolvent boundary

Date: 2026-08-13

Status: **the endpoint gauge has an exact constant-description two-neighbour product, but that product is orientation-even and leaves one global `mu_2` ambiguity. On divisor coefficients, the endpoint functional is the odd-cycle anti-resolvent of seven public sources. Its rational cyclic translate rank is `n-1`; the existing finite-field representation theorem gives dimension at least `(n-1)/6` on secp256k1; and the signed secp256k1 quarter-orbit meets `3s/2-20` partial GLV orbits. No tested transposed, local-neighbour, complete-GLV-orbit, or rectangular-block mechanism beats the square-root boundary. Unrestricted addition-enabled nonlinear circuits remain open.**

Only frozen toy curves, known toy generators, public generator replacements, and public secp256k1 constants are used. No unknown-scalar external point, wallet, private key, or production target is accepted.

## 1. Input from C13-C14

Let

```text
E: y^2=F(x),
H=<G>, |H|=n=2m+1,
P_k=[k]G.
```

C13 constructs a degree-zero divisor `D`, its compact representative

```text
D0=(A)-(O), A=[a]G,
```

and a principal gauge divisor

```text
E_G=D-D0=div(h_G).
```

With

```text
Z_G(P)=h_G(P)/h_G(P+G),
```

C13 gives

```text
f_G(P)=gamma*c_(A,-G)(P)*Z_G(P),                 (C15.1)
```

where `gamma` is independent of `P` and

```text
div(c_(A,-G))=(A)+(-G)-(A-G)-(O).                (C15.2)
```

C14 proves that an abstract `G_m`-torsor supplies no canonical rational scalar of nonzero fibre weight. Such a scalar is already a rational trivialization. C15 therefore works with the prescribed gauge instead of renaming it as a generalized-Jacobian coordinate.

## 2. Endpoint divisor equals the target minus four public points

Write

```text
e_k=ord_(P_k)(h_G),
z_k=ord_(P_k)(Z_G)=e_k-e_(k+1).
```

Let

```text
q=delta_a+delta_(n-1)-delta_(a-1)-delta_0        (C15.3)
```

be the divisor coefficient vector of `c_(A,-G)`. The C10 target divisor has

```text
v_k=(-1)^k-delta_(k,m).                          (C15.4)
```

Substitution of the exact C12 primitive gives

```text
boxed:
v=z+q.                                           (C15.5)
```

Thus, outside the four public indices `0,a-1,a,n-1`, endpoint valuation is already the exact parity valuation. The four exceptions are handled by one compact Miller quotient.

## 3. Exact compact two-neighbour law

C13's one-step identity is

```text
g(X)=gamma_1*c_(A,2G)(X)*h_G(X)/h_G(X-2G),       (C15.6)
```

where

```text
g(X)=x(X-G)-x([m]G).
```

Set `X=P+2G`. Then

```text
boxed:
Z_G(P)Z_G(P+G)
 =gamma_1*c_(A,2G)(P+2G)/g(P+2G).                (C15.7)
```

The right side is one four-point Miller quotient divided by one local factor. This is a genuine constant-description compression of two adjacent endpoint values. It does not choose one orientation.

## 4. Global `mu_2` ambiguity and the local-neighbour boundary

For a generic orbit put

```text
u_k=Z_G(P+[k]G),
R_k=u_k*u_(k+1).                                  (C15.8)
```

Both vectors `u` and `-u` satisfy every local equation. Since `n` is odd,

```text
product_k u_k=1,
product_k (-u_k)=-1.                             (C15.9)
```

The canonical branch is therefore selected only by a full-cycle condition. Eliminating successive variables gives

```text
boxed:
u_0=(product_(j odd) R_j)^(-1),                 (C15.10)
```

using exactly `(n-1)/2` odd-neighbour factors.

In the universal Laurent neighbour-oracle model, the only relation among generic `R_j` is `product_j R_j=1`. Every Laurent monomial equal to `u_0` has exponent vector

```text
(-1 on odd j, 0 on even j)+t*(1,...,1).
```

Its minimum support is `(n-1)/2`. Hence a local-neighbour Laurent evaluator needs linear input support. This is a scoped query lower bound, not a lower bound for circuits exploiting extra curve-specific relations among the shifted values.

## 5. Seven-source anti-resolvent

Let

```text
(Tx)_k=x_(k+1).
```

The endpoint divisor satisfies

```text
boxed:
(I+T)z=w,                                        (C15.11)
```

with

```text
w=
 delta_0+delta_(a-2)-delta_a
 -delta_(m-1)-delta_m-delta_(n-2)+2delta_(n-1).  (C15.12)
```

For all frozen orders and secp256k1 these are seven distinct sources. Since `n` is odd,

```text
(I+T)*sum_(j=0)^(n-1)(-T)^j=2I,
```

so

```text
boxed:
2z=sum_(j=0)^(n-1)(-T)^j w.                     (C15.13)
```

The endpoint gauge is therefore seven public defects passed through the same dense odd-cycle anti-resolvent that underlies the earlier parity Green kernel. A sparse source does not make the output sparse.

## 6. Exact rational translate rank

For prime `n`, every nonzero rational vector `x` with `sum_k x_k=0` has cyclic translate rank `n-1`.

If the generating polynomial `X(U)` vanished at a nontrivial `n`-th root, the prime cyclotomic polynomial `Phi_n` would divide `X`. Since `deg X<n`, this would force `X=c Phi_n`; evaluating at `1` and using `X(1)=0`, `Phi_n(1)=n` gives `c=0`, a contradiction.

Therefore

```text
boxed:
rank_Q{x,Tx,...,T^(n-1)x}=n-1.                  (C15.14)
```

This closes fixed-rank rational shift-equivariant Toeplitz, Hankel, displacement, recurrence, and transposed states for the endpoint vector.

Over finite fields, C8 separately proves that every nontrivial secp256k1 translation representation over `F_(p^d)` has charged base-field dimension

```text
d*m >= ord_n(p)=(n-1)/6.                        (C15.15)
```

No unrestricted nonlinear circuit lower bound is inferred.

## 7. Exact secp256k1 GLV fragmentation

For secp256k1 write

```text
n=8s+1,
A=[s]G,
s=(n-1)/8.
```

The signed odd quarter is

```text
S={1,3,...,4s-1}, |S|=2s.                       (C15.16)
```

Let `lambda` be the public GLV eigenvalue, with `lambda^2+lambda+1=0 mod n`. For `j=2t+1` and

```text
c=(lambda-1)*2^(-1) mod n,
```

one has

```text
lambda*j in S
iff
(lambda*t+c) mod n < 2s.                         (C15.17)
```

An exact Euclidean floor-sum computation gives

```text
boxed:
|S intersect lambda*S|=s/2+20.                  (C15.18)
```

In an order-three orbit, `|S|-|S intersect lambda*S|` counts one for every partial orbit and zero for every empty or complete orbit. Hence

```text
boxed:
N_partial=3s/2-20.                               (C15.19)
```

Numerically,

```text
N_partial=
21711016731996786641919559689128982722407043302326544571738468089034655280168,
```

which has 254 bits.

Thus complete GLV order-three orbit aggregates plus bounded corrections cannot represent the signed quarter. At least one correction per partial orbit is required. This does not close arbitrary CM circuits that exploit interval structure by a different mechanism.

## 8. Rectangular joint-evaluation boundary

The prescribed gauge has pole degree

```text
N=r or r+1, r=floor((n+1)/4).
```

For secp256k1, `N=(n-1)/4+1`.

In a rectangular baby/giant grammar with baby width `q` and `b` giant blocks,

```text
q*b>=N,
q+b>=2sqrt(N)=Omega(sqrt(n)).                    (C15.20)
```

Sharing preprocessing between `Q` and `Q+G` changes constants but not the exponent. This is scoped to the declared block representation.

## 9. High-index Ward/division loophole

Logarithmic index recurrence depth does not automatically select the canonical marked-generator branch. The prior public-lift gauge theorem proves that standard Ward fast doubling reconstructs two known-parity lifts whose residues form a fixed public pair; selecting the canonical member is precisely parity.

A single translated division-polynomial or elliptic-net section with public index also has bounded support on a prime subgroup because multiplication by an index coprime to `n` is a permutation. Finite multiplicative collections cannot produce the dense endpoint divisor. Addition-enabled nonhomogeneous identities remain outside this no-go.

## 10. Replay

The full executable checks:

```text
24      base compact neighbour-product identities
1218    global sign-branch identities
12      full-cycle product identities
6       odd-product reconstructions
129     public generator replacements
258     replacement neighbour-product identities
6       endpoint-target divisor identities
6       seven-source anti-resolvent identities
6       rational rank n-1 certificates
```

It also checks the exact secp256k1 floor-sum certificate and brute/floor-sum controls for both order-three eigenvalues modulo the frozen order `433`.

Full result SHA-256:

```text
f6f0cec2dc589600667cf3413b93cdc66bb69a4307badb8e507ff3051779e0b3
```

## 11. Answer

```text
Compact adjacent endpoint product                         yes
Does it select one orientation?                           no
Residual ambiguity                                        one global mu_2 branch
Natural local reconstruction                              (n-1)/2 factors
Universal neighbour-oracle Laurent lower bound            (n-1)/2 inputs
Sparse endpoint source                                    seven points
Rational cyclic translate rank                            n-1
Finite-field linear dimension on secp                     at least (n-1)/6
Partial GLV orbits in signed quarter                      3s/2-20
Rectangular joint block exponent                          square-root
Strictly sub-square-root evaluator                        absent
Parity oracle below square root                           absent
Sub-square-root ECDLP                                     absent
Unrestricted addition-enabled nonlinear circuit           open
```

## 12. Successor

The next package is

```text
SPARSE-SOURCE-NONLINEAR-ANTIRESOLVENT-066.
```

It must evaluate at an encoded point the canonical solution of

```text
(I+T)z=w
```

without materializing `n-1` modes, querying linearly many local products, or receiving the global branch as advice. The highest-value routes are nonlinear divide-and-conquer apply/evaluate circuits, transposed modular composition outside translation representations, addition-enabled section circuits, bounded-width structured ABPs, and scoped lower bounds for explicitly declared resolvent grammars.
