# ML-P1E toy scaling qualification

This package is a route-neutral engineering calibration, not a native Research
Engine candidate or outcome. It leaves the frozen P0 secp256k1 assay unchanged.

The main ladder changes the field and group size together. It does not keep
secp256k1 and merely restrict the secret interval. Every catalog curve has the
form

```text
y^2 = x^3 + 7 over F_p
```

with `p mod 12 = 7`, prime group order, cofactor one, a non-anomalous order,
embedding degree greater than 100, and a checked j=0 GLV eigenpair. Thus a
`b`-bit rung has about `b+1` informative compressed public bits and about `2b`
affine coordinate bits.

The authorized R2 ladder is 13, 16, 20, and 24 bits. The first rung moved from
12 to 13 bits because the exact 12-bit `y^2=x^3+7` prime-order family cannot
supply ten curve instances disjoint from the retired catalog. The 28- and
32-bit rungs are
deferred. They require a new policy decision and an immutable,
mechanism-bearing candidate after a positive independently validated 24-bit
result.

## Catalog and blind boundary

Each rung contains ten independently generated curves:

- `c0-c2`: training curves;
- `c3-c6`: development curves;
- `c7-c9`: physically blind curves.

The current replacement catalog uses the committed domain separator
`output-lock-recovery-r2` and explicitly excludes all 40 field primes from the
invalidated catalog. The exclusion list is bound by SHA-256 in the
configuration and preregistration. The earlier blind shards are retired
because an output-path collision made their selection provenance invalid
before the independent validator ran. This is an incident-recovery boundary,
not a hyperparameter choice.

Each curve contains six derived generators. Indices `g0-g2` are the training
or reference-index role, `g3` is the development role, and `g4-g5` are blind.
On a new curve even `g0-g2` are new physical group elements; the historical
split name `new_curve_seen_generator` means a reference generator index, not a
point previously observed by the learner.

Raw records are stored in separate `development` and `blind` files for every
field size. Selection rejects any shard containing both scopes and records the
exact files it opened. The frozen recipe cannot authorize evaluation unless:

1. selection opened no blind shard;
2. every deliberate leak canary passed;
3. random-label, within-cluster permutation, opaque-label, curve/generator-only,
   and mismatched-Q controls stayed null;
4. the selection result, ledger, dataset manifest, catalog, configuration,
   source dependencies, and runtime versions match their frozen hashes.

The runner holds an exclusive lock for the complete output stage. Successful
ledgers are rebuilt from the exact in-memory attempt matrix, written through a
unique staging file, atomically replaced, and read back before their hash is
used. A separate validator must then recompute the selection matrix and be
committed before evaluation may open a blind shard.

## Leakage-resistant generator holdout

For a catalog base `G0`, every derived generator is `Gj=[rj]G0`. Dataset rows
use unique SHA-256 rejection-sampled canonical scalars `k` and disjoint
physical points `Q=[k]G0` across all splits. The target relative to `Gj` is

```text
d = k * inverse(rj) mod n
```

The multiplier `rj` is retained only for provenance and independent replay. It
is never a learner feature. Public model inputs contain `p`, `n`, `Gj`, and
`Q`; curve IDs, generator IDs, and `rj` are excluded.

The independent dataset validator reconstructs the exact ordered scalar sample
and scalar-to-split/generator allocation without importing the producer. By
default it also verifies `[d]G=Q` for every one of the roughly 1.1 million
records.

## Metrics and controls

The target is the complete `b`-bit scalar vector. A scalar is never represented
as one floating-point regression target.

Information gain is measured against the exact public baseline

```text
P(bit_j = 1 | d uniform in [1,n-1])
```

computed separately for each row from public group order `n`. This removes the
trivial gain available from learning group-order-dependent scalar marginals.
Intervals use whole curve/generator clusters and Student-t critical values.
The architecture search is included in the family-wise correction.

Representations include compressed point bits, affine bits, and public GLV
constants. The opaque control uses deterministic 64-bit SHA-256 labels for each
point; it is a high-entropy representation control, not an algebraic feature.

The preregistered CPU matrix has 14 architectures and seven seeds:

- 196 screen fits at 13 and 16 bits;
- seven unchanged 20-bit reference confirmations;
- sixteen pre-blind control fits;
- 28 frozen ladder fits, seven per size.

That is 247 attempted fits when all runs succeed. A passing 13/16 screen cannot
change the selected architecture at 20 bits. The 20-bit evaluation is a fixed
confirmation, and the recipe is committed before any blind shard is opened.

## What the ladder measures

The frozen architecture is retrained from scratch on training curves at each
field size and evaluated on held-out curves and generators at that same size.
This is a retrained scaling curve. It is not cross-size model extrapolation from
13-20 bits to 24 bits.

- `seen_curve_seen_generator`: new Q values on trained curve/generator clusters;
- `seen_curve_new_generator`: complete generator holdout on trained curves;
- `new_curve_seen_generator`: reference-index generators on held-out curves;
- `new_curve_new_generator`: development-index generators on held-out curves;
- `blind_curve_blind_generator`: untouched curves and generators, opened only
  after the recipe freeze.

A result surviving only the first split is classified as memorization or an
instance-specific representation effect.

## Reproduce

From the repository root, define paths appropriate for the local run and then:

```text
python experiments/ml_structure_probe/p1_toy_scaling/generate_curves.py \
  --config experiments/ml_structure_probe/p1_toy_scaling/config/p1_toy_scaling.json \
  --output experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json

python experiments/ml_structure_probe/p1_toy_scaling/validate_curves.py \
  --config experiments/ml_structure_probe/p1_toy_scaling/config/p1_toy_scaling.json \
  --catalog experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json \
  --output experiments/ml_structure_probe/reports/p1_toy_scaling/curve_validation.json

python experiments/ml_structure_probe/p1_toy_scaling/generate_dataset.py \
  --config experiments/ml_structure_probe/p1_toy_scaling/config/p1_toy_scaling.json \
  --catalog experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json \
  --output-dir experiments/ml_structure_probe/artifacts/p1_toy_scaling \
  --manifest experiments/ml_structure_probe/reports/p1_toy_scaling/dataset_manifest.json

python experiments/ml_structure_probe/p1_toy_scaling/validate_dataset.py \
  --config experiments/ml_structure_probe/p1_toy_scaling/config/p1_toy_scaling.json \
  --catalog experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json \
  --manifest experiments/ml_structure_probe/reports/p1_toy_scaling/dataset_manifest.json \
  --dataset-dir experiments/ml_structure_probe/artifacts/p1_toy_scaling \
  --output experiments/ml_structure_probe/reports/p1_toy_scaling/dataset_validation.json
```

First commit the source, configuration, and pending preregistration. Generate
the catalog only from that clean source commit. Then update
`preregistration.json` with the exact validated hashes, set its status to
`catalog_and_dataset_validated_selection_authorized`, and commit the catalog,
manifest, both validations, and authorized preregistration. The raw `.npy`
shards remain ignored. Selection refuses to run on a dirty tree or against an
unvalidated binding.

Run selection while the blind shards remain unopened:

```text
python experiments/ml_structure_probe/p1_toy_scaling/run_assay.py \
  --stage select \
  --config experiments/ml_structure_probe/p1_toy_scaling/config/p1_toy_scaling.json \
  --preregistration experiments/ml_structure_probe/p1_toy_scaling/preregistration.json \
  --catalog experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json \
  --manifest experiments/ml_structure_probe/reports/p1_toy_scaling/dataset_manifest.json \
  --curve-validation experiments/ml_structure_probe/reports/p1_toy_scaling/curve_validation.json \
  --dataset-validation experiments/ml_structure_probe/reports/p1_toy_scaling/dataset_validation.json \
  --dataset-dir experiments/ml_structure_probe/artifacts/p1_toy_scaling \
  --output-dir experiments/ml_structure_probe/reports/p1_toy_scaling
```

Commit `selection_result.json`, `selection_ledger.jsonl`, and
`frozen_assay_recipe.json`. From that clean commit, independently validate the
selection freeze without opening either raw shard:

```text
python experiments/ml_structure_probe/p1_toy_scaling/validate_selection.py \
  --config experiments/ml_structure_probe/p1_toy_scaling/config/p1_toy_scaling.json \
  --preregistration experiments/ml_structure_probe/p1_toy_scaling/preregistration.json \
  --catalog experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json \
  --manifest experiments/ml_structure_probe/reports/p1_toy_scaling/dataset_manifest.json \
  --curve-validation experiments/ml_structure_probe/reports/p1_toy_scaling/curve_validation.json \
  --dataset-validation experiments/ml_structure_probe/reports/p1_toy_scaling/dataset_validation.json \
  --selection-result experiments/ml_structure_probe/reports/p1_toy_scaling/selection_result.json \
  --selection-ledger experiments/ml_structure_probe/reports/p1_toy_scaling/selection_ledger.jsonl \
  --recipe experiments/ml_structure_probe/reports/p1_toy_scaling/frozen_assay_recipe.json \
  --output experiments/ml_structure_probe/reports/p1_toy_scaling/selection_validation.json
```

Commit the passing `selection_validation.json`. Only then run:

```text
python experiments/ml_structure_probe/p1_toy_scaling/run_assay.py \
  --stage evaluate \
  --config experiments/ml_structure_probe/p1_toy_scaling/config/p1_toy_scaling.json \
  --preregistration experiments/ml_structure_probe/p1_toy_scaling/preregistration.json \
  --catalog experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json \
  --manifest experiments/ml_structure_probe/reports/p1_toy_scaling/dataset_manifest.json \
  --curve-validation experiments/ml_structure_probe/reports/p1_toy_scaling/curve_validation.json \
  --dataset-validation experiments/ml_structure_probe/reports/p1_toy_scaling/dataset_validation.json \
  --dataset-dir experiments/ml_structure_probe/artifacts/p1_toy_scaling \
  --recipe experiments/ml_structure_probe/reports/p1_toy_scaling/frozen_assay_recipe.json \
  --selection-result experiments/ml_structure_probe/reports/p1_toy_scaling/selection_result.json \
  --selection-ledger experiments/ml_structure_probe/reports/p1_toy_scaling/selection_ledger.jsonl \
  --selection-validation experiments/ml_structure_probe/reports/p1_toy_scaling/selection_validation.json \
  --output-dir experiments/ml_structure_probe/reports/p1_toy_scaling \
  --raw-dir experiments/ml_structure_probe/artifacts/p1_toy_scaling/raw
```

Finally run `validate_results.py` against the raw frozen predictions and both
ledgers. Raw datasets and predictions stay ignored; compact catalogs,
manifests, ledgers, results, validations, and the report are retained.

## Claim boundary

Allowed conclusions are limited to the exact toy catalog, representations,
models, controls, and budgets. This package cannot register a native Engine
outcome, promote a route, make an asymptotic claim, or infer secp256k1
learnability. Model training is offline reusable work and is reported
separately from online inference and candidate verification.
