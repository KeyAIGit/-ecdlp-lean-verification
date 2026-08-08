# Generic Harnack disc package promotion review record (H1-H5)

Date: 2026-08-08

Scope: promotion of the independently accepted H1-H5 statement surface of
`domains/riemann-hypothesis/HARNACK_CONTRACT.md` into the built module
`ResearchOS/Analysis/HarnackDisc.lean`. This record is cited by the five
`HK-*` rows in `VERIFIED_RESEARCHOS.md`.

## Placement decision

The module is filed under `ResearchOS/Analysis/`, **not** under
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`.

1. **The surface is domain-neutral.** All five signatures speak only of
   `poissonKernel`, `Metric.sphere` / `ball` / `closedBall` in ℂ,
   `InnerProductSpace.HarmonicOnNhd`, `Real.circleAverage`, and real
   inequalities. The module imports one Mathlib module
   (`Mathlib.Analysis.Complex.Harmonic.Poisson`) and **zero repository
   modules**; the contract records no repo prerequisites. Nothing in the file
   names ζ, ξ, `completedRiemannZeta₀`, a theta kernel, `WeakFEPair`, or a
   zero of anything.
2. **The RH subtree is load-bearing, not decorative.**
   `scripts/gen_researchos_registry.py` pins `riemann-hypothesis` rows to
   `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`. Filing generic
   machinery there would have required either an `RH-*` claim id or a
   loosened subtree rule; the first misrepresents the content, the second
   weakens a gate.
3. **The lane already exists.** Unlike the Mellin promotion, this change
   registers **no new lane, no new subtree, and no new directory**. The
   domain-neutral `analysis-generic` lane
   (`domains/registry.json`, corpus `domains/analysis/corpus.md`) and the
   `ResearchOS/Analysis/` subtree were registered by the Mellin promotion
   (`notes/reviews/MELLIN_PROMOTION_2026_08_07.md`). The only plumbing this
   change adds is the `HK-` claim-id prefix in `PREFIX_DOMAINS`, registered
   exactly as `MB-` is; `DOMAIN_SUBTREES` and
   `scripts/check_ledger_isolation.py`'s `RESEARCHOS_LANE_DOMAINS` are
   untouched because `analysis-generic` is already in both.
4. **What the shelf is.** A shelf, not a research program: no frontier, no
   metrics source, no barrier map. `metrics_source` for the lane stays null,
   so no headline count moves.

## Review basis

1. **Independent statement acceptance.** The contract's five-signature
   statement surface (H1-H5) was accepted 2026-08-07 under owner-delegated
   review authority by a two-lens panel (truth-pin lens; boundary lens) —
   verdict ACCEPT WITH APPLIED EDITORIAL FIXES, six consolidated fixes, all
   prose/status/locator level, zero blocking items, zero statement changes.
   Record: `notes/reviews/HARNACK_ACCEPTANCE_2026_08_07.md`. The contract
   carries Annex A (findings A2-A7, appended at acceptance as Fix 1, all
   corrections already applied in the contract text, no signature changed).
2. **Prerequisites.** None. Like the Mellin package and unlike the
   bridge/xi/conjugation/multiplicity packages, this one waits on no merged
   repo module; its whole dependency set is pinned Mathlib. Promotion
   ordering therefore imposed no wait.
3. **Draft review provenance.** The promoted body is the drafts-lane file
   reviewed 2026-08-07 (`drafts/README.md`): the five statements were
   verified character-identical to the contract's §1/§2 `lean` blocks, the
   root-level-versus-namespace mean-value trap the contract audit found is
   correctly handled, and every registered obligation (H-1a, H-2a, H-3a/3b/
   3c/3d, H-4a, H-5a) is carried as an inline fallback. Verdict
   `LIKELY_ELABORATES`, zero fixes needed. `LIKELY_ELABORATES` is a
   static-reading verdict and is **not** a kernel verdict.
4. **Kernel check.** The verdict is delivered by CI on this promotion change:
   `lake build` compiles the module (reachable from `ResearchOS.lean`, in the
   analysis-shelf import group), the no-incomplete-proof gate scans it (it is
   outside `Targets/`), the regenerated `ResearchOS/LedgerAxiomAudit.lean` +
   `scripts/check_axioms.py` enforce the per-row `standard` axiom base, and
   `gen_researchos_registry.py --check` enforces inverse coverage. If any gate
   is red, no row is counted.

## Load-bearing checks

- **H2 exists only because the in-tree analogue is `private`.**
  `continuousOn_herglotz_riesz` (`Analysis/Complex/Harmonic/Poisson.lean:30-35`)
  is a `private lemma` and cannot be cited, so the (easier) `poissonKernel`
  form is re-proved by the same pattern: nonvanishing `have` in the local
  context, then `fun_prop`. This is obligation H-2a, the package's largest,
  MEDIUM, with three recorded routes (plain `fun_prop` per Annex A6 first,
  then the fully explicit `ContinuousOn.div`, then prove-on-a-larger-set +
  `.mono`). It is the most likely single CI bounce.
- **The mean-value lemma must be called by its root-level name.**
  `Analysis/Complex/Harmonic/MeanValue.lean` has no `namespace` command and no
  harmonic file has an `export`, so `:27` declares
  `_root_.HarmonicOnNhd.circleAverage_eq`. Dot notation on an
  `InnerProductSpace.HarmonicOnNhd`-typed term cannot resolve it; H3 uses the
  bare name, with the `_root_.`-explicit spelling recorded as the fallback
  (contract Annex A2).
- **Junk-value honesty is carried, not assumed away.** `Real.circleAverage` is
  total and returns `0` on a non-integrable integrand
  (`circleAverage.integral_undef`, `CircleAverage.lean:63`). Both
  `CircleIntegrable` arguments of `Real.circleAverage_mono`
  (`CircleAverage.lean:271`, where both are mandatory) are therefore supplied
  in H3 — `hintf` for `f` and `hint` for `poissonKernel c w • f`, the latter
  built from H2. Dropping either would make the comparison chain unsound
  against a zeroed junk average; the contract's death condition 3 forecloses
  that escape.
- **The `|R|` seam is real and is handled at three sites.** The pinned
  representation `…circleAverage_poissonKernel_smul`
  (`Harmonic/Poisson.lean:91`) is stated on `closedBall c R`, while
  `HarmonicOnNhd.circleAverage_eq` (`MeanValue.lean:27`),
  `CircleIntegrable.smul_of_continuousOn` (`CircleIntegral.lean:247`), and
  `Real.circleAverage_mono` are stated on `|R|`. `habs : |R| = R`
  (`abs_of_pos hR`) bridges all three sites (obligation H-3b).
- **`hR : 0 < R` is dropped in H3 and retained in H4, both deliberately.** In
  H3 the open-ball hypothesis `hw : w ∈ Metric.ball c R` forces it via
  `Metric.pos_of_mem_ball` (`Pseudo/Defs.lean:376`), a declared delta against
  the pool signature (`UPSTREAM_POOL.md:490-497`). In H4 closed-ball
  membership does **not** force it, and both the `hw'` and `hc` steps consume
  it, so it stays an explicit hypothesis (contract death condition 5).
