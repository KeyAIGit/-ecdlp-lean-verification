# DUAL-ORBIT-QUADRATIC-RESOLVENT-034

Date: 2026-08-12

Status: **exact scalar-Legendre observables obtained; no classical sub-square-root carry, parity, or ECDLP algorithm obtained**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from package 033

For

```text
H=<G>,  |H|=n,
Q=[k]G,
C3={1,lambda,lambda^2},
```

and a primitive dual phase `zeta_n`, define

```text
M_a(k)=product_(c in C3) (1-zeta_n^(a*c*k)),
U_a(k)=M_a(k)/M_a(1).
```

The normalized-period blackbox gives the carry when the distinguished dual
class `a=1` is supplied.  Package 033 showed that public Frobenius data leaves
two large dual quotient orbits, corresponding to square and nonsquare scalar
classes.

This package determines exactly what the symmetric product over one of those
two orbits contains.

## 2. Exact multiplicative quadratic resolvent

Assume

```text
n = 1 mod 12.
```

Then `-1` and the order-three scalar `lambda` are squares modulo `n`, so `C6`
is contained in the quadratic-residue subgroup.

Let

```text
QR  = nonzero quadratic residues modulo n,
NQR = nonresidues modulo n,
A_QR  = product_(r in QR)  (1-zeta_n^r),
A_NQR = product_(r in NQR) (1-zeta_n^r).
```

Multiplying `U_a(k)` over `a mod C3` inside `QR` gives

```text
Lambda_G(k)
 = product_(a in QR/C3) U_a(k)
 = [product_(r in QR)(1-zeta_n^(r*k))] / A_QR.
```

Multiplication by `k` either preserves or swaps the two quadratic classes.
Therefore

```text
chi_n(k)=+1  ->  Lambda_G(k)=1,
chi_n(k)=-1  ->  Lambda_G(k)=A_NQR/A_QR.              (Q1)
```

Also

```text
A_QR*A_NQR=product_(r=1..n-1)(1-zeta_n^r)=Phi_n(1)=n.
```

Thus the quadratic dual-orbit product is exactly two-valued and encodes the
Legendre class of the hidden scalar.

Since `U_(-a)=U_a`, the product over `QR/C3` is the square of the product over
the actual `QR/C6` Frobenius-orbit classes.  The unsquared orbit product has a
branch ambiguity, but its square already gives equation `(Q1)`.

## 3. A public-line additive projector

The multiplicative formula still refers to the complementary dual line.  A
more constructive exact identity is available entirely on the public subgroup.

For any point function `f` define

```text
S_f(P)=sum_(a=1..n-1) chi_n(a) f([a]P).
```

For `Q=[k]G`, reindex with `b=a*k`:

```text
S_f(Q)
 = sum_a chi_n(a) f([a*k]G)
 = chi_n(k) sum_b chi_n(b) f([b]G)
 = chi_n(k) S_f(G).                                (Q2)
```

Hence, whenever `S_f(G)` is nonzero,

```text
chi_n(k)=S_f(Q)/S_f(G).                            (Q3)
```

This is an exact generator-normalized scalar-Legendre observable using only
public multiples of its input point.  It does not require an independent dual
torsion point.

## 4. The natural j=0 function

On

```text
E: y^2=x^3+7
```

the GLV automorphism sends

```text
x -> beta*x,  beta^3=1.
```

Because `lambda` is square modulo `n`, the quadratic weights are unchanged by
GLV reindexing.  Therefore

```text
sum_a chi_n(a) x([a]G)^j
 = beta^j sum_a chi_n(a) x([a]G)^j.
```

For `j=1,2`, the factor `beta^j` is nontrivial, so the sum vanishes.  The first
coordinate power not forced to vanish is

```text
f(P)=x(P)^3.
```

It is invariant under both GLV and negation.  The frozen replay verifies:

```text
S_3(P)=sum_a chi_n(a)x([a]P)^3,
S_3([k]G)=chi_n(k)S_3(G).
```

On every retained frozen `j=0` subgroup with `n=1 mod 12`, `S_3(G)` is nonzero.
This is positive bounded evidence, not a proof of nonvanishing on secp256k1.

## 5. Complexity

