# UORC056 successor prompt

## QUADRATIC-HILBERT90-NORM-ONE-TWIST-071

Continue from C20 without reopening closed pair-product or branch-even square-root classes.

### Fixed input

For

```text
Z(P)=h_G(P)/h_G(P+G),
M(P)=N_phi(Z)(P)=product_(i=0)^2 Z(phi^i(P)),
K(P)=Z(P)Z(-P),
```

C20 proves

```text
M(P)M(-P)=N_phi(K)(P).                           (C21.1)
```

The right side has the exact compact form

```text
N_phi(K)(P)=
 (x(P)^3-x(P_(a-1))^3) /
 product_(j in {1,a,m})(x(P)^3-x(P_j)^3).        (C21.2)
```

Define the public factor

```text
C0(P)=
 (y(P)-y(P_(a-1))) /
 ((y(P)-y(P_1))(y(P)-y(P_a))(y(P)-y(P_m))).      (C21.3)
```

C20 verifies

```text
C0(P)C0(-P)=N_phi(K)(P).                         (C21.4)
```

Hence

```text
R(P)=M(P)/C0(P)                                  (C21.5)
```

is branch-odd and satisfies

```text
boxed:
R(P)R(-P)=1.                                     (C21.6)
```

On the seven-curve corpus `C0` has constant signature `6/3/9`, support `12`, and pole degree `9`, while `R` remains dense.

### Central target

Determine whether the norm-one cocycle `R` can be evaluated from public `E,G,Q` with fully charged cost

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon)).
```

A positive result must recover the actual branch-odd value. It may not receive `M`, `R`, a half-divisor, an oriented norm factor, or a square-root/factorization sign as advice.

### Mandatory package A: exact quadratic Hilbert-90 formulation

Work in

```text
L=F_p(y),
K0=F_p(y^2),
tau(y)=-y.
```

Prove and replay:

```text
R*tau(R)=1,
div(R)=D-tau(D)
```

for an explicit half-divisor `D`.

State Hilbert 90 precisely:

```text
R=H/tau(H).                                      (C21.7)
```

The tautological choice `H=1+R` is not a construction because it already requires `R`. Find an `H` from public compact data, or prove a lower bound for an explicitly declared `H` grammar.

### Mandatory package B: minimal half-divisor and gauge freedom

Classify all solutions of `(C21.7)`:

```text
H -> c(y^2)*H
```

for `c in K0^*`.

Compute:

```text
minimum divisor support of H,
minimum pole degree of H,
minimum coordinate degree after K0 gauge normalization,
number and structure of exceptional collisions.
```

Distinguish a dense half-divisor theorem from an unrestricted circuit lower bound.

### Mandatory package C: explicit rational reconstruction routes

Test the following independently:

```text
continued fractions in y,
Pade and rational interpolation,
half-gcd and subproduct trees,
transposed modular composition,
resultant and norm-equation factorization,
structured Toeplitz/Hankel solves,
addition-enabled straight-line programs,
recursive translation or GLV cocycles.
```

Charge all coefficients, stored divisor points, precomputation, and branch choices. A short output degree description is not enough if constructing its coefficients is linear.

### Mandatory package D: compact factor variation

The public factor `C0` is not unique. Search public factors

```text
C1(P)C1(-P)=N_phi(K)(P)                          (C21.8)
```

within a predeclared constant-degree grammar over the four public `y` values and their GLV/translation transforms.

For every candidate define

```text
R1=M/C1,
R1(P)R1(-P)=1.
```

Determine whether any factor choice reduces the norm-one twist divisor below the square-root boundary. Do not fit one factor separately to each hidden endpoint or query point.

### Mandatory package E: branch and canonicalization gate

A norm equation determines a torsor, not an oriented element. Analyze whether any proposed canonicalization

```text
least residue,
monic numerator/denominator,
value at a public base point,
leading coefficient,
p-adic lift,
Frobenius phase
```

is computable from public compact data and provably selects the same `R` as the endpoint gauge.

If the rule needs one value of `R`, one sign, or one half-divisor coefficient, charge it as orientation advice.

### Mandatory package F: bounded synthesis and held-out protocol

Predeclare a grammar over

```text
C0,
N_phi(K),
y,
y^2,
public Miller quotients,
constant-offset translations,
GLV transforms,
low-degree factors,
norm-one Mobius transforms,
continued-fraction convergents.
```

Use the fixed split

```text
discovery: p=43,61,67,
validation: p=79,97,
held-out: p=127,163,
```

plus the six public generator replacements. Reject formulas undefined at collisions unless they include a public regularization rule.

### Mandatory package G: scoped theorem

Prove at least one broad statement such as:

```text
bounded-degree public norm factors cannot reduce the twist support below Omega(n);
```

or

```text
any Laurent/continued-fraction half-divisor representation in the declared grammar needs Omega(n) charged coefficients;
```

or

```text
canonicalization rules invariant under public compact norm data preserve one mu_2 orientation ambiguity.
```

State the exact representation and cost model. Do not claim an unrestricted arithmetic-circuit lower bound.

### Positive gate

A candidate receives credit only if it includes:

```text
exact identity on every nonexceptional subgroup point,
public collision handling,
generator covariance,
branch-odd output,
no hidden factor/sign/half-divisor advice,
full coefficient and memory accounting,
reproducible implementation,
held-out validation,
strictly sub-square-root total complexity.
```

### Negative gate

A negative result must provide:

```text
an explicit grammar,
a proved invariant or lower bound,
exact replay,
a precise list of uncovered algorithmic classes.
```

Finite failure is evidence only.

### Required final flags

```text
compact_norm_factor_used=true
exact_norm_one_twist_constructed=true
compact_public_H_found=?
minimal_half_divisor_linear=?
canonical_orientation_without_advice=?
continued_fraction_subsqrt_evaluator_found=?
transposed_norm_equation_evaluator_found=?
sub_sqrt_evaluator_found=?
parity_oracle_found=?
sub_sqrt_ecdlp_found=?
```
