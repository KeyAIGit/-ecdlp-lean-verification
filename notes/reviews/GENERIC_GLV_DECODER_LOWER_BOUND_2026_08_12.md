# Generic-Group Lower Bound for Exact Reusable GLV Decoders

Date: 2026-08-12

Status: **scoped corollary; no non-generic lower bound claim**.

## Assumptions

Assume an exact reusable carry decoder `D` is itself a generic-group algorithm:
it receives only opaque encodings of `G`, `Q`, and group-operation access, and it
uses at most `T(n)` generic group operations per query.

Assume the registered chosen-multiplier/local sparse-Fourier reduction from an
exact carry oracle to ECDLP, with polynomial-logarithmic query and arithmetic
overhead.

## Reduction

For public multipliers `t`, the reduction forms

```text
[t]Q=[t*k]G
```

and queries

```text
D([t]Q)=g(t*k mod n).
```

The known constant-heavy spectrum of the scalar carry recovers a constant-size
candidate list containing `k` in the stated source-conditional local-SFT model.
Therefore the composed ECDLP algorithm uses

```text
poly(log n) * T(n) + poly(log n)
```

generic group operations.

## Lower bound consequence

Shoup's generic-group lower bound for discrete logarithms in a prime-order group
requires `Omega(sqrt(n))` generic group operations.  Hence the composed
algorithm implies

```text
T(n)=Omega(sqrt(n)/poly(log n)).
```

Thus an exact reusable sub-square-root decoder cannot be purely generic, apart
from possible polynomial-logarithmic factors in the stated reduction.

## Research consequence

Every admissible positive construction must exploit non-generic structure of
the secp256k1 representation, such as:

```text
field coordinates,
CM/GLV arithmetic,
nontrivial public field characters,
generator-sensitive theta/sigma data,
p-adic or analytic descent,
or another representation-specific identity.
```

Merely reorganizing generic group operations cannot produce the required
shortcut.

## Source and claim boundary

Primary lower-bound source:

Victor Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*,
EUROCRYPT 1997, LNCS 1233, pp. 256-266.

This note is conditional on the exact reusable decoder and the registered
local-SFT oracle reduction.  It does not rule out representation-specific
algorithms and does not prove a lower bound for arbitrary arithmetic circuits
over finite-field coordinates.
