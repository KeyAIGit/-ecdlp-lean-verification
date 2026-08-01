# Hypothesis pipeline and toy-evidence audit - 2026-08-01

## Decision

The repository has two different computational layers and they must not be
reported as one:

1. The hypothesis-space screen enumerates typed research-question cells. It
   performs no elliptic-curve arithmetic and produces no scientific outcome.
2. A bounded experiment runs only after an exact mechanism, preregistration,
   independent validator, and dated authorization exist. That is where toy
   curves can test a discriminating prediction.

The one-million-cell harness passed resumability, exhaustion, tamper, and
source-isolated historical-producer replay tests. This replay checks the frozen
producer from an archived commit under `python -I -S`, with ambient Python
import paths removed; it is not an independent scientific implementation.
Every shard receipt binds the exact campaign evaluator path and digest recorded
by its evaluation identity. A canonical
campaign is intentionally not retained on this branch:
the historical-scope correction changes the evidence identity, and scientific
source commits must first be reachable from protected `main`. The current
evaluation will be run exactly once after merge.

## Qualified campaign contract

The pre-merge qualification ran in resumable fixed power-of-two shards and
reconstructed the same canonical million-cell root. Its temporary receipts were
discarded because the evaluator source was not yet reachable from protected
`main`; they are tests, not canonical research memory.

| Measure | Qualified or retained pre-merge value |
|---|---:|
| Requested canonical budget after merge | 600 seconds |
| Finite universe size | 1,000,000 |
| Unique universe cells retained before merge | 0 |
| Unique evaluation cells retained before merge | 0 |
| Duplicate evaluations | 0 |
| Cold structural rejects | 768,880 |
| Warm proposal seeds | 231,120 |
| Hot cells | 0 |
| Operational errors | 0 |
| Scientific outcomes | 0 |
| Ranker or Brier labels | 0 |
| Experiment authorizations | 0 |
| Route promotions | 0 |

Throughput is an operational measurement only. Qualification repeatedly
reconstructed the canonical coverage root
`dff1e8cb52594158fc94556cbef3025be647fab310132c34ee58aed3b8399207`.

The separately anchored benchmark `HSR-2026-08-01-001` processed its prior
frozen instance at a median **11,879,612 typed cells/minute** (minimum
11,636,013; maximum 11,905,335). This is one engineering measurement, produced
by the harness's own monotonic clock. It is not independently timed scientific
evidence, and replaying the same million cells for ten minutes would add zero
unique map coverage.

`cold` means that a typed combination failed at least one deterministic
structural gate. It does not mean that a mathematical hypothesis was falsified.
`warm` means only that the combination is a proposal seed; it still lacks an
assured mechanism and independent scientific review. No result from this
campaign is training data for the research ranker.

## Toy-evidence inventory

| Lane | Actual tested scope | What was checked | Assurance and limitation |
|---|---|---|---|
| P0 GLV-Semaev | 16/20/24-bit toy curves, `m=2`, seed 1 | Direct pair enumeration and EC relation verification | Historical partial negative for finite GLV orbit keying. The legacy 24-bit row used a cofactor-3 curve and is not a current-model native outcome. |
| P1 Semaev solve | Cofactor-1 16/20/24-bit curves, two-term relations, seed 1, 2,000 targets per setting | S3 solver against brute-force EC enumeration | Sound and complete on the tested rows; no scaling or faithful Petit claim. |
| P1-m3 | Cofactor-1 16/20/24-bit curves, three-term distinct-index relations, seed 1 | S4-resultant solver against brute-force EC enumeration | Zero spurious rows in scope. The validator reuses the relation confirmation helper and the run does not test Groebner cost. |
| P3 system | 16/20-bit `m=2`; 16-bit-only `m=3`; factor bases up to 12; seed 1 | Lex solver, custom Macaulay proxy, and brute-force EC relation replay | Descriptive toy proxy. The `m=3` solving degree is only a capped lower bound. No faithful Petit construction. |
| P4 composed map | Single-seed toy rows; decisive degree measurement only at `m=2`, factor-base size 4 | A non-faithful composed-map presentation against a raw baseline | It explicitly implements neither PKC 2016 construction. It is not evidence against faithful Petit. |
| M16 fixed-target yield | Three synthetic E7 subgroups, arities 19/21/23, two matched arms, five seeds, 30 cells, 3,000,000 trials | Preregistered relation-yield comparison and independent raw-artifact replay | Strongest current bounded toy run. It retained a bounded negative for a GLV-specific advantage, but no solver, recovery, scaling, or secp256k1 result. |

