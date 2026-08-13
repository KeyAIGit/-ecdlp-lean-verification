# RANK-TWO-NET-MULTI-CELL-049

Date: 2026-08-12

Status: **the smallest genuinely rank-two three-point coordinate determinant is exactly a multiplicative rank-two net ratio; it does not create an independent generator-oriented square-root equation.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from packages 046-048

For an odd prime-order subgroup

```text
H=<G>, |H|=n,
M=(n-1)/2,
```

package 046 identified canonical scalar parity with the unique marked-generator root `Y_G` satisfying

```text
Y_G(X)^2 = X^3+7 mod K_H(X),
Y_G(x([k]G))/y([k]G)=(-1)^k.                     (R1)
```

Packages 047-048 showed that one-cell and rank-one multi-cell Ward determinants collapse into multiplicative EDS monomials or universal Pluecker syzygies.

The present package leaves rank-one Ward geometry and tests the first genuinely rank-two additive determinant involving two marked points.

## 2. Rank-two setup

Let `W=W_(E,G,Q)` be the normalized rank-two elliptic net associated to public points `G,Q`. For an index vector

```text
u=(u1,u2) in Z^2,
```

write

```text
P_u=[u1]G+[u2]Q,
X_u=x(P_u),
Y_u=y(P_u).
```

All identities below are on the nondegenerate chart where the displayed points, net values, and coordinate differences are defined and nonzero.

## 3. Three-point coordinate determinant

For three public index vectors `u,v,w`, define

```text
D(u,v,w)
 =Y_u(X_v-X_w)
  +Y_v(X_w-X_u)
  +Y_w(X_u-X_v).                                 (R2)
```

This is the determinant of the three rows

```text
[1, X_u, Y_u],
[1, X_v, Y_v],
[1, X_w, Y_w].
```

It is the numerator of the rank-three net polynomial `Omega_(1,1,1)` evaluated at `(P_u,P_v,P_w)`.

## 4. Matrix-pullback factor

The exact integer-matrix pullback law gives

```text
Omega_(1,1,1)(P_u,P_v,P_w)
 = W(u+v+w) W(u) W(v) W(w)
   / [W(u+v) W(u+w) W(v+w)].                     (R3)
```

The elliptic-net coordinate-difference identity gives

```text
X_u-X_v
 = -W(u+v)W(u-v)/[W(u)^2 W(v)^2].                (R4)
```

Apply `(R4)` to the three factors in the Vandermonde denominator of `Omega_(1,1,1)` and substitute `(R3)`.

## 5. Exact genuinely rank-two collapse

After cancellation,

```text
boxed:
D(u,v,w)
 = - W(u+v+w) W(u-v) W(u-w) W(v-w)
     / [W(u)^3 W(v)^3 W(w)^3].                   (R5)
```

Thus the smallest coupled rank-two `3 x 3` additive determinant is not an independent additive branch equation. It is one multiplicative rank-two net ratio.

The identity is symbolic. The vectors may be small, near the subgroup order, beyond the period, or any other public integer functions of `n`.

## 6. Zero-sum specialization

If

```text
u+v+w=0,
```

then `W(u+v+w)=W(0)=0`, so `(R5)` gives

```text
D(u,v,w)=0.                                      (R6)
```

Geometrically, `P_u+P_v+P_w=O`, so the three curve points are collinear. The determinant detects the ordinary group-law relation and not the marked parity branch.

## 7. Relation to the target Y_G

The target `Y_G` contains a correlated sign choice over every Kummer pair. Formula `(R5)` contains only ordinary rank-two net sections at public indices.

Therefore this determinant adds no new absolute square-root equation beyond the multiplicative net algebra audited in earlier packages. Its quadratic character may be a nontrivial public sign sequence, but the determinant identity itself does not select `Y_G`.

This package does not claim that every possible multiplicative rank-two net expression is useless on every curve. It closes the declared three-point determinant and matrix-pullback mechanism.

## 8. Dependent-pair replay

For toy validation, set

```text
Q=[k]G
```

with known frozen toy scalars. Matrix pullback gives the normalized rank-two value

```text
W_(G,Q)(a,b)
 = W_G(a+bk)
   / [W_G(k)^(b^2-ab) W_G(k+1)^(ab)].            (R7)
```

The replay independently computes the points `P_u` by elliptic-curve addition and verifies `(R5)` against the coordinate determinant.

It also checks the standard normalization values

```text
W(1,0)=W(0,1)=W(1,1)=1,
W(2,0)=2y(G),
W(0,2)=2y(Q),
W(1,-1)=x(Q)-x(G),
W(2,1)=x(G)-x(G+Q),
W(1,2)=x(Q)-x(G+Q),
W(2,2)=2y(G+Q).
```

## 9. Frozen exact results

The verifier uses the frozen prime-order `j=0` toy subgroups

```text
n=19,31,67,271,397,433.
```

It checks:

1. `432` independent rank-two normalization identities;
2. `3,592` bounded three-point determinant factorizations;
3. `48` zero-sum collinearity specializations;
4. `88` public near/beyond-period vector triples;
5. `24` fixed determinant-character candidates, each rejecting parity up to global sign on its complete admissible toy domain.

The character mismatch is bounded evidence only. The determinant factorization is exact.

## 10. Answer

```text
First genuinely rank-two additive object             three-point coordinate determinant
Exact normal form                                    multiplicative rank-two net ratio
Factor                                               -W(u+v+w)W(u-v)W(u-w)W(v-w)/(W(u)^3W(v)^3W(w)^3)
Zero-sum specialization                              ordinary collinearity
Do public n-dependent vectors evade the collapse?    no
Does this construct Y_G?                             no
Public parity / absolute EDS-residue decoder         absent
Unconditional classical sub-sqrt ECDLP              absent
```

## 11. Closed and open classes

Closed so far:

```text
rank-one one-cell Ward determinants,
rank-one Ward two-cell minors,
rank-one natural three-cell minors and Pluecker syzygies,
the smallest genuinely rank-two three-point coordinate determinant,
known integer-matrix pullbacks of that determinant.
```

Still open:

1. higher Frobenius-Stickelberger coordinate determinants;
2. independently normalized theta/sigma rows rather than one common pullback;
3. non-determinantal rank-two additive circuits;
4. p-adic analytic branch selection;
5. unrestricted short nonlinear circuits for `Y_G`.

## 12. Strategic successor

The next theorem-first package is

```text
FROBENIUS-STICKELBERGER-DETERMINANT-050.
```

Its question is whether the general `m`-point evaluation determinant for a basis of `L(mO)` also factors into the classical sigma product

```text
sigma(sum z_i) * product_(i<j) sigma(z_i-z_j)
```

up to public denominator factors, and therefore remains inside the multiplicative theta/net algebra after pullback to `(G,Q)`.

A positive factorization would close the full natural coordinate-determinant ladder, not only the three-point case. A survivor must use genuinely independent row normalizations or a branch-sensitive analytic datum and must include complete preprocessing, representation, memory, precision, and online cost.

## 13. Formalization boundary

`Ecdlp/Proved/RankTwoNetMultiCell.lean` formalizes the cross-multiplied commutative-ring cancellation behind `(R5)` and the zero-total-factor consequence under nonzero denominator factors. It does not formalize elliptic curves, net polynomials, the matrix-pullback theorem, coordinate formulas, secp256k1, parity, or ECDLP.
