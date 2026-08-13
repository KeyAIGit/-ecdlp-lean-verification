# NESTED-TWO-ADDITION-COORDINATE-041

Date: 2026-08-12

Status: **exact structured search of the first genuinely nested two-addition coordinate class; no carry executor identity found**.

No external point, public key, wallet, private scalar, or production-sized ECDLP target is accepted. The package is toy-only and does not claim a secp256k1 carry decoder or sub-square-root algorithm.

## 1. Exact target and nested class

Write

```text
z(Q)=x(Q)^3,
h_G(z(Q))=g_G(Q)*chi_p(y(Q)).
```

The function-level C6-invariant nested class is

```text
H(z)=1+c1*z^a,

F(z)=kappa*z^u*H(z)^epsilon
     *(1+c2*z^b*H(z)^t),
```

with

```text
u,epsilon in {0,1},
a,b,t mod p-1,
c1,c2 in F_p,
chi_p(kappa) in {+1,-1}.
```

The requested exact identity is

```text
chi_p(F(z(Q)))=h_G(z(Q))
```

on every quotient orbit, equivalently

```text
chi_p(y(Q)F(z(Q)))=g_G(Q)
```

on every nonzero subgroup point.

This class is genuinely nested: the second addition consumes the output of the first through `H^t`. It contains sparse trinomials, binomial-times-trinomial square classes, and high-degree expressions whose exponents have short addition chains.

A second exact screen retains character-only symmetry exceptions by testing

```text
H(Q)=1+c1*x(Q)^a*y(Q)^b,

F(Q)=kappa*x(Q)^u*y(Q)^v*H(Q)^epsilon
     *(1+c2*x(Q)^r*y(Q)^s*H(Q)^t)
```

directly against carry on all nonzero subgroup points, without assuming that the intermediate functions themselves descend to the C6 quotient.

## 2. Exact search method

For fixed `(a,c1,t,b)`, all `c2 in F_p` are tested simultaneously.

For each point and desired sign, the allowed `c2` values are represented by a Python integer bitset:

```text
{c2 : chi_p(1+c2*W(Q))=desired_sign}.
```

Intersecting these masks over all points is exact. No sampling, floating-point score, statistical threshold, or learned model is used.

Every retained formula is also checked for totality: a zero in `H` or the final additive factor is rejected.

## 3. Quotient-symmetric results

### `(p,n)=(1087,271)`, full structured profile

```text
a,b:             54 public structured exponents
c1:              43 public structured constants
t:               all 53 nonzero structured exponents
c2:              all 1,087 field elements
outside classes: 8
admissible W:    6,167,610
nominal formulas 53,633,536,560
exact decoders:  0
```

The exponent corpus includes small signed exponents, powers of two, divisors of `p-1`, and public `n`/GLV-derived values. The constant corpus includes small signed constants, the curve coefficient, CM constants, generator coordinates, and their public inverses.

### `(p,n)=(1087,271)`, all-first-constant profile

```text
a,b:             every integer from -8 through 8
c1:              all 1,087 field elements
t:               -1,1,2,3,4,5,7,8,16
c2:              all 1,087 field elements
outside classes: 8
admissible W:    2,716,821
nominal formulas 23,625,475,416
exact decoders:  0
```

### Additional medium profiles

```text
(p,n)=(1663,433):
  nominal formulas 13,558,665,168
  exact decoders   0

(p,n)=(907,967):
  nominal formulas 6,499,184,688
  exact decoders   0
```

Total quotient-symmetric search:

```text
nominal exact formula evaluations: 97,316,861,832
exact decoders:                    0
```

## 4. Character-only exceptional branch

The nonquotient screen tests monomials in both `x` and `y`, allowing the final quadratic character to have the correct GLV/negation law even when the intermediate rational functions do not.

### `(p,n)=(1087,271)`

```text
a,b,r,s:         -4 through 4
monomials:       81 for each additive stage
c1:              43 structured constants
t:               -1,1,2,3,4,5,7,8,16
c2:              all 1,087 field elements
outside classes: 16
admissible W:    2,153,466
nominal formulas 37,453,080,672
exact decoders:  0
```

### `(p,n)=(1663,433)`

```text
a,b,r,s:         -3 through 3
monomials:       49 for each additive stage
c1:              43 structured constants
t:               -1,1,2,3,4,5,7,8,16
c2:              all 1,663 field elements
outside classes: 16
admissible W:    802,179
nominal formulas 21,344,378,832
exact decoders:  0
```

## 5. Aggregate result

```text
nominal exact formula evaluations: 156,114,321,336
exact carry decoders:              0
```

No first executor identity was found in the declared nested profiles.

This is a bounded structured negative result, not a theorem against every pair of exponents and constants and not a secp256k1 impossibility result. In particular it does not exclude:

```text
a secp256k1-specific exceptional constant;
arbitrary full-range exponents in the nonquotient branch;
three or more genuinely coupled additive innovations;
theta, p-adic, analytic, pairing, or EDS inputs not expressible as coordinate monomials.
```

## 6. A natural third-addition trap

The most obvious GLV-orbit product of one monomial does not create a new class.

For `M(phi Q)=beta^a M(Q)` and `beta^2+beta+1=0`,

```text
product_(j=0..2) (1+c*beta^(a*j)*M)
```

is either

```text
(1+c*M)^3
```

when `3|a`, or

```text
1+c^3*M^3
```

when `3` does not divide `a`.

Modulo squares, the first has the same class as the one-addition factor `1+cM`; the second is itself one addition. Therefore simply multiplying the three GLV translates returns to package 040 and is not the next executor class.

## 7. Next exact object

The next coordinate class should not be an arbitrary third addition. It must couple at least two distinct GLV weight components.

The theorem-first successor is

```text
MIXED-WEIGHT-GLV-RESOLVENT-042.
```

Central question:

> Can a generator-sensitive resolvent built from at least two distinct CM weight components produce an exact anti-Kummer carry square class, without collapsing to one-addition orbit norms, storing an orientation table, or importing a faithful dual character?

The first candidates should be exact low-rank determinants or resultants of two non-proportional mixed-weight sections. Pure monomial orbit determinants and same-feature orbit products must be algebraically reduced before any screen.

## 8. Reproducibility

- `nested_two_addition_coordinate.py` replays the quotient profiles.
- `nested_two_addition_exceptional.py` replays the direct character-symmetry profiles.
- `nested_two_addition_coordinate_results.json` freezes the counts above.

No broad random or ML search is part of this package.
