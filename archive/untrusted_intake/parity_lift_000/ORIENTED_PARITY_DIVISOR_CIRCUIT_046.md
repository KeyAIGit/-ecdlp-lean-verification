# ORIENTED-PARITY-DIVISOR-CIRCUIT-046

Date: 2026-08-12

Status: **canonical scalar parity is identified exactly with one generator-oriented square root in the subgroup Kummer algebra; symmetric kernel data fixes the square but not the branch, while coefficient tables, explicit root products, and bounded-degree determinants remain at or above the square-root boundary**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from package 045

Let

```text
H=<G>, |H|=n,
Q=[k]G,
M=(n-1)/2,
```

where `n` is an odd prime and `k` is the canonical representative in
`{1,...,n-1}`.

Package 045 proved that the canonical even set

```text
E={2,4,...,n-1}
```

has trivial multiplier stabilizer, while the only multiplier swapping it with
the odd set is `-1`. In particular, neither the order-three secp256k1 GLV unit
nor the full `C6` unit action preserves the parity divisor.

The remaining question was whether the high-degree oriented divisor could still
have a short `n`-dependent circuit.

## 2. Exact scalar-label half-root factorization

Before returning to encoded curve points, parity has a completely explicit
formula in the hidden scalar field `F_n`.

Define

```text
A_n(X)=product_(j=1)^M (X-2j),
B_n(X)=product_(j=1)^M (X-(2j-1)).
```

The even and odd canonical representatives partition `F_n^*`, so

```text
A_n(X) B_n(X)=X^(n-1)-1.                         (O1)
```

Negation swaps the two classes. Hence

```text
B_n(X)=(-1)^M A_n(-X).                           (O2)
```

For every nonzero scalar `k`, exactly one of `A_n(k)` and `B_n(k)` vanishes.
Therefore

```text
P_n(k)=[B_n(k)-A_n(k)]/[B_n(k)+A_n(k)]
      =(-1)^k.                                   (O3)
```

This is an exact degree-`M` rational parity decoder when the numerical scalar
`k` is already available. It is not an evaluator on the encoded point
`Q=[k]G`.

## 3. The subgroup Kummer kernel

Work on

```text
E/F_p : y^2=x^3+7.
```

The nonzero points of `H` split into `M` opposite pairs

```text
{P,-P}.
```

Let

```text
K_H(X)=product_(one pair {P,-P}) (X-x(P)).        (O4)
```

Then `K_H` is squarefree of degree `M`. It depends on the subgroup but not on a
choice of sign inside each pair.

Every pair contains exactly one even canonical scalar and one odd canonical
scalar, because `n-k` has parity opposite to `k`.

Choose representatives

```text
P_j=[j]G, 1<=j<=M.
```

The even member of the pair `{P_j,-P_j}` has y-coordinate

```text
(-1)^j y(P_j).
```

There is therefore a unique interpolation polynomial

```text
Y_G(X), deg(Y_G)<M,
```

such that

```text
Y_G(x(P_j))=(-1)^j y(P_j).                       (O5)
```

This polynomial is the oriented parity square root.

## 4. Exact square-root congruence

At every root of `K_H`, equation `(O5)` gives

```text
Y_G(x(P_j))^2=y(P_j)^2=x(P_j)^3+7.
```

Since `K_H` is squarefree,

```text
boxed:
Y_G(X)^2 = X^3+7 mod K_H(X).                     (O6)
```

The Kummer kernel and the curve equation determine the square in `(O6)`, but
not its generator-oriented square root.

## 5. Exact parity decoder on curve points

For every nonzero point

```text
P=[k]G,
```

the y-coordinate is nonzero because the subgroup has odd order. Equation
`(O5)` gives

```text
boxed:
Y_G(x(P))/y(P)=(-1)^k.                           (O7)
```

Indeed, when `1<=k<=M`, this is the interpolation condition. When `k=n-j`, the
point is `-P_j`; both the y-coordinate and canonical parity change sign.

Thus the following objects are exactly equivalent up to public field
operations:

```text
canonical scalar parity,
an oriented half of the subgroup divisor,
the generator-oriented root Y_G of (O6).
```

This is the principal positive result of the package. It replaces an undefined
search for a parity circuit by one exact algebraic target.

## 6. Branch count in the split Kummer algebra

Consider

```text
A_H=F_p[X]/(K_H).
```

Because `K_H` splits into `M` distinct linear factors,

```text
A_H ~= product_(j=1)^M F_p.
```

At every component, `X^3+7` is nonzero and has the two square roots

```text
plus_or_minus y(P_j).
```

The congruence

```text
Y^2=X^3+7 mod K_H
```

therefore has exactly

```text
2^M                                             (O8)
```

componentwise roots in `A_H`.

The target `Y_G` is one structured member of this space. This `2^M` count is a
branch count in a declared split-algebra representation, not an arithmetic-
circuit lower bound.

## 7. Generator dependence

Replace the marked generator by

```text
G_u=[u]G, u in F_n^*.
```

The subgroup and `K_H` do not change, but the canonical label of a fixed point
is multiplied by `u^(-1)`. Hence `G_u` selects another root `Y_(G_u)` of the
same congruence `(O6)`.

If two generators selected the same root, they would define the same even
canonical subset. Their ratio would preserve the parity set. Package 045 shows
that the preserving multiplier is only `1`. Therefore

