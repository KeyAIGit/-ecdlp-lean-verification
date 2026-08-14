# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track B17: polynomial-Pell sign seed and half-gcd boundary

Date: 2026-08-14

Status: **the B7A polynomial-Pell equation has an exact public marked-generator
sign condition that distinguishes its two quadratic conjugates. However, the
symmetric Pell input alone is generator-blind, explicit solutions contain
`Theta(n)` coefficients, and standard half-gcd/subresultant rational
reconstruction requires an oriented modular-root state or constructs the dense
solution. The public one-point seed selects a candidate after construction but
no method is known that propagates it to an arbitrary query below the
square-root gate.**

No external point, private key, wallet, unknown scalar, or production-sized
DLP target is accepted. Executable checks use only the ten frozen toy
subgroups from B7A.

## 1. Central target is unchanged

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with all preprocessing, advice, coefficient generation, representation,
memory, branch selection, and online work charged inside

```text
O(n^(1/2-epsilon)).
```

B7A constructs the principal factor

```text
f_G(P)=A_G(X)+y(P)B_G(X),
X=x(P),
```

and the polynomial-Pell identity

```text
A_G(X)^2-F(X)B_G(X)^2
 =c_G K_H(X)(X-x(S_G)),
F(X)=X^3+7.                                       (B17.1)
```

The parity selector away from the public exceptional pair is

```text
Pi_G(Q)=-y(Q)B_G(x(Q))/A_G(x(Q)).                 (B17.2)
```

B17 asks whether half-gcd, subresultant, Padé, or rational reconstruction can
evaluate `(B17.2)` without materializing `A_G`, `B_G`, or an oriented root in
the split Kummer algebra.

## 2. Quadratic conjugation leaves the norm input unchanged

If `(A,B,c)` satisfies `(B17.1)`, then so do

```text
(-A,B,c),
(A,-B,c),
(-A,-B,c).                                       (B17.3)
```

In particular,

```text
(-A)^2-FB^2=A^2-FB^2.                            (B17.4)
```

The subgroup kernel `K_H`, the curve polynomial `F`, the public linear factor
`X-x(S_G)`, and the norm polynomial are unchanged by `G -> -G`.

Under the B7A normalization that fixes the last nonzero coefficient of `B`, the
frozen exact solutions satisfy

```text
A_(-G)=-A_G,
B_(-G)= B_G.                                      (B17.5)
```

But the selector changes sign:

```text
Pi_(-G)(Q)=-Pi_G(Q).                              (B17.6)
```

Therefore a procedure whose effective input is only the symmetric Pell data
cannot select the generator-oriented answer for both marked generators.

## 3. A public one-point sign condition exists

The canonical scalar `1` is odd and `n-1` is even. Therefore `-G` belongs to
the zero half of `f_G`, while `G` does not. In coordinates,

```text
f_G(-G)=A_G(x(G))-y(G)B_G(x(G))=0.               (B17.7)
```

Equivalently,

```text
boxed:
A_G(x(G))=y(G)B_G(x(G)).                         (B17.8)
```

For the reversed marked generator `-G`, the sign of `y(G)` reverses and the
condition selects `A_(-G)=-A_G`.

Thus the missing orientation is not logically absent from the public input.
The marked point supplies an exact anti-invariant seed.

However `(B17.8)` is one scalar condition. It distinguishes the conjugate pair
once that pair has been constructed, but it does not by itself evaluate the
degree-`Theta(n)` solution at the other `(n-1)/2` Kummer components.

## 4. Why standard half-gcd does not yet solve the target

A rational-reconstruction formulation normally starts from an oriented modular
root

```text
R(X)=A_G(X)/B_G(X) mod K_H(X),
R(X)^2=F(X) mod K_H(X),                           (B17.9)
```

possibly after removing the public exceptional factor where both numerator and
denominator vanish.

Supplying `R(X)` explicitly supplies the generator-oriented branch values in
the split Kummer algebra. Its standard coefficient representation has
`Theta(n)` size and is equivalent to the missing oriented state.

Alternatively, solving `(B17.1)` directly by polynomial extended-Euclidean,
continued-fraction, subresultant, or half-gcd methods constructs polynomials
with total coefficient count

```text
N=(n+1)/2.                                       (B17.10)
```

Balanced recursion lowers depth, not output size. A transposed one-point
variant would need an independently compressed oriented input state; B6 and
B16 show that the standard translation and recurrence states are dense.

This is a boundary for standard explicit Pell/reconstruction representations,
not a lower bound against every nonlinear arithmetic circuit.

## 5. Frozen exact replay

For each of the ten B7A frozen curves the replay constructs normalized
solutions for `G` and `-G` independently and verifies:

1. the Kummer kernel polynomial is identical;
2. the public anchor x-coordinate is identical;
3. `A_(-G)=-A_G` and `B_(-G)=B_G`;
4. both solutions have the same Pell norm polynomial;
5. the public seed `(B17.8)` holds for both marked generators;
6. the opposite local value is nonzero;
7. selector `(B17.2)` gives exact canonical parity whenever defined;
8. any denominator exception is contained in the fully public anchor pair.

Across the corpus there are `1086` exact nonexceptional parity checks and `6`
public exceptional evaluations.

## 6. Formalization boundary

`Ecdlp/Proved/PolynomialPellSignSeedBoundary.lean` kernel-checks:

1. invariance of the quadratic norm under `A -> -A`;
2. covariance of the marked one-point seed under simultaneous generator/y
   negation;
3. sign reversal of the rational selector when the conjugate factor is chosen.

It does not formalize polynomials, elliptic curves, half-gcd, subresultants,
Kummer algebras, secp256k1, parity recovery, or ECDLP.

## 7. Decision

```text
Exact symmetric Pell equation                         yes
Public anti-invariant seed at G                       yes
Symmetric Pell data alone selects orientation         no
Explicit A,B coefficient count                        (n+1)/2
Standard rational reconstruction without root input   no
Standard half-gcd with explicit oriented root          linear-state input
One-point sign seed propagated sub-root                not found
Public parity oracle                                  absent
```

## 8. Remaining genuinely open mechanism

After B16-B17, the standard linear, orbit-polynomial, and explicit Pell routes
are exhausted. A positive B result must be a nonlinear **seed-propagation
identity** that takes

```text
K_H and its compact Frobenius representation,
the public marked seed A(x(G))=y(G)B(x(G)),
the query Q,
```

and evaluates the conjugate choice at `x(Q)` without constructing the split
root, the Pell coefficients, the endpoint path, or a square-root-size state.

No such identity is presently known. This is the same unchanged central target
056, now expressed as propagation of one public branch seed through a highly
structured split algebra.