# ANTI-FROBENIUS-ORIENTATION-SEED-031

Date: 2026-08-12

Status: **exact classification of anti-Frobenius seeds and canonical normalized resolvent; no public sub-square-root evaluator obtained**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Anti-invariant line

Let

```text
K=F_(p^d),
K0=F_(p^(d/2)),
sigma(x)=x^(p^(d/2)).
```

On the secp256k1 cyclotomic realization, `sigma` is an involution and acts on the Gaussian-period resolvent by

```text
sigma(A_G(Q))=-A_G(Q),
A_G(Q)=eta_G(Q)-conjugate(eta_G(Q)).
```

Define

```text
V_minus={x in K : sigma(x)=-x}.
```

If `tau` is any nonzero member of `V_minus`, then every `x` in `V_minus` satisfies

```text
sigma(x/tau)=(-x)/(-tau)=x/tau.
```

Hence

```text
x/tau in K0,
x=(x/tau)tau.
```

Conversely, multiplying `tau` by any element of `K0` remains anti-invariant. Therefore `V_minus` is a one-dimensional vector space over `K0`.

This classifies all anti-Frobenius orientation seeds: they differ only by a fixed-subfield scalar. The difficulty is not existence of a seed, but a canonical generator-sensitive normalization of that line.

## 2. Canonical first seed

The most direct generator-sensitive choice is

```text
tau_G=A_G(G).
```

It gives the normalized period-orientation resolvent

```text
U_G(Q)=A_G(Q)/A_G(G).
```

Properties:

```text
U_G(G)=1;
sigma(U_G(Q))=U_G(Q);
U_G(phi Q)=U_G(Q);
U_G(-Q)=-U_G(Q).
```

Under the fixed complex embedding used to define the cyclotomic carry sign,

```text
g_G(Q)=g_G(G) sign(U_G(Q)).
```

Thus `U_G` is an exact normalized carry observable. It removes the arbitrary anti-Frobenius scale by anchoring at the public generator.

## 3. Why this is not yet an algorithm

Both numerator and denominator require the order-`n` dual phase. Writing

```text
z=zeta_n^k
```

gives

```text
U_G([k]G)=
  [z^k+z^(lambda*k)+z^(lambda^2*k)
   -z^(-k)-z^(-lambda*k)-z^(-lambda^2*k)]
  /
  [z+z^lambda+z^(lambda^2)
   -z^(-1)-z^(-lambda)-z^(-lambda^2)].
```

The normalization cancels the common anti-Frobenius line but does not supply a public map from `Q` to the numerator.

Under a cyclotomic Galois automorphism indexed by `a`,

```text
U_k -> A_(a*k)/A_a.
```

The subgroup `plus_or_minus C3` fixes the normalized family. The natural explicit state space therefore remains the quotient

```text
(Z/nZ)^*/(plus_or_minus C3)
```

of size `(n-1)/6`, matching the Gaussian-period conjugate-pair count and the half-kernel degree.

The package records this as a representation-size barrier, not a proof that every circuit evaluating `U_G` must have that size.

## 4. Generator change

For

```text
G'=[u]G,
Q=[k]G,
```

the normalized observable obeys

```text
U_[uG](Q)=U_G([u^(-1)]Q)
```

when each generator uses the character normalization sending its own generator to the chosen primitive phase.

In particular,

```text
U_[-G](Q)=U_G(-Q)=-U_G(Q).
```

Thus the normalization remains genuinely generator-sensitive. A kernel-only construction cannot produce it, in agreement with package 027.

## 5. Exact recurrence when the scalar is known

Let

```text
r1=z,
r2=z^lambda,
r3=z^(lambda^2),
r1*r2*r3=1,
s=r1+r2+r3,
t=r1^(-1)+r2^(-1)+r3^(-1).
```

The power sums

```text
P_m=r1^m+r2^m+r3^m
```

obey the order-three recurrence

```text
P_(m+3)=s P_(m+2)-t P_(m+1)+P_m.
```

The numerator of `U_m` is `P_m-P_(-m)`. This gives a very short recurrence over the enormous period coefficient field.

It does not evaluate `U_G(Q)` from `Q` because the unknown recurrence index is exactly `k`, and the coefficients `s,t` already live in the large cyclotomic period field. It illustrates the remaining tradeoff:

```text
small recurrence order <-> enormous coefficient representation and unknown index.
```

## 6. Answer

```text
Are anti-Frobenius seeds classified?                    yes
Dimension over the fixed subfield                       one
Canonical first seed                                    A_G(G)
Exact normalized carry observable                       U_G(Q)=A_G(Q)/A_G(G)
Does normalization remove arbitrary anti-scale?         yes
Does it avoid the dual-character evaluation?            no
Explicit quotient-state count                           (n-1)/6
Public sub-sqrt evaluator                               absent
Public carry or hard-R3 decoder                         absent
Unconditional sub-sqrt ECDLP algorithm                  absent
```

## 7. Next object

The successor is

```text
NORMALIZED-PERIOD-BLACKBOX-032.
```

Central question:

> Can `U_G(Q)` be evaluated directly from `(E,G,Q)` through a bounded-rank theta/net/sigma identity, a compact CM correspondence, or a black-box recurrence with total time, memory, preprocessing, advice, and precision `O(n^(1/2-epsilon))`, without constructing the period field, evaluating a faithful order-`n` character, or traversing the unknown scalar index?

The theorem-first gates are:

1. classify all bounded-rank net/sigma expressions with the same generator-change covariance as `U_G`;
2. identify whether any such expression is not already a public point-function normalization or EDS-residue reformulation;
3. prove a direct evaluation identity or show that its normalization ratio is a faithful dual character;
4. count coefficient-field degree and advice size;
5. promote only an exact carry decoder with a literal recovery and cost theorem.

No new broad statistical search is admitted without an exact candidate identity.

## 8. Formalization boundary

`Ecdlp/Proved/AntiFrobeniusOrientationSeed.lean` formalizes the one-dimensional anti-invariant-line calculation for an involutive field automorphism.

The complex sign relation, cyclotomic Galois stabilizer, generator-change law, and recurrence interpretation remain explicit mathematical derivations outside the Lean core.
