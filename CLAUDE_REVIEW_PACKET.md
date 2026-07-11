# Claude Review Packet: Whole-Repository Foundation

Review mode: adversarial.

Scope: the whole repository, not only the changed files.

**Status: Accepted review record.** This packet's foundation (repository
architecture, artifact ownership, cleanup plan) was adversarially reviewed and
**merged to `main`** — it is now the active foundation, not a branch under review.
Retained as the historical review record; the original goal was to test whether
the repo architecture, artifact ownership, and cleanup plan were correct enough
to become the foundation for future work. (They were.)

## Context

The project is a Lean 4 / Mathlib formalization and Research OS for ECDLP and
elliptic-curve cryptography. The proof invariant is unchanged:

- no `sorry`
- no `admit`
- no custom axioms
- Lean kernel and CI gates decide proved mathematics

This branch adds a repository-level operating model:

- `REPOSITORY_ARCHITECTURE.md`
- `repo/ARTIFACTS.yaml`
- `repo/CLEANUP_PLAN.md`
- orientation links from `README.md`, `AGENTS.md`, and `tasks/NEXT.md`

It intentionally does not delete or move files.

## What To Attack

Please assume the architecture is wrong until evidence supports it.

Check these questions:

1. Are any files or directories misclassified as canonical, generated, curated,
   scratch, experimental trace, or archive candidate?
2. Does `repo/ARTIFACTS.yaml` create a second source of truth that could drift
   from `STATUS.md`, `VERIFIED.md`, or generated data?
3. Which generated artifacts are still too easy to hand-edit without detection?
4. Does the cleanup plan risk losing mathematical provenance, especially under
   `notes/ward/`, `scratch/`, or old reports?
5. Are any root docs still duplicating live counts instead of linking to
   `STATUS.md`?
6. Do any docs still name retired or stale workflows?
7. Would a low-context agent know where to start and where not to touch?
8. Does the branch preserve the distinction between:
   - verified Lean theorem
   - corpus claim
   - generated frontier status
   - research hypothesis
   - public narrative claim
9. What should be the next PR after this one?

## Required Review Output

Please answer in this format:

```md
## Verdict
approve | request changes | block

## Blocking Issues
- path:line - issue - why it matters - proposed fix

## Misclassified Artifacts
- path - current class - better class - evidence

## Unsafe Cleanup Candidates
- path - why unsafe - smallest reversible action

## Drift Risks
- risk - source of truth affected - recommended gate

## Next PR
One concrete next PR, with scope and exit criteria.
```

## Block Conditions

Block this branch if:

- it encourages deleting provenance before review;
- it weakens the Lean proof invariant;
- it creates a competing theorem-count source of truth;
- it misrepresents a hypothesis, target, or public claim as a proved theorem;
- it hides a generated artifact behind hand-maintained prose.

## Reviewer Notes

This is an architectural foundation PR. The expected useful outcome may be
"request changes" with a better classification. That is success: the point is
to make cleanup safe before cleanup happens.
