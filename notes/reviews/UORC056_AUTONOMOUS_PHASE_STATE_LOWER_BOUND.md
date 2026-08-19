# UORC-056 Autonomous Phase-State Lower Bound

## Status

Proved finite-state boundary for autonomous coherent transport.

This theorem explains why a fixed two-, three-, or six-phase root state cannot carry exact canonical parity around an odd prime-order cycle.

## Model

Let the canonical scalar positions be the odd cycle `Z/nZ`, with parity word

`f(k)=(-1)^k` for representatives `0<=k<n`.

Assume a public state map `S(k)` takes values in a finite set `X`. Assume there is one position-independent update rule `F:X->X` such that

`S(k+1)=F(S(k))`

for every position on the cycle, and a decoder `d:X->{+1,-1}` such that

`d(S(k))=f(k)`

exactly.

The update is autonomous: after the initial state is known, the next state depends only on the current state, not on the coordinates of the current point, the step index, or additional external data.

## Lemma: the odd-cycle parity word has no nontrivial rotational symmetry

Along the canonical sequence

`0,1,...,n-1`,

successive parity signs alternate everywhere except at the wrap-around edge from `n-1` to `0`.

Because `n` is odd, both `n-1` and `0` are even. Therefore this is the unique adjacent pair with equal signs.

Any cyclic rotation preserving the complete parity word must preserve that unique seam. Hence it fixes position `0` and is the identity rotation.

## Theorem: the state map is injective

Assume `S(a)=S(b)`. Applying the deterministic update repeatedly gives

`S(a+t)=S(b+t)`

for every nonnegative `t`.

Decoding gives

`f(a+t)=f(b+t)`

for every `t`. Thus rotation by `b-a` preserves the complete parity word. By the lemma, `a=b` modulo `n`.

Therefore `S` is injective and

`|X| >= n`.

The lower bound is tight: storing the complete scalar position uses exactly `n` states.

## Consequences

No autonomous exact transport can use only:

- one sign;
- a square-root branch with two phases;
- a cubic branch with three phases;
- a sextic branch with six phases;
- any fixed or `poly(log n)` number of discrete phase labels.

For secp256k1, such an autonomous state must have at least as many distinguishable values as the entire subgroup.

## What the theorem does not exclude

The theorem does not exclude a state consisting of `poly(log n)` **bits** or field elements, because such a state space can contain at least `n` distinct values. It also does not exclude:

- updates depending on the public coordinates of the current point;
- non-autonomous updates depending on the public addition-chain step;
- nonlinear arithmetic states over the base field;
- a direct decoder that does not generate the parity word by repeated `+G` transport;
- theta, Miller, CM, p-adic, or modular-composition states with query-dependent dynamics.

## Research implication

A successful coherent-root transport cannot be only a small phase label updated by one fixed transition. It must carry field-valued information or use public query-dependent data. The remaining search should therefore avoid constant-phase automata and require every proposed transport to declare where its at-least-`n` distinguishable states are represented without hiding an exponential table.
