# NEXT.md

This is the only active work queue. It contains current contracts, not a progress
diary. Completed work remains discoverable in Git history, `VERIFIED.md`, and the
durable notes linked from `STATUS.md`.

Canonical start order:

1. Read `STATUS.md`.
2. Read this file.
3. Load `repo/FORMAL_SUBSTRATE.json` for dependency and release decisions.
4. Load `experiments/HYPOTHESES.yaml` only for hypothesis or publication work.

If prose conflicts with `STATUS.md` or a generated registry, the generated
artifact wins and the prose must be corrected in the same PR. No task in this
queue authorizes a merge.

## Active Tasks

### TASK-001 - Close the formal-substrate map

Kind: data | ops | theorem
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: The repository needs one machine-readable answer to what is
proved, what depends on what, and what blocks the release boundary.
Inputs:
- `VERIFIED.md`
- `data/result_registry.json`
- `BARRIERS.md`
- `Ecdlp/Targets/`
- `targets/`
Expected output:
- `repo/FORMAL_SUBSTRATE.json` with exhaustive theorem-family coverage,
  critical-path nodes, dependencies, blockers, and release disposition.
- A knowledge graph with semantic `member_of`, `supports`, `depends_on`,
  and `blocked_by` edges in addition to file imports.
Exit criteria:
- Every ledger row belongs to exactly one substrate family.
- Every critical node has resolvable dependencies, evidence, and status.
- The substrate checker and graph regeneration are green.
Files allowed to edit:
- `repo/FORMAL_SUBSTRATE.json`
- `scripts/check_formal_substrate.py`
- `scripts/build_knowledge_graph.py`
- generated graph artifacts and directly stale architecture prose
Files that must be regenerated:
- `data/knowledge_graph.json`
- `data/knowledge_graph.md`
How to verify:
- `python3 scripts/check_formal_substrate.py`
- `python3 scripts/build_knowledge_graph.py --check`

### TASK-002 - Make ledger trust coverage exhaustive

Kind: theorem | data | ops
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: Headline trust claims should cover every canonical ledger row,
not a hand-selected audit subset or incidental prose citations.
Inputs:
- `VERIFIED.md`
- built Lean declarations under `Ecdlp/` and `ResearchOS/`
- `Ecdlp/AxiomAudit.lean`
- `TRUST_REPORT.md`
Expected output:
- A result registry that resolves each ledger cell to exact declarations,
  explicitly recording grouped rows and anonymous-instance evidence.
- A generated full-ledger axiom audit, with documented exemptions only where a
  ledger cell is not itself a named declaration.
Exit criteria:
- Ledger resolution and audit coverage are both 100%.
- Built modules remain at zero `sorry` and zero custom axioms.
- Pure-kernel versus `Lean.ofReduceBool` trust is reported without overclaim.
Files allowed to edit:
- `scripts/gen_result_registry.py`
- `scripts/gen_axiom_audit.py`
- `Ecdlp/LedgerAxiomAudit.lean`
- `TRUST_REPORT.md`
- generated result-registry artifacts
How to verify:
- `python3 scripts/gen_result_registry.py --check`
- `python3 scripts/gen_axiom_audit.py --check`
- `lake env lean Ecdlp/LedgerAxiomAudit.lean`

### TASK-003 - Resolve or freeze the N7 uniform frontier

Kind: theorem | research
Hypothesis: none; this is an existing formal frontier
Why it matters: N7 uniform is the first unresolved geometric bridge on the
general-`n` torsion path. Its lifecycle must end in a proof or an exact blocker,
not an indefinitely active stem.
Inputs:
- `Ecdlp/Targets/n7_uniform_carrier_induction.lean`
- `Ecdlp/Targets/n7_uniform_secp256k1_x.lean`
- `targets/n7_uniform_secp256k1_x.json`
- `notes/N7_EVEN_X_DOUBLING_ANALYSIS.md`
Expected output:
- A bounded proof pass over the seven carrier obligations.
- Either a promoted sorry-free theorem, or a machine-readable blocker naming
  the missing upstream torsion bridge and the four certificate-heavy walls.
Exit criteria:
- No false or weakened statement is promoted.
- Open-stem counts and target status agree with the substrate manifest.
- A non-closing pass records attempted routes and a precise resume condition.
Files allowed to edit:
- the two N7 target stems and their target metadata
- `Ecdlp/Proved/` and `Ecdlp.lean` only on a complete proof
- N7 barrier/analysis notes
How to verify:
- `python3 scripts/check_targets.py`
- `lake env lean Ecdlp/Targets/n7_uniform_carrier_induction.lean`

### TASK-004 - Normalize operations and prepare final adversarial review

Kind: ops | publication
Hypothesis: `H6_PUBLICATION_BOUNDARY_TRACK`
Why it matters: Claude should receive one coherent whole-repository review
surface after implementation, with no merge and no need for repeated user checks.
Inputs:
- all generated artifacts and checks
- remote branch/workflow inventory
- `repo/ARTIFACTS.yaml`
- the completed contracts above
Expected output:
- Exhaustive artifact classification and generated-file fixpoint gate.
- Branch and workflow inventories with keep/park/delete-after-review decisions.
- One final Claude adversarial review packet tied to one draft PR.
Exit criteria:
- The full local gate battery passes on Windows and Linux CI.
- The review packet distinguishes facts, generated views, open targets, and
  deferred experiments.
- The PR remains draft and unmerged.
Files allowed to edit:
- `repo/`, `scripts/`, `.github/workflows/`, architecture/publication docs
- generated artifacts produced by those scripts
How to verify:
- `python3 scripts/check_repo_artifacts.py`
- `python3 scripts/check_generated_fixpoint.py --check`
- all checks listed in the final review packet

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
