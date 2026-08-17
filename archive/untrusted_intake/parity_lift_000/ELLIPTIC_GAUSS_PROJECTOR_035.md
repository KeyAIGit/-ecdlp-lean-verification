# ELLIPTIC-GAUSS-PROJECTOR-035

Date: 2026-08-12

Status: **exact generator-oriented factor interpretation and scoped representation-degree obstruction; no sub-square-root decoder obtained**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Exact projector from package 034

For a prime-order subgroup

```text
H=<G>,  |H|=n,  n=1 mod 12,
```

let `chi_n` be the quadratic character modulo `n`.  On the `j=0` curve define

```text
z(P)=x(P)^3,
S_3(P)=sum_(a=1..n-1) chi_n(a) z([a]P).
```

For `Q=[k]G`, exact reindexing gives

```text
S_3(Q)=chi_n(k)S_3(G).                         (G1)
```

Thus a nonzero `S_3(G)` gives a generator-normalized oracle for the scalar
Legendre class.

The direct sum has `Theta(n)` terms.  The purpose of this package is to locate
`S_3` inside the algebraic factorization and determine what standard
elliptic-Gauss normalization preserves or destroys.

## 2. C6 quotient and oriented factors

The GLV unit group is

```text
C6={plus_or_minus 1, plus_or_minus lambda, plus_or_minus lambda^2}.
```

Because `n=1 mod 12`, every member of `C6` is a square modulo `n`.  The value

```text
z([a]G)=x([a]G)^3
```

is constant on each `C6` orbit, and `chi_n(a)` is constant there as well.

Define the two root sets

```text
Z_plus  ={z([a]G): a square,    modulo C6},
Z_minus ={z([a]G): a nonsquare, modulo C6}.
```

Each set has cardinality

```text
d=(n-1)/12.
```

They are disjoint.  Otherwise equality of two `x^3` values on a `j=0` GLV
orbit would put the two scalar indices in the same `C6` class, which preserves
the quadratic character.

Define monic factors

```text
F_plus(Z) =product_(r in Z_plus)  (Z-r),
F_minus(Z)=product_(r in Z_minus) (Z-r).
```

Their product is the full nonzero `C6`-orbit polynomial.  They depend on the
chosen generator: replacing `G` by `[u]G` preserves the two factors if
`chi_n(u)=+1` and swaps them if `chi_n(u)=-1`.

## 3. S_3 is the first separating coefficient

Each `C6` orbit contributes six equal terms to the scalar sum, so

```text
S_3(G)=6*(sum_(r in Z_plus) r - sum_(r in Z_minus) r).       (G2)
```

For a monic polynomial, the coefficient of `Z^(d-1)` is minus the sum of its
roots.  Hence `S_3` is exactly six times the difference of the first
non-leading coefficients of `F_plus` and `F_minus`.

On all retained frozen cases, this coefficient is already different and
`S_3(G)` is nonzero.

More generally, because `F_plus` and `F_minus` are distinct monic degree-`d`
polynomials, Newton identities imply that at least one of their first `d` power
sums differs.  Therefore at least one projector

```text
S_(3m)(G)=sum_a chi_n(a)x([a]G)^(3m),  1<=m<=d,
```

is nonzero.  This is an unconditional finite-family existence statement, but
the guaranteed family has size `(n-1)/12` and does not yield a compact
algorithm.

## 4. Exact bounded-degree obstruction

Suppose a polynomial `h(Z)` satisfies

```text
h(z([a]G))=chi_n(a)
```

on every nonzero `C6` orbit.  Then

```text
h(Z)^2-1
```

has `(n-1)/6` distinct roots.  Unless `h` is constant, this forces

```text
deg h >= (n-1)/12.                              (D1)
```

Likewise, let `r` be a rational function on the elliptic curve whose value on
every nonzero point `[a]G` is `chi_n(a)`.  The nonzero rational function

```text
r^2-1
```

has at least `n-1` zeros.  If the rational map defined by `r` has degree `D`,
the zero divisor of `r^2-1` has degree at most `2D`, so

```text
D >= (n-1)/2.                                    (D2)
```

For secp256k1 these bounds are approximately `2^252.4` and `2^255`,
respectively.

These are exact representation-degree bounds.  They do not rule out a compact
straight-line program for a high-degree function, just as repeated squaring
can represent a very high power with few operations.

## 5. Why the standard elliptic-Gauss invariant loses the bit

From `(G1)` and `chi_n(k)^2=1`,

