# RH growth-order definition contract acceptance record (ENTIRE_ORDER)

Date: 2026-08-07

Status: FINAL — stage-one independent contract acceptance of the
growth-order definitional surface, committed as the acceptance change for
`domains/riemann-hypothesis/ENTIRE_ORDER_CONTRACT.md`.

## THE DECISION, STATED FIRST

**The DEFINITION is ACCEPTED.** G0–G2 (the three definitions `maxModulus`,
`growthOrder`, `growthType` — codomain `ℝ≥0∞`, inner clamp `max … 1`, outer
clamp `ENNReal.ofReal`) and L1–L6 (the six calibration lemmas), exactly 9
public signatures, are accepted at stage one **as offered, with applied
editorial fixes and zero signature changes**. The definition is **not**
returned to design. Per death condition 1 of the contract, this record is
the citable acceptance object, and its existence **unlocks the drafts-lane
transcription** `domains/riemann-hypothesis/drafts/RiemannGrowthOrder.lean`
(character-identical to the 9-signature surface; still outside every lake
target, still carrying no kernel verdict). Consumers of `growthOrder` /
`growthType` must cite this file, not the contract draft.

No queue edit is made by this record; queue flips are the orchestrator's.

## Reviewed baseline

- repository branch `claude/rimmen-hypothesis-b6gd62` at
  `3201153651e9a5c6a4b4491a807f6cda57417933`;
