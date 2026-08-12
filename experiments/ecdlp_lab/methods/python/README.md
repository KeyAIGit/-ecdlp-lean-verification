# Python reference DLP methods

This directory contains the P03 engineering baselines for `ECDLP-LAB-001`.

## Scope

- digest-authorized synthetic groups only;
- subgroup order below `2^32`;
- no interval promise, target secret, wallet material, or secp256k1-sized group;
- no scientific outcome, route effect, or Research Engine write.

## Methods

### `bsgs_v1`

A cold-start baby-step giant-step implementation. It records reusable offline
baby-table construction, online target work, table entries, a separately
labelled `64 * entries` historical memory estimate, and method self-check work
outside the legacy P1 count.

### `ordinary_rho_xmod3_v1`

The frozen historical ordinary Pollard-rho walk:

```text
partition: infinity -> 0, finite point -> x mod 3
0: X <- X + G
1: X <- 2X
2: X <- X + Q
cycle detection: Floyd
four SHA-256-derived restarts
8*ceil(sqrt(order)) loop iterations per restart
```

Restarts, collisions, noninvertible collisions, state steps, and group-law
invocations are explicit.

## Independence

The methods delegate point arithmetic to the hash-frozen P1 producer adapter.
Every returned scalar is then checked through
`experiments/framework/ec_oracle.py`, an independently implemented affine
oracle that exposes validation but no DLP search.

## Historical replay

Run:

```bash
python3 -m experiments.ecdlp_lab.methods.python.legacy_replay
```

The replay authenticates the old runner, old result, and 40-curve catalog,
derives each target validation-side from the retained expected scalar, strips
that scalar from the method input, and requires exact agreement on both the
candidate and `legacy_p1_group_operations` for all 64 retained solver rows.
Historical wall times and memory figures remain descriptive; they are not
current telemetry.
