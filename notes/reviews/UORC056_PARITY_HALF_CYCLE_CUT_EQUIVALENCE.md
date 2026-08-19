# UORC-056 Parity Equals a Canonical Half-Cycle Cut

## Status

Proved exact reformulation for every odd-order cyclic group.

## Statement

Let `n` be odd and let `Q=[k]G` with canonical scalar `0<=k<n`.

Let `inv2` be the public inverse of `2` modulo `n`, and define

`R=[inv2]Q=[r]G`,

where `0<=r<n` is canonical.

Then:

- if `k` is even, `r=k/2`, so `r< n/2`;
- if `k` is odd, `r=(k+n)/2`, so `r> n/2`.

Therefore exact parity is equivalent to deciding whether the canonical scalar of `R` lies in the lower or upper half of the cycle.

## Proof

Because `2r` is congruent to `k` modulo `n` and both lie between `0` and `2n-2`, only two equalities are possible:

`2r=k`

or

`2r=k+n`.

In the first case, `k` is even and `r=k/2` lies in the lower half.

In the second case, `k+n` is even. Since `n` is odd, this means `k` is odd, and `r=(k+n)/2` lies in the upper half.

Conversely, each half forces the corresponding equality and parity.

## Meaning

Canonical parity is not a local two-coloring of the abstract odd cycle. It is a question about which side of one globally chosen cut the halved point occupies.

This explains the unique seam seen in the full-shift theorem:

- the group law knows the cycle;
- canonical parity additionally chooses an origin and a linear order `0,1,...,n-1`;
- the algorithm must recover the side of that hidden order cut from public coordinates.

## Consequences

A successful evaluator can be described equivalently as any of the following:

- an exact parity oracle;
- an exact lower-half versus upper-half oracle after public halving;
- a public canonical-order cut detector;
- a mechanism that detects whether modular division by two wrapped through `n`.

The GLV carry and Kummer-sector decompositions are specialized manifestations of the same global wrap information.

## Research implication

The engine should test candidate states for exact cut detection, not only correlation with alternating signs. A local invariant that is unchanged under moving the cut cannot solve the problem. Positive candidates must introduce a public orientation or ordering mechanism tied to `G` and to the canonical representative convention.
