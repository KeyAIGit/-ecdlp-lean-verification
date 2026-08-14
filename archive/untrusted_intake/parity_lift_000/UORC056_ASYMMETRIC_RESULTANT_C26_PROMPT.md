# GPT Pro focused continuation

## ASYMMETRIC-SPARSE-RESULTANT-EVALUATION-075

Start from `research/uorc056-sparse-circulant-c25`. Create a separate branch named `research/uorc056-asymmetric-resultant-c26`. Do not change `main`, `research/parity-lift-000`, or the C21-C25 branches.

Use only symbolic variables, public frozen prime orders, public toy curves, public secp256k1 constants, and deterministic public coefficient families. Do not accept an external point with unknown scalar, wallet, private key, production target, user-supplied branch value, or the hidden integer `k` as an algorithmic input.

## Fixed input

C25 classifies

```text
D_(a,b,c)(k)
  = det(aI+bT+cT^k)
  = Res_z(z^n-1,a+bz+cz^k).
```

The exact S3/Mobius action is known. Every zero-coefficient stratum is `k`-independent. For every prime order `n>11`, the `b=c`, `a=c`, and all-equal strata have opposite-parity stabilizer collisions certified by a complete residue cover modulo 55440.

The `a=b` stabilizer acts by

```text
k -> 1-k mod n,
```

whose canonical representative preserves parity. Thus the two surviving fixed-label lanes are

```text
A. a=b!=c,
B. a,b,c pairwise distinct.
```

Any extraction invariant under permutation of the coefficient labels is already blocked by C25. The surviving extraction must use the fixed labels nontrivially and must explain why those labels are canonically tied to the desired generator-relative Hilbert-90 branch.

The direct public-Q construction uses the regular representation of dimension `n`, an `n`-term root product, or a degree-`n` resultant. None passes the complete cost gate.

## Central target

Find one uniform public coefficient family

```text
(a_n,b_n,c_n)
```

in lane A or B and one exact extraction `Extract` such that for every admissible canonical scalar `k`, with `Q=[k]G`,

```text
Extract(D_(a_n,b_n,c_n)(G,Q))=(-1)^k
```

or equals the canonical branch represented by the Hilbert-90 twist.

The complete public-Q cost must satisfy

```text
C_preprocessing + C_advice + C_memory
+ C_representation + C_online
= O(n^(1/2-epsilon)).
```

The hidden integer `k`, all `n` roots of unity, a degree-`n` polynomial, an `n`-element subgroup table, or an `n`-dimensional translation matrix are forbidden as uncharged input.

## Mandatory attack order

### A. Fixed-label parity collision search

For lane A and lane B, search for exact same-label identities beyond the coefficient stabilizer. Sources may include:

```text
transpose or reversal of the circulant,
reciprocal polynomial identities,
Galois conjugation of the root product,
coefficient scaling,
resultant reciprocity,
Jacobi complement identities,
compound matrices,
Schur complements,
cyclotomic norm relations,
composition of Mobius identities returning the coefficient labels.
```

A collision is useful only if it preserves the fixed coefficient order and maps some `k` to an opposite-parity canonical representative.

Separate universal identities from finite-field accidental collisions.

### B. Exact extraction grammars

Test at least:

```text
exact determinant value,
zero/nonzero,
quadratic character,
fixed higher multiplicative characters,
trace or norm to a subfield,
valuation at fixed small primes for integer coefficients,
ratios of a bounded number of fixed-label coefficient variants,
logarithmic derivatives with respect to a,b,c,
bounded minors or cofactors,
coefficient-labeled ordered tuples.
```

For every extraction, prove covariance under

```text
G -> -G,
G -> [u]G,
Q -> -Q,
global Hilbert-90 branch flip.
```

A finite exact match is evidence only. A positive result requires one all-order theorem.

### C. Integer and finite-field coefficient families

Search coefficient families with charged description size `polylog(n)`, including:

