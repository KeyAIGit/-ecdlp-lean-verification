# C43/C43B composed-frontier authority repair

Date: 2026-08-17

Status: authority/provenance repair only. No theorem, replay result, or C44
construction is changed or added.

## Decision

PR #418 and PR #419 were created as exact Git siblings from the same C42 head:

```text
728d1a7a1c60463cc4546e2bb21fa3eaf3936d58  C42
├── 52015c53ce3770268437aac71ee74e0517719834  C43 / PR #418
└── acdc7c6ea5d76ac58afb1574d1efa9bbf60c050f  C43B / PR #419
```

Neither original package is the Git or declared parent of the other, and
neither supersedes the other.

Their scientific roles are complementary:

- C43 is required inherited knowledge. It supplies the universal-cover normal
  form, H1--H7, the gauge-charge type system, the corrected
  `ord_n(2)=(n-1)/64` and `ord_p(2)=(p-1)/14` certificates, and the 32-cycle
  action. Its H7 result leaves only an unsquared anchor-to-query open transport
  as the local charged type.
- C43B realizes the exact `LOCAL-GLV-GAUGE-BREAKING-C43` route declared by C42.
  In the gauge language of C43, it refines H7 on the GLV orbit to the exact
  surviving object
  `J_G(X)=Y_G(beta X)Y_G(beta^2 X)/(X^3+7)`, with residual Klein-four gauge.
  This specialization is the composed frontier carrier, but it does not erase
  or replace the C43 framework.

The authoritative state is therefore a DAG composition. Commit
`1d436cba35b78526e800dae005aa2abce33a9994` has the exact ordered parents
`acdc7c6ea5d76ac58afb1574d1efa9bbf60c050f` and
`52015c53ce3770268437aac71ee74e0517719834`. It imports both scientific trees
without rewriting either package's historical parent declaration.

The machine authority is
`notes/UORC056_C_TRACK_LINEAGE_C43B.json`. Its typed relations are:

```text
DECLARED_PARENT(C43, C42)
DECLARED_PARENT(C43B, C42)
REALIZES(C43B, C42/LOCAL-GLV-GAUGE-BREAKING-C43)
REFINES(C43B, C43/H7-GAUGE-TYPED-OPEN-TRANSPORT)
COMPOSES(COMPOSED-C43-C43B, C43)
COMPOSES(COMPOSED-C43-C43B, C43B)
FRONTIER_CARRIER(COMPOSED-C43-C43B, C43B)
NEXT_OPEN_PROBLEM(COMPOSED-C43-C43B, ORDERED-SECTOR-TRANSPORT-C44)
```

There is intentionally no `SUPERSEDES(C43B,C43)` relation and no false
`DECLARED_PARENT(C43B,C43)` relation. Pull-request numbers and timestamps are
provenance locators, not selection inputs.

## Exact open frontier

`ORDERED-SECTOR-TRANSPORT-C44` remains an open problem: construct a public,
unsquared evaluator for `J_G(x(Q))` that is Klein-four-sensitive,
generator-marked and ordered, does not enumerate the `(n-1)/6` GLV quotient
roots, does not hide an order-`n` table in advice or coefficients, and reports
an explicit total charged cost through a circuit, recurrence, transfer law, or
local functional equation.

No implementation branch or commit is authorized. The v1-compatible top-level
`successor` is therefore `null`; the planned problem and its gates are retained
inside the typed authority extension. This repair does not activate C44.

## Integration and downstream interpretation

The composed authority must land in
`research/uorc056-local-glv-gauge-breaking-c43` with the two-parent commit
above still in its ancestry. Squash or rebase integration would destroy the
asserted Git composition and must not be used.

Only after that branch contains the composed head, close PR #418 with the
disposition **integrated, not superseded**. Keep its branch and exact head.
Closing it before composition would discard an active authority input; leaving
it open after composition makes the current downstream v0.2 resolver retain
the old equal-candidate tie because that resolver does not yet interpret the
nested `COMPOSES` and `FRONTIER_CARRIER` relations.

After integration, PR #419 remains the single active carrier branch and its
tree contains both exact claim sets. The closure of #418 is a lifecycle state,
not a scientific supersession. If that integrated disposition is not applied,
downstream must continue to report `FRONTIER_CONFLICT` rather than infer a
winner from recency or PR number.
