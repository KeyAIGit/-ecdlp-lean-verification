# NORMALIZED-PERIOD-BLACKBOX-032

Date: 2026-08-12

Status: **exact dual-pairing realization and orbit-selection obstruction for the normalized Gaussian-period carry observable**.

No external point, private key, wallet, or production-sized discrete-log target is accepted. This package constructs no public carry, R3, parity, or ECDLP decoder.

## 1. Input object

Let `H=<G>` be a cyclic subgroup of odd prime order `n`, let `lambda` have order three modulo `n`, and choose a primitive phase `zeta_n`. For

```text
Q=[k]G
```

define

```text
M_a(k)=product_(j=0..2) (1-zeta_n^(a*lambda^j*k)),
U_a(k)=M_a(k)/M_a(1).
```

The generator-normalized observable from package 031 is the distinguished case

```text
U_G(Q)=U_1(k).
```

Because the three exponents sum to zero modulo `n`, `M_a(k)` is the anti-conjugate Gaussian-period resolvent. Its real sign after normalization is the GLV carry sign up to the public calibration at `G`.

## 2. Cyclotomic-unit norm identity

Put

```text
r_j=zeta_n^(a*lambda^j).
```

Then

```text
U_a(k)
 = product_(j=0..2) (1-r_j^k)/(1-r_j)
 = Norm_C3((1-zeta_n^(a*k))/(1-zeta_n^a)).       (N1)
```

Thus the exact normalized carry observable is a relative norm of a cyclotomic `q`-integer. This is a substantial simplification of its algebraic type: it is not an arbitrary theta value, but a three-factor norm of one faithful order-`n` phase.

For known `k`, the numerator can be evaluated numerically with `O(log n)`-bit precision. Indeed

```text
|M_a(k)|
 = 8 product_j |sin(pi*a*lambda^j*k/n)|
 >= 8 sin(pi/n)^3,
```

because every exponent is nonzero modulo the prime `n`. Precision is therefore not the central obstruction. The missing operation is evaluating the unknown-index phase from `Q`.

## 3. Exact pairing blackbox

Let `T` be an independent `n`-torsion point and let `e_n` be a non-degenerate bilinear pairing normalized by

```text
e_n(G,T)=zeta_n.
```

Then bilinearity gives

```text
e_n(Q,T)=zeta_n^k,
e_n([lambda^j]Q,T)=zeta_n^(lambda^j*k).
```

Consequently

```text
U_G(Q)
 = product_(j=0..2)
     (1-e_n([lambda^j]Q,T))
     /(1-e_n([lambda^j]G,T)).                    (P1)
```

Equation `(P1)` is an exact bounded-rank blackbox identity. It answers one part of the package positively:

```text
bounded number of dual-phase evaluations -> exact U_G(Q).
```

But it also identifies the missing datum exactly. The identity requires a nontrivial dual torsion direction `T`. Points in the public line `H` do not supply it: alternating pairings are trivial on `H x H`, and the GLV orbit remains scalar-dependent inside `H`.

In the CM description, the required `T` lies in the complementary conjugate kernel rather than in the rational kernel `H`.

## 4. Full dual norm collapses

Let `T` run through all nonzero points of the dual cyclic line. For fixed nonzero `k`, multiplication by `k` permutes the nonzero residues modulo `n`. Therefore

```text
product_(a=1..n-1)
  (1-zeta_n^(a*k))/(1-zeta_n^a)
=1.                                               (F1)
```

Equivalently, the full norm over every possible dual generator is exactly constant and loses all information about `k`.

The same phenomenon holds after grouping by the GLV subgroup

```text
C3={1,lambda,lambda^2}.
```

Multiplication by `k` permutes the `C3` cosets, so

```text
product_(a mod C3) U_a(k)=1.                      (F2)
```

Thus averaging or norming over the un-oriented complementary kernel cannot recover carry. A successful construction must select one dual `C3` orbit rather than use a symmetric full-kernel object.

## 5. Exact orbit-choice count

The normalized functions satisfy

```text
U_(lambda*a)(k)=U_a(k),
U_(-a)(k)=U_a(k).
```

Hence the natural orbit selector is indexed by

