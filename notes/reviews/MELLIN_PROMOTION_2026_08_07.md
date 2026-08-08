# Generic Mellin norm-bound package promotion review record (MB1-MB4)

Date: 2026-08-07

Scope: promotion of the independently accepted MB1-MB4 statement surface of
`domains/riemann-hypothesis/MELLIN_BOUND_CONTRACT.md` into the built module
`ResearchOS/Analysis/MellinBound.lean`. This record is cited by the five
`MB-*` rows in `VERIFIED_RESEARCHOS.md`.

## Placement decision

The module is filed under `ResearchOS/Analysis/`, **not** under
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`.

1. **The surface is domain-neutral.** All five signatures are generic over
   `{E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]` and mention only
   `mellin`, `Real.rpow`, Bochner set integrals, and `IntegrableOn` /
   `AEStronglyMeasurable`. The module imports four Mathlib modules and **zero
   repository modules**; the contract records "Repo prerequisites: none."
   Nothing in the file names ζ, ξ, `completedRiemannZeta₀`, a theta kernel,
   `WeakFEPair`, or a zero of anything.
2. **The RH subtree is load-bearing, not decorative.**
   `scripts/gen_researchos_registry.py` pins `riemann-hypothesis` rows to
   `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`. Filing generic
   machinery there would have required either an `RH-*` claim id or a
   loosened subtree rule; the first misrepresents the content, the second
   weakens a gate. Both are worse than a new directory.
3. **A new subdirectory under `ResearchOS/` is structurally free.**
   `lakefile.toml` declares the `ResearchOS` `lean_lib` by root name, so
   every module reachable from `ResearchOS.lean` is built with no lakefile
   edit. `scripts/check_ledger_isolation.py` rule 4 requires exactly that
   reachability, and the import added to `ResearchOS.lean` supplies it; rule
   5's audit whitelist is keyed to exact paths and is unaffected; rule 3's
   domain-metrics rule is satisfied because the new domain claims null
   metrics.
4. **Cost of the choice, stated.** Honest placement required registering a
   new lane: `analysis-generic` in `domains/registry.json` (with corpus
   `domains/analysis/corpus.md`), the `MB-` prefix in `PREFIX_DOMAINS`, the
   `ResearchOS/Analysis/` subtree in `DOMAIN_SUBTREES`, and the id in
   `RESEARCHOS_LANE_DOMAINS`. That lane is a **shelf, not a research
   program**: it has no frontier, no metrics source, and no barrier map.

## Review basis

1. **Independent statement acceptance.** The contract's five-signature
   statement surface (MB1, MB2, MB3 ×2, MB4) was accepted 2026-08-07 under
   owner-delegated review authority — verdict ACCEPT WITH APPLIED EDITORIAL
   FIXES, six consolidated fixes, all prose/citation/skeleton level, zero
   blocking items, zero statement changes. Record:
   `notes/reviews/MELLIN_ACCEPTANCE_2026_08_07.md`. The contract itself
   carries the red-team Annex A (findings R1-R4, all fixed in place, no
   signature changed).
2. **Prerequisites.** None. Unlike the bridge/xi/conjugation/multiplicity
   packages, this one waits on no merged repo module; its whole dependency
   set is pinned Mathlib. Promotion ordering therefore imposed no wait.
3. **Draft review provenance.** The promoted body is the drafts-lane file
   reviewed 2026-08-07: the five statements were verified character-identical
   to the contract's §2 `lean` blocks by mechanical diff, every invoked API
   was grep-verified at the pin, and all nine registered obligations
   (MEL-1a/1b, 2a/2b, 3a/3b, 4a/4b/4c) are carried as inline fallbacks.
   Verdict `LIKELY_ELABORATES`, zero fixes needed. `LIKELY_ELABORATES` is a
   static-reading verdict and is **not** a kernel verdict.
4. **Kernel check.** The verdict is delivered by CI on this promotion change:
   `lake build` compiles the module, the no-incomplete-proof gate scans it
   (it is outside `Targets/`), the regenerated
   `ResearchOS/LedgerAxiomAudit.lean` + `scripts/check_axioms.py` enforce the
   per-row `standard` axiom base, and `gen_researchos_registry.py --check`
   enforces inverse coverage. If any gate is red, no row is counted.

## Load-bearing checks

- **MB1 is unconditional, and must stay so.**
  `norm_integral_le_integral_norm` (Bochner/Basic.lean:924) needs no
  integrability — its proof internalizes the non-`AEStronglyMeasurable` case
  — and `setIntegral_congr_fun` (Bochner/Set.lean:73) is a congruence.
  Adding any guard to MB1 is the contract's death condition 3.
- **Integrability sits on the bound, never on `f`.** MB2-MB4 assume
  `IntegrableOn (fun t => t ^ (σ - 1) * g t) (Ioi 0)`. These hypotheses are
  not decoration: `not_integrableOn_Ioi_rpow` (ImproperIntegrals.lean:160)
  shows `t ^ σ` alone is never integrable on `Ioi 0`, so without them the
  conclusions would be false-by-junk against a zeroed non-integrable
  right-hand side.
- **MB3's support restriction is the honest content.** `t ↦ t ^ (σ - 1)` is
  increasing in `σ` only for `t ≥ 1`; the unrestricted monotonicity statement
  is **false** (death condition 4). `hgsupp` (`g = 0` on `Ioo 0 1`) is
  therefore a hypothesis of the theorem, not a convenience. The `t = 1`
  boundary is placed in the `1 ≤ t` branch by `lt_or_ge t 1` (MEL-3b); the
  seam must be re-checked before any move to `Ioc 0 1` support.
- **MB4's measurability hypothesis is carried, not smuggled.** Middle-exponent
  integrability comes from `Integrable.mono` (L1Space/Integrable.lean:86),
  whose measurability leg is not derivable from bare endpoint `IntegrableOn`
  hypotheses, so `hmg : AEStronglyMeasurable g (volume.restrict (Ioi 0))` is
  an explicit argument. `Integrable.mono` is called **by name** through
  `hsum.integrable`: dot notation on an `IntegrableOn`-typed term is captured
  by `IntegrableOn.mono` (IntegrableOn.lean:124), a set/measure monotonicity
  lemma and the wrong target. This is obligation MEL-4a, the package's only
  MEDIUM and the most likely single CI bounce.
- **Two recorded proof-body deviations from the contract skeleton, no
  statement touched.** (i) `le_of_lt ht` replaces `ht.le`, because dot
  notation on `ht : t ∈ Set.Ioi 0` resolves in the `Membership.mem`
  namespace. (ii) `ht'` / `h0` restate the context in the `0 < _` / `0 ≤ _`
  shapes `positivity` consumes. Both are proof-only; the contract's
  Return-to-stage-one condition is not triggered.
