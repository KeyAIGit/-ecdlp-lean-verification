# Riemann Hypothesis research track

Status: **exploratory; Stage 0 evidence package assembled. RH-001, RH-002,
RH-003, RH-004, RH-006, RH-007, and RH-008 are closed; the RH-002 independent
disposition review completed 2026-08-07 with all three retained `PARK`
dispositions CONFIRMED
(`notes/reviews/RH002_DISPOSITION_REVIEW_2026_08_07.md`). RH-009 —
acceptance-only review of the multiplicity/divisor statement surface, no built
module and no kernel verdict — is the sole ACTIVE task; RH-010 is BLOCKED on
it. No route is selected and no route execution is authorized.**

Priority date: 2026-08-04

Owning queue: `tasks/RIEMANN_HYPOTHESIS.md`

## Exact objective

Work toward either a proof or a disproof of the classical Riemann Hypothesis.
The canonical formal target is the pinned Mathlib declaration
`_root_.RiemannHypothesis`. In human terms, every nontrivial zero of the
analytically continued Riemann zeta function must have real part `1/2`.

The repository currently claims no proof candidate and no progress on the
conjecture itself. The built target reformulations, the kernel-checked xi
equivalence package, and the kernel-checked conjugation-symmetry package are
foundation interfaces only.

## Current stage

Stage 0 is a foundation and specification audit:

1. Freeze the exact target, normalization, pole handling, and zero terminology.
2. Audit pinned Mathlib v4.31.0 at commit
   `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.
3. Record present, missing, and uncertain foundations by exact module and
   declaration name.
4. Bind each mathematical claim to a primary source and exact locator.
5. Adversarially compare the admitted routes.
6. Select at most one meaningful kernel-checkable intermediate result, or
   retain a precise blocker if no candidate survives.

The detailed source, claim, route, and evidence map is in `corpus.md`.

Stage 0 execution state (updated 2026-08-07): items 1-3 are complete — the exact
target is frozen and the pinned audit has been independently replayed with
0 mismatches (`notes/reviews/RH001_INDEPENDENT_REPLAY_2026_08_05.md`). The
source contracts are accepted after a 59-row replay: 57 rows were confirmed
and 2 were amended, leaving 0 open source discrepancies (`RH-006`).
The admitted routes were adversarially compared (`ROUTE_TRIAGE.md`:
`PARK`/`PARK`/`PARK`, no route selected); the independent disposition review
completed 2026-08-07 and **CONFIRMED** all three `PARK` dispositions
(`notes/reviews/RH002_DISPOSITION_REVIEW_2026_08_07.md`), with second-agent
replay of the load-bearing `[D]` desk-citation locators remaining an
outstanding finality gate tracked in `ROUTE_TRIAGE.md`. The full Route A and
Route B success bars would imply RH;
for Route C, no known published mechanism meets the all-heights
individual-zero-exclusion bar, and meeting that full bar would imply RH.
Item 6 resolved to the foundation path: the route-neutral target bridge from
`TARGET_BRIDGE_CONTRACT.md` is kernel-checked in the repo-local
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/TargetBridge.lean` module
(PR #299, `288d65b`), closing `S1-TARGET` without making any claim about the
truth of RH. `S0-TRUST` was closed by PR #298 (`d6e146fa`). The
source-contract prerequisite is now satisfied; independent acceptance of the
xi contract is also complete
(`notes/reviews/RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`). The accepted
surface was promoted in PR #304 (`afdae08`) as twelve built declarations with
ledger, registry, full-build, and axiom-audit coverage, closing `S1-XI`.
X11 discharges only local analytic-order transport; `S1-MULTIPLICITY` remains
open because no built divisor or complete multiplicity-preserving symmetry
package exists (a non-built statement surface is under acceptance-only review
as `RH-009`, with no kernel verdict). The conjugation package was promoted in
PR #307 (`c277b86`) as sixteen built declarations with ledger, registry,
full-build, and axiom-audit coverage; it supplies the conjugation leg and
pointwise order transport only, so `S1-CONJ` remains open on divisor
invariance under `ρ ↦ 1 − conj ρ`. The remaining foundation packages stay
explicit preconditions, and no claim about RH's truth changes.

## Evidence boundary

- Finite zero checks, finite coefficient checks, numerical experiments, and
  model-generated arguments are evidence inputs only. None proves the universal
  statement.
- An equivalent criterion becomes an active route only after its full
  hypotheses and equivalence obligation are recorded.
- A Lean theorem counts as verified only after it builds with no `sorry`,
  `admit`, custom axiom, or unreviewed trust extension, and after independent
  review confirms that the formal statement matches the cited mathematics.
- A conditional implication does not count as progress when its premise merely
  hides RH or an equivalent difficulty.

## Repository isolation

- Existing ECDLP results, negative findings, authorizations, and history remain
  unchanged.
- `repo/ECDLP_*` and the ECDLP Research Engine neither authorize nor score RH
  work.
- RH claims and tasks use the `RH-` identifier prefix.
- Future theorem-bearing RH modules belong under
  `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`.
- No RH theorem is added to the built surface until a domain ledger and axiom
  audit cover it. PR #299 satisfies that rule for the target bridge, PR #304
  for the twelve-declaration xi package, and PR #307 for the
  sixteen-declaration conjugation package.
- This domain keeps `metrics_source: null` until an independently honest metric
  and ledger contract exists.

## Repository split threshold

Keep Stage 0 in this repository because it reuses the existing ResearchOS
control plane and pinned verifier. Create a separate RH repository only after a
selected route needs its own dependency graph, proof ledger, or CI surface.
That decision must preserve links back to this source corpus and the dated route
review.
