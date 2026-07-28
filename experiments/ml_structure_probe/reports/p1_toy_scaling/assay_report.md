# P1E toy-curve ML scaling report

## Decision boundary

This is a route-neutral engineering qualification. It is not a native Research Engine outcome and makes no secp256k1 or asymptotic claim.
Dataset records: 1105920.
The selected architecture is retrained independently at each size; this is not cross-size weight extrapolation.

## Search

- Screen fits: 196
- Selection fits: 219 successful, 0 failed
- Frozen evaluation fits: 28 successful, 0 failed
- Frozen architecture: `trees-compressed-d6-l16`
- Corrected transfer gate: `False`
- Independent pre-blind selection validation: `pass` (`6e7a9ed3cb78`)
- Metric baseline: exact per-record bit probabilities for d uniform in [1,n-1], computed from public group order n

## Frozen ladder

| bits | split | info bits/key | bit lift | exact | top-256 |
|---:|---|---:|---:|---:|---:|
| 13 | seen_curve_seen_generator | -0.0247763 | -0.00296018 | 0 | 0.0400391 |
| 13 | seen_curve_new_generator | -0.00887479 | 0.000425681 | 0 | 0.0400391 |
| 13 | new_curve_seen_generator | -0.0637414 | -0.00138972 | 0.00012207 | 0.0478516 |
| 13 | new_curve_new_generator | -0.0595842 | -0.00171837 | 0 | 0.0400391 |
| 13 | blind_curve_blind_generator | -0.204192 | -0.000532101 | 0.000325521 | 0.0439453 |
| 16 | seen_curve_seen_generator | -0.0062117 | -0.000897696 | 0 | 0.00390625 |
| 16 | seen_curve_new_generator | -0.00905013 | -0.00216675 | 0 | 0.00585938 |
| 16 | new_curve_seen_generator | -0.105015 | 0.000724792 | 0 | 0.0078125 |
| 16 | new_curve_new_generator | -0.105309 | -0.000110626 | 0 | 0.00292969 |
| 16 | blind_curve_blind_generator | -0.0375329 | -0.00030009 | 4.06901e-05 | 0.00683594 |
| 20 | seen_curve_seen_generator | -0.00212253 | -0.00106498 | 0 | 0 |
| 20 | seen_curve_new_generator | -0.00119916 | -0.000909424 | 0 | 0 |
| 20 | new_curve_seen_generator | -0.180182 | -8.92639e-05 | 0 | 0 |
| 20 | new_curve_new_generator | -0.182547 | 4.88281e-05 | 0 | 0.000976562 |
| 20 | blind_curve_blind_generator | -0.185152 | -0.000240072 | 0 | 0 |
| 24 | seen_curve_seen_generator | -0.00181252 | -0.000401225 | 0 | 0 |
| 24 | seen_curve_new_generator | -0.00127344 | 0.000298394 | 0 | 0 |
| 24 | new_curve_seen_generator | -0.0127536 | -0.00012366 | 0 | 0 |
| 24 | new_curve_new_generator | -0.0125873 | 0.000435193 | 0 | 0 |
| 24 | blind_curve_blind_generator | -0.0279179 | -0.000704024 | 0 | 0 |

## Controls

- Pipeline valid: `True`
- Canary pass: `True`
- Negative-control pass: `True`

## Matched generic baselines

| bits | method | success | median group ops | median seconds |
|---:|---|---:|---:|---:|
| 13 | bsgs | 1.000 | 105.0 | 0.00019164 |
| 13 | pollard_rho | 1.000 | 328.0 | 0.000536107 |
| 16 | bsgs | 1.000 | 387.0 | 0.000607143 |
| 16 | pollard_rho | 1.000 | 713.5 | 0.00121593 |
| 20 | bsgs | 1.000 | 1435.0 | 0.00241401 |
| 20 | pollard_rho | 1.000 | 2534.0 | 0.00477624 |
| 24 | bsgs | 1.000 | 6027.5 | 0.0112938 |
| 24 | pollard_rho | 1.000 | 19335.5 | 0.0359142 |

Generic baselines are cold-start measurements. The BSGS table is rebuilt per target here, although it can be reused for additional targets sharing the same curve and generator. Memory values are explicit estimates, not process peak-RSS measurements.

## Interpretation rule

A result limited to seen curves and generators is memorization or an instance-specific representation effect. Sizes 28 and 32 remain closed unless blind 24-bit curve-and-generator transfer yields an independently verified explicit mechanism with scaling better than the square-root baseline.
