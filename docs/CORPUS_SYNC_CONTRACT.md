# Corpus synchronization contract

## Purpose

KeyAI needs more than a folder of papers. A long-horizon research agent must know which source is current, which older version remains historically relevant, which threat model a result belongs to, what was actually reviewed, and what evidence is still missing.

The canonical machine-readable instance is `domains/ecdlp/corpus_manifest.json`. The reusable schema is `domains/corpus_manifest.schema.json`. Any future domain can adopt the same contract without inheriting ECDLP-specific assumptions.

## Invariants

1. Source history is append-only. A superseded paper remains present and points to its replacement.
2. A source card is metadata, not an accepted mathematical claim.
3. Claim promotion requires an exact locator, assumptions, scope, evidence class, and applicability statement.
4. Classical plain ECDLP, auxiliary-input or implementation attacks, and fault-tolerant quantum ECDLP are separate threat models.
5. Local binary artifacts are hash-pinned. Remote-only primaries are labeled as such.
6. Missing primaries stay visible and blocked rather than being silently replaced by secondary summaries.
7. Literature intake does not authorize experiments. A proposal still has to pass `repo/ECDLP_DECISION_SUBSTRATE.json`.
8. Negative evidence, parked routes, and stop conditions are retained so another agent does not repeat the same work without a new premise.

## Agent workflow

A research agent should:

1. load the domain registry and its `corpus_manifest`;
2. filter sources by the active threat model;
3. prefer `current_version: true`, while following relations to understand prior work;
4. inspect `claim_extraction_status` before treating a source as structured evidence;
5. use audit snapshots to identify what changed since the previous review;
6. submit any candidate mechanism to the decision gate before allocating experiments or proof work;
7. preserve the source ID and exact evidence locator in every downstream claim, task, experiment, and theorem note.

## What this contract does not establish

It does not prove completeness of the literature, semantic correctness of every source, current hardware feasibility, or a solution to the plain secp256k1 ECDLP. It creates a falsifiable and reviewable memory layer so future models spend context on the frontier rather than reconstructing project history.
