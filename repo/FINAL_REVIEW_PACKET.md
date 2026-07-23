# Claude adversarial review packet: PR #235

## Review contract

- Review PR #235 against `main` at the PR head that is current when review starts.
- Treat this as the single repository-wide integration review. It contains the
  work from draft PR #234 plus the formal-substrate normalization.
- Do not merge, mark ready, delete branches, weaken gates, or start new
  hypothesis work.
- Review adversarially. Try to falsify the claims below from source and CI
  evidence rather than accepting this packet as evidence.
- Report findings first. A clean review must still name residual risks.

## Intended release boundary

This PR closes the *substrate map*, not every open mathematical program. Its
release rule is explicit: every required critical node must be either:

1. `closed`, with kernel-backed anchors and evidence; or
2. `blocked_accepted`, with an exact blocker, evidence, and resume condition.

Experimental hypothesis generation, general all-`n` torsion, a complete Weil
pairing, P-256 exact cardinality, and N7 uniform multiplication are not claimed
as solved.

## Claims to attack

### 1. Ledger and trust coverage

- `VERIFIED.md` contains 296 canonical accounting rows (about 257 distinct
  headline results).
- `data/result_registry.json` resolves every row into 442 distinct named Lean
  declarations plus 7 anonymous-instance evidence records, with zero unresolved
  references.
- Grouped file cells and namespace wildcards are file-scoped. In particular,
  `Ecdlp/Proved/{ShamirSSS,GlvTorsionAction,ScalarGroupStructure}.lean` must not
  expand to the whole `Ecdlp` namespace.
- `Ecdlp/LedgerAxiomAudit.lean` is generated from that registry and contains one
  `#print axioms` command for every named declaration.
- CI requires the Lean output name set to equal the registry name set exactly.
  Apostrophes inside Lean identifiers must not truncate names.
- No audited declaration may depend on `sorryAx`, `Lean.guardMsgsAx`, or a
  project-defined axiom. Standard Lean/Mathlib axioms are allowed. The
  `native_decide` compiler-trust extension is allowed only because it is
  explicitly disclosed in `TRUST_REPORT.md`.

### 2. Formal architecture

- `repo/FORMAL_SUBSTRATE.json` partitions all 296 ledger rows into 8 result
  families and maps 17 critical nodes: 11 closed, 4 blocked/accepted, 2 deferred.
- Every non-deferred critical node appears exactly once in
  `release.required_nodes`.
- Every declared blocker is referenced, has evidence, and has a concrete resume
  condition.
- No node marked closed relies on an open `Ecdlp/Targets/` stem.
- Semantic graph edges (`member_of`, `supports`, `depends_on`, `blocked_by`) match
  the manifest; import edges alone are not presented as the research DAG.

### 3. N7 boundary

- N7 remains `blocked`, not `todo`, `open`, or `closed`.
- `Ecdlp/Targets/n7_uniform_carrier_induction.lean` has exactly 7 independent
  bare `sorry` obligations. The wrapper stem has 1 downstream `sorry`; it is not
  an eighth independent algebra wall.
- The five committed fixed-index certificate scripts recorded in
  `notes/N7_UNIFORM_BLOCKER.md` pass, but they do not constitute a uniform Lean
  proof.
- Mathlib PR #13782 is external, open upstream work and is not treated as a
  landed dependency.
- The resume condition is narrow enough to prevent repeated speculative N7
  grinding without a new bridge or reproducible certificate generator.

### 4. Repository and automation ownership

- `repo/ARTIFACTS.yaml` classifies every tracked or untracked, non-ignored repo
  file into an explicit owner class. Unapproved overlaps fail CI.
- Generated pure artifacts are fresh and all generated artifacts reach a
  one-pass fixpoint across LF/CRLF environments.
- `repo/AUTOMATION_INVENTORY.json` classifies all 17 workflows. Its checker reads
  actual `on:` blocks, verifies trigger-policy equality, and requires paths
  scoping for paid or conditional self-tests.
- Parked model/hypothesis workflows have no schedule and are not authorized by
  the active queue.
- `repo/BRANCH_INVENTORY.json` records 16 real remote branches, excluding the
  symbolic remote HEAD. It authorizes no deletion. Ahead/behind and ancestry are
  snapshot evidence, not proof that branch content is unique or redundant.

### 5. Public and Research OS consistency

