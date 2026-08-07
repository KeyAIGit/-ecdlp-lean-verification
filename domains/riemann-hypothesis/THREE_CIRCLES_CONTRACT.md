# Hadamard three-circles contract (upstream pool item 3): draft v1

Status: **DRAFT v1 (2026-08-07) — non-built review artifact, offered for STAGE ONE
(INDEPENDENT CONTRACT ACCEPTANCE) ONLY. NOT Lean-checked.** No declaration below
has been elaborated; no `lake build` has been run against any of it. Under the one
invariant, the Lean kernel via CI is the sole judge of every statement in this
contract, and this document carries no kernel verdict of any kind.

**Authority and standing.** This is the statement-surface contract for
`UPSTREAM_POOL.md` §3 ("Hadamard three-circles"), whose §3.1–§3.3 were
**re-verified against the pin this session** rather than trusted (one divergence
found and absorbed; see §1, decision 3). It is an *offered artifact*, not an
active task. An adversarial red-team review of this contract was run
2026-08-07 (verdict **SOUND_WITH_FIXES**, findings B1–B2, both applied in
place; see Annex A). That review accepts a statement surface only: it is not
a kernel verdict and promotes nothing. The RH queue —
`tasks/RIEMANN_HYPOTHESIS.md`, whose dated decision of 2026-08-07 records
`RH-002` as **complete** (all three PARK dispositions CONFIRMED) and moves
the single ACTIVE slot to `RH-011` (acceptance-only review of the zero-set
slice statement surface; no built module, no kernel verdict, no route
execution authorized) — is the authority for this lane;
`repo/ECDLP_DECISION_SUBSTRATE.json` governs the ECDLP lane and its current
dated decision selects no route. Nothing here is authorization to work a route,
and this contract must not be cited as evidence that any route is selected.

**Two-stage gate (same as `MULTIPLICITY_CONTRACT.md` §Two-stage gate).** Stage
one is independent acceptance of the statement surface below: it produces no
built module, no ledger row, no registry or axiom-audit entry, and no kernel
verdict. Stage two is a separate built promotion PR whose verdict is delivered
by CI. An acceptance PR must not carry a promotion. A drafts-lane file lies
outside every lake target (`lakefile.toml:2`, `defaultTargets = ["Ecdlp",
"ResearchOS"]`), so **no green CI run on an acceptance PR is evidence of
anything about the draft.**

Working name: `drafts/ThreeCircles.lean`. Natural eventual home is **upstream**
(`Mathlib/Analysis/Complex/Hadamard.lean` or a small file next to it); every
statement is generic complex analysis over pinned objects and mentions nothing
ζ/ξ-specific. Tag for every statement: `[GEN]` `[PIN]`.

Statement surface: **TC1 – TC11**, comprising **exactly 11 public signatures**
(**1 `def` + 10 theorems**), every one spelled explicitly in a `lean` block in
§2. No signature is mandated in prose only.

Scope: the classical Hadamard three-circles theorem — log-convexity of the
circle-sup of `‖f‖` for `f` analytic on a closed annulus — obtained by
transporting the **pinned** three-lines theorem
(`Complex.HadamardThreeLines.norm_le_interp_of_mem_verticalClosedStrip'`,
Hadamard.lean:607) along `z ↦ exp z`, which maps a vertical strip onto an
annulus. It contains **no** ζ, **no** ξ, **no** zero counting, **no** growth
order, **no** Jensen inequality, and **no** claim of progress on the Riemann
Hypothesis. It closes **no** barrier row of `MATHLIB_CAPABILITY_MAP.md`.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0),
toolchain `leanprover/lean4:v4.31.0`, verified this session via
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`. Every
`file:line` locator below is from that exact tree (paths relative to the
`Mathlib/` root of the pin) and was **re-verified this session by reading the
tree**, not copied from `UPSTREAM_POOL.md`.

## Candidate fields

- **Mechanism.** The pinned endpoint-bound three-lines theorem
  (Hadamard.lean:607, general strip `l < u`, namespaces `Complex` :66 /
  `HadamardThreeLines` :67) is applied to the composite `f ∘ exp` on the strip
  `re ⁻¹' Icc (log r₁) (log r₃)`. `‖exp w‖ = Real.exp w.re`
  (`Complex.norm_exp`, Trigonometric.lean:995) makes `exp` carry the strip
  into the closed annulus and each boundary line into a boundary circle; a
  single explicit witness `Real.log r₂ + z.arg * I` (via
  `Complex.norm_mul_exp_arg_mul_I`, Arg.lean:56) puts any point of the middle
  circle in the image. Because `f ∘ exp` needs only holomorphy, `MapsTo`, and
  boundedness — never injectivity — **no branch of `log` is required
  anywhere**; that is the design point of the whole reduction, and it is why
  three-circles is a corollary of three-lines at this pin rather than an
  independent development.
- **Expected information gain.** A generic, upstream-shaped statement surface
  confirming (or refuting, cheaply) `UPSTREAM_POOL.md` §3.3's "cheap; a
  reduction, not a new analytic idea" assessment. No information about the
  truth of RH is produced, and no barrier row moves at either stage.
- **Claim boundary.** All eleven statements are unconditional consequences of
  pinned Mathlib theorems; there is **no repo prerequisite at all** — unlike
  the multiplicity package, nothing here consumes `Xi.lean` or `Conj.lean`.
  Nothing touches enumeration, counting, growth order, Hadamard products, or
  any route's research obligation. Exactly **one** `def` (TC1), mirroring the
  pinned `sSupNormIm` convention (Hadamard.lean:77).
- **Death condition (stop rule).** Stop or split if a proof would need a new
  axiom, a branch of the complex logarithm (any section of `exp`), a
  `CompleteSpace E` instance, a second `def`, or a statement at `r₁ = 0`
  riding on the `Real.log 0 = 0` junk value. Full list in §Death conditions.
  A clean blocker is preferable to a false convexity.

Proposed module preamble (name-resolution review only):

```lean
import Mathlib.Analysis.Complex.Hadamard                 -- three-lines, verticalStrip, sSupNormIm
import Mathlib.Analysis.SpecialFunctions.Complex.Arg    -- norm_mul_exp_arg_mul_I
import Mathlib.Analysis.SpecialFunctions.ExpDeriv       -- Complex.differentiable_exp
import Mathlib.Analysis.SpecialFunctions.Log.Basic      -- Real.exp_log, log_le_log, log_div
import Mathlib.Analysis.Complex.ReImTopology            -- Complex.closure_preimage_re
import Mathlib.Analysis.Complex.Trigonometric           -- Complex.norm_exp
import Mathlib.Analysis.SpecialFunctions.Pow.Real       -- Real.rpow_add', rpow_one, rpow_nonneg

open Complex Complex.HadamardThreeLines Metric Set
open scoped Real
```

Notation used below: the closed annulus is the set-builder literal
`{w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}` and the open annulus is
`{w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃}`, **written inline at each use site, not as a
new definition** (decision 1, §1). Circles enter theorem binders as `‖w‖ = r`
hypotheses; the set `Metric.sphere (0 : ℂ) r` (Topology/MetricSpace/
Pseudo/Defs.lean:429) appears only inside the helper block TC1–TC4.

Name-collision scan (grep over the pinned tree this session): **zero hits** in
`Mathlib/` for every proposed name — `sSupNormCircle`, `sSupNormCircle_nonneg`,
`bddAbove_image_norm_sphere`, `le_sSupNormCircle`,
`exp_mem_annulus_of_mem_verticalClosedStrip`,
`exp_mem_annulus_of_mem_verticalStrip`, `exists_exp_eq_of_norm_eq`,
`norm_le_interp_of_norm_eq`, `sSupNormCircle_le_interp`,
`norm_le_of_mem_annulus`. A repo-wide scan (`.lean` and `.md`) returns exactly
one textual hit: `UPSTREAM_POOL.md:371`'s own proposed name
`Complex.norm_le_interp_of_norm_eq_of_le_of_le`, of which TC8's name is a
substring — a prose mention in the pool document, not a declaration; no code
collision. An annulus scan at the pin: `grep -rn "def annulus\|Annulus"
Mathlib/` finds **no `Set`-level annulus object** and `Hadamard.lean` itself
never says "annulus" (0 case-insensitive hits) — re-verifying
`UPSTREAM_POOL.md` §0 row 11 rather than trusting it.

---

## 0. Exact pinned interface (quoted from the tree at the pin)

