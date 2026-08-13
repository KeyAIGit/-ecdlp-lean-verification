# ELLIPTIC-NET-ORIENTED-SQUARE-ROOT-047

Date: 2026-08-12

Status: **every determinant that is exactly one Ward or elliptic-net recurrence cell factors into a multiplicative net monomial; the first normalized rank-two additive determinant is therefore not an independent generator-oriented square-root equation**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from package 046

For an odd prime-order subgroup

```text
H=<G>, |H|=n,
M=(n-1)/2,
```

package 046 defined the subgroup Kummer kernel `K_H(X)` and the unique
marked-generator interpolation root `Y_G(X)` satisfying

```text
Y_G(X)^2 = X^3+7 mod K_H(X),
Y_G(x([k]G))/y([k]G)=(-1)^k.                     (N1)
```

The exact constructive target is therefore no longer an unspecified parity
function. It is a short circuit for the specific oriented square root `Y_G`.

Stange's elliptic nets are natural candidates because they provide nonlinear
recurrences and rational net polynomials of rapidly growing index without
expanding all coefficients. The present package tests the first additive
escape: a determinant or discrete Wronskian consisting of one recurrence cell.

## 2. General elliptic-net recurrence

An elliptic net is a function

```text
W:A -> K
```

on a free abelian indexing group satisfying

```text
W(p+q+s)W(p-q)W(r+s)W(r)
+W(q+r+s)W(q-r)W(p+s)W(p)
+W(r+p+s)W(r-p)W(q+s)W(q)=0.                    (N2)
```

Write the three monomials in `(N2)` as `A`, `B`, and `C`. Then

```text
A+B=-C.                                          (N3)
```

Thus every additive cancellation that is exactly two summands of one net
recurrence is already a single multiplicative net monomial.

This is the basic one-cell collapse.

## 3. Rank-one Ward determinant at arbitrary indices

For an elliptic divisibility sequence, `(N2)` specializes to Ward's recurrence

```text
W(m+r)W(m-r)
 =W(m+1)W(m-1)W(r)^2
  -W(r+1)W(r-1)W(m)^2.                           (N4)
```

The right side has the appearance of a discrete determinant or Wronskian. But
`(N4)` factors it exactly as

```text
W(m+r)W(m-r).                                    (N5)
```

The indices `m` and `r` may be fixed, near the subgroup order, or much larger.
Therefore replacing small indices by `n`-dependent indices does not prevent the
one-cell determinant from collapsing.

Earlier point-function-coboundary packages already classified the quadratic
characters of finite multiplicative products of ordinary division-polynomial
sections. Hence the factorization `(N5)` returns this determinant to an already
audited multiplicative class.

## 4. Minimal normalized rank-two determinant

Let `W=W_(E,P,Q)` be a normalized nondegenerate rank-two elliptic net. The
rank-two recurrence identity in Stange's baseset calculation gives

```text
W(2,2)W(1,-1)W(1,0)W(0,1)
 =W(1,1)[
    W(0,2)W(2,1)W(1,0)
   -W(0,1)W(2,0)W(1,2)
  ].                                               (N6)
```

Normalization means

```text
W(1,0)=W(0,1)=W(1,1)=1.
```

Consequently

```text
boxed:
D(P,Q)
 :=W(0,2)W(2,1)-W(2,0)W(1,2)
 =W(2,2)W(1,-1).                                  (N7)
```

The first natural additive `2 by 2` net determinant is therefore exactly a
multiplicative product.

## 5. Coordinate form on the short Weierstrass model

On

```text
E:y^2=x^3+7,
P=(x_1,y_1),
Q=(x_2,y_2),
R=P+Q,
```

the explicit rank-two net polynomials give

```text
W(2,0)=2y_1,
W(0,2)=2y_2,
W(1,-1)=x_2-x_1,
W(2,1)=x_1-x(R),
W(1,2)=x_2-x(R),
W(2,2)=2y(R).                                     (N8)
```

Substitution in `(N7)` gives

```text
boxed:
D(P,Q)=2y(P+Q)[x(Q)-x(P)].                        (N9)
```

Thus the determinant is a directly evaluable coordinate product. It neither
constructs nor approximates the interpolation coefficients of `Y_G`.

