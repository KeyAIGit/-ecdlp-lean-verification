# GLV-NORMALIZATION-RIGIDITY-008

Date: 2026-08-11

Status: **isolated theorem-first scoped no-go package**.
No external point, key, wallet, or production discrete-log instance is
accepted. The package changes no canonical Research Engine state and makes no
unconditional ECDLP-complexity claim.

## 1. Decision

Within the homogeneous algebraic net/theta category defined below, a section
with an odd number of hidden EDS-residue factors **cannot** have a GLV carry
multiplier different from the perfectly periodic point-function multiplier.

Equivalently, in this category there is no public section `A` whose C3 orbit
norm isolates

```text
R3(Q)=rho(Q)rho(phi Q)rho(phi^2 Q)
```

without the canonical carry factor.

This is a scoped theorem, not a universal impossibility statement about
arbitrary rational circuits, global analytic theta branches, p-adic
continuations, or algorithms outside the category.

## 2. The current algebraic category

Let `C_quad` be the smallest class of scalar-valued homogeneous sections
containing the ordinary division/net-polynomial sections and the perfectly
periodic point section, and closed under:

1. tensor products and duals;
2. fixed integral-index pullbacks and fixed public translations;
3. GLV, Frobenius, and fixed bounded-isogeny pullbacks;
4. multiplication by public weight-zero rational functions;
5. finite jets taken with an invariant local parameter or invariant
   differential;
6. homogeneous linear combinations of sections with the same normalization
   law;
7. the product over the order-three GLV orbit.

Every object in `C_quad` carries a quadratic normalization exponent

```text
q_A(k)=a_A*k^2+b_A*k+c_A.
```

The coefficients may depend on the public curve, generator, chosen section,
and fixed pullback, but not on the hidden scalar representative `k`.

This quadratic law is not an extra heuristic assumption. It is the algebraic
content of:

- scale equivalence of elliptic nets by quadratic forms;
- the sigma-function definition of net polynomials;
- the integral-matrix transformation formula for net polynomials;
- tensor/dual closure of the corresponding line bundles.

Finite jets remain in the same normalization class because the normalization
scalar is independent of the local coordinate. A GLV derivative may add a
cube-root eigenvalue, but that phase is binary-trivial, as shown below.

### Excluded from `C_quad`

The following are deliberately not included:

- sums of terms with different quadratic weights after an ad hoc
  trivialization;
- interpolation tables whose size grows with the subgroup order;
- arbitrary rational functions whose evaluation circuit is not derived from
  the stated operations;
- global theta/sigma monodromy with a new branch choice;
- p-adic analytic continuation from the formal group to all prime-to-`p`
  torsion points.

These exclusions are the exact boundary of the theorem.

## 3. Exact parity theorem

Let the canonical scalar representatives of a GLV orbit be

```text
k0,k1,k2 in {1,...,n-1},
```

with odd subgroup order `n`, and let

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

The proof is elementary but decisive:

```text
ki^2 = ki                         (mod 2),
k0+k1+k2 = gamma*n = gamma        (mod 2),
3*c = c                           (mod 2).
```

Therefore the C3 carry coefficient is exactly

```text
epsilon_A = a_A+b_A               (mod 2).
```

We call `epsilon_A` the binary normalization weight.

### Odd weight

If

```text
epsilon_A=1,
```

then (R) gives

```text
sum_i q_A(ki)=gamma+constant       (mod 2).
```

Thus every odd-gauge section has the same canonical GLV carry multiplier as
the perfectly periodic point function, up to a fixed public global sign.

### Even weight

If

```text
epsilon_A=0,
```

then its orbit normalization is carry-free, but its EDS gauge weight is even.
It cannot contain an odd number of nonpublic EDS-residue factors.

Hence the forbidden combination is impossible inside `C_quad`:

```text
odd hidden EDS gauge weight
+
no GLV carry multiplier.
```

## 4. Closure under the allowed operations

### Tensor products and duals

Quadratic exponents add under tensor product and negate under duality. Their
binary weights therefore add modulo two. The rigidity relation is preserved.

### Fixed affine pullback

For a fixed index map

```text
k -> r+s*k,
```

the quadratic coefficient is multiplied by `s^2`. Since

```text
s^2=s                           (mod 2),
```

the new binary weight is the old weight multiplied by `s mod 2`.

An odd-slope pullback preserves the same carry. An even-slope pullback kills
both the carry and the odd EDS gauge. It cannot switch to a new carry class.

### Finite jets

Differentiating a homogeneous section does not differentiate its
index-dependent normalization scalar. Every finite invariant jet has the same
quadratic weight as the original section.

### GLV linearization

Any scalar produced purely by an order-three GLV linearization satisfies

```text
z^3=1.
```

But then

```text
z=(z^2)^2.
```

Thus every cube root of unity is already a square. A quadratic character cannot
extract a new binary phase from the GLV eigenvalue itself.

### Bounded isogenies

An odd-degree pullback preserves odd weight and hence the same carry. An
even-degree pullback has even binary weight and cannot retain an odd residue
aggregate. The previously studied Eisenstein cubic root cover falls in the
odd-degree case and was explicitly identified with an inverse 3-isogeny.

### Homogeneous sums