- reviewed object `domains/riemann-hypothesis/ENTIRE_ORDER_CONTRACT.md`
  (974 lines pre-fix, SHA-256
  `45f1632f5b72476bce2a635b3f3a3ca39de6be6890b2b68e8e39e3ec1787e7b8`, Git
  blob `61d7110ed724b5c99bd1638bef41392dad6af4f1`); post-editorial-fix state
  (1,013 lines) SHA-256
  `5c45eb9d59ea9f2e20075f239c637bef68df22241970677ccaaa106784f8c8dd`
  (Git blob `0e0850b598f11c789c98e39d1b107bd3af33e18d`; the applied fixes
  landed on the branch in commit `59d5220` — "land in-flight panel edits" —
  during the parallel review sweep, verified blob-identical to this
  consolidation's post-fix state);
- pinned Mathlib revision `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`
  (v4.31.0), re-verified by `git rev-parse HEAD` at
  `/workspace/leanprover-community/mathlib4` by every lens and again at
  consolidation.

No Lean toolchain was run. Every check below is source reading; nothing in
this record is a kernel verdict.

## Authority and effect

This panel acted under **owner-delegated review authority**; the two-stage
gate discipline of `MULTIPLICITY_CONTRACT.md` §Two-stage gate applies
verbatim; form precedent
`notes/reviews/RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`. This is the
independent stage-one pass after the contract's own red-team audit
(contract Annex A). Acceptance under this record:

- covers the **statement surface only** of the growth-order definitional
  pillar (G0–G2 + L1–L6, exactly 9 public signatures, retallied by all
  three lenses: 3 defs + 6 lemmas);
- carries **no kernel verdict** — no Lean toolchain was run, and only the
  Lean kernel via CI can ever supply one;
- **changes no barrier row** — `S1-GROWTH`
  (`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:388`, quoted
  verbatim and verified unchanged by two lenses) remains **OPEN**; its exit
  demands "explicit quantitative bounds sufficient for the selected
  theorem", and **definitions supply zero bounds** — S1-GROWTH is not
  advanced by definitions alone;
- **promotes nothing** — a stage-two built promotion of a
  `GrowthOrder.lean` module, judged solely by CI, is a separate later
  change; this record is not it and does not schedule it;
- **edits no queue state** — the RH queue's sole ACTIVE slot remains
  `RH-012` (zero-set lane, route-neutral); all routes remain PARKED; this
  surface holds no slot;
- selects no route and provides no evidence for or against the Riemann
  Hypothesis.

**What acceptance uniquely does here (the design-bearing point):** this is
the one pillar of the RH lane for which no notion exists at the pin at all,
so every future growth theorem will be stated *about this object*. A wrong
definition poisons everything downstream, which is why the contract's own
death condition 1 forbade consumption before acceptance. That gate is now
satisfied: the reviewed, frozen definitional target exists, and future
growth statements may consume `growthOrder` / `growthType` by citing this
record.

## Panel composition

Three independent lenses, each reading the contract in full (all 975
pre-fix lines including Annex A) against the pinned Mathlib checkout:

1. **Mathematical-truth (definition) lens** — re-derived the clamp design:
   agreement with the textbook order for every entire function; the §1.1
   inner-clamp counterexample re-derived independently; all test values
   (orders 0, 1, ∞; type of exp) recomputed.
2. **Pin-fidelity (API) lens** — re-printed all ~60 Mathlib locators at the
   pin, reproduced the absence audit and collision scan, and
   paper-typechecked all 9 signatures.
3. **Claim-boundary lens** — audited the claim boundary, two-stage gate,
   all 9 death conditions, name freshness in both scopes, and the honesty
   of the L2/L5 HIGH obligations.

## Decision: **ACCEPT WITH APPLIED EDITORIAL FIXES**

Zero blocking defects across all three lenses; **no declaration name,
binder, hypothesis, conclusion, codomain, or clamp changed**. Eleven
consolidated editorial fixes were applied (three documentation defects from
the definition lens, four locator/quotation-precision defects from the pin
lens, four boundary-precision defects from the boundary lens), plus a
Status-header line recording this acceptance and its record location.

## Per-lens verdicts

| Lens | Verdict | Blocking defects | Editorial fixes |
|---|---|---|---|
| Mathematical truth (definition) | **ACCEPT** — no signature-changing defect | none | D1–D3 (applied as Fixes 1–3) |
| Pin fidelity (API) | **ACCEPT for stage-one** | none | 4 (applied as Fixes 4–7) |
| Claim boundary / gate | **ACCEPT WITH EDITORIAL FIXES** | none | DEF-1–DEF-4 (applied as Fixes 8–11) |

No lens returned BLOCK, REJECT, or return-to-design. **Blocking items:
none.** In particular, the two design calls the contract flagged as the
stage-one question were each independently endorsed:

- **Inner clamp `max … 1`**: the counterexample `M(f,r) = e^{−r}` (inner
  `log M = −r`, pinned `Real.log (−r) = Real.log r` via `log_neg_eq_log`,
  Log/Basic.lean:120) makes the raw quotient exactly 1 for all r > 1, so
  the raw formula assigns order 1 to exponential decay and falsifies L4 in
  **every** codomain, including scout A's EReal version. The clamp is
  load-bearing and correct. Moreover (Fix 2) the clamped form is not a
  deviation at all: `Real.log (max x 1) = log⁺ x`, so G1 is literally the
  classical `log⁺ log⁺` (Boas/Levin) formulation of order — a
  transcription, which materially improves the Mathlib-upstream case.
- **Codomain `ℝ≥0∞`**: the ENNReal limsup is total; the order-∞ case
  (`M = e^{e^r}`) is representable, where a raw ℝ `Filter.limsup` returns
  junk; the EReal alternative buys only dead negative cases once the clamps
  are in place. Verified at least as strong as EReal at the pin, row by
  row.

## Applied editorial fixes

All eleven consolidated fixes were applied to
`domains/riemann-hypothesis/ENTIRE_ORDER_CONTRACT.md` during this
acceptance session; the post-fix baseline hashes above are of the fixed
file. None touches a signature.

**Fix 1 (definition D1) — G1 docstring endpoint correction.** The outer-clamp
bullet's "outer log of a value in `[0,1)`, i.e. `1 ≤ M(f,r) ≤ e`" was wrong
at both endpoints; it now reads "in `(0,1)`, i.e.
`1 < maxModulus f r < e`; endpoints give quotient exactly `0`" (at `M ≤ 1`
the outer-log argument is 0 and `log 0 = 0`; at `M = e` the quotient is
exactly 0).

**Fix 2 (definition D2) — `log⁺` classical-footing note (strengthens the
contract).** One passage added to §1.1 and one bullet to the G1 docstring:
the inner clamp under `Real.log` is exactly `log⁺`, and with the outer
clamp G1 is the textbook `limsup log⁺ log⁺ M(r) / log r` formulation —
demoting §1.3's "riskiest choice" from deviation to transcription (a
reconciling parenthetical was added to §1.3; its review-call framing is
retained).

**Fix 3 (definition D3) — codomain-table route guard.** The §1.2 "product
bound" cell citing `ENNReal.limsup_mul_le'` now carries "(codomain evidence
only; NOT the L5 route — see S1G-L5)", so no stage-two implementer reads
the table as a route hint that L5's own skeleton forbids.

**Fix 4 (pin 1) — stray `ExpGrowth.lean:38` locator annotated.** Both the
§0 comment and the consolidated table now read ":38 (`expGrowthInf`, not
used), :41 (`expGrowthSup`)".

**Fix 5 (pin 2) — `repo:` locator convention stated.** The Pinned-Mathlib
paragraph now states the convention: root artifacts repo-root-relative;
bare filenames of the lane's own documents (`MATHLIB_CAPABILITY_MAP.md`,
`UPSTREAM_POOL.md`) resolve in `domains/riemann-hypothesis/`.

