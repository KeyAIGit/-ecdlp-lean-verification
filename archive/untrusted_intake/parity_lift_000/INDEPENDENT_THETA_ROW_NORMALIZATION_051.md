# INDEPENDENT-THETA-ROW-NORMALIZATION-051

Date: 2026-08-12

Status: **independent changes of local row trivialization and a common public basis change factor completely out of the determinant. They cannot create cross-row generator orientation; any new bit is already the product of the row factors. Genuinely different theta characteristics or row-dependent section spaces remain open.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from package 050

Package 050 shows that a standard common-basis Frobenius-Stickelberger determinant has rank-two net normal form

```text
D_m(P_1,...,P_m)
 = c_m * W(sum_i u_i)
       * product_(i<j) W(u_i-u_j)
       / product_i W(u_i)^m.                    (T1)
```

Therefore a new determinant mechanism must escape the use of one common basis and one common quadratic normalization.

The first proposed escape is to normalize each evaluation row independently.

## 2. Geometric meaning of a row trivialization

Let `L` be one line bundle and let

```text
s_1,...,s_m
```

be a common basis of a section space. At each point `P_i`, choosing a local trivialization of the one-dimensional fibre `L|_(P_i)` identifies every section value with a field element.

Changing that local trivialization multiplies **every entry in row i by the same nonzero scalar** `r_i`.

Thus, if

```text
A_ij = s_j(P_i),
```

then independent row trivializations and a common basis change `C` produce

```text
A' = diag(r_1,...,r_m) * A * C.                 (T2)
```

This is the exact algebraic model of independent local row normalization for one common line bundle.

## 3. Exact determinant factorization

By multiplicativity of determinant,

```text
boxed:
det(A')
 = (product_i r_i) * det(A) * det(C).            (T3)
```

Combining `(T1)` and `(T3)` gives

```text
det(A')
 = det(C) * product_i r_i
   * c_m * W(sum_i u_i)
   * product_(i<j) W(u_i-u_j)
   / product_i W(u_i)^m.                        (T4)
```

No new interaction among the rows is created. The only additional point-dependent information is

```text
product_i r_i.                                   (T5)
```

Therefore, if the quadratic character of `det(A')` isolates parity or the absolute EDS orientation while the common-basis factor does not, then the missing bit is already present in the product of row trivialization factors.

The determinant has not compressed or generated that bit; it has only multiplied by it.

## 4. Basis changes are equally harmless

Any public change from one common basis to another is represented by one point-independent invertible matrix `C` on the right.

Its only effect is the public constant

```text
det(C).
```

Consequently:

```text
common section space + arbitrary public basis
```

is the same mechanism class as package 050.

## 5. Sign-branch visibility

Suppose the row normalizations are only signs

```text
r_i in {+1,-1}.
```

Then the determinant sees only

```text
product_i r_i.
```

Among the `2^m` sign vectors, exactly `2^(m-1)` have the same product. Hence a determinant with scalar row normalization loses all branch information except one aggregate bit.

That one aggregate bit could equal parity only if the row factors were themselves constructed with the required generator-sensitive orientation.

## 6. Relation to Y_G

The target from package 046 is

```text
Y_G(x([k]G))/y([k]G)=(-1)^k.                    (T6)
```

A bounded-size determinant with independently rescaled rows cannot select `Y_G` merely from the determinant interaction. After dividing out the common-basis Frobenius-Stickelberger factor, its entire residual is `(T5)`.

Thus a proposed row-normalized theta determinant must answer a simpler prior question:

```text
Can product_i r_i(P_i) be computed publicly and equal the required branch bit?
```

If yes, that product is already the decoder. If no, inserting it into a determinant does not help.

This is a reduction of mechanism, not a general lower bound on arbitrary products of point functions.

## 7. Frozen exact replay

`independent_theta_row_normalization.py` uses the six frozen prime-order `j=0` subgroups and the pole-ordered evaluation matrices from package 050.

For dimensions `m=3,4,5,6`, it applies:

1. three deterministic families of nonzero row factors derived from public point coordinates;
2. a nontrivial public upper-triangular common basis change;
3. two row-sign vectors having the same product;
4. a single row-sign flip.

It verifies exactly:

```text
det(diag(r) A C)=product(r) det(A) det(C),
quadratic-character quotient equals product of row characters,
two sign flips leave the determinant unchanged,
one sign flip negates the determinant.
```

The replay is an exact finite-field sanity check of `(T3)` in the actual matrices used by the research line. The theorem itself is ordinary determinant algebra.

## 8. Closed mechanism class

Closed by this package:

```text
one common line bundle and section space,
arbitrary public common basis changes,
independent scalar local trivializations at each row,
public diagonal row rescaling of the package-050 determinant ladder.
```

Any target bit obtained in this class is already contained in the product of the explicit row factors.

## 9. What remains genuinely open

Not closed:

1. rows drawn from genuinely different theta characteristics or different line bundles;
2. row-dependent basis transformations that cannot be factored as one scalar per row and one common column matrix;
3. Heisenberg/metaplectic intertwiners between distinct section spaces;
4. non-determinantal theta addition circuits;
5. p-adic analytic branch selection;
6. unrestricted short nonlinear circuits for `Y_G`.

These are qualitatively different from a change of trivialization.

## 10. Answer

```text
Do independent scalar row trivializations create a new determinant interaction? no
Exact residual beyond the common determinant                              product_i r_i
Does a common public basis change create point-dependent information?      no
How many sign vectors share one determinant multiplier?                    2^(m-1)
Does this construct Y_G?                                                    no, unless the row factors already do
Public parity / absolute EDS-residue decoder                               absent
Unconditional classical sub-sqrt ECDLP                                    absent
```

## 11. Strategic successor

The next theorem-first package is

```text
TWISTED-THETA-CHARACTERISTIC-052.
```

It must leave the scalar-row-rescaling model entirely. The first candidate should use two genuinely different theta characteristics or Heisenberg translates whose evaluation rows do not live in one common section basis.

The package must determine:

1. the exact transformation law under the subgroup generator and under `G -> -G`;
2. whether the twist creates an anti-invariant generator-sensitive bit or merely a public character;
3. whether all characteristics can be evaluated without materializing a dimension-`n` theta representation;
4. complete preprocessing, representation, memory, precision, and online cost;
5. whether the surviving quantity selects `Y_G` or only another multiplicative/coboundary factor.

## 12. Formalization boundary

`Ecdlp/Proved/IndependentThetaRowNormalization.lean` formalizes determinant factorization under diagonal row scaling and a common basis change, plus the product-one specialization. It does not formalize line bundles, theta functions, elliptic curves, secp256k1, parity, or ECDLP.
