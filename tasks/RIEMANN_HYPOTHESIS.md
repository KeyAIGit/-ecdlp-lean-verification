# Riemann Hypothesis research queue

This file owns the active KeyAI queue for the Riemann Hypothesis. The domain
boundary is `domains/riemann-hypothesis/README.md`; the canonical target and
source map live in `domains/riemann-hypothesis/corpus.md`.

The lane is **active exploratory research**, not a claimed proof program with a
known path to completion. Existing ECDLP state remains authoritative in its own
decision substrate and queue. New discretionary mathematical work defaults to
this queue during the RH activation cycle.

## Current decision

Decision update: 2026-08-07. `RH-001`, `RH-002`, `RH-003`, `RH-004`,
`RH-006`, `RH-007`, and `RH-008` are complete.
`S0-TRUST` is closed by PR #298, and the repo-local target bridge is built,
audited, and merged by PR #299, closing `S1-TARGET`. The `RH-002`
independent disposition review completed 2026-08-07: all three `PARK`
dispositions are **CONFIRMED** (Route A Li/Weil, Route B
Nyman-Beurling/Báez-Duarte, Route C explicit formula), no theorem-bearing
route is selected, no route execution is authorized, and the review's dated
wording amendments are applied in `ROUTE_TRIAGE.md` and
`SOURCE_CONTRACTS.md`; record:
`notes/reviews/RH002_DISPOSITION_REVIEW_2026_08_07.md`. Second-agent replay
of the load-bearing `[D]` desk-citation locators remains an outstanding
finality gate tracked in `ROUTE_TRIAGE.md`; it does not occupy a queue
slot. The `RH-006` source replay has
59/59 rows dispositioned (57 confirmed, 2 amended), and the accepted package
is recorded in `RH006_SOURCE_CONTRACT_ACCEPTANCE_2026_08_06.md`. `RH-007`
completed through merged PR #304 (`afdae08`): its twelve X1-X11 declarations
are built, ledgered, registry-covered, and axiom-audited, closing `S1-XI`.
`RH-008` completed through merged PR #307 (`c277b86`): its sixteen Z1-Z9
conjugation declarations are built, ledgered, registry-covered, and
axiom-audited. It closes only the conjugation leg: `S1-CONJ`
remains open on divisor invariance, `S1-MULTIPLICITY` remains open, and no
claim about RH's truth changes. `RH-009` (independent acceptance of the
multiplicity/divisor statement surface) completed 2026-08-07: ACCEPT WITH
APPLIED EDITORIAL FIXES, zero blocking items, record
`RH009_MULT_CONTRACT_ACCEPTANCE_2026_08_07.md`. `RH-010` completed
2026-08-07 through merged PR #313 (`2a20629`): the kernel checked all
thirty-four M1-M17 declarations on the exact merged head, with complete
inverse ledger coverage and both axiom audits green. This closes
`S1-MULTIPLICITY` and — together with merged PR #307 — completes the
`S1-CONJ` exit evidence; both closures are recorded in the dated
capability-map addendum. `RH-011` completed 2026-08-07: the three-lens panel
accepted the 23-signature zero-set slice surface with zero blocking items
(record `RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`); acceptance changes no
barrier row — `S1-GLOBAL-ZEROS` remains OPEN. By this dated decision the
single ACTIVE slot moves to `RH-012` (slice drafting plus separate kernel
promotion, the RH-010 pattern; CI is the sole judge). Do not
begin a route proof attempt, large computation, new equivalence formalization,
or autonomous hypothesis sweep.

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

Status: **COMPLETE 2026-08-07**

