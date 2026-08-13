# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C9: primal orientation and the finite-etale branch boundary

Date: 2026-08-13

Status: **an exact nonlinear primal-coordinate normal form has been found, together with three scoped obstructions. Canonical parity is an oriented square-root branch over the Kummer kernel algebra. The identity is exact, but its dense representation has linear size and no sub-square-root public branch evaluator is known.**

## 1. Strategic gate

This track no longer promotes a mechanism merely because a fast implementation would solve parity. A surviving mechanism must satisfy all three conditions:

```text
1. it actually returns (-1)^k for Q=[k]G,
2. its construction is not already an encoding of k or a renamed DLP,
3. it names a concrete resource absent from a generic cyclic group that can
   plausibly reduce the exponent below 1/2.
```

A compact equation without a compact branch-selection law does not pass condition 3.

Throughout, let

```text
E: y^2=F(x)=x^3+a*x+b
H=<G>
|H|=n
n odd and prime
Q=[k]G, 1<=k<n
sigma_G(Q)=(-1)^k.
```

The C6 first variation is

```text
V(E,G,Q)=-n^(-1)[t]det(I+T_G+tT_Q)=sigma_G(Q).
```

The purpose of C9 is to express this same observable in genuinely nonlinear
primal coordinates and to identify exactly where compact evaluation remains
blocked.

## 2. Anti-Kummer theorem

For nonzero `Q=[k]G`,

```text
-Q=[n-k]G.
```

Because `n` is odd,

```text
sigma_G(-Q)=(-1)^(n-k)=-(-1)^k=-sigma_G(Q).       (K1)
```

But the Kummer coordinate satisfies

```text
x(-Q)=x(Q).                                       (K2)
```

Therefore no function that factors only through `x(Q)`, or more generally
through the unoriented quotient `E/{+1,-1}`, can equal canonical parity on
`H\{O}`.

```text
boxed:
canonical parity does not descend to the Kummer quotient.              (K3)
```

This closes x-only, unsigned-kernel, and inversion-invariant formulas. It does
not close an oriented formula that uses `y(Q)` or another equivalent lift.

## 3. Exact oriented interpolation normal form

Put

```text
m=(n-1)/2
P_i=[i]G=(x_i,y_i), 1<=i<=m.
```

The `x_i` are pairwise distinct. Also `y_i` is nonzero, because a nonzero
2-torsion point cannot lie in a subgroup of odd order.

There is a unique polynomial

```text
r_G(X) in F_p[X], deg(r_G)<m
```

satisfying

```text
r_G(x_i)=(-1)^i/y_i, 1<=i<=m.                    (N1)
```

For `P_i` this gives

```text
y(P_i)r_G(x(P_i))=(-1)^i.
```

For the other point in the Kummer pair,

```text
-P_i=[n-i]G,
y(-P_i)=-y_i,
(-1)^(n-i)=-(-1)^i.
```

Hence the same identity holds on every nonzero point of `H`:

```text
boxed:
sigma_G(Q)=y(Q)r_G(x(Q)).                         (N2)
```

Combining with C6 gives the exact nonlinear primal first variation

```text
boxed:
V(E,G,Q)=y(Q)r_G(x(Q)).                           (N3)
```

This is a genuine primal-coordinate identity. It is not yet a compact
evaluator: a dense representation of `r_G` has `m=Theta(n)` coefficients.

## 4. Finite-etale square-root branch

Define the Kummer kernel polynomial

```text
h_H(X)=product_(i=1)^m (X-x_i).                  (E1)
```

At each root `x_i`,

```text
F(x_i)r_G(x_i)^2
=y_i^2*((-1)^i/y_i)^2
=1.
```

Therefore

```text
boxed:
F(X)r_G(X)^2 = 1 mod h_H(X).                     (E2)
```

Equivalently, with

```text
Y_G(X)=F(X)r_G(X) mod h_H(X),
```

one has

```text
Y_G(X)^2=F(X) mod h_H(X),
sigma_G(Q)=Y_G(x(Q))/y(Q).                       (E3)
```

After base change to a splitting field, the finite etale algebra is

```text
A_H=K[X]/(h_H) isomorphic to product_(i=1)^m K.
```

