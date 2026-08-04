# Riemann Hypothesis research queue

This file owns the active KeyAI queue for the Riemann Hypothesis. The domain
boundary is `domains/riemann-hypothesis/README.md`; the canonical target and
source map live in `domains/riemann-hypothesis/corpus.md`.

The lane is **active exploratory research**, not a claimed proof program with a
known path to completion. Existing ECDLP state remains authoritative in its own
decision substrate and queue. New discretionary mathematical work defaults to
this queue during the RH activation cycle.

## Current decision

Execute `RH-001` first. Do not begin a proof attempt, large computation, new
equivalence formalization, or autonomous hypothesis sweep before `RH-001` has
produced a pinned dependency map and `RH-002` has completed adversarial route
triage.

The exact Lean target is the already-pinned Mathlib declaration
`_root_.RiemannHypothesis`. Do not create a competing definition.

## RH-001: pinned formal capability and barrier map

ID: `RH-001`

Status: **ACTIVE**

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

Status: **BLOCKED on RH-001**

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

Status: **BLOCKED on RH-002 SELECT**

Kind: theorem / review

Hypothesis: The selected route contains one missing lemma whose proof or failure
would change the route decision.

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
  theorem is counted;
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
