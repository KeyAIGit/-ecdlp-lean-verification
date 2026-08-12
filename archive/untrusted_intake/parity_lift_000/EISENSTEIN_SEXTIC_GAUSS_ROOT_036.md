# EISENSTEIN-SEXTIC-GAUSS-ROOT-036

Date: 2026-08-12

Status: **exact sextic-character projector whose normalized cube is the hidden scalar Legendre class; direct evaluation remains linear in the subgroup order**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from packages 034 and 035

For

```text
H=<G>,  |H|=n,
Q=[k]G,
```

package 034 produced the exact public-line projector

```text
S_3(P)=sum_(a=1..n-1) chi_n(a)x([a]P)^3,
S_3([k]G)=chi_n(k)S_3(G).
```

Package 035 identified `S_3(G)` as the first coefficient separating the two
generator-oriented quadratic factors of the `C6` orbit polynomial.  Its square
is generator-blind, while its sign is the desired scalar Legendre class.

The present package asks whether the special `j=0` CM structure supplies a
lower-degree oriented root before the final quadratic projection.

## 2. Sextic character adapted to the GLV action

On

```text
E: y^2=x^3+7
```

the rational GLV automorphism satisfies

```text
phi(x,y)=(beta*x,y),
beta^3=1,
phi(G)=[lambda]G.
```

Assume

```text
n=1 mod 12,
v_3(n-1)=1.
```

Then there is a unique primitive sextic character

```text
psi:(Z/nZ)^* -> mu_6 subset F_p^*
```

among the two conjugate choices such that

```text
psi(lambda)=beta^(-1)=beta^2.                    (S1)
```

Condition `(S1)` exactly cancels the GLV eigenphase of the x-coordinate.
Indeed, reindexing by `lambda` gives

```text
sum_a psi(a)x([a]G)
 =psi(lambda)beta sum_a psi(a)x([a]G).
```

A nonzero sum is therefore permitted precisely for the adapted choice.

Because the character has order six,

```text
psi^3=chi_n,
psi=psi^4*psi^3,
```

where `psi^4` is the cubic component and `psi^3` the quadratic component.

## 3. Oriented sextic elliptic Gauss projector

Define

```text
T_psi(P)=sum_(a=1..n-1) psi(a)x([a]P).           (S2)
```

For `Q=[k]G`, put `b=a*k`.  Multiplicativity gives

```text
T_psi(Q)
 =sum_b psi(b*k^(-1))x([b]G)
 =psi(k)^(-1)T_psi(G).                           (S3)
```

Whenever `T_psi(G)` is nonzero, define

```text
R_psi(Q)=T_psi(Q)/T_psi(G).
```

Then

```text
R_psi(Q)^3=psi(k)^(-3)=chi_n(k),                 (S4)
R_psi(Q)^6=1.                                    (S5)
```

Thus the hidden scalar Legendre bit is the cube of one normalized sextic
projector.  This is a more structured root of the package-034 observable.

The relation does not give GLV carry or scalar parity: `chi_n(-k)=chi_n(k)` for
`n=1 mod 4`.

## 4. Frozen exact evidence

The frozen family has six prime-order subgroups with `n=1 mod 12`.

Four of them have the secp256k1-style condition

```text
v_3(n-1)=1.
```

On every one of those four cases:

```text
the adapted sextic character is unique;
T_psi(G) is nonzero;
T_psi([k]G)=psi(k)^(-1)T_psi(G) for every k!=0;
R_psi([k]G)^3=chi_n(k) for every k!=0;
T_psi([k]G)^6=T_psi(G)^6 for every k!=0.
```

The natural GLV-compatible projectors weighted by `x^j` for

```text
j in {1,4,7,10}
```

are all nonzero on the retained cases.

Two other `n=1 mod 12` frozen groups have `v_3(n-1)>1`.  There every sextic
character is trivial on the GLV `C3` subgroup, so it cannot satisfy `(S1)`.
They require a character carrying the full 3-primary part of `n-1`, not merely
an order-six character.  This is a structural exclusion, not a failed
statistical fit.

Frozen nonvanishing is bounded evidence only.  It is not a secp256k1
nonvanishing theorem.

## 5. Exact secp256k1 CM certificate

For the standard secp256k1 GLV eigenvalue `lambda`, the public short lattice
vector

```text
a=0x3086D221A7D46BCDE86C90E49284EB15,
b=-0xE4437ED6010E88286F547FA90ABFE4C3
```

satisfies

```text
a+b*lambda=0 mod n,
a^2-a*b+b^2=n.                                   (S6)
```

Thus the subgroup order is the Eisenstein norm of the CM element `a+b*rho`.
The public parameters also satisfy

