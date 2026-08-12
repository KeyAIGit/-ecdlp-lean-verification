# PARITY-LIFT-000

Status: **isolated, non-executable research fixture**.

This line asks whether the canonical scalar parity

```text
Q = [k]G  ->  k mod 2,  with 0 <= k < ord(G)
```

can be computed at total cost below the generic square-root baseline.

It is intentionally separate from active solver and relation-generation work.
It changes no Research Engine state, selects no route, targets no real key, and
authorizes no production-sized discrete-log run.

## Refined two-layer target

A canonical sign-sensitive coordinate lift by itself is not the breakthrough:
one can normalize ordinary projective coordinates chart by chart. The actual
unknown is an exact cheap decoder.

The current source alignment separates parity into

```text
(-1)^k = chi(phi_raw(Q)) * rho_G(Q),
Q=[k]G,
rho_G(Q)=chi(psi_k(G)).
```

On secp256k1 the first factor is a public sign-sensitive point function and the
second factor is the hidden EDS Residue bit. The current residual target is
therefore

```text
Given public (G,Q), compute rho_G(Q) below square-root cost.
```

The branch also records a source-level normalization discrepancy between the
raw point function with exponent `k^2` and the normalized perfectly periodic
EDS with exponent `k^2-1`. No claim silently identifies the two.

## Formal foundations

`Ecdlp/Proved/ScalarParity.lean` kernel-checks the four base results:

1. `scalarParity_neg`;
2. `scalarParity_not_factor_through_Kummer`;
3. `no_global_alternating_translation_observable`;
4. `parityOracle_recovers_dlog`.

`Ecdlp/Proved/EdsResidueBalance.lean` proves the fixed-index quadratic exponent
cancellation that blocks finite products or ratios of balanced transported EDS
observables from exposing the absolute residue bit by that mechanism alone.

## Reproducible bounded checks

### Odd cyclic arithmetic

```bash
cd experiments/parity_lift_000
python3 verify.py
```

`parity_lift_000_results.json` checks the arithmetic identities and full Fourier
support on frozen tiny odd orders.

### Direct character parity screens

```bash
python3 char_parity_toy_screen.py
python3 structured_char_parity_screen.py
```

These use only five frozen toy curves. They report scoped negatives for small
affine-line and fixed-index division-polynomial families, plus one explicitly
non-scaling finite interpolation example.

### Fixed-public secp256k1 EDS alignment

```bash
python3 verify_secp_eds_residue_bridge.py
```

This script accepts no external point or scalar. It checks only fixed public
parameters and fixed known scalars, distinguishing

```text
phi_raw([k]G)=phi_raw(G)^(k^2) W_G(k)
```

from

```text
W_tilde_G(k)=phi_raw([k]G)/phi_raw(G)
            =phi_raw(G)^(k^2-1) W_G(k).
```

An independent Sage or second-CAS replay remains required.

### Kummer-residue toy screen

```bash
python3 kummer_residue_toy_screen.py
```

The frozen result verifies the curve-dependent negation law

```text
rho_G(-Q)=chi(-1)*chi(phi_raw(G))*rho_G(Q).
```

Only one of the five frozen curves has a Kummer-invariant residue bit; on that
curve no product of at most four admissible `chi(x+c)` factors is exact. This is
a bounded negative, not an asymptotic lower bound.

## Claim boundary

The generated JSON artifacts are structural evidence only. They do not compute
an unknown-target EDS residue, construct a parity oracle, or establish an ECDLP
speedup.

The exploratory interpretation, closed mechanism classes, remaining
hypotheses, and proof obligations are quarantined under
`archive/untrusted_intake/parity_lift_000/` so the line cannot silently alter
canonical evidence or Research Engine state.
