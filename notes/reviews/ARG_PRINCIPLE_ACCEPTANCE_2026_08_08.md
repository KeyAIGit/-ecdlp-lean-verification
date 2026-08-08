# Circle-only argument principle contract acceptance record (upstream pool item 7)

Date: 2026-08-08

Status: **FINAL — stage-one independent statement-surface acceptance.**
Reviewed object: `domains/riemann-hypothesis/ARG_PRINCIPLE_CONTRACT.md`.
Statement surface: W1, A1-A4 — five public signatures, Form A (circle-only).

## The decision, stated first

**ACCEPTED at stage one, with editorial fixes, zero blocking findings.**
Three independent lenses — mathematical truth, pin fidelity, claim boundary —
each returned ACCEPT_WITH_EDITORIAL_FIXES with **no blocking item**, and
**no lens proposed a change to any public signature**. Between them they raised
17 non-blocking findings, enumerated in full below.

What this record does and does not do. It is the citable acceptance object for
the statement surface, and under the two-stage gate its existence unlocks exactly
one thing: the drafts-lane transcription `domains/riemann-hypothesis/drafts/ArgPrinciple.lean`. It carries **no
kernel verdict**; no declaration in the contract has been elaborated and no `lake
build` has been run against any of it. The kernel's verdict is delivered only by a
separate stage-two promotion change. Acceptance never implies promotion.

## Verification standing of the findings below — read before acting on any of them

Each finding below is the work of **one** lens. The three lenses ran
independently and did not cross-check each other, and **no adversarial verifier
was run against any individual finding**. That is a weaker evidentiary standard
than the hazard-sweep findings recorded elsewhere in `notes/reviews/`, where
every proposed repair was put to a separate agent instructed to refute it.

Consequences a reader must carry:

- A finding here is a **claim with a locator**, not a verified fact. Where a
  finding says a pinned lemma exists, the locator was read by its author and by
  nobody else. Re-open it before relying on it.
- The verdict is nevertheless sound at the level it operates: three lenses
  independently found **nothing blocking** and **no lens asked for a signature
  change**. Agreement on the absence of a defect across three independent
  readings is the evidence for the ACCEPT; it is not evidence for the precise
  content of any single finding.
- The cost-reducing findings in particular deserve confirmation before they are
  used to re-price the package, because a wrong "this is cheaper than you think"
  is more damaging than a wrong "this is harder than you think": it invites a
  drafter to skip preparation.

## Findings that change how the package should be planned

The two findings that change the package's cost, both of which make it CHEAPER
than its own contract claims:

1. **`A1` is not the package's hard step.** The contract calls it "the single
   genuinely new move" and registers `S1AP-BRIDGE` as HIGH, gating A2-A4. The
   truth lens found `MeromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin`
   at `Mathlib/Analysis/Meromorphic/IsolatedZeros.lean:99`, whose hypothesis
   shape is A1's exactly (with the strictly weaker `MeromorphicAt` in place of
   `AnalyticAt`) and whose conclusion is the punctured form. The delta is one
   step through `AnalyticAt.frequently_eq_iff_eventually_eq`
   (Analytic/IsolatedZeros.lean:141). If that reading holds — and it is a
   single-lens finding, so confirm the two locators before re-pricing — A1 is a
   three-line corollary rather than a HIGH gate. A1 remains TRUE and its signature needs no change — the defect is in
   the risk register and the novelty prose, which a stage-two planner would
   have relied on.

   Why the contract's own name-collision scan did not catch it: that scan greps
   the five PROPOSED NAMES. A name-only scan cannot detect a semantic duplicate
   living under a different name. That limitation should be stated in the scan.

2. **The `|R|` sign-flip the contract calls absent is ~3 lines away.** `W1`'s
   alternative-route discussion says the `∮` flip "does not exist at the pin",
   which is literally true of a named `∮` lemma and misleading in effect:
   `circleAverage_abs_radius` (MeasureTheory/Integral/CircleAverage.lean:135,
   `@[simp]`) already does it, and `circleIntegral` is a `circleAverage`
   multiple. Promoting the Cauchy+flip route to primary retires two MEDIUM
   obligations (`S1AP-W1a`, `S1AP-W1b`) entirely.

And one finding that is a soundness observation rather than a cost one:

