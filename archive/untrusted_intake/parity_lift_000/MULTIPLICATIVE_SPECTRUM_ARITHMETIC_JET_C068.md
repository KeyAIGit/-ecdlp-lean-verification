# MULTIPLICATIVE-SPECTRUM-ARITHMETIC-JET-C068

Date: 2026-08-13

Status: **the C060 canonical torsion-lift digit has no admitted heavy multiplicative Fourier signal on six independent frozen groups up to order 1,765,741. The apparent 0.1-scale coefficients on small groups follow the matched random C6-quotient maximum and shrink as quotient-size inverse square root.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Why multiplicative Fourier is the correct new channel

Let

```text
u_G(k)=u_x([k]G),
```

where `u_x` is the exact canonical torsion-lift digit from C060. For an unknown

```text
Q=[k]G
```

and a public multiplier `t`,

```text
u_Q(t)=u_x([t]Q)=u_G(t*k mod n).                 (M1)
```

Choose a primitive root `r` modulo the prime subgroup order and write

```text
t=r^j,
k=r^s.
```

Then `(M1)` becomes a cyclic shift:

```text
u_Q(r^j)=u_G(r^(j+s)).                            (M2)
```

Therefore the multiplicative Fourier coefficients of any public phase of `u_x` acquire known frequency-dependent phases under the hidden scalar. A heavy coefficient would yield a sample-efficient scalar-recovery channel even though the additive scalar-domain spectrum in C061 is flat.

## 2. C6 quotient

The exact C060 symmetries give

```text
u_x(-Q)=u_x(Q),
nu_x(phi Q)=u_x(Q).
```

Hence the multiplicative-exponent sequence has period

```text
m=(n-1)/6.                                       (M3)
```

All spectra are computed on this quotient. The matched null permutes the observed quotient values, preserving their exact marginal distribution and C6 repetition.

## 3. Signals

Two complete public signal families are tested:

```text
f_a(k)=exp(2*pi*i*a*u_x([k]G)/p),
a in {1,2,3,5,7,11,13,17},

q(k)=chi_p(u_x([k]G)).                            (M4)
```

For the phase family, each null trial takes the maximum over all eight powers and every nonzero multiplicative frequency. This prevents selecting a favorable phase power after seeing the result.

## 4. Independent frozen cases

The six cases are exactly the independently frozen arithmetic cases from package 026:

```text
(p,n)=(14,919,511,   414,259),
      (28,468,039,   451,837),
      (54,919,927,   677,947),
      (48,468,247,   932,101),
      (14,113,051, 1,085,431),
      (49,435,999, 1,765,741).
```

For each case the unique `n`-torsion lift of `G` modulo `p^2` is computed once. The homomorphic torsion lift then enumerates all `[k]G` by repeated addition, and projective coordinates are converted with batched inversion. This gives the complete exact `u_x` sequence in linear group-enumeration time without solving any unknown-target discrete logarithm.

## 5. Matched-null results

Each case uses 32 random permutations of the observed C6-quotient values.

Summary, sorted by `n`:

```text
n          best phase max   phase null-95%  chi max     chi null-95%
414259     0.01389047       0.01498058      0.01186444  0.01417656
451837     0.01346377       0.01448572      0.01219240  0.01299904
677947     0.01062894       0.01248583      0.01013955  0.01131842
932101     0.00933409       0.01065702      0.00830032  0.00939533
1085431    0.00988296       0.00972926      0.00903749  0.00884586
1765741    0.00677179       0.00778306      0.00629839  0.00742716
```

Aggregate gate:

```text
phase-family null-99 exceedances:       0 / 6
quadratic-character null-99 exceedances:1 / 6
largest two phase above null-95:         no
largest two chi above null-95:           no
any phase reaching 1/log(n):             no
admitted phase signal:                   false
admitted quadratic signal:               false
```

The isolated exceedance on `n=1,085,431` is not repeated on the largest case and fails the frozen cross-case gate.

On the largest case,

```text
sqrt(m)*best phase maximum = 3.6736,
sqrt(m)*chi maximum        = 3.4168,
```

which is the scale of the maximum of a random length-`m` spectrum, not a constant-heavy or inverse-polylogarithmic coefficient.

## 6. Result

```text
Exact public arithmetic-jet sequence             available
Multiplicative hidden-scalar shift law            exact
Complete C6 quotient spectrum                     evaluated
Heavy phase coefficient                           absent under matched gate
Heavy quadratic-character coefficient             absent under matched gate
Sample-efficient multiplicative recovery channel absent
Public carry, hard-R3, or scalar recovery         absent
```

## 7. Strategic conclusion

C060 remains a genuinely new compact public arithmetic coordinate, but both of its natural spectral uses are now bounded negatively:

```text
additive scalar-domain spectrum       square-root scale,
multiplicative exponent-domain spectrum matched-random scale.
```

Blindly testing more fixed phase powers is not a new mechanism. A successor must explain an exact nonlinear transformation that changes the spectral scale or uses the arithmetic lift in a structurally different way.

## 8. Successor

The next independent object is

```text
ARITHMETIC-LIFT-TRACE-COLLISION-C069.
```

Rather than Fourier-analyzing one digit, it asks whether the full canonical lift modulo `p^2` admits a low-degree public trace/norm relation under two independent scalar pullbacks whose collision equation eliminates the random-looking digit and leaves the GLV carry. The first pass must derive an exact resultant or trace identity before any search.

## Claim boundary

A failed frozen spectral gate is not a lower bound against arbitrary nonlinear arithmetic-jet algorithms. No production target or secp256k1 scalar recovery is claimed.
