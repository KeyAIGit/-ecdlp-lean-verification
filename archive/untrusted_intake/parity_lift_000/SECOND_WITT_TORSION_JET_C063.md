# SECOND-WITT-TORSION-JET-C063

Date: 2026-08-13

Status: **the canonical prime-to-p torsion lift was extended to p^3 and its second intrinsic Witt/logarithmic digits were extracted. They are exact public polylogarithmic C6-invariants, but the declared exact quadratic-character gates and full additive phases again show no decoder or heavy spectrum on the frozen medium corpus.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Iterated torsion Hensel lift

Starting from the unique torsion lift modulo `p^r`, lift an affine coordinate by

```text
x -> x+p^r s
```

and solve the curve equation uniquely for `y`. The normalized formal parameter of `[n]P` modulo `p^(r+1)` is affine in `s`; since `n` is a p-adic unit, one Newton step gives the unique torsion lift modulo `p^(r+1)`.

Thus the lift to any fixed precision `p^r` costs

```text
O(r log n)
```

ring arithmetic. C063 uses `r=3`.

## 2. Second intrinsic digits

Write

```text
x_tor/omega(x)=1+p*x1+p^2*x2 mod p^3,
y_tor/omega(y)=1+p*y1+p^2*y2 mod p^3.             (W1)
```

The first digits `x1,y1` are C060. The normalized second logarithmic digits are

```text
lx2=x2-x1^2/2 mod p,
ly2=y2-y1^2/2 mod p,                              (W2)
```

because

```text
p^(-1) log(1+p*x1+p^2*x2)
 =x1+p*(x2-x1^2/2) mod p^2.
```

All four raw digits and both logarithmic digits satisfy

```text
u(phi Q)=u(Q),
u(-Q)=u(Q).                       (W3)
```

They are exact functions on the six-orbit quotient.

## 3. Exact frozen screen

The declared features include

```text
x1,x2,y1,y2,lx2,ly2,
lx2+ly2,lx2-ly2,
x1*ly2-y1*lx2,
selected first/second-digit combinations,
1.
```

Every affine pencil, every field coefficient, and both global quadratic signs were checked against

```text
h_G(Q)=g_G(Q)chi_p(y(Q))
```

on the seven C060 medium groups.

```text
target-formula instances: 2,540,460
exact identities:         0
```

The full digit tuple separates all retained quotient points, but exact lookup from it has linear quotient size and is not a succinct decoder.

## 4. Full phase spectrum

The complete additive phases of `x2,y2,lx2,ly2` were evaluated on the two largest groups.

For `n=3469` and `n=4021`:

```text
maximum Fourier magnitude = O(1/sqrt(n)),
sqrt(n)*maximum           between about 2.32 and 3.28,
Fourier L1                about 51 to 57, i.e. sqrt(n)-scale.
```

No constant-heavy coefficient or inverse-polylogarithmic family appears in the declared second-digit signals.

## 5. Result

```text
Exact second p-adic/Witt observable        constructed
Evaluation cost                            O(log n) at fixed p^3 precision
New information beyond first digit         yes as a coordinate value
Exact declared carry quotient identity     absent
Heavy scalar Fourier spectrum              absent in frozen screen
Public scalar-recovery algorithm           absent
```

## 6. Strategic boundary

Blindly increasing p-adic precision now repeats the same pattern: each new digit is public and compact, but no structural transformation law links it to carry, and its phase behaves at square-root scale.

A further precision increase is admitted only after an exact arithmetic-differential identity predicts which Witt polynomial should isolate the generator-oriented branch.

## 7. Successor

The next nonredundant hypothesis is not `p^4`. It is

```text
FROBENIUS-DELTA-CHARACTER-SELECTOR-C064.
```

Construct the canonical ordinary arithmetic differential character associated with the lifted Frobenius/CM endomorphism, evaluate it on the Teichmuller section, and determine whether a nonlinear Frobenius eigencomponent predicts the required orientation or collapses to the already screened Witt digits.

## Claim boundary

Finite screens are not a secp256k1 impossibility theorem. No carry, hard-R3, parity, or scalar-recovery construction is obtained.
