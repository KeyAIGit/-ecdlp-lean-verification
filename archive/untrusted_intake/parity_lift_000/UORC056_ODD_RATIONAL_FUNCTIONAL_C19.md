# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C19: odd rational functional calculus and compact negation reciprocity

Date: 2026-08-14

Status: **odd rational functionals are classified by the two local orders `a=ord_0(R)` and `b=ord_infinity(R)`. Every class except simultaneous poles at zero and infinity receives a linear divisor-support certificate. The unbalanced double-pole class has exact unique-minimum poles on type-1 or type-2 GLV orbits, whose secp256k1 counts are computed exactly by a logarithmic floor-sum certificate. The balanced double-pole class reduces to a one-dimensional residue-ratio spectrum. Exhaustive scans of `T^s+rho/T^s`, `s=1,3,5,7`, and a 162-template rational grammar find no divisor collapse. A new positive structure is found: `K_G(P)=Z_G(P)Z_G(-P)` has an exact degree `1/3` public formula, but it is branch-even and does not select the remaining global sign.**

Only the public seven-curve extension corpus, public generator replacements, and public secp256k1 constants are used. No external unknown-scalar point, wallet, private key, or production target is accepted.

## 1. Setup

Let

```text
E: y^2=x^3+7,
H=<G>, |H|=n,
phi(x,y)=(beta*x,y),
phi([k]G)=[lambda*k]G,
lambda^2+lambda+1=0 mod n.
```

C15 constructs

```text
Z_G(P)=h_G(P)/h_G(P+G)
```

with one unresolved global ambiguity `Z_G -> -Z_G`.

For an odd rational function `R(-T)=-R(T)`, define

```text
Theta_R(P)=sum_(i=0)^2 R(Z_G(phi^i(P)))
          =Tr_<phi>(R(Z_G))(P).                 (C19.1)
```

The endomorphism cyclically permutes the summands, hence

```text
Theta_R in F_p(E)^<phi>=F_p(y).                 (C19.2)
```

Oddness gives the exact branch covariance

```text
Theta_R(-Z_G)=-Theta_R(Z_G).                    (C19.3)
```

Thus every nonzero member is logically an odd selector. The issue is representation and evaluation cost.

## 2. Normal forms and local orders

Every odd rational function can be written in either useful form

```text
R(T)=T*A(T^2)/B(T^2),                           (C19.4)
```

or

```text
R(T)=A(T^2)/(T*B(T^2)).                         (C19.5)
```

For the first form,

```text
a=ord_0(R)=1+2(ord_0(A)-ord_0(B)),
b=ord_infinity(R)=2deg(B)-2deg(A)-1.            (C19.6)
```

For the second,

```text
a=-1+2(ord_0(A)-ord_0(B)),
b=2deg(B)-2deg(A)+1.                            (C19.7)
```

Both are nonzero odd integers.

Outside at most four endpoint-correction orbits, the three GLV conjugates of `Z_G` have valuations in `{+1,-1}`. A type-`r` orbit has `r` zero branches and `3-r` pole branches. Therefore `R(Z_i)` has

```text
r copies of a and 3-r copies of b.              (C19.8)
```

This gives the following exact classification.

* If `a<b`, every nonexceptional type-1 orbit has `ord(Theta_R)=a`.
* If `b<a`, every nonexceptional type-2 orbit has `ord(Theta_R)=b`.
* If `a>0` and `b>0`, every nonexceptional orbit lies in the divisor of every nonzero `Theta_R`.
* If `a<0<b`, all type-0 and type-1 orbits lie in the divisor, giving support at least `(n-1)/6-4`.
* If `b<0<a`, all type-2 and type-3 orbits lie in the divisor, giving the same bound.
* If both orders are negative and unequal, type 1 or type 2 supplies exact unique-minimum poles.
* The only genuine leading-cancellation regime is `a=b=-s<0`, with positive odd `s`.

## 3. Exact parity-type counts

Write

```text
N_0=N_3=y,
N_1=N_2=x,
x+y=(n-1)/6.                                    (C19.9)
```

Let `m=(n-1)/2`, `H={1,...,m}`, and

```text
I=|H intersect lambda^(-1)H|.                   (C19.10)
```

This is the number of directed even-to-even GLV edges, so

```text
I=N_2+3N_3=x+3y.                                (C19.11)
```

Hence

```text
y=(I-(n-1)/6)/2,
x=(3(n-1)/6-I)/2.                              (C19.12)
```

The modular interval count `I` is evaluated with two logarithmic floor sums.

For secp256k1:

```text
N_0=N_3=
4824670384888174809315457708695329493868231844961454349275215130896590062290

N_1=N_2=
14474011154664524427946373126085988481604695534884363047825645392689770186766.
```

This yields the exact scoped support bounds

```text
all-positive orders:
38597363079105398474523661669562635950945854759691634794201721047172720498108

opposite-sign orders:
19298681539552699237261830834781317975472927379845817397100860523586360249052

unbalanced double-pole unique-type orbits:
14474011154664524427946373126085988481604695534884363047825645392689770186762.
```

Their bit lengths are 255, 254, and 253.

## 4. Balanced double-pole residue theorem

Assume `a=b=-s<0`. At a zero branch write

```text
Z_i=alpha_i*t+O(t^2),
```

and at a pole branch

```text
Z_i=gamma_i*t^(-1)+O(1).
```

Normalize the two endpoint principal coefficients of `R` by

```text
rho=r_0/r_infinity.
```

The leading coefficient on a mixed orbit is

```text
r_infinity *
(sum_poles gamma_i^s + rho*sum_zeros alpha_i^(-s)).  (C19.13)
```

If the second sum is nonzero, cancellation occurs for the unique ratio

```text
rho_orbit=
-sum_poles gamma_i^s / sum_zeros alpha_i^(-s).   (C19.14)
```

Therefore one public constant `rho` can cancel the leading pole on no more than the multiplicity of that value in the public orbit-ratio spectrum. Per-orbit fitting is linear advice and is not credited.

## 5. Two invariant formulas

Let

```text
E1=z_0+z_1+z_2,
E2=z_0z_1+z_1z_2+z_2z_0,
E3=z_0z_1z_2.
```

The branch action is `(E1,E2,E3)->(-E1,E2,-E3)`.

For `R(T)=T+c/T`,

```text
Theta_R=E1+c*E2/E3=(E1*E3+c*E2)/E3.            (C19.15)
```

For `R(T)=T/(1+cT^2)`,

```text
N=E1+c(E1E2-3E3)+c^2E2E3,                      (C19.16)

D=1+c(E1^2-2E2)+c^2(E2^2-2E1E3)+c^3E3^2
 =(1-cE2)^2+c(E1-cE3)^2.                        (C19.17)
```

Thus `Theta_R=N/D`. This family has `a=b=+1`, so denominator balancing cannot remove the full nonexceptional endpoint support.

## 6. Exact screens

The public corpus is

```text
(p,n)=
(43,31),
(61,61),
(67,79),
(79,67),
(97,79),
(127,127),
(163,139).
```

All `rho in F_p^*` were scanned for `T^s+rho/T^s`, `s=1,3,5,7`. All `c in F_p^*` were scanned for `T/(1+cT^2)`.

For `s=1`:

| p | quotient orbits | distinct ratios | max multiplicity | leading pole lower bound | min support `T+c/T` | min support `T/(1+cT^2)` |
|---:|---:|---:|---:|---:|---:|---:|
| 43 | 10 | 5 | 1 | 6 | 9 | 9 |
| 61 | 20 | 10 | 2 | 14 | 18 | 16 |
| 67 | 26 | 14 | 2 | 20 | 24 | 25 |
| 79 | 22 | 12 | 2 | 16 | 20 | 21 |
| 97 | 26 | 14 | 2 | 20 | 24 | 25 |
| 127 | 42 | 26 | 2 | 36 | 40 | 41 |
| 163 | 46 | 31 | 2 | 40 | 44 | 43 |

The bounded grammar was fixed before screening:

```text
T*(1+a1 U+a2 U^2)/(1+b1 U+b2 U^2),
(1+a1 U+a2 U^2)/(T*(1+b1 U+b2 U^2)),
U=T^2,
a_i,b_i in {-1,0,1}.
```

It contains `162` templates. The split was

```text
discovery: p=43,61,67,
validation: p=79,97,
held-out: p=127,163.
```

The best support per curve was

```text
9,16,25,21,25,41,43
```

out of

```text
10,20,26,22,26,42,46
```

quotient orbits. All 1134 template-curve local valuations were resolved exactly within the committed 36-term Laurent window. No zero or sub-square-root divisor-support candidate appeared.

## 7. Compact negation product

Define

```text
K_G(P)=Z_G(P)Z_G(-P).                            (C19.18)
```

If `n=2m+1` and `a` is the public C13 class index, then

```text
div(K_G)=
4(O)+(P_(a-1))+(P_(1-a))
-(P_1)-(P_(-1))
-(P_a)-(P_(-a))
-(P_m)-(P_(m+1)).                                (C19.19)
```

After monic normalization,

```text
boxed:
K_G(P)=
(x(P)-x([a-1]G)) /
((x(P)-x(G))(x(P)-x([a]G))(x(P)-x([m]G))).       (C19.20)
```

Therefore

```text
Z_G(-P)=K_G(P)/Z_G(P).                           (C19.21)
```

The replay checks the exact closed form on all seven curves. It also checks six public replacements `G->[u]G`, `u in {2,3,5}`, on the first two curves. In every case the GLV eigenvalue is preserved, the numerator and denominator degrees remain `1` and `3`, the divisor support remains at most nine, and the balanced ratio spectrum remains nonconstant.

This does not select parity. `K_G` is invariant under `Z_G->-Z_G`. It determines the product of the two opposite endpoint values but not the sign of their sum in

```text
X^2-S_G(P)X+K_G(P)=0,
S_G(P)=Z_G(P)+Z_G(-P).                           (C19.22)
```

The simple paired traces `Tr(S_G)` and `Tr(Z_G-Z_G(-P))` remain dense on the corpus.

## 8. Scope and successor

Closed:

```text
all positive-positive local-order pairs;
all opposite-sign pairs;
all unbalanced negative-negative pairs;
exact secp256k1 parity-type counts;
balanced negative leading cancellation as a residue-ratio problem;
the declared one-parameter and 162-template grammars;
compact negation reciprocity.
```

Still open:

```text
arbitrary balanced double-pole rational functions beyond the declared grammars;
variable-coefficient expressions using K_G;
short circuits for S_G=Z_G+Z_G(-P);
quadratic extraction without hidden square-root advice;
unrestricted nonlinear circuits in F_p(y).
```

The successor is

```text
NEGATION-PAIRED-QUADRATIC-RESOLVENT-070.
```

Final flags:

```text
odd_rational_normal_form_classified=true
local_order_pair_classified=true
secp_exact_parity_orbit_counts=true
compact_negation_product_found=true
constant_coefficient_balanced_subsqrt_support_found=false
bounded_rational_synthesis_subsqrt_support_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```

Result SHA-256 without the digest field:

```text
983edb4d3dbf75e2f60e9c9fd1dfcd6b45aa64b5e9c0747b59323274dd53c3fb
```
