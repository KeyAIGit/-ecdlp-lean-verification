# DIRECT-GLV-UNIFORM-GRAMMAR-012

Status: **isolated bounded research package; no production target**.

## Why uniformity is the next gate

Packages 010 and 011 allowed coefficients to be fitted separately inside each
finite field. That is useful for exhausting a declared finite class, but it
cannot distinguish an algorithm from a lookup table encoded into coefficients.
Indeed, package 010 showed that the complete family

```text
c -> chi(z-c)
```

has full binary rank on every frozen quotient set. Sufficiently many fitted
factors can therefore interpolate any finite sign table.

Package 012 imposes the missing requirement:

```text
one symbolic expression must be evaluated unchanged on every frozen field.
```

Only the public field and subgroup parameters are substituted. No coefficient
is fitted separately for a curve.

## Quotient target

As in packages 010 and 011, put

```text
z(Q) = x(Q)^3,
h(Q) = g(Q) * chi(y(Q)).
```

A rational selector with the required GLV and negation symmetries must satisfy

```text
chi(R(z(Q))) = h(Q)
```

on the `(n-1)/6` quotient orbits.

## Public constant grammar

The frozen atoms are

```text
0, 1, -1, B, -B,
beta, beta^2,
n, -n,
lambda, -lambda,
lambda^2, -lambda^2,
```

where `B=7`. The integer representatives of `n` and `lambda` are reduced
modulo the current base field.

Allowed constant operations are

```text
+, -, *, inverse when defined.
```

A binary operation costs one, and inversion costs one. Semantic duplicates on
the fifteen frozen fields are removed while retaining the shortest program.
This produces

```text
1561 constant programs of cost at most two,
145 coefficient programs of cost at most one,
3601 ordered coefficient pairs with total cost at most one.
```

Among the cost-at-most-two programs, 1356 are nonzero on every nontrivial
frozen case. They induce 640 distinct per-curve leading square-class patterns,
of which 244 remain distinct on the training split.

This semantic deduplication is an implementation reduction on the frozen
fields, not a symbolic identity theorem.

## Exponent grammar

For a positive integer `e`, the declared cost is the multiplication count of
ordinary left-to-right binary exponentiation:

```text
cost(e) = bit_length(e)-1 + popcount(e)-1.
```

The bound is

```text
cost(e) <= 7.
```

There are 54 allowed exponents, with maximum unreduced exponent `128`.

## Frozen split

The three tiny quotient sets are used only as an overfitting diagnostic:

```text
orders 19, 31, 67: 19 quotient bits in total.
```

The nontrivial split was frozen before candidate scoring:

| split | subgroup orders | quotient bits |
|---|---|---:|
| train | 271, 367, 397, 433, 547, 571, 811, 967 | 726 |
| validation | 1093, 1249 | 390 |
| test | 3469, 4021 | 1248 |

Candidate selection maximizes training accuracy only. Validation and test bits
are never used to choose an expression.

## Exact uniform families

### A. Up to two power-affine factors

The exact grammar is

```text
u * product_{j=1}^d (z^(e_j) + c_j),
0 <= d <= 2,
cost(e_j) <= 7,
cost(c_j) <= 1,
cost(u) <= 2.
```

After removing candidates that vanish on any nontrivial sampled point, there
are

```text
3451 valid primitive expressions,
3398 distinct primitive sign patterns.
```

Including the 244 training leading patterns and zero, one, or two distinct
primitive patterns gives

```text
1,409,076,088 nominal training classes.
```

Exact result:

```text
training exact decoders: 0,
all-nontrivial exact decoders: 0.
```

The same uniform grammar does fit the combined nineteen-bit tiny diagnostic:

```text
(B + lambda)
* (z + lambda^2 + 1)
* (z^3 + beta^2*lambda).
```

This fit does not transfer to the nontrivial cases. It is a direct demonstration
of why tiny finite success is not evidence of a scalable selector.

### B. Sparse trinomials

The exact grammar is