The M16 run is the closest match to Constitution v3 because it has multiple
sizes, paired controls, multiple seeds, a frozen prediction, a resource cap,
and an independent standard-library validator. It still cannot establish
persistence at 256 bits. The earlier P0-P4 lanes are historical evidence and
do not retroactively become native Engine outcomes.

## Historical correction

Immutable event `REO-2026-07-24-006` records field bits `[16, 20]` for the P3
`m=3` result. Both the planned grids and the actual measurement rows contain
`m=3` only at 16 bits; the 20-bit measurements are `m=2`. The original event
bytes remain unchanged. Correction
`HSCORR-2026-08-01-P3-M3-BITS` overlays an effective scope of `[16]`, binds the
event and source artifacts by SHA-256, and is checked by the Research Engine.

## Constitution conformance

The campaign implementation and qualification satisfy the Constitution's
memory and anti-overclaim rules. A canonical run has not yet been retained:

- no toy result is extrapolated to 256 bits;
- no screening cell is called a hypothesis or falsification;
- no exact-target secp256k1 experiment ran;
- no candidate was admitted, recommended, or authorized;
- canonical successful output will be committed as hash-anchored receipts;
- post-preflight operational errors retain bounded diagnostics and a hash chain
  while the retention path remains writable; a secondary retention failure is
  surfaced as a warning, and pre-anchor local deletion is not claimed to be
  impossible;
- a new evidence snapshot changes the evaluation identity but does not create
  new universe coverage;
- the same exhausted evaluation refuses further work.

The repository does not yet satisfy the scientific release gate of three
native Engine outcomes and an external scientific review. That remains a
deliberate open requirement, not a software failure.

## Ranker memory boundary

The six existing review-ledger rows remain byte-anchored historical records and
are permanently ineligible for training: they are migrations, lack independent
source/model/context review, and predate evidence-closure binding. New schema-2
rows bind the review, frozen candidate features, candidate-specific evidence
manifest, and evidence closure into one `ledger_entry_sha256`. Multiple reviews
of that same candidate version produce one training example; conflicting
verdicts produce no example. The global evidence root is retained for audit but
does not make unrelated candidate reviews stale. Training admission is held in
the separate append-only `HYPOTHESIS_REVIEW_REGISTRY_V1`; it survives current
queue rotation and permits multiple reviews per immutable candidate version.
Neither a portfolio decision nor self-declared independence booleans can
register a label. The ranker directly checks the proposal and five bound review
artifacts, including role completeness, blinded sessions, distinct reviewers
and contexts, cross-family coverage, and proposer separation. These remain
provenance attestations rather than proof of intellectual independence.

## Durable memory model

GitHub is the canonical external memory. The model itself is not assumed to
retain private mutable weights or reliable cross-task memory. Future agents
must reconstruct state from:

`source -> claim -> route/question -> proposal seed -> exact mechanism ->
preregistration -> authorization -> raw artifact -> independent replay ->
scoped outcome -> reopening condition`.

The campaign ledger stores coverage and failures, while scientific feedback
continues to flow only through typed desk decisions, claim state, and experiment
outcomes. Campaign artifacts are intentionally excluded from the screen's own
evidence inputs, preventing a self-confirming loop.

## Next gate

Run the current-evidence evaluation once after the new evaluator and
correction are reachable from protected `main`. It must add zero new universe
cells and one million versioned evaluation cells. Do not report it as new-space
coverage. A larger campaign is permitted only after a new evidence-bounded
grammar defines genuinely distinct mechanism-bearing axes and a new
`universe_id`. The desired 100-million scale is an engineering target after
that grammar exists, not a cardinality knob.

The next scientific action remains a source-backed proposal cycle. A proposal
must survive exact-mechanism, target-property, prior-art, cost-bridge, recovery,
and validator reviews before any new toy experiment can be authorized.
