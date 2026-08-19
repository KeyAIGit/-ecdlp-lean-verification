# UORC-056 Exact Rational Degree in a Cyclic Character Coordinate

## Status

Proved optimal degree in the idealized model where the scalar position is represented by one primitive additive character.

This is a representation-class theorem, not a public secp256k1 algorithm: efficiently obtaining the character value from `Q=[k]G` would itself be a discrete-logarithmic task.

## Setting

Let `n` be odd and let `omega` be a primitive `n`-th root of unity over a field of characteristic not equal to `2` and not dividing `n`.

Encode the scalar position `k` by

`z_k = omega^k`.

We seek a rational function

`R(z)=A(z)/B(z)`

such that:

- `B(z_k)` is nonzero for every `k`;
- `R(z_k)=+1` when `k` is even;
- `R(z_k)=-1` when `k` is odd.

Let `d=max(deg A, deg B)`.

## Lower bound

There are `(n+1)/2` even canonical representatives and `(n-1)/2` odd representatives.

At every even point,

`A(z_k)-B(z_k)=0`.

Thus the polynomial `A-B` has `(n+1)/2` distinct roots.

If `d<(n+1)/2`, then `A-B` must be the zero polynomial, so `A=B` identically.

But then `R(z)=1` at every point where `B` is nonzero, contradicting the required value `-1` at every odd point.

Therefore

`d >= (n+1)/2`.

## Matching construction

Define the two root products

`E(z) = product over even k of (z-z_k)`,

`O(z) = product over odd k of (z-z_k)`.

Their degrees are `(n+1)/2` and `(n-1)/2` respectively.

Set

`R(z) = (O(z)-E(z)) / (O(z)+E(z))`.

At an even point, `E=0` and `O` is nonzero, so `R=+1`.

At an odd point, `O=0` and `E` is nonzero, so `R=-1`.

The denominator is nonzero at every target point. The construction has degree `(n+1)/2`, exactly matching the lower bound.

Hence the minimal rational degree is

`(n+1)/2`.

## Meaning

Even after the scalar is idealized as one root of unity, an ordinary low-degree rational formula cannot decode canonical parity. The optimal rational representation explicitly separates the cycle into its even and odd halves.

For a 256-bit prime order, the required degree is of size approximately `2^255`, not `poly(256)`.

This is a degree and representation-size boundary, not a general arithmetic-circuit lower bound. A polynomial of enormous degree can sometimes have a short repeated-squaring circuit.

## Computational obstruction exposed by the construction

The matching decoder is controlled by the two half-orbit products `E` and `O`. Therefore a positive result in this model would have to compute their ratio or an equivalent half-cycle product without materializing approximately `n/2` factors.

This identifies a precise remaining mechanism:

- a short product recursion;
- a divide-and-conquer segment primitive;
- a modular-composition identity;
- a theta or elliptic-unit product formula;
- another high-degree, low-circuit representation.

Absent such compression, the exact rational decoder has exponential description or evaluation cost.

## Consequences for H-PCX

Closed:

- one-character rational decoders of degree `poly(log n)`;
- claims that the cyclic parity table has a low-degree rational interpolation;
- sparse low-degree numerator/denominator descriptions in the character coordinate.

Not closed:

- high-degree rational functions with short straight-line programs;
- nonlinear multi-state representations;
- public coordinate-specific secp256k1 constructions;
- compressed evaluation of the half-orbit products.
