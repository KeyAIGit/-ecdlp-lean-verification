# MULTIPLICATIVE-SPECTRUM-ARITHMETIC-JET-C068-C071

Date: 2026-08-13

Status: **the canonical torsion-lift digit has no admitted first-order, higher-order, or higher-residue multiplicative spectral signal on frozen groups up to order 1,765,741. One borderline order-13441 event failed a separately frozen seven-curve replay.**

No external point, private key, wallet, or production-sized target is accepted.

## 1. Exact shift model

Let

```text
u_G(k)=u_x([k]G),
```

where `u_x` is the exact canonical torsion-lift digit. For a public multiplier `t` and `Q=[k]G`,

```text
u_Q(t)=u_G(t*k mod n).
```

After choosing a primitive root modulo `n`, multiplication by `k` becomes a cyclic shift in the multiplicative exponent coordinate. The exact C6 symmetries reduce the period to

```text
m=(n-1)/6.
```

## 2. C068 first-order spectra

Signals:

```text
exp(2*pi*i*a*u_x/p), a=1,2,3,5,7,11,13,17,
chi_p(u_x).
```

Six independent frozen groups were checked:

```text
n=414259,451837,677947,932101,1085431,1765741.
```

The matched null permutes the observed C6-quotient values. For the phase family it takes the maximum over all eight powers and all nonzero frequencies.

```text
phase null-99 exceedances:       0/6
quadratic null-99 exceedances:   1/6
largest two above null-95:       no for both families
any phase reaching 1/log(n):     no
```

Largest case:

```text
best phase maximum  0.00677179, null-95 0.00778306
chi maximum         0.00629839, null-95 0.00742716
```

The exact enumerator and frozen spectrum workflow are stored beside this note.

## 3. C069 higher-order phase test

A flat ordinary spectrum can hide a low-degree polynomial phase. Second phase derivatives, diagonal third derivatives, and a sampled U3 cube average were therefore checked on the three largest retained cases.

```text
n=932101:  best second derivative 0.0071641, null max 0.0074237
n=1085431: best second derivative 0.0065895, null max 0.0061737
n=1765741: best second derivative 0.0041373, null max 0.0050003
```

The isolated middle-case exceedance is absent at the largest order. Third derivatives are smaller and the sampled cube averages remain at Monte-Carlo noise scale.

## 4. C070 higher residue characters

Field-character phases of orders `3`, `6`, and `13441` were tested. The order-13441 family used powers

```text
1,2,3,5,7,11,13,17.
```

Five of six cases remain below the family-wise null. The largest case produced one borderline order-13441, power-7 maximum:

```text
observed 0.00807052
16-trial null maximum 0.00789890
sqrt(m)-scaled value 4.3781
```

This one candidate was frozen without changing order, power, sign, or threshold.

## 5. C071 independent fixed-candidate replay

The preselected order-13441, power-7 character was replayed on seven separate frozen cases:

```text
n=34231,52489,77689,82153,206197,549481,683737.
```

```text
null-95 exceedances: 0/7
null-99 exceedances: 0/7
largest two above null-95: no
```

Largest holdout:

```text
observed 0.00971685
null-95 0.01156177
null-99 0.01214901
```

The C070 borderline event does not replicate.

## 6. Decision

The following natural spectral uses of the canonical arithmetic digit now show matched-random scaling in frozen scope:

```text
additive scalar-domain phases,
multiplicative exponent-domain phases,
second and third multiplicative phase derivatives,
sampled U3 structure,
higher field-residue characters including order 13441.
```

This does not prove pseudorandomness and does not exclude every nonlinear arithmetic-lift construction. No production target or secp256k1 scalar computation is part of this package.
