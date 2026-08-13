# Square-class circuit frontier

Date: 2026-08-12

Status: **structural reduction after linear-state, rational-degree, one-addition, and structured nested two-addition barriers; no general arithmetic-circuit lower bound and no decoder**.

## 1. Exact target

The target remains

```text
g_G(Q)=g_G(G)*sign(U_G(Q)),
```

or any publicly equivalent exact output `R3_G(Q)` or `h_G(x(Q)^3)`.

A direct quadratic-character coordinate decoder has the form

```text
chi_p(F_G(Q))=g_G(Q).
```

The rational-character degree theorem forces square-root-scale degree, but repeated squaring prevents degree alone from becoming a circuit-size lower bound.

## 2. Square-class innovations

In `K=F_p(E)` modulo squares,

```text
[F*G]=[F]+[G],
[1/F]=[F],
[F^2]=0,
[F^(odd)]=[F],
[F^p]=[F].
```

An addition contributes one new class:

```text
[F+G]=[F]+[1+G/F].
```

Package 039 proves that one such innovation can already have conductor above `sqrt(n)` after a short squaring chain. Thus degree, conductor, genus, odd support, and addition count do not separately lower-bound circuit size strongly enough.

## 3. Exact coordinate gates completed

### One addition

Every one-addition monomial square class has form

```text
kappa*x^u*y^v*(1+c*x^a*y^b).
```

Complete medium exhaustions over all exponent pairs and all constants produced zero exact carry decoders.

### Nested two additions

The quotient class

```text
H=1+c1*z^a,
F=kappa*z^u*H^epsilon*(1+c2*z^b*H^t),
z=x^3,
```

and a direct full-point character-symmetry branch were searched exactly in predeclared structured profiles.

```text
nominal formula evaluations: 156,114,321,336
exact decoders:              0
```

This is bounded structured evidence, not a universal theorem.

## 4. Same-feature GLV symmetrization collapses

For `M(phi Q)=beta^a M(Q)` and `beta^2+beta+1=0`, the orbit product

```text
product_(j=0..2)(1+c*beta^(a*j)M)
```

is either `(1+cM)^3` or `1+c^3M^3`. Modulo squares it returns to the one-addition gate. Therefore a naive third addition obtained by multiplying the three GLV translates is not a new class.

## 5. Current nonlinear frontier

The next admitted coordinate object must couple at least two nonproportional CM weight components. The first class is a generator-sensitive mixed-weight determinant, resultant, or theta/net resolvent whose anti-invariant output survives public-factor reduction.

Immediate rejection tests:

1. pure monomial orbit columns factor into public monomials;
2. same-feature orbit products collapse to one addition;
3. character-balanced expressions cancel the generator character;
4. fitted coefficients or selected dual-orbit data are hidden advice;
5. an empirical correlation without an exact identity is not admissible.

## 6. Current answer

```text
Low-degree rational-character decoder                     excluded
Explicit translation-linear state                         excluded
Complete medium one-addition monomial class               zero decoders
Structured nested two-addition coordinate profiles        zero decoders
Same-feature GLV orbit product                             collapses
Mixed-weight GLV resolvent                                 open
Canonical p-adic/analytic orientation circuit             open
Public carry or hard-R3 decoder                            absent
Classical sub-square-root ECDLP algorithm                  absent
```

The surviving coordinate problem is no longer “add another nonlinear gate.” It is whether mixing distinct CM weights can create a genuinely generator-oriented square class rather than another public norm or balanced invariant.