```lean
-- Analysis/Complex/Hadamard.lean. `namespace Complex` :66, `namespace HadamardThreeLines` :67.
-- Section variables governing :588/:607: {E : Type*} [NormedAddCommGroup E] (f : ℂ → E) at :237,
-- plus variable [NormedSpace ℂ E] at :396. NO CompleteSpace, NO CharZero.
def verticalStrip (a : ℝ) (b : ℝ) : Set ℂ := re ⁻¹' Ioo a b            -- :70
def verticalClosedStrip (a : ℝ) (b : ℝ) : Set ℂ := re ⁻¹' Icc a b      -- :73
noncomputable def sSupNormIm {E : Type*} [NormedAddCommGroup E]
    (f : ℂ → E) (x : ℝ) : ℝ :=
  sSup ((norm ∘ f) '' re ⁻¹' {x})                                      -- :77 (bare sSup: junk 0
                                                                        --  when unbounded/empty)

-- :588 — the sSupNormIm ("sup-function") form, kept for reference; NOT the form used below.
lemma norm_le_interpStrip_of_mem_verticalClosedStrip {l u : ℝ} (hul : l < u)
    {f : ℂ → E} {z : ℂ}
    (hz : z ∈ verticalClosedStrip l u) (hd : DiffContOnCl ℂ f (verticalStrip l u))
    (hB : BddAbove ((norm ∘ f) '' verticalClosedStrip l u)) :
    ‖f z‖ ≤ ‖interpStrip' f l u z‖

-- :607 — THE transport input: endpoint-bound form, general strip l < u.
lemma norm_le_interp_of_mem_verticalClosedStrip' {f : ℂ → E} {z : ℂ} {a b l u : ℝ}
    (hul : l < u) (hz : z ∈ verticalClosedStrip l u) (hd : DiffContOnCl ℂ f (verticalStrip l u))
    (hB : BddAbove ((norm ∘ f) '' verticalClosedStrip l u))
    (ha : ∀ z ∈ re ⁻¹' {l}, ‖f z‖ ≤ a) (hb : ∀ z ∈ re ⁻¹' {u}, ‖f z‖ ≤ b) :
    ‖f z‖ ≤ a ^ (1 - (z.re - l) / (u - l)) * b ^ ((z.re - l) / (u - l))

-- Analysis/Calculus/DiffContOnCl.lean:33 (structure; both fields `protected`), :39, :42
structure DiffContOnCl (f : E → F) (s : Set E) : Prop where
  protected differentiableOn : DifferentiableOn 𝕜 f s
  protected continuousOn : ContinuousOn f (closure s)
theorem DifferentiableOn.diffContOnCl (h : DifferentiableOn 𝕜 f (closure s)) : DiffContOnCl 𝕜 f s
theorem Differentiable.diffContOnCl (h : Differentiable 𝕜 f) : DiffContOnCl 𝕜 f s

-- The exp toolbox
theorem norm_exp (z : ℂ) : ‖exp z‖ = Real.exp z.re
                                    -- Analysis/Complex/Trigonometric.lean:995 (namespace Complex :954)
theorem norm_mul_exp_arg_mul_I (x : ℂ) : ‖x‖ * exp (arg x * I) = x
                                    -- Analysis/SpecialFunctions/Complex/Arg.lean:56 (no x ≠ 0 needed)
theorem exp_add : exp (x + y) = exp x * exp y
                                    -- Analysis/Complex/Exponential.lean:109 (namespace Complex :90)
@[simp, norm_cast] theorem ofReal_exp (x : ℝ) : (Real.exp x : ℂ) = exp x
                                    -- Analysis/Complex/Exponential.lean:189
@[simp] theorem differentiable_exp : Differentiable 𝕜 exp
                                    -- Analysis/SpecialFunctions/ExpDeriv.lean:97
                                    -- (namespace Complex :83; [NormedAlgebra 𝕜 ℂ]; use 𝕜 := ℂ)
theorem continuous_exp : Continuous exp
                                    -- Analysis/SpecialFunctions/Exp.lean:68 (namespace Complex :33)

-- Real exp/log order facts (namespace Real)
theorem exp_pos (x : ℝ) : 0 < exp x            -- Analysis/Complex/Exponential.lean:282
theorem exp_lt_exp {x y : ℝ} : exp x < exp y ↔ x < y   -- Analysis/Complex/Exponential.lean:311
theorem exp_le_exp {x y : ℝ} : exp x ≤ exp y ↔ x ≤ y   -- Analysis/Complex/Exponential.lean:315
theorem exp_log (hx : 0 < x) : exp (log x) = x         -- Analysis/SpecialFunctions/Log/Basic.lean:58
theorem log_zero : log 0 = 0                           -- Log/Basic.lean:102 (the junk value)
theorem log_div (hx : x ≠ 0) (hy : y ≠ 0) : log (x / y) = log x - log y   -- Log/Basic.lean:137
theorem log_le_log_iff (h : 0 < x) (h₁ : 0 < y) : log x ≤ log y ↔ x ≤ y   -- Log/Basic.lean:146
@[gcongr, bound] lemma log_le_log (hx : 0 < x) (hxy : x ≤ y) : log x ≤ log y  -- Log/Basic.lean:150
@[gcongr, bound] theorem log_lt_log (hx : 0 < x) (h : x < y) : log x < log y  -- Log/Basic.lean:154

-- Strip topology
theorem closure_preimage_re (s : Set ℝ) : closure (re ⁻¹' s) = re ⁻¹' closure s
                                    -- Analysis/Complex/ReImTopology.lean:70 (namespace Complex :42)
theorem closure_Ioo {a b : α} (hab : a ≠ b) : closure (Ioo a b) = Icc a b
                                    -- Topology/Order/DenselyOrdered.lean:72

-- Compactness / boundedness
instance : ProperSpace ℂ                        -- Analysis/Complex/Basic.lean:138
isCompact_closedBall (x : α) (r : ℝ)            -- Topology/MetricSpace/ProperSpace.lean:40 (export :42)
theorem isCompact_sphere (x : α) (r : ℝ) : IsCompact (sphere x r)   -- ProperSpace.lean:45
theorem IsCompact.of_isClosed_subset (hs : IsCompact s) (ht : IsClosed t) (h : t ⊆ s) :
    IsCompact t                                 -- Topology/Compactness/Compact.lean:103
theorem IsCompact.bddAbove_image [ClosedIciTopology α] [Nonempty α] {f : β → α} {K : Set β}
    (hK : IsCompact K) (hf : ContinuousOn f K) : BddAbove (f '' K)  -- Topology/Order/Compact.lean:332
theorem isClosed_le (hf : Continuous f) (hg : Continuous g) : IsClosed {b | f b ≤ g b}
                                    -- Topology/Order/OrderClosed.lean:444
theorem BddAbove.mono ⦃s t : Set α⦄ (h : s ⊆ t) : BddAbove t → BddAbove s
                                    -- Order/Bounds/Basic.lean:218
theorem le_csSup (h₁ : BddAbove s) (h₂ : a ∈ s) : a ≤ sSup s
                                    -- Order/ConditionallyCompleteLattice/Basic.lean:198

-- Real sSup on possibly-empty/unbounded sets (namespace Real; junk sSup = 0)
protected lemma sSup_le (hs : ∀ x ∈ s, x ≤ a) (ha : 0 ≤ a) : sSup s ≤ a
                                    -- Algebra/Order/Archimedean/Real/Basic.lean:228
lemma sSup_nonneg (hs : ∀ x ∈ s, 0 ≤ x) : 0 ≤ sSup s   -- Archimedean/Real/Basic.lean:294

-- Spheres and norms
def sphere (x : α) (ε : ℝ) := { y | dist y x = ε }      -- Topology/MetricSpace/Pseudo/Defs.lean:429
                                                         -- (namespace Metric :361)
@[to_additive] theorem mem_sphere_one_iff_norm : a ∈ sphere (1 : E) r ↔ ‖a‖ = r
                                    -- Analysis/Normed/Group/Basic.lean:303
                                    -- additive twin: mem_sphere_zero_iff_norm
@[to_additive] theorem mem_closedBall_one_iff : a ∈ closedBall (1 : E) r ↔ ‖a‖ ≤ r
                                    -- Normed/Group/Basic.lean:260; twin: mem_closedBall_zero_iff
theorem sphere_subset_closedBall : sphere x ε ⊆ closedBall x ε
                                    -- Topology/MetricSpace/Pseudo/Defs.lean:480
@[simp] theorem NormedSpace.sphere_nonempty {x : E} {r : ℝ} : (sphere x r).Nonempty ↔ 0 ≤ r
                                    -- Analysis/Normed/Module/RCLike/Real.lean:128
@[to_additive (attr := continuity, fun_prop) continuous_norm]
theorem continuous_norm' : Continuous fun a : E => ‖a‖   -- Analysis/Normed/Group/Continuity.lean:117
@[to_additive (attr := fun_prop) ContinuousOn.norm]
theorem ContinuousOn.norm' (h : ContinuousOn f s) : ContinuousOn (fun x => ‖f x‖) s
                                    -- Normed/Group/Continuity.lean:242

-- Composition on sets
theorem DifferentiableOn.comp (hg : DifferentiableOn 𝕜 g t) (hf : DifferentiableOn 𝕜 f s)
    (st : MapsTo f s t) : DifferentiableOn 𝕜 (g ∘ f) s   -- Analysis/Calculus/FDeriv/Comp.lean:194
theorem ContinuousOn.comp (hg : ContinuousOn g t) (hf : ContinuousOn f s)
    (h : MapsTo f s t) : ContinuousOn (g ∘ f) s          -- Topology/ContinuousOn.lean:497
theorem ContinuousOn.mono (hf : ContinuousOn f s) (h : t ⊆ s) : ...  -- ContinuousOn.lean:312
theorem image_comp (f : β → γ) (g : α → β) (a : Set α) : f ∘ g '' a = f '' g '' a
                                    -- Data/Set/Image.lean:224
lemma image_mono (h : s ⊆ t) : f '' s ⊆ f '' t           -- Data/Set/Image.lean:219
theorem MapsTo.image_subset (h : MapsTo f s t) : f '' s ⊆ t   -- Data/Set/Function.lean:137
theorem mem_image_of_mem (f : α → β) (h : x ∈ a) : f x ∈ f '' a   -- Data/Set/Operations.lean:140

-- rpow bookkeeping (namespace Real; `^` below is Real.rpow: ℝ base, ℝ exponent)
theorem rpow_one (x : ℝ) : x ^ (1 : ℝ) = x               -- SpecialFunctions/Pow/Real.lean:148
theorem rpow_nonneg {x : ℝ} (hx : 0 ≤ x) (y : ℝ) : 0 ≤ x ^ y   -- Pow/Real.lean:163
theorem rpow_add' (hx : 0 ≤ x) (h : y + z ≠ 0) : x ^ (y + z) = x ^ y * x ^ z  -- Pow/Real.lean:210

-- the involution-free additive identity used in TC11
@[to_additive (attr := simp)]
theorem div_mul_cancel (a b : G) : a / b * b = a          -- Algebra/Group/Defs.lean:1253
                                    -- additive twin (simp): sub_add_cancel : a - b + b = a

-- Complex re arithmetic (Data/Complex/Basic.lean)
theorem ofReal_re (r : ℝ) : Complex.re (r : ℂ) = r        -- :88
theorem add_re (z w : ℂ) : (z + w).re = z.re + w.re       -- :169
theorem mul_I_re (z : ℂ) : (z * I).re = -z.im             -- :266
```

