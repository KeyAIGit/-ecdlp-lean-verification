# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C31A: forced secp256k1 finite-characteristic source defect

Date: 2026-08-15

Status: **C31's characteristic-zero rank theorem remains correct, and all five
frozen base-field matrices remain full rank. The actual secp256k1 base field is
exceptional. Exact arithmetic gives
`ord_n(2)=ord_p(2)=(n-1)/2`. Therefore exactly two odd multiplicative
characters satisfy `chi(2)=1/2`, and the source eigenvalue vanishes for both.
The secp256k1 half-source matrix consequently has nullity at least two and rank
at most `(n-1)/2-2`. This is a two-dimensional forced collapse, not a
sub-root compression. The package does not prove that the nullity is exactly
two, because additional odd weighted character sums may also vanish modulo
`p`. No nonlinear anchor-propagation algorithm, parity evaluator, or
sub-square-root ECDLP algorithm is constructed.**

Only public secp256k1 constants, deterministic integer factorization, exact
modular exponentiation, symbolic character identities, and small public prime
witnesses are used. No external unknown-scalar point, private key, wallet,
production target, dense source vector, or branch table is accepted.

## 1. C31 boundary being resolved

C31 defines the half-source matrix

```text
M_(u,r)=epsilon([r*u^(-1)]_n),
1<=u,r<=(n-1)/2,
```

where

```text
epsilon(a)=(-1)^a
```

uses the canonical nonzero residue modulo the subgroup prime `n`.

Over characteristic zero, multiplicative Fourier analysis gives

```text
rank(M)=(n-1)/2.
```

C31 deliberately did not transfer that result to the actual curve field
`F_p`, because an integer determinant can vanish after reduction modulo a
particular prime.

C31A proves that such a reduction defect is not merely possible here. It is
forced by the exact secp256k1 arithmetic.

## 2. General finite-characteristic zero mechanism

Let

```text
U=(Z/nZ)^*,
|U|=n-1=2m,
```

and work over the algebraic closure of a field of odd characteristic `p`, with
`p!=n`.

For a multiplicative character `chi` of `U`, define

```text
H_chi=sum_(a=1)^m chi(a),
W_chi=sum_(a=1)^(n-1) a chi(a),
lambda_chi=sum_(a in U) epsilon(a)chi(a).         (C31A.1)
```

For every nontrivial odd character,

```text
lambda_chi=2 chi(2) H_chi,                       (C31A.2)
```

and the exact weighted permutation identity is

```text
n chi(2) H_chi=(1-2chi(2))W_chi.                 (C31A.3)
```

If

```text
chi(2)=1/2,                                      (C31A.4)
```

then the right side of `(C31A.3)` vanishes. Since `n` and `chi(2)` are nonzero
in characteristic `p`,

```text
H_chi=0,
lambda_chi=0.                                    (C31A.5)
```

Thus every character in the evaluation fiber over `1/2` is an exact source
null direction.

## 3. Exact secp256k1 order coincidence

Let

```text
p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,

n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,

m=(n-1)/2.
```

The executable certificate factors `p-1` and `n-1`, then checks minimality of
the two multiplicative orders. It obtains

```text
boxed:
ord_n(2)=m,
ord_p(2)=m.                                      (C31A.6)
```

The order `m` is even, and exact modular exponentiation gives

```text
2^(m/2)=-1 mod n,
2^(m/2)=-1 mod p.                                (C31A.7)
```

The evaluation map

```text
Hom(U,Fbar_p^*) -> <2>^,
chi -> chi(2)
```

has image size `m`, hence kernel size

```text
(n-1)/m=2.                                       (C31A.8)
```

Because `1/2` has order `m` in `F_p^*`, it lies in the image. Therefore exactly
two characters satisfy `(C31A.4)`.

They are both odd. Indeed

```text
-1=2^(m/2) mod n,
```

so for either character

```text
chi(-1)=chi(2)^(m/2)=(1/2)^(m/2)=-1 mod p.       (C31A.9)
```

Combining `(C31A.5)` through `(C31A.9)` gives exactly two forced zero
multiplicative Fourier eigenvalues.

## 4. Transfer to the half-source matrix

C31 orders the full translate matrix by positive and negative half
representatives and obtains

```text
F=[ M -M
   -M  M ].                                      (C31A.10)
```

The full operator vanishes on symmetric vectors and acts on antisymmetric
vectors through `2M`. The two characters above are odd, hence lie in the
antisymmetric sector. Their zero eigenvalues therefore give

