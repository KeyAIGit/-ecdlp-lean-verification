# GLV-GAUSSIAN-PERIOD-CUT-029

Date: 2026-08-12

Status: **exact structural simplification of the cyclotomic carry phase; no public Q-only evaluator obtained**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Object

Let `n` be an odd prime and let `lambda` have order three modulo `n`. Put

```text
C3={1,lambda,lambda^2}.
```

For

```text
Q=[k]G,
z=zeta_n^k,
```

define the cubic Gaussian period

```text
eta_G(Q)=z+z^lambda+z^(lambda^2).
```

It is invariant under the GLV orbit:

```text
eta_G(phi Q)=eta_G(Q).
```

Under negation,

```text
eta_G(-Q)=conjugate(eta_G(Q)).
```

## 2. The product phase collapses to the period orientation

Because

```text
1+lambda+lambda^2=0 mod n,
```

one has

```text
(1-z)(1-z^lambda)(1-z^(lambda^2))
 = z^(-1)+z^(-lambda)+z^(-lambda^2)
   -(z+z^lambda+z^(lambda^2))
 = conjugate(eta_G(Q))-eta_G(Q).
```

Thus

```text
M_G(Q)=-2*i*Im(eta_G(Q)).
```

Combining this with the already-established half-angle formula gives

```text
g_G(Q)=(-1)^gamma(Q)=-sign(Im eta_G(Q))
```

for every nonzero point, with the sign convention used by this branch.

The carry is therefore not hidden in all three cyclotomic factors separately. It is exactly the orientation of one C3 Gaussian period relative to complex conjugation.

## 3. Exact orbit size

The Galois group of `Q(zeta_n)` is `(Z/nZ)^*`. Multiplication by an exponent `a` sends

```text
eta_1 -> eta_a=zeta_n^a+zeta_n^(lambda*a)+zeta_n^(lambda^2*a).
```

The subgroup `C3` fixes `eta_1`.

Distinct `C3` cosets give distinct periods. If two coset sums were equal, their difference would give a sparse integer polynomial of degree at most `n-1` vanishing at `zeta_n`. Since the minimal polynomial is

```text
Phi_n(X)=1+X+...+X^(n-1),
```

that sparse difference would have to be zero; it cannot be a nonzero multiple of `Phi_n`. Hence the two cosets are equal.

Therefore the stabilizer is exactly `C3` and

```text
[Q(eta_1):Q]=(n-1)/3.
```

Since `-1` is not in the odd-order subgroup `C3`, no nontrivial period is real:

```text
eta_a != eta_(-a)=conjugate(eta_a).
```

Complex conjugation pairs the `(n-1)/3` periods into exactly

```text
(n-1)/6
```

orientation pairs.

For secp256k1 this pair count is

```text
(n-1)/6
=19298681539552699237261830834781317975472927379845817397100860523586360249056.
```

This is exactly the same count as the C6 orbit pairs used by the generator-oriented half-kernel. The equality of counts follows from the same scalar quotient; this package does not claim an explicit algebraic isomorphism between the period roots and the y-coordinate half-kernel roots.

## 4. What was simplified

The previous global phase appeared to require the product

```text
product_i (1-zeta_n^(lambda^i*k)).
```

It is now reduced to one orientation question:

```text
Is eta_G(Q) the upper or lower member of its conjugate pair?
```

Equivalently, let

```text
T=eta+conjugate(eta),
N=eta*conjugate(eta),
Delta=T^2-4*N=(eta-conjugate(eta))^2.
```

The Frobenius/Galois-invariant data `T,N,Delta` determine the unordered pair

```text
{eta,conjugate(eta)}
```

but not its orientation. The carry is the missing square-root branch of `Delta`.

This explains simultaneously why trace and norm lose the bit and why an oriented half-factor is required.

## 5. Complexity consequence

An explicit generic representation of `eta` over the rationals has degree `(n-1)/3`, and the unordered conjugate-pair state space has size `(n-1)/6`. Materializing either object is vastly above the square-root operation scale for secp256k1.

This is a representation-size obstruction, not a circuit lower bound. A direct bit-only algorithm could in principle determine the branch without constructing the period field.

## 6. Answer of this package

```text
Can the cyclotomic product be simplified?                yes
Exact simplified object                                  C3 Gaussian period eta
Does carry equal its conjugate orientation?              yes
Explicit period-field degree                             (n-1)/3
Number of conjugate orientation pairs                    (n-1)/6
Public Q-only orientation evaluator                      absent
Sub-sqrt carry/R3/ECDLP algorithm                        absent
```

## 7. Next object

The next object is not another splitting and not the full period. It is the **period-orientation resolvent**

```text
A_G(Q)=eta_G(Q)-conjugate(eta_G(Q)).
```

Only its sign is required. The successor package is

```text
PERIOD-ORIENTATION-RESOLVENT-030.
```

Central question:

> Is there a public, generator-sensitive theta/net/sigma triple resolvent whose value is a known nonzero factor times `A_G(Q)`, or whose finite-field character directly selects the same branch, with total cost `O(n^(1/2-epsilon))`, without constructing `eta`, `mu_n`, or an object with `(n-1)/6` states?

The first theorem gate is to classify every bounded-rank zero-sum triple line/net function by its behavior under conjugation and generator reversal. A candidate that is conjugation invariant cannot decode carry. A candidate whose anti-invariant factor is merely a full dual character returns to package 028 and is rejected.

## 8. Formalization boundary

`Ecdlp/Proved/GlvGaussianPeriodCut.lean` formalizes the algebraic resolvent identity for three nonzero field elements whose product is one. It does not formalize cyclotomic fields, complex positivity, Galois orbit degree, or a public evaluator from elliptic-curve coordinates.
