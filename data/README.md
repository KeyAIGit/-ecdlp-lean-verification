# Knowledge-graph corpus (provenance)

This directory vendors the claim corpus that Layer 3 (the target generator,
`scripts/generator.py`) consumes. The corpus is **read-only input**: it is never
modified by the proof pipeline.

## Primary file

- `KG_CLAIM_FORMALIZATION_v1.csv` — 486 atomic ECDLP claims (Batches B01–B09).
  - Columns: `claim_id, batch, source_id, claim_type, formal_status, model,
    mathlib_area, preconditions, formal_statement, label`.
  - Source: ECDLP corpus, folder `15_Knowledge_Graph/07_Formalization`.
  - Expected SHA256:
    `44e2fa6a2bcf61961b38644151b0296a65b6104a381830853b63f3a970004ccb`
    (matches `07_Formalization/SHA256SUMS.txt`).

The bytes are vendored verbatim so the checksum above can be reproduced; do not
re-type or reformat the file through an assistant (that would break the hash).

## How a claim becomes a Lean target

`generator.py` filters formalizable rows, picks a template by `mathlib_area` /
`claim_type`, and emits an open conjecture stem into `Ecdlp/Targets/<id>.lean`
plus a registry row `targets/<id>.json`. The generator only *proposes* statements;
the Lean kernel is the only judge of whether a proof closes them.
