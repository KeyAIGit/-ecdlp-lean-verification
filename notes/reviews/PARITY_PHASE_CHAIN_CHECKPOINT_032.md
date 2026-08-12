# Parity phase chain checkpoint through package 032

Date: 2026-08-12

Branch: `research/direct-glv-carry-descent-010`

Synchronized research PR: `#373`, based on `research/parity-lift-000`

## One-line objective

Given public

```text
E, G, Q=[k]G,
```

compute one exact generator-relative bit with total cost below `sqrt(n)`.

## Exact chain through package 031

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

Packages 027 through 031 establish:

```text
kernel-only CM data are generator-blind;
standard theta splittings are trivial or full order-n characters;
carry is one Gaussian-period conjugation orientation;
Frobenius-invariant descent loses that orientation;
A_G(G) canonically normalizes the anti-Frobenius line.
```

## Package 032

The normalized period has an exact order-six recurrence over its splitting coefficient field. If

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
Exact order-six splitting-field recurrence                found
Compact finite-field linear recurrence                    excluded
Compact finite-field translation-linear state             excluded
Direct nonlinear public coordinate evaluator              absent
Universal nonlinear circuit lower bound                   absent
Unconditional classical sub-sqrt ECDLP algorithm          absent
```

## Next package

```text
NORMALIZED-PERIOD-NONLINEAR-CIRCUIT-033
```

Central question:

> Can `sign(U_G(Q))` be evaluated directly from public point coordinates by a uniform nonlinear arithmetic, theta/sigma, p-adic, analytic, or nonlocal EDS identity below the square-root baseline, without maintaining a translation-linear order-`n` state and without hiding a faithful dual character or `(n-1)/6` orientation table in constants?

The first gate is not another statistical screen. It is a classification of exact rational/algebraic coordinate circuits with the required generator covariance, GLV invariance, negation anti-invariance, uniform constant generation, and all-in cost.