- **Sharpness is not a claim.** The constants in H3 are the sharp classical
  ones, but no statement in this package asserts their optimality, no
  extremal `f` is exhibited, and the contract's claim boundary forbids adding
  such a statement without a new contract.
- **Zero definitions, zero instances.** The package is five theorems, so it
  introduces no new object whose meaning would need its own review.
- **H-3a remains the likeliest CI-cycle burner.** Four sites mix
  function-on-function smul (`Pi.smul_apply'`) with scalar-on-function smul
  (`Pi.smul_apply`); the defeq `show`/`exact` fallback is recorded inline at
  each site.

## Draft synchronization

The built module and the drafts-lane copy
(`domains/riemann-hypothesis/drafts/HarnackDisc.lean`) are byte-identical
from the first `import` through end of file — verified this session by `diff`
over the two slices, which reported no differences, and by matching SHA-256
`228c28de20875aeadfe9e6d50fb5bd852f007c12d311882430b47fef7abb7cdc` over the
common region (17248 bytes). They differ only in their leading status header:
the built copy carries the house-style built header, the drafts copy the
DRAFTS-LANE MIRROR header. Any proof-only kernel repair must be applied to
both copies before a new CI run; a statement change stops promotion and
returns to contract review.

## Claim boundary

This package is **generic complex analysis**. It closes **no** barrier,
advances **no** barrier, and partially closes **no** barrier: no row of
`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` and no `S1-*` item is
closed, weakened, re-scoped, or marked stale by it. No row of that map names
Harnack as exit evidence — the map has zero Harnack hits, re-verified this
session. Its effect on the capability map is **inventory only**, and this
change leaves that file untouched: no row is edited, added, or removed, and
none needs to be. The only fact created is that these five generic lemmas now
exist in built source. Generic machinery lowers the cost of a future exit but
never retires a row (contract death condition 6, inheriting
`MULTIPLICITY_CONTRACT.md` death condition 9).

