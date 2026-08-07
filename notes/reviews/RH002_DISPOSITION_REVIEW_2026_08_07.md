# RH-002 — independent disposition review and closure record, 2026-08-07

**All three `PARK` dispositions stand.** Route A `PARK`, Route B `PARK`, and
Route C `PARK` are each **CONFIRMED** as recorded in
`domains/riemann-hypothesis/ROUTE_TRIAGE.md`. No `PARK` becomes `SELECT`, no
disposition is upgraded silently or otherwise, and no claim about the truth
of the Riemann Hypothesis is made or implied by this review or its closure.

This record completes the sole remaining `RH-002` exit item: independent
review of the three recorded dispositions, their source anchors, and revival
bars. Per that exit item's own scope, the review may confirm or amend a
disposition but **does not itself authorize theorem construction,
computation, or route execution** — and it authorizes none.

## Reviewers and independence

Three independent per-route review agents, one per route family, each
working in isolation from the others and from the original triage author:

| reviewer | scope | verdict |
|---|---|---|
| Route A reviewer | Weil-first Li positivity (`ROUTE_TRIAGE.md` Route A section; `SC-LI-*`, `SC-WEIL-*`, `SC-BRIDGE-*`, `SC-BOMB-*` anchors) | **CONFIRM** |
| Route B reviewer | Nyman-Beurling/Báez-Duarte closure (Route B section; `SC-NB-01..06` anchors; 20% pilot cap) | **CONFIRM** |
| Route C reviewer | explicit formula + global inequality (Route C section; `SC-BOMB-*`, `SC-BRIDGE-*` anchors; dependency screen) | **CONFIRM** |

No reviewer edited a repository file; this closure change is applied by a
single separate writer from the three written verdicts.

## Method

- **Environment:** repository working tree at the closure round's HEAD;
  pinned Mathlib checkout `/workspace/leanprover-community/mathlib4` at
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, verified by `git rev-parse` in
  each review and again by the closing writer. No Lean toolchain: source
  reading only; no kernel verdict is claimed or produced anywhere in this
  round.
- **Checks per route:** (1) the disposition follows from the recorded
  evidence; (2) every cited source anchor resolves — `SC-*` row IDs against
  `SOURCE_CONTRACTS.md`, normative locators against the pinned-source table,
  quotes against the `RH-006` replay and acceptance records, and Mathlib
  `file:line` locators against the pinned checkout; (3) the revival bar is
  precise, testable by a future reader, and genuinely decision-changing;
  (4) triggers claiming cost-only status are cost-only, and no trigger
  auto-`SELECT`s; (5) the defects recorded in
  `notes/reviews/RH_LANE_CLAIMS_AUDIT_2026_08_07.md` that fall in the route's
  scope are addressed as dated amendments.
- **Inputs:** `domains/riemann-hypothesis/ROUTE_TRIAGE.md`,
  `SOURCE_CONTRACTS.md`, `MATHLIB_CAPABILITY_MAP.md`, `corpus.md`;
  `notes/reviews/RH006_SOURCE_REPLAY_2026_08_06.md`,
  `RH006_SOURCE_CONTRACT_ACCEPTANCE_2026_08_06.md`,
  `RH_SOURCE_PDF_CHECKSUM_REPLAY_2026_08_05.md`,
  `CAPABILITY_MAP_REVERIFICATION_2026_08_07.md`,
  `RH_LANE_CLAIMS_AUDIT_2026_08_07.md`; the pinned Mathlib tree.

## Per-route verdicts

### Route A — Weil-first Li positivity: CONFIRM

