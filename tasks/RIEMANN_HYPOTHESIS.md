# Riemann Hypothesis research queue

This file owns the active KeyAI queue for the Riemann Hypothesis. The domain
boundary is `domains/riemann-hypothesis/README.md`; the canonical target and
source map live in `domains/riemann-hypothesis/corpus.md`.

The lane is **active exploratory research**, not a claimed proof program with a
known path to completion. Existing ECDLP state remains authoritative in its own
decision substrate and queue. New discretionary mathematical work defaults to
this queue during the RH activation cycle.

## Current decision

Decision update: 2026-08-06. `RH-001`, `RH-003`, `RH-004`, and `RH-006` are complete.
`S0-TRUST` is closed by PR #298, and the repo-local target bridge is built,
audited, and merged by PR #299, closing `S1-TARGET`. `RH-002` remains
`PARK`/`PARK`/`PARK`, with no theorem-bearing route selected and its
dispositions still pending independent review. The `RH-006` source replay has
59/59 rows dispositioned (57 confirmed, 2 amended), and the accepted package
is recorded in `RH006_SOURCE_CONTRACT_ACCEPTANCE_2026_08_06.md`. `RH-007` is
the sole active task. Its X1-X11 statement surface is independently
accepted in `RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`; the only authorized
next action is a separate built promotion with kernel and axiom CI. Do not
begin a route proof attempt, large computation, new equivalence formalization,
or autonomous hypothesis sweep. The built xi module must carry its
`RH-*` ledger rows, registry entries, audit lines, and promotion review in the
same later PR.

The exact Lean target is the already-pinned Mathlib declaration
`_root_.RiemannHypothesis`. Do not create a competing definition.

## RH-001: pinned formal capability and barrier map

ID: `RH-001`

Status: **COMPLETE 2026-08-05**

Closure evidence: the capability map was independently replayed against the
exact pinned Mathlib revision — 0 mismatches across all positive inventory
rows, 12/12 negative rows confirmed (several strengthened tree-wide), the
`Λ₀` sign-inconsistency claim confirmed, the missing `riemannZeta_zero`
anchor recorded (`RiemannZeta.lean:149`), and exactly three candidates
admitted to `RH-002`. Record:
`notes/reviews/RH001_INDEPENDENT_REPLAY_2026_08_05.md`; dated addendum in
`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md`. Scoped carve-out:
the adversarial source-to-formalization review of `SOURCE_CONTRACTS.md`
against the SHA-256-pinned PDFs is **not** part of this closure; it is
carried as an explicit `RH-003` review precondition, and
`SOURCE_CONTRACTS.md` remained "proposed under independent review" at this
closure point. Subsequent update (2026-08-06): `RH-006` accepted the amended
package; see `RH006_SOURCE_CONTRACT_ACCEPTANCE_2026_08_06.md`.

Kind: research / review

Hypothesis: A declaration-level audit of Mathlib v4.31.0 and the primary sources
will expose a smaller and more decision-useful frontier than starting from a
generic list of RH approaches.

Why it matters: Without this map, an agent can spend months reproving available
facts, formalizing an equivalence whose prerequisites are absent, or hiding the
hard part inside an unchecked assumption.

Inputs:

