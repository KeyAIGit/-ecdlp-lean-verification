# ML-STRUCTURE-PROBE-FULL-KEY-AUTOML-V1-BLIND frozen blind evaluation

## Decision

- Pipeline status: `pass`
- Both blind halves crossed: `False`
- Interpretation: The frozen five-seed ensemble did not cross every preregistered threshold on both untouched blind halves. This is a bounded blind null for the recorded data, representation, model, and compute budget.

The five model seeds, feature representation, architecture, training budget, and thresholds were frozen before either blind split was loaded. One probability-averaging ensemble was evaluated unchanged on both halves. No blind metric was used for fitting or selection.

## Dataset separation

| role | dataset root SHA-256 | manifest SHA-256 | records used |
|---|---|---|---:|
| development | `81324f58ae00f4f3d33972a5dafa7cd27dc60fdc35f6f41866cafc3be0231e40` | `def4ff99c54f4611436c39e91ab09aa65de3673562c7e6a6538e075193ef8812` | 1,000,000 |
| development | `eb1a2f1301f211ef973f82d9d13b80cb469d6f115cc1869be48d2b8ea1605421` | `5c50fde3c82d093a703907f46602fe021a618b4759bff865f73ceabdd5b37d2e` | 1,000,000 |
| blind_a + blind_b | `fc3104ca99aac35cc6891c7dc4756e5e28637e423314191be37ab714638be95f` | `02b3e29c826b6e5005cd39f33dee5ebe009c0245f5cd45af46f1e46f4554a66f` | 1,000,000 |

## Frozen ensemble

- Recipe: `arch-076`
- Recipe SHA-256: `42dfa03ab24fb67152fe818f061ce0895d3e08c45034c5be70d005bafbc87299`
- Feature mode: `byte_popcounts`
- Family: `extra_trees`
- Seeds: `131, 173, 211, 257, 307`
- Actual fit records: `100,000`
- Models fitted: `5`
- Total fit time: `24.445` seconds

## Blind metrics

| half | records | info bits/key | info 95% low | bit lift | lift 95% low | paired z | mean Hamming | exact keys | threshold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| blind_a | 500,000 | -0.0015314739 | -0.0017159137 | -3.9742188e-05 | -0.0001226238 | -0.93981 | 128.004 | 0 | False |
| blind_b | 500,000 | -0.0016253061 | -0.0018095596 | -2.4765625e-06 | -8.5369206e-05 | -0.058557 | 128.009 | 0 | False |

## Frozen thresholds

| metric | minimum |
|---|---:|
| information gain, bits/key | 0.01 |
| bit accuracy lift | 0.001 |
| paired accuracy z | 5.0 |
| lower 95% CI, information gain | > 0 |
| lower 95% CI, bit accuracy lift | > 0 |

## Frozen recipe schema and value

Schema version 1 requires the exact recipe fields shown below. `development_splits` declares the ordered development pool and `train_records_per_manifest` is the total taken across it. `dev_records_per_manifest` records the search-time holdout size for provenance and is not counted twice. Exactly five unique ensemble seeds are required. The two blind portions are evaluation-only.

```json
{
  "architecture": {
    "family": "extra_trees",
    "feature_mode": "byte_popcounts",
    "id": "arch-076",
    "max_train_records": 100000,
    "params": {
      "max_depth": 6,
      "max_features": "sqrt",
      "min_samples_leaf": 256,
      "n_estimators": 16
    }
  },
  "blind_policy": {
    "fit_on_blind": false,
    "require_thresholds_on_both_halves": true,
    "required_splits": [
      "blind_a",
      "blind_b"
    ],
    "selection_on_blind": false,
    "single_ensemble_evaluation": true
  },
  "dev_records_per_manifest": 200000,
  "development_splits": [
    "train",
    "validation",
    "test"
  ],
  "ensemble_seeds": [
    131,
    173,
    211,
    257,
    307
  ],
  "experiment_id": "ML-STRUCTURE-PROBE-FULL-KEY-AUTOML-V1-BLIND",
  "feature_mode": "byte_popcounts",
  "feature_workers": 8,
  "frozen_from": {
    "ledger_sha256": "648e9dd3b1ba19a19e60be1d76e8a4789de1c175118b92099e167e38cb3eac9f",
    "search_config_sha256": "1cb241574df4ee31751c395a6872dec7f7f9c8f3197f1f7f330babf78d6f34d7",
    "search_result_sha256": "3aba659f33cfebcad6991c1d3a407f42b20ddcac33d4f5bd6e80bafc818878dc",
    "source_commit": "11af097743e23a048b8e81dbbe2292919d6245c1"
  },
  "jobs": 8,
  "prediction_batch_records": 10000,
  "recipe_id": "arch-076",
  "schema_version": 1,
  "scientific_evidence": false,
  "thresholds": {
    "minimum_bit_accuracy_lift": 0.001,
    "minimum_information_bits_per_key": 0.01,
    "minimum_paired_z": 5.0
  },
  "train_records_per_manifest": 1000000
}
```

## Scope

This is a bounded synthetic secp256k1 representation assay. A threshold crossing is not a discrete-log solution or a complexity claim. It requires independent leakage review, reproduction, and mechanism extraction before any research-route consideration.
