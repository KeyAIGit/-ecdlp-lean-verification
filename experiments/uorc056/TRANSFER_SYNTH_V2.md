# UORC-056 transfer synthesis package 002

This package executes the next bounded stage after exact toy `Y_G` ground
truth.  It does not search for a different observable.  It asks whether a
single small symbolic sign circuit can evaluate the same central target on
several fields:

```text
Q=[k]G  ->  Y_G(x(Q))/y(Q)=(-1)^k.
```

## Why this stage is different from finite interpolation

The first bounded synthesizer rediscovered an exact weight-four formula on the
smallest field `p=43`, but that formula contained field-fitted constants and
became undefined on the remaining frozen curves.  Such a formula is a finite
interpolation seed, not evidence for a uniform evaluator.

`UORC-056-C-SYNTH-V2` therefore forbids field-specific fitted coefficients.
Every candidate is assembled from the same symbolic sources on every curve:

- coordinates of `Q`, `[2]Q`, `[3]Q`, and `[4]Q`;
- the two canonical cubic-CM transforms `beta*x(Q)` and `beta^2*x(Q)`;
- the doubling slope and the chord joining `Q` to `[2]Q`;
- constants `0`, `±1`, `±2`, `±7`, the canonical cube roots, and coordinates
  of `G`, `[2]G`, and `[3]G` where the grammar permits them;
- quadratic character and multiplication of at most four sign atoms.

An atom is rejected on a curve if it has a zero or pole at any nonidentity
subgroup point.  There is no free per-curve global sign.  A curve-dependent
phase is allowed only when it is itself produced by an admitted public
symbolic character atom.

## Exact searches

The executable performs four kinds of checks:

1. exact search on all five frozen curves at once;
2. exact search on the first three curves followed by unchanged evaluation on
   the two holdouts;
3. exact single-curve searches on the first three curves, to measure the gap
   between finite fit and transfer;
4. a deterministic near-miss diagnostic on all five curves.

Weights one and two are exhaustively searched.  Exact weights three and four
use a complete meet-in-the-middle semantic map.  The near-miss diagnostic is
complete through weight two and uses a declared deterministic beam at weights
three and four; it is never promoted to an exact claim.

## Reproduce

From the repository root:

```bash
PYTHONPATH=scripts python -m unittest -v \
  scripts/test_uorc056_transfer_synth_v2.py

python scripts/uorc056_transfer_synth_v2.py \
  --max-weight 4 \
  --beam-size 192 \
  --out /tmp/uorc056-transfer-v2.json
```

GitHub Actions runs the same commands and uploads the complete JSON evidence.

## Admission rule

A candidate may trigger symbolic lifting only when the identical formula is
exact and defined on the complete nonzero orbit of every admitted validation
curve.  Even a five-curve candidate remains only a transfer seed.  Promotion
would additionally require:

1. a symbolic identity rather than fixture equality;
2. a construction valid for a growing family of subgroup orders;
3. a complete preprocessing/advice/memory/representation/online cost proof;
4. independent CAS replay and formalization of the core identity;
5. no materialization of `Y_G` or an equivalent scalar-indexed table.

Failure closes only this finite grammar.  It does not prove a lower bound for
all arithmetic circuits.