The direct algorithm computes `S_3(P)` by enumerating all nonzero scalars:

```text
Theta(n) point-function values,
Theta(n) field operations,
```

or comparable preprocessing/advice if tabulated.  This is far above the
Pollard square-root scale.

Equation `(Q2)` therefore gives an exact public formula but not yet a useful
cryptanalytic algorithm.

The object is an elliptic Gauss projector: a character-weighted sum of a point
function over a torsion line.  Universal elliptic Gauss-sum theory shows that
related sums admit modular-function representations, but this package does not
assume that those representations have sub-square-root size for cryptographic
level `n`, nor that their standard coordinate choice coincides with `x^3` in
this CM setting.

## 6. Why the new bit is not carry

For secp256k1

```text
n=1 mod 4,
chi_n(-k)=chi_n(k).
```

The scalar-Legendre bit is negation-even, whereas

```text
g_G(-Q)=-g_G(Q).
```

Thus neither `(Q1)` nor `(Q3)` is itself a carry decoder.

If a public evaluator for `chi_n(k)` were available, shifted queries would give

```text
Q+[a]G=[k+a]G
   -> chi_n(k+a),
```

which is the shifted Legendre-symbol problem.  Efficient quantum recovery is
known for that oracle.  A comparable unconditional classical sub-square-root
recovery is not established here.

## 7. Frozen replay

`dual_orbit_quadratic_resolvent.py` verifies, on the frozen toy family:

1. exact quadratic-class mapping under multiplication by every nonzero `k`;
2. the two values of the multiplicative orbit product in auxiliary fields
   carrying `mu_n`;
3. `A_QR*A_NQR=n`;
4. non-collapse of the two auxiliary values;
5. exact reindexing identity `(Q2)` for every nonzero scalar;
6. forced vanishing of the `x` and `x^2` projectors;
7. nonvanishing of the `x^3` projector on every retained case;
8. GLV and negation invariance of `x^3`.

The auxiliary cyclotomic replay validates exponent-set identities only.  It is
not an efficient secp256k1 representation.

## 8. Answer

```text
Does the quadratic dual-orbit product have two exact values?       yes
What hidden information does it expose?                            chi_n(k)
Is there a public-line exact projector for the same bit?            yes
Natural j=0 projector                                               sum chi(a)x([a]P)^3
Frozen retained cases with nonzero base projector                   all
Direct evaluation cost                                              Theta(n)
Does the bit equal carry or parity?                                  no
Classical sub-square-root recovery from shifted Legendre oracle      absent
Public carry / hard-R3 decoder                                       absent
Unconditional classical sub-square-root ECDLP algorithm              absent
```

## 9. Next object

The successor is

```text
ELLIPTIC-GAUSS-PROJECTOR-035.
```

Its exact object is

```text
S_3(P)=sum_(a=1..n-1) chi_n(a)x([a]P)^3.
```

Central question:

> Does the `j=0` CM specialization of this elliptic Gauss projector admit a
> compact modular, theta, sigma, isogeny, or recurrence representation with
> total time, memory, preprocessing, advice, and precision
> `O(n^(1/2-epsilon))`, and can its nonvanishing on secp256k1 be proved without
> constructing the `(n-1)/2` weighted orbit?

The theorem-first obligations are:

1. identify the precise modular weight, level, and CM transformation law of
   `S_3`;
2. prove nonvanishing or provide a finite public family of point functions for
   which at least one projector is nonzero;
3. compare with universal elliptic Gauss-sum and elliptic Jacobi-sum formulas;
4. derive an explicit representation and count its degree, coefficient size,
   and specialization cost as functions of `n`;
5. reject any representation with `Omega(sqrt(n))` advice or output size;
6. if a compact Legendre oracle is obtained, analyse shifted-Legendre recovery
   separately and do not call it a classical ECDLP break without a literal
   sub-square-root reduction.

No broad statistical model search is admitted without a new exact identity.

## 10. Formalization boundary

`Ecdlp/Proved/DualOrbitQuadraticResolvent.lean` formalizes the elementary
normalization and eigenvalue-cancellation identities used by the projector.
It does not formalize quadratic characters, elliptic curves, finite sums over
torsion, cyclotomic products, nonvanishing on secp256k1, or a complexity bound.