`PARK` (PARKED-DIRECT / ALIVE-AS-FORMALIZATION-LANE) stands. The survey
shows every cited result is an equivalence, identity, conditional
asymptotic, or bounded numeric; the day-45 bar is met by nothing published
and is itself RH-equivalent via the Bombieri-Lagarias abstract criterion
plus the Voros dichotomy, so the direct screen is guaranteed a
death-condition outcome. `PARK`-not-`STOP` is justified: nothing refutes
the framework, and the dependency chain is the shared infrastructure Route
C's dependency screen also needs. All cited `SC-*` rows resolve; the
`SC-WEIL-01` amended involution attribution is exactly consistent across
contract, acceptance record, and replay. Findings requiring amendment:
audit D2 (RH-SRC pinning overstated), D5 (admission count), D23
(death-condition count), plus three precision items — the missing
never-auto-`SELECT` clause on the Route A trigger preamble, an `A-T2`
coverage gap (full-tail `Re λ_n ≥ 0` with no growing margin already forces
RH by the recorded Voros dichotomy yet met no trigger as worded), and a
"Gate 0" attribution pointing at the wrong document. All applied; none
changes the disposition.

### Route B — Nyman-Beurling/Báez-Duarte: CONFIRM

`PARK` as route-to-RH stands; foundation objects clean; **0% of the 20%
pilot execution cap spent, and the cap is untouched by this round.** The
bar (unconditional `B(N) → 0` for a natural-span family) is RH-strength via
the unconditional closure→RH direction of `BD02-v2` Thm 1.1 through the
classical Nyman-Beurling edge, with RH-dependence confined exactly as
`SC-NB-05` ledgers it. The three pre-execution death conditions match the
capability-map admission row verbatim. Burnol only pre-falsifies rates
faster than `1/log N`, not the family concept, so `PARK`-not-`STOP` is
right. The `RH-006` `dt` correction is consistent across all three records.
Pinned-Mathlib anchors re-verified at the pin (`LSeries_eq_mul_integral`
at `SumCoeff.lean:137`; `fourierTransformₗᵢ` at
`Analysis/Fourier/LpSpace.lean:50`; `norm_fourier_eq` at `:89`;
`measurable_fract` at `MeasureTheory/Function/Floor.lean:45`). Findings
requiring amendment: audit D6 (phantom `LSeries_eq_tsum` name — zero hits
tree-wide, independently re-confirmed), D7 (stale ordering clause inverted
into an apparent authorization), plus the missing never-auto-`SELECT`
clause on `B-T1`. All applied; none changes the disposition, cap, bar, or
trigger substance.

### Route C — explicit formula + global inequality: CONFIRM

`PARK` as a direct route stands; `REQUIRED DEPENDENCY SCREEN` for Route A
retained, budget charged to Route A. The death condition "family still
unnamed" holds in the repository and the literature, independently
re-confirmed at the pin (`CAPABILITY_MAP_REVERIFICATION_2026_08_07.md`:
no Riemann-Weil explicit formula, no Perron, tree-wide). All cited
`SC-BOMB-*`/`SC-BRIDGE-*` rows resolve and are among the 57 `RH-006`
CONFIRMED rows; neither `RH-006` amendment touches a Route-C-cited row.
`Complex.borelCaratheodory` verified present at the pin. The
preregistration block is fully testable, and the record honestly states
that full-bar satisfaction would imply RH while the literature gap is not
an impossibility proof. Findings requiring amendment: audit D1 (indicative
nonexistence of a vertical-strip zero-free region — entails ¬RH as
written and contradicted the same document's outcome item 1; replaced by
the supported non-knowledge statement) and D3 (uncompared domination by
the `RH-SRC-007` verified range). The Route C confirmation was conditional
on applying D1/D3/D4; all are applied, so the CONFIRM is unconditional in
this record. Both rewordings strengthen the `PARK` rationale: `PARK` needs
only non-knowledge, never nonexistence.

## Amendments applied by this closure

In `domains/riemann-hypothesis/ROUTE_TRIAGE.md` (in-place fixes to
non-frozen survey/policy prose, each enumerated in the document's dated
section "Independent disposition review 2026-08-07 (`RH-002` closure)";
no frozen decision text rewritten):

1. D2 — citation policy: checksum/locator pinning restricted to `LAG07`,
   `BOM-CLAY`, `BD02-v2`; `RH-SRC-00x` citations are `[D]`-class.
2. D5 — admission sentence: two admitted, third carried at its pre-cycle
   `PARK`, three screened.
3. D23 — Route A death-condition count "4 of 6" → "5 of 6".
4. Route A trigger preamble: explicit "each reopens desk review only, never
   auto-`SELECT`".
