# Square-class circuit frontier

Date: 2026-08-12

Status: **structural reduction after linear-state, rational-degree, one-addition, nested two-addition, and translated mixed-weight coordinate gates; no general circuit lower bound and no decoder**.

## Exact target

The target remains

```text
g_G(Q)=g_G(G)*sign(U_G(Q)),
```

or any publicly equivalent exact output `R3_G(Q)` or `h_G(x(Q)^3)`.

## Completed coordinate gates

```text
one-addition monomial class:
  complete medium exhaustion, zero exact decoders;

nested two-addition quotient and direct-character profiles:
  156,114,321,336 nominal exact formula evaluations,
  zero exact decoders;

same-feature cubic GLV orbit product:
  exact collapse to one-addition square class.
```

## Translated mixed-weight determinant

For the first public translated characteristic

```text
M_ij(Q,R)=x(phi^i Q + phi^j R),
```

the matrix is C3-circulant after public row scaling. Its DFT decomposition has one exact-square component. The anti-Kummer plus/minus determinant reduces, modulo a square denominator and public constants, to

```text
y(Q)*x(Q)^3*R4(X^3,x(Q)^3;7),
```

where `R4` has degree four in the quotient coordinate. Thus the natural translated determinant returns to a low-degree direct coordinate square class.

A scalar pullback only permutes Fourier frequencies, so a single pulled-back copy cannot amplify the base spectrum into carry.

The stronger exact pencils

```text
F([m]Q)+c*G([ell]Q)
```

were exhausted over all nonzero `m,ell`, all `c`, and nine declared component pairs on the medium groups of orders 271 and 433:

```text
nominal exact formula instances: 1,637,634,348
exact carry decoders:            0
```

This is bounded toy evidence, not a secp256k1 impossibility theorem.

## Current frontier

The bounded-pole translated-coordinate realization of mixed weights is no longer the priority. A new survivor must leave the common bounded-pole coordinate category, most naturally through genuinely different theta characteristics or a Heisenberg/metaplectic intertwiner.

Immediate rejection tests:

1. one common theta basis factors into a multiplicative net ratio;
2. scalar row rescaling contributes only the supplied row-factor product;
3. translated `x/y` characteristics collapse after C3 diagonalization;
4. one scalar pullback only permutes Fourier magnitudes;
5. fitted coefficients, dual-orbit orientation, or label tables are hidden advice.

## Current answer

```text
Low-degree rational-character decoder                     excluded
Explicit translation-linear state                         excluded
Complete medium one-addition monomial class               zero decoders
Structured nested two-addition profiles                   zero decoders
Translated mixed-weight determinant                       low-degree collapse
Complete declared two-pullback mixed pencils              zero decoders
Genuinely twisted theta/Heisenberg characteristic          open
Canonical p-adic/analytic orientation circuit             open
Public carry or hard-R3 decoder                            absent
Classical sub-square-root ECDLP algorithm                  absent
```