Closure evidence: the independent disposition review of all three recorded
dispositions, their source anchors, and revival bars completed 2026-08-07
with verdicts **CONFIRM / CONFIRM / CONFIRM** — all three `PARK`s stand, no
`PARK` became `SELECT`, and the review authorized no route execution, no
computation, and no theorem construction. Dated wording amendments were
applied to `domains/riemann-hypothesis/ROUTE_TRIAGE.md` (audit defects D1,
D2, D3, D5, D6, D7, D23 of
`notes/reviews/RH_LANE_CLAIMS_AUDIT_2026_08_07.md`, plus three Route A
precision items including the preregistered broadening of trigger `A-T2`)
and to `domains/riemann-hypothesis/SOURCE_CONTRACTS.md` (audit defect D4,
the withdrawn-infinitude recurrence, per the `SC-NB-04` amendment
precedent); no disposition, budget, or revival bar changed. Record:
`notes/reviews/RH002_DISPOSITION_REVIEW_2026_08_07.md`. Second-agent replay
of the load-bearing `[D]` desk-citation locators remains an outstanding
finality gate recorded in `ROUTE_TRIAGE.md`; it does not hold a queue slot.

Reactivation basis (2026-08-06): the route-neutral foundation cycle through
`RH-007` is complete. The only unfinished RH-002 exit item is independent
review of the three recorded dispositions, their source anchors, and revival
bars. This review may confirm or amend a disposition but does not itself
authorize theorem construction, computation, or route execution.

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

Status: **COMPLETE 2026-08-06**

Closure evidence: independently accepted statement surface in PR #303
(`202eba0`), followed by the separately gated built promotion in PR #304
(`afdae08`). The promotion carries exactly twelve `RH-XI-*` ledger rows,
complete ResearchOS inverse coverage, the generated axiom audit, and the
promotion review record. Its repaired final head passed the full build,
no-incomplete-proof gate, ECDLP axiom audit, and ResearchOS per-row axiom
audit. This closes `S1-XI` only; `S1-MULTIPLICITY` remains open.

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

