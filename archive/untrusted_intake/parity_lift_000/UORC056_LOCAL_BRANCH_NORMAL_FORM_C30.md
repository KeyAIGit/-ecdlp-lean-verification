# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C30: local quadratic-branch normal form and one-point certificate equivalence

Date: 2026-08-15

Status: **every everywhere-regular one-point rational certificate built from public branch-even data and one quadratic branch reduces to `E+O*Y`. If `O` vanishes on any required component, the certificate identifies the two branches there and cannot decode the oriented root on all points. If `O` is a unit on every component, the original branch is recovered by `Y=O^(-1)(C-E)`, so the certificate is a constant-overhead recoding rather than a new compression mechanism. In particular, multiplication or division by the squarefree kernel derivative `K_H'` is a public unit gauge. An exact four-atom local kernel-derivative character screen also has zero survivors on all 46,260 frozen marked-query cases. No public oriented seed, parity evaluator, or sub-square-root ECDLP algorithm is constructed.**

Only public frozen toy curves, public prime orders, deterministic public
polynomial operations, and symbolic rank-two algebra are used. No external
unknown-scalar point, private key, wallet, production target, scalar bits,
root table, or target-dependent orientation advice is accepted.

## 1. Why C30 is the correct successor to autonomous-state rigidity

C29 closes fixed autonomous state updates. A surviving evaluator must therefore
be nonautonomous or target-dependent: it may apply a sequence of public maps to
one query without representing every translation step by one fixed state
transition.

The cheapest possible version would be a one-point certificate. Examples are

```text
K_H'(x(Q)),
K_H''(x(Q))/K_H'(x(Q)),
a residue or local leading coefficient,
a public kernel norm or jet,
a fractional-linear transform of an oriented square root.
```

Such a certificate would be valuable only if it retained the selected branch
but was easier to compute than `Y_G(x(Q))`. C30 gives an exact dichotomy for the
whole rational one-point class.

## 2. Finite-etale quadratic branch algebra

Let

```text
A = product_i K_i
```

be a finite product of fields of odd characteristic. Let `F in A^*`, and form

```text
B=A[Y]/(Y^2-F).
```

The branch involution is

```text
tau(Y)=-Y,
tau(a)=a for a in A.
```

Every element of `B` has a unique rank-two form

```text
C=E+O*Y,
E,O in A.                                           (C30.1)
```

The arithmetic is closed in this form:

```text
(E,O)+(E',O')=(E+E',O+O'),

(E,O)(E',O')
=(EE'+OO'F, EO'+OE'),                              (C30.2)

(E,O)^(-1)
=(E,-O)/(E^2-O^2F)                                (C30.3)
```

whenever the public norm in the denominator is a unit.

Therefore every regular rational circuit whose public leaves lie in `A` and
whose only branch-sensitive input is `Y` compiles exactly to `(E,O)`.

This is not a bounded-degree statement. It covers arbitrary finite rational
circuits, repeated squaring, nested inversions, and large implicit algebraic
degree, provided the expression remains in the same quadratic branch algebra.

## 3. Exact branch-separation dichotomy

Under the branch flip,

```text
C(Y)=E+O*Y,
C(-Y)=E-O*Y.
```

Hence

```text
boxed:
C(Y)-C(-Y)=2 O Y.                                  (C30.4)
```

Because `2` and `Y` are units componentwise, two cases are exhaustive.

### Case A: `O` is not a unit

In a product of fields, `O` is not a unit exactly when one component `O_i`
vanishes. On that component,

```text
C_i(Y_i)=C_i(-Y_i).
```

Thus no decoder receiving only `C` and public branch-even data can recover the
branch on every required component.

A patch for each vanishing component is orientation advice and is charged. A
candidate that excludes those points is not an all-point parity evaluator.

### Case B: `O` is a unit

Then

```text
boxed:
Y=O^(-1)(C-E).                                     (C30.5)
```

So the certificate and the original branch are mutually reducible by public
rank-two arithmetic. If `E`, `O`, and `O^(-1)` are available within the claimed
cost, the reduction has constant online overhead.

Therefore an everywhere branch-separating local rational certificate does not
remove the oriented-root problem. It changes coordinates on the same branch
torsor.

## 4. Relation to the C23 sign-blind theorem

C23 proved that rational circuits over branch-even leaves cannot manufacture a
branch-sensitive value. C30 supplies the complementary statement once one
branch-sensitive leaf is present:

```text
no branch-sensitive leaf:
  every rational output is branch-even;

one quadratic branch-sensitive leaf:
  every rational output is E+O*Y;

O nonunit:
  branch collision somewhere;

O unit:
  exact recovery of Y.
```

Together, C23 and C30 exhaust local rational postprocessing as a source of new
orientation. The remaining problem is not how to re-encode a known branch. It
is how to generate the first public branch-sensitive seed.

## 5. Fractional-linear certificates

A common proposed local transform is

```text
C=(a+bY)/(c+dY).
```

Rationalizing the denominator gives

```text
(a+bY)(c-dY)
=(ac-bdF)+(bc-ad)Y,                               (C30.6)

(c+dY)(c-dY)=c^2-d^2F.                            (C30.7)
```

