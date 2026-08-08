# Polynomial-growth Liouville package promotion review record (L1-L5)

Date: 2026-08-08

Scope: promotion of the independently accepted L1-L5 statement surface of
`domains/riemann-hypothesis/POLY_LIOUVILLE_CONTRACT.md` (UPSTREAM-POOL item 4)
into the built module `ResearchOS/Analysis/PolyLiouville.lean`. This record is
cited by the five `PL-*` rows in `VERIFIED_RESEARCHOS.md`. Format precedent:
`notes/reviews/MELLIN_PROMOTION_2026_08_07.md`.

## Placement decision

The module is filed under `ResearchOS/Analysis/`, **not** under
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`.

1. **The surface is domain-neutral.** L1 and L2 are generic over
   `{F : Type*} [NormedAddCommGroup F] [NormedSpace ℂ F] [CompleteSpace F]`;
   L3-L5 specialise to `ℂ → ℂ` only because `Polynomial.eval` forces it. All
   five quantify over an **arbitrary** entire `f` and mention only
   `Differentiable ℂ`, `iteratedDeriv`, `HasSum`/Taylor sums, `Polynomial ℂ`,
   and norms. The module imports five Mathlib modules and **zero repository
   modules**; the contract records no repo prerequisites. Nothing in the file
   names ζ, ξ, `completedRiemannZeta₀`, an `LSeries`, a critical strip, or a
   zero of anything.
2. **The RH subtree is load-bearing, not decorative.**
   `scripts/gen_researchos_registry.py` pins `riemann-hypothesis` rows to
   `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`. Filing generic
   machinery there would have required either an `RH-*` claim id or a loosened
   subtree rule; the first misrepresents the content, the second weakens a
   gate.
3. **The shelf already exists, so this promotion adds no machinery.** The
   `analysis-generic` lane, its `domains/registry.json` entry, the
   `ResearchOS/Analysis/` subtree in `DOMAIN_SUBTREES`, and the lane id in
   `scripts/check_ledger_isolation.py`'s `RESEARCHOS_LANE_DOMAINS` were all
   registered by the `MB-*` Mellin promotion. This change therefore registers
   exactly **one** new thing — the `PL-` prefix in `PREFIX_DOMAINS`, mapped to
   the existing `analysis-generic` lane — plus the documentation of that
   prefix in the ledger header. No new lane, no new subtree, no lakefile edit:
   `lakefile.toml` declares the `ResearchOS` `lean_lib` by root name, so the
   import added to `ResearchOS.lean` is all the build and all of
   `check_ledger_isolation.py` rule 4 (reachability) require.
4. **The shelf is a shelf, not a research program.** `analysis-generic` has no
   frontier, no metrics source, and no barrier map, and nothing on it is owned
   by or counts toward any conjecture program. These rows move no RH-lane
   count.

## Review basis

1. **Independent statement acceptance.** The contract's five-signature
   statement surface (L1-L5) was accepted 2026-08-07 under owner-delegated
   review authority — two independent lenses (truth-pin, claim boundary),
   verdict **ACCEPT WITH APPLIED EDITORIAL FIXES**, six consolidated fixes,
   all prose/locator/record-completeness level, **zero blocking items, zero
   statement changes**. Record:
   `notes/reviews/POLY_LIOUVILLE_ACCEPTANCE_2026_08_07.md`. The contract
   carries its own adversarial Annex A (findings A1-A5, folded in pre-
   acceptance, no signature changed).
2. **The acceptance conferred no standing on the draft, and this record does
   not treat it as if it had.** Acceptance Fix 3 is explicit: stage one
   accepted the contract's §2 statement blocks only, `drafts/PolyLiouville.lean`
   had **no standing** under it, and any stage-two use of the draft requires an
   **independent character-identity check** of its statements against §2. That
   check is the draft review of 2026-08-07 recorded in
   `domains/riemann-hypothesis/drafts/README.md`: statements character-
   identical by mechanical diff, all eleven registered obligations (PL-1a/1b/1c,
   2a/2b/2c, 3a/3b, 4a, 5a/5b) carried as inline fallbacks including the
   HasSum/SummationFilter seam, verdict PASS with one comment-only locator fix.
   `PASS` there is a static-reading verdict and is **not** a kernel verdict.
3. **Prerequisites.** None. Like the Mellin package and unlike the
   bridge/xi/conjugation/multiplicity packages, this one waits on no merged
   repo module; its whole dependency set is pinned Mathlib. Promotion ordering
   imposed no wait.
4. **Kernel check.** The verdict is delivered by CI on this promotion change:
   `lake build` compiles the module, the no-incomplete-proof gate scans it (it
   is outside `Targets/`), the regenerated `ResearchOS/LedgerAxiomAudit.lean` +
   `scripts/check_axioms.py` enforce the per-row `standard` axiom base, and
   `gen_researchos_registry.py --check` enforces inverse coverage. If any gate
   is red, no row is counted. **No Lean toolchain was run while preparing this
   promotion**; nothing in this record is a kernel verdict.

## Load-bearing checks

- **L1 carries all the analysis; L3 is packaging.** The contract's §1 decision
  makes the vanishing-coefficient lemma primary, and the built module keeps
  that order: L2 consumes L1, L3 consumes L2, L4 and L5 consume L3. Reordering
  or re-deriving L3 directly would discard the Banach-valued content of L1/L2.
- **`0 ≤ C` is derived, never assumed.** `hC0` comes from specialising the
  growth hypothesis at `0` (`hC 0` plus `norm_nonneg`), so no nonnegativity
  side-condition was smuggled into any signature. This also keeps the `C = 0`
  and `n = 0` corners honest: at `C = 0` the polynomial `P` is `0` with
  `degree ⊥`, and the degree chain `degree P ≤ 0 + n·1 = n < k = degree Q`
  still holds in `WithBot ℕ`.
- **The degree chain is an explicit term chain, deliberately.** Annex A
  finding A1: the `degree_*_le` family carries **no** `@[gcongr]` attribute at
  the pin and the goal is a bound rather than a congruence shape, so `gcongr`
  has nothing to fire. The chain also uses `degree_pow_le_of_le`
  (Degree/Defs.lean:406, conclusion `b * a`, multiplication in `WithBot ℕ`) and
  **not** `degree_pow_le` (:402, the `n • degree p` smul shape); mixing the two
  is a type error, and the distinction is recorded inline.
- **PL-2a is the package's riskiest seam and is carried, not hidden.** L2
  composes three lemmas across the SummationFilter API: `HasSum` elaborates as
  `HasSum f a (unconditional ℕ)` by defaulted third argument
  (InfiniteSum/Defs.lean:106), and `hasSum_taylorSeries_of_entire`,
  `hasSum_sum_of_ne_finset_zero` (`[L.LeAtTop]`, :295) and `HasSum.unique`
  (`[T2Space α] [L.NeBot]`, :323/:326) must all instantiate at that same
  defaulted filter with **instance resolution**, not unification, supplying
  `LeAtTop` and `NeBot` (SummationFilter.lean:171/:173). No explicit `L` is
  written anywhere, deliberately. Two exact fallbacks are inline (pin
  `(L := unconditional ℕ)` on the collapse call only; use `HasSum.unique h1 h2`
  in place of dot notation). If both fail, contract death condition 5 applies:
  stop and re-plan via the tsum route — which carries the **same** `[L.LeAtTop]`
  seam (`tprod_eq_prod`, InfiniteSum/Basic.lean:457) — and if that also fails,
  `UPSTREAM_POOL.md` §4.3's difficulty assessment must be corrected before any
  further attempt. Do not patch around it. This is the single most likely CI
  bounce in the package.
- **L2's summand is written in the pinned smul-shape and factor order.** It
  matches `hasSum_taylorSeries_of_entire` (TaylorSeries.lean:129-130)
  syntactically, so `HasSum.unique` applies with no congruence step. Any
  reshaping of that summand reopens the seam.
- **L4 is a self-check, not a new fact.** The degree-0 corollary is classical
  Liouville, already provable at the pin from
  `Differentiable.exists_const_forall_eq_of_bounded` (Liouville.lean:123) via
  `isBounded_iff_forall_norm_le`. Its value here is that the package derives it
  a second way; the `PL-4` row says exactly that and claims no novelty.
- **One recorded name-resolution deviation, no statement touched.** The
  contract preamble opens neither `Complex` nor a `namespace Complex` block,
  and the five declarations carry the `Complex.` prefix in their names exactly
  as the contract's §2 blocks spell them. Every `Complex`-namespace lemma and
  every cross-reference between L1-L5 is therefore written **fully qualified**
  in the proof bodies, where the contract's skeletons spell them unqualified
  (which cannot resolve at the top level). Proof-only; statements are
  untouched and the contract's return-to-stage-one condition is not triggered.
- **Zero definitions, zero instances.** The package is five theorems, so it
  introduces no new object whose meaning would need its own review.

## Draft synchronization

The built module and the drafts-lane copy
(`domains/riemann-hypothesis/drafts/PolyLiouville.lean`) are byte-identical
from the first `import` through end of file — verified this session by `diff`
over the two slices, which reported no differences, and by matching SHA-256
`c945ee678903eb2636221450269a8a85dbf8768adad34d8c4acbd363d0609522` (18247
bytes) over the common region. They differ only in their leading status
header: the built copy carries the promoted-module header, and the drafts copy
was converted from its non-built draft header to the drafts-lane **mirror**
form in this change. Any proof-only kernel repair must be applied to both
copies before a new CI run; a statement change stops promotion and returns to
contract review.

## Claim boundary

This package is **generic complex analysis**. It closes **no** barrier,
advances **no** barrier, and partially closes **no** barrier: no row of
`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` and no `S1-*` item is
closed, weakened, re-scoped, or marked stale by it. In particular `S1-GROWTH`
("no zeta/xi vertical or order-one growth theorem",
`MATHLIB_CAPABILITY_MAP.md:388`) remains **OPEN** and untouched — polynomial
growth of an arbitrary entire `f` does not reach that row's order-one
exponential ζ/ξ scope, as both acceptance lenses independently re-confirmed.
The capability-map effect is **inventory only**, and this change leaves that
file untouched: no row is edited, added, or removed, and none needs to be. The
only fact created is that these five generic lemmas now exist in built source.
Generic machinery lowers the cost of a future exit but never retires a row
(contract death condition 6, inheriting `MULTIPLICITY_CONTRACT.md` finding A4).

Even on a fully green merge, what is gained is exactly five statements about
arbitrary entire functions that are **assumed** to satisfy a polynomial growth
bound. No growth bound is established for any named function; ξ, ζ, and every
other specific function are outside the package entirely. Nothing here is a
step in a proof of anything about the Riemann Hypothesis unless and until some
future, separately reviewed work supplies such a bound for a named function —
and this record asserts nothing about whether that is feasible.

No route is selected, opened, or advanced. This promotion provides **no
evidence for or against the Riemann Hypothesis**, and makes no claim of
progress on it in either direction. The RH queue is untouched by this change:
`RH-012` remains the single ACTIVE task, and this promotion neither is that
task nor competes with it. This record adds no queue entry of any status.

## Files changed by this promotion

- `ResearchOS/Analysis/PolyLiouville.lean` — new built module (promoted body).
- `ResearchOS.lean` — import added in the domain-neutral analysis-shelf group.
- `domains/riemann-hypothesis/drafts/PolyLiouville.lean` — header converted to
  the drafts-lane mirror form; body byte-unchanged.
- `VERIFIED_RESEARCHOS.md` — five `PL-*` rows; header prefix sentence extended
  to document `PL-` alongside `MB-`.
- `scripts/gen_researchos_registry.py` — `PL-` added to `PREFIX_DOMAINS`,
  mapped to the existing `analysis-generic` lane.
- `domains/riemann-hypothesis/drafts/README.md` — the `PolyLiouville.lean` row
  updated to record the promotion.
- `notes/reviews/POLY_LIOUVILLE_PROMOTION_2026_08_08.md` — this record.

The generated `data/researchos_result_registry.json` and
`ResearchOS/LedgerAxiomAudit.lean` are regenerated by the repository-wide
generator pass, not by this record.