Completed output: built
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean` (X1-X11),
merged in PR #304 with twelve ledger rows, registry coverage, generated audit,
and promotion review in the same PR. Barrier `S1-XI` is closed; the local
analytic-order-transport component is discharged, but `S1-MULTIPLICITY`
remains open pending a divisor interface and multiplicity-preserving
symmetries.

## RH-008: conjugation-package promotion

ID: `RH-008`

Status: **COMPLETE 2026-08-06**

Acceptance disposition: the reviewed promotion atomically activated and
completed `RH-008` while reconciling already-pushed in-flight work under the
repository charter. It did not select or execute an RH route. `RH-002` kept
the sole ACTIVE slot for its independent `PARK`/`PARK`/`PARK` disposition
review (closed 2026-08-07; the slot passed through `RH-009`, accepted the same day, to `RH-010`).

Closure evidence: the built module, sixteen ledger rows, inverse registry
coverage, generated axiom audit, synchronized draft, and promotion review
land together. The exact promotion head must pass the full build,
no-incomplete-proof gate, and both axiom audits before merge. This closes no
named barrier: the divisor-invariance half of `S1-CONJ` remains open.

Kind: theorem / review

Activation basis (2026-08-06): both prerequisites the `S1-CONJ` contract
carries are now kernel-checked on `main` — bridge P2/P3 (PR #299, `288d65b`)
for Z8, and the xi definition X1 (PR #304, `afdae08`) for Z7 and Z9-xi. The
contract's statement surface was independently accepted in PR #301
(`7bf13ab`), including the corrected Annex-B `F1` sign. The reserved-draft
clause recorded there ("reserved for a later, separately reviewed promotion
after its prerequisites are accepted") is therefore satisfied.

Hypothesis: the accepted Z1-Z9 statement surface can be promoted without any
statement change — module + sixteen `RH-CONJ-*` ledger rows + regenerated
registry and axiom audit + promotion review record in one change, with the
kernel verdict delivered by CI, exactly as the bridge (RH-004) and the xi
package (RH-007) were.

Expected output:

- built `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Conj.lean`
  (Z1-Z9, sixteen public declarations) importing the built bridge and xi
  modules directly;
- a drafts-lane mirror byte-identical from the first `import` to end of file;
- sixteen ledger rows at axiom base `standard`, complete inverse coverage,
  and `notes/reviews/RH_CONJ_PROMOTION_2026_08_06.md`.

Exit criteria:

- the full build, no-incomplete-proof gate, inverse ledger coverage, and both
  axiom audits are green on the exact merged head;
- no statement deviates from the accepted contract; a statement change stops
  promotion and returns to contract review;
- the capability map records the conjugation leg only: `S1-CONJ` stays open
  because divisor invariance under `ρ ↦ 1 − conj ρ` belongs to the still-open
  `S1-MULTIPLICITY` package;
- no claim about the truth of RH is made or implied.

## RH-009: independent acceptance of the multiplicity/divisor statement surface

ID: `RH-009`

Status: **COMPLETE 2026-08-07**

Closure evidence: three-lens acceptance panel (mathematical truth, pin
fidelity, claim boundary) under owner-delegated review authority returned
**ACCEPT WITH APPLIED EDITORIAL FIXES** — zero blocking items, two editorial
fixes applied to the contract (death condition 5 rewritten to cover both
support identifications; the exceptional-points anti-pitfall bullet corrected
to distinguish binder hypotheses from carrier scoping). Record:
`notes/reviews/RH009_MULT_CONTRACT_ACCEPTANCE_2026_08_07.md`. Acceptance
covers the 34-signature statement surface only: it produces no built module,
no ledger row, and no kernel verdict, and it changes no barrier row.

Kind: review

Activation basis (2026-08-07): `RH-002` closed on 2026-08-07 — all three
`PARK` dispositions confirmed by independent review, no route selected, no
route execution authorized
(`notes/reviews/RH002_DISPOSITION_REVIEW_2026_08_07.md`) — freeing the
queue's single ACTIVE slot. This dated queue decision installs `RH-009` as
the sole ACTIVE task, per
`domains/riemann-hypothesis/MULTIPLICITY_QUEUE_ENTRY_PROPOSAL.md` (the
acceptance-only variant). The earlier pull request carrying
`MULTIPLICITY_CONTRACT.md` and `drafts/RiemannMult.lean` was blocked by an
independent reviewer and closed unmerged; the reviewer's ordering is that
the corrected contract returns as an **acceptance-only** change after
`RH-002` closes, with kernel promotion held back as a separate change
(`RH-010`). Activating this task selects no route, unparks no route, and
makes no claim about the truth of RH.

Provenance: every prerequisite of the surface is kernel-checked on current
`main` — the target bridge (PR #299, `288d65b`), the xi package (PR #304,
`afdae08`, supplying `riemannXi` and X11
`analyticOrderAt_riemannXi_eq_riemannZeta`,
repo:`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean:248`), and the
conjugation package (PR #307, `c277b86`, supplying
`analyticOrderAt_riemannZeta_conj` repo:`…/Conj.lean:440` and
`analyticOrderAt_riemannXi_conj` repo:`…/Conj.lean:452`). No statement waits on
an unmerged PR. PR #306 and PR #308 are CLOSED and UNMERGED and must not be
cited as provenance in the contract, the draft, the PR description, commit
metadata, or any review record.

Hypothesis: the corrected statement surface M1-M17 of
`domains/riemann-hypothesis/MULTIPLICITY_CONTRACT.md` — **exactly thirty-four
public signatures, each spelled explicitly in a `lean` block**, mirrored by the
thirty-four declarations of `domains/riemann-hypothesis/drafts/RiemannMult.lean`
— can be independently accepted at the pin without weakening, dropping, or
inventing a statement, with every dependency either pinned Mathlib or a
kernel-checked theorem on `main`.

Why it matters: acceptance of a statement surface is the only reviewable gate
that exists before elaboration. Static review is not a kernel verdict, and the
drafts lane is invisible to CI, so a package that is promoted without a prior
accepted surface has never been checked by anyone against anything. Separating
acceptance from promotion also keeps a statement change cheap: it is repaired in
review rather than discovered mid-promotion.

Inputs:

- `domains/riemann-hypothesis/MULTIPLICITY_CONTRACT.md` (draft v2)
- `domains/riemann-hypothesis/drafts/RiemannMult.lean` (non-built; its
  `drafts/README.md:30` row)
- `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:386`
  (`S1-MULTIPLICITY`) and `:389` (`S1-CONJ`)
- built modules on `main`: `…/RiemannHypothesis/TargetBridge.lean`,
  `…/Xi.lean`, `…/Conj.lean`
- pinned Mathlib at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0)

Expected output:

- one acceptance record under `notes/reviews/` (sibling precedents:
  `notes/reviews/RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`, and the
  `Acceptance note 2026-08-06` of `CONJ_SYMMETRY_CONTRACT.md`), carrying an
  explicit `ACCEPT`, `ACCEPT WITH APPLIED EDITORIAL FIXES`, or `REJECT`;
- a per-signature disposition covering all thirty-four signatures, including the
  four M15 specializations that a previous revision mandated in prose only and
  that are now spelled at `MULTIPLICITY_CONTRACT.md:1170`, `:1174`, `:1184`,
  `:1188` (`riemannXi_divisor_univ_conj`, `riemannXi_divisor_strip_conj`,
  `riemannXi_divisor_univ_one_sub_conj`, `riemannXi_divisor_strip_one_sub_conj`);
- corrections applied in place to the contract, the drafts mirror, and the
  `drafts/README.md` row;
- **by construction: no built module, no import added to `ResearchOS.lean`, no
  ledger row, no entry in `data/researchos_result_registry.json` or
  `data/result_registry.json`, no `VERIFIED_RESEARCHOS.md` line, no regenerated
  axiom audit, and no kernel verdict.**

Exit criteria:

- an independent reviewer records a disposition for every one of the
  thirty-four signatures; no signature is mandated in prose only;
- every `file:line` locator in the contract and the draft is replayed at the pin
  and against current `main`, and every mismatch is corrected or flagged;
- provenance cites only merged work (#299 `288d65b`, #304 `afdae08`, #307
  `c277b86`) and current `main`; no reference to PR #306 or PR #308 survives
  anywhere in the contract, the draft, the review record, the PR description, or
  commit metadata;
- no model identifier appears in the PR description, commit metadata, or any
  repository artifact touched by the change;
- `AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero` is cited with its true
  namespace and hypotheses — `Mathlib/Analysis/Analytic/Order.lean:687`, inside
  `namespace AnalyticOnNhd` (`:575`–`:700`), signature
  `[PreconnectedSpace 𝕜] {f : 𝕜 → E} (z : 𝕜) (hf : ∀ z₀, AnalyticAt 𝕜 f z₀) :
  analyticOrderAt f z = ⊤ ↔ f = 0` — so the analyticity hypothesis is
  everywhere-pointwise and the conclusion is global vanishing of `f`, not
  vanishing on a set; the unqualified spelling is rejected;
- every occurrence of "finite order" is replaced by **finite local analytic
  order** (`analyticOrderAt … ≠ ⊤`, M12) or **finite local meromorphic order**
  (`meromorphicOrderAt … ≠ ⊤`, the hypothesis consumed by
  `MeromorphicNFOn.zero_set_eq_divisor_support`); no phrasing may be read as a
  growth order of an entire function;
- the accepted surface claims only pointwise local finiteness (M12, M16′) and
  divisor-support/zero-set equality (M13, M16″); **no statement, note, or annex
  claims that the ξ or ζ divisor support is infinite**, and none claims local
  finiteness of the zero set beyond what the pinned lemmas give;
- the record states in terms that cannot be misread that it is **not** a kernel
  verdict: `drafts/RiemannMult.lean` lies outside every lake target
  (`lakefile.toml:2` declares `defaultTargets = ["Ecdlp", "ResearchOS"]`), the
  build step `.github/workflows/ci.yml:420` runs `lake build` over those targets
  only, and the no-incomplete-proof scan at `:359` covers only `Ecdlp.lean`,
  `Ecdlp/`, `ResearchOS/`, `ResearchOS.lean`; therefore a green CI run on this
  change says nothing about the draft;
- no barrier row is changed: acceptance of a statement surface closes neither
  `S1-MULTIPLICITY` nor the divisor-invariance half of `S1-CONJ`, and the
  capability map is not edited to suggest otherwise;
- no `sorry`, `admit`, custom axiom, new `def`, or unreviewed assumption appears
  in the accepted surface; the package remains free of enumeration, counting,
  growth, Hadamard products, Li coefficients, and zero-simplicity claims;
- the change carries no promotion; if the reviewer's fixes alter any statement,
  the altered statement is re-accepted here rather than carried into `RH-010`;
- rejection or partial acceptance is retained as a scoped negative result (for
  example the M12 death condition: if the S1M-FIN obligation resists every
  recorded route, M13 is dropped and the divisor block is reduced, never
  hypothesis-floated to the caller and called an exit);
- no route is selected or unparked, and no claim about the truth of RH is made
  or implied.

Files allowed to edit:

- `domains/riemann-hypothesis/MULTIPLICITY_CONTRACT.md`
- `domains/riemann-hypothesis/drafts/RiemannMult.lean` and
  `domains/riemann-hypothesis/drafts/README.md`
- a new curated record under `notes/reviews/`
- `tasks/RIEMANN_HYPOTHESIS.md`

Files that must not be edited:

- `ResearchOS/`, `ResearchOS.lean`, `Ecdlp/`, `Ecdlp.lean`
- `data/researchos_result_registry.json`, `data/result_registry.json`,
  `VERIFIED.md`, `VERIFIED_RESEARCHOS.md`, and generated views
- `lakefile.toml`, `lake-manifest.json`, `.github/workflows/`
- `repo/ECDLP_DECISION_SUBSTRATE.json` and ECDLP experiment authorizations

How to verify:

- independent mathematical review of all thirty-four signatures against the pin;
- replay every locator with `rg` at
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` and on current `main`;
- run `python3 scripts/check_domains.py` and
  `python3 scripts/check_repo_artifacts.py`;
