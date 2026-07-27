# ML-STRUCTURE-PROBE-P0-AUTOML-1M-REPLICA retained qualification

## Result

- Status: `pass`
- Records: `1,000,000`
- Dataset root SHA-256: `eb1a2f1301f211ef973f82d9d13b80cb469d6f115cc1869be48d2b8ea1605421`
- Clean source commit: `fd8a93b090b8b2fb7f5b8c59b57dd8150ea619cf`
- Generation: `9,281.3` records/s in `107.743` s
- Unique scalars: `1,000,000`
- Independent arithmetic spots: `2,049`
- AutoML attempts: `3` completed, `0` failed
- Linear signals: `none`
- AutoML signals: `none`

## Data checks

| check | observed | threshold |
|---|---:|---:|
| scalar bits max |z| | 2.676 | 6.5 |
| public x bits max |z| | 3.206 | 8.0 |
| public y parity |z| | 0.7 | 6.5 |

## Linear baseline

| task | validation info gain | test info gain | test lift | test z | signal |
|---|---:|---:|---:|---:|---|
| canary_public_y_parity | 0.995576 | 0.995577 | 0.498845 | 446.1817 | True |
| canary_scalar_leak | 0.995579 | 0.99557 | 0.49701 | 444.5472 | True |
| d_bit_0 | -0.000405104 | -0.000677754 | -0.004725 | -4.2262 | False |
| d_bit_127 | -0.000498683 | -0.000478104 | -0.00191 | -1.7084 | False |
| d_mod_3 | -0.00173778 | -0.00165736 | -0.000285 | -0.2701 | False |
| permuted_d_bit_0 | -0.000419138 | -0.000397287 | 0.002515 | 2.2495 | False |

## AutoML finalists

| task | recipe | train records | validation info gain | test info gain | test lift | test z | signal |
|---|---|---:|---:|---:|---:|---:|---|
| d_bit_0 | trees_bytes_d8_l5 | 200,000 | -3.25784e-05 | -6.62004e-05 | -0.00453 | -4.0518 | False |
| d_bit_127 | logistic_limbs_a1e4 | 600,000 | -7.64986e-06 | -2.55955e-05 | -0.00173 | -1.5474 | False |
| d_mod_3 | logistic_limbs_a1e4 | 600,000 | -6.59255e-05 | -2.24832e-06 | 3.5e-05 | 0.0332 | False |

## Interpretation

No selected model crossed the preregistered representation threshold on both validation and the one-shot test. This is a bounded null for the tested model, feature, task, and compute budgets.

This is an engineering qualification and a bounded representation assay. It is not evidence of a secp256k1 discrete-log shortcut, and it does not establish unlearnability outside the recorded tasks, representations, methods, and budgets.