**Fix 6 (pin 3) — §0 quotation honesty.** The §0 heading now declares
"binders/notation lightly normalized — implicit-binder blocks may be elided
and dot-notation `f.limsup u` may be written `limsup u f`; no hypothesis or
instance argument is altered", and Annex A.1's "verbatim" is softened to
"verbatim up to §0's declared binder elision and notation normalization".

**Fix 7 (pin 4) — `IsCompact.bddAbove` quote completed.** The §0 quote now
carries `[Nonempty α]` (Topology/Order/Compact.lean:322 reads
`[ClosedIciTopology α] [Nonempty α]`; harmless at the only use site
`α := ℝ`, but load-bearing instance arguments are surfaced per the
contract's own practice).

**Fix 8 (boundary DEF-1) — death condition 1 no longer self-trips.**
Condition 1 now states that the L1–L6 calibration lemmas — including their
character-identical transcription into `drafts/RiemannGrowthOrder.lean` —
are the object under review, not downstream consumers; "downstream" means
any statement outside the 9-signature surface.

**Fix 9 (boundary DEF-2) — queue-state precision.** §Ordering/authority now
anchors "not an active task" to the queue's sole ACTIVE slot `RH-012`
(zero-set slice build-out, route-neutral, different lane; this surface
holds no slot), and the claim-boundary bullet's "no route is active in the
RH queue" now reads "all routes remain PARKED; the queue's ACTIVE slot
(`RH-012`) is route-neutral and in a different lane".

**Fix 10 (boundary DEF-3) — collision-scan scope recorded in full.** The
scan sentence now records both scopes: pinned Mathlib **and** repo Lean
sources (`ResearchOS/`, `Ecdlp/`, root modules, `drafts/`) — zero hits for
all 9 names in both scopes (re-run by the boundary lens and re-run again at
consolidation: 0 hits each).

**Fix 11 (boundary DEF-4) — the citable record named.** The two-stage-gate
paragraph now states that the stage-one acceptance record is a dated file
under `notes/reviews/` (form precedent RH011), and that file — this file —
is what death condition 1 requires consumers to cite.

**Status header** updated to record the acceptance, this record's path, and
the unlock of `drafts/RiemannGrowthOrder.lean`.

## Review basis (spot summary of the panel's independent checks)

1. **Textbook agreement.** For nonconstant entire f, M(f,r) is nondecreasing
   and → ∞, both clamps eventually inactive, and the ENNReal limsup equals
   `ofReal ρ` for finite textbook order ρ and `⊤` for order ∞ (where a raw
   ℝ limsup returns junk `sSup ∅ = 0` — correctly killing the ℝ codomain).
   Constants/bounded f: value 0, the textbook convention; both L1 branches
   verified numerically (‖c‖ = 42 and ‖c‖ = 0.3).
2. **Test values all agree.** Order 0 for constants and M ~ C·r⁵ (slowly,
   ~n·loglog r/log r — consistent with L2's honest HIGH costing); order ∞
   for M = e^(e^r); exp: raw quotient ≡ 1 exactly for r > 1 → L3 = 1;
   M = e^(r²) → 2; growthType exp at p = 1 ≡ 1 → L6.
3. **Pin fidelity.** All ~60 load-bearing locators re-printed at the pin
   and matched, including the traps: `ENNReal.limsup_add_le` does carry
   `[CountableInterFilter f]` (Order/Filter/ENNReal.lean:231) and
   `atTop : Filter ℝ` is not one (`⋂ n, Ici (n:ℝ) = ∅ ∉ atTop`) — L5's
   skeleton correctly routes around it; `limsup_max` has exactly four
   `isBoundedDefault` autoParams (:1141–:1145);
   `div_le_div_of_nonneg_right` (GroupWithZero/Basic.lean:1199) needs only
   `0 ≤ c`. Absence audit reproduced exactly (0 hits for any growth-order
   notion; the single "canonical product" hit is category-theoretic and
   unrelated).
4. **Shape-typecheck of all 9 signatures (paper).** G0 is a bare real
   `sSup` matching the `sSupNormIm` carrier (Hadamard.lean:77, verified);
   G1/G2 lambdas are `ℝ → ℝ≥0∞` with a single `ofReal` boundary, limsup
   total via `CompleteLinearOrder ℝ≥0∞`; G2's `r ^ p` resolves only via
   `Pow ℝ ℝ` (S1G-2 caution safe-side); L1–L6 instantiate with all required
   instances present. Count: 3 defs + 6 lemmas = 9.
5. **Death conditions and gate.** All 9 conditions present and enforceable;
   condition 7 correctly inherits MULTIPLICITY finding A4
   (`MULTIPLICITY_CONTRACT.md:1788` verified); condition 1 was unviolated
   at review time — no `RiemannGrowthOrder.lean` in `drafts/` and repo-wide
   grep for the stems returned 0 hits (no dependents exist). The two-stage
   gate matches the MULTIPLICITY discipline and the RH011 precedent;
   "an acceptance PR must not carry a promotion" present.
6. **L2/L5 HIGH obligations honestly costed, not softened.** Confirmed
   independently: no assembled `log log (C·rⁿ)/log r → 0` lemma and no
   `atTop`-usable ENNReal limsup-additivity exist at the pin. L2's fallback
   forbids weakening to `≤ ε` or `natDegree = 0`; L5's `+ ε` fallback is
   pre-labeled a FAILED design gate. Acceptance is granted *with* these
   costs as stated and cannot be read as a claim that the proofs are
   routine.
7. **Divergence audit vs scout A.** `UPSTREAM_POOL.md` §1 re-read: EReal
   codomain, no inner clamp — the claimed exactly-two load-bearing
   divergences are exactly two, and both are argued and now independently
   endorsed. Maintainer-shape assessment: total definitions with documented
   junk + gated lemmas is standard Mathlib practice (`Real.log`,
   `MeromorphicOn.divisor` precedents correctly cited); likely upstream
   bikesheds identified (iSup-vs-sSup spelling; `HasGrowthOrderLE`
   Prop-layer, correctly excluded as DEFERRED-G2), none blocking.

## Statement disposition

| Block | Declaration | Disposition |
|---|---|---|
| G0 | `maxModulus` | ACCEPT. Bare real `sSup` on the sphere, `sSupNormIm`-style; total with documented junk; hypothesis-free. |
| G1 | `growthOrder` | **ACCEPT — THE definition.** `ℝ≥0∞` codomain; inner `max … 1` + outer `ofReal` clamps independently re-derived as load-bearing (L4 false without them, in every codomain); clamped form = classical `log⁺ log⁺` (Fix 2). |
| G2 | `growthType` | ACCEPT. Same two clamps verbatim (symmetric conventions); gate by documentation + death condition 6, following the `MeromorphicOn.divisor` total-def precedent; rpow pitfall registered. |
| L1 | `growthOrder_const` | ACCEPT. Both branches re-derived; closer instances pinned (Topology/Order/Real.lean:53/:55). |
| L2 | `growthOrder_polynomial` | ACCEPT with obligation S1G-L2 **HIGH** as stated (unassembled asymptotic; may split to its own stage-two PR; must not be weakened). |
| L3 | `growthOrder_exp` | ACCEPT. `[PIN]` upheld: quotient eventually exactly 1; pinned ingredients suffice, no asymptotics; the decisive calibration test. |
| L4 | `growthOrder_le_of_eventually_le` | ACCEPT. The clamp-design acceptance test; unconditional as stated (death condition 5 protects it). |
| L5 | `growthOrder_mul_le` | ACCEPT with obligation S1G-L5 **HIGH** as stated (ε-absorption; `CountableInterFilter` trap avoided; continuity hypotheses load-bearing and cheap for consumers). |
| L6 | `growthType_exp` | ACCEPT. Exercises G2's gate honestly at the (order, type) = (1, 1) classical calibration point. |

## Gate result and limits

Stage-one acceptance of the 9-signature growth-order definitional surface
is complete: **ACCEPT WITH APPLIED EDITORIAL FIXES** — eleven consolidated
fixes applied, all prose/documentation-only, zero blocking items, zero
signature changes. **The definition is accepted, not returned to design;
its drafts-lane transcription `drafts/RiemannGrowthOrder.lean` is
unlocked.**

Stated plainly, the limits of this record:

- **No kernel verdict.** No Lean toolchain was run; nothing here is
  Lean-checked. Under the one invariant, only the Lean kernel via CI can
  verify these statements, and that judgment has not occurred.
- **No barrier-row change.** `S1-GROWTH` remains **OPEN** and is not
  advanced: definitions supply zero quantitative bounds. All routes remain
  PARKED; no capability-map row is closed, weakened, or re-scoped.
- **No promotion, no queue edit.** Nothing was promoted, imported into the
  build, or scheduled; the queue's ACTIVE slot (`RH-012`) is untouched;
  queue flips are the orchestrator's, not this panel's.
- **No claim about RH.** This record provides no evidence for or against
  the Riemann Hypothesis.
