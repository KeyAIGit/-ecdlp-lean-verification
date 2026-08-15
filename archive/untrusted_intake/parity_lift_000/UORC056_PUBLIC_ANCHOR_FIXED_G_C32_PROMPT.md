# GPT Pro focused continuation

## PUBLIC-ANCHOR-FIXED-G-NONLINEAR-PROPAGATION-082

This prompt supersedes the wording in
`UORC056_FIXED_G_NONLINEAR_SOURCE_C32_PROMPT.md` wherever that file speaks of
creating the first branch-sensitive value.

Start from `research/uorc056-oriented-source-rank-c31`. Create a separate branch
named `research/uorc056-public-anchor-propagation-c32`. Do not modify `main`,
`research/parity-lift-000`, or the C23-C31 branches.

## Public anchor

The oriented branch is already normalized at the generator:

```text
Y_G(x(G))=-y(G).
```

Thus C32 is not allowed to claim that the input contains no oriented datum. It
contains exactly one public oriented anchor. The unresolved task is to propagate
that anchor to

```text
Q=[k]G
```

without receiving `k`, its bits, a branch table, a dense signed divisor, all
intermediate orbit values, or a full dual phase.

The target remains

```text
Y_G(x(Q))/y(Q)=(-1)^k
```

with complete charged cost

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon)).
```

## Required separation

For every proposal distinguish three objects:

```text
Anchor(E,G)=-y(G),
Propagate(E,G,Q,Anchor),
Decode(E,G,Q,PropagatedState).
```

A local rational transform of a value already available at `Q` is covered by
C30. A fixed linear dictionary for all generator replacements is covered by
C31 in characteristic zero. C32 must implement a nonlocal propagation law from
`G` to `Q` for one fixed generator.

## Mandatory attack order

### A. Public jump law

Search for an exact law that moves the anchor over a long public displacement
without walking every local edge:

```text
Jump(P,R)=Y_G(x(R))/Y_G(x(P))
```

or a projective equivalent. The jump must be computable from public
`E,G,P,R` and compact public state, and must satisfy composition:

```text
Jump(P,R)Jump(R,S)=Jump(P,S).
```

Do not accept a jump whose construction uses the scalar distance between
`P` and `R`.

### B. Divide-and-conquer integration

The known local cocycle under translation is public, but black-box walking is
linear. Seek a nonlocal segment identity with recursively composable state.

For every tree record:

```text
leaf generator,
segment endpoints,
state width,
composition cost,
wraparound treatment,
number of materialized leaves,
branch normalization inherited from G.
```

A balanced tree over `Theta(n)` leaves remains linear. A standard
baby-step/giant-step state at `Theta(sqrt(n))` does not meet the fixed-epsilon
gate.

### C. Target-dependent modular composition

Write

```text
Y_G(X)=A(X^3)+X B(X^3)+X^2 C(X^3).
```

Attempt to evaluate `A,B,C` only at `T=x(Q)^3`, using the public anchor to
select the correct global branch. Do not build their coefficient vectors.

Candidate mechanisms:

```text
recursive remainder trees,
Krylov or transposed quotient-algebra action,
minimal-polynomial towers,
recursive resultants,
CM-compatible modular composition,
public Frobenius-id kernel operators,
noncommutative transfer matrices.
```

For each route identify exactly how the one anchor influences the state at the
query. A branch choice injected only at the final local step is circular.

### D. Anchor-aware Hilbert-90 integration

The local cocycle has cyclic norm one. Standard Hilbert-90 lifts are dense or
ambiguous up to a global scalar. The public anchor fixes that scalar at one
component. Determine whether the normalized lift can be evaluated at one query
without constructing the full orbit vector.

Charge:

```text
normalization,
linear-system state,
cyclic convolution,
minimal polynomial,
field extensions,
all queried cocycle edges.
```

A solution of an `n`-dimensional circulant system is not compact merely because
only one coordinate is returned.

### E. Product, determinant, and resultant routes

A determinant or resultant may aggregate the anchor only if its coefficient
generator carries the anchor nonlocally. Sign-blind coefficients remain covered
by C23.

Investigate:

```text
ordered endpoint minors,
anchor-normalized first variations,
recursive oriented resultants,
noncommuting translation pairs,
projective segment transfer matrices.
```

Prove the exact anchor-to-output law, not only finite injectivity.

### F. Fixed-generator transposed source

C31 does not close a nonlinear compiler for one fixed `G`. A transposed method
must generate the action of the one source from the anchor on demand. It may not
receive the source vector or a basis spanning every generator replacement.

State the source functional, generation algorithm, rank/query model, and all
preprocessing. Transposition of a dense already-oriented source receives no
credit.

### G. Public-Q replay

The evaluator must be called with public points. The harness may know scalar
labels only to score correctness.

Required coverage:

```text
all nonzero points on frozen curves,
G -> -G,
Q -> -Q,
GLV rotations,
public generator replacements for covariance only,
all zeros, poles, and wrap points,
held-out curves.
```

### H. Complete cost and formalization

Charge every group operation, kernel map, product-tree node, Krylov vector,
minimal polynomial, field element, branch normalization, retry, and online
operation.

Formalize exact jump, composition, anchor normalization, and scoped lower-bound
identities in Lean where practical. Keep finite screens and unproved complexity
claims separate.

## Positive gate

```text
public anchor explicitly consumed,
nonlocal propagation law defined,
no scalar distance or hidden index,
exact all-point public-Q correctness,
sub-root total state and time,
generator/query covariance,
reproducible held-out validation,
exact oriented-root or parity theorem.
```

## Negative gate

Name an exact propagation grammar, then prove an indistinguishability, query,
state, source-rank, or representation lower bound. Do not claim an unrestricted
circuit or ECDLP lower bound.

## Required flags

```text
public_oriented_anchor_used=?
nonlocal_jump_law_found=?
jump_composition_proved=?
sublinear_segment_integration_found=?
sublinear_anchor_normalized_hilbert90_found=?
sublinear_modular_composition_found=?
transposed_source_generated_from_anchor=?
scalar_distance_used=?
all_point_public_Q_replay_passed=?
exact_oriented_root_extraction_found=?
exact_parity_extraction_found=?
complete_cost_gate_passed=?
compact_branch_odd_evaluator_found=?
sub_sqrt_evaluator_found=?
parity_oracle_found=?
sub_sqrt_ecdlp_found=?
```
