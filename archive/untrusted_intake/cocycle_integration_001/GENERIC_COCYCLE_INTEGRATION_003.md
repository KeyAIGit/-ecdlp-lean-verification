# GENERIC-COCYCLE-INTEGRATION-003

Date: 2026-08-12

Status: **isolated theorem package for a restricted oracle model**. This branch is
stacked on `research/cocycle-integration-001`, is separate from the active
`PARITY-LIFT-000` / direct-GLV circuit work, targets no external point or key,
and claims no unconditional EDS or ECDLP lower bound.

## 1. Model

Let the oriented cycle have edges indexed by a finite set of size `n`. A binary
edge cocycle is represented additively by

```text
delta_i in F_2.
```

Cycle closure supplies the one public global relation

```text
sum_i delta_i = 0.
```

Fix an anchor potential `s_0=0`. For the vertex `[k]G`, the potential is the
prefix integral

```text
s_k = sum_(0 <= i < k) delta_i.
```

For EDS signs this additive notation corresponds to multiplication in
`{+1,-1}`. The public adjacent residue ratio is the local edge value, and the
absolute residue is the anchored potential.

The declared black-box model allows an algorithm to:

1. perform arbitrary generic group computations;
2. query individual edge labels at any group points it has produced;
3. know the cycle-closure parity;
4. use no additional algebraic correlation among the edge labels.

The last condition is the decisive restriction. Actual EDS edge labels are
structured, so this model is a boundary theorem, not the final answer.

## 2. Exact indistinguishability theorem

Let `A` be the target cut and `S` the queried edge set. Suppose there is an
unqueried edge

```text
i in A \ S
```

and another

```text
j in A^c \ S.
```

Compare two edge assignments:

```text
delta_0 = 0,
delta_1 = 1_{i,j}.
```

They have:

- identical answers on every queried edge;
- identical global closure parity, because two edges were flipped;
- opposite target cut parity, because exactly one flipped edge lies in `A`.

Therefore a transcript determines the target potential for every closed binary
edge assignment only if

```text
A subset S
```

or

```text
A^c subset S.
```

The Lean file

```text
Ecdlp/Proved/CocycleQueryAmbiguity.lean
```

formalizes:

- `two_unqueried_edges_hide_cut_parity`;
- `exact_closed_cut_decoder_covers_one_side`;
- `exact_closed_cut_query_card_lower_bound`.

The resulting exact query bound is

```text
|S| >= min(|A|, |A^c|).
```

For the prefix cut of a target `k` on an `n`-cycle:

```text
q >= min(k, n-k).
```

Choosing a midpoint target gives the worst-case bound

```text
q >= floor(n/2).
```

This is stronger than a square-root bound, but only because the model treats the
closed local cocycle as otherwise arbitrary.

## 3. Adaptive and randomized algorithms

The witness also applies to deterministic adaptive queries. Follow the
all-zero-answer transcript. If the final queried set misses one edge on each
side of the target cut, the two-flip assignment produces a second closed input
with the same complete transcript and the opposite answer.

For randomized algorithms, fix the random coins to obtain the deterministic
statement. Under the uniform distribution on closed binary edge assignments,
the target cut parity remains an unbiased bit after conditioning on any
transcript that leaves one unqueried edge on each side. Thus a bounded-query
algorithm has success exactly `1/2` on that conditional distribution until it
covers one whole side.

The adaptive/randomized formulation is recorded here as the model-level
consequence of the kernel-checked finite witness; a full probabilistic Lean
formalization is not part of this package.

## 4. Consequence for the EDS-residue program

For

```text
Q=[k]G,
rho_G(Q)=chi(psi_k(G)),
delta_G(P)=rho_G(P+G) rho_G(P),
```

the adjacent ratio `delta_G(P)` can be public while `rho_G(Q)` remains an
anchored prefix product.

This package proves:

> Local adjacent residue queries plus cycle closure, considered as black-box
> data, cannot be integrated in sublinear exact query complexity.

Therefore a positive sub-square-root EDS-residue algorithm must exploit more
than local ratios. It must exhibit at least one of:

1. a succinct segment-product primitive;
2. a global theta/sigma section with a canonically fixed branch;
3. a nonlocal recurrence that compresses long prefix products;
4. a coordinate-sensitive correlation absent from the arbitrary-edge model;
5. preprocessing whose size and online cost are both explicitly charged.

This cleanly separates `SEGMENT-PRIMITIVE-002` from repeated local-edge
sampling: a real segment primitive must evaluate the whole prefix as one
structured object, not merely hide a linear walk behind notation.

## 5. Relation to known generic lower bounds

Shoup's classical generic-group lower bound gives square-root complexity for
prime-order discrete logarithms (`EUROCRYPT 1997`, DOI
`10.1007/3-540-69053-0_18`). The exact parity-to-DLP reduction means that a
fully generic exact residue/parity routine used `O(log n)` times cannot have
per-call generic cost below roughly `sqrt(n)/log n` without contradicting that
bound.

That corollary does **not** cover coordinate-sensitive EDS, theta, division-
polynomial, or finite-field-character computations. Those are precisely the
non-generic structures under investigation.

Relevant extensions include:

- Lauter--Stange, EDS Association / Residue / Discrete Log,
  arXiv `0803.0728`;
- Corrigan-Gibbs--Kogan, generic DLP with preprocessing,
  IACR ePrint `2017/1113`;
- Corrigan-Gibbs--Henzinger--Wu, structured generic-group model,
  IACR ePrint `2026/384`.

The 2026 structured model may support a later lower bound if a proposed
observable exploits recognizable structure on only a controlled fraction of
points. No such transfer theorem is claimed here.

## 6. Frozen finite replay

The companion verifier

```text
experiments/cocycle_integration_003/verify_query_ambiguity.py
```

checks the exact criterion for every query set on cycles through size 14 and
runs deterministic larger samples on odd sizes through 127. Its role is
transcription insurance; the Lean kernel is the judge of the finite witness.

## 7. Current decision

The central real-curve question remains open:

```text
Given x(Q), can rho_G(Q) be computed below square-root total cost?
```

But one mechanism class is now closed exactly:

```text
arbitrary closed local-edge oracle data with no additional global structure.
```

The next nonconflicting research step is to define a restricted structured
segment-primitive model and determine whether EDS recurrences, theta addition
laws, or low-description circuits can evaluate a long cocycle prefix without
implicitly performing square-root preprocessing or recovering the scalar.