Since `F(x_i)` is nonzero, equation `(E2)` has exactly two roots in each
component and hence exactly

```text
2^m
```

roots in `A_H`. The parity branch is the root whose component signs are fixed
by `(N1)`.

This branch count is a boundary, not by itself a lower bound. For a fixed
kernel and varying marked generator, only a structured subset of these roots
is relevant. The point `G` is already a compact description of the selected
branch. What remains open is a fast public evaluation law extracting that
branch at `x(Q)` without walking the orbit or materializing `A_H`.

## 5. Unsigned elliptic products erase parity exactly

Define

```text
A_even(X)=product_(1<=k<n, k even) (X-x([k]G)),
A_odd(X) =product_(1<=k<n, k odd ) (X-x([k]G)).
```

The involution

```text
k -> n-k
```

swaps even and odd indices because `n` is odd, while preserving the
x-coordinate:

```text
x([n-k]G)=x([k]G).
```

Each Kummer pair contributes once to each product. Thus

```text
boxed:
A_even(X)=A_odd(X)=h_H(X).                       (P1)
```

Consequently every ordinary unsigned kernel product loses canonical parity
before any norm, resultant, logarithmic derivative, or residue is applied.
A useful Velu-type mechanism must contain an oriented quantity that does not
collapse under `(P1)`.

## 6. Bounded-pole-degree rational obstruction

Let `f` be a nonconstant rational function on `E`, defined at all points of
`H\{O}`, and suppose

```text
f([k]G)=(-1)^k for 1<=k<n.                       (R1)
```

Let

```text
D=deg((f)_infinity)
```

be the degree of the pole divisor of `f`.

The rational function `f^2-1` has at least `n-1` distinct zeros. It is not the
zero function: in the function field, which is an integral domain of
characteristic different from 2, `f^2=1` would imply `f=1` or `f=-1`, contrary
to nonconstancy and the two values in `(R1)`.

The pole divisor of `f^2-1` has degree at most `2D`. Equality of zero and pole
divisor degrees gives

```text
n-1 <= 2D.
```

Therefore

```text
boxed:
D >= (n-1)/2.                                    (R2)
```

This rejects every constant-pole-degree or `o(n)` pole-degree rational
coordinate formula for exact parity. It does not prove a circuit lower bound:
a high-degree rational function can sometimes have a logarithmic-size
arithmetic circuit. A positive circuit proposal must expose that circuit and
its complete application cost.

## 7. No global anti-translation eigenfunction

Suppose a function `f` on the odd cycle satisfied

```text
tau_G f=-f
```

everywhere. Since `tau_G^n=1`,

```text
f=tau_G^n f=(-1)^n f=-f.
```

In characteristic different from 2 this forces `f=0`.

```text
boxed:
there is no nonzero global -1 translation eigenfunction on an odd cycle.  (T1)
```

The defect in the established equation

```text
(I+tau_G)s_G=2*delta
```

is therefore essential. A theta or eigenfunction proposal must explain how
its divisor, defect, line-bundle multiplier, or cover carries this
nonperiodicity. A globally periodic scalar eigenfunction cannot do so.

## 8. Translation recurrence does not yet compress

From `(N2)`, away from the identity defect,

```text
y(P+G)r_G(x(P+G))=-y(P)r_G(x(P)).
```

Hence

```text
r_G(x(P+G))
=-y(P)/y(P+G) * r_G(x(P)).                       (T2)
```

This is the original public local cocycle in primal form. Iterating `(T2)`
computes the branch, but takes the orbit length unless a new nonlocal jump law
is found. The normal form therefore explains the bottleneck but does not
remove it.

## 9. Cost ledger

The direct construction has:

```text
subgroup enumeration                              Theta(n) points
h_H dense representation                         Theta(n) coefficients
r_G dense interpolation                          Theta(n) coefficients
generic modular square-root state                 degree Theta(n)
online evaluation after dense preprocessing       O(n), or quasi-linear with
                                                  fast polynomial methods
complete charged target                           O(n^(1/2-epsilon))
```

A short equation such as `(E2)` does not make the representation short. It
leaves both `h_H` and the distinguished branch to be generated.

