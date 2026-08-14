# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — HIGHER-ARITY INDEX B5

Date: 2026-08-14

Status: **adding three or more index sets can reduce the number of leaf multiples, but every explicit hierarchical elliptic-resultant construction has a final binary elimination whose input degree is still of square-root size. Higher arity does not beat the exponent unless one avoids materializing both root-child polynomials entirely.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Frozen central target

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with all-in cost `O(n^(1/2-epsilon))`.

Package B4 showed that the standard two-set square-root Vélu index architecture already requires `ceil(sqrt(n))-1` input states on secp256k1 and that the oriented half-divisor also requires a nontrivial order-`n` line-bundle trivialization.

The next possible escape is to use three or more index sets.

## 2. Three-set combinatorics looks promising only at the leaves

For three index sets of sizes

```text
a=#I,
b=#J,
c=#L,
```

one triple can produce at most four distinct Kummer values

```text
x([+/-i +/-j +/-l]G),
```

because global negation identifies opposite sign vectors. Thus ideal collision-free coverage can have size on the order of

```text
4abc.                                                       (H1)
```

Choosing `a,b,c` near `M^(1/3)` makes the number of leaf multiples look sub-square-root.

## 3. Iterated elliptic resultants restore the square-root bottleneck

The first binary elliptic addition/resultant combines `I` and `J` into an intermediate polynomial of degree approximately

```text
A=2ab.                                                       (H2)
```

Combining this with `L` uses a second input of degree approximately

```text
B=2c.                                                        (H3)
```

The final coverage is bounded by

```text
M <= A B.                                                    (H4)
```

Therefore

```text
boxed:
max(A,B) >= sqrt(M).                                         (H5)
```

Balancing the three leaf sets cannot lower the largest explicitly represented intermediate below the square-root scale. Choosing `ab` small forces `c` large; choosing `c` small forces `ab` large.

## 4. Arbitrary binary resultant tree

The same argument does not depend on there being exactly three leaf sets.

At the root of any hierarchical binary resultant tree, let the two explicitly represented child polynomials have degrees `A` and `B`, and let `c` uncovered factors be evaluated directly. If the construction covers `M` oriented labels, then

```text
M <= A B + c.                                                (H6)
```

Let

```text
C=max(A,B,c).
```

Then

```text
boxed:
M <= C^2+C.                                                  (H7)
```

Thus

```text
C >= ceil((sqrt(1+4M)-1)/2)=Omega(sqrt(M)).                 (H8)
```

For secp256k1, `M=(n-1)/2`, and the exact integer lower bound is

```text
C >= 240615969168004511545033772477625056927,                (H9)
```

which has 128 bits and is approximately `2^127.5`.

This is an explicit-representation lower bound: a child polynomial of that degree carries at least that many coefficients or root/product-tree states in the declared model. Resultant arithmetic and the missing generator-oriented trivialization only add cost.

## 5. Scope of the closure

Closed by B4-B5:

```text
standard two-set square-root Velu index systems,
any finite number of index sets combined through an explicit binary resultant tree,
residual factors explicitly listed at the root,
x-only symmetric kernel-product evaluation in this architecture.
```

The argument allows arbitrary public indices, redundant integer representations, balancing strategies, and parallel scheduling. These improve constants, not the exponent.

## 6. What is not closed

The result does not exclude:

1. a direct sparse multivariate resultant that never materializes either root child;
2. a transposed black-box evaluation algorithm acting only on one query value;
3. a special CM recurrence whose state dimension is not proportional to an intermediate polynomial degree;
4. a genuinely nonlinear generator-sensitive circuit outside the index/resultant architecture.

Any such proposal must specify the exact represented state and prove that no degree-`Omega(sqrt(n))` intermediate is hidden in preprocessing, advice, or memory.

## 7. Frozen exact replay

`uorc056_higher_arity_index.py` verifies the root-coverage inequalities on the same ten frozen orders as B4. It exhausts relaxed root-degree triples and three-set cardinalities on the toy range and records the exact secp256k1 bounds.

The replay is combinatorial and does not evaluate any unknown point.

## 8. Formalization boundary

`Ecdlp/Proved/HigherArityIndexBoundary.lean` kernel-checks:

```text
A<=C, B<=C, c<=C, M<=AB+c => M<=C^2+C,
M<=AB => M<=max(A,B)^2.
```

It does not formalize resultants, elliptic addition polynomials, theta functions, secp256k1, parity recovery, or ECDLP.

## 9. Answer for this B-track class

```text
Can three leaf sets have cube-root leaf count?                 yes
Can an iterated explicit resultant keep all states cube-root?  no
Root child degree                                              Omega(sqrt(M))
Exact secp child-degree lower bound                            240615969168004511545033772477625056927
Does explicit higher-arity indexing meet n^(1/2-epsilon)?      no
Public parity / absolute EDS oracle                            absent
Sub-square-root ECDLP                                          absent
```

## 10. Strategic successor

The next B-track package is

```text
UORC056-TRANSPOSED-KERNEL-EVALUATION-B6.
```

It asks whether one can evaluate the generator-oriented section at one public `x(Q)` using transposed modular composition, black-box resultants, or a linear recurrence without constructing a square-root-degree intermediate polynomial. The first gate is to separate known fast evaluation of the generator-blind kernel polynomial from the missing evaluation of its oriented square root.
