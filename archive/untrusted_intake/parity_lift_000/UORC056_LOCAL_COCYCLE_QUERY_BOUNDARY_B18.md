# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track B18: local-cocycle query and seed-propagation boundary

Date: 2026-08-14

Status: **a public branch seed plus black-box access to the compact local
cocycle does not yield a sub-square-root endpoint evaluator. Unless the queried
edges connect the anchor to the target, a componentwise multiplicative gauge
produces two global potentials with identical seed and identical queried edge
answers but different target values. On an odd cycle the worst target requires
`(n-1)/2` local edges. This closes local walking and edge-oracle-only
propagation, while leaving genuinely nonlocal algebraic identities open.**

No external point, private key, wallet, unknown scalar, or production-sized
DLP target is accepted. Executable checks use abstract frozen cycles only.

## 1. Central target is unchanged

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with all preprocessing, advice, representation, memory, branch selection, and
online work charged inside

```text
O(n^(1/2-epsilon)).
```

B13-B17 give:

```text
one exact public marked-generator seed,
a compact public local cocycle h(P)=F(P+T)/F(P),
T=[2]G,
translation order n.
```

B18 asks whether one can recover `F(Q)/F(P0)` using only evaluations of this
local edge and ordinary multiplicative composition.

## 2. Queried-edge graph

Identify one translation orbit with the cycle

```text
0,1,...,n-1,
```

where edge `i` joins `i` to `i+1 mod n`. Let `S` be the set of local cocycle
edges queried by an algorithm.

The queried edges define a graph `(V,S)`. Let `F : V -> K^*` be one global
potential and

```text
h_i=F_(i+1)/F_i.                                  (B18.1)
```

## 3. Component gauge obstruction

Choose a gauge

```text
g : V -> K^*
```

that is constant on every connected component of `(V,S)`, and define

```text
F'_i=g_i F_i.                                     (B18.2)
```

For every queried edge `i in S`, both endpoints lie in one component, so

```text
g_(i+1)=g_i
```

and therefore

```text
F'_(i+1)/F'_i=F_(i+1)/F_i=h_i.                   (B18.3)
```

If the anchor component receives gauge `1`, then

```text
F'_anchor=F_anchor.                               (B18.4)
```

If the target is in another component, assign it any gauge `c!=1`. Then

```text
F'_target=c F_target != F_target.                 (B18.5)
```

The two potentials have:

```text
the same public seed,
the same answers on every queried local edge,
different endpoint/global values.
```

Every potential still defines a norm-one cyclic cocycle because the full
product telescopes. Thus cyclic norm one does not remove this ambiguity.

## 4. Exact query consequence

In the black-box local-edge model, the endpoint ratio is determined only if the
queried-edge graph connects the anchor and target.

For target index `t`, the minimum number of cycle edges in a connecting path is

```text
d(t)=min(t,n-t).                                  (B18.6)
```

The worst target is the midpoint class and requires

```text
boxed:
max_t d(t)=(n-1)/2.                               (B18.7)
```

For secp256k1 this equals

```text
57896044618658097711785492504343953926418782139537452191302581570759080747168.
```

Hence local walking, adaptive local-edge queries, and multiplication of queried
edge values are linear in the worst case and cannot satisfy the fixed-epsilon
sub-square-root gate.

If preprocessing must support every possible target, the queried graph must be
connected and therefore needs at least `n-1` stored/query edges.

## 5. Scope boundary

B18 does **not** rule out an algorithm that uses the explicit algebraic formula
for the Miller cocycle nonlocally, for example a new resultant, special-function,
CM, or functional identity that evaluates a whole segment without querying its
individual edges.

It closes only mechanisms whose information about the global potential is the
anchor value plus black-box local cocycle evaluations and their field
combinations.

## 6. Exhaustive frozen replay

`uorc056_local_cocycle_query_boundary.py` exhausts all queried-edge subsets for
cycles of lengths

```text
7,11,13.
```

For every target outside the anchor component it constructs an explicit
component gauge and verifies exactly:

1. the anchor value is unchanged;
2. every queried edge answer is unchanged;
3. the target value changes;
4. both full cocycle norms remain one;
5. the minimum connecting query count is `min(t,n-t)`.

The replay checks `10,368` query masks and `119,552` mask-target pairs, including
`98,856` explicit indistinguishable gauge pairs.

## 7. Formalization boundary

`Ecdlp/Proved/LocalCocycleQueryBoundary.lean` kernel-checks:

1. a gauge constant across one queried edge preserves its cocycle value;
2. gauge one preserves the anchor value;
3. a nontrivial gauge changes the target value.

It does not formalize graph connectivity, query algorithms, elliptic curves,
Miller functions, secp256k1, parity recovery, or ECDLP.

## 8. Decision

```text
Public seed                                      yes
Compact public local edge                        yes
Black-box edge-only endpoint propagation         worst-case (n-1)/2 queries
All-target edge table                            at least n-1 edges
Fixed-epsilon sub-root through local walking      no
Nonlocal algebraic seed-propagation identity      open
Public parity oracle                             absent
```

## 9. Remaining central mechanism

After B18, a positive B-track result can no longer be a walk, block product,
explicit Hilbert-90 vector, linear recurrence, or explicit Pell reconstruction.
It must be a nonlocal base-field identity that propagates the public marked
branch seed to `x(Q)` without representing the intervening cycle.

That is not a renamed target. It is exactly the unchanged
`UNIFORM-ORIENTED-ROOT-CIRCUIT-056` evaluator.