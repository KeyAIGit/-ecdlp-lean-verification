# NEXT - active Research OS queue

This file is the small-context task queue. Keep it short: 3-7 active tasks,
each with a contract that an agent can execute without rediscovering the
project from scratch.

Canonical start order for agents:

1. Read `STATUS.md`.
2. Read this file.
3. Read `experiments/HYPOTHESES.yaml` only when the task touches hypotheses,
   experiments, frontier interpretation, or publication planning.

If prose elsewhere conflicts with `STATUS.md`, `STATUS.md` wins. If this file
conflicts with `STATUS.md`, update both in the same PR and run the consistency
checks.

## Active Tasks

### TASK-001 - Harden the Research OS truth layer

Kind: ops | data | site
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: Low-context agents and public readers need one reliable route
from machine facts to next work.
Inputs:
- `STATUS.md`
- `data/stats.json`
- `data/frontier_map.json`
- `data/knowledge_graph.json`
- `index.html`
- `dashboard.html`
Expected output:
- A drift gate that verifies stats, frontier, graph, status, site counters,
  task queue, and hypothesis registry agree at the obvious machine-readable
  seams.
Exit criteria:
- `python3 scripts/check_counts.py` passes.
- `python3 scripts/gen_stats.py --check` passes.
- `python3 scripts/check_status_consistency.py` passes.
Files allowed to edit:
- `scripts/check_status_consistency.py`
- `scripts/gen_status.py`
- `.github/workflows/ci.yml`
- `.github/workflows/docs-sync.yml`
- `STATUS.md`
- `tasks/NEXT.md`
- `experiments/HYPOTHESES.yaml`

### TASK-002 - Export small/medium/large agent bundles

Kind: ops | agent
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: Small-context agents should not waste turns reconstructing the
same orientation from scattered prose.
Inputs:
- `STATUS.md`
- `tasks/NEXT.md`
- `data/stats.json`
- `data/frontier_map.json`
- `VERIFIED.md`
- `BARRIERS.md`
- `notes/FOUNDATIONS.md`
- `notes/SECURITY_SCOPE.md`
Expected output:
- `scripts/export_agent_bundle.py`
- Generated bundle files under a documented output path or ignored cache path.
Exit criteria:
- Small bundle contains only the current status, active queue, and core machine
  counts.
- Medium bundle adds ledger/barrier/security/foundation context.
- Large bundle can include graph excerpts and task-relevant Lean files.
Files allowed to edit:
- `scripts/export_agent_bundle.py`
- `AGENTS.md`
- `README.md`
- `.gitignore`

### TASK-003 - Add dashboard Sync Health

Kind: site | data
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: The public surface should show whether the Research OS state is
fresh and internally consistent.
Inputs:
- `scripts/check_status_consistency.py`
- `data/stats.json`
- `data/frontier_map.json`
- `data/knowledge_graph.json`
- `STATUS.md`
- `scripts/build_dashboard.py`
Expected output:
- A dashboard section or tab that reports sync health, canonical counts, and
  regeneration commands.
Exit criteria:
- Dashboard displays current ledger rows, distinct results, frontier
  completeness, graph theorem count, and last regeneration source.
- Consistency check covers the machine-readable values used by the dashboard.
Files allowed to edit:
- `scripts/build_dashboard.py`
- `dashboard.html`
- `index.html`
- `scripts/check_status_consistency.py`

### TASK-004 - Formalize experiment manifests

Kind: experiment | data
Hypothesis: `H5_SEMAEV_WINDOW`
Why it matters: Negative computational results should compress the search space
instead of disappearing into notes.
Inputs:
- `experiments/HYPOTHESES.yaml`
- `notes/ENGINE.md`
- `notes/SECURITY_SCOPE.md`
- `BARRIERS.md`
Expected output:
- A minimal experiment manifest schema for reproducible runs.
- A first Semaev/Groebner benchmark task contract.
Exit criteria:
- Every experiment run records hypothesis id, script, input dataset, commit,
  machine profile, and result summary.
Files allowed to edit:
- `experiments/`
- `datasets/`
- `scripts/`
- `notes/`

### TASK-005 - Extend the closed keystone: geometric `E[n]` + P-256 cardinality

