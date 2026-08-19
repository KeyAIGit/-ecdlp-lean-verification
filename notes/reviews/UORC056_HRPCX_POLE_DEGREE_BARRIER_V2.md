# UORC-056 H-RPCX pole-degree barrier V2

## Status

This note closes a second H-RPCX architecture: a low-pole-degree algebraic state followed by a low-degree polynomial readout.

It does not give an arithmetic-circuit lower bound. High-degree functions computed by short straight-line programs remain open.

## Setup

Let `E` be a smooth projective curve over a field of characteristic different from `2`. Let `H*` be a finite set of `N` points. Let

`target : H* -> {+1,-1}`

be nonconstant.

Suppose a rational function `f` is regular on every point of `H*` and satisfies

`f(P) = target(P)`

for every `P in H*`.

Write `deg_poles(f)` for the total degree of the pole divisor of `f`.

## Exact theorem

Every such `f` satisfies

`deg_poles(f) >= N/2`.

For the nonzero points of an odd prime-order subgroup, `N = n-1`. Therefore

`deg_poles(f) >= (n-1)/2`.

For secp256k1 this lower bound is exponential in `log2 n`.

## Proof

Consider

`h = f^2 - 1`.

At every point of `H*`, the value of `f` is either `+1` or `-1`, so `h` vanishes. Therefore `h` has at least `N` zeros, counted without multiplicity.

The target is nonconstant, so `f` is neither the constant function `+1` nor the constant function `-1`. Because a function field is an integral domain, `f^2 - 1` is not identically zero.

For every nonzero rational function on a smooth projective curve, the total degree of its zero divisor equals the total degree of its pole divisor. The poles of `f^2 - 1` are bounded by twice the pole divisor of `f`. Hence

`N <= deg_zeros(h) = deg_poles(h) <= 2 deg_poles(f)`.

This gives the claimed lower bound.

## State plus polynomial decoder

Suppose public state coordinates `S_1,...,S_r` all have poles bounded by one effective divisor `D_0`. Let a polynomial decoder `D` have total degree `d`, and put

`f = D(S_1,...,S_r)`.

Then the poles of `f` are bounded by `d D_0`. Consequently,

`d * deg(D_0) >= N/2`.

Therefore an H-RPCX proposal cannot have all three properties simultaneously:

1. `deg(D_0) = poly(log n)`;
2. decoder degree `d = poly(log n)`;
3. exact parity on all nonzero subgroup points.

## Meaning for the engine

Reject a candidate if its full exact decoder reduces to a rational function with proven pole budget `o(n)`.

Do not reject a candidate merely because its resulting rational function has huge degree. A huge degree can sometimes be produced by a short circuit, for example by repeated squaring.

The surviving class must contain at least one of the following:

- a high-degree state produced by a low-size circuit;
- a high-degree decoder produced by a low-size circuit;
- a branch, character, theta, p-adic, or other operation not represented by a low-pole-degree rational function;
- a global transport mechanism whose complexity is small even though its algebraic degree is exponential.

## Relation to V1

V1 excludes low-dimensional linear translation-stable modules.

V2 excludes low-pole-degree algebraic states with low-degree polynomial readout.

Together they force the positive search toward the only still plausible compression regime:

`high algebraic degree + low arithmetic-circuit size + exact public branch selection`.
