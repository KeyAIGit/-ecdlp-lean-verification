# UORC-056 CM threefold root decomposition V14

Date: 2026-08-14

Status: **exact normal form for the central oriented root. It isolates the already-known GLV carry and a four-state intra-orbit branch selector. Dense construction is still linear-size, so this is not yet the target evaluator.**

Central target:

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

## 1. Kernel and CM decomposition

For the frozen `j=0` family, with `alpha(x,y)=(beta*x,y)` and `n=1 mod 6`, the half-kernel x-set is a union of complete `C3` orbits. Hence

```text
K_H(X)=kappa(X^3),
deg kappa=(n-1)/6.                               (V14.1)
```

Writing `T=X^3`, every oriented root has a unique decomposition

```text
Y_G(X)=A(T)+X B(T)+X^2 C(T).                    (V14.2)
```

From `Y_G^2=X^3+7 mod K_H`, the three CM weights give exact equations in `F_p[T]/(kappa)`:

```text
A^2+2TBC=T+7,                                   (V14.3)
2AB+TC^2=0,                                     (V14.4)
B^2+2AC=0.                                      (V14.5)
```

## 2. Exact C3 projectors

For `Q=[k]G`, put

```text
s0=sigma(Q),
s1=sigma(alpha Q),
s2=sigma(alpha^2 Q).
```

Then

```text
3A/y=s0+s1+s2,                                  (V14.6)
3xB/y=s0+beta^2*s1+beta*s2,                     (V14.7)
3x^2C/y=s0+beta*s1+beta^2*s2.                   (V14.8)
```

Thus `A/xB/x^2C` are exactly the three `C3` Fourier modes of the parity triple.

Equation `(V14.6)` implies

```text
A/y in {+1,-1,+1/3,-1/3},
```

and therefore

```text
(A^2-(T+7)) (9A^2-(T+7))=0 mod kappa.           (V14.9)
```

In particular `A` never vanishes on the subgroup orbit.

## 3. Four-state branch selector

Define

```text
r(T)=B(T)/A(T),
u(Q)=x(Q)r(T).
```

Eliminating `C` from `(V14.4)` and `(V14.5)` gives

```text
r(T)(T r(T)^3+8)=0,                             (V14.10)
```

or denominator-free

```text
B(T)(T B(T)^3+8A(T)^3)=0 mod kappa.             (V14.11)
```

Exactly,

```text
u=0               iff all three signs agree;
u=-2              iff Q is the unique minority member;
u=-2*beta^2       iff alpha(Q) is the minority;
u=-2*beta         iff alpha^2(Q) is the minority.              (V14.12)
```

For every mixed orbit, `u^3=-8`.

## 4. Direct field-valued reconstruction

Since `(V14.5)` gives `C=-B^2/(2A)`, only `A` and `B` are independent. The central bit is reconstructed directly, without an outer quadratic character:

```text
sigma_G(Q)=
(2A(T)^2+2A(T)x(Q)B(T)-x(Q)^2B(T)^2)
/
(2y(Q)A(T)).                                     (V14.13)
```

Equivalently,

```text
sigma_G(Q)=A(T)/y(Q) * (1+u-u^2/2).             (V14.14)
```

## 5. Relation to the old R3/GLV-carry line

For canonical representatives

```text
k0=k,
k1=[lambda*k]_n,
k2=[lambda^2*k]_n,
k0+k1+k2=gamma*n,
gamma in {1,2},
```

we have

```text
s0*s1*s2=(-1)^gamma.                            (V14.15)
```

This is exactly the **already-known GLV carry sign**. V14 does not rename it as a new observable.

The new part is the exact decomposition of the central oriented root around that carry: `A/y` gives the invariant majority mode and `B/A` identifies the minority sector inside the `C3` orbit.

## 6. Exact replay and cost boundary

The committed replay verifies `(V14.1)`--`(V14.15)` on:

```text
5 curves,
438 oriented roots,
46,260 root/query evaluations.
```

Each of `A,B,C` has degree below `(n-1)/6`. Because `C` is determined by `A,B`, dense representation drops from roughly `3D` coefficients to `2D`, `D=(n-1)/6`.

This is still `Theta(n)` representation cost. The result is a structural reduction, not a sub-square-root algorithm.

## 7. New focused frontier

The central task is now split exactly into:

```text
A-mode: evaluate the invariant majority/carry component A(T)/y;
sector-mode: evaluate r(T)=B(T)/A(T), where x*r has four possible values.
```

A positive result must compute these without materializing `kappa,A,B`, storing an orbit branch table, or walking the subgroup. The next search should test whether either component has a compact Miller/CM/theta/transposed representation.

## Claim boundary

V14 is an exact algebraic normal form and one-third dense-representation reduction. The four-branch equation does not select the distinguished branch by itself; that selection remains the central bottleneck.
