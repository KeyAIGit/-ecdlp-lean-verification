# UORC-056 transfer synthesis v2 result

Decision: **NO_EXACT_CANDIDATE_IN_UORC-056-C-SYNTH-V2**

## Exact gates

- Exact on all five frozen curves: `False`.
- Minimum all-five weight: `None`.
- Exact on the first three curves: `False`.
- Minimum first-three weight: `None`.
- Symbolic lifting: `not_triggered_because_no_three_curve_exact_seed_exists`.

## Catalogue

- Raw symbolic atoms: `1639`.
- Valid on all five curves: `272`.
- All-curve semantic classes: `218`.

## Diagnostic near miss

- Errors: `160` of `438`.
- Accuracy: `0.634703196347`.
- Formula: `chi(gy1) * chi((x1+beta2_x1+neg_two)) * chi((x1*doubling_slope))`.

The near miss is not an exact candidate and is not promoted.

## Single-curve seeds

- `E7-P43-N31`: found=`True`, minimum_weight=`3`.
- `E7-P67-N79`: found=`False`, minimum_weight=`None`.
- `E7-P79-N67`: found=`False`, minimum_weight=`None`.

## Scientific boundary

This result closes or advances only the explicitly frozen bounded grammar. It does not by itself establish a uniform sub-square-root evaluator.
