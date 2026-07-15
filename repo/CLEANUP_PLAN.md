# Cleanup Plan

> **EXECUTED (tranche 1, 2026-07 — see `ROADMAP.md` §4):** `notes/ward/` → `archive/ward/`,
> `scratch/` → `archive/scratch/`, `generator-report.md` → `archive/`, `platform/` →
> `archive/platform/` (platform-ci retired), superseded strategy/review docs → `archive/docs/`.
> This plan is kept as the decision record; remaining candidates live in `repo/ARTIFACTS.yaml`.

This plan is deliberately conservative. The current branch classifies the repo;
it does not delete, rename, or move risky files. The next cleanup PR should only
act after Claude or human review confirms the classification.

## Goals

- Make the repo easier for Claude, Codex, and humans to navigate.
- Preserve mathematical provenance and Lean correctness.
- Reduce stale duplicate truth without hiding research history.
- Separate current product surface from exploratory trace.

## Non-Goals For This PR

- No deletion of Lean files.
- No movement of `Ecdlp/Proved/` modules.
- No rewrite of the vendored corpus CSV.
- No bulk archive of `notes/ward/` or `scratch/`.
- No dashboard rewrite beyond separately reviewed generator work.

## Phase 0: Architecture Baseline

Status: this branch.

Deliverables:

- `REPOSITORY_ARCHITECTURE.md`
- `repo/ARTIFACTS.yaml`
- `repo/CLEANUP_PLAN.md`
- `CLAUDE_REVIEW_PACKET.md`
- small orientation links from `README.md` and `AGENTS.md`

Exit criteria:

- Claude can review the whole repo architecture without guessing which files
  are canonical, generated, scratch, or archival.
- No destructive change is required to validate this phase.

## Phase 1: Validate The Manifest

Status: partly included in this staging branch.

Actions:

1. Add a small path-existence validator for `repo/ARTIFACTS.yaml`. Done:
   `scripts/check_repo_artifacts.py`.
2. Teach CI to run it. Done in `ci.yml`; docs-sync also runs it.
3. Mark generated artifacts in one place rather than relying on scattered prose.
4. Check that public docs link to `STATUS.md` instead of duplicating counts.

Risks:

- YAML parsing adds a dependency if done carelessly. The current validator uses
  a tiny stdlib parser for the subset of YAML shape used by the manifest.

## Phase 2: Dashboard And Site Sync Health

Proposed follow-up PR.

Actions:

1. Make `scripts/build_dashboard.py` robust across Windows and Linux.
2. Add a visible Sync Health block to `dashboard.html`.
3. Ensure `index.html` counters are updated only by a clear sync path.
4. Extend `scripts/check_status_consistency.py` only where values are actually
   machine-readable.

Risks:

- A dashboard-only PR can look cosmetic while accidentally changing public
  claims. Keep source counters tied to `data/stats.json` and `data/frontier_map.json`.

## Phase 3: Archive Experimental Trace

Proposed follow-up PR after review.

Candidate areas:

| Path | Proposed action | Why not delete immediately |
|---|---|---|
| `notes/ward/` | Move to `archive/ward-induction/` or add a stronger README marking it as trace | It may preserve Ward/EDS proof-search provenance. |
| `scratch/` | Move useful stems into `Ecdlp/Targets/` or `notes/`; archive the rest | Some files may be seeds for future formal targets. |
| `generator-report.md` | Either mark generated with a command or archive as a historical report | Its ownership is unclear. |

Before movement:

- Search all links/imports/references.
- Check whether any CI or site navigation exposes the path.
- Preserve a short provenance README in the archive directory.
- Keep movement in a PR separate from mathematical edits.

## Phase 4: Consolidate Orientation Docs

Proposed follow-up PR.

Actions:

1. Decide whether `READ_FIRST.md`, `AGENTS.md`, `AGENT.md`, and `CLAUDE.md`
   each have distinct jobs.
2. Remove duplicate explanations of counts and current status.
3. Keep `STATUS.md` as the live snapshot and `REPOSITORY_ARCHITECTURE.md` as
   the repository map.
4. Add "where to start" routes for three audiences: proof reviewer, public
   reader, and agent.

Risks:

- Over-consolidation can erase useful operating detail. Prefer link-and-slim
  over merging everything into one long document.

## Phase 5: Proof Surface Hygiene

Only after the documentation and archive policy settle.

Actions:

1. Audit import topology under `Ecdlp/Proved/`.
2. Keep module naming stable unless a proof-specific PR justifies a move.
3. Ensure every new theorem row updates `VERIFIED.md`, stats, graph, and checks.

Risks:

- Renaming Lean modules is high-friction and can obscure review history. Do it
  only for real proof-maintenance value.

## Claude Gate

Before any archive/delete PR, ask Claude:

1. What evidence shows this file or directory is inactive?
2. What future proof/research path could still need it?
3. Which links/imports/site references break if it moves?
4. Should it be deleted, archived, summarized, or left alone?
5. What is the smallest reversible action?

The default action is to preserve provenance until the answer is clear.
