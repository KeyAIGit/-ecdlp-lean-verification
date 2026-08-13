# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — COMPACT FROBENIUS KERNEL B3

Date: 2026-08-13

Status: **the compact map `alpha=Frob-id` exposes the full rational kernel with a short formula, but its denominator, local pole coefficient, invariant differential, and all target-side pullbacks are generator-blind. At every rational kernel point the local numerator is a square built from the public curve coordinate; no marked branch is selected.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Frozen central target

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

On secp256k1 the rational subgroup is the full group and

```text
H=E(F_p)=ker(Frob-id).
```

The endomorphism

```text
alpha=Frob-id
```

has degree `n` but is evaluable by one Frobenius and one group subtraction. It is therefore the strongest natural compact-map candidate in the B track.

## 2. Explicit x-coordinate formula

Write

```text
F(X)=X^3+7,
D(X)=X^p-X.
```

For a point `P=(X,Y)`, put

```text
P^p=(X^p,Y^p).
```

The slope of `P^p-P` is `(Y^p+Y)/(X^p-X)`. Since

```text
(Y^p+Y)^2
 =F(X)^p+2F(X)^((p+1)/2)+F(X),
```

we obtain

```text
x(alpha(P))=N(X)/D(X)^2,                         (F1)
```

where

```text
N(X)=F(X)^p+2F(X)^((p+1)/2)+F(X)
     -(X^p+X)D(X)^2.                             (F2)
```

This is a short straight-line description despite algebraic degree about `p`.

## 3. Rational and nonrational x factors

Assume there is no rational two-torsion. Define

```text
A(X)=F(X)^((p-1)/2),
K(X)=gcd(X^p-X,A(X)-1),
C(X)=gcd(X^p-X,A(X)+1).                          (F3)
```

The roots of `K` are exactly the x-coordinates of nonzero rational points. The roots of `C` are the base-field x-values for which `F(x)` is a nonsquare. Hence

```text
D(X)=K(X)C(X).                                   (F4)
```

For cofactor-one prime-order curves,

```text
deg K=(n-1)/2.                                  (F5)
```

The exact cancellation in `(F1)` is

```text
gcd(N,D^2)=C^2,
D^2/C^2=K^2.                                    (F6)
```

Thus the reduced denominator of the compact endomorphism is precisely the square of the subgroup Kummer kernel.

## 4. Local coefficient at a rational kernel point

Let `q=x(Q)` for a nonzero rational point `Q=(q,y)`. Then

```text
D(q)=0,
D'(q)=-1,
F(q)=y^2,
N(q)=4F(q)=4y^2.                                (F7)
```

Therefore in the local coordinate `u=X-q`,

```text
x(alpha(P))=4y^2/u^2+lower pole terms.           (F8)
```

The local pole coefficient is a public square. It is identical for the two marked-generator problems `(G,Q)` and `(-G,Q)` except for explicit signed coordinate data already present in the input.

After removing the complementary factor, let

```text
N_red=N/C^2.
```

Since `(X^p-X)'=-1`, differentiating `D=KC` at `q` gives

```text
K'(q)C(q)=-1.                                   (F9)
```

Consequently

```text
boxed:
N_red(q)=4F(q)K'(q)^2.                          (F10)
```

Any square root of the compact local coefficient is

```text
+/- 2yK'(q).
```

Selecting its sign is precisely additional branch data. The compact map supplies the square but not the generator-oriented root.

## 5. Translation invariance of the whole local germ

For every `T in ker(alpha)`,

```text
alpha(P+T)=alpha(P)+alpha(T)=alpha(P).           (F11)
```

Thus any target-side rational function pulled back through `alpha` is invariant under translation by the entire kernel.

In invariant formal coordinates at the identity, Frobenius has zero differential and

```text
d(alpha)=d(Frob)-d(id)=-1.                       (F12)
```

Translation identifies the complete local germ at every kernel point with the same germ at the identity. Local jets of the compact map cannot order or orient the kernel points.

Coordinate jets may contain the public coordinates of the centre point, but any signed factor inserted through `y(G)` or `y(Q)` already contains the sign externally; the compact endomorphism has not generated or compressed it.

## 6. Consequence for the marked Kummer root

The objects

```text
alpha,
K,
C,
N,
N_red,
local pole coefficient,
invariant local jets,
target-side pullbacks through alpha
```

are determined by the curve and the unoriented subgroup. They are the same for the marked generators `G` and `-G`.

But

```text
Y_(-G)=-Y_G.                                     (F13)
```

Therefore no decoder using only this compact-map data can be correct for both marked generators. A successful B-track evaluator must add a genuinely generator-sensitive operation not reducible to an explicit signed input factor.

## 7. Frozen exact replay

`uorc056_compact_frobenius_kernel.py` uses cofactor-one prime-order toy curves and checks exactly:

1. the Euler-factor definitions of `K` and `C`;
2. `D=KC`;
3. `gcd(N,D^2)=C^2`;
4. reduced denominator `K^2`;
5. `N(q)=4F(q)` at every nonzero rational point;
6. `N_red(q)=4F(q)K'(q)^2`;
7. generator-negation blindness of all declared compact data.

The secp256k1 certificate records the exact degrees and the cofactor-one kernel identification. No unknown target scalar is evaluated.

## 8. Formalization boundary

`Ecdlp/Proved/CompactKernelTranslation.lean` kernel-checks the abstract group-homomorphism core:

```text
T in ker(alpha) => alpha(P+T)=alpha(P),
```

and the resulting invariance of every pullback `f(alpha(P))`.

It does not formalize Frobenius, differentials, polynomial gcds, secp256k1, parity, or ECDLP.

## 9. Answer for this class

```text
Is alpha=Frob-id compactly evaluable?                  yes
Does its reduced denominator contain K_H^2?            yes
Does the local numerator contain a square root?         only up to +/-
Does invariant local data distinguish kernel points?   no
Does it choose the marked generator branch?             no
Public parity / absolute EDS oracle                     absent
Sub-square-root ECDLP                                   absent
```

## 10. Strategic successor inside B

The remaining direct-kernel object is no longer the full compact endomorphism. It is the **oriented half-divisor** selecting one point from each pair `{P,-P}`.

The next B package must:

1. write its exact divisor and public exceptional pole;
2. construct the corresponding generalized Miller/elliptic-factorial function;
3. evaluate the best known index-system or square-root-Velu representation;
4. determine whether its all-in cost can fall strictly below `sqrt(n)`;
5. reject any representation that merely rebuilds all `(n-1)/2` branch choices.

The central task remains `UNIFORM-ORIENTED-ROOT-CIRCUIT-056`.