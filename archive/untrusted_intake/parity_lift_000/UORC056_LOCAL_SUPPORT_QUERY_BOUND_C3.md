# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C3: exact local-support query lower bound

Date: 2026-08-13

Status: **the direct translation-resolvent application through point idempotents is closed. Any exact deterministic algorithm whose Q-dependent observations are membership queries in public subgroup subsets of support at most b must satisfy q*b >= (n-1)/2 along its all-zero transcript. For translated singleton defects, at least (n-1)/2 queries are necessary. Arbitrary nonlinear post-processing does not change the bound.**

## 1. Model

Let `n=2M+1` be odd and let the unknown canonical scalar index be

```text
k in {0,...,n-1}.
```

The target is

```text
parity(k)=(-1)^k.
```

A deterministic exact algorithm may make adaptive queries. At query `i`, after seeing previous answers, it chooses a public subset

```text
S_i subset {0,...,n-1},
|S_i| <= b,
```

and receives one bit

```text
answer_i = 1[k in S_i].
```

After at most `q` queries it must output parity for every `k`.

This model allows arbitrary computation between queries. The only restriction is that every Q-dependent primitive has subgroup support at most `b`.

The direct resolvent seed has `b=1` because

```text
delta_(-G)(Q+[a]G)=1
```

for exactly one scalar position.

## 2. Exact lower bound

Consider the adaptive path on which every oracle answer is zero. The sequence of sets chosen on this path is fixed. Let

```text
U=S_1 union ... union S_q.
```

Then

```text
|U| <= q*b.                                      (L1)
```

There are exactly

```text
M+1 even indices,
M odd indices.                                   (L2)
```

Assume

```text
q*b < M.                                         (L3)
```

By `(L1)`, `U` cannot contain every odd index, and it cannot contain every even index. Therefore there exist

```text
k_even notin U,
k_odd  notin U.                                  (L4)
```

Both inputs produce the same all-zero transcript, but their required outputs are opposite. This contradicts exact correctness.

Hence

```text
boxed:
q*b >= M=(n-1)/2.                                (L5)
```

No assumption was made about linearity, rationality, or the amount of arithmetic after the queries.

## 3. Singleton defect consequence

For translated point-idempotent queries,

```text
b=1.
```

Equation `(L5)` gives

```text
boxed:
q >= (n-1)/2.                                    (L6)
```

The bound is tight in the abstract labelled-index model: query every odd index; if all answers are zero, output even. In the actual coordinate problem, constructing the odd-index query family already requires the hidden orientation, so tightness does not provide a public evaluator.

This closes:

```text
explicit alternating orbit evaluation,
adaptive equality search for the unique wrap defect,
short operator DAGs evaluated only by translated delta probes,
arbitrary nonlinear post-processing of fewer than (n-1)/2 singleton probes.
```

## 4. Block-support tradeoff

If a candidate primitive tests membership in a block of at most `b` subgroup positions, exact parity still requires

```text
q >= ceil(M/b).                                  (L7)
```

Thus a baby-step giant-step style scheme with `b` positions summarized per block cannot beat the local-support product barrier

```text
query_count * support_per_query >= (n-1)/2.       (L8)
```

This is not a universal arithmetic lower bound. A genuinely nonlocal observable can have full support and a short formula. The theorem says that merely grouping local defect probes into bounded-support blocks cannot create the required compression.

## 5. Relation to the translation resolvent

The exact parity function satisfies

```text
s_G=sum_(j=0)^(n-1)(-1)^j tau_G^j delta_(-G).
```

The support theorem explains why evaluating this formula through direct seed probes expands. The alternating coefficients do not help before the unique nonzero defect location has been located to its parity class.

The theorem separates two tasks:

```text
closed:
locate the defect parity using bounded-support membership probes;

open:
evaluate a genuinely nonlocal coordinate function, resultant, norm,
or determinant that combines the orbit algebraically before local expansion.
```

## 6. Consequence for the master prompt

The next positive candidate must violate at least one premise of the local-support model. It must provide a primitive whose Q-dependent value is not reducible to membership in `b=o(n)` explicit orbit locations, or whose internal algebraic evaluation combines large support at sub-square-root total cost.

The highest-value surviving routes are therefore:

1. a constant-description resultant or norm that evaluates a full-support observable directly;
2. an oriented fast elliptic product with a nonlocal cancellation unavailable to ordinary block membership;
3. a nonlinear coordinate-algebra transfer state whose merge law does not expose local supports;
4. a scoped lower bound for one such richer grammar.

## 7. Answer

```text
Direct translated-delta evaluator                         rejected
Exact singleton-query complexity                          (n-1)/2
Bounded-support query tradeoff                             q*b >= (n-1)/2
Does arbitrary nonlinear post-processing evade it?        no
Does this prove a universal circuit lower bound?           no
Genuinely nonlocal determinant/resultant route             open
Public parity evaluator                                   absent
Sub-square-root ECDLP                                      absent
```