## 6. Why this does not select the oriented square root

The root `Y_G` of package 046 contains one correlated sign choice above every
Kummer pair. Equation `(N7)` contains only two ordinary net factors, and `(N9)`
contains only the public points `P`, `Q`, and `P+Q`.

The determinant can be evaluated, and its quadratic character may form a
nontrivial sign sequence, but the recurrence supplies no identity equating that
sequence with `(N1)`. On every retained frozen subgroup the determinant
character disagrees with canonical parity at some points and agrees at others,
so neither it nor its global negative is an exact toy decoder.

That finite mismatch is only a rejection of this explicit candidate. It is not
promoted to a general secp256k1 character-sum theorem.

## 7. Matrix pullbacks and normalization

The exact elliptic-net pullback law under an integer matrix expresses a
transformed net value as another net value multiplied by basis terms with
quadratic exponents. Therefore a known integral change of basis can transport
`(N2)` or `(N7)`, but it cannot turn a one-cell identity into an independent
absolute branch equation. The transported correction remains quadratic scale
data.

A matrix depending on the hidden scalar could align a basis with the unknown
relation between `G` and `Q`, but supplying that matrix would already expose the
scalar label that the construction is meant to recover.

## 8. Mechanism class closed

Closed by this package:

```text
one Ward recurrence cell at arbitrary public indices,
one rank-two elliptic-net recurrence cell,
the minimal normalized 2 by 2 net determinant,
known integral-basis pullbacks of those same one-cell identities.
```

Every object in this declared class factors into a multiplicative net monomial
and therefore does not provide a new oriented square-root equation.

Not closed:

1. a sum combining several recurrence cells before factorization;
2. a determinant whose minors are not individual net recurrence cells;
3. a discrete Wronskian with independently normalized rows;
4. a high-index theta or sigma determinant with genuine additive
   cancellation;
5. a p-adic analytic continuation selecting a branch globally;
6. any short circuit for `Y_G` outside the declared net grammar.

## 9. Frozen exact replay

`elliptic_net_oriented_square_root.py` verifies on the frozen prime orders

```text
19,31,67,271,397,433
```

all of the following:

1. `5,320` bounded Ward cells satisfy `(N4)` exactly;
2. `180` near-period and beyond-period Ward cells satisfy `(N4)` exactly;
3. `1,200` nondegenerate rank-two point pairs satisfy `(N7)`;
4. the same `1,200` pairs satisfy the coordinate identity `(N9)`;
5. the determinant never vanishes on the retained chart;
6. its quadratic character is not parity up to a global sign on any retained
   case.

The Ward replay uses division-polynomial recurrences and accepts no unknown
scalar target.

## 10. Answer

```text
Does one Ward determinant remain additive?                  no
Exact factor                                                W(m+r)W(m-r)
Does the minimal rank-two determinant remain additive?      no
Exact factor                                                W(2,2)W(1,-1)
Coordinate form                                             2y(P+Q)(x(Q)-x(P))
Do public high indices avoid the collapse?                  no
Does a known basis pullback create an absolute branch?      no
Does this construct Y_G?                                    no
Public parity / EDS-residue decoder                         absent
Unconditional classical sub-sqrt ECDLP                     absent
```

## 11. Strategic successor

The next theorem-first object is

```text
MULTI-CELL-NET-CANCELLATION-048.
```

Its central question is:

> Can a bounded-support linear combination of at least two independent
> elliptic-net recurrence cells avoid monomial factorization and produce the
> generator-oriented root `Y_G`, while keeping total index, normalization,
> coefficient, and evaluation cost below `n^(1/2)`?

The package must define a finite additive grammar, reduce it modulo the net
recurrence ideal, and distinguish three outcomes:

1. exact collapse to the multiplicative net algebra;
2. a nonzero but orientation-blind public coordinate function;
3. a genuinely new oriented square-root relation.

No statistical template family is accepted without an exact symbolic normal
form.

## 12. Formalization boundary

`Ecdlp/Proved/EllipticNetOrientedSquareRoot.lean` formalizes the abstract
three-term recurrence collapse and the normalized rank-two determinant
identity. It does not formalize elliptic nets, division polynomials, coordinate
formulas, matrix pullbacks, character sums, secp256k1, or ECDLP.
