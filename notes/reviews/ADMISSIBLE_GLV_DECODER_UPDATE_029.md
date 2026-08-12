# Admissible GLV Decoder Update after GLV-GAUSSIAN-PERIOD-CUT-029

Date: 2026-08-12

Status: **final object compression after synchronized packages 010, 027, 028 and 029**.

## 1. Exact collapse of the triple cut

Let

```text
z=chi_G(Q)=zeta_n^k,
eta_G(Q)=z+z^lambda+z^(lambda^2).
```

Using `1+lambda+lambda^2=0 mod n`, the cyclotomic triple product satisfies

```text
(1-z)(1-z^lambda)(1-z^(lambda^2))
  = conjugate(eta_G(Q))-eta_G(Q)
  = -2*i*Im(eta_G(Q)).
```

Hence the exact carry is

```text
g_G(Q)=-sign(Im eta_G(Q)).
```

The target is therefore not three individual phase evaluations.  It is the
orientation of one cubic Gaussian period relative to complex conjugation.

## 2. Exact but large state

The distinct periods are indexed by the cosets of

```text
C3={1,lambda,lambda^2}
```

inside `(Z/nZ)^*`.  Their number is `(n-1)/3`, and complex conjugation groups
them into `(n-1)/6` unordered pairs.

The invariant data

```text
T=eta+conjugate(eta),
N=eta*conjugate(eta),
Delta=T^2-4*N
```

determine the unordered pair but not the sign of

```text
A_G(Q)=eta_G(Q)-conjugate(eta_G(Q)).
```

The missing carry is exactly the square-root/orientation branch of `Delta`.
This is the same cardinality as the generator-oriented half-kernel quotient.

## 3. Final synchronized constructive question

```text
PERIOD-ORIENTATION-RESOLVENT
```

> Does there exist a uniform public evaluator
>
> ```text
> D(E,G,phi,Q)=sign(A_G(Q))=g_G(Q)
> ```
>
> with all-in time, memory, preprocessing, advice and precision
> `O(n^(1/2-epsilon))`, which does not construct `eta_G(Q)`, `mu_n`, the
> degree-`(n-1)/3` period field, the `(n-1)/6` conjugate-pair table, or an
> equivalent generator-oriented half-kernel partition?

An equivalent positive object may output `R3_G(Q)` or the quotient label
`h_G(x(Q)^3)`, because these are publicly interconvertible with `g_G(Q)`.

## 4. First theorem-sized search class

The first admitted class is a bounded-rank, generator-sensitive,
conjugation-anti-invariant theta/net/sigma resolvent `F_G(Q)` satisfying

```text
F_G(Q)=U_G(Q)*A_G(Q),
```

where `U_G(Q)` is a publicly computable nonzero factor with a proved branch and
sub-square-root total cost.

Required rejection tests:

1. if `F_G` is conjugation invariant, it cannot choose the orientation;
2. if its anti-invariant part is a faithful order-`n` dual character, it
   returns to package 028 and is not compressed;
3. if its coefficients or advice encode `(n-1)/6` labels, it is interpolation;
4. if it is generator-blind, package 027 rules it out;
5. if it is an ordinary small rational quotient character, package 010 already
   supplies the first bounded negative gate.

## 5. Current existence answer

```text
exact carry function                                          exists
exact half-kernel representation                              exists
exact full-phase / Gaussian-period orientation representation exists
known admissible sub-sqrt orientation evaluator               absent
universal non-generic impossibility theorem                   absent
purely generic sub-sqrt evaluator                             excluded
```

Thus the remaining program is no longer a search for a bit, residue, phase or
normalization.  It is a compression problem for one exact conjugation-
orientation functional.
