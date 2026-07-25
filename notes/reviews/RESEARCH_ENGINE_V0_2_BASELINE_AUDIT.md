# Research Engine v0.2 baseline audit

Date: 2026-07-25

This is the read-only baseline recorded before the v0.2 repair. It is an audit
snapshot, not evidence that the reviewed engine is stable.

## Repository and pull requests

- Repository: `KeyAIGit/-ecdlp-lean-verification`.
- Protected baseline: `origin/main` =
  `fed55d84675fd96e5f40204b9f5f49baa8c01172`.
- PR #245 is merged as `e1dfd77d9c6bfe28936fb54df1437829fcf3c355`.
- PR #247 is merged as the protected baseline above.
- PR #243 is an open draft at
  `577e22fba37de513592bd5b77e0bb681322d7f88`; it must not be merged or
  ported wholesale.
- PR #246 is an open review-only draft at
  `e0a382b51e3263f41c295ad72c7a315ff2c317a6`; its fixed-group-order
  solving-degree conclusion is retracted and the branch is superseded.
- PR #248 is an open draft based on the protected baseline, with head
  `7acd78fb263d640538e8f29aa6b63a4820fd20b6`.

No pull request was merged, closed, or marked ready during this audit.

## Historical byte baseline

The eight historical outcome files are immutable inputs. Their raw file hashes
at the protected baseline are:

| Event | Bytes | Raw SHA-256 |
|---|---:|---|
| `REO-2026-07-24-001` | 2575 | `04da083fdd540da92542d04bd8b436a4b81f653c5f2fe8f220186aed230b6f2f` |
| `REO-2026-07-24-002` | 2118 | `47f03443503d078c069081b2c5645e617dede099fd57ae8b93f6cf8447eebed9` |
| `REO-2026-07-24-003` | 2356 | `a2e846d65df808c65b9ea3cecf8af0ce09d65b9b04c0184599f6cd00a10e2359` |
| `REO-2026-07-24-004` | 2148 | `19b98cfe564a0fb07f081184af0e03504f0b36fe472c0681bff9e1598a7bea11` |
| `REO-2026-07-24-005` | 2277 | `6fdc5b81828447b43f91ed6cd5c0480454eee266832046489a4d3076c8dd68e0` |
| `REO-2026-07-24-006` | 2049 | `1dd743cb8cc12ca46e1212dd14e389763d1bcdca867660e045f0e08c09bb25ed` |
| `REO-2026-07-24-007` | 2301 | `e0e6916381f61884db2775caedb7d751443ec4bc117f76480a1915a3e8e21183` |
| `REO-2026-07-24-008` | 2654 | `4be39c49f910c4a3c33c9f2e2b6956b437debf5269a1afcdcfa7a9e998d45e45` |

The canonical-JSON review root remains
`d9de2351a499d395d09005199aac73744c1bf212ff9759ceed5d229d076ca7a3`.
The repair must preserve both the raw bytes and this root.

## Reproduction of the PR #248 failure

The 52 Research Engine tests pass in a full local clone only because the object
database still contains `origin/agent/research-engine-v0`. The generation
fixture uses its pre-squash head:

`68e9ff36a5c07c842dc9fbbeec3c3da7a02896ca`

That commit exists locally but is not an ancestor of protected `main`. In a
single-branch clone of PR #248, exactly 10 of 52 tests fail because the commit
does not resolve and the evidence hashes cannot be reproduced. This confirms
that object existence is not an adequate scientific provenance rule.

## Severity-ranked findings

### P0

1. **Owner authorization can be bypassed.** Candidate metadata and the generic
   exploration capability can make a candidate selectable without a separate
   dated owner decision matching the current decision substrate.
2. **Terminal candidates occupy selection slots.** Selection runs before prior
   outcomes are applied, so three terminal candidates can permanently exclude
   a fourth live candidate. A completed prerequisite is also selected again
   instead of merely satisfying its dependent.
3. **Calibration is mutable.** Brier records read priors and likelihoods from
   the current candidate policy rather than the frozen candidate/version
   digest attached to the event.

### P1

4. **PR #248 has branch-only provenance.** `git cat-file -e` accepts a commit
   that an ordinary protected-main clone cannot reproduce.
5. **Scientific gates are partly self-declared.** Candidate booleans and
   substantive-looking prose can clear mechanism, prediction, cost, and
   validator gates without derived evidence contracts.
6. **Candidate snapshot and lifecycle are conflated.** Mechanism, prior,
   authorization, dependencies, and mutable execution state share one policy
   object.
7. **The claim hierarchy is missing.** The repository cannot represent a
   bounded-negative child claim while retaining its parent route as open
   without overloading `HYP_GLV_SEMAEV_001`.
8. **Selection is greedy and falsely precise.** One point prior, one likelihood
   model, and a wall-time-oriented ratio do not express rank sensitivity,
   shared setup, correlation, or portfolio diversity.
9. **Research lanes share one lifecycle.** Literature ingestion, structural
   certificates, mechanism development, validator engineering, bounded
   experiments, and formalization need different gates.
10. **Petit and Weil-descent semantics drift.** The canonical attack registry
    still contains statements that explain P4's non-faithfulness by the lack of
    Weil restriction, although PKC 2016 gives native prime-field
    constructions. P4 is non-faithful because it implements neither source
    construction.

### P2

11. `TASK-010` is simultaneously `active_review_preparation` in the research
    queue and `parked` in `AGENTS.md`.
12. The branch inventory records 18 remote branches at `e892800`, while the
    audit observed 25 real remote heads at `fed55d8`.
13. The Research Engine review briefs still describe pre-merge branches as the
    current checkpoint and need an explicit frozen-historical marker.
14. Kudo et al., CANS 2018 is correctly limited to metadata and abstract in the
    source registry and must remain `full_text_unread`.
15. The strengthened fixed-target certificate is an `S4` certificate. Generic
    `S3/S4 fixed-target` wording must be narrowed; the exhaustive result remains
    certificate-backed, not a Lean theorem.

## Required disposition

- Preserve the zero-authorization and zero-promotion state.
- Repair #248 without rewriting the eight historical outcomes.
- Create a separate minimal GLV affine-target closeout from protected `main`;
  do not merge PR #243.
- Treat seeds as research-question or proposal seeds, never as hypotheses or
  executable candidates.
- Keep zero quality-cleared proposals as an acceptable result.
