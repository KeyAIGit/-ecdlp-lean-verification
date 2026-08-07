# Capability-map re-verification review record — 2026-08-07

**This record amends nothing.** It is a review of
`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` against the pinned Mathlib
tree. No row of the map was edited, no label was changed, no barrier was closed,
reopened, re-scoped, or repriced, no route was selected, and no claim about the
truth of the Riemann Hypothesis is made or implied anywhere below. Every proposed
correction in this record is a *proposal for the maintainer*, not an applied edit.

Two statements that this record deliberately does **not** make, because an earlier
round was caught making exactly this mistake: nothing found here shows that any
open barrier is cheaper, staler, or nearer its exit evidence than the map records.
Where a pinned generic tool turns out to exist that the map does not list, that is
a *bookkeeping* defect in the inventory. It is not evidence about the difficulty of
the zeta/xi-specific statement the barrier is actually about, and it must not be
read as one.

## Scope and method

- **Target under review:** `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md`
  (625 lines, audit date 2026-08-04, status line claims an independent replay on
  2026-08-05 with 0 mismatches and 12/12 negatives confirmed).
- **Pinned Mathlib revision:** `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0),
  checkout `/workspace/leanprover-community/mathlib4`. Verified in this session with
  `git rev-parse HEAD`; working tree clean.
- **Method:** ripgrep over the pinned source tree only. No Lean toolchain is
  available in this container, so nothing here is kernel-checked; every verdict is a
  source-reading verdict about *what declaration text exists at a locator*, not about
  what elaborates.
- **Division of labour:** five independent row blocks — `zeta-core`,
  `completion-gamma`, `analysis` (generic complex analysis), `series-integrals`, and
  `negatives` (every `NOT-FOUND-IN-SCOPE` and absence claim in the file). Blocks
  overlapped deliberately on the rows most likely to be contested. Overlaps that
  produced different verdicts are recorded in §5 rather than silently reconciled.
- **Verdict definitions used, as specified for this round:**
  - **CONFIRMED** — the reviewer personally located the declaration and its
    signature matches the row description.
  - **WRONG** — the declaration is missing, renamed, in a different namespace, or
    carries different hypotheses than the row implies.
  - **IMPRECISE** — the row is defensible as literally written but would mislead a
    careful reader.

### Why this round was called

Prior scouting reported two defects in the map: (a) the pinned Hadamard three-lines
theorem and its `verticalStrip` API are absent from the map entirely; (b) two
capability rows were misread by a later note that believed it had discovered them
fresh. Finding (a) is **reproduced and confirmed** below (§3 U1, §4 D-12/D-25).
Finding (b) is **not independently reproducible from this round's evidence** — see
§5.4, where the honest statement of what was and was not found is recorded.

## 1. Tally

Claims checked: **83** distinct map claims, counted as follows.

| section of the map | claims checked | CONFIRMED | WRONG | IMPRECISE |
|---|---|---|---|---|
| Exact formal target (L13, L63-70, L79-80) | 2 | 2 | 0 | 0 |
| Inventory: zeta and completion (L93-103) | 11 | 10 | 0 | 1 |
| Inventory: zeros, half-planes, formulae (L109-121) | 13 | 11 | 0 | 2 |
| Inventory: reusable generic infrastructure (L127-141) | 15 | 10 | 0 | 5 |
| Missing named route interfaces (L147-158) | 12 | 8 | 0 | 4 |
| Decision-summary negatives + generic sentence (L27-38) | 6 | 3 | 0 | 3 |
| Gate-0 "sign source of truth" prose (L164-181) | 1 | 1 | 0 | 0 |
| Barrier table, open rows only (L386-392) | 7 | 5 | 0 | 2 |
| Semantic mismatch register (L398-407) | 10 | 8 | 0 | 2 |
| Route C "No such family is currently named" (L374) | 1 | 1 | 0 | 0 |
| Dated addenda (2026-08-05 §1/§2; 2026-08-06 fifth) | 5 | 2 | 0 | 3 |
| **total** | **83** | **61** | **0** | **22** |

Two notes on this tally.

1. **Zero WRONG rows.** Every positive locator in the map resolves to the named
   declaration at the exact claimed `file:line` with a matching signature. No
   `PRESENT` row was falsified by failing to find the declaration. The map's
   positive inventory is, at the locator level, accurate.
2. **The defects are of a different kind than the previous replay looked for.** The
   2026-08-05 replay checked "does the locator resolve?" and answered yes 100% of
   the time — correctly. This round checked "would a careful reader be misled?", and
   the answer is no for 61 claims and yes for 22. Of the 22, sixteen are the same
   underlying failure mode: **a row states a true zeta/xi-specific absence in wording
   that also denies, or silently omits, pinned generic machinery of the same name.**

Three additional rows are CONFIRMED but carry caveats a maintainer may want folded
into the text; they are listed separately in §2.2 and are not counted as defects.

## 2. Defects, with proposed corrections

### 2.1 IMPRECISE rows (22)

The map is **not** amended by this table. `→` marks proposed replacement text.

| # | map loc. | verdict | what a careful reader would get wrong | proposed correction |
|---|---|---|---|---|
| D-1 | L98 `relation between completions` | IMPRECISE (contested — see §5.1) | Every neighbouring row warns about exceptional-point hypotheses (L100 explicitly). `completedRiemannZeta_eq` is **hypothesis-free and total**, quantified over all `s : ℂ` with no `s ≠ 0` / `s ≠ 1`, so a reader primed by the neighbours will case-split needlessly. | → `… \| completedRiemannZeta_eq, line 84 \| unconditional in s; exact source for all sign algebra` |
| D-2 | L101 `zeta functional equation` | IMPRECISE | Boundary reads "carries negative-integer and pole exclusions". The pinned hypothesis is `∀ n : ℕ, s ≠ -n`, which at `n = 0` gives `s ≠ 0`: the exclusion set is **every non-positive integer**, `s = 0` included. A reader building the FE-first critical-strip localization (L495-503, DAG L247-252) could wrongly assume `s = 0` is admissible. | → `… \| riemannZeta_one_sub, line 176 \| hypotheses (∀ n : ℕ, s ≠ -n) and s ≠ 1 exclude every non-positive integer, s = 0 included, together with the pole` |
| D-3 | L119 `von Mangoldt arithmetic function` | IMPRECISE (locator) | Bare basename `VonMangoldt.lean:65` does not sit under `Mathlib/NumberTheory/` the way the neighbouring rows' convention implies; the actual path is `Mathlib/NumberTheory/ArithmeticFunction/VonMangoldt.lean`. | → `ArithmeticFunction.vonMangoldt, ArithmeticFunction/VonMangoldt.lean:65; ArithmeticFunction.vonMangoldt_sum, line 102` |
| D-4 | L120 `zeta logarithmic derivative` | IMPRECISE (namespace) | The declaration lives inside `namespace ArithmeticFunction` (opened `Dirichlet.lean:423`); the row gives the bare name. It is also stated for `L ↗Λ`, so it needs the `LSeries`↔zeta bridge `LSeries_one_eq_riemannZeta` (`Dirichlet.lean:307`), which the map never records. | → `ArithmeticFunction.LSeries_vonMangoldt_eq_deriv_riemannZeta_div, Dirichlet.lean:434 (companion …_eq, line 427) \| only 1 < re(s); stated for L ↗Λ, so it also needs LSeries_one_eq_riemannZeta, line 307` |
| D-5 | L127 `real gamma factor` | IMPRECISE (namespace) | Full name is `Complex.Gammaℝ` (`namespace Complex` opened `Deligne.lean:37`). The map qualifies namespaces elsewhere (`ArithmeticFunction.vonMangoldt`, `MeromorphicOn.divisor`, `PhragmenLindelof.vertical_strip`, `MeasureTheory.Lp.instCompleteSpace`), so the bare name is an inconsistency, not a convention. | → `Complex.Gammaℝ, Gamma/Deligne.lean:43` |
| D-6 | L128 `gamma zero classification` | **IMPRECISE (substantive)** | `Gammaℝ_eq_zero_iff` gives zero set `∃ n : ℕ, s = -(2 * n)` = `{0, -2, -4, …}`, **strictly larger** than the target's trivial-zero set `-2*(n+1)`. The boundary "must be combined with exact nontrivial-zero exclusions" reads as "just exclude the trivial zeros" — precisely the false-bridge reading the map's own `S0-SEMANTIC` text and third addendum guard against. | → `Complex.Gammaℝ_eq_zero_iff, line 73 \| zero set is {0,-2,-4,…}, strictly larger than the target's -2(n+1); s = 0 must be excluded separately` |
| D-7 | L129 `inverse gamma entire` | IMPRECISE (namespace/shape) | Full name `Complex.differentiable_Gammaℝ_inv`; statement is in `(·)⁻¹` form, not `1 / ·`. Capability and boundary are correct. | → `Complex.differentiable_Gammaℝ_inv, line 88 (stated for fun s ↦ (Gammaℝ s)⁻¹)` |
| D-8 | L134 `Phragmen-Lindelof` | **IMPRECISE (substantive)** | This is the map's only strip row. It under-reports the pinned strip suite (`horizontal_strip:113`, `eq_zero_on_vertical_strip:303`, `eqOn_vertical_strip:321`, four quadrant families, `right_half_plane_of_bounded_on_real:717`) and, far more consequentially, omits the entire **Hadamard three-lines** layer built on top of it. A reader pairing this row with `S1-GROWTH` concludes the pin offers only the raw PL principle and would rebuild three-lines. | → `Phragmen-Lindelof and strip interpolation \| GENERIC \| PhragmenLindelof.vertical_strip, PhragmenLindelof.lean:275 (horizontal_strip:113, eqOn_vertical_strip:321, right_half_plane_of_bounded_on_real:717); Hadamard three lines, Analysis/Complex/Hadamard.lean — Complex.HadamardThreeLines.verticalStrip:70, verticalClosedStrip:73, sSupNormIm:77, interpStrip:246, interpStrip':301, norm_le_interpStrip_of_mem_verticalClosedStrip:588, norm_le_interp_of_mem_verticalClosedStrip':607 \| no zeta boundary-growth package; three lines still needs a proved sup bound on each edge line before it says anything about zeta or xi` |
| D-9 | L137 `functional-equation Mellin pair` | IMPRECISE (contested — see §5.2) | The row omits that `WeakFEPair.hasMellin` is gated on `P.k < re s` and transforms `f - f₀`, not `f`. Route B (L331) needs a Mellin identity for exactly `0 < re s < 1`; this machinery does not reach there, and the row does not say so. Also `StrongFEPair.hasMellin` (`AbstractFuncEq.lean:203`) is a distinct unconditional declaration, so the `WeakFEPair.` prefix is load-bearing. | → append to boundary: `gated on P.k < re s and stated for f - f₀; does not reach 0 < re s < 1` |
| D-10 | L141 `fractional part` | IMPRECISE | "no `ρ_a(x) = fract(1/(ax))` measurability/integrability package" is true of the composite, but measurability itself is generic and pinned: `measurable_fract` and `Measurable.fract`, `MeasureTheory/Function/Floor.lean:45,52`. | → `… \| Int.fract, Algebra/Order/Floor/Defs.lean:259; measurability pinned — measurable_fract, Measurable.fract, MeasureTheory/Function/Floor.lean:45,52 \| missing is the ρ_a-specific L² membership, dilation, and integrability package, not measurability` |
| D-11 | L152 `nontrivial-zero enumeration or counting function` | IMPRECISE (contested — see §5.3) | The zeta/xi negative survives (see §4). But "no canonical `N(T)`, ordered sequence, or symmetric finite truncation" reads as a *generic* absence, and a generic, multiplicity-aware, divisor-based counting theory is pinned and unmentioned: `ValueDistribution.logCounting` (`LogCounting/Basic.lean:96`, `:272`). | → append: `a generic multiplicity-aware counting theory is pinned (ValueDistribution.logCounting/proximity/characteristic); what is missing is the classical critical-strip N(T), an ordering, and symmetric cutoffs for zeta/xi` |
| D-12 | L154 `vertical growth and finite/order-one entire growth` | **IMPRECISE (substantive — the headline defect)** | The zeta/xi half is correct and survives. But the consequence column says "**Hadamard** and contour arguments are blocked", and Hadamard's *three-lines theorem* is pinned (`Analysis/Complex/Hadamard.lean`). The row also conflates a zeta-specific gap with a generic one: there is genuinely no order-of-growth notion for entire functions at the pin, but that is a separate, definitional absence. | → split into two rows: `zeta/xi vertical growth bound \| NOT-FOUND-IN-SCOPE \| no bound on ‖ζ‖ or ‖ξ‖ along vertical lines; this input must be supplied before any strip-interpolation or contour argument says anything about zeta` and `order of growth of an entire function \| NOT-FOUND-IN-SCOPE \| no order/genus/type definition at the pin; the pinned Hadamard three-lines layer and Nevanlinna characteristic are generic vehicles, so this is a definitional gap` |
| D-13 | L155 `canonical product or Hadamard factorization` | IMPRECISE | The infinite/Hadamard half is confirmed absent (no canonical product, no Weierstrass elementary factor, no genus). But two **finite** factorization theorems are pinned and unlisted: `MeromorphicOn.extract_zeros_poles` (`Meromorphic/FactorizedRational.lean:291`) and `MeromorphicOn.exists_canonicalDecomp` (`Analysis/Complex/CanonicalDecomposition.lean:315`). | → `… \| no infinite canonical product, Weierstrass elementary factor, or genus, hence no product over xi zeros; finite zero/pole extraction on compacts is pinned (MeromorphicOn.extract_zeros_poles, FactorizedRational.lean:291; MeromorphicOn.exists_canonicalDecomp, CanonicalDecomposition.lean:315)` |
| D-14 | L158 `Nyman-Beurling/Báez-Duarte objects` | IMPRECISE (contested — see §5.3) | The Nyman objects are confirmed absent. But "only generic `Lp`, Mellin, and fractional-part infrastructure exists" understates two pinned pieces the map's own Addendum §2 names as remaining cost: `MeasureTheory.Lp.compMeasurePreservingₗᵢ` (`MeasureTheory/Function/LpSpace/Basic.lean:627`) and `mellin_eq_fourier` (`Analysis/MellinInversion.lean:49`). | → append: `plus MeasureTheory.Lp.compMeasurePreservingₗᵢ (LpSpace/Basic.lean:627) and mellin_eq_fourier (MellinInversion.lean:49)` |
| D-15 | L29-30 decision-summary item 3 | IMPRECISE | Same defect as D-11, in the summary voice, where it is read first and hardest to unlearn. | → mirror D-11 |
| D-16 | L31 decision-summary item 4 | IMPRECISE | Same defect as D-12/D-13: "no … Hadamard factorization" in a summary that never distinguishes factorization from three lines. | → mirror D-12/D-13; keep "factorization" and never abbreviate to "Hadamard" |
| D-17 | L35-38 "Generic … machinery exist" sentence | IMPRECISE (enumeration reads as exhaustive) | The list omits Hadamard three lines, Nevanlinna value distribution, `Lp` measure-preserving isometries, complex primitives, branch-log existence, identity theorem, maximum modulus, Liouville/Cauchy estimates, and contour machinery — all pinned. | → mark the list explicitly non-exhaustive and point at the generic-infrastructure table as authority |
| D-18 | L387 `S1-GLOBAL-ZEROS` barrier row | IMPRECISE (wording only) | "no global enumeration, symmetric truncation, convergence, or counting API" reads generically; same defect as D-11. **The barrier's status and exit evidence are unchanged by this record.** | → scope the phrase to zeta/xi explicitly; do not alter the exit-evidence string |
| D-19 | L388 `S1-GROWTH` barrier row | IMPRECISE (wording only) | "no zeta/xi vertical or order-one growth theorem \| blocks Hadamard and contour shifts". The zeta/xi clause is exact; the *blocks* clause repeats D-12's ambiguity. **The barrier's status and exit evidence are unchanged by this record.** | → say "blocks the Hadamard *factorization* and contour-shift steps"; do not alter the exit-evidence string |
| D-20 | L402 register: conditionally convergent Li star-sum | IMPRECISE | "no zero-sum API" is right about zeta/xi, but at this pin `tsum`/`HasSum` are *parameterized by a summation filter*: `∑'[L]` notation (`InfiniteSum/Defs.lean:152,154`), `SummationFilter.unconditional/conditional` (`SummationFilter.lean:165,215`), and `symmetricIcc/Ioo/Ico/Ioc` (`ConditionalInt.lean`). The mismatch is therefore *how to pin the cutoff*, and the pin offers a first-class way to do it. | → `… \| no zeta/xi zero-sum API, but a first-class conditional-summation API exists (∑'[L], SummationFilter.conditional, symmetricIcc/Ioo/Ico/Ioc) \| the cutoff must be pinned by choosing the summation filter; an unqualified ∑' means the unconditional filter and is not the star-sum` |
| D-21 | L403 register: global `log ξ` | IMPRECISE | The statement is right, but the map nowhere records that the pin supplies the construction tools its own Route-A local-log contract (L304-308) demands: `Complex.exists_continuousOn_eqOn_exp_comp` (`Analysis/Complex/BranchLogRoot.lean:37`) and `DifferentiableOn.isExactOn_ball` / `Differentiable.isExactOn_univ` (`Analysis/Complex/HasPrimitives.lean:290,309`). | → append the two locators to the "mismatch to close" cell as available generic inputs; the xi-side nonvanishing input remains unbuilt |
| D-22 | Addendum 2026-08-05 §1 (L476-483) | **IMPRECISE (this is the wording that let the gap survive replay)** | "`riemannXi`, Hadamard factorization for finite-order entire functions, and any zeta/conjugation theorem additionally absent **tree-wide** at the pin." `riemannXi` and zeta-conjugation are confirmed absent tree-wide. But a tree-wide claim phrased around "Hadamard" collides with `Mathlib/Analysis/Complex/Hadamard.lean`: a bare `grep -rn Hadamard Mathlib/` returns that file immediately. | → `Hadamard *factorization* for finite-order entire functions is absent tree-wide; Hadamard's *three-lines* theorem is present (Analysis/Complex/Hadamard.lean) and is a distinct result` |
| D-23 | Addendum 2026-08-05 §2 (L484-494) | IMPRECISE (cost sentence + one mislabel) | (a) The residual-cost sentence says the `SC-NB-04` cost reduces to "the log-substitution and scaling unitaries plus the dense-core pointwise formula"; the log substitution and the `2π` rescaling are themselves pinned as `mellin_eq_fourier` (`MellinInversion.lean:49`, with `mellinInv_eq_fourierInv` at `:75`). (b) `LSeries_eq_mul_integral` (`SumCoeff.lean:137`) is an L-series corollary, not "the Abel-summation machinery"; that is `Mathlib/NumberTheory/AbelSummation.lean` (`sum_mul_eq_sub_sub_integral_mul`, `:129`). | → name `mellin_eq_fourier`/`mellinInv_eq_fourierInv` explicitly and state the residual as the L²-class passage and the measure bookkeeping between Mathlib's `volume`-on-`ℝ` Plancherel and the source's `dτ/(2π)`; relabel Abel summation to `AbelSummation.lean:129`. **This does not license any barrier re-pricing; `S2-NYMAN` status is untouched.** |
| D-24 | Addendum 2026-08-06 fifth (L604-606) | **IMPRECISE (half of it is close to WRONG)** | It records "the two generic complex-analysis lemmas that are **genuinely absent** at the pin (`AnalyticAt.conj_conj`, `analyticOrderAt_conj_conj`)". `analyticOrderAt_conj_conj` is genuinely absent (the pinned order-transport lemmas `Analytic/Order.lean:528,561` require a ℂ-analytic inner map, which `conj` is not). `AnalyticAt.conj_conj` is absent **only by that name**: `HasDerivAt.conj_conj:93`, `hasDerivAt_conj_conj_iff:100`, `DifferentiableAt.conj_conj:117`, `differentiableAt_conj_conj_iff:123`, `deriv_conj_conj:139` are all pinned in `Analysis/Calculus/Deriv/Star.lean`, and the file's own module doc names `conj_conj`. | → `analyticOrderAt_conj_conj is genuinely absent at the pin. AnalyticAt.conj_conj is absent only by that name: the HasDerivAt/DifferentiableAt/deriv conj_conj family is pinned at Analysis/Calculus/Deriv/Star.lean:93,100,117,123,139, with the standard transfer analyticAt_iff_eventually_differentiableAt, Analysis/Complex/CauchyIntegral.lean:689.` The RH-008 promotion's own repo-local proofs are unaffected; only the *characterization of the pin* is imprecise. |

