# Admissible GLV Decoder Class

Date: 2026-08-12

Status: **synchronized research contract for PR #365 and PR #373; no production target and no asymptotic break claim**.

## Decision first

There is no ambiguity at the level of existence of a function.  For the fixed
ordered instance `(E,G,phi)`, the GLV carry is a well-defined public-point
function

```text
Q -> g_G(Q) in {-1,+1}.
```

Exact public descriptions exist by exhaustive lookup, interpolation on the
six-orbit quotient, or the generator-oriented half-kernel factor.  The known
exact descriptions have linear-size state, degree, or preprocessing.

The open question is therefore not whether the bit exists.  It is:

> Does the bit admit a **uniform, generator-sensitive, exact and reusable public
> representation whose total time, memory, preprocessing and advice are below
> the generic square-root baseline?**

As of this checkpoint:

```text
known exact representation:                  yes
known admissible sub-sqrt representation:    no
proved universal non-existence:              no
```

The current evidence and scoped theorems rule out several large natural
families, but do not rule out a high-degree low-circuit construction, a genuine
generator-sensitive theta/sigma splitting, or a canonical p-adic construction
with an exact base-field output.

## 1. Fixed instance and target bit

Let

```text
E/F_p : y^2 = x^3 + 7,
H=<G>, |H|=n prime,
phi(x,y)=(beta*x,y),
phi(G)=[lambda]G,
lambda^2+lambda+1=0 mod n.
```

For `Q=[k]G`, let `k0,k1,k2` be the canonical representatives in
`{1,...,n-1}` of

```text
k, lambda*k, lambda^2*k.
```

Then

```text
k0+k1+k2 = gamma_G(Q)*n,
gamma_G(Q) in {1,2}.
```

Define

```text
g_G(Q)=(-1)^gamma_G(Q).
```

The required decoder must work for every nonzero point of `H`, not only for one
selected point.

## 2. Three exactly equivalent output interfaces

The EDS residue is

```text
rho_G(Q)=chi(psi_k(G)),  Q=[k]G.
```

The odd GLV aggregate is

```text
R3_G(Q)=rho_G(Q)*rho_G(phi Q)*rho_G(phi^2 Q).
```

The public point-function orbit norm is

```text
C3_G(Q)=C_G(Q)*C_G(phi Q)*C_G(phi^2 Q),
```

and the established bridge is

```text
C3_G(Q)=g_G(Q)*R3_G(Q).
```

Hence an exact `g_G` decoder and an exact `R3_G` decoder are mutually
convertible by public multiplication with `C3_G`.

For the direct quotient interface put

```text
z(Q)=x(Q)^3=y(Q)^2-7,
h_G(z(Q))=g_G(Q)*chi(y(Q)).
```

Because `g_G` and `chi(y)` are both anti-invariant under negation and invariant
under `phi`, `h_G` is a function of the six-element orbit

```text
{+/-Q,+/-phi Q,+/-phi^2 Q}.
```

The carry is recovered publicly by

```text
g_G(Q)=h_G(z(Q))*chi(y(Q)).
```

Accordingly one admissible decoder may expose any one of the following exact
interfaces:

```text
D_g(Q)=g_G(Q),
D_R(Q)=R3_G(Q),
D_h(z(Q))=h_G(z(Q)).
```

No interface is preferred cryptographically; they are public transformations
of the same bottleneck.

## 3. Exact but inadmissible representations

### 3.1 Lookup or interpolation

The quotient contains `(n-1)/6` six-orbits.  A table or a Lagrange polynomial
can encode `h_G` exactly on those points.  Its description and preprocessing
are linear in the quotient size.

### 3.2 Generator-oriented half-kernel

Let

```text
S_G={P in H\{O}: g_G(P)=+1}.
```

The carry-positive C3-orbit factor is

```text
H_G(Y)=product_(P in S_G/C3) (Y-y(P)).
```

It has degree `(n-1)/6` and satisfies

```text
H_G(y(Q))=0  iff  g_G(Q)=+1.
```

Thus a completely exact public algebraic representation exists.  Constructing
or storing it in the direct way materializes a linear number of roots or
coefficients.  The research question is whether its membership decision can be
evaluated without materializing that state.

The factor is genuinely generator-oriented.  Under `G'=[u]G`,

```text
g_[uG](Q)=g_G([u^(-1)]Q),
S_[uG]=[u]S_G.
```

In particular `G` and `-G` require complementary factors, while their subgroup
kernel is identical.  A kernel-only or un-oriented CM construction therefore
cannot select the correct factor for both generators.

## 4. Definition of an admissible decoder family

A decoder family belongs to `D_adm` only if all conditions below are met.

### A. Uniform public construction

The algorithm or circuit is generated from the ordered public data

```text
(p,E,n,G,phi)
```

and evaluated on public `Q`.  Its generator sensitivity must be explicit and
must obey the generator-change covariance law.  A construction depending only
on `H` or on a kernel polynomial is not admissible as a generator-relative
solution.

### B. Exact and total output

The primary target is exact output on every `Q in H\{O}`.  Zeros, poles,
exceptional points, extension-field choices and branch cuts must be handled by
a proved rule.  A numerical or p-adic implementation must include a precision
theorem that makes the final bit exact.

### C. Required symmetries

For a carry decoder:

```text
D_g(phi Q)=D_g(Q),
D_g(-Q)=-D_g(Q).
```

For a quotient decoder:

```text
D_h(z(phi Q))=D_h(z(Q)),
D_h(z(-Q))=D_h(z(Q)).
```

These are necessary checks, not sufficient evidence.

### D. No hidden scalar or orientation advice

The construction may not use:

```text
k or a scalar lift of Q,
a path of length proportional to k,
a level-n character whose orientation was chosen using k,
a theta/sigma branch selected from target labels,
a table or model encoding the complete carry partition,
or an implicit ECDLP inside preprocessing.
```

### E. All-in complexity accounting

Count together:

```text
parameter generation,
preprocessing,
advice/model description,
memory,
per-query evaluation,
precision and extension-field arithmetic,
and the number of chosen-multiplier queries used by recovery.
```

The admissibility threshold is

```text
T_total, M_total, advice_size = O(n^(1/2-epsilon))
```

for some fixed `epsilon>0`.  The strong target is polynomial in
`log p` and `log n`.

A polynomial of degree or a lookup table of size `Theta(n)` is not made
admissible by calling its coefficients public.

### F. Reusable oracle behavior

The same fixed construction must evaluate

```text
D_g([t]Q)=g_G([t]Q)
```

for publicly selected `t`.  Correctness on one distinguished `Q` is
insufficient because the downstream recovery uses chosen multipliers.

### G. Hard-branch public-factor quotient gate

Every candidate for `R3_G` must first be divided by all known public factors.
An exact match in the easy point-scale branch, where `R3` already equals a
public `C3` norm, is not progress.  The residual candidate must isolate
`R3_G` in the hard branch or isolate `g_G` directly.

### H. Training and nonlinear models

Training is admissible only as a discovery aid.  A positive claim requires a
fixed extractable public circuit, independent held-out replay, generator and
orbit leakage controls, and full accounting of model size and labelled
preprocessing.  A curve-specific model that stores a linear fraction of the
quotient labels is an interpolation table, not a succinct decoder.

### I. Weak predictors are a separate contract

A predictor with advantage `epsilon` is not automatically an admissible exact
decoder.  It requires a proved noisy carry-to-ECDLP reduction with explicit
sample, failure-probability and total-cost bounds.  Until that theorem is
attached, the master class is exact.

### J. Verification boundary

A positive construction requires:

```text
an exact identity or theorem,
a second independent CAS replay,
a frozen toy scaling protocol,
a complete cost proof,
a literal carry/R3-to-scalar recovery replay,
and formalization of the finite arithmetic core where practical.
```

## 5. Synchronized status of PR #365 and PR #373

### Closed or strongly bounded classes

1. Direct parity through x-only/Kummer coordinates.
2. Fixed-rank relative EDS/net relations that preserve the global sign gauge.
3. Bounded isogeny and natural root-cover descents already replayed.
4. The first order-n torsion jet and near-period division-polynomial sections.
5. Finite products and ratios of ordinary division-polynomial sections.
6. The scoped homogeneous quadratic-normalization category `C_quad`.
7. Pure level-n cyclotomic descent under Frobenius-compatible branch choice.
8. Kernel-only or un-oriented CM half-factor selection.
9. Public x-coordinate predicates with polylogarithmic field-Fourier L1.
10. Split quotient-character products with at most four factors on the frozen
    direct-descent corpus.
11. All rational square classes of total numerator-plus-denominator degree at
    most two on that corpus.
12. The tested order-13441 binary lookup, eight phase powers, same-curve fixed
    low-pass families, bounded nonlinear models and their independent selected
    replication.

The finite screens are bounded evidence.  The algebraic, covariance and
spectral statements are scoped theorems with the boundaries recorded in their
source packages.

### Open admissible mechanism classes

1. A generator-sensitive theta/sigma splitting that outputs only the needed
   carry bit without materializing an order-n dual character.
2. A high-degree but genuinely low-circuit base-field expression whose advice
   and coefficients are uniformly generated from `(E,G,phi)`.
3. A canonical p-adic or analytic construction with exact public branch,
   precision and sub-square-root total cost.
4. A nonlocal order-dependent EDS/theta section outside the closed homogeneous
   category and surviving the public-factor quotient gate.
5. A new exact identity using the remaining public field-character structure,
   provided it is generator-sensitive and not a disguised label table.

## 6. The single next constructive question

The synchronized successor is not another broad feature screen.  It is:

```text
GENERATOR-SENSITIVE-HALF-KERNEL-EVALUATION
```

> Given only `(E,G,phi,Q)`, can one decide whether
> `H_G(y(Q))=0`, equivalently compute `g_G(Q)` or `R3_G(Q)`, in total
> `O(n^(1/2-epsilon))` resources, without constructing the `(n-1)/6` roots or
> coefficients of `H_G`, without materializing a nontrivial order-n dual
> character, and without hiding the same information in advice or a branch
> choice?

The first theorem-sized subquestion is:

> Does every standard generator-sensitive theta/sigma linearization over
> `<G>` differ from a public generator-blind normalization by an order-n dual
> character, and if so, can a single nonlinear bit of that character be
> evaluated with sub-square-root state without representing an equivalent
> n-state object?

A positive answer must provide the evaluator and cost proof.  A negative answer
must specify the representation category and prove an advice/state/time lower
bound inside that category.

## 7. Why solving this finishes the current bottleneck

An exact carry oracle gives chosen-multiplier values

```text
t -> g_G([t]Q)=g(t*k mod n).
```

The carry has a known constant-heavy Fourier spectrum.  The registered local
sparse-Fourier reduction recovers a constant-size list containing the hidden
scalar in the stated source-conditional model, followed by public candidate
verification.

Therefore the remaining missing arrow in the current parity/EDS/GLV program is
precisely

```text
(E,G,phi,Q) -> g_G(Q)  or  R3_G(Q).
```

Everything downstream is already isolated.  Any future package must either
construct this arrow under `D_adm` or close one explicitly named mechanism
class.  New goals, labels or observables are not admitted merely because a
screen produces a finite correlation.
