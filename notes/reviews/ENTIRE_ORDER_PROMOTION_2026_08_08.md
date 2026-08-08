# Growth-order definitional package promotion record (ENTIRE_ORDER)

Date: 2026-08-08

Scope: promotion of the independently accepted G0-G2 + L1-L6 statement surface
of `domains/riemann-hypothesis/ENTIRE_ORDER_CONTRACT.md` into the built module
`ResearchOS/Analysis/GrowthOrder.lean`. This record is cited by the nine `GO-*`
rows in `VERIFIED_RESEARCHOS.md`.

## The thing to read first

This is the package most likely to be misread, so the boundary goes at the top
rather than at the bottom. What is promoted is a **definition** of growth order
for an arbitrary function, plus six facts about that definition evaluated on
constants, polynomials and `exp`. `S1-GROWTH`
(`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:388`) asks for a
**zeta/xi vertical or order-one growth theorem**. A definition supplies zero
quantitative bounds, and none of L1-L6 mentions ζ or ξ. `S1-GROWTH` is
therefore **OPEN and untouched** by this change: not closed, not advanced, not
partially closed. Having the vocabulary lowers the cost of a future exit; that
is inventory, and inventory never retires a barrier row.

## Review basis

1. **Independent statement acceptance.** The nine-signature surface was
   accepted 2026-08-07 under owner-delegated review authority — "accepted at
   stage one as offered, with applied editorial fixes and zero signature
   changes", the definition explicitly **not** returned to design. Record:
   `notes/reviews/ENTIRE_ORDER_ACCEPTANCE_2026_08_07.md`. Per the contract's
   death condition 1, that record is what unlocked the drafts-lane
   transcription, and nothing downstream of it.
2. **No prerequisites.** The package imports pinned Mathlib only. Nothing in
   the repository has to be merged first, and nothing depends on it today.
3. **Draft review provenance.** The promoted body is the drafts-lane file
   reviewed 2026-08-07: all nine blocks character-identical including
   docstrings, both HIGH obligations (L2, order of a polynomial; L5, order of a
   product) assembled in full from pinned ingredients rather than split,
   verdict `LIKELY_ELABORATES` with one comment-only fix.
4. **Statement identity re-verified at promotion time.** All nine signatures
   re-compared mechanically against the contract's canonical blocks immediately
   before this promotion, byte-exact with whitespace not normalised. Nine of
   nine identical.
5. **Name-collision scan.** These nine declarations live in `namespace Complex`,
   so their real names are `Complex.maxModulus`, `Complex.growthOrder`,
   `Complex.growthType`, and the six `Complex.growthOrder_*` / `Complex.growthType_*`
   lemmas. All nine qualified names were checked against the pinned Mathlib tree
   and against every declaration already built in `ResearchOS/`: no collision.
   The ledger rows carry the qualified names, not the bare ones.
6. **Kernel check.** The verdict is delivered by CI on this promotion change:
   `lake build` compiles the module, the no-incomplete-proof gate scans it, the
   regenerated `ResearchOS/LedgerAxiomAudit.lean` + `check_axioms.py` enforce
   the per-row `standard` axiom base, and `gen_researchos_registry.py --check`
   enforces inverse coverage. If any gate is red, no row is counted.

## Load-bearing checks

- **A definition is a design commitment.** G1 fixes the junk conventions — both
  `def`s totalized, the clamps kept symmetric between G1 and G2 — and every
  downstream statement inherits them. That is precisely why this surface took
  an independent acceptance of its own before any Lean was written, and why
  L1, L3 and L6 exist: they are the smoke tests that the chosen convention
  returns the classical value on the three cases where the answer is known in
  advance (constant → 0, `exp` → 1, type of `exp` at exponent one → 1).
- **No statement-level slack.** L2 is `= 0`, not `≤ ε` and not a `natDegree`
  restatement. L5 is `≤ max`, with no `+ ε`; an L5 carrying statement-level ε
  slack was a pre-labelled FAILED design gate in the contract, and the ε that
  appears inside its proof is proof-internal and never reaches the statement.
- **L5 is an inequality, not an equality.** The order of a product is bounded
  by the max of the two orders. Equality is false in general and is not
  claimed.
- **G2 is only ever evaluated inside its gate.** `growthType` is defined under
  a finite-positive-order gate; no statement in the package evaluates it
  outside that documented gate.
- **L4 is unconditional as stated.** Monotonicity under an eventual pointwise
  bound holds without side conditions, the degenerate cases being carried by
  the totalization clamps rather than excluded by hypothesis.

## Draft synchronization

The built module and the drafts-lane copy
(`domains/riemann-hypothesis/drafts/RiemannGrowthOrder.lean`) are byte-identical
from the first `import` through end of file; they differ only in their leading
status header. Any proof-only kernel repair must be applied to both copies
before a new CI run; a statement change stops promotion and returns to contract
review.

## Claim boundary

Once and only once the exact merged head passes the full build, the
no-incomplete-proof gate, inverse ledger coverage, and both axiom audits: what
exists is three definitions and six calibration lemmas about an arbitrary
`f : ℂ → E`. This package **closes no barrier, advances no barrier, and
partially closes no barrier**; `S1-GROWTH` stays OPEN for the reasons stated at
the top of this record, and the capability map is not edited by this change.
The effect is **inventory only**.

No route is selected, opened, or advanced. This promotion provides **no
evidence for or against the Riemann Hypothesis**, and makes no claim of
progress on it in either direction. The RH queue is untouched: `RH-012` remains
the single ACTIVE task, and this promotion neither is that task nor competes
with it. This record adds no queue entry of any status.

## Files changed by this promotion

- `ResearchOS/Analysis/GrowthOrder.lean` — new built module (promoted body).
- `ResearchOS.lean` — import added in the domain-neutral analysis-shelf group.
- `VERIFIED_RESEARCHOS.md` — nine `GO-*` rows; header prefix sentence extended
  to document `GO-` alongside `MB-`, `HK-`, `PL-` and `TC-`.
- `scripts/gen_researchos_registry.py` — `GO-` added to `PREFIX_DOMAINS`,
  mapped to the existing `analysis-generic` lane.
- `domains/riemann-hypothesis/drafts/README.md` — the `RiemannGrowthOrder.lean`
  row updated to record the promotion.
- `notes/reviews/ENTIRE_ORDER_PROMOTION_2026_08_08.md` — this record.

The generated `data/researchos_result_registry.json`,
`data/result_registry.json` and `ResearchOS/LedgerAxiomAudit.lean` are
regenerated by the repository-wide generator pass, not by this record.
