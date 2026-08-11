# PARITY-LIFT-000

Status: **isolated, non-executable research draft**.

This line asks whether the canonical scalar parity

```text
Q = [k]G  ->  k mod 2,  with 0 <= k < ord(G)
```

can be computed through a sign-sensitive theta/phase representation at total
cost below the generic square-root baseline.

It is intentionally separate from the active theta/Jacobi solver-presentation
screen and the GLV/Semaev phase-elimination work. It changes no Research Engine
state, selects no attack route, targets no real key, and authorizes no
secp256k1 discrete-log run.

## Important correction

A canonical sign-sensitive coordinate lift by itself is not the breakthrough:
one can normalize ordinary projective coordinates chart by chart. The actual
object sought is a pair

```text
lift(G,Q) + decoder(lift(G,Q)) = parity(log_G(Q))
```

whose **combined** online cost is asymptotically or concretely below Pollard rho
and whose normalization does not hide a discrete logarithm, exponential table,
or secret-length walk.

## Frozen checks

`verify.py` validates, on odd cyclic toy groups and secp256k1 scalar arithmetic:

1. `scalarParity_neg`;
2. `scalarParity_not_factor_through_Kummer`;
3. `no_global_alternating_translation_observable`;
4. `parityOracle_recovers_dlog`;
5. full Fourier support of the canonical parity sequence.

Run:

```bash
cd experiments/parity_lift_000
python3 verify.py
python3 -m py_compile verify.py
```

The generated `parity_lift_000_results.json` is structural evidence only. It
proves no parity oracle exists and makes no ECDLP speedup claim.

The mathematical interpretation, exact mechanism classes closed, remaining
hypothesis, and proof obligations are recorded in
`notes/PARITY_LIFT_000.md`.
