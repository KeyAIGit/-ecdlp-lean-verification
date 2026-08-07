# Mellin norm-bound contract (UPSTREAM-POOL §6) acceptance record

Date: 2026-08-07

Status: FINAL — stage-one statement-surface acceptance of
`domains/riemann-hypothesis/MELLIN_BOUND_CONTRACT.md` (MB1–MB4), with
editorial fixes applied in place during this acceptance session.

## Reviewed baseline

- repository branch `claude/rimmen-hypothesis-b6gd62` at
  `3201153651e9a5c6a4b4491a807f6cda57417933`;
- reviewed object `domains/riemann-hypothesis/MELLIN_BOUND_CONTRACT.md`
  (754 lines pre-fix, SHA-256
  `23ddf0b7e1880da1df6d1e044ed2d763f7ac18c5217bf69a0a420f6434f0ce8a`, Git
  blob `440e9619d3797f28b6c4ef9dd655fa8afd7c45ff`); post-editorial-fix state
  (782 lines) SHA-256
  `2eccf9e256b736e9a858afd7f80933cee9b0c857ed4db4a112a9624bfa1cc8d6`
  (Git blob `2365b525bb4685ca1b7553b80f2a2c4f2ffb2e72`);
- cross-check object (NOT the acceptance object): non-built companion draft
  `domains/riemann-hypothesis/drafts/MellinBound.lean` (321 lines, SHA-256
  `852479ec60b1cb32143e76567f6e767aaf3e5952a19d405621e509df3efed780`),
  outside every lake target and the no-`sorry` gate's scan surface per
  `drafts/README.md`; its five theorem statements were mechanically diffed
  against the contract's §2 blocks — **character-identical ×5**;
- pinned Mathlib revision `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`
  (v4.31.0), re-verified by both lenses via `git rev-parse HEAD` at
  `/workspace/leanprover-community/mathlib4` during this review;
- repo cross-reference context: `UPSTREAM_POOL.md` (:71, :555, :566, :787),
  `MULTIPLICITY_CONTRACT.md` (:1905, :1942, :2092),
  `CONJ_SYMMETRY_CONTRACT.md` (:5).

No Lean toolchain was run. Every check below is source reading; nothing in
this record is a kernel verdict.

## Authority and effect

This panel acted under **owner-delegated review authority**. The two-stage
gate of `MULTIPLICITY_CONTRACT.md` §Two-stage gate and promotion ordering
(heading confirmed at :2092) applies verbatim; form precedent
`notes/reviews/RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`. Acceptance under
this record:

- covers the **statement surface only** of the Mellin norm-bound package
  (MB1, MB2, MB3 ×2, MB4 — exactly 5 public Lean signatures, independently
  retallied by both lenses), plus the recorded withdrawal C1 of the pool's
  ill-typed `norm_mellin_le_mellin_norm`;
- carries **no kernel verdict** — no Lean toolchain was run, and only the
  Lean kernel via CI can ever supply one;
- **changes no barrier row** — the package is `[GEN]` generic machinery; per
  its own death condition 6 (inheriting `MULTIPLICITY_CONTRACT.md` finding
  A4 / death condition 9), no `MATHLIB_CAPABILITY_MAP.md` row is closed,
  weakened, or re-scoped;
- **promotes nothing** — a stage-two built promotion of a `MellinBound.lean`
  module, judged solely by CI/the kernel, is a separate later change; this
  record is not it and does not schedule it. The companion draft carries no
  kernel verdict and is not promoted, imported, or scheduled by this record;
- selects no route, touches no queue file, and provides no evidence for or
  against the Riemann Hypothesis.

## Panel composition

Two independent lenses, each reading the contract in full against the pinned
Mathlib checkout:

1. **Truth-pin lens (mathematics + API fidelity)** — re-derived all five
   statements at every point of their stated domains, including all four
   degenerate quadrants of the unconditional MB1 (non-AESM /
   AESM-non-integrable × RHS-integrable / not), the `t = 1` boundary of the
   strip split, and both rpow monotonicity directions in MB4; re-opened
   every load-bearing `file:line` locator at the pin (MellinTransform,
   Bochner/Basic, Bochner/Set, Pow/Real, MulAction, L1Space/Integrable,
   Restrict, BorelSpace/Order, Data/Complex/Basic, ImproperIntegrals,
   Pow/Continuity, Topology/ContinuousOn, IntegrableOn, LinearOrder — all
   EXACT); re-confirmed Annex A findings R1/R2/R4 and correction C1;
   reproduced the collision scan (0 hits for all 5 names plus the withdrawn
   name); verified the companion draft's cited locators.
