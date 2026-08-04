# Riemann Hypothesis research track

Status: **exploratory, active Stage 0**

Priority date: 2026-08-04

Owning queue: `tasks/RIEMANN_HYPOTHESIS.md`

## Exact objective

Work toward either a proof or a disproof of the classical Riemann Hypothesis.
The canonical formal target is the pinned Mathlib declaration
`_root_.RiemannHypothesis`. In human terms, every nontrivial zero of the
analytically continued Riemann zeta function must have real part `1/2`.

The repository currently claims no proof candidate, no new equivalence, and no
progress on the conjecture itself.

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
  audit cover it. The current activation PR contains no new Lean declaration.
- This domain keeps `metrics_source: null` until an independently honest metric
  and ledger contract exists.

## Repository split threshold

Keep Stage 0 in this repository because it reuses the existing ResearchOS
control plane and pinned verifier. Create a separate RH repository only after a
selected route needs its own dependency graph, proof ledger, or CI surface.
That decision must preserve links back to this source corpus and the dated route
review.
