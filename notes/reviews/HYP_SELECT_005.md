# HYP-SELECT-005: 100k research-question funnel

Date: 2026-07-31

Audited base: `main` at
`1f4464e7d5fb0bcdff9fd5f5bf09fa4a557ea41a`.

Decision:
`9 NON-EXECUTABLE RESEARCH BETS / 0 ADMISSIBLE / 0 AUTHORIZED`.

This is a screening-system result, not an ECDLP result. It does not claim
that 100,000 scientifically independent attacks were invented. It replays
exactly 100,000 typed question signatures derived from 100 untrusted
brainstorming anchors and three ten-element obligation axes.

## 1. Result

The streaming run produced:

| Stage | Count |
|---|---:|
| Generation attempts | 100,000 |
| Unique semantic normal forms | 100,000 |
| Structurally retained | 26,520 |
| Rejected by one or more deterministic gates | 73,480 |
| Per-base Pareto records | 635 |
| Bounded review queue | 29 |
| Non-executable research bets | 9 |
| Admissible / recommended / authorized | 0 / 0 / 0 |
| Route promotions / experiment events | 0 / 0 |

The RFC6962-style streaming root is:

```text
529d10a7556a28e0409600465f867e2d28a17ca2bcc1d66daf6eb7de0136a34a
```

The full 100,000-row ledger is intentionally not committed. The generator
keeps an on-disk exact-normal-form index, an `O(log N)` Merkle frontier,
bounded rejection samples, Pareto records, and the 29-row review queue.
The committed aggregate is about four orders of magnitude smaller than a
fully materialized proposal ledger.

## 2. Trust boundary

The source TSV came from the unmerged historical branch
`origin/agent/hyp-select-004-hundred-screen` at
`246177fa18d4b1a517f7c821229f7154f918e850`. Its `PASS`, `KILL`,
`SHORTLIST`, `MERGED`, and `canonical` fields are preserved only as review
provenance.

They are not scientific gates. In particular, different child claims that
shared one old `canonical` label are not collapsed. Semantic identity uses
the exact source claim, family, type, and typed obligation program.

Every generated signature still carries all three warnings:

- `exact_mechanism_missing`;
- `novelty_unverified`;
- `source_independence_unestablished`.

Therefore a structurally retained signature is not a hypothesis, a
candidate, a route decision, or permission to execute.

## 3. Deterministic funnel

The finite grammar is:

```text
100 base research questions
  x 10 mechanism obligations
  x 10 cost-changing bridges
  x 10 decisive-test obligations
  = 100,000 signatures
```

The bulk stage makes zero language-model calls. It rejects incompatible
types, adjacent key-recovery scope, attacks without a scaling bridge,
barriers without a scoped mechanism, enabling tasks without a dependency
bridge, and known closed patterns without a permitted reopening class.

It does not use a single aggregate score. Structurally surviving records
are reduced by per-type Pareto dominance and explicit diversity caps.
Human/model review then operates only on the bounded queue.

## 4. Retained research bets

The tenth slot is deliberately empty. Filling it would retain solver
engineering, a duplicate obligation, or a bounded-negative GLV branch only
to satisfy a quota.

