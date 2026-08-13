# GPT Pro research prompt

## UNIFORM-ORIENTED-ROOT-CIRCUIT-056: compact translation-resolvent branch selection

Work autonomously on one narrow theorem-first task. Continue until you obtain either a reproducible positive evaluator satisfying every exactness and cost gate below, or a scoped no-go theorem that closes a declared mechanism class and leaves one sharper successor.

### Repository discipline

Repository: `KeyAIGit/-ecdlp-lean-verification`

Work only on `research/uorc056-uniform-circuit`.

Do not modify `main`, `research/parity-lift-000`, or tracks A, B, D, E. Fetch the current branch head, inspect PR #365 and the latest A/B/C commits, preserve concurrent work, create small commits, and use only the frozen toy curves and public constants already in the repository.

### Frozen target and complete cost gate

Let

```text
E/F_p : y^2=x^3+7,
H=<G>, |H|=n,
Q=[k]G.
```

Compute exactly

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k.
```

One call must have complete charged cost

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon))
```

for a fixed `epsilon>0`. Charge tables, coefficients, branch bits, full dual states, compilation, normalization, exceptional cases, extension degree, memory, and query-dependent work.

### Do not rediscover closed routes

Treat the existing line as input and verify exact file names before using it:

1. `Y_G^2=x^3+7 mod K_H` and `Y_G(x([k]G))/y([k]G]=(-1)^k`.
2. `Y_(-G)=-Y_G`, while `K_H` is fixed.
3. Miller, division-polynomial, endpoint, Ward/net, common-basis determinant, row-rescaling, ordinary theta-characteristic, standard metaplectic, and local p-adic routes are closed in their declared gauge-even or generator-blind models.
4. Dyadic branch expansion, full Fourier support, explicit root or coefficient materialization, and standard level-`n` states require large state.
5. High degree alone is not a circuit lower bound.

Do not spend the main pass on another multiplicative two-endpoint product or a degree-only argument.

### New exact starting package

Read and replay:

```text
archive/untrusted_intake/parity_lift_000/UORC056_TRANSLATION_RESOLVENT_C2.md
experiments/parity_lift_000/uorc056_translation_resolvent.py
```

For `p=3 mod 4`, define

```text
R_0(X)=(X^3+7)^((p+1)/4),
C_G=Y_G/R_0 mod K_H.
```

Then

```text
R_0(x(P))=y(P)chi(y(P)),
C_G(x([k]G))=(-1)^k chi(y([k]G)),
C_G^2=1 mod K_H,
e_G=(1-C_G)/2,
e_G^2=e_G,
C_(-G)=-C_G.
```

Thus ordinary square-root extraction is cheap. The target is the generator-selected Kummer idempotent.

On `V=Fun(H,F_p)`, define

```text
(tau_G f)(P)=f(P+G),
s_G([k]G)=(-1)^k,
d_G=delta_(-G).
```

Then

```text
(I+tau_G)s_G=2d_G,
s_G=sum_(j=0)^(n-1)(-1)^j tau_G^j d_G.
```

The seed is publicly cheap:

```text
d_G(P)=[1-(x(P)-x_G)^(p-1)]*[1-y(P)/y_G]/2.
```

Let `T_G` be translation in the point-idempotent basis and `ev_Q` evaluation at `Q`. Then

```text
det(I+T_G)=2,
det(I+T_G+t*d_G*ev_Q)=2+t*(-1)^k.
```

This determinant is exact, generator-sensitive, and nonmultiplicative. It is not an algorithm because its natural dimension is `n`.

### Primary question

Determine whether

```text
ev_Q (I+tau_G)^(-1)d_G
```

or the equivalent rank-one determinant can be evaluated uniformly below `n^(1/2-epsilon)` without constructing an `n`-dimensional basis, a full dual character, an oriented half-kernel, `Theta(n)` coefficients, or the hidden scalar.

Allocate most effort to this question. Do not dilute the pass across unrelated ECDLP directions.

### Required attack order

#### 1. Formalize the operator core

Prove with exact hypotheses:

```text
(I+tau) sum_(j=0)^(n-1)(-1)^j tau^j=2I,
(I+tau_G)s_G=2d_G,
det(I+T_G)=2,
the rank-one determinant identity,
C_G^2=1 and idempotence of (1-C_G)/2,
C_(-G)=-C_G,
S_(a+b)=S_a+(-1)^a tau^a S_b.
```

