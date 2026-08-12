# GLV-NORMALIZATION-RIGIDITY-008

Date: 2026-08-11

Status: **isolated theorem-first scoped no-go package**.
No external point, key, wallet, or production discrete-log instance is
accepted. The package changes no canonical Research Engine state and makes no
unconditional ECDLP-complexity claim.

## 1. Decision

Within the homogeneous quadratic-normalization algebraic category `C_quad`
defined below, a section with an odd residual EDS-residue factor **cannot** have
a GLV carry multiplier different from the perfectly periodic point-function
multiplier.

Equivalently, in this category there is no public section `A` whose C3 orbit
norm isolates

```text
R3(Q)=rho(Q)rho(phi Q)rho(phi^2 Q)
```

without the canonical carry factor.

This is a scoped theorem. It is not a universal impossibility statement about
arbitrary mixed-weight rational circuits, global analytic theta branches,
p-adic continuation, or algorithms outside the category.

## 2. Exact scope contract

An admitted unary section `A` has a public transformation law with two pieces
of binary bookkeeping:

```text
A([k]G)
  = public_A(k) * s^q_A(k) * rho_G([k]G)^epsilon_A,

q_A(k)=a_A*k^2+b_A*k+c_A,
epsilon_A in {0,1}.
```

Here `s` is the fixed quadratic character of the chosen EDS normalization,
`rho_G` is the residual EDS character, and `public_A(k)` is evaluable from the
public point and fixed parameters.

The category invariant is

```text
epsilon_A = a_A+b_A                 (mod 2).       (I)
```

Thus `epsilon_A=1` means that, after all multiplication-law and normalization
cancellations, one genuinely nonpublic EDS character remains. It is not merely
a count of raw division-polynomial factors: for example an even-index pullback
may contain one written EDS term while its hidden base-residue exponent is even
and therefore public.

`C_quad` is the smallest class containing the perfectly periodic point section
and ordinary homogeneous division/net-polynomial sections, together with
public weight-zero rational factors, and closed under:

1. tensor products and duals;
2. fixed integral-index pullbacks and fixed public translations;
3. GLV, Frobenius, and fixed bounded-isogeny transports whose action on the
   chosen subgroup is public;
4. finite invariant jets;
5. homogeneous sums of sections sharing one normalization law;
6. fixed-rank elliptic-net constructions;
7. products over the order-three GLV orbit.

The generators satisfy (I), and every closure operation preserves it:

- tensor/dual add or negate both binary weights;
- for `k -> r+t*k`, the hidden residue exponent is multiplied by `t^2`, while
  the quadratic coefficient changes by the same parity because `t^2=t mod 2`;
- invariant jets leave the index-dependent normalization scalar unchanged;
- public weight-zero factors contribute zero to both sides;
- fixed-rank net pullbacks have exact even source coefficients, proved below;
- homogeneous sums are admitted only within one common linearization class.

### Outside the theorem

The following are not in `C_quad`:

- sums of different normalization weights supplied with a new public
  trivialization;
- interpolation tables growing with subgroup order;
- arbitrary rational circuits not derived from the stated operations;
- global theta/sigma monodromy with a new branch choice;
- p-adic analytic continuation from the formal group to all prime-to-`p`
  torsion points.

A positive construction must leave at least one of these scope assumptions.

## 3. C3 parity theorem

Let `k0,k1,k2` be the canonical scalar representatives of one GLV orbit in an
odd-order subgroup:

```text
k0+k1+k2=gamma*n,
gamma in {1,2}.
```

For

```text
q(k)=a*k^2+b*k+c,
```

one has

```text
q(k0)+q(k1)+q(k2)
  = (a+b)*gamma+c                 (mod 2).       (R)
```

Indeed,

```text
ki^2=ki mod 2,
n=1 mod 2,
3*c=c mod 2.
```

Combining (R) with the category invariant (I):

```text
epsilon_A=1
  -> C3 normalization contains gamma up to a fixed sign;

epsilon_A=0
  -> C3 normalization is carry-free, but no odd residual EDS factor remains.
```

Therefore the forbidden combination

```text
odd residual EDS weight + no GLV carry
```

cannot occur inside `C_quad`.

## 4. Why the closure operations do not escape

### Fixed affine pullbacks

The quadratic weight changes by a square of the public slope. Since

```text
t^2=t mod 2,
```

an odd-slope pullback preserves the same carry class, while an even-slope
pullback removes both carry and odd residual EDS dependence.

### Fixed-rank joint elliptic nets

Increasing net rank does not create a missing binary phase. In the
integral-matrix net transformation law, the coefficient attached to one source
point with net-index coordinate `v`, where `r` is the sum of the other
coordinates, is

```text
v + (v^2-v*r) + v*r
  = v*(v+1),
```

which is always even. The three terms are respectively the conversion of the
integer-index EDS term to a public point label, the unary source-point exponent,
and all pair-source exponents involving that point.

The tempting rank-three term `Psi_(1,1,1)` on

```text
(Q,phi Q,phi^2 Q)
```

also degenerates structurally. Its explicit numerator is

```text
y0*(x1-x2)+y1*(x2-x0)+y2*(x0-x1).
```

All three GLV-orbit points on `y^2=x^3+7` share the same `y`, so the numerator
vanishes identically. The corresponding first normal derivative reduces to a
fixed unit after sigma-factor cancellation and supplies no new binary phase.

### Finite jets

Differentiating a homogeneous unary section does not differentiate its
index-dependent normalization scalar. Its finite invariant jets retain the same
quadratic weight. The rank-three zero-sum case is covered by the cancellation
above.

### GLV linearization

A phase produced solely by an order-three GLV linearization satisfies

```text
z^3=1.
```

But

```text
z=(z^2)^2.
```