(D-24 and D-22 were each independently flagged by three of the five blocks; they are
the two best-corroborated defects in this record.)

### 2.2 CONFIRMED rows carrying caveats (not counted as defects)

| map loc. | caveat |
|---|---|
| L94 `analyticity` | Locators exact. The pinned conclusion of `analyticOn_riemannZeta` is `AnalyticOnNhd ℂ riemannZeta {1}ᶜ` — strictly stronger than the `AnalyticOn` its name suggests, and the stronger form is what `analyticOrderAt` work needs. `differentiableOn_riemannZeta` (`:140`) is unlisted. |
| L103 `local Laurent remainder` | Locators exact. The pinned limit *identifies* the constant term as `γ` (Euler-Mascheroni) rather than merely bounding a remainder — more than "remainder" conveys. |
| L111 `right closed half-plane nonvanishing` | Locator exact. Binders are strict-implicit `⦃s⦄` (affects application style), and the boundary phrase "including the assigned value at `1`" rests entirely on `riemannZeta_one_ne_zero` (`ZetaAsymp.lean:431`), which the map never cites. |

## 3. Capabilities present at the pin that the map does not mention at all

Grepping the map for `liouville|maximum modulus|AbsMax|schwarz|cauchy|identity theorem|isolated zero|three.line|ValueDistribution|characteristic|Nevanlinna|extract_zeros_poles|canonicalDecomp|logCounting|verticalStrip|theta|Jacobi|Stirling|digamma|SummationFilter|AbelSummation`
returns **zero hits**. Ordered by how much each would change what a reader of the map
believes about the pin. Every locator below was checked; the ones re-verified directly
in this session are marked ✔.

