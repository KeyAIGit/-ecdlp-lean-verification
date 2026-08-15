# GPT Pro focused continuation

## TARGET-DEPENDENT-ORIENTED-COMPILER-079

Start from `research/uorc056-autonomous-state-rigidity-c29`. Create a separate branch named `research/uorc056-target-dependent-oriented-compiler-c30`. Do not change `main`, `research/parity-lift-000`, or the C23-C29 branches.

Use only symbolic variables, public frozen toy curves, public prime orders, public secp256k1 constants, and deterministic public coefficient families. Do not accept an external unknown-scalar point, wallet, private key, production target, numeric `k`, its bits, a scalar-indexed table, a dual-character table, a dense oriented-root table, a half-orbit label table, or target-dependent advice that already contains the answer.

## Fixed input

The target remains

```text
Q=[k]G,
Y_G(x(Q))/y(Q)=(-1)^k.
```

C27 closes broad public-Q linear, trace, and coordinate-sparse Krylov states. C28 closes low-pole-degree rational states and ordinary low-degree `A/B` coordinates. C29 closes fixed autonomous state compression:

```text
a state-only exact autonomous orbit requires n semantic values,
global genus-zero autonomous states are excluded for secp256k1,
global genus-one autonomous states are isogeny recodings.
```

Therefore C30 must not propose one fixed update `S(P+G)=R(S(P))`. It must construct or exclude a genuinely nonautonomous compiler.

## Central target

Construct a public uniform compiler

```text
Compile(E,G,n,Q) -> (R_0,...,R_m,seed,decoder)
```

such that

```text
state_0=seed(E,G,Q),
state_(i+1)=R_i(E,G,Q,state_i),
Decode(E,G,Q,state_m)=(-1)^k,
```

with complete charged cost

```text
C_preprocessing + C_advice + C_memory
+ C_representation + C_online
=O(n^(1/2-epsilon)).
```

The sequence may depend on public coordinates, recursion level, the public binary expansion of `n`, GLV constants, and deterministic branch-free conditions. It may not depend on numeric `k` or a value equivalent to `k`.

## First target

The first output target is

```text
S_AB(Q)=(A(T),B(T)),
T=x(Q)^3,
Y_G(X)=A(X^3)+XB(X^3)+X^2C(X^3).
```

The direct decoder is

```text
(-1)^k=(2A^2+2AxB-x^2B^2)/(2yA)
```

on its regular domain.

Do not materialize the coefficient vectors of `A`, `B`, `C`, `Y_G`, or the half-kernel.

## Mandatory attack order

### A. Compiler contract

For every proposal list:

```text
public inputs,
seed coordinates,
map family R_i,
number of maps,
map description sizes,
state dimension,
field extensions,
branch conditions,
decoder,
exceptional set,
generator covariance.
```

### B. Divide-and-conquer oriented products

Derive product-tree, half-product, and transposed identities for the oriented Miller/elliptic factorial objects. Search for recurrences that split the public order `n` rather than the hidden endpoint `k`.

Reject a recurrence whose child selection uses `k`, one bit of `k`, or membership in an oriented half.

### C. Modular composition

Test whether `A(T)` and `B(T)` admit a uniform composition chain

```text
F_0 o F_1 o ... o F_m
```

or a bounded-width vector composition. Charge every coefficient and the compiler that generates each `F_i`.

### D. Addition-chain and CM maps

Use public maps including

```text
Q -> [2]Q,
Q -> alpha Q,
T -> -(T+4b)^3/(27T^2),
```

but distinguish a public transformation of `Q` from a rule that knows which scalar preimage or branch to choose.

### E. Nonlocal jump identities

Search for an exact jump law evaluating a segment or endpoint potential from public endpoints without walking each local cocycle edge. Include Miller, elliptic-unit, Hilbert-90, resultant, norm/trace, and transposed-evaluation candidates.

### F. Compiler lower-bound grammars

If no positive mechanism appears, choose one exact grammar and prove a scoped obstruction. High-value grammars include:

```text
bounded-width composition with fixed public map library,
branch-free straight-line programs with generator-blind constants,
product trees whose partition is independent of Q,
transposed linear evaluation with compactly generated dense probes,
constant-number norm/trace towers,
addition chains with only public scalar multipliers.
```

### G. All-point public-Q replay

Any positive evaluator must receive `Q`, never `k`, and pass:

```text
all nonzero scalars on every frozen curve,
all public generator replacements,
G -> -G,
Q -> -Q,
three GLV rotations,
all denominator zeros and degree drops.
```

The harness may know `k` only to score the output.

### H. Complete cost gate

Charge:

```text
compiler generation,
all map coefficients,
state and map storage,
preprocessing,
advice,
field extensions,
branch handling,
online operations,
verification repetitions.
```

### I. Formalization

Formalize exact recurrence identities, branch-collision theorems, composition budgets, and fixed arithmetic in Lean where practical. Do not label finite screens or unproved circuit complexity claims as kernel-checked.

## Positive gate

A positive result must include:

```text
one literal public-Q nonautonomous compiler,
no scalar or branch leakage,
all-point correctness,
generator covariance,
complete sub-square-root cost,
reproducible code,
held-out validation.
```

## Negative gate

A negative result must include:

```text
one exact compiler grammar,
a proved invariant, collision, query, width, or representation lower bound,
complete exception handling,
classes covered and not covered.
```

## Required final flags

```text
target_dependent_compiler_found=?
public_branch_sensitive_seed_found=?
joint_A_B_evaluator_found=?
modular_composition_chain_found=?
nonlocal_jump_identity_found=?
bounded_width_composition_blocked=?
all_point_public_Q_replay_passed=?
exact_parity_extraction_found=?
complete_cost_gate_passed=?
compact_branch_odd_evaluator_found=?
sub_sqrt_evaluator_found=?
parity_oracle_found=?
sub_sqrt_ecdlp_found=?
```
