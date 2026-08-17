# UORC-056 C36 to C37 authority repair

Date: 2026-08-17

Status: metadata and provenance correction only. This note changes no
scientific result, does not authorize an experiment, and does not select or
activate C44.

## Decision

The actual C37 package

```text
HALF-INDEX-MILLER-QUADRATIC-BRANCH-085
PR #408
research/uorc056-half-index-miller-c37
0b36801d1d413ec595fad87509e85c0368a9ead7
```

realizes the planned successor identifier recorded by the canonical C36
package:

```text
MIXED-INDEX-ELLIPTIC-NET-OR-RESULTANT-C37
```

The downstream-compatible `successor` is therefore the exact realized branch
`research/uorc056-half-index-miller-c37`. The planned identifier remains in the
lineage record as historical provenance and is connected to the actual package
by a typed `REALIZES` relation.

The typed parent/successor pair is exactly:

```text
REGULARIZED-ANCHOR-MILLER-TRANSLATION-084 (#407, C36)
  SUCCESSOR -> HALF-INDEX-MILLER-QUADRATIC-BRANCH-085 (#408, C37)

HALF-INDEX-MILLER-QUADRATIC-BRANCH-085 (#408, C37)
  PARENT -> REGULARIZED-ANCHOR-MILLER-TRANSLATION-084 (#407, C36)
```

No package is superseded by this correction.

## Root cause

Git ancestry and the C37 parent declaration were already correct. The defect
was stale planned-successor naming without a typed realization binding:

- C36 #407 exposed `MIXED-INDEX-ELLIPTIC-NET-OR-RESULTANT-C37` as if it were a
  resolvable current package identifier.
- The earlier C36 research note preserved the still older proposal
  `MILLER-STATE-DECODER-C37`.
- C37 #408 was implemented under the canonical ID
  `HALF-INDEX-MILLER-QUADRATIC-BRANCH-085` and branch
  `research/uorc056-half-index-miller-c37`.
- No `REALIZES` or alias relation connected the planned name to the actual
  package.

A deterministic resolver must not infer equivalence from the shared stage
number, timestamp, or recency. The old metadata therefore correctly produced
`EXPLICIT_SUCCESSOR_PARENT_CONFLICT`.

## Exact PR and Git evidence

| PR | role | branch head | observed base ref and SHA | exact ancestry |
|---|---|---|---|---|
| #406 | parallel C36 | `research/uorc056-multi-argument-miller-decoder-c36` at `7fc757fa31740e40ec68f8d27b572765fc244a39` | `research/uorc056-anchor-mixed-miller-c35` at `7c64cf1acda8569945e7f5298b557571f3585a3a` | base SHA is an ancestor; it is not an ancestor of C37 |
| #407 | canonical parent C36 | `research/uorc056-regularized-anchor-miller-c36` at `330ea2f084441c0375b2a6c675112b2b2e23bd88` | same base ref, observed at `7c64cf1acda8569945e7f5298b557571f3585a3a` | fork point is `a19e137f5a0a06c4a00506141ccb89be053ab8bc`; the base branch advanced on the parallel line after this fork |
| #408 | realized C37 | `research/uorc056-half-index-miller-c37` at `0b36801d1d413ec595fad87509e85c0368a9ead7` | `research/uorc056-regularized-anchor-miller-c36` at `330ea2f084441c0375b2a6c675112b2b2e23bd88` | C36 #407 head is the exact merge base and an ancestor |

The first C37 commit `0699a6f28a3bcc7c00479239ff48c03aaab9e79c`
directly follows the C36 #407 head. The parallel C36 #406 head and actual C37
have merge base `a19e137f5a0a06c4a00506141ccb89be053ab8bc`;
#406 is not a C37 ancestor.

The exact source blobs pinned in the machine record are:

| package | lineage source blob |
|---|---|
| C36 #407 | `8d86765d4abd3842dceb71a781d7934032b37e7d` |
| C37 #408 | `df8514d695f703bc5f2acb9bb2b0119f001a4de2` |
| parallel C36 #406 | `7291998b654cb37b4bf5812babba343b519757cf` |