```text
Y_(G_u)=Y_(G_v) iff u=v.                         (O9)
```

There are exactly `n-1` generator-selected roots. Also

```text
Y_(-G)=-Y_G.                                     (O10)
```

Subgroup-only kernel or isogeny data cannot distinguish these marked-generator
orientations. A successful circuit must consume the marked generator in an
essential way.

## 8. Restricted circuit audit

### 8.1 Coefficient materialization

Writing `Y_G` explicitly requires up to `M` field coefficients. On secp256k1,

```text
M=(n-1)/2 approximately 2^255.
```

A coefficient table is therefore inadmissible.

### 8.2 Explicit oriented product tree

Any construction that represents one oriented half-divisor by one leaf per
root has `M` leaves. A binary product tree has at least

```text
M-1
```

multiplication gates. Balancing reduces depth to `O(log n)` but does not reduce
circuit size.

This closes only explicit leaf-product representations.

### 8.3 Bounded-degree determinant

Suppose an oriented half-root section is represented by the determinant of an
`r` by `r` matrix whose entries have divisor or polynomial degree at most `d`.
The determinant has degree at most `r*d`. Since it must contain `M` oriented
roots,

```text
r*d >= M.                                        (O11)
```

For secp256k1, a balanced bounded-entry representation reaches essentially the
`2^128` frontier. This is a degree-size tradeoff for the declared determinant
model. It does not exclude entries of enormous degree represented by short
nonlinear circuits.

### 8.4 Symmetric kernel data

The pair

```text
(K_H, X^3+7 mod K_H)
```

is unchanged under every independent component sign flip. Any procedure using
only these symmetric objects can verify a proposed square root but cannot
select `Y_G` without extra generator-sensitive data.

## 9. Relation to elliptic nets and EDS

Stange's elliptic-net framework provides rational net polynomials on products
of elliptic curves, nonlinear recurrences, and exact pullback laws under integer
matrices. It is therefore a natural source of short high-degree circuits.
However, normalized elliptic nets require a preferred basis, and their standard
multiplicative pullback factors are quadratic scale data.

Lauter and Stange show that the perfectly periodic point function is computable
from a public point and that adjacent EDS residue ratios are public. The missing
absolute EDS residue is the same global orientation isolated here: on the
secp256k1 normalization it differs from scalar parity by a public point-function
factor.

Consequently, standard net recurrence can propagate an already selected
branch, but the unresolved question is whether an additive or determinant net
identity selects the specific root `Y_G` without enumerating the canonical
scalar path.

## 10. Frozen exact replay

`oriented_parity_divisor_circuit.py` verifies on six frozen prime-order
`j=0` subgroups:

```text
n=19,31,67,271,397,433.
```

For every retained case it checks:

1. the scalar factorization `(O1)`;
2. the negation relation `(O2)`;
3. the exact scalar decoder `(O3)` at every nonzero scalar;
4. squarefreeness and degree of `K_H`;
5. interpolation of `Y_G`;
6. the congruence `(O6)`;
7. the parity identity `(O7)` at every nonzero subgroup point;
8. `n-1` distinct marked-generator orientation vectors;
9. the global sign change `(O10)`;
10. product-tree and bounded-entry determinant size certificates.

In all retained toy cases, `Y_G` has maximal possible interpolation degree
`M-1`. This is bounded evidence only and is not asserted for secp256k1.

## 11. Answer

```text
Exact scalar-label parity rational function                 yes
Exact curve-side generator-oriented object                 Y_G
Defining equation                                           Y_G^2=x^3+7 mod K_H
Exact parity extraction                                     Y_G(x(P))/y(P)
Square roots in the split Kummer algebra                    2^M
Marked-generator roots                                      n-1 distinct
Does subgroup-only kernel data select Y_G?                  no
Explicit coefficient/product representation cost           Theta(n)
Bounded-entry determinant tradeoff                          r*d >= M
General short nonlinear high-degree circuit                 open
Public parity / EDS-residue decoder                         absent
Unconditional classical sub-sqrt ECDLP                     absent
```

## 12. Strategic successor

The next theorem-first object is

```text
ELLIPTIC-NET-ORIENTED-SQUARE-ROOT-047.
```

Its central question is:

> Can a constant-rank elliptic-net, sigma, theta, or additive determinant
> identity construct or evaluate the specific generator-oriented root `Y_G`
> modulo `K_H` in complete `O(n^(1/2-epsilon))` cost, rather than merely
> propagating a quadratic normalization or verifying `Y_G^2`?

The package must:

1. instantiate the exact integer-matrix pullback law for rank-two nets;
2. separate multiplicative quadratic-scale factors from additive cancellation;
3. prove that already-closed multiplicative sections do not select `Y_G`;
4. test one minimal additive determinant or Wronskian family with an exact
   transformation law;
5. charge index size, recurrence length, coefficient generation, memory,
   exceptional points, and branch extraction;
6. return a positive circuit or a scoped no-go theorem.

## 13. Formalization boundary

`Ecdlp/Proved/OrientedParityDivisorCircuit.lean` formalizes componentwise sign
square invariance, injectivity of the sign action at nonzero roots, the two
ratio branches, and the binary product-tree gate arithmetic. It does not
formalize elliptic curves, Kummer kernel polynomials, interpolation, the exact
`2^M` root count, divisor degrees, determinant complexity, secp256k1, or ECDLP.
