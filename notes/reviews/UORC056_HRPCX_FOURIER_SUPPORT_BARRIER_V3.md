# UORC-056 H-RPCX Fourier-support barrier V3

## Purpose

V1 excludes a linear readout from a small translation-stable linear state.
V3 allows a nonlinear polynomial readout and gives the exact spectral budget it must satisfy.

## Setup

Work on an odd cyclic group `C_n`. Over a splitting field, translation diagonalizes into the `n` cyclic characters.

Assume a public state is contained in a translation-stable linear module whose set of Fourier frequencies is `A`, with `|A| = r`.

Let the final decoder be a polynomial of total degree at most `d` in the state coordinates.

## Theorem

The Fourier support of the decoded function is contained in

`0A union 1A union ... union dA`,

where `jA` is the set of sums of `j` frequencies from `A`, with repetition allowed.

Therefore its support size is at most

`binomial(r+d, d)`.

Canonical parity on an odd cycle has nonzero Fourier coefficient at every one of the `n` frequencies. Hence every exact decoder of this form must satisfy

`binomial(r+d, d) >= n`.

## Proof that parity has full Fourier support

Let `zeta` be an `n`-th root of unity and fix a frequency `t`. The Fourier coefficient is

`sum_{k=0}^{n-1} (-1)^k zeta^(-t k)`.

This is a geometric sum with ratio `-zeta^(-t)`. Since `n` is odd, its numerator is `2`, and since an odd-order root of unity is never `-1`, its denominator is nonzero. Explicitly the coefficient equals

`2 / (1 + zeta^(-t))`.

It is therefore nonzero at every frequency.

## Consequences

A constant number of translation eigenmodes followed by a constant-degree polynomial decoder cannot compute exact parity for a growing family.

More generally, a proposed H-RPCX state with `r` spectral modes and decoder degree `d` is rejected whenever

`binomial(r+d,d) < n`.

This is an exact theorem, not a heuristic rank test.

## Scope

V3 does not exclude:

- polynomial degree growing with `log n` fast enough to satisfy the binomial bound;
- arithmetic circuits whose formal degree is exponential in circuit depth;
- nonlinear state evolution that is not contained in a small translation-stable linear module;
- branch operations, characters, theta functions, or p-adic transports outside polynomial readout.

The result is a quantitative admission gate. It prevents the engine from treating a small constant-degree nonlinear readout as a plausible escape from V1.