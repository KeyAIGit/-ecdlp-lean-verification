# MULTI-CELL-NET-CANCELLATION-048

Date: 2026-08-12

Status: **the natural two-cell Ward/EDS determinant obtained by eliminating the common middle coefficient collapses exactly to one multiplicative EDS monomial for arbitrary indices; genuinely independent three-or-more-cell syzygies and non-Ward minors remain open**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from package 047

Package 047 showed that every determinant consisting of exactly one Ward or elliptic-net recurrence cell factors back into a multiplicative net monomial. In particular, the first normalized rank-two `2 x 2` determinant is not an independent equation for the generator-oriented Kummer square root `Y_G`.

The next live class is a bounded additive combination of at least two independent recurrence cells.

## 2. Two Ward cells with a shared middle index

For a rank-one elliptic divisibility sequence `W`, Ward's recurrence is

```text
W(m+t)W(m-t)
 = W(m+1)W(m-1)W(t)^2
   - W(t+1)W(t-1)W(m)^2.                         (M1)
```

Fix `m` and apply `(M1)` twice, at shifts `r` and `s`:

```text
A_r = U W(r)^2 - V_r W(m)^2,
A_s = U W(s)^2 - V_s W(m)^2,                     (M2)
```

where

```text
A_t = W(m+t)W(m-t),
U   = W(m+1)W(m-1),
V_t = W(t+1)W(t-1).
```

The common coefficient `U` is the obvious object to eliminate.

## 3. Exact two-cell determinant

Form

```text
D(m;r,s)
 = A_r W(s)^2 - A_s W(r)^2.                      (M3)
```

Substituting `(M2)` cancels the entire `U` contribution:

```text
D(m;r,s)
 = W(m)^2 [V_s W(r)^2 - V_r W(s)^2].             (M4)
```

But the bracket is itself Ward's recurrence, now with middle index `s` and shift `r`:

```text
V_s W(r)^2 - V_r W(s)^2
 = W(r+s)W(s-r).                                  (M5)
```

Therefore

```text
boxed:
W(m+r)W(m-r)W(s)^2
 - W(m+s)W(m-s)W(r)^2
 = W(m)^2 W(r+s)W(s-r).                          (M6)
```

This identity is symbolic and holds for arbitrary indices whenever Ward's recurrence holds.

## 4. Determinant interpretation

Equation `(M6)` is the exact determinant identity

```text
det [
  W(m+r)W(m-r)    W(r)^2
  W(m+s)W(m-s)    W(s)^2
]
 = W(m)^2 W(r+s)W(s-r).                          (M7)
```

Thus the first natural multi-cell Pluecker/Wronskian construction does not retain an irreducible additive numerator. It factors to one multiplicative EDS monomial.

The result is stronger than package 047's one-cell closure because `r` and `s` are independent and may depend publicly on the subgroup order `n`.

## 5. Adjacent specialization

Set

```text
s=r+1.
```

Since a normalized EDS has `W(1)=1`, `(M6)` becomes

```text
boxed:
W(m+r)W(m-r)W(r+1)^2
 - W(m+r+1)W(m-r-1)W(r)^2
 = W(m)^2 W(2r+1).                               (M8)
```

So the most obvious adjacent discrete Wronskian is exactly one odd-index EDS term times `W(m)^2`.

This excludes the hypothesis that merely coupling two adjacent Ward cells creates a new absolute branch selector.

## 6. Consequence for the oriented square root target

Package 046 identified the target as the marked-generator root `Y_G` satisfying

```text
Y_G(X)^2 = X^3+7 mod K_H(X),
Y_G(x([k]G))/y([k]G)=(-1)^k.                     (M9)
```

A successful additive net construction would need an equation whose surviving term is not already in the multiplicative EDS/net algebra and whose normalization genuinely selects the marked-generator branch.

The family `(M7)` fails this test exactly: its output is the ordinary product

```text
W(m)^2 W(r+s)W(s-r).
```

Hence it supplies no independent square-root equation for `Y_G`.

This is a mechanism-class closure, not a proof that the quadratic character of every such product is useless on every curve. Earlier packages separately audit the fixed-index multiplicative residue mechanism.

## 7. Why high public indices do not evade the theorem

No bounded-index hypothesis appears in `(M6)`. Therefore one may take, for example,

```text
m=n+a,
r=n+b,
s=2n+c,
```

or any other publicly specified integer expressions in the subgroup order.

Periodicity may simplify some factors, but it cannot restore an additive determinant: the symbolic factorization happened before reduction modulo the period.

A basis or index depending on the hidden scalar `k` is not admissible, since it would inject the information the construction is meant to recover.

## 8. Frozen exact replay

`multi_cell_net_cancellation.py` evaluates division-polynomial EDS terms on the frozen prime-order `j=0` subgroups

```text
n=19,31,67,271,397,433.
```

For each retained case it checks:

1. exhaustive bounded triples `(m,r,s)` with indices up to `18`;
2. the exact determinant identity `(M6)`;
3. the adjacent specialization `(M8)`;
4. public near-period and beyond-period index patterns.

All arithmetic is exact in the finite field. There is no floating-point fitting and no unknown target scalar.

## 9. Formalization

`Ecdlp/Proved/MultiCellNetCancellation.lean` kernel-checks the algebraic elimination step:

```text
A_r = U R^2 - V_r M^2,
A_s = U S^2 - V_s M^2

=>

A_r S^2 - A_s R^2
 = M^2 (V_s R^2 - V_r S^2).
```

When the bracket is identified with the second Ward product, Lean obtains the full determinant collapse abstractly.

The file does not formalize elliptic curves, division polynomials, the Ward recurrence theorem itself, secp256k1, parity, or ECDLP.

## 10. Answer

```text
Does the natural two-cell Ward determinant remain additive?   no
Exact factor                                                  W(m)^2 W(r+s)W(s-r)
Does choosing public n-dependent indices avoid collapse?      no
Does the adjacent two-cell Wronskian remain additive?         no
Adjacent factor                                               W(m)^2 W(2r+1)
Does this construct Y_G?                                      no
Public parity / absolute EDS-residue decoder                  absent
Unconditional classical sub-sqrt ECDLP                       absent
```

## 11. Decomposition of the remaining central task

The remaining `Y_G` problem can now be decomposed into increasingly narrow mechanism classes:

```text
A. one recurrence cell                         closed by 047
B. shared-coefficient two-cell Ward minors     closed by 048
C. two unrelated cells / non-Ward minors       open
D. three-or-more recurrence-cell syzygies      open
E. independently normalized theta/sigma rows   open
F. p-adic analytic branch selection            open
G. unrestricted short nonlinear circuit        open
```

Each stage asks the same exact question: after symbolic normalization, is there any surviving generator-sensitive branch information not already expressible as a public or multiplicative net section?

## 12. Strategic successor

The next subpackage is

```text
MULTI-CELL-NET-CANCELLATION-048B.
```

It will construct the first finite recurrence-ideal grammar with at least three cells and perform exact symbolic `S`-polynomial / elimination reductions. The target is not numerical correlation. A candidate survives only if its normal form contains a genuinely new generator-sensitive additive relation rather than a Ward/Pluecker product or a public coordinate function.

The first objects are:

1. three Ward cells with common `m` but independent shifts `r,s,t`;
2. two cells with different middle indices and one shared shift;
3. the smallest `3 x 3` Casoratian/Wronskian built from Ward products;
4. corresponding rank-two net cells after preferred-basis normalization.

Any surviving relation must then be tested against `(M9)` and receive a complete index, coefficient, memory, normalization, and branch-extraction cost accounting.
