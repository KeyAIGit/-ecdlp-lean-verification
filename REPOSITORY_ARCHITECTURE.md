# Repository Architecture

This document is the repository-level map for the ECDLP Lean project. It does
not introduce new mathematical claims. Its job is to separate sources of truth,
generated views, operational controls, public surfaces, and cleanup candidates
so future agents can improve the repository without drifting the facts.

Machine-readable companions:

- `repo/ARTIFACTS.yaml` classifies every repository file by ownership and edit policy.
- `repo/FORMAL_SUBSTRATE.json` maps result families, critical dependencies, blockers,
  release disposition, and open targets.
- `repo/ECDLP_DECISION_SUBSTRATE.json` decides which attack routes apply to the
  exact secp256k1 objective, what evidence would promote them, and which missing
  foundations are worth building now.
- `repo/PRODUCT_MODEL.json` owns the product category, current-vs-future
  capability boundary, public rhetoric, customer hypotheses, and MVP exit gate.
- `repo/PILOT_PROTOCOL.json` owns TASK-011 qualification, safety, measurements,
  evidence schema, and the discovery disposition that may unlock TASK-012.
- `repo/AUTOMATION_INVENTORY.json` classifies every workflow.
- `repo/BRANCH_INVENTORY.json` records the dated, non-destructive remote-branch
  snapshot; ancestry alone never authorizes deletion.
- `repo/FINAL_REVIEW_PACKET.md` is the frozen adversarial-review contract for
  draft PR #235. It is historical input, not the final packet for this branch;
  `TASK-010` owns the eventual whole-program review.

Their checks live under `scripts/check_*inventory.py`,
`scripts/check_formal_substrate.py`, `scripts/check_ecdlp_decision_substrate.py`,
`scripts/check_product_model.py`, and `scripts/check_repo_artifacts.py`.

## Operating Principle

The repository is a verified research asset, not just a pile of proofs. Every
change should preserve three invariants:

1. Lean elaboration and the kernel remain the proof authority; uses of
   `native_decide` additionally trust the compiler and are disclosed by the axiom audit.
2. `STATUS.md` and `data/stats.json` remain the canonical human/machine
   snapshot for live counts.
3. Cleanup happens by classification first, then review, then movement or
   deletion in a separate PR.
4. Product claims resolve to `repo/PRODUCT_MODEL.json`, while pilot evidence and
   disposition resolve to `repo/PILOT_PROTOCOL.json`; a reference deployment is
   never presented as a validated hosted product or as customer traction.

This matters because the project has several audiences at once: Lean reviewers,
cryptography readers, small-context agents, public-site visitors, and future
publication reviewers. Each audience needs a stable route through the repo.

## Layer Map

| Layer | Purpose | Primary paths | Edit policy |
|---|---|---|---|
| Kernel-verified proof surface | Machine-checked theorems and imports | `Ecdlp.lean`, `Ecdlp/`, `Ecdlp/Proved/`, `lakefile.toml`, `lean-toolchain`, `lake-manifest.json` | Edit only with Lean build/no-sorry/axiom gates. Do not move proved files without updating imports and `VERIFIED.md`. |
| Open proof targets | Candidate statements and target metadata | `Ecdlp/Targets/`, `targets/` | Open conjectures live here, not in `Ecdlp/Proved/`. Target JSON should track target stems. |
| Canonical corpus and overlays | Read-only claim corpus plus curated coverage overrides | `data/KG_CLAIM_FORMALIZATION_v1.csv`, `data/corpus_coverage_overrides.json`, `data/claim_traceability.jsonl` | Treat the corpus as vendored input. Curated overlays may be edited with review. |
| ECDLP decision layer | Target-specific route applicability, evidence gates, and foundation priority | `repo/ECDLP_DECISION_SUBSTRATE.json` | The JSON is canonical. Its Markdown view is generated. A missing Mathlib module is not automatically a project priority. |
| Product and pilot decision layer | Product category, reference-deployment boundary, customer hypotheses, discovery evidence, safety, and MVP gates | `repo/PRODUCT_MODEL.json`, `repo/PILOT_PROTOCOL.json` | Both JSON contracts are canonical. Public surfaces are generated from them; planned features and unvalidated users remain explicit. |
| Verified ledger and trust boundary | Human-auditable theorem ledger and scope statements | `VERIFIED.md`, `TRUST_REPORT.md`, `ABSTRACT_SCOPE.md`, `BARRIERS.md`, `COVERAGE.md` | Keep counts delegated to `STATUS.md`/`data/stats.json`; keep scope wording adversarially honest. |
| Generated machine views | Derived stats, registries, graphs, audits, badges, and snapshots | `data/stats.json`, `data/{result_registry,source_registry,knowledge_graph}.json`, `Ecdlp/LedgerAxiomAudit.lean`, `badges/theorems.json`, `STATUS.md` | Do not hand-edit. Change generators and regenerate. |
| Public surfaces | Product thesis, operator workspace, route explorer, and external-pilot contract | `index.html`, `dashboard.html`, `explore.html`, `pilot.html`, `assets/`, `fonts/`, `CNAME` | Generate all four pages through `scripts/site_generator.py`; canonical counters must remain useful without JavaScript. |
| Research OS control plane | Active tasks, hypotheses, formal architecture, automation, and agent orientation | `AGENTS.md`, `CLAUDE.md`, `ROADMAP.md`, `tasks/NEXT.md`, `experiments/HYPOTHESES.yaml`, `REPOSITORY_ARCHITECTURE.md`, `repo/` | Keep short, current, and executable by low-context agents. |
| Reproducible experiments | Non-kernel scripts, manifests, and measured evidence | `experiments/` | Measurements are evidence, never proofs. Parked hypotheses authorize no new runs. |
| Automation and scripts | CI, generators, checks, autonomous loops, server helpers | `.github/workflows/`, `scripts/`, `requirements.txt`, `prompts/` | Prefer explicit gates over narrative promises. Scripts that generate committed artifacts must document outputs. |
| Research notes | Durable mathematical strategy, maps, and reviewed reasoning | `notes/*.md`, `docs/`, `PUBLISHABLE_UNITS.md` | Keep as curated research memory. Link to canonical counts instead of copying them. |
| Archive (frozen) | Superseded docs and exploratory traces, preserved for provenance | `archive/` (docs, ward, scratch, platform, generator-report) | Do not delete in ordinary work. Classify, preserve provenance, and use a dedicated retention audit before archive/delete. |

