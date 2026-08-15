# GPT Pro focused continuation

## FIXED-G-NONLINEAR-SOURCE-COMPILER-082

Start from `research/uorc056-oriented-source-rank-c31`. Create a separate branch
named `research/uorc056-fixed-g-nonlinear-source-c32`. Do not modify `main`,
`research/parity-lift-000`, or the C23-C31 branches.

Use only symbolic variables, public frozen toy curves, public prime orders,
public secp256k1 constants, and deterministic public coefficient families. Do
not accept an unknown-scalar external point, private key, wallet, production
target, numeric scalar `k`, scalar bits, a dense oriented source vector, a
branch table, every marked-generator source, or a full dual character as
uncharged input.

## Fixed boundary

C30 proves that local rational certificates do not create orientation. C31
proves that a fixed characteristic-zero linear dictionary containing every
marked-generator oriented source needs `(n-1)/2` independent directions. The
surviving route is therefore nonlinear and fixed-generator:

```text
input: one public E,G,Q,
output: Y_G(x(Q)) or (-1)^k,
no fixed dictionary spanning all G->[u]G sources.
```

The unchanged total cost gate is

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon)).
```

## Mandatory attack order

### A. One-generator compiler contract

For every candidate distinguish:

```text
compile(E,G,n),
evaluate(compiled_state,Q),
decode(output).
```

Record the exact transformation under

```text
G -> -G,
G -> [u]G,
Q -> -Q,
Q -> alpha Q.
```

The compiler may depend on the one input generator. It may not import a table
for all generator replacements.

### B. Nonlinear source generation

Search for a circuit producing the action of the oriented source without
materializing its coordinates. Candidate mechanisms include

```text
nonlinear recurrence in a quotient algebra,
recursive oriented resultants,
product trees with compressed leaf generation,
addition-chain evaluation of CM components A,B,C,
black-box polynomial remainders,
noncommutative transfer matrices,
exterior or determinant states with a genuinely branch-sensitive coefficient.
```

At each step identify where the first branch-sensitive value appears. C23
rejects a circuit whose complete primitive inputs remain branch-even.

### C. Fixed-G modular composition

Write

```text
Y_G(X)=A(X^3)+X B(X^3)+X^2 C(X^3).
```

Attempt to evaluate the three components at `T=x(Q)^3` from a short compiler.
Do not construct their coefficient vectors.

For every composition route record

```text
state width,
degree growth,
number of public kernel-map calls,
minimal-polynomial or quotient-algebra size,
branch normalization,
zero and pole handling,
all G-dependent constants.
```

A degree-Theta(n) object is admissible only with an explicit short circuit.

### D. Product-tree and factorial escape

Earlier packages close explicit linear-size products and ordinary two-level
square-root blocking. A positive tree must have a new recursive identity that
reduces both leaf generation and tree width.

Reject any construction with

```text
Theta(n) leaves,
Theta(sqrt(n)) stored blocks,
a hidden endpoint index,
a q^k phase,
a dense signed divisor.
```

### E. Transposed on-demand action

A transposed evaluator is admissible only if the oriented source action is
generated on demand. It may not receive the source vector or a fixed basis
containing all marked-generator sources.

Name the linear functional, its source-generation circuit, and the exact rank
or query model. Charge every Krylov vector, moment, basis coordinate, and
verification certificate.

### F. secp256k1 finite-characteristic audit

If the linear route is retained, determine the rank modulo the actual
secp256k1 field prime of the structured half-source matrix

```text
M_(u,r)=(-1)^canonical(r*u^(-1) mod n).
```

A positive modular rank certificate must be sublinear to construct and
independently verifiable. An explicit `(n-1)/2` matrix is forbidden.

Do not infer base-field rank from characteristic-zero rank alone.

### G. Exact replay

Any positive candidate must be called with public points, never numeric scalar
labels. The harness may know labels only to score correctness.

Required coverage:

```text
all nonzero points on frozen curves,
all marked generators used only for covariance validation,
held-out curves,
G -> -G,
Q -> -Q,
GLV rotations,
all exceptional denominators,
all branch collisions.
```

### H. Formalization and cost

Formalize exact compiler identities and scoped obstructions in Lean where
practical. Keep finite screens and unproved complexity assumptions separate.

Charge every preprocessing, advice, memory, representation, online operation,
field extension, random sample, and retry.

## Positive gate

```text
one explicit fixed-G nonlinear compiler,
first branch-sensitive value generated from public inputs,
no all-generator linear dictionary,
exact all-point public-Q correctness,
complete sub-root ledger,
reproducible held-out validation,
exact oriented-root or parity theorem.
```

## Negative gate

Name an exact compiler grammar, then prove a branch invariant, source-rank
bound, query lower bound, or representation lower bound. Do not claim an
unrestricted circuit or ECDLP lower bound.

## Required flags

```text
fixed_G_compiler_defined=?
first_branch_sensitive_value_generated=?
all_generator_dictionary_used=?
nonlinear_source_circuit_found=?
sublinear_modular_composition_found=?
sublinear_product_tree_found=?
transposed_source_generated_on_demand=?
secp_base_field_source_rank_proved=?
all_point_public_Q_replay_passed=?
exact_oriented_root_extraction_found=?
exact_parity_extraction_found=?
complete_cost_gate_passed=?
compact_branch_odd_evaluator_found=?
sub_sqrt_evaluator_found=?
parity_oracle_found=?
sub_sqrt_ecdlp_found=?
```