5. `A-T2` broadened (preregistered trigger change, recorded as such): adds
   full-tail `Re λ_n ≥ 0` with no growing margin, at full RH-proof
   severity; the execution bar is unchanged.
6. "Gate 0" attribution corrected to the `SOURCE_CONTRACTS.md`
   shared-notation section realizing the capability map's Gate 0.
7. D1 — Route C zero-free-region clause restated as non-knowledge, never
   nonexistence. Graded S1 on the record, per the concurring Route B and
   Route C recommendations, with the S0 boundary considered explicitly.
8. D3 — Connes-Consani clause restated without the uncompared domination
   claim.
9. D6 — phantom `LSeries_eq_tsum...` removed.
10. D7 — Route B foundation items stated as unscheduled and unauthorized;
    20% cap explicitly re-bound at 0% spent.
11. `B-T1` header: explicit "reopens desk review only, never auto-`SELECT`".
12. Status line updated to record the completed review and the remaining
    `[D]`-replay finality gate.

In `domains/riemann-hypothesis/SOURCE_CONTRACTS.md` (accepted under
`RH-006`; applied per the existing `SC-NB-04` amendment precedent — in-place
rewording of the non-frozen shared-notation sentence plus a dated amendment
note adjacent to the acceptance record, plus a status-line note):

13. D4 — "A Lean `Multiset` cannot represent the infinite divisor" replaced
    by the supported statement: only local finiteness is available at the
    pin (`isClosed_riemannZetaZeros`, `isDiscrete_riemannZetaZeros`,
    `IsCompact.inter_riemannZetaZeros_finite` —
    `Mathlib/NumberTheory/LSeries/ZetaZeros.lean:57,60,64`, all three
    re-verified at the pinned checkout in this round); infinitude of `S_xi`
    is not asserted, not proved in pinned Mathlib, and not needed by any
    row of the package. This closes the recurrence of the previously
    withdrawn infinitude claim. The `RH-006` acceptance and its two applied
    amendments are unaffected; no quoted source semantics change.

No reviewer required any `SC-*` row fix; all row-level anchors were
confirmed.

## What this review does NOT authorize

- **No route execution.** All three routes remain `PARK`ed; Route B's 20%
  pilot cap remains 0% spent; no `SC-NB` or Route-C-specific Lean work is
  scheduled or authorized.
- **No computation.** No numeric sweep, no bounded verification run, no
  model sweep.
- **No theorem construction.** This round produces no Lean statement, no
  contract, and no kernel verdict; the successor task `RH-009` is
  acceptance-only review of an already-merged non-built statement surface
  and is activated by the queue decision, not by this review.
- **No claim of progress on the truth of RH**, in either direction.
- Reconsideration triggers reopen desk review only; none auto-`SELECT`s.

## Remaining finality gate (outside RH-002's queue slot)

Second-agent replay of the exact locators of every load-bearing `[D]` desk
citation — above all Voros 2004/2006 (carrying the "meeting the bar would
itself prove RH" claim and the broadened `A-T2`), Burnol (the Route B
revival-bar window constant and the `o(1/log N)` automatic-STOP clause),
and secondarily Vasyunin and Bettin-Conrey. This gate is recorded in
`ROUTE_TRIAGE.md` (outcome item 4 and the dated review section) and is
unchanged by this closure. The pinned `LAG07`/`BOM-CLAY`/`BD02-v2` anchors
alone already support all three `PARK`s, which is why the dispositions can
be confirmed while this gate remains open.

## Queue effect

`RH-002` is set **COMPLETE 2026-08-07** with this record as closure
evidence. By the same dated decision, `RH-009` (independent acceptance of
the multiplicity/divisor statement surface, acceptance-only) becomes the
queue's sole ACTIVE task, and `RH-010` (kernel promotion) is installed
BLOCKED on `RH-009`, both per
`domains/riemann-hypothesis/MULTIPLICITY_QUEUE_ENTRY_PROPOSAL.md`. The
exactly-one-ACTIVE-task invariant holds before and after this closure.
