# GPT Pro focused continuation

## UNIFORM-ORIENTED-ROOT-CIRCUIT-056, Track C6

Work only on `research/uorc056-uniform-circuit` in `KeyAIGit/-ecdlp-lean-verification`. Do not modify `main`, `research/parity-lift-000`, or tracks A, B, D, E.

### Frozen target

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

### Established input

Read and reproduce:

```text
archive/untrusted_intake/parity_lift_000/UORC056_TRANSLATION_RESOLVENT_C2.md
archive/untrusted_intake/parity_lift_000/UORC056_LOCAL_SUPPORT_QUERY_BOUND_C3.md
archive/untrusted_intake/parity_lift_000/UORC056_CIRCULANT_NORM_BOUNDARY_C4.md
archive/untrusted_intake/parity_lift_000/UORC056_SPARSE_TWO_TRANSLATION_RESULTANT_C5.md
experiments/parity_lift_000/uorc056_translation_resolvent.py
experiments/parity_lift_000/uorc056_sparse_two_translation_resultant.py
```

Treat as closed:

```text
translated singleton defects and bounded-support membership blocks,
Q-only spectral invariants of T_Q,
one fixed norm after z -> z^k,
one-anchor translated determinants,
generic rank-one determinant reduction without a new Green-entry evaluator,
local Krylov extraction,
every two-term translation norm,
trinomial coefficient families b=c and a=c on secp256k1.
```

Do not repeat Miller, endpoint, common-theta, degree-only, full-Fourier, or explicit degree-`n` routes already closed by the parent line.

### Exact surviving object

Let

```text
T=T_G,
T_Q=T^k.
```

The first surviving full-support determinant grammar is

```text
D_(a,b,c)(k)
=det(aI+bT+cT^k)
=Res(z^n-1,a+bz+cz^k).
```

The six affine exponent symmetries are already proved. The smallest symmetry-compatible family is

```text
boxed:
D_(a,a,c)(G,Q)=det(aI+aT_G+cT_Q).
```

The symmetry `k -> 1-k` preserves canonical parity, so it does not reject this family.

### Central task

Determine whether there exist publicly generated coefficients `a,c` and an exact extraction map `Extract` such that

```text
Extract(D_(a,a,c)(G,Q), public data)=(-1)^k
```

for every nonzero subgroup point, while `D` and `Extract` have complete cost below `n^(1/2-epsilon)` without knowing `k`.

If the `a=b` family closes, move once to a fully asymmetric triple and state the exact reason it escapes the theorem. Do not broaden beyond three translation monomials in this pass.

### Required attack order

1. Derive exact laws under

   ```text
   G -> -G,
   Q -> -Q,
   G -> [u]G,
   coefficient scaling and permutation.
   ```

2. Derive a recurrence, sparse resultant normal form, transfer matrix, or cycle-cover expression for `D_(a,a,c)(k)` that exposes all dependence on `k`.

3. Test exact extraction grammars in increasing order:

   ```text
   determinant value,
   quadratic character,
   ratio of two public coefficient specializations,
   quadratic character of that ratio,
   one constant-size polynomial relation among a bounded number of specializations.
   ```

4. For each survivor, give a complete evaluation algorithm. Charge degree, state dimension, roots of unity, modular composition, coefficient generation, extension fields, memory, and every query-dependent operation.

5. If compact evaluation fails, define one exact finite grammar and prove a no-go from its affine symmetry, recurrence state, query support, or representation size. Do not claim a universal circuit lower bound.

### Mandatory replay

Use every nonzero scalar on the six frozen prime-order toy subgroups. Test all generator replacements on the small cases when feasible. Include exact checks for

```text
G -> -G,
Q -> -Q,
all denominator and zero cases,
all six exponent symmetries,
no accidental dependence on a hidden scalar label.
```

No external point, wallet, private key, or production target is accepted.

### Rejection gates

Reject a candidate if it:

```text
materializes an n by n matrix,
constructs a degree-n coefficient vector,
uses all n roots of unity,
hides Theta(sqrt(n)) or larger advice,
requires k to place an exponent or choose a branch,
merely calls a generic resultant or determinant routine,
returns only toy correlation,
reduces to C2 Green-entry extraction without a new evaluator,
reintroduces a closed symmetry class.
```

### Required outputs

Produce one memo, one deterministic exact replay, narrow Lean theorems only for claims actually proved, and small reviewable commits. Separate the report into

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

unless every exactness and cost gate is genuinely satisfied.

### First question

```text
Can the parity-compatible trinomial resultant
Res(z^n-1,a+az+cz^k)
be reduced to a constant-size public recurrence or coordinate invariant whose
exact branch is canonical scalar parity, without knowing k and without a
degree-n state?
```

Do not stop at writing the resultant. Either construct the evaluator or close one precise coefficient and extraction grammar.

Respond to the user in Russian. Repository mathematics may be written in English.
