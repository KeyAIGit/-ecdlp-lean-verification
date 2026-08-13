# GLV Decoder / ECDLP Complexity Equivalence

Date: 2026-08-12

Status: **complexity interpretation of the synchronized decoder contract**.

## Forward direction

Any algorithm that recovers the canonical scalar `k` from `Q=[k]G` can compute

```text
g_G(Q)=(-1)^gamma_G(Q)
```

with only polylogarithmic additional arithmetic.  Therefore a sub-square-root
ECDLP algorithm immediately gives a sub-square-root carry decoder.

## Reverse direction

The registered GLV carry reduction evaluates one fixed exact public decoder on
chosen multiples

```text
[t]Q=[t*k]G
```

to obtain

```text
t -> g_G([t]Q)=g(t*k mod n).
```

The scalar carry function has a constant-heavy additive Fourier spectrum.  In
the source-conditional local sparse-Fourier model already recorded in the
parity branch, these chosen-multiplier values recover a constant-size list
containing `k`, followed by public candidate verification.

Hence an exact reusable decoder with cost `T(n)` yields an ECDLP algorithm with
cost

```text
poly(log n) * T(n) + poly(log n)
```

under the stated local-SFT reduction and query model.

## Consequence

Within that model:

```text
polylog exact GLV decoder  <=>  polylog ECDLP algorithm,
sub-sqrt exact GLV decoder <=>  sub-sqrt ECDLP algorithm,
```

up to polynomial-logarithmic overhead in the decoder-to-ECDLP direction.

The equivalence is algorithmic, not representational.  A large lookup,
interpolation polynomial, half-kernel factor, or full order-`n` phase already
defines the bit exactly, but does not meet the all-in decoder cost contract.

Therefore the absence of a known admissible decoder is not a missing software
optimization.  Constructing one would be the substantive cryptanalytic
breakthrough for this line.

## Claim boundary

The reverse implication uses the explicitly recorded source-conditional local
sparse-Fourier theorem and exact reusable oracle assumptions.  A noisy decoder
requires a separate robustness theorem.  This note does not claim that such an
exact decoder exists and does not establish an unconditional lower bound.
