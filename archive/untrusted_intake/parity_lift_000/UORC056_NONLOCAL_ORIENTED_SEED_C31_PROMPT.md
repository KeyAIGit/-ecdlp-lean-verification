# GPT Pro focused continuation

## NONLOCAL-ORIENTED-SEED-GENERATION-081

Start from `research/uorc056-local-branch-normal-form-c30`. Create a separate
branch named `research/uorc056-nonlocal-oriented-seed-c31`. Do not change
`main`, `research/parity-lift-000`, or the C23-C30 branches.

Use only symbolic variables, public frozen toy curves, public prime orders,
public secp256k1 constants, and deterministic public coefficient families. Do
not accept an external unknown-scalar point, wallet, private key, production
target, numeric `k`, its bits, a scalar-indexed table, a dense oriented-root
coefficient vector, a full dual character, or a pre-existing branch-sensitive
square root as uncharged input.

## Fixed input from C23, C29, and C30

C23 proves:

```text
rational arithmetic over branch-even leaves cannot manufacture orientation.
```

C29 proves:

```text
fixed autonomous state updates either fail on secp256k1 genus-zero state,
or recode the same scalar on an isogenous genus-one state.
```

C30 proves:

```text
every local rational certificate in one quadratic branch is E+O*Y;
O nonunit gives a branch collision;
O unit recovers Y by Y=O^(-1)(C-E);
K_H' and every public invertible local jet are only unit gauges.
```

Therefore C31 must not introduce another symbol that is locally rationally
equivalent to `Y_G`. It must identify a genuinely nonlocal operation that
creates the first branch-sensitive seed from public branch-even inputs.

The unchanged central target is

```text
Q=[k]G,
Eval(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
```

with complete charged cost

```text
C_preprocessing + C_advice + C_memory
+ C_representation + C_online
=O(n^(1/2-epsilon)).
```

## Central question

Construct or exclude in an exact declared model a public operation

```text
Seed(E,G,Q) in an algebraic or analytic state space
```

such that

```text
Seed changes under the oriented branch involution,
Seed is generated without receiving an oriented branch,
Seed determines Y_G(x(Q)) or parity with sub-root total cost.
```

A branch-sensitive output is not enough. The operation that creates its
orientation must be explicit and charged.

## Mandatory attack order

### A. Input and branch-world contract

For every candidate list:

```text
public inputs,
branch-even inputs,
new nonlocal primitive,
output state,
branch involution,
generator-negation law,
query-negation law,
all preprocessing and advice.
```

Run the two-world audit before computation. If all primitive inputs and the
primitive itself agree in the two branch worlds, C23 closes the candidate.

If the candidate receives a square root, path orientation, row normalization,
coefficient sign, dual point, or endpoint index, identify how that datum is
constructed from public `(E,G,Q)`.

### B. Oriented product-tree route

The target branch can be represented by alternating products over the marked
orbit. Search for a divide-and-conquer tree whose internal nodes are public and
whose root value at one query is branch-sensitive.

Required checks:

```text
leaf generation without scalar labels,
orientation of left/right child order,
composition law under interval concatenation,
public treatment of wraparound,
state width at every level,
number of leaves actually materialized,
G -> -G covariance,
all exceptional zeros and poles.
```

A balanced tree with `Theta(n)` leaves is still linear representation and does
not pass. A baby-step/giant-step tree at `Theta(sqrt(n))` does not satisfy a
fixed-epsilon improvement.

### C. Target-dependent modular composition

Study whether the CM components

```text
Y_G(X)=A(X^3)+X B(X^3)+X^2 C(X^3)
```

can be evaluated at `X=x(Q)` without constructing their coefficients.

Candidate mechanisms:

```text
addition-chain modular composition,
transposed evaluation against K_H,
Krylov evaluation of one functional,
minimal-polynomial towers,
recursive resultants,
remainder trees generated from public point operations,
black-box application of Frobenius-id kernel maps.
```

For every algorithm separate:

```text
numeric-index control,
public-Q control,
state dimension,
precomputation size,
number of kernel or group oracle calls,
branch-sensitive datum created at each step.
```

