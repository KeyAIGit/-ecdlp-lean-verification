# RH-009 multiplicity-contract acceptance record

Date: 2026-08-07

Status: FINAL — committed in the RH-009 acceptance change after the RH-002
closure (merged PR #311) landed on `main`.

## Reviewed baseline

- repository branch `claude/rimmen-hypothesis-b6gd62` at
  `834330f81ee8323070f2b784705a3f4c7ab96c33`;
- reviewed-and-fixed `domains/riemann-hypothesis/MULTIPLICITY_CONTRACT.md`
  (post-editorial-fix state) SHA-256
  `d2e259fc688cc71b24c49e6188531ef5251371bfe49441068c687f681ddb488a`
  (Git blob `c81345898ed78e6aca5da625fe4dfd0554d59462`);
- companion non-built `domains/riemann-hypothesis/drafts/RiemannMult.lean`
  SHA-256
  `d8fe365874d626bad28380c69e21e280a3dad591a7a954c77594d3be609a18a1`
  (Git blob `e6ccd2d8644495caff0811f93a11e24f43135753`) — read for
  cross-checking only; it is **not** the object of acceptance;
- pinned Mathlib revision
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (re-verified by `git rev-parse`
  at `/workspace/leanprover-community/mathlib4` during this review);
- merged kernel-checked context on `main`:
  `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/TargetBridge.lean`,
  `Xi.lean`, `Conj.lean`; provenance commits `288d65b` (PR #299),
  `afdae08` (PR #304), `c277b86` (PR #307) all confirmed ancestors of
  `origin/main`. PRs #306/#308 are cited nowhere as provenance.

No Lean toolchain was run. Every check below is source reading; nothing in
this record is a kernel verdict.

## Authority and effect

This panel acted under **owner-delegated review authority** as recorded in the
repository governance notes (RH queue, `tasks/RIEMANN_HYPOTHESIS.md`;
two-stage gate per the contract's normative section and the RH-007 precedent
`notes/reviews/RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`). Acceptance under
this record:

- covers the **statement surface only** of the S1-MULTIPLICITY contract
  (M1–M17, exactly 34 public Lean signatures);
- **changes no barrier row** — `S1-MULTIPLICITY` and `S1-CONJ` in
  `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` remain OPEN;
- **promotes nothing** and produces **no kernel content**;
- does not override the RH-queue ordering (`RH-002` remains the sole ACTIVE
  task; no route is selected);
- provides no evidence for or against the Riemann Hypothesis.

## Panel composition

Three independent lenses, each reading the contract in full (2,179 lines
pre-fix) against the pinned Mathlib checkout and the merged repository
modules:

1. **Mathematical-truth lens** — re-derived every one of the 34 statements at
   every point of its stated domain, including exceptional-point and
   junk-value symmetry audits.
2. **Pin-fidelity (API) lens** — re-opened every load-bearing `file:line`
   locator at the pin (~70 checks), verified both recorded naming traps,
   ran the 34-name collision scan, and mechanically compared contract
   signatures against the companion draft.
3. **Claim-boundary and scope lens** — audited the closure discipline, the
   exit-item mapping for `S1-MULTIPLICITY` and `S1-CONJ`, the death
   conditions and deferrals, and the two-stage gate.

## Decision: **ACCEPT WITH APPLIED EDITORIAL FIXES**

This decision accepts only the mathematical statement surface of
`MULTIPLICITY_CONTRACT.md`: seventeen contract blocks (M1–M17, including
M16' and M16'') carrying exactly 34 public declarations, independently
retallied by two lenses (M1–M8 = 8, M9 = 2, M10 = 1, M11 = 1, M12 = 2,
M13 = 1, M14 = 3, M15 = 6, M16 = 4, M16' = 2, M16'' = 1, M17 = 3). It does
not claim that the non-built Lean draft elaborates, does not promote a
module, does not close `S1-MULTIPLICITY` or `S1-CONJ`, and provides no
evidence for or against RH.

The applied fixes changed only death-condition and anti-pitfall prose. No
declaration name, binder, hypothesis, conclusion, or skeleton changed.

## Per-lens verdicts

| Lens | Verdict | Blocking defects | Editorial fixes |
|---|---|---|---|
| Mathematical truth | **ACCEPT** | none | none required (3 NOTEs, none conditioning acceptance) |
| Pin fidelity (API) | **ACCEPT** | none | none required (2 NOTEs, neither requiring contract change) |
| Claim boundary and scope | **ACCEPT WITH EDITORIAL FIXES** | none | 2 required (Findings 1 and 2), 1 optional (Finding 3) |

No lens returned BLOCK or REJECT. **Blocking items: none.**

## Applied editorial fixes

Both required fixes were applied to
`domains/riemann-hypothesis/MULTIPLICITY_CONTRACT.md` during this acceptance
session; the baseline hashes above are of the post-fix file.

**Fix 1 (boundary lens, Finding 1 — APPLIED). Death condition 5 updated for
the A5 surface growth.** M16' is proved from M12 (`X11 ▸
analyticOrderAt_riemannXi_ne_top`) and M16'' consumes M16'; the old DC5
named only M13 and reduced the block to "M9–M11 + M14/M15", omitting both
the falling ζ statements and the surviving M16/M17, so an executor hitting
the DC5 branch could drop M13 yet keep calling the ζ interface half
supplied. The body of death condition 5 now reads:

> If `analyticOrderAt riemannXi z ≠ ⊤` resists all three recorded routes,
> M13 — and with it M16' and M16'', which derive their finiteness from M12
> through X11 — must be dropped, and the divisor block reduced to M9–M11,
> M14/M15, M16 and M17 (none of which needs M12), with both support
> identifications (ξ on `U`, ζ on Ω) recorded as a new deferred item. Do
> **not** state M13 or M16'' with the `≠ ⊤` hypothesis floated to the caller
> and then call either half of the interface exit item closed.

**Fix 2 (boundary lens, Finding 2 — APPLIED). Anti-pitfall "Exceptional
points" bullet corrected.** The old bullet said every ζ statement "carries
`0 < s.re` and `s.re < 1`", which is literally true only for M4/M6/M8 and
parts of M16; M17 (and M16'') carry the strip as the divisor's carrier set
with no binder hypothesis on `s`. The bullet now opens:

> Every ζ statement is strip-bound: M4/M6/M8 carry `0 < s.re` and
> `s.re < 1` as hypotheses; M16–M17 carry Ω as the divisor's carrier set,
> outside which both sides are zero by `apply_eq_zero_of_notMem`.

The bullet's remaining sentences (Ω excludes `1`, `0`, and every Γℝ pole;
ξ entire) are unchanged.

**Optional items NOT applied** (recorded here so they are not lost):

- Boundary lens Finding 3 (NOTE, optional): append "— row retirement is a
  stage-two maintainer decision on the map file (death condition 9)" to the
  header's "Barrier-closure boundary" sentence. Not applied — the point is
  resolved precisely in §Claim boundary and death condition 9.
- API lens NOTE-1 (optional shorthand expansion in M4's falsity note):
  after "`differentiableAt_riemannZeta`,
  `Mathlib/NumberTheory/LSeries/RiemannZeta.lean:137`" insert "(pointwise
  differentiability on the open set `ℂ \ {1}` upgraded to analyticity via
  `DifferentiableOn.analyticAt`, CauchyIntegral.lean:625)". Not applied —
  the conclusion and scoping are correct; the citation is shorthand only.
- API lens NOTE-2: `drafts/RiemannMult.lean:568–570` comment "definition at
  Analytic/Basic.lean:117, body :118" is off by one at the pin (def at
  :118, body :119). Comment-only, in the companion draft, which is not the
  object of acceptance; correctable in the stage-two promotion without
  returning to stage one.
- Math lens NOTE-1 (M4, `n = 0` cast normalization), NOTE-2 (S1M-12a
  instance chain verified at source: `PathConnectedSpace.connectedSpace`,
  `instance (priority := 100)` at
  `Mathlib/Topology/Connected/PathConnected.lean:607`, completes
  Convex.lean:168 → ConnectedSpace → PreconnectedSpace — the contract's
  refusal to claim resolution without a toolchain remains conservative and
  correct), NOTE-3 ("fourfold" naming mirrors merged
  `riemannZeta_fourfold_zero`, Conj.lean:306). No changes required.

## Review basis

1. The BLOCK verdict's seven requirements were confirmed applied; the
   adversarial-review findings A1–A10 (Annex A) were re-verified as actually
   applied in the text, including all six Annex A §E locator corrections.
2. The corrected qualification of
   `AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero` was confirmed at the
   pin (Order.lean:687, inside `namespace AnalyticOnNhd` :575–:700), with
   both recorded traps verified verbatim: the fully-qualified name is
   mandatory (:693 carries an explicit `_root_.` prefix), and the lemma
   takes no `AnalyticOnNhd` argument — point explicit, hypothesis
   `∀ z₀, AnalyticAt 𝕜 f z₀`, conclusion global `f = 0`.
3. The `MeromorphicOn` and `Complex` namespace traps were confirmed
   (Divisor.lean:28–468 with :71/:177 unprefixed and :83 the `_root_`
   contrast; CauchyIntegral.lean:173–770 with :678 inside and :625
   `_root_.DifferentiableOn.analyticAt`, `protected`).
4. All 34 names are collision-free against the pinned `Mathlib/` tree, the
   repository build surface (`Ecdlp.lean`, `Ecdlp/`, `ResearchOS.lean`,
   `ResearchOS/`), and the three merged modules; `riemannXi` itself has 0
   hits in pinned Mathlib.
5. The contract's 34 signatures are character-identical (modulo line
   wrapping/whitespace) with the companion draft, which contains exactly 34
   `theorem`s and no `def`, `sorry`, `admit`, `axiom`, or `native_decide`.
6. Every load-bearing pinned locator was re-opened at the pin and matched
   exactly (~70 checks across Order.lean, Deriv/Add.lean,
   Algebra/Group/Basic.lean, Divisor.lean, NormalForm.lean,
   LocallyFinsupp.lean, Untop0.lean, Meromorphic/Order.lean and Basic.lean,
   Analytic/Basic.lean, CauchyIntegral.lean, ENat/Basic.lean,
   RiemannZeta.lean, Nonvanishing.lean, Constructions.lean, Linear.lean,
   Convex.lean, ZetaZeros.lean, Complex sources). Zero incorrect locators.
7. Repo-side citations (Xi.lean X11 at :248 and its docstring, Conj.lean
   :440/:452 orientations, `ResearchOS.lean:7–9` imports, capability-map
   quotations at :386/:389/:591–593/:614–618, RH queue :28/:122,
   `lakefile.toml:2/:10/:14`, `ci.yml:359/:420/:428/:438`) all verified
   verbatim.

## Statement disposition

| block | declaration surface | disposition |
|---|---|---|
| M1 | `riemannXi_comp_one_sub` | ACCEPT. Pointwise from kernel-checked `riemannXi_one_sub`; ξ written pole-safely. |
| M2 | `analyticOrderAt_comp_const_sub` | ACCEPT. `deriv = −1 ≠ 0`; `sub_sub_cancel` orientation exact; true for all `f` — junk 0 hits both sides together. |
| M3 | `analyticOrderAt_riemannXi_one_sub` | ACCEPT. M2 at `c = 1` plus M1; self-check at `s = 0` consistent (ξ(0) = ξ(1) = 1/2 ≠ 0). |
| M4 | `analyticOrderAt_riemannZeta_one_sub` (strip) | ACCEPT as scoped. Strip hypotheses load-bearing; global form correctly documented **false** (ζ(−2) = 0, ζ(3) ≠ 0); no simplicity claim (A7 respected). |
| M5–M8 | conj and composite/fourfold order symmetries | ACCEPT. Conj.lean:440/:452 orientations verified; `conj(1−s) = 1−conj s`; Klein four-group orbit correct; M8 keeps strip hypotheses on the middle conjunct. |
| M9 | ξ analytic/meromorphic on every `U` (2 sigs) | ACCEPT. Entire → `AnalyticOnNhd` via :678 + `.mono`; no openness/connectedness needed. |
| M10 | `riemannXi_divisor_apply` | ACCEPT. Pinned Divisor.lean:71 instantiated; carrier hypothesis `hz : z ∈ U` present and necessary. |
| M11 | `riemannXi_divisor_nonneg` | ACCEPT. `untop₀ ∘ map` values ≥ 0 on `U`, 0 off `U`; LocallyFinsupp:401. |
| M12 | ξ finite local order, analytic + meromorphic twins (2 sigs) | ACCEPT. Identity theorem refuted by ξ(0) = 1/2; A3-corrected fallback complete (Order.lean:624 fifth argument produced); local order only, no growth notion. |
| M13 | `riemannXi_divisor_support` | ACCEPT. NormalForm:578 orientation `.symm` correct; M12-before-M13 ordering respected; `≠ ⊤` never floated. |
| M14 | ξ divisor reflection symmetry (3 sigs) | ACCEPT. Symmetry hypothesis on `U` forces in/out branches to agree; correctly needs no `≠ ⊤` hypothesis (S1M-14a decoupling sound). |
| M15 | ξ divisor conj and composite symmetries (6 sigs) | ACCEPT. Both symmetry hypotheses required and carried; formerly prose-mandated instances now explicit signatures. |
| M16 | ζ on Ω: analyticity, divisor apply/nonneg (4 sigs) | ACCEPT. `1 ∉ Ω`; `negPart = 0` follows; nothing asserted on sets containing 1 (DEFERRED-3 restated per A5). |
| M16' | ζ finite local order on Ω (2 sigs) | ACCEPT. Transport by X11 alone from M12; no zero-free region or nonvanishing witness needed. |
| M16'' | ζ divisor support on Ω | ACCEPT. M13 pattern with M16' discharging the bound; finite-order-before-support ordering respected. |
| M17 | ζ divisor symmetries on Ω (3 sigs) | ACCEPT. Ω-stability under all three maps re-derived; Ω is a mandatory hypothesis carrier (general-`U` form would need unhypothesized M4, which is false — death condition 6); S1M-17-skel `rw`+`?_` defect honestly pre-registered as proof-engineering-only. |

## Load-bearing cross-cutting checks

- **Exceptional points and junk symmetry.** ξ entire — no exceptional point
  in any ξ statement. Every ζ statement is strip-bound (per applied Fix 2:
  hypotheses on M4/M6/M8, carrier set Ω on M16–M17); both evaluation points
  of every ζ equality lie in Ω, which excludes the ζ pole at `1`, the point
  `0`, and every Γℝ pole. All junk conventions (`analyticOrderAt` 0 off
  analyticity, `meromorphicOrderAt` 0 off meromorphy, `untop₀ ⊤ = 0`,
  divisor 0 off `U`) appear identically on both sides of every equality.
- **No enumeration, counting, or growth.** All 34 signatures are pointwise
  order/divisor equalities, one nonnegativity, two set identities, four
  analyticity/finiteness facts. No index type, `Finset` of zeros, `N(T)`,
  `logCounting`, or growth-order object anywhere. The local-finiteness field
  of `locallyFinsuppWithin` is discharged inside the pinned
  `MeromorphicOn.divisor` definition (Divisor.lean:39–55, verified at
  source), so no analytic obligation is smuggled through it.
- **No unproved-conjecture dependence.** Every prerequisite is pinned
  Mathlib or kernel-checked on `main`; no statement mentions
  `RiemannHypothesis`; X10 is consumed by no M.
- **Barrier-exit sufficiency.** M9–M13 + M16–M16'' jointly supply both
  halves of the "zeta/xi divisor interface"; M3/M5/M7/M8 + M14/M15/M17
  supply the multiplicity-preserving symmetries at order and divisor level;
  the M15 `one_sub_conj` family + M17c supply the `ρ ↦ 1−conj ρ`
  divisor-invariance half of `S1-CONJ`. Jointly sufficient for the named
  exit items **only once kernel-checked and promoted**; the contract
  nowhere claims more.

## Static review versus kernel verdict

The companion draft is intentionally outside every lake target (verified at
`lakefile.toml:2/:10/:14` and `ci.yml:359/:420/:428/:438`); a green CI run on
the acceptance PR says nothing about the draft. The following remain
elaboration risks until a stage-two built change runs the kernel:

- the M2 beta-redex closer (`simpa only [sub_sub_cancel] using …`);
- natural-number cast normalization in the M4 falsity note's `n = 0`
  instantiation;
- the S1M-12a instance chain (source-verified this session but not
  elaborated);
- the M16 `.and`-vs-`.inter` delta (classified proof-only under the
  return-to-stage-one condition);
- the pre-registered S1M-17-skel `rw`+`?_` skeleton defect.

None justifies weakening a theorem statement or a hypothesis carrier. If the
built implementation requires such a change, promotion must stop and return
to contract review (stage one).

## Gate result

The stage-one contract-acceptance phase for the S1-MULTIPLICITY statement
surface is complete: **ACCEPT WITH APPLIED EDITORIAL FIXES** (two fixes,
both applied and recorded verbatim above; zero blocking items). A separate
stage-two promotion change is authorized to attempt kernel verification of
exactly this 34-signature statement surface, judged solely by authoritative
CI.

This acceptance alone is a statement-surface acceptance only. It produces no
kernel verdict; the Lean kernel via a stage-two CI run remains the sole
judge of proof. It changes no barrier row: `S1-MULTIPLICITY` and `S1-CONJ`
remain OPEN, and any row retirement is a stage-two maintainer decision on
the map file (death condition 9). It promotes nothing — promotion remains a
separate, kernel-gated change — and it closes no task, selects no route,
and changes nothing about the truth status of RH.