The #406 lineage source remains under `archive/untrusted_intake/`, is typed
`PARALLEL`, and is explicitly non-authorizing. The regression gate rejects any
attempt to make it C37's `PARENT` or `SUCCESSOR`.

## Bounded downstream-compatibility audit

The bounded pass inspected the active authority path around C39, C40, C41,
C42, C43, and C43B. It found one additional immediate blocker and three pieces
of nonblocking provenance debt.

### Blocker: unresolved C43/C43B sibling authority

PR #418 (`research/uorc056-universal-cover-language-c43` at
`52015c53ce3770268437aac71ee74e0517719834`) and PR #419
(`research/uorc056-local-glv-gauge-breaking-c43` at
`acdc7c6ea5d76ac58afb1574d1efa9bbf60c050f`) are sibling packages based on the
same exact C42 head `728d1a7a1c60463cc4546e2bb21fa3eaf3936d58`.

C42's contract and research note name
`LOCAL-GLV-GAUGE-BREAKING-C43` as the successor. PR #419 matches that planned
route; PR #418 is a separate universal-cover atlas. Neither supersedes the
other. The relation still needs a reviewable authority correction on the C42
line: C43B `REALIZES` the named C42 successor, while C43 is `PARALLEL`.

This repair does not encode that separate branch-head decision in C36
metadata. Until it is authoritatively represented, a downstream resolver must
retain the equal-leader conflict and must not select either sibling by PR
number, timestamp, or recency.

### Nonblocking provenance debt

- Closed/superseded C39 PR #409 names PR #410 as its canonical corrected C39
  package, but the branch it names belongs to actual PR #414 at
  `866162ab7598b81855a304770735b3aa3299a78f`; PR #410 is C40. The downstream
  already treats #409 as historical, so this stale pointer is not the current
  blocker.
- C39 PRs #413 and #414 share the same machine profile ID without a typed
  supersession relation. The canonical marker currently distinguishes #414,
  but the stacked C41/C42 line descends from #409 rather than #414. Repairing
  that history would require a separate authority decision, not a rebase in
  this patch.
- C40 PR #415 contains the false secp256k1 specialization
  `ord_n(2)=(n-1)/2` and a transitive doubling action. The audited correction
  in PR #418 is `ord_n(2)=(n-1)/64` with 32 cycles. PR #415 is red and is not
  selected or trusted; its general gauge result must not be silently declared
  wholly superseded by a correction to one arithmetic field.

No other active duplicate identity or contradictory result metadata was found
that outranks these explicit blockers in the bounded pass. Branch-only
`research/uorc056-period-lattice-net-gauge-c43` has no PR or authorizing
lineage/profile record and remains non-authoritative.

## Compatibility and synchronization boundary

An open side PR is not sufficient for downstream authority. The downstream
controller chooses the C36 lineage record at the exact head of
`research/uorc056-regularized-anchor-miller-c36`; it also inventories repair
PRs separately. This correction must first be reviewed and merged into that
specific branch. Merging it only to `main` would not replace the trusted C36
branch-head record.

After that human merge, the downstream controller should run, in order:

```bash
cd ~/projects/keyai-parity-lab
make spec-audit
make frontier-sync
make frontier-audit
make frontier-report
```

If the audit still reports `FRONTIER_CONFLICT` because of the C43/C43B sibling
tie, the controller must stop. It must not publish a frontier source bundle or
begin scientific search.

## Regression gate

Run:

```bash
python scripts/test_uorc056_c36_c37_authority.py
python scripts/check_uorc056_c36_c37_authority.py --verify-git
```

The first command reproduces the old planned-token mismatch, verifies the new
branch-resolvable successor, and tests adversarial parent swaps. The second
checks the exact historical Git objects, source blobs, merge bases, positive
C36 #407 ancestry, and negative C36 #406 ancestry.
