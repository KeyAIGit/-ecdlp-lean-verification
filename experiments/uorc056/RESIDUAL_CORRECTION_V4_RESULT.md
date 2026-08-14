# UORC-056 residual correction v4 result

Decision: **NO_EXACT_ONE_OR_TWO_ATOM_CORRECTION_TO_SELECTED_V2_NEAR_MISS**

## Exact correction gate

- Selected V2 residual errors: `160` of `438`.
- Searched one-atom corrections: `218`.
- Searched two-atom corrections: `23653`.
- Exact corrections found: `0`.
- Best corrected total errors: `154`.
- Best corrected actual weight: `5`.
- Symbolic lifting: `not_triggered`.

## Per-curve residual structure

| curve | errors | negation disagreement | doubling disagreement | GLV disagreement | best modulus | lift |
|---|---:|---:|---:|---:|---:|---:|
| `E7-P43-N31` | 14 | 0 | 12 | 8 | 9 | 0.333333333333 |
| `E7-P67-N79` | 32 | 0 | 44 | 28 | 16 | 0.153846153846 |
| `E7-P79-N67` | 18 | 0 | 32 | 28 | 15 | 0.060606060606 |
| `E7-P127-N127` | 52 | 0 | 68 | 52 | 10 | 0.079365079365 |
| `E7-P163-N139` | 44 | 0 | 60 | 60 | 15 | 0.043478260870 |

The modular and Fourier rows are diagnostics on known toy indices, not evaluators from Q.

The exact correction search is exhaustive only around the selected V2 near miss and at most two additional admitted atoms.
