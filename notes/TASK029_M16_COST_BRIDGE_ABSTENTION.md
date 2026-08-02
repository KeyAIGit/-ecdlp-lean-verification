# TASK-029 M16 cost-bridge abstention

Date: 2026-08-01

## Question

Can the current source-grounded evidence for `CELL-M-PKC-SMOOTH-M16` support a
non-executable `HYP-M16-SOLVER-SLOPE-001` proposal with an exact generalized-root
algorithm, complete recovery semantics, and a cost-changing bridge against a
matched plain baseline?

## Frozen input

- current seed: `HGS-3266E42A729C`
- route: `R-PETIT-COMPOSED-MAPS`
- threat model: classical plain single-target ECDLP
- source commit: `b8871e529923c1189da6330dfa0b320edf1f3fa9`
- typed-evidence digest:
  `602d93c115099c81f02b8a8ac531e33036e6988d5d3ddf2ec257b1118e5cd75d`
- source-grounded packet:
  `fb4384aedf160cd435f4a7950b73dca57d074f32eeb792b00571d1e95376d23f`

The synthesis was a post-hoc parser replay against this commit-bound packet.
The canonical prompt was not delivered through an attested provider transport.
Source and model-family independence are therefore `not_established`.

## Result

The correct output is strict abstention. The source fixes the M16 input
presentation and a partial cost identity, but it does not supply the missing
generalized-root algorithm or a theorem pricing the complete pipeline.

Retained attempt:

- ID: `HGA-M16-COST-BRIDGE-ABSTAIN-001`
- fragment SHA-256:
  `804c2843eef630184d156dbcfd490c887fc503fbacedc5f95ca1d80cd2da24b4`
- status: `not_specified_due_to_abstention`
- scientific outcome: false
- calibration: excluded
- ranker label: false
- retention: zero
- authorization/execution: false
- route effect: none
- cell effect: `open_to_open`

This is immutable search memory, not a hypothesis proposal, five-role proposal
review, experiment outcome, negative result, novelty claim, or route decision.

## Exact blockers

1. `MISSING-M16-GR-SOLVER-001`: specify a source-faithful generalized-root
   algorithm for the exact 65-member nonidentity-target M16 System (4), including
   representation, exceptional-locus policy, termination, and complete recovery.
2. `MISSING-M16-COST-THEOREM-001`: prove or independently validate a common-unit
   cost statement covering solving, recovery, preprocessing, memory, independent
   relation collection, rank, and sparse linear algebra against the matched
   baseline.

The published partial expression gives the necessary balanced-regime threshold
`T_A(p,16,L_p) = O(p^(7/16-epsilon))`; it does not identify an algorithm `A` or
establish that bound.

## Representation audit

The review retained four non-equivalent presentations without silently treating
them as cost-equivalent:

| presentation | variables | equations | largest explicit input degree |
|---|---:|---:|---:|
| direct source System (4) | 64 | 65 | `deg_x S17 = 32768` |
| recursive `S3` plus source map chain | 78 | 79 | 13441 |
| recursive `S3` plus quadratic circuit | 398 | 399 | 4 |
| one fixed affine chart before membership constraints | `14-|I|` | 15 | 4 |

These counts do not order solving degree, fill-in, memory, runtime, recovery cost,
or total attack cost. Replacing direct System (4) with another presentation creates
a new implementation identity and requires its own cost bridge.

## Independent review boundary

Three separate read-only review roles agreed on abstention:

- creative/mechanism review: no exact cost-changing proposal can be supported;
- algebra/cost review: no theorem orders the available representations or bounds
  the complete solver pipeline;
- recovery/governance review: sound acceptance is not complete recovery, and the
  fixed-target, subgroup-only, and nonidentity scope must remain explicit.

They shared the parent context and do not establish source independence. Their
observations are retained only as blockers on proposal creation.

## Reopening conditions

Reopen proposal drafting only when evidence supplies at least one concrete solver
algorithm and a matching complete-cost argument, or when a primary source provides
an equivalent construction with exact recovery and scaling semantics. A renamed
request for a solver, a toy runtime, or a lower-degree re-encoding is insufficient.

No solver run, TASK-026 rerun, exact-target secp256k1 work, route promotion, or
experiment authorization follows from TASK-029.

