# UORC-056 H-PCX Complexity Equivalence

## Status

Proved logical equivalence. This note corrects the interpretation of H-PCX as a substantially weaker existence target.

## Definitions

For a uniform family of odd prime-order cyclic elliptic-curve groups, let `Parity(E,G,Q)` denote exact canonical scalar parity for `Q=[k]G`, `0<=k<n`.

H-PCX requires:

- a public state map `S(E,G,Q)` of size `poly(log n)`;
- construction of `S` in `poly(log n)` time and memory;
- a public exact decoder `D(E,G,S)` in `poly(log n)` time;
- no superpolynomial advice, preprocessing, representation, precision, or branch cost.

## Theorem 1: H-PCX is equivalent to polynomial-time exact parity

### H-PCX implies a parity algorithm

Given `E,G,Q`, compute `S(E,G,Q)` and then compute `D(E,G,S)`. The total of two polynomial costs is polynomial. Exactness of `D` gives exact canonical parity.

### A parity algorithm implies H-PCX

Assume a public polynomial-time exact parity algorithm `A(E,G,Q)` exists. Choose the state to be the public input point itself:

`S(E,G,Q)=Q`.

The state uses a constant number of field elements, is already public, and is constructible at constant cost. Define

`D(E,G,S)=A(E,G,S)`.

Then every H-PCX requirement is satisfied.

Therefore H-PCX is not merely a precursor to a polynomial parity algorithm. As presently quantified, it is exactly another formulation of one.

A nonconstructive proof of H-PCX could precede an optimized implementation, but it would already prove membership in classical polynomial time.

## Theorem 2: exact parity is polynomial-time equivalent to ECDLP

### ECDLP implies parity

Recover the canonical scalar `k` and return whether it is even.

### Parity implies ECDLP

Let `Q_0=Q=[k_0]G`. At step `i`, query exact parity and obtain the least significant bit `b_i` of the current canonical scalar `k_i`.

Remove that bit from the point:

`Q_i - [b_i]G = [k_i-b_i]G`.

The remaining scalar is even. Since `n` is odd, `2` is invertible modulo `n`; multiply the point by the public inverse of `2`:

`Q_{i+1}=[(k_i-b_i)/2]G`.

Thus `k_i=2 k_{i+1}+b_i`. Repeating for at most `ceil(log2 n)` steps recovers every binary digit of `k`.

The reduction uses only polynomially many group operations and parity queries.

Hence, for the family,

`H-PCX  <=>  exact parity in P  <=>  ECDLP in P`.

## Position of H-RPCX

H-RPCX additionally requires the state or decoder to be recoverable from an effectively enumerable feature family by bounded search and exact identification. Therefore:

`H-RPCX => H-PCX`,

but the reverse implication is not known and need not hold for an arbitrary feature language.

H-RPCX is a stronger, not weaker, hypothesis.

## Consequence for theorem search

The engine must not label a proof of general H-PCX as an easier preliminary result. It would be a complete classical polynomial-time solution of the exact parity problem and therefore of ECDLP for the declared family.

The tractable intermediate targets are restricted structural theorems, for example:

- low rank within an explicitly defined matrix family;
- a bounded-width recurrence within an explicitly defined grammar;
- closure of a particular CM/Miller/theta state module;
- a circuit upper bound for a specified representation;
- a lower bound excluding one declared class.

Each restricted theorem must state exactly which model it covers and must not be promoted to general H-PCX without all full-cost obligations.