**U1 — Hadamard three-lines theorem and the `verticalStrip` API.** ✔
`Mathlib/Analysis/Complex/Hadamard.lean`: `namespace Complex` `:66`,
`namespace HadamardThreeLines` `:67`, `verticalStrip:70` (`re ⁻¹' Ioo a b`),
`verticalClosedStrip:73`, `sSupNormIm:77`, `interpStrip:246`, `interpStrip':301`,
`norm_le_interpStrip_of_mem_verticalClosedStrip:588`,
`norm_le_interp_of_mem_verticalClosedStrip':607`.
*Why it matters here:* this is the convexity-of-`log M` layer sitting directly on top
of the map's only strip row (L134), and it is what "Hadamard … blocked" (L154) and
"Hadamard … absent tree-wide" (Addendum §1) would be read as denying. It is the
mechanism behind the defect this round was called for, and should be recorded as a
**search-hygiene finding** — the 2026-08-05 replay searched by row, not by file — not
merely as a missing row. *It changes nothing about `S1-GROWTH`: three lines is inert
until a proved sup bound on each edge line of a strip exists for `ζ` or `ξ`, and no
such bound exists at the pin (§4, N-8).*

**U2 — Nevanlinna value-distribution package.** ✔
`Mathlib/Analysis/Complex/ValueDistribution/`: `logCounting` (`LogCounting/Basic.lean:96`
divisor form, `:272` `ℝ → ℝ` form, `logCounting_divisor:280`, `logCounting_monotoneOn:355`),
`proximity` (`Proximity/Basic.lean:50`), `characteristic`
(`CharacteristicFunction.lean:53`, `:= proximity f a + logCounting f a`), First Main
Theorem `characteristic_sub_characteristic_inv_le` (`FirstMainTheorem.lean:97`),
`logCounting_isBigO_one_iff_analyticOnNhd` (`LogCounting/Asymptotic.lean:108`),
Cartan (`Cartan.lean:100/109/126`), and
`Function.locallyFinsuppWithin.logCounting_divisor_eq_circleAverage_sub_const`
(`LogCounting/Basic.lean:588`) — the counting-function restatement of the very Jensen
theorem the map's row L133 already cites. *Why it matters here:* the map's L152/L387
wording denies a counting API in generic terms. A generic one exists.

