# Three-circles contract acceptance record (upstream pool item 3)

Date: 2026-08-07

Status: FINAL — the consolidated editorial fixes below were applied in place
and landed on `main` in the in-flight panel-edit commits (`f385247`,
`59d5220`); this record is the verdict those commits' message deferred to.

## Reviewed baseline

- repository `main` at review start `3201153` (post-PR #315 `9129e8c`, which
  merged the RH-011 acceptance, activated `RH-012`, and introduced
  `domains/riemann-hypothesis/drafts/ThreeCircles.lean`);
- reviewed object `domains/riemann-hypothesis/THREE_CIRCLES_CONTRACT.md`
  (pre-fix 1,258 lines, SHA-256
  `3c30a352aab4c84de76c6b8d75f710dae43565460dbce7b5777778e23de5c765`, Git
  blob `fe0d80b235fbe1cfa1e038340aed1a276ee8a83f`); post-editorial-fix state
  (1,274 lines) SHA-256
  `b3f94a99d6a5e30415e8b83a08c9c2414a2a06f656e14689b8f261edbb247d52` (Git
  blob `0fa21b9fd9e1a3150da4526aded33aa74c382c8f`);
- pinned Mathlib revision `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`
  (v4.31.0, toolchain `leanprover/lean4:v4.31.0`), re-verified by
  `git rev-parse HEAD` at `/workspace/leanprover-community/mathlib4`
  independently by each lens and again by the consolidator;
- queue authority `tasks/RIEMANN_HYPOTHESIS.md` (dated 2026-08-07 decision:
  `RH-011` complete, `RH-012` sole ACTIVE);
- format precedent `notes/reviews/RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`.

No Lean toolchain was run. Every check below is source reading; nothing in
this record is a kernel verdict.

## Authority and effect

This panel acted under **owner-delegated review authority**. Unlike the
RH-011 record, this acceptance is **not** a queue task: the contract is an
*offered artifact* under `UPSTREAM_POOL.md` §3, and the RH queue's sole
ACTIVE task remains `RH-012` (zero-set slice drafting plus separate kernel
promotion) throughout — this acceptance neither occupies nor moves the
ACTIVE slot. The two-stage gate of `MULTIPLICITY_CONTRACT.md` §Two-stage
gate applies verbatim. Acceptance under this record:

- covers the **statement surface only** of the Hadamard three-circles
  package (TC1–TC11, exactly 11 public Lean signatures: 1 `def` +
  10 theorems), each spelled in a `lean` block of the contract's §2;
- carries **no kernel verdict** — no Lean toolchain was run, and only the
  Lean kernel via CI can ever supply one;
- **changes no barrier row** — `MATHLIB_CAPABILITY_MAP.md` contains no
  three-circles/annulus row (re-verified by the boundary lens); generic
  pinned machinery never retires a row (the MULTIPLICITY finding-A4 rule);
- **promotes nothing** — the existing drafts-lane file
  `drafts/ThreeCircles.lean` is outside every lake target and was **not
  judged** by this review beyond the name-collision observation (Fix 3); a
  stage-two built promotion, judged solely by CI, is a separate later change
  that no dated decision has scheduled;
- selects no route and provides no evidence for or against the Riemann
  Hypothesis.

## Panel composition

Two independent lenses, each reading the contract in full against the pinned
Mathlib checkout, plus a consolidator applying the merged fixes:

