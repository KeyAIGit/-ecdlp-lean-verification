# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track B14: endpoint segment and cyclic-factorial equivalence

Date: 2026-08-14

Status: **the endpoint-only segment evaluator and the cyclic elliptic factorial
evaluator are not two independent missing mechanisms. They are exactly the
same global multiplicative potential, up to one public anchor scalar. Standard
explicit Hilbert-90/circulant representations have linear state, while standard
two-level block products meet the square-root frontier. No strict
sub-square-root evaluator is obtained.**

No external point, private key, wallet, unknown scalar, or production-sized
discrete-log target is accepted. Executable checks use abstract frozen cyclic
models only.

## 1. Central target is unchanged

The central target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with preprocessing, advice, memory, representation, branch selection,
normalization, query work, and online work all charged inside

```text
O(n^(1/2-epsilon)).
```

B8-B13 construct a public local multiplicative cocycle for a generator-oriented
global factor. The two remaining descriptions were:

```text
endpoint segment:
    C(P,Q)=H_G(Q)/H_G(P),

cyclic elliptic factorial:
    Q -> H_G(Q).
```

This package proves that these descriptions are equivalent.

## 2. Pair-groupoid identity

Let `X` be one orbit or coset and let `K` be a multiplicative field group.
For any nonzero potential

```text
F : X -> K^*
```

define

```text
E(P,Q)=F(Q)/F(P).                                  (B14.1)
```

Then

```text
E(P,P)=1,
E(P,Q)E(Q,R)=E(P,R).                              (B14.2)
```

Conversely, suppose a public endpoint function satisfies `(B14.2)`. Fix one
public anchor `P0` and put

```text
F_(P0)(Q)=E(P0,Q).                                (B14.3)
```

Then

```text
boxed:
E(P,Q)=F_(P0)(Q)/F_(P0)(P).                       (B14.4)
```

Therefore:

```text
exact endpoint evaluator + one anchor
    <=> exact global potential evaluator.         (B14.5)
```

A constant rescaling `F -> cF` does not change `E`. More generally, on one
`H`-coset any factor pulled back from the quotient `E/H` is constant along the
coset and cancels from `(B14.1)`.

Thus the endpoint problem removes one scalar normalization, but it does not
define a smaller mechanism class than the cyclic factorial itself.

## 3. Translation cocycle and Hilbert 90

Let `T=[2]G` and let

```text
sigma(P)=P+T.
```

For a potential `F` define

```text
h(P)=F(P+T)/F(P).                                 (B14.6)
```

For a known integer `m`,

```text
product_(j=0)^(m-1) h(P+jT)
 =F(P+mT)/F(P)
 =E(P,P+mT).                                     (B14.7)
```

The cyclic norm telescopes:

```text
product_(j=0)^(n-1) h(P+jT)=1.                   (B14.8)
```

The standard multiplicative Hilbert-90 construction recovers a potential from
`h` by an `n`-term sum of cumulative products. In the explicit orbit basis the
linear recurrence is

```text
F_(i+1)=h_i F_i.                                  (B14.9)
```

Its cyclic coefficient matrix has rank `n-1` when `(B14.8)` holds, and its
one-dimensional kernel is spanned by

```text
(F_0,F_1,...,F_(n-1)).
```

All entries are nonzero. Hence the standard explicit orbit-vector,
normal-basis, trace-row, or circulant solution materializes `n` field elements.
The sparse recurrence matrix does not make its distinguished kernel vector
sparse.

This is a representation statement for the standard orbit basis, not a
general arithmetic-circuit lower bound.

## 4. Exact two-level block frontier

The standard block-product strategy for a product of length `m` chooses:

```text
b  local factors per baby block,
g  giant blocks,
m <= b*g.
```

If both the baby state and giant evaluations are charged, the width/work is at
least

```text
w=b+g.
```

The elementary identity

```text
(b+g)^2 >= 4bg
```

gives

```text
boxed:
w^2 >= 4m.                                        (B14.10)
```

At the parity midpoint

```text
m=M=(n-1)/2,
```

this is a square-root frontier. For secp256k1 the exact ceiling recorded by
the package is

```text
481231938336009023090067544955250113854
```

charged units, a 129-bit quantity.

This scoped bound covers the ordinary two-level baby-step/giant-step,
block-product, and product-tree-with-materialized-block-state model. It does
not rule out a genuinely different nonlinear identity.

## 5. Why the unknown endpoint index matters

Algorithms for factorial or q-factorial terms normally receive the term index
`m`. The endpoint input here supplies only encoded points

```text
P,
Q=P+[m]T.
```

Recovering the canonical `m` is itself a discrete logarithm in the prime-order
translation orbit.

A routine that instead receives `zeta_n^m`, `q^m`, or an oriented dual point has
been supplied a faithful dual character. That is forbidden advice under the
056 cost model and, on secp256k1, has the explicit extension-field obstruction
recorded by the dual-character packages.

Therefore an indexed factorial algorithm is not automatically an endpoint-only
algorithm.

## 6. Relation to B13

B13 gives a projective cocycle of straight-line size `O(log n)` and derives:

```text
exact normalization  = cyclic norm,
global factor        = multiplicative Hilbert-90 lift.
```

B14 shows that the endpoint segment, the cyclic elliptic factorial, and the
distinguished Hilbert-90 lift are three presentations of one missing global
object:

```text
compact local cocycle
    -> exact global potential
    -> endpoint ratios
    -> oriented root/parity.                     (B14.11)
```

The two user-facing open items are therefore merged mathematically, not solved
algorithmically.

## 7. Frozen exact replay

`uorc056_endpoint_factorial_equivalence.py` uses five abstract cyclic
finite-field models of orders

```text
7,13,17,19,31.
```

It verifies exactly:

1. endpoint groupoid composition;
2. local-product telescoping;
3. reconstruction of every endpoint from one anchor row;
4. invariance under a constant potential gauge;
5. cyclic norm one;
6. rank `n-1` and dense one-dimensional kernel of the recurrence matrix;
7. the standard `n`-term Hilbert-90 identity;
8. the two-level square-root tradeoff.

The replay contains no elliptic-curve target and proves no lower bound beyond
the declared representations.

## 8. Decision

```text
Are endpoint evaluator and cyclic factorial separate?      no
Endpoint evaluator from global potential                    immediate
Global potential from endpoint evaluator plus anchor        immediate
Standard explicit Hilbert-90 state                          n
Standard orbit/circulant kernel vector                       dense
Standard two-level block cost                               Omega(sqrt(n))
Does an indexed q-factorial routine solve endpoint input?   no; m is hidden
Public parity evaluator                                     absent
Classical sub-square-root ECDLP                              absent
```

## 9. Successor

The next scoped package is

```text
UORC056-CYCLIC-FACTORIAL-STANDARD-BOUNDARY-B15.
```

It analyzes the exact root-of-unity shadow of the alternating factorial,
proves density and full linearized frequency support, and compares the known
q-holonomic square-root algorithmic frontier with the 056 fixed-epsilon
sub-root gate.
