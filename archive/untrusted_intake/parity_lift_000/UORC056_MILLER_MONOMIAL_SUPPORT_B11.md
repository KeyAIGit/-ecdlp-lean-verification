# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — MILLER MONOMIAL SUPPORT B11

Date: 2026-08-14

Status: **the alternating Miller potential has nonzero divisor coefficient at every point of the prime-order kernel. A product or ratio of ordinary Miller and line-function atoms must therefore use linearly many atoms, even after multiplication by a quotient-invariant full-orbit divisor. This closes direct short Miller-monomial formulas for the oriented factor.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Frozen central target

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

Package B8 defines the alternating Miller potential `H_G`. For `n=2M+1`, its divisor coefficients on the kernel labels are

```text
label 0:                  -M,
label 1:                  M+1,
even nonzero labels:      -1,
odd labels other than 1:  +1.                    (B11.1)
```

Every one of the `n` coefficients is nonzero.

## 2. Support of standard Miller atoms

An ordinary Miller function has divisor

```text
div(f_(m,R))=m(R)-([m]R)-(m-1)(O),               (B11.2)
```

with support at no more than three points.

A line quotient has divisor

```text
div(g_(R,S))=(R)+(S)-(R+S)-(O),                  (B11.3)
```

with support at no more than four points.

Therefore a product or ratio of `r` ordinary Miller/line atoms has divisor support at most

```text
4r.                                               (B11.4)
```

Before any quotient-invariant correction, representing `H_G` in this class requires

```text
r >= ceil(n/4).                                   (B11.5)
```

## 3. Quotient-invariant corrections do not make the representation short

A divisor pulled back from the quotient `E/H` has constant coefficient along each full `H`-orbit. On the rational kernel orbit this changes every coefficient in `(B11.1)` by one common integer `c`.

The coefficient `-1` occurs `M` times, `+1` occurs `M-1` times, and the two exceptional coefficients occur once each. Hence for every integer `c`, at most `M` coefficients can be cancelled.

Thus

```text
boxed:
#supp(div(H_G)-c sum_(T in H)(T)) >= M+1.         (B11.6)
```

A Miller/line monomial after any such quotient correction still requires

```text
boxed:
r >= ceil((M+1)/4).                              (B11.7)
```

For secp256k1 this is

```text
r >= 14474011154664524427946373126085988481604695534884363047825645392689770186793,
```

which has 253 bits.

## 4. Meaning of the bound

This explains why B8's compact norm can use only three ordinary Miller functions while the oriented factor itself cannot. The norm adds the negated divisor and cancels all dense alternating coefficients. The branch-sensitive factor retains them.

The result closes formulas of the form

```text
quotient pullback * product_(i=1)^r f_(m_i,R_i)^e_i
                         * product_(j=1)^s g_(A_j,B_j)^d_j
```

when the number of atoms is sublinear and no high-degree pullback/composition is hidden inside an atom.

It does not rule out a division-polynomial-style short circuit whose one atom already has a dense zero divisor, a cyclic elliptic factorial, or an endpoint-only nonlinear recurrence.

## 5. Frozen exact replay

`uorc056_miller_monomial_support.py` uses the ten frozen prime orders from B4-B10. It verifies:

1. the exact coefficient pattern `(B11.1)`;
2. support size `n`;
3. the minimum support after every relevant constant full-orbit shift is `M+1`;
4. the exact atom lower bounds `ceil(n/4)` and `ceil((M+1)/4)`.

No curve point or unknown scalar is evaluated.

## 6. Formalization boundary

`Ecdlp/Proved/MillerMonomialSupportBoundary.lean` kernel-checks the arithmetic implication

```text
support <= 4r,
M+1 <= support
=>
M+1 <= 4r.
```

It does not formalize divisors, Miller functions, quotient pullbacks, elliptic curves, secp256k1, parity recovery, or ECDLP.

## 7. Answer for this B-track class

```text
Support of div(H_G)                                      n
Minimum after full-orbit constant correction            M+1
Support per ordinary Miller/line atom                    at most 4
secp minimum number of direct atoms                      253-bit integer above
Does a short ordinary Miller monomial represent H_G?    no
Public parity / absolute EDS oracle                      absent
Sub-square-root ECDLP                                    absent
```

## 8. Remaining nonlinear candidate

The surviving B-specific candidate is no longer an ordinary Miller monomial. It is the alternating sigma product itself, viewed as a finite elliptic shifted factorial or cyclic elliptic-dilogarithm-type solution of the two-step difference equation.

A positive result must give an exact base-field evaluator for that object without expanding its `M` factors, importing a full order-`n` character, or storing a state of square-root size.