If the control flow uses the degree `k`, Euclidean quotients of `(n,k)`, the
binary expansion of `k`, or `q^k`, it is not a public-Q evaluator.

### D. Transposed oriented functional

A transposed method may compute one evaluation without materializing a dense
function. Formalize the exact linear functional and its source vector.

Reject the candidate if the source vector contains the oriented values

```text
((-1)^j y([j]G))_j
```

or an equivalent dense signed divisor. Transposition moves cost between source
and query; it does not make an oriented source free.

A positive result must generate the source action from public operations in
sub-root cost.

### E. Nonlocal determinant or resultant

C23 permits a determinant or resultant to transport a branch-sensitive entry,
but not to create one from sign-blind coefficients. C31 may use such an object
only if at least one coefficient is generated by a new public nonlocal law.

Investigate:

```text
ordered endpoint minors,
first variations with public Q,
noncommuting translation pairs,
orientation-sensitive elimination order,
resultants whose coefficient generation is itself target-dependent,
exact projective phases not removed by public normalization.
```

Apply C30 to every local postprocessing of the resulting value.

### F. Norm, trace, and continuation towers

A norm is usually branch-even. A trace is branch-sensitive only if a
branch-sensitive lift was selected first. For every tower specify:

```text
base algebra,
extension degree,
Frobenius action,
chosen embedding or path,
normalization at infinity,
descent map,
precision and representation cost.
```

A Hensel, theta, sigma, or Coleman continuation must explain how its starting
branch or path is public. Continuing a supplied branch is covered by C30 and is
not seed generation.

### G. One-point all-generator replay

Any positive candidate must be called with public points, not numeric scalars.
The harness may know the scalar only to score correctness.

Required replay:

```text
all nonzero scalars on every frozen toy curve,
all marked generators,
G -> -G,
G -> [u]G,
Q -> -Q,
GLV rotations,
all zeros, poles, degree drops, and branch collisions,
held-out curves not used to choose formulas.
```

### H. Complete cost ledger

Charge:

```text
point enumeration,
product-tree leaves and internal nodes,
kernel coefficients,
Krylov vectors,
minimal polynomials,
operator oracles,
field extensions,
precision,
randomness and exact verification,
preprocessing,
advice,
memory,
representation,
online operations,
all retries.
```

No object of size `Omega(sqrt(n))` may be hidden behind the word
"precomputation", "functional", "oracle", "basis", or "certificate".

### I. Formalization

Formalize exact branch-world invariants, compiler identities, and scoped
state/query bounds in Lean where practical. Keep finite screens, analytic
assumptions, and unproved complexity claims outside the kernel-checked label.

## Positive gate

A positive result must include:

```text
one explicit public nonlocal primitive,
proof that it creates rather than receives branch sensitivity,
one exact public-Q evaluator,
all-point correctness,
generator and query covariance,
complete O(n^(1/2-epsilon)) ledger,
reproducible code,
held-out validation,
exact parity or oriented-root theorem.
```

## Negative gate

A negative result must name an exact nonlocal grammar, for example:

```text
bounded-depth product trees with charged leaves,
rank-r transposed source functionals,
q public kernel-map queries,
fixed-width modular-composition towers,
branch-even norm/trace towers,
continuation algorithms with no public seed.
```

Then prove an invariant, source-size lower bound, query lower bound, or exact
branch collision. Do not claim an unrestricted circuit or ECDLP lower bound.

## Required final flags

```text
public_nonlocal_primitive_defined=?
primitive_creates_branch_sensitivity=?
branch_sensitive_seed_received_as_advice=?
sublinear_oriented_product_tree_found=?
sublinear_public_Q_modular_composition_found=?
sublinear_transposed_oriented_functional_found=?
nonlocal_resultant_seed_found=?
public_continuation_normalization_found=?
all_point_public_Q_replay_passed=?
exact_oriented_root_extraction_found=?
exact_parity_extraction_found=?
complete_cost_gate_passed=?
compact_branch_odd_evaluator_found=?
sub_sqrt_evaluator_found=?
parity_oracle_found=?
sub_sqrt_ecdlp_found=?
```