**U3 — Finite factorization / canonical decomposition.** ✔
`MeromorphicOn.extract_zeros_poles` (`Meromorphic/FactorizedRational.lean:291`),
`MeromorphicOn.extract_zeros_poles_log` (`:333`),
`MeromorphicOn.exists_canonicalDecomp` (`Analysis/Complex/CanonicalDecomposition.lean:315`),
`Complex.canonicalFactor:50`, `divisor_canonicalFactor:192`,
`divisor_ball_support_finite` (`Meromorphic/Divisor.lean:104`),
`divisor_sphere_support_finite` (`:83`), `Function.locallyFinsuppWithin`
(`Topology/LocallyFinsupp.lean:48`, `finiteSupport:254`) and
`Topology/LocallyFinsupp/Pushforward.lean`. *Why it matters here:* it is the finite-radius
form of the divisor→product step L155 calls missing, and the pushforward file is the
natural generic home for a `ρ ↦ 1 - conj ρ` divisor symmetry.

**U4 — `Meromorphic` normal form for `Gamma`.** ✔
`MeromorphicNFOn.Gamma : MeromorphicNFOn Gamma univ` (`Analysis/Meromorphic/Complex.lean:19`),
`Meromorphic.Gamma:25`, `MeromorphicOn.Gamma:28`. *Why it matters here:* rows L131-132
label meromorphic order and `MeromorphicOn.divisor` `GENERIC` with "no zeta
specialization" — true for zeta, but there **is** a Gamma specialization, so
`MeromorphicOn.divisor Gamma` is immediately constructible. This is a bookkeeping gap
only; it says nothing about the zeta/xi divisor that `S1-MULTIPLICITY` is about.

