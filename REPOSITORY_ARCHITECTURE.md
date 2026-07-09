# Repository Architecture

This document is the repository-level map for the ECDLP Lean project. It does
not introduce new mathematical claims. Its job is to separate sources of truth,
generated views, operational controls, public surfaces, and cleanup candidates
so future agents can improve the repository without drifting the facts.

For the machine-readable companion, see `repo/ARTIFACTS.yaml`. For proposed
cleanup sequencing, see `repo/CLEANUP_PLAN.md`.

## Operating Principle

The repository is a verified research asset, not just a pile of proofs. Every
change should preserve three invariants:

1. The Lean kernel remains the only judge of proved mathematics.
2. `STATUS.md` and `data/stats.json` remain the canonical human/machine
   snapshot for live counts.
3. Cleanup happens by classification first, then review, then movement or
   deletion in a separate PR.

This matters because the project has several audiences at once: Lean reviewers,
cryptography readers, small-context agents, public-site visitors, and future
publication reviewers. Each audience needs a stable route through the repo.

## Layer Map

| Layer | Purpose | Primary paths | Edit policy |
|---|---|---|---|
| Kernel-verified proof surface | Machine-checked theorems and imports | `Ecdlp.lean`, `Ecdlp/`, `Ecdlp/Proved/`, `lakefile.toml`, `lean-toolchain`, `lake-manifest.json` | Edit only with Lean build/no-sorry/axiom gates. Do not move proved files without updating imports and `VERIFIED.md`. |
| Open proof targets | Candidate statements and target metadata | `Ecdlp/Targets/`, `targets/` | Open conjectures live here, not in `Ecdlp/Proved/`. Target JSON should track target stems. |
| Canonical corpus and overlays | Read-only claim corpus plus curated coverage overrides | `data/KG_CLAIM_FORMALIZATION_v1.csv`, `data/corpus_coverage_overrides.json`, `data/claim_traceability.jsonl` | Treat the corpus as vendored input. Curated overlays may be edited with review. |
| Verified ledger and trust boundary | Human-auditable theorem ledger and scope statements | `VERIFIED.md`, `TRUST_REPORT.md`, `ABSTRACT_SCOPE.md`, `BARRIERS.md`, `COVERAGE.md` | Keep counts delegated to `STATUS.md`/`data/stats.json`; keep scope wording adversarially honest. |
| Generated machine views | Derived stats, graphs, frontier maps, badges, and snapshots | `data/stats.json`, `data/frontier_map.json`, `data/knowledge_graph.json`, `data/knowledge_graph.md`, `badges/theorems.json`, `STATUS.md` | Do not hand-edit generated numbers. Change generators and regenerate. |
| Public surfaces | Static site and dashboard | `index.html`, `dashboard.html`, `assets/`, `fonts/`, `CNAME` | Site may be hand-maintained, but canonical counters should come from generated data or checked sync paths. |
| Research OS control plane | Active tasks, hypotheses, and agent orientation | `AGENTS.md`, `AGENT.md`, `CLAUDE.md`, `tasks/NEXT.md`, `experiments/HYPOTHESES.yaml` | Keep short, current, and executable by low-context agents. |
| Automation and scripts | CI, generators, checks, autonomous loops, server helpers | `.github/workflows/`, `scripts/`, `requirements.txt`, `prompts/` | Prefer explicit gates over narrative promises. Scripts that generate committed artifacts must document outputs. |
| Research notes | Durable mathematical strategy, maps, and reviewed reasoning | `notes/*.md`, `docs/`, `PUBLISHABLE_UNITS.md`, `WORK_SCOPE.md`, `DIRECTOR_CHARTER.md` | Keep as curated research memory. Link to canonical counts instead of copying them. |
| Experimental trace | Useful but noisy exploratory artifacts | `notes/ward/`, `scratch/`, some generated reports | Do not delete in this PR. Classify, preserve provenance, and ask Claude/human review before archive/delete. |

## Source Of Truth Matrix

