# CANONICAL-MIDPOINT-CIRCULARITY-005

Date: 2026-08-12

Status: **isolated restricted-model theorem package**, stacked on
`STRUCTURED-SEGMENT-PRIMITIVE-004`. It remains separate from the active
`PARITY-LIFT-000`, admissible-GLV, period-orientation, and direct circuit
branches. It targets no external point or key and claims no unconditional EDS
or ECDLP lower bound.

## 1. Exact binary split

For the canonical scalar

```text
0 <= k < n,
Q=[k]G,
```

the canonical path midpoint is

```text
m=floor(k/2).
```

There is an exact decomposition

```text
k=2*m+b,
b=k mod 2.
```

The one-bit correction `b` is unique. Therefore an interface returning the
canonical midpoint also returns parity by

```text
b=k-2*m.
```

The Lean file

```text
Ecdlp/Proved/CanonicalMidpointCircularity.lean
```

kernel-checks the uniqueness of both the midpoint and the correction, plus the
corresponding scalar-action identity in an arbitrary additive monoid.

## 2. Why the public group half is not the canonical path midpoint

In an odd-order cyclic group, doubling is bijective. The public point

```text
H=[2^(-1) mod n]Q
```

is uniquely computable from `Q`. Its canonical scalar representative is

```text
h=(k+(k mod 2)*n)/2.
```

Thus

```text
h=k/2+(k mod 2)*(n+1)/2.
```

Consequently:

```text
k even: h=k/2,
k odd:  h=k/2+(n+1)/2.
```

The public group half equals the canonical path midpoint if and only if `k` is
even. Deciding whether the half-order correction must be removed is exactly the
parity decision.

This makes a common divide-and-conquer proposal circular:

1. compute the public group half;
2. treat it as the midpoint of the canonical path;
3. recursively integrate the first half.

Step 2 silently assumes the target parity bit.

## 3. Branch-oblivious recursion

One may retain both candidate branches instead of choosing. At the first level
they correspond to the two possible low bits. Repeating the construction to
depth `d` retains up to `2^d` low-bit strings unless an additional exact
compression invariant merges them.

At depth approximately `log2(n)`, naive branch retention reaches order-`n`
state count. This observation is a decision-tree warning, not yet a formal lower
bound for arbitrary shared circuits: distinct branches might share internal
computation, and a genuine global identity could bypass canonical midpoint
selection entirely.

## 4. Mechanism class closed

The package closes only constructions whose segment recursion requires the
canonical scalar midpoint as an intermediate public point but offers no
independent rule for selecting its correction branch.

Such a construction has imported the parity bit into its recursion interface.
It is not a decoder for parity.

## 5. What remains open

The theorem does not exclude:

1. midpoint-independent theta/sigma addition identities;
2. a segment primitive parameterized by unordered endpoint data;
3. a circuit evaluating both halves with subexponential sharing;
4. p-adic or analytic descent with a canonical branch from field structure;
5. a nonlocal EDS recurrence that returns the whole prefix product directly;
6. any other coordinate-sensitive algorithm with an independently proved total
   cost below the generic square-root baseline.

## 6. Next target

The next useful restricted model is

```text
BINARY-SEGMENT-CIRCUIT-006
```

with explicit requirements:

- endpoints and metadata are public point data;
- every branch selector is charged and may not depend on a hidden scalar bit;
- advice and preprocessing size are counted;
- shared subcircuits are represented explicitly;
- the output is the absolute EDS residue, not another relative label.

A positive result would be a public midpoint-independent composition law. A
negative result would need a lower bound inside that declared circuit model,
not an extrapolation from the midpoint theorem.