1. **Truth-and-pin lens** — re-derived all 11 statements (exp-transport
   truth including the `2πI`-periodicity bookkeeping, degenerate radii
   `r₂ = r₁` / `r₂ = r₃`, the load-bearing `0 < r₁`, TC2's `r < 0` junk
   case, TC11's endpoint `t` values), batch-re-verified all ~56 `file:line`
   locators verbatim at the pin, and independently reproduced Annex A's
   import-closure BFS (exactly 2,484 modules from the seven preamble
   imports) and the collision scans.
2. **Boundary-and-gates lens** — independently re-verified the pin and the
   load-bearing Hadamard.lean/Arg.lean/Trigonometric.lean quotations,
   re-derived the exponent transport (`:607` at `l := log r₁`,
   `u := log r₃`, `z.re := log r₂` yields TC8's RHS literally), and audited
   the claim boundary (all five NOT-bullets), the eight death conditions,
   name freshness for all 11 declarations, the two-stage gate
   (`lakefile.toml:2` quote exact), and the charged def-gate question.

## Special scrutiny: the one `def` (TC1 `sSupNormCircle`)

Definitions are design-bearing, so TC1 was charged for separate scrutiny.
Both lenses converged: **ACCEPT, and no entire-order-style standalone def
gate is warranted.** Grounds (recorded in the contract, death condition 4,
by Fix 6):

- **Copied, not invented.** The bare-`sSup` junk-0 convention is verbatim
  the pinned `sSupNormIm` (Hadamard.lean:77, re-read by both lenses);
  center fixed at `(0 : ℂ)` matches both the classical statement and the
  pinned convention. No second def, no smuggled data.
- **Quarantined.** `sSupNormCircle` appears in the signatures of only
  TC1/TC2/TC4/TC9; the workhorse TC8 and both corollaries TC10/TC11 are
  def-free (`‖w‖ = r` binders), so a wrong def cannot poison the
  load-bearing statements. Junk cases are consistently discharged
  downstream (TC2 covers the empty sphere; TC9 guards the RHS through
  `Real.sSup_le`'s `0 ≤ a` argument; TC4 supplies `BddAbove` through TC3).
- **Ceded to upstream.** TC-DEFERRED-1 and the claim boundary already
  reserve the eventual spelling to a Mathlib review; repo-wide grep shows
  zero consumers outside the contract and its own draft.

This distinguishes `ENTIRE_ORDER_CONTRACT.md`'s `growthOrder` (a novel
object with no pin-side notion, about which a whole lane's future theorems
will be stated) on all three axes; death condition 4's one-def budget plus
the standard two-stage gate suffice here.

## Decision: **ACCEPT WITH APPLIED EDITORIAL FIXES**

All 11 signatures are mathematically true as stated at the pin; **no
declaration name, binder, hypothesis, conclusion, or proof skeleton
changed**. Zero blocking items from either lens. Both lenses independently
returned ACCEPT WITH EDITORIAL FIXES; their defect lists overlapped on the
authority-staleness and scan-staleness items and were merged into the six
consolidated fixes below.

| Lens | Verdict | Blocking defects | Editorial fixes |
|---|---|---|---|
| Truth and pin | **ACCEPT WITH EDITORIAL FIXES** | none | 4 (its D1–D4 map onto Fixes 1, 3, 4, 5) |
| Boundary and gates | **ACCEPT WITH EDITORIAL FIXES** | none | 4 (its D1–D4 map onto Fixes 1, 2, 3, 6) |

No inter-lens conflict arose; the one consolidator-verified datum beyond the
lens reports is the `Complex.ofReal_im` locator (Fix 4), re-read at the pin:
Data/Complex/Basic.lean:92, `@[simp, norm_cast]`, as recorded.

## Applied editorial fixes

All six consolidated fixes were applied to
`domains/riemann-hypothesis/THREE_CIRCLES_CONTRACT.md` (plus one collateral
comment fix in `drafts/ThreeCircles.lean`) during this acceptance session;
the post-fix baseline hashes above are of the fixed file. None touches a
signature. Annex A's frozen dated findings (B1–B2 text) are left unedited,
per the RH-011 precedent; the one annex edit (Fix 2's count correction in
front 6) corrects that front's own tally to what both scans actually
covered.

**Fix 1 — Authority staleness (both lenses, MEDIUM; the same defect class
as the contract's own Annex A finding B2, now one queue step further).**
Three sites — Authority and standing, Claim boundary route bullet, death
condition 8 — no longer name `RH-011` as the RH queue's sole ACTIVE task;
they now record the dated 2026-08-07 queue decision: `RH-011` **complete**
(23-signature slice surface accepted, record
`RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`) and the single ACTIVE slot
moved to `RH-012` (zero-set slice drafting plus separate kernel promotion;
CI the sole judge). Standing unchanged: the contract remains an offered
artifact either way. Collateral: the same stale sentence in the
`drafts/ThreeCircles.lean` header comment (outside this acceptance's
object) was fixed opportunistically.

**Fix 2 — Scan-list completeness (boundary lens, LOW).** The name-collision
scan list enumerated 10 names for an 11-signature surface, omitting TC10's
`norm_le_interp_of_norm_eq'`; the name is now listed, and Annex A front 6
reads "all eleven proposed names". The result was already implied by
substring coverage via TC8's unprimed name, and the boundary lens
independently re-grepped **0 hits** in pinned `Mathlib/` for all eleven
names including the primed one and the def.

**Fix 3 — Scan staleness (both lenses, LOW, benign).** The repo-wide
"exactly one textual hit (`UPSTREAM_POOL.md:371`)" claim predated PR #315,
which merged `drafts/ThreeCircles.lean` — the drafts-lane implementation of
this very surface, carrying all eleven names. A dated staleness note now
records these as self-hits of the surface under review (non-built, outside
every lake target, no kernel verdict) with foreign collisions still zero in
pinned `Mathlib/` and the repo.

**Fix 4 — TC7 dependency completeness (truth-and-pin lens, LOW).** TC7's
skeleton simp set uses `Complex.ofReal_im`, which was absent from TC7's
pinned-dependencies block and the pinned API table. Added to both with the
consolidator-verified locator Data/Complex/Basic.lean:92.

**Fix 5 — Sphere-scope wording (truth-and-pin lens, LOW).** The notation
paragraph claimed `Metric.sphere (0 : ℂ) r` "appears only inside the helper
block TC1–TC4", but the TC9 and TC11 *proof skeletons* use
`Metric.sphere` / `NormedSpace.sphere_nonempty` internally (statements are
clean). Reworded to: appears in no theorem *statement* outside the helper
block TC1–TC4 (proof-internal uses in the TC9/TC11 skeletons are expected).

**Fix 6 — Def-gate determination recorded (boundary lens, non-blocking).**
Death condition 4 now closes the precedent question explicitly: unlike
`ENTIRE_ORDER_CONTRACT.md`'s `growthOrder`, TC1's `sSupNormCircle` carries
no standalone design-bearing acceptance gate — its convention is the pinned
`sSupNormIm`'s verbatim, the def-free TC8/TC10/TC11 do not depend on it, no
repo module may state theorems about it except through this accepted
surface, and an upstream re-spelling supersedes it (TC-DEFERRED-1).

## Review basis (spot summary of the panel's independent checks)

1. **Exp-transport truth, periodicity included.** The consumed input is the
   endpoint-bound `:607` form only (boundary hypotheses pointwise over the
   entire line; `hB` boundedness, not a sup value); the `sSupNormIm` form
   `:588` is reference-only and consumed nowhere. The line→circle discharge
   (`norm_exp` :995 + `exp_log` :58 at every one of the infinitely many
   period-translates) is sound with no sup identification across `exp`;
   surjectivity is used at exactly one point via TC7's total-`arg` witness
   (`norm_mul_exp_arg_mul_I`, Arg.lean:56, stated for all `x`, no branch of
   `log` anywhere). Instantiating `:607` at `l := log r₁`, `u := log r₃`,
   evaluation point with real part `log r₂` yields literally TC8's
   exponents (re-derived independently by both lenses); TC10's ratio
   algebra needs exactly `hne`; TC11's `(1−t)+t = 1 ≠ 0` holds for all `t`
   including endpoints, and `sub_add_cancel` exists at the pin as the
   `@[to_additive (attr := simp)]` twin of `div_mul_cancel`
   (Group/Defs.lean:1253).
2. **Degenerate and junk cases.** `r₂ = r₁` / `r₂ = r₃` land on the
   closed-strip boundary, which `:607`'s `hz` admits; the `M₁^1 * M₃^0`
   degeneration is as stated; `r₁ < r₃` genuinely forced by `hul`;
   `0 < r₁` load-bearing (`log_zero` junk verified at Log/Basic.lean:102 —
   death condition 5 is real, not decoration); TC2's `r < 0` empty-sphere
   case honest and hypothesis-free; TC11's `0 ≤ M` derivation via
   `NormedSpace.sphere_nonempty` (RCLike/Real.lean:128) valid.
3. **Pin fidelity: zero incorrect locators.** All ~56 locators re-opened at
   the pin, with verbatim shape checks on every load-bearing statement,
   including the B1-corrected `log_le_log` :150, the two-namespace prime
   trap (`:66`/`:67`; primed name at `:607`, unprimed absent),
   `IsCompact.bddAbove_image` :332 with `[ClosedIciTopology α] [Nonempty α]`
   verbatim, `Real.sSup_le` :228 `protected`, `image_comp` orientation
   :224, `DiffContOnCl` :33 with both fields `protected` (anonymous
   constructor forced, as the skeleton has it), and all namespace-line
   claims. Annex A's front 5 was independently reproduced: the
   public-import-closure BFS from the seven preamble imports gives exactly
   2,484 modules containing every cited module.
4. **Claim boundary and death conditions.** All five NOT-bullets verified,
   including the capability-map absence of any three-circles/annulus row
   ("closes no barrier" holds at both stages). The eight death conditions
   are sound and complete; the `r₁ = 0` and log-branch conditions are real
   failure modes, not decoration. The two-stage gate is present and
   verbatim-consistent with the MULTIPLICITY discipline
   (`lakefile.toml:2`, `defaultTargets = ["Ecdlp", "ResearchOS"]`, exact).
5. **Annulus honesty.** Reproduced at the pin: zero `def annulus|Annulus`
   hits under `Mathlib/`, zero case-insensitive "annulus" hits in
   `Hadamard.lean`; the inline set-builders denote the honest closed/open
   annuli about 0, and the TC8 compactness argument
   (`isCompact_closedBall` + `IsCompact.of_isClosed_subset` + two
   `isClosed_le`) is correct for the set-builder form.

## Statement disposition

| Block | Declaration surface (11 signatures) | Disposition |
|---|---|---|
| TC1 | `sSupNormCircle` (the one `def`) | ACCEPT under special scrutiny (see the dedicated section): convention copied verbatim from pinned `sSupNormIm`; quarantined; upstream-superseded. |
| TC2 | `sSupNormCircle_nonneg` | ACCEPT. Mirror of pinned `sSupNormIm_nonneg`; junk `r < 0` case included honestly, no side condition. |
| TC3 | `bddAbove_image_norm_sphere` | ACCEPT. Compact sphere + `bddAbove_image`; instance chain (`ProperSpace ℂ`) verified. |
| TC4 | `le_sSupNormCircle` | ACCEPT. `le_csSup` against TC3; TC-SPH bridge recorded. |
| TC5/TC6 | `exp_mem_annulus_of_mem_verticalClosedStrip` / `…_verticalStrip` | ACCEPT. `MapsTo` legs, closed and open; `norm_exp` + `exp_log` monotone chains. |
| TC7 | `exists_exp_eq_of_norm_eq` | ACCEPT. The surjectivity leg: explicit total-`arg` witness, no branch of `log`; dependency block completed by Fix 4. |
| TC8 | `norm_le_interp_of_norm_eq` | ACCEPT. The workhorse exp-transport of pinned `:607`; raw strip exponents literal, zero log-algebra; TC-BB honestly registered HIGH (syntactic stacking, not mathematical content). |
| TC9 | `sSupNormCircle_le_interp` | ACCEPT. The log-convexity headline in three-point inequality form, matching the pin's own presentational choice; junk-safe via `Real.sSup_le`'s `0 ≤ a`. |
| TC10 | `norm_le_interp_of_norm_eq'` | ACCEPT. Classical ratio-exponent corollary; all log-algebra quarantined here; exponent shapes match `UPSTREAM_POOL.md` §3.1. |
| TC11 | `norm_le_of_mem_annulus` | ACCEPT. Two-boundary maximum principle; `0 ≤ M` derived, not assumed; `rpow_add'` side condition valid at all `t`. |

## Notes not conditioning acceptance (recorded so they are not lost)

- TC-BB (the `hB` transport through the compact annulus, registered HIGH)
  remains the most likely single stage-two friction point; its two recorded
  fallbacks stand, and the "bound on the strip directly" route stays
  pre-rejected (death condition 7).
- `drafts/ThreeCircles.lean` was not judged by this review beyond the
  collision observation in Fix 3; whether its bodies elaborate is CI's
  question in a stage-two promotion, which no dated decision has scheduled.
- The truth-and-pin lens's line tally of the reviewed object (1,259) versus
  the measured 1,258 is a counting-convention artifact (trailing newline);
  the content hashes above are authoritative.

## Gate result and limits

Stage-one acceptance of the 11-signature three-circles statement surface is
complete: **ACCEPT WITH APPLIED EDITORIAL FIXES** — six consolidated fixes
applied (plus one collateral comment fix), all prose/status-only, zero
blocking items, zero statement changes.

Stated plainly, the limits of this record:

- **No kernel verdict.** No Lean toolchain was run; nothing here is
  Lean-checked. Under the one invariant, only the Lean kernel via CI can
  verify these statements, and that judgment has not occurred.
- **No barrier-row change.** No `MATHLIB_CAPABILITY_MAP.md` row is closed,
  weakened, or re-scoped; generic pinned machinery never retires a row,
  at either stage.
- **No promotion and no scheduling.** Nothing was promoted or imported into
  the build; a stage-two built promotion is a separate later change
  requiring its own dated decision; queue flips are the orchestrator's, not
  this panel's — the sole ACTIVE task remains `RH-012` throughout.
- **No route selection and no claim about RH.** This record provides no
  evidence for or against the Riemann Hypothesis and must not be cited as
  momentum toward any route.