| Question | Source of truth | Derived or supporting views |
|---|---|---|
| How many verified ledger rows/distinct results/modules exist now? | `data/stats.json`, generated from `VERIFIED.md` | `STATUS.md`, `badges/theorems.json`, site counters |
| What is actually proved? | `Ecdlp/Proved/*.lean` plus `VERIFIED.md` | `data/knowledge_graph.json`, `data/knowledge_graph.md` |
| What corpus claims exist? | `data/KG_CLAIM_FORMALIZATION_v1.csv` | `data/frontier_map.json`, `targets/*.json` |
| Which corpus claims are verified/partial/blocked/etc.? | `data/frontier_map.json` plus `data/corpus_coverage_overrides.json` | `STATUS.md`, `COVERAGE.md`, dashboard |
| What is safe to claim publicly? | `STATUS.md`, `TRUST_REPORT.md`, `ABSTRACT_SCOPE.md`, `notes/SECURITY_SCOPE.md` | `README.md`, `ONE_PAGE_SUMMARY.md`, `PUBLISHABLE_UNITS.md` |
| What should an agent work on next? | `tasks/NEXT.md` | `experiments/HYPOTHESES.yaml`, `AGENTS.md`, `WORK_SCOPE.md` |
| What should be archived or deleted? | `repo/CLEANUP_PLAN.md` after review | `repo/ARTIFACTS.yaml`, Claude review comments |

## Generated Artifact Rules

Generated artifacts should be updated through their generators whenever
possible:

| Artifact | Generator/check |
|---|---|
| `data/stats.json`, `badges/theorems.json` | `scripts/gen_stats.py` |
| `STATUS.md` | `scripts/gen_status.py` |
| `data/frontier_map.json` | `scripts/build_frontier_map.py` |
| `data/knowledge_graph.json`, `data/knowledge_graph.md` | `scripts/build_knowledge_graph.py` |
| `COVERAGE.md` | `scripts/coverage_report.py` |
| `dashboard.html` | `scripts/build_dashboard.py` |
| obvious cross-surface drift | `scripts/check_status_consistency.py`, `scripts/check_counts.py` |

If a generated artifact must be hand-edited in an emergency, the follow-up PR
should either encode the change in the generator or mark the artifact as
hand-maintained in `repo/ARTIFACTS.yaml`.

## Cleanup Policy

This branch intentionally avoids destructive cleanup. The first pass is
classification.

Cleanup should follow this sequence:

1. Classify each area as canonical, generated, curated note, operational,
   experimental trace, scratch, static asset, or archive candidate.
2. Ask Claude for adversarial review of misclassifications and deletion risks.
3. Move/archive only files with clear provenance and no import/site references.
4. Run generator checks and Lean/CI gates after every movement that touches
   imports, generated views, links, or public surfaces.

High-risk areas:

- `Ecdlp/Proved/`: moving files changes import topology and proof review paths.
- `VERIFIED.md`: changing rows changes stats and public claims.
- `data/KG_CLAIM_FORMALIZATION_v1.csv`: vendored corpus; do not reformat.
- `notes/ward/`: noisy, but may contain provenance for Ward/EDS work.
- `scratch/`: may contain unpromoted Lean experiments; classify before removal.

## PR Discipline

Use separate PRs for separate kinds of risk:

| PR type | Allowed risk |
|---|---|
| Architecture/classification | Adds maps, manifests, review packets; no file deletion. |
| Generator/gate | Changes scripts and generated artifacts together. |
| Lean proof | Changes Lean surface, `VERIFIED.md`, stats, graph, and gates together. |
| Public site | Changes site/dashboard; checks counters and wording against canonical data. |
| Archive/delete | Moves or deletes classified artifacts after review. |

This keeps Claude review useful: reviewers can attack one risk class at a time.

## Claude Review Contract

When Claude reviews this architecture, ask it to assume the map is wrong until
proved otherwise. The review should answer:

1. Which files or directories are misclassified?
2. Which generated artifacts are still being hand-edited or checked weakly?
3. Which cleanup candidates must not be deleted?
4. Which docs still duplicate canonical counts or stale workflow names?
5. Which parts of the repo would confuse a small-context agent?
6. What one follow-up PR would most improve long-term maintainability?

The intended result is not immediate deletion. It is a shared operating model
for all future work.
