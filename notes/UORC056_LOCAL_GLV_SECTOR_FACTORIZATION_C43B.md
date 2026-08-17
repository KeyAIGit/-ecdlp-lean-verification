# UORC-056 C43B: local GLV carry and ordered-sector factorization

Date: 2026-08-17

Status: exact algebraic factorization verified on five frozen and four independently checked held-out prime-order `j=0` curves. The package does not produce a cheap parity evaluator.

## 1. Target

Let

\[
E: y^2=x^3+7,
\qquad
Q=[k]G,
\qquad
Y_G(x(Q))=(-1)^k y(Q).
\]

Let the order-three GLV endomorphism be

\[
\phi(x,y)=(\beta x,y),
\qquad
\phi(G)=[\lambda]G,
\qquad
\lambda^2+\lambda+1\equiv0\pmod n.
\]

C42 showed that the cubic GLV norm reduces the representation dimension but does not select the missing orientation. C43B resolves the exact local algebra left inside one GLV orbit.

## 2. Three signs in one GLV orbit

For a nonzero scalar class define

\[
s_0(k)=(-1)^k,
\qquad
s_1(k)=(-1)^{[\lambda k]_n},
\qquad
s_2(k)=(-1)^{[\lambda^2k]_n}.
\]

Because

\[
k+[\lambda k]_n+[\lambda^2k]_n\in\{n,2n\},
\]

the product

\[
g_G(k)=s_0(k)s_1(k)s_2(k)
\]

is a public two-sector carry sign once its oriented root is known.

Define the GLV-invariant coordinate

\[
T=X^3.
\]

The half-kernel polynomial factors through it:

\[
\boxed{K_H(X)=\kappa(T)=\kappa(X^3).}
\]

## 3. Exact carry root

Define

\[
\boxed{
C_G(T)=Y_G(X)Y_G(\beta X)Y_G(\beta^2X),
\qquad T=X^3.
}
\]

At a point \(Q=[k]G\), the three `y` coordinates are equal, hence

\[
C_G(x(Q)^3)=g_G(k)y(Q)^3.
\]

The exact quotient-ring square identity is

\[
\boxed{
C_G(T)^2=(T+7)^3\pmod{\kappa(T)}.
}
\]

This is a dimensional compression by a factor of three, but it retains only the product of the three local signs.

## 4. Ordered-sector root

Define

\[
\boxed{
J_G(X)=\frac{Y_G(\beta X)Y_G(\beta^2X)}{X^3+7}
\pmod{K_H(X)}.
}
\]

At \(Q=[k]G\),

\[
J_G(x(Q))=s_1(k)s_2(k).
\]

Therefore

\[
\boxed{J_G(X)^2=1\pmod{K_H(X)}}
\]

and

\[
\boxed{
Y_G(X)(X^3+7)=C_G(X^3)J_G(X)\pmod{K_H(X)}.
}
\]

The parity bit becomes

\[
\boxed{
(-1)^k=g_G(k)J_G(x(Q)).
}
\]

This is the strongest exact local normal form found in the GLV line so far.

## 5. Why the cubic norm is insufficient

Fixing the product

\[
s_0s_1s_2=g
\]

leaves four sign triples. They form a Klein-four torsor under even sign flips. A cyclic norm, symmetric product, determinant built from neutral entries, or closed GLV loop sees the product but cannot identify the ordered first sign \(s_0\).

Thus the remaining object is not another norm. It is an ordered, unsquared sector transport that selects

\[
J_G(x(Q))=s_1s_2.
\]

In the gauge language of C43, this object has nonzero endpoint charge.

## 6. Exact corpus

The replay uses the inherited five frozen rows and four held-out rows independently checked for curve order, generator order, cube-root action, and GLV eigenvalue:

| p | n | G | beta | lambda |
|---:|---:|---:|---:|---:|
| 61 | 61 | (2,25) | 13 | 47 |
| 211 | 199 | (3,33) | 14 | 106 |
| 991 | 1009 | (1,151) | 113 | 634 |
| 2089 | 2143 | (1,777) | 1262 | 1793 |

Across all nine curves, the replay verifies:

```text
1,923 pointwise carry and reconstruction checks
K_H(X)=kappa(X^3)
Y_G(X)^2=X^3+7 mod K_H
C_G(T)^2=(T+7)^3 mod kappa
J_G(X)^2=1 mod K_H
Y_G(X)(X^3+7)=C_G(X^3)J_G(X) mod K_H
G reversal negates Y_G and C_G
0 arithmetic errors
```

Certificate digest:

```text
825dfe1107116fc8f6e64e357e434254dc1200f15118b13349262a9f15e7d601
```

## 7. Fixture audit

An earlier unverified branch draft included three alleged held-out rows that did not satisfy the declared curve and point contracts. The first independent CI replay exposed the failure. Those rows, their DFT screen, their aggregate claims, and their tests were deleted rather than repaired in place.

C43B makes no character-grammar or DFT closure claim. Only the exact factorization above survives the audit.

## 8. secp256k1 frontier

For the secp256k1 subgroup order,

\[
\deg K_H=\frac{n-1}{2},
\qquad
\deg \kappa=\frac{n-1}{6}.
\]

The GLV quotient therefore still contains

\[
\frac{n-1}{6}
\]

orbits, a 254-bit-scale object. The factor-of-three compression is exact but not asymptotically sufficient.

## 9. Successor problem C44

The next target is

\[
\boxed{
\text{a public unsquared evaluator for }J_G(x(Q)).
}
\]

It must satisfy all of the following gates:

1. distinguish the residual Klein-four sector gauge;
2. remain generator-marked and ordered;
3. avoid enumerating the \((n-1)/6\) GLV quotient roots;
4. avoid hiding an order-\(n\) table in advice or coefficients;
5. expose a circuit, recurrence, transfer law, or local functional equation whose total charged cost is explicit.

The leading candidate languages are open GLV transport, a marked nonhomomorphic p-adic polylogarithmic specialization, and a local functional equation coupling the three ordered GLV sectors.

## 10. Claim boundary

C43B does not claim:

- a numerical evaluator for `J_G(x(Q))`;
- a parity oracle;
- a sub-square-root ECDLP algorithm;
- an unrestricted impossibility theorem for all GLV constructions;
- a character-grammar closure;
- that factor-three dimensional compression is computationally sufficient.
