# RH-011 zero-set slice contract acceptance record

Date: 2026-08-07

Status: FINAL — committed in the RH-011 acceptance change after the RH-010
promotion (merged PR #313, `2a20629`) landed on `main`.

## Reviewed baseline

- repository branch `claude/rimmen-hypothesis-b6gd62` at
  `3783f311b352fbaf9489ff2e86c138b3b2bf86d1` (post-PR #314);
- reviewed object `domains/riemann-hypothesis/ZERO_SET_SLICE_CONTRACT.md`
  (1,247 lines pre-fix, SHA-256
  `857a5d9a704c84b5a58e9915f139ca21cc133a5684c21083b70d7e92850f5e78`, Git
  blob `7559068b277fff203aea68d86f060e1fbe885601`); post-editorial-fix state
  (1,281 lines) SHA-256
  `2e9b54442443d46fe3a3e83d24bc83bb9b191e8d95666b59948f959e3187fd62`
  (Git blob `0a5cb2dee6a381d47e2a1a3cc382cc156b6f391d`);
- built M-package prerequisite
  `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean` (1,009
  lines, SHA-256
  `1cf5180a5b5f04cfaa87e6f60e7ed16d6e452cd6eb0d669d0850904761a2d91e`),
  merged in PR #313 (`2a20629`), kernel-checked on `main`, imported at
  `ResearchOS.lean:10`. Per the RH-011 charge, **every `[MULT]` citation was
  re-checked against this BUILT module**, not against
  `MULTIPLICITY_CONTRACT.md`;
- pinned Mathlib revision `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`
  (v4.31.0), re-verified by `git rev-parse HEAD` at
  `/workspace/leanprover-community/mathlib4` during this review;
- merged kernel-checked repo context: `Xi.lean` (PR #304 `afdae08`),
  `Conj.lean` (PR #307 `c277b86`).

No Lean toolchain was run. Every check below is source reading; nothing in
this record is a kernel verdict.

## Authority and effect

This panel acted under **owner-delegated review authority** as recorded in
the repository governance notes: the RH queue's dated 2026-08-07 decision
installs `RH-011` — the acceptance-only review of this statement surface —
as the sole ACTIVE task (`tasks/RIEMANN_HYPOTHESIS.md:760–764`, "acceptance
only; produces no built module and no kernel verdict"); the two-stage gate
of `MULTIPLICITY_CONTRACT.md` §Two-stage gate applies verbatim; form
precedent `notes/reviews/RH009_MULT_CONTRACT_ACCEPTANCE_2026_08_07.md`.
This is the second, independent pass after the design-time consolidation
review (`SOUND_WITH_FIXES`, contract Annex N). Acceptance under this record:

- covers the **statement surface only** of the zero-set / compact
  divisor-sum slice (N2-D1–D9 and N1.1–N1.9, exactly 23 public Lean
  signatures, independently retallied by all three lenses:
  D1–D6 = 6, D7 = 2, D8 = N1.1 = 1, D9 = 1, N1.2–N1.5 = 4,
  N1.6–N1.8 = 6, N1.9 = 3);
- carries **no kernel verdict** — no Lean toolchain was run, and only the
  Lean kernel via CI can ever supply one;
- **changes no barrier row** — `S1-GLOBAL-ZEROS` in
  `MATHLIB_CAPABILITY_MAP.md` (row at `:387`, quoted verbatim and verified
  unchanged) remains **OPEN**; the surface advances the row's neutral slice
  without closing it, and all routes remain **PARKED**;
- **promotes nothing** — a stage-two built promotion of a `ZeroSet.lean`
  module, judged solely by CI/the kernel, is a separate later change; this
  record is not it and does not schedule it;
- selects no route, states no cutoff shape, and provides no evidence for or
  against the Riemann Hypothesis.

## Panel composition

Three independent lenses, each reading the contract in full against the
pinned Mathlib checkout and the built merged repository modules:

1. **Mathematical-truth lens** — re-derived all 23 statements at every point
   of their stated domains (including `K = ∅`, noncompact `K` where allowed,
   `U = ∅`, `U = Set.univ`), with exceptional-point and junk-value symmetry
   audits.
2. **Pin-fidelity (API) lens** — re-opened every load-bearing `file:line`
   locator at the pin (~60 checks), re-verified the `to_additive`
   generated-name risk (S1N1-SUM), re-ran the 24-stem collision scan
   post-merge, and compared every `[MULT]` citation against the built
   `Mult.lean`.
3. **Claim-boundary and scope lens** — audited the closure discipline, the
   `S1-GLOBAL-ZEROS` exit-item mapping, neutrality (no cutoff shape in any
   signature), the death conditions and deferrals, and the two-stage gate.

## Decision: **ACCEPT WITH APPLIED EDITORIAL FIXES**

All 23 statements are mathematically true as stated; **no declaration name,
binder, hypothesis, conclusion, or proof skeleton changed**. Zero blocking
items. The applied fixes fall in two classes: (i) staleness-of-status prose
— the contract was drafted while the `RH-010` promotion was in flight, and
PR #313 merged before this acceptance ran; (ii) one factual correction to a
recorded naming claim (`Complex.conj_conj`), found by the boundary lens and
confirmed by direct source read at the pin.

## Per-lens verdicts

| Lens | Verdict | Blocking defects | Editorial fixes |
|---|---|---|---|
| Mathematical truth | **ACCEPT WITH EDITORIAL FIXES** | none | 4 required (all status-prose staleness; consolidated below as Fixes 1–4) |
| Pin fidelity (API) | **ACCEPT WITH EDITORIAL FIXES** | none | 3 required + 1 optional (E1–E3 map onto Fixes 1, 2, 4; E4 — N2-f spelling — folded into Fix 2's supersession note) |
| Claim boundary and scope | **ACCEPT WITH EDITORIAL FIXES** | none | 5 required (A–E map onto Fixes 1–5; Fix D is the `Complex.conj_conj` factual correction, unique to this lens) |

No lens returned BLOCK or REJECT. **Blocking items: none.**

One inter-lens conflict was resolved by direct source read during
consolidation: the math lens re-affirmed the contract's claim that
`Complex.conj_conj` is absent at the pin; the boundary lens found it present
as `alias Complex.conj_conj := starRingEnd_self_apply` at
`Algebra/Star/Basic.lean:364` (with `RCLike.conj_conj` at :366). The
consolidator re-opened the pinned file: **the boundary lens is correct** —
the alias exists. Harmless in effect (the recorded primary spelling
`starRingEnd_self_apply`, :348, exists and the alias unfolds to the same
term), but the factual premise required correction (Fix 5).

## Applied editorial fixes

All five consolidated fixes were applied to
`domains/riemann-hypothesis/ZERO_SET_SLICE_CONTRACT.md` during this
acceptance session; the post-fix baseline hashes above are of the fixed
file. None touches a signature.

**Fix 1 — Queue position (header ¶2).** The stale "sole ACTIVE task is
`RH-010` … `tasks/RIEMANN_HYPOTHESIS.md:616`" paragraph (the `:616` locator
had also drifted) now records that, by the dated 2026-08-07 queue decision,
the sole ACTIVE task is `RH-011` — the acceptance review of this very
surface (`tasks/RIEMANN_HYPOTHESIS.md:760–764`) — with `RH-010` completed
the same day via merged PR #313 (`2a20629`). The document still authorizes
no route work; the two-stage gate sentence is unchanged.

**Fix 2 — Package prerequisites re-anchored to the built module.** The
M-table header no longer says "promotion in flight / never as already
kernel-checked"; it now states the M-package is **kernel-checked on `main`**
(merged PR #313, built `Mult.lean`, imported at `ResearchOS.lean:10`), with
built-module locators as the citation of record and the
`MULTIPLICITY_CONTRACT.md` locators retained parenthetically as
accepted-surface provenance: M9 `Mult.lean:361` (plus
`meromorphicOn_riemannXi` :377), M10 `:388`, M11 `:410`, M12 `:444`/`:504`,
M13 `:538`, M14 `:573`, M15 `:634`/`:670` — each verified by this panel
name-for-name and binder-for-binder against the contract's usage (M10's RHS
`((analyticOrderAt riemannXi z).map (↑)).untop₀` exact; M13's forward
orientation confirmed, so the recorded forward-`rw` with no `.symm` is
correct; M14/M15's `hU` / `hU₁`,`hU₂` hypothesis shapes and order verbatim
against N1.6–N1.8). A dated supersession note was inserted after the honesty
note, which also records (per the API lens's optional E4, so it is not
lost) that the built M13 fixes the support spelling as the coercion form
`Function.support (MeromorphicOn.divisor riemannXi U)` — the form every
signature in this contract already uses — resolving the N2-f package-wide
spelling decision in that direction.

**Fix 3 — Conditionality prose settled.** Every "in flight / not
kernel-checked tonight / not provable at this pin until the `RH-010`
promotion lands / becomes provable the moment the promotion merges" framing
was replaced with the settled form: the §2 legend (`[MULT]` now records
provenance and import ordering, not an open conditionality), the
Candidate-fields claim boundary, the preamble's Mult import comment, the
N1.1 all-ingredients verdict ("provable now from the pin plus `main`,
either route"), the D9 verdict, and the §Claim boundary "What is claimed"
bullet.

**Fix 4 — N-SEQ discharged.** The obligation register's head row, the
N1.1 and D9 obligation blocks, and Annex D's first bullet now read
**N-SEQ: DISCHARGED 2026-08-07** — the `RH-010` promotion merged (PR #313,
`2a20629`), the Mult module is kernel-checked on `main` and importable, and
the sequencing condition is satisfied. The residual discipline is preserved
verbatim in every location: the built ZeroSet module must **import** the
built Mult module and must never inline re-derive M-package content (death
condition 5, unchanged and still in force).

**Fix 5 — `Complex.conj_conj` factual correction (S1N1-7b).** The N1.7
obligation text, the register row, and Annex N §B no longer claim the name
is absent at the pin; they now record it as an alias of
`starRingEnd_self_apply` at `Algebra/Star/Basic.lean:364`, with
`starRingEnd_self_apply` (:348) kept as the primary recorded spelling and
the alias as a same-term fallback, and the correction attributed to this
RH-011 acceptance. Annex N's frozen design-time record is otherwise
untouched (its historical "queue state as re-verified then" sentences
correctly describe what that earlier review saw).

## Review basis (spot summary of the panel's independent checks)

1. **Truth at exceptional points.** ξ entire, no excluded point; D1 witness
   `riemannXi 0 = 1/2 ≠ 0` kernel-checked (`Xi.lean:72`). D7 honest for
   arbitrary `U` because `MeromorphicOn.divisor` is total with junk value 0
   (Divisor.lean:39, verified at source). Decision 3 is correct mathematics:
   the hypothesis-free generic carrier-finiteness form is **false**
   (Blaschke boundary-accumulation counterexample valid;
   LocallyFinsupp.lean:54 guarantees local finiteness only at points of
   `U`), N1.1 is genuinely a ξ-entirety theorem, and death condition 6
   rightly forbids the false generality. All three involutions re-derived,
   including `1 − conj(1 − conj w) = w`.
2. **Junk-value symmetry.** Every equality carries junk conventions on both
   sides simultaneously; N1.6–N1.8 comp and image forms are unconditionally
   true for arbitrary (even infinite-support) `K` because
   `finprod_mem_congr`/`finprod_mem_image` are finiteness-hypothesis-free at
   the pin (Finprod.lean:565/:929); `IsCompact` appears exactly where honest
   sums demand it; N1.5's `K₂`-only compactness asymmetry is correct and
   strictly more neutral.
3. **Pin fidelity.** ~60 load-bearing locators re-opened at the pin across
   Order.lean, DiscreteSubset.lean, Constructions.lean, Compact.lean,
   Lindelof.lean, LocallyFinsupp.lean, Divisor.lean, Finprod.lean,
   Group/Finset.lean, ZetaZeros.lean, the Set/Logic/Algebra glue files, and
   the full N2-a/N2-d instance chains: **zero incorrect locators** (the one
   false *claim* — `Complex.conj_conj` absence — was about a name not
   cited as a dependency, and is corrected by Fix 5). The S1N1-SUM risk is
   accurately registered: `@[to_additive]` bare at Finprod.lean:499/:929,
   generated additive names absent from source (0 grep hits), in-tree
   precedent for the dictionary translation at
   `Data/Set/Card/Arithmetic.lean:112`, explicit additive names confirmed
   for `sum_nonneg`/`sum_le_sum_of_subset_of_nonneg`.
4. **`[MULT]` vs the built module.** All nine consumed declarations exist in
   the built kernel-checked `Mult.lean` with exactly the consumed names,
   binder shapes, hypothesis order, and RHS spellings (locators in Fix 2);
   nothing in the built module re-scopes any consumed statement; the shaped
   (`univ`/strip) divisor instances the built M-package additionally ships
   belong to the accepted M-surface, appear in none of this contract's 23
   signatures, and do not breach the neutrality rule.
5. **Collision freshness.** All 23 proposed names plus the superseded
   `IsCompact.inter_riemannXi_divisor_support_finite` re-scanned post-merge
   against pinned `Mathlib/`, `ResearchOS/`, `Ecdlp/`, the root modules, and
   the drafts directory — **0 hits each**, including against the
   declarations PR #313 introduced; `riemannXi` has 0 hits in pinned
   `Mathlib/`; no `ZeroSet` module exists yet, so the working name is free.
6. **Neutrality and claim boundary.** All 23 signatures mechanically
   re-scanned for `closedBall`, `sphere`, balls, norms, `.re`, `.im`,
   strips, boxes, intervals: zero hits in any signature; shapes occur only
   in the licensed places (quoted non-mirrored pinned specials, the N2-d
   proof-internal fallback, N-DEFERRED-3's refusal). Zero `def`s. No
   enumeration, ordering, counting, growth, density, or convergence object
   anywhere (`Set.Countable` yields existence of an injection, not a
   listing; N1.4 is a cast identity, not a counting function). Repo-side
   citations (`Xi.lean`, `Conj.lean`, `MULTIPLICITY_CONTRACT.md` block
   locators, `MATHLIB_CAPABILITY_MAP.md:387`) all verbatim on `main`; the
   capability map's 2026-08-07 addendum closing `S1-MULTIPLICITY`/`S1-CONJ`
   does not interact with this contract's claims.

## Statement disposition

| Block | Declaration surface (23 signatures) | Disposition |
|---|---|---|
| N2-D1 | `compl_riemannXi_zeroSet_mem_codiscrete` | ACCEPT. One-stroke engine (Order.lean:682, `[ConnectedSpace 𝕜]`); witness ξ(0) = 1/2 ≠ 0 kernel-checked; simpler than the ζ precedent. |
| N2-D2/D3 | `isClosed_…` / `isDiscrete_riemannXi_zeroSet` | ACCEPT. Verbatim ζ idiom (ZetaZeros.lean:57–61) with the ξ engine. |
| N2-D4 | `IsCompact.inter_riemannXi_zeroSet_finite` | ACCEPT. Arbitrary-compact quantifier shape, the neutrality carrier; proof shape verbatim ZetaZeros.lean:65–67. |
| N2-D5 | `countable_riemannXi_zeroSet` | ACCEPT. Beyond the ζ precedent, named by DEFERRED-2; countability produces no listing; shape-free fallback recorded. |
| N2-D6 | `tendsto_riemannXi_zeroSet_cofinite_cocompact` | ACCEPT (optional). Filter form of D4; compact stays universally quantified (DiscreteSubset.lean:148). |
| N2-D7 | discrete/closed divisor support (2 sigs) | ACCEPT. Carrier facts, honestly labeled; Divisor.lean:39 total with junk 0, so arbitrary `U` is sound. |
| N1.1 = N2-D8 | `riemannXi_divisor_inter_support_finite` | ACCEPT. The multiplicity-aware statement; both routes (M9+M10 univ-comparison primary; D4+M13 alternative) consume only built, kernel-checked M-package theorems; the false generic form correctly refused (death condition 6). |
| N2-D9 | `countable_riemannXi_divisor_support` | ACCEPT. The one statement genuinely pinned to the M13 seam; forward `rw` orientation confirmed against built `Mult.lean:538`. |
| N1.2 | `riemannXi_divisor_finsum_mem_eq_sum` | ACCEPT. Well-definedness bridge; embedded proof term sound by proof irrelevance of `Set.Finite`; S1N1-SUM risk honestly registered with real fallbacks. |
| N1.3/N1.4 | finsum nonneg / `toNat` cast identity (2 sigs) | ACCEPT. M11 effectivity through `le_def` (LocallyFinsupp.lean:404); N1.4 is a cast identity, not a counting object (N-DEFERRED-2). |
| N1.5 | `riemannXi_divisor_finsum_mem_mono` | ACCEPT. `K₂`-only compactness asymmetry correct; no junk caveat arises. |
| N1.6 | reflection comp + image forms (2 sigs) | ACCEPT. `hU` verbatim built M14 (`Mult.lean:573`); unconditional in `K`. |
| N1.7 | conj comp + image forms (2 sigs) | ACCEPT. `hU` verbatim built M15 (`Mult.lean:634`); S1N1-7b corrected (Fix 5). |
| N1.8 | composite comp + image forms (2 sigs) | ACCEPT. Both `hU₁`, `hU₂` required, order verbatim built `Mult.lean:670`; involution chain sound. |
| N1.9 | three symmetric-window set identities (3 sigs) | ACCEPT. `[GEN]`/`[PIN]`, fully pinned; the only statements where `K`-symmetry does work; the refusal to state a redundant symmetric-`K` sum variant with an unused `hK` is sound. |

## Notes not conditioning acceptance (recorded so they are not lost)

- The RH-010 queue-block locator drift (`:616` → status now at `:626`,
  RH-011 at `:760`) is subsumed by Fix 1.
- Annex N §C Front 5's "ACTIVE, in flight" sentences are the frozen
  design-time record of what that review verified at its own date and are
  deliberately left unedited.
- The eta/coercion seams (S1N1-1a/2, N2-f) remain correctly pre-registered
  as stage-two elaboration risks with real fallbacks at the pin; N2-f's
  package-wide spelling decision is now pre-resolved in favor of the
  coercion form by the built M13 (Fix 2 supersession note).
- S1N1-SUM (generated additive finsum names) remains the most likely single
  CI bounce for stage two; probe with `#check` in the promotion PR.

## Gate result and limits

Stage-one acceptance of the 23-signature zero-set / compact-divisor-sum
statement surface is complete: **ACCEPT WITH APPLIED EDITORIAL FIXES** —
five consolidated fixes applied, all prose/status-only, zero blocking
items, zero statement changes.

Stated plainly, the limits of this record:

- **No kernel verdict.** No Lean toolchain was run; nothing here is
  Lean-checked. Under the one invariant, only the Lean kernel via CI can
  verify these statements, and that judgment has not occurred.
- **No barrier-row change.** `S1-GLOBAL-ZEROS` remains **OPEN**; all routes
  remain **PARKED**; no capability-map row is closed, weakened, or
  re-scoped by this acceptance. A future built promotion may record only
  that the neutral slice is machine-checked, with the barrier still open.
- **No promotion.** Nothing was promoted, imported into the build, or
  scheduled for promotion. A stage-two built promotion of exactly this
  surface (a `ZeroSet.lean` module importing the built Mult module, judged
  solely by CI) is a separate, later change requiring its own dated
  decision; queue flips are the orchestrator's, not this panel's.
- **No claim about RH.** This record provides no evidence for or against
  the Riemann Hypothesis.
