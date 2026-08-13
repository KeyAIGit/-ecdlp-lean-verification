# Parity phase chain checkpoint through package 035

Date: 2026-08-12

Branch: `research/direct-glv-carry-descent-010`

Synchronized research PR: `#373`, based on `research/parity-lift-000`

## One-line objective

Given public

```text
E, G, Q=[k]G,
```

compute one exact generator-relative bit with total cost below `sqrt(n)`.

## Exact reduction chain

```text
hard R3_G(Q)
    <-> GLV carry g_G(Q), using public C3_G(Q)=g_G(Q)R3_G(Q)

GLV carry
    = orientation of eta_G(Q)
    = g_G(G)*sign(U_G(Q))
```

where

```text
eta_G([k]G)=zeta_n^k+zeta_n^(lambda*k)+zeta_n^(lambda^2*k),
A_G(Q)=eta_G(Q)-conjugate(eta_G(Q)),
U_G(Q)=A_G(Q)/A_G(G).
```

## Canonical packages 032 and 033 on the parent branch

The parent parity branch records:

```text
NORMALIZED-PERIOD-BLACKBOX-032:
  exact bounded-rank pairing formula for U_G after a dual n-torsion orbit is supplied;

DUAL-C3-ORBIT-SELECTOR-033:
  standard CM/Frobenius data do not compactly select the required dual orbit;
  a nonzero dual point needs extension degree (n-1)/6 and a +/-C3 orbit needs (n-1)/12.
```

These packages identify the missing dual-orbit orientation but do not provide a public carry decoder.

## Package 035: linear-state barrier

The normalized period also has an exact order-six recurrence over its splitting coefficient field. If

```text
s=zeta+zeta^lambda+zeta^(lambda^2),
t=zeta^(-1)+zeta^(-lambda)+zeta^(-lambda^2),
```

then the characteristic polynomial is

```text
(X^3-sX^2+tX-1)(X^3-tX^2+sX-1).
```

The short recurrence is not a compact public evaluator. Let

```text
d=ord_n(p),
m_e=d/gcd(d,e),
C6={+/-1,+/-lambda,+/-lambda^2}.
```

The exact minimum linear recurrence rank over `F_(p^e)` is

```text
r_e=|C6*<p^e>|.
```

For secp256k1,

```text
e*r_e >= 3*d=(n-1)/2.
```

Even if the final readout is arbitrary nonlinear, any explicit state in
`(F_(p^e))^r` updated linearly under `Q -> Q+G` satisfies

```text
e*r >= d=(n-1)/6.
```

Thus the rank-six recurrence merely moves complexity into an extension of degree `d/2=(n-1)/12`.

## Frozen replay

```text
frozen cases:                                 15
cyclic recurrence checks:                     14,313
exact Frobenius rank/degree checks:            12,401
secp256k1 subgroup enumeration:                none
```

## Current answer

```text
Exact normalized carry observable                         found
Exact bounded-rank pairing formula with dual input         found
Compact public dual-orbit selector                         absent
Exact order-six splitting-field recurrence                 found
Compact finite-field linear recurrence                     excluded
Compact finite-field translation-linear state              excluded
Direct nonlinear public coordinate evaluator               absent
Universal nonlinear circuit lower bound                    absent
Unconditional classical sub-sqrt ECDLP algorithm           absent
```

## Next package

```text
RATIONAL-CHARACTER-DEGREE-BARRIER-036
```

It attacks the first broad direct-coordinate subclass:

```text
Q -> chi(f(Q)),
```

where `f` is a rational function on the elliptic curve. The goal is an asymptotic degree barrier, not another bounded formula screen.