- confirm the diff adds no file under a lake target, changes no registry, ledger
  or audit artifact, and leaves `ResearchOS.lean` untouched;
- confirm the diff and its commit metadata contain no model identifier and no
  reference to PR #306 or PR #308.

## RH-010: multiplicity/divisor package promotion after contract acceptance

ID: `RH-010`

Status: **COMPLETE 2026-08-07**

Closure evidence: merged PR #313 (`2a20629`). The full build on the exact
merged head kernel-checked all thirty-four declarations; inverse ledger
coverage is complete (81 rows → 82 declarations); both axiom audits are green
with every new row at axiom base `standard`; the drafts-lane mirror is
byte-identical from the first import. The only promotion-round repair was
prose (the textual no-incomplete-proof scan tripped on the module's own
claim-boundary comment; reworded, no proof or statement changed). Record:
`notes/reviews/RH_MULT_PROMOTION_2026_08_07.md`. This closes
`S1-MULTIPLICITY` and — together with merged PR #307 — completes the
`S1-CONJ` exit evidence; the dated capability-map addendum records both
closures. No claim about the truth of RH changes.

Activation basis: `RH-009` accepted the statement surface on 2026-08-07
(record above); the dated queue decision of that day moved the single ACTIVE
slot to this promotion task.

Kind: theorem

Blocking basis (2026-08-07): the reviewer requires independent acceptance of the
statement surface and the built promotion to be **two separate changes**, in
that order — the path the bridge took (acceptance-free foundation, PR #299
`288d65b`), the xi package took (acceptance PR #303 `202eba0`, then promotion PR
#304 `afdae08`), and the conjugation package took (acceptance PR #301 `7bf13ab`,
then promotion PR #307 `c277b86`). This task is blocked until `RH-009` records
an acceptance, and it may only be activated by a dated queue decision at that
point; `RH-009` holds the queue's sole ACTIVE slot as of 2026-08-07. An
acceptance change must not carry this promotion, and this task must not re-open
statement questions: any needed statement change returns to `RH-009`.

Hypothesis: the surface accepted under `RH-009` can be represented in Lean and
kernel-checked **without changing a single accepted statement** and without
expanding the trusted base — module plus one ledger row per public declaration
plus regenerated registry and axiom audit plus promotion review in one change,
with the verdict delivered by CI.

Why it matters: static review of the drafts lane is source reading only; CI does
not elaborate `drafts/RiemannMult.lean`. Until a built promotion is green, no
statement of this package counts as proved under the one invariant, and neither
the `S1-MULTIPLICITY` exit evidence nor the divisor half of `S1-CONJ` has any
kernel support.

Inputs:

- the `RH-009` acceptance record and the accepted
  `MULTIPLICITY_CONTRACT.md` surface (M1-M17, thirty-four signatures)
- `domains/riemann-hypothesis/drafts/RiemannMult.lean`
- built `…/RiemannHypothesis/TargetBridge.lean`, `…/Xi.lean`, `…/Conj.lean` on
  `main`
- pinned Mathlib at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0)