- `domains/riemann-hypothesis/README.md`
- `domains/riemann-hypothesis/corpus.md`
- `lake-manifest.json`
- pinned Mathlib source at commit
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`
- exact primary sources for Li/Weil, Nyman-Beurling, explicit-formula, and
  de Bruijn-Newman routes

Expected output:

- `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md`
- declaration-level inventory of what is already formalized;
- dependency DAG from each top-three criterion to `_root_.RiemannHypothesis`;
- an exact audit of a standard entire xi object, its functional symmetries, and
  the correspondence between its zeros and Mathlib's RH target;
- severity-ranked missing foundations with exact Mathlib search evidence;
- explicit treatment of zero multiplicity, which is not represented by the
  current set-valued `riemannZetaZeros` API;
- a list of semantic mismatches between source statements and available types;
- no more than three candidates admitted to `RH-002`.

Exit criteria:

- every available formal fact has an exact declaration and pinned file anchor;
- every missing fact is distinguished from a failed search;
- each route lists its convergence, regularity, branch, multiplicity, and
  infinite-sum obligations;
- no candidate is called easier merely because it is an equivalent statement;
- an independent reviewer can reproduce the inventory from the pinned revision.

Files allowed to edit:

- `domains/riemann-hypothesis/`
- `tasks/RIEMANN_HYPOTHESIS.md`
- a new curated review under `notes/reviews/`

Files that must not be edited:

- `Ecdlp/`
- `repo/ECDLP_DECISION_SUBSTRATE.json`
- ECDLP experiment outcomes or authorizations
- `VERIFIED.md` and generated views

How to verify:

- check every declaration against the pinned Mathlib commit;
- run `python3 scripts/check_domains.py` and
  `python3 scripts/check_repo_artifacts.py`;
- obtain an adversarial source-to-formalization review.

## RH-002: route triage and candidate selection

ID: `RH-002`

Status: **EXECUTED 2026-08-05 — dispositions `PARK`/`PARK`/`PARK`, no
`SELECT`; pending independent disposition review**

Outcome record: `domains/riemann-hypothesis/ROUTE_TRIAGE.md`. Route A's full
tail-positivity bar and Route B's unconditional closure bar would each imply
RH. For Route C, no known published mechanism meets the preregistered
all-heights individual-zero-exclusion bar; satisfying that full bar would
imply RH, but the present literature gap is not an impossibility theorem.
Zero theorem-bearing routes selected ("at most one" is
satisfied by zero); Route B's 20% pilot execution cap is untouched; every
route retains a scoped reason, a preregistered revival bar, and
reconsideration triggers. The successor work item is foundation, not route
execution: `RH-003` activates under the capability map's "First
implementable foundation and stop rule" (the route-neutral target bridge
closes named barrier `S1-TARGET`), explicitly not as a route `SELECT` and
not as progress on RH.

Kind: research / review

Hypothesis: At most one of Li/Weil positivity, Nyman-Beurling closure, and an
explicit-formula, mollifier-limit, or zero-free inequality route will expose a
theorem-sized next step with favorable information value under the current
library.

Why it matters: Parallel activation of several enormous equivalence programs
would create theorem volume without a credible bridge to RH.

Expected output:

- one source-anchored desk screen per admitted route;
- matched dependency, reviewer-hour, and compute budgets;
- explicit `SELECT`, `PARK`, or `STOP` disposition for every route;
- at most one selected theorem-bearing candidate.

Exit criteria:

- the selected candidate has a precise statement, mechanism, dependencies,
  expected information gain, claim boundary, and death condition;
- the candidate is not merely RH or an equivalent criterion renamed as an
  assumption;
- every rejected route retains a scoped reason and reconsideration trigger.

Files allowed to edit:

- `domains/riemann-hypothesis/`
- `notes/reviews/`
- `tasks/RIEMANN_HYPOTHESIS.md`

How to verify:

- independent mathematical review of all three dispositions;
- source locators and assumptions replayed by a second agent.

## RH-003: freeze one theorem contract

ID: `RH-003`

Status: **COMPLETE 2026-08-06**

Closure evidence: the frozen contract and its non-built Lean draft were
independently reviewed and merged by the external reviewer (tightening
commit `38a70f0`, squash-merge of PR #297 as `8c70680`); per the owner's
instruction, review-and-merge is the acceptance step for this lane. The
`SOURCE_CONTRACTS.md` acceptance review was still open at this closure point
and gated Annex A xi work only. Subsequent update (2026-08-06): `RH-006`
accepted the amended package; independent acceptance of the xi contract is
the remaining review gate.

Kind: theorem / review

Activation basis (2026-08-05): `RH-002` produced no route `SELECT`, so the
original "BLOCKED on RH-002 SELECT" clause is superseded by a dated
decision: `RH-003` activates under the capability map's "First implementable
foundation and stop rule" — the first Lean PR may contain only the
route-neutral target-equivalence bridge, which closes named barrier
`S1-TARGET` and is shared infrastructure for every admitted route. This is
foundation work, not a selected theorem-bearing route and not progress on
RH.

Hypothesis: The route-neutral target bridge (exact nontrivial-zero domain
plus the zero-free-half-plane and critical-line equivalences for the
totalized `riemannZeta`) is provable from pinned Mathlib theorems alone,
with every exceptional point explicit and no new axiom, and its frozen
contract will survive independent review without weakening any exclusion.

Frozen contract: `domains/riemann-hypothesis/TARGET_BRIDGE_CONTRACT.md`
(draft v2, adversarially reviewed once, verdict `SOUND_WITH_FIXES`, all
findings applied). Remaining exit requirements: independent reviewer
acceptance of the statements against the contract (including the FE-first
scope note) and the `SOURCE_CONTRACTS.md` acceptance review before any
Annex A xi work. That source review was subsequently satisfied by `RH-006` on
2026-08-06. The `S0-TRUST` precondition is satisfied as of 2026-08-06
(PR #298 merged; see the capability map's dated closure addendum).

Expected output:

- exact Lean statement in a non-built review artifact first;
- paper proof or proof skeleton with all analytic side conditions;
- declaration dependency list;
- counterexample search or adversarial failure analysis;
- independent reviewer acceptance before promotion to built Lean.

Exit criteria:

- no `sorry`, `admit`, custom axiom, or unreviewed assumption;
- no hidden use of RH or a source-equivalent condition;
- failure is retained as a scoped negative result.

## RH-004: kernel-check the selected foundation

ID: `RH-004`

Status: **COMPLETE 2026-08-06**

Closure evidence: merged PR #299 (`288d65b`). `lake build`, the no-sorry
gate, and the generated ResearchOS axiom audit are green on the built
module `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/TargetBridge.lean`
(eight declarations, `standard` axiom base per row); the eight
`RH-BRIDGE-*` ledger rows, regenerated registries/audits, and the promotion
review record (`notes/reviews/RH_BRIDGE_PROMOTION_2026_08_06.md`) landed in
the same PR. One kernel round exposed exactly the pre-registered P1-d
witness-cast obligation; the audit-recorded alternate closed it. Named
barrier `S1-TARGET` is closed (dated addendum in the capability map). This
changes a named blocker, not the truth status of RH.

Kind: theorem

Hypothesis: The reviewed theorem contract can be represented in Lean without
weakening the statement or expanding the trusted base.

Expected output:

- one scoped built module under the non-ECDLP `ResearchOS` lane;
- a domain-specific result record and axiom-audit coverage designed before the
  theorem is counted; the reviewed design
  (`domains/riemann-hypothesis/S0_TRUST_DESIGN.md`, v2, adversarially
  reviewed `SOUND_WITH_FIXES`) was implemented and merged through PR #298
  (`d6e146fa`), so this trust prerequisite is satisfied;
- CI-green proof with exact trust and claim scope.

Exit criteria:

- `lake build` passes;
- no-sorry and axiom audits cover the declaration;
- independent review confirms the Lean statement matches the paper statement;
- the result changes a named route decision or blocker.

## RH-006: second-agent replay of the source-contract package

ID: `RH-006`

Status: **COMPLETE 2026-08-06**

Closure evidence: the replay record dispositioned all 59 rows (57 confirmed,
2 flagged), and the external acceptance pass applied both amendments with no
open source discrepancy. The source-named `LAG07` tilde and the derived
conjugate-adjoint reflection are now distinct; the `BD02-v2` measure quote now
uses literal `dt` while preserving the derived `d tau/(2*pi)` normalization.
Records: `notes/reviews/RH006_SOURCE_REPLAY_2026_08_06.md` and
`notes/reviews/RH006_SOURCE_CONTRACT_ACCEPTANCE_2026_08_06.md`.

Kind: research / review

Hypothesis: A statement-by-statement replay of `SOURCE_CONTRACTS.md` against
the three SHA-256-pinned PDFs (checksums re-verified 2026-08-05 —
`notes/reviews/RH_SOURCE_PDF_CHECKSUM_REPLAY_2026_08_05.md`) will either
confirm every transcription (signs, cutoffs, measures, multiplicity
conventions, recorded errata) or surface exact discrepancies before any
LAG07-convention-touching Lean work begins.

Why it matters: before this task, `SOURCE_CONTRACTS.md` was still "proposed
under independent review"; its acceptance was a required gate before the
xi-package promotion (`RH-007`) and every later Li/Weil/Nyman contract. The xi
contract still needs its own explicit independent acceptance record before
promotion. A wrong sign or cutoff transcribed from a source would poison every
downstream formalization.

Expected output: a replay record under `notes/reviews/` comparing each
`SOURCE`-role statement in `SOURCE_CONTRACTS.md` with the pinned PDFs
(exact locators), explicitly re-checking: the Λ normalization and LAG07
(2.7) factor-2 note; SC-LI-01/02/03 cutoffs and star limits; SC-WEIL-01/02;
SC-BOMB-01/02/03 including the trace-formula signs and the autocorrelation
measure (`dy`, not `dy/y`); SC-BRIDGE-01..04; SC-NB-01..06 including both
recorded v2 errata. Discrepancies listed with severity; no contract text
edited by this task.

Exit criteria: every `SOURCE` row confirmed or flagged; the record is
sufficient for the external reviewer to accept or amend
`SOURCE_CONTRACTS.md` in one pass.

Files allowed to edit: `notes/reviews/`, `tasks/RIEMANN_HYPOTHESIS.md`.

## RH-007: xi-package promotion after contract acceptance

ID: `RH-007`

Status: **ACTIVE - xi contract accepted; separate built promotion authorized, pending kernel and axiom CI**

Kind: theorem / review

Activation basis (2026-08-06): `RH-006` accepted the amended source-contract
package. The remaining immediate decision is whether the xi contract itself
deserves explicit independent acceptance. Static plausibility of its draft is
not a kernel verdict. Subsequent update (2026-08-06): the independent review
accepted all twelve X1-X11 declarations with editorial-only fixes; record:
`notes/reviews/RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`. Promotion is now
authorized only as a separate kernel-checking change.

Hypothesis: the accepted xi-package contract
(`domains/riemann-hypothesis/XI_PACKAGE_CONTRACT.md`, draft v2) and its
non-built Lean draft (`drafts/RiemannXi.lean`, statically audited) can be
promoted without changing the X1-X11 statement surface, exactly as the bridge
was — module +
`RH-XI-*` ledger rows + regenerated registry/audit in one PR, kernel
verdict via CI.

Completed acceptance output:
`notes/reviews/RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`, with an explicit
`ACCEPT WITH APPLIED EDITORIAL FIXES`. The review checks all X1-X11
statements, the X5 sign, the X6 zero-set split, exceptional points, the
canonical RH target, X11's analytic-order transport, and the boundary between
static review and kernel verification.

Current expected output: built
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean` (X1-X11),
closing barrier `S1-XI` and the analytic-order-transport component of
`S1-MULTIPLICITY`; ledger, registry, audit, and promotion review record in
the same PR.

