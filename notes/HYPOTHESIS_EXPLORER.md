# Hypothesis-space guide

## What can and cannot be mapped

The mathematical space of ECDLP ideas is open-ended. New transformations,
information sources, recovery methods, cost models, and combinations can always
be proposed, so the repository does not claim a complete map of every possible
hypothesis.

The actionable frontier is finite relative to the current evidence snapshot and
the grammar in `repo/HYPOTHESIS_GENERATION_V0.json`. Its canonical generated map
is:

- `data/knowledge_graph.json` for machine use;
- `data/knowledge_graph.md` for a rendered view;
- `data/typed_evidence_state.json` for mechanism and target-property cells;
- `data/research_engine_state.json` for generated research-question seeds;
- `data/research_engine_shadow_intake.json` for non-executable follow-up stubs.

This is a versioned evidence-bounded projection, not a Cartesian product of
keywords and not a completeness theorem.

## Identity and deduplication

A generated research-question seed is identified by its typed mechanism and
cell, the three synthesis axes, route, threat model, and exact typed-evidence
and claim-state digests. The cell carries its construction, requirements, cost
quantity, and evidence boundary. Current seeds do not instantiate a proposal's
fixed-target semantics, recovery map, non-generic information source,
preprocessing, amortization, or complete changed-cost signature.

Those additional fields belong to proposal identity. They become mandatory
only if a seed later passes intake and is expanded into a proposal. No current
seed has done so, and the current projection contains zero quality-cleared
proposals.

Two cells may share the same three synthesis axes and still represent different
scientific questions. In the current state,
`CELL-M-PKC-SMOOTH-M16` and `CELL-M-PKC-AUXILIARY-CURVE` share the same feature,
primitive, and unresolved-question IDs, but differ in their exact construction,
target-property status, evidence, and admissible next step.

## Current finite frontier

The generated state has seven typed cells, two seed-eligible cells, four shadow
stubs, zero quality-cleared proposals, zero retained candidate snapshots, and
zero experiment authorizations. A seed or stub is a research question, not a
hypothesis, candidate, or route promotion.

TASK-015 assigns the sole next desk priority to
`CELL-M-PKC-SMOOTH-M16` and its `desk_cost_contract` stub. The arithmetic
applicability predicates are already resolved. The remaining work is limited to
the unresolved representation, symbolic size, recovery, independence, memory,
preprocessing, and total-cost fields of `CQ-SEMAEV-S17-SYSTEM-COST`.

`CELL-M-PKC-AUXILIARY-CURVE` stays parked until a primary source supplies a
finite family or search domain with a completeness criterion. An unbounded
search over auxiliary curves cannot produce an honest negative verdict.

## Authorization boundary

The selected desk question authorizes no materialized S17 or recursive
polynomial system and no solver run, Sage, msolve, F4, or parameter sweep. It
also authorizes no secp256k1 discrete-log computation, novelty claim while CANS
2018 remains unread, or route promotion. The valid terminal outputs are an
exact symbolic cost bridge, a narrowly scoped blocker, or zero retained
hypotheses.

## Historical model-fleet path

The older model-fleet explorer remains available only for reproducibility of
historical workflows. It is not the canonical search or mapping path and cannot
authorize a proposal or experiment. The canonical current path is the typed
evidence state, generated seed layer, shadow intake, and graph projection listed
above.

## Ranking-model boundary

`scripts/hypothesis_ranker.py` is the automatic ranking-model boundary. Its
small specification and parameter artifact are stored in Git; a generated state
binds them to the current funnel and review-record digests. Large language-model
weights are never repository artifacts. If a future model is too large for the
one-megabyte ranker limit, Git stores only its external URI, license,
reproduction metadata, and SHA-256.

Reviewed labels persist in `data/hypothesis_review_ledger.jsonl`. Each append-only
record binds the review digest, batch Merkle root, semantic signature, and frozen
feature snapshot, so a later batch may change its queue without erasing or
silently reinterpreting earlier supervision.

The current model is deliberately untrained. Three migrated portfolio reviews
exist, but all three record source, model-family, and context independence as
false. Consequently they are preserved as research provenance and excluded
from training. Activation requires at least 30 eligible independent labels,
both positive and negative examples, five families, two reviewers, three native
outcomes, and frozen-family holdout validation.

`scripts/train_hypothesis_ranker.py` implements deterministic L2-regularized
logistic training and leave-one-family-out validation using only the Python
standard library. Its CI mode reports the unmet gate and exits without writing
weights. This keeps the training path continuously tested while preventing a
synthetic or undersized dataset from creating an apparently learned model.

Even after those gates pass, ranker v0 remains shadow-only. It may compare
ordering quality against future outcomes, but it cannot alter deterministic hard
gates, recommend or authorize an experiment, promote a route, or target a real
secp256k1 key.
