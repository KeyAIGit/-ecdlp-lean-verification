# FROBENIUS-STICKELBERGER-DETERMINANT-050

Date: 2026-08-12

Status: **the standard common-basis Frobenius-Stickelberger evaluation determinant factors, after rank-two pullback, into one multiplicative elliptic-net ratio. The factorization holds for the entire natural determinant ladder; independently normalized or twisted rows remain open.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from package 049

For an odd prime-order subgroup

```text
H=<G>, |H|=n,
```

package 046 identified canonical scalar parity with the marked-generator Kummer root `Y_G`:

```text
Y_G(X)^2 = X^3+7 mod K_H(X),
Y_G(x([k]G))/y([k]G)=(-1)^k.                     (F1)
```

Packages 047-049 showed that one-cell Ward determinants, rank-one multi-cell minors, and the first genuinely rank-two three-point determinant all collapse into multiplicative net expressions.

The present package tests the full standard coordinate-determinant ladder rather than another isolated minor.

## 2. Classical Frobenius-Stickelberger factorization

Let `z_1,...,z_m` be points on the complex uniformization `C/Lambda`, and let

```text
1, wp, wp', ..., wp^(m-2)
```

be the classical pole-ordered basis. Frobenius and Stickelberger give a determinant factorization of the form

```text
det(f_j(z_i))
 = c_m * sigma(sum_i z_i)
       * product_(i<j) sigma(z_i-z_j)
       / product_i sigma(z_i)^m,                 (F2)
```

where `c_m` is a nonzero constant depending only on the chosen basis and ordering.

Primary source: Frobenius and Stickelberger, *Zur Theorie der elliptischen Functionen* (1877), English translation arXiv:2603.27466, formula (3). The translation writes the derivative basis explicitly and derives the sigma-product factorization.

For the short Weierstrass model `y^2=x^3+7`, a pole-ordered algebraic basis of `L(mO)` is

```text
1, x, y, x^2, xy, x^3, x^2y, ...                (F3)
```

with pole weights `0,2,3,...,m`. Changing from the derivative basis to `(F3)` only changes the public constant `c_m`.

## 3. Pullback to a normalized rank-two elliptic net

Let `W=W_(E,G,Q)` be the normalized rank-two elliptic net, and let

```text
u_i=(a_i,b_i),
P_i=[a_i]G+[b_i]Q.
```

Stange's sigma definition gives

```text
sigma(P_u)=W(u) * B(u),                           (F4)
```

where `B(u)` is a product of the three preferred-basis sigma values with exponents

```text
q_G(a,b)=a^2-ab,
q_Q(a,b)=b^2-ab,
q_GQ(a,b)=ab.                                    (F5)
```

Each exponent is a quadratic form.

For every quadratic form `q` and vectors `u_1,...,u_m`,

```text
q(sum_i u_i)
 + sum_(i<j) q(u_i-u_j)
 = m * sum_i q(u_i).                             (F6)
```

Therefore all preferred-basis scale factors in `(F2)` cancel exactly after substituting `(F4)`.

The rank-two pullback is

```text
boxed:
D_m(u_1,...,u_m)
 = c_m * W(sum_i u_i)
       * product_(i<j) W(u_i-u_j)
       / product_i W(u_i)^m.                    (F7)
```

Here `D_m` is the evaluation determinant for any fixed common basis of `L(mO)`, and `c_m` is public and independent of the points.

Formula `(F7)` contains no new additive branch datum. It lies entirely in the multiplicative rank-two net algebra.

## 4. Relation to the three-point result

For `m=3`, the pole-ordered basis is `[1,x,y]`. Formula `(F7)` becomes the package-049 identity, up to the row/column orientation convention:

```text
D_3
 = W(u+v+w)W(u-v)W(u-w)W(v-w)
   / [W(u)^3W(v)^3W(w)^3].                      (F8)
```

Thus package 049 was the first member of the general Frobenius-Stickelberger ladder.

## 5. Four-, five-, and six-point determinants

The first new cases use the bases

```text
m=4: [1,x,y,x^2],
m=5: [1,x,y,x^2,xy],
m=6: [1,x,y,x^2,xy,x^3].                         (F9)
```

On the retained finite-field normalization the exact replay finds `c_m=1` for `m=3,4,5,6`:

```text
D_m
 = W(sum_i u_i)
   * product_(i<j) W(u_i-u_j)
   / product_i W(u_i)^m.                        (F10)
```

This finite-field normalization statement is verified only for the declared bases and frozen corpus. The general mechanism-class conclusion uses `(F2)` and `(F6)` and requires only that `c_m` be public and nonzero.

## 6. Zero-sum specialization

If

```text
sum_i u_i=0,
```

then `W(sum_i u_i)=W(0)=0`, so

```text
D_m=0.                                           (F11)
```

The determinant detects an ordinary linear relation among the points. It does not select the marked square-root branch `Y_G`.

## 7. Why public high indices do not help

Formula `(F7)` is symbolic in the integer vectors. The vectors may contain `n+a`, `2n+b`, or larger public addition-chain indices.

Periodicity can simplify the resulting net values, but cannot restore an independent additive numerator: factorization occurs before period reduction.

A vector depending on the unknown scalar `k` is inadmissible because it supplies the hidden coordinate the construction is intended to recover.

## 8. Closed mechanism class

Closed by packages 049-050:

```text
standard m-point evaluation determinants for one common basis of L(mO),
classical Frobenius-Stickelberger coordinate determinants,
known integer-matrix pullbacks to the rank-two net (G,Q),
zero-sum and high-public-index specializations of the same ladder.
```

Every member factors as one public constant times a multiplicative net ratio.

This does **not** prove that the quadratic character of every possible multiplicative ratio is useless on every curve. It proves that the determinant supplies no independent additive equation for `Y_G` beyond the already-audited multiplicative net algebra.

## 9. What remains open

Not closed:

1. determinants whose rows or columns have genuinely independent theta/sigma normalizations;
2. twisted line bundles or characteristics not obtained from one common `L(mO)` basis;
3. non-determinantal additive theta circuits;
4. p-adic analytic continuation selecting a generator-oriented branch;
5. unrestricted short nonlinear circuits for `Y_G`.

A successful survivor must retain generator-sensitive sign information after all public quadratic scale factors are removed.

## 10. Frozen exact replay

`frobenius_stickelberger_determinant.py` uses the frozen prime-order `j=0` subgroups

```text
n=19,31,67,271,397,433.
```

It independently computes curve points and normalized rank-two net values, then verifies:

```text
m=3 determinant factorizations,
m=4 determinant factorizations,
m=5 determinant factorizations,
m=6 determinant factorizations,
public near/beyond-period four-point tuples,
zero-sum four-point determinants,
fixed four-point determinant characters rejecting parity up to global sign.
```

The determinant identities are exact finite-field equalities. The character mismatch is bounded toy evidence only.

## 11. Answer

```text
Does the general standard determinant remain additive?       no
Exact normal form                                             public constant * multiplicative net ratio
Do preferred-basis sigma factors survive pullback?            no; quadratic balance cancels them
Do public n-dependent vectors evade the factorization?        no
Does zero-sum specialization select a branch?                  no; determinant vanishes
Does this construct Y_G?                                      no
Public parity / absolute EDS-residue decoder                  absent
Unconditional classical sub-sqrt ECDLP                       absent
```

## 12. Strategic successor

The next theorem-first package is

```text
INDEPENDENT-THETA-ROW-NORMALIZATION-051.
```

Its central question is:

> Can rows or columns carrying genuinely different theta characteristics, line-bundle trivializations, or sigma normalizations produce a determinant whose scale quotient is not a common quadratic coboundary and whose surviving sign selects `Y_G`?

The package must first define exactly what data are public, how each row is normalized, and how the construction changes under `G -> [u]G`. Any candidate must include complete coefficient-generation, preprocessing, memory, precision, online-evaluation, and branch-extraction cost.

A common-basis determinant, a public diagonal rescaling of its rows, or a quadratic net pullback is already closed by `(F7)` and is not a new candidate.

## 13. Formalization boundary

`Ecdlp/Proved/FrobeniusStickelbergerDeterminant.lean` formalizes the four-point quadratic exponent cancellations for the three rank-two preferred-basis scale forms and a zero-total-factor consequence. It does not formalize complex sigma functions, the Frobenius-Stickelberger theorem, elliptic curves, net polynomials, arbitrary `m`, secp256k1, parity, or ECDLP.