Thus

```text
E=(ac-bdF)/(c^2-d^2F),
O=(bc-ad)/(c^2-d^2F).                             (C30.8)
```

If the denominator norm and projective determinant `bc-ad` are units, `O` is a
unit and the transform is branch-equivalent to `Y`. If the determinant
vanishes on a component, the two branches collide there.

This includes Cayley transforms, local resolvents, one-point cross-ratios, and
many proposed residue normalizations.

## 6. Kernel derivative is a unit gauge

Let

```text
A_H=F_p[X]/(K_H(X)).
```

The half-kernel polynomial `K_H` is squarefree, so

```text
gcd(K_H,K_H')=1.
```

Therefore the residue class of `K_H'` is a unit in `A_H`.

For the oriented root `Y_G`, define

```text
Z_G=K_H' Y_G.                                     (C30.9)
```

Then

```text
Z_G^2=(K_H')^2 F,
Y_G=(K_H')^(-1) Z_G.                              (C30.10)
```

The two square-root fibers are carried bijectively into each other. The branch
law is unchanged:

```text
Y_G -> -Y_G
implies
Z_G -> -Z_G.
```

Consequently a local formula involving `K_H'Y_G`, `Y_G/K_H'`, a discriminant
unit, or another public invertible kernel jet is not a new oriented evaluator.
It is a public gauge transformation of the same evaluator.

If the jet factor is not a unit, it loses the branch on its zero components and
cannot satisfy the all-point gate without additional patches.

## 7. Frozen local kernel-derivative character screen

The exact screen considers the four normalized signs

```text
chi(y(Q)/y(G)),
chi(K_H'(x(Q))/K_H'(x(G))),
chi(K_H'(beta*x(Q))/K_H'(beta*x(G))),
chi(K_H'(beta^2*x(Q))/K_H'(beta^2*x(G))).
```

Every one of their `2^4=16` products is tested against normalized parity on
all five frozen curves, every marked generator, and every nonzero scalar.

The result is

```text
marked generators:          438
marked-query cases:       46,260
products tested:              16
exact survivors:               0
```

This finite screen is not the theorem above and is not generalized beyond the
declared atoms. It records that the most immediate kernel-derivative character
shortcut fails even before the unit-gauge classification is invoked.

## 8. Executable rank-two replay

For each of the 438 marked oriented roots, the replay verifies on every
half-kernel component:

```text
Y_G^2=F,
K_H'(x_i)!=0,
Z_G=K_H'Y_G,
Y_G=(K_H')^(-1)Z_G,
Z_G(Y_i)!=Z_G(-Y_i).
```

It also compiles deterministic rank-two expressions to `(E,O)`, checks their
values on both branches, recovers `Y` whenever `O` is a unit, and inserts
deliberately singular odd coefficients to verify exact component collisions.

Frozen totals include

```text
curves:                          5
marked generators:            438
kernel-gauge components:    23,130
local character cases:      46,260
errors:                           0
```

The JSON replay is generated deterministically in CI, checked against exact
structural totals, and uploaded as a workflow artifact.

## 9. What C30 closes

Closed in the declared scope:

```text
all everywhere-regular rational one-point postprocessings of one quadratic branch,
all public unit gauges of the oriented root,
K_H' multiplication or division as a separate mechanism,
fractional-linear transforms with public coefficients,
certificates whose odd coefficient vanishes at a required component,
the declared four-atom kernel-derivative character grammar on the frozen corpus.
```

The algebraic theorem is independent of expanded degree or circuit depth.
It is a semantic equivalence theorem, not a computational lower bound for
generating the first branch-sensitive input.

## 10. What remains open

C30 does not close:

```text
a nonlocal algorithm that generates orientation without receiving Y_G,
target-dependent modular composition over many public points,
transposed product-tree evaluation of an oriented divisor,
analytic continuation with an independently public path normalization,
an algebraic extension whose branch is selected by new public structure,
unrestricted arithmetic circuits.
```

A future proposal cannot claim progress merely by returning a new symbol `C`
with a local rational relation to `Y_G`. It must identify the operation that
creates the nonzero odd coefficient without already receiving equivalent
branch information.

## 11. Successor

The successor is

```text
NONLOCAL-ORIENTED-SEED-GENERATION-081.
```

Its fixed question is:

> Can public `(E,G,Q)` generate the first branch-sensitive value through a
> nonlocal product, modular-composition, transposed evaluation, or continuation
> operation whose complete construction and online cost is
> `O(n^(1/2-epsilon))`, without a dense oriented divisor, numeric scalar,
> branch table, full dual character, or pre-existing quadratic branch seed?

Required final flags:

```text
quadratic_branch_normal_form_compiler_built=true
branch_even_rational_circuit_creates_orientation=false
everywhere_branch_separating_local_certificate_is_unit_equivalent=true
kernel_derivative_is_unit_gauge=true
local_kernel_derivative_character_candidate_found=false
public_oriented_seed_found=false
target_dependent_nonlocal_compiler_found=false
exact_parity_extraction_found=false
complete_cost_gate_passed=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```

The result is not an unrestricted parity or ECDLP lower bound.
