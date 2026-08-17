# CHECKPOINT — GLV-NORMALIZATION-RIGIDITY-008

Date: 2026-08-11
Branch: `research/parity-lift-000`
Draft PR: `#365`

## Decision

Inside the scoped homogeneous quadratic-normalization category `C_quad`, no
odd-EDS-gauge section can have a C3 carry multiplier different from the
perfectly periodic point-function multiplier.

The arithmetic core is

```text
q(k)=a*k^2+b*k+c,
k0+k1+k2=gamma*n,
n odd,

sum_i q(ki) = (a+b)*gamma+c mod 2.
```

Therefore:

```text
a+b odd  -> the section carries gamma up to a fixed sign;
a+b even -> the section has even EDS gauge weight.
```

The order-three GLV eigenphase cannot supply a binary correction because
`z^3=1` implies `z=(z^2)^2`.

## Fixed-rank net closure

The integral-matrix net transformation gives, per source coordinate,

```text
v + (v^2-v*s) + v*s = v*(v+1),
```

which is always even. Thus increasing net rank does not create a new binary
normalization phase. The explicit rank-three `(1,1,1)` numerator vanishes on a
`j=0` GLV orbit because all three points share the same `y` coordinate.

## Weight-zero boundary check

The smallest direct-carry family

```text
chi(y(Q)),
chi(y(Q)*(x(Q)^3+a))
```

was screened on 15 frozen toy subgroups through order 4021 with 200 matched
anti-Kummer/C3-invariant controls per case.

```text
quadratic parity checks:               1,072,350
exact decoder at order >=271:                   0
cases strictly above matched 95% null:           0
```

Small exact matches at orders 19, 31, and 67 are classified as finite
resonances.

## Artifacts

- `Ecdlp/Proved/GlvNormalizationRigidity.lean`
- `archive/untrusted_intake/parity_lift_000/GLV_NORMALIZATION_RIGIDITY_008.md`
- `experiments/parity_lift_000/glv_normalization_rigidity_screen.py`
- `experiments/parity_lift_000/glv_normalization_rigidity_results.json`

## Remaining frontier

A successful construction must leave `C_quad`, for example through a
canonically trivialized mixed-weight section, genuinely global theta/sigma
monodromy, a public p-adic continuation, or a nonlocal order-dependent
weight-zero carry decoder.

Provisional successor: `GLOBAL-MONODROMY-SECTION-009`.