3. **`0 < R` in A2 and A3 is load-bearing for TRUTH, not convenience.** The
   contract frames the negative-radius trap as W1-specific. Witness at the pin:
   `f = id`, `c = 0`, `R = -1`. Then `closedBall 0 (-1) = ∅` and
   `sphere 0 (-1) = ∅`, so both hypotheses are vacuous and the divisor finsum
   over `ball 0 (-1) = ∅` is `0`; but the left side is
   `∮ z in C(0,-1), 1/z = 2πI ≠ 0` by `circleIntegral.integral_sub_center_inv`
   (CircleIntegral.lean:532, hypothesis exactly `R ≠ 0`). A2 and A3 would be
   FALSE without `0 < R`. The trap is package-wide and must be said so.

## All findings, by lens

### Lens: mathematical truth — ACCEPT_WITH_EDITORIAL_FIXES, 0 blocking, 5 non-blocking

What was checked: Pin re-verified: `git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD` → fabf563a7c95a166b8d7b6efca11c8b4dc9d911f. Read the whole contract including all annexes.

TRUTH VERDICT PER SIGNATURE.

W1 — TRUE, positively verified. `circleIntegral f c R := ∫ θ in 0..2*π, deriv (circleMap c R) θ • f (circleMap c R θ)` (CircleIntegral.lean:385) with notation at :389 documented as ∮_{|z-c|=|R|} (:16, :60). Two independent proofs of W1 at the pin: (i) Cauchy for 0 ≤ R (`DiffContOnCl.circleIntegral_eq_zero`, CauchyIntegral.lean:459, `h0 : 0 ≤ R`) plus the radius flip derivable from `circleAverage_abs_radius` (CircleAverage.lean:135) / `circleMap_neg_radius` (CircleIntegral.lean:162, `circleMap c (-r) x = circleMap c r (x + π)`) and 2π-periodicity; (ii) the contract's primitive route — I checked the mathematics: on `sphere c |R|`, (z-w)/(c-w) = 1 + (z-c)/(c-w) with ‖(z-c)/(c-w)‖ = |R|/dist

**Not checked, and why** (load-bearing — do not read absence of a finding here as a clean bill): 1. NOTHING WAS ELABORATED. There is no Lean toolchain here and I ran none. No signature is known to typecheck. In particular I could not check: whether `2 * Real.pi * Complex.I * ((∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u : ℤ) : ℂ)` elaborates with the intended coercions under the proposed `open Complex Metric Filter Function` / `open scoped Real Topology` preamble; whether the `: ℤ` type ascription on the finsum resolves the `locallyFinsuppWithin` FunLike coercion the way the contract intends; whether declaring `theorem circleIntegral.integral_sub_inv_of_notMem_closedBall` with a dotted name interacts badly with the reopened `namespace circleIntegral`; whether `deriv` resolves to `_root_.deriv` inside `namespace Complex` with `open Complex` active. These are name-resolution/elaboration questions, not truth questions, but they can make a true statement unbuildable.

2. I did not

