# SECP-13441-CHARACTER-HELDOUT-022

Date: 2026-08-12

Status: exact secp256k1 field arithmetic plus negative rolling held-out toy screen.

No external point, key, wallet, or production-sized discrete-log target is
accepted.

## 1. Why the factor 13441 matters

The secp256k1 base-field prime satisfies the exact identity

```text
p - 1
  = 2 * 3 * 7 * 13441
    * 205115282021455665897114700593932402728804164701536103180137503955397371.
```

Thus an order-13441 multiplicative character exists already in the base field.
For the public perfectly-periodic point function `Phi`, define

```text
phase_13441(Q) = Phi(Q)^((p-1)/13441) in mu_13441.
```

The exponent `(p-1)/13441` is divisible by both `3` and `2`. Consequently the
phase is invariant under the public order-three field GLV multiplier and under
binary sign changes. It is therefore structurally compatible with a
GLV/Kummer-invariant carry observable.

## 2. Frozen family and admission protocol

The screen uses sixteen frozen prime-order subgroups on

```text
y^2 = x^3 + 7
```

in fields satisfying

```text
p = 3 mod 4,
p = 1 mod 3,
13441 divides p-1.
```

The largest frozen subgroup order is `683737`; the largest field prime is
`13145299`.

Training is always performed on smaller curves and testing on larger unseen
curves. Four rolling held-out curves are used for carry, and four rolling
held-out point-scale `s=-1` curves are used for hard-branch `R3`.

The tested inputs are the canonical phase exponent in `Z/13441Z`, optionally
combined with the public orientations

```text
half_y,
chi_y.
```

Five fixed lookup families are evaluated:

```text
raw 13441-entry lookup,
circular Fourier low-pass bandwidth 8,
bandwidth 32,
bandwidth 128,
bandwidth 512.
```

Low-pass variants prevent phase bins absent from the training curves from being
treated as automatic prediction failures.

A variant is admitted only if the same target, orientation, and lookup family:

```text
exceeds its matched null 95% envelope on at least three held-out curves,
and retains at least 2% advantage on both largest tests.
```

## 3. Result

The complete run contains:

```text
cases                                  16
carry held-out cases                    4
hard-R3 held-out cases                  4
evaluations                            60
isolated null-95% exceedances           5
admitted variants                       0
```

The five isolated exceedances are spread across different variants. Under an
idealized independent `5%` null, at least five exceedances among sixty tests
has probability about `0.18`; the actual tests are correlated, so this number
is only a scale reference, not a formal p-value.

The strongest repeated-looking variant was

```text
carry : half_y : lowpass_512.
```

It exceeded the individual null-95% envelope on two of four tests, but its
largest-order accuracy was only

```text
0.5030362596,
```

and its minimum advantage on the two largest tests was only

```text
0.0030362596.
```

This is far below the predeclared `0.02` requirement.

All other largest-order accuracies are approximately random. Representative
values are:

```text
carry : chi_y : raw             0.4978588227
carry : half_y : raw            0.4994910316
carry : half_y : lowpass_128    0.5006318228
R3 : raw                        0.4994120538
R3 : lowpass_128                0.5011758924
R3 : lowpass_512                0.5010618133
```

The raw lookup encountered as many as `741` phase bins unseen during carry
training and `4544` unseen bins during hard-R3 training. The low-pass variants
explicitly interpolate across those missing bins and still fail the admission
gate.

## 4. Interpretation

The negative result is stronger than a failed direct table because it also
rules out the tested smooth circular binary decoders at four increasing
Fourier bandwidths.

It does not show that the full order-13441 phase is useless. In particular, it
does not test:

```text
all complex-valued uses of the phase,
all 13440 nontrivial phase powers,
a secp256k1-specific non-universal table,
non-binary multivariate processing,
the remaining large cofactor of p-1.
```

For that reason the next package studies the full complex phase spectrum rather
than another binary lookup:

```text
SECP-13441-PHASE-SPECTRUM-023.
```

## 5. Formalized arithmetic core

`Ecdlp/Proved/Secp13441CharacterBoundary.lean` proves:

```text
13441 is prime,
13441 divides p-1,
the exact displayed factorization,
3 divides (p-1)/13441,
2 divides (p-1)/13441,
an order-three multiplier disappears after this exponent,
an order-two sign disappears after this exponent.
```

The remaining large cofactor is used only in the exact multiplication identity;
its primality is not needed by the Lean character argument.

## 6. Reproducibility

The computational package consists of:

```text
experiments/parity_lift_000/secp_13441_character_screen.py
experiments/parity_lift_000/secp_13441_character_runner.py
Ecdlp/Proved/Secp13441CharacterBoundary.lean
.github/workflows/secp-13441-character-screen.yml
```

The runner replaces the small trial-division helper with SymPy's
arbitrary-precision primality backend before executing the frozen screen.

## Claim boundary

The secp256k1 factorization, divisibility, and phase invariances are exact. The
lookup result is bounded held-out toy evidence against universal cross-curve
binary decoders. It is not an asymptotic lower bound and constructs no carry,
EDS-residue, parity, or ECDLP oracle.
