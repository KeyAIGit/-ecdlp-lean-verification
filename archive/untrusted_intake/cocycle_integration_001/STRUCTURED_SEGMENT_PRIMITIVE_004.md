# STRUCTURED-SEGMENT-PRIMITIVE-004

Date: 2026-08-12

Status: **isolated restricted-model theorem package**, stacked on
`GENERIC-COCYCLE-INTEGRATION-003`. It is separate from the active direct-GLV,
Kummer-circuit, and uniform-grammar branches. It targets no external point or
key and claims no unconditional EDS or ECDLP lower bound.

## 1. Target

For

```text
Q=[k]G,
rho_G(Q)=chi(psi_k(G)),
delta_G(P)=rho_G(P+G) rho_G(P),
```

the local edge value `delta_G(P)` may be publicly computable while the absolute
value is the anchored prefix product

```text
rho_G([k]G) = rho_G(O) * product_(0 <= i < k) delta_G([i]G).
```

`GENERIC-COCYCLE-INTEGRATION-003` shows that querying local edges one by one is
linear in the worst case when the edge sequence is treated as arbitrary closed
binary data. This package asks whether preprocessing or divide-and-conquer can
compress the prefix.

## 2. Checkpoint-and-walk model

Store `S` checkpoint states. During an online query, choose one checkpoint and
one offset from a range of size `T`, then deterministically walk/advance to the
target and accumulate the local cocycle along that short segment.

Every possible target must be represented by at least one pair

```text
(checkpoint, offset).
```

There are at most `S*T` such pairs. A surjective decoder onto an order-`n`
target space therefore requires

```text
boxed: n <= S*T.
```

The Lean file

```text
Ecdlp/Proved/SegmentCheckpointTradeoff.lean
```

proves:

- `checkpointDecoder_timeSpace_tradeoff`;
- `checkpointWalk_timeSpace_tradeoff`;
- `checkpointWalk_order_tradeoff`.

Consequences:

- constant or polylogarithmic storage forces essentially linear online walking;
- polylogarithmic online walking forces essentially linear checkpoint storage;
- balancing storage and online offsets reaches the square-root frontier;
- charging the work required to obtain absolute checkpoint residues can only
  make the scheme more expensive.

A bidirectional local walk changes only a constant factor: a checkpoint covers
at most about `2T+1` targets, so the same product tradeoff remains.

## 3. Why ordinary scalar halving does not give a canonical segment split

A tempting divide-and-conquer recursion computes the public group half

```text
H = [2^(-1) mod n] Q.
```

For the canonical scalar `0 <= k < n`, with odd `n`, this represents

```text
H = [k/2]G              when k is even,
H = [(k+n)/2]G          when k is odd.
```

The desired canonical path midpoint is instead

```text
M = [floor(k/2)]G.
```

Choosing `M` from the public half requires deciding whether

```text
Q = [2]M
```

or

```text
Q = [2]M + G.
```

That decision is exactly `k mod 2`, the target parity bit. Conversely, once the
bit `b=k mod 2` is known,

```text
M = [2^(-1) mod n](Q-[b]G)
```

is public. Thus a recursion that assumes access to the canonical midpoint is
circular: its branch selector already solves the bit under investigation.

A branch-oblivious recursion can evaluate both possibilities, but after `d`
levels it carries all `2^d` possible low-bit strings. Without a new pruning or
compression invariant, depth `log2(n)` returns to linear-scale state expansion.

This halving argument is currently an exact arithmetic observation and a model
boundary, not yet a general circuit lower bound.

## 4. What the theorem closes

Closed mechanism class:

```text
precompute finitely many absolute checkpoints, then answer every target by a
bounded local edge walk from one checkpoint.
```

Within this class, preprocessing space times online local-walk range is at least
the group order.

The result also rejects descriptions that claim a cheap “segment primitive” but
materialize it as a table of checkpoints plus local traversal without charging
the table.

## 5. What survives

The theorem does not exclude:

1. a uniform closed formula for a long prefix product;
2. a theta/sigma multiplication law returning the whole segment in
   polylogarithmic work;
3. a global p-adic normalization with a canonical branch;
4. an arithmetic circuit whose internal states do not correspond to
   checkpoint/offset pairs;
5. preprocessing with a more subtle representation, provided its total size,
   build cost, and online cost are all charged;
6. a structure-sensitive algorithm outside the generic/local-edge model.

Any positive proposal must state exactly which of these escape hatches it uses.

## 6. Next theorem target

The next class should be a **binary segment-composition circuit** with explicit
interfaces:

```text
Segment(A,C) = Combine(Segment(A,B), Segment(B,C), metadata),
```

where endpoints are public group points and metadata has bounded description
size. The key question is whether the circuit can choose or synthesize `B`
without:

- recovering a scalar bit;
- branching over both canonical halves;
- storing square-root-scale checkpoints;
- importing an equivalent absolute residue oracle.

A useful successor is

```text
CANONICAL-MIDPOINT-CIRCULARITY-005
```

followed by a precise restricted recursion model. A positive counterexample
would need to exhibit a public midpoint-independent composition law.
