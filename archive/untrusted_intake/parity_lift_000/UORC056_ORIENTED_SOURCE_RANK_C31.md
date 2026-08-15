# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C31: marked-generator oriented-source rank and transposed-dictionary boundary

Date: 2026-08-15

Status: **the family of marked-generator oriented-root source vectors has exact
characteristic-zero rank `(n-1)/2`. The proof diagonalizes the multiplicative
translation matrix. Even multiplicative characters vanish by branch
antisymmetry, while every odd character is nonzero by the standard primitive
odd Dirichlet `L(0,chi)` nonvanishing theorem. Restricting rows and columns to
one representative of each `+/-` pair preserves this rank, and multiplying
columns by the nonzero values `y([r]G)` preserves it again. Therefore any fixed
linear source dictionary that contains all marked-generator oriented roots
needs at least `(n-1)/2` independent directions. Exact finite-field replay
finds full half rank on all five frozen base fields. The package does not claim
that the same rank has been proved modulo the secp256k1 field prime, and it does
not exclude a nonlinear fixed-generator source compiler.**

No external unknown-scalar point, private key, wallet, production target,
scalar bits, dense secp256k1 source vector, root table, or uncharged oriented
advice is accepted.

## 1. Why source generation is now the central object

C23 proves that branch-even rational leaves cannot create orientation. C30
proves that every local rational certificate built after one quadratic branch
has the form

```text
E+O*Y.
```

If `O` is not a unit, the certificate collides on a component. If `O` is a
unit, the original branch is recovered. Thus local postprocessing is no longer
a separate route.

A transposed or modular-composition evaluator may still hope to compute one
value without storing the dense polynomial. Such a method has two parts:

```text
source generation,
application of the source to the query functional.
```

The second part may be fast. C31 asks whether the first part can be hidden in a
small fixed linear dictionary.

## 2. Exact marked-generator source matrix

Let

```text
n=2m+1
```

be an odd prime, let `H=<G>`, and use the base half-kernel points

```text
P_r=[r]G=(x_r,y_r), 1<=r<=m.
```

For a marked generator

```text
G_u=[u]G,
```

write `u^(-1)` for the inverse modulo `n`. The exact orientation convention
gives

```text
boxed:
Y_[u]G(x_r)
 =epsilon([r*u^(-1)]_n) y_r,                    (C31.1)
```

where

```text
epsilon(a)=(-1)^a,
1<=a<n
```

uses the canonical nonzero residue.

Define the sign source matrix

```text
M_(u,r)=epsilon([r*u^(-1)]_n),
1<=u,r<=m.                                      (C31.2)
```

The actual oriented-value matrix is obtained by nonzero column scaling:

```text
V_(u,r)=M_(u,r)y_r.                              (C31.3)
```

Because the subgroup has odd order, every `y_r` is nonzero.

Generator negation gives the exact redundant half:

```text
row_(n-u)=-row_u.                                (C31.4)
```

Thus the first `m` marked generators contain the complete linear source span.

## 3. Multiplicative Fourier diagonalization

Let

```text
U=(Z/nZ)^*,
f(a)=epsilon(a).
```

Consider the full multiplicative translate matrix

```text
F_(u,r)=f(u^(-1)r),
u,r in U.                                           (C31.5)
```

The group `U` is cyclic. Its multiplicative characters diagonalize this
convolution matrix. The eigenvalue at a character `chi` is

```text
hat f(chi)=sum_(a in U) f(a) chi(a).             (C31.6)
```

### Even characters

Since `n` is odd,

```text
f(-a)=-f(a).
```

If `chi(-1)=+1`, the terms at `a` and `-a` cancel, so

```text
hat f(chi)=0.                                    (C31.7)
```

### Odd characters

Assume `chi(-1)=-1` and put

```text
H_chi=sum_(a=1)^m chi(a),
W_chi=sum_(a=1)^(n-1) a chi(a).                  (C31.8)
```

The even residues are `2,4,...,n-1`, so

```text
hat f(chi)=2 chi(2) H_chi.                       (C31.9)
```

Multiplication by two permutes the nonzero residues. Tracking whether the
canonical preimage is `b/2` or `(b+n)/2` gives

```text
n chi(2) H_chi=(1-2chi(2))W_chi.                (C31.10)
```

Every odd character modulo the prime `n` is nontrivial and primitive. The
standard generalized-Bernoulli identity is

```text
L(0,chi)=-W_chi/n,
```

and the primitive odd value is nonzero. Also `1-2chi(2)` cannot vanish because
`chi(2)` is a root of unity. Hence

```text
boxed:
hat f(chi)!=0 for every odd chi.                 (C31.11)
```

There are exactly `m` odd characters. Therefore

```text
rank_C(F)=m.                                     (C31.12)
```

The analytic nonvanishing input is stated explicitly. It is not disguised as
a Lean result.

## 4. Transfer to the half matrix

Order the rows and columns of the full matrix by

```text
U=H_+ union (-H_+),
H_+={1,...,m}.
```

Using `f(-a)=-f(a)`, the full matrix has block form

```text
F = [ M  -M
     -M   M ].                                  (C31.13)
```

It kills symmetric vectors `(v,v)` and acts on antisymmetric vectors `(v,-v)`
as `(2Mv,-2Mv)`. Therefore

```text
rank(F)=rank(M).                                 (C31.14)
```

Combining with `(C31.12)` gives

```text
boxed:
rank_C(M)=m=(n-1)/2.                             (C31.15)
```

