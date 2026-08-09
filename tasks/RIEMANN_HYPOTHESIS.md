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
promotion, the RH-010 pattern; CI is the sole judge).

Decision update: 2026-08-08. `RH-012` completed through merged PR #320
(`2d80593`): the kernel checked all twenty-three zero-set slice declarations on
the exact merged head, with complete inverse ledger coverage and both axiom
audits green. Per its exit criteria this **advances the `S1-GLOBAL-ZEROS`
bookkeeping and does NOT close it** — that row lists six exit items, of which
the slice supplies a route-neutral form of one (finite divisor sums over an
arbitrary compact), leaves four untouched, and cannot reach the remaining two
(`|ρ| ≤ T` for Li, `|Im ρ| < T` for Weil) because supplying either would be a
route selection. All three `RH-002` dispositions remain `PARK`/CONFIRMED and no
route is selected. Separately the same day, eleven domain-neutral analysis
pillars were promoted to `ResearchOS/Analysis/` through merged PRs #318 and
#319 (thirty-five declarations under the `MB-`, `HK-`, `PL-`, `TC-` and `GO-`
prefixes); those are inventory only, took no queue slot, and moved no barrier
row. By this dated decision the single ACTIVE slot moves to `RH-013`, a
measurement-only re-verification of the `S1-GLOBAL-ZEROS` cost against a
directory the original assessment did not examine. Do not
begin a route proof attempt, large computation, new equivalence formalization,
or autonomous hypothesis sweep.

Decision update: 2026-08-08 (second). `RH-013` completed through merged PRs #322
and #324. `PROBE_BATTERY_DESIGN.md`'s scope statement — a governance constraint,
not a description — had gone stale by 92 built declarations across seven
modules, and so was silently forbidding probes that had become legitimate. It
now names all ten built modules and, more usefully, states that the authority is
`VERIFIED_RESEARCHOS.md` and the `ResearchOS.lean` import list rather than the
paragraph itself. §F adds 52 probe candidates over the newly built surfaces,
bringing the document to 84. Two adversarial reviews changed the content before
it landed, and a self-audit against the exit criteria caught one further defect
after: a note claiming a witness had been respecified while the text still
carried the original. Nothing was run; `MD-1`..`MD-6` remain outstanding, so no
probe is authorized by any of this. No barrier row changed and no ledger row was
added. By this dated decision the single ACTIVE slot moves to `RH-014`.

Decision update: 2026-08-08 (third). `RH-014` completed with a NULL RESULT, the
outcome its exit criteria named as likely and acceptable: all 107 declarations
of `Mathlib/Analysis/Complex/ValueDistribution/` were read at the pin, not one
names ζ or ξ, and the `S1-GLOBAL-ZEROS` cost therefore **stands as written**. No
barrier row was edited; the dated addendum records the measurement and the
adversarial correction applied during it. By this dated decision the single
ACTIVE slot moves to `RH-015`, applying the accepted editorial fixes to the two
upstream contracts.

Decision update: 2026-08-08 (fourth). `RH-015` completed: 40 editorial fixes
applied across the two accepted contracts, 3 withdrawn on inspection, and 5
stopped at the signature boundary — four renames and one convention change that
would each have edited a public signature, which the task forbids because the
stage-one acceptance is valid only for the surface as it stands. A mechanical
check confirms no signature moved. One finding was corrected in the opposite
direction: the acceptance record had judged `A4`'s `0 < R` to be mere
convenience, and an editor found a counterexample showing `A4` is FALSE at
`R = -1` too, so the negative-radius trap is package-wide. By this dated
decision the single ACTIVE slot moves to `RH-016`, the drafts-lane
transcription the argument-principle acceptance unlocks.

Decision update: 2026-08-09. `RH-016` completed through merged PR #328: the
argument-principle draft exists in the drafts lane, five signatures
character-identical to the corrected contract, reviewed under two independent
lenses with six findings applied. The kernel has NOT seen it. By this dated
decision the single ACTIVE slot moves to `RH-017`, the stage-two promotion that
asks the kernel.

