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
reference): the three RH modules imported by `ResearchOS.lean:7-9` —
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/TargetBridge.lean` (P1–P5),
`.../Xi.lean` (X1–X11), `.../Conj.lean` (Z1–Z9). The M1–M17 multiplicity surface
is **accepted only** (RH-009, `tasks/RIEMANN_HYPOTHESIS.md:449`); its kernel
promotion RH-010 (`:616`) holds the queue's single ACTIVE slot (`:620-621`) and
`domains/riemann-hypothesis/drafts/RiemannMult.lean` lies outside every lake
target (`MULTIPLICITY_QUEUE_ENTRY_PROPOSAL.md:140`) — **no probe references any
M declaration**.

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
  validator, and stop condition" (`tasks/RIEMANN_HYPOTHESIS.md:778-779`), an
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
- **RH-005 is PARKED and stays parked** (`tasks/RIEMANN_HYPOTHESIS.md:743-747`).
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
  `tasks/RIEMANN_HYPOTHESIS.md:585,706`).
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

Candidate total: 32 probes, all C0–C2, no retries, no models, no numerics.
**The 32 candidates exceed the per-batch budget cap (§P2, suggested N ≤ 12)
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
   (`tasks/RIEMANN_HYPOTHESIS.md:601`) and `RH-010` (`:725`); per the S0-TRUST
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
condition." (`tasks/RIEMANN_HYPOTHESIS.md:778-779`) — and the standing
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
  territory and RH-005 is PARKED, tasks/RIEMANN_HYPOTHESIS.md:747).
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
`tasks/RIEMANN_HYPOTHESIS.md:578`: "free of enumeration, counting, growth,
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
   invariant; RH-010 pattern, `tasks/RIEMANN_HYPOTHESIS.md:662-674`). At that
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
  32 candidates cannot run as one batch and must decompose into at least three
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
  authorization in the batch header. The 32 candidates require at least three
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
  on the must-not-edit lists of RH-009 (`tasks/RIEMANN_HYPOTHESIS.md:601`) and
  RH-010 (`:725`); belongs to a dated ops-lane task or direct maintainer
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
`tasks/RIEMANN_HYPOTHESIS.md:36-43,405,449,578,585,601,616,620-621,662-674,706,725,743-747,778-779`.
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
