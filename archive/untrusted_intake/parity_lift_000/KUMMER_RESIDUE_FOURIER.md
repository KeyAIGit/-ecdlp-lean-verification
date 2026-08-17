# KUMMER-RESIDUE-FOURIER-001

Date: 2026-08-11

Status: **untrusted structural interpretation of frozen toy data**. This note
claims no asymptotic theorem and no ECDLP improvement.

## 1. Direct parity has a linear Fourier spike

For canonical scalar parity

```text
s(k)=(-1)^k,   0<=k<n,
```

on an odd cyclic order, the exact transform is

```text
S(j)=2/(1+exp(-2*pi*i*j/n)).
```

Every frequency is nonzero, and at `j=(n-1)/2` one has

```text
|S(j)| = 1/sin(pi/(2n)) ~ 2n/pi.
```

This linear-size coefficient drives the draft mixed-character conductor bound
in `CHAR_PARITY_001`: a low-conductor rational character trace cannot directly
be the canonical parity sequence.

## 2. The residual EDS bit is a different sequence

After EDS alignment,

```text
s(k) = chi(phi_raw([k]G)) * rho_G([k]G).
```

The public factor `chi(phi_raw([k]G))` is a high-degree but efficiently
recurrence-evaluable trace. It can carry the linear-size parity spike. Nothing
forces the residual sequence `rho_G` to retain that spike.

Therefore the direct-parity Fourier and conductor lower bounds cannot be copied
to `rho_G` without a new argument.

## 3. Frozen toy Fourier screen

`kummer_residue_toy_screen.py` sets `rho_G(O)=0` and computes the complete DFT on
the five frozen prime-order toy curves.

The maximum coefficient sizes are:

| p | n | max | max/sqrt(n) |
|---:|---:|---:|---:|
| 43 | 31 | 10.1987 | 1.8317 |
| 67 | 79 | 14.7490 | 1.6594 |
| 79 | 67 | 16.1328 | 1.9709 |
| 127 | 127 | 25.6372 | 2.2749 |
| 163 | 139 | 24.2937 | 2.0606 |

The maxima are square-root scale in this tiny fixture, not linear scale. On the
single Kummer-invariant curve, `F_127`, every Fourier coefficient is nonzero,
but the maximum is only about `2.275*sqrt(n)`.

These data are consistent with a pseudorandom or ordinary character-sum trace.
They do not prove such a bound for a growing family.

## 4. Consequence for the research hierarchy

The factorization has moved the parity problem into a more promising class:

```text
public high-complexity trace  x  hidden Kummer residue trace.
```

A low-degree or low-conductor candidate

```text
chi(f(x(Q))) = rho_G(Q)
```

is **not** excluded by the linear parity Fourier spike. Its mixed sums of size
`O(sqrt(p))` would be compatible with the toy observations.

This does not mean such an `f` exists. It means the previous no-go argument no
longer applies to the correctly isolated residual bit.

## 5. Highest-value next theorem

The next analytic question should be stated directly for the EDS residue trace:

> Across a growing secp-like family satisfying
> `chi(-1)*chi(phi_raw(G))=1`, what are the best upper and lower bounds for the
> cyclic Fourier coefficients of `rho_G([k]G)`?

A useful result would distinguish among:

1. bounded-conductor Kummer character traces;
2. high-conductor but short-recurrence traces;
3. genuinely scalar-indexed EDS complexity with no low-cost x-only
   representation.

The theorem must track both geometric conductor and evaluation-circuit cost;
conductor alone is not a runtime lower bound.

## 6. Claim boundary

The square-root-scale toy coefficients improve the choice of hypothesis. They
do not supply a decoder, predict secp256k1 coefficients, or constitute evidence
that ECDLP is easier than the generic square-root baseline.
