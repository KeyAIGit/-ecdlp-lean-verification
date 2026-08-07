# RH lane — claims audit, 2026-08-07

**This record amends nothing.** It edits no lane document, changes no status
line, closes no barrier, and applies no proposed replacement. Every "proposed
replacement" below is a proposal only; a delegated maintainer decides what, if
anything, is applied, and each application should be a reviewable change in its
own right. Nothing here selects a route, unparks a route, closes a barrier, or
asserts progress on the truth of the Riemann Hypothesis. `RH-002` remains the
sole ACTIVE task; `S1-CONJ` and `S1-MULTIPLICITY` remain OPEN.

Audit date: 2026-08-07. Repository HEAD at audit time: `ad97231`. Mathlib pin:
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, checkout
`/workspace/leanprover-community/mathlib4` (HEAD confirmed by `git rev-parse`).

---

## 1. Purpose and standard

The lane has been caught three times claiming more than its evidence supports:
a barrier row declared stale when it was not; a claim that a divisor support is
infinite when only local finiteness was established; and a note whose
recommendation rested on a softened negative. This audit hunts the remaining
instances across the lane's document surface.

Severity scale used throughout:

| Sev | Meaning |
|---|---|
| **S0** | Asserted as established but not: progress on RH's truth, a barrier closed without exit evidence, a route selected or unparked, a proof claimed without a kernel verdict. |
| **S1** | Evidence exists but does not cover the claim as stated: overgeneralization, a local bound asserted globally, a finiteness/infinitude claim beyond what is proved. |
| **S2** | Defensible but misleading to a careful reader: growth-ambiguous vocabulary, a CI-verified assertion about a file CI never elaborates, provenance citing a closed or unmerged PR, a status refuted by merged evidence. |
| **S3** | Cosmetic or locator errors. |

---

## 2. Method, coverage, and evidence sources

Four document sets were audited independently, then consolidated here. Each
finding was required to quote the offending sentence verbatim with file and
line, state what the evidence actually supports, and propose exact replacement
text. Findings that could not be substantiated against primary evidence were
dropped rather than hedged.

**Sets and coverage.**

| Set | Documents |
|---|---|
| `triage-sources` | `domains/riemann-hypothesis/ROUTE_TRIAGE.md`, `SOURCE_CONTRACTS.md` |
| `contracts` | `TARGET_BRIDGE_CONTRACT.md`, `XI_PACKAGE_CONTRACT.md`, `CONJ_SYMMETRY_CONTRACT.md` |
| `queue-status` | `tasks/RIEMANN_HYPOTHESIS.md`, `domains/riemann-hypothesis/README.md`, `S0_TRUST_DESIGN.md` |
| `ledger-reviews` | `VERIFIED_RESEARCHOS.md` and the nine RH-lane records under `notes/reviews/` |