Sections may be added canonically only when they belong to the same linearized
line bundle and hence share one quadratic normalization exponent. Their sum
therefore remains in the same carry class.

A sum of different weights requires a new trivialization. That is precisely a
new absolute section and lies outside the category proved rigid here.

## 5. Consequence for the known odd aggregate

Recall

```text
R3(Q)=rho(Q)rho(phi Q)rho(phi^2 Q),
C3(Q)=g(Q)R3(Q),
g(Q)=(-1)^gamma(Q).
```

`R3` has odd EDS gauge weight. Therefore any homogeneous public section in
`C_quad` whose raw law contains `R3` must have orbit character

```text
constant * g(Q) * R3(Q),
```

not

```text
constant * R3(Q).
```

This explains, in one theorem, the exact coincidences already observed for:

```text
perfectly periodic point function,
first order-n torsion jet,
psi_(n+1),
psi_(n-1),
finite products and duals of these sections.
```

They are not unrelated failures. They are instances of one quadratic
normalization law.

## 6. Weight-zero escape check

A logically different possibility is a public weight-zero function that
decodes the carry `g(Q)` directly. Such a function would not contradict the
rigidity theorem; it would solve the missing factor independently.

The simplest overlooked candidate is

```text
chi(y(Q)).
```

It has the correct symmetries:

```text
chi(y(phi Q))=chi(y(Q)),
chi(y(-Q))=-chi(y(Q))
```

for the frozen fields with `chi(-1)=-1`, exactly like `g`.

The bounded boundary screen therefore tested

```text
chi(y(Q)),
chi(y(Q)*(x(Q)^3+a)),             a in F_p,
```

and detected exact products of two invariant linear factors without an
`O(p^2)` enumeration.

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
exact degree-two decoders:                     3
exact decoder at order >=271:                  0
cases strictly above matched 95% null:         0
```

The exact matches occurred only at orders `19`, `31`, and `67`. They are finite
small-order resonances, not scaling evidence.

Largest cases:

| order | best observed | matched null median | matched null 95% |
|---:|---:|---:|---:|
| 3469 | 0.584775 | 0.577855 | 0.588235 |
| 4021 | 0.579104 | 0.571642 | 0.582090 |

Neither crosses the predeclared strict 95-percent gate.

Artifacts:

- `experiments/parity_lift_000/glv_normalization_rigidity_screen.py`;
- `experiments/parity_lift_000/glv_normalization_rigidity_results.json`.

## 7. Formalization

`Ecdlp/Proved/GlvNormalizationRigidity.lean` kernel-checks the arithmetic core:

```text
square_sub_self_even
glvOrbitSquareCarryParity
glvOrbitLinearCarryParity
quadraticNormalizationOrbitParity
oddCarryWeight_forces_basicCarry
evenCarryWeight_killsCarry
affinePullbackWeightParity
cubeRootLinearization_isSquare
```

The theorem file contains no `sorry` and no custom axiom.

The Lean result is deliberately algebraic. The identification of the full
geometric category with quadratic normalization sections is supported by the
net-polynomial sigma and scale-equivalence theorems and is recorded here as the
scope contract. A full formalization of line bundles, linearizations, and jet
bundles is not claimed.

## 8. Exact answer

```text
section with a different carry multiplier found in C_quad:   no
scoped rigidity theorem for C_quad:                          yes
order-three GLV eigenphase can change quadratic character:  no
fixed affine/tensor/dual/finite-jet escape:                   no
simple weight-zero carry decoder:                            no scaling signal
arbitrary mixed-weight/global analytic category:             open
public R3 or carry decoder:                                  absent
unconditional sub-square-root ECDLP algorithm:               absent
```

Thus the requested alternative has been resolved for the current homogeneous
algebraic category: **such a section cannot exist there.**

## 9. New constructive frontier

Further enumeration inside `C_quad` is now low-value. A successful section must
leave at least one theorem assumption. The live possibilities are:

1. a mixed-weight rational construction with a canonical public
   trivialization;
2. a global theta/sigma monodromy section not equivalent to quadratic net
   normalization;
3. a p-adic sigma continuation with a public branch and precision theorem;
4. a weight-zero carry decoder with nonlocal order-dependent structure.

The highest-value successor is provisionally:

```text
GLOBAL-MONODROMY-SECTION-009.
```

Its admission test is strict: it must state exactly which `C_quad` closure rule
it escapes and why evaluation remains below the square-root baseline.

## Primary mathematical anchors

- Katherine E. Stange, *Elliptic Nets and Elliptic Curves*: sigma definition of
  net polynomials, integral-matrix transformation, scale equivalence by
  quadratic forms, and unique normalization.
- Kristin Lauter and Katherine E. Stange, *The Elliptic Curve Discrete
  Logarithm Problem and Equivalent Hard Problems for Elliptic Divisibility
  Sequences*: perfectly periodic point function, EDS-residue problem, and
  parity-to-ECDLP reduction.
- Repository packages `RELATIVE-RESIDUE-GAUGE-001`,
  `ABSOLUTE-EDS-SECTION-003`, `NONLOCAL-ODD-ANCHOR-004`, and
  `GLV-CARRY-SEPARATION-005`.
