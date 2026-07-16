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

### TASK-005 - Geometric `E[n] ≅ (ℤ/n)²`: prove the N5 scalar rung

Kind: theorem | research
Hypothesis: `H2_GLV_SUBGROUP_VS_WHOLE_GROUP`
Why it matters: The scoping half of this task is **delivered** (2026-07-16): the
decomposition memo in `notes/POINT_COUNTING_KEYSTONE.md` §"The successor gap"
chose the geometric-torsion branch (P-256 cardinality stays parked on Hasse) and
named the smallest missing piece — the **N5 scalar obligation**, no two
consecutive zeros in the curve-specialized scalar EDS over `𝔽̄_p`. It is
**unblocked**: the L4 engine (`normEDS_isEllSequence`, `normEDS_somos4`) and the
L5/L6/L6b degenerate-case certificates are kernel-verified; the eval-bridge
descent (`DivisionPolynomialEvalBridge.lean`) turns the scalar lemma into node
N5 (`IsCoprime (Φ n) (ΨSq n)`), feeding the counting route toward `#E[n] = n²`
and (via the proved prime-case N10(iii)) `E[n] ≅ (ℤ/n)²` — the Weil-pairing
non-degeneracy substrate.
Inputs:
- `Ecdlp/Targets/normeds_no_consecutive_zero.lean` (the open stem — the target)
- `targets/normeds_no_consecutive_zero.json` (budget + hint with proof shape)
- `notes/POINT_COUNTING_KEYSTONE.md` §successor gap (the memo)
- `notes/DIVISION_POLY_TORSION_MAP.md` (N5 row, critical path)
Expected output:
- A kernel-accepted proof of `secp256k1_normEDS_no_consecutive_zero`, promoted
  per the standard lifecycle (stem consumed, registry verified, ledger row). No
  weakening, no `sorry`. If attempts stall, a frozen memo recording the exact
  failing induction step instead.
Exit criteria:
- Either the rung proved and promoted, or the blocker memo naming the precise
  identity that resists (with the attempted decomposition).
Files allowed to edit:
- `Ecdlp/Proved/` (new module on success) + `Ecdlp.lean` + `VERIFIED.md`
- `targets/normeds_no_consecutive_zero.json`, `Ecdlp/Targets/`
- `notes/POINT_COUNTING_KEYSTONE.md`, `notes/DIVISION_POLY_TORSION_MAP.md`

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

### TASK-007 - Declare v0.1 on main

Kind: ops | docs
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: Consolidation tranches 1 and 2 are executed (ROADMAP.md §4:
archive/, ROADMAP as the one strategy doc, README as the one front door,
AGENTS.md as the one agent doc, notes/INDEX.md). What remains is the release
act itself, which only makes sense on `main`.
Inputs:
- `ROADMAP.md` (§4 structure tables, §5 near-term program)
- `REPOSITORY_ARCHITECTURE.md` + `repo/CLEANUP_PLAN.md` (map + tranche records)
- `README.md` (already states v0.1)
Expected output:
- The consolidation PR merged by the maintainer; the full gate battery green on
  `main`; an annotated git tag `v0.1` on the merge commit.
Exit criteria:
- `git tag v0.1` exists on main; STATUS.md and the site reflect the merged
  state; no known-false statement in canonical docs.
Files allowed to edit:
- none (tagging + a follow-up docs-sync run on main; open a new task for any
  fallout)

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