Decision update: 2026-08-09. `RH-017` completed through merged PR #329. The
kernel accepted all five declarations on the third round; the axiom audit
reports 145 results on the allowed base with no `sorryAx`, no custom axiom and
nothing using `native_decide`; the full battery was re-run on the exact merged
head `16027ed` and the generators are at a fixpoint there. No barrier row moved
and `S1-GLOBAL-ZEROS` stays OPEN, as the entry required.

The slot does NOT move to Weierstrass drafting, which is what the 2026-08-08
acceptance unlocked. It moves to `RH-018`, repairing the Weierstrass contract
first, because
`notes/reviews/WEIERSTRASS_FINDINGS_VERIFICATION_2026_08_09.md` established that
three of that contract's applied explanations are mechanically false and that
its `W6` skeleton, as applied, cannot close. Drafting from a contract in that
state would spend kernel rounds discovering what a reader can already be told.
This repeats the `RH-015` → `RH-016` order deliberately.

Decision update: 2026-08-09 (second). `RH-018` completed through merged PR
#330 and corrective PR #333. The accepted 28-declaration surface never moved:
the statement-block digest remains
`4149484c52db2c30972ba1455e791706724fd740e8f5dc97886947ad26f93d38`.
PR #330 applied the mechanism and skeleton corrections; adversarial review then
found three documentation-boundary defects in that merged result, and PR #333
corrected them without touching a statement: the W7/W11/W12 counterexamples
now use the required distinct fibers, W12's `Nat.card` is described only as a
finite-fiber local multiplicity, and the upstream search is recorded as scoped
evidence rather than an exhaustive no-duplication claim. No barrier row moved.
By this dated decision the single ACTIVE slot moves to `RH-019`, drafts-lane
transcription and static review only. Kernel promotion, if the draft survives,
is a separate later task.

Decision update: 2026-08-09 (third). `RH-019` completes in this change: the
non-built `WeierstrassFactors.lean` draft contains exactly the accepted 28
W1–W12 declarations with complete proof-shaped bodies, and two independent
static lenses accepted the exact final file with zero blocking findings. The
review record is `WEIERSTRASS_DRAFT_REVIEW_2026_08_09.md`; the file SHA-256 is
`fe34390369b02dc0eea9f318ba60f971ff1fc6e170634ecdacbda9823160a810`.
Nothing in the drafts lane was elaborated, so this is not a kernel verdict.
No barrier or route changes. By this dated decision the single ACTIVE slot
moves to `RH-020`, the separate built promotion whose exact-head CI is the sole
judge.

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

Status: **COMPLETE 2026-08-08 — kernel-checked through merged PR #320
(`2d80593`); advances `S1-GLOBAL-ZEROS` bookkeeping without closing it**

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

## RH-013: extend the probe battery design to the whole built surface

ID: `RH-013`

Status: **COMPLETE 2026-08-08 — the probe battery design now covers the whole
built surface; merged PRs #322 and #324. Design only: nothing was run and no
batch was opened**

Kind: tooling

Activation basis (2026-08-08, owner decision): `RH-012` completed through
merged PR #320 and the single ACTIVE slot had to move
(`scripts/gen_status.py:69`, `scripts/check_status_consistency.py:609` enforce
exactly one ACTIVE RH contract). Two candidates were put to the owner; the
owner selected this one. The competing candidate — re-verifying the
`S1-GLOBAL-ZEROS` cost against `Mathlib/Analysis/Complex/ValueDistribution/`,
which the original assessment did not examine — is NOT abandoned. It is
recorded under "Deferred" below and in the 2026-08-08 capability-map addendum,
and it remains available for a later slot.

