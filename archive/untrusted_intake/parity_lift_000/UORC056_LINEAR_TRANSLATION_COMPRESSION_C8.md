# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C8: linear translation-compression boundary

Date: 2026-08-13

Status: **all nontrivial finite-field linear representations of the prime-order translation subgroup have charged base-field dimension at least `ord_n(p)`. For secp256k1 this is `(n-1)/6`, so every nontrivial linear translation compression is linear in `n`. Ambient algebraic representations of the full elliptic curve are trivial. The surviving evaluator must be nonlinear in public coordinates or must escape translation-representation form.**

## 1. Ambient algebraic representations are trivial

Let `E` be an elliptic curve over a field and let

```text
rho:E -> GL_m
```

be a morphism of algebraic groups.

The variety `E` is proper and geometrically connected, while `GL_m` is affine. Every matrix coordinate of `rho` is a global regular function on `E`, hence is constant. Since a group morphism sends the identity to the identity matrix,

```text
boxed:
rho(P)=I for every P in E.                       (A1)
```

Therefore a fixed-dimensional ambient algebraic linearization of all translations cannot distinguish `G`, `Q`, or their relative scalar.

This includes ordinary ambient cohomological translation actions: translations of an abelian variety act trivially on the usual cohomology. A determinant or trace built only from such an action is generator-blind.

## 2. Finite subgroup representations

The regular action used by C6 is not a representation of the connected algebraic group `E`; it is a representation of the finite subgroup

```text
H=<G> isomorphic to C_n.
```

Let

```text
rho:H -> GL_m(F_(p^d))                           (R1)
```

be nontrivial, with `n` prime and `n` different from `p`.

Because `n` is prime, the kernel of `rho` is either all of `H` or trivial. Nontriviality therefore implies that

```text
rho(G)
```

has exact order `n`.

Let

```text
r=ord_n(p).
```

Over `F_(p^d)`, the degree of a primitive `n`th root of unity is

```text
ord_n(p^d)=r/gcd(r,d).                           (R2)
```

A matrix of exact order `n` must have a primitive `n`th root among its eigenvalues over a splitting field. Hence its minimal polynomial contains an irreducible cyclotomic factor of degree `ord_n(p^d)`. Since the degree of a minimal polynomial is at most the matrix dimension,

```text
m >= r/gcd(r,d).                                 (R3)
```

Charging representation over the base field gives

```text
boxed:
d*m >= d*r/gcd(r,d) >= r=ord_n(p).              (R4)
```

Thus moving to an extension field can trade matrix dimension for extension degree, but cannot lower the full base-field representation size below `ord_n(p)`.

## 3. secp256k1 consequence

C7 verifies exactly that

```text
ord_n(p)=(n-1)/6.
```

Therefore every nontrivial representation

```text
H -> GL_m(F_(p^d))
```

satisfies

```text
boxed:
d*m >= (n-1)/6=Theta(n).                        (S1)
```

This is far above the complete target

```text
O(n^(1/2-epsilon)).
```

In particular:

```text
one-dimensional character over an extension      extension degree >= (n-1)/6,
small matrix over a moderate extension            product d*m >= (n-1)/6,
base-field matrix representation                  dimension m >= (n-1)/6,
regular point representation                      dimension n.
```

## 4. Determinant-line consequence

Suppose a proposed small complex has chain groups carrying honest linear representations of `H` over finite extensions of `F_p`, and its determinant-line or torsion invariant depends on `G,Q` only through those translation matrices.

If the total charged base-field dimension is below `ord_n(p)`, every translation representation occurring in the complex is trivial. The resulting determinant-line expression is independent of `G` and `Q` and cannot equal canonical parity.

If one representation is nontrivial, its charged dimension alone is at least `ord_n(p)` by `(R4)`.

Thus a translation-equivariant linear complex cannot meet the sub-square-root gate on secp256k1.

## 5. Exact scope

Closed:

```text
fixed-dimensional algebraic representations of the ambient elliptic curve,
ordinary ambient-cohomology translation traces,
nontrivial base-field linear representations of H below ord_n(p),
small extension-field character representations after charging d*m,
translation-equivariant linear determinant-line complexes below ord_n(p).
```

Not closed:

```text
nonlinear coordinate functions of G and Q,
Q-dependent matrices that do not form a group representation,
residue or intersection formulas outside finite-dimensional translation modules,
arithmetic circuits using rational curve coordinates directly,
nonlinear oriented elliptic-product summaries.
```

This is a representation-class lower bound, not a universal arithmetic-circuit lower bound.

## 6. Strategic consequence

The highest-value surviving task is no longer to find a smaller linear model of `T_G` and `T_Q`. On secp256k1, no nontrivial finite-field linear model has sub-square-root charged size.

The next pass must seek a genuinely nonlinear primal-coordinate identity for

```text
-n^(-1)[t]det(I+T_G+tT_Q)=(-1)^k,
```

or prove a scoped no-go for one nonlinear residue, intersection, or oriented-product grammar.

## 7. Answer

```text
ambient algebraic translation representation             trivial
nontrivial H representation over F_(p^d)                 d*m >= ord_n(p)
secp256k1 ord_n(p)                                       (n-1)/6
small linear determinant-line compression                rejected
nonlinear primal-coordinate first variation              open
accepted-cost evaluator                                  absent
sub-square-root ECDLP                                    absent
```