**U5 — near-`s = 1` zeta facts.** ✔ `riemannZeta_one` (`Harmonic/ZetaAsymp.lean:408`,
`= (γ - log (4 * π)) / 2`), `riemannZeta_one_ne_zero:431`,
`riemannZeta_eventually_ne_zero_nhds_one:442` (`∀ᶠ s in 𝓝 1, riemannZeta s ≠ 0`),
`deriv_riemannZeta_zero:451`, `completedRiemannZeta_one:416`,
`completedRiemannZeta₀_one:425`, `completedRiemannZeta₀_zero:447`. *Why it matters here:*
the map's `S0-SEMANTIC` framing treats the totalized value at `1` as an opaque
convention; it is a closed form. The last two pin `Λ₀` at both exceptional points and
are an independent cross-check on any `riemannXi 0 = riemannXi 1 = 1/2` derivation.
The `eventually_ne_zero` lemma is the zeta-side analogue of the map's Route-A local-log
input (L304-308) — *analogue, not substitute*: the contract asks for a neighbourhood on
which **xi** is nonzero, and that remains unbuilt.

**U6 — Identity theorem, isolated zeros, analytic↔differentiable transfer.**
`AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq` (`Analytic/Uniqueness.lean:223`);
`AnalyticAt.eventually_eq_zero_or_eventually_ne_zero` (`Analytic/IsolatedZeros.lean:125`),
`eqOn_zero_of_preconnected_of_frequently_eq_zero:214`;
`MeromorphicAt.frequently_zero_iff_eventuallyEq_zero` (`Meromorphic/IsolatedZeros.lean:43`);
`analyticAt_iff_eventually_differentiableAt` (`Analysis/Complex/CauchyIntegral.lean:689`),
`analyticOnNhd_iff_differentiableOn:667`, `DifferentiableOn.analyticOnNhd:631`.
*Why it matters here:* the fifth addendum states the RH-008 proof *already used* "the
pinned identity principle on `{1}ᶜ`" — the project depends on a capability the inventory
never lists — and `analyticAt_iff_eventually_differentiableAt` is the transfer that
makes D-24's correction concrete.

**U7 — `conj_conj` differentiability family.** ✔ `Analysis/Calculus/Deriv/Star.lean`:
`HasDerivAt.conj_conj:93`, `hasDerivAt_conj_conj_iff:100`, `DifferentiableAt.conj_conj:117`,
`differentiableAt_conj_conj_iff:123`, `deriv_conj_conj:139`; plus
`Analysis/Calculus/FDeriv/Star.lean`. See D-24.

**U8 — Gamma-side API the map has no row for at all.** `Complex.Gamma_ne_zero`
(`Gamma/Beta.lean:427`), `Gamma_eq_zero_iff:447`, `Gamma_ne_zero_of_re_pos:453`,
`differentiable_one_div_Gamma:509`, `GammaSeq:230` / `GammaSeq_tendsto_Gamma:335`;
digamma `Complex.digamma := logDeriv Gamma` (`Gamma/Digamma.lean:39`), `digamma_one = -γ:47`,
`digamma_one_half:50`, `digamma_apply_add_one:55`, `meromorphic_digamma:61`;
`Complex.hasDerivAt_Gammaℝ_one` (`GammaDeriv.lean:205`), `hasDerivAt_Gammaℂ_one:193`,
`Real.hasDerivAt_Gamma_one:96`; `Gammaℝ` reflection package (`Deligne.lean`)
`Gammaℝ_ne_zero_of_re_pos:66`, `Gammaℝ_one:77`, `Gammaℝ_residue_zero:95`, `Gammaℝ_add_two:55`,
`Gammaℂ:51`, `Gammaℝ_mul_Gammaℝ_add_one:115`, `Gammaℝ_one_sub_mul_Gammaℝ_one_add:131`,
`Gammaℝ_div_Gammaℝ_one_sub:148`, `inv_Gammaℝ_one_sub:163`, `inv_Gammaℝ_two_sub:178`.
*Why it matters here:* two rows the map does list are stated in terms of `Gamma`
(L101, L100), and the reflection lemmas are the Gamma-side content of the functional
equation.

**U9 — Theta/kernel substrate and the Hurwitz transfer lemmas.** `jacobiTheta₂`
(`JacobiTheta/TwoVariable.lean:252`), `jacobiTheta₂_functional_equation:469`,
`jacobiTheta₂_conj:408`, `jacobiTheta₂'_conj:454`; `jacobiTheta`
(`OneVariable.lean:29`), `jacobiTheta_S_smul:43`, `norm_jacobiTheta_sub_one_le:90`,
`isBigO_at_im_infty_jacobiTheta_sub_one:112`; `HurwitzZeta.evenKernel`
(`HurwitzZetaEven.lean:65`), `cosKernel:89`, `evenKernel_functional_equation:132`,
`isBigO_atTop_evenKernel_sub:223`; the quantitative file `JacobiTheta/Bounds.lean`
(`isBigO_atTop_F_nat_zero_sub:132`, `_F_nat_one:179`, `_F_int_zero_sub:249`, `_F_int_one:266`);
and the `rfl` transfer lemmas that expose the whole Hurwitz layer to zeta —
`RiemannZeta.lean:69,72,75,79` and `HurwitzZeta.hurwitzZetaEven_zero:121`,
`cosZeta_zero:123`, `hurwitzZeta_zero:127`, `expZeta_zero:131`.
*Why it matters here:* this is the analytic substrate under `completedRiemannZeta` and
the only place at the pin holding quantitative decay estimates for the zeta integrand.
`jacobiTheta₂_conj` also shows a theta-level conjugation input exists — which does
**not** contradict the fifth addendum's zeta-level absence claim (§4, N-2).

