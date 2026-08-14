# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C18: odd polynomial GLV trace functional boundary

Date: 2026-08-14

Status: **for every nonzero odd polynomial `P`, the invariant `Theta_P=Tr_<phi>(P(Z_G))` is an exact odd selector of the remaining global branch and descends to `F_p(y)`. Nevertheless, on every nonexceptional type-2 GLV orbit it has an exact pole of order `deg(P)`, and on every nonexceptional type-3 orbit it vanishes. Hence its quotient divisor has support at least `(n-1)/6-4` and pole degree at least `(n-1)/12-2`. Arbitrarily high degree, additions, repeated squaring, and Newton power-sum recurrences do not create divisor collapse in this class. Odd rational functional calculus remains open.**

Only the public seven-curve extension corpus and public secp256k1 constants are used. No external unknown-scalar point, wallet, private key, or production target is accepted.

## 1. Setup

Let

```text
E: y^2=x^3+7,
H=<G>, |H|=n,
phi(x,y)=(beta*x,y),
phi([k]G)=[lambda*k]G,
lambda^2+lambda+1=0 mod n.
```

C15 isolates the endpoint gauge

```text
Z_G(P)=h_G(P)/h_G(P+G).
```

Its public adjacent products determine it only up to the global change `Z_G -> -Z_G`.

Write

```text
Z_i(P)=Z_G(phi^i(P)), i=0,1,2.
```

For a nonzero odd polynomial

```text
P(T)=sum_j c_j T^(2j+1),
```

let `D` and `L` be its actual largest and smallest nonzero degrees. Define

```text
Theta_P(P0)=sum_(i=0)^2 P(Z_i(P0))
           =Tr_<phi>(P(Z_G))(P0).                 (C18.1)
```

## 2. Exact transformation laws

The endomorphism `phi` cyclically permutes the three terms, so

```text
Theta_P(phi(P0))=Theta_P(P0).                    (C18.2)
```

Therefore

```text
Theta_P in F_p(E)^<phi>=F_p(y).                  (C18.3)
```

Since `P(-T)=-P(T)`, the global branch law is

```text
boxed:
Theta_P(-Z_G)=-Theta_P(Z_G).                     (C18.4)
```

Thus every nonzero member of the family is logically capable of selecting the unresolved branch.

## 3. Local valuation theorem

Outside at most four nonzero GLV orbits meeting the C15 correction support, the valuations of the three conjugates are parity signs in `{+1,-1}`.

### Type 2

Exactly one conjugate has valuation `-1` and two have valuation `+1`. On the pole branch, the highest term `c_D Z^D` has valuation `-D`. Every lower term on that branch has larger valuation, and all terms on the two zero branches have positive valuation. The leading term is unique, hence

```text
boxed:
ord(Theta_P)=-D.                                 (C18.5)
```

No additive cancellation is possible.

### Type 3

All three conjugates have valuation `+1`. Each `P(Z_i)` has valuation at least `L`, so their sum either vanishes locally or satisfies

```text
boxed:
ord(Theta_P)>=L>0.                               (C18.6)
```

Thus every nonexceptional type-3 quotient point is a zero of every nonzero `Theta_P`.

## 4. Uniform support bound

The `(n-1)/3` nonzero GLV orbits are paired by negation. Negation sends type `r` to type `3-r`, so if `N_r` is the number of type-`r` orbits,

```text
N_0=N_3,
N_1=N_2,
N_2+N_3=(n-1)/6.                                (C18.7)
```

At most four of these orbits meet the endpoint correction. Therefore every nonzero odd polynomial trace satisfies

```text
boxed:
#supp div(Theta_P) >= (n-1)/6-4.                 (C18.8)
```

On the quotient line `P^1_y`, zero and pole degrees agree. Hence

```text
boxed:
deg_poles(Theta_P) >= (n-1)/12-2.                (C18.9)
```