| Role | Seed | Question and decisive next test |
|---|---|---|
| Primary, existing proposal | `HQS1-1A2C703A752AB404C9E2D08F824B6521` | Bind to the existing `HYP-M16-SOLVER-SLOPE-001`. Perform five digest-bound reviews of its regime, yield, recovery, rank, and common-cost gates. No solver run. |
| Hedge barrier | `HQS1-0F66909024099BE4E8AA6F5B2C76165F` | Build a faithful structured-generic-group simulation or return the first violated axiom and a minimal counterexample. |
| Primary enabler | `HQS1-215DF9F00F61AB08D340BBB7EEF2C2A6` | Derive a fixed-target relation-incidence law for one exact structured factor base, including repetitions, stabilizers, exceptional fibers, and rank semantics. |
| Cross-route barrier | `HQS1-152789DAF4DCF18DCE5D2AB949261907` | Freeze a conditional full-cost identity covering acquisition, failed solving, recovery, rank, sparse linear algebra, preprocessing, memory, and equal success. |
| Walk barrier | `HQS1-18315184F7578ED755F531EF50AAF60D` | State exact chain assumptions and prove return-time conservation, with a counterexample outside the theorem scope. |
| Orthogonal watchlist | `HQS1-AF3D59D7A69DEA15F1B26A59052EE1EE` | Freeze `f(k)=chi(x([k]G))`, the access model, preprocessing, and recovery algorithm; then prove a spectrum/character-sum result that supports or closes the cluster. |
| Known-mechanism watchlist | `HQS1-64D6E4ED21BBC4BD41AC802368CA6DAF` | Complete primary-source and target-applicability extraction for the published `p+1` norm-one trace construction before any solver design. |
| Trace enabler | `HQS1-0AADF803634BB283C8E262ED605E8602` | Certify the reduced Dickson/trace circuit, fibers, saturation, recovery, and eliminated degree; compact circuit size is not accepted as solving degree. |
| Merged primary enabler | `HQS1-10622A7F9F18A904EF36A51EDA50AA7C` | Derive exact fixed-target fiber moments after repetition and stabilizer corrections; merge operationally into the relation-incidence obligation. |

Only the first three form the proposed review portfolio:

- primary: existing M16 solver-slope proposal;
- hedge: SGGM applicability barrier;
- enabler: exact Semaev relation incidence.

The other six are barrier or watchlist positions. They receive no
experiment budget and do not compete for the current execution slot.

## 5. Main exclusions

- Low-degree isogeny presentation is a matched representation control until
  it has an information source and complete recovery, not a new attack.
- Multihomogeneous, specialization, hybrid, saturation, and exceptional
  solver variants can move cost into fill-in, rare successful instances,
  recovery, or relation rank. They remain desk obligations, not bets.
- Character-partition and linear-complexity variants were merged into the
  one coordinate-character watchlist question.
- ML predictor, active-learning, and registry entries are research tooling,
  not ECDLP mechanisms.
- GLV quotient, division-polynomial, and infinity-density variants are not
  reopened. Current main already records the GLV-specific TASK-026 arm as
  bounded negative.
- The M16 seed is not counted as a new mechanism. It is bound to the
  existing canonical proposal.

## 6. Review status

Architecture, streaming, cryptanalysis-skeptic, cost, and portfolio-chair
passes were run in parallel. They were useful adversarial passes, but they
share the same project context and do not establish source or model-family
independence. They do not satisfy the existing five-review candidate gate.

No global novelty claim is made. Unread or incompletely ingested primary
literature remains a hard limitation, especially for the `p+1` watchlist.

## 7. Replay

```bash
python3 scripts/hypothesis_funnel.py --check
python3 scripts/test_hypothesis_funnel.py
```

The production artifact binds:

- Constitution v3.0;
- the exact 100-row brainstorming input;
- typed evidence and claim state;
- decision substrate and attack registry;
- source registry and current hypothesis ledger;
- the HYP-SELECT-003 current-main decision;
- baseline commit and generator policy.

Changing any bound scientific input or operator policy changes all instance
digests and the Merkle root. Review decisions are downstream and do not
rewrite the frozen bulk identities.

## 8. Boundary

This batch validates a scalable screening mechanism. It does not validate
autonomous scientific discovery. The generator still begins from a
human/model-authored 100-question pool, and its operators express mechanism,
cost, and test obligations rather than inventing exact mathematical maps.

The next scientific action remains review of the already canonical
non-executable M16 proposal. A future batch should replace more of the
brainstorming pool with typed unresolved child claims, reopening conditions,
target-property contradictions, unread source obligations, and missing
recovery or cost bridges.