```text
fixed small integers,
functions of n modulo a fixed modulus,
small roots of unity,
public GLV constants,
public curve coefficients,
coefficients derived from a fixed number of public point-function values.
```

Reject a family whose coefficient labels secretly contain a parity bit, an oriented root, a dual character, or a half-divisor choice.

### D. Lacunary resultant algorithms

Derive exact one-value algorithms for

```text
Res(z^n-1,a+bz+cz^k)
```

using:

```text
subresultant sequences,
Euclidean reduction,
continued fractions of n/k,
companion matrix compression,
linear recurrences,
transfer matrices,
cyclotomic norms,
sparse resultant algorithms,
modular composition,
baby-step giant-step determinant evaluation.
```

For each algorithm distinguish:

```text
complexity when numeric k is supplied,
complexity when only public Q=[k]G is supplied.
```

A polylogarithmic algorithm in the bit length of a supplied `k` is not a public-Q evaluator.

### E. Public-Q control flow

Explain how public group operations generate every branch, quotient, Euclidean step, or transfer-matrix choice used by the algorithm without learning `k`.

Potential valid controls must be functions of public `E,G,Q` and fixed constants. Invalid controls include:

```text
the Euclidean algorithm of the hidden pair (n,k),
the binary digits of k,
a table indexed by k,
a permutation of all subgroup points,
all characters of the cyclic subgroup.
```

If no compact control flow exists, state a scoped lower bound for the declared numeric-k recurrence or regular-representation grammar.

### F. Hilbert-90 branch bridge

Even an exact parity pattern in a determinant must be connected to the canonical endpoint-gauge branch. Prove one of:

```text
Extract(D(G,Q))=Y_G(x(Q))/y(Q),
Extract(D(G,Q))=(-1)^k,
Extract(D(G,Q)) times a public factor equals the hidden EDS residue.
```

Do not infer branch sensitivity merely from coefficient asymmetry.

### G. All-point and generator tests

A positive candidate must pass:

```text
all nonzero scalars on every frozen curve,
all public generator replacements,
held-out orders,
all determinant zeros and collisions,
no fitted global sign after labels are observed,
exact generator covariance.
```

### H. Cost ledger

Charge:

```text
coefficient generation,
field extensions,
character tables,
preprocessing,
advice,
memory,
resultant representation,
number of determinant queries,
public-Q control state,
online field operations,
zero handling,
branch extraction.
```

### I. Formalization

Formalize exact same-label symmetries, parity collisions, recurrence identities, and scoped no-go theorems in Lean where practical. Keep finite screens, heuristic character searches, and unproved sparse-resultant complexity claims separate from kernel-checked algebra.

## Positive gate

A positive candidate must include:

```text
one uniform fixed-label coefficient family,
one exact all-order parity or branch theorem,
public-Q realization without k,
all zero and collision rules,
generator covariance,
complete sub-square-root cost,
reproducible code,
held-out validation.
```

## Negative gate

A negative result must include:

```text
exact fixed-label coefficient or extraction grammar,
proved same-label invariant or control-flow obstruction,
opposite-parity collision or charged representation bound,
finite exceptions,
classes not covered.
```

Do not claim an unrestricted arithmetic-circuit or determinant lower bound.

## Required final flags

```text
a_eq_b_fixed_label_collision_proved=?
fully_asymmetric_fixed_label_collision_proved=?
exact_value_extraction_survives=?
quadratic_character_extraction_survives=?
higher_character_extraction_survives=?
bounded_variant_ratio_survives=?
sublinear_numeric_k_resultant_algorithm_found=?
sublinear_public_Q_control_flow_found=?
exact_Hilbert90_branch_bridge_found=?
complete_cost_gate_passed=?
compact_branch_odd_evaluator_found=?
sub_sqrt_evaluator_found=?
parity_oracle_found=?
sub_sqrt_ecdlp_found=?
```