## RH-005: bounded computation policy

ID: `RH-005`

Status: **PARKED pending a selected claim**

Kind: experiment / review

Hypothesis: A bounded interval-arithmetic certificate can be valuable only when
it validates a preregistered finite claim needed by the selected route.

Expected output:

- producer and independently written validator;
- exact precision, interval, coverage, failure, and resource contracts;
- classification as bounded computational evidence only.

Exit criteria:

- no finite computation is represented as evidence for global RH;
- every certificate has complete coverage semantics and deterministic replay;
- the run is not authorized until a dated task decision supplies a finite target
  and budget.

## Global hard rules

- Never claim a proof unless the exact target is checked and the encoding is
  independently reviewed.
- Never use numerical agreement, many verified zeros, or positive initial Li
  coefficients to infer the infinite statement.
- Never use the Euler product or Dirichlet series outside a proved convergence
  region.
- Never rearrange zero sums, differentiate a logarithm, divide by zeta, or shift
  a contour without explicit convergence, branch, pole, and residue obligations.
- Never count an equivalent restatement as progress by itself.
- Never launch an open-ended model or compute sweep. Every run needs a fixed
  question, budget, validator, and stop condition.
- Preserve negative results and uncertainty.

## Activation milestones

| horizon | required result |
|---|---|
| first 30 days | `RH-001` capability map and exact source extracts |
| first 60 days | `RH-002` dispositions for the top three routes |
| first 90 days | one reviewed theorem candidate, or an evidence-backed decision that none should be activated yet |

At day 90, create a separate RH repository only if the selected route needs an
independent dependency graph, ledger, or CI surface. Until that threshold, the
existing `ResearchOS` control plane is the smaller reversible choice.
