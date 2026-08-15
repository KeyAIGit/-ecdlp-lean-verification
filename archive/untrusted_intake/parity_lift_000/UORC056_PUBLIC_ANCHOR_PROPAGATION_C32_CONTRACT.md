# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C32 contract: public-anchor nonlocal propagation

Date: 2026-08-15

Status: active research contract. No positive evaluator is claimed.

## 1. Exact target

The canonical orientation is already public at the generator:

```text
Y_G(x(G))=-y(G).
```

For a public query

```text
Q=[k]G,
```

the task is to propagate this anchor and return

```text
Y_G(x(Q))/y(Q)=(-1)^k
```

with complete charged cost

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon)).
```

The algorithm may not receive `k`, its bits, a scalar distance, a branch table,
a dense oriented source, every local edge, a full dual phase, or a
square-root-width block state as free input.

## 2. Predecessor boundaries that must not be repeated

C32 is required to reuse, not rediscover, the following results.

### Local walking and seed tables

The local cocycle is public, but black-box edge propagation and multi-seed
nearest-anchor strategies meet the linear or square-root frontier. This is the
B18/local-support boundary.

### Endpoint versus global potential

An exact endpoint jump satisfying composition is equivalent, up to one public
anchor gauge, to a global potential. Renaming global integration as an endpoint
oracle is not a new route. This is the B14 endpoint/factorial equivalence.

### Dyadic and mixed-radix branching

Explicit branchless halving, radix trees, and candidate-state enumeration have
already been classified by packages 043 and 044. The width grows with the
number of unresolved residue classes and meets the square-root frontier before
full scalar recovery.

### Local algebraic postprocessing

C30 proves that every everywhere-regular local rational certificate in one
quadratic branch is `E+O*Y`. A nonunit `O` loses the branch on a component; a
unit `O` recovers `Y`. Kernel derivatives and invertible local jets are only
public gauges.

### Autonomous state machines

C29 closes fixed global autonomous algebraic updates: genus-zero state is
impossible for secp256k1, while genus-one state preserves the same scalar on an
isogenous curve.

### Fixed all-generator linear dictionaries

C31 proves characteristic-zero source rank `(n-1)/2`. C31A proves that the
actual secp256k1 base field has a forced nullity of at least two, but this only
reduces the possible linear dimension from `m` to at most `m-2`, still a
255-bit state scale. Exact production-field rank remains open.

## 3. Admissible surviving classes

C32 may advance only through a genuinely fixed-generator, nonlocal, nonlinear
mechanism such as:

```text
one-query modular composition without dense coefficients,
anchor-normalized Hilbert-90 integration without an n-state lift,
a recursive product identity with sub-root leaf generation,
a transposed source action generated on demand from the anchor,
a nonlocal determinant or resultant with a proved anchor-to-output law,
a continuation mechanism with an independently public path normalization.
```

Each candidate must identify exactly where the anchor enters and how it reaches
the target. A branch choice inserted only after a value equivalent to `Y_G(Q)`
has already been computed is circular.

## 4. Mandatory input contract

Every candidate must expose three maps:

```text
Anchor(E,G)=-y(G),
State=Propagate(E,G,Q,Anchor),
Output=Decode(E,G,Q,State).
```

The following values are forbidden as hidden control:

```text
k,
k mod b,
a binary or mixed-radix expansion of k,
a Euclidean chain involving k,
q^k or another faithful dual phase,
the path length from G to Q,
all oriented interpolation values.
```

## 5. Positive gate

A positive C32 result requires:

```text
one explicit public nonlocal propagation law,
proof that it consumes the public anchor,
no numeric-scalar control leakage,
all-point correctness on frozen curves,
G -> -G and Q -> -Q covariance,
held-out validation,
complete fixed-epsilon sub-root cost,
exact oriented-root or parity theorem.
```

## 6. Negative gate

A negative package must name an exact grammar and prove one of:

```text
branch indistinguishability,
query lower bound,
state-width lower bound,
source-rank lower bound,
representation-size lower bound,
reduction to a previously closed propagation mechanism.
```

No unrestricted circuit or ECDLP lower bound may be claimed.

## 7. First attack order

C32 will examine in this order:

```text
1. anchor-normalized one-coordinate Hilbert-90 evaluation;
2. fixed-G target-dependent modular composition of the CM components A,B,C;
3. on-demand transposed source generation;
4. recursive oriented resultants or transfer matrices;
5. exact production-field source-rank refinement only if the linear route is reused.
```

The dyadic/radix route is explicitly excluded from repetition.

## 8. Required flags

```text
public_oriented_anchor_used=?
nonlocal_propagation_law_found=?
numeric_scalar_control_used=?
sublinear_anchor_normalized_hilbert90_found=?
sublinear_fixed_G_modular_composition_found=?
transposed_source_generated_on_demand=?
recursive_oriented_resultant_found=?
all_point_public_Q_replay_passed=?
exact_oriented_root_extraction_found=?
exact_parity_extraction_found=?
complete_cost_gate_passed=?
compact_branch_odd_evaluator_found=?
sub_sqrt_evaluator_found=?
parity_oracle_found=?
sub_sqrt_ecdlp_found=?
```