- `STATUS.md` owns live headline counts; public pages display the same static
  fallback values before JavaScript runs.
- Only H1 and H3 are active. Closed and parked hypotheses are not displayed as
  eight open hypotheses.
- `tasks/NEXT.md` contains only substrate-closing contracts; new hypothesis
  testing is deferred.
- Foundation/Weil/publication docs do not describe W3 as open or imply that W4/W5
  are closed.

## Known trust boundaries

- The Lean kernel remains the proof authority, but `native_decide` declarations
  extend trust to the pinned Lean compiler. This is not pure kernel reduction.
- `data/result_registry.json`, the knowledge graph, dashboard, and this packet
  are derived evidence, not proofs.
- The declaration registry uses a source parser, not Lean environment
  reflection. CI compensates by elaborating every generated name and demanding
  exact output-set equality. Review whether the source parser can still
  over-expand or omit ledger evidence while passing that check.
- The 7 anonymous instances cannot be named with `#print axioms`; verify each
  exemption is genuinely anonymous, source-scoped, and not being used to hide a
  named result.
- `Ecdlp/Targets/` is deliberately outside the build graph and contains open
  obligations. CI forbids built files from importing it.
- Branch cleanup is intentionally postponed. No historical branch should be
  deleted from this PR.

## Minimum reproduction

```bash
python3 scripts/check_counts.py
python3 scripts/test_check_counts.py
python3 scripts/test_ledger_utils.py
python3 scripts/test_check_axioms.py
python3 scripts/check_status_consistency.py
python3 scripts/check_formal_substrate.py
python3 scripts/check_repo_artifacts.py
python3 scripts/check_automation_inventory.py
python3 scripts/check_branch_inventory.py
python3 scripts/gen_result_registry.py --check
python3 scripts/gen_axiom_audit.py --check
python3 scripts/check_generated_fixpoint.py --check
lake build
lake env lean Ecdlp/LedgerAxiomAudit.lean > axiom_audit.txt 2>&1
python3 scripts/check_axioms.py axiom_audit.txt data/result_registry.json
```

Also inspect the PR's complete GitHub Actions result. Do not accept local Python
checks as a substitute for the final Lean elaboration.

## Adversarial questions

1. Can any ledger row resolve to unrelated declarations because of wildcard,
   shorthand, brace, basename, namespace, or `supporting` expansion?
2. Can any public declaration be assigned an incorrect qualified name by nested
   namespace/section parsing while still producing an apparently valid audit?
3. Are the 7 anonymous-instance exemptions exact and necessary?
4. Does the axiom checker parse every multiline Lean output form and every legal
   identifier, and does it reject unknown, missing, unexpected, or custom axioms?
5. Is any of the 11 `closed` critical nodes broader than its actual theorem
   anchors and documented scope?
6. Are all 4 `blocked_accepted` critical nodes genuine foundational boundaries
   rather than unfinished tractable work mislabeled as closure?
7. Does the N7 record distinguish checked reduction, symbolic evidence, fixed-`n`
   certificates, and the absent uniform proof without ambiguity?
8. Can a generated artifact drift while the fixpoint, source registry, bundle,
   and public counter gates remain green?
9. Does any paid workflow have a broad automatic trigger, hidden schedule, or
   authority inconsistent with the inventory?
10. Is any branch disposition unsafe, especially the 26-ahead historical branch
    or the two candidate queues?
11. Does any public document still imply unconditional ECDLP hardness, a complete
    Weil pairing, solved N7, pure-kernel trust for `native_decide`, or a retired
    theorem count?

## Required review output

Return:

1. Findings ordered `P0`, `P1`, `P2`, `P3`, each with file/line, violated claim,
   reproduction or reasoning, and the smallest safe correction.
2. A `False closures` section naming any critical node whose disposition is not
   justified. Write `none found` only after checking all 17 nodes.
3. A `Trust gaps` section covering declaration resolution, anonymous instances,
   axiom parsing, `native_decide`, and excluded Targets.
4. A `Residual risks` section even if there are no actionable findings.
5. One verdict: `BLOCK`, `READY_FOR_OWNER_DECISION`, or
   `NEEDS_NARROW_FOLLOWUP`.
6. The literal line `MERGE AUTHORIZED: NO`.

Do not replace findings with a general summary. Do not merge the PR.