Kind: theorem | research
Hypothesis: `H2_GLV_SUBGROUP_VS_WHOLE_GROUP`
Why it matters: The strong keystone `#E(𝔽_p) = n` is **proved** for secp256k1
(no Hasse/Schoof — curve-specific certificate, `CurveCardinalityExact.lean`,
2026-07-13), and with it `E(𝔽_p) = ⟨G⟩`, cyclicity, and the unconditional GLV
eigenvalue all landed (`CurveFullGroup.lean`, `PointGroupEquiv.lean`). The
original TASK-005 scoping goal is therefore complete. What the closure exposes
next: (a) the **geometric torsion structure** `E[n] ≅ (ℤ/n)²` needs points over
field extensions — still a genuine Mathlib gap; (b) the certificate exploits
`j = 0`, so **P-256's `#E = n` stays open** (Hasse or a new certificate route).
Inputs:
- `notes/POINT_COUNTING_KEYSTONE.md` (status banner marks the closure)
- `Ecdlp/Proved/CurveCardinalityExact.lean`, `CurveFullGroup.lean`
- `BARRIERS.md`
Expected output:
- A decomposition memo for the *next* smallest missing foundation: either the
  extension-field point machinery behind `E[n] ≅ (ℤ/n)²`, or a P-256
  cardinality route. No weakening, no `sorry`.
Exit criteria:
- Either a proved rung, or a frozen blocker memo naming the smallest missing
  Mathlib foundation with an honest effort estimate.
Files allowed to edit:
- `notes/POINT_COUNTING_KEYSTONE.md`
- `BARRIERS.md`
- new `Ecdlp/Targets/` stem (open, not built) if a partial rung is stated

### TASK-006 - Prepare publication boundary track

Kind: publication
Hypothesis: `H6_PUBLICATION_BOUNDARY_TRACK`
Why it matters: The verified substrate already supports useful publications
even without a subgeneric ECDLP breakthrough.
Inputs:
- `PUBLISHABLE_UNITS.md`
- `VERIFIED.md`
- `data/knowledge_graph.json`
- `notes/SECURITY_SCOPE.md`
- `TRUST_REPORT.md`
Expected output:
- One publication unit upgraded to an executable outline with claims,
  theorem references, figures, and trust boundaries.
Exit criteria:
- The outline can be reviewed independently from the full repository.
Files allowed to edit:
- `PUBLISHABLE_UNITS.md`
- `docs/`
- `notes/`

### TASK-007 - Consolidation tranche 2 (ROADMAP.md §4)

Kind: ops | agent | docs
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: Tranche 1 (archive of ward/scratch/platform/superseded strategy
docs, ROADMAP.md as the one strategy file) is executed. Fewer prose surfaces =
structurally less drift; tranche 2 finishes the root-doc consolidation and
declares v0.1.
Inputs:
- `ROADMAP.md` (§4, tranche-2 table)
- `REPOSITORY_ARCHITECTURE.md` + `repo/CLEANUP_PLAN.md` (map + tranche-1 record)
- `README.md`, `READ_FIRST.md`, `ONE_PAGE_SUMMARY.md`, `RESEARCH_MAP.md`
- `AGENT.md`, `AGENTS.md`
Expected output:
- ONE_PAGE_SUMMARY + READ_FIRST merged into README (the v0.1 front door);
  RESEARCH_MAP folded into ROADMAP/notes; AGENT.md folded into AGENTS.md;
  a truth pass over AGENTS.md/README.md; `notes/INDEX.md`.
Exit criteria:
- Root prose ≈ 12 files per ROADMAP §4; all gates green; README states v0.1.
Files allowed to edit:
- `README.md`, `READ_FIRST.md`, `ONE_PAGE_SUMMARY.md`, `RESEARCH_MAP.md`
- `AGENT.md`, `AGENTS.md`, `ROADMAP.md`, `notes/`, `archive/docs/`
- `repo/`, `scripts/` (reference updates + gates), `tasks/NEXT.md`

## Task Contract Template

```md
# TASK

ID:
Kind: theorem | experiment | data | site | publication | ops | agent
Hypothesis:
Why it matters:
Inputs:
Expected output:
Exit criteria:
Files allowed to edit:
Files that must be regenerated:
How to verify:
```