Every cube root of unity is therefore already a square, so quadratic character
cannot read a new binary GLV eigenphase.

### Fixed bounded isogenies

On the chosen prime-order subgroup a fixed isogeny/root cover is a public
transport, possibly followed by a known scalar map. Its binary effect is
therefore governed by the affine-pullback theorem. The previously constructed
Eisenstein cubic root was explicitly identified with a public inverse
3-isogeny and supplied no independent phase.

### Homogeneous sums

Sections can be added canonically only inside the same linearized line bundle,
where they share one quadratic normalization. A sum of different weights
requires a new trivialization and is outside `C_quad` rather than a
counterexample within it.

## 5. Consequence for the odd aggregate

Recall

```text
R3(Q)=rho(Q)rho(phi Q)rho(phi^2 Q),
C3(Q)=g(Q)R3(Q),
g(Q)=(-1)^gamma(Q).
```

`R3` has odd residual EDS weight. Hence every homogeneous public section in
`C_quad` whose raw law contains `R3` has orbit character

```text
constant * g(Q) * R3(Q),
```

not

```text
constant * R3(Q).
```

This unifies the exact collapses already found for the perfectly periodic point
function, the first order-`n` torsion jet, `psi_(n+1)`, `psi_(n-1)`, fixed-rank
net pullbacks, and finite tensor/dual products.

## 6. Weight-zero carry escape screen

A public weight-zero function could still decode `g(Q)` directly without
changing a line-bundle multiplier. The simplest overlooked candidate was

```text
chi(y(Q)).
```

It has the right symmetries on the frozen fields:

```text
chi(y(phi Q))=chi(y(Q)),
chi(y(-Q))=-chi(y(Q)).
```

The bounded screen tested

```text
chi(y(Q)),
chi(y(Q)*(x(Q)^3+a)),              a in F_p,
```

and nondegenerate products of two distinct invariant linear factors.

Protocol:

```text
15 frozen j=0 prime-order toy subgroups,
orders 19 through 4021,
200 matched random anti-Kummer/C3-invariant controls per case,
1,072,350 exact quadratic-orbit parity checks.
```

Results:

```text
exact single decoders:                         2
exact nondegenerate degree-two decoders:       2
exact decoder at order >=271:                  0
cases strictly above matched 95% null:         0
```

Exact matches occur only at small orders `19`, `31`, and `67` and are classified
as finite resonances. On the two largest groups:

| order | best observed | matched null median | matched null 95% |
|---:|---:|---:|---:|
| 3469 | 0.584775 | 0.577855 | 0.588235 |
| 4021 | 0.579104 | 0.571642 | 0.582090 |

Neither crosses the strict matched 95-percent gate.

Artifacts:

- `experiments/parity_lift_000/glv_normalization_rigidity_screen.py`;
- `experiments/parity_lift_000/glv_normalization_rigidity_results.json`.

## 7. Formalization boundary

`Ecdlp/Proved/GlvNormalizationRigidity.lean` kernel-checks the arithmetic core:

```text
square_sub_self_even
glvOrbitSquareCarryParity
glvOrbitLinearCarryParity
quadraticNormalizationOrbitParity
oddCarryWeight_forces_basicCarry
evenCarryWeight_killsCarry
affinePullbackWeightParity
netPullbackPointScaleCoefficient
netPullbackPointScaleCoefficient_even
rankThreeCommonYNumerator_zero
cubeRootLinearization_isSquare
```

The file contains no `sorry` and no custom axiom.

Lean formalizes the integer parity and fixed-rank cancellation statements. It
does not formalize the cited papers, the inductive definition of `C_quad`, line
bundles, theta groups, or jet bundles. The geometric identification and closure
argument are the explicit scope contract of this research note, supported by
the sigma, transformation, scale-equivalence, and normalization theorems in the
source literature.

## 8. Exact answer

```text
section with a different carry multiplier in C_quad:   impossible by scope theorem
order-three GLV eigenphase escape:                     impossible
fixed affine/tensor/dual/unary-jet escape:              impossible
fixed-rank joint-net escape:                           impossible
simple weight-zero carry decoder:                      no scaling signal
mixed-weight/global analytic category:                 open
public R3 or carry decoder:                            absent
unconditional sub-square-root ECDLP algorithm:         absent
```

Thus the requested alternative is resolved for the current homogeneous
algebraic category: **no such section exists there.**

## 9. Constructive frontier

Further enumeration inside `C_quad` is low-value. The next package should test
only constructions that explicitly escape the theorem:

1. a mixed-weight rational construction with a canonical public
   trivialization;
2. global theta/sigma monodromy not equivalent to quadratic net normalization;
3. p-adic sigma continuation with a public branch and precision theorem;
4. a nonlocal order-dependent weight-zero carry decoder.

Provisional successor:

```text
GLOBAL-MONODROMY-SECTION-009.
```

Its admission test is strict: state exactly which `C_quad` rule is escaped and
why evaluation remains below the square-root baseline.

## Primary anchors

- Katherine E. Stange, *Elliptic Nets and Elliptic Curves*: sigma definition of
  net polynomials, integral-matrix transformation, scale equivalence by
  quadratic forms, unique normalization, and the explicit rank-three net
  polynomial.
- Kristin Lauter and Katherine E. Stange, *The Elliptic Curve Discrete
  Logarithm Problem and Equivalent Hard Problems for Elliptic Divisibility
  Sequences*: perfectly periodic point function, EDS-residue problem, and
  parity-to-ECDLP reduction.
- Repository packages `RELATIVE-RESIDUE-GAUGE-001`,
  `ABSOLUTE-EDS-SECTION-003`, `NONLOCAL-ODD-ANCHOR-004`, and
  `GLV-CARRY-SEPARATION-005`.
