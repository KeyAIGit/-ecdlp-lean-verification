# MULTI-CELL-NET-CANCELLATION-048

Date: 2026-08-12

Status: **rank-one Ward multi-cell products admit an exact rank-two determinantal model; the shared-middle two-cell determinant factors, the natural three-cell determinant vanishes, and four-index products satisfy the Grassmann-Pluecker relation. Genuinely rank-two elliptic-net minors and non-Ward branch selectors remain open.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from package 047

Package 047 showed that every determinant consisting of exactly one Ward or elliptic-net recurrence cell factors back into a multiplicative net monomial. In particular, the first normalized rank-two `2 x 2` determinant is not an independent equation for the generator-oriented Kummer square root `Y_G`.

Package 048 asks whether combining several rank-one Ward cells creates a genuinely new additive relation.

## 2. Ward recurrence as a rank-two minor

For a rank-one elliptic divisibility sequence `W`, define

```text
R(j)=W(j)^2,
V(j)=W(j+1)W(j-1),
A(a,b)=W(a+b)W(a-b).
```

Ward's recurrence is exactly

```text
boxed:
A(a,b)=V(a)R(b)-V(b)R(a).                        (M1)
```

Thus every Ward product is a `2 x 2` minor:

```text
A(a,b)=det [
  V(a) R(a)
  V(b) R(b)
].                                                (M2)
```

This exposes the hidden algebraic reason many additive Ward constructions collapse: all columns live in a two-dimensional determinantal geometry.

## 3. Exact two-cell determinant

Fix `m` and two independent shifts `r,s`. Eliminating the common Ward coefficient gives

```text
boxed:
A(m,r)R(s)-A(m,s)R(r)=R(m)A(s,r).                (M3)
```

Equivalently,

```text
W(m+r)W(m-r)W(s)^2
 - W(m+s)W(m-s)W(r)^2
 = W(m)^2W(r+s)W(s-r).                           (M4)
```

The first natural two-cell Pluecker/Wronskian therefore collapses to one multiplicative EDS monomial.

For `s=r+1` and normalized `W(1)=1`,

```text
W(m+r)W(m-r)W(r+1)^2
 - W(m+r+1)W(m-r-1)W(r)^2
 = W(m)^2W(2r+1).                                (M5)
```

So coupling adjacent Ward cells does not create an absolute branch selector.

## 4. Three-cell determinant

For fixed `m`, the column relation

```text
A(m,t)=V(m)R(t)-R(m)V(t)                         (M6)
```

shows that the three columns

```text
A(m,t), R(t), V(t)
```

have rank at most two as `t` varies. Hence for arbitrary `r,s,t`,

```text
boxed:
det [
  A(m,r) R(r) V(r)
  A(m,s) R(s) V(s)
  A(m,t) R(t) V(t)
]=0.                                              (M7)
```

The smallest natural `3 x 3` Casoratian/Wronskian built from these Ward products therefore vanishes identically rather than selecting a new orientation.

## 5. Four-index Pluecker syzygy

Because all `A(a,b)` are `2 x 2` minors of one rank-two array, for arbitrary indices `a,b,c,d` they satisfy

```text
boxed:
A(a,b)A(c,d)
 - A(a,c)A(b,d)
 + A(a,d)A(b,c)=0.                               (M8)
```

This is the Grassmann-Pluecker relation. It is not a numerical coincidence and does not depend on small indices.

Consequently the first multi-cell rank-one Ward grammar is governed by rank-two minor algebra rather than by an independent generator-oriented square-root equation.

## 6. Relation to the target Y_G

Package 046 identified the exact target

```text
Y_G(X)^2 = X^3+7 mod K_H(X),
Y_G(x([k]G))/y([k]G)=(-1)^k.                     (M9)
```

A useful net construction must do more than generate another exact identity: after symbolic reduction it must retain generator-sensitive branch information capable of selecting this particular `Y_G`.

The rank-one Ward minor grammar fails that test:

```text
one cell                    -> multiplicative monomial,
shared-middle two cells     -> multiplicative monomial,
natural three-cell minor    -> zero,
four-index syzygy           -> Pluecker identity.
```

This does not prove that every arbitrary polynomial in EDS terms is useless. It closes the declared determinant/minor mechanism class.

## 7. Public high indices

No bounded-index assumption occurs in `(M1)`-`(M8)`. The indices may be public functions of the subgroup order, such as `n+a`, `2n+b`, or larger addition-chain values.

Periodicity can simplify factors after evaluation, but cannot restore an independent additive equation because the rank-two factorization is symbolic before period reduction.

A basis or index depending on the unknown scalar `k` is not admissible: supplying it would inject the hidden information the construction is intended to recover.

## 8. Frozen exact replay

`multi_cell_net_cancellation.py` evaluates division-polynomial EDS terms on the frozen prime-order `j=0` subgroups

```text
n=19,31,67,271,397,433.
```

It checks exactly:

1. the rank-two minor representation `(M1)`;
2. exhaustive bounded shared-middle two-cell identities `(M3)`;
3. the adjacent specialization `(M5)`;
4. public near-period and beyond-period index patterns;
5. natural `3 x 3` determinant vanishing `(M7)`;
6. four-index Grassmann-Pluecker relations `(M8)`.

All arithmetic is exact in the finite field. There is no floating-point fitting and no unknown target scalar.

## 9. Formalization

`Ecdlp/Proved/MultiCellNetCancellation.lean` kernel-checks:

```text
shared-coefficient two-cell elimination,
two-cell determinant collapse,
three-row rank-two determinant = 0,
four-minor Grassmann-Pluecker relation.
```

The file formalizes the commutative-ring algebra after the Ward-shaped hypotheses are supplied. It does not formalize elliptic curves, division polynomials, the Ward recurrence theorem itself, secp256k1, parity, or ECDLP.

## 10. Answer

```text
Rank-one Ward product geometry                              rank two
Natural two-cell determinant                              factors
Exact two-cell factor                                     W(m)^2 W(r+s)W(s-r)
Natural three-cell 3x3 determinant                        zero
Four-index multi-cell relation                            Grassmann-Pluecker
Do public n-dependent indices evade this?                 no
Does this rank-one Ward minor grammar construct Y_G?      no
Public parity / absolute EDS-residue decoder              absent
Unconditional classical sub-sqrt ECDLP                   absent
```

## 11. Decomposition of the remaining central task

The `Y_G` problem is now narrowed to mechanism classes not captured by the rank-one Ward minor geometry:

```text
A. one recurrence cell                         closed by 047
B. rank-one Ward two-cell minors               closed by 048
C. rank-one Ward natural 3x3 minors            closed by 048
D. rank-one Ward Pluecker syzygies              structurally classified by 048
E. genuinely rank-two elliptic-net multi-cells  open
F. independent theta/sigma determinant rows     open
G. p-adic analytic branch selection             open
H. unrestricted short nonlinear circuit         open
```

Each remaining stage asks the same question: after exact normalization and reduction, is there generator-sensitive information that selects the marked root `Y_G`, rather than a public coordinate function, a multiplicative net section, zero, or a universal syzygy?

## 12. Strategic successor

The next theorem-first object is

```text
RANK-TWO-NET-MULTI-CELL-049.
```

The first task is to leave rank-one Ward geometry entirely and build a finite symbolic grammar from genuinely rank-two net cells involving both marked points. The candidate must use at least two independent rank-two recurrence cells whose normal form is not inherited from one rank-one subnet.

The package will test:

1. the smallest coupled rank-two `3 x 3` minors after preferred-basis normalization;
2. cells mixing `(a,b)` indices with both coordinates nonzero;
3. exact reduction under the rank-two recurrence ideal and known basis changes;
4. whether any surviving term is generator-sensitive under `G -> [u]G` in the way required by `Y_G`;
5. total index, recurrence, normalization, coefficient, memory, and branch-extraction cost.

A numerical correlation is insufficient. A survivor must be an exact symbolic relation not reducible to rank-one Ward minors, a public coordinate identity, or a multiplicative net monomial.