```text
(Z/nZ)^*/(plus_or_minus C3),
```

which has

```text
(n-1)/6
```

states.

On the frozen toy family the complete sign signatures are distinct for every such class. This is the same state count as

```text
Gaussian-period conjugate pairs;
generator-oriented half-kernel degree;
anti-Frobenius normalized-resolvent states.
```

For secp256k1 the count is

```text
19298681539552699237261830834781317975472927379845817397100860523586360249056.
```

This equality is a representation-size statement, not a general circuit lower bound.

## 6. Why normalization at G does not remove the dual choice

Changing the dual generator from `T` to `[a]T` changes the normalized observable to

```text
U_a(k)=M_a(k)/M_a(1).
```

The denominator calibrates the anti-Frobenius scale at the public generator, but the resulting function still depends on the class of `a` modulo `plus_or_minus C3`. In general

```text
U_a(k) != U_1(k).
```

Therefore anchoring at `G` removes an arbitrary scalar on one anti-invariant line, but it does not canonically choose the dual line or its `C3` orbit.

This is the precise reason that a kernel-only CM, theta, sigma, or pairing construction cannot become generator-oriented merely by dividing by its value at `G`.

## 7. Scoped decision for bounded-rank blackboxes

Within the standard central-extension, biextension, and pairing realization:

```text
Can U_G be written using boundedly many phase evaluations?       yes
Exact formula                                                    (P1)
Does the public rational subgroup provide the dual direction?    no
Does full-kernel norm retain carry?                              no, it is 1
Does normalization at G remove orbit selection?                 no
Explicit orbit choices                                           (n-1)/6
Public sub-sqrt dual-orbit selector                              absent
Public carry / hard-R3 decoder                                   absent
Unconditional sub-sqrt ECDLP algorithm                           absent
```

This package does not prove that every conceivable nonlinear arithmetic circuit must explicitly materialize a dual orbit. It closes the standard bounded-rank pairing/theta blackbox unless it comes with a new compact dual-orbit selector.

## 8. Relation to elliptic nets

Standard elliptic net polynomials are rational functions attached to fixed linear relations among finitely many points, and their matrix pullback laws carry explicit quadratic normalization factors. They can realize Miller and pairing line functions, but an exact realization of `(P1)` still needs the independent dual torsion input or an equivalent splitting.

A proposed net/sigma formula is therefore admitted only if it supplies one of the following new ingredients:

```text
an independently defined complementary-kernel orbit;
a direct Q-only evaluation of the relative cyclotomic norm;
a proof that its normalization is not a disguised faithful dual character.
```

Merely replacing the pairing factors in `(P1)` by net-polynomial notation does not change the algorithmic cost.

## 9. Next object

The successor is

```text
DUAL-C3-ORBIT-SELECTOR-033.
```

Central question:

> Can the public CM data `(E,G,phi,Frobenius)` select and evaluate one class in the complementary dual quotient `(Z/nZ)^*/(plus_or_minus C3)` with total time, memory, preprocessing, advice, and precision `O(n^(1/2-epsilon))`, without constructing an independent `n`-torsion point, a faithful order-`n` character, or an `(n-1)/6`-entry table?

The theorem-first obligations are:

1. express the complementary CM kernel and its `C3` action exactly;
2. prove the full-orbit norm collapse and the `plus_or_minus C3` covariance;
3. classify kernel-only and Frobenius-symmetric orbit selectors;
4. test whether a generator-sensitive CM ideal, polarization, or theta characteristic distinguishes a single dual orbit;
5. count the field of definition and advice size;
6. obtain either a compact exact selector or a scoped no-go for standard CM/polarization data.

No new broad statistical search is admitted without a new exact orbit-selection identity.

## 10. Formalization boundary

`Ecdlp/Proved/NormalizedPeriodBlackbox.lean` formalizes elementary normalized-resolvent identities, negation cancellation, and the fact that a full product ratio is one when its numerator is a permutation of its denominator.

Lean does not formalize Weil pairings, complementary CM kernels, cyclotomic fields, Galois orbit degrees, or the claim that every geometric blackbox factors through `(P1)`. Those remain explicit premises of the scoped result.