**Naming trap (pre-registered).** The three-lines input at :607 lives inside
**two** namespaces (`Complex` :66, `HadamardThreeLines` :67): its full name is
`Complex.HadamardThreeLines.norm_le_interp_of_mem_verticalClosedStrip'` — note
the **prime**; the unprimed `norm_le_interp_of_mem_verticalClosedStrip` does
not exist at the pin (:588 is `norm_le_interp**Strip**_of_…`, the `sSupNormIm`
form). Likewise `verticalStrip`/`verticalClosedStrip` resolve bare only under
`open Complex.HadamardThreeLines`. Every skeleton below assumes the preamble's
`open`; the built file must keep it or write full names.

---

## 1. Formulation decisions (the honest formulation at the pin)

Four design choices, stated so a reviewer can reject them cheaply:

1. **Annulus = inline set-builder, no new `Set` object.** The pin has no
   annulus (re-verified: zero `def annulus|Annulus` hits under `Mathlib/`, zero
   "annulus" mentions in Hadamard.lean). Introducing one would be a second
   `def` for pure notation, and `UPSTREAM_POOL.md` §3.3 already flags the
   choice as reviewer-sensitive. Both annuli are therefore spelled
   `{w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}` / `{w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃}` at each
   use site, exactly as `MULTIPLICITY_CONTRACT.md` handles Ω.

2. **One helper `def`, mirroring the pinned convention.** TC1's
   `sSupNormCircle f r := sSup ((norm ∘ f) '' Metric.sphere (0 : ℂ) r)` is the
   circle twin of the pinned `sSupNormIm` (Hadamard.lean:77): a **bare
   `sSup`**, meaningful when the image is nonempty and bounded above (both
   discharged by TC3 + `NormedSpace.sphere_nonempty` under this contract's
   hypotheses), junk `0` otherwise, exactly the conditionally-complete-lattice
   convention of the file being extended. Theorems outside the helper block
   bind circles as `‖w‖ = r`, so `Metric.sphere` never leaks into the main
   statements; the bridge is `mem_sphere_zero_iff_norm`.

3. **Raw strip exponents in the workhorse; ratio exponents demoted to a
   corollary.** :607's conclusion instantiates *literally* (after rewriting
   the witness's real part) to exponents
   `(log r₂ - log r₁) / (log r₃ - log r₁)` and its complement. TC8/TC9 state
   exactly that, so the main proofs contain **zero log-algebra**. The
   textbook shape `log(r₃/r₂)/log(r₃/r₁)` needs `Real.log_div` and
   denominators-nonzero bookkeeping, so it is quarantined in corollary TC10.
   *This is the one deliberate divergence from `UPSTREAM_POOL.md` §3.1, whose
   proposed signature carries the ratio form; the pool's exponent check
   (`t = log(r₂/r₁)/log(r₃/r₁)`) was re-verified and TC10 recovers its exact
   shape.*

4. **Hypothesis shape: `0 < r₁`, `r₁ ≤ r₂`, `r₂ ≤ r₃`, `r₁ < r₃`; middle
   radius pinned by `hz : ‖z‖ = r₂`.** Equality at either end is allowed and
   degenerates correctly (at `r₂ = r₁` the bound is `M₁ ^ 1 * M₃ ^ 0`);
   `r₁ < r₃` is forced because the strip needs `log r₁ < log r₃` (:607's
   `hul`); `0 < r₁` is **not** decoration — at `r₁ = 0` every `Real.log`
   occurrence rides the junk `log 0 = 0` (Log/Basic.lean:102) and the
   statement becomes false-shaped (death condition 5). `E` needs only
   `[NormedAddCommGroup E] [NormedSpace ℂ E]` — the pinned three-lines needs
   **no `CompleteSpace`** (§0 section-variable note), and this surface must
   not acquire one (death condition 6).

**Periodicity honesty note (the bookkeeping named in advance).** `exp` maps
each boundary line `re ⁻¹' {log rᵢ}` **onto** the circle `‖w‖ = rᵢ`
infinitely-many-to-one (period `2πI`). The transport never needs a section of
`exp`: the boundary hypotheses of :607 quantify over the whole line and are
discharged **pointwise** by `‖exp y‖ = Real.exp y.re = rᵢ` (line → circle,
TC-PERIOD); surjectivity is needed at exactly **one** point — the evaluation
point on the middle circle — and is supplied by the explicit witness of TC7
(circle → strip, TC-SURJ). Any proof attempt that inverts `exp` on a set has
left the contract (death condition 3).

---

## 2. Statement list TC1 – TC11

All statements `[GEN]` `[PIN]`. Throughout, `E : Type*`,
`[NormedAddCommGroup E]`, and (only where marked) `[NormedSpace ℂ E]`.

---

### Block A — circle-sup helper (the only `def`)

## TC1. Circle sup of the norm `[GEN]` `[PIN]` — **the** `def`

### Statement

```lean
noncomputable def sSupNormCircle {E : Type*} [NormedAddCommGroup E]
    (f : ℂ → E) (r : ℝ) : ℝ :=
  sSup ((norm ∘ f) '' Metric.sphere (0 : ℂ) r)
```

### Pinned dependencies (TC1)

Convention and shape copied from `sSupNormIm` — Hadamard.lean:77 (bare `sSup`
of a norm image; junk `0` when unbounded or empty). `Metric.sphere` —
Pseudo/Defs.lean:429.

### Obligations (TC1)

- **TC-SPH** (LOW): everything downstream converts `w ∈ Metric.sphere (0:ℂ) r`
  ↔ `‖w‖ = r` via `mem_sphere_zero_iff_norm` (the `@[to_additive]` twin of
  Normed/Group/Basic.lean:303). Fallback: unfold `Metric.sphere` to
  `dist w 0 = r` and close with `dist_zero_right`/`dist_eq_norm` simp set.

---

## TC2. Nonnegativity `[GEN]` `[PIN]`

### Statement

```lean
lemma sSupNormCircle_nonneg {E : Type*} [NormedAddCommGroup E]
    (f : ℂ → E) (r : ℝ) : 0 ≤ sSupNormCircle f r
```

### Proof skeleton

Mirror of the pinned `sSupNormIm_nonneg` (Hadamard.lean:99–102) verbatim:

```lean
  apply Real.sSup_nonneg
  rintro y ⟨w, _, hw⟩
  simp only [← hw, Function.comp, norm_nonneg]
```

### Pinned dependencies (TC2)

`Real.sSup_nonneg` — Algebra/Order/Archimedean/Real/Basic.lean:294;
`norm_nonneg`. Note the junk case is *included*: for `r < 0` the sphere is
empty, the image is empty, `sSup ∅ = 0`, and the statement is still true —
no side condition needed.

### Obligations (TC2)

None beyond TC-SPH.

---

## TC3. Bounded above on a sphere `[GEN]` `[PIN]`

### Statement

```lean
lemma bddAbove_image_norm_sphere {E : Type*} [NormedAddCommGroup E]
    {f : ℂ → E} {r : ℝ} (hc : ContinuousOn f (Metric.sphere (0 : ℂ) r)) :
    BddAbove ((norm ∘ f) '' Metric.sphere (0 : ℂ) r)
```

### Proof skeleton

```lean
  exact (isCompact_sphere (0 : ℂ) r).bddAbove_image hc.norm
```

### Pinned dependencies (TC3)

