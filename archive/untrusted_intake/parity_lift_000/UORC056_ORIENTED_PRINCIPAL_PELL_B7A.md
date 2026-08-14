# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track B7A: canonical principalization and polynomial-Pell boundary

Date: 2026-08-14

Status: **the canonical parity half has an exact generator-oriented principal
factor. Its quadratic norm is the symmetric subgroup kernel times one public
linear factor, producing a concrete polynomial-Pell equation and an exact
parity selector. Standard generalized Miller trees still have linear charged
size, and every explicit one-level plus/minus index system has square-root
charged width. No strict sub-square-root evaluator is obtained.**

No external point, private key, wallet, unknown scalar, or production-sized
discrete-log target is accepted. Production-sized constants are used only for
public integer and complexity certificates.

## 1. Central target is unchanged

Let

```text
E/F_p : y^2=F(x)=x^3+7,
H=<G>,
|H|=n,
n odd and prime,
Q=[k]G, 1<=k<n.
```

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k
```

with preprocessing, advice, memory, representation, branch selection, and
online work all charged inside

```text
O(n^(1/2-epsilon)).
```

B2 showed that ordinary Miller characters expose only two-endpoint residue
edges. B3 showed that the compact map `Frob-id` exposes `K_H^2` and local
squares but does not select the marked branch. B4 proved that the raw even-minus-odd half-divisor has a nontrivial
order-`n` Picard class and identified the need for a compensating public pair.
B5-B7 then closed explicit resultant trees, ordinary transposed linearization,
and bounded-state linear CM recurrences. B7A chooses the compensating pair
canonically and converts the remaining nonlinear branch into one exact
quadratic norm factorization.

## 2. Exact sum of the canonical even half

Put

```text
M=(n-1)/2,
E_G={ [2]G,[4]G,...,[n-1]G }.
```

The sum of its scalar labels is

```text
2(1+2+...+M)=M(M+1)=(n^2-1)/4.
```

Modulo `n`, this gives

```text
S_G := sum_(P in E_G) P = [-4^(-1)]G.             (B7A.1)
```

Define the public anchor

```text
A_G := -S_G = [4^(-1)]G                         (B7A.2)
```

and

```text
N=M+1=(n+1)/2.
```

Then the degree-zero divisor

```text
D_G = sum_(P in E_G) [P] + [A_G] - N[O]          (B7A.3)
```

has zero group sum. This is exactly the canonical compensation predicted by
B4. If `Delta_G=E_G-O_G` has class `[M]G=[-2^(-1)]G`, then

```text
[A_G]-[S_G] has class [2^(-1)]G,
[Delta_G]+[A_G]-[S_G]=0 in Pic^0(E).              (B7A.4)
```

Indeed `A_G+[M]G=S_G`, so B4's general pair
`(R)-(R+[M]G)` is obtained by the public choice `R=A_G`.

The divisor `D_G` has zero group sum. On an elliptic curve, the Abel-Jacobi criterion therefore
makes `D_G` principal. There is a nonzero rational function `f_G`, unique up to
one field scalar, such that

```text
div(f_G)=D_G.                                    (B7A.5)
```

If `A_G` is already in `E_G`, its zero occurs with multiplicity two. The
frozen replay verifies the resulting multiplicity through the exact norm
factorization below rather than by treating a repeated evaluation row as a
second independent condition.

## 3. Riemann-Roch coordinate form

The only pole of `f_G` is at `O`, of order `N`. The standard basis of
`L(N[O])` on a short Weierstrass curve gives

```text
f_G(P)=A_G^poly(x(P))+y(P)B_G^poly(x(P)),         (B7A.6)
```

where

```text
deg A_G^poly <= floor(N/2),
deg B_G^poly <= floor((N-3)/2).                   (B7A.7)
```

To avoid confusing the anchor point with the polynomial, the remainder of this
memo writes the two polynomials as `A(X)` and `B(X)`.

Generator reversal acts by quadratic conjugation. Since the even support for
`-G` is the negative of the even support for `G`,

```text
f_(-G)(P) is proportional to f_G(-P)
            =A(x(P))-y(P)B(x(P)).                (B7A.8)
```

Thus this object passes the mandatory `G -> -G` sensitivity gate.

## 4. Exact quadratic norm and polynomial-Pell equation

Let

```text
K_H(X)=product_(j=1)^M (X-x([j]G)).              (B7A.9)
```

As a function on the curve, `K_H(x)` has the `n-1` nonzero subgroup points as
its zeros. Multiplying `f_G(P)` by its quadratic conjugate adds the negative
zero divisor. The even and odd halves then cover every nonzero subgroup point,
and the two public anchor points contribute one additional opposite pair.

Consequently there is a nonzero constant `c_G` such that

```text
f_G(P)f_G(-P)
 =c_G K_H(x(P))(x(P)-x(S_G)).                    (B7A.10)