## Source Of Truth Matrix

| Question | Source of truth | Derived or supporting views |
|---|---|---|
| How many verified ledger rows/distinct results/modules exist now? | `data/stats.json`, generated from `VERIFIED.md` | `STATUS.md`, `badges/theorems.json`, site counters |
| What is actually proved? | `Ecdlp/Proved/*.lean` plus `VERIFIED.md` | `data/knowledge_graph.json`, `data/knowledge_graph.md` |
| Which exact declarations does each ledger row cite? | `data/result_registry.json` | `Ecdlp/LedgerAxiomAudit.lean` |
| What is the formal critical path and release boundary? | `repo/FORMAL_SUBSTRATE.json` | semantic edges in `data/knowledge_graph.json` |
| Which route should be pursued for the exact secp256k1 objective? | `repo/ECDLP_DECISION_SUBSTRATE.json` | `repo/ECDLP_DECISION_SUBSTRATE.md`, decision edges in `data/knowledge_graph.json` |
| What product exists now, for whom, and what qualifies as MVP? | `repo/PRODUCT_MODEL.json` | `index.html`, `dashboard.html`, `explore.html`, `pilot.html`, `tasks/NEXT.md` |
| What may TASK-011 collect, what evidence closes discovery, and what may unlock TASK-012? | `repo/PILOT_PROTOCOL.json` | `.github/ISSUE_TEMPLATE/keyai-pilot.yml`, `pilot.html`, `STATUS.md` |
| What detailed evidence exists for each attack family? | `data/attack_registry.json` | `notes/RESEARCH_MAP.md` |
| What corpus claims exist? | `data/KG_CLAIM_FORMALIZATION_v1.csv` | `data/frontier_map.json`, `targets/*.json` |
| Which corpus claims are verified/partial/blocked/etc.? | `data/frontier_map.json` plus `data/corpus_coverage_overrides.json` | `STATUS.md`, `COVERAGE.md`, dashboard |
| What is safe to claim publicly? | `repo/PRODUCT_MODEL.json`, `STATUS.md`, `TRUST_REPORT.md`, `ABSTRACT_SCOPE.md`, `notes/SECURITY_SCOPE.md` | generated site, `README.md`, `PUBLISHABLE_UNITS.md` |
| What should an agent work on next? | `tasks/NEXT.md` | `experiments/HYPOTHESES.yaml`, `AGENTS.md`, `ROADMAP.md` |
| What must any future candidate report and pass? | `experiments/framework/candidate_run.schema.json` plus `candidate_contract.py` | deterministic positive/negative fixtures and independent `ec_oracle.py` validation |
| What should be archived or deleted? | `repo/CLEANUP_PLAN.md` after a dedicated retention audit | `repo/ARTIFACTS.yaml`, reference scans, and the audit record |

## Generated Artifact Rules

Generated artifacts should be updated through their generators whenever
possible:

| Artifact | Generator/check |
|---|---|
| `data/stats.json`, `badges/theorems.json` | `scripts/gen_stats.py` |
| `STATUS.md` | `scripts/gen_status.py` |
| `data/frontier_map.json` | `scripts/build_frontier_map.py` |
| `data/knowledge_graph.json`, `data/knowledge_graph.md` | `scripts/build_knowledge_graph.py` |
| `repo/ECDLP_DECISION_SUBSTRATE.md` | `scripts/build_ecdlp_decision_view.py` |
| `data/result_registry.json` | `scripts/gen_result_registry.py` |
| `Ecdlp/LedgerAxiomAudit.lean` | `scripts/gen_axiom_audit.py` |
| `COVERAGE.md` | `scripts/coverage_report.py` |
| `index.html`, `dashboard.html`, `explore.html`, `pilot.html` | `scripts/build_dashboard.py` compatibility entry point → `scripts/site_generator.py` |
| obvious cross-surface drift | `scripts/check_status_consistency.py`, `scripts/check_counts.py` |
| repository artifact classification | `scripts/check_repo_artifacts.py` |
| formal dependency/release map | `scripts/check_formal_substrate.py` |
| ECDLP route and foundation decisions | `scripts/check_ecdlp_decision_substrate.py` |
| product category, capability, and public claim boundary | `scripts/check_product_model.py` |
| generated-artifact closure | `scripts/check_generated_fixpoint.py --check` |

If a generated artifact must be hand-edited in an emergency, the follow-up PR
should either encode the change in the generator or mark the artifact as
hand-maintained in `repo/ARTIFACTS.yaml`.

## Research And Product Maps

The repository deliberately has four related but non-interchangeable maps:

1. `data/frontier_map.json` classifies the imported claim corpus. Its priority
   numbers describe corpus coverage, not attack value.
2. `repo/FORMAL_SUBSTRATE.json` records the release-facing Lean dependency
   frontier. A blocked theorem can be valuable library work without being the
   next cryptanalytic priority.
3. `repo/ECDLP_DECISION_SUBSTRATE.json` owns the project decision for the exact
   plain single-target secp256k1 problem. It may defer a large formal gap when
   the route's prerequisite is false or no candidate needs the theorem.
4. `repo/PRODUCT_MODEL.json` is orthogonal to those mathematical maps. It
   decides what KeyAI is as a product and what the reference repository proves
   about that product. `repo/PILOT_PROTOCOL.json` owns the bounded external
   discovery contract and evidence required before product implementation expands.

The target parameters come from SEC 2. The GLV structure is traced to Gallant,
Lambert, and Vanstone. The quantum boundary starts with Shor and currently
tracks the 2026 logical-resource estimate by Luo et al.; that estimate is not a
claim that suitable fault-tolerant hardware exists.

## Cleanup Policy

This branch intentionally avoids destructive cleanup. The first pass is
classification.

Cleanup should follow this sequence:

1. Classify each area as canonical, generated, curated note, operational,
   experimental trace, scratch, static asset, or archive candidate.
2. Review misclassifications and deletion risks at a stable checkpoint; use an
   independent reviewer when one is available.
3. Move/archive only files with clear provenance and no import/site references.
4. Run generator checks and Lean/CI gates after every movement that touches
   imports, generated views, links, or public surfaces.

High-risk areas:

- `Ecdlp/Proved/`: moving files changes import topology and proof review paths.
- `VERIFIED.md`: changing rows changes stats and public claims.
- `data/KG_CLAIM_FORMALIZATION_v1.csv`: vendored corpus; do not reformat.
- `archive/ward/`: noisy, but may contain provenance for Ward/EDS work (frozen).
- `archive/scratch/`: unpromoted Lean experiments, frozen; revive via git mv.

## Review Discipline

Repository-wide normalization landed in PR #236. Subsequent proof, product,
generator, site, and archive risks use separate branches and scoped PRs. The
owner delegated merge authority on 2026-07-22: green required CI, explicit
scope, and rollback safety are the merge gate. Independent adversarial review
remains useful but is not blocking while no other reviewer is connected.
Destructive branch/file cleanup remains a separate inventory-first action.

## Independent Review Contract

When an independent reviewer audits this architecture, ask it to assume the map
is wrong until proved otherwise. The review should answer:

1. Which files or directories are misclassified?
2. Which generated artifacts are still being hand-edited or checked weakly?
3. Which cleanup candidates must not be deleted?
4. Which docs still duplicate canonical counts or stale workflow names?
5. Which parts of the repo would confuse a small-context agent?
6. What one follow-up PR would most improve long-term maintainability?

The intended result is not immediate deletion. It is a shared operating model
for all future work.
