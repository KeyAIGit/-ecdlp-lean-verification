# UORC-056 secp256k1 Pairing Embedding-Degree Boundary

## Status

Exact arithmetic certificate produced and independently replayable.

## Question

Could one map `Q=[k]G` through a Weil or Tate pairing into a multiplicative root-of-unity coordinate `z=omega^k`, and then decode canonical parity there?

Any finite-field pairing target containing the `n`-th roots of unity must contain a field `F_(p^K)` for which

`n | p^K-1`.

The least such `K` is the embedding degree

`K=ord_n(p)`.

## Exact result for secp256k1

For the secp256k1 field prime `p` and subgroup order `n`,

`ord_n(p)=(n-1)/6`

and therefore

`K = 19298681539552699237261830834781317975472927379845817397100860523586360249056`.

Its binary logarithm is approximately

`253.41503749927884`.

Thus `K` itself is of size about `2^253.4`.

## Certificate

The complete factorization used is

`n-1 = 2^6 * 3 * 149 * 631`

`      * 107361793816595537`

`      * 174723607534414371449`

`      * 341948486974166000522343609283189`.

All displayed factors are prime.

Let `K=(n-1)/6`. Exact modular exponentiation verifies

`p^K = 1 mod n`.

For every prime divisor `q` of `K`, exact modular exponentiation verifies

`p^(K/q) != 1 mod n`.

These are the standard complete witnesses that the multiplicative order is exactly `K`.

The script `scripts/uorc056_secp_embedding_degree.py` replays the factorization, primality checks, and all modular exponentiation witnesses.

## Consequence

A direct MOV-style or pairing-style transfer of the secp256k1 subgroup into a finite-field multiplicative group requires an extension whose degree is exponential in the 256-bit security parameter.

Representing one generic element of `F_(p^K)` requires `K` base-field coordinates before considering arithmetic cost. This already violates every polynomial-in-`log n` state, memory, and representation bound.

Therefore the following route is closed:

1. compute an ordinary finite-field pairing coordinate `omega^k` in a polynomial-size extension;
2. decode parity with a root-of-unity half-cycle formula.

The obstruction occurs before parity decoding: the required pairing target is exponentially large.

## What remains open

This does not exclude:

- pairings or reciprocity objects whose values remain in a compact symbolic representation rather than a generic `F_(p^K)` element;
- CM, theta, or elliptic-unit constructions that avoid materializing the embedding field;
- a coordinate-specific nonlinear state living entirely over `F_p`;
- non-pairing high-degree low-circuit evaluators.

Any proposed compact pairing route must explain how it avoids both the extension degree `K` and the information hidden in a generic target-field element.
