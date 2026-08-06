# Riemann Hypothesis research queue

This file owns the active KeyAI queue for the Riemann Hypothesis. The domain
boundary is `domains/riemann-hypothesis/README.md`; the canonical target and
source map live in `domains/riemann-hypothesis/corpus.md`.

The lane is **active exploratory research**, not a claimed proof program with a
known path to completion. Existing ECDLP state remains authoritative in its own
decision substrate and queue. New discretionary mathematical work defaults to
this queue during the RH activation cycle.

## Current decision

Decision date: 2026-08-05. `RH-001` is complete (independent replay recorded).
`RH-002` is executed: all three admitted route families are `PARK`ed with
preregistered revival bars and reconsideration triggers, **no theorem-bearing
route is selected**, and the dispositions await independent review
(`domains/riemann-hypothesis/ROUTE_TRIAGE.md`). `RH-003` is now the sole
active contract: the frozen route-neutral target-bridge theorem contract
(`domains/riemann-hypothesis/TARGET_BRIDGE_CONTRACT.md`) awaits independent
review. Do not begin a proof attempt, large computation, new equivalence
formalization, or autonomous hypothesis sweep. Update 2026-08-06: `S0-TRUST`
is CLOSED (PR #298 merged to `main`; dated addendum in
`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md`). No built RH Lean
until `RH-003` review passes; the promoted module must carry its `RH-*`
ledger row, registry entry, and audit line in the same PR.

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
`SOURCE_CONTRACTS.md` remains "proposed under independent review".

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

Outcome record: `domains/riemann-hypothesis/ROUTE_TRIAGE.md`. Each admitted
family's preregistered day-45 bar is provably unreachable short of RH itself
(Weil-first Li via the Bombieri-Lagarias/Voros oscillation dichotomy;
Nyman-Beurling via the unconditional closure→RH direction; explicit-formula
via the absence of any individual-zero-exclusion mechanism in the
literature). Zero theorem-bearing routes selected ("at most one" is
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

Status: **ACTIVE**

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
Annex A xi work. The `S0-TRUST` precondition is satisfied as of 2026-08-06
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

Status: **BLOCKED on RH-003 review**

Kind: theorem

Hypothesis: The reviewed theorem contract can be represented in Lean without
weakening the statement or expanding the trusted base.

Expected output:

- one scoped built module under the non-ECDLP `ResearchOS` lane;
- a domain-specific result record and axiom-audit coverage designed before the
  theorem is counted; a proposed design now exists
  (`domains/riemann-hypothesis/S0_TRUST_DESIGN.md`, v2, adversarially
  reviewed `SOUND_WITH_FIXES`) — its implementation requires a separate
  ops-lane task/PR and is not authorized by the RH lane;
- CI-green proof with exact trust and claim scope.

Exit criteria:

- `lake build` passes;
- no-sorry and axiom audits cover the declaration;
- independent review confirms the Lean statement matches the paper statement;
- the result changes a named route decision or blocker.

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