1. **§Candidate fields ("The single genuinely new move (A1)"); §2 A1 commentary ("the pool's named hardest step"); Obligation register row S1AP-BRIDGE (HIGH, "the co** — A1 is a thin corollary of a pinned lemma the contract never cites. `MeromorphicAt.eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin` at Mathlib/Analysis/Meromorphic/IsolatedZeros.lean:99 (inside `namespace MeromorphicAt`, :31–:130) reads verbatim: `theorem eventuallyEq_nhdsNE_of_eventuallyEq_codiscreteWithin (hf : MeromorphicAt f x) (hg : MeromorphicAt g x) (h₁x : x ∈ U) (h₂x : AccPt x (𝓟 U)) (h : f =ᶠ[codiscreteWithin U] g) : f =ᶠ[𝓝[≠] x] g`. That is A1's hypothesis shape exactly (with the strictly weaker MeromorphicAt in place of AnalyticAt), with the punctured conclusion. The delta to A1 is one step: `AnalyticAt.frequently_eq_iff_eventually_eq` (Mathlib/Analysis/Analytic/IsolatedZeros.lean:141) applied to `.frequently` of that conclusion, using the instance `NormedField.nhdsNE_neBot (x : α) : NeBot (𝓝[≠] x)` (Mathlib/Analysis/Normed/Field/Basic.lean:242, `@[instance]`, inside `namespace NormedField` :193–:279) and `AnalyticAt.meromorphicAt` (Mathlib/Analysis/Meromorphic/Basic.lean:40). So A1 is a 3-line proof, not the package's HIGH-risk gate. The §Name-collision scan did not c

   *Fix:* Add IsolatedZeros.lean:99 (and :59, :109, :117-family) to §0; downgrade S1AP-BRIDGE from HIGH to LOW and record the two-line discharge; delete or rewrite "the single genuinely new move" and "the pool's named hardest step" for A1 (the genuinely un-pinned content of this package is A2's assembly, not A1); rename A1 to match the pinned family, e.g. `AnalyticAt.eventuallyEq_nhds_of_eventuallyEq_codiscreteWithin`; and add a sentence to §Name-collision scan stating that a name-only scan does not establish semantic novelty.

2. **§2 W1 "Alternative route"; DEFERRED-AP4; obligations S1AP-W1a and S1AP-W1b (both MEDIUM)** — The contract says the ∮-level sign-flip `∮ … C(c,R) = ∮ … C(c,|R|)` "does not exist at the pin" and points only at the hard reconstruction pattern (CircleIntegral.lean:292–:296, periodic shift by π). Literally true as a named ∮-lemma, but the contract never mentions `circleAverage`, where the flip is already done: `circleAverage_abs_radius : circleAverage f c |R| = circleAverage f c R` (Mathlib/MeasureTheory/Integral/CircleAverage.lean:135, `@[simp]`) and `circleAverage_neg_radius` (:129), built on `circleAverage_eq_integral_add` (:117) and `circleMap_neg_radius` (CircleIntegral.lean:162). With `circleAverage f c R = (2*π)⁻¹ • ∫ θ in 0..2*π, f (circleMap c R θ)` (CircleAverage.lean:54) and `circleIntegral f c R = ∫ θ in 0..2*π, deriv (circleMap c R) θ • f (circleMap c R θ)` (CircleIntegral.lean:385) together with `deriv_circleMap` (:129) and `circleMap_sub_center`, one gets `∮ z in C(c,R), g z = 2*π • circleAverage (fun z ↦ ((z - c) * I) • g z) c R`, so the ∮ flip falls out of :135 in a few lines. W1 then reduces to `DiffContOnCl.circleIntegral_eq_zero` (Mathlib/Analysis/Complex/Cauc

   *Fix:* Add CircleAverage.lean:54/:117/:129/:135 to §0; restate DEFERRED-AP4 as "absent as a named ∮ lemma but ~3 lines from circleAverage_abs_radius"; promote the Cauchy+flip route to primary for W1 and demote the log-primitive route to the recorded fallback, retiring S1AP-W1a/W1b/W1c as the primary path.

3. **§2 A2/A3/A4 signatures (`hR : 0 < R`) versus W1 (`|R|`); §5.2; Death condition 8** — Two issues, both about the same negative-radius trap. (a) The contract frames that trap as W1-specific, but `0 < R` in A2 and A3 is soundness-load-bearing, not merely convenient. Witness at the pin: f = id, c = 0, R = -1. Then `closedBall 0 (-1) = ∅` so `hf : AnalyticOnNhd ℂ f (closedBall c R)` is vacuous, `sphere 0 (-1) = ∅` so `hf₀` is vacuous, `ball 0 (-1) = ∅` so the divisor finsum is 0 and A2's RHS is 0; but the LHS is `∮ z in C(0,-1), 1/z = 2*π*I ≠ 0` by `circleIntegral.integral_sub_center_inv` (CircleIntegral.lean:532, hypothesis exactly `hR : R ≠ 0`) — the same witness §5.2 already uses against the pool's W1. A2 and A3 would be FALSE without `0 < R`; A4 would be false too (RHS ranges over 2πI·ℕ but 2πI·n = 2πI forces n = 1, which is attainable, so A4 survives this particular witness — take instead f = (·)², giving LHS 4πI and no n with 2πI·n = 4πI... n = 2 works, so A4 is not broken by this family; A4's `0 < R` is convenience, A2/A3's is soundness). (b) Internal convention inconsistency: W1 is stated on `|R|` while A2–A4 use `0 < R`, whereas Mathlib's own family here uses `R 

   *Fix:* Extend §5.2 and death condition 8 to say the trap is package-wide, and state explicitly under A2/A3 that `0 < R` is required for truth (with the f = id, c = 0, R = -1 witness against `0 ≤ R` weakening to R < 0). Either adopt the pin's `R ≠ 0` + `|R|` convention across A2–A4 for consistency with W1 and with JensenFormula.lean:307, or add one sentence justifying the deliberate split.

4. **§2 W1 statement: `theorem circleIntegral.integral_sub_inv_of_notMem_closedBall`** — The proposed name records `notMem_closedBall` but not that the ball is `closedBall c |R|` rather than `closedBall c R`. The contract itself elevates the `R` vs `|R|` confusion to a death condition (8) and to the one correction it made to the pool; a consumer who applies the lemma by name is exactly the failure mode the contract is guarding against. (Mathlib's :557 `integral_sub_zpow_of_undef` has the same silent `|R|`, so this is convention-conformant — but that convention is what produced the pool's defect.)

   *Fix:* Either name it `..._of_notMem_closedBall_abs` / `..._of_abs_lt_dist`, or require a docstring on the built declaration stating the ball is `closedBall c |R|` and cross-referencing §5.2.

5. **§0 quote of `MeromorphicOn.extract_zeros_poles` (FactorizedRational.lean:291) and §Pinned dependencies (A2)** — The contract correctly reports that the theorem carries no `IsOpen U` (I re-read the section variables at Mathlib/Analysis/Meromorphic/FactorizedRational.lean:35–:38: only `𝕜`, `E`, `U : Set 𝕜`), but does not mention that the theorem's own docstring (:284–:290) begins "If `f` is meromorphic on an **open** set `U`". A stage-two implementer using `U := closedBall c R` will hit that docstring and may stall or wrongly conclude the use is illegitimate. The binders govern and the use is legitimate.

   *Fix:* Add one line to the §0 note: "docstring at :284–:290 says 'open set U'; the binders carry no `IsOpen`, and the binders govern — `U := closedBall c R` is legal."


### Lens: pin fidelity — ACCEPT_WITH_EDITORIAL_FIXES, 0 blocking, 6 non-blocking

What was checked: Pin confirmed: `git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD` → fabf563a7c95a166b8d7b6efca11c8b4dc9d911f.

EVERY §0 locator opened and its signature text compared against the file (all correct, no stale line, no deviation from the quoted signature):
- CircleIntegral.lean :54–56 (docstring, PR-10000 sentence verbatim), :129, :176, :292, :337, :422, :425, :430, :451, :461, :527, :532, :538, :557, :566, :699. Namespace boundaries re-derived by grepping `^namespace`/`^end`: `namespace circleIntegral` spans :419–:584 and reopens :696–:718 — Annex A F1's correction is right, and `circleIntegral_congr_codiscreteWithin` (:430) is indeed inside the :419 block. `ContinuousOn.circleIntegrable` (:337) and `circleIntegrable_neg_radius` (:292) are root-level as §0 says.
- CauchyIntegral.lean :440, :459 (`_root_.DiffContOnCl.circleIntegral_eq_zero`, `h0 : 0 ≤ R`, `omit [CompleteSpace 

**Not checked, and why** (load-bearing — do not read absence of a finding here as a clean bill): - Nothing was elaborated. There is no Lean toolchain here, so no statement is known to typecheck and no skeleton is known to close. Every judgement above is a text-level comparison against the pinned source plus hand-derivation. In particular the delicate higher-order unification in W1 (`HasDerivAt.comp`'s `?h z =?= (z - w) / (c - w)` against `fun y => (id y - w) / (c - w)`, and the `Function.comp` vs lambda shape at contract line 413) is judged plausible, not verified; likewise the finprod→`Finset.prod` seam in A2 step 7 and the `Set.Finite` vs `Function.HasFiniteSupport` coercion alignment needed to feed `FactorizedRational.finprod_eq_fun` (:67).

- Three prose-named auxiliaries I could NOT open a declaration site for in the mathlib4 tree at the pin, and therefore do not certify: `Pi.smul_apply` (Algebra/Group/Action/Pi.lean:41 declares the dependent `Pi.smul_apply'`; the non-primed na

1. **§0, line 269 (`theorem logDeriv_mul … (hf : f x ≠ 0) (hg : g x ≠ 0) … -- :54`)** — This is the one §0 entry whose `…` elision hides an EXPLICIT positional argument. The real declaration at Mathlib/Analysis/Calculus/LogDeriv.lean:54–57 is `theorem logDeriv_mul {f g : 𝕜 → 𝕜'} (x : 𝕜) (hf : f x ≠ 0) (hg : g x ≠ 0) (hdf : DifferentiableAt 𝕜 f x) (hdg : DifferentiableAt 𝕜 g x) : logDeriv (fun z => f z * g z) x = logDeriv f x + logDeriv g x`. `(x : 𝕜)` is explicit and PRECEDES `hf`. Every other §0 elision hides only implicits. Given that today's CI round was lost to an explicitness assumption, this is exactly the wrong entry to abbreviate.

   *Fix:* Quote :54–57 verbatim in §0, with `(x : 𝕜)` and both `DifferentiableAt` binders shown. Same treatment for :73 (`logDeriv_prod {ι : Type*} {s : Finset ι} {f : ι → 𝕜 → 𝕜'} {x : 𝕜} (hf : ∀ i ∈ s, f i x ≠ 0) (hd : ∀ i ∈ s, DifferentiableAt 𝕜 (f i) x)`), whose second hypothesis is likewise elided.

2. **A2 proof skeleton step 7 (contract lines 593–599) and obligation S1AP-LOGD (lines 635–646)** — S1AP-LOGD names the lambda-shape hazard for `logDeriv_fun_zpow` ('`(f · ^ n)` lambda shape versus the `(· - u) ^ D u` factor shape') but not the same hazard one level up. At the pin, `logDeriv_mul`'s conclusion is `logDeriv (fun z => f z * g z) x` (LogDeriv.lean:56) and `logDeriv_prod`'s is `logDeriv (∏ i ∈ s, f i ·) x` (LogDeriv.lean:75) — both lambda spellings — while step 7 computes with `logDeriv (φ * g) z`, a Pi-level product of two functions. These are defeq but not syntactically equal, so `rw` will not fire and `exact` needs a `show`. Not a soundness problem; it is an unrecorded seam of exactly the kind the register is for.

   *Fix:* Extend S1AP-LOGD to name all three lambda shapes (`logDeriv_mul` :56, `logDeriv_prod` :75, `logDeriv_fun_zpow` :88) and record `Pi.mul_apply`/`show` as the discharge, alongside the already-recorded `Pi.smul_apply` of S1AP-SMUL.

3. **Skeleton prose throughout: S1AP-W1a/W1b (lines 448–459), S1AP-BRIDGE fallback (ii) (line 522), A3/A4 dependency lines (752–753), A2 step 11 / S1AP-CAST (line 67** — A set of consumed lemmas is named without a `file:line`, contrary to the house rule that Annex A finding F3 itself enforced for `EventuallyEq.eq_of_nhds`. A3/A4 even cite '`Finset.sum_nonneg`, `Int.toNat_of_nonneg` (core big-operators/order API, same files as A3's)', which is a locator-free hand-wave. I opened the ones I could; all resolve, and two of them are load-bearing explicitness facts the contract silently got right without saying so.

   *Fix:* Add these verified locators to §0: `Complex.abs_re_le_norm` — Analysis/Complex/Norm.lean:38 (`@[bound] theorem abs_re_le_norm (z : ℂ) : |z.re| ≤ ‖z‖`, namespace `Complex` — note the RCLike homonym at Analysis/RCLike/Basic.lean:690); `HasDerivAt.comp` — Analysis/Calculus/Deriv/Comp.lean:258, with `x` EXPLICIT (re-declared `(x)` at :71, comment at :67–68 'we put x explicit to help the elaborator'), which is what makes the skeleton's `.comp z (…)` correct; `hasDerivAt_id` — Analysis/Calculus/Deriv/Basic.lean:681 under `variable (s x L)` at :673, so `hasDerivAt_id z` is correct; `HasDerivAt.sub_const` — alias at Analysis/Calculus/Deriv/Add.lean:403 of `hasDerivAt_sub_const_iff` (:400, `(c : F)` 

4. **§0, Divisor.lean namespace note, lines 191–194** — The naming-trap note is imprecise in a way that inverts the risk. It says :68/:71/:177 AND :91/:104 'need the MeromorphicOn. prefix', then records only that dot notation on a `MeromorphicOn` hypothesis discharges :91/:104. At the pin, :68 (`divisor_apply`, hypothesis `hf : MeromorphicOn f U`) is equally dischargeable by dot notation, whereas :71 (`AnalyticOnNhd.divisor_apply`) and :177 (`AnalyticOnNhd.divisor_nonneg`) take `AnalyticOnNhd` hypotheses while living inside `namespace MeromorphicOn` (:28–:468) with no `_root_`, so they must be written `MeromorphicOn.AnalyticOnNhd.divisor_apply` / `MeromorphicOn.AnalyticOnNhd.divisor_nonneg` in full. A2 steps 5 and 11, A3 and A4 all consume :71/:177. §3 point 1 states this correctly (citing Mult.lean:388–390); §0 blurs it.

   *Fix:* Rewrite the §0 note as: ':68/:91/:104 take a `MeromorphicOn` hypothesis and resolve by dot notation; :71/:177 take an `AnalyticOnNhd` hypothesis but sit in `namespace MeromorphicOn`, so dot notation does NOT resolve and the fully-qualified `MeromorphicOn.AnalyticOnNhd.…` is mandatory (built precedent: repo:ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:390 and :412); only :83 is `_root_`-escaped.'

5. **W1 proof skeleton, contract line 403: `apply circleIntegral.integral_eq_zero_of_hasDerivWithinAt'`** — The primitive `f` in `circleIntegral.integral_eq_zero_of_hasDerivWithinAt'` (CircleIntegral.lean:538) is an implicit argument that does not occur in the conclusion, so a bare `apply` opens a metavariable `?f` in the context BEFORE `intro z hz` and only closes it at the final `exact hd.hasDerivWithinAt` on line 419. This is the same shape as confirmed failure class (B) — a lemma applied with its intermediate object left undetermined. It should succeed here (the assignment `fun u => Complex.log ((u - w) / (c - w))` has no dependence on `z`), but the round-trip cost if it does not is a wasted CI run, and the fix is free.

   *Fix:* Replace with `refine circleIntegral.integral_eq_zero_of_hasDerivWithinAt' (f := fun u : ℂ => Complex.log ((u - w) / (c - w))) ?_` so the primitive is pinned before the binder is introduced. Record it as a one-line note under S1AP-W1a.

6. **Header line 20 and line 26 (`drafts/ArgPrinciple.lean`), and line 146 ('A repo-side scan of `drafts/` shows no `ArgPrinciple.lean`')** — There is no top-level `drafts/` directory in the repository. The drafts lane is `domains/riemann-hypothesis/drafts/` (11 files: HarnackDisc, MellinBound, PolyLiouville, README, RiemannConj, RiemannGrowthOrder, RiemannMult, RiemannTargetBridge, RiemannXi, ThreeCircles, ZeroSetSlice). The scan claim is true on the merits (no `ArgPrinciple.lean` exists anywhere in the repo), and the shorthand is inherited verbatim from `MULTIPLICITY_CONTRACT.md:17`, so this is a pre-existing repo-wide abbreviation rather than a new defect — but a stage-two PR author reading the contract literally will create the file in the wrong place, and a file at top-level `drafts/` would still be outside every lake target so the CI-scope argument survives either way.

   *Fix:* Spell the path once as `domains/riemann-hypothesis/drafts/ArgPrinciple.lean` at first use (line 20 or 26), noting that the short form matches the sibling contract's convention.


### Lens: claim boundary — ACCEPT_WITH_EDITORIAL_FIXES, 0 blocking, 6 non-blocking

What was checked: Read the entire contract, all 1158 lines, including Annex A (red-team record, findings F1–F5, sections A–E). Under my lens specifically: (1) Read all five public signatures at :386–388, :472–479, :545–551, :688–692, :735–739 and confirmed none mentions riemannZeta, riemannXi, completedRiemannZeta/₀, LSeries, a critical line or strip, or the zero set of any named function; A1 is generic over `𝕜`/`E`, A2–A4 quantify over an arbitrary `f : ℂ → ℂ`, W1 has no function argument at all; the surface contains zero `def`s as claimed. (2) Read the full barrier table of MATHLIB_CAPABILITY_MAP.md:380–392 plus its six addenda (:505–656) and checked every barrier claim in the contract against the row text — this produced nonblocking finding 1 (S1-GLOBAL-ZEROS:387 is broader than the contract's paraphrase) and finding 2 (only "closes" is negated; "advances"/"partially closes"/"inventory only" are not st

**Not checked, and why** (load-bearing — do not read absence of a finding here as a clean bill): No kernel is available and nothing was elaborated, so I verified no proof and no statement's truth. Specifically outside what I checked: (a) Pin fidelity of the roughly ninety file:line locators in §0 and Annex A section C — I opened exactly two (Divisor.lean:104, FactorizedRational.lean:291) plus the pin hash; the remaining locators, all namespace-block boundaries, the five name-collision scans, and the `windingNumber`/`argument principle` absence scans are the citation reviewer's lens and I did not re-run them. (b) Mathematical truth of W1, A1, A2, A3, A4 under their stated hypotheses, including Annex A section D's edge-case opinions (R = 0 for W1, necessity of `hacc` in A1) — I did not independently verify any of it, and my boundary verdict does not depend on it; a false statement found by the truth lens would override this ACCEPT. (c) Whether any proof skeleton closes, and the severi

1. **ARG_PRINCIPLE_CONTRACT.md:867–870 (§Claim boundary, second bullet)** — The disclaimer mischaracterizes the barrier row it disclaims. Verbatim: "In particular this is **not** progress on `S1-GLOBAL-ZEROS`, whose row concerns zero *enumeration* for specific functions — A2's divisor sum is an integer attached to one disc, not an enumeration, an ordering, or a counting function `N(T)`." The row itself (MATHLIB_CAPABILITY_MAP.md:387) is broader than enumeration: its blocks column reads "no global enumeration, symmetric truncation, convergence, or counting API" and its exit-evidence column LEADS with "finite divisor sums". A2/A3/A4 are finite divisor sums. The conclusion (no progress) still holds, because the row is scoped to this repository's zeta/xi layer and A2 sums the divisor of an arbitrary f, but the stated reason is not the row's actual content, and a reader checking the row will find the contract's paraphrase does not match it.

   *Fix:* Replace the paraphrase with the row's real text and the real reason: "…not progress on `S1-GLOBAL-ZEROS`. That row's exit evidence leads with 'finite divisor sums' (MATHLIB_CAPABILITY_MAP.md:387), and A2–A4 are finite divisor sums — but of an ARBITRARY f over one disc, whereas the row is scoped to this repository's zeta/xi layer and additionally requires symmetric truncation, weighted summability, and the source-matched |rho| <= T / |Im rho| < T limits. The row is untouched and stays OPEN; the effect is inventory only."

2. **ARG_PRINCIPLE_CONTRACT.md:42–43 (Scope) and :860–870 (§Claim boundary, first two bullets)** — The contract negates only the word "closes": "This contract closes **no barrier** of `MATHLIB_CAPABILITY_MAP.md`" and "**No barrier is closed by building it either.**" It never says in terms that it ADVANCES no barrier and PARTIALLY CLOSES no barrier, nor that its capability-map effect is INVENTORY ONLY. Those three are covered only implicitly by "Generic machinery lowers the *cost* of some future exit; it never retires a row" (:865–866). The repo already has a settled formula for exactly this situation and this contract does not use it: drafts/README.md:33 (HarnackDisc) and :34 (PolyLiouville) read "it closes no barrier, advances no barrier, partially closes no barrier (its capability-map effect is inventory only), bears on no conjecture, and provides no evidence for or against RH", and the built headers repeat it (ResearchOS/Analysis/HarnackDisc.lean:26–31).

   *Fix:* Adopt the established sentence verbatim in §Claim boundary: "It closes no barrier, advances no barrier, and partially closes no barrier of `MATHLIB_CAPABILITY_MAP.md` — its capability-map effect is INVENTORY ONLY. Generic machinery lowers the cost of a future exit; it never retires a row."

3. **ARG_PRINCIPLE_CONTRACT.md:26–29 (Working name) and :988–996 (§Stage two)** — The contract names no repo-side destination and no ledger domain for a stage-two promotion. It names only `drafts/ArgPrinciple.lean` and, as an alternative, upstream `Mathlib/Analysis/Complex/ArgumentPrinciple.lean`; §Stage two says a promotion PR "carries the built module, its ledger rows, the regenerated registry and axiom audit" without saying which shelf or which claim-id prefix. Three facts make that omission actionable rather than cosmetic: (a) the ledger prefix map is a CLOSED machine whitelist — scripts/gen_researchos_registry.py:47–63 maps only nt-/RH-/MB-/HK-/PL-/TC-/GO-, with DOMAIN_SUBTREES forcing riemann-hypothesis rows under ResearchOS/AnalyticNumberTheory/RiemannHypothesis/ and analysis-generic rows under ResearchOS/Analysis/, and the in-file comment states "domain-neutral lemmas may not be filed inside a conjecture program's subtree, where they would read as that program's content" (VERIFIED_RESEARCHOS.md:22–25 restates it); (b) the drafts-lane promotion invariant at drafts/README.md:40–45 says a promoted draft moves "only together with its `RH-*` ledger rows", which

   *Fix:* Add one line to §Stage two: "This package is domain-neutral. Its built form belongs on the domain-neutral shelf `ResearchOS/Analysis/ArgPrinciple.lean`, NOT under `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`, with `analysis-generic` ledger rows under a newly registered prefix (e.g. `AP-`) added to `PREFIX_DOMAINS` in scripts/gen_researchos_registry.py — the MellinBound/Harnack/PolyLiouville pattern (drafts/README.md:32–34). The `RH-*` default in drafts/README.md:44 does not apply."

4. **ARG_PRINCIPLE_CONTRACT.md:853–854 (DEFERRED-AP5)** — Verbatim: "…the sphere-side `logDeriv` expansion gains a pole-factor case split, and the analytic case is the one with consumers in sight." This is the only sentence in the document that asserts a downstream consumer, and it names none. In a document whose entire licence is route-neutrality, an unnamed "consumers in sight" invites the reader to supply one; the natural supply inside domains/riemann-hypothesis/ is an entire function (xi), and the analytic-vs-meromorphic split the sentence turns on is exactly the xi-vs-zeta split. It also sits uneasily beside :805–806 ("any such instantiation belongs to a future, separately authorized, queue-governed contract") and :900–901 ("A clean generic package plus a missing instantiation is the correct end state"). It does not select a route and does not assert anything about RH, but it is the sentence a boundary reviewer must quote.

   *Fix:* Either name the consumers explicitly and neutrally ("the analytic case is what DEFERRED-AP2/AP3 and an upstream Mathlib submission would consume") or delete the clause, leaving "…gains a pole-factor case split. A future delta, not a redesign."

5. **ARG_PRINCIPLE_CONTRACT.md:36–46 (Scope) and :858–882 (§Claim boundary) — absence of a shape-neutrality statement** — The route-neutrality argument rests entirely on lexical grounds ("No statement mentions `riemannZeta`, `riemannXi`, an L-function, a critical strip, or any route"), and never addresses region SHAPE. The whole surface is disc-only: A2–A4 count over `Metric.ball c R` with the contour `C(c, R)`. The repo's own precedent treats shape as the route-selection vector to be checked mechanically: RH-011 required "the no-cutoff-shape neutrality property re-verified mechanically" and tasks/RIEMANN_HYPOTHESIS.md:790–792 states the ZERO_SET_SLICE surface is "parameterized by an arbitrary compact `K`, with no cutoff shape anywhere, because choosing a cutoff shape is a route selection and all routes remain PARKED". I checked this and conclude it is NOT a route selection here — the statements quantify over an arbitrary f with no zero set of any named function to truncate, and the disc is forced by the pinned library (only `circleIntegral` exists; Form B/general contours are absent at the pin). But the disclaimer as written does not survive the obvious challenge that the disc is also the Li-side |rho|

   *Fix:* Add to §Claim boundary: "Shape neutrality. The disc/circle is not a cutoff choice in the RH-011 sense: no statement here truncates the zero set of any named function, so there is nothing for a shape to select over. The disc is forced by the pin — `circleIntegral` is the only contour API present, and general contours are Form B (death condition 5). The asymmetry is recorded rather than hidden: nothing here supplies a strip- or rectangle-shaped count, and the route-neutral compact-`K` form at the xi level already exists separately in ZERO_SET_SLICE_CONTRACT.md."

6. **ARG_PRINCIPLE_CONTRACT.md:108–109 (Expected information gain)** — "Plus W1, a few-line library-gap closure independent of the rest." The contract's own §5.2 retracts precisely this cost estimate for the route it then adopts: ":958–960: "Consequently the pool's 'few-line addition via the Cauchy theorem' is accurate for `0 ≤ R` only; the uniform statement uses the primitive route (:538 + slitPlane log)". W1's primary route carries two MEDIUM obligations (S1AP-W1a, S1AP-W1b) and its displayed skeleton has two `sorry` holes (:412, :418). An effort claim, not a barrier claim, but it is an overclaim inside the section that states what the package delivers.

   *Fix:* Change to "Plus W1, a self-contained library-gap closure independent of the rest (few-line via Cauchy for `0 ≤ R`; the uniform-sign primitive route adopted here carries S1AP-W1a/W1b, see §5.2)."


## Status of the editorial fixes

The findings above are **enumerated here and NOT yet applied to the contract
text**. That is deliberate and is recorded rather than glossed: applying several
dozen edits to a contract of this length is its own change, and doing it inside
an acceptance record would make the record and the object it accepts move
together, which defeats the point of having a citable acceptance object.

The accepted thing is therefore precisely the statement surface as it stands
today. Any later application of these fixes must not touch a public signature —
no lens asked for one — and if any proposed fix turns out to require a signature
change, that returns the surface to contract review rather than proceeding.

## Claim boundary

This record is a review step with no kernel content. The package it accepts
closes no barrier, advances no barrier, and partially closes no barrier; it
selects no route; and it provides no evidence for or against the Riemann
Hypothesis in either direction. `RH-002`'s three `PARK` dispositions remain
CONFIRMED. This record adds no ledger row and no queue entry of any status.
