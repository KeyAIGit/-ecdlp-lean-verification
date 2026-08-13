# TWISTED-THETA-CHARACTERISTIC-052

Date: 2026-08-13

Status: **on a genus-one curve, distinct theta characteristics differ by a nontrivial two-torsion line bundle. For secp256k1 no nontrivial theta characteristic is defined over the base field; the three nontrivial characteristics form one Frobenius orbit, and their canonical norm collapses to `y(P)^2`. Standard twisted-characteristic descent therefore loses the generator-oriented sign required by `Y_G`.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Target from package 046

For the odd prime-order subgroup

```text
H=<G>, |H|=n,
```

package 046 defined the unique marked-generator root `Y_G` in the Kummer algebra:

```text
Y_G(X)^2 = X^3+7 mod K_H(X),
Y_G(x([k]G))/y([k]G)=(-1)^k.                     (C1)
```

Packages 047-051 close the natural common-basis determinant ladder and scalar row re-trivializations. Package 052 asks whether genuinely different theta characteristics or theta line bundles can supply the missing branch.

## 2. Theta characteristics in genus one

For a smooth genus-one curve `E`, the canonical line bundle is trivial. A theta characteristic is therefore a line bundle `kappa` satisfying

```text
kappa^tensor2 ~= O_E.                            (C2)
```

Hence theta characteristics form the two-torsion subgroup of `Pic^0(E)`. After choosing the origin of an elliptic curve, they are indexed by `E[2]`.

On

```text
E_b : y^2=x^3+b
```

the three nontrivial geometric two-torsion points are

```text
T_i=(r_i,0),
r_i^3+b=0.                                      (C3)
```

The corresponding nontrivial characteristic is represented by the degree-zero divisor class `T_i-O`.

## 3. Difference of two characteristics

If `kappa_1` and `kappa_2` are theta characteristics, then

```text
M=kappa_1 tensor kappa_2^(-1)
```

satisfies

```text
M^tensor2 ~= O_E.                                (C4)
```

If the characteristics are distinct, `M` is a nontrivial degree-zero two-torsion line bundle. Thus there is no global point-independent isomorphism between the two line bundles. Comparing their section values as ordinary field scalars requires a chosen local or meromorphic trivialization of `M`.

Such a choice is additional branch data. Squaring the comparison or taking a Galois norm removes the ambiguity but also removes its sign.

## 4. Concrete characteristic functions

For `T_i=(r_i,0)`, the rational function

```text
f_i(P)=x(P)-r_i                                  (C5)
```

has divisor

```text
div(f_i)=2(T_i)-2(O).                            (C6)
```

Therefore `f_i` is the square of the corresponding theta-characteristic section in the line-bundle sense. It is not itself a canonical signed square root.

Let the roots satisfy

```text
r_1+r_2+r_3=0,
r_1r_2+r_1r_3+r_2r_3=0,
r_1r_2r_3=-b.
```

Then

```text
boxed:
product_i (x(P)-r_i)=x(P)^3+b=y(P)^2.            (C7)
```

For public non-two-torsion points `G,Q`, the normalized Frobenius norm is

```text
boxed:
product_i (x(Q)-r_i)/(x(G)-r_i)
 = y(Q)^2/y(G)^2.                                (C8)
```

The canonical descent is therefore an ordinary square. It is unchanged by

```text
G -> -G,
Q -> -Q.
```

It cannot select the marked branch in `(C1)`.

## 5. secp256k1 specialization

For secp256k1,

```text
E : y^2=x^3+7,
#E(F_p)=n,
n is odd,
cofactor=1.
```

A rational nontrivial two-torsion point would have order two and would divide `#E(F_p)`. Since the group order is odd,

```text
E[2](F_p)={O}.                                   (C9)
```

Thus only the trivial theta characteristic is defined over `F_p`. The cubic `x^3+7` has no `F_p` root and is irreducible; its three roots, and hence the three nontrivial characteristics, form a Frobenius orbit of length three over `F_(p^3)`.

Their orbit norm is exactly `(C7)`. Consequently the canonical base-field object obtained from the full orbit is `y^2`, which erases the sign.

## 6. Why using G as a normalization point does not repair the descent

