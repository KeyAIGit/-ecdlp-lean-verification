# GPT Pro focused continuation

## PRIMAL-FIRST-VARIATION-EVALUATOR-057

Work autonomously on one narrow theorem-first continuation of `UNIFORM-ORIENTED-ROOT-CIRCUIT-056`.

Repository:

```text
KeyAIGit/-ecdlp-lean-verification
```

Work only on:

```text
research/uorc056-uniform-circuit
```

Do not modify `main`, `research/parity-lift-000`, or tracks A, B, D, E. Use only frozen toy curves, frozen known toy scalars, and public secp256k1 constants. Accept no external point, private key, wallet, production target, or unknown scalar instance.

## Central target and cost gate

For

```text
H=<G>, |H|=n,
Q=[k]G,
```

compute exactly

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k
```

with complete charged cost

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon))
```

for one fixed `epsilon>0`.

Charge all tables, coefficients, roots, branch bits, extension degrees, basis conversions, exceptional cases, memory, and query-dependent work.

## Read and reproduce first

```text
archive/untrusted_intake/parity_lift_000/UORC056_TRANSLATION_RESOLVENT_C2.md
archive/untrusted_intake/parity_lift_000/UORC056_LOCAL_SUPPORT_QUERY_BOUND_C3.md
archive/untrusted_intake/parity_lift_000/UORC056_CIRCULANT_NORM_BOUNDARY_C4.md
archive/untrusted_intake/parity_lift_000/UORC056_SPARSE_TWO_TRANSLATION_RESULTANT_C5.md
archive/untrusted_intake/parity_lift_000/UORC056_TRINOMIAL_FIRST_VARIATION_C6.md
archive/untrusted_intake/parity_lift_000/UORC056_DUAL_EXPONENT_AND_PAIRING_BOUNDARY_C7.md
experiments/parity_lift_000/uorc056_translation_resolvent.py
experiments/parity_lift_000/uorc056_sparse_two_translation_resultant.py
experiments/parity_lift_000/uorc056_trinomial_first_variation.py
experiments/parity_lift_000/uorc056_secp256k1_embedding_degree.py
```

## Established exact observable

Let `T_G` and `T_Q` be regular translation operators. For nonzero `Q=[k]G`,

```text
R_(G,Q)(t)=det(I+T_G+tT_Q),
R'_(G,Q)(0)=-n(-1)^k.
```

Therefore

```text
boxed:
(-1)^k=-n^(-1)[t]det(I+T_G+tT_Q).
```

The extraction law is solved. The remaining problem is compact public evaluation.

The dual notation

```text
[t]Res(z^n-1,1+z+t z^k)
```

is not a public sparse representation. Explicitly producing the exponent in `z^k` produces the full scalar `k`. Full dual diagonalization uses `n` character components. For secp256k1, `ord_n(p)=(n-1)/6`, so a conventional pairing extension has `Theta(n)` base-field dimension.

## Treat as closed

Do not repeat:

```text
Miller/division/net/endpoint multiplicative products,
gauge-even two-endpoint observables,
explicit degree-n roots or coefficient tables,
full Fourier or level-n theta states,
translated singleton defects,
bounded-support membership blocks with q*b<(n-1)/2,
Q-only spectral invariants,
one fixed norm after z -> z^k,
one-anchor translated determinants,
local Krylov extraction,
every two-term translation norm,
trinomial classes b=c and a=c,
explicit compilation of z^k,
one pairing character as parity,
standard n-torsion pairing extensions.
```

## Primary task

Evaluate

```text
V(E,G,Q)=-n^(-1)[t]det(I+T_G+tT_Q)
```

directly from public elliptic coordinates below `n^(1/2-epsilon)`, without recovering `k`, constructing an `n`-dimensional regular or dual state, materializing `K_H` coefficient-by-coefficient, or hiding square-root advice.

Allocate effort approximately:

```text
45 percent  finite-etale trace, residue, norm, intersection or determinant line
25 percent  oriented fast elliptic products and first-variation Velu methods
15 percent  rational translation, modular composition and transposed computation
15 percent  scoped lower bounds and adversarial integration
```

## Required attack order

### 1. Formalize the operator core

Prove exactly:

```text
det(I+T_G)=2,
(I+T_G)^(-1)=(1/2)sum_(j=0)^(n-1)(-1)^jT_G^j,
Tr(T_R)=n if R=O and 0 otherwise,
R'_(G,Q)(0)=-n(-1)^k.
```

Add narrow Lean theorems only for the abstract algebra actually proved. No `sorry`. Use the Baur-Strassen boundary correctly: a small symbolic circuit for `R(t)` gives its derivative with constant-factor overhead, but one fixed numerical determinant value does not.

### 2. Primal finite-etale coordinate algebra

Represent the subgroup coordinate algebra and translations by public `G,Q` without a hidden scalar exponent. Seek an exact formula for

```text
Tr((I+tau_G)^(-1)tau_Q)
```

using a constant number of:

```text
residues,
coordinate traces,
resultants or norms,
intersection numbers of correspondences,
determinant-line or torsion quantities,
finite fixed-point formulas with an orientation weight.
```

Identify the actual algebra dimension and evaluation operations. Reject a degree-n quotient merely renamed as a constant object.

### 3. Ambient-cohomology gate

Test whether a proposed Lefschetz or cohomological compression lives only on the constant-dimensional cohomology of the ambient elliptic curve. A survivor must explain where marked-generator orientation enters and must flip correctly under `G -> -G` and `Q -> -Q`. If one declared ambient grammar is translation-blind, prove that scoped no-go theorem.

### 4. Oriented fast elliptic product

Differentiate a public elliptic-product family before full orbit expansion. Test square-root Velu, baby-step/giant-step resultants, logarithmic derivatives, and biquadratic evaluations. A `tilde O(sqrt(n))` method is a useful boundary but does not satisfy the target. Determine whether orientation forces one independent branch bit per block.

### 5. Rational translation and transposed computation

Audit modular composition, transposed modular composition, power projection, quotient-algebra traces, low-displacement representations, and black-box determinants. Charge quotient degree, vector length, operator-vector products, denominators, and basis conversion. Reject any method with an `n`-dimensional application state or a `Q` interface reducible to the C3 local-support model.

### 6. Small-complex determinant line

Search for a publicly generated chain complex of dimension below `sqrt(n)` whose torsion or determinant-line variation is exactly `-n(-1)^k`. Reject a complex whose differential contains `k`, an oriented half-orbit, or a degree-n matrix.

### 7. Scoped lower-bound fallback

If no evaluator survives, define one finite primal-coordinate grammar and prove a real obstruction such as generator blindness, conjugacy invariance, gauge-even transformation, support growth, full-state requirement, or reduction to the original Green coefficient. Do not claim a universal arithmetic-circuit lower bound.

## Mandatory gates

Every survivor must pass all points on all six frozen subgroups, generator replacement on toy cases, `G -> -G`, `Q -> -Q`, all denominator and exceptional cases, and a complete cost ledger.

Reject immediately if a candidate:

```text
uses z^k as if k were public,
uses all roots of unity,
materializes an n-dimensional algebra or matrix,
calls a generic determinant/resultant without its state cost,
hides Theta(sqrt(n)) advice,
chooses a branch using parity itself,
returns only toy correlation,
argues from degree alone,
leaves a DLP in mu_n,
uses a short operator formula whose application expands to n leaves.
```

## Required outputs

Produce one self-contained memo, deterministic exact replay, narrow Lean proofs, small reviewable commits, complete cost ledger, and one successor question. Separate the Russian report into:

```text
PROVED
REPLAYED
SUPPORTED ONLY
REJECTED IN DECLARED MODEL
OPEN
```

Keep

```text
evaluator_found=false,
parity_oracle_found=false,
sub_sqrt_ecdlp_found=false
```

unless every exactness and cost gate is satisfied.

## First question

```text
Can Tr((I+tau_G)^(-1)tau_Q) be computed as a constant-number
primal elliptic-coordinate residue, norm, intersection, or determinant-line
quantity below n^(1/2-epsilon), without introducing k or a degree-n state?
```

Do not stop at the trace identity. Construct the public compact evaluator or close the first precisely declared primal-coordinate representation class.

Respond to the user in Russian. Repository mathematics may be written in English.