Create a narrow Lean file for only the abstract algebra actually proved. No `sorry`. State the formalization boundary.

#### 2. Succinct determinant and coordinate-algebra route

Test:

```text
resultants and norms in the subgroup coordinate algebra,
cyclic-plus-rank-one or displacement-rank reductions,
scalar Fredholm determinants,
cycle-cover cancellation,
Schur complements after public Kummer or GLV decompositions,
black-box determinant methods using translation and evaluation oracles.
```

For every candidate identify the actual dimension, representation of `ev_Q`, number of operator-vector products, whether a dense state appears, and whether the method merely calls `A^(-1)d`, which is the target.

A generic structured algorithm quasi-linear in dimension `n` is rejected.

#### 3. Nonlinear partial-resolvent composition

Let

```text
S_m=sum_(j=0)^(m-1)(-1)^j tau^j.
```

Use

```text
S_(a+b)=S_a+(-1)^a tau^a S_b.
```

Search for a bounded nonlinear summary that merges partial segments without doubling query arguments. Charge both state size and total query fan-out. Reject an `O(log n)` operator DAG whose evaluation expands to `n` translated leaves.

If no merge survives, define a finite grammar and prove a state, support, or fan-out lower bound for that grammar.

#### 4. Oriented fast elliptic products

Use square-root Velu and fast elliptic polynomials only as a baseline. Ask whether the alternating orientation can be absorbed into a constant-size biquadratic resultant or whether it forces one branch bit per block. A `tilde O(sqrt(n))` result is informative but does not satisfy the target.

#### 5. Kummer doubling cocycle

For Kummer index `j in {1,...,(n-1)/2}`, unsigned doubling is

```text
d(j)=2j if 2j<=(n-1)/2, else n-2j,
```

and its orientation cocycle is

```text
epsilon_j=(-1)^(d(j)).
```

Search for an exact coordinate formula using x-only doubling, field characters, CM/GLV data, or bounded division-polynomial residues. Reject formulas that use the hidden index, recurse to the same evaluator, or reduce to a relative EDS edge.

### Mandatory adversarial gates

Every survivor must pass:

```text
all points of all six frozen toy subgroups,
G -> -G,
Q -> -Q,
G -> [u]G for toy generators,
exact denominator and exception handling,
complete cost ledger,
no hidden scalar-dependent index or path,
no full dual state,
no reduction to a closed gauge-even mechanism.
```

Reject immediately if a candidate:

1. outputs only `rho(a)rho(b)`;
2. expands `Theta(n)` orbit terms;
3. stores `Theta(n)` roots, coefficients, phases, or basis entries;
4. hides `Theta(sqrt(n))` advice while claiming a strict exponent improvement;
5. diagonalizes translation with all `n` characters;
6. calls a generic determinant on an `n` by `n` matrix;
7. chooses the correct half, midpoint, wrap, or branch without deriving it;
8. gives only toy correlation;
9. argues from degree alone;
10. has a short formula but an uncharged large application state.

### Required outputs

Produce:

1. one self-contained memo with exact target, derivation, transformation law, replay, full cost ledger, conclusion, formalization boundary, and one successor question;
2. deterministic exact Python replay extending the existing frozen implementation;
3. narrow Lean theorems for claims actually proved;
4. reviewable commits on the branch;
5. a final Russian report separating `PROVED`, `REPLAYED`, `SUPPORTED`, `OPEN`, and `REJECTED IN MODEL X`.

Keep

```text
evaluator_found=false,
parity_oracle_found=false,
sub_sqrt_ecdlp_found=false
```

unless a complete positive construction genuinely satisfies every gate.

### First action

Reproduce the package, then answer this exact question:

```text
Can det(I+T_G+delta_(-G)ev_Q) be reduced to a constant-size
resultant, norm, or nonlinear transfer state in public curve coordinates,
with complete cost below n^(1/2-epsilon), without constructing the
degree-n subgroup algebra or importing a dual character?
```

Do not stop at the determinant identity. Produce the compact evaluation mechanism or close the first precisely declared representation class with an exact theorem.

Respond to the user in Russian. Repository mathematics may be written in English.