The defect being fixed. `domains/riemann-hypothesis/PROBE_BATTERY_DESIGN.md`
(dated 2026-08-07) declares at its lines 17-26 that the built kernel-checked
surface — "**the only surface any probe may reference**" — is exactly three
modules: `TargetBridge.lean` (P1-P5), `Xi.lean` (X1-X11), `Conj.lean` (Z1-Z9).
It further states that the M1-M17 multiplicity surface is "accepted only", that
its promotion holds the queue's ACTIVE slot, and that consequently "no probe
references any M declaration".

Every one of those statements is now false:

- `Mult.lean` (34 declarations, `RH-MULT-*`) was promoted and merged in PR #313;
- `ZeroSetSlice.lean` (23 declarations, `RH-SLICE-*`) in PR #320;
- five domain-neutral modules on `ResearchOS/Analysis/` — `MellinBound`,
  `PolyLiouville`, `HarnackDisc`, `ThreeCircles`, `GrowthOrder` (35
  declarations under `MB-`, `PL-`, `HK-`, `TC-`, `GO-`) — in PRs #318 and #319.

Because the stale sentence is a governance CONSTRAINT and not merely a
description, the staleness does not just omit material: it forbids probes that
are now entirely legitimate. Roughly 92 built declarations across 7 modules are
currently unreachable by any probe on the strength of a sentence that time has
falsified.

This matters beyond bookkeeping. The stated purpose of the pillar programme is
a large body of small, cheaply-repeatable machine checks that run WITHOUT
building a new pillar each time. Under the current design document, none of the
eleven pillars promoted on 2026-08-08 can be probed at all, so building further
pillars does not advance that purpose until this is corrected.

Exit criteria:

- the scope statement is rewritten against the ledger `VERIFIED_RESEARCHOS.md`
  rather than against memory, and states how it is to be kept current;
- every newly built surface is covered by probe CANDIDATES in the document's
  existing four classes (A regression, B cross-module composition, C type-level
  expressibility, D negative boundary) — no new class is invented;
- every candidate cites only built, merged declarations, each with a `file:line`
  opened and quoted; a drafts-lane citation fails the task;
- no candidate selects a route: any probe requiring a cutoff shape, contour,
  truncation family (`|ρ| ≤ T`, `|Im ρ| < T`) or test-function class is
  forbidden, and `RH-002`'s three `PARK` dispositions stay CONFIRMED;
- no candidate lets a green result read as evidence about the Riemann
  Hypothesis, and no Class D red result is presented as a discovery;
- in particular, a domain-neutral shelf lemma instantiated at `riemannXi` is an
  RH-lane claim in disguise and is not a shelf probe;
- the document's status is unchanged: **DESIGN ONLY, UNAUTHORIZED TO RUN**. This
  task freezes no batch, opens no batch, and runs nothing. The maintainer
  decisions MD-1..MD-6 remain outstanding and are not pre-empted;
- on completion this closes no barrier, changes no barrier row, and adds no
  ledger row.

Deferred, and deliberately not lost: the `S1-GLOBAL-ZEROS` re-verification
against `Mathlib/Analysis/Complex/ValueDistribution/` (`characteristic`,
CharacteristicFunction.lean:53; `logCounting`, LogCounting/Basic.lean:96,:272;
First Main Theorem, FirstMainTheorem.lean:97). `logCounting` is a counting
function and that barrier asks for counting, so the row's cost estimate is
unverified. Any later slot may take it up; until then the caveat stands as
recorded.

## RH-014: re-verify the `S1-GLOBAL-ZEROS` cost against the value-distribution directory

ID: `RH-014`

Status: **COMPLETE 2026-08-08 — measured; the row's cost STANDS and no barrier
row was edited. Null result, which the exit criteria named as the likely and
acceptable outcome**

Kind: reconnaissance

Activation basis (2026-08-08): this is the candidate the owner deferred when
selecting the probe-battery refresh for the `RH-013` slot, recorded at the time
as "not abandoned … available for a later slot". `RH-013` completed through
merged PRs #322 and #324, so the slot is free and this takes it.