Known square-root Velu and baby-step/giant-step kernel methods may reach a
square-root boundary for related isogeny products. A `tilde O(sqrt(n))`
boundary is useful evidence but does not satisfy the required exponent
improvement.

## 10. Mechanism ranking under the structural-resource gate

### Highest priority: oriented high-degree primal circuit

Required missing resource:

```text
a public logarithmic or fixed-depth recurrence that evaluates the
distinguished branch at x(Q) without constructing h_H or r_G densely.
```

Examples worth testing are a structured polynomial-Pell recurrence, a
division-polynomial addition law that does not use the hidden index, or a
transposed branch evaluation whose state remains below `sqrt(n)`.

This direction survives because high algebraic degree alone does not imply a
large circuit. It receives no credit until an actual hidden-index-free circuit
is written.

### Medium priority: nonlinear finite-etale residue or oriented isogeny

Required missing resource:

```text
a constant-number residue, norm, intersection, or first-variation operation
that retains orientation and can be applied from a compressed kernel
description below sqrt(n).
```

Unsigned kernel polynomials fail by `(P1)`. A degree-`m` quotient algebra
renamed as one residue also fails the cost gate.

### Conditional priority: theta or p-adic lift

Required missing resource:

```text
a bounded-level auxiliary cover or lift with a provable orientation phase and
sub-square-root extension, precision, and descent cost.
```

Direct Frobenius on `H subset E(F_p)` is the identity and is generator-blind.
A useful Frobenius phase must live on an auxiliary object and must survive
descent to `(N2)`.

### Low priority: CM, Kummer, GLV, nonlocal EDS

Kummer alone fails `(K3)`. Fixed-degree CM and GLV endomorphisms currently
supply constant-factor symmetries but no identified exponent-changing state
reduction. Nonlocal EDS remains equivalent to evaluating `(T2)` unless a
public jump recurrence is found.

### Parked

```text
pairing transfer,
linear translation representations,
full character bases,
generic determinants,
explicit z^k,
ordinary unsigned Velu products.
```

These have already failed a precise representation or cost gate.

## 11. New central problem

The next task is not to find another identity. The identity is now explicit:

```text
V(E,G,Q)=y(Q)r_G(x(Q)).
```

The actual task is:

```text
ORIENTED-ETALE-BRANCH-EVALUATION-059

Given public E, G, Q and n, evaluate at x(Q) the distinguished root r_G of

    F*r^2=1 mod h_H

in O(n^(1/2-epsilon)) complete charged cost, without:

1. constructing h_H or r_G densely,
2. enumerating Theta(n) subgroup points,
3. encoding the hidden scalar in an exponent, path, basis, or branch table,
4. using a linear representation of charged dimension Theta(n),
5. leaving a DLP in an auxiliary group.
```

Every candidate must first identify the mathematical resource absent from a
generic cyclic group and explain why that resource can change the exponent.
Without that explanation, the branch is parked before detailed development.

## 12. Frozen verification record

The committed frozen verification data are stored at:

```text
experiments/parity_lift_000/uorc056_primal_orientation_branch_result.json
```

They were generated by a locally executed deterministic replay restricted to
six frozen toy curves with prime subgroup orders

```text
19, 31, 67, 271, 397, 433.
```

The committed result records:

```text
all 1212 nonzero-point checks,
all 1212 anti-Kummer checks,
1206 local translation-recurrence checks,
129 generator replacements,
11070 generator-replacement point checks,
18 alternate square-root branch checks,
zero denominator exceptions,
all six cases passed.
```

The connector accepted the mathematical memo and complete frozen JSON result.
It did not accept the executable replay source, so this branch does not claim
that source as a committed artifact. The frozen data are finite evidence for
the exact identities; the general statements above rest on the algebraic
proofs in this memo rather than on the finite screen alone.

## 13. Result flags

```text
primal_orientation_obstruction_found=true
bounded_pole_degree_rational_evaluator_blocked=true
global_anti_translation_eigenfunction_blocked=true
oriented_interpolation_normal_form_found=true
finite_etale_square_root_branch_identified=true
compact_sub_sqrt_evaluation_found=false
evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```