2. **Claim-boundary and scope lens** — audited the claim boundary (5
   signatures, zero `def`s, zero occurrences of ζ/ξ/Λ₀/theta/FEPair/
   evenKernel/zero tokens in any statement block, "no repo prerequisites"
   confirmed), all 8 death conditions for internal consistency, the
   non-normative framing and exact locators of the §3 FUTURE-consumer seam,
   name freshness at the pin and repo-wide, and the two-stage gate wiring
   including the §Return-to-stage-one condition.

## Decision: **ACCEPT WITH APPLIED EDITORIAL FIXES**

All five signatures are mathematically true as stated — including every
degenerate case of the unconditional MB1 — and the contract's honest-shape
analysis (unconditional MB1; `IntegrableOn`-on-the-bound MB2–MB4;
load-bearing `hgsupp` in MB3; both endpoints plus `hmg` in MB4) is correct.
Correction C1 (withdrawal of `norm_mellin_le_mellin_norm` as ill-typed) is
confirmed: no `NormedSpace ℂ ℝ` instance exists at the pin. **No declaration
name, binder, hypothesis, conclusion, or claim-boundary item changed.** Zero
blocking items. The applied fixes fall in three classes: (i) one
staleness-of-status repair (the companion draft now exists); (ii) one
degenerate-case prose correction (MB1's truth unaffected); (iii) citation
and proof-skeleton accuracy repairs (no signature impact; MEL-4a remains
MEDIUM).

## Per-lens verdicts

| Lens | Verdict | Blocking defects | Editorial defects |
|---|---|---|---|
| Truth-pin (math + API) | **ACCEPT WITH FIXES** | none | 4 (1 MEDIUM prose, 2 LOW citation, 1 LOW proof-skeleton; map onto Fixes 2, 3, 4, 5) |
| Claim boundary and scope | **ACCEPT WITH EDITORIAL FIXES** | none | 3 (1 MEDIUM-editorial staleness, 2 LOW; map onto Fixes 1, 5, 6) |

No lens returned BLOCK or REJECT. **Blocking items: none.** The death-
condition-9 citation defect was found independently by both lenses (Fix 5);
the consolidated count is **six** distinct fixes.

## Applied editorial fixes

All six consolidated fixes were applied to
`domains/riemann-hypothesis/MELLIN_BOUND_CONTRACT.md` during this acceptance
session; the post-fix baseline hashes above are of the fixed file. None
touches a signature.

**Fix 1 — Companion-draft staleness (Status header).** The header's "no
draft `.lean` file exists for this package yet" was false at review time:
`domains/riemann-hypothesis/drafts/MellinBound.lean` exists (header dated
2026-08-07, post-Annex-A skeletons) with its row in `drafts/README.md`. Same
staleness class as RH-011 Fixes 1–3. The clause now records the non-built
companion draft, that it sits outside every lake target and the no-`sorry`
gate's scan surface, that no CI workflow elaborates it, and that it carries
no kernel verdict. The adjacent "no `lake build` has been run against any of
it" sentence is still true and stays.

**Fix 2 — Degenerate-case prose (MB1; MEDIUM).** The sanity paragraph and
Annex A.1.1 claimed that when the Mellin integrand is not a.e. strongly
measurable "both sides are `0`". False: non-AESM zeroes only the LHS; the
RHS can be strictly positive. Counterexample (truth-pin lens): `f t = ε t •
1` on `(1, 2)`, `0` elsewhere, with `ε` a Bernstein-set-valued non-measurable
`±1` sign — the ℂ-integrand is non-AESM on `volume.restrict (Ioi 0)`, yet
`‖f t‖ = indicator (1,2)`, so the RHS `= ∫₁² t^(σ-1) dt > 0`. MB1 itself
still holds (LHS `= ‖0‖ = 0`; the RHS is nonnegative unconditionally —
exactly the `integral_nonneg_of_ae` step inside Bochner/Basic.lean:924's own
proof), and §1.1's wording was already correct. Both passages now read: the
LHS is `0` (`integral_non_aestronglyMeasurable`, Bochner/Basic.lean:213) and
the RHS is nonnegative, so the inequality holds. The
AESM-but-non-integrable half (`integrable_norm_iff` L1Space/Integrable.lean
:616 + `integral_undef` Bochner/Basic.lean:206 zero both sides) was correct
and is kept.

**Fix 3 — MB4 skeleton routed off the `IntegrableOn.mono` capture
(MEL-4a; proof-skeleton only).** The skeleton's
`refine (hga.add hgb).mono ?_ ?_` cannot reach `Integrable.mono`
(L1Space/Integrable.lean:86): dot notation on an `IntegrableOn`-typed term
resolves to `IntegrableOn.mono` (IntegrableOn.lean:124, signature
`(hs : s ⊆ t) (hμ : μ ≤ ν)` — a set/measure-monotonicity lemma, the wrong
target). Same defect class as `MULTIPLICITY_CONTRACT.md` finding A2. The
companion draft already routes around it; both draft spellings are now
folded into the skeleton and the MEL-4a text:
`refine MeasureTheory.Integrable.mono hsum.integrable hms ?_` (named call,
restrict-measure reading made explicit via `IntegrableOn.integrable`,
IntegrableOn.lean:95), and `continuousOn_id' (Set.Ioi (0 : ℝ))` with the
explicit set argument (explicit at Topology/ContinuousOn.lean:737; the bare
dot-notation spelling may not resolve). The register row was updated
accordingly. MEL-4a's severity stays **MEDIUM**; no signature impact.

**Fix 4 — `hfc` citation `:190` → `:189`.** The `hfc` hypothesis of
`mellin_convergent_iff_norm` is on MellinTransform.lean:189 (theorem head
:188), not :190. Corrected in the sanity paragraph and the Annex A R3 row.

**Fix 5 — Death-condition-9 citation (found by both lenses).** Annex A.1.3
cited "death condition 9 at :383"; `MULTIPLICITY_CONTRACT.md:383` is only a
cross-reference sentence — the death condition itself is defined at
`MULTIPLICITY_CONTRACT.md:1905` ("A capability-map row is declared 'stale'
from generic-Mathlib evidence."). Now cited as ":1905, cross-referenced at
:383".

**Fix 6 — Annex A tally reword (Status header).** "Four locator corrections
and one obligation resolution" omitted R3, which Annex A itself classifies
as an unsound-prose-justification repair, not a locator correction. Now:
"locator corrections (R1–R2), one prose-justification repair (R3), and one
obligation resolution (R4) applied in place, no signature changed."

## Review basis (spot summary of the panel's independent checks)

1. **Truth at every degenerate point.** MB1 checked across all four
   degenerate quadrants (non-AESM / AESM-non-integrable × RHS-integrable /
   not); the honest chain is Bochner/Basic.lean:924 (unconditional, internal
   `by_cases` on AESM) composed with the integrability-free congruence
   Bochner/Set.lean:73. MB2's hypotheses exactly match
   `norm_integral_le_of_norm_le` (:937). MB3: `t = 1` lands in the `1 ≤ t`
   branch under `lt_or_ge`; the unrestricted form is correctly declared
   false (indicator near `t = 0`), so `hgsupp` is load-bearing and death
   condition 4 is sound. MB4: both rpow monotonicity directions
   (Pow/Real.lean:613/:639) applied on the correct branches; `hmg` genuinely
   needed — measurability of the middle integrand is not derivable from bare
   endpoint `IntegrableOn`.
2. **Pin fidelity.** All load-bearing locators re-opened at the pin: the
   MellinTransform cluster (:42/:45/:91/:188/:198/:277/:338/:345/:350/:351/
   :353/:354–366/:414), Bochner/Basic (:141/:206/:213/:241/:924/:937),
   Bochner/Set (:73/:752–753/:764/:818), Pow/Real (:163/:337/:613/:639, with
   namespaces confirmed), MulAction (:95/:96/:98), L1Space/Integrable
   (:86/:616), Restrict :641, BorelSpace/Order :197, Data/Complex/Basic
   (:147/:640), ImproperIntegrals (:131/:160), Pow/Continuity :278 (root
   namespace), Topology/ContinuousOn :737, IntegrableOn :760, LinearOrder
   (:97/:100) — all EXACT, zero incorrect locators surviving the fixes.
3. **Annex A re-confirmation.** R1: the full `simp_rw` chain fires once at
   :198; the second site is a different `simp_rw` set (:351) plus
   `rw [norm_cpow_eq_rpow_re_of_pos ht]` at :353; the pool's drifted `:349`
   at `UPSTREAM_POOL.md:787` is real and correctly quarantined. R4: zero
   declarations `Measurable.rpow_const`/`measurable_rpow`/`Measurable.rpow`
   at the pin (the single wildcard grep hit is
   `aestronglyMeasurable_rpowIntegrand₀₁`, not a match); route (ii) fully
   located. C1: no `NormedSpace ℂ ℝ` instance at the pin, withdrawal
   confirmed.
4. **Name freshness.** Grep at the pin: zero hits in `Mathlib/` for all five
   proposed names (`norm_mellin_le`, `norm_mellin_le_of_norm_le`,
   `setIntegral_rpow_mul_mono_exponent`, `norm_mellin_le_of_re_le`,
   `norm_mellin_le_add_of_re_mem_Icc`) and the withdrawn
   `norm_mellin_le_mellin_norm`. Repo-wide `*.lean` scan hits only the
   non-built companion draft; no built `MellinBound` module exists anywhere,
   so the working name is free.
5. **Claim boundary and seam.** Statement blocks contain exactly 5
   signatures, zero `def`s, and zero occurrences of
   ζ/ξ/Λ/theta/Riemann/FEPair/evenKernel/zero tokens; all four preamble
   imports are pinned Mathlib ("no repo prerequisites" holds). §3 is framed
   non-normatively throughout and asserted nowhere; all four seam locators
   exact at the pin (RiemannZeta.lean:63, HurwitzZetaEven.lean:302/:254/:255
   /:65/:77, AbstractFuncEq.lean:385/:81/:258). All 8 death conditions
   internally consistent; DC8 ↔ §Return condition ↔ MEL-4a's strengthening
   fallback form a closed loop (MB4-only re-open; MB1–MB3 independent).
6. **Two-stage gate.** Gate paragraph matches the referenced convention
   (`MULTIPLICITY_CONTRACT.md:2092`); "an acceptance PR must not carry a
   promotion" present; §Return-to-stage-one condition present and
   signature-scoped.

## Statement disposition

| Block | Declaration surface (5 signatures) | Disposition |
|---|---|---|
| MB1 | `norm_mellin_le` | ACCEPT. TRUE unconditionally; all four degenerate quadrants checked; the unconditional real-valued shape is honest at the pin (junk-value semantics), and death condition 3 keeps it that way. |
| MB2 | `norm_mellin_le_of_norm_le` | ACCEPT. Hypotheses exactly match Bochner/Basic.lean:937; RHS depends on `s` only through `s.re`. |
| MB3 | `setIntegral_rpow_mul_mono_exponent` | ACCEPT. TRUE on the support class; `hgsupp` load-bearing; `t = 1` seam sound (MEL-3b). |
| MB3 | `norm_mellin_le_of_re_le` | ACCEPT. Usable half-plane form; unrestricted monotonicity correctly declared false (death condition 4). |
| MB4 | `norm_mellin_le_add_of_re_mem_Icc` | ACCEPT. Both endpoints + `hmg` genuinely needed; skeleton repaired by Fix 3; MEL-4a remains MEDIUM with the signature-strengthening fallback re-opening MB4 only. |
| — | `norm_mellin_le_mellin_norm` (pool §6, second signature) | WITHDRAWN (C1) as ill-typed at the pin; content carried by MB2's RHS; `ofReal` resurrection recorded as DEFERRED-1. |

## Notes not conditioning acceptance (recorded so they are not lost)

- The pool's drifted locator `:349` at `UPSTREAM_POOL.md:787` remains in the
  pool file, which is outside this contract's write scope; Annex A R1
  quarantines it correctly. A future pool-hygiene pass may fix it there.
- MEL-4a remains the most likely single CI bounce for stage two; the
  companion draft's spellings (now folded into the contract by Fix 3) are
  the tested-by-reading route, and the `hms`-strengthening fallback with its
  MB4-only re-open is the recorded escape.
- The boundary lens's first collision-scan attempt produced a false positive
  (8169 from `grep -rc` zero-count rows), corrected with `grep -rln` to the
  true zero-hit result; recorded here as a methods note for future scans.
- The Bernstein-set counterexample behind Fix 2 is worth keeping: it shows
  the norm of a non-measurable integrand can itself be integrable, so
  "non-AESM zeroes both sides" is never a safe shortcut in this package's
  degenerate-case prose.

## Gate result and limits

Stage-one acceptance of the 5-signature Mellin norm-bound statement surface
is complete: **ACCEPT WITH APPLIED EDITORIAL FIXES** — six consolidated
fixes applied, all prose/citation/skeleton-level, zero blocking items, zero
statement changes.

Stated plainly, the limits of this record:

- **No kernel verdict.** No Lean toolchain was run; nothing here is
  Lean-checked. Under the one invariant, only the Lean kernel via CI can
  verify these statements, and that judgment has not occurred. The
  companion draft's `LIKELY_ELABORATES` static review is not a kernel
  verdict either.
- **No barrier-row change.** No `MATHLIB_CAPABILITY_MAP.md` row is closed,
  weakened, or re-scoped by this acceptance; generic machinery lowers the
  cost of a future exit but never retires a row (death condition 6).
- **No promotion.** Nothing was promoted, imported into the build, or
  scheduled for promotion. A stage-two built promotion of exactly this
  surface, judged solely by CI, is a separate later change requiring its
  own dated decision; queue flips are the orchestrator's, not this panel's.
- **No claim about RH.** This record provides no evidence for or against
  the Riemann Hypothesis, and no route is selected, opened, or advanced.