**U10 — Stirling: a confirmed absence the map never records.**
`Mathlib/Analysis/SpecialFunctions/Stirling.lean` contains only the *real factorial*
asymptotic (`stirlingSeq:56`, `tendsto_stirlingSeq_sqrt_pi:239`,
`factorial_isEquivalent_stirling:246`, `le_factorial_stirling:276`,
`le_log_factorial_stirling:293`). There is **no complex Stirling, no log-Γ asymptotic,
and no vertical-strip Gamma bound anywhere at the pin** (a case-insensitive file scan
returns only that file, `Combinatorics/Enumerative/Stirling.lean`, and a TODO at
`Gamma/BohrMollerup.lean:37`). *Why it matters here:* the Gamma-factor vertical
asymptotic is the standard first ingredient of any `ξ` vertical-growth statement.
Recording it as an explicit `NOT-FOUND-IN-SCOPE` row beside `S1-GROWTH` would make the
barrier's cost *more* legible, not less.

**U11 — Summation filters (conditional and symmetric summation).**
`SummationFilter` (`Topology/Algebra/InfiniteSum/SummationFilter.lean`): `unconditional:165`,
`conditional:215`, `support:61`, `conditional_filter_eq_map_Iic/Ici/range:234/241/247`,
classes `LeAtTop`/`NeBot`; `symmetricIcc/symmetricIoo/symmetricIco/symmetricIoc`
(`InfiniteSum/ConditionalInt.lean`); `∑'[L]`/`∏'[L]` notation (`InfiniteSum/Defs.lean:152,154`).
See D-20.

**U12 — Infinite-product analysis.** `Complex.multipliable_of_summable_log`
(`Analysis/SpecialFunctions/Log/Summable.lean:32`),
`Complex.multipliable_one_add_of_summable` (`:49` — see §5.4 for a locator dispute),
`tprod_one_add_ne_zero_of_summable:216`, the `NormedRing` variant at `:169`;
`multipliableLocallyUniformlyOn_one_add` (`Analysis/Normed/Module/MultipliableUniformlyOn.lean:137`);
`logDeriv_tprod_eq_tsum` (`Analysis/Calculus/LogDerivUniformlyOn.lean:24`); worked
template `HasProdLocallyUniformlyOn_euler_sin_prod`
(`Analysis/SpecialFunctions/Trigonometric/Cotangent.lean:132`).

**U13 — Mellin↔Fourier bridge and Mellin/Dirichlet machine.** ✔ `mellin_eq_fourier`
(`Analysis/MellinInversion.lean:49`), `mellinInv_eq_fourierInv` (`:75`);
`MellinEqDirichlet.lean` `hasSum_mellin:24` and variants `:70,:91,:118,:134`;
`Complex.VerticalIntegrable` (`Analysis/MellinTransform.lean:86`).

**U14 — `Lp` isometries and Plancherel in inner-product form.**
`MeasureTheory.Lp.compMeasurePreservingₗᵢ` (`MeasureTheory/Function/LpSpace/Basic.lean:627`,
with `compMeasurePreservingₗ:620`, `norm_compMeasurePreserving:572`);
`indicatorConstLp` (`LpSpace/Indicator.lean:289`); `MeasureTheory.Lp.inner_fourier_eq`
(`Analysis/Fourier/LpSpace.lean:93`). Note Mathlib's `𝓕` uses the `e^{-2πi⟨x,ξ⟩}` kernel
and the isometry carries `[InnerProductSpace ℝ E] [FiniteDimensional ℝ E]` over `volume`
— a different normalization from the "unnormalized Fourier transform" the map's Route B
text names, and the difference is exactly the `τ/(2π)` rescaling supplied by U13.

**U15 — `LSeries` bridges, injectivity, Abel summation, Chebyshev.**
`LSeries_one_eq_riemannZeta` (`LSeries/Dirichlet.lean:307`), `LSeriesHasSum_one:312`,
`LSeries_zeta_eq_riemannZeta:278`, `LSeries_one_mul_Lseries_moebius:316`,
`ArithmeticFunction.LSeries_zeta_mul_Lseries_moebius:291`;
`LSeries.eq_of_LSeries_eventually_eq` (`LSeries/Injectivity.lean:217`),
`LSeries_injOn:239`; `LSeries.abscissaOfAbsConv` (`LSeries/Convergence.lean:30`);
`Mathlib/NumberTheory/AbelSummation.lean` (`sum_mul_eq_sub_sub_integral_mul:129`,
`sum_mul_eq_sub_integral_mul₀:211`, `tendsto_sum_mul_atTop_nhds_one_sub_integral:281`,
`summable_mul_of_bigO_atTop:366`); `Chebyshev.psi:70`, `Chebyshev.theta:77`,
`eventually_primeCounting_le:647` (`Mathlib/NumberTheory/Chebyshev.lean`). No PNT at the
pin (only the "prerequisites for" comment at `Nonvanishing.lean:25`).

**U16 — Branch logs and primitives.** `Complex.exists_continuousOn_eqOn_exp_comp`
(`Analysis/Complex/BranchLogRoot.lean:37`), `exists_continuousOn_pow_eq:67`;
`DifferentiableOn.isExactOn_ball` (`Analysis/Complex/HasPrimitives.lean:290`),
`Differentiable.isExactOn_univ:309`, `IsConservativeOn.isExactOn_ball:274`. See D-21.

**U17 — Maximum modulus, Liouville/Cauchy estimates, contour machinery, and the rest of
the classical toolkit.** `Analysis/Complex/AbsMax.lean` (`norm_le_of_forall_mem_frontier_norm_le:400`,
`eqOn_of_eqOn_frontier:432`, `norm_eqOn_of_isPreconnected_of_isMaxOn:230`,
`exists_mem_frontier_isMaxOn_norm:383`); `Analysis/Complex/Liouville.lean`
(`norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le:44`,
`norm_deriv_le_of_forall_mem_sphere_norm_le:76`,
`Differentiable.exists_eq_const_of_bounded:128`); `Analysis/Complex/CauchyIntegral.lean`
(`integral_boundary_rect_eq_zero_of_differentiableOn:295`,
`circleIntegral_sub_inv_smul_of_differentiable_on_off_countable:532`,
`DiffContOnCl.circleIntegral_eq_zero:459`); `Analysis/Complex/Schwarz.lean:188,255`;
plus `RemovableSingularity.lean`, `LocallyUniformLimit.lean`, `OpenMapping.lean`,
`TaylorSeries.lean`. *Why it matters here:* the Route C DAG names "contour shift,
pole/zero residues" as required and the map has no contour row at all; the iterated-derivative
Cauchy estimate is the generic shape of a Li-coefficient computation, for which the map
lists no tool.