The defect being measured. The `S1-GLOBAL-ZEROS` reconnaissance was carried out
without examining `Mathlib/Analysis/Complex/ValueDistribution/`, which at the
pin contains `characteristic` (CharacteristicFunction.lean:53), `logCounting`
(LogCounting/Basic.lean:96, :272) with monotonicity and bound lemmas,
`logCounting_isBigO_one_iff_analyticOnNhd` (Asymptotic.lean:108), and a First
Main Theorem (FirstMainTheorem.lean:97, :109). `logCounting` is a counting
function and `S1-GLOBAL-ZEROS` is the barrier asking for counting, so the row's
cost estimate is **unverified — not wrong, unverified**. The zero-set slice
promotion (`RH-012`) made that row load-bearing, which is what makes the check
worth a slot now.

Exit criteria:

- every declaration under `Mathlib/Analysis/Complex/ValueDistribution/` is read
  at the pin and recorded with a locator and its statement;
- the reading is set against the six exit items the `S1-GLOBAL-ZEROS` row
  actually lists, item by item, rather than against the row's title;
- a dated capability-map addendum states either that the row's cost stands as
  written or that it does not, with the evidence either way — **a null result is
  a complete and acceptable outcome**, and is the more likely one;
- the two route-specific items (`|ρ| ≤ T` for Li, `|Im ρ| < T` for Weil) are
  reported as out of reach regardless of what the directory contains, since
  supplying either is a route selection;
- if the directory does bear on the row, that is recorded as a MEASUREMENT; any
  change to the row's status remains a separate change with its own independent
  review, and no barrier is closed by this task;
- nothing here selects a route, adds a ledger row, or asserts anything about the
  truth of the Riemann Hypothesis.

Anti-goal, stated because the temptation is real: Nevanlinna theory is the
natural home of zero-counting, and finding a counting function in Mathlib will
feel like progress on `S1-GLOBAL-ZEROS`. It is not, until someone shows the
pinned statements discharge the row's listed exit items for ζ or ξ specifically.
Generic counting machinery for arbitrary meromorphic functions lowers the cost
of a future exit and retires no row — the same rule that governs every package
on the `analysis-generic` shelf.

## RH-015: apply the accepted editorial fixes to the two upstream contracts

ID: `RH-015`

Status: **COMPLETE 2026-08-08 — 40 fixes applied, 3 withdrawn, 5 stopped at the
signature boundary; no public signature moved, verified mechanically**

Kind: contract maintenance

Activation basis (2026-08-08): `RH-014` completed with a null result — the
`S1-GLOBAL-ZEROS` cost stands and no barrier row was edited. The slot moves to
the one piece of accepted work that is fully specified and currently blocking a
drafter.

Both `ARG_PRINCIPLE_CONTRACT.md` and `WEIERSTRASS_FACTORS_CONTRACT.md` took
stage-one acceptance on 2026-08-08 (merged PR #323, records in
`notes/reviews/`), with **zero blocking findings from six reviewers** and **no
lens asking for a signature change**. Those records deliberately enumerated the
41 editorial fixes without applying them, so that the record and the object it
accepts would not move together. Applying them is this task.

Why it is worth a slot rather than being left to whoever drafts next: two of the
argument-principle findings **re-price the package**, and in the direction that
misleads. `A1` is registered as the HIGH-severity gate and described as the
package's single genuinely new move, while a pinned lemma the contract never
cites appears to leave a one-step delta; and the `|R|` sign-flip the contract
calls absent at the pin already exists. A drafter reading the unfixed contract
would prepare for the wrong difficulty.

Exit criteria:

- every enumerated fix is applied or explicitly declined with a reason recorded
  in the acceptance record; silence is not an outcome;
- **no public signature changes.** No lens asked for one. If applying a fix
  turns out to require a signature change, that fix STOPS and the surface
  returns to contract review — it does not proceed under this task;
