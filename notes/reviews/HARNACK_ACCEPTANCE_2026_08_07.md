# Harnack disc contract acceptance record

Date: 2026-08-07

Status: FINAL — stage-one acceptance of the `HARNACK_CONTRACT.md` statement
surface (H1–H5) under owner-delegated review authority. This is a pool-item
acceptance, not a queue task: the reviewed contract is an offered artifact
against `UPSTREAM_POOL.md` §5 (Harnack inequality) and occupies no ACTIVE
slot.

## Reviewed baseline

- repository HEAD `3201153651e9a5c6a4b4491a807f6cda57417933` (clean tree at
  review time);
- reviewed object `domains/riemann-hypothesis/HARNACK_CONTRACT.md`
  (692 lines pre-fix, SHA-256
  `80250320aaa78ce5aeec27e4370c488d347a342b1d89cb67b23060264b518e7c`, Git
  blob `499c2580dc15a8806b96837d617ca747bac04b59`; introduced at commit
  `3783f31`, PR #314); post-editorial-fix state (758 lines) SHA-256
  `e82866a081f55250a96ae2f5ae12e9b7c466e8880d7b6b030eb16121e24fc67d`
  (Git blob `4b1872e1a8f2cd5ad212e5505100caa65f0e4c1f`);
- pinned Mathlib revision `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`
  (v4.31.0), re-verified by `git rev-parse HEAD` at
  `/workspace/leanprover-community/mathlib4` during this review by both
  lenses and again at consolidation;
- drafts-lane context: `domains/riemann-hypothesis/drafts/HarnackDisc.lean`
  (listed at `drafts/README.md:32`, reviewed 2026-08-07,
  `LIKELY_ELABORATES`) implements exactly this surface; it is outside every
  lake target (`lakefile.toml:2`, `defaultTargets = ["Ecdlp",
  "ResearchOS"]`, verified verbatim) and received no kernel verdict here.

No Lean toolchain was run. Every check below is source reading; nothing in
this record is a kernel verdict.

Form precedent: `notes/reviews/RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`.

## Authority and effect

This panel acted under **owner-delegated review authority**. The reviewed
contract is **not** an RH-queue task: at the reviewed baseline the queue's
sole ACTIVE task is `RH-012` (`tasks/RIEMANN_HYPOTHESIS.md:809–:824`), which
this contract does not occupy, and no route execution is authorized. The
two-stage gate of `MULTIPLICITY_CONTRACT.md` §Two-stage gate and promotion
ordering applies verbatim (adopted by reference in the contract's final
section, checked against the source at `:2092`). Acceptance under this
record:

- covers the **statement surface only** of the Harnack disc package —
  **H1–H5, exactly 5 public signatures, zero `def`s**, independently
  retallied by both lenses: H1 `poissonKernel_mem_Icc`, H2
  `continuousOn_poissonKernel`, H3 `InnerProductSpace.HarmonicOnNhd.harnack`,
  H4 `…harnack_half`, H5 `…pos_of_pos_center`; no signature is mandated in
  prose only;
- carries **no kernel verdict** — no Lean toolchain was run, and only the
  Lean kernel via CI can ever supply one; a green CI run on an acceptance PR
  is evidence of nothing about the draft, which sits outside every lake
  target;
- **changes no barrier row** — no row of `MATHLIB_CAPABILITY_MAP.md` names
  Harnack as exit evidence (zero Harnack hits in the map, verified), and
  none is closed, weakened, or re-scoped here;
- **promotes nothing** — a stage-two built change (or the third disposition,
  an upstream Mathlib PR, which remains a separate maintainer decision) is
  not scheduled by this record;
- selects no route and provides no evidence for or against the Riemann
  Hypothesis.

## Panel composition

Two independent lenses, each reading the contract in full against the
pinned Mathlib checkout and the repository at the reviewed baseline:

1. **Truth-pin lens** (mathematical truth + pin fidelity) — re-derived all
   five statements at every point of their stated domains, re-opened ~40
   load-bearing `file:line` locators at the pin including statement shapes,
   re-ran the collision greps, and audited the junk-value and hypothesis
   honesty of the H3 comparison chain.
2. **Boundary lens** (claim boundary and scope) — audited the lane
   authority, claim boundary, death conditions, deferred items, two-stage
   gate adoption, pool-signature delta declaration, and name freshness
   (including a repo-side scan beyond the contract's pin-only scan).

## Decision: **ACCEPT WITH APPLIED EDITORIAL FIXES**

All five statements are mathematically true as stated; **no declaration
name, binder, hypothesis, conclusion, or proof skeleton changed**. Zero
blocking items. The applied fixes fall in three classes: (i) a dangling
in-document reference (the cited Annex A did not exist and was appended);
(ii) staleness-of-status prose — the contract was drafted while `RH-010`
was ACTIVE, and both `RH-010` and `RH-011` completed before this acceptance
ran; (iii) three small locator/naming residues.

## Per-lens verdicts

| Lens | Verdict | Blocking defects | Editorial fixes |
|---|---|---|---|
| Truth-pin | **ACCEPT WITH EDITORIAL FIXES** | none | 3 required (D1 Annex A, D2 queue, D3 locator residue) + 2 optional (D4 working name, D5 crossed pairing) |
| Boundary | **ACCEPT WITH REQUIRED EDITORIAL FIXES** | none | 3 required (D1 queue, D2 working name, D3 Annex A) + 1 optional (D4 repo-side scan note) |

No lens returned BLOCK or REJECT. **Blocking items: none.**

One classification divergence was resolved at consolidation: the truth-pin
lens classed the `drafts/Harnack.lean` → `drafts/HarnackDisc.lean`
working-name drift as optional, the boundary lens as required. The
consolidator applied it (Fix 4): the draft implementing exactly this
surface is committed under the realized name, both lenses verified the
two-stage-gate consequence is unaffected either way, and a resolvable name
is strictly better. No factual conflict arose between the lenses; all
overlapping checks (pin hash, signature tally, root-level mean-value trap,
`hR`-drop soundness, death-condition-5 wording) agreed.

## Applied editorial fixes

All six consolidated fixes were applied to
`domains/riemann-hypothesis/HARNACK_CONTRACT.md` during this acceptance
session; the post-fix baseline hashes above are of the fixed file. None
touches a signature.

**Fix 1 — Annex A appended (truth-pin D1 = boundary D3).** Ten in-text
citations ("Annex A, finding A2…A7") referenced an annex that existed
nowhere — not in the file, never in its git history, and in no committed
review record (repo-wide grep: zero hits). A new
`## Annex A — pre-acceptance adversarial audit findings (2026-08-07…)`
section now closes the file, recording the six already-applied corrections
under their original numbering: A2 (root-level
`_root_.HarmonicOnNhd.circleAverage_eq` — `MeanValue.lean` has no
`namespace` command), A3 (RH-002 → RH-010 queue correction, noted as
further superseded at acceptance), A4 (death condition 5: H4 without `hR`
is true but unprovable by the recorded skeleton), A5 (`Normed/Group`
locators `:869`/`:877`, attrs `:868`/`:876`), A6 (the in-tree private proof
uses plain `fun_prop`, no `disch`), A7 (`div_le_iff₀` at
`GroupWithZero/Basic.lean:1138`). Every citation now resolves in-file,
matching house convention (`MULTIPLICITY_CONTRACT.md` embeds its annexes;
the zero-set slice contract carries Annex N/D in-file).

**Fix 2 — Queue position (truth-pin D2 = boundary D1; two sites).** The
lane-authority header and the Claim boundary both said the sole ACTIVE task
is `RH-010`; superseded twice since drafting. Both sites now record: the
sole ACTIVE task is `RH-012` (zero-set slice drafting plus kernel
promotion, `tasks/RIEMANN_HYPOTHESIS.md:809–:824`); `RH-010` and `RH-011`
completed 2026-08-07 (merged PR #313 `2a20629`; acceptance record
`notes/reviews/RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`). The bracketed
Annex-A3 correction note now records its own supersession. Kept unchanged,
verbatim: "No route execution is authorized" and "this contract does not
occupy it" — both remain true and load-bearing.

**Fix 3 — H4 dependency-block locator residue (truth-pin D3).** The one
uncorrected residue of finding A5: H4's pinned-dependencies block still
read `Analysis/Normed/Group/Basic.lean:875/:868` for
`mem_closedBall_iff_norm` / `mem_ball_iff_norm`, contradicting the
contract's own §0b correction and its dependency table, and wrong at the
pin (nothing relevant at `:875`). Now `:877/:869 (attrs :876/:868)` —
re-verified at source during consolidation: `@[to_additive
mem_ball_iff_norm]` at `:868` generating at `:869`, `@[to_additive
mem_closedBall_iff_norm]` at `:876` generating at `:877`.

**Fix 4 — Working name realized (boundary D2 = truth-pin D4).** Both
mentions of `drafts/Harnack.lean` (two-stage-gate paragraph and the
Working-name line) now read `drafts/HarnackDisc.lean` with a dated
realized-at-acceptance note; the committed draft at that path implements
exactly this surface (`drafts/README.md:32`; five theorem heads
spot-verified identical to H1–H5 by the truth-pin lens). The
outside-every-lake-target consequence is unaffected.

**Fix 5 — H2 crossed pairing (truth-pin D5, optional, applied).** The H2
dependency note paired `mem_ball_iff_norm` / `mem_sphere_iff_norm` with
`Harmonic/Poisson.lean:65` and `Poisson.lean:108` in the wrong order
(collectively true, pairwise swapped). Now explicit and correct:
`mem_sphere_iff_norm` at `Harmonic/Poisson.lean:65`, `mem_ball_iff_norm` at
`Poisson.lean:108` — both use sites re-read at the pin during
consolidation.

**Fix 6 — Repo-side collision scan recorded (boundary D4, optional,
applied).** §0b's collision-scan paragraph, previously pin-only, now also
records the boundary lens's repo-side result per the RH011 precedent: zero
hits for `harnack` (any casing) and for each of the five proposed names
across `ResearchOS/`, `Ecdlp/`, the root modules, and the drafts lane —
except `drafts/HarnackDisc.lean`, the surface's own draft, not a collision.

## Review basis (spot summary of the panel's independent checks)

1. **Pin fidelity.** ~40 load-bearing locators re-opened at the pin across
   `Complex/Poisson.lean` (:24 section variable, :39, :54, :57, :60 private
   aux, :73 function-level bridge, :87/:118, :101/:134 expanded-quotient
   bounds with hypothesis order `(hz) (hw)`, :108, :245/:255),
   `Harmonic/Poisson.lean` (:8–9, :25–26, :28, :30–35 private + plain
   `fun_prop`, :44–67, :91 `closedBall c R` not `|R|`, :102),
   `Harmonic/Analytic.lean:70`, `InnerProductSpace/Harmonic/Basic.lean`
   (:27/:39/:46/:51), `CircleAverage.lean` (:42–:382 `namespace Real`, :54,
   :63, :271 both integrability args mandatory + `sphere c |R|` +
   `@[gcongr]`, :318, :331 with instance block :36–:40, :339),
   `CircleIntegral.lean` (:176, :233, :237, :247 `sphere c |R|`,
   :333/:337), `Pseudo/Defs.lean` (:376/:460/:480),
   `Normed/Group/Basic.lean` (:869/:877, attrs :868/:876),
   `Abs.lean:93`, `ContDiff/Defs.lean:551`, `GroupWithZero/Basic.lean`
   (:1430 and :1138): **one stale locator** (Fix 3), all others exact,
   verbatim, statement shapes included.
2. **The root-level mean-value trap: real and correctly handled.**
   `Harmonic/MeanValue.lean` has zero `namespace` commands and no harmonic
   file has an `export`, so `:27` declares
   `_root_.HarmonicOnNhd.circleAverage_eq` (hypothesis on
   `closedBall c |R|`, verbatim); dot notation on an
   `InnerProductSpace.HarmonicOnNhd` term cannot resolve it, and the H3
   skeleton's bare-name call is the correct spelling. Cross-evidence:
   `JensenFormula.lean:268` and `PosLogEqCircleAverage.lean:58/:162` use
   the bare name and neither file opens `InnerProductSpace`.
3. **Mathematical truth.** All five statements re-derived. H1–H2: the
   denominator is nonvanishing on the sphere since `‖z − c‖ = R > ‖w − c‖`.
   H3: the calc chain is sound with junk-value honesty intact —
   `Real.circleAverage` is total with junk value 0
   (`circleAverage.integral_undef`, `CircleAverage.lean:63`, verified at
   source), and both `CircleIntegrable` hypotheses are carried through
   `circleAverage_mono`. H4: `r ≤ R/2 ⟺` the factor-3 bounds; death
   condition 5's corrected wording re-derived independently by both lenses
   (H4 without `hR` is true — `R = 0` forces `w = c`, `h₀` closes both
   halves; `R < 0` vacuous — but unprovable by the recorded skeleton whose
   `hw'`/`hc` steps consume `0 < R`). H5 immediate from H3's lower half.
   The `hR`-drop in H3 vs the pool signature (`UPSTREAM_POOL.md:490–497`,
   pool carries `hR : 0 < R`, verified) is sound and honestly declared:
   `Metric.pos_of_mem_ball` (`Pseudo/Defs.lean:376`, verbatim) recovers it.
4. **Claim boundary.** No ζ/ξ/zeros token in any signature (retallied:
   exactly 5 theorems, zero `def`s). `MATHLIB_CAPABILITY_MAP.md` has zero
   Harnack hits, so "no row names Harnack as exit evidence" is exact.
   Sharpness is nowhere claimed as a theorem, and the boundary forbids
   adding one without a new contract. Closed-ball hypothesis honesty
   confirmed: both `hf` and `h₀` on the closed ball are consumed
   (representation and mean value need it).
5. **Death conditions.** All 7 well-formed. DC3 correctly forecloses the
   junk-average escape and matches the junk-value bullet; DC6 faithfully
   adopts `MULTIPLICITY_CONTRACT.md` death condition 9 (`:1905`, "never
   retires a row" — text matches); DC5's mathematics verified (item 3
   above).
6. **Name freshness.** Zero hits for `harnack` (any casing) in pinned
   `Mathlib/`; zero hits for each of the five proposed names at the pin and
   in the repository trees; the only repo occurrences are the surface's own
   draft (now recorded in §0b, Fix 6).
7. **Two-stage gate.** `MULTIPLICITY_CONTRACT.md` §Two-stage gate and
   promotion ordering exists (`:2092`) and its stage-one products ("no
   built module, no ledger row, no kernel verdict"; "an acceptance PR must
   not carry a promotion") match the contract's adoption verbatim; the
   third disposition (upstream Mathlib PR) is correctly reserved as a
   separate maintainer decision.

## Statement disposition

| Block | Declaration (5 signatures) | Disposition |
|---|---|---|
| H1 | `poissonKernel_mem_Icc` | ACCEPT. Packages the pinned expanded-quotient bounds (`Poisson.lean:101/:134`) on `poissonKernel` once, via the function-level bridge `:73` + `:39`; syntactic seam registered as H-1a with two fallbacks; private aux `:60` correctly not consumed. |
| H2 | `continuousOn_poissonKernel` | ACCEPT. Honest re-proof forced by the `private` in-tree analogue (`Harmonic/Poisson.lean:30–35`); H-2a (MEDIUM) is the package's largest obligation, with three recorded routes and death condition 3 behind them. |
| H3 | `InnerProductSpace.HarmonicOnNhd.harnack` | ACCEPT. The deliverable: sharp classical constants, no sharpness claim as a statement; every prerequisite pinned, including the Poisson representation (`Harmonic/Poisson.lean:91`) — the pool's "hardest step" is interior to that pinned proof; junk-value honesty carried through both `circleAverage_mono` steps; `hR` drop vs pool signature sound (`pos_of_mem_ball`). |
| H4 | `…harnack_half` | ACCEPT. Factor-3 half-radius corollary; `hR : 0 < R` correctly retained (closed-ball membership does not force it); arithmetic re-derived; dependency-block locator residue fixed at acceptance (Fix 3). |
| H5 | `…pos_of_pos_center` | ACCEPT. Two-line positivity propagation from H3's lower half; no independent obligations. |

The three deferrals (DEFERRED-H1 `HarmonicContOnCl` variant, DEFERRED-H2
Harnack chain on compacts, DEFERRED-H3 vanishing propagation) are correctly
out of surface, each with the reason recorded.

## Notes not conditioning acceptance (recorded so they are not lost)

- H-2a (kernel continuity re-proof, `fun_prop` discharge) remains the most
  likely single CI bounce for any stage-two elaboration; the Annex A6 note
  (try the in-tree private proof's plain-`fun_prop` shape first) is the
  right first move.
- H-3a (Pi-smul unfoldings, four sites) is the most likely CI-cycle burner;
  the defeq `show`/`exact` fallback is recorded.
- The drafts-lane file `HarnackDisc.lean` carries a prior
  `LIKELY_ELABORATES` review (`drafts/README.md:32`); that verdict is not
  strengthened by this record, and its kernel verdict awaits a separate
  change.
- §0a item 5's redundancy claim (pool's `hR` forced by `w ∈ ball c R`) was
  independently confirmed; the pool note itself (`UPSTREAM_POOL.md:482–549`)
  is now partially superseded in the package's favor per §0a item 2, which
  this panel verified at source.

## Gate result and limits

Stage-one acceptance of the 5-signature Harnack disc statement surface is
complete: **ACCEPT WITH APPLIED EDITORIAL FIXES** — six consolidated fixes
applied, all prose/status/locator-only, zero blocking items, zero statement
changes.

Stated plainly, the limits of this record:

- **No kernel verdict.** No Lean toolchain was run; nothing here is
  Lean-checked. Under the one invariant, only the Lean kernel via CI can
  verify these statements, and that judgment has not occurred.
- **No barrier-row change.** No `MATHLIB_CAPABILITY_MAP.md` row is closed,
  weakened, or re-scoped; no row names Harnack as exit evidence, and
  generic pinned machinery never retires a row regardless (death
  condition 6).
- **No promotion.** Nothing was promoted, imported into the build, or
  scheduled. A stage-two built change — or an upstream Mathlib PR, the
  package's natural eventual home — is a separate, later decision this
  record does not make; queue flips are the orchestrator's, not this
  panel's.
- **No queue edit.** `tasks/RIEMANN_HYPOTHESIS.md` was not modified;
  `RH-012` remains the sole ACTIVE task and this contract does not occupy
  it.
- **No claim about RH.** This record provides no evidence for or against
  the Riemann Hypothesis.
