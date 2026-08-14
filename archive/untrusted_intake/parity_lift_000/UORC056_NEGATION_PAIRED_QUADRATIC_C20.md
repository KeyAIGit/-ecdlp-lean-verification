# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C20: negation-paired quadratic resolvent, odd-prism obstruction, and norm-one reduction

Date: 2026-08-14

Status: **C20 closes the declared negation-paired, pair-product, branch-even quadratic-extraction, and Dickson-recurrence mechanisms. The compact function `K(P)=Z(P)Z(-P)` is exact, but the paired sum `S=Z+Z(-P)` and paired difference `D=Z-Z(-P)` have linear subgroup divisor support. Every odd Dickson polynomial contains the hard factor `S`. The universal adjacent/negation product graph is the odd prism `C_n square K_2`; its edge data determine all endpoint values only up to one global sign, and even after both telescoping constraints a Laurent evaluator for one oriented value needs `(n-1)/2` edge products. A new positive reduction is obtained: the hard cubic GLV norm has a compact public quadratic norm factor, leaving an exact dense norm-one Hilbert-90 cocycle. No strictly sub-square-root evaluator, parity oracle, or sub-square-root ECDLP algorithm is found.**

Only the public seven-curve extension corpus, six public generator replacements, and public secp256k1 constants are used. No external point with unknown scalar, wallet, private key, or production target is accepted.

## 1. Fixed setup

Let

```text
E: y^2=x^3+7,
H=<G>, |H|=n=2m+1,
P_k=[k]G,
phi(x,y)=(beta*x,y),
phi(P_k)=P_(lambda*k),
lambda^2+lambda+1=0 mod n.
```

C15 constructs the endpoint gauge

```text
Z(P)=h_G(P)/h_G(P+G),
```

with one unresolved global involution

```text
sigma: Z -> -Z.
```

C19 proves the compact negation product

```text
K(P)=Z(P)Z(-P)
    =(x(P)-x(P_(a-1))) /
      ((x(P)-x(P_1))(x(P)-x(P_a))(x(P)-x(P_m))).   (C20.1)
```

Define

```text
S(P)=Z(P)+Z(-P),
D(P)=Z(P)-Z(-P).
```

Then

```text
sigma(S)=-S,
sigma(D)=-D,
sigma(K)=K.                                      (C20.2)
```

## 2. Exact pair algebra

The basic identities are

```text
boxed:
S^2-D^2=4K,                                      (C20.3)
Z(-P)=K(P)/Z(P),                                 (C20.4)
Z(P)=(S(P)+D(P))/2,
Z(-P)=(S(P)-D(P))/2.                             (C20.5)
```

If the global rational representation is

```text
Z(P)=(A(x(P))+y(P)B(x(P)))/C(x(P)),
```

then point negation gives

```text
Z(-P)=(A(x(P))-y(P)B(x(P)))/C(x(P)),
```

and hence

```text
boxed:
S=2A/C,
D=2yB/C,
K=(A^2-(x^3+7)B^2)/C^2.                         (C20.6)
```

The difference-of-squares numerator in `K` has a large exact cancellation, producing the degree `1/3` formula in `(C20.1)`. The individual pieces `A/C` and `yB/C` do not inherit that cancellation.

## 3. The nine-point divisor theorem

The divisor of `(C20.1)` is

```text
div(K)=
  4(O)
  +(P_(a-1))+(P_(1-a))
  -(P_1)-(P_(-1))
  -(P_a)-(P_(-a))
  -(P_m)-(P_(-m)).                               (C20.7)
```

Thus its support is the nine-point set

```text
E_pair={O, plus_or_minus(a-1), plus_or_minus 1,
        plus_or_minus a, plus_or_minus m}.       (C20.8)
```

All nine points are distinct on the public corpus and on the secp256k1 instance.

The exact endpoint divisor from C15 is

```text
z_k=ord_(P_k)(Z)
   =(-1)^k-delta_(k,m)-delta_(k,a)-delta_(k,n-1)
     +delta_(k,a-1)+delta_(k,0).                 (C20.9)
```

For every `k` outside `E_pair`,

```text
z_k in {+1,-1},
z_(-k)=-z_k.                                     (C20.10)
```

Therefore one of `Z(P_k),Z(-P_k)` has a simple pole and the other has a simple zero. Their leading terms cannot cancel in either the sum or the difference:

```text
boxed:
ord_(P_k)(S)=ord_(P_k)(D)=-1
for P_k not in E_pair.                           (C20.11)
```

Consequently,

```text
#supp div(S) >= n-9,
#supp div(D) >= n-9,
deg_poles(S),deg_poles(D) >= n-9,                (C20.12)

deg_poles(S^2),deg_poles(D^2) >= 2(n-9).        (C20.13)
```

These are exact divisor statements for the declared endpoint gauge. They are not unrestricted arithmetic-circuit lower bounds.

## 4. Fixed fields of the paired traces

For `i=0,1,2`, set

```text
S_i(P)=S(phi^i(P)),
D_i(P)=D(phi^i(P)).
```

Define

```text
T_S(P)=sum_i S_i(P),
T_D(P)=sum_i D_i(P).                             (C20.14)
```

The automorphism `phi` cyclically permutes the summands. Point negation fixes every `S_i` and negates every `D_i`. Hence

```text
T_S(phi(P))=T_S(P),   T_S(-P)=T_S(P),
T_D(phi(P))=T_D(P),   T_D(-P)=-T_D(P).           (C20.15)
```

Because

```text
F_p(E)^<phi>=F_p(y)
```

and the even/odd decomposition under `y -> -y` is

```text
F_p(y)=F_p(y^2) direct_sum y*F_p(y^2),
```

we obtain

```text
boxed:
T_S in F_p(y^2)=F_p(x^3),
T_D in y*F_p(y^2)=y*F_p(x^3).                   (C20.16)
```

The replay verifies the corresponding exponent classes modulo three exactly.

### Exact corpus profiles

| p | n | deg signature S | support/poles S | deg signature T_S | support/poles T_S | deg signature T_D | support/poles T_D |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 43 | 31 | 16/0/17 | 30/34 | 18/0/21 | 30/42 | 0/18/21 | 30/42 |
| 61 | 61 | 28/0/29 | 58/58 | 27/0/30 | 60/60 | 0/27/30 | 60/60 |
| 67 | 79 | 40/0/41 | 78/82 | 42/0/45 | 78/90 | 0/42/45 | 78/90 |
| 79 | 67 | 34/0/35 | 66/70 | 36/0/39 | 66/78 | 0/36/39 | 66/78 |
| 97 | 79 | 40/0/41 | 78/82 | 42/0/45 | 78/90 | 0/42/45 | 78/90 |
| 127 | 127 | 64/0/65 | 126/130 | 66/0/69 | 126/138 | 0/63/66 | 120/132 |
| 163 | 139 | 68/0/69 | 136/138 | 69/0/72 | 138/144 | 0/69/72 | 138/144 |

A signature `d_A/d_B/d_C` refers to `(A(x)+yB(x))/C(x)`. Support and poles count nonzero affine subgroup points and total pole multiplicity there.

## 5. Dickson recurrence

Put

```text
alpha=Z(P),
beta0=Z(-P),
alpha+beta0=S,
alpha*beta0=K,
U_j=alpha^j+beta0^j.                             (C20.17)
```

Then

```text
U_0=2,
U_1=S,
boxed:
U_j=S*U_(j-1)-K*U_(j-2).                        (C20.18)
```

The first terms are

```text
U_2=S^2-2K,
U_3=S^3-3KS,
U_4=S^4-4KS^2+2K^2,
U_5=S^5-5KS^3+5K^2S.                            (C20.19)
```

The symbolic replay proves for every `r>=0`:

```text
boxed:
U_(2r) in F_p[S^2,K],
U_(2r+1)=S*V_r(S^2,K).                          (C20.20)
```

Thus every odd Dickson value contains the unresolved branch-odd base `S`. A short recurrence in the public index `j` does not construct `S`.

Outside `E_pair`, one of `alpha,beta0` has order `-1` and the other order `+1`. For every positive `j`, the pole term is unique:

```text
boxed:
ord_(P_k)(U_j)=-j
for P_k not in E_pair.                           (C20.21)
```

Therefore

```text
#supp div(U_j) >= n-9,
deg_poles(U_j) >= j(n-9).                        (C20.22)
```

### Trace screen

The predeclared odd indices were

```text
j in {1,3,5,7,9,15,31}.                         (C20.23)
```

The corpus split was fixed before screening:

```text
discovery: p=43,61,67,
validation: p=79,97,
held-out: p=127,163.                             (C20.24)
```

On all seven base curves, every screened `Tr_phi(U_j)` had support on every nonzero GLV quotient orbit. Six public generator replacements were also checked. Five had full support for every selected `j`. For `p=61` and replacement `G -> [3]G`, `j=1` had support `18/20`, with exactly two cancellations. All replacement screens retained support at least `q-4`, where `q=(n-1)/3`.

This is reproducible support evidence, not a theorem excluding a special arbitrary high index with additional curve-specific structure. The exact all-index theorem is `(C20.20)-(C20.22)`, before GLV trace.

## 6. Quadratic extraction is the original orientation problem

The paired roots satisfy

```text
X^2-SX+K=0,
Delta=S^2-4K=D^2.                               (C20.25)
```

If only `K,S^2,D^2` are available, the possible oriented pairs are

```text
(S,D),
(S,-D),
(-S,D),
(-S,-D).                                        (C20.26)
```

Changing `D` alone swaps `Z(P)` and `Z(-P)`. Changing both `S` and `D` is the original global branch change `Z -> -Z`.

Let `B` be the field generated by public constants and the declared branch-even leaves

```text
K_i,
S_i^2,
D_i^2,
K_i/K_j,
adjacent products,
even elementary symmetric functions,
even Dickson values.                            (C20.27)
```

The involution `sigma` fixes every element of `B`. Addition, multiplication, inversion, trace, norm, and deterministic branching on `B` preserve this invariance. Hence:

```text
boxed:
Every deterministic rational circuit over B is sigma-fixed.  (C20.28)
```

Such a circuit cannot output `S_i`, `D_i`, an odd `U_j`, or parity.

A square-root gate applied to a radicand in `B` produces two possible orientations. A public convention such as a canonical finite-field square root is still a function only of the radicand, so it makes the same choice for the two gauge branches, while the target `S_i` or `D_i` changes sign. Proving that the convention equals the target is exactly the missing orientation theorem. Without such a theorem, the root sign is hidden advice.

This obstruction is scoped to circuits whose leaves are branch-even. It does not exclude a genuinely new independently constructed branch-odd public anchor.

## 7. Adjacent and negation products form an odd prism

For a generic variable point `P`, define

```text
u_k=Z(P+[k]G),
v_k=Z(-P-[k]G),
A^+_k=u_k*u_(k+1),
A^-_k=v_k*v_(k+1),
K_k=u_k*v_k.                                    (C20.29)
```

The product graph has two `n`-cycles and one perfect matching. It is the prism

```text
Gamma_n=C_n square K_2.                         (C20.30)
```

For odd `n`:

```text
vertices=2n,
edges=3n,
connected components=1,
cycle rank=n+1,
shortest odd cycle=n.                           (C20.31)
```

Suppose two generic vertex assignments have the same edge products. Their ratios `r_v` satisfy

```text
r_u*r_v=1
```

on every edge. Connectedness makes the ratios alternate between `t` and `t^-1`; an odd cycle forces `t^2=1`. Therefore the generic fibre is exactly

```text
{(u,v),(-u,-v)}.                                (C20.32)
```

Thus edge products reconstruct the endpoint values only up to one global sign. A connected spanning graph on `2n` vertices needs at least `2n-1` edges, and finite reconstruction also needs an odd cycle, so at least `2n` edge products are needed to reconstruct every vertex up to sign. This is tight: one odd `u`-cycle plus all `n` matching edges has `2n` edges.

### Tight Laurent support with telescoping anchors

The endpoint definition gives

```text
product_k u_k=1,
product_k v_k=1.                                (C20.33)
```

In the Laurent monomial model over all prism edge products, an expression equal to one oriented value `u_0` must use at least

```text
boxed:
(n-1)/2 edge factors.                            (C20.34)
```

Proof sketch: if fewer than `(n-1)/2` edges are used, at least one non-target `u` vertex and one `v` vertex are untouched. In the exponent-lattice equation this forces both telescoping multipliers to zero. The right side then has total exponent one, while every edge column has even total exponent two, a contradiction.

The bound is attained by

```text
boxed:
u_0=(product_(j odd) A^+_j)^(-1).         (C20.35)
```

The negation matching products `K_k` do not improve this Laurent support.

Curve-specific rational identities may compress individual edge evaluations, but they cannot break `(C20.32)`: every pair product is exactly invariant under the global sign involution.

## 8. Bounded nonlinear grammar

The declared grammar contains rational combinations of

```text
K_i,
Tr(K_i), Norm(K_i),
S_i^2,D_i^2,
S_i^2/K_i,D_i^2/K_i,
Tr(S_i^2),Tr(D_i^2),
even elementary symmetric functions,
even Dickson polynomials.                       (C20.36)
```

Every leaf and every rational output is branch-even by `(C20.28)`. Exact signatures show:

```text
K, Tr(K), Norm(K): constant-degree objects,
S^2,D^2,S^2/K,D^2/K: linear-degree objects,
Tr(S^2),Tr(D^2): linear-degree fixed-field objects. (C20.37)
```

Ratios are treated as global rational functions, including their zeros and poles. No candidate is credited by silently deleting collision points. No branch-odd evaluator appears in discovery, validation, held-out, or generator-replacement tests.

## 9. New positive reduction: compact norm plus Hilbert-90 twist

Let

```text
M(P)=N_phi(Z)(P)=product_(i=0)^2 Z(phi^i(P)).    (C20.38)
```

This is the C16 branch-odd cubic GLV norm. Since `K=Z*Z after negation`,

```text
boxed:
M(P)M(-P)=N_phi(K)(P).                           (C20.39)
```

The right side is compact. From `(C20.1)`,

```text
N_phi(K)(P)=
 (x(P)^3-x(P_(a-1))^3) /
 product_(j in {1,a,m})(x(P)^3-x(P_j)^3).        (C20.40)
```

Because `x^3=y^2-7`, this is a degree `1/3` rational function in `y^2`.

More strongly, define the public oriented factor

```text
C0(P)=
 (y(P)-y(P_(a-1))) /
 ((y(P)-y(P_1))(y(P)-y(P_a))(y(P)-y(P_m))).      (C20.41)
```

The replay proves exactly

```text
boxed:
C0(P)C0(-P)=N_phi(K)(P).                         (C20.42)
```

Therefore

```text
R(P)=M(P)/C0(P)                                  (C20.43)
```

satisfies

```text
boxed:
R(P)R(-P)=1.                                     (C20.44)
```

The public factor `C0` has constant signature `6/3/9`, affine support `12`, and affine pole degree `9` on every base curve. The norm-one twist `R` remains dense:

| p | n | signature C0 | support/poles C0 | signature R | support/poles R |
|---:|---:|---:|---:|---:|---:|
| 43 | 31 | 6/3/9 | 12/9 | 24/21/24 | 30/24 |
| 61 | 61 | 6/3/9 | 12/9 | 45/42/45 | 60/45 |
| 67 | 79 | 6/3/9 | 12/9 | 60/57/60 | 78/60 |
| 79 | 67 | 6/3/9 | 12/9 | 48/45/48 | 66/48 |
| 97 | 79 | 6/3/9 | 12/9 | 60/57/60 | 78/60 |
| 127 | 127 | 6/3/9 | 12/9 | 96/93/96 | 126/96 |
| 163 | 139 | 6/3/9 | 12/9 | 102/99/102 | 138/102 |

This is the strongest positive structural output of C20. The orientation problem is no longer an arbitrary square root. It is a concrete norm-one cocycle in the quadratic extension

```text
F_p(y)/F_p(y^2).                                 (C20.45)
```

By Hilbert 90, a norm-one rational function has the form

```text
R(y)=H(y)/H(-y)                                  (C20.46)
```

for some rational `H`. Finding or evaluating the dense twist with sub-square-root fully charged cost is the successor problem.

## 10. secp256k1 transfer

For

```text
n=
115792089237316195423570985008687907852837564279074904382605163141518161494337,
```

C20 gives

```text
paired S,D support and pole lower bound:
115792089237316195423570985008687907852837564279074904382605163141518161494328,

paired-square pole lower bound:
231584178474632390847141970017375815705675128558149808765210326283036322988656,

U_31 pole lower bound:
3589554766356802058130700535269325143437964492651322035860760057387063006324168,

pair-product Laurent support lower bound:
57896044618658097711785492504343953926418782139537452191302581570759080747168,

generic prism reconstruction edge lower bound:
231584178474632390847141970017375815705675128558149808765210326283036322988674.
```

The respective bit lengths are `256`, `256`, `261`, `255`, and `257` where recorded by the replay.

## 11. Scoped answers

```text
compact_K_used                                      true
paired_sum_compact_evaluator_found                  false
paired_difference_compact_evaluator_found           false
quadratic_sign_selected_without_advice              false
Dickson_divisor_collapse_found                      false
pair_product_global_sign_lower_bound_proved         true
compact_public_Hilbert90_factor_found               true
norm_one_twist_remains_dense_on_corpus              true
sub_sqrt_evaluator_found                            false
parity_oracle_found                                 false
sub_sqrt_ecdlp_found                                false
```

## 12. What is closed and what is not

Closed within the declared model:

```text
exact K,S,D pair algebra,
nine-point exception theorem,
linear support of S,D,S^2,D^2,
fixed fields of Tr_phi(S),Tr_phi(D),
all-index Dickson factorization and untraced support theorem,
predeclared Dickson trace screen through j=31,
branch-even rational grammar,
branch-even square-root orientation gate,
odd-prism pair-product reconstruction,
tight Laurent edge-support lower bound,
compact GLV/negation norm factorization,
public Hilbert-90 norm-one reduction.
```

Not closed:

```text
an independently constructed compact branch-odd anchor,
arbitrary nonlinear circuits outside the fixed-leaf grammar,
a direct formula for a special high-index Tr_phi(U_j) not constructed through S,
sub-square-root evaluation of the norm-one twist R,
a general arithmetic-circuit lower bound,
Lean formalization of C20.
```

## 13. Replay

The deterministic replay uses:

```text
7 public curves,
6 public generator replacements,
7 odd Dickson indices,
exact rational identities,
local Laurent valuations,
fixed-field exponent certificates,
prism graph certificates,
secp256k1 exact integer bounds.
```

Result SHA-256, excluding the digest field:

```text
74db667ddeb9df578bc8563192f48d5e422696628876d739a0c8fd473114c4c3
```

## 14. Successor

The next package is

```text
QUADRATIC-HILBERT90-NORM-ONE-TWIST-071.
```

It must determine whether the exact cocycle

```text
R(y)R(-y)=1
```

can be represented or evaluated below the square-root boundary without receiving an oriented factor, a hidden square-root sign, or linear-size divisor advice.
