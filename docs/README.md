# Documentation map

This directory contains curated explanatory material. It is not the source of
live counters or theorem status.

## Start with the canonical surfaces

| Need | Source |
|---|---|
| Current numbers and honest project status | [`../STATUS.md`](../STATUS.md) |
| Unified navigation across verified results | [`../VERIFIED_ALL.md`](../VERIFIED_ALL.md) |
| ECDLP theorem ledger | [`../VERIFIED.md`](../VERIFIED.md) |
| ResearchOS theorem ledger | [`../VERIFIED_RESEARCHOS.md`](../VERIFIED_RESEARCHOS.md) |
| Whole-repository ownership and edit policy | [`../REPOSITORY_ARCHITECTURE.md`](../REPOSITORY_ARCHITECTURE.md) |
| Machine-readable decision and lifecycle contracts | [`../repo/README.md`](../repo/README.md) |
| Active work router | [`../tasks/NEXT.md`](../tasks/NEXT.md) |

## Documentation areas

- `domains/` at the repository root owns domain-specific contracts and route maps.
- `notes/INDEX.md` is the curated research-memory index.
- `notes/reviews/` contains dated promotion, audit, and review records.
- `repo/` contains machine-readable product, decision, evidence, lifecycle, and
  artifact-ownership contracts.
- `archive/` is frozen history and must not be treated as current state.

## Editing rule

Do not copy live counts into documentation. Link to `STATUS.md` or the relevant
machine source. If a document starts acting like a second source of truth,
replace duplicated state with a link or make it a generated artifact.
