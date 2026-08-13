# GPT Pro focused continuation

## NONLINEAR-PRIMAL-FIRST-VARIATION-058

Work only on `research/uorc056-uniform-circuit` in `KeyAIGit/-ecdlp-lean-verification`. Do not modify `main`, `research/parity-lift-000`, or tracks A, B, D, E. Use only frozen toy data and public curve constants.

## Exact target

For `H=<G>`, `|H|=n`, and `Q=[k]G`, compute

```text
A(E,G,Q)=(-1)^k
```

with complete cost

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon))
```

for one fixed `epsilon>0`.

## Established exact identity

Read and reproduce C2 through C8, especially:

```text
archive/untrusted_intake/parity_lift_000/UORC056_TRINOMIAL_FIRST_VARIATION_C6.md
archive/untrusted_intake/parity_lift_000/UORC056_DUAL_EXPONENT_AND_PAIRING_BOUNDARY_C7.md
archive/untrusted_intake/parity_lift_000/UORC056_LINEAR_TRANSLATION_COMPRESSION_C8.md
```

For nonzero `Q=[k]G`,

```text
boxed:
(-1)^k=-n^(-1)[t]det(I+T_G+tT_Q)
      =-n^(-1)Tr((I+T_G)^(-1)T_Q).
```

The observable and extraction law are solved. Only compact public evaluation remains.

## Treat as closed

Do not repeat:

```text
explicit z^k, because generating its exponent gives k,
full Fourier or character states,
standard pairing transfer to mu_n,
translated point defects or bounded-support blocks,
Q-only spectral invariants,
one-anchor determinants,
two-term translation norms,
linear translation representations below ord_n(p),
translation-equivariant linear determinant-line complexes.
```

C8 proves that every nontrivial representation

```text
H -> GL_m(F_(p^d))
```

has charged base-field dimension

```text
d*m >= ord_n(p).
```

For secp256k1,

```text
ord_n(p)=(n-1)/6.
```

Therefore every nontrivial finite-field linear translation compression has linear cost. A surviving mechanism must be genuinely nonlinear in public curve coordinates and must not merely hide a translation representation inside a new basis.

## Primary question

```text
Can Tr((I+tau_G)^(-1)tau_Q) be expressed and evaluated as a
constant-number nonlinear primal-coordinate residue, intersection,
logarithmic derivative, norm, or oriented elliptic-product quantity below
n^(1/2-epsilon), without k and without a degree-n state?
```

Allocate effort:

```text
50 percent  nonlinear finite-etale residue, intersection or coordinate identity
30 percent  first-variation fast elliptic products and oriented Velu methods
10 percent  transposed coordinate computation outside linear representations
10 percent  scoped nonlinear lower bounds and adversarial integration
```

## Required attack order

### 1. Nonlinear finite-etale trace

Represent `H`, `G`, `Q`, and translations using public curve equations or rational maps, not a hidden exponent. Seek a constant-number formula for the trace using:

```text
Grothendieck residues,
intersection multiplicities of public correspondences,
logarithmic derivatives of subgroup products,
coordinate norms with bounded input descriptions,
nonlinear fixed-point weights,
resultants whose actual application state is sub-square-root.
```

For every formula expose the algebra dimension, denominator set, coefficient generation, basis conversion, extension fields, and online operations.

### 2. Ambient-geometry gate

A fixed-dimensional algebraic representation of the ambient elliptic curve is trivial, and ordinary translation actions on ambient cohomology are blind. A survivor must identify a nonlinear marked-generator structure that flips under both `G -> -G` and `Q -> -Q`.

If a declared residue or correspondence grammar factors only through ordinary ambient cohomology or a linear translation module, prove a scoped no-go theorem and stop that route.

### 3. First-variation elliptic product

Differentiate before expanding the orbit. Test whether square-root Velu or fast elliptic-polynomial decompositions can compute the first variation through a constant number of signed baby-step/giant-step resultants or logarithmic derivatives.

A `tilde O(sqrt(n))` boundary is not sufficient. A positive result needs one fixed exponent improvement. If orientation requires one branch bit per block, define the block grammar exactly and prove its state or advice lower bound.

### 4. Nonlinear transposed computation

Audit modular composition, power projection, transposed evaluation, and quotient-algebra traces only when they avoid a nontrivial linear representation of charged dimension `ord_n(p)`. Reject a short operator description whose evaluation materializes an `n`-entry vector or degree-`n` quotient.

### 5. Scoped fallback theorem

If no positive mechanism survives, close one finite nonlinear grammar such as:

```text
constant-number ambient residues,
bounded-degree correspondence intersections,
bounded-state signed BSGS summaries,
constant-number logarithmic derivatives of public kernel products.
```

Prove an exact obstruction: generator blindness, gauge-evenness, support growth, branch-bit accumulation, or reduction to the original Green coefficient. Do not claim a universal circuit lower bound.

## Mandatory gates

Every survivor must pass all points on all six frozen toy subgroups, generator replacement on small cases, `G -> -G`, `Q -> -Q`, all exceptional points, and the complete cost ledger.

Reject if it:

```text
uses k in an exponent, index, basis, path or branch,
uses all roots of unity,
materializes degree n,
hides square-root advice,
leaves a DLP in another group,
returns only toy correlation,
uses a linear translation representation under another name,
uses a short formula whose application expands to n leaves.
```

## Outputs

Produce one memo, deterministic exact replay, narrow Lean theorems only for claims actually proved, small reviewable commits, complete cost accounting, and one successor question. Report in Russian with sections:

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

unless every gate is genuinely satisfied.

Start with the nonlinear finite-etale residue/intersection class. Construct the evaluator or close that class precisely before broadening.