Any expression formed from

```text
x(G), x(Q),
Frobenius-symmetric functions of the nontrivial E[2] orbit
```

is unchanged under `G -> -G`, while the target root changes:

```text
Y_(-G)=-Y_G.                                     (C10)
```

Therefore such a generator-blind descent cannot select `Y_G` for both marked generators.

A formula may insert `y(G)` or another explicit signed row factor. But then the generator orientation is already contained in that explicit factor. Package 051 proves that placing such factors inside a determinant does not generate or compress an additional bit.

## 7. Split controls

Two frozen toy fields in the corpus have all three nontrivial two-torsion points rational. There, each individual `f_i(P)=x(P)-r_i` is directly evaluable in the base field.

The exact replay checks the normalized quadratic characters

```text
chi((x([k]G)-r_i)/(x(G)-r_i)).                   (C11)
```

Across the complete retained odd-order subgroups, none equals canonical scalar parity up to a global sign. The matches are exactly balanced in the retained controls.

This finite result is only a rejection of the individual rational-characteristic candidates. The general no-go in this package is the base-field nonexistence and norm-collapse statement for standard theta-characteristic descent on secp256k1.

## 8. Closed mechanism class

Closed by this package:

```text
two distinct base-field theta characteristics on secp256k1,
canonical Frobenius norm of the three nontrivial characteristics,
symmetric orbit descent through the functions x-r_i,
normalization of that norm at the public generator,
using scalar row trivializations to disguise the same branch input.
```

The exact collapsed object is

```text
y(Q)^2/y(G)^2.
```

It contains no generator-oriented square-root sign.

## 9. What remains open

Not closed:

1. a genuinely metaplectic or Heisenberg lift that is not merely a chosen two-torsion line-bundle trivialization;
2. a public generator-sensitive intertwiner between distinct high-level theta spaces;
3. a non-determinantal theta addition circuit whose output is anti-invariant under `G -> -G`;
4. p-adic analytic continuation that canonically fixes the branch;
5. unrestricted short nonlinear circuits for `Y_G(x(Q))`.

Any proposed lift must account for the source of its linearization. If the linearization already contains a choice among the three nontrivial characteristics or a signed square root of `(C7)`, that choice is advice and must be charged.

## 10. Frozen exact replay

`twisted_theta_characteristic.py` uses the six frozen prime-order `j=0` toy subgroups

```text
n=19,31,67,271,397,433.
```

It verifies:

1. all subgroup points satisfy `y^2=x^3+7`;
2. the two-torsion cubic has either zero or three base-field roots;
3. on split controls, the product of the three characteristic functions equals `y^2`;
4. the normalized product equals `y(Q)^2/y(G)^2`;
5. every individual normalized characteristic square-class rejects parity up to global sign;
6. all symmetric characteristic data is unchanged by point negation.

The secp256k1 certificate uses only the fixed public field, group order, and cofactor-one data. No unknown scalar target is evaluated.

## 11. Answer

```text
Distinct geometric theta characteristics                        yes; indexed by E[2]
Distinct base-field theta characteristics on secp256k1          no
Nontrivial characteristic field of definition                  F_(p^3)
Canonical Frobenius-orbit norm                                  y(P)^2
Normalized norm at G,Q                                         y(Q)^2/y(G)^2
Does the norm retain generator orientation?                    no
Does scalar row re-trivialization create it?                    no
Does standard twisted-characteristic descent construct Y_G?    no
Public parity / absolute EDS-residue decoder                    absent
Unconditional classical sub-sqrt ECDLP                         absent
```

## 12. Strategic successor

The next theorem-first package is

```text
METAPLECTIC-THETA-INTERTWINER-053.
```

Its central question is narrower than package 052:

> Can a public high-level theta structure or metaplectic/Heisenberg intertwiner provide a generator-sensitive linear lift whose output is not equivalent to selecting a nonrational two-torsion characteristic, a full dual character, or an explicit signed row factor?

The package must classify the ambiguity group of the lift, show its behavior under `G -> -G` and `Q -> -Q`, and include complete representation, preprocessing, memory, precision, and online evaluation cost. A projective action without a canonical linearization is insufficient.