**Primary evidence used.** The pinned Mathlib tree (declaration existence,
exact `file:line` locators, whole-tree absence checks); the built modules
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/{TargetBridge,Xi,Conj}.lean`
read in full; `ResearchOS.lean` and `lakefile.toml` for import closure and
default targets; `.github/workflows/ci.yml` for gate wiring;
`data/researchos_result_registry.json` and `scripts/gen_researchos_registry.py
--check`; `scripts/check_ledger_isolation.py`; `git log` / `git show` for merge
provenance and commit SHAs; and the lane's own review records for
cross-checking, never as a substitute for primary evidence.

**Consolidation corrections.** Two bookkeeping errors in the sub-audits were
found and corrected here rather than propagated:

- The `triage-sources` supporting citation for D4 gave
  `MULTIPLICITY_CONTRACT.md:1564-1569` for the withdrawn-infinitude sentence.
  The sentence is at `:1592-1593` (and repeated at `:1787-1788`) at HEAD
  `ad97231`. That file is under active repair by another agent, so its anchors
  drift; the corrected anchors are used below.
- The `contracts` set's prose count ("eight S3") disagreed with its own
  enumeration (nine items, S3-1 … S3-9). The enumeration is authoritative; nine
  are recorded.

**What could not be checked, and why.**

- **No Lean toolchain in this environment.** `lake`, `lean` and `elan` are
  absent. No kernel verdict could be reproduced. Every "kernel-checked" or
  "CI-gated" assertion in this audit was verified *structurally only*: that the
  module is in the import closure of a default lake target (`ResearchOS.lean`,
  `lakefile.toml`), and that the corresponding CI step exists and covers the
  path (`ci.yml:359` no-incomplete-proof scan, `:420` `lake build`, `:428`
  Ecdlp audit, `:438` ResearchOS audit). This audit therefore **cannot** confirm
  that any specific head was green.
- **No workflow run logs were fetched.** Where a review record cites run IDs
  (e.g. `RH_XI_PROMOTION`), the IDs were read but not resolved against GitHub.
- **Merge status was verified against local `git log` only**, not against the
  GitHub API. The cited SHAs (`d6e146fa`, `288d65b`, `202eba0`, `afdae08`,
  `c277b86`) are present on the checked-out branch; that is the whole of the
  verification.
- **Source PDFs are not in the repository**, so the three SHA-256 pins in
  `SOURCE_CONTRACTS.md:66-68` could not be recomputed from artifacts. They were
  checked only for internal consistency with the checksum-replay record.
- **`[D]` desk-level literature claims were not checked against the papers.**
  Findings D1 and D3 below turn on this: they are findings about what the
  documents *assert*, not adjudications of the underlying mathematics.
- **Excluded from edit and from full audit by scope rule:**
  `MULTIPLICITY_CONTRACT.md`, `drafts/RiemannMult.lean`, `drafts/README.md`
  (under repair by other agents) and `MATHLIB_CAPABILITY_MAP.md` (owned by
  another audit). These were read as evidence only.
- **Unaudited lane documents — a real coverage gap.** No set covered
  `domains/riemann-hypothesis/UPSTREAM_POOL.md` (955 lines, added today in
  `ad97231`), `EXPLAINER.md`, `MATHLIB_SEARCH_LOG.md`, `corpus.md`,
  `.mult_queue_entry_draft.md`, or the four files under `drafts/`. The
  `UPSTREAM_POOL.md` gap is the most consequential: it is large, new, and was
  written after every sub-audit's scope was fixed. It should be the first
  target of the next round.

---

## 3. Defects

**Tally: S0 = 0. S1 = 4. S2 = 18. S3 = 18. Total = 40.**

No document in the audited surface claims progress on the truth of RH as an
established result, describes a barrier as closed without its exit evidence,
selects or unparks a route, or claims a proof for which no kernel verdict is
recorded. One finding (**D1**) sits on the S0 boundary and is argued as such
below; the maintainer should make that call explicitly rather than inherit it.

### 3.1 S1 — evidence does not cover the claim as stated

All four are in the `triage-sources` set.

---

#### D1 — `domains/riemann-hypothesis/ROUTE_TRIAGE.md:228-229` — nonexistence asserted where only non-knowledge is supported

> `  `β > 1/2` the exclusion holds only up to bounded height; no uniform`
> `  vertical-strip zero-free region `σ ≥ σ₀ < 1` exists;`

**What the evidence supports.** The cited literature (de la Vallée Poussin;
Vinogradov-Korobov, both `[D]`) supports only that no such region is *known*.
Nonexistence is proved nowhere in the lane. This is not a neutral slip: if RH
holds, the region `σ ≥ 1/2 + ε` is zero-free and uniform in `t`, so the clause
as written **entails ¬RH**. It also contradicts this document's own line 301
("this literature gap is not an impossibility proof"). The second clause has
the same defect — "the exclusion holds only up to bounded height" is a
statement about what has been proved, not about what is true.

**Severity.** Recorded **S1**, and flagged as the audit's single S0 boundary
case. Under a literal reading a sentence entailing ¬RH, stated in the
indicative, is a claim about RH's truth asserted as established, which is S0 by
definition. The reason it is recorded at S1 is that the surrounding paragraph
is explicitly a survey of what the literature excludes, so a charitable reader
supplies "is known". The audit declines to soften this to a wording nit and
declines to inflate it to S0 unilaterally: **the grading is the maintainer's
call and should be made on the record.** The proposed replacement removes the
ambiguity either way.

**Proposed replacement (lines 228-231):**
> `  `β > 1/2` the published exclusions reach only bounded height; no uniform`
> `  vertical-strip zero-free region `σ ≥ σ₀`, `σ₀ < 1`, is known — whether one`
> `  exists is open, and RH would imply one, so this is a gap in the literature`
> `  and not an impossibility result;`

---

#### D2 — `ROUTE_TRIAGE.md:46-48` — locator/checksum status extended to sources that have neither

> `Sources already pinned with locators and checksums (`LAG07`, `BOM-CLAY`,`
> ``BD02-v2` in `SOURCE_CONTRACTS.md`; `RH-SRC-001..008` in `corpus.md`) are`
> `cited by those IDs.`

**What the evidence supports.** Checksums and normative locators exist for
exactly three sources — `LAG07`, `BOM-CLAY`, `BD02-v2`
(`SOURCE_CONTRACTS.md:64-69`; 3/3 SHA-256 matches in
`RH_SOURCE_PDF_CHECKSUM_REPLAY_2026_08_05.md`). The `corpus.md` register
(`corpus.md:47-54`) carries a URL and a read-state column only — no checksum,
no page or theorem locator — and says outright "publisher record available;
**exact theorem extraction required**" for `RH-SRC-003` and `RH-SRC-004`. This
is load-bearing: the sentence is the exemption clause that keeps `RH-SRC-00x`
citations out of the `[D]` locator-replay obligation, and the very next section
cites "Li 1997 (`RH-SRC-003`, Thm 1)" (`:65`) and Bombieri-Lagarias
(`RH-SRC-004`, `:67`) as if locator-pinned.

**Proposed replacement:**
> `Sources pinned with normative locators and audited PDF checksums (`LAG07`,`
> ``BOM-CLAY`, `BD02-v2` in `SOURCE_CONTRACTS.md`) are cited by those IDs. The`
> ``corpus.md` register IDs `RH-SRC-001..008` are URL-pinned only: no checksum,`
> `and no page-level locator except where they coincide with the three audited`
> `PDFs (`RH-SRC-001` = `BOM-CLAY`, `RH-SRC-005` = `BD02-v2`). Any load-bearing`
> `theorem citation to a `RH-SRC-00x` ID therefore counts as a `[D]` desk`
> `citation and must have its exact locator replayed before finality.`

---

#### D3 — `ROUTE_TRIAGE.md:237-240` — a support-dependent bound asserted to be dominated globally

> `Connes-Consani`
> `  finite/low-frequency positivity `[D]` is support/bandwidth-restricted, so`
> `  it can only certify zero-freeness already covered by bounded-height`
> `  verification (`RH-SRC-007`); the support parameter does not tend to`
> `  infinity with controlled constants;`

**What the evidence supports.** Support/bandwidth restriction supports only
that the certifiable range is bounded by a height depending on the support
parameter. The stronger claim — that this height lies inside the `RH-SRC-007`
verified range (3·10¹²) — requires a quantitative comparison. No constant, no
locator, and no replay of this `[D]` citation appears anywhere in the record.

**Proposed replacement:**
> `Connes-Consani`
> `  finite/low-frequency positivity `[D]` is support/bandwidth-restricted, so`
> `  any zero-freeness it certifies is confined to a bounded height determined`
> `  by the support parameter; no explicit constant for that height is on`
> `  record here, so it has not been compared with the `RH-SRC-007` verified`
> `  range, and the support parameter does not tend to infinity with controlled`
> `  constants;`

---

#### D4 — `SOURCE_CONTRACTS.md:119-120` — infinitude of the divisor support asserted, not proved

> `A Lean `Multiset` cannot`
> `represent the infinite divisor.`

**What the evidence supports.** At the pin, Mathlib gives only **local**
finiteness of the zero set: `isClosed_riemannZetaZeros`
(`Mathlib/NumberTheory/LSeries/ZetaZeros.lean:57`),
`isDiscrete_riemannZetaZeros` (`:60`),
`IsCompact.inter_riemannZetaZeros_finite` (`:64`). This document nowhere
derives infinitude — `SC-XI-01` item 2 imports only the *upper* bound
`N_xi(T) ≤ C·T·log T`. Infinitude does follow classically from `LAG07`
Theorem 2.1(4)/(2.11) (replay-confirmed), but the contract does not cite it for
this purpose. **This is a recurrence of the exact defect the lane was already
caught on**, and the withdrawal is on the record elsewhere:
`MULTIPLICITY_CONTRACT.md:1592-1593` (repeated `:1787-1788`) — "**Nothing here
establishes, asserts, or implies that the ξ or ζ divisor support is
infinite.**" Reported, not edited: the multiplicity contract is under repair by
another agent, but the offending sentence flagged here is in
`SOURCE_CONTRACTS.md`, which is in scope.

**Proposed replacement:**
> `A Lean `Multiset` may not be used: nothing here proves the support finite,`
> `and only local finiteness is available at the pin`
> `(`Mathlib/NumberTheory/LSeries/ZetaZeros.lean:57,60,64`), so the packaging`
> `must be a locally finite divisor. Infinitude of `S_xi` is not asserted here,`
> `is not proved in pinned Mathlib, and is not needed by any row below.`

---

### 3.2 S2 — defensible but misleading

| # | Set | file:line | Verbatim | What the evidence supports | Proposed replacement |
|---|---|---|---|---|---|
| D5 | triage | `ROUTE_TRIAGE.md:16-19` | "Candidates admitted from `RH-001` (exactly three, per the capability map's "RH-002 admission decision" table): Weil-first Li positivity, Nyman-Beurling/Báez-Duarte closure, and the explicit-formula-plus-global-inequality family." | The cited table says the opposite. `MATHLIB_CAPABILITY_MAP.md:412` — "**Only two receive candidate status.**" Two rows carry `ADMIT` (`:423` Weil-first Li, `:424` Nyman-Beurling capped at 20%); the third (`:425`) reads "`PARK` as a direct route; `REQUIRED DEPENDENCY SCREEN` for Li" — a pre-cycle disposition, not an admission. Three families were screened; two were admitted. | "Route families screened in `RH-002` (three, per the capability map's "RH-002 admission decision" table, which admits two as candidates and had already parked the third): Weil-first Li positivity (`ADMIT` as the main direct screen) and Nyman-Beurling/Báez-Duarte closure (`ADMIT` as a pilot capped at 20% of later execution budget), plus the explicit-formula-plus-global-inequality family, carried at its pre-cycle disposition "`PARK` as a direct route; `REQUIRED DEPENDENCY SCREEN` for Li" and re-screened here." |
| D6 | triage | `ROUTE_TRIAGE.md:187-189` | "de-risked by the present Abel-summation machinery `LSeries_eq_tsum...`/`LSeries_eq_mul_integral`, `Mathlib/NumberTheory/LSeries/SumCoeff.lean:137`)" | `LSeries_eq_mul_integral` exists exactly at that locator (verified). **No declaration beginning `LSeries_eq_tsum` exists anywhere in Mathlib at the pin** — whole-tree grep returns zero hits. The upstream capability-map addendum (`:493-494`) cites only `LSeries_eq_mul_integral`. A name with no referent is presented as present-at-the-pin API. | "de-risked by the present Abel-summation machinery `LSeries_eq_mul_integral`, `Mathlib/NumberTheory/LSeries/SumCoeff.lean:137`)" |
| D7 | triage | `ROUTE_TRIAGE.md:191-193` | "These are formalization-only items, ordered strictly after the route-neutral bridge and `S0-TRUST`, and are not progress on RH." | **Both stated preconditions are now discharged** — `S0-TRUST` CLOSED 2026-08-05 (PR #298, `d6e146fa`), route-neutral bridge merged as PR #299 (`288d65b`). A reader today reads the ordering clause as a queue position that has come up. Nothing authorizes that: `tasks/RIEMANN_HYPOTHESIS.md:17-29` records `RH-002` as `PARK`/`PARK`/`PARK`, "no route execution is authorized", and forbids "new equivalence formalization". This is the audit's clearest case of stale hedging that flips direction into an overclaim. | "These are formalization-only items and are not progress on RH. They are unscheduled and unauthorized: the route-neutral bridge and `S0-TRUST` are now complete, but no `SC-NB` work may begin while the `RH-002` dispositions are under independent review, and each item would require its own preregistered task." |
| D8 | contracts | `TARGET_BRIDGE_CONTRACT.md:3-8` | "Status: **DRAFT v2 (2026-08-05) — non-built review artifact … Not Lean-checked. No file in `Ecdlp/`, `ResearchOS/`, or any built target may be created from this document before independent review (RH-003 exit).**" | False. `288d65b` (PR #299, merged 2026-08-05) added `ResearchOS/…/TargetBridge.lean` (206 lines, eight declarations); `ResearchOS.lean` imports it, `ResearchOS` is a default lake target, so CI elaborates, sorry-scans (`ci.yml:359`) and axiom-audits it (`:436-438`). `MATHLIB_CAPABILITY_MAP.md:384,533-551` records `S1-TARGET` CLOSED by that PR. The file was edited again after the merge (`a29ebfc`, PR #302) and the status left untouched. | "Status: **v2 (2026-08-05) — retained specification artifact. Adversarially reviewed once (verdict `SOUND_WITH_FIXES`, all five findings applied; see Annex B). The built counterpart merged as PR #299 (`288d65b`) into `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/TargetBridge.lean` (P1-P5 plus three recorded corollaries; eight declarations) after the RH-003 exit review, and passed the full build, the no-incomplete-proof scan, ResearchOS inverse ledger coverage and both axiom audits with every `RH-BRIDGE-*` row at axiom base `standard`. The separate `S0-TRUST` prerequisite was satisfied by merged PR #298 (`d6e146fa`) on 2026-08-05.**" |
| D9 | contracts | `TARGET_BRIDGE_CONTRACT.md:690-692` | "Nothing here is claimed proved until the kernel checks it in the RH-004 built PR after independent review." | The RH-004 built PR is #299 (`288d65b`); the kernel has checked it, and `notes/reviews/RH_BRIDGE_PROMOTION_2026_08_06.md` is the promotion record cited by the eight `RH-BRIDGE-*` ledger rows. | "These obligations were kernel-checked by the merged RH-004 promotion PR #299 (`288d65b`) after independent review; the contract itself remains the retained specification artifact." |
| D10 | contracts | `CONJ_SYMMETRY_CONTRACT.md:3` | "Status: **DRAFT v2 (2026-08-06) — non-built review artifact. Not Lean-checked. Independent statement review is complete; built promotion remains blocked until the preconditions carried from `TARGET_BRIDGE_CONTRACT.md` / `XI_PACKAGE_CONTRACT.md` are met and the real module passes kernel and axiom CI.**" | `c277b86` (PR #307, merged 2026-08-06) added `ResearchOS/…/Conj.lean` (458 lines, sixteen public declarations matching Z1-Z9). Both carried preconditions had landed: bridge #299, xi #304. Map `:595-618` records the promotion. The file's last commit `7bf13ab` (#301) predates the promotion. **The accompanying barrier claim is correct and must be preserved: `S1-CONJ` remains OPEN.** | "Status: **v2 (2026-08-06) — retained specification artifact. Independent statement review is complete, and the built counterpart merged as PR #307 (`c277b86`) into `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Conj.lean` (the sixteen Z1-Z9 declarations) after both carried preconditions landed — the target bridge in PR #299 (`288d65b`), the xi package in PR #304 (`afdae08`) — and after the head passed the full build, the no-incomplete-proof scan, ResearchOS inverse ledger coverage and both axiom audits with every `RH-CONJ-*` row at axiom base `standard`. Promotion does **not** close the barrier: `S1-CONJ` remains OPEN, see the Barrier-closure boundary below.**" |
| D11 | contracts | `CONJ_SYMMETRY_CONTRACT.md:692` | "Nothing here is claimed proved until the kernel checks it in a built PR after independent review, bridge (P1-P5) landing (for Z8), xi-package landing (for Z7/Z9-xi), and closure of the carried preconditions." | All four conditions are satisfied and the module is merged. | "These obligations were kernel-checked by the merged promotion PR #307 (`c277b86`), after independent review, bridge (P1-P5) landing in PR #299 (for Z8), xi-package landing in PR #304 (for Z7/Z9-xi), and closure of the carried preconditions; the contract itself remains the retained specification artifact. Kernel verification of the package does not close `S1-CONJ`." |
| D12 | contracts | `CONJ_SYMMETRY_CONTRACT.md:3` | "The internal adversarial verdict was `SOUND_WITH_FIXES` with zero S0/S1/S2 findings" | The contract's own Annex B (`:707-710`) records **four** findings on a different scale: F1 (LOW) a wrong `linear_combination` sign in the Z3 skeleton, F2 (LOW), F3/F4 (INFO). That review never graded on S0-S3, so "zero S0/S1/S2" is a retroactive mapping the record does not carry — and it contradicts the lane's applied convention: `TARGET_BRIDGE_CONTRACT.md:709-710` grades an elaboration bug and two uncited glue lemmas **S2**; `XI_PACKAGE_CONTRACT.md:693-699` grades a cosmetic locator range **S2**. F1 required correction by the acceptance pass (`:716-718`). What is supported is: no statement-level finding. | "The internal adversarial verdict was `SOUND_WITH_FIXES` with no statement-level finding — no declaration name, binder, hypothesis, conclusion or claim boundary was challenged. All four findings were proof-skeleton or locator fixes (Annex B), of the class the sibling bridge and xi reviews scored S2/S3. The external acceptance pass then synchronized both proof skeletons, including the corrected F1 sign (Annex B and the dated acceptance note below)." |
| D13 | queue | `tasks/RIEMANN_HYPOTHESIS.md:14-15` | "Decision update: 2026-08-06. `RH-001`, `RH-003`, `RH-004`, `RH-006`, `RH-007`, and `RH-008` are complete." | One merged lane change behind `main`: `ab58e8c` (2026-08-07) merged `MULTIPLICITY_CONTRACT.md` (+1831) and `drafts/RiemannMult.lean` (+1006). No task covers it and the block records no line for it, although `.mult_queue_entry_draft.md:7-9` states that installing the matching entries "also requires a dated line in the **Current decision** block". A reader concludes nothing has landed since 2026-08-06. | "Decision update: 2026-08-07. `RH-001`, `RH-003`, `RH-004`, `RH-006`, `RH-007`, and `RH-008` are complete. A non-built S1-MULTIPLICITY statement surface (`MULTIPLICITY_CONTRACT.md`, `drafts/RiemannMult.lean`) merged on 2026-08-07 as `ab58e8c`; it is an offered artifact with no queue entry, no acceptance record, and no kernel verdict, and it neither activates a task nor moves the ACTIVE slot." |
| D14 | queue | `tasks/RIEMANN_HYPOTHESIS.md:380-381` | "The exact promotion head must pass the full build, no-incomplete-proof gate, and both axiom audits before merge." | RH-008 is marked COMPLETE 2026-08-06 (`:370`) but its closure-evidence paragraph is written prospectively and cites no PR, commit or record — unlike RH-004 (`:241`) and RH-007 (`:325-326`). The evidence exists: PR #307 = `c277b86`; `ResearchOS.lean:9` imports `Conj.lean`; sixteen `RH-CONJ-*` rows in `VERIFIED_RESEARCHOS.md` and the registry; record `notes/reviews/RH_CONJ_PROMOTION_2026_08_06.md`. | "Closure evidence: merged PR #307 (`c277b86`). The built module `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Conj.lean`, sixteen `RH-CONJ-*` ledger rows at axiom base `standard`, inverse registry coverage, the regenerated axiom audit, the synchronized draft, and `notes/reviews/RH_CONJ_PROMOTION_2026_08_06.md` landed together, and the full build, no-incomplete-proof gate, and both axiom audits were green on the merged head. This closes no named barrier: the divisor-invariance half of `S1-CONJ` remains open." |
| D15 | queue | `tasks/RIEMANN_HYPOTHESIS.md:25-26` | "The reviewed RH-008 reconciliation builds and audits the sixteen Z1-Z9 conjugation declarations." | Same gap in the current-decision block: present tense, no merge provenance, while the parallel RH-007 sentence at `:22-24` cites "merged PR #304 (`afdae08`)". | "`RH-008` completed through merged PR #307 (`c277b86`): its sixteen Z1-Z9 conjugation declarations are built, ledgered, registry-covered, and axiom-audited." |
| D16 | queue | `domains/riemann-hypothesis/README.md:3-4` | "Status: **exploratory; Stage 0 evidence package assembled. RH-001, RH-003, RH-004, RH-006, and RH-007 are closed; RH-002 is active only for independent review of the three retained `PARK` dispositions.**" | RH-008 is missing. `tasks/RIEMANN_HYPOTHESIS.md:370` marks it COMPLETE 2026-08-06 and PR #307 (`c277b86`) is on `main`. The domain-boundary document understates the closed set. | "Status: **exploratory; Stage 0 evidence package assembled. RH-001, RH-003, RH-004, RH-006, RH-007, and RH-008 are closed; RH-002 is active only for independent review of the three retained `PARK` dispositions.**" |
| D17 | queue | `domains/riemann-hypothesis/README.md:20-21` | "The built target reformulations and kernel-checked xi equivalence package are foundation interfaces only." | The built RH surface is three modules and 36 ledgered declarations: `TargetBridge.lean` (8 `RH-BRIDGE-*`), `Xi.lean` (12 `RH-XI-*`), `Conj.lean` (16 `RH-CONJ-*`), all imported from `ResearchOS.lean:7-9` (counts re-verified). A reader concludes the conjugation package is not on the built surface. | "The built target reformulations, the kernel-checked xi equivalence package, and the kernel-checked conjugation-symmetry package are foundation interfaces only." |
| D18 | queue | `domains/riemann-hypothesis/README.md:87-88` | "PR #299 satisfies that rule for the target bridge, and PR #304 satisfies it for the twelve-declaration xi package." | The rule ("No RH theorem is added to the built surface until a domain ledger and axiom audit cover it") is satisfied for all three packages — the sixteen `RH-CONJ-*` rows and audit lines landed in #307 — but the enumeration stops at #304, leaving 16 of 36 built RH declarations unaccounted for in the document that states the rule. Same omission at `:61-62`, which never names the conjugation package or `S1-CONJ`, though map `:595` carries "Addendum 2026-08-06 (fifth): `S1-CONJ` conjugation leg landed — barrier STILL OPEN". | `:87-88` → "PR #299 satisfies that rule for the target bridge, PR #304 for the twelve-declaration xi package, and PR #307 for the sixteen-declaration conjugation package." Append to `:62`: "The conjugation package was promoted in PR #307 (`c277b86`) as sixteen built declarations with ledger, registry, full-build, and axiom-audit coverage; it supplies the conjugation leg and pointwise order transport only, so `S1-CONJ` remains open on divisor invariance under `ρ ↦ 1 − conj ρ` and `S1-MULTIPLICITY` remains open." |
| D19 | ledger | `notes/reviews/RH_CONJ_PROMOTION_2026_08_06.md:44-45` | "`1 − s` enters the package only in Z8, through the already kernel-checked bridge P3, after conjugation is established." | False as written. `1 − w` occurs inside Z3 at `Conj.lean:195` (`… = Gammaℝ w * riemannZeta w + 1 / w + 1 / (1 - w)`, verified) and again in Z4 at `:236-240`. What *is* substantiated is the load-bearing claim: the **reflection** `s ↦ 1 − s` is confined to Z8 — no `*_one_sub` lemma occurs anywhere in `Conj.lean` outside Z8's two uses of bridge P3 (`:313`, `:315`). | "The **reflection** `s ↦ 1 − s` enters the package only in Z8, through the already kernel-checked bridge P3, after conjugation is established; the `1 − w` occurrences in Z3's `key` and in Z4 are the pole terms of `completedRiemannZeta_eq`, not the functional equation." |
| D20 | ledger | `VERIFIED_RESEARCHOS.md:60` (`RH-CONJ-Z3`, `claim_scope`) | "Conjugation symmetry of the entire pole-removed completion; proved by an independent puncture-free identity-theorem pass." | The pass is its own (over `Set.univ`, no puncture, `Conj.lean:181-192`) but not independent of the package: `Conj.lean:216` closes `hfg` with `rw [key _ hz', key _ hz, Gammaℝ_conj, riemannZeta_conj]`, consuming Z1 and Z2. The review record uses the accurate wording (`RH_CONJ_PROMOTION:52-53`). | "Conjugation symmetry of the entire pole-removed completion; proved by its own puncture-free identity-theorem pass over all of ℂ, consuming Z1 and Z2 on the half-plane 1 < re s." |
| D21 | ledger | `notes/reviews/RH_CONJ_PROMOTION_2026_08_06.md` — §4 "Kernel check", file ends at line 89 with no completion section | "The verdict is delivered by CI on this promotion change: `lake build` compiles the module, the no-incomplete-proof gate scans it … If any gate is red, no row is counted." | The record states the *intended* verdict, never a delivered one, yet sixteen ledger rows (`VERIFIED_RESEARCHOS.md:57-72`) carry `status = proved` and name this file as their `review_record`. Both sibling records do record the verdict: `RH_BRIDGE_PROMOTION:60-63` ("passed `lake build`, the no-sorry gate, and both axiom audits, and was squash-merged as PR #299 (`288d65b`)"), `RH_XI_PROMOTION:81-87` (head `1aed6d6d…`, run IDs `31077632257` / `31077632309`, squash `afdae08`). Independently confirmable here: `Conj.lean` is in the built import closure, all 16 declarations are audited, `gen_researchos_registry.py --check` passes. **No kernel verdict for PR #307 is recorded anywhere in the repository**; `tasks/RIEMANN_HYPOTHESIS.md:378-381` likewise states the gate prospectively while marking RH-008 COMPLETE. See §5 note on why this is S2 and not S0. | Append, mirroring the two sibling records: "## Completion note — The final head of PR #307 passed the full `lake build`, the no-incomplete-proof scan, `scripts/gen_researchos_registry.py --check` inverse coverage, and both generated axiom audits with all sixteen new rows at axiom base `standard`; it was squash-merged as `c277b86`. Record the exact head SHA and the two workflow run IDs here. Until those identifiers are recorded, the sixteen `RH-CONJ-*` rows rest on the merged-CI requirement alone and no run is cited as evidence." |
| D22 | ledger | `notes/reviews/RH001_INDEPENDENT_REPLAY_2026_08_05.md:61-63` | "**Candidate count**: the map's RH-002 admission table admits exactly three route families, satisfying the RH-001 output bullet "no more than three candidates admitted to RH-002"." | Same conflation as D5, independently instantiated. The table lists three and admits two (`MATHLIB_CAPABILITY_MAP.md:411-412`, text unchanged since the commit that added this replay record). The conclusion survives either way; the count under the heading "Candidate count" does not. | "**Candidate count**: the map's RH-002 admission table lists exactly three route families and gives `ADMIT` candidate status to two of them (the third, explicit formula plus a global inequality, is `PARK` as a direct route with a required dependency screen). Either count satisfies the RH-001 output bullet "no more than three candidates admitted to RH-002"." |

---

### 3.3 S3 — cosmetic and locator

| # | Set | file:line | Defect | Proposed replacement |
|---|---|---|---|---|
| D23 | triage | `ROUTE_TRIAGE.md:93` | "**Death conditions already triggered at desk time** (4 of 6 from the admission row)" — the four quoted strings merge two distinct row items ("finite positive coefficients or PSD blocks" and "numerics"), so they cover **five** of six; only "a rearranged conditional sum" is untriggered. Understates; nothing downstream breaks. | Replace `(4 of 6 from the` with `(5 of 6 from the` and note that "finite positive coefficients or PSD blocks, numerics" covers two row items. |
| D24 | contracts | `XI_PACKAGE_CONTRACT.md:619` and `:564` | X11 dependency list cites `DifferentiableAt.comp` (FDeriv/Comp.lean:127), superseded per Annex C by `DifferentiableAt.fun_comp'` (`:122`), which is what merged `Xi.lean:278` and `drafts/RiemannXi.lean:301` call. The contract lists a declaration its artifact does not use and omits the one it does. | `:619` two rows — "\| `DifferentiableAt.fun_comp'` \| …Comp.lean:122 \| X11 (post-Annex-C repair) \|" and "\| `DifferentiableAt.comp` \| …Comp.lean:127 \| superseded by `fun_comp'` — see Annex C \|". `:564` — replace `` `DifferentiableAt.comp` (FDeriv/Comp.lean:127) `` with `` `DifferentiableAt.fun_comp'` (FDeriv/Comp.lean:122) ``. |
| D25 | contracts | `XI_PACKAGE_CONTRACT.md:527` | Off-by-one: line 121 is the `@[fun_prop]` attribute; the declaration is at `:122`. Worth recording explicitly because `variable (x)` is in force from `:45` to `:224`, which is the actual reason Annex C's repair was needed. | "-- required by the pinned composition API (`DifferentiableAt.fun_comp'`, FDeriv/Comp.lean:122; its section point is explicit: `variable (x)` is in force from :45 through :224)" |
| D26 | contracts | `XI_PACKAGE_CONTRACT.md:539-541`, `:570` | X11 `hstrip` skeleton uses `.inter`; merged `Xi.lean:308-313` and `drafts/RiemannXi.lean:331-334` use `IsOpen.and` (`Topology/Basic.lean:116`), "avoiding the `∩`-vs-set-builder defeq gap of `.inter` entirely". `IsOpen.and` is absent from the pinned API table and `:570` still presents F3(a) as a live defeq risk. | Replace the `hstrip` block with the `IsOpen.and` form; add table row "\| `IsOpen.and` \| Mathlib/Topology/Basic.lean:116 \| X11 (`hstrip`) \|"; at `:570` replace the F3(a) clause with "(a) `hstrip` — **discharged syntactically**: `IsOpen.and` (Topology/Basic.lean:116) is stated on set-builders `{x \| p x ∧ q x}`, so the `∩`-vs-set-builder defeq gap of `.inter` never arises". |
| D27 | contracts | `XI_PACKAGE_CONTRACT.md:294-296` | X6 skeleton uses tactic-`match`; merged `Xi.lean:127-132` uses `cases n with`, and `Xi.lean:128` records why it is load-bearing: "`cases` substitutes in `hs0`/`htriv`, unlike a tactic-`match` on the goal alone". | Replace with the `cases n with \| zero … \| succ m …` form, carrying the substitution comment. |
| D28 | contracts | `XI_PACKAGE_CONTRACT.md:333` | Locator range includes a blank line: the `s = 1` split occupies `Nonvanishing.lean:412-414`; `:415` is blank. `TARGET_BRIDGE_CONTRACT.md:307` cites the correct range. | "… (Nonvanishing.lean:412-414)." |
| D29 | contracts | `CONJ_SYMMETRY_CONTRACT.md:38-40`; `XI_PACKAGE_CONTRACT.md:41-42` | Proposed preambles cannot elaborate their own skeletons. CONJ's Z2/Z3 use `𝓝` (Topology scope) and `eventually_of_mem` (`Filter`); merged `Conj.lean:46-50` records both opens as "deviation from contract preamble". XI's X11 uses `=ᶠ[𝓝 s]` and `filter_upwards`; merged `Xi.lean:27-28` is `open Complex Filter` / `open scoped Real Topology`. | CONJ: `open Complex` / `open Filter` / `open scoped Real ComplexConjugate Topology`. XI: `open Complex Filter` / `open scoped Real Topology`. |
| D30 | contracts | `TARGET_BRIDGE_CONTRACT.md:596-638` | Pinned API table out of sync with the merged module: `TargetBridge.lean:52` uses `Complex.cpow_ne_zero_iff` (`Pow/Complex.lean:49`) as primary, with the contract's `cpow_eq_zero_iff` surviving only as the commented alternate at `:54-55`; `:74/120/154` use `Complex.mul_re` (`Data/Complex/Basic.lean:214`) and `Complex.natCast_im` (`:357`). None of the three is in the table. | Add three rows: `Complex.cpow_ne_zero_iff` (Pow/Complex.lean:49, P1 primary; `cpow_eq_zero_iff` :45 the recorded alternate); `Complex.mul_re` (Basic.lean:214, P2-a/P4-a); `Complex.natCast_im` (Basic.lean:357, P2-a/P4-a). |
| D31 | contracts | `TARGET_BRIDGE_CONTRACT.md:38` | "All five theorems are unconditional consequences of pinned Mathlib theorems" — the contract itself states three further declarations (`:331`, `:483`, `:502`) and the merged module carries eight, as map `:538` records. The claim boundary does not extend to the corollaries. | "- **Claim boundary.** All five numbered theorems and their three recorded corollaries (eight declarations in total) are unconditional consequences of pinned Mathlib theorems; none touches multiplicity, growth, zero counting, or any route's research obligation." |
| D32 | contracts | `CONJ_SYMMETRY_CONTRACT.md:18` | "a real-positive cpow base" — the base is `(n : ℂ)` for `n : ℕ`, which is `0` at `n = 0`. The contract's own design note at `:197` relies on `Complex.natCast_arg` (`Arg.lean:226`, unconditional) precisely so `n = 0` needs no split; `Complex.cpow_conj` needs only `x.arg ≠ π`. | "- **Mechanism.** The Dirichlet series `zeta_eq_tsum_one_div_nat_cpow` has termwise-real coefficients and a real-**nonnegative** cpow base `(n : ℂ)` — including `n = 0`, whose `arg` is `0 ≠ π` by `natCast_arg`, so no term is split off — hence `conj ∘ ζ ∘ conj` agrees with `ζ` on the open half-plane `1 < re s`;" |
| D33 | queue | `S0_TRUST_DESIGN.md:3-6` | "**Status: PROPOSED design v2 … No file in this design has been created or modified; implementation is NOT authorized by this document (§5).**" — the design was implemented and merged (`d6e146fa`, PR #298): the four scripts, `ResearchOS/LedgerAxiomAudit.lean`, the registry and `VERIFIED_RESEARCHOS.md` all exist, and `ci.yml:282,293-294,436-441` run the gates. Corrected two lines later at `:12-13`, so this is header ordering — but the first status line a scanner reads is false. | "**Status: IMPLEMENTED (design v2, 2026-08-05; adversarially reviewed once, verdict `SOUND_WITH_FIXES`, all seven findings applied — Annex A). Implemented and merged in PR #298 (`d6e146fa`); see the implementation addendum below. The pre-implementation wording of §0-§6 is retained as design provenance, not as current repository state.**" |
| D34 | queue | `S0_TRUST_DESIGN.md:7`, `:123`, `:124`, `:158`, `:186`, `:399` | Every cited `README.md` anchor is wrong at HEAD and matches no revision of the README: the `metrics_source` clause is at `:89-90` (verified), the future-modules clause at `:84-85`, the `RH-` prefix bullet at `:83`, the independent-review clause at `:71-73`. `README.md:74-75` is now "A conditional implication does not count as progress when its premise merely hides RH…" (verified). | `:7` → `README.md:89-90`; `:123` → `:83-85`; `:124` → `(README.md:89-90)`; `:158` → `(README.md:83)`; `:186` → `per README.md:71-73`; `:399` → `of README.md:89-90`. |
| D35 | queue | `S0_TRUST_DESIGN.md:221`, `:336-337`, `:344`, `:489` | `ci.yml` anchors moved when Phase 1 landed. Actual, re-verified: no-sorry grep `:359`; `lake build` `:420`; ECDLP audit `:426-431`; ResearchOS audit `:436-441`; registry `--check` `:282`; isolation `:293-294`; cross-import guard `:378-383`. §0's findings are covered by the `:13` provenance disclaimer, but §3 and §6 read as live gate locations. | Replace `ci.yml:343`→`:359`, `:387`→`:420`, `:393-398`→`:426-431`, `:274-278`→`:278-282`, `:352-358`→`:368-374` throughout §3 and §6, and prefix §6 with "Post-implementation anchors (verified 2026-08-07)". |
| D36 | queue | `S0_TRUST_DESIGN.md:454-456` | Finding F1 (`:38`) names six stale documents including "`ABSTRACT_SCOPE.md:18`, `Ecdlp/AxiomAudit.lean:8-10` itself"; the Phase-1 remediation list drops both. `ABSTRACT_SCOPE.md:18` was in fact fixed, but `Ecdlp/AxiomAudit.lean:9-10` still reads "CI runs it standalone (`lake env lean Ecdlp/AxiomAudit.lean`)" and no workflow invokes it — the only `.github/workflows/` mention is the comment at `ci.yml:355`. The file F1 identified as the source of the stale CI claim is the one the design's own list forgot. | Append "…, `ABSTRACT_SCOPE.md:18`, and the F1 self-description in `Ecdlp/AxiomAudit.lean:8-10`, which must stop describing itself as CI-executed" to the remediation list. |
| D37 | queue | `S0_TRUST_DESIGN.md:259-262` | "replaces glob-based exemptions with the **exact path set** `{Ecdlp/AxiomAudit.lean, Ecdlp/LedgerAxiomAudit.lean, ResearchOS/LedgerAxiomAudit.lean}` wherever it controls a gate" — the implementation used two basename excludes instead (`ci.yml:359`, `:383`: `--exclude='AxiomAudit.lean' --exclude='LedgerAxiomAudit.lean'`, re-verified). The ADV-2 property still holds, via §4.6 only: `scripts/check_ledger_isolation.py:41-43` carries the exact three-path whitelist. The text asserts a mechanism the merged code does not use. | Append an implementation note recording that PR #298 narrowed the `ci.yml` globs to the two exact basenames and that the exact three-path set is enforced by the §4.6 whitelist, which fails on any other `*AxiomAudit.lean` file. |
| D38 | queue | `tasks/RIEMANN_HYPOTHESIS.md:218-219`; `S0_TRUST_DESIGN.md:12` | Three dates for one merge: PR #298 merged as `d6e146fa` with commit date **2026-08-05** (also used at `S0_TRUST_DESIGN.md:12` and map `:382` "CLOSED 2026-08-05"), while the task text says "satisfied as of 2026-08-06" and the map's narrative addendum is headed 2026-08-06. Related: `tasks:22` and `:54` cite `RH006_SOURCE_CONTRACT_ACCEPTANCE_2026_08_06.md` as a bare basename; the file is under `notes/reviews/`. | "The `S0-TRUST` precondition is satisfied: PR #298 merged 2026-08-05 as `d6e146fa`; the capability map's closure addendum recording it is dated 2026-08-06." Spell the review path in full at `:22` and `:54`. |
| D39 | ledger | `VERIFIED_RESEARCHOS.md:67` (`RH-CONJ-Z8`), same for `:68` (`Z8P`) | "Set-level fourfold zero action inside the open critical strip" — `riemannZeta_fourfold_zero` (`Conj.lean:306-315`) is a pointwise conjunction of three zero-equations under `0 < ρ.re`, `ρ.re < 1`, `riemannZeta ρ = 0`; no set occurs in the statement. The ledger's own vocabulary reserves "Set-level" for genuine set equalities (`:63-64`) and uses "Membership-level" at `:62`. Under-claims rather than over-claims. | "Pointwise fourfold zero action inside the open critical strip, with no multiplicity transported; consumes the kernel-checked bridge P3 and asserts nothing about re = 1/2." Apply the same substitution to `Z8P` at `:68`. |
| D40 | ledger | `VERIFIED_RESEARCHOS.md:42` (`RH-BRIDGE-P5T`) | "The totalized value at 1 is nonzero; a translation fact about the zero-set object." — the declaration `one_notMem_riemannZetaZeros` (`TargetBridge.lean:179-180`) states `(1 : ℂ) ∉ riemannZetaZeros`. "The totalized value at 1 is nonzero" is the *pinned input* `riemannZeta_one_ne_zero` (`Harmonic/ZetaAsymp.lean:431`), not what the row's declaration proves. The second clause discloses correctly. | "Non-membership of 1 in the pinned zero set; a translation of the pinned `riemannZeta_one_ne_zero` into the zero-set object, nothing more." |

---

## 4. The strongest surviving claims

A claim that withstands a determined attack is worth recording as such. Each of
the following was attacked and survived against primary evidence.

1. **`S1-CONJ` is recorded as OPEN everywhere, despite a merged sixteen-declaration
   conjugation package.** This is the strongest surviving claim in the audit,
   because it is precisely the temptation the lane was previously caught by.
   `CONJ_SYMMETRY_CONTRACT.md:14` and `:672`, `tasks/RIEMANN_HYPOTHESIS.md:26-28`
   and `:382`, `RH_CONJ_PROMOTION_2026_08_06.md:85-89`, `Conj.lean:20-23`, and the
   capability map's fifth addendum all state that the barrier closes only when
   divisor invariance under `ρ ↦ 1 − conj ρ` also lands — and the map's wording
   is matched word for word. `S1-MULTIPLICITY` is likewise open everywhere. No
   document in the audited surface claims a route SELECT, an unparked route, or
   progress on RH's truth.
2. **Every statement signature in the three contracts is character-identical to
   its merged module.** Bridge P1-P5 + three corollaries vs `TargetBridge.lean:29,
   104,115,127,145,179,182,199`; xi X1-X11 (twelve declarations) vs `Xi.lean:41,
   46,61,72,78,89,120,157,180,192,208,248`; conj Z1-Z9 (sixteen) vs `Conj.lean:58,
   86,163,179,234,246,256,262,282,292,306,317,336,357,440,452`. No contract states
   a theorem its module does not prove, and no module proves a weaker statement
   than its contract records.
3. **`RH001_INDEPENDENT_REPLAY_2026_08_05.md` replays with zero locator
   mismatches.** Every positive locator re-run at the pin matched exactly across
   ~30 Mathlib files. The sign-inconsistency finding is exact
   (`RiemannZeta.lean:20` vs the theorem at `:84-85`, with the docstrings at
   `:62`/`:88` siding with the theorem). The whole-tree negatives hold:
   `riemannXi` has zero hits tree-wide; exactly sixteen files mention
   `riemannZeta` and none relates it to conjugation.
4. **All four absence claims in the contracts set are true at the pin**, including
   the `S1C-ORD` novelty claim: `Analysis/Analytic/Order.lean` contains no
   `conj`/`star` result of any kind, and the only `conj_conj` calculus lemmas are
   `HasDerivAt`/`DifferentiableAt` at `Deriv/Star.lean:93/100/117/123`. Newly
   re-verified here: `LSeries_eq_tsum` has **zero** hits tree-wide (basis of D6).
5. **The ledger is machine-consistent.** `gen_researchos_registry.py --check` →
   "47 ledger rows → 48 declarations, inverse coverage complete, anchors fresh";
   `check_ledger_isolation.py` passes; counts re-verified independently here as
   8 + 12 + 16 RH rows. Zero rows carry `native_decide`.
6. **The CI wiring is real, not nominal.** All three modules are in the
   `ResearchOS.lean` import closure of a default lake target, so `ci.yml:359` and
   `:436-441` genuinely cover them. This audit found **no** CI-verified assertion
   about a file CI never elaborates — every draft reference in the queue set is
   explicitly marked "non-built" or "statically audited".
7. **Provenance is clean of closed and unmerged PRs across the entire audited
   surface.** Only #297, #298, #299, #301, #302, #303, #304 and #307 are cited,
   all merged and all present in `git log`. #300, #306 and #308 appear nowhere in
   the audited documents. (Outside scope, for the owning agent's awareness:
   `MULTIPLICITY_CONTRACT.md:91-95` and `:1998-1999` explicitly flag #306 and
   #308 as closed-and-unmerged and forbid citing them — that file is handling it.)
8. **`RH006_SOURCE_REPLAY` arithmetic is exact and its negative is not softened.**
   27 + 12 + 20 = 59 rows; exactly 57 `**CONFIRMED**` and 2 `**DISCREPANCY —
   RESOLVED**`; both records preserve "57 confirmed, 2 amended" rather than
   relabelling amendments as confirmations, and both amendments are actually
   applied in `SOURCE_CONTRACTS.md`. The RH-001 record likewise reports positive
   and negative inventories under separate scopes instead of collapsing them.
9. **The three drafts-lane synchronization claims are literally true**: `diff`
   from the first `import` to EOF is empty for all three pairs.
10. **The exactly-one-ACTIVE invariant holds.** `RH-002` is the only ACTIVE task;
    `.mult_queue_entry_draft.md` correctly declines to mark RH-009/RH-010 ACTIVE.

---

## 5. Patterns, not instances

The individual defects matter less than the fact that four of them recur as
classes. Fixing instances without fixing the class buys one clean audit.

### P1 — Post-merge staleness (D8, D9, D10, D11, D13, D14, D15, D16, D17, D18, D21, D33, D34, D35). Dominant.

Fourteen of the forty defects — over a third — are documents written *before* a
PR landed and never revisited after it did. Status lines say DRAFT and "Not
Lean-checked" for modules that are merged, imported, ledgered and audited;
obligation registers say "nothing is claimed proved until the kernel checks it"
about theorems the kernel has checked; enumerations of built packages stop at
the second of three; anchors into files that grew by a hundred lines point at
the wrong text.

Two things make this the dominant pattern rather than a bookkeeping nuisance.

**First, the direction of error is mostly safe but not uniformly so.** Most
instances *understate* — which protects the one invariant, and is why none of
them is S0. But a stale hedge can invert. **D7** is the proof: "ordered strictly
after the route-neutral bridge and `S0-TRUST`" was a conservative deferral when
written and is now a queue position that has come up, on a route the lane has
explicitly parked. A precondition clause becomes an authorization the moment its
precondition lands. Every "ordered after X" and "blocked until X" in the lane
should be re-read as an authorization the day X closes.

**Second, staleness erodes the record's evidential value even when it
understates.** The lane's defence against overclaiming is that its documents can
be trusted as a description of state. A reader who learns that DRAFT means
"merged three days ago" stops reading status lines, and then a real status line
carries no signal.

*Structural remedy worth considering:* make promotion PRs required to touch the
originating contract's status line and the domain README's package enumeration,
the way they already touch the ledger and the capability map. The three items
that consistently go stale — contract status, README package list, task closure
evidence — are exactly the three not currently coupled to the promotion change.

### P2 — Count and enumeration drift (D5, D22, D23, D31, D17, D18)

The same miscount reaches two independent documents: "three candidates admitted"
appears in both `ROUTE_TRIAGE.md:16` and `RH001_INDEPENDENT_REPLAY:61`, while the
cited table says "Only two receive candidate status". That is not a typo
propagating; it is a paraphrase of a table replacing the table. Same shape at
D31 (five theorems vs eight declarations), D23 (4 of 6 vs 5 of 6), D17/D18 (two
packages vs three). None of these changes a conclusion — the ≤3 bullet is
satisfied on either count — which is exactly why they survived review. *Remedy:*
when a document restates a count from another document, cite the source line and
quote its own summary sentence rather than recomputing from the rows.

### P3 — Scope-word inflation (D1, D3, D4, D19, D20, D32, D39, D40)

A single word carries more than the evidence: "exists" for "is known" (D1);
"infinite" for "not proved finite" (D4); "Set-level" for pointwise (D39);
"real-positive" for real-nonnegative (D32); "independent" for "its own" (D20);
"only in Z8" for "the reflection only in Z8" (D19); "the totalized value at 1 is
nonzero" for a non-membership statement (D40); a support-dependent height
asserted to be dominated globally (D3). This is the class that produced two of
the lane's three prior incidents, and **D4 is a literal recurrence of one of
them** — the infinitude claim, withdrawn in the multiplicity contract, still
standing in the source contract. *Remedy:* the withdrawal of a claim should be
grep-scoped to the whole lane, not applied to the document where it was caught.
Any sentence containing "infinite", "all", "every", "exists", "no … exists" or a
global quantifier over height is worth a locator before it ships.

### P4 — Intended verdict recorded as delivered verdict (D21, D14)

`RH_CONJ_PROMOTION` describes what CI *will* do and ends; sixteen ledger rows
marked `proved` name it as their review record. Its two siblings both record a
delivered verdict with SHAs and run IDs. This is graded **S2, not S0**, and the
reasoning should be explicit: the rows do not claim a proof with *no* kernel
verdict — the module is merged on `main`, is in the built import closure of a
default target, and CI's gates are wired to cover it, so a green required check
is a precondition of the merge that happened. What is missing is the *citation*
of that verdict in the record that the ledger points at. **This audit could not
close the gap itself: with no Lean toolchain and no run logs fetched, it can
confirm the wiring but not the run.** The honest statement is that the sixteen
rows rest on the merged-CI requirement rather than on a cited run, and the
record should say so until the head SHA and run IDs are written down.

---

## 6. Disposition

- Nothing in this record is applied. No lane document was edited.
- Recommended order if a maintainer acts: **D1** first (it is the one finding
  that touches the S0 boundary, and its grading needs an explicit decision),
  then **D4** (a recurrence of a previously withdrawn claim), then **D7** (a
  stale hedge that has inverted into an apparent authorization), then **D21**
  (record the PR #307 verdict identifiers), then the remaining S2 staleness in
  one pass, then S3.
- **Next round should start with `domains/riemann-hypothesis/UPSTREAM_POOL.md`**
  (955 lines, added 2026-08-07 in `ad97231`), which no set covered, followed by
  `EXPLAINER.md`, `MATHLIB_SEARCH_LOG.md`, `corpus.md`, and the four files under
  `drafts/`.
- `MULTIPLICITY_CONTRACT.md`, `drafts/RiemannMult.lean`, `drafts/README.md` and
  `MATHLIB_CAPABILITY_MAP.md` were read as evidence only and are owned by other
  agents this round. Two observations were logged for their owners: `Xi.lean:205`
  and `Conj.lean:279` describe already-merged siblings as "draft"; and
  `Conj.lean:90-92` claims a deviation from a contract skeleton that the
  acceptance pass has since synchronized. Both are module-comment defects, not
  contract defects.