```text
boxed:
nullity_Fp(M)>=2,                                (C31A.11)
```

and

```text
boxed:
rank_Fp(M)<=m-2.                                 (C31A.12)
```

Multiplying source columns by the nonzero values `y([r]G)` is invertible, so
the same defect applies to the oriented-value source matrix.

For secp256k1,

```text
m=
57896044618658097711785492504343953926418782139537452191302581570759080747168,
```

hence the proved rank upper bound is

```text
m-2=
57896044618658097711785492504343953926418782139537452191302581570759080747166.
```

This saves exactly two possible linear directions from the C31
characteristic-zero dimension. It remains a 255-bit state scale.

## 5. Why exact rank is not claimed

The two zeros above come from the public factor

```text
1-2chi(2).
```

For any other odd character, `(C31A.3)` reduces nonvanishing of
`lambda_chi` to nonvanishing of the weighted sum `W_chi` modulo `p`.
Additional zeros are therefore possible if a generalized Bernoulli or
Dirichlet character sum vanishes modulo the field prime.

C31A does not evaluate all such character sums and does not claim

```text
nullity(M)=2.
```

Equivalently, it does not claim that the secp256k1 source rank is exactly
`m-2`. The exact remaining defect is a separate cyclotomic divisibility
problem.

This limitation is explicit because the production matrix is far too large to
materialize and characteristic-zero nonvanishing is insufficient.

## 6. Exact executable certificates

The Python package verifies:

```text
p and n are prime,
complete factorizations of p-1 and n-1,
minimality of ord_n(2)=m,
minimality of ord_p(2)=m,
2^(m/2)=-1 modulo both primes,
evaluation-fiber size 2,
forced nullity lower bound 2.
```

It also exhausts small prime pairs with the same order coincidence and checks
the concrete half-source matrix by exact Gaussian elimination. Every screened
pair has nullity at least two; all screened examples happen to have nullity
exactly two. The latter is finite evidence only.

The output records whether `p^2` divides `2^(m/2)+1`; this is arithmetic
context, not an exact source-rank theorem.

## 7. Effect on C31

Not retracted:

```text
characteristic-zero rank(M)=m,
full rank on all five frozen base fields,
the marked-generator source formula,
the fixed-dictionary lower bound in characteristic zero.
```

Corrected for secp256k1:

```text
full base-field rank is false,
nullity is at least two,
exact nullity remains open.
```

The result does not open a practical linear shortcut. A dictionary of dimension
`m-2` is still exponentially above the square-root gate, and C31A does not even
prove that `m-2` is attainable as the exact rank.

## 8. What C31A closes and leaves open

Closed:

```text
secp256k1 full-rank hypothesis for the half-source matrix,
claims that C31 characteristic-zero rank transfers unchanged to F_p,
claims that the finite-characteristic exception is only hypothetical.
```

Open:

```text
exact secp256k1 half-source rank,
additional odd character zeros modulo p,
a compact nonlinear fixed-G compiler,
public-anchor nonlocal propagation,
sublinear modular composition,
unrestricted arithmetic circuits.
```

## 9. Formalization boundary

`Ecdlp/Proved/Uorc056SecpSourceDefect.lean` kernel-checks:

```text
the weighted-sum zero implication,
the source-eigenvalue zero implication,
2^m=1 modulo n and p,
2^(m/2)=-1 modulo n and p,
the evaluation-fiber arithmetic,
the exact secp dimension and rank-upper-bound arithmetic.
```

Lean does not formalize the character group, surjectivity of the evaluation
map, the count of its fiber, or the block-matrix rank transfer. Those steps are
stated in the note and separated from the kernel-checked core.

## 10. Successor

C31A does not replace the corrected successor:

```text
PUBLIC-ANCHOR-FIXED-G-NONLINEAR-PROPAGATION-082.
```

The canonical anchor remains

```text
Y_G(x(G))=-y(G).
```

The central positive task is still to propagate this one known orientation to
an arbitrary public `Q` without a dense source, scalar index, branch table,
full dual phase, or square-root-width state.

Required flags:

```text
secp_base_field_full_rank=false
secp_base_field_rank_defect_proved=true
secp_base_field_nullity_lower_bound=2
secp_base_field_exact_rank_proved=false
subroot_fixed_dictionary_found=false
nonlinear_anchor_propagation_found=false
exact_parity_extraction_found=false
complete_cost_gate_passed=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```
