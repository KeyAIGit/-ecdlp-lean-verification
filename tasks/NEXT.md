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

> TASK-001/002/003 (truth-layer gate, agent bundles, dashboard sync health)
> completed and removed 2026-07-16 — their exit criteria are the live green gates
> (`check_status_consistency.py`, `export_agent_bundle.py --check`, dashboard Sync Health).

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

### TASK-008 - The ψₙ↔E[n] velocity queue (24/7 cycle targets)

Kind: theorem | research
Hypothesis: `H2_GLV_SUBGROUP_VS_WHOLE_GROUP`
Why it matters: Rolling, pre-decomposed target list so each continuation cycle
starts immediately (AGENTS.md §High-velocity prover protocol).
Current queue (in order; each = one design→verify→integrate→push cycle):
1. **N7@4**: `x(4P) = Φ₄/ΨSq₄` via tangent-doubling at 2P (even-n rung; template:
   `QuintupleMultiplicationFormula` chain with one doubling instead of a chord).
2. **E[2] completeness**: `#E[2](𝔽̄_p) = 4 = 2²`, `E[2] ≅ (ℤ/2)²` — the even
   companion of the N13 family (3 roots of `X³+7` over `𝔽̄_p`, each with `y = 0`,
   plus `O`; needs a small `X³+7` separability/roots-count brick).
3. **N8/N9 conditional forms**: state the general `ψₙ(P) ≠ 0 ⟹ x([n]P) = Φₙ/ΨSqₙ`
   reductions with N7-general as an explicit hypothesis (map rows N8/N9).
4. **Upstream extraction**: split the curve-free pieces (Ward rigidity, EDS lemmas,
   kernel-structure lemma, the N13 pattern) into a Mathlib-PR-shaped bundle memo.
5. **Weil W3 evaluation half**: extend `evalAt` to rational functions regular at `P`
   via localization (`notes/FOUNDATIONS.md` W3) — reopens the pairing ladder.
Landed from this queue: E[3] (first N13 instance), E[5]+E[7], N7@4 (N7 small-n
ladder complete), E[2] (N13 family now `n ∈ {2, 3, 5, 7}` — all primes with a bridge) — all 2026-07-16.
Exit criteria:
- Each item lands as a CI-green module + ledger row(s), or a frozen honest blocker
  memo naming the missing foundation.
Files allowed to edit:
- new `Ecdlp/Proved/*.lean`, `scripts/certs/*`, ledger/docs per the protocol.

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