- the two cost-reducing findings are **confirmed against the pin before being
  applied**, since they were single-lens findings with no adversarial verifier,
  and a wrong "this is cheaper than you thought" invites a drafter to skip
  preparation. If confirmation fails, the finding is recorded as withdrawn;
- the `0 < R` soundness finding is applied as a package-wide statement, not a
  `W1`-local one;
- each acceptance record gains a dated line recording which fixes landed;
- no drafts-lane file is created by this task, no ledger row is added, no
  barrier row changes, and no route is selected.

## RH-016: draft the circle-only argument-principle package

ID: `RH-016`

Status: **COMPLETE 2026-08-08 — draft written and independently reviewed;
merged PR #328. The kernel did not check it — that is RH-017's business**

Kind: theorem

Activation basis (2026-08-08): `RH-015` completed — the two accepted contracts
carry their editorial fixes and no public signature moved. Under the two-stage
gate, a stage-one acceptance record unlocks exactly one thing: the drafts-lane
transcription. `ARG_PRINCIPLE_CONTRACT.md` now has both its acceptance record
(merged PR #323) and its corrections, so that transcription is the next step and
it is fully specified.

The argument-principle package is chosen over Weierstrass because `RH-015`
established that the two contracts are in different states of readiness.
Weierstrass drew thirteen pin-lens findings concentrated in the `W12` proof
skeleton — its statement surface is sound while its PROOF PLAN is the
least-verified part of the contract, which is the opposite of where its risk
register puts the difficulty. Drafting it now would be drafting against a plan
nobody has checked. The argument principle has the reverse profile: its
difficulty was mis-registered as HIGH at `A1`, `RH-015` re-priced it against the
pin, and the corrected contract now names where the real work is
(`S1AP-LOGD` is the sole remaining HIGH).

Exit criteria:

- a drafts-lane file `domains/riemann-hypothesis/drafts/ArgPrinciple.lean`
  implementing `W1` and `A1`-`A4`, five signatures, each CHARACTER-IDENTICAL to
  the corrected contract — verified mechanically, not by eye;
- complete proof bodies throughout: no proof placeholder of any spelling, and no
  new axiom;
- the file stays outside every lake target, so the Lean kernel does NOT check it
  and no CI run on this task is evidence about it. The kernel verdict comes only
  from a separate stage-two promotion change;
- every Mathlib lemma invoked is opened at the pin and its locator recorded
  inline, including the `A1` chain `RH-015` verified
  (`Meromorphic/IsolatedZeros.lean:99`, `Analytic/IsolatedZeros.lean:141`,
  `Meromorphic/Basic.lean:40`, `Normed/Field/Basic.lean:242`);
- the `0 < R` soundness note is honoured: no proof may quietly relax it, since
  `RH-015` established that `A2`, `A3` AND `A4` are all FALSE at `R < 0`;
- an independent adversarial review of the draft before it is offered for
  promotion;
- no ledger row, no barrier row change, no route selected, and no claim about
  the truth of the Riemann Hypothesis.

Note on where this lands if it is ever promoted: the package is generic — it
quantifies over an arbitrary meromorphic `f` and mentions no ζ or ξ — so its
built home would be the domain-neutral `ResearchOS/Analysis/` shelf under its
own ledger prefix, not the RH subtree. That placement decision belongs to the
promotion change, not to this one.

## RH-017: promote the argument-principle package to the built surface

ID: `RH-017`

Status: **COMPLETE 2026-08-09 — kernel-checked through merged PR #329; five
declarations accepted, no barrier row moved**

Kind: theorem

Activation basis (2026-08-09): `RH-016` completed — the draft exists, its five
signatures are character-identical to the corrected contract, and two
independent lenses reviewed it. Under the two-stage gate the kernel verdict
comes only from a separate promotion change, and this is that change.

Exit criteria:

- the built module, its `AP-*` ledger rows, the regenerated registries and
  axiom audit, and the promotion record all land in ONE change, or inverse
  coverage fails CI;
- the full battery passes on the EXACT merged head: `lake build`, the
  no-incomplete-proof gate, inverse ledger coverage, and both axiom audits;
- a statement change at any point stops the task and returns the surface to
  contract review — a proof-only repair does not;
- the drafts-lane mirror stays byte-identical to the built module from the
  first `import`;
- on green merge this closes no barrier and changes no barrier row. In
  particular `S1-GLOBAL-ZEROS` stays OPEN: `A2` sums the divisor of an
  ARBITRARY `f` over an arbitrary open disc, names no ζ or ξ, and chooses no
  truncation family, so it does not touch that row's exit items.

Expectation recorded in advance, so that a rejection is read as a round and not
as a surprise: the drafter named `A2` — roughly 330 lines with several
higher-order unification points — as the declaration most likely to be rejected,
and wrote its inline fallbacks most densely for that reason.

Outcome (2026-08-09), against those criteria one by one. Everything landed in
one change and inverse coverage holds. The battery was re-run on the EXACT
merged head `16027ed` — fourteen gates, both registry `--check` passes, the CI
no-`sorry` grep verbatim — all green, with the generators at a fixpoint so no
artifact is stale. No statement moved at any point: the five signature digests
are identical across all three rounds, so every repair was proof-only and the
surface never returned to contract review. The drafts mirror is byte-identical
from the first `import`. No barrier row changed.

The prediction held exactly: **every error in all three rounds was in `A2`, and
the other four declarations drew none.** What the prediction did not cover is
that round 1's own post-mortem was wrong. It read a free scalar-field
metavariable as the cause of a transposed goal and repaired both with one
`show`; round 2 showed the two are independent, because the transposition is
assigned by first-order approximation while the SECOND argument elaborates,
before the postponed tactic block is entered. The lesson worth keeping is not
about `zpow`: a diagnosis written from a single failing round is itself a
hypothesis, and this one survived only until the next round tested it.

## RH-018: apply the re-verification corrections to the Weierstrass contract

ID: `RH-018`

Status: **COMPLETE 2026-08-09 — merged PRs #330 and #333; 28/28
signatures byte-identical, no barrier row moved**

Kind: contract repair

Activation basis (2026-08-09): `RH-017` completed through merged PR #329, so the
queue's single ACTIVE slot is free. It moves here rather than to the Weierstrass
drafting that the 2026-08-08 acceptance unlocked, because
`notes/reviews/WEIERSTRASS_FINDINGS_VERIFICATION_2026_08_09.md` established that
**three of the thirteen pin-fidelity findings state a false mechanism, and their
reasoning is already copied into the contract** — at exactly the three sites the
findings existed to protect. The same re-verification found that the applied
`W6` fix does not close, so the contract currently ships a skeleton that cannot
work. That alone forces this task ahead of drafting.

Exit criteria:

- the 28 public signatures are byte-identical before and after, verified by
  digest. This task may not move the statement surface; a signature change stops
  it and returns the surface to contract review;
- the three refuted mechanisms are rewritten to say what actually happens, not
  merely softened:
  - `W6` — both sides are `HMul` at arity 6, the shape gate passes, and
    `mul_le_mul` splits the goal into `2 ≤ 4/(p+1)`, false for every `p ≥ 2`,
    with both side conditions discharged. The hazard is a silent wrong answer,
    not a refusal;
  - `W8` — the normalization stays mandatory and its justification strengthens
    (the `@[gcongr]` attribute rejects differing-head lemmas at declaration
    time, so no bridge can ever exist), but the symptom is "unsolved goals", and
    the `rw [← div_pow]` alternative must be struck: it swaps one mismatch for
    another;
  - `W5` / `S1W-LOG` — the `▸` misfire does not exist; `elabSubst` is forced by
    `tryPostponeIfHasMVars?` into the branch that rewrites the hypothesis
    forward and yields the wanted type. The `▸`-free skeleton stays; the
    obligation's severity is re-priced;
- the `W6` `calc` gains the pre-combined `have` it needs, or a fourth line;
- both `W8` routes gain the `‖x‖ ≤ R` step they bottom out at and that the
  skeleton never derives from `K ⊆ closedBall 0 R`;
- every `ℂ_ℤ` occurrence is marked unwritable outside its defining file
  (`local notation`, Cotangent.lean:34) — five sites, two of them inside anchors
  a lens certified as clean;
- the `WeierstrassCurve` occurrence count at contract line 161 is corrected or
  removed;
- the acceptance record's self-contradiction on finding 12(ii) is resolved in
  the lens body, not only in the disposition section;
- `§1.2` records that `hane + hsum` are CONTRADICTORY over an uncountable index
  (so those signatures are vacuous there, not merely countably indexed), that
  the `hane` map needs three different witnesses, and that "provably redundant"
  in `W8`–`W10` is a truth claim whose proof route does not survive the
  deletion;
- the upstream duplication check is recorded honestly: no relevantly named new
  module was found, the nine declared names have zero hits in the eight
  dependency files at current master, and seven of those eight files have moved.
  This is scoped evidence, not a whole-tree semantic duplication audit; the
  in-flight PR queue was unreachable from the session, so the gap
  `UPSTREAM_POOL_V2` names is HALF closed and must be described that way;
- no barrier row changes. This is documentation; it proves nothing.

Recorded in advance: the temptation here is to soften a wrong explanation into a
vague one. A vague explanation is worse, because a wrong one can be refuted.
Each rewrite must name the mechanism that actually fires and the file and line
that decides it.

Outcome (2026-08-09): every exit item was completed across PR #330 and its
corrective follow-up #333. The 28 signatures stayed byte-identical at digest
`4149484c52db2c30972ba1455e791706724fd740e8f5dc97886947ad26f93d38`.
The three refuted mechanisms, the W6/W8 skeleton gaps, the inaccessible local
notation, the occurrence count, and the acceptance-record contradiction were
repaired. The final adversarial pass also replaced the false single-witness
summary with the three required zero-fiber cases, distinguished W12's local
finite-fiber cardinality from global zero counting, and narrowed the upstream
duplication note to the search it actually performed. No Lean source, public
statement, ledger entry, or barrier row changed.

## RH-019: transcribe the Weierstrass package into the drafts lane

ID: `RH-019`

Status: **COMPLETE 2026-08-09 — 28/28 exact declarations, two static lenses,
no kernel verdict**

Kind: draft

Activation basis (2026-08-09): `RH-018` completed through merged PRs #330 and
#333. The accepted contract is therefore safe to transcribe, but not yet safe
to promote. This task creates only
`domains/riemann-hypothesis/drafts/WeierstrassFactors.lean` and its review
record; a built module belongs to a separate later task.

Exit criteria:

- exactly 28 public declarations W1–W12, with every signature
  character-identical to the accepted contract and the statement digest
  checked explicitly; adding the deliberately omitted 29th `_fun_` declaration
  or changing a binder, hypothesis, or conclusion stops the task and returns
  it to contract review;
- complete proof-shaped bodies with no `sorry`, `admit`, custom `axiom`,
  `unsafe`, or hidden fallback assumption, while the file remains outside all
  Lake targets and is not imported by `ResearchOS.lean`;
- two independent static review lenses cover statement identity, pinned API
  plausibility, mathematics, and dependency order. Green repository CI on this
  non-built draft is explicitly not a Lean kernel verdict;
- the claim boundary remains generic fixed-finite-genus elementary factors and
  canonical products over arbitrary `p` and `a`. W12's `Nat.card` is only a
  finite-fiber local multiplicity. The task claims no ζ/ξ zero enumeration,
  global zero count, growth theorem, genus selection, Hadamard existence,
  route selection, barrier closure, or progress on RH;
- `S1-GLOBAL-ZEROS` and `S1-GROWTH` remain OPEN, every RH route remains PARKED,
  and no barrier row moves.

Recorded in advance: W12 carries the sole HIGH obligation (`S1W-ORD`), W8 has
the longest locally-uniform convergence argument, and W4's cast bridge is the
likeliest cheap elaboration failure. These are review priorities, not excuses
to weaken a statement.

Outcome (2026-08-09): the draft landed in the task change as a 28-declaration,
non-built transcription with complete proof-shaped bodies and no `sorry`,
`admit`, custom `axiom`, `unsafe`, or hidden fallback assumption. The statement
lens found 28/28 character-exact matches, no extra 29th `_fun_` declaration,
and a reproducible normalized-surface hash
`5c1bbe331f63ae63bb31c88d80e2af6442562091a1996f799e132d254d62d735`.
The historical `414948…` digest has no preserved serialization algorithm and is
not claimed reproduced by this task. The mathematics/API lens reviewed every
body at exact final file SHA-256
`fe34390369b02dc0eea9f318ba60f971ff1fc6e170634ecdacbda9823160a810`:
zero soundness blockers and zero required patches. W12 reaches `Nat.card` only
after proving the one fiber finite, so it remains a local multiplicity. The
file is outside all Lake targets; CI on this change is not a Lean verdict.
`S1-GLOBAL-ZEROS` and `S1-GROWTH` remain OPEN, all routes remain PARKED, and no
barrier row moved.

## RH-020: promote the Weierstrass package to the analysis shelf

ID: `RH-020`

Status: **ACTIVE 2026-08-09 — separate built promotion; exact-head kernel CI
is the sole judge**

Kind: theorem promotion

Activation basis (2026-08-09): `RH-019` completed the accepted non-built draft
and two independent static reviews. This task asks the kernel about that exact
surface. It does not authorize a statement change, a proof route, or any
zeta-specific specialization.

Exit criteria:

- one promotion change adds
  `ResearchOS/Analysis/WeierstrassFactors.lean`, imports it from
  `ResearchOS.lean`, registers a new `WF-` prefix in the existing
  `analysis-generic` lane, adds one ledger row for each of the 28 public
  declarations, regenerates both registry/audit surfaces, and records the
  promotion review; inverse coverage must be complete in the same tree;
- the built module and the reviewed draft remain character-identical from the
  first `import` through the final declaration except for an explicitly
  reviewed header. The declaration count stays 28 and the deliberately omitted
  `analyticOrderAt_fun_finsetProd` is not introduced;
- every statement remains character-identical to the accepted W1–W12 contract.
  A changed binder, hypothesis, conclusion, name, or domain stops promotion and
  returns the surface to contract review. A proof-only kernel repair must be
  synchronized back into the draft and re-reviewed on its exact hash;
- the exact PR head passes isolated elaboration of the new module, full
  `lake build`, no-incomplete-proof and lane-isolation gates, inverse ledger
  coverage, and both axiom audits with no `sorryAx`, custom axiom, or unreviewed
  trust extension;
- the package stays on the domain-neutral `ResearchOS/Analysis/` shelf. It
  remains generic fixed-finite-genus analysis: no ζ/ξ zero enumeration, global
  zero count, growth theorem, genus selection, Hadamard existence, route
  selection, barrier closure, or progress on RH;
- `S1-GLOBAL-ZEROS` and `S1-GROWTH` remain OPEN, every RH route remains PARKED,
  and no barrier row moves.

Recorded in advance: the most likely first kernel failures are W4's reindex and
cast normal form, W8's locally uniform product inference, and W12's
Pi/subtype/cardinality coercions. Kernel rejection is a proof-repair round, not
permission to weaken the accepted statement.

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