Column scaling by the nonzero `y_r` is invertible, so

```text
boxed:
rank_C(V)=m.                                     (C31.16)
```

## 5. Fixed linear dictionary consequence

Suppose a transposed source mechanism stores or generates a fixed family

```text
phi_1,...,phi_d in K^m
```

and requires every marked-generator oriented source row to lie in their linear
span:

```text
V_u=sum_(j=1)^d c_(u,j) phi_j.                   (C31.17)
```

Then

```text
span{V_u} subseteq span{phi_j},
```

so `(C31.16)` forces

```text
boxed:
d>=(n-1)/2.                                     (C31.18)
```

The lower bound is tight as a dimension statement because the coordinate basis
has `m` directions. It is not a claim that this explicit basis is a useful
algorithm.

For secp256k1 the characteristic-zero bound is

```text
57896044618658097711785492504343953926418782139537452191302581570759080747168,
```

which lies strictly between `2^254` and `2^255`.

Thus a fixed low-rank linear dictionary cannot be the missing oriented source
in characteristic zero.

## 6. Exact frozen finite-field replay

The executable replay checks the five frozen curves

```text
(p,n)=
(43,31),
(67,79),
(79,67),
(127,127),
(163,139).
```

For every curve it constructs `M` and `V` directly over the base field and
checks

```text
rank_Fp(M)=m,
rank_Fp(V)=m,
rank_Fp(full marked matrix)=m.                   (C31.19)
```

It also verifies `(C31.1)` and `(C31.4)` on every marked-generator/source-node
pair.

Frozen totals are

```text
curves:                              5
sum of half dimensions:            219
half-source matrix entries:     11,565
all marked source entries:      23,130
marker-formula checks:          23,130
generator-negation checks:      23,130
full-rank base-field curves:          5
errors:                               0
```

For every frozen order the replay additionally finds an auxiliary prime field
in which the multiplicative Fourier coefficients vanish exactly at the even
characters and are nonzero exactly at the odd characters. One good reduction
already certifies that the corresponding integer half matrix is nonsingular in
characteristic zero.

## 7. Critical secp256k1 base-field boundary

The all-prime theorem above is a characteristic-zero theorem. An integer matrix
that is nonsingular over characteristic zero can lose rank modulo a particular
prime dividing its determinant.

C31 does not evaluate the enormous determinant modulo the secp256k1 field
prime and therefore does not claim

```text
rank_Fp(M)=m
```

for production secp256k1.

This limitation matters. The package closes characteristic-zero/cyclotomic
fixed dictionaries and records exact finite-field evidence on the frozen
corpus. It does not silently transfer that conclusion into the secp256k1 base
field.

A later package may attack the structured determinant modulo the secp field
prime. A positive algorithm may instead escape the entire fixed-linear-
dictionary model.

## 8. What C31 closes

Closed in the declared scope:

```text
characteristic-zero fixed linear dictionaries spanning all marked-generator oriented sources,
transposed methods that receive such a fixed low-rank source dictionary,
frozen-base-field fixed dictionaries below the exact half-kernel rank,
claims that generator replacement produces only a bounded-dimensional linear family.
```

The result is about source generation, not about the cost of applying one
already available source to one query.

## 9. What remains open

Not closed:

```text
a nonlinear compiler that receives one public G and generates one source,
a fixed-G evaluator that never supports all generator replacements from one dictionary,
rank collapse modulo the secp256k1 field prime,
nonlinear product trees,
target-dependent modular composition,
nonlinear determinant, resultant, theta, or continuation mechanisms,
unrestricted arithmetic circuits.
```

The remaining positive question is now narrower:

> Can one fixed public generator produce its own oriented source through a
> nonlinear, nonlocal circuit whose complete cost is strictly below the square
> root frontier, without storing a fixed linear basis for all possible marked
> generators?

## 10. Formalization boundary

`Ecdlp/Proved/Uorc056OrientedSourceRank.lean` kernel-checks:

```text
injectivity of nonzero column scaling,
the signed block action on symmetric and antisymmetric inputs,
negation closure of a linear span,
exact secp256k1 and frozen arithmetic totals.
```

Lean does not formalize multiplicative character Fourier transforms, primitive
Dirichlet `L(0,chi)` nonvanishing, the all-prime rank theorem, or the concrete
finite-field Gaussian eliminations. These are stated separately rather than
being hidden behind the kernel-checked label.

## 11. Successor

The successor is

```text
FIXED-G-NONLINEAR-SOURCE-COMPILER-082.
```

It must work with one fixed public `(E,G,Q)` and avoid a fixed linear dictionary
for every generator replacement. The highest-priority mechanisms are:

```text
nonlinear divide-and-conquer generation of one oriented source,
target-dependent modular composition,
recursive oriented resultants,
transposed evaluation whose source action is generated on demand,
a secp256k1 modular rank certificate if the linear route is retained.
```

Required flags:

```text
marked_generator_source_formula_verified=true
characteristic_zero_half_source_rank_exact=true
frozen_base_field_half_source_rank_full=true
fixed_linear_dictionary_subroot_possible_char0=false
secp_base_field_half_source_rank_proved=false
nonlinear_oriented_source_compiler_found=false
sublinear_transposed_oriented_functional_found=false
public_nonlocal_primitive_defined=false
primitive_creates_branch_sensitivity=false
exact_oriented_root_extraction_found=false
exact_parity_extraction_found=false
complete_cost_gate_passed=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```