**U18 — Assorted zeta rows the map has no line for.**
`riemannZeta_neg_nat_eq_bernoulli` (`HurwitzZetaValues.lean:251`, with the `bernoulli'`
variant at `:240`) — subsumes the trivial-zeros row and gives nonvanishing at negative
**odd** integers directly; positive even special values `riemannZeta_two_mul_nat:206`,
`…'`:217, `riemannZeta_two:226`, `riemannZeta_four:232`; real-axis positivity
`riemannZeta_pos_of_one_lt` (`Dirichlet.lean:336`), `riemannZeta_re_pos_of_one_lt:343`,
`riemannZeta_im_eq_zero_of_one_lt:347`; `differentiableAt_completedZeta`
(`RiemannZeta.lean:93`), `completedRiemannZeta_residue_one:110`,
`completedHurwitzZetaEven_residue_zero` (`HurwitzZetaEven.lean:464`),
`completedZeta_eq_tsum_of_one_lt_re` (`RiemannZeta.lean:189`),
`two_mul_riemannZeta_eq_tsum_int_inv_pow_of_even:226`;
`riemannZeta_eulerProduct_tprod` (`EulerProduct/DirichletLSeries.lean:96`);
`zeta_eq_tsum_one_div_nat_add_one_cpow` (`RiemannZeta.lean:211`),
`zeta_nat_eq_tsum_of_gt_one:220`.

## 4. Surviving negatives

A negative that survives a determined attempt to falsify it is itself evidence, and
this is the part of the record that should be reused. **Every one of the map's twelve
`NOT-FOUND-IN-SCOPE` rows survived**: no reviewer located the named object under
another name, another namespace, or in greater generality. Four of the twelve carry the
imprecise *framing* recorded in §2.1 (D-11, D-12, D-13, D-14), but in each case the
zeta/xi-specific object the row names is absent, and the barrier the row supports keeps
exactly the status the map gives it.

| # | negative | survives as | falsification attempted |
|---|---|---|---|
| N-1 | standard Riemann xi (L147) | fully, as written | `rg 'riemannXi\|RiemannXi'` tree-wide → 0 hits. Only `completedRiemannZeta₀` (`RiemannZeta.lean:63`) exists |
| N-2 | conjugation symmetry for zeta/completion (L148) | fully, as written | `conj`/`starRingEnd` in `Mathlib/NumberTheory/LSeries/*.lean` → 7 hits, all inside theta-kernel *proofs* (`HurwitzZetaOdd.lean:64-66,115,136`; `HurwitzZetaEven.lean:79,94`); none is a statement about `riemannZeta`, `completedRiemannZeta(₀)`, or `hurwitzZetaEven`. `conj` appears in `RiemannZeta.lean` and `ZetaZeros.lean` zero times. The pinned `jacobiTheta₂_conj` (U9) is a theta-level input and does not contradict this |
| N-3 | critical-strip localization (L149) | fully, as written | `rg 'zeroFree\|criticalStrip\|criticalLine'` → 0 hits; the full 27-declaration `riemannZeta*` enumeration contains no zero-localization statement; `ZetaZeros.lean` (74 lines) holds only membership, closedness, discreteness, compact-finiteness, cofinite/cocompact escape |
| N-4 | zeta/xi analytic order equality (L150) | fully, as written | `rg 'analyticOrderAt\|meromorphicOrderAt' \| rg -i 'zeta\|LSeries\|dirichlet'` → 0 hits |
| N-5 | zeta/xi divisor (L151) | fully, as written | `rg 'divisor' Mathlib/NumberTheory/**/*.lean` → only `Nat.divisors`/`divisorsAntidiagonal`; no complex-analytic divisor anywhere in `NumberTheory/`. The object is *formable* from `MeromorphicOn.divisor`; no lemma exists |
| N-6 | multiplicity-aware zero sum (L153) | fully, as written | no zeta/xi zero sum at the pin; the generic side is `locallyFinsuppWithin` + `MeromorphicOn.divisor`, unspecialized |
| N-7 | nontrivial-zero enumeration / counting function (L152) | as a **zeta/xi** negative | `N(T)`-style declaration under `Mathlib/NumberTheory/` → none. Falsified only as a *generic* claim (U2) |
| N-8 | vertical growth, order-one entire growth (L154) | as a **zeta/xi** negative, and as a **definitional** negative | `rg '‖riemannZeta\|isBigO.*riemannZeta'` → only `isBigO_riemannZeta_sub_one_div` (`ZetaAsymp.lean:365`, a local statement near `s = 1`); `rg '‖completedRiemannZeta'` → 0. Separately `rg 'orderOfGrowth\|growthOrder\|entireOrder\|exponentOfConvergence'` → 0 files; "finite order" hits only *pointwise* `meromorphicOrderAt ≠ ⊤`. No complex Stirling / vertical Gamma bound either (U10). The generic strip tool exists (U1); the zeta/xi input it would consume does not |
| N-9 | canonical product / Hadamard factorization (L155) | as an **infinite-product** negative | `rg -i 'canonicalProduct\|elementaryFactor\|weierstrassFactor\|genus'` → only the unrelated Weierstrass ℘-function, Stone-Weierstrass, and `PowerSeries.IsWeierstrassFactorization*` commutative algebra. Falsified only for the *finite* analogue (U3) |
| N-10 | Riemann-Weil explicit formula (L156) | fully, as written | `rg -i 'explicit formula\|guinand\|riemann-von mangoldt\|selberg trace'` → no analytic-number-theory hit. No Perron-type formula either (`rg -i perron` → nothing relevant) |
| N-11 | Li/Keiper coefficients and criterion (L157) | fully, as written | `rg -i 'keiper\|li coefficient'` → 0 hits |
| N-12 | Nyman-Beurling / Báez-Duarte (L158) | as an **objects-and-equivalence** negative | tree-wide case-insensitive `nyman\|beurling\|baez\|duarte` → zero mathematical hits (two Coxeter bibliography lines only). No `Int.fract` Mellin identity in `NumberTheory/`. Falsified only for two generic ingredients (U14, U13) |