`isCompact_sphere` — ProperSpace.lean:45 (needs `ProperSpace ℂ` —
Analysis/Complex/Basic.lean:138, instance, nothing to build);
`IsCompact.bddAbove_image` — Topology/Order/Compact.lean:332;
`ContinuousOn.norm` — the `@[to_additive]` name of
Normed/Group/Continuity.lean:242.

### Obligations (TC3)

- **TC-COMP** (LOW): `hc.norm : ContinuousOn (fun x => ‖f x‖) …` versus the
  goal's `norm ∘ f` — definitionally equal, but `bddAbove_image` matches by
  unification, so an `exact` may need `show BddAbove ((fun x => ‖f x‖) ''
  Metric.sphere (0:ℂ) r)` first. Fallback:
  `simpa [Function.comp] using (isCompact_sphere (0:ℂ) r).bddAbove_image hc.norm`.

---

## TC4. Pointwise bound by the circle sup `[GEN]` `[PIN]`

### Statement

```lean
lemma le_sSupNormCircle {E : Type*} [NormedAddCommGroup E]
    {f : ℂ → E} {r : ℝ} {w : ℂ}
    (hc : ContinuousOn f (Metric.sphere (0 : ℂ) r)) (hw : ‖w‖ = r) :
    ‖f w‖ ≤ sSupNormCircle f r
```

### Proof skeleton

```lean
  exact le_csSup (bddAbove_image_norm_sphere hc)
    (Set.mem_image_of_mem _ (mem_sphere_zero_iff_norm.mpr hw))
```

### Pinned dependencies (TC4)

TC3; `le_csSup` — Order/ConditionallyCompleteLattice/Basic.lean:198;
`Set.mem_image_of_mem` — Data/Set/Operations.lean:140;
`mem_sphere_zero_iff_norm` (TC-SPH).

### Obligations (TC4)

- **TC-COMP** again (LOW): the membership produced is
  `(norm ∘ f) w ∈ (norm ∘ f) '' …` with `(norm ∘ f) w` needing to be seen as
  `‖f w‖` — `Function.comp_apply` in a `simpa` if `exact` balks.

---

### Block B — exp-transport bookkeeping (strip ↔ annulus)

## TC5. `exp` carries the closed strip into the closed annulus `[GEN]` `[PIN]`

### Statement

```lean
lemma exp_mem_annulus_of_mem_verticalClosedStrip {r₁ r₃ : ℝ}
    (h₁ : 0 < r₁) (h₃ : 0 < r₃) {w : ℂ}
    (hw : w ∈ verticalClosedStrip (Real.log r₁) (Real.log r₃)) :
    Complex.exp w ∈ {z : ℂ | r₁ ≤ ‖z‖ ∧ ‖z‖ ≤ r₃}
```

### Proof skeleton

```lean
  simp only [verticalClosedStrip, Set.mem_preimage, Set.mem_Icc] at hw
  simp only [Set.mem_setOf_eq, Complex.norm_exp]
  exact ⟨by calc r₁ = Real.exp (Real.log r₁) := (Real.exp_log h₁).symm
              _ ≤ Real.exp w.re := Real.exp_le_exp.mpr hw.1,
         by calc Real.exp w.re ≤ Real.exp (Real.log r₃) := Real.exp_le_exp.mpr hw.2
              _ = r₃ := Real.exp_log h₃⟩
```

### Pinned dependencies (TC5)

`Complex.norm_exp` — Trigonometric.lean:995 (namespace `Complex` :954);
`Real.exp_le_exp` — Analysis/Complex/Exponential.lean:315 (namespace `Real`
:200); `Real.exp_log` — Log/Basic.lean:58; `verticalClosedStrip` —
Hadamard.lean:73.

### Obligations (TC5)

- **TC-EXP-MONO** (LOW): direction of `exp_le_exp` (it is an `iff`; use
  `.mpr`). Fallback: `gcongr` (both `Real.exp` monotonicity and
  `Real.log_le_log` carry `@[gcongr]`/`@[bound]` at the pin).

---

## TC6. `exp` carries the open strip into the open annulus `[GEN]` `[PIN]`

### Statement

```lean
lemma exp_mem_annulus_of_mem_verticalStrip {r₁ r₃ : ℝ}
    (h₁ : 0 < r₁) (h₃ : 0 < r₃) {w : ℂ}
    (hw : w ∈ verticalStrip (Real.log r₁) (Real.log r₃)) :
    Complex.exp w ∈ {z : ℂ | r₁ < ‖z‖ ∧ ‖z‖ < r₃}
```

### Proof skeleton

TC5 verbatim with `Set.mem_Ioo` for `Set.mem_Icc`, `Real.exp_lt_exp`
(Analysis/Complex/Exponential.lean:311) for `exp_le_exp`, and strict `calc`
steps.

### Pinned dependencies (TC6)

As TC5, plus `Real.exp_lt_exp` — Analysis/Complex/Exponential.lean:311;
`verticalStrip` — Hadamard.lean:70.

### Obligations (TC6)

TC-EXP-MONO (LOW), as TC5.

---

## TC7. `exp`-surjectivity onto a circle, with real part pinned `[GEN]` `[PIN]` — *the surjectivity leg*

### Statement

```lean
lemma exists_exp_eq_of_norm_eq {r : ℝ} (hr : 0 < r) {z : ℂ} (hz : ‖z‖ = r) :
    ∃ w : ℂ, w.re = Real.log r ∧ Complex.exp w = z
```

### Proof skeleton

The witness is explicit; **no logarithm of `z` is chosen** — `z.arg` is total.

```lean
  refine ⟨Real.log r + z.arg * I, ?_, ?_⟩
  · simp [Complex.add_re, Complex.ofReal_re, Complex.mul_I_re, Complex.ofReal_im]
  · rw [Complex.exp_add, ← Complex.ofReal_exp, Real.exp_log hr, ← hz]
    exact Complex.norm_mul_exp_arg_mul_I z
```

### Pinned dependencies (TC7)

`Complex.norm_mul_exp_arg_mul_I` — Arg.lean:56, **verified verbatim**:
`(x : ℂ) : ‖x‖ * exp (arg x * I) = x`, stated for **all** `x` (at `x = 0` both
sides are `0`), so no `z ≠ 0` hypothesis is needed even though `hr` supplies
one; `Complex.exp_add` — Analysis/Complex/Exponential.lean:109;
`Complex.ofReal_exp` — Exponential.lean:189 (`@[simp, norm_cast]`);
`Real.exp_log` — Log/Basic.lean:58; re-arithmetic — Data/Complex/Basic.lean:88
(`ofReal_re`), :169 (`add_re`), :266 (`mul_I_re`).

### Obligations (TC7)

- **TC-SURJ** (MEDIUM). Two known friction points, both coercion-shaped:
  (i) the `rw` chain must pass through
  `exp (↑(log r) + ↑z.arg * I) = exp ↑(log r) * exp (↑z.arg * I)`
  (`exp_add`), then convert `exp ↑(log r)` to `↑(Real.exp (Real.log r))`
  **against** the `@[simp]` normal form (`← ofReal_exp`), rewrite under the
  coercion (`Real.exp_log hr`), and finally fold `↑r` to `↑‖z‖` (`← hz`,
  which must fire under `Complex.ofReal`). If `← hz` fails to rewrite under
  the coercion, fallback: `subst`-free `have : (r : ℂ) = (‖z‖ : ℂ) :=
  congrArg _ hz.symm; rw [this]` or `push_cast`/`norm_cast` before the final
  `exact`. (ii) the real-part goal after `simp` must close to
  `Real.log r + -0 = Real.log r` or be already closed; if the simp set leaves
  `-(↑z.arg).im`, add `Complex.ofReal_im` explicitly (it is in the listed
  set). Fallback for the whole leg: prove `Complex.exp (↑(Real.log r) +
  ↑z.arg * I) = z` by `simp [Complex.exp_add, ← Complex.ofReal_exp,
  Real.exp_log hr, hz, Complex.norm_mul_exp_arg_mul_I]` and extract.

---

### Block C — the workhorse

## TC8. Three-circles, pointwise endpoint-bound form `[GEN]` `[PIN]` — *the exp-transport of the pinned three-lines*

### Statement

```lean
theorem norm_le_interp_of_norm_eq {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] {f : ℂ → E} {r₁ r₂ r₃ M₁ M₃ : ℝ} {z : ℂ}
    (h₁ : 0 < r₁) (h₁₂ : r₁ ≤ r₂) (h₂₃ : r₂ ≤ r₃) (h₁₃ : r₁ < r₃)
    (hd : DifferentiableOn ℂ f {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃})
    (hc : ContinuousOn f {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃})
    (hM₁ : ∀ w : ℂ, ‖w‖ = r₁ → ‖f w‖ ≤ M₁)
    (hM₃ : ∀ w : ℂ, ‖w‖ = r₃ → ‖f w‖ ≤ M₃)
    (hz : ‖z‖ = r₂) :
    ‖f z‖ ≤ M₁ ^ (1 - (Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁))
          * M₃ ^ ((Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁))
```

(`^` is `Real.rpow`. The exponents are exactly what Hadamard.lean:607 emits at
`l := Real.log r₁`, `u := Real.log r₃` after the witness's real part is
rewritten to `Real.log r₂` — decision 3.)

### Proof skeleton

*Full assembly sketch. Stages are named to match the obligation register.*

```lean
  have h₂ : 0 < r₂ := h₁.trans_le h₁₂
  have h₃ : 0 < r₃ := h₁.trans h₁₃
  have hul : Real.log r₁ < Real.log r₃ := Real.log_lt_log h₁ h₁₃
  -- (TC-SURJ) the evaluation point upstairs
  obtain ⟨w, hwre, hwexp⟩ := exists_exp_eq_of_norm_eq h₂ hz
  have hw : w ∈ verticalClosedStrip (Real.log r₁) (Real.log r₃) := by
    simp only [verticalClosedStrip, Set.mem_preimage, Set.mem_Icc, hwre]
    exact ⟨Real.log_le_log h₁ h₁₂, Real.log_le_log h₂ h₂₃⟩
  -- (TC-CL) closure of the open strip is the closed strip
  have hcl : closure (verticalStrip (Real.log r₁) (Real.log r₃))
      = verticalClosedStrip (Real.log r₁) (Real.log r₃) := by
    rw [verticalStrip, verticalClosedStrip, Complex.closure_preimage_re,
        closure_Ioo hul.ne]
  -- MapsTo, open and closed (TC5/TC6)
  have hmapsO : Set.MapsTo Complex.exp (verticalStrip (Real.log r₁) (Real.log r₃))
      {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃} :=
    fun _ hw => exp_mem_annulus_of_mem_verticalStrip h₁ h₃ hw
  have hmapsC : Set.MapsTo Complex.exp (verticalClosedStrip (Real.log r₁) (Real.log r₃))
      {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃} :=
    fun _ hw => exp_mem_annulus_of_mem_verticalClosedStrip h₁ h₃ hw
  -- (TC-DCOC) DiffContOnCl of the composite; fields are protected, use ⟨_, _⟩
  have hd' : DiffContOnCl ℂ (f ∘ Complex.exp) (verticalStrip (Real.log r₁) (Real.log r₃)) :=
    ⟨hd.comp Complex.differentiable_exp.differentiableOn hmapsO,
     by rw [hcl]; exact hc.comp Complex.continuous_exp.continuousOn hmapsC⟩
  -- (TC-BB) boundedness upstairs, transported from the compact annulus
  have hann : IsCompact {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃} :=
    (isCompact_closedBall (0 : ℂ) r₃).of_isClosed_subset
      ((isClosed_le continuous_const continuous_norm).inter
        (isClosed_le continuous_norm continuous_const))
      (fun w hw => mem_closedBall_zero_iff.mpr hw.2)
  have hB : BddAbove ((norm ∘ (f ∘ Complex.exp)) ''
      verticalClosedStrip (Real.log r₁) (Real.log r₃)) := by
    have hbig : BddAbove ((norm ∘ f) '' {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}) :=
      hann.bddAbove_image hc.norm
    refine hbig.mono ?_
    calc (norm ∘ (f ∘ Complex.exp)) '' verticalClosedStrip _ _
        = (norm ∘ f) '' (Complex.exp '' verticalClosedStrip _ _) :=
          Set.image_comp (norm ∘ f) Complex.exp _
      _ ⊆ (norm ∘ f) '' {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃} :=
          Set.image_mono hmapsC.image_subset
  -- (TC-PERIOD) boundary bounds upstairs: pointwise on the WHOLE line, no section of exp
  have ha : ∀ y ∈ Complex.re ⁻¹' {Real.log r₁}, ‖(f ∘ Complex.exp) y‖ ≤ M₁ := by
    intro y hy
    refine hM₁ _ ?_
    rw [Complex.norm_exp, show y.re = Real.log r₁ from hy, Real.exp_log h₁]
  have hb : ∀ y ∈ Complex.re ⁻¹' {Real.log r₃}, ‖(f ∘ Complex.exp) y‖ ≤ M₃ := by
    intro y hy
    refine hM₃ _ ?_
    rw [Complex.norm_exp, show y.re = Real.log r₃ from hy, Real.exp_log h₃]
  -- the pinned three-lines, endpoint form (Hadamard.lean:607)
  have key := Complex.HadamardThreeLines.norm_le_interp_of_mem_verticalClosedStrip'
    hul hw hd' hB ha hb
  -- rewrite evaluation point and exponent; no log-algebra
  rw [Function.comp_apply, hwexp, hwre] at key
  exact key
```

### Pinned dependencies (TC8)

TC5, TC6, TC7; and, all re-verified verbatim this session:
`Complex.HadamardThreeLines.norm_le_interp_of_mem_verticalClosedStrip'` —
Hadamard.lean:607 (hypothesis order `hul hz hd hB ha hb`; conclusion
`‖f z‖ ≤ a ^ (1 - (z.re - l) / (u - l)) * b ^ ((z.re - l) / (u - l))`; needs
only `[NormedAddCommGroup E] [NormedSpace ℂ E]` — section variables
Hadamard.lean:237/:396, **no `CompleteSpace`**);
`Real.log_lt_log` — Log/Basic.lean:154; `Real.log_le_log` — Log/Basic.lean:150;
`Complex.closure_preimage_re` — ReImTopology.lean:70; `closure_Ioo` —
DenselyOrdered.lean:72 (hypothesis `a ≠ b`, supplied by `hul.ne`);
`DiffContOnCl` — DiffContOnCl.lean:33 (anonymous constructor; both fields
`protected`, so no named-field dot access);
`Complex.differentiable_exp` — ExpDeriv.lean:97; `Complex.continuous_exp` —
Exp.lean:68; `DifferentiableOn.comp` — FDeriv/Comp.lean:194;
`ContinuousOn.comp` — ContinuousOn.lean:497;
`isCompact_closedBall` — ProperSpace.lean:40/:42 + `ProperSpace ℂ` instance
(Analysis/Complex/Basic.lean:138); `IsCompact.of_isClosed_subset` —
Compact.lean:103; `isClosed_le` — OrderClosed.lean:444; `continuous_norm` —
Continuity.lean:117 (to_additive name); `mem_closedBall_zero_iff` — twin of
Normed/Group/Basic.lean:260; `IsCompact.bddAbove_image` — Compact.lean:332;
`ContinuousOn.norm` — Continuity.lean:242 (to_additive name); `BddAbove.mono`
— Bounds/Basic.lean:218; `Set.image_comp` — Image.lean:224; `Set.image_mono`
— Image.lean:219; `Set.MapsTo.image_subset` — Function.lean:137;
`Complex.norm_exp` — Trigonometric.lean:995; `Real.exp_log` — Log/Basic.lean:58.

### Obligations (TC8)

- **TC-BB** (HIGH — the riskiest step of the package). The strip is **not**
  compact, so `hB` must be transported, and the transport is where three
  syntactic hazards stack: (i) :607's `hB` is stated for `norm ∘ f` with `f`
  instantiated to `f ∘ Complex.exp`, i.e. the set is
  `(norm ∘ (f ∘ exp)) '' strip`, while `Set.image_comp` speaks of
  `((norm ∘ f) ∘ exp) '' strip` — equal only up to `Function.comp`
  associativity, which is defeq but **not** syntactic, so the `calc`'s first
  step may need `show` or `Function.comp_assoc`; (ii) `Set.image_comp`'s
  statement orientation (`f ∘ g '' a = f '' g '' a`, Image.lean:224) must be
  applied left-to-right with `f := norm ∘ f`, `g := exp`; (iii) the annulus
  compactness argument threads `mem_closedBall_zero_iff` through a
  set-builder membership. Fallbacks, in order: (a) drop `image_comp` entirely
  — unfold `BddAbove`/`upperBounds` and chase
  `rintro _ ⟨y, hy, rfl⟩; exact le_csSup … (Set.mem_image_of_mem _ (hmapsC hy))`
  against `hbig`; (b) prove `hB` directly from `hcl ▸ hd'.continuousOn` —
  **rejected in design**: the strip is unbounded, `IsCompact.bddAbove_image`
  does not apply to it, and no pinned lemma bounds a continuous image of an
  unbounded set; the transport through the compact annulus is forced. This is
  the step `UPSTREAM_POOL.md` §3.3 named "the only place a careful writer
  will spend time" — re-verified and **agreed, upgraded to HIGH** for the
  syntactic stacking, not for mathematical content.
- **TC-PERIOD** (MEDIUM). The boundary hypotheses `ha`/`hb` of :607 quantify
  over the **entire** vertical line, whose points hit each circle point
  infinitely often (`exp` has period `2πI`). The discharge must run
  line → circle (each line point *lands on* the circle, by
  `norm_exp` + `exp_log`) and never circle → line (choosing preimages — a
  section of `exp` — is unnecessary and unavailable without `log` branches;
  death condition 3). The skeleton's `show y.re = Real.log r₁ from hy` step
  converts `y ∈ re ⁻¹' {log r₁}` (i.e. `y.re ∈ {log r₁}`) to the equation;
  if the `show` fails on `Set.mem_singleton_iff` unfolding, fallback:
  `simp only [Set.mem_preimage, Set.mem_singleton_iff] at hy` first.
- **TC-CL** (MEDIUM). `closure (verticalStrip l u) = verticalClosedStrip l u`
  is **not** a pinned lemma; it is assembled from `Complex.closure_preimage_re`
  (ReImTopology.lean:70) + `closure_Ioo` (DenselyOrdered.lean:72, needs
  `l ≠ u` — supplied by `hul.ne`, which is why `r₁ < r₃` is a hypothesis and
  not `r₁ ≤ r₃`). The `rw` must unfold the two `def`s (Hadamard.lean:70/:73)
  first; if `rw [verticalStrip]` misfires on the definitional unfold,
  fallback: `simp only [verticalStrip, verticalClosedStrip]` or `unfold`.
- **TC-DCOC** (LOW). `DiffContOnCl`'s fields are `protected`
  (DiffContOnCl.lean:33) — construct with the anonymous constructor `⟨_, _⟩`
  as in the skeleton; the second component's expected type is
  `ContinuousOn (f ∘ exp) (closure (verticalStrip …))`, so the `rw [hcl]`
  must happen **inside** that component (as written), not on the outer goal.
- **TC-EVAL** (MEDIUM). The final
  `rw [Function.comp_apply, hwexp, hwre] at key` performs three rewrites in
  `key`: `(f ∘ exp) w ↝ f (exp w)`, `exp w ↝ z`, `w.re ↝ Real.log r₂`. Order
  matters (`hwexp` must fire before `w` disappears from the norm; `hwre` must
  fire on **both** exponent occurrences — `rw` rewrites all occurrences, so
  this is safe). If `Function.comp_apply` fails syntactically, fallback:
  `simp only [Function.comp_apply] at key`. Occurrence audit: after the first
  two rewrites, `w` occurs in `key` only as `w.re` (twice, in the two
  exponents); `hwre` clears both; the result is **literally** the goal — by
  design there is no residual algebra (decision 3).

---

### Block D — the log-convexity headline and corollaries

## TC9. **Hadamard three-circles: log-convexity of the circle sup** `[GEN]` `[PIN]` — *the headline*

### Statement

```lean
theorem sSupNormCircle_le_interp {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] {f : ℂ → E} {r₁ r₂ r₃ : ℝ}
    (h₁ : 0 < r₁) (h₁₂ : r₁ ≤ r₂) (h₂₃ : r₂ ≤ r₃) (h₁₃ : r₁ < r₃)
    (hd : DifferentiableOn ℂ f {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃})
    (hc : ContinuousOn f {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}) :
    sSupNormCircle f r₂ ≤
      sSupNormCircle f r₁
        ^ (1 - (Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁))
      * sSupNormCircle f r₃
        ^ ((Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁))
```

This *is* the statement "`log (sSupNormCircle f (Real.exp x))` is convex in
`x`" in inequality form at three points, without mentioning `ConvexOn` — the
pin's own three-lines development makes the same presentational choice
(Hadamard.lean:582–607 states interpolation inequalities, not a `ConvexOn`
object), and this contract follows it (no new convexity API is introduced or
needed).

### Proof skeleton

```lean
  have h₂ : 0 < r₂ := h₁.trans_le h₁₂
  have h₃ : 0 < r₃ := h₁.trans h₁₃
  -- circles sit inside the closed annulus
  have hsub : ∀ {r : ℝ}, r₁ ≤ r → r ≤ r₃ →
      Metric.sphere (0 : ℂ) r ⊆ {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃} := by
    intro r hr₁ hr₃ w hw
    have hwn := mem_sphere_zero_iff_norm.mp hw
    exact ⟨hwn ▸ hr₁, hwn ▸ hr₃⟩
  -- sSup over the middle circle, against a nonneg RHS (junk-safe)
  refine Real.sSup_le ?_ (mul_nonneg
    (Real.rpow_nonneg (sSupNormCircle_nonneg f r₁) _)
    (Real.rpow_nonneg (sSupNormCircle_nonneg f r₃) _))
  rintro y ⟨z, hz, rfl⟩
  exact norm_le_interp_of_norm_eq h₁ h₁₂ h₂₃ h₁₃ hd hc
    (fun w hw => le_sSupNormCircle (hc.mono (hsub le_rfl h₁₃.le)) hw)
    (fun w hw => le_sSupNormCircle (hc.mono (hsub h₁₃.le le_rfl)) hw)
    (mem_sphere_zero_iff_norm.mp hz)
```

### Pinned dependencies (TC9)

TC1, TC2, TC4, TC8; `Real.sSup_le` — Archimedean/Real/Basic.lean:228
(**protected**; write `Real.sSup_le`; its second argument `0 ≤ a` is exactly
why the RHS-nonnegativity subgoal exists — this is the junk-safety of the
bare-`sSup` convention, decision 2); `Real.rpow_nonneg` — Pow/Real.lean:163;
`mul_nonneg`; `ContinuousOn.mono` — ContinuousOn.lean:312;
`mem_sphere_zero_iff_norm` (TC-SPH).

### Obligations (TC9)

- **TC-SUP** (MEDIUM). Three small hazards: (i) after `rintro y ⟨z, hz, rfl⟩`
  the goal head is `(norm ∘ f) z ≤ …` — `Function.comp_apply` may need a
  `simp only` before the final `exact`; (ii) `hwn ▸ hr₁` transports
  `r₁ ≤ r` along `‖w‖ = r` **backwards** — if the `▸` direction misfires,
  fallback `exact ⟨hwn.symm ▸ hr₁, hwn.symm ▸ hr₃⟩` or `constructor <;> rw
  [hwn] <;> assumption`; (iii) the two `hsub` instantiations pass endpoint
  inequalities (`le_rfl`, `h₁₃.le`) — audit that inner circle uses
  `hsub le_rfl h₁₃.le` and outer uses `hsub h₁₃.le le_rfl`, as written.

---

## TC10. Corollary: classical ratio-exponent form `[GEN]` `[PIN]`

### Statement

```lean
theorem norm_le_interp_of_norm_eq' {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] {f : ℂ → E} {r₁ r₂ r₃ M₁ M₃ : ℝ} {z : ℂ}
    (h₁ : 0 < r₁) (h₁₂ : r₁ ≤ r₂) (h₂₃ : r₂ ≤ r₃) (h₁₃ : r₁ < r₃)
    (hd : DifferentiableOn ℂ f {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃})
    (hc : ContinuousOn f {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃})
    (hM₁ : ∀ w : ℂ, ‖w‖ = r₁ → ‖f w‖ ≤ M₁)
    (hM₃ : ∀ w : ℂ, ‖w‖ = r₃ → ‖f w‖ ≤ M₃)
    (hz : ‖z‖ = r₂) :
    ‖f z‖ ≤ M₁ ^ (Real.log (r₃ / r₂) / Real.log (r₃ / r₁))
          * M₃ ^ (Real.log (r₂ / r₁) / Real.log (r₃ / r₁))
```

(This is precisely the `UPSTREAM_POOL.md` §3.1 shape; its exponent check —
`t = log(r₂/r₁)/log(r₃/r₁)`, `1 - t = log(r₃/r₂)/log(r₃/r₁)` — was
re-verified.)

### Proof skeleton

```lean
  have h₂ : 0 < r₂ := h₁.trans_le h₁₂
  have h₃ : 0 < r₃ := h₁.trans h₁₃
  have hne : Real.log r₃ - Real.log r₁ ≠ 0 :=
    sub_ne_zero.mpr (Real.log_lt_log h₁ h₁₃).ne'
  have e₂ : Real.log (r₂ / r₁) / Real.log (r₃ / r₁)
      = (Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁) := by
    rw [Real.log_div h₂.ne' h₁.ne', Real.log_div h₃.ne' h₁.ne']
  have e₁ : Real.log (r₃ / r₂) / Real.log (r₃ / r₁)
      = 1 - (Real.log r₂ - Real.log r₁) / (Real.log r₃ - Real.log r₁) := by
    rw [Real.log_div h₃.ne' h₂.ne', Real.log_div h₃.ne' h₁.ne']
    field_simp
  rw [e₁, e₂]
  exact norm_le_interp_of_norm_eq h₁ h₁₂ h₂₃ h₁₃ hd hc hM₁ hM₃ hz
```

### Pinned dependencies (TC10)

TC8; `Real.log_div` — Log/Basic.lean:137 (hypotheses `x ≠ 0`, `y ≠ 0`,
supplied as `.ne'` of the positivity chain); `Real.log_lt_log` —
Log/Basic.lean:154; `sub_ne_zero`.

### Obligations (TC10)

- **TC-ALG** (LOW). All the log-algebra of the package is quarantined here
  (decision 3). The `e₁` identity `(u - m)/(u - l) = 1 - (m - l)/(u - l)`
  needs `u - l ≠ 0` (`hne`); if `field_simp` leaves a `ring`-shaped residue,
  append `ring`. Nothing else in TC1–TC11 rewrites a logarithm.

---

## TC11. Corollary: two-boundary maximum principle on the annulus `[GEN]` `[PIN]`

### Statement

```lean
theorem norm_le_of_mem_annulus {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] {f : ℂ → E} {r₁ r₃ M : ℝ} {z : ℂ}
    (h₁ : 0 < r₁) (h₁₃ : r₁ < r₃)
    (hd : DifferentiableOn ℂ f {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃})
    (hc : ContinuousOn f {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃})
    (hM₁ : ∀ w : ℂ, ‖w‖ = r₁ → ‖f w‖ ≤ M)
    (hM₃ : ∀ w : ℂ, ‖w‖ = r₃ → ‖f w‖ ≤ M)
    (hz : z ∈ {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}) :
    ‖f z‖ ≤ M
```

### Proof skeleton

```lean
  obtain ⟨hz₁, hz₃⟩ := hz
  -- 0 ≤ M, witnessed on the (nonempty) inner circle — this is where sphere_nonempty earns its keep
  obtain ⟨w₀, hw₀⟩ := NormedSpace.sphere_nonempty (x := (0 : ℂ)) (r := r₁) |>.mpr h₁.le
  have hM : 0 ≤ M := (norm_nonneg _).trans (hM₁ w₀ (mem_sphere_zero_iff_norm.mp hw₀))
  -- TC8 at the middle radius ‖z‖
  have key := norm_le_interp_of_norm_eq h₁ hz₁ hz₃ h₁₃ hd hc hM₁ hM₃ rfl
  set t := (Real.log ‖z‖ - Real.log r₁) / (Real.log r₃ - Real.log r₁) with ht
  calc ‖f z‖ ≤ M ^ (1 - t) * M ^ t := key
    _ = M ^ ((1 - t) + t) := (Real.rpow_add' hM (by rw [sub_add_cancel]; norm_num)).symm
    _ = M := by rw [sub_add_cancel, Real.rpow_one]
```

### Pinned dependencies (TC11)

TC8; `NormedSpace.sphere_nonempty` — RCLike/Real.lean:128 (`@[simp]`; iff, use
`.mpr h₁.le`; needs the nontrivial real normed space ℂ — satisfied);
`mem_sphere_zero_iff_norm` (TC-SPH); `Real.rpow_add'` — Pow/Real.lean:210
(hypotheses `0 ≤ x` and `y + z ≠ 0`; the sum here is
`(1 - t) + t = 1 ≠ 0` via `sub_add_cancel`, the `@[to_additive (attr :=
simp)]` twin of `div_mul_cancel`, Group/Defs.lean:1253); `Real.rpow_one` —
Pow/Real.lean:148.

### Obligations (TC11)

- **TC-RPOW** (LOW). Two known frictions: (i) `key`'s middle radius is the
  *term* `‖z‖`, so its hypotheses are `r₁ ≤ ‖z‖` / `‖z‖ ≤ r₃` — exactly
  `hz₁`/`hz₃` after `Set.mem_setOf_eq` unfolding (if `obtain` on `hz` fails
  syntactically, prepend `simp only [Set.mem_setOf_eq] at hz`); the `hz`
  argument of TC8 is `rfl : ‖z‖ = ‖z‖`. (ii) `rpow_add'` is stated
  base-first (`x ^ (y + z) = x ^ y * x ^ z`); the `calc` applies it right-to-
  left (`.symm`) — if the `set t` abbreviation blocks the `sub_add_cancel`
  rewrite inside the side-goal, inline `t` (`rw [ht]`) first or discharge the
  side-goal as `by simp` (`sub_add_cancel` is `@[simp]`).
- **TC-NONNEG** (LOW). `0 ≤ M` is **derived, not assumed** — the inner circle
  is nonempty (`0 < r₁`), so `hM₁` at any witness dominates a norm. Do not
  "simplify" the statement by adding `0 ≤ M` as a hypothesis; it is
  redundant, and adding redundant hypotheses to a proposed upstream statement
  is exactly what a Mathlib review would strip.

---

## Pinned API dependencies table

| Symbol (full name) | Locator (pin) | Used by |
|---|---|---|
| `Complex.HadamardThreeLines.norm_le_interp_of_mem_verticalClosedStrip'` | Hadamard.lean:607 | TC8 |
| `Complex.HadamardThreeLines.norm_le_interpStrip_of_mem_verticalClosedStrip` | Hadamard.lean:588 | (reference only; not consumed) |
| `Complex.HadamardThreeLines.verticalStrip` / `verticalClosedStrip` | Hadamard.lean:70 / :73 | TC5–TC9 |
| `Complex.HadamardThreeLines.sSupNormIm` | Hadamard.lean:77 | TC1 (convention only) |
| `DiffContOnCl` (structure) | DiffContOnCl.lean:33 | TC8 |
| `Complex.norm_exp` | Trigonometric.lean:995 | TC5, TC6, TC8 |
| `Complex.norm_mul_exp_arg_mul_I` | Arg.lean:56 | TC7 |
| `Complex.exp_add` / `Complex.ofReal_exp` | Analysis/Complex/Exponential.lean:109 / :189 | TC7 |
| `Complex.differentiable_exp` / `Complex.continuous_exp` | ExpDeriv.lean:97 / Exp.lean:68 | TC8 |
| `Real.exp_pos` / `exp_lt_exp` / `exp_le_exp` | Analysis/Complex/Exponential.lean:282 / :311 / :315 | TC5, TC6 |
| `Real.exp_log` / `log_zero` / `log_div` / `log_le_log_iff` / `log_le_log` / `log_lt_log` | Log/Basic.lean:58 / :102 / :137 / :146 / :150 / :154 | TC5–TC10 |
| `Complex.closure_preimage_re` | ReImTopology.lean:70 | TC8 |
| `closure_Ioo` | DenselyOrdered.lean:72 | TC8 |
| `instance : ProperSpace ℂ` | Analysis/Complex/Basic.lean:138 | TC3, TC8 |
| `isCompact_closedBall` / `isCompact_sphere` | ProperSpace.lean:40,:42 / :45 | TC8 / TC3 |
| `IsCompact.of_isClosed_subset` | Compact.lean:103 | TC8 |
| `IsCompact.bddAbove_image` | Topology/Order/Compact.lean:332 | TC3, TC8 |
| `isClosed_le` | OrderClosed.lean:444 | TC8 |
| `BddAbove.mono` | Order/Bounds/Basic.lean:218 | TC8 |
| `le_csSup` | ConditionallyCompleteLattice/Basic.lean:198 | TC4 |
| `Real.sSup_le` (protected) / `Real.sSup_nonneg` | Archimedean/Real/Basic.lean:228 / :294 | TC9 / TC2 |
| `Metric.sphere` / `sphere_subset_closedBall` | Pseudo/Defs.lean:429 / :480 | TC1 / (TC3 route) |
| `mem_sphere_zero_iff_norm` (to_additive of :303) | Normed/Group/Basic.lean:303 | TC4, TC9, TC11 |
| `mem_closedBall_zero_iff` (to_additive of :260) | Normed/Group/Basic.lean:260 | TC8 |
| `NormedSpace.sphere_nonempty` | RCLike/Real.lean:128 | TC11 |
| `continuous_norm` / `ContinuousOn.norm` (to_additive) | Continuity.lean:117 / :242 | TC3, TC8 |
| `DifferentiableOn.comp` / `ContinuousOn.comp` / `ContinuousOn.mono` | FDeriv/Comp.lean:194 / ContinuousOn.lean:497 / :312 | TC8, TC9 |
| `Set.image_comp` / `Set.image_mono` / `Set.MapsTo.image_subset` / `Set.mem_image_of_mem` | Image.lean:224 / :219 / Function.lean:137 / Operations.lean:140 | TC4, TC8 |
| `Real.rpow_one` / `rpow_nonneg` / `rpow_add'` | Pow/Real.lean:148 / :163 / :210 | TC9, TC11 |
| `sub_add_cancel` (to_additive-simp of Group/Defs.lean:1253) | Group/Defs.lean:1253 | TC11 |
| `Complex.ofReal_re` / `add_re` / `mul_I_re` | Data/Complex/Basic.lean:88 / :169 / :266 | TC7 |

---

## Obligation register

