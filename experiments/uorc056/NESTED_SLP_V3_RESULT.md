# UORC-056 nested SLP v3 result

Decision: **NO_EXACT_SEED_FOUND_IN_DECLARED_NESTED_SLP_BEAM**

- Minimum exact all-five size: `None`.
- Exact all-five candidates: `0`.
- Exact first-three candidates: `0`.
- Symbolic lifting: `not_triggered`.

## Best all-five diagnostic

- Penalty: `162`.
- Expression: `(((y3-y1)-(y4-y2))*gy1)`.

## Layer statistics

```json
[
  {
    "best_all_five_penalty": 210,
    "best_first_three_penalty": 78,
    "generated": 27,
    "retained": 27,
    "size": 0
  },
  {
    "best_all_five_penalty": 188,
    "best_first_three_penalty": 70,
    "distinct_error_signatures": 75,
    "generated": 1538,
    "retained": 96,
    "size": 1
  },
  {
    "best_all_five_penalty": 172,
    "best_first_three_penalty": 56,
    "distinct_error_signatures": 73,
    "generated": 10511,
    "retained": 96,
    "size": 2
  },
  {
    "best_all_five_penalty": 172,
    "best_first_three_penalty": 56,
    "distinct_error_signatures": 72,
    "generated": 29038,
    "retained": 96,
    "size": 3
  },
  {
    "best_all_five_penalty": 162,
    "best_first_three_penalty": 56,
    "distinct_error_signatures": 52,
    "generated": 47363,
    "retained": 96,
    "size": 4
  }
]
```

The search is beam-pruned beyond the seed layer. A miss is not a lower bound.