Additional absence claims that also survived, outside the twelve-row table:

- Route C's "No such family is currently named" (L374) — CONFIRMED.
- Every "missing specialization" cell in the `GENERIC` table (L130-141) except
  Phragmen-Lindelof (D-8) and fractional part (D-10) — CONFIRMED.
- Barrier rows `S1-CONJ`, `S1-EXPLICIT`, `S2-LI`, `S2-NYMAN` negative content — CONFIRMED.
- Register rows for meromorphic `ζ`, `Λ₀` vs standard `ξ`, multiset/divisor of zeros, sum
  over zeros, Weil test class, Hilbert-space Nyman, density estimates, finite verified
  range — CONFIRMED.
- Addendum fifth: "no conjugation lemma for `riemannZeta`, `completedRiemannZeta(₀)`,
  `hurwitzZetaEven`, or any `LSeries` exists at the pin" — CONFIRMED.
- Gate-0 sign inconsistency: independently re-confirmed by two blocks. Module docstring
  `RiemannZeta.lean:19-20` writes `Λ₀(s) = Λ(s) + 1 / (s - 1) - 1 / s` (both signs
  flipped); inline `:62` and `:88` agree with the theorem at `:84`. The map's
  `Λ(s) = Λ₀(s) - 1/s - 1/(1-s)` is verbatim the theorem, and the theorem remains
  authoritative.

## 5. Disagreements between reviewers, and thin evidence

Recorded rather than reconciled, so the maintainer decides.

**5.1 — L98 `completedRiemannZeta_eq`.** `zeta-core` returned CONFIRMED (the locator and
statement match exactly, which they do). `completion-gamma` returned IMPRECISE on the
ground that the row sits among neighbours that all warn about exceptional-point
hypotheses while this lemma has none, so the omission actively misleads. Both readings
are defensible; the disagreement is about whether "misleading by context" counts as
IMPRECISE. I have recorded it as IMPRECISE (D-1) at low severity because the correction
is one clause and the failure mode (needless case-splitting) is cheap but real.

**5.2 — L137 `WeakFEPair.hasMellin`.** `series-integrals` returned CONFIRMED (both
locators hit; the `WeakFEPair.` prefix is correctly load-bearing since
`StrongFEPair.hasMellin` at `:203` is a distinct declaration). `completion-gamma`
returned IMPRECISE because the row does not say the theorem is gated on `P.k < re s`
and transforms `f - f₀`, while Route B needs `0 < re s < 1`. Recorded as IMPRECISE
(D-9); a reader who takes this row as Route-B raw material is the reader the row should
protect.

**5.3 — L152 and L158.** `series-integrals` returned CONFIRMED for both (the zeta/xi
objects are absent, which they are). `negatives` returned IMPRECISE for both (the
generic machinery the rows implicitly deny is pinned). This is the same
zeta-specific-vs-generic ambiguity as D-12, and I have followed `negatives` (D-11, D-14)
because the summary voice at L29-33 repeats the same phrasing where it is read as
generic.

**5.4 — Evidence that is thin, and one locator dispute.**

- **The second reported defect is not reproduced.** This round verified the map against
  Mathlib, not against downstream notes, so it cannot confirm or deny "two capability
  rows were misread by a later note that thought it had discovered them fresh". What I
  can state: `domains/riemann-hypothesis/UPSTREAM_POOL.md` re-cites, as freshly located
  "pinned ingredients", at least six declarations that are already capability-map rows —
  `analyticOrderAt` (`Order.lean:47`, map L130), `MeromorphicOn.divisor` (map L132),
  `MeromorphicOn.circleAverage_log_norm` (`JensenFormula.lean:307`, map L133),
  `AnalyticOnNhd.sum_divisor_le` (`:389`, map L133), `PhragmenLindelof.vertical_strip`
  (`:275`, map L134), and `mellin` (`MellinTransform.lean:91`, map L135) — and contains
  no cross-reference to the capability map at all (`grep -i "capability map"` → 0 hits).
  That is the plausible mechanism for the reported rediscovery, but I did not verify
  which two rows the report meant, and I am not asserting it did so in error. A
  maintainer wanting that finding nailed down should commission a note-vs-map round.
- **Locator dispute, resolved.** `UPSTREAM_POOL.md` gives `verticalStrip` at
  `Hadamard.lean:68`, `verticalClosedStrip` at `:71`, and
  `norm_le_interpStrip_of_mem_verticalClosedStrip` at `:590`. I checked all three
  directly at the pin: they are `:70`, `:73`, and `:588`. Its `sSupNormIm:77`,
  `norm_le_interp_of_mem_verticalClosedStrip':607`, `namespace Complex :66`, and
  `namespace HadamardThreeLines :67` are correct. Three off-by-two locators in the note,
  not in the map.
- **Locator dispute, against a reviewer.** The `series-integrals` block attributed
  `Complex.multipliable_one_add_of_summable` to `Log/Summable.lean:169`. I checked:
  `namespace Complex` spans `:25`-`:53`, so the `Complex` lemma is at **`:49`**; `:169`
  is the `NormedRing`-namespace variant. The block's U2 item is correct in substance and
  wrong in locator; U12 above records the corrected form. This is a reminder that
  reviewer output is itself unverified until re-grepped.
- **No kernel evidence anywhere in this record.** No Lean toolchain was available. Every
  verdict is source-reading only. Nothing here has the standing of a `lake build`.

## 6. What this record does and does not license

Does: it gives a maintainer a per-row list of proposed amendments to
`MATHLIB_CAPABILITY_MAP.md`, with the evidence attached, plus eighteen groups of pinned
capabilities the map does not currently list.

Does **not**: it does not amend the map; it does not close, reopen, re-scope, or reprice
any barrier — `S1-MULTIPLICITY`, `S1-GLOBAL-ZEROS`, `S1-GROWTH`, `S1-CONJ`,
`S1-EXPLICIT`, `S2-LI`, and `S2-NYMAN` all keep exactly the status and exit evidence the
map records; it does not select or rank a route; it does not claim progress on the
Riemann Hypothesis. The presence of a generic tool at the pin is not a barrier exit, and
no sentence in this record should be quoted as one.
