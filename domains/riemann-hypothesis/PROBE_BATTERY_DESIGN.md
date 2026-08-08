# PROBE BATTERY DESIGN — RH built surface (design only; NOT a run order)

Date: 2026-08-07. Status: **DESIGN ONLY — UNAUTHORIZED TO RUN.** This document
carries no batch ID, freezes no batch, and authorizes nothing. Every table below
is a *candidate inventory*, not a frozen probe list; a probe list becomes frozen
only inside a batch header (§P2) opened by an explicit dated maintainer/queue
decision (§MD). Nothing in this file has been run; nothing in this file may be
run on the strength of this file alone.

Repository: `/home/user/-ecdlp-lean-verification`. Mathlib pinned at
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (`lake-manifest.json:8`; checkout
`/workspace/leanprover-community/mathlib4`), toolchain `leanprover/lean4:v4.31.0`
(`lean-toolchain:1`). All claims below rest on direct source reading of the
working tree and the pinned checkout; no build, no elaboration, no model call
was performed in producing this design.

Built, kernel-checked surface on `main` (the only surface any probe may
reference) — **ten modules**, all imported by `ResearchOS.lean`:

- the RH chain, `ResearchOS.lean:15-19`:
  `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/TargetBridge.lean` (P1–P5),
  `.../Xi.lean` (X1–X11), `.../Conj.lean` (Z1–Z9), `.../Mult.lean` (M1–M17, 34
  declarations, merged PR #313), `.../ZeroSetSlice.lean` (23 declarations,
  merged PR #320);
- the domain-neutral `analysis-generic` shelf, `ResearchOS.lean:10-14`:
  `ResearchOS/Analysis/MellinBound.lean`, `.../PolyLiouville.lean`,
  `.../HarnackDisc.lean` (merged PR #318), `.../ThreeCircles.lean`,
  `.../GrowthOrder.lean` (merged PR #319) — 35 declarations under the `MB-`,
  `PL-`, `HK-`, `TC-` and `GO-` ledger prefixes;
- plus the two elementary number-theory modules, which no probe here uses.

**How this sentence is to be kept current.** The authority is
`VERIFIED_RESEARCHOS.md` and the import list of `ResearchOS.lean`, not this
paragraph. Anyone extending the battery must re-derive the surface from those
two files rather than trusting the text above. That instruction exists because
the previous version of this paragraph went stale and, being a governance
CONSTRAINT rather than a description, silently forbade probes over 92 built
declarations across seven modules for a day. Corrected 2026-08-08 under `RH-013`.

Superseded statements, recorded rather than deleted, since a reader may be
holding the older text: the earlier scope named only three RH modules and cited
them at `ResearchOS.lean:7-9` (now the shelf comment block); it declared the
M1–M17 surface "accepted only" with its promotion RH-010 holding the ACTIVE slot
and stated that "**no probe references any M declaration**". RH-010 completed
2026-08-07 and M1–M17 has been built and merged since PR #313, so all of that is
now false and the M surface is fully probe-eligible.

Purpose: design — do not run — a battery of many small machine-checkable
statements over the built foundation: (a) regression probes instantiating built
theorems, (b) type-level probes testing whether a candidate idea can even be
EXPRESSED in the built vocabulary (the cheapest falsifier of ill-posed ideas),
(c) negative probes expected to fail because the language honestly lacks the
concept (growth, counting) — their failure documents the boundary.

---

## §0. Governance frame (non-negotiable, restated before any probe)

- **Built surface in scope.** Exactly the three RH modules listed above.
- **No open-ended sweeps.** Per the queue's global hard rule "Never launch an
  open-ended model or compute sweep. Every run needs a fixed question, budget,
  validator, and stop condition" (`tasks/RIEMANN_HYPOTHESIS.md`, §Global hard rules, the never-launch-an-open-ended-sweep rule), an
  *authorized* probe batch would be: a **fixed** file list frozen in its batch
  header before the first invocation (drawn from, but not identical to, the
  candidate tables below — see §P2's per-batch size cap), **budget** one
  `lake env lean` pass per file, no retries, zero model calls (no
  Featherless/Kimi tier — probes are tactic/term-only), **validator** = diff of
  actual verdicts against the batch's frozen expected-verdict column, with red
  probes required to fail with the recorded *error class* (unknown identifier
  vs. instance failure vs. binder/type mismatch vs. unsolved goals — a red for
  the wrong reason is a probe bug, not a boundary result), **stop condition** =
  end of the frozen list, one pass. Discrepancies are filed as dated notes,
  never fixed in-loop. **This document is not such a batch and does not open
  one.**
- **RH-005 is PARKED and stays parked** (`tasks/RIEMANN_HYPOTHESIS.md`, §`RH-005`:
  bounded computation policy).
  No probe below performs or gestures at numerical zero verification, interval
  arithmetic, or any bounded computation; the `norm_num`/`simp` discharges in
  Class A act on tiny literal casts during elaboration and are not bounded
  numerics; nothing here touches RH-005's activation conditions or counts
  toward them.
- **Probes are never results and never ledger rows.** `VERIFIED_RESEARCHOS.md`
  records built theorems only (e.g., row `RH-BRIDGE-P1` at
  `VERIFIED_RESEARCHOS.md:37`).
- **S0-TRUST interaction.** The inverse-coverage gate requires every built
  public ResearchOS declaration to be ledgered
  (`domains/riemann-hypothesis/S0_TRUST_DESIGN.md:487`; enforced at
  `scripts/gen_researchos_registry.py:263`, scanning exact built paths only,
  `:40`). Since probes must never be ledger rows, the **default placement is
  non-built**: standalone files under `domains/riemann-hypothesis/probes/`
  (a lane that does not yet exist — creating it is maintainer decision MD-1),
  outside every lake target, same standing as `drafts/RiemannMult.lean`,
  elaborated via `lake env lean <file>`; this has zero gate interaction. A
  **built** probe lane would require amending the registry checker and the
  ledger acceptance criteria with an exact-path probe carve-out — **that is a
  maintainer decision with a dated record (MD-4); this document specifies its
  shape and explicitly does not make it.** (Note for that decision: all probes
  below are `example`/`#check` declarations, which introduce no public names;
  but path-level governance still requires the explicit carve-out before any
  probe file enters a lake target, and any future `def`/`theorem` in a probe
  file would trip the gate by design.)
- **No route selection.** The battery is route-neutral, reads only the built
  surface, and must never be cited as evidence for activating, unparking, or
  preferring any route (`repo/ECDLP_DECISION_SUBSTRATE.json` discipline;
  `tasks/RIEMANN_HYPOTHESIS.md`, §Current decision and §Global hard rules).
- **Epistemic status.** Probes test the *stability and expressive reach of the
  built interface*, nothing else. **a thousand green probes prove nothing about
  the truth of RH.**

Probe file preamble (all classes):
`import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Conj` (transitively
pulls Xi and TargetBridge, `Conj.lean:32-33`), plus
`import Mathlib.NumberTheory.LSeries.HurwitzZetaValues` for A5/A7 only
(`riemannZeta_two`, Mathlib `HurwitzZetaValues.lean:226`;
`riemannZeta_neg_two_mul_nat_add_one`, Mathlib `RiemannZeta.lean:171`),
`import Mathlib.Analysis.Meromorphic.Divisor` for C7 only, and
`open Complex; open scoped Real ComplexConjugate`.

Cost classes: **C0** = elaboration only (`#check`, no proof term, no kernel
theorem); **C1** = term-mode or single-tactic closure; **C2** = short tactic
block (≤ ~15 lines) reusing an already-built obligation discharge verbatim. All
costs are dominated by one-time olean loading; no probe may exceed one
file-level timeout (maintainer-set, MD-3; suggest the CI default).

---

## §A. Class A — regression instantiation probes (expected GREEN)

Fixed question (for a batch that would host these): "does each built theorem
still apply, unchanged, at a concrete instance?" A red here on green `main`
means interface or pin drift (or a probe-file bug) — file a note; never patch
the built module in-loop.

Referenced built declarations (all verified):
`riemannZeta_ne_zero_of_re_le_zero` TargetBridge.lean:29,
`riemannZeta_ne_zero_of_re_eq_zero` :115, `one_notMem_riemannZetaZeros` :179;
`riemannXi` Xi.lean:41, `riemannXi_one_sub` :61, `riemannXi_zero` :72,
`riemannXi_one` :78, `riemannXi_ne_zero_of_one_le_re` :157,
`analyticOrderAt_riemannXi_eq_riemannZeta` :248; `Gammaℝ_conj` Conj.lean:58,
`riemannZeta_conj` :86, `riemannZeta_fourfold_zero'` :317. Pin:
`riemannZetaZeros` Mathlib `ZetaZeros.lean:33`, `riemannZeta_two`
`HurwitzZetaValues.lean:226`, `riemannZeta_neg_two_mul_nat_add_one`
`RiemannZeta.lean:171`, `Gammaℝ` `Deligne.lean:43`.

```lean
-- A1  (P2 corollary at s = I; re I = 0)                                 [C1]
example : riemannZeta Complex.I ≠ 0 :=
  riemannZeta_ne_zero_of_re_eq_zero Complex.I_re

-- A2  (X4 endpoints, both at once)                                      [C1]
example : riemannXi 0 = 1 / 2 ∧ riemannXi 1 = 1 / 2 := ⟨riemannXi_zero, riemannXi_one⟩

-- A3  (X3 at a concrete off-line point)                                 [C1]
example : riemannXi (1 / 2 - Complex.I) = riemannXi (1 / 2 + Complex.I) := by
  simpa [show (1 : ℂ) - (1 / 2 + Complex.I) = 1 / 2 - Complex.I by ring]
    using riemannXi_one_sub (1 / 2 + Complex.I)

-- A4  (X7 at s = 2; discharge is `1 ≤ (2 : ℂ).re`)                      [C1]
example : riemannXi 2 ≠ 0 := riemannXi_ne_zero_of_one_le_re (by simp)

-- A5  (Z2 against the pin's Basel value: conjugation fixes a real value) [C1]
example : riemannZeta ((starRingEnd ℂ) (2 : ℂ)) = (π : ℂ) ^ 2 / 6 := by
  rw [riemannZeta_conj, riemannZeta_two]
  simp [map_div₀, map_pow, Complex.conj_ofReal]

-- A6  (P5 helper, verbatim)                                             [C1]
example : (1 : ℂ) ∉ riemannZetaZeros := one_notMem_riemannZetaZeros

-- A7  (P1 sharpness: the trivial-zero exclusion is NOT vacuous —
--      dropping `htriv` from P1 would be false; ties the built `-2*(n+1)`
--      vocabulary to the pin's trivial-zero lemma at n = 0)              [C1]
example : ∃ s : ℂ, s.re ≤ 0 ∧ riemannZeta s = 0 :=
  ⟨-2, by norm_num, by simpa using riemannZeta_neg_two_mul_nat_add_one 0⟩

-- A8  (Z8' projection shape stability)                                  [C1]
example {ρ : ℂ} (hz : riemannZeta ρ = 0) (htriv : ¬∃ n : ℕ, ρ = -2 * (n + 1)) :
    riemannZeta ((starRingEnd ℂ) ρ) = 0 :=
  (riemannZeta_fourfold_zero' hz htriv).2.1

-- A9  (X11 at a concrete strip point, re = 1/2)                         [C1]
example : analyticOrderAt riemannXi (1 / 2 + Complex.I)
    = analyticOrderAt riemannZeta (1 / 2 + Complex.I) :=
  analyticOrderAt_riemannXi_eq_riemannZeta
    (by norm_num [Complex.add_re, Complex.I_re]) (by norm_num [Complex.add_re, Complex.I_re])

-- A10 (Z1 at a real point)                                              [C1]
example : Gammaℝ ((starRingEnd ℂ) (3 : ℂ)) = (starRingEnd ℂ) (Gammaℝ 3) := Gammaℝ_conj 3
```

Red meanings: A1/A4/A9 red = concrete-`re` simp/norm_num discharge drift (the
same LOWCONF cast class the built modules flag at Xi.lean:166-169,
TargetBridge.lean:119-122) — cheap early warning before it bites a promotion;
A5/A7 red = drift between the built trivial-zero/`conj` vocabulary and the
pin's value lemmas; A8 red = anonymous-constructor shape of Z8 changed;
A2/A3/A6/A10 red = outright interface break, should be impossible on green
`main`.

## §B. Class B — cross-module composition probes (expected GREEN)

Fixed question: "do the three modules still compose along their intended
seams?" These exercise exactly the seams the module headers declare (X10
imports bridge P2, Xi.lean:12; Z8 imports P2/P3, Conj.lean:25,301-304; Z9-xi
imports `riemannXi`, Conj.lean:276-280).

Referenced built declarations: `riemannHypothesis_iff_zero_free_gt_half`
TargetBridge.lean:145, `riemannHypothesis_iff_zetaZeros_re_eq_half` :182,
`riemannHypothesis_iff_zetaZeros_re_eq_half'` :199;
`riemannXi_eq_zero_iff_riemannZeta_eq_zero` Xi.lean:120,
`riemannXi_zero_mem_critical_strip` :192,
`riemannHypothesis_iff_riemannXi_zeros_re_eq_half` :208,
`analyticOrderAt_riemannXi_eq_riemannZeta` :248; `riemannXi_conj`
Conj.lean:282, `riemannZetaZeros_conj_image` :262, `riemannZeta_fourfold_zero`
:306, `analyticOrderAt_riemannXi_conj` :452.

```lean
-- B1  (P4 ∘ X10: the two RH equivalences are mutually consistent)       [C1]
example : (∀ s : ℂ, 1 / 2 < s.re → riemannZeta s ≠ 0)
    ↔ (∀ s : ℂ, riemannXi s = 0 → s.re = 1 / 2) :=
  riemannHypothesis_iff_zero_free_gt_half.symm.trans
    riemannHypothesis_iff_riemannXi_zeros_re_eq_half

-- B2  (P5 ∘ P5': the two zero-set formulations agree)                   [C1]
example : (∀ s ∈ riemannZetaZeros, (¬∃ n : ℕ, s = -2 * (n + 1)) → s.re = 1 / 2)
    ↔ (∀ s ∈ riemannZetaZeros, (¬∃ n : ℕ, s = -2 * (n + 1)) ∧ s ≠ 1 → s.re = 1 / 2) :=
  riemannHypothesis_iff_zetaZeros_re_eq_half.symm.trans
    riemannHypothesis_iff_zetaZeros_re_eq_half'

-- B3  (Z7 closes xi zeros under conjugation)                            [C1]
example {s : ℂ} (hz : riemannXi s = 0) : riemannXi ((starRingEnd ℂ) s) = 0 := by
  rw [riemannXi_conj, hz, map_zero]

-- B4  (Z9-xi ∘ X11: order transport across both packages)               [C1]
example {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannXi ((starRingEnd ℂ) s) = analyticOrderAt riemannZeta s :=
  (analyticOrderAt_riemannXi_conj s).trans (analyticOrderAt_riemannXi_eq_riemannZeta h0 h1)

-- B5  (X11 at the conjugate point: the order square commutes)           [C1]
example {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannXi ((starRingEnd ℂ) s)
      = analyticOrderAt riemannZeta ((starRingEnd ℂ) s) :=
  analyticOrderAt_riemannXi_eq_riemannZeta (by rwa [Complex.conj_re]) (by rwa [Complex.conj_re])

-- B6  (Z6 image form is involutive)                                     [C1]
example : (starRingEnd ℂ) '' ((starRingEnd ℂ) '' riemannZetaZeros) = riemannZetaZeros := by
  rw [riemannZetaZeros_conj_image, riemannZetaZeros_conj_image]

-- B7  (deepest seam: xi zero ⟹ all four zeta zeros; X9 → X6 → Z8,
--      reusing the shared htriv cast discharge verbatim from Xi.lean:164-170) [C2]
example {s : ℂ} (hz : riemannXi s = 0) :
    riemannZeta s = 0 ∧ riemannZeta (1 - s) = 0 ∧
      riemannZeta ((starRingEnd ℂ) s) = 0 ∧ riemannZeta (1 - (starRingEnd ℂ) s) = 0 := by
  obtain ⟨h0, h1⟩ := riemannXi_zero_mem_critical_strip hz
  have hs0 : s ≠ 0 := fun e => by simp [e] at h0
  have hs1 : s ≠ 1 := fun e => by simp [e] at h1
  have htriv : ¬∃ n : ℕ, s = -2 * (n + 1) := by
    rintro ⟨n, rfl⟩
    rw [show ((-2 : ℂ) * ((n : ℂ) + 1)).re = -2 * ((n : ℝ) + 1) by
      simp [Complex.mul_re, Complex.natCast_re, Complex.natCast_im]] at h0
    nlinarith [Nat.cast_nonneg (α := ℝ) n]
  have hζ : riemannZeta s = 0 :=
    (riemannXi_eq_zero_iff_riemannZeta_eq_zero hs0 hs1 htriv).mp hz
  obtain ⟨hr, hc, hrc⟩ := riemannZeta_fourfold_zero h0 h1 hζ
  exact ⟨hζ, hr, hc, hrc⟩
```

Red meanings: B1/B2 red = the `RiemannHypothesis` unfold discipline diverged
between modules (the P4-b/P5-a/X10-b `show`-pattern,
TargetBridge.lean:162-164,191-193; Xi.lean:226-229) — the highest-value
regression signal in the battery, since RH-010 will lean on the same anchor
(pin def `RiemannHypothesis`, Mathlib `RiemannZeta.lean:182`); B7 red = the
shared LOWCONF cast obligation (X7-a/X10-a class) drifted; B4/B5 red =
`analyticOrderAt` API drift at the pin (Mathlib
`Analysis/Analytic/Order.lean:47,175,497`).

## §C. Class C — type-level expressibility probes (`#check` only; expected GREEN = elaborates)

Fixed question: "can this candidate idea even be *stated* in built + pin
vocabulary?" — the cheapest falsifier of ill-posed ideas. A `#check` produces
no theorem, enters nothing into the kernel, and asserts nothing true. **Caveat
recorded up front:** elaboration success is weak evidence — Lean's total
functions let many meaningless statements typecheck (junk values of
`analyticOrderAt` off analyticity, `Nat.card` = 0 on infinite sets). Green here
licenses only "a contract could be drafted" — the drafting itself still enters
the queue through its normal pipeline; red kills an idea before any prover
minute is spent.

```lean
-- C1  (the OPEN divisor-invariance leg of S1-CONJ, pointwise-order form
--      — expressible today, provable by nobody yet)                     [C0]
#check (∀ s ∈ riemannZetaZeros,
  analyticOrderAt riemannZeta s = analyticOrderAt riemannZeta (1 - (starRingEnd ℂ) s) : Prop)

-- C2  ("all nontrivial zeros are simple" is statable)                   [C0]
#check (∀ s ∈ riemannZetaZeros, 0 < s.re → s.re < 1 →
  analyticOrderAt riemannZeta s = 1 : Prop)

-- C3  (no infinite-order xi zero)                                       [C0]
#check (∀ s : ℂ, analyticOrderAt riemannXi s ≠ ⊤ : Prop)

-- C4  (RH in xi-order vocabulary — a candidate X10 refinement)          [C0]
#check (RiemannHypothesis ↔ ∀ s : ℂ, analyticOrderAt riemannXi s ≠ 0 → s.re = 1 / 2 : Prop)

-- C5  (existence of a lowest zero above the real axis)                  [C0]
#check (∃ s ∈ riemannZetaZeros, 0 < s.im ∧
  ∀ z ∈ riemannZetaZeros, 0 < z.im → s.im ≤ z.im : Prop)

-- C6  (box-finiteness of zeros — statable, and in fact already PINNED:
--      IsCompact.inter_riemannZetaZeros_finite, Mathlib ZetaZeros.lean:64) [C0]
#check (∀ T : ℝ,
  ({s ∈ riemannZetaZeros | 0 ≤ s.im ∧ s.im ≤ T ∧ 0 ≤ s.re ∧ s.re ≤ 1}).Finite : Prop)

-- C7  (the RH-010 vocabulary object exists at the pin:
--      MeromorphicOn.divisor, Mathlib Analysis/Meromorphic/Divisor.lean:39) [C0]
#check (MeromorphicOn.divisor riemannZeta {s : ℂ | 0 < s.re ∧ s.re < 1})

-- C8  (order-reflection idea, the multiplicity face of the functional
--      equation — statable now, proof belongs to the M-surface era)     [C0]
#check (∀ s : ℂ, 0 < s.re → s.re < 1 →
  analyticOrderAt riemannZeta s = analyticOrderAt riemannZeta (1 - s) : Prop)
```

Red meanings: any C red = the idea's natural phrasing does not elaborate over
built + pin vocabulary; the correct response is a vocabulary/contract proposal
through the queue, **not** a workaround in a probe file. C6/C7 exist to keep
the boundary map honest in the other direction: they document that *local
finiteness* and *divisors* are already pin-expressible (`ZetaZeros.lean:64`,
`Divisor.lean:39`), so no one may claim those as "missing foundations" — this
matters because the naive boundary story ("counting is inexpressible") is
false at the local level; see §D for what is genuinely absent.

## §D. Class D — negative boundary probes (expected RED; the failure is the deliverable)

Fixed question: "does the language honestly lack this concept?" Each probe
must fail with the **recorded error class**; the batch validator would reject
reds for any other reason. A D probe turning GREEN is the actionable outcome:
it means the capability boundary moved (pin bump or promotion) and
`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` is stale — the follow-up
is a *proposed* dated capability-map update submitted to the maintainer (MD-5),
never an in-loop edit of that RH-lane file. Absences below were verified by
grep over the full pinned checkout on 2026-08-07.

```lean
-- D1  (Finset-sum over the zero set: global multiplicity-weighted counting
--      has no direct term — the ∑ x ∈ s binder demands a Finset, and
--      riemannZetaZeros : Set ℂ, Mathlib ZetaZeros.lean:33)              [C0]
-- EXPECTED RED: binder/type mismatch (Set is not Finset).
#check ∑ ρ ∈ riemannZetaZeros, (analyticOrderAt riemannZeta ρ).toNat

-- D2  (no decidable/finite enumeration of the zero set)                 [C0]
-- EXPECTED RED: failed to synthesize `Fintype ↥riemannZetaZeros`.
#check riemannZetaZeros.toFinset

-- D3  (no enumeration sequence of zeros exists at the pin; ZetaZeros.lean
--      exports set-level facts only, lines 33-72)                       [C0]
-- EXPECTED RED: unknown identifier.
#check zetaZeroSeq

-- D4  (no finite-order/growth-order theory for entire functions:
--      grep `growthOrder` over Mathlib/ at the pin = zero hits)          [C0]
-- EXPECTED RED: unknown identifier.
#check growthOrder riemannXi

-- D5  (no Hadamard factorization of entire functions: the only Hadamard
--      object in Analysis/ is the matrix product, Analysis/Matrix/Order.lean) [C0]
-- EXPECTED RED: unknown identifier.
#check HadamardFactorization

-- D6  (no argument principle at the pin: grep `argumentPrinciple|argument_principle`
--      = zero hits)                                                     [C0]
-- EXPECTED RED: unknown identifier.
#check argumentPrinciple

-- D7  (no Riemann–von Mangoldt / explicit formula: grep
--      `explicitFormula|explicit_formula|vonMangoldt_explicit` = zero hits) [C0]
-- EXPECTED RED: unknown identifier.
#check riemannVonMangoldt
```

Honesty notes required alongside any D report: (i) D1's red documents only
that the *Finset route* is blocked — the pin's `finsum`/`∑ᶠ` is total and
would elaborate with junk value 0 on infinite sets, so D1 must never be quoted
as "counting is inexpressible", only as "counting is not expressible *without*
an explicit finiteness or junk-value discipline"; (ii) D4's red documents the
absence of the named finite-order *theory*, not of growth talk — raw bounds
like `∃ C, ∀ s, ‖riemannXi s‖ ≤ C * Real.exp ‖s‖` elaborate fine; (iii) D3–D7
are canonical-name representatives backed by the recorded greps, not proofs of
absence of every conceivable spelling — each red report must carry its grep
line as evidence, mirroring the `MATHLIB_SEARCH_LOG.md` discipline.

## §E. Verdict/severity matrix (validator contract for any authorized batch)

| Class | Expected | Green means | Red means | Action on surprise |
|---|---|---|---|---|
| A (10 candidates) | GREEN | built theorems apply unchanged at instances | interface/pin drift or probe bug | dated note; never in-loop fixes to built modules |
| B (7 candidates) | GREEN | module seams (P↔X↔Z) compose; RH anchor uniform | seam/defeq drift — pre-RH-010 warning | dated note, flag to RH-010 owner |
| C (8 candidates) | GREEN (elaborates) | idea statable; contract drafting *possible* | idea ill-posed in current vocabulary — cheapest kill | idea returns to queue for vocabulary work or is dropped |
| D (7 candidates) | RED (recorded error class) | **boundary moved** — capability map stale; propose dated update (MD-5) | boundary confirmed and documented | green: proposed capability-map update to maintainer; wrong-class red: probe bug |

Candidate total: **84 probes** — the original 32 over the RH chain, plus the 52 added by §F over the surfaces promoted 2026-08-08 (Mult 17, ZeroSetSlice 14, analysis shelf 21). All C0–C2, no retries, no models, no numerics. A thousand green probes prove nothing about the truth of the Riemann Hypothesis.
**The 84 candidates exceed the per-batch budget cap (§P2, suggested N ≤ 12)
and therefore cannot run as one batch**: if ever authorized, they decompose
into at least three batches (e.g. PB-A regression, PB-B/C composition +
expressibility, PB-D boundary), each with its own frozen header, fixed
question, and separate dated authorization. None is a result; none gets a
ledger row; none selects a route. And once more, verbatim, because every probe
report must end with it: **a thousand green probes prove nothing about the
truth of RH.**

---

## §P0. The gate being designed against (verified quotes)

The S0-TRUST inverse-coverage gate is `scripts/gen_researchos_registry.py`,
run by CI at `.github/workflows/ci.yml:281-282` ("Check ResearchOS result
registry (VERIFIED_RESEARCHOS.md ↔ ResearchOS source) — run: python3
scripts/gen_researchos_registry.py --check"). Its load-bearing properties:

- **Inverse coverage** — `gen_researchos_registry.py:260-266`:
  ```
  uncovered = sorted(set(declarations) - set(cited))
  for name in uncovered:
      errors.append(
          f"inverse coverage: built public declaration {name!r} "
          f"({declarations[name]['file']}:{declarations[name]['line']}) has "
          "no VERIFIED_RESEARCHOS.md row"
      )
  ```
- **Scan surface** — `gen_researchos_registry.py:71-79` (`researchos_files`):
  exactly `ResearchOS.lean` plus every `*.lean` under `ResearchOS/`, minus the
  exact-path exemption `AUDIT_EXEMPT = {"ResearchOS/LedgerAxiomAudit.lean"}`
  (`gen_researchos_registry.py:42`, "by exact path, never by glob"). Files
  outside `ResearchOS/` are invisible to this gate.
- **What counts as a declaration** — `DECL_RE` at
  `gen_researchos_registry.py:58-63` matches kinds
  `theorem|lemma|def|abbrev|instance|opaque|structure|class|inductive`;
  `example` is not in the alternation, and `private`/`local` declarations are
  skipped at `:119`.
- **Companion trap**: a probe file placed under `ResearchOS/` but *not*
  imported fails the isolation gate — `scripts/check_ledger_isolation.py:162-168`
  errors with "`is not transitively imported from ResearchOS.lean — it would
  be source-scanned but never kernel-checked by lake build`" (CI step at
  `ci.yml:291-294`). If it *is* imported, it is built by `lake build`
  (`ci.yml:420`) and enters the no-sorry scan at `ci.yml:359` (`grep …
  'sorry' Ecdlp.lean Ecdlp/ ResearchOS/ ResearchOS.lean`, Targets and the two
  audit harnesses excluded).

So the two candidate homes behave completely differently, and the gate leaves
no third position.

## §P1. Where probes would live

### Option A (RECOMMENDED for all three probe classes): non-built probes lane `domains/riemann-hypothesis/probes/`

Sibling of the existing drafts lane, which already has exactly the needed CI
posture: `domains/riemann-hypothesis/drafts/README.md:8-16` — files there are
"intentionally outside every lake target (`lakefile.toml` declares
`defaultTargets = ["Ecdlp", "ResearchOS"]` …), outside the no-sorry gate's
scan surface, and outside the result registries. **CI does not elaborate the
files in this directory as they stand**." The `probes/` directory does not
exist today; creating it is maintainer decision MD-1.

Verified consequences for a `probes/` lane:
- **Inverse coverage: no interaction.** The registry scans only
  `ResearchOS.lean` + `ResearchOS/**` (`gen_researchos_registry.py:71-79`);
  `domains/**` is never parsed. No probe declaration can ever trigger "built
  public declaration … has no VERIFIED_RESEARCHOS.md row", and no ledger row
  is ever needed. No gate carve-out required.
- **No-sorry gate: no interaction** (`ci.yml:359` scans `Ecdlp.lean Ecdlp/
  ResearchOS/ ResearchOS.lean` only).
- **Isolation gate: no interaction** (`check_ledger_isolation.py:138-168`
  walks `ResearchOS/` only).
- **Artifact manifest: already classified.** `domains/` is a listed path of
  the operations class (`repo/ARTIFACTS.yaml:258`), so new probe files do not
  trip the "unclassified tracked file" failure
  (`scripts/check_repo_artifacts.py:230-236`).
- **Execution semantics (under an authorized batch only).** A probe would be
  run as `lake env lean domains/riemann-hypothesis/probes/<file>.lean` — the
  same mechanism CI uses for open stems (`ci.yml:447-459`, "Typecheck open
  target stems (non-blocking, sorry allowed)", `continue-on-error: true`).
  This gives a *real kernel verdict on the probe file against the built
  oleans* while never entering `lake build`, the ledger, or the registry.
  Class (a) and (b) probes expect exit 0; class (c) negative probes expect
  nonzero exit with a specific error — impossible to host in any built file,
  natural here.
- **Honesty cost, stated plainly:** a green probe here is kernel-checked *at
  run time only*; nothing re-checks it on later pushes. That is the correct
  trade — probes are diagnostics, not results — and the probe log (§P3)
  records the commit + pin each run was taken at.

### Option B: CI-checkable probe target inside `ResearchOS/` — REQUIRES A MAINTAINER GATE CARVE-OUT; NOT DESIGNED IN

Evaluated and rejected as the default, on three verified collisions:
1. **Inverse coverage.** Any `theorem`/`lemma`/`def` in
   `ResearchOS/Probes/*.lean` becomes a "built public declaration" and fails
   CI without a `VERIFIED_RESEARCHOS.md` row
   (`gen_researchos_registry.py:260-266`) — but probes are never ledger rows
   (governance, non-negotiable). The only in-language escapes are
   `example`-only or `private`-only files, which pass solely because `DECL_RE`
   (`:58-63`, `:119`) is blind to them. Relying on that blindness IS a
   carve-out of the "built ⇒ ledgered ⇒ audited" closure and must be recorded
   as an explicit maintainer decision (an amendment to `S0_TRUST_DESIGN.md`
   §1.3.5 semantics plus, if a path exemption is preferred instead, an
   exact-path addition mirroring `AUDIT_EXEMPT` at
   `gen_researchos_registry.py:42`). **This document does not make that
   decision (MD-4).**
2. **Import closure.** Unimported → `check_ledger_isolation.py:162-168` fails;
   imported → built, so a probe failure breaks `lake build` (`ci.yml:420`) and
   negative probes are categorically excluded.
3. **Lane authority.** Wiring a probe step into CI touches
   `.github/workflows/`, which is on the must-not-edit list of both `RH-009`
   and `RH-010` (`tasks/RIEMANN_HYPOTHESIS.md`, the "Files allowed" clause of
   each task); per the S0-TRUST
   precedent such changes belong to a dated ops task or direct maintainer
   action (`S0_TRUST_DESIGN.md` §5, Phase 1: "outside the RH lane's
   files-allowed … requires its own dated task/PR under the repository's ops
   lane or direct maintainer action") (MD-6).

Option B is admissible later only for class (a) regression probes that have
proven durable value, only `example`-only, and only after the maintainer
records the carve-out. Until then: Option A for everything.

## §P2. Per-batch governance template (mandatory header of every batch file)

Grounds: the queue's global hard rule — "Never launch an open-ended model or
compute sweep. Every run needs a fixed question, budget, validator, and stop
condition." (`tasks/RIEMANN_HYPOTHESIS.md`, §Global hard rules, the never-launch-an-open-ended-sweep rule) — and the standing
decision "Do not begin a route proof attempt, large computation, new
equivalence formalization, or autonomous hypothesis sweep" (`:41-43`). A batch
file bearing this header still runs nothing by itself: opening the batch is a
dated maintainer/queue decision (MD-2).

```
BATCH <PB-NNN>  date: <YYYY-MM-DD>  author: <agent/human>
authorization: <link/ref to the dated maintainer/queue decision opening this batch>
pin: mathlib fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (lake-manifest.json:8), lean4 v4.31.0 (lean-toolchain:1)
base commit: <sha of main the oleans were built from>
FIXED QUESTION: one sentence; names the built declarations or the single vocabulary
  gap being probed (e.g. "Do P2/P3/Z8 still instantiate at s = 1/2 + t*I?",
  "Is 'number of zeros with |Im ρ| ≤ T' expressible using only riemannZetaZeros
  and pinned Mathlib, without Finset/counting imports the lane lacks?").
PROBE LIST (frozen before first run): PB-NNN-01 … PB-NNN-kk, each with class
  (a regression | b expressibility | c negative-boundary) and EXPECTED VERDICT
  (ELABORATES | FAILS: <expected error class>).
BUDGET: ≤ N probe files (suggest N ≤ 12); exactly one `lake env lean` invocation
  per file; zero retries; no model calls; no `native_decide`/`decide` on
  nontrivial data (probes are elaboration checks — computation is RH-005
  territory and RH-005 is PARKED, `tasks/RIEMANN_HYPOTHESIS.md`, §`RH-005`).
VALIDATOR: exit code + first-error-line match against the expected-verdict table;
  mechanical, no judgment.
STOP CONDITION: every listed probe attempted exactly once; batch closes on the
  last exit code. A SURPRISE (observed ≠ expected) closes the batch normally and
  is escalated as a finding — it is never "fixed" by editing the probe mid-batch.
NON-RESULTS CLAUSE (verbatim, required): probes are never results or ledger rows;
  a thousand green probes prove nothing about the truth of RH; this batch selects
  no route and changes no barrier row.
```

Probe-class discipline: (a) regression probes instantiate a built theorem
(P1-P5 at `TargetBridge.lean:29,104,115,127,145,179,182,199`; X1-X11 at
`Xi.lean:41-248`; Z1-Z9 at `Conj.lean:58-452`) at a concrete point and expect
ELABORATES; (b) expressibility probes write only the *statement* (body `sorry`
is fine — the lane is outside the no-sorry scan) and expect the statement to
elaborate or fail, which is the cheapest falsifier of an ill-posed idea; (c)
negative probes state a concept the vocabulary honestly lacks (zero counting,
growth order, zero enumeration — exactly what the accepted M-surface excludes,
`tasks/RIEMANN_HYPOTHESIS.md`, §`RH-009` exit criteria: "free of enumeration, counting, growth,
Hadamard products, Li coefficients, and zero-simplicity claims") and expect
FAILS; the recorded error *is* the boundary documentation.

## §P3. Probe log — `domains/riemann-hypothesis/probes/PROBE_LOG.md` (never the ledger; created only under MD-1)

Append-only, one row per probe run. Required file header, verbatim intent:

> This file is a diagnostic log, NOT a result ledger. No row here is a
> theorem, a claim, or evidence about RH. It is never parsed by
> `ledger_utils.parse_ledger` or `parse_researchos_ledger`, never cited from
> `VERIFIED.md` or `VERIFIED_RESEARCHOS.md`, and never feeds any registry,
> audit, badge, or counter. A thousand green probes prove nothing about the
> truth of RH.

Columns (12 is NOT required — deliberately use a different column count than
the ledger's strict 12-cell contract, `VERIFIED_RESEARCHOS.md:14-15`, so a
misdirected `parse_researchos_ledger` hard-fails instead of mis-parsing):

| batch | probe_id | class | file | targets (built decls exercised) | expected | observed (exit code + first error line, verbatim, for FAILS) | commit@pin | date |

Rules: observed verdicts are one of `PASS_AS_EXPECTED`, `FAIL_AS_EXPECTED`,
`SURPRISE`. A `SURPRISE` row must name the follow-up (a finding note under
`notes/`, or a proposed queue item) and must not be rewritten. Rows are never
deleted; a retired probe gets a strikethrough-free `retired` note in a
trailing column, not removal.

## §P4. Promotion path for a probe worth keeping

A probe never promotes *as a probe*. Worth keeping means one of:

1. **Regression probe (a) that caught a real break** (e.g. a Mathlib-bump
   rehearsal changes an X/Z statement's elaboration). Path: its statement is
   not a new result — it instantiates ledgered theorems — so it stays in the
   probes lane permanently and is listed in the batch file as `pinned: true`.
   Moving it to a built CI-checked location is exactly Option B and waits on
   the maintainer carve-out decision (MD-4). No ledger row ever.
2. **Expressibility probe (b) whose statement turns out load-bearing** for a
   contract. Path: the statement leaves the probe world entirely and enters
   the lane's normal three-step pipeline, exactly as the xi, conjugation, and
   multiplicity packages did: contract statement surface + drafts mirror
   (`domains/riemann-hypothesis/drafts/`, non-built) → independent acceptance
   as its own change (RH-009 pattern) → kernel promotion as a separate change
   with its `RH-*` ledger row, regenerated registry, audit line, and promotion
   review in one PR, or inverse coverage fails CI (drafts/README.md promotion
   invariant; RH-010 pattern, `tasks/RIEMANN_HYPOTHESIS.md`, §`RH-010`). At that
   point it is an ordinary declaration; the originating probe is marked
   `retired → promoted as <claim_id>` in the log. The probe's earlier green is
   not evidence in that pipeline — acceptance and promotion re-establish
   everything from scratch.
3. **Negative probe (c)**: never promotes. Its artifact is the log row; if the
   boundary it documents deserves permanence, the correct home is a dated
   negative-inventory line in
   `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` — an RH-lane edit
   requiring its own dated decision, proposed to the maintainer, not made here
   (MD-5).

Opening any probe batch, creating `probes/`, and the Option-B carve-out are
each maintainer/queue decisions; this design supplies the template they would
authorize against, and nothing more. Probes are never results or ledger rows;
no route is selected; RH-005 stays parked; a thousand green probes prove
nothing about the truth of RH.

---

## Annex R. Red-team pass — defects found in the consolidated draft, and fixes applied

The two source sections were attacked for: wording that authorizes a run,
unparks RH-005, changes a gate, counts probes as results, or frames probes as
RH evidence. Defects found and fixed in this consolidation:

- **R1 — Self-authorizing run order (fixed).** The draft taxonomy header read
  "nothing here may be run without the batch governance in §0", and §0 defined
  a batch as "a **fixed** file list (this document's tables) … stop condition
  = end of the fixed list, one pass", with §E adding "Total: 32 probes …
  one pass, no retries". Together these made the document itself satisfy the
  four-part sweep rule (fixed question, budget, validator, stop condition) —
  i.e., a design note that doubled as a ready-to-fire run order, where mere
  §0-compliance would "authorize" execution with no human decision. Fix: the
  status header now states the document carries no batch ID and authorizes
  nothing; §0's batch definition is explicitly conditional ("an *authorized*
  probe batch would be…") and ends "This document is not such a batch and does
  not open one"; §E's total is relabeled "candidate total"; §P1's "A probe is
  run on demand" became "would be run … under an authorized batch only"; §P2
  gained a mandatory `authorization:` header line pointing at the dated
  opening decision (MD-2).
- **R2 — Budget contradiction enabling a sweep-shaped run (fixed).** The
  taxonomy's §E declared a single "one pass" over all 32 probes while the
  harness's §P2 caps a batch at N ≤ 12 files. Read together, the larger number
  would have licensed running the whole battery as one un-capped batch —
  exactly the open-ended-sweep shape the queue forbids. Fix: §E now states the
  84 candidates cannot run as one batch and must decompose into at least seven
  separately authorized batches, each with its own frozen header and fixed
  question.
- **R3 — In-loop RH-lane edit smuggled into the D-class action (fixed).** §D
  read "the capability boundary moved … and MATHLIB_CAPABILITY_MAP.md is
  stale, update it", and §E's action column read "green: dated capability-map
  update" — imperative wording instructing an RH-lane file edit as an
  automatic consequence of a probe verdict, contradicting §P4.3 (capability-map
  edits are dated decisions proposed to the maintainer). A probe outcome
  silently editing a lane document is a probe counting as a result. Fix: both
  places now say the follow-up is a *proposed* dated update submitted to the
  maintainer (MD-5), never an in-loop edit.
- **R4 — Premature artifact creation (fixed).** §P3 specified
  `probes/PROBE_LOG.md` in the present tense as though the file exists or is
  to be created now, while §P4 elsewhere said creating `probes/` is a
  maintainer decision. Fix: §P3's heading and §0/§P1 now mark the lane and log
  as non-existent today, created only under MD-1; §P1 Option A states the
  directory "does not exist today".
- **R5 — Probe green leaking into the promotion pipeline as evidence
  (hardened).** §P4.2's promotion path could be read as letting an
  expressibility probe's green carry weight into acceptance. Fix: added the
  sentence that the probe's earlier green is not evidence in that pipeline —
  acceptance and promotion re-establish everything from scratch. Relatedly,
  §C's "licenses only 'a contract could be drafted'" now adds that drafting
  itself still enters the queue through its normal pipeline.
- **R6 — RH-005 adjacency left implicit (hardened).** Class A probes discharge
  side goals with `norm_num`/`simp` on literal casts; an attacker could frame
  any arithmetic as "bounded computation" creeping toward RH-005, or
  conversely cite the probes' harmlessness to argue RH-005's parking is moot.
  Fix: §0's RH-005 bullet now states explicitly that these discharges are
  elaboration-time literal-cast arithmetic, not bounded numerics, and that
  nothing here touches or *counts toward* RH-005's activation conditions.

Attack surfaces checked and found already sound (no fix needed): no wording
edits any gate file (`gen_researchos_registry.py`, `check_ledger_isolation.py`,
`ci.yml` are quoted, never amended — Option B's required amendments are
specified as MD-4/MD-6 and not made); no probe references the M-surface or the
RH-010 draft; the verbatim sentence "a thousand green probes prove nothing
about the truth of RH" appears in §0, §E, §P2's template, §P3's header, and
§P4; probes are excluded from ledger, registry, audit, badge, and counter by
construction; no route is selected or preferred anywhere.

---

## What this note does NOT do

- It does **not** run, schedule, or authorize any probe, batch, build,
  elaboration, or model call. No `lake`, `lean`, or API invocation occurred in
  producing it, and none is licensed by it.
- It does **not** create `domains/riemann-hypothesis/probes/`,
  `PROBE_LOG.md`, or any batch file.
- It does **not** unpark RH-005, advance its activation conditions, or perform
  any bounded computation; it does not occupy or contend for the queue's
  single ACTIVE slot (RH-010 holds it).
- It does **not** modify, exempt, or reinterpret any gate:
  `gen_researchos_registry.py`, `check_ledger_isolation.py`, the no-sorry
  scan, and `.github/workflows/ci.yml` are untouched and quoted only.
- It does **not** add any row to `VERIFIED.md` or `VERIFIED_RESEARCHOS.md`,
  and no probe verdict ever will.
- It does **not** select, activate, prefer, or argue for any RH route, and it
  must never be cited as doing so.
- It does **not** constitute evidence about the Riemann Hypothesis. A thousand
  green probes prove nothing about the truth of RH.

## Maintainer decisions required before anything here becomes real

- **MD-1 — Create the non-built probes lane.** Whether to create
  `domains/riemann-hypothesis/probes/` (with `PROBE_LOG.md` and a README
  mirroring `drafts/README.md`'s CI-posture statement). Dated decision;
  operations-class paths under `domains/` per `repo/ARTIFACTS.yaml:258`.
- **MD-2 — Open each probe batch.** Every batch is individually authorized:
  assign `PB-NNN`, freeze the probe list and expected verdicts, record the
  authorization in the batch header. The 84 candidates require at least seven
  such decisions (per-batch cap N ≤ 12); the maintainer sets N.
- **MD-3 — Per-file timeout.** The maintainer sets the file-level `lake env
  lean` timeout for probe runs (suggested: the CI default).
- **MD-4 — Option-B built probe lane carve-out (deferred; not recommended
  now).** If a CI-checked probe lane inside `ResearchOS/` is ever wanted:
  a dated amendment to `S0_TRUST_DESIGN.md` §1.3.5 semantics (or an exact-path
  exemption mirroring `AUDIT_EXEMPT`, `gen_researchos_registry.py:42`),
  restricted to `example`-only class-(a) files. This note specifies the shape
  and does not make the decision.
- **MD-5 — Capability-map updates on a D-probe green.** Any edit to
  `MATHLIB_CAPABILITY_MAP.md` (dated negative-inventory line, or removal when
  a boundary moves) is proposed to the maintainer with the probe's log row and
  grep evidence attached; never applied in-loop.
- **MD-6 — Any CI wiring for probes.** Touches `.github/workflows/`, which is
  on the must-not-edit lists of RH-009 and RH-010 (`tasks/RIEMANN_HYPOTHESIS.md`,
  the "Files allowed" clause of each task); belongs to a dated ops-lane task or direct maintainer
  action per the S0-TRUST precedent.

---

Verified source anchors — repo: `ResearchOS.lean:5-9`;
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/TargetBridge.lean:18,29,104,115,127,145,162-164,179,182,191-193,199`;
`.../Xi.lean:12,17,41,46,61,72,78,89,120,157,164-170,180,192,208,218-222,226-229,248`;
`.../Conj.lean:25,30,32-33,58,86,163,179,234,246,256,262,276-280,282,292,301-304,306,317,336,357,440,452`;
`lake-manifest.json:8`; `lean-toolchain:1`; `lakefile.toml:2`;
`VERIFIED_RESEARCHOS.md:14-15,37`;
`scripts/gen_researchos_registry.py:40,42,58-63,71-79,119,260-266`;
`scripts/check_ledger_isolation.py:138-168`;
`.github/workflows/ci.yml:281-282,291-294,359,420,447-459`;
`domains/riemann-hypothesis/S0_TRUST_DESIGN.md:487`;
`domains/riemann-hypothesis/drafts/README.md:8-16`;
`domains/riemann-hypothesis/MULTIPLICITY_QUEUE_ENTRY_PROPOSAL.md:140`;
`repo/ARTIFACTS.yaml:258`; `scripts/check_repo_artifacts.py:230-236`;
`tasks/RIEMANN_HYPOTHESIS.md` — cited throughout by section (§Current decision,
§Global hard rules, §`RH-005`, §`RH-009`, §`RH-010`, §`RH-012`, §`RH-013`) rather
than by line, per the locator policy at the end of this document; every raw line
anchor this list previously carried had drifted and none resolved.
Pin (checkout `/workspace/leanprover-community/mathlib4` @
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`):
`Mathlib/NumberTheory/LSeries/RiemannZeta.lean:63,89,99,105,144,149,171,182`;
`Mathlib/NumberTheory/LSeries/ZetaZeros.lean:33,35,57,60,64`;
`Mathlib/NumberTheory/LSeries/Nonvanishing.lean:410`;
`Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:431`;
`Mathlib/NumberTheory/LSeries/HurwitzZetaValues.lean:226,232`;
`Mathlib/Analysis/Analytic/Order.lean:47,86,120,175,497`;
`Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:43,66,73`;
`Mathlib/Analysis/Meromorphic/Divisor.lean:39`;
`Mathlib/Analysis/Meromorphic/Order.lean:47`; absence greps (zero hits at
pin): `growthOrder`, `argumentPrinciple|argument_principle`,
`explicitFormula|explicit_formula|vonMangoldt_explicit`, entire-function
Hadamard factorization (only `Mathlib/Analysis/Matrix/Order.lean` matches
"hadamard" under Analysis/), `def riemannXi` (name is repo-owned).

---

## §F. Candidate probes over the surfaces promoted 2026-08-08 (`RH-013`)

Status, inherited verbatim from this document's header and restated because it
is the whole point: **DESIGN ONLY — UNAUTHORIZED TO RUN.** This section carries
no batch ID, freezes no probe list, and authorizes nothing. Every entry is a
*candidate*. A probe list becomes frozen only inside a batch header (§P2) opened
by an explicit dated maintainer decision (§MD), and MD-1..MD-6 remain
outstanding. A thousand green probes prove nothing about the truth of the Riemann Hypothesis. A red Class D probe documents a boundary in
the language; it is not a discovery.

Why this section exists. §0's scope statement was written 2026-08-07 and named
three built modules as "the only surface any probe may reference". That sentence
is a governance CONSTRAINT, so when it went stale it did not merely omit
material — it forbade probes that had become entirely legitimate. Between then
and 2026-08-08, `Mult.lean` (34 declarations) was promoted in PR #313,
`ZeroSetSlice.lean` (23) in PR #320, and five domain-neutral modules (35) in
PRs #318 and #319: 92 built declarations across seven modules, unreachable by
any probe on the strength of a sentence time had falsified. §0 is corrected in
the same change as this section.

Every declaration cited below was opened in the BUILT module and carries a
`VERIFIED_RESEARCHOS.md` ledger row. No candidate references a drafts-lane file.
No candidate selects a route: none requires a cutoff shape, contour, truncation
family (`|ρ| ≤ T`, `|Im ρ| < T`) or test-function class, and `RH-002`'s three
`PARK` dispositions remain CONFIRMED.
### §F.0 What two adversarial reviews changed before anything was written

The inventory below is not what three drafting agents produced. Two independent
reviewers (governance/claim-boundary; accuracy/staleness) returned
ACCEPT_WITH_FIXES with fifteen blocking findings between them. The corrections
that changed content, rather than wording, are recorded here because a later
reader deserves to know which entries were repaired and why:

1. **Three candidates carried "expect GREEN" over a proof body that does not
   exist** — `PM-A5`, `SH-A5` and `SH-B4` end in comments or a literal `…`.
   Both reviewers caught this independently. They are relabelled **SKETCH —
   expected verdict UNDETERMINED**, and are not batch-eligible until a body
   exists. A predicted verdict over an unwritten proof is exactly the kind of
   claim this document exists to prevent.
2. **Two candidates violated the slice package's own neutrality rule.**
   `PS-A1` and `PS-A2` instantiated the compact at `Metric.closedBall (0 : ℂ) 1`,
   while `ZeroSetSlice.lean:158-161` states verbatim that no instantiation at
   `Metric.closedBall` appears in the package, as a death condition. A disc is
   readable as a truncation family, which is the route-selection tell. Both are
   respecified over `isCompact_singleton`, which exercises the identical
   mechanics with no cutoff reading.
3. **One candidate presented a classical expectation as a repository-derived
   fact.** `SH-C2` asserted that GO-8's inequality cannot be an equality, with
   a witness (`exp` against `exp ∘ neg`) that no built row supports. Restated as
   a classical expectation, explicitly not established anywhere here.
4. **One value claim was simply false.** `PS-B1` claimed it would catch a
   regression "while the whole build stays green"; the build already exercises
   that orientation at `ZeroSetSlice.lean:342`. The narrower, true claim is kept.
5. **The refresh introduced new staleness of its own**, caught before it landed:
   two wrong anchors, including `ResearchOS.lean:9-13` for the shelf imports
   (they are at `:10-14`). Corrected. This is the same failure mode as the
   defect being fixed, appearing inside the fix — recorded rather than tidied
   away.

### §F.1 Surface: Mult — 17 candidates (A:5, B:4, C:5, D:3)
Candidate count exceeds §P2's suggested cap of N ≤ 12 per batch, so if this
surface is ever authorized it decomposes into more than one batch.

| id | class | expected | uses | sketch / what it catches |
|---|---|---|---|---|
| `PM-A1` | A | GREEN | `riemannXi_divisor_apply` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:388 — "theorem riemannXi_divisor_apply {U : Set ℂ} {z : ℂ} (hz : z ∈ U) : Meromor | example : MeromorphicOn.divisor riemannXi Set.univ 0 = 0 ∧ MeromorphicOn.divisor riemannXi {z : ℂ \| 0 < z.re ∧ z.re < 1} 0 = 0 := by   constructor   · rw [riemannXi_divisor_apply (Set.mem_univ (0 : ℂ)),         (analyticOnNhd_riemannXi Set.univ 0 (Set.mem_univ 0)).analyticOrderAt_eq_zero.mpr        — *This is the only concrete divisor VALUE the built surface can pin down, and it pins it twice by two disjoint routes that must both keep returning 0 for different reasons. It is the single probe that makes the untop-zero * |
| `PM-A2` | A | GREEN | `riemannXi_divisor_univ_one_sub` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:593 — "theorem riemannXi_divisor_univ_one_sub (s : ℂ) : MeromorphicOn.divi | example : MeromorphicOn.divisor riemannXi Set.univ 1 = MeromorphicOn.divisor riemannXi Set.univ 0 := by   simpa using riemannXi_divisor_univ_one_sub 0 — *M14's three signatures are all universally quantified, so a bare instantiation tests nothing; this one tests the two things that can actually break. First, the point argument must normalize `1 - 0` to the literal `1` — t* |
| `PM-A3` | A | GREEN | `analyticOrderAt_riemannZeta_one_sub` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:253 — "theorem analyticOrderAt_riemannZeta_one_sub {s : ℂ} (h0 : 0 <  | example : analyticOrderAt riemannZeta (1 - (1 / 2 + Complex.I))     = analyticOrderAt riemannZeta (1 / 2 + Complex.I) :=   analyticOrderAt_riemannZeta_one_sub     (by norm_num [Complex.add_re, Complex.I_re])     (by norm_num [Complex.add_re, Complex.I_re]) — *Every ζ-side declaration of this package (M4 :253, M6 :310, M8 :342, M16E :812, M16F :823, and all three M17 signatures) is gated behind the identical `0 < s.re ∧ s.re < 1` pair, and every future caller must discharge it* |
| `PM-A4` | A | GREEN | `riemannXi_divisor_nonneg` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:410 — "theorem riemannXi_divisor_nonneg (U : Set ℂ) : 0 ≤ MeromorphicOn.divisor  | example (z : ℂ) : 0 ≤ MeromorphicOn.divisor riemannXi Set.univ z := by   simpa using Function.locallyFinsuppWithin.le_def.mp (riemannXi_divisor_nonneg Set.univ) z — *M11 is stated in the locallyFinsuppWithin order, not pointwise; every consumer must cross the FunLike/Pi-order seam to use it. ZeroSetSlice.lean:391 and :436 already cross exactly this seam twice (OBLIG S1N1-3, recorded * |
| `PM-A5` | A | **SKETCH — UNDETERMINED** | The statement under test is `analyticOrderAt_riemannZeta_one_sub` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:253 (hypotheses `h0 h1`); its non-decorat | example : ¬ (∀ s : ℂ, analyticOrderAt riemannZeta (1 - s) = analyticOrderAt riemannZeta s) := by   intro h   -- ζ is analytic at 3 and at -2 (both ≠ 1), via differentiableAt_riemannZeta + DifferentiableOn.analyticAt   -- analyticOrderAt riemannZeta 3 = 0        (Nonvanishing.lean:410 + Order.lean:13 — *It machine-checks the falsity witness that justifies M4/M6/M8/M16E/M16F/M17 all carrying strip hypotheses — currently asserted in a comment (Mult.lean:229-239) and checked by nothing. Its unique catch: it is a permanent * **[no proof body; not batch-eligible]** |
| `PM-B1` | B | GREEN | `riemannXi_zero_mem_critical_strip` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean:192 — "theorem riemannXi_zero_mem_critical_strip {s : ℂ} (hz : riemannXi  | example {s : ℂ} (hz : riemannXi s = 0) :     analyticOrderAt riemannZeta (1 - (starRingEnd ℂ) s) = analyticOrderAt riemannZeta s :=   analyticOrderAt_riemannZeta_one_sub_conj     (riemannXi_zero_mem_critical_strip hz).1 (riemannXi_zero_mem_critical_strip hz).2 — *The Xi↔Mult seam: Xi.lean:192 is the tree's only producer of the strip pair, and Mult's whole ζ block is its only heavy consumer, yet no built declaration puts them adjacent — Mult reaches ζ through X11 (Xi.lean:248), ne* |
| `PM-B2` | B | GREEN | `analyticOrderAt_riemannXi_conj` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Conj.lean:452 — "theorem analyticOrderAt_riemannXi_conj (s : ℂ) : analyticOrderAt ri | example (s : ℂ) :     analyticOrderAt riemannXi ((starRingEnd ℂ) (1 - s))       = analyticOrderAt riemannXi (1 - (starRingEnd ℂ) s) := by   rw [analyticOrderAt_riemannXi_conj (1 - s),        -- Conj.lean:452, conjugation leg first       analyticOrderAt_riemannXi_one_sub s,           -- Mult.lean:197 — *Mult.lean's COMPOSITE COMMUTATION CHECK (:294-308) is the package's justification for choosing one rewrite order over the other, and it is prose. This probe closes the square: it forces the conjugation-first route (Conj.* |
| `PM-B3` | B | GREEN | `riemannXi_divisor_support` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:538 — "theorem riemannXi_divisor_support (U : Set ℂ) : Function.support (Meromo | example {K : Set ℂ} (hK : IsCompact K) :     (K ∩ (Set.univ ∩ riemannXi ⁻¹' {0})).Finite := by   rw [← riemannXi_divisor_support Set.univ]   exact riemannXi_divisor_inter_support_finite Set.univ hK — *This is the Mult↔ZeroSetSlice seam at its most fragile point: the two modules must agree, syntactically, on the spelling `Function.support (MeromorphicOn.divisor riemannXi U)` versus the reducible abbrev `D.support` (Loc* |
| `PM-B4` | B | GREEN | `riemannXi_divisor_finsum_mem_comp_conj` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/ZeroSetSlice.lean:504 — "theorem riemannXi_divisor_finsum_mem_comp_conj {U : | example {U : Set ℂ} (hU : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (K : Set ℂ) :     ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U ((starRingEnd ℂ) z)       = ∑ᶠ z ∈ (starRingEnd ℂ) '' K, MeromorphicOn.divisor riemannXi U z :=   (riemannXi_divisor_finsum_mem_comp_conj hU K).trans     (riemannXi_divisor — *The slice ships two forms per symmetry — summand transport and window transport (:457-466) — both derived from the same M15 pointwise identity, and never relates them. This probe asserts the relation, which is the statem* |
| `PM-C1` | C | GREEN | `meromorphicOn_riemannXi` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:377 — "theorem meromorphicOn_riemannXi (U : Set ℂ) : MeromorphicOn riemannXi U";  | #check (MeromorphicOn.divisor riemannXi Set.univ : Function.locallyFinsupp ℂ ℤ) — *It states, in one line and with no proof, that the built ξ divisor inhabits the pin's GLOBAL divisor type — the argument type of every whole-plane divisor API at the pin, including the counting layer (see `nothing_useful* |
| `PM-C2` | C | GREEN | `analyticOrderAt_riemannXi_ne_top` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:444 — "theorem analyticOrderAt_riemannXi_ne_top (z : ℂ) : analyticOrderA | #check ((∀ z : ℂ, analyticOrderAt riemannXi z ≠ ⊤) ∧ Complex.growthOrder riemannXi ≠ ⊤ : Prop) -- left conjunct: exactly M12 (Mult.lean:444), BUILT and true. -- right conjunct: a sentence about the growth order of ξ. NOT built, NOT claimed, -- and NOT implied by the left conjunct. — *Mult.lean spends four separate passages (the header :15-16, M12's READING OF "ORDER" :420-428, M16' :800-810, and the closing boundary :1001) insisting that finite LOCAL analytic order is not a growth order — and until P* |
| `PM-C3` | C | GREEN | `riemannZeta_divisor_strip_apply` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:786 — "theorem riemannZeta_divisor_strip_apply {z : ℂ} (hz : z ∈ {w : ℂ \ | #check (∀ K : Set ℂ, IsCompact K →   (0 : ℤ) ≤ ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannZeta {w : ℂ \| 0 < w.re ∧ w.re < 1} z : Prop) — *Mult supplies the ζ-on-Ω divisor (M16–M17, eight declarations) and ZeroSetSlice supplies the compact-sum layer — but only for ξ. Nothing records whether that asymmetry is a vocabulary gap or a proof gap. Green settles it* |
| `PM-C4` | C | GREEN | `riemannXi_divisor_univ_one_sub` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:593 (quoted in PM-A2); DESIGN NOTE (DEFERRED-1) at Mult.lean:556-565 — "St | #check (⇑(MeromorphicOn.divisor riemannXi Set.univ) ∘ (fun s : ℂ => 1 - s)           = ⇑(MeromorphicOn.divisor riemannXi Set.univ) : Prop) — *It sharpens DEFERRED-1 from "the invariance cannot be stated at object level" to the true and much more useful statement: the FUNCTION-level invariance is statable today (and would follow from M14RU by `funext`), and wha* |
| `PM-C5` | C | GREEN | `riemannZeta_divisor_strip_one_sub` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:863 — "theorem riemannZeta_divisor_strip_one_sub (s : ℂ) : MeromorphicO | #check (∀ U : Set ℂ, (∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U) →   ∀ s : ℂ, MeromorphicOn.divisor riemannZeta U (1 - s)             = MeromorphicOn.divisor riemannZeta U s : Prop) -- ELABORATES. The proposition is FALSE (witness: U = Set.univ, s = 3, 1 - 3 = -2; -- see PM-A5 and Mult.lean:229-239). Green is ab — *It is the battery's calibration probe: a green C verdict attached to a proposition the package itself records as false. §C's standing caveat — "Lean's total functions let many meaningless statements typecheck" — is curre* |
| `PM-D1` | D | RED | `riemannXi_divisor_support` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:538 (quoted in PM-B3) supplies the object being summed over; `riemannXi_divisor | #check ∑ ρ ∈ Function.support (MeromorphicOn.divisor riemannXi Set.univ),          MeromorphicOn.divisor riemannXi Set.univ ρ -- EXPECTED RED: binder/type mismatch — the `∑ x ∈ s` binder demands a Finset ℂ, -- and Function.support … : Set ℂ. — *PROBE_BATTERY_DESIGN.md's D1 probed this boundary against `riemannZetaZeros`, a set with no multiplicity attached; the objection to that probe was always that the real question is whether the MULTIPLICITY-weighted global* |
| `PM-D2` | D | RED | `riemannXi_divisor_support` at Mult.lean:538 (the support object); `riemannXi_divisor_inter_support_finite` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/ZeroSetSl | #check (Function.support (MeromorphicOn.divisor riemannXi Set.univ)).toFinset -- EXPECTED RED: failed to synthesize `Fintype ↥(Function.support …)`. — *It fixes the exact altitude of the built finiteness story, which is easy to overstate now that the surface carries both `Countable` (slice :340) and compact-intersection `Finite` (slice :278) results. The red says: on th* |
| `PM-D3` | D | RED | DESIGN NOTE (DEFERRED-1) at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:556-565, quoted in full under PM-C4 — the load-bearing absence claim that makes M1 | #check MeromorphicOn.divisor_comp -- EXPECTED RED: unknown identifier. -- Twin spelling, same boundary, would need its own file under a one-#check-per-file -- batch convention:  #check Function.locallyFinsuppWithin.comap -- (also EXPECTED RED: unknown identifier) — *This is the only probe in the battery that watches a design assumption of the built module rather than the module itself. Six of the surface's thirty-four declarations are pointwise ONLY because no pushforward exists; if* |

**Where this surface supports nothing, which is a finding and not a gap:** FOUR CLASSES OF PROBE THIS SURFACE DOES NOT SUPPORT, each a real finding.

1. NO CLASS D PROBE OF THE FORM "MULTIPLICITY-WEIGHTED COUNTING IS ABSENT" IS DEFENSIBLE HERE, AND THE DESIGN'S FRAMING IS WRONG. At the pin, Mathlib/Analysis/Complex/ValueDistribution/LogCounting/Basic.lean:96 declares "noncomputable def logCounting {E : Type*} [NormedAddCommGroup E] [ProperSpace E] : locallyFinsupp E ℤ →+ (ℝ → ℝ)" inside `namespace Function.locallyFinsuppWithin` (:49), and :305 proves "logCounting f 0 = (divisor f univ)⁺.logCounting". Its input type is EXACTLY the type of `MeromorphicOn.divisor riemannXi Set.univ` (LocallyFinsupp.lean:61's abbrev; see PM-C1). So a multiplicity-weighted, logarithmically-weighted counting function over the built ξ divisor is expressible at the pin today — the boundary is not vocabulary, it is that no repo declaration connects the two, and connecting them is not free: `logCounting` carries the `‖z‖ ≤ r` closed-ball truncation inside its own definition (`toClosedBall r`, used at :96 and characterized at :71). Writing any probe over it therefore adopts a truncati

### §F.2 Surface: ZeroSetSlice — 14 candidates (A:4, B:4, C:3, D:3)
Candidate count exceeds §P2's suggested cap of N ≤ 12 per batch, so if this
surface is ever authorized it decomposes into more than one batch.

| id | class | expected | uses | sketch / what it catches |
|---|---|---|---|---|
| `PS-A1` | A | GREEN | `IsCompact.inter_riemannXi_zeroSet_finite` at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/ZeroSetSlice.lean:163 — quoted: `theorem IsCompact.inter_riemannXi_zeroSet | example : (({(0 : ℂ)} : Set ℂ) ∩ riemannXi ⁻¹' {0}).Finite :=   isCompact_singleton.inter_riemannXi_zeroSet_finite    -- [C1] — *This is the only cheap check on the package's one deliberately odd name: a ROOT-level theorem placed in the `IsCompact` namespace so that dot notation on a compactness witness resolves (mirroring the pin's `IsCompact.int* **[witness respecified from the drafters' `Metric.closedBall (0 : ℂ) 1` to `isCompact_singleton`: `ZeroSetSlice.lean:158-161` forbids instantiating the compact at a disc as a death condition, because a disc reads as a truncation family and a truncation family is a route selection. The singleton exercises the identical mechanics with no cutoff reading.]** |
| `PS-A2` | A | GREEN | `riemannXi_divisor_finsum_mem_mono` at ZeroSetSlice.lean:425 — quoted: `theorem riemannXi_divisor_finsum_mem_mono (U : Set ℂ) {K₁ K₂ : Set ℂ}` / `    (hK₂ : IsCompact K₂) | example (U : Set ℂ) :     ∑ᶠ z ∈ (∅ : Set ℂ), MeromorphicOn.divisor riemannXi U z       ≤ ∑ᶠ z ∈ ({(0 : ℂ)} : Set ℂ), MeromorphicOn.divisor riemannXi U z :=   riemannXi_divisor_finsum_mem_mono U isCompact_singleton (Set.empty_subset _)    -- [C1] — *It pins the R5 asymmetry — a reviewed design property that no gate enforces. Nothing in the repo would fail if someone "tidied" the signature into `(hK₁ : IsCompact K₁) (hK₂ : IsCompact K₂)`: the module would still build* **[witness respecified from the drafters' `Metric.closedBall (0 : ℂ) 1` to `isCompact_singleton`: `ZeroSetSlice.lean:158-161` forbids instantiating the compact at a disc as a death condition, because a disc reads as a truncation family and a truncation family is a route selection. The singleton exercises the identical mechanics with no cutoff reading.]** |
| `PS-A3` | A | GREEN | `riemannXi_divisor_finsum_mem_comp_one_sub` at ZeroSetSlice.lean:470 — quoted: `theorem riemannXi_divisor_finsum_mem_comp_one_sub {U : Set ℂ}` / `    (hU : ∀ z : ℂ, (1 -  | example (K : Set ℂ) :     ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi Set.univ (1 - z)       = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi Set.univ z :=   riemannXi_divisor_finsum_mem_comp_one_sub (fun z => by simp) K    -- [C1] — *The six Block-D symmetry lemmas all take their window hypothesis in the iff shape `∀ z, σ z ∈ U ↔ z ∈ U`, and every future consumer must produce one. No built declaration in the slice ever discharges such an hU — the mod* |
| `PS-A4` | A | GREEN | `image_one_sub_conj_of_symm` at ZeroSetSlice.lean:611 — quoted: `theorem image_one_sub_conj_of_symm {K : Set ℂ}` / `    (hK : ∀ z : ℂ, (1 - (starRingEnd ℂ) z) ∈ K ↔ z ∈ K | example : (fun w : ℂ => 1 - (starRingEnd ℂ) w) '' Set.univ = Set.univ :=   image_one_sub_conj_of_symm (fun z => by simp)    -- [C1] — *Block E (three declarations, RH-SLICE-N19A/B/C) is the only block of the package with zero consumers anywhere in the repository — nothing built, drafted, or ledgered applies it, because it was exported for hypothetical f* |
| `PS-B1` | B | GREEN | `IsCompact.inter_riemannXi_zeroSet_finite` at ZeroSetSlice.lean:163 (quoted in PS-A1); `riemannXi_divisor_support` (M13) at Mult.lean:538 — quoted: `theorem riemannXi_div | -- re-derives RH-SLICE-D8 by the route the built proof does NOT take example (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :     (K ∩ Function.support (MeromorphicOn.divisor riemannXi U)).Finite := by   refine Set.Finite.subset hK.inter_riemannXi_zeroSet_finite ?_   -- slice D4   rw [riemannXi_divisor_ — *Highest-value probe on this surface. The built D8 proof (ZeroSetSlice.lean:280-299) goes through M9/M10 and the LocallyFinsupp carrier, and NEVER touches M13; the M13 route was written down in the module as an alternativ* **[rationale corrected in review; see §F.0]** |
| `PS-B2` | B | GREEN | `riemannXi_divisor_inter_support_finite` at ZeroSetSlice.lean:278 (quoted in PS-B1) — its `Set.Finite` term is the index of the honest finite sum, named in the statement  | -- every point the compact sum actually sums over is a genuine ξ zero example (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :     ((riemannXi_divisor_inter_support_finite U hK).toFinset : Set ℂ) ⊆ riemannXi ⁻¹' {0} := by   rw [Set.Finite.coe_toFinset, riemannXi_divisor_support U]        -- slice D8 ind — *N1.2 is the well-definedness bridge for the whole Block C/D sum vocabulary, and its right-hand side sums over a Finset built from a PROOF TERM (`(riemannXi_divisor_inter_support_finite U hK).toFinset`). Nothing anywhere * |
| `PS-B3` | B | GREEN | `riemannXi_divisor_finsum_mem_nonneg` at ZeroSetSlice.lean:387 — quoted: `theorem riemannXi_divisor_finsum_mem_nonneg (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :` / `    | example {K : Set ℂ} (hK : IsCompact K) (hKs : K ⊆ {z : ℂ \| 0 < z.re ∧ z.re < 1}) :     0 ≤ ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannZeta {w : ℂ \| 0 < w.re ∧ w.re < 1} z := by   have h : ∀ z ∈ K, MeromorphicOn.divisor riemannZeta {w : ℂ \| 0 < w.re ∧ w.re < 1} z       = MeromorphicOn.divisor riemannX — *Three built modules in one chain (ZeroSetSlice + Mult + Xi), and it is the exact composition a ζ-side successor to the slice would have to perform. Two things it catches that nothing else does. First: the slice is ξ-only* |
| `PS-B4` | B | GREEN | `riemannXi_conj` (Z7) at ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Conj.lean:282 — quoted: `theorem riemannXi_conj (s : ℂ) :` / `    riemannXi ((starRingEnd ℂ) s) | example {K : Set ℂ} (hK : IsCompact K) :     (K ∩ (starRingEnd ℂ) ⁻¹' (riemannXi ⁻¹' {0})).Finite := by   have hZ : (starRingEnd ℂ) ⁻¹' (riemannXi ⁻¹' {0}) = riemannXi ⁻¹' {0} := by     ext z     simp only [Set.mem_preimage, Set.mem_singleton_iff, riemannXi_conj,       starRingEnd_apply, star_eq_zer — *The slice made a recorded decision NOT to introduce a `riemannXiZeros` definition (ZeroSetSlice.lean:96-98, contract §1 Decision 1, death condition 4): the zero set is spelled inline as `riemannXi ⁻¹' {0}` at every use s* |
| `PS-C1` | C | GREEN | `riemannXi_divisor_finsum_mem_eq_sum` at ZeroSetSlice.lean:363 (quoted in PS-B2) supplies the sum spelling `∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z`; `IsCompact.int | -- "the zeros in K are all simple", in slice vocabulary — statable? #check (∀ K : Set ℂ, IsCompact K →   (∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi Set.univ z)     = ((K ∩ riemannXi ⁻¹' {0}).ncard : ℤ) : Prop)    -- [C0] — *The single most likely next idea over this surface is "multiplicity-weighted sum versus plain count", i.e. simplicity of zeros. The design's §D honesty note warns that the naive boundary story ("counting is inexpressible* |
| `PS-C2` | C | GREEN | `riemannXi_divisor_inter_support_finite` at ZeroSetSlice.lean:278 (quoted in PS-B1) is the ξ-specific true form; the module's own falsity warning is at ZeroSetSlice.lean: | -- the forbidden generalization: same shape, arbitrary function in place of ξ #check (∀ (f : ℂ → ℂ) (U K : Set ℂ), IsCompact K →   (K ∩ Function.support (MeromorphicOn.divisor f U)).Finite : Prop)    -- [C0] — *This is the one probe whose GREEN is a warning rather than a reassurance, and it is worth running for exactly that reason. The module records that this generic form is FALSE (death condition 6, ZeroSetSlice.lean:271-272)* |
| `PS-C3` | C | GREEN | `riemannXi_divisor_finsum_mem_eq_sum` at ZeroSetSlice.lean:363 (quoted in PS-B2) fixes the compact-parameterized sum spelling that this probe drops the compact from; `rie | -- the compact-free "total" sum: writable at all? #check (∑ᶠ z : ℂ, MeromorphicOn.divisor riemannXi Set.univ z)    -- [C0] — *It draws the honest line that the package's whole design rests on. `finsum` is total, so the global sum WRITES fine and denotes an integer; what it does not do is count anything, because on an infinite-support family it * |
| `PS-D1` | D | RED | `IsCompact.inter_riemannXi_zeroSet_finite` at ZeroSetSlice.lean:163 (quoted in PS-A1). Pin: `isCompact_univ`, Mathlib/Topology/Compactness/Compact.lean:787 `theorem isCom | -- EXPECTED RED: failed to synthesize `CompactSpace ℂ` #check IsCompact.inter_riemannXi_zeroSet_finite (K := (Set.univ : Set ℂ)) isCompact_univ    -- [C0] — *It converts the package's most important prose disclaimer into a mechanical fact. Everyone reading D4/D8 asks the same question — "can I just take K = everything?" — and the answer is no, for a reason that is one instanc* |
| `PS-D2` | D | RED | `countable_riemannXi_zeroSet` at ZeroSetSlice.lean:179 — quoted: `theorem countable_riemannXi_zeroSet : (riemannXi ⁻¹' {0}).Countable :=` (ledger row RH-SLICE-D5, VERIFIE | -- EXPECTED RED: failed to synthesize `Fintype ↥(riemannXi ⁻¹' {0})` #check (riemannXi ⁻¹' {0}).toFinset    -- [C0] — *D5 (countable) plus D4 (finite on every compact) is precisely the combination that tempts a reader into believing a global enumeration is now available — countable sounds like listable, and locally finite sounds like glo* |
| `PS-D3` | D | RED | The absence is the recorded design decision at ZeroSetSlice.lean:96-98 — quoted: `The ξ zero set is spelled inline as `riemannXi ⁻¹' {0}` at every use site —` / `M13's sp | -- EXPECTED RED: unknown identifier 'riemannXiZeros' #check riemannXiZeros    -- [C0] — *Unlike a fabricated-name probe, this one guards a specific, recorded, reviewed decision: the slice deliberately declined to introduce a ξ zero-set definition, and introducing one later is a statement-surface change that * |

**Where this surface supports nothing, which is a finding and not a gap:** CLASS D, growth: this surface supports no defensible growth-absence probe, and the design's existing D4 (`#check growthOrder riemannXi`, PROBE_BATTERY_DESIGN.md:336-339, "grep `growthOrder` over Mathlib/ at the pin = zero hits") is now stale REPO-WIDE — not merely at the pin. `growthOrder` is a built repo declaration: ResearchOS/Analysis/GrowthOrder.lean:117 `noncomputable def growthOrder (f : ℂ → E) : ℝ≥0∞`, inside `namespace Complex` (:77-672), promoted through PR #319. Under the probe preamble's `open Complex` the bare name would now resolve, so D4 as written is a boundary-moved GREEN. That finding belongs to the GrowthOrder surface's own inventory, not this one; I record it here only to explain why I propose no growth probe and to flag that the existing D4 row needs re-reading before any batch freezes it. Nothing in ZeroSetSlice mentions growth, and inventing a growth probe over slice vocabulary would manufacture a boundary the package never claimed.

CLASS D, counting-by-name: I decline the whole family of `#check <plausible-counting-name>` probes (`riemannXi_zeroCount`, `N_riem

### §F.3 Surface: analysis-generic shelf — 21 candidates (A:9, B:4, C:4, D:4)
Candidate count exceeds §P2's suggested cap of N ≤ 12 per batch, so if this
surface is ever authorized it decomposes into more than one batch.

| id | class | expected | uses | sketch / what it catches |
|---|---|---|---|---|
| `SH-A1` | A | GREEN | `Complex.growthOrder_polynomial` at ResearchOS/Analysis/GrowthOrder.lean:227 — quoted: `theorem growthOrder_polynomial (P : Polynomial ℂ) :` / `growthOrder (fun z : ℂ =>  | example : Complex.growthOrder (fun z : ℂ => z ^ 2 + 1) = 0 := by   have h : (fun z : ℂ => z ^ 2 + 1)       = fun z : ℂ => (Polynomial.X ^ 2 + Polynomial.C 1 : Polynomial ℂ).eval z := by     funext z; simp   rw [h]; exact Complex.growthOrder_polynomial _ — *GO-5 is stated only about the lambda `fun z => P.eval z`, never about a function anyone would actually write down. This is the only probe that tests whether the ledger's headline claim ("the order of a polynomial is 0, s* |
| `SH-A2` | A | GREEN | `Complex.iteratedDeriv_eq_zero_of_norm_le_pow` at ResearchOS/Analysis/PolyLiouville.lean:92 — quoted: `theorem Complex.iteratedDeriv_eq_zero_of_norm_le_pow {F : Type*} [N | example (c : ℂ) : iteratedDeriv 2 (fun z : ℂ => z) c = 0 :=   Complex.iteratedDeriv_eq_zero_of_norm_le_pow (C := 1) (n := 1)     differentiable_id' (fun z => by simp) (by norm_num) c — *PL-1 is the statement the module's own header calls "the statement that carries all the analysis", and its hypothesis bundle (`Differentiable` + a `C * (1 + ‖z‖) ^ n` bound + `n < k`) has never once been discharged at a * |
| `SH-A3` | A | GREEN | `InnerProductSpace.HarmonicOnNhd.harnack` at ResearchOS/Analysis/HarnackDisc.lean:204 — quoted: `theorem InnerProductSpace.HarmonicOnNhd.harnack {f : ℂ → ℝ} {c w : ℂ} {R  | example {c w : ℂ} {R k : ℝ} (hk : 0 ≤ k) (hw : w ∈ Metric.ball c R) :     (R - ‖w - c‖) / (R + ‖w - c‖) * k ≤ k :=   (InnerProductSpace.HarmonicOnNhd.harnack (f := fun _ => k)     (InnerProductSpace.harmonicOnNhd_const k) (fun _ _ => hk) hw).1 — *The probe writes the CONCLUSION out by hand and then asks HK-3 to supply it, so it is an orientation canary, not a restatement: if the two Harnack constants were ever exchanged, `.1` would deliver `(R + ‖w - c‖)/(R - ‖w * |
| `SH-A4` | A | GREEN | `poissonKernel_mem_Icc` at ResearchOS/Analysis/HarnackDisc.lean:93 — quoted: `theorem poissonKernel_mem_Icc {c w z : ℂ} {R : ℝ} (hz : z ∈ Metric.sphere c R) (hw : w ∈ Met | example {c z : ℂ} {R : ℝ} (hR : 0 < R) (hz : z ∈ Metric.sphere c R) :     poissonKernel c c z = 1 := by   have h := poissonKernel_mem_Icc hz (Metric.mem_ball_self hR)   simp only [sub_self, norm_zero, sub_zero, add_zero, div_self hR.ne',     Set.mem_Icc] at h   exact le_antisymm h.2 h.1 — *This is the only SHARPNESS check available for HK-1. At the centre the two-sided bound collapses to the single value 1, so the probe extracts a concrete, independently-known fact (`P(c, c, ·) = 1`) from a purely inequati* |
| `SH-A5` | A | **SKETCH — UNDETERMINED** | `norm_le_interp_of_norm_eq` at ResearchOS/Analysis/ThreeCircles.lean:214 — quoted: `theorem norm_le_interp_of_norm_eq {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E] | example {z : ℂ} (hz : ‖z‖ = 2) : ‖z‖ ≤ 2 := by   have key := norm_le_interp_of_norm_eq (f := fun w : ℂ => w)     (r₁ := 1) (r₂ := 2) (r₃ := 8) (M₁ := 1) (M₃ := 8)     (by norm_num) (by norm_num) (by norm_num) (by norm_num)     differentiable_id'.differentiableOn continuous_id.continuousOn     (fun w — *The identity function ATTAINS the three-circles bound at these radii, so this is the only probe on the shelf that tests TC-8 at equality rather than as slack. The radii are chosen asymmetric (1, 2, 8) precisely so that e* **[no proof body; not batch-eligible]** |
| `SH-A6` | A | GREEN | `norm_mellin_le_add_of_re_mem_Icc` at ResearchOS/Analysis/MellinBound.lean:224 — quoted: `theorem norm_mellin_le_add_of_re_mem_Icc {E : Type*} [NormedAddCommGroup E] [Nor | example {f : ℝ → ℂ} {g : ℝ → ℝ} {s : ℂ}     (hg0 : ∀ t ∈ Set.Ioi (0:ℝ), 0 ≤ g t)     (h : ∀ t ∈ Set.Ioi (0:ℝ), ‖f t‖ ≤ g t)     (hmg : MeasureTheory.AEStronglyMeasurable g (MeasureTheory.volume.restrict (Set.Ioi 0)))     (hgs : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (s.re - 1) * g t) (Set.Ioi  — *MB-4 is the only shelf statement whose bound is a SUM of two integrals rather than one, and the degenerate line `a = b = s.re` is the single point where its strength can be compared with MB-2's. The probe records, machin* |
| `SH-A7` | A | GREEN | `InnerProductSpace.HarmonicOnNhd.harnack_half` at ResearchOS/Analysis/HarnackDisc.lean:320 — quoted: `theorem InnerProductSpace.HarmonicOnNhd.harnack_half {f : ℂ → ℝ} {c  | example {c w : ℂ} {R k : ℝ} (hk : 0 ≤ k) (hR : 0 < R)     (hw : w ∈ Metric.closedBall c (R / 2)) : k / 3 ≤ k ∧ k ≤ 3 * k :=   InnerProductSpace.HarmonicOnNhd.harnack_half (f := fun _ => k)     (InnerProductSpace.harmonicOnNhd_const k) (fun _ _ => hk) hR hw — *HK-4's factor 3 is derived arithmetic (`div_le_div_iff₀` and `div_le_iff₀` on the radius ratio at `‖w - c‖ ≤ R/2`), independent of HK-3's constants, and it is the form the module header says downstream consumers take. Wr* |
| `SH-A8` | A | GREEN | `norm_mellin_le_of_re_le` at ResearchOS/Analysis/MellinBound.lean:200 — quoted: `theorem norm_mellin_le_of_re_le {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E] {f : | example {f : ℝ → ℂ} {g : ℝ → ℝ}     (hg0 : ∀ t ∈ Set.Ioi (0:ℝ), 0 ≤ g t)     (hgsupp : ∀ t ∈ Set.Ioo (0:ℝ) 1, g t = 0)     (h : ∀ t ∈ Set.Ioi (0:ℝ), ‖f t‖ ≤ g t)     (hgs : MeasureTheory.IntegrableOn       (fun t : ℝ => t ^ ((2 + Complex.I).re - 1) * g t) (Set.Ioi 0))     (hgb : MeasureTheory.Integr — *The only content beyond signature stability is the concrete `(2 + Complex.I).re ≤ 3` discharge — exactly the LOWCONF literal-cast class the existing design flags as its §A rationale (PROBE_BATTERY_DESIGN.md:168-171), and* |
| `SH-A9` | A | GREEN | `Complex.growthOrder_le_of_eventually_le` at ResearchOS/Analysis/GrowthOrder.lean:399 — quoted: `theorem growthOrder_le_of_eventually_le {f : ℂ → E} {g : ℂ → E} (h : ∀ᶠ r | example {f : ℂ → ℂ}     (h : ∀ᶠ r : ℝ in Filter.atTop,       Complex.maxModulus f r ≤ Complex.maxModulus Complex.exp r) :     Complex.growthOrder f ≤ 1 := by   have h1 := Complex.growthOrder_le_of_eventually_le h   rwa [Complex.growthOrder_exp] at h1 — *This is the ONLY route by which the shelf currently yields a finite-order conclusion about an unnamed function: GO-7 supplies monotonicity and GO-6 supplies the single calibrated comparison point. The probe checks that t* |
| `SH-B1` | B | GREEN | `sSupNormCircle` at ResearchOS/Analysis/ThreeCircles.lean:90 — quoted: `noncomputable def sSupNormCircle {E : Type*} [NormedAddCommGroup E] (f : ℂ → E) (r : ℝ) : ℝ := sSu | example {E : Type*} [NormedAddCommGroup E] (f : ℂ → E) (r : ℝ) :     sSupNormCircle f r = Complex.maxModulus f r := rfl — *THE highest-value probe on this surface. Two separately contracted, separately accepted, separately promoted packages (PR #318 and PR #319) independently define the SAME carrier under two names with character-identical b* |
| `SH-B2` | B | GREEN | `Complex.exists_polynomial_of_norm_le_pow` at ResearchOS/Analysis/PolyLiouville.lean:282 — quoted: `theorem Complex.exists_polynomial_of_norm_le_pow {f : ℂ → ℂ} {C : ℝ} { | example {f : ℂ → ℂ} {C : ℝ} {n : ℕ} (hf : Differentiable ℂ f)     (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖) ^ n) : Complex.growthOrder f = 0 := by   obtain ⟨p, _, hev⟩ := Complex.exists_polynomial_of_norm_le_pow hf hC   rw [show f = fun z : ℂ => p.eval z from funext hev]   exact Complex.growthOrder_polyn — *The single most useful composed fact the shelf can currently produce — "polynomial growth implies growth order zero" — and it exists in neither module. It tests the exact seam between the two independently promoted ℂ-sid* |
| `SH-B3` | B | GREEN | `sSupNormCircle_le_interp` at ResearchOS/Analysis/ThreeCircles.lean:339 — quoted: `theorem sSupNormCircle_le_interp {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E] { | example {f : ℂ → ℂ} {r₁ r₂ r₃ : ℝ} (h₁ : 0 < r₁) (h₁₂ : r₁ ≤ r₂) (h₂₃ : r₂ ≤ r₃)     (h₁₃ : r₁ < r₃)     (hd : DifferentiableOn ℂ f {w : ℂ \| r₁ < ‖w‖ ∧ ‖w‖ < r₃})     (hc : ContinuousOn f {w : ℂ \| r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}) :     Complex.maxModulus f r₂ ≤       Complex.maxModulus f r₁           ^ (1 -  — *SH-B1 tests the defeq at the definition; this tests it THROUGH a theorem, which is the only thing a consumer ever needs. The statement — log-convexity of the growth-order carrier — is what any future order-vs-maximum-mod* |
| `SH-B4` | B | **SKETCH — UNDETERMINED** | `InnerProductSpace.HarmonicOnNhd.harnack` at ResearchOS/Analysis/HarnackDisc.lean:204 (quoted under SH-A3). `Complex.maxModulus` at ResearchOS/Analysis/GrowthOrder.lean:8 | example {f : ℂ → ℝ} {R r : ℝ}     (hf : InnerProductSpace.HarmonicOnNhd f (Metric.closedBall (0:ℂ) R))     (h₀ : ∀ z ∈ Metric.closedBall (0:ℂ) R, 0 ≤ f z)     (hr0 : 0 ≤ r) (hrR : r < R) :     Complex.maxModulus f r ≤ (R + r) / (R - r) * f 0 := by   -- Real.sSup_le: nonneg RHS from h₀ 0 and 0 < R -  — *The only probe that connects HarnackDisc to any other shelf module. HarnackDisc is otherwise an island: its conclusions are pointwise inequalities on `f : ℂ → ℝ`, and nothing tests whether they can be aggregated against * **[no proof body; not batch-eligible]** |
| `SH-C1` | C | GREEN | `sSupNormCircle` at ResearchOS/Analysis/ThreeCircles.lean:90 (quoted under SH-B1). Context: ThreeCircles.lean:334-337 states of TC-9 that it "IS the statement 'log (sSupN | #check (∀ (f : ℂ → ℂ) (a b : ℝ),   ConvexOn ℝ (Set.Icc a b)     (fun x : ℝ => Real.log (sSupNormCircle f (Real.exp x))) : Prop) — *TC-DEFERRED-2 is a recorded deferral: the module deliberately did not state its headline as `ConvexOn`. This probe settles, for the cost of one `#check`, whether that deferral was a vocabulary gap or purely a proof-effor* |
| `SH-C2` | C | GREEN | `Complex.growthOrder_mul_le` at ResearchOS/Analysis/GrowthOrder.lean:467 — quoted: `theorem growthOrder_mul_le {f g : ℂ → ℂ} (hf : Continuous f) (hg : Continuous g) : gro | #check (∀ f g : ℂ → ℂ, Continuous f → Continuous g →   Complex.growthOrder (f * g)     = max (Complex.growthOrder f) (Complex.growthOrder g) : Prop) — *GO-8's ledger row goes out of its way to say the equality is not claimed. This probe separates the two possible reasons — unstatable versus unproved (and in fact false) — and pins the answer at 'expressible'. That matter* **[rationale corrected in review; see §F.0]** |
| `SH-C3` | C | GREEN | `Complex.maxModulus` at ResearchOS/Analysis/GrowthOrder.lean:86 and `Complex.growthOrder` at :117 (both quoted above). Header context, GrowthOrder.lean:114-116: "for nonc | #check (∀ (f : ℂ → ℂ) (p : ℝ), 0 < p →   (Complex.growthOrder f < ENNReal.ofReal p ↔     ∀ᶠ r : ℝ in Filter.atTop, Complex.maxModulus f r ≤ Real.exp (r ^ p)) : Prop) — *GO-2 is an accepted DESIGN COMMITMENT whose header explicitly declines to assert that it computes the classical order. The classical characterisation — order below `p` iff the maximum modulus is eventually below `exp (r * |
| `SH-C4` | C | GREEN | `Complex.growthOrder` at ResearchOS/Analysis/GrowthOrder.lean:117 (quoted under SH-A1); `Complex.growthOrder_exp` at :358 supplies the calibration that makes the exponent | #check (∀ f : ℂ → ℂ, Differentiable ℂ f → (∀ z : ℂ, f z ≠ 0) →   Complex.growthOrder f ≤ 1 →   ∃ a b : ℂ, ∀ z : ℂ, f z = Complex.exp (a * z + b) : Prop) — *The existing design's D4 recorded `growthOrder` as an unknown identifier at the pin (PROBE_BATTERY_DESIGN.md:336-339, "grep `growthOrder` over Mathlib/ at the pin = zero hits"). That grep is still correct about Mathlib a* |
| `SH-D1` | D | RED | Absent name. Contrast pair, both opened and quoted: `sSupNormCircle_nonneg` at ResearchOS/Analysis/ThreeCircles.lean:100 — `lemma sSupNormCircle_nonneg {E : Type*} [Norme | -- EXPECTED RED: unknown identifier 'Complex.maxModulus_nonneg'. #check Complex.maxModulus_nonneg — *Documents a real and currently invisible asymmetry: two definitionally identical carriers, one with a helper API and one with none. Every consumer of `Complex.maxModulus` — including GO-5's and GO-8's own proofs, which r* |
| `SH-D2` | D | RED | `Complex.maxModulus` at ResearchOS/Analysis/GrowthOrder.lean:86 — quoted: `noncomputable def maxModulus (f : ℂ → E) (r : ℝ) : ℝ` — domain fixed to `ℂ`. Contrast: `norm_me | -- EXPECTED RED: type mismatch — `fun x : ℝ => x` has type `ℝ → ℝ` -- but is expected to have type `ℂ → ?E`. #check Complex.maxModulus (fun x : ℝ => x) — *Makes machine-checkable the structural fact that otherwise only lives in prose: the shelf is two disjoint islands. MellinBound is stated for `f : ℝ → E` on `Set.Ioi 0`; PolyLiouville, HarnackDisc, ThreeCircles and Growth* |
| `SH-D3` | D | RED | Absent name. Present anchor: `Complex.growthType` at ResearchOS/Analysis/GrowthOrder.lean:140 — quoted: `noncomputable def growthType (f : ℂ → E) (p : ℝ) : ℝ≥0∞ := Filter | -- EXPECTED RED: unknown identifier 'Complex.growthType_polynomial'. #check Complex.growthType_polynomial — *GO-3 is a definition with exactly ONE fact attached to it (GO-9, at `exp` and `p = 1`). This red documents that the growth-TYPE theory does not exist as a theory: any consumer wanting the type of a constant, a polynomial* |
| `SH-D4` | D | RED | Absent name. Present anchor: `Complex.growthOrder_mul_le` at ResearchOS/Analysis/GrowthOrder.lean:467 — quoted: `theorem growthOrder_mul_le {f g : ℂ → ℂ} (hf : Continuous | -- EXPECTED RED: unknown identifier 'Complex.growthOrder_add_le'. #check Complex.growthOrder_add_le — *The order algebra on this shelf is multiplicative only. GO-8 covers products; there is no statement about sums, and the ledger's own framing ("the order of a product of two continuous functions is at most the max of thei* |

**Where this surface supports nothing, which is a finding and not a gap:** 1. NO CLASS B PROBE LINKS MellinBound TO ANY OTHER SHELF MODULE, and none should be invented. MellinBound is stated for `f : ℝ → E` integrated over `Set.Ioi 0` (MellinBound.lean:86, :125, :169, :200, :224); PolyLiouville, HarnackDisc, ThreeCircles and GrowthOrder are all stated for functions on `ℂ` (PolyLiouville.lean:92, HarnackDisc.lean:204, ThreeCircles.lean:90, GrowthOrder.lean:86). The only syntactic bridge would be pre-composition with `Complex.ofReal`, which nothing in the repository consumes and which would be a probe about a contrivance rather than about the seam. The honest instrument is SH-D2, which turns the type boundary itself into a machine-checkable red. The shelf is two disjoint islands and no amount of probe design changes that.

2. NO CLASS D PROBE ON THIS SURFACE CAN HONESTLY DOCUMENT "GROWTH IS INEXPRESSIBLE" ANY MORE. The existing design's D4 (PROBE_BATTERY_DESIGN.md:336-339, `#check growthOrder riemannXi`, EXPECTED RED unknown identifier, justified by "grep `growthOrder` over Mathlib/ at the pin = zero hits") is stale on the shelf side: the Mathlib grep is stil

### §F.4 Standing caveats for every entry above

- Elaboration is not truth. A Class C probe that elaborates shows the built
  vocabulary can STATE an idea; it says nothing about whether the idea is true.
- A thousand green probes prove nothing about the truth of the Riemann Hypothesis.
- A Class D red documents that the language honestly lacks a concept. It is the
  deliverable, not a failure, and not a discovery.
- A domain-neutral shelf lemma instantiated at `riemannXi` is an RH-lane claim
  wearing a disguise, not a shelf probe. `PM-C2` is the single candidate that
  places a conjecture object and a shelf declaration in one proposition; it is
  kept only as a type-level expressibility check, it creates no ownership
  relation between the RH chain and the shelf, and it is not a precedent for a
  built RH→shelf dependency.
- This section changes no barrier row, adds no ledger row, and selects no route.


---

## Locator policy for this document, added 2026-08-08

Raw `file:line` anchors into living documents are not maintained here any more,
and the reason is worth stating because it was learned the expensive way.

An adversarial review of the §F refresh reported that the queue anchor
`tasks/RIEMANN_HYPOTHESIS.md:778-779` had drifted to `:938-939`. By the time the
fix was applied it had moved AGAIN, to `:966-967`, because `RH-013` was inserted
above it in the meantime. Updating the number would have restarted the clock
rather than fixed anything.

So: anchors into `tasks/RIEMANN_HYPOTHESIS.md` and other frequently-edited
documents are cited by **section heading and rule name**, which survive edits.
Anchors into built Lean modules and into the pinned Mathlib checkout keep their
`file:line` form — those move only under a deliberate, reviewed change, and the
line number is load-bearing evidence there.

Three findings from the §F review were left unapplied when §F landed in PR #322
— the two count corrections and this locator policy. That was an under-delivery
rather than a decision, and it is recorded here instead of being closed quietly.
