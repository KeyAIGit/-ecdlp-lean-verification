# ML-STRUCTURE-PROBE-P0-AUTOML-1M retained qualification

## Result

- Status: `pass`
- Records: `1,000,000`
- Dataset root SHA-256: `81324f58ae00f4f3d33972a5dafa7cd27dc60fdc35f6f41866cafc3be0231e40`
- Clean source commit: `be7d11151d48473cb6cc808f5b197a9b6ac89a6b`
- Generation: `9,066.4` records/s in `110.298` s
- Unique scalars: `1,000,000`
- Independent arithmetic spots: `2,049`
- AutoML attempts: `87` completed, `0` failed
- Linear signals: `none`
- AutoML signals: `none`

## Data checks

| check | observed | threshold |
|---|---:|---:|
| scalar bits max |z| | 3.58 | 6.5 |
| public x bits max |z| | 2.632 | 8.0 |
| public y parity |z| | 0.916 | 6.5 |

## Linear baseline

| task | validation info gain | test info gain | test lift | test z | signal |
|---|---:|---:|---:|---:|---|
| canary_public_y_parity | 0.995586 | 0.995584 | 0.4996 | 446.8560 | True |
| canary_scalar_leak | 0.995582 | 0.995577 | 0.49982 | 447.0526 | True |
| d_bit_0 | -0.000529003 | -0.000501154 | -0.000225 | -0.2012 | False |
| d_bit_127 | -0.000463284 | -0.000466011 | -0.002555 | -2.2853 | False |
| d_mod_3 | -0.00128735 | -0.00137211 | 0.001045 | 0.9909 | False |
| permuted_d_bit_0 | -0.000453952 | -0.000405571 | 0.00114 | 1.0196 | False |

## AutoML finalists

| task | recipe | train records | validation info gain | test info gain | test lift | test z | signal |
|---|---|---:|---:|---:|---:|---:|---|
| d_bit_0 | trees_bytes_d8_l5 | 200,000 | -3.34732e-05 | -4.52929e-05 | -0.000375 | -0.3354 | False |
| d_bit_127 | logistic_limbs_a1e4 | 600,000 | -2.3607e-06 | -3.15535e-05 | -0.00252 | -2.2540 | False |
| d_mod_3 | logistic_limbs_a1e4 | 600,000 | -6.07606e-05 | -5.33734e-05 | -0.000965 | -0.9150 | False |

## Interpretation

No selected model crossed the preregistered representation threshold on both validation and the one-shot test. This is a bounded null for the tested model, feature, task, and compute budgets.

This is an engineering qualification and a bounded representation assay. It is not evidence of a secp256k1 discrete-log shortcut, and it does not establish unlearnability outside the recorded tasks, representations, methods, and budgets.