- **Zero definitions, zero instances.** The package is five theorems (death
  condition 2), so it introduces no new object whose meaning would need its
  own review.

## Draft synchronization

The built module and the drafts-lane copy
(`domains/riemann-hypothesis/drafts/MellinBound.lean`) are byte-identical
from the first `import` through end of file — verified this session by `diff`
over the two slices, which reported no differences, and by matching SHA-256
`91f62aec76c5a2441a2808caf6150be3ec16e3ec1dcf5ff221a04b8145777535` over the
common region. They differ only in their leading status header. Any
proof-only kernel repair must be applied to both copies before a new CI run;
a statement change stops promotion and returns to contract review.

## Claim boundary

This package is **generic complex analysis and measure theory**. It closes
**no** barrier, advances **no** barrier, and partially closes **no** barrier:
no row of `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` and no
`S1-*` item is closed, weakened, re-scoped, or marked stale by it. Its effect
on the capability map is **inventory only**, and this change leaves that file
untouched: no row is edited, added, or removed, and none needs to be. The only
fact created is that these five generic lemmas now exist in built source.
Generic machinery lowers the cost of a future exit but never retires a row
(contract death condition 6, inheriting `MULTIPLICITY_CONTRACT.md` finding A4).

Even on a fully green merge, what is gained is exactly five norm
inequalities: no Mellin transform is evaluated, none is shown convergent
(MB2-MB4 *assume* integrability of the bound), and no analytic continuation,
functional equation, or growth statement is made. The `Λ₀`-seam of the
contract's §3 is a non-normative citation of a hypothetical future consumer;
nothing in the promoted surface mentions it, and this record asserts nothing
about whether that seam composes.

No route is selected, opened, or advanced. This promotion provides **no
evidence for or against the Riemann Hypothesis**, and makes no claim of
progress on it in either direction. The RH queue is untouched by this change:
`RH-012` remains the single ACTIVE task, and this promotion neither is that
task nor competes with it.
