# Full-key secp256k1 AutoML development report

## Verdict

This is a synthetic engineering representation assay. It is not a key-recovery result and it is not scientific evidence.

The search completed **301** predeclared training attempts. The frozen development ensemble reached **-0.00323476 bits/key** information gain, **0.000104629** bit-accuracy lift, and **0** exact 256-bit keys.

A compressed secp256k1 key occupies 33 bytes (264 physical bits), but its independent public representation is 256 x-coordinate bits plus one y-parity bit (257 informative bits). The 512-bit x||y affine representation was also searched; y is deterministically recoverable from x and parity, so it adds no independent information.

## Frozen recipe

- Architecture: `arch-076`
- Family: `extra_trees`
- Input: `byte_popcounts`
- Hidden/configuration: `{"max_depth": 6, "max_features": "sqrt", "min_samples_leaf": 256, "n_estimators": 16}`
- Output: 256 simultaneous Bernoulli probabilities, one per private-scalar bit
- Selection: development data only; a new independent million remains blind

## Development metrics

| Metric | Value |
|---|---:|
| Information gain, bits/key | -0.00323476201 |
| Bit accuracy | 0.500024043 |
| Prior-null bit accuracy | 0.499919414 |
| Bit accuracy lift | 0.000104628906 |
| Paired accuracy z | 1.57155 |
| Mean Hamming distance | 127.994 |
| Exact 256-bit matches | 0 |

## Search stages

| Stage | Attempts | Successful |
|---|---:|---:|
| confirm | 36 | 36 |
| control_label_leak_1 | 2 | 2 |
| control_label_leak_32 | 2 | 2 |
| control_label_leak_8 | 2 | 2 |
| control_permuted_keys | 3 | 3 |
| control_random_labels | 3 | 3 |
| cross_dataset | 8 | 8 |
| final_ensemble_member | 5 | 5 |
| screen | 240 | 240 |

## Controls

- Random-label attempts: 3
- Whole-key permutation attempts: 3
- Deliberate label-leak attempts: 6
- Maximum null information gain: -0.665468 bits/key
- Minimum deliberate-leak information gain: -0.319438 bits/key

## Interpretation boundary

Two million development pairs occupy a negligible fraction of the secp256k1 scalar space. A null result rejects only the tested model, representation and compute budgets. A positive development metric is only a candidate until the single frozen ensemble repeats it independently on both halves of the new blind million.