If a particular trace is identically zero, it is rejected as an evaluator before this divisor statement is needed.

For secp256k1 the exact bounds are

```text
quotient support >=
19298681539552699237261830834781317975472927379845817397100860523586360249052

pole degree >=
9649340769776349618630915417390658987736463689922908698550430261793180124526
```

The bit lengths are 254 and 253 respectively.

## 5. High-degree low-description recurrence

Let

```text
E1=Z_0+Z_1+Z_2,
E2=Z_0 Z_1+Z_1 Z_2+Z_2 Z_0,
E3=Z_0 Z_1 Z_2,
S_m=Z_0^m+Z_1^m+Z_2^m.
```

Newton identities give

```text
S_0=3,
S_1=E1,
S_2=E1^2-2E2,
S_m=E1*S_(m-1)-E2*S_(m-2)+E3*S_(m-3).           (C18.10)
```

Consequently `Theta_P=sum_m c_m S_m`. A high-index `S_m` has a short recurrence description once `E1,E2,E3` are already available. This does not compute those hard invariant inputs, and the local theorem shows that increasing `m` does not reduce divisor support.

C18 therefore covers an addition-enabled, arbitrarily high-degree polynomial functional class, not only bounded-degree formulas.

## 6. Closed and open classes

Closed in this package:

```text
Theta_P=Tr_<phi>(P(Z_G))
for every nonzero odd polynomial P,
including instance-dependent public coefficients with fully charged construction.
```

Not closed:

```text
odd rational R(T) with poles at T=0 or T=infinity;
nonlinear rational combinations of E1,E2,E3 outside polynomial trace;
transposed evaluation of the residue components C0,C1,C2;
unrestricted short nonlinear circuits in F_p(y).
```

The degree and support statements are not claimed as an unrestricted arithmetic-circuit lower bound.

## 7. Replay

The extension corpus is generated by the public rule:

```text
first seven ascending primes p congruent 1 mod 3
for which E:y^2=x^3+7 has prime order n congruent 1 mod 3.
```

It gives

```text
(p,n)=
(43,31),
(61,61),
(67,79),
(79,67),
(97,79),
(127,127),
(163,139).
```

The full replay checks

```text
7 curves and GLV eigenpairs,
28 nonlinear odd polynomial instances,
3584 Newton recurrence scalar identities,
495 endpoint orbit-valuation identities,
4 exact global rational-function controls over F_43,
GLV descent, odd covariance, type-2 poles, type-3 zeros, and all support bounds.
```

The global controls use

```text
T,
T^3+2T,
T^5+3T^3+5T,
T^7+3T^5+5T^3+7T.
```

All four have support on 27 of the 30 nonzero points in the `n=31` subgroup.

Two full executions are byte-identical. Full result SHA-256:

```text
d207bd1b3a68ec7ba46504045f8d142fabeb2a798ce9746da1a042809b6de30c
```

## 8. Answer

```text
Exact odd polynomial branch selector             yes
Arbitrary odd polynomial degree                  covered
Addition-enabled Newton formulas                 covered
Uniform quotient support lower bound             (n-1)/6-4
Uniform quotient pole-degree lower bound         (n-1)/12-2
Polynomial functional divisor collapse           absent
Odd rational functional calculus                 open
Strictly sub-square-root evaluator                absent
Parity oracle below square root                   absent
Sub-square-root ECDLP                             absent
```

## 9. Successor

The next package is

```text
ODD-RATIONAL-FUNCTIONAL-CALCULUS-069.
```

It must classify reduced odd rational functions `R(-T)=-R(T)` through the odd local orders `ord_0(R)` and `ord_infinity(R)`. The highest-value candidates are balanced families such as

```text
T/(1+cT^2),
T+c/T,
T*A(T^2)/B(T^2),
A(T^2)/(T*B(T^2)).
```

A positive result needs uniform symbolic cancellation and complete sub-square-root cost. Per-orbit coefficient fitting receives no credit.