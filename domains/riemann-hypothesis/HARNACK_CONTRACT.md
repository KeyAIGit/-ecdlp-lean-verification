# Harnack double inequality on a disc (upstream-pool item): draft contract v1

Status: **DRAFT v1 (2026-08-07) — non-built review artifact, offered for STAGE ONE
(INDEPENDENT CONTRACT ACCEPTANCE) ONLY. NOT Lean-checked.** No declaration below
has been elaborated; no `lake build` has been run against any of it. Under the one
invariant, the Lean kernel via CI is the sole judge of every statement in this
contract, and this document carries no kernel verdict of any kind.

**Two-stage gate.** This contract follows the two-stage discipline of
`MULTIPLICITY_CONTRACT.md` (§Two-stage gate and promotion ordering) verbatim:
stage one is acceptance of the statement surface H1–H5 only and produces **no
built module, no ledger row, and no kernel verdict**; any built form is a
separate PR whose verdict is delivered by CI. A drafts-lane file (working name
`drafts/Harnack.lean`) lies outside every lake target (`lakefile.toml:2`
declares `defaultTargets = ["Ecdlp", "ResearchOS"]`), so **no green CI run on
an acceptance PR is evidence of anything about this draft.**

**Lane authority.** The RH queue (`tasks/RIEMANN_HYPOTHESIS.md`) is the
authority for this lane; per its dated decision update of 2026-08-07, `RH-002`
is COMPLETE (all three PARK dispositions confirmed, no route selected) and the
sole ACTIVE task is `RH-010` (kernel promotion of the accepted multiplicity
surface). No route execution is authorized. [Corrected from "RH-002" — Annex
A, finding A3.] This document is an
offered artifact against `UPSTREAM_POOL.md` §5 (Harnack inequality), **not** an
active task, **not** a route, and **not** authorization to work one. It closes
no barrier: no row of `MATHLIB_CAPABILITY_MAP.md` names Harnack as exit
evidence, and none is retired here. Nothing below bears on the truth of the
Riemann Hypothesis.

Working name: `drafts/Harnack.lean`. Eventual natural home is **upstream
Mathlib** (`Mathlib/Analysis/Complex/Harmonic/`, per `UPSTREAM_POOL.md` §5);
upstreaming is a separate maintainer decision, not part of this contract.
Statement surface: **H1 – H5**, comprising **exactly 5 public signatures**,
every one spelled explicitly in a `lean` block in §2. No signature is mandated
in prose only. The package contains **zero `def`s**.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0),
verified this session via
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`. Every
`file:line` locator below is from that exact tree (paths relative to the
`Mathlib/` root of the pin) and was re-read this session; none is inherited
from earlier scouting without re-verification.

---

## 0a. Grounding corrections to `UPSTREAM_POOL.md` §5 (re-verified this session)

The pool note (`UPSTREAM_POOL.md:482–549`) was re-verified line by line at the
pin. Three of its claims are **confirmed**, one is **superseded in the
package's favor**, and one new friction is recorded.

1. **CONFIRMED — the sharp kernel bounds are pinned theorems.**
   `re_herglotzRieszKernel_le` at `Analysis/Complex/Poisson.lean:101` and
   `le_re_herglotzRieszKernel` at `Poisson.lean:134`, exactly as the pool
   claims. **Shape caveat the pool does not record:** both are stated on the
   *expanded quotient* `((z - c + (w - c)) / ((z - c) - (w - c))).re`, not on
   `poissonKernel` and not on `herglotzRieszKernel` applied. The bridge is
   `poissonKernel_eq_re_herglotzRieszKernel` (`Poisson.lean:73`, a
   **function-level** equality `poissonKernel c w = Complex.re ∘
   herglotzRieszKernel c w`) plus `herglotzRieszKernel_def` (`:39`). H1 below
   packages this seam once, with the syntactic risk registered as H-1a.

2. **SUPERSEDED (cost class drops) — the Poisson representation of a harmonic
   function on a disc IS a pinned theorem.** The pool cites only the
   holomorphic version `DiffContOnCl.circleAverage_poissonKernel_smul`
   (`Analysis/Complex/Poisson.lean:245`, primed `:255` — both re-verified) and
   names the open/closed `DiffContOnCl` thickening as the hardest step. In
   fact the pin contains a **second** Poisson file,
   `Analysis/Complex/Harmonic/Poisson.lean`, with

   - `InnerProductSpace.HarmonicOnNhd.circleAverage_poissonKernel_smul`
     (`Harmonic/Poisson.lean:91`): for `f : ℂ → ℝ`,
     `HarmonicOnNhd f (closedBall c R)` and `w ∈ ball c R`,
     `Real.circleAverage (poissonKernel c w • f) c R = f w`;
   - the `HarmonicContOnCl` variant at `:102`.

   The thickening step, `exists_analyticOnNhd_ball_re_eq`
   (`Harmonic/Analytic.lean:70`), `reCLM.circleAverage_comp_comm`, and all
   `CircleIntegrable` side conditions of the representation are discharged
   **inside** that pinned proof (`Harmonic/Poisson.lean:44–67`). **The
   representation is therefore a pinned prerequisite, not an obligation of
   this contract**, and the pool's "hardest step" no longer exists. What
   remains unwritten at the pin is exactly the integration/comparison step:
   Harnack itself (`grep -ri harnack Mathlib/` at the pin: **zero hits**,
   re-run this session).

3. **CONFIRMED, WITH ONE CORRECTION — namespace.** `HarmonicOnNhd` is
   `InnerProductSpace.HarmonicOnNhd`
   (`Analysis/InnerProductSpace/Harmonic/Basic.lean:27` opens the namespace,
   defs at `:39`/`:46`), so the main theorem's full name is
   `InnerProductSpace.HarmonicOnNhd.harnack`; dot notation
   `hf.circleAverage_poissonKernel_smul` resolves because the pinned
   representation lives in the same namespace (`Harmonic/Poisson.lean:28`).
   **Correction (Annex A, finding A2):** the mean-value lemma is the
   exception. `Harmonic/MeanValue.lean` contains **no** `namespace` command
   (only `open InnerProductSpace Metric Real` at `:18`), so its declarations
   are **root-level**: the full name is
   `_root_.HarmonicOnNhd.circleAverage_eq`, not
   `InnerProductSpace.HarmonicOnNhd.circleAverage_eq`. Cross-evidence at the
   pin: `Analysis/Complex/JensenFormula.lean:268` and
   `Analysis/SpecialFunctions/Integrals/PosLogEqCircleAverage.lean:58/:162`
   reference it by the bare name without opening `InnerProductSpace`, and no
   `export` exists in any harmonic file. Consequence: call it by its bare
   name (the H3 skeleton already does); dot notation `hf.circleAverage_eq`
   on an `InnerProductSpace.HarmonicOnNhd` hypothesis will **not** resolve.
   The same applies to `HarmonicContOnCl.circleAverage_eq`
   (`MeanValue.lean:50`, DEFERRED-H1).

4. **NEW FRICTION — the in-tree kernel-continuity lemma is `private`.**
   `continuousOn_herglotz_riesz` (`Harmonic/Poisson.lean:30–35`) is exactly
   the continuity fact the `CircleIntegrable` side conditions need, and it is
   `private lemma`: it cannot be cited. H2 below re-proves the (easier)
   `poissonKernel` form; the private proof's pattern (nonvanishing `have` +
   `fun_prop`) is copyable. Registered as H-2a, the largest single obligation
   of the package.

5. **SIGNATURE DELTA vs the pool's proposal.** The pool signature
   (`UPSTREAM_POOL.md:490–497`) carries `hR : 0 < R`. That hypothesis is
   redundant: `w ∈ ball c R` already forces `0 < R`
   (`Metric.pos_of_mem_ball`, `Topology/MetricSpace/Pseudo/Defs.lean:376`,
   used for exactly this purpose in the pinned proof at
   `Harmonic/Poisson.lean:46`). H3 drops it. The corollary H4 quantifies over
   a closed ball, where the argument does need `0 < R` explicitly, so H4
   keeps it.

---

## 0b. Exact pinned interface (quoted from the tree at the pin)

```lean
-- Analysis/Complex/Poisson.lean:54 (def), :57 (pointwise), :73 (function-level bridge)
noncomputable def poissonKernel (c w z : ℂ) : ℝ :=
  (‖z - c‖ ^ 2 - ‖w - c‖ ^ 2) / ‖(z - c) - (w - c)‖ ^ 2
lemma poissonKernel_def (c w z : ℂ) :
    poissonKernel c w z = (‖z - c‖ ^ 2 - ‖w - c‖ ^ 2) / ‖(z - c) - (w - c)‖ ^ 2
lemma poissonKernel_eq_re_herglotzRieszKernel {c w : ℂ} :
    poissonKernel c w = Complex.re ∘ herglotzRieszKernel c w

-- Analysis/Complex/Poisson.lean:101, :134 — THE two analytic inputs.
-- Both stated on the EXPANDED quotient; R is the section variable of :24.
theorem re_herglotzRieszKernel_le {c z : ℂ} (hz : z ∈ sphere c R) (hw : w ∈ ball c R) :
    ((z - c + (w - c)) / ((z - c) - (w - c))).re ≤ (R + ‖w - c‖) / (R - ‖w - c‖)
theorem le_re_herglotzRieszKernel {c z : ℂ} (hz : z ∈ sphere c R) (hw : w ∈ ball c R) :
    (R - ‖w - c‖) / (R + ‖w - c‖) ≤ ((z - c + (w - c)) / ((z - c) - (w - c))).re

-- Analysis/Complex/Harmonic/Poisson.lean:91 — THE representation input, PINNED.
-- Inside `namespace InnerProductSpace` (:28); f : ℂ → ℝ, from the variable block :26.
theorem HarmonicOnNhd.circleAverage_poissonKernel_smul
    (hf : HarmonicOnNhd f (closedBall c R)) (hw : w ∈ ball c R) :
    Real.circleAverage (poissonKernel c w • f) c R = f w
-- (HarmonicContOnCl variant at :102 — deferred, see DEFERRED-H1.)

-- Analysis/Complex/Harmonic/MeanValue.lean:27 — mean value at the center. NOTE the |R|.
-- ROOT-LEVEL name (`_root_.HarmonicOnNhd.circleAverage_eq` — the file has `open
-- InnerProductSpace` at :18 and no `namespace` command; Annex A2). Bare-name calls only.
theorem HarmonicOnNhd.circleAverage_eq (hf : HarmonicOnNhd f (closedBall c |R|)) :
    circleAverage f c R = f c

-- Analysis/InnerProductSpace/Harmonic/Basic.lean:39, :46, :51 (ns InnerProductSpace, :27)
def HarmonicAt := (ContDiffAt ℝ 2 f x) ∧ (Δ f =ᶠ[𝓝 x] 0)
def HarmonicOnNhd := ∀ x ∈ s, HarmonicAt f x
lemma HarmonicOnNhd.contDiffOn (hf : HarmonicOnNhd f s) : ContDiffOn ℝ 2 f s

-- MeasureTheory/Integral/CircleAverage.lean — `namespace Real` spans :42–:382.
noncomputable def circleAverage : E := (2 * π)⁻¹ • ∫ θ in 0..2 * π, f (circleMap c R θ)  -- :54
@[gcongr]
theorem circleAverage_mono {c : ℂ} {R : ℝ} {f₁ f₂ : ℂ → ℝ} (hf₁ : CircleIntegrable f₁ c R)
    (hf₂ : CircleIntegrable f₂ c R) (h : ∀ x ∈ Metric.sphere c |R|, f₁ x ≤ f₂ x) :
    circleAverage f₁ c R ≤ circleAverage f₂ c R                                          -- :271
theorem circleAverage_smul : circleAverage (a • f) c R = a • circleAverage f c R          -- :331
-- (:331's 𝕜 needs [NormedDivisionRing 𝕜] [Module 𝕜 E] [NormSMulClass 𝕜 E]
--  [SMulCommClass ℝ 𝕜 E], variable block :36–:40 — all satisfied at 𝕜 = E = ℝ.)

-- MeasureTheory/Integral/CircleIntegral.lean
def CircleIntegrable (f : ℂ → E) (c : ℂ) (R : ℝ) : Prop := …                              -- :176
theorem const_smul {f : ℂ → A} (h : CircleIntegrable f c R) :
    CircleIntegrable (a • f) c R                    -- :233, namespace CircleIntegrable
@[to_fun] theorem smul_of_continuousOn {f : ℂ → F} {g : ℂ → 𝕜} (hf : CircleIntegrable f c R)
    (hg : ContinuousOn g (sphere c |R|)) : CircleIntegrable (g • f) c R                   -- :247
theorem ContinuousOn.circleIntegrable {f : ℂ → E} {c : ℂ} {R : ℝ} (hR : 0 ≤ R)
    (hf : ContinuousOn f (sphere c R)) : CircleIntegrable f c R                           -- :337

-- Metric / norm / order glue
theorem pos_of_mem_ball (hy : y ∈ ball x ε) : 0 < ε        -- Topology/MetricSpace/Pseudo/Defs.lean:376
theorem sphere_subset_closedBall : sphere x ε ⊆ closedBall x ε                 -- Pseudo/Defs.lean:480
theorem mem_closedBall_self (h : 0 ≤ ε) : x ∈ closedBall x ε                   -- Pseudo/Defs.lean:460
-- mem_ball_iff_norm / mem_closedBall_iff_norm: @[to_additive] twins of
-- mem_ball_iff_norm'' / mem_closedBall_iff_norm'' — Analysis/Normed/Group/Basic.lean:869/:877
-- (attribute lines :868/:876; earlier locators :868/:875 corrected, Annex A5)
-- abs_of_pos: @[to_additive] twin of mabs_of_one_lt — Algebra/Order/Group/Unbundled/Abs.lean:93
theorem ContDiffOn.continuousOn (h : ContDiffOn 𝕜 n f s) : ContinuousOn f s
                                                    -- Analysis/Calculus/ContDiff/Defs.lean:551
lemma div_le_div_iff₀ (hb : 0 < b) (hd : 0 < d) : a / b ≤ c / d ↔ a * d ≤ c * b
                                                    -- Algebra/Order/GroupWithZero/Basic.lean:1430
```

Name-collision scan (grep over the pinned tree this session): **zero hits** for
all five proposed names — `poissonKernel_mem_Icc`, `continuousOn_poissonKernel`,
`InnerProductSpace.HarmonicOnNhd.harnack`, `…harnack_half`,
`…pos_of_pos_center` — and zero hits for `harnack` in any casing anywhere in
`Mathlib/`.

Proposed draft preamble (name-resolution review only; a drafts-lane file, so
plain `import`, not the pin's `module`/`public import` idiom):

```lean
import Mathlib.Analysis.Complex.Harmonic.Poisson
-- transitively supplies Harmonic/MeanValue, Complex/Poisson, CircleAverage,
-- CircleIntegral, and the InnerProductSpace harmonic API (Harmonic/Poisson.lean:8–9)

open Complex InnerProductSpace Metric Real
```

Notation below: `r` abbreviates `‖w - c‖` in prose only; every `lean` block
spells `‖w - c‖` in full. No new definition is introduced anywhere.

---

## 1. Statement list H1 – H5

Legend: `[PIN]` provable from pinned Mathlib alone (this whole package is
`[PIN]` — it consumes no repo theorem and no merged-package prerequisite);
`[GEN]` generic, natural Mathlib upstream.

---

### Block A — kernel glue (pinned bounds re-expressed on `poissonKernel`)

## H1. Two-sided kernel bound on the sphere `[GEN]` `[PIN]`

### Statement

```lean
theorem poissonKernel_mem_Icc {c w z : ℂ} {R : ℝ}
    (hz : z ∈ Metric.sphere c R) (hw : w ∈ Metric.ball c R) :
    poissonKernel c w z ∈
      Set.Icc ((R - ‖w - c‖) / (R + ‖w - c‖)) ((R + ‖w - c‖) / (R - ‖w - c‖))
```

### Proof skeleton

```lean
  have hkey : poissonKernel c w z = ((z - c + (w - c)) / ((z - c) - (w - c))).re := by
    simp only [poissonKernel_eq_re_herglotzRieszKernel, Function.comp_apply,
      herglotzRieszKernel_def]                       -- Poisson.lean:73, :39
  exact ⟨hkey ▸ le_re_herglotzRieszKernel hz hw,     -- Poisson.lean:134
         hkey ▸ re_herglotzRieszKernel_le hz hw⟩     -- Poisson.lean:101