```

Substituting `(B7A.6)` and `y^2=F(x)` gives the exact polynomial identity

```text
boxed:
A(X)^2-F(X)B(X)^2
 =c_G K_H(X)(X-x(S_G)).                          (B7A.11)
```

This is the first concrete generator-oriented polynomial-Pell normal form in
the 056 B-track. The right side is symmetric and generator-blind up to the public
anchor pair. The factor `A+yB` selects the canonical even half; its conjugate
`A-yB` selects the canonical odd half.

The scalar ambiguity `f_G -> u f_G` changes `c_G` by the square `u^2`. Hence
the quadratic character of `c_G` is intrinsic to the declared divisor.

For secp256k1,

```text
n = 1 mod 8,
p = 3 mod 4,
N=(n+1)/2 is odd.
```

The leading term of `(B7A.11)` is therefore

```text
c_G=-lc(B)^2,
```

so

```text
chi_p(c_G)=-1.                                   (B7A.12)
```

This fixes a norm square class, but it does not by itself select between the
two conjugate factors.

## 5. Exact parity selector from the principal factor

For a nonzero subgroup point `Q=[k]G`, exactly one of `Q` and `-Q` belongs to
the canonical even half, except at one fully public anchor pair described
below. Therefore

```text
boxed:
Pi_G(Q)
 =[f_G(-Q)-f_G(Q)]/[f_G(-Q)+f_G(Q)]
 =(-1)^k.                                        (B7A.13)
```

Using `(B7A.6)`, the same selector is

```text
Pi_G(Q)=-y(Q)B(x(Q))/A(x(Q)).                    (B7A.14)
```

At a subgroup root of the norm, `A(X)=0` forces `B(X)=0`, because `F(x(Q))` is
nonzero in an odd-order subgroup. Hence the only denominator exceptions are
points where both conjugate factors vanish.

For secp256k1, `S_G=[(n-1)/4]G` has an even canonical scalar and
`A_G=[4^(-1)]G` has an odd canonical scalar. Both are zeros of `f_G`, so
`(B7A.13)` is `0/0` at the public pair

```text
{S_G,A_G}.
```

This is not hidden advice. A complete evaluator first compares `Q` with these
two public points, returns `+1` at `S_G` and `-1` at `A_G`, and otherwise uses
`(B7A.13)`.

The constructive bottleneck is now exact:

```text
evaluate A(x(Q)) and B(x(Q)) without materializing A, B, or K_H.
```

## 6. Generalized Miller construction and its charged size

For a finite point list `T`, let `mu_T` be a Miller function with divisor

```text
sum_(P in T)[P]-[sum T]-(|T|-1)[O].              (B7A.15)
```

For disjoint lists `U,V`, the standard line-function merge gives

```text
mu_(U union V)
 is proportional to
 mu_U mu_V g_(sum U,sum V),                      (B7A.16)
```

where `g_(P,Q)` is the usual line-over-vertical factor. Applying the final
public anchor yields `f_G` exactly.

A balanced merge tree changes parallel depth but not charged size:

```text
leaves = N,
merges = N-1,
depth >= ceil(log_2 N).                          (B7A.17)
```

For secp256k1, `N` is approximately `2^255`. The ordinary generalized Miller
construction is therefore an exact representation, not an admissible compact
evaluator.

This is consistent with the standard Miller principle: a straight-line program
can be short in the bit length of a compact divisor description, but the
declared parity divisor is supplied here by `Theta(n)` individually oriented
points unless a new compression law is found.

## 7. One-level square-root index-system boundary

The square-root Velu method accelerates symmetric kernel products by writing a
large index set in a one-level baby-step/giant-step form. To audit the analogous
oriented construction, suppose an explicit plus/minus index system uses sets
`I,J,K` with

```text
a=|I|,
b=|J|,
k=|K|,
E_G subseteq (I+J) union (I-J) union K.           (B7A.18)
```

Even before collisions are charged, this representation covers at most

```text
2ab+k
```

support points. Thus

```text
M <= 2ab+k.                                      (B7A.19)
```

If the charged width is

```text
w=a+b+k,
```

then nonnegativity gives

```text
boxed:
2M <= w(w+2).                                    (B7A.20)
```

Hence

```text
w=Omega(sqrt(M))=Omega(sqrt(n)).                 (B7A.21)
```

For secp256k1, the exact integer certificate is

```text
w >= 2^128-1,
```

with a balanced witness of width `2^128`.

This closes only explicit one-level plus/minus index systems whose support is
materialized through the declared sets. It is not a lower bound against nested
resultants, transposed evaluation, nonlinear recurrences, or an implicit
factorization of `(B7A.11)`.

The ordinary x-only square-root Velu output remains generator-blind because it
computes symmetric kernel data such as `K_H` or the quotient isogeny. Adding one
oriented leaf for every selected branch passes orientation but remains at the
square-root width boundary by `(B7A.20)`.

## 8. Frozen exact replay

The executable verifier

```text
experiments/parity_lift_000/uorc056_oriented_principal_pell.py
```

uses ten frozen cofactor-one prime-order toy curves:

```text
(p,n)=(13,7),(43,31),(61,61),(67,79),(79,67),
      (97,79),(127,127),(163,139),(211,199),(349,313).