| ID | Statement | Severity | Content | Fallback recorded |
|---|---|---|---|---|
| **TC-BB** | TC8 | **HIGH** | `hB` discharge: strip is non-compact, so boundedness transports through the compact annulus; `∘`-associativity of `norm ∘ (f ∘ exp)` vs `(norm ∘ f) ∘ exp` is defeq-not-syntactic, stacked on `Set.image_comp` orientation and set-builder membership | yes (upperBounds mem-chase avoiding `image_comp`; the "bound on the strip directly" route is pre-rejected as impossible) |
| TC-SURJ | TC7 | MEDIUM | exp-surjectivity onto the circle: explicit witness `Real.log r + z.arg * I`; coercion chain `← ofReal_exp` → `exp_log` → `← hz` under `Complex.ofReal`; re-computation simp set | yes (congrArg/push_cast; whole-leg simp) |
| TC-PERIOD | TC8 | MEDIUM | periodicity bookkeeping: :607's boundary hypotheses range over the whole `2πI`-periodic line; discharge is pointwise line→circle via `norm_exp`+`exp_log`; never invert `exp` | yes (`simp only [mem_preimage, mem_singleton_iff]` preprocessing; inversion attempt = death condition 3) |
| TC-CL | TC8 | MEDIUM | `closure (verticalStrip l u) = verticalClosedStrip l u` is assembled, not pinned: `closure_preimage_re` + `closure_Ioo hul.ne`; needs the strict `l < u`, hence `r₁ < r₃` | yes (`simp only`/`unfold` for the def-unfolds) |
| TC-EVAL | TC8 | MEDIUM | final rewrite chain `comp_apply, hwexp, hwre` must clear `w` completely; both exponent occurrences of `w.re` rewritten; result must be the goal literally | yes (`simp only [Function.comp_apply] at key`); occurrence audit recorded |
| TC-SUP | TC9 | MEDIUM | `Real.sSup_le` (protected) needs RHS `≥ 0` (junk-safety of bare `sSup`); `rintro … rfl` leaves `(norm ∘ f) z` head; `▸` transport direction in `hsub` | yes (`Function.comp_apply` simp; `.symm ▸` / `rw` fallback) |
| TC-DCOC | TC8 | LOW | `DiffContOnCl` fields protected; anonymous constructor; `rw [hcl]` inside the second component | yes (as written; `DifferentiableOn.diffContOnCl` route via :39 if constructor fights) |
| TC-EXP-MONO | TC5, TC6 | LOW | `exp_le_exp`/`exp_lt_exp` iff-direction; `exp_log` endpoints | yes (`gcongr` — the pin tags the log/exp monotonicity lemmas `@[gcongr]`) |
| TC-SPH | TC1, TC4, TC9, TC11 | LOW | sphere-set vs `‖w‖ = r` binder bridge, `mem_sphere_zero_iff_norm` | yes (`dist_zero_right` simp route) |
| TC-COMP | TC3, TC4 | LOW | `norm ∘ f` vs `fun x => ‖f x‖` unification at `bddAbove_image`/`le_csSup` | yes (`show`/`simpa [Function.comp]`) |
| TC-ALG | TC10 | LOW | all log-algebra quarantined here: two `log_div` rewrites + `field_simp` with `hne` | yes (append `ring`) |
| TC-RPOW | TC11 | LOW | `rpow_add'` needs `0 ≤ M` and `(1-t)+t ≠ 0`; `set` abbreviation vs `sub_add_cancel` | yes (inline `t`; `simp`) |
| TC-NONNEG | TC11 | LOW | (informational) `0 ≤ M` is derived from sphere nonemptiness, not assumed; do not add it as a hypothesis | n/a |

No obligation is analytic. Every analytic input — the three-lines
interpolation itself, `exp`'s differentiability, the modulus formula
`‖exp w‖ = e^{w.re}`, the polar decomposition, compactness of closed balls in
ℂ — is a quoted pinned theorem at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.
There is **no repo prerequisite**: nothing here imports or mentions
`ResearchOS`, ξ, ζ, or any repo theorem. Nothing here is claimed proved until
the kernel checks it in a built PR after independent review.

### Deferred items (explicitly out of this package)

- **TC-DEFERRED-1 — an annulus `Set` abbreviation.** Would be a second `def`
  for pure notation, flagged reviewer-sensitive in `UPSTREAM_POOL.md` §3.3.
  If this surface goes upstream, the Mathlib review decides the spelling;
  this contract keeps set-builder literals (death condition 4 guards the
  drift).
- **TC-DEFERRED-2 — `ConvexOn` packaging of `x ↦ log (sSupNormCircle f
  (Real.exp x))`.** Strictly more statement mass (convexity API, `log` of a
  sup, domain plumbing) for zero additional interpolation content; the
  three-point inequality TC9 *is* the log-convexity. Revisit only if an
  upstream reviewer asks for it.
- **TC-DEFERRED-3 — three-circles for `sSupNormIm`-style `sSup` over
  *open-annulus interior* radii, Hardy convexity, or `p`-mean versions.**
  Different theorems, different inputs (subharmonicity); not this reduction.

---

## Claim boundary

**What this contract is.** A statement surface for the classical Hadamard
three-circles theorem as an exp-transport of the pinned three-lines theorem,
with every dependency spelled at
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. It is the promised elaboration of
`UPSTREAM_POOL.md` §3, whose locators and difficulty assessment were
**re-verified against the tree this session** (all §3.2 locators check out;
§3.1's ratio-form signature is demoted to corollary TC10 in favor of the
rewrite-free raw form, and the §3.3 "hardest step" call is confirmed and
sharpened to obligation TC-BB).

**What this contract is NOT.**

- **It closes no barrier.** No row of `MATHLIB_CAPABILITY_MAP.md` names
  three-circles as exit evidence; the map's §0-adjacent absences
  (`three.circle` 0 files, annulus 0 lines — re-verified) describe *cost*,
  and per the standing rule (MULTIPLICITY finding A4, death condition 9
  there), generic pinned machinery — which is all this package is — **never
  retires a row**. Stage-one acceptance changes no barrier row; even a
  stage-two kernel-checked build would change none.
- **It selects no route and is not route work.** The RH queue's sole ACTIVE
  task is `RH-011` (acceptance-only review of `ZERO_SET_SLICE_CONTRACT.md`;
  no built module, no kernel verdict); the ECDLP decision substrate
  selects no route. This document is an offered artifact under the upstream
  pool, prepared so that *if* a future dated decision wants three-circles,
  the statement surface is already reviewed. It must not be cited as momentum
  toward any route.
- **No RH-truth claim.** The statements bound moduli of arbitrary analytic
  functions on annuli. They mention no L-function and carry no information
  about the location of anyone's zeros. This package supplies neither
  evidence for nor against RH and must not be described as progress toward
  it.
- **No growth-order content.** "Log-convexity of circle sups" is a *local*
  interpolation statement on a fixed compact annulus. It is not a growth
  order, not a Jensen inequality, not a counting bound, and it must not be
  dressed up as a step toward Hadamard factorization (`UPSTREAM_POOL.md` §0
  row 3's canonical-product absence is untouched).
- **No claim of Mathlib acceptance.** "Upstream-shaped" means the statements
  avoid repo-local objects; whether Mathlib wants them, and in what spelling
  (see TC-DEFERRED-1), is a decision owned by a Mathlib review, not by this
  contract.
- **Nothing is kernel-checked.** Every skeleton above is a proof *sketch*
  with pre-registered fallbacks, exactly as fragile as its obligation row
  says. The one invariant stands: a statement exists in this repository's
  proved layer only when CI's kernel check accepts it, and no statement here
  is in that layer.

---

## Death conditions

Stop and re-plan — do **not** patch around — if any of the following occurs.

1. **A new axiom would be needed.** No `axiom`, no `sorry`, no `admit`, no
   `native_decide` on an unproved side condition. The Lean kernel is the sole
   verifier.
2. **Any dependency on an unproved conjecture**, including as a hypothesis
   smuggled into a binder.
3. **A branch of `log` (any section of `exp`) becomes load-bearing.** The
   design point of the reduction is that `f ∘ exp` needs `MapsTo` and one
   explicit preimage witness (TC7), never an inverse of `exp` on a set. If a
   proof attempt starts selecting preimages along the boundary lines or
   constructing `Complex.log`-based charts, the formulation has drifted;
   stop. (This is the failure mode TC-PERIOD pre-registers.)
4. **A second `def` is proposed.** The package budget is exactly one `def`
   (TC1). An annulus `Set` object, a `ConvexOn` wrapper, or any structure
   with a proof-carrying field is out of contract (TC-DEFERRED-1/2); needing
   one signals either scope creep or an upstream-review decision that is not
   ours to preempt.
5. **A statement is proposed at `r₁ = 0` (or with `0 < r₁` dropped).**
   `Real.log 0 = 0` (Log/Basic.lean:102) makes every exponent silently junk,
   `hul` fails, and the "annulus" is a punctured disc whose three-circles
   statement is a *different theorem* (removable-singularity content). A
   junk-value-riding generalization is false-shaped, not stronger.
6. **`[CompleteSpace E]` creeps in.** The pinned three-lines needs only
   `[NormedAddCommGroup E] [NormedSpace ℂ E]` (Hadamard.lean:237/:396); every
   TC statement is spelled at that generality. A route that demands
   completeness is the wrong route.
7. **`hB` gets discharged by boundedness on the strip.** The strip is
   unbounded; any "direct" boundedness there is either wrong or secretly
   re-proving the annulus transport. Use the TC-BB route or its recorded
   fallback only.
8. **A barrier row or route authorization is inferred from this contract.**
   The RH queue (`tasks/RIEMANN_HYPOTHESIS.md`, `RH-011` sole ACTIVE) is the
   lane authority; `repo/ECDLP_DECISION_SUBSTRATE.json` governs the other
   lane and selects no route. This contract is a statement design. Declaring
   any capability-map row stale on the strength of this generic package is
   itself a death condition (the MULTIPLICITY finding-A4 rule, inherited
   verbatim).

---

*End of contract. 11 signatures (1 def + 10 theorems), 13 obligation rows,
zero repo prerequisites, zero kernel verdicts.*