```text
S_3([k]G)^2=S_3(G)^2.                            (G3)
```

Thus the square is generator-blind.  It depends on the curve and the
unoriented cyclic subgroup, not on whether the chosen generator differs by a
square or a nonsquare scalar.

Classical universal elliptic Gauss-sum constructions attach character-weighted
coordinate sums to torsion points and construct invariant powers and Jacobi
ratios by modular functions.  For a quadratic character, the first invariant
power is precisely a square.  Equation `(G3)` shows why such a standard
invariant cannot by itself recover the generator-oriented sign.

The oriented quantity `S_3(G)` is a square-root branch of the universal
quadratic invariant.  Replacing `G` by a nonsquare multiple reverses that
branch.

## 6. Generic modular representation size

For prime level `n`, the standard `Gamma_0(n)` modular function field has
degree `n+1` over the `j`-line.  Generic universal elliptic Gauss-sum
representations therefore use level-dependent modular data of linear size in
`n` or larger.

The present curve has the special CM value `j=0`, so generic modular degree is
not a circuit lower bound for the specialization.  A CM identity could in
principle compress the value dramatically.  But it must preserve the
square-root orientation tied to `G`; a formula for `S_3^2` alone is useless for
the hidden scalar bit.

## 7. Frozen replay

`elliptic_gauss_projector.py` verifies on every retained frozen group:

1. `C6` invariance of `x^3` and of the quadratic scalar class;
2. disjoint quadratic-residue and nonresidue `C6` root sets;
3. degrees `(n-1)/12` of the two oriented factors;
4. exact factorization into the full `C6`-orbit polynomial;
5. identity `(G2)` from both root sums and factor coefficients;
6. nonvanishing of `S_3`;
7. generator-change preservation or swapping of the factors;
8. generator-blindness of `S_3^2`;
9. the first differing power sum is already `m=1` on the frozen family.

## 8. Answer

```text
Where is the scalar-Legendre bit stored?                   in the orientation F_plus vs F_minus
What is S_3?                                                first coefficient difference
Exact public formula                                        yes, character-weighted orbit sum
Direct cost                                                  Theta(n)
Standard universal invariant                                S_3^2
Does the square preserve the hidden sign?                   no
Minimum C6-invariant polynomial decoder degree              (n-1)/12
Minimum bounded curve-rational decoder degree               (n-1)/2
Do those bounds exclude compact high-degree circuits?       no
Nonvanishing on frozen n=1 mod 12 cases                     yes
Nonvanishing theorem for secp256k1                           absent
Public carry / hard-R3 decoder                              absent
Classical sub-square-root ECDLP algorithm                   absent
```

## 9. Next object

The successor is

```text
EISENSTEIN-ORIENTED-GAUSS-ROOT-036.
```

Its object is the generator-oriented square root

```text
Gamma_G=S_3(G),
Gamma_G^2=unoriented universal quadratic elliptic-Gauss invariant.
```

Central question:

> Does the `j=0` Eisenstein-CM specialization provide a canonical, publicly
> evaluable orientation of `Gamma_G` or of the ratio
> `Gamma_Q/Gamma_G=chi_n(k)` with total cost
> `O(n^(1/2-epsilon))`, rather than only the generator-blind square?

The theorem-first obligations are:

1. identify `S_3` as a precise modular/theta object and determine its weight,
   level, and character;
2. derive its Eisenstein-CM specialization and compare it with elliptic Gauss
   and Jacobi sums in the CM literature;
3. determine whether a ray-class, cubic-theta, or Hecke-character formula
   canonically chooses the sign from `(E,G)`;
4. prove nonvanishing on secp256k1 or construct a finite compact fallback
   family;
5. count modular polynomial degree, coefficient size, ray-class degree,
   preprocessing, and online specialization cost;
6. reject formulas that compute only `Gamma_G^2` or hide an oriented table of
   size `Omega(sqrt(n))`;
7. even if a Legendre oracle results, analyse classical shifted-Legendre
   recovery separately before claiming a classical ECDLP improvement.

No broad statistical search is admitted without a new exact CM identity.

## 10. Formalization boundary

`Ecdlp/Proved/EllipticGaussProjector.lean` formalizes the elementary fact that
a quadratic-character eigenprojector has generator-blind square and that
normalizing an oriented value recovers the sign.  It does not formalize
elliptic Gauss sums, modular curves, divisor degrees, Newton identities,
secp256k1 nonvanishing, or arithmetic-circuit complexity.