Even on a fully green merge, what is gained is exactly five statements about
the Poisson kernel and nonnegative harmonic functions on a disc: no harmonic
function is constructed, none is evaluated, no boundary behaviour is
described, and the three deferred items (`HarmonicContOnCl` variant, Harnack
chain on compacts, vanishing propagation) remain out of surface.

No route is selected, opened, or advanced. This promotion provides **no
evidence for or against the Riemann Hypothesis**, and makes no claim of
progress on it in either direction. The RH queue is untouched by this change:
`RH-012` remains the single ACTIVE task, and this promotion neither is that
task nor competes with it.

## Kernel round 1 (rejected) and the proof-only repair

The first CI run of this promotion (PR #318, run 31237149293) **rejected** this
module, with one error and two warnings:

1. `HarnackDisc.lean:220:66` — `Application type mismatch`: `hw` has type
   `w ∈ ball c R` but was expected to have type `w ∈ ball c |(|R|)|`, in the
   application `continuousOn_poissonKernel hw`. The site is OBLIG H-3b site 2,
   where `CircleIntegrable.smul_of_continuousOn` (CircleIntegral.lean:247) wants
   its continuity hypothesis on `sphere c |R|` while H2 supplies it on
   `sphere c R`. The bridge was written as `habs ▸ continuousOn_poissonKernel hw`
   with `habs : |R| = R`. That equation admits both rewrite directions against
   the expected type, and `▸`'s heuristic took the one that replaces `R` by
   `|R|`; the doubled absolute value in the error message is that substitution
   applied to the `|R|` already present. Repaired by the contract-recorded
   fallback, applied verbatim: an explicit `show ContinuousOn (poissonKernel c w)
   (Metric.sphere c |R|) by rw [habs]; exact continuousOn_poissonKernel hw`,
   which states the target type outright and rewrites it in the one intended
   direction, so no heuristic is consulted.
2. `HarnackDisc.lean:146:21` — two `aesop: failed to prove the goal after
   exhaustive search` **warnings**, not errors: the H2 line
   `fun_prop (disch := aesop)` was accepted by the kernel. The diagnosis
   recorded inline is that the side goal actually needed, `ContinuousOn.div₀`'s
   `∀ x ∈ s, g x ≠ 0`, is `hne'` verbatim and is closed by `fun_prop`'s built-in
   `with_reducible assumption` before the discharger runs; the two aesop calls
   were spent on the unprovable side conditions of the competing `Continuous.div₀`
   / `ContinuousAt.div₀` candidates. **That line was deliberately left
   unchanged.** A repair round exists to fix what the kernel rejected; narrowing
   the discharger to silence cosmetic warnings would be an unforced edit to
   already-accepted code, and it belongs in its own change with its own CI round.

**Nothing in the H1-H5 statement surface moved** — five of five signatures
byte-identical to the pre-repair head by mechanical comparison, and the three
`HK-*` anchors whose line numbers shifted kept their `sha256` statement digest
exactly. Only one proof term and its surrounding comments changed, so this is a
proof repair and not a contract-review event.

The kernel verdict on the repaired head is again delivered by CI, not by this
record. If the re-run is red, no row here counts.
