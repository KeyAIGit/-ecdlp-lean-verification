# SECP-13441-PHASE-SPECTRUM-023

Date: 2026-08-12

Status: exact decimation identity plus negative matched-null full-phase spectrum.

No external point, key, wallet, or production-sized discrete-log target is
accepted.

## 1. Why the full phase is stronger than a binary lookup

For the public perfectly-periodic point function `Phi`, define

```text
f_G(k) = Phi([k]G)^((p-1)/13441) in mu_13441.
```

If `Q=[k]G`, then chosen-multiple queries satisfy the exact identity

```text
f_Q(t) = Phi([t]Q)^((p-1)/13441)
       = Phi([t*k]G)^((p-1)/13441)
       = f_G(t*k).                                   (1)
```

Thus the hidden multiplier acts by multiplicative decimation. With normalized
additive Fourier transform on `Z/nZ`,

```text
hat_f_Q(j) = hat_f_G(j*k^(-1)).                      (2)
```

A constant or inverse-polylogarithmic heavy coefficient of the full complex
phase could therefore support the same local sparse-Fourier strategy previously
proved for an exact carry oracle. This does not require choosing a binary
phase-to-carry lookup first.

## 2. Experiment

The same sixteen frozen toy subgroups from package 022 are used. Fifteen have
order at least `500`; the largest order is `683737`.

Eight deterministic nontrivial phase powers are tested:

```text
1, 2, 3, 5, 7, 11, 13, 17.
```

All are coprime to `13441`. For each curve and power the screen computes:

```text
the full normalized scalar-domain FFT,
the largest nonzero coefficient,
the complete Fourier L1 norm,
GLV-frequency orbit symmetry,
negation symmetry,
the exact hidden-decimation frequency permutation.
```

Each large curve is compared with twenty-four random phase functions that
preserve the same `C6` scalar-orbit symmetry. This matched null controls the
maximum over all scalar frequencies.

A phase power is admitted only if it:

```text
exceeds matched null 95% on at least three large curves,
and remains above 1/log(n)^2 on both largest subgroup orders.
```

## 3. Exact checks

The maximum numerical residuals were:

```text
GLV Fourier-orbit symmetry       9.96e-17
negation Fourier symmetry        8.33e-17
hidden-decimation identity       9.74e-17
```

These are floating-point FFT residuals for exact finite identities.

## 4. Spectral result

No tested power was admitted.

Across the fifteen large cases, the number of individual matched-null 95%
exceedances was:

```text
power 1     1
power 2     1
power 3     2
power 5     0
power 7     1
power 11    0
power 13    1
power 17    1
```

No power ever reached `1/log(n)` on a large case.

At the largest subgroup order `683737`, the matched random `C6` null-95%
maximum was

```text
0.0045704615.
```

The observed maxima were:

```text
power 1     0.0045104473
power 2     0.0043426648
power 3     0.0039133455
power 5     0.0041860094
power 7     0.0044414682
power 11    0.0042429551
power 13    0.0041587033
power 17    0.0046561017
```

Only power `17` is slightly above the individual null-95% value on this one
curve. It is not repeated across enough curves and does not satisfy the
largest-two inverse-log-squared condition.

Multiplying the maxima by `sqrt(n)` gives values between roughly `1.93` and
`3.85` over the large frozen family. At order `683737`, the eight values are
between approximately `3.24` and `3.85`. This is the scale expected from a
random-looking `C6`-invariant phase rather than a constant-heavy structured
signal.

The complete normalized Fourier `L1` norms on the two largest orders were
approximately:

```text
order 549481     656.4 to 657.2
order 683737     732.4 to 733.6.
```

They grow at square-root scale, not logarithmic scale.

## 5. Consequence

The order-13441 public phase has the exact algorithmically useful decimation
structure, but the eight tested deterministic powers do not have a heavy
additive Fourier spectrum. On the frozen family their extreme coefficients are
indistinguishable from matched random `C6` phases.

Therefore the direct route

```text
public full phase
  -> local sparse Fourier heavy-frequency recovery
  -> hidden multiplier
```

has no admitted signal for these powers.

## 6. What remains open

The result does not cover:

```text
all 13440 nontrivial phase powers,
optimized combinations of several powers,
nonlinear algorithms using the full phase distribution,
a secp256k1-specific learned circuit,
the remaining large cofactor of p-1,
proof of an asymptotic square-root bound for the growing-conductor Phi phase.
```

A particularly important remaining test is curve-specific learning. An
algorithm on secp256k1 may generate its own labeled known multiples, train on
that same curve, and apply the model to an unknown point. Cross-curve package
022 does not exclude this. The next package therefore uses within-curve
C6-orbit cross-validation:

```text
SECP-13441-WITHIN-CURVE-CV-024.
```

## 7. Formalized core

`Ecdlp/Proved/Secp13441PhaseSpectrumBoundary.lean` proves:

```text
chosen-multiple point-function queries are multiplicative decimations,
two decimations compose by multiplying hidden scalars,
fixed public phase powers preserve decimation,
the eight tested powers are coprime to 13441.
```

Lean does not formalize the FFT or the matched-null admission rule.

## 8. Artifacts

```text
experiments/parity_lift_000/secp_13441_phase_spectrum.py
Ecdlp/Proved/Secp13441PhaseSpectrumBoundary.lean
.github/workflows/secp-13441-phase-spectrum.yml
```

## Claim boundary

The query decimation and finite symmetry identities are exact. The spectral
conclusion is bounded toy evidence for eight deterministic powers, not an
asymptotic lower bound for all order-13441 phase algorithms.
