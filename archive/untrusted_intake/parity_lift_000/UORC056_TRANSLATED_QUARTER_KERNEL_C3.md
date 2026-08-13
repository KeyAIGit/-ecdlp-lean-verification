# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C3: translated quarter-kernel trace evaluator

Date: 2026-08-13

Status: **an exact evaluator normal form is constructed for every prime order
`n = 1 mod 4`, including secp256k1. Scalar parity becomes a translated
quarter-kernel zero test, and equivalently one rational trace-pair ratio
satisfying a polynomial Pell identity. The formula is exact, uniform, and
generator-sensitive, but its present explicit representation has `Theta(n)`
coefficients and does not pass the full cost gate.**

No external point, private key, wallet, unknown scalar, or production-sized DLP
target is accepted.

## 1. Frozen target

For

```text
H=<G>, |H|=n, Q=[k]G,
```

the target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k
```

with

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon)).
```

Track C2 gave an exact `n`-state translation resolvent. C3 constructs a
coordinate-side evaluator object directly.

## 2. The n=4h+1 specialization

Write

```text
n=4h+1,
M=(n-1)/2=2h.
```

The secp256k1 subgroup order satisfies `n mod 4 = 1`.

Let

```text
R=[(n+1)/2]G=[2h+1]G.
```

Then

```text
2R=G,
-R=[M]G.
```

Thus `R` is the unique public half of the marked generator, with odd canonical
scalar `2h+1`.

## 3. Quarter-kernel

Define

```text
J_G(X)=product_(j=1)^h (X-x([(2j-1)]G)).          (C3.1)
```

Its roots represent

```text
A_G={+/-G,+/-3G,...,+/-(2h-1)G}.                 (C3.2)
```

The set is stable under point negation, so

```text
J_(-G)=J_G.                                      (C3.3)
```

Also

```text
deg J_G=h=(n-1)/4.                               (C3.4)
```

## 4. Exact translated-set identity

For every even canonical scalar `k=2a`,

```text
k-(2h+1)=2(a-h)-1,
```

which is one of `+/-(1,3,...,2h-1)`. Conversely, adding `R` to the symmetric
odd set gives every nonzero even scalar point exactly once:

```text
boxed:
R+A_G={ [2]G,[4]G,...,[n-1]G }.                  (C3.5)
```

Therefore, for every nonzero `Q=[k]G`,

```text
k is even
iff Q != R and J_G(x(Q-R))=0.                    (C3.6)
```

The exceptional query `Q=R` is public and has odd scalar. Equation `(C3.6)` is
already an exact zero-test evaluator.

## 5. Exact half-divisor

Set

```text
F_even(P)=J_G(x(P-R)).                            (C3.7)
```

Because `J_G(x(P))` has one zero at every point of `A_G` and a pole of order
`M=2h` at the identity, translation gives

```text
div(F_even)
 =sum_(j=1)^M ([2j]G)-M(R).                      (C3.8)
```

The pole `R` is odd, so it does not cancel a selected even zero. Similarly,

```text
F_odd(P)=J_G(x(P+R))                              (C3.9)
```

selects the odd half and has its public pole at `-R`.

## 6. Homogeneous trace pair

Write

```text
E: Y^2=X^3+7,
R=(r,s),
d(X)=(X-r)^2.
```

The addition formulas simplify to

```text
x(P-R)=[u(X)+2sY]/d(X),
x(P+R)=[u(X)-2sY]/d(X),                           (C3.10)
```

where

```text
u(X)=rX^2+r^2X+14.                               (C3.11)
```

Homogenize the first translated value:

```text
d(X)^h J_G((u(X)+2sY)/d(X))
   =A_G(X)+Y B_G(X).                              (C3.12)
```

The conjugate translation is

```text
d(X)^h J_G((u(X)-2sY)/d(X))
   =A_G(X)-Y B_G(X).                              (C3.13)
```

The degree bounds are

```text
deg A_G <= M,
deg B_G <= M-2.                                  (C3.14)
```

All retained frozen cases attain them exactly.

## 7. Polynomial Pell identity

Let

```text
K_H(X)=product_(j=1)^M (X-x([j]G)).              (C3.15)
```

Multiplying the conjugate functions and comparing divisors gives a nonzero
public constant `c_G` with

```text
boxed:
A_G(X)^2-(X^3+7)B_G(X)^2
 =c_G K_H(X)(X-r)^M.                             (C3.16)
```

At every nonzero subgroup point `Q=(q,y)`, `K_H(q)=0`, hence

```text
A_G(q)^2=y^2 B_G(q)^2.                           (C3.17)
```

## 8. Rational evaluator

On an even point, the `P-R` numerator vanishes:

```text
A_G(q)+yB_G(q)=0.
```

On an odd point, the conjugate numerator vanishes:

```text
A_G(q)-yB_G(q)=0.
```

Therefore

```text
boxed:
A(E,G,Q)
 =-y(Q) B_G(x(Q))/A_G(x(Q))
 =(-1)^k.                                        (C3.18)
```

The exact bridge to the package-046 oriented root is

```text
boxed:
Y_G(X)A_G(X)+(X^3+7)B_G(X)=0 mod K_H(X).         (C3.19)
```

Dividing `(C3.19)` by `A_G(x(Q))y(Q)` gives `(C3.18)`.

This is an actual coordinate evaluator formula, not merely an existence
question or an operator lower bound.

## 9. Generator transformation

Under `G -> -G`,

```text
J_(-G)=J_G,
R_(-G)=-R_G,
r_(-G)=r_G,
s_(-G)=-s_G.
```

Hence

```text
A_(-G)=A_G,
B_(-G)=-B_G,                                     (C3.20)
```

and the evaluator changes sign exactly:

```text
A(E,-G,Q)=-A(E,G,Q).                             (C3.21)
```

The mandatory orientation gate is satisfied.

## 10. Frozen replay

`uorc056_translated_quarter_kernel.py` checks four fixed public prime-order
`j=0` curves with

```text
n=61,313,397,433.
```

For every case it verifies exactly:

1. `n=1 mod 4` and `2R=G`;
2. `J_(-G)=J_G`;
3. the translated-set identity `(C3.5)`;
4. the zero-test evaluator `(C3.6)` at every nonzero scalar;
5. homogeneous construction of `A_G,B_G`;
6. the Pell identity `(C3.16)` with a nonzero constant quotient;
7. nonvanishing of `A_G` on all nonzero subgroup points;
8. the rational evaluator `(C3.18)` at every nonzero scalar;
9. the oriented-root bridge `(C3.19)`;
10. covariance `(A,B)->(A,-B)` under `G->-G`.

The replay performs `1,200` exact zero-test checks and `1,200` exact ratio
checks. It accepts no runtime target.

## 11. Cost boundary

The construction is exact, but the materialized objects cost

```text
J_G coefficients       h+1       =Theta(n),
A_G coefficients       at most M+1,
B_G coefficients       at most M-1,
combined trace pair     at most 2M=n-1 field elements.
```

Therefore the explicit construction fails the representation gate. No public
sub-square-root evaluator is claimed.

The remaining compiler target is now exact:

```text
Given public (E,G,Q), evaluate A_G(x(Q)) and B_G(x(Q)) from (C3.12)
without materializing J_G, A_G, B_G, or a degree-n quotient algebra.          (C3.22)
```

## 12. Connection to B3 and C2

B3 compactly exposes the full unoriented kernel norm through `Frob-id` but does
not select a branch. C3 supplies a distinguished Pell factorization whose norm
contains that full kernel:

```text
norm(A_G+YB_G)=c_G K_H(X)(X-r)^M.
```

C2 expresses parity as an `n`-state translation resolvent. C3 compresses the
description of the desired output to one quadratic trace/norm pair, but not yet
its evaluation cost.

The next constructive question is:

```text
Can the distinguished solution (A_G,B_G) of (C3.16), selected by divisor
(C3.8), be evaluated at one public x-coordinate below n^(1/2-epsilon) using the
compact Frob-id kernel map, modular composition, or a square-root-Velu index
system, without expanding the quarter-kernel?                                (C3.23)
```

A positive answer immediately instantiates the central evaluator through
`(C3.18)`.

## 13. Formalization boundary

`Ecdlp/Proved/OrientedHalfDivisorTraceEvaluator.lean` kernel-checks the
conjugate product, Pell specialization at a kernel root, square-one output, the
two branch-to-sign implications, sign covariance, and the algebraic bridge from
`Y_G A_G+(X^3+7)B_G=0` to the evaluator ratio.

It does not formalize elliptic curves, divisor equality `(C3.8)`, the polynomial
construction `(C3.12)`, secp256k1, circuit complexity, or ECDLP.

## 14. Answer

```text
Exact translated half-divisor constructed?                yes
Exact quarter-kernel zero-test evaluator?                 yes
Exact rational trace-pair evaluator?                      yes
Correct G -> -G transformation?                           yes
Polynomial Pell norm identity?                            yes
Bridge to Y_G?                                            yes
Explicit representation below sqrt(n)?                   no
Compact evaluation of distinguished trace pair?          open
Public parity oracle satisfying full cost gate?           absent
Classical sub-sqrt ECDLP                                   absent
```