```

### Pinned dependencies (H1)

`poissonKernel_eq_re_herglotzRieszKernel` — `Analysis/Complex/Poisson.lean:73`
(function-level, so `simp only` must rewrite the head `poissonKernel c w`
under application; `rw` also works since the subterm occurs applied);
`herglotzRieszKernel_def` — `Poisson.lean:39`;
`re_herglotzRieszKernel_le` / `le_re_herglotzRieszKernel` —
`Poisson.lean:101/:134`, verified verbatim this session including the
expanded-quotient shape and the hypothesis order `(hz) (hw)`. The private aux
`poissonKernel_eq_re_herglotzRieszKernel_aux` (`Poisson.lean:60`) is **not**
usable and is not used.

### Obligations (H1)

- **H-1a** (LOW): the syntactic seam. `simp only` must beta/`comp_apply`-reduce
  `(Complex.re ∘ herglotzRieszKernel c w) z` and unfold to *exactly* the
  quotient the two bound theorems are stated on (`z - c + (w - c)` — note the
  pinned statements' parenthesization). Fallback: prove `hkey` by
  `rw [poissonKernel_def]`-side computation is **not** available without the
  private aux; instead use
  `have := congrFun (poissonKernel_eq_re_herglotzRieszKernel (c := c) (w := w)) z`
  then `simpa [herglotzRieszKernel_def] using this`. Second fallback: replace
  `hkey ▸` with `constructor <;> rw [hkey]` to keep the rewrite direction
  explicit.

---

## H2. Continuity of the Poisson kernel on the sphere `[GEN]` `[PIN]`

### Statement

```lean
theorem continuousOn_poissonKernel {c w : ℂ} {R : ℝ} (hw : w ∈ Metric.ball c R) :
    ContinuousOn (poissonKernel c w) (Metric.sphere c R)
```

### Proof skeleton

```lean
  have hne : ∀ z ∈ Metric.sphere c R, (z - c) - (w - c) ≠ 0 := by
    intro z hz h
    rw [sub_eq_zero] at h
    have h₁ : ‖w - c‖ < R := mem_ball_iff_norm.1 hw
    have h₂ : ‖z - c‖ = R := mem_sphere_iff_norm.1 hz
    rw [h] at h₂
    linarith
  unfold poissonKernel
  fun_prop (disch := aesop)
  -- side goal shape: ∀ z ∈ sphere c R, ‖(z - c) - (w - c)‖ ^ 2 ≠ 0,
  -- discharged from hne via norm_ne_zero_iff and pow_ne_zero
```

### Pinned dependencies (H2)

`poissonKernel` — `Poisson.lean:54` (a plain quotient of continuous real
expressions); `mem_ball_iff_norm` / `mem_sphere_iff_norm` —
`Analysis/Normed/Group/Basic.lean` `to_additive` layer (both used in-tree in
exactly this position at `Harmonic/Poisson.lean:65` and `Poisson.lean:108`).
In-tree precedent for the proof *pattern* (nonvanishing `have` + `fun_prop`):
the `private` lemma `continuousOn_herglotz_riesz`, `Harmonic/Poisson.lean:30–35`.

### Obligations (H2)

- **H-2a** (MEDIUM) — **the largest obligation of the package.** The in-tree
  analogue is `private` and cannot be cited, so this continuity fact must be
  re-proved, and `fun_prop (disch := …)` discharge of the denominator side
  condition is the step most likely to need hand-holding. Note (Annex A6): the
  in-tree private proof (`Harmonic/Poisson.lean:33–35`) uses a **plain**
  `fun_prop` with the nonvanishing fact as an anonymous `have` in the local
  context (no `disch` argument) — try that shape first. Fallback (fully
  explicit): `ContinuousOn.div` with numerator
  `((continuous_norm.comp (continuous_id.sub continuous_const)).pow 2
  |>.sub continuous_const).continuousOn`, denominator likewise, and
  nonvanishing `fun z hz => pow_ne_zero 2 (norm_ne_zero_iff.mpr (hne z hz))`.
  Second fallback: prove continuity on the larger set
  `{z | ‖z - c‖ ∈ Set.Ioc ‖w - c‖ R}` mimicking `Harmonic/Poisson.lean:30–35`
  verbatim and `.mono` down to the sphere. If all three routes fail, death
  condition 3 applies.

---

### Block B — the deliverable

## H3. Harnack double inequality on a disc, explicit constants `[GEN]` `[PIN]`

### Statement

```lean
theorem InnerProductSpace.HarmonicOnNhd.harnack {f : ℂ → ℝ} {c w : ℂ} {R : ℝ}
    (hf : HarmonicOnNhd f (Metric.closedBall c R))
    (h₀ : ∀ z ∈ Metric.closedBall c R, 0 ≤ f z)
    (hw : w ∈ Metric.ball c R) :
    (R - ‖w - c‖) / (R + ‖w - c‖) * f c ≤ f w ∧
      f w ≤ (R + ‖w - c‖) / (R - ‖w - c‖) * f c
