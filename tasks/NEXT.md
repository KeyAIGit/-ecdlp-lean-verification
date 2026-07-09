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

### TASK-005 - Audit GLV truth wording

Kind: publication | docs | theorem
Hypothesis: `H2_GLV_SUBGROUP_VS_WHOLE_GROUP`
Why it matters: The project must clearly distinguish the closed crypto-subgroup
GLV result from the still-open whole-point-group or point-counting-dependent
claims.
Inputs:
- `Ecdlp/Proved/GlvSubgroupEigenvalue.lean`
- `VERIFIED.md`
- `STATUS.md`
- `README.md`
- `ABSTRACT_SCOPE.md`
- `TRUST_REPORT.md`
Expected output:
- Consistent wording across the canonical docs.
Exit criteria:
- Docs say exactly which GLV eigenvalue statement is proved, which statement is
  open, and which foundation gates it.
Files allowed to edit:
- `scripts/gen_status.py`
- `STATUS.md`
- `README.md`
- `ABSTRACT_SCOPE.md`
- `TRUST_REPORT.md`
- `VERIFIED.md`

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

### TASK-007 - Normalize repository architecture

Kind: ops | agent | docs
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: Future Claude/Codex runs need a whole-repository map before
they safely remove noise, move files, or change generated artifacts.
Inputs:
- `REPOSITORY_ARCHITECTURE.md`
- `repo/ARTIFACTS.yaml`
- `repo/CLEANUP_PLAN.md`
- `CLAUDE_REVIEW_PACKET.md`
- `AGENTS.md`
- `README.md`
Expected output:
- A reviewed architecture foundation that classifies canonical, generated,
  curated, scratch, and archive-candidate files.
Exit criteria:
- Claude adversarial review identifies no blocking misclassification.
- Any archive/delete work is split into a later PR.
Files allowed to edit:
- `REPOSITORY_ARCHITECTURE.md`
- `repo/`
- `CLAUDE_REVIEW_PACKET.md`
- `AGENTS.md`
- `README.md`
- `tasks/NEXT.md`

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
