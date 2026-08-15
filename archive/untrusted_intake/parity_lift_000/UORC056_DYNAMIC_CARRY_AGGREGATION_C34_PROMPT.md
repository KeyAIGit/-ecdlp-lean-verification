# GPT Pro focused continuation

## DYNAMIC-ORIENTED-CARRY-AGGREGATION-C34

Start from `research/uorc056-oriented-addition-cocycle-c33`. Create a separate
branch named `research/uorc056-dynamic-carry-aggregation-c34`. Do not change
`main`, `research/parity-lift-000`, or the C29-C33 branches.

Use only symbolic variables, public frozen toy curves, public prime orders,
public secp256k1 constants and deterministic public coefficient families. Do
not accept an external unknown-scalar point, wallet, private key, production
target, numeric `k`, its bits, a carry table, an oriented-root table, a faithful
dual phase or target-dependent advice.

## Fixed input from C33

For

```text
Q=[k]G,
sigma_G(Q)=(-1)^k,
```

define

```text
C_G(P,R)=sigma_G(P)sigma_G(R)sigma_G(P+R).
```

C33 proves

```text
sigma_G(P+R)=C_G(P,R)sigma_G(P)sigma_G(R),
C(P,R)C(P+R,T)=C(R,T)C(P,R+T),
sigma_G(Q)=C_G([2^-1]Q,[2^-1]Q).
```

Thus one direct carry query is parity-complete. A binary or base-field scalar
gauge that removes carry is parity itself; an extension-field escape imports a
faithful order-n character. Fixed separated carry dictionaries have rank n,
and fixed-jump products require all n-1 nontrivial thresholds.

The only surviving addition-chain possibility is to aggregate several dynamic
carry factors without evaluating a parity-complete carry in isolation.

## Central target

Choose a public addition circuit for the known relation

```text
[n]Q=O.
```

Recursively expand every oriented addition gate. This gives an exact identity

```text
sigma_G(Q)=public_phase * product_i C_G([a_i]Q,[b_i]Q)^(epsilon_i),
```

where the integer labels `a_i,b_i` and exponents `epsilon_i in {0,1}` are public
and depend only on the chosen circuit for `n`.

Construct or exclude an exact public-Q evaluator for the complete product with
charged cost

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon)).
```

The evaluator may not expose an individual diagonal carry that is already
parity under a public invertible scalar change.

## Mandatory attack order

### A. Addition-circuit compiler

Implement a compiler that accepts a public addition DAG for an integer `m` and
returns the carry exponents in the full expansion of `sigma([m]Q)`. Track DAG
sharing modulo two exactly. Verify the terminal identity for several public
chains for `m=n`.

### B. Chain-independence and cocycle moves

Use the C33 cocycle identity to prove that two addition DAGs for the same
integer produce equivalent carry products. Classify elementary reassociation,
commutation and doubling moves. Determine whether every product reduces to one
parity-complete diagonal carry or whether some chain yields a genuinely
different aggregate.

### C. Miller and elliptic-net telescoping

Test whether the full selected carry product is the quadratic, cubic, sextic or
exact field value of one public object built from

```text
Miller line functions,
division polynomials,
elliptic-net Ward recurrences,
net polynomials,
normalized endpoint products,
Hilbert-90 cocycles.
```

The code must consume only `E,G,Q` and public chain labels. Numeric `k` may be
used by the harness only for scoring.

### D. Divisor and covariance audit

For every proposed aggregate, derive its divisor and transformation under

```text
G -> -G,
Q -> -Q,
Q -> [u]Q,
GLV rotation.
```

Reject generator-blind aggregates immediately. A global phase inserted after
the fact does not count unless its public construction is proved.

### E. Dynamic carry rank and query grammar

If no telescoping object is found, define an exact grammar for products or
rational combinations of dynamic carries

```text
C([a_i]Q,[b_i]Q).
```

Prove a collision, Fourier-support, divisor, rank, query or representation
lower bound for that declared grammar. Do not claim an unrestricted carry or
ECDLP lower bound.

### F. Complete cost ledger

Charge addition-DAG construction, every point multiple, line or net value,
field extension, character extraction, zero handling, preprocessing, advice,
memory, representation and online operations.

### G. Formalization

Formalize carry-product compilation, cocycle invariance under DAG moves,
selected exact identities and fixed secp256k1 arithmetic in Lean where
practical. Keep finite screens and unproved complexity claims outside the
kernel-checked boundary.

## Positive gate

A positive result requires

```text
one exact dynamic carry aggregate,
no individual parity-complete carry oracle,
no numeric-k control,
all-point public-Q replay,
generator covariance,
complete sub-root cost,
exact parity theorem.
```

## Negative gate

A negative result requires

```text
one exact dynamic-carry grammar,
proved invariant or lower bound,
complete exceptional-set treatment,
classes covered and not covered.
```

## Required flags

```text
addition_dag_compiler_built=?
carry_product_chain_independence_proved=?
all_public_chains_reduce_to_parity_complete_carry=?
miller_carry_aggregate_found=?
elliptic_net_carry_aggregate_found=?
hilbert90_carry_aggregate_found=?
dynamic_carry_lower_bound_proved=?
all_point_public_Q_replay_passed=?
exact_parity_extraction_found=?
complete_cost_gate_passed=?
compact_branch_odd_evaluator_found=?
sub_sqrt_evaluator_found=?
parity_oracle_found=?
sub_sqrt_ecdlp_found=?
```