```

(Delta vs `UPSTREAM_POOL.md:490–497`: `hR : 0 < R` dropped as redundant —
§0a item 5. The constants are the sharp classical ones; sharpness itself is
**not** claimed as a statement.)

### Proof skeleton

```lean
  have hR : 0 < R := Metric.pos_of_mem_ball hw               -- Pseudo/Defs.lean:376
  have habs : |R| = R := abs_of_pos hR
  -- pinned representation (the load-bearing input):
  have hrep : Real.circleAverage (poissonKernel c w • f) c R = f w :=
    hf.circleAverage_poissonKernel_smul hw                   -- Harmonic/Poisson.lean:91
  -- pinned mean value at the center (|R| plumbing):
  have hmean : Real.circleAverage f c R = f c :=
    HarmonicOnNhd.circleAverage_eq (by rwa [habs])           -- MeanValue.lean:27
  -- integrability:
  have hfc : ContinuousOn f (Metric.sphere c R) :=
    hf.contDiffOn.continuousOn.mono Metric.sphere_subset_closedBall
      -- Basic.lean:51; ContDiff/Defs.lean:551; Pseudo/Defs.lean:480
  have hintf : CircleIntegrable f c R := hfc.circleIntegrable hR.le
      -- CircleIntegral.lean:337
  have hint : CircleIntegrable (poissonKernel c w • f) c R :=
    hintf.smul_of_continuousOn (habs ▸ continuousOn_poissonKernel hw)   -- :247, H2
  -- pointwise comparison on the sphere (H1 × nonnegativity):
  have hlow : ∀ z ∈ Metric.sphere c |R|,
      ((R - ‖w - c‖) / (R + ‖w - c‖) • f) z ≤ (poissonKernel c w • f) z := by
    intro z hz
    rw [habs] at hz
    simpa only [Pi.smul_apply', Pi.smul_apply, smul_eq_mul] using
      mul_le_mul_of_nonneg_right (poissonKernel_mem_Icc hz hw).1
        (h₀ z (Metric.sphere_subset_closedBall hz))
  have hhigh : ∀ z ∈ Metric.sphere c |R|,
      (poissonKernel c w • f) z ≤ ((R + ‖w - c‖) / (R - ‖w - c‖) • f) z := by
    intro z hz
    rw [habs] at hz
    simpa only [Pi.smul_apply', Pi.smul_apply, smul_eq_mul] using
      mul_le_mul_of_nonneg_right (poissonKernel_mem_Icc hz hw).2
        (h₀ z (Metric.sphere_subset_closedBall hz))
  refine ⟨?_, ?_⟩
  · calc (R - ‖w - c‖) / (R + ‖w - c‖) * f c
        = Real.circleAverage ((R - ‖w - c‖) / (R + ‖w - c‖) • f) c R := by
          rw [Real.circleAverage_smul, hmean, smul_eq_mul]   -- CircleAverage.lean:331
      _ ≤ Real.circleAverage (poissonKernel c w • f) c R :=
          Real.circleAverage_mono hintf.const_smul hint hlow -- :271, CircleIntegral.lean:233
      _ = f w := hrep
  · calc f w
        = Real.circleAverage (poissonKernel c w • f) c R := hrep.symm
      _ ≤ Real.circleAverage ((R + ‖w - c‖) / (R - ‖w - c‖) • f) c R :=
          Real.circleAverage_mono hint hintf.const_smul hhigh
      _ = (R + ‖w - c‖) / (R - ‖w - c‖) * f c := by
          rw [Real.circleAverage_smul, hmean, smul_eq_mul]
```

### Pinned dependencies (H3)

H1, H2;
`InnerProductSpace.HarmonicOnNhd.circleAverage_poissonKernel_smul` —
`Harmonic/Poisson.lean:91` (verified verbatim this session, including the
`closedBall c R` hypothesis — **not** `|R|` — and the Pi-smul statement shape);
`HarmonicOnNhd.circleAverage_eq` — **root-level**, `MeanValue.lean:27`
(verified verbatim: hypothesis on `closedBall c |R|`; the file has `open
InnerProductSpace` only, no `namespace` command — Annex A2 — so the skeleton's
bare-name call is the correct spelling and dot notation must not be used);
`InnerProductSpace.HarmonicOnNhd.contDiffOn` — `Harmonic/Basic.lean:51`;
`ContDiffOn.continuousOn` — `ContDiff/Defs.lean:551`;
`ContinuousOn.circleIntegrable` — `CircleIntegral.lean:337`;
`CircleIntegrable.smul_of_continuousOn` — `CircleIntegral.lean:247` (its `g`
argument wants `sphere c |R|`, hence the `habs ▸`);
`CircleIntegrable.const_smul` — `CircleIntegral.lean:233` (`A := ℝ`);
`Real.circleAverage_mono` — `CircleAverage.lean:271` (pointwise hypothesis on
`sphere c |R|`; **both** integrability arguments are mandatory);
`Real.circleAverage_smul` — `CircleAverage.lean:331` (`𝕜 := ℝ`, instances per
§0b); `Metric.pos_of_mem_ball` / `Metric.sphere_subset_closedBall` —
`Pseudo/Defs.lean:376/:480`; `abs_of_pos` — to_additive twin of
`mabs_of_one_lt`, `Algebra/Order/Group/Unbundled/Abs.lean:93`;
`mul_le_mul_of_nonneg_right` — core order library.

### Obligations (H3)

- **H-3a** (MEDIUM): the Pi-smul unfoldings. `poissonKernel c w • f` is a
  function-on-function smul (`Pi.smul_apply'` shape:
  `(g • f) z = g z • f z`), while `((R - ‖w - c‖)/(R + ‖w - c‖)) • f` is a
  scalar-on-function smul (`Pi.smul_apply` shape); both must land on `_ * f z`
  via `smul_eq_mul` before `mul_le_mul_of_nonneg_right` applies. The `simpa
  only [Pi.smul_apply', Pi.smul_apply, smul_eq_mul]` closers carry this; if
  either simp set misses, fall back to `show poissonKernel c w z * f z ≤ _`
  (defeq) and close with `exact`. This is bookkeeping, but it appears four
  times and is the most likely CI-cycle burner.
- **H-3b** (LOW): the `|R|` plumbing — three distinct spots (`hmean`'s
  hypothesis, `smul_of_continuousOn`'s sphere, `circleAverage_mono`'s
  pointwise hypothesis) each need `habs` in a different direction. All are
  one-line `rwa`/`▸` fixes; listed so a failure is recognized as plumbing,
  not mathematics.
- **H-3c** (LOW): `Real.circleAverage_smul` instance search at `𝕜 = E = ℝ`
  (`NormedDivisionRing ℝ`, `Module ℝ ℝ`, `NormSMulClass ℝ ℝ`,
  `SMulCommClass ℝ ℝ ℝ` — all pinned instances). Fallback:
  `Real.circleAverage_fun_smul` (`CircleAverage.lean:339`) with a `funext`
  reshape.
- **H-3d** (LOW): `hintf.const_smul` must elaborate with `A := ℝ`, `a :=` the
  quotient; `CircleIntegrable.const_fun_smul` (`CircleIntegral.lean:237`) is
  the lambda-form fallback.

---

### Block C — corollaries (the forms consumed downstream)

## H4. Harnack at the center: factor 3 on the half-radius ball `[GEN]` `[PIN]`

### Statement

```lean
theorem InnerProductSpace.HarmonicOnNhd.harnack_half {f : ℂ → ℝ} {c w : ℂ} {R : ℝ}
    (hf : HarmonicOnNhd f (Metric.closedBall c R))
    (h₀ : ∀ z ∈ Metric.closedBall c R, 0 ≤ f z)
    (hR : 0 < R) (hw : w ∈ Metric.closedBall c (R / 2)) :
    f c / 3 ≤ f w ∧ f w ≤ 3 * f c
```

(`hR` is genuinely needed here: a closed ball is nonempty at radius `0`, so
membership does not force `0 < R` the way H3's open-ball hypothesis does.)

### Proof skeleton

```lean
  have hr : ‖w - c‖ ≤ R / 2 := mem_closedBall_iff_norm.1 hw
  have hw' : w ∈ Metric.ball c R := mem_ball_iff_norm.2 (by linarith)
  obtain ⟨h₁, h₂⟩ := hf.harnack h₀ hw'                       -- H3
  have hc : 0 ≤ f c := h₀ c (Metric.mem_closedBall_self hR.le)  -- Pseudo/Defs.lean:460
  have hd₁ : 0 < R + ‖w - c‖ := by positivity
  have hd₂ : 0 < R - ‖w - c‖ := by linarith [norm_nonneg (w - c)]
  constructor
  · calc f c / 3 = 1 / 3 * f c := by ring
      _ ≤ (R - ‖w - c‖) / (R + ‖w - c‖) * f c := by
          gcongr ?_ * f c
          rw [div_le_div_iff₀ (by norm_num) hd₁]             -- GroupWithZero/Basic.lean:1430
          linarith    -- 1 * (R + r) ≤ (R − r) * 3  ⟺  4r ≤ 2R  ⟸  r ≤ R/2
      _ ≤ f w := h₁
  · calc f w ≤ (R + ‖w - c‖) / (R - ‖w - c‖) * f c := h₂
      _ ≤ 3 * f c := by
          gcongr ?_ * f c
          rw [div_le_iff₀ hd₂]
          linarith    -- R + r ≤ 3 * (R − r)  ⟺  4r ≤ 2R
```

### Pinned dependencies (H4)

H3; `mem_closedBall_iff_norm` / `mem_ball_iff_norm` — to_additive twins,
`Analysis/Normed/Group/Basic.lean:875/:868`; `Metric.mem_closedBall_self` —
`Pseudo/Defs.lean:460`; `div_le_div_iff₀` —
`Algebra/Order/GroupWithZero/Basic.lean:1430` (the `₀`-suffixed name is the
pinned spelling, used in-tree at `Poisson.lean:87/:118`).

### Obligations (H4)

- **H-4a** (LOW): division bookkeeping. If `gcongr` does not produce the bare
  fraction-comparison side goal, fall back to
  `mul_le_mul_of_nonneg_right _ hc` with the fraction inequality proved
  standalone. `div_le_iff₀` **is** the pinned name for the one-sided form
  (`Algebra/Order/GroupWithZero/Basic.lean:1138`, re-verified — Annex A7), so
  the previously recorded `3 = 3 / 1` contingency is retired; it remains
  available (`div_le_div_iff₀ hd₂ (by norm_num : (0:ℝ) < 1)`) should the
  elaborated form differ.

---

## H5. Positivity propagation from the center `[GEN]` `[PIN]`

### Statement

```lean
theorem InnerProductSpace.HarmonicOnNhd.pos_of_pos_center {f : ℂ → ℝ} {c w : ℂ} {R : ℝ}
    (hf : HarmonicOnNhd f (Metric.closedBall c R))
    (h₀ : ∀ z ∈ Metric.closedBall c R, 0 ≤ f z)
    (hc : 0 < f c) (hw : w ∈ Metric.ball c R) :
    0 < f w
```

### Proof skeleton

```lean
  have hR : 0 < R := Metric.pos_of_mem_ball hw
  have hrR : ‖w - c‖ < R := mem_ball_iff_norm.1 hw
  have hpos : 0 < (R - ‖w - c‖) / (R + ‖w - c‖) :=
    div_pos (by linarith) (by positivity)
  exact lt_of_lt_of_le (mul_pos hpos hc) (hf.harnack h₀ hw).1   -- H3, lower half
```

### Pinned dependencies (H5)

H3; `div_pos`, `mul_pos`, `lt_of_lt_of_le` — core order library;
`Metric.pos_of_mem_ball` — `Pseudo/Defs.lean:376`.

### Obligations (H5)

- **H-5a** (LOW): none beyond H3; the only risk is `positivity` on
  `R + ‖w - c‖` needing `hR` in scope (it does not — `norm_nonneg` plus `hR`
  via `linarith` is the fallback).

---

## Pinned API dependencies table

| Symbol | Locator (pin `fabf563a…`) | Consumed by |
|---|---|---|
| `poissonKernel` (def) | `Analysis/Complex/Poisson.lean:54` | H1, H2, H3 |
| `poissonKernel_eq_re_herglotzRieszKernel` | `Poisson.lean:73` | H1 |
| `herglotzRieszKernel_def` | `Poisson.lean:39` | H1 |
| `re_herglotzRieszKernel_le` | `Poisson.lean:101` | H1 |
| `le_re_herglotzRieszKernel` | `Poisson.lean:134` | H1 |
| `InnerProductSpace.HarmonicOnNhd.circleAverage_poissonKernel_smul` | `Analysis/Complex/Harmonic/Poisson.lean:91` | H3 |
| `HarmonicOnNhd.circleAverage_eq` (**root-level**, not in ns `InnerProductSpace` — Annex A2) | `Analysis/Complex/Harmonic/MeanValue.lean:27` | H3 |
| `InnerProductSpace.HarmonicOnNhd` / `.contDiffOn` | `Analysis/InnerProductSpace/Harmonic/Basic.lean:46/:51` (ns `:27`) | H3–H5 |
| `Real.circleAverage` (def) | `MeasureTheory/Integral/CircleAverage.lean:54` (ns `Real` `:42–:382`) | H3 |
| `Real.circleAverage_mono` | `CircleAverage.lean:271` | H3 |
| `Real.circleAverage_smul` / `_fun_smul` | `CircleAverage.lean:331/:339` | H3 |
| `CircleIntegrable` (def) | `MeasureTheory/Integral/CircleIntegral.lean:176` | H3 |
| `CircleIntegrable.const_smul` / `.const_fun_smul` | `CircleIntegral.lean:233/:237` | H3 |
| `CircleIntegrable.smul_of_continuousOn` | `CircleIntegral.lean:247` | H3 |
| `ContinuousOn.circleIntegrable` / `'` | `CircleIntegral.lean:337/:333` | H3 |
| `ContDiffOn.continuousOn` | `Analysis/Calculus/ContDiff/Defs.lean:551` | H3 |
| `Metric.pos_of_mem_ball` | `Topology/MetricSpace/Pseudo/Defs.lean:376` | H3, H5 |
| `Metric.sphere_subset_closedBall` | `Pseudo/Defs.lean:480` | H3 |
| `Metric.mem_closedBall_self` | `Pseudo/Defs.lean:460` | H4 |
| `mem_ball_iff_norm` (to_additive of `mem_ball_iff_norm''`) | `Analysis/Normed/Group/Basic.lean:869` (attr `:868`) | H2–H5 |
| `mem_closedBall_iff_norm` (to_additive of `…''`) | `Normed/Group/Basic.lean:877` (attr `:876`) | H4 |
| `abs_of_pos` (to_additive of `mabs_of_one_lt`) | `Algebra/Order/Group/Unbundled/Abs.lean:93` | H3 |
| `div_le_div_iff₀` | `Algebra/Order/GroupWithZero/Basic.lean:1430` | H4 |

Explicitly **not** consumed (interior to pinned proofs, or private):
`DiffContOnCl.circleAverage_poissonKernel_smul` (`Poisson.lean:245/:255`),
`InnerProductSpace.HarmonicOnNhd.exists_analyticOnNhd_ball_re_eq`
(`Harmonic/Analytic.lean:70`), `ContinuousLinearMap.circleAverage_comp_comm`
(`CircleAverage.lean:318`), and the `private` `continuousOn_herglotz_riesz`
(`Harmonic/Poisson.lean:30`).

## Obligation register

| ID | Severity | One-line content | Fallbacks recorded |
|---|---|---|---|
| H-1a | LOW | expanded-quotient syntactic seam in H1 | 2 |
| H-2a | **MEDIUM** | kernel continuity must be re-proved (in-tree analogue is `private`); `fun_prop` discharge | 3, then death condition 3 |
| H-3a | **MEDIUM** | Pi-smul unfoldings (`Pi.smul_apply'` vs `Pi.smul_apply` + `smul_eq_mul`), ×4 sites | defeq `show`/`exact` |
| H-3b | LOW | `|R|` plumbing at three sites | `rwa`/`▸` |
| H-3c | LOW | `circleAverage_smul` instances at `𝕜 = ℝ` | `_fun_smul` |
| H-3d | LOW | `const_smul` elaboration | `const_fun_smul` |
| H-4a | LOW | fraction bookkeeping / `gcongr` shape | explicit `mul_le_mul_of_nonneg_right` |
| H-5a | LOW | `positivity` scope | `linarith` |

### Deferred items (explicitly out of this package)

- **DEFERRED-H1**: the `HarmonicContOnCl` variant of H3 (representation pinned
  at `Harmonic/Poisson.lean:102`, mean value at `MeanValue.lean:50`; continuity
  on the sphere would come from the structure's own continuity field rather
  than `contDiffOn`). Cheap, but a second surface; not stated here.
- **DEFERRED-H2**: the Harnack-chain corollary (`f w₁ ≤ K * f w₂` uniformly on
  a compact subset of a domain), named by the pool as the form usually consumed
  downstream. It needs a covering argument and constants depending on the
  compact set; different cost class, not stated here.
- **DEFERRED-H3**: vanishing propagation (`f c = 0 → Set.EqOn f 0 (ball c R)`),
  a two-line consequence of H3's upper half plus `h₀`; omitted to keep the
  surface at five signatures.

## Claim boundary

- **What this contract is.** A statement design for the Harnack double
  inequality on a disc with explicit sharp constants, plus its kernel glue and
  two corollaries — a candidate for `UPSTREAM_POOL.md` §5. Every prerequisite
  of every statement H1–H5 is **pinned Mathlib**; the package consumes no repo
  theorem, no merged-package prerequisite, and no unmerged PR. **In
  particular, the Poisson representation of a harmonic function on a disc is
  a pinned theorem** (`Harmonic/Poisson.lean:91`), verified this session —
  the earlier pool note's residual worry (open/closed thickening) is interior
  to that pinned proof and is not an obligation here. This is the honest
  correction §0a item 2 records, and it moves the item's cost class down: the
  unwritten content is comparison bookkeeping (H3) plus one re-proved
  continuity lemma (H2), not analysis.
- **What this contract is not.** It is unbuilt: it carries no kernel verdict,
  closes no `MATHLIB_CAPABILITY_MAP.md` row (no row names Harnack as exit
  evidence, and generic pinned machinery never retires a row regardless —
  MULTIPLICITY_CONTRACT.md death condition 9 is adopted here as death
  condition 6), selects no route, and is not authorization to work one. The
  RH queue's sole ACTIVE task is `RH-010` (per the queue's 2026-08-07
  decision update; corrected from `RH-002` — Annex A3), and this contract
  does not occupy it.
- **No RH content.** ζ, ξ, and their zeros appear nowhere in H1–H5. Harnack
  inequalities feed positive-harmonic-function arguments generically; nothing
  here supplies evidence for or against the Riemann Hypothesis, and this
  package must not be described as progress toward it.
- **No sharpness claim as a statement.** The constants
  `(R ∓ ‖w-c‖)/(R ± ‖w-c‖)` are the classical sharp ones, but no statement
  asserts optimality, and none should be added without a new contract.
- **Junk-value honesty.** `Real.circleAverage` of a non-integrable function is
  `0` by definition (`CircleAverage.lean:63`, `circleAverage.integral_undef`).
  Every comparison step in H3 therefore carries explicit `CircleIntegrable`
  hypotheses through `circleAverage_mono`; no step may be "simplified" by
  dropping them, since a vacuous average would make the chain unsound rather
  than merely ugly.
- **Hypothesis honesty.** H3 requires harmonicity on the **closed** ball and
  nonnegativity on the **closed** ball. Both are used: the representation and
  mean-value inputs need the closed ball; nonnegativity is consumed only on
  the sphere and at the center, but is stated on the closed ball to match the
  standard form and the pool signature. Weakening either is DEFERRED-H1
  territory, not a silent edit.

## Death conditions

Stop and re-plan — do **not** patch around — if any of the following occurs.

1. **A new axiom would be needed.** No `axiom`, no `sorry`, no `admit`. The
   Lean kernel is the sole verifier.
2. **Any dependency on an unproved conjecture**, including as a smuggled
   binder hypothesis.
3. **H2 cannot be discharged by any of its three recorded routes.** Then the
   integrability side conditions of `circleAverage_mono` are unreachable and
   the package as designed fails; do **not** respond by removing the
   integrability hypotheses, routing through the junk value of a non-integrable
   `circleAverage`, or asserting the comparison on averages without them.
   A clean blocker is preferable to a vacuous inequality.
4. **A pinned statement would need restating.** If the Pi-smul or `|R|` seams
   (H-3a/H-3b) tempt a local redefinition of `circleAverage`, `poissonKernel`,
   or a "cleaner" duplicate of a pinned lemma — stop; adapt at the use site.
   The package must contain zero `def`s and restate nothing pinned.
5. **The hypotheses drift.** H3 stated with `ball` instead of `closedBall` in
   `hf`, or with nonnegativity only at the center, is a different (and in the
   first case unproved-here) statement; H4 stated without `hR : 0 < R` is a
   different statement — still true (at `R = 0`, `hw` forces `w = c` and `h₀`
   closes both halves; at `R < 0` the closed ball is empty and it is vacuous)
   but **not provable by the H4 skeleton**, whose `hw'` and `hc` steps both
   consume `0 < R` [wording corrected from "is false at `R = 0`" — Annex A4].
   Either drift is a redesign, not a fix.
6. **A capability-map row is declared "stale" or "closed" from this work.**
   Generic pinned Mathlib lowers cost; it never retires a row, and this
   package touches no row's exit evidence in any case
   (MULTIPLICITY_CONTRACT.md death condition 9, adopted).
7. **The contract is cited as RH progress or as a route step.** It is neither;
   see Claim boundary.

## Two-stage gate (adopted by reference)

The full two-stage statement of `MULTIPLICITY_CONTRACT.md` (§Two-stage gate
and promotion ordering) is adopted for this package unchanged: stage one is
acceptance of the H1–H5 surface only (this document); stage two, if it ever
occurs, is a separate built change whose verdict comes from CI, and an
acceptance PR must not carry a promotion. Because the natural home of a built
form is upstream Mathlib rather than this repository's built targets, a third
possible disposition — an upstream PR against Mathlib — is likewise a separate
maintainer decision that this document does not make.