```text
n=7 mod 9,
n=1 mod 12,
v_3(n-1)=1,
lambda^((n-1)/3)=lambda^2 mod n.                 (S7)
```

These congruences place secp256k1 in exactly the character-theoretic branch
screened by `(S1)` through `(S5)`.

The certificate identifies the CM kernel and the cubic orientation of its
unit.  It does not evaluate `T_psi(G)` or select its generator-oriented
quadratic branch.

## 6. Relation to known elliptic Gauss sums

Universal elliptic Gauss-sum theory studies character-weighted torsion
coordinate sums and constructs invariant powers and elliptic Jacobi ratios as
modular functions.  Those invariant powers are suitable for point-counting
because they remove the character eigenphase.

The present object deliberately retains that phase.  Its sixth power is
invariant, but its cube changes by the scalar quadratic character.  Therefore
a modular formula for `T_psi^6` does not solve our problem.

In the Eisenstein-CM literature, cubic elliptic Gauss sums are normalized by a
canonical cubic root associated with an Eisenstein prime, and for primes in
the `7 mod 9` branch formulas of the form

```text
cubic elliptic Gauss sum = coefficient * canonical_root^2
```

are obtained.  This supports the existence of a canonical cubic CM
normalization.  It does not by itself orient the independent quadratic
component of our sextic character, nor identify the present x-weighted sum
with that specific analytic elliptic function.

The exact remaining question is therefore a mixed cubic-quadratic, or
elliptic-Jacobi, orientation problem.

## 7. Complexity

The literal evaluation of `(S2)` requires

```text
Theta(n) scalar multiples or an equivalent table,
Theta(n) field operations.
```

The short identity `(S3)` is useful only after the base projector is available.
The generic universal modular algorithms have level-dependent data and do not
supply a sub-square-root specialization for a cryptographic-sized level `n`.

This package obtains no public evaluator with cost `o(sqrt(n))`.

## 8. Answer

```text
Does an adapted sextic character exist for the secp branch?       yes
Does it cancel the GLV x phase?                                   yes
Exact normalized projector                                        R_psi=T_psi(Q)/T_psi(G)
What does its cube equal?                                          chi_n(k)
What does its sixth power retain?                                  no generator information
Frozen secp-style projectors nonzero                               all four
secp256k1 Eisenstein norm certificate                              exact
Direct evaluation cost                                             Theta(n)
secp256k1 nonvanishing theorem                                     absent
Compact oriented CM/Jacobi formula                                absent
Public carry / hard-R3 / parity decoder                           absent
Classical sub-square-root ECDLP algorithm                         absent
```

## 9. Next object

The successor is

```text
GENERATOR-ORIENTED-ELLIPTIC-JACOBI-037.
```

Its exact object is the generator-oriented cube

```text
J_G=T_psi(G)^3,
J_Q/J_G=chi_n(k).
```

The sixth power `J_G^2=T_psi(G)^6` is generator-blind and belongs to the
standard invariant layer.  The missing bit is the square-root branch of that
invariant selected by the public generator.

Central question:

> Can the `j=0`, `n=7 mod 9` Eisenstein-CM specialization express the oriented
> cube `T_psi(G)^3`, or directly the ratio `T_psi(Q)^3/T_psi(G)^3`, through a
> compact elliptic Jacobi sum, Hecke-character value, ray-class symbol, or
> theta/sigma identity with total cost `O(n^(1/2-epsilon))`, rather than only
> the generator-blind sixth power?

The theorem-first obligations are:

1. identify the exact modular weight and character of the x-weighted sextic
   projector, including the parity exception to the standard x/y convention;
2. derive its relation, if any, to a product of cubic and quadratic elliptic
   Gauss sums and to universal elliptic Jacobi sums;
3. determine the generator-change law of every candidate CM formula;
4. reject every expression invariant under nonsquare generator change, since
   such an expression computes only the square;
5. prove nonvanishing on secp256k1 or give a compact finite fallback family;
6. count ray-class degree, modular-polynomial degree, coefficient size,
   preprocessing, online work, and advice;
7. even after a compact scalar-Legendre oracle, give a separate literal
   classical shifted-Legendre recovery theorem before claiming a classical
   ECDLP improvement.

No broad statistical search is admitted without a new exact identity.

## 10. Formalization boundary

`Ecdlp/Proved/EisensteinSexticGaussRoot.lean` formalizes the elementary cube,
sixth-power, and character-factorization identities.  It does not formalize
elliptic Gauss sums, CM, Hecke characters, modular forms, secp256k1
nonvanishing, or arithmetic-circuit complexity.
