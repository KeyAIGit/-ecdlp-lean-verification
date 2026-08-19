# UORC-056 Finite-Image Rational Degree Bound

## Status

Proved general algebraic-geometry boundary for exact finite-state rational observables on the subgroup.

This theorem is independent of the particular affine coordinate used to write the rational function.

## Setting

Let `C` be a smooth irreducible projective curve over a field, and let `H` be a set of `N` distinct points of `C` at which a rational function `R` is finite.

Assume that on `H`, the function takes values in a fixed finite set

`A={a_1,...,a_s}`

of size `s`.

Assume at least two values are actually required, so `R` is not the same constant on all target points.

Let `d` be the degree of the rational map `R:C->P^1`, equivalently the total pole degree of `R`.

## Theorem

If `R` is exact on all `N` target points, then

`d >= N/s`.

More precisely, `N <= s d`.

## Proof

Form the rational function

`F = product_{a in A} (R-a)`.

At every target point `P` in `H`, one factor vanishes because `R(P)` belongs to `A`. Hence `F` has at least `N` distinct zeros.

Each factor `R-a` has pole divisor of degree at most `d`. Therefore `F` has total pole degree at most `s d`.

For a nonzero rational function on a smooth projective curve, total zero degree equals total pole degree. Thus

`N <= s d`.

The only alternative is that `F` is identically zero in the function field. Because the function field is an integral domain, one factor `R-a` must then be identically zero, making `R` constant. That cannot realize two or more required output classes.

Therefore `d >= N/s`.

## Exact parity consequence

For a direct sign decoder, `A={+1,-1}` and `s=2`. On a prime-order subgroup of size `n`, any rational function satisfying

`R([k]G)=(-1)^k`

for every canonical scalar must have

`deg R >= n/2`.

For secp256k1 this is exponential in the 256-bit input length.

## Joint four-state consequence

For the joint classifier

`W_G in {-3,-1,1,3}`,

we have `s=4`. Any direct rational function whose value is exactly `W_G` on all subgroup points must have

`deg R >= n/4`.

Thus combining the GLV carry and Kummer sector into four output states does not create a low-degree rational observable.

## General finite-state consequence

A rational state taking at most `poly(log n)` distinct values still requires degree at least

`n/poly(log n)`.

Therefore a polynomially bounded finite output alphabet cannot by itself yield a low-degree exact rational representation.

## What the theorem closes

- direct low-degree rational parity decoders on the elliptic curve;
- direct low-degree rational four-state `W_G` decoders;
- any exact finite-image rational observable with degree `poly(log n)` and only `poly(log n)` output values.

## What remains open

The theorem is a degree bound, not an arithmetic-circuit lower bound. It does not exclude:

- a degree approximately `n` function evaluated by a short straight-line program;
- applying a character, trace, branch selector, or nonlinear decoder to a field-valued rational state;
- modular composition or repeated-squaring representations;
- query-dependent CM/Miller/theta/p-adic states;
- states with exponentially many possible field values but only polynomial description length.

Any positive route must therefore exploit high-degree low-circuit complexity or leave the direct finite-image rational model.
