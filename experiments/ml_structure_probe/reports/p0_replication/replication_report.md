# P0 fresh-seed frozen-model replication

- Primary dataset: `81324f58ae00f4f3d33972a5dafa7cd27dc60fdc35f6f41866cafc3be0231e40`
- Replica dataset: `eb1a2f1301f211ef973f82d9d13b80cb469d6f115cc1869be48d2b8ea1605421`
- Replicated signals: `none`

| task | frozen recipe | primary test info gain | primary test z | replica test info gain | replica test z | replicated signal |
|---|---|---:|---:|---:|---:|---|
| d_bit_0 | trees_bytes_d8_l5 | -4.52929e-05 | -0.3354 | -6.62004e-05 | -4.0518 | False |
| d_bit_127 | logistic_limbs_a1e4 | -3.15535e-05 | -2.2540 | -2.55955e-05 | -1.5474 | False |
| d_mod_3 | logistic_limbs_a1e4 | -5.33734e-05 | -0.9150 | -2.24832e-06 | 0.0332 | False |

## Interpretation

No frozen model produced a threshold-crossing signal in both fresh-seed assays. This is a replicated bounded null for the recorded models, representations, tasks, curve, and budgets.

The model recipes were selected on the primary validation split and frozen before the second synthetic seed was generated. Both runs use separate train, validation, and test derivation domains. This does not support any inference beyond the explicitly recorded scope.
