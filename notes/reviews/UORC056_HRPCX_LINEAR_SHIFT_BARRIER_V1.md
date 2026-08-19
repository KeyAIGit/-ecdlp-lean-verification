# UORC-056 H-RPCX linear-shift barrier V1

## Status

This note proves an exact negative theorem for one central H-RPCX route. It does **not** refute H-RPCX in general.

## Target

Let `C_n = <G>` be a cyclic group of odd order `n`. For the canonical representative `k in {0,...,n-1}`, define

`par(k) = (-1)^k`.

An H-RPCX candidate may try to place `par` inside a low-dimensional linear space of public functions that is stable under the public translation

`Q -> Q + G`.

The theorem below shows that this route cannot have dimension polynomial in `log n`.

## Exact theorem

Let `F` be any field in which `2 != 0`. Let `T` denote cyclic translation on functions on `C_n`:

`(T f)(k) = f(k-1 mod n)`.

Let `V` be an `F`-linear subspace of all functions `C_n -> F`. Assume:

1. `par` belongs to `V`;
2. `V` is stable under `T`.

Then

`dim_F(V) >= n`.

Since the ambient function space itself has dimension `n`, one in fact has `V = F^{C_n}`.

Therefore no state space of dimension `poly(log n)` can satisfy these assumptions for a growing odd-order family.

## Proof

Form the group-algebra element

`P(z) = 1 - z + z^2 - ... + z^(n-1)`

inside `F[z]/(z^n - 1)`.

Because `n` is odd, the last sign is positive. Hence

`(1 + z) P(z) = 1 + z^n`.

In the quotient, `z^n = 1`, so

`(1 + z) P(z) = 2`.

Since `2` is invertible in `F`, `P(z)` is invertible, with explicit inverse

`P(z)^(-1) = (1 + z)/2`.

The circulant matrix whose columns are the cyclic shifts

`par, T par, ..., T^(n-1) par`

is exactly convolution by `P`. Because `P` is invertible, that matrix has rank `n`. Thus all `n` cyclic shifts of parity are linearly independent.

Any `T`-stable linear space containing `par` contains all these shifts. It must therefore have dimension at least `n`.

## Equivalent linear-recurrence statement

The periodic parity word on an odd cycle has cyclic linear complexity exactly `n` over every field of characteristic different from `2`.

Consequently, no linear recurrence of width `poly(log n)` can generate exact canonical parity around the whole odd cycle.

## Consequence for H-RPCX

The following candidate architecture is closed:

1. a state vector with `d = poly(log n)` field coordinates;
2. translation by `G` represented by a linear update of that state;
3. parity obtained by a linear readout;
4. exact correctness for every point in the odd-order group.

It is also closed if the proposal is phrased as a low-dimensional translation-stable linear feature module containing parity.

For secp256k1, `n` is approximately `2^256`, so the required linear dimension is approximately `2^256`, not a polynomial in `256`.

## What remains open

This theorem does not exclude:

- nonlinear state updates;
- nonlinear readout from a small state;
- a state that is not closed under `Q -> Q + G`;
- high-degree functions with low arithmetic-circuit size;
- theta, CM, Miller, p-adic, or modular-composition constructions with a genuinely nonlinear branch transport;
- a direct evaluator that computes parity without materializing a translation-stable linear module.

These are the only classes that should continue in the H-RPCX search after V1.

## Existence-level equivalence

A uniform H-PCX or H-RPCX theorem with public `poly(log n)` state construction and public `poly(log n)` exact decoding immediately gives a classical polynomial-time parity algorithm by composition.

An exact parity algorithm gives full ECDLP by repeated bit peeling:

1. read the current parity;
2. subtract `G` if the current scalar is odd;
3. multiply by the public inverse of `2` modulo `n`;
4. repeat for at most `ceil(log2 n)` steps.

Conversely, a polynomial-time ECDLP algorithm gives parity immediately.

Thus, at the uniform polynomial-time level,

`H-RPCX existence <=> exact parity in polynomial time <=> ECDLP in polynomial time`.

A nonconstructive proof of H-RPCX may be shorter in presentation than an explicit algorithm, but it is not a weak result. It proves the existence of a classical polynomial-time ECDLP method for the family.

## Engine rule introduced by V1

Reject any future candidate as soon as all three conditions hold:

1. its exact parity readout is linear;
2. its feature space is linear and stable under translation by `G`;
3. the claimed dimension is `o(n)`.

The rejection is theorem-backed and requires no toy-curve search.