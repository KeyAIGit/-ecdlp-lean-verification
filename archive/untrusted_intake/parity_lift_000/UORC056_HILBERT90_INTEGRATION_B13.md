# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track B13: compact cocycle normalization and Hilbert-90 integration boundary

Date: 2026-08-14

Status: **the canonical oriented principal factor from B7A has a public translation-cocycle representative of straight-line size `O(log n)` modulo one base-field scalar. Exact normalization of that representative is a cyclic norm, and recovery of the global oriented factor is a multiplicative Hilbert-90 lift. The standard exact normalization and lift use `n` translated terms. No strict sub-square-root evaluator is obtained.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted. Executable checks use only fixed toy curves, fixed public subgroup generators, and fixed public cosets disjoint from those subgroups.

## 1. Frozen central target

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with preprocessing, advice, memory, representation, branch selection, normalization, query work, and online work all charged inside

```text
O(n^(1/2-epsilon)).
```

B7A, added after the earlier B8-B12 sequence was already underway, constructed the exact generator-oriented principal factor

```text
f_G(P)=A_G^pol(x(P))+y(P)B_G^pol(x(P))
```

with divisor

```text
D_G=sum_(r=1)^M [2rG]+[A_G]-N[O],
M=(n-1)/2,
N=M+1=(n+1)/2,
S_G=[-4^(-1)]G,
A_G=-S_G=[4^(-1)]G.
```

It also obtained

```text
(A_G^pol)^2-(X^3+7)(B_G^pol)^2
 =c_G K_H(X)(X-x(S_G))
```

and the exact parity selector

```text
[f_G(-Q)-f_G(Q)]/[f_G(-Q)+f_G(Q)]=(-1)^k
```

outside one fully public exceptional pair.

Packages B8-B12 independently found a compact local cocycle for the alternating Miller potential `H_G` and isolated endpoint integration as the unresolved operation. B13 places the B7A principal factor and that alternating potential in one multiplicative Hilbert-90 framework, then audits the exact normalization and lift cost. It asks whether the global oriented section can be recovered from a short local recurrence.

## 2. Public translation operator

Put

```text
T=[2]G
```

and let the pullback operator be

```text
(sigma u)(P)=u(P+T).
```

Because `2` is invertible modulo the odd prime `n`, translation by `T` has order `n` on every `H`-coset.

Define the exact multiplicative cocycle

```text
h_G(P)=sigma(f_G)(P)/f_G(P)=f_G(P+T)/f_G(P).        (B13.1)
```

Shifting the canonical even support by `-T` cancels every interior point and leaves only one boundary replacement:

```text
{2G,4G,...,(n-1)G}-T
 ={O,2G,4G,...,(n-3)G}.
```

Consequently

```text
div(h_G)
 =[O]-[-G]+[A_G-T]-[A_G]-N[-T]+N[O].              (B13.2)
```

The global half-divisor has therefore collapsed locally to a divisor with constant-size support plus one large public Miller multiplicity.

## 3. Compact projective Miller representative

Let `F_(m,R)` be the standard Miller function

```text
div(F_(m,R))=m[R]-[mR]-(m-1)[O].
```

For

```text
m=N=(n+1)/2,
R=-T,
```

we have

```text
N(-T)=-G.                                               (B13.3)
```

Let

```text
g_(P,Q)=ell_(P,Q)/v_(P+Q),
```

so that

```text
div(g_(P,Q))=[P]+[Q]-[P+Q]-[O].
```

The tangent line at `-G` has divisor

```text
div(ell_(-G,-G))=2[-G]+[T]-3[O].
```

A direct divisor calculation now gives

```text
boxed:
h_G(P) is proportional over F_p^* to
h_0,G(P)
 =g_(A_G-T,T)(P)
  /[ell_(-G,-G)(P) F_(N,-T)(P)].                    (B13.4)
```

Indeed, the divisor of the right side is exactly `(B13.2)`.

This is a genuine compression:

```text
one Miller loop with multiplier N       O(log n) line steps
one addition-line quotient              O(1)
one tangent line                         O(1)
```

For secp256k1, the public multiplier `N` has 255 bits. A binary Miller chain uses

```text
254 doubling line steps,
191 addition line steps,
445 Miller line steps total,
plus 2 external line factors.                            (B13.5)
```

The result is generator-sensitive. Replacing `G` by `-G` reverses the translation and applies the expected negation pullback to the cocycle.

The result is projective, not yet an exact normalized coboundary. There is a constant `lambda_G in F_p^*` such that

```text
h_G=lambda_G h_0,G.                                    (B13.6)
```

## 4. Exact scalar normalization is a cyclic norm

Since `h_G=sigma(f_G)/f_G`, its cyclic norm telescopes:

```text
Norm_sigma(h_G)
 =product_(j=0)^(n-1) sigma^j(h_G)
 =1.                                                    (B13.7)
```

The projective representative has constant norm

```text
nu_G=Norm_sigma(h_0,G) in F_p^*.
```

Equation `(B13.6)` gives

```text
lambda_G^n nu_G=1.                                     (B13.8)
```

For secp256k1,

```text
gcd(n,p-1)=1,
```

so the `n`-th power map on `F_p^*` is bijective. Therefore the exact scalar is uniquely determined by

```text
boxed:
lambda_G=(nu_G^(-1))^(n^(-1) mod (p-1)).               (B13.9)
```

This removes a logical ambiguity but does not yet give a cheap algorithm. The direct cyclic norm in `(B13.7)` has `n` translated factors. A quotient-function-field norm or resultant representation must charge its degree-`n` state, preprocessing, and memory. B13 has not found a strict sub-square-root procedure for `nu_G`.

Thus the first exact nonlinear bottleneck is now

```text
compute the constant cyclic norm of the compact Miller SLP
without expanding an n-state quotient algebra.                 (B13.10)
```

## 5. The global factor is a multiplicative Hilbert-90 lift

Assume the exact normalized cocycle `h_G` is available. Define

```text
c_0=1,
c_i=product_(j=0)^(i-1) sigma^j(h_G),  1<=i<n.
```

For any auxiliary function `theta` for which the following sum is nonzero, put

```text
b_theta
 =sum_(i=0)^(n-1) c_i sigma^i(theta).                 (B13.11)
```

Using `Norm_sigma(h_G)=1`, a cyclic index shift gives

```text
sigma(b_theta)=h_G^(-1)b_theta.                       (B13.12)
```

Hence

```text
f_theta=b_theta^(-1)
```

satisfies

```text
sigma(f_theta)=h_G f_theta.                           (B13.13)
```

Every solution differs from `f_G` by a function in the fixed field `F_p(E/H)`. The declared divisor, pole order, and B7A normalization select the distinguished oriented factor.

Formula `(B13.11)` is exact, but its standard representation contains

```text
n cumulative coefficients,
n translated theta values,
n summands.                                           (B13.14)
```

Writing the sum by a balanced tree reduces parallel depth, not charged size. A faster lift must exploit additional structure and must not hide a degree-`n` normal basis, quotient algebra, circulant matrix, or trace vector in free advice.

The central task has therefore acquired a sharper equivalent form inside the B7A route:

```text
boxed:
evaluate the distinguished Hilbert-90 lift f_G(Q),
or directly B_G^pol(x(Q))/A_G^pol(x(Q)),
without constructing the n-term lift or the dense Pell factor. (B13.15)
```

## 6. Relation to the alternating Miller potential from B8-B12

The B8 potential `H_G` obeys another public relation

```text
H_G(P+2G)=c_2(P)H_G(P).
```

Thus `H_G` is also a multiplicative coboundary for the same order-`n` translation action. B9 segment products are its cumulative coefficients, and the cyclic elliptic factorial of B12 is one explicit presentation of the corresponding global potential. The Hilbert-90 formulation does not replace those packages. It identifies their common integration problem:

```text
compact cocycle -> exact cyclic normalization -> distinguished global section.
```

For the B7A factor, B13 additionally supplies the explicit projective Miller representative `(B13.4)` and verifies its exact scalar normalization on generic public cosets.

## 7. Why the compact local edge is not already parity

The cocycle gives a relative transition

```text
f_G(P+T)/f_G(P).
```

It is invariant under replacing `f_G` by an invariant multiple from the quotient field. It therefore does not choose the global half-divisor section by itself.

This is the function-field version of the earlier EDS gauge obstruction:

```text
short local edge          available,
absolute global section   missing.
```

At points of `H`, the cocycle also has its declared zeros and poles exactly where the even/odd boundary is crossed. A direct field-value recurrence through those singular points is not a parity evaluator. One must reconstruct the rational section or its relevant local limits.

## 8. Frozen exact replay

The executable

```text
experiments/parity_lift_000/uorc056_hilbert90_integration.py
```

uses five fixed curves with fixed public prime-order subgroups and fixed public cosets disjoint from those subgroups:

```text
(p,n,G,R,#E(F_p))=
(31,  7, (27, 6),  (0,10),  21),
(37, 13, (8,36),   (0, 9),  39),
(101,17, (62,50),  (4,24), 102),
(103,37, (38,17),  (0,25), 111),
(109,43, (4,17),   (0,15), 129).
```

Across 117 generic coset points it verifies exactly:

1. every selected coset has length `n` and is disjoint from `H`;
2. `N(-T)=-G`;
3. the B7A principal factor is nonzero on the outside coset;
4. `h_0,G` from `(B13.4)` is proportional to `f_G(P+T)/f_G(P)` by one constant independent of `P`;
5. the exact cocycle norm is one;
6. the projective norm satisfies `(B13.8)`;
7. unique `n`-th-root normalization recovers the exact cocycle;
8. the explicit `n`-term Hilbert-90 sum reconstructs `f_G` up to one invariant scalar;
9. generator negation has the predicted cocycle covariance;
10. all Miller line-step counts agree with the public binary chain.

All arithmetic is exact. The outside cosets are used only to avoid evaluating rational functions at their declared subgroup zeros and poles. No unknown scalar is recovered.

## 9. Formalization boundary

The Lean file

```text
Ecdlp/Proved/Hilbert90IntegrationBoundary.lean
```

kernel-checks only the elementary algebraic core:

1. the half-plus-one scalar identity behind `N(-T)=-G`;
2. telescoping products of multiplicative coboundaries;
3. cyclic norm one when the endpoint equals the starting value;
4. the reciprocal local step used by the Hilbert-90 lift;
5. the exact cardinality `n` of the standard summation index.

It does not formalize elliptic curves, divisor pullbacks, Miller functions, quotient function fields, cyclic Galois extensions, secp256k1, parity recovery, or ECDLP.

## 10. Decision

```text
Canonical oriented principal factor                         yes, B7A
Compact local translation divisor                           yes
Projective cocycle SLP size                                 O(log n)
Exact secp Miller line steps                                445 plus 2 factors
Exact scalar determined mathematically                      yes, by cyclic norm
Known strict sub-square-root cyclic-norm algorithm          absent
Standard multiplicative Hilbert-90 lift size                n terms
Known compact distinguished lift                            absent
Public parity oracle                                        absent
Classical sub-square-root ECDLP                              absent
```

This is real constructive progress beyond B8-B12: the large oriented divisor no longer needs to be treated as an unstructured degree-`Theta(n)` object at the local level. Its translation derivative has a short public Miller representation. The unresolved information is now isolated in a precise global integration problem.

## 11. Immediate successor

The next package, provisionally `UORC056-HILBERT90-TRACE-COMPRESSION-B14`, should not search for another local edge. B8 and B13 already provide two explicit compact local representatives. It should test one of the following exact compression mechanisms for `(B13.11)`:

1. transposed trace evaluation in the cyclic quotient algebra without materializing a degree-`n` normal basis;
2. displacement-rank or circulant compression of the Hilbert-90 linear system, with the cost of constructing its first row charged;
3. CM/GLV block decomposition of the trace orbit, proving that the block state is genuinely smaller than `sqrt(n)`;
4. half-gcd or subresultant extraction of only `B_G^pol(x(Q))/A_G^pol(x(Q))` from the Pell norm equation;
5. a nonlinear segment monoid whose combine law carries the exact normalization scalar and whose total represented state is proved sub-square-root.

Any candidate is rejected if it supplies `nu_G`, a normal basis, a full trace row, or the distinguished Hilbert-90 eigenvector as uncharged advice.