```

For every case it verifies exactly:

1. the support-sum identity `(B7A.1)`;
2. the anchored zero-divisor group sum;
3. the one-dimensional Riemann-Roch solution for `A+yB`;
4. the full polynomial identity `(B7A.11)`;
5. the exact subgroup zero set, including anchor multiplicity through the norm;
6. the parity selector on every nonzero point, with public exceptions handled;
7. generator reversal as quadratic conjugation;
8. the leading norm square class;
9. the exact `N-1` binary merge count;
10. the one-level width inequality.

Aggregate frozen totals are:

```text
cases                              10
nonzero-point selector checks      1092
ordinary ratio checks              1086
public exceptional checks          6
maximum tested pole order           157
all exact identities                 true
```

The toy polynomials are generally dense. This is bounded evidence against a
naive sparsity hypothesis, not a circuit lower bound for secp256k1.

## 9. Formalization boundary

The Lean file

```text
Ecdlp/Proved/OrientedPrincipalPellBoundary.lean
```

kernel-checks only the algebraic and combinatorial core:

1. the exact quarter-sum integer identity;
2. quadratic conjugate norm multiplication;
3. the two nonexceptional selector branches;
4. binary merge-tree leaves versus merges;
5. the one-level index-width inequality.

It does not formalize elliptic curves, Abel-Jacobi, Riemann-Roch, polynomial
interpolation, the divisor of `K_H`, secp256k1, or an ECDLP algorithm.

## 10. Decision

```text
Exact generator-oriented principal factor                 yes
Exact divisor                                             even half + public anchor
Exact polynomial-Pell norm                                yes
Generator reversal                                        quadratic conjugation
Exact parity selector from f_G                            yes, with public pair gate
Ordinary generalized Miller size                          Theta(n)
Explicit one-level plus/minus index width                 Omega(sqrt(n))
Does x-only square-root Velu select the factor?            no
Strict sub-square-root evaluator                           absent
Public parity oracle                                       absent
Classical sub-square-root ECDLP                            absent
```

This package advances the constructive line because the missing branch is no
longer only an abstract square root modulo `K_H`. It is one explicit factor in
an exact quadratic norm equation with a public anchor and an exact rational
selector.

## 11. Strategic consequence

This checkpoint feeds the already planned nonlinear successor:

```text
UORC056-NONLINEAR-CM-STATE-B8.
```

Its exact question is now sharpened to:

> Given public `E,G,Q,n`, can one evaluate the distinguished factor
> `A(x(Q))+y(Q)B(x(Q))`, or directly the ratio `-y(Q)B(x(Q))/A(x(Q))`, from
> the norm equation `(B7A.11)` in complete `O(n^(1/2-epsilon))` cost without
> constructing `K_H`, `A`, or `B` densely?

The first admitted mechanisms are:

1. a transposed subresultant or half-gcd evaluation that outputs only
   `A(x(Q)):B(x(Q))`;
2. a nonlinear factor-extraction law using the compact `Frob-id` kernel map;
3. a nested index system whose charged state is provably below the one-level
   square-root frontier;
4. a continued-fraction or polynomial-Pell recurrence whose program is
   generated from `(E,G,n)` without an oriented root table;
5. a local-to-global factorization seeded by the marked generator, with all
   quotient-algebra dimension and branch costs charged.

A candidate is rejected immediately if it only computes the symmetric norm,
chooses between `A+yB` and `A-yB` by hidden advice, or renames a degree-`M`
quotient algebra as one constant-size operation.
