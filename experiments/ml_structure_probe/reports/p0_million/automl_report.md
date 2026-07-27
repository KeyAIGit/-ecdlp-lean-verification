# ML-STRUCTURE-PROBE-P0-AUTOML-1M AutoML qualification

This report is a route-neutral engineering observation. It is not a discrete-log solution, a complexity claim, or a Research Engine candidate.

## Outcome

- Pipeline status: `pass`
- Dataset records: `1,000,000`
- AutoML attempts completed: `87`
- AutoML attempts failed: `0`
- Controls pass: `True`
- Representation signals: `none`

## Method coverage

| family | feature modes | completed runs | failed runs |
|---|---|---:|---:|
| bernoulli_nb | compressed_bits | 12 | 0 |
| extra_trees | compressed_bytes, x_limbs16 | 15 | 0 |
| hist_gbdt | compressed_bytes, x_limbs16 | 9 | 0 |
| mlp | compressed_bits, compressed_bytes | 12 | 0 |
| rbf_sgd | compressed_bytes | 9 | 0 |
| sgd_logistic | byte_popcounts, compressed_bits, compressed_bytes, x_limbs16 | 30 | 0 |

## Adaptive selection

| task | round | selected recipes for next round |
|---|---|---|
| d_bit_0 | screen | logistic_limbs_a1e4, trees_bytes_d8_l5, rbf_bytes_g01, mlp_bytes_h64_32, hist_bytes_l15, bernoulli_bits_a10 |
| d_bit_127 | screen | rbf_bytes_g01, logistic_limbs_a1e4, trees_bytes_d8_l5, mlp_bytes_h64_32, hist_bytes_l15, bernoulli_bits_a10 |
| d_mod_3 | screen | trees_bytes_d8_l5, logistic_limbs_a1e4, rbf_bytes_g01, mlp_bytes_h64_32, hist_bytes_l15, bernoulli_bits_a10 |
| d_bit_0 | confirm | trees_bytes_d8_l5, logistic_limbs_a1e4 |
| d_bit_127 | confirm | logistic_limbs_a1e4, trees_bytes_d8_l5 |
| d_mod_3 | confirm | trees_bytes_d8_l5, logistic_limbs_a1e4 |
| d_bit_0 | final_selection | trees_bytes_d8_l5 |
| d_bit_127 | final_selection | logistic_limbs_a1e4 |
| d_mod_3 | final_selection | logistic_limbs_a1e4 |

## Final untouched-test evaluation

| task | selected model | validation info gain | test info gain | test accuracy lift | test z | threshold |
|---|---|---:|---:|---:|---:|---|
| d_bit_0 | trees_bytes_d8_l5 | -3.34732e-05 | -4.52929e-05 | -0.000375 | -0.3354 | not crossed |
| d_bit_127 | logistic_limbs_a1e4 | -2.3607e-06 | -3.15535e-05 | -0.00252 | -2.2540 | not crossed |
| d_mod_3 | logistic_limbs_a1e4 | -6.07606e-05 | -5.33734e-05 | -0.000965 | -0.9150 | not crossed |

## Controls

| task | validation info gain | test info gain | test accuracy lift | test z |
|---|---:|---:|---:|---:|
| canary_public_y_parity | 0.994539 | 0.994523 | 0.4981 | 315.0284 |
| canary_scalar_leak | 0.994533 | 0.994517 | 0.49979 | 316.0950 |
| permuted_d_bit_0 | -0.00132343 | -0.00106897 | 0.00289 | 1.8278 |

## Interpretation

No selected model crossed the preregistered representation threshold on both validation and the one-shot test. This is a bounded null for the tested model, feature, task, and compute budgets.

Validation was used for adaptive model and hyperparameter selection. Exactly one selected recipe per scientific task was then evaluated on the test split. The JSONL ledger contains every completed and failed attempt, its budget, parameters, warnings, metrics, and timing.

A threshold crossing would still require fresh seeds, fresh curves and generators, mechanism extraction, cost accounting, and the repository's normal candidate gates. A null result is bounded to the tested representations, models, budgets, and tasks.
