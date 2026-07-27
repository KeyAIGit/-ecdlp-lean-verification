# ML-STRUCTURE-PROBE-P0-AUTOML-1M-REPLICA AutoML qualification

This report is a route-neutral engineering observation. It is not a discrete-log solution, a complexity claim, or a Research Engine candidate.

## Outcome

- Pipeline status: `pass`
- Dataset records: `1,000,000`
- AutoML attempts completed: `3`
- AutoML attempts failed: `0`
- Controls pass: `True`
- Representation signals: `none`

## Method coverage

| family | feature modes | completed runs | failed runs |
|---|---|---:|---:|
| extra_trees | compressed_bytes | 1 | 0 |
| sgd_logistic | x_limbs16 | 2 | 0 |

## Adaptive selection

| task | round | selected recipes for next round |
|---|---|---|
| d_bit_0 | frozen_replication | trees_bytes_d8_l5 |
| d_bit_127 | frozen_replication | logistic_limbs_a1e4 |
| d_mod_3 | frozen_replication | logistic_limbs_a1e4 |

## Final untouched-test evaluation

| task | selected model | validation info gain | test info gain | test accuracy lift | test z | threshold |
|---|---|---:|---:|---:|---:|---|
| d_bit_0 | trees_bytes_d8_l5 | -3.25784e-05 | -6.62004e-05 | -0.00453 | -4.0518 | not crossed |
| d_bit_127 | logistic_limbs_a1e4 | -7.64986e-06 | -2.55955e-05 | -0.00173 | -1.5474 | not crossed |
| d_mod_3 | logistic_limbs_a1e4 | -6.59255e-05 | -2.24832e-06 | 3.5e-05 | 0.0332 | not crossed |

## Controls

| task | validation info gain | test info gain | test accuracy lift | test z |
|---|---:|---:|---:|---:|
| canary_public_y_parity | 0.994543 | 0.994543 | 0.49782 | 314.8520 |
| canary_scalar_leak | 0.994531 | 0.994521 | 0.49597 | 313.6892 |
| permuted_d_bit_0 | -0.00112656 | -0.00171828 | -0.0021 | -1.3282 |

## Interpretation

No selected model crossed the preregistered representation threshold on both validation and the one-shot test. This is a bounded null for the tested model, feature, task, and compute budgets.

Validation was used for adaptive model and hyperparameter selection. Exactly one selected recipe per scientific task was then evaluated on the test split. The JSONL ledger contains every completed and failed attempt, its budget, parameters, warnings, metrics, and timing.

A threshold crossing would still require fresh seeds, fresh curves and generators, mechanism extraction, cost accounting, and the repository's normal candidate gates. A null result is bounded to the tested representations, models, budgets, and tasks.
