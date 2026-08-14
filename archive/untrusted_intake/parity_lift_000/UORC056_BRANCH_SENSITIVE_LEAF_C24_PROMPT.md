# GPT Pro focused continuation

## BRANCH-SENSITIVE-LEAF-CLASSIFICATION-073

Start from `research/uorc056-sign-blind-additive-c23`. Create a separate branch named `research/uorc056-branch-sensitive-leaf-c24`. Do not change `main`, `research/parity-lift-000`, or the C21-C23 branches.

Use only the public frozen curves, public generator replacements, public secp256k1 constants, and symbolic variables. Do not accept an external point with an unknown scalar, wallet, private key, production target, or user-supplied oriented root.

## Fixed input

C21 gives the exact norm-one Hilbert-90 twist

```text
R(y)R(-y)=1,
R(y)=H(y)/H(-y),
R(infinity)=1.
```

C22 proves linear charged support for every explicit half-divisor and for a valuation-transparent multiplicative grammar.

C23 proves a size-independent two-world theorem:

```text
if every leaf has the same value in the global branch worlds R and -R,
then every rational arithmetic circuit, determinant, and Sylvester resultant
constructed from those leaves also has the same value in the two worlds.
```

Addition can create new zeros, so do not reuse the C22 support-union theorem for additive circuits. Use the C23 branch-indistinguishability invariant instead.

The surviving object must therefore contain a genuinely branch-sensitive public primitive.

## Central target

Find a public leaf or coefficient generator

```text
L(E,G,Q)
```

with a rigorously proved nontrivial transformation under the global branch flip:

```text
L_- != L_+
```

or an equivalent branch-odd relation that permits exact recovery of the canonical value represented by `R(Q)`.

Its complete cost must satisfy

```text
C_preprocessing + C_advice + C_memory
+ C_representation + C_online
= O(n^(1/2-epsilon)).
```

A value of `R`, one oriented square root, one half-divisor coefficient, one hidden scalar-index interval, one branch bit, or one equivalent normalization value is forbidden input.

## Mandatory attack order

### A. Candidate inventory

Classify, rather than rediscover blindly, the strongest surviving families already suggested by the repository:

```text
twisted theta characteristics,
rows from genuinely different line bundles or section spaces,
Heisenberg or metaplectic intertwiners,
p-adic analytic continuation,
asymmetric Frobenius lifts,
higher absolute torsion jets,
GLV-orbit sections with a carry multiplier different from the point-function multiplier,
addition-enabled elimination coefficients,
sparse translation resultants with non-fixed coefficients,
compressed determinant or resultant coefficients not generated from norm-only data.
```

For each family, identify its exact public inputs and whether it is already covered by C23.

### B. Four transformation laws

For every candidate prove or compute separately:

```text
global branch flip R -> -R,
geometric involution tau(y)=-y,
generator inversion G -> -G,
generator replacement G -> [u]G.
```

Do not confuse the global branch flip with the geometric involution. For the Hilbert-90 twist, `tau(R)=R^-1`, while C23 concerns `R -> -R`.

A candidate with identical values under the global branch flip is sign-blind and is immediately rejected by C23, regardless of determinant dimension or circuit depth.

### C. No-smuggling audit

Trace every normalization constant, path choice, local trivialization, square-root convention, p-adic lift, theta characteristic, row coefficient, and pivot rule back to public data.

Reject a candidate if constructing it requires:

```text
one value of R or H,
one oriented root,
one hidden half-divisor choice,
unknown scalar k,
a table with Omega(sqrt(n)) charged orientation state,
an uncharged analytic continuation path carrying the missing sign.
```

### D. Exact elimination test

If the candidate is a determinant or resultant coefficient, separate two statements:

```text
the determinant/resultant transports the coefficient,
the coefficient is publicly constructed.
```

The first statement alone is not progress. Supply the full coefficient-generation algorithm and show that it does not factor through C23 sign-blind data.

### E. Exact branch extraction

A positive candidate must return an exact branch-odd output on every nonexceptional subgroup point. State all exceptional points and collision rules.

Required checks:

```text
all subgroup points on frozen curves,
held-out curves,
public generator replacements,
global branch covariance,
generator covariance,
no global sign fitted after seeing labels.
```

### F. Complete cost ledger

Charge:

```text
coefficient generation,
field extensions,
precision,
preprocessing,
advice,
memory,
representation,
online evaluation,
branch extraction,
exception handling.
```

A degree-n determinant evaluated by a black box is not compact unless the black-box construction and state are also below the gate.

### G. Scoped negative theorem

If no candidate survives, state one exact mechanism class and prove why every member is sign-blind, dependent on a known public equation, or requires a charged branch-sensitive resource of forbidden size.

Do not claim an unrestricted arithmetic-circuit lower bound.

### H. Formalization

Extend Lean only with exact abstract theorems proved in the package. Keep finite screens, theta identities, analytic assumptions, and elliptic-curve geometry clearly separated from kernel-checked algebra.

## Positive gate

A surviving leaf must provide:

```text
exact nontrivial global-branch law,
public construction from E,G,Q,
no hidden orientation advice,
canonical normalization,
all-point correctness,
generator covariance,
complete cost below n^(1/2-epsilon),
reproducible code,
held-out validation.
```

## Negative gate

A negative result must provide:

```text
exact candidate family,
proved transformation law,
reason it is sign-blind or dependent,
charged resource that would be required to escape,
replay or formal certificate,
classes not covered.
```

## Required final flags

```text
branch_sensitive_public_leaf_found=?
branch_sensitive_leaf_constructible_without_advice=?
twisted_theta_survives_C23=?
p_adic_branch_path_publicly_canonical=?
new_GLV_carry_multiplier_found=?
nonfixed_resultant_coefficient_found=?
compressed_nonfixed_determinant_found=?
complete_cost_gate_passed=?
compact_branch_odd_evaluator_found=?
sub_sqrt_evaluator_found=?
parity_oracle_found=?
sub_sqrt_ecdlp_found=?
```
