# HYP-SELECT-006: million-cell typed screening

Date: 2026-07-31

## Decision

Add a high-throughput screening layer above the frozen HYP-SELECT-005 run. The
new layer enumerates exactly 1,000,000 typed research-question challenge cells,
retains no raw million-row ledger, and exposes only aggregate coverage, bounded
samples, and a small review queue.

Queue records separate three identities: a content-addressed scientific
signature, an evidence-bound evaluation instance, and a mixed-radix batch
ordinal. Changing an operator's meaning invalidates the scientific signature;
unrelated evidence drift invalidates only the evaluation instance.

This is not a claim that one million independent or novel attack hypotheses were
invented. A cell is the Cartesian tuple:

```
base question
  x mechanism obligation
  x cost bridge
  x decisive test
  x adversarial challenge
```

The tenth axis contains threat-model, target-property, prior-art, mechanism,
recovery, precomputation, end-to-end cost, scaling, validator-independence, and
reopening-premise challenges. It makes the screen stricter and the map more
diagnostic; it does not create mathematical evidence.

## Result

- typed cells: 1,000,000
- cold structural rejections: 768,880
- warm unresolved cells: 231,120
- hot assured cells: 0
- bounded review queue: 35
- admissible / recommended / authorized: 0 / 0 / 0
- route promotions / experiment events: 0 / 0
- instance root: `272bcc9e877fc4ae86789cbb55d1362830e4e8f77b95ee027d6e25a202e52404`

The hot/warm/cold map is `data/hypothesis_space_map.json`. Its coverage boundary
is the frozen finite projection only, not all ECDLP ideas or all literature.

## Performance

Measured on the local Codex Windows runtime:

| implementation | cells | elapsed | cells/minute |
|---|---:|---:|---:|
| HYP-SELECT-005 reference path | 100,000 | 12.307 s | about 487,500 |
| HYP-SELECT-006 binary streaming path | 1,000,000 | 10.428 s | about 5,754,000 |

The performance target of 1,000,000 cells/minute was exceeded by about 5.5x on
this host. The wall-clock figure is a benchmark, not a deterministic CI fact.
CI enforces replay and state equality; `--benchmark` reports host-specific rate.

The speedup comes from removing per-cell SQLite writes, replacing repeated JSON
serialization with a fixed binary leaf format, proving Cartesian typed identity
from unique axis IDs, precomputing type/operator gates, and retaining only small
Pareto fronts.

## Scientific boundary

- Typed identity is not semantic deduplication or novelty.
- Cold means structurally rejected under the registered gates, not mathematically
  impossible outside the exact cell scope.
- Warm means worth preserving as an unresolved question, not plausible attack
  evidence.
- The generator cannot create hot state. Hot requires an externally assured exact
  mechanism, cost bridge, and independent review.
- No model call, experiment, solver sweep, exact-target computation, route
  promotion, or ECDLP claim was made.