Expected output:

- one built module
  `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean` importing the
  built xi and conjugation modules directly, plus its import line in
  `ResearchOS.lean`;
- a drafts-lane mirror byte-identical from its first `import` to end of file;
- one `RH-MULT-*` ledger row per public declaration with its declared axiom
  base, complete inverse registry coverage, and regenerated
  `ResearchOS/LedgerAxiomAudit.lean`, `data/researchos_result_registry.json`,
  and `VERIFIED_RESEARCHOS.md`;
- a promotion review record under `notes/reviews/`;
- only those capability-map and RH-queue updates the kernel outcome actually
  supports.

Exit criteria:

- on the exact merged head: `lake build` is green
  (`.github/workflows/ci.yml:420`), the no-incomplete-proof scan is green
  (`:359`), and both axiom audits are green (`:428` ECDLP lane, `:438`
  ResearchOS per-row lane);
- no `sorry`, `admit`, custom axiom, or `native_decide` extension of the trusted
  base; every ledger row carries axiom base `standard`;
- every public declaration of the module has a ledger row and inverse registry
  coverage; the counts agree with the accepted surface;
- **no statement deviates from the accepted surface.** A weakened hypothesis, an
  added or dropped signature, a renamed carrier, a new `def`, or a changed
  carrier set stops promotion and returns the change to `RH-009` for
  re-acceptance; proof-only repairs (term shapes, tactic choices, elaboration
  order) stay inside this task and are recorded in the promotion review;
- the promotion review records what the kernel outcome supports and no more:
  whether the ζ/ξ divisor interface and the multiplicity-preserving divisor
  symmetries named as remaining `S1-MULTIPLICITY` exit evidence
  (`MATHLIB_CAPABILITY_MAP.md:386`) are now kernel-checked, and whether the
  divisor-invariance half of `S1-CONJ` (`:389`) is discharged. This entry
  asserts no barrier closure in advance; a barrier row moves only on the
  reviewed evidence of the merged head, and generic pinned Mathlib never retires
  a row on its own;
- the established content is stated exactly: pointwise local finiteness of the
  analytic/meromorphic order (M12, M16′) and equality of divisor support with
  the zero set (M13, M16″). No record claims that the ξ or ζ divisor support is
  infinite, and no phrase reads as a growth order;
- failure of any gate is retained as a scoped negative result, with the blocking
  obligation named; a clean blocker is preferable to a promotion that quietly
  edits what was accepted;
- no route is selected or unparked; the promotion changes named-blocker
  bookkeeping only, and makes no claim about the truth of RH.

Files allowed to edit:

- `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean` (new),
  `ResearchOS.lean`, `ResearchOS/LedgerAxiomAudit.lean`
- `data/researchos_result_registry.json`, `VERIFIED_RESEARCHOS.md`
- `domains/riemann-hypothesis/drafts/RiemannMult.lean`,
  `domains/riemann-hypothesis/drafts/README.md`,
  `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md`
- a new curated record under `notes/reviews/`
- `tasks/RIEMANN_HYPOTHESIS.md`

Files that must not be edited:

- `MULTIPLICITY_CONTRACT.md`'s accepted statement blocks (a needed change sends
  the work back to `RH-009`)
