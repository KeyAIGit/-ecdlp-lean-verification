# UORC-056 Exact Parity Has Full Cyclic Shift Span

## Status

Proved algebraic boundary for the linear translation-stable version of H-PCX.

This result does **not** refute nonlinear polynomial-time parity algorithms. It closes the most direct low-rank/stable-module route in which exact parity is placed inside a linear space of functions that is invariant under translation `Q -> Q + G`.

## Setting

Let `n` be odd. Index the cyclic subgroup by the canonical scalars

`0,1,...,n-1`.

Define the exact parity sign

`f(k)=+1` for even `k`, and `f(k)=-1` for odd `k`.

Let `T` be cyclic translation by one scalar:

`(T f)(k)=f(k-1 mod n)`.

Let `delta_0` be the point-indicator function: it is `1` at scalar `0` and `0` everywhere else.

## Seam identity

For every nonzero canonical scalar `k`, the integers `k` and `k-1` have opposite parity, so

`f(k)+(T f)(k)=0`.

At `k=0`, cyclic translation reads the previous canonical scalar as `n-1`. Since `n` is odd, `n-1` is even, hence

`f(0)+(T f)(0)=1+1=2`.

Therefore, exactly as functions on the odd cycle,

`(I+T)f = 2 delta_0`.

This is the algebraic form of the unique wrap-around seam in an alternating sign pattern on an odd cycle.

## Full-span theorem

Work over any coefficient field in which `2` is invertible.

Let `V` be a linear subspace of all functions on the subgroup. Assume:

1. `f` belongs to `V`;
2. `V` is invariant under `T`.

Then `T f` belongs to `V`, so the seam identity implies `delta_0` belongs to `V`.

Applying `T` repeatedly gives every point indicator

`delta_j = T^j delta_0`.

The `n` point indicators form a basis of the complete function space. Hence

`V` is the complete `n`-dimensional function space.

Equivalently, the `n` cyclic shifts

`f, T f, T^2 f, ..., T^(n-1) f`

are linearly independent and form a basis.

## Explicit inverse transform

Let `C` map the point-indicator basis to the shifted-parity basis:

`C(delta_j)=T^j f`.

Because `C` commutes with `T`, the seam identity gives

`(I+T) C = 2 I`.

Therefore

`C^(-1) = (I+T)/2`.

So the full-span statement is not merely existential: the inverse of the parity-shift circulant is a local two-term operator. In particular, over characteristic different from `2`, the circulant is invertible and its determinant has absolute value `2^(n-1)`.

## Corollary 1: no short cyclic linear recurrence

Suppose exact parity satisfied a nonzero constant-coefficient cyclic linear recurrence of order `r<n`:

`a_0 f + a_1 T f + ... + a_r T^r f = 0`.

This would be a linear dependence among fewer than `n` members of the shifted-parity basis, contradicting the full-span theorem.

Therefore the minimal constant-coefficient cyclic linear recurrence order is `n`. A recurrence of width `poly(log n)` cannot generate exact parity under fixed translation.

## Corollary 2: full additive Fourier support

Over a splitting field containing the `n`-th roots of unity, translation is diagonalized by the additive characters of the cyclic group.

If any Fourier coefficient of parity were zero, the cyclic span would omit that character eigenspace and have dimension smaller than `n`. Since the cyclic span is complete, every one of the `n` additive Fourier coefficients is nonzero.

Equivalently, exact canonical parity cannot be expressed as a sum of only `poly(log n)` additive group characters. All `n` characters are required in this linear representation.

The coefficient at frequency `j` can also be evaluated directly as a finite geometric sum. Its numerator is `2`, and its denominator cannot vanish because an odd-order group has no character value equal to `-1`.

## Consequence for H-PCX

There is no `poly(log n)`-dimensional **linear** function space which simultaneously:

- contains exact canonical parity;
- is invariant under the public translation `Q -> Q+G`.

Its dimension must be exactly `n`, which is exponential in `log n`.

Thus the following candidate proof strategies are closed:

- a low-rank matrix built from every additive translate of exact parity;
- a small linear module containing parity and closed under addition of `G`;
- a bounded-dimensional constant-coefficient linear recurrence generating exact parity;
- a sparse decomposition into additive group characters.

## What remains open

The theorem does not exclude:

- nonlinear states or nonlinear decoders;
- representations not closed under `Q -> Q+G`;
- short arithmetic circuits whose intermediate functions do not lie in one small translation-stable linear space;
- modular-composition, theta, CM, p-adic, or branch-transport constructions with nonlinear dynamics;
- a direct evaluator specialized to coordinates of secp256k1.

## Interpretation

On an even path, the alternating signs look locally simple. On an odd cycle, the wrap-around creates one exceptional seam. Adding the parity pattern to its one-step shift isolates that seam as a single point. Once a translation-stable linear system can isolate one point, it can translate that point around the entire group and therefore reconstruct every possible table entry.

The exact parity function is therefore maximally noncompressible inside the linear translation-stable model, even though it has a very short verbal definition.