```text
u * (z^e + a*z + b),
cost(e) <= 7,
cost(a)+cost(b) <= 1,
cost(u) <= 2.
```

There are

```text
57,519 valid expressions,
57,463 distinct sign patterns,
14,020,972 nominal training classes after leading patterns.
```

Exact result:

```text
training exact decoders: 0,
all-nontrivial exact decoders: 0.
```

The training-selected best expression is

```text
(B + lambda^4)
* (z^48 - lambda^2*z + B + 1).
```

Its accuracy is

| split | correct / total | accuracy |
|---|---:|---:|
| train | 434 / 726 | 59.78% |
| validation | 203 / 390 | 52.05% |
| test | 611 / 1248 | 48.96% |

### C. Shifted powers

The exact grammar is

```text
u * ((z+a)^e + b),
cost(e) <= 7,
cost(a)+cost(b) <= 1,
cost(u) <= 2.
```

There are

```text
81,789 valid expressions,
79,189 distinct sign patterns,
19,322,116 nominal training classes after leading patterns.
```

Exact result:

```text
training exact decoders: 0,
all-nontrivial exact decoders: 0.
```

The training-selected best expression is

```text
(-beta*n - lambda)
* ((z + beta^2 - lambda^2)^10 + 1).
```

Its accuracy is

| split | correct / total | accuracy |
|---|---:|---:|
| train | 434 / 726 | 59.78% |
| validation | 188 / 390 | 48.21% |
| test | 653 / 1248 | 52.32% |

## Selection-capacity diagnostic

For each single-expression family, the result records the smallest number of
correct training bits whose binomial tail, multiplied by the number of distinct
candidate classes, is at most `0.05` under independent random signs.

This is a family-size capacity diagnostic, not a p-value for the structured
carry target.

| family | observed best train | 5% random-union gate |
|---|---:|---:|
| one power-affine factor | 424 / 726 | 435 / 726 |
| sparse trinomial | 434 / 726 | 442 / 726 |
| shifted power | 434 / 726 | 442 / 726 |

Every observed maximum lies below its family-wise random-capacity gate.

The mean test accuracies of the twenty best training-selected expressions are

```text
50.11% for one power-affine factor,
50.32% for sparse trinomials,
50.01% for shifted powers.
```

Thus the training excess does not persist on the two largest frozen groups.

## Interpretation

The strongest conclusion is not merely another zero-hit count. It is the
failure of cross-curve transfer.

Instance-specific interpolation is abundant, but a single public expression
from this grammar cannot even fit the eight training curves exactly. The best
training-selected candidates regress to chance on held-out curves. Within this
scope, the carry table behaves like instance-specific information rather than
a low-description public invariant.

This materially narrows the surviving route. A useful direct selector must now
have at least one of the following properties:

1. a substantially richer uniform expression tree;
2. three or more coupled power-affine factors with a public coefficient rule;
3. additional canonical invariants beyond `z=x^3` and the listed public atoms;
4. a canonical p-adic construction whose output descends to the base field;
5. a structural theorem not represented by finite expression enumeration.

## Claim boundary

This package does not establish an asymptotic circuit lower bound. It does not
cover arbitrary arithmetic circuits, canonical p-adic outputs, or all possible
public coefficient-generation algorithms. The `lambda` atom is an integer
representative reduced into the base field; it is not asserted to be a
canonical geometric field invariant.

No result here evaluates an unknown secp256k1 point, private scalar, wallet, or
external target. No sub-square-root ECDLP algorithm is established.

## Next gate

The next package should move from grammar growth toward a structural invariant:

```text
DIRECT-GLV-QUOTIENT-SPECTRUM-013
```

It should place `h` on the cyclic quotient

```text
F_n^* / < -1, lambda >
```

and measure exact Fourier spectrum, autocorrelation, binary linear complexity,
and cross-curve spectral stability against matched random controls. The aim is
to determine whether any common low-dimensional representation survives after
uniform low-description formulas have failed.