- `Ecdlp/`, `Ecdlp.lean`, `data/result_registry.json`, `VERIFIED.md`
- `lakefile.toml`, `lake-manifest.json` (no Mathlib bump), `.github/workflows/`
- `repo/ECDLP_DECISION_SUBSTRATE.json` and ECDLP experiment authorizations

How to verify:

- CI on the exact merged head: full build, no-incomplete-proof scan, ECDLP axiom
  audit, ResearchOS per-row axiom audit;
- `python3 scripts/check_axioms.py researchos_axiom_audit.txt
  data/researchos_result_registry.json`, plus
  `python3 scripts/check_domains.py` and
  `python3 scripts/check_repo_artifacts.py`;
- an independent reviewer diffs every promoted signature against the accepted
  contract text and confirms character-level agreement;
- confirm the drafts mirror is byte-identical to the built module from the first
  `import` to end of file;
- confirm the diff and its commit metadata contain no model identifier and no
  reference to PR #306 or PR #308.

## RH-011: acceptance of the zero-set slice statement surface

ID: `RH-011`

Status: **COMPLETE 2026-08-07**

Closure evidence: three-lens acceptance panel under owner-delegated review
authority returned **ACCEPT WITH APPLIED EDITORIAL FIXES** on the 23-signature
zero-set slice surface — zero blocking items, five consolidated editorial
fixes applied (queue-position and prerequisite re-anchoring to the built
Mult.lean, conditionality prose settled, the N-SEQ ordering obligation
discharged by the merged promotion, and one factual lemma-existence
correction resolved by direct source read). Record:
`notes/reviews/RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`. Acceptance covers
the statement surface only: no kernel verdict, no barrier-row change —
`S1-GLOBAL-ZEROS` remains OPEN and all routes PARKED.

Kind: review

Activation basis (2026-08-07): `RH-010` closed `S1-MULTIPLICITY` and
completed the `S1-CONJ` exit evidence, so every package prerequisite of the
route-neutral zero-set slice is kernel-checked on `main`. This dated queue
decision installs the slice's acceptance as the sole ACTIVE task.

Hypothesis: the drafted contract
`domains/riemann-hypothesis/ZERO_SET_SLICE_CONTRACT.md` (23 public
signatures: xi zero-set topology; finite divisor sums over an arbitrary
compact set; symmetry invariance of those sums — parameterized by an
arbitrary compact `K`, with no cutoff shape anywhere, because choosing a
cutoff shape is a route selection and all routes remain PARKED) can pass
independent statement-surface acceptance without any statement change.

Expected output: an acceptance record under `notes/reviews/` in the RH-009
format — statement-surface acceptance only, no kernel content, no barrier-row
change; kernel promotion would be a separate later task under a new dated
decision.

Exit criteria:

- every statement reviewed for mathematical truth at exceptional points, pin
  fidelity, and claim boundary;
- the no-cutoff-shape neutrality property re-verified mechanically;
- any blocking finding stops acceptance and returns the contract to design;
- this task advances `S1-GLOBAL-ZEROS` bookkeeping only if acceptance lands,
  and closes no barrier in any case.

## RH-012: zero-set slice drafting and kernel promotion

ID: `RH-012`

Status: **ACTIVE 2026-08-07 — drafting plus kernel promotion as its own
change; the kernel via CI is the sole judge**

Kind: theorem

Activation basis (2026-08-07): `RH-011` accepted the 23-signature slice
surface with zero blocking items. This dated queue decision moves the single
ACTIVE slot to the build-out: a drafts-lane Lean file implementing the
accepted surface (statements character-identical; adversarially reviewed),
followed by a separate kernel-promotion change carrying the module, its
`RH-*` ledger rows, regenerated registries and audits, and the promotion
record — the RH-010 pattern exactly.

Exit criteria:

- the draft passes independent review with statements character-identical to
  the accepted contract;
- the promotion change passes the full build, no-incomplete-proof gate,
  inverse ledger coverage, and both axiom audits on the exact merged head;
- a statement change at any point stops the task and returns the surface to
  contract review;
- on green merge this advances `S1-GLOBAL-ZEROS` bookkeeping without closing
  it, and no claim about the truth of RH changes.

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
