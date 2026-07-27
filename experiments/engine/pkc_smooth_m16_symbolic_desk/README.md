# PKC smooth-subgroup M16 symbolic desk

This directory records the non-experimental desk result for the first
secp256k1 arity at which the registered PKC 2016 arithmetic predicates both
pass:

```text
m = 16
D = 2 * 3 * 7 * 13441 = 564522.
```

The result is a scoped blocker, not a solver result, attack hypothesis, or
authorization.  The exact presentation counts reduce the missing S17 cost
quantity to a partial one, but they do not determine solving degree, recovery
rate, relation rank, sparse linear algebra, or total work.

## Exact presentation counts

The artifact compares three non-materialized presentations with the target
x-coordinate treated as a fixed constant:

| presentation | variables | equations | maximum input degree |
|---|---:|---:|---:|
| direct S17 plus source factor chain | 64 | 65 | 524288 |
| recursive S3 plus source factor chain | 78 | 79 | 13441 |
| recursive S3 plus quadratic source-factor circuit | 398 | 399 | 4 |

The direct S17 has per-leaf degree 32768 and target-specialized total-degree
upper bound 524288.  Its actual expanded support is unknown.  The number
`32769^16` in the artifact is only a dense rectangular support capacity.
The direct matrix-template count is conditional on assigning that upper-bound
degree to the specialized relation.  If specialization lowers the degree, its
row count changes; the recorded value is not a bound for the changed profile.

For secp256k1,

```text
S3(x,y,z)
  = x^2 y^2 + x^2 z^2 + y^2 z^2
    - 2(x^2 y z + x y^2 z + x y z^2)
    - 28(x + y + z).
```

This has nine monomials when all three variables are symbolic.  The one S3
node containing a fixed target has three terms when that target x-coordinate
is zero and nine otherwise.  The artifact retains both cases rather than
assuming a target value.

The source map factors the exponent through `2, 3, 7, 13441`.  Applying the
standard left-to-right binary chain separately to those four source maps costs
`1 + 2 + 4 + 17 = 24` multiplication gates per factor coordinate.  With the
final output constrained to one, this gives 23 auxiliaries per coordinate,
384 quadratic binomial equations over sixteen coordinates, and 368
membership auxiliaries.  This is a proved construction-specific upper bound,
not an optimal addition-chain claim.

## Conditional matrix envelopes

For a system with `v` variables and equation degrees `d_j`, the committed
artifact records, at an explicitly selected total-degree cutoff `delta`,

```text
columns = binomial(v + delta, v)
rows    = sum_j binomial(v + delta - d_j, v)
```

before row deduplication.  It also multiplies `rows * columns` by a conditional
32-byte dense field-element size.  These are raw template capacities at the
stated cutoff.  They are not solving-degree estimates, solver-memory bounds,
or evidence that a dense algorithm would be used.

## Factor-base and recovery boundary

The membership layer itself is exact.  Since `D` divides `p-1`,
`x^D - 1` has exactly `D` simple roots in `F_p` and the polynomial source map
has no denominator components.

The usable curve factor base is not thereby known.  If

```text
S_H = sum_{x in H} chi(x^3 + 7),
```

then the number of x-coordinates in `H` that lift to secp256k1 is
`U = (D + S_H)/2`, and the signed point count is `2U`.  There are no zero-y
roots because secp256k1 has no rational two-torsion.  The order-three GLV
action partitions usable coordinates into triples, so a GLV-aware logarithm
table would have `U/3` factor columns.  Neither `U` nor relation rank is
currently known.  The artifact binds this conditional accounting to the
repository's exact curve-cardinality, full-group, GLV eigenvalue, and
three-element nonfixed-orbit theorems.

The integer `ceil(sqrt(n))` is retained only as an uncalibrated generic
reference ceiling.  The artifact does not call it a matched Pollard-rho
baseline: system solving, field work, group work, parallelism, and
equal-success probability have not been converted to common units.

For a direct recovered x-tuple there are at most `2^16` raw factor-sign
assignments, or `2^15` classes when either sign of the target x-coordinate is
accepted.  Fixing one global sign permits a meet-in-the-middle split with
lists of at most `2^7` and `2^8` group sums, followed by exact curve and group
verification.  Recursive S3 recovery still needs a proof covering points at
infinity, tangent and duplicate fibers, extension-field lifts, and compatible
sign choices across the tree.

## Reproduce and validate

From the repository root:

```bash
python3 experiments/engine/pkc_smooth_m16_symbolic_desk/generate.py --check
python3 experiments/engine/pkc_smooth_m16_symbolic_desk/validate.py
python3 -m py_compile \
  experiments/engine/pkc_smooth_m16_symbolic_desk/generate.py \
  experiments/engine/pkc_smooth_m16_symbolic_desk/validate.py
```

To intentionally regenerate after review:

```bash
python3 experiments/engine/pkc_smooth_m16_symbolic_desk/generate.py --write
```

The validator imports neither the producer nor its helpers.  It independently
recomputes the decisive arithmetic, gate counts, presentation sizes, matrix
templates, recovery ceilings, canonical JSON, and artifact hash.
