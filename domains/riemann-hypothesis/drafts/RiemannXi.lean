/-
NON-BUILT DRAFT — RH xi package (safe entire normalization), statements X1–X11.

This file implements the frozen contract
`domains/riemann-hypothesis/XI_PACKAGE_CONTRACT.md` (DRAFT v2, 2026-08-05),
with the adversarial-review fixes F1–F3 folded in
(F1: `DifferentiableAt.comp` WITHOUT an explicit point argument, per the pinned
signature at FDeriv/Comp.lean:127; F2: every X5 field-algebra variant clears
denominators under `hs0`/`hs1` — never a bare `linear_combination` over
inverses; F3: the registered X11 defeq shapes, discharged at X11's `hstrip`,
`hGdiff`, and `hu`).

It is NOT part of any lake target: it must not be imported from `Ecdlp.lean`
or any built module. S0-TRUST was satisfied by PR #298; this draft remains
pending independent review and the RH-004 built-promotion gate carried from
`TARGET_BRIDGE_CONTRACT.md`.
The Lean kernel has NOT checked this file; nothing in it is claimed proved
until a built PR is kernel-verified.

SIBLING DEPENDENCY (bridge package): this file requires
`domains/riemann-hypothesis/drafts/RiemannTargetBridge.lean` (bridge P1–P5)
in the same eventual module or as an import — the built PR imports the built
bridge module; since both drafts are non-built, this file is written as if it
begins with the bridge file's content already available, and references the
bridge theorem by name as if in scope (it is NOT re-proved here).
The X10 reverse direction uses bridge P2, whose statement is exactly:

  theorem riemannZeta_zero_mem_critical_strip {s : ℂ} (hz : riemannZeta s = 0)
      (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) : 0 < s.re ∧ s.re < 1

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0).
Every cited lemma name and signature below was grep-verified at that exact
revision this session. Obligations discharged inline: X2-a (id/Pi vs lambda
defeq shapes), X4-a (endpoint `norm_num` set), X5-a (denominator-clearing
field algebra per fix F2), X6-a (ℕ→ℂ witness cast and the `n = 0` branch),
X7-a/X10-a (real-part cast form, shared discharge with bridge P2-a/P4-a),
X10-b (`RiemannHypothesis` def unfolding via `show`, as bridge P4-b/P5-a),
X11-G (assembly of `Gammaℝ` differentiability from pinned parts — no pinned
`Gammaℝ` differentiability lemma exists, only `differentiable_Gammaℝ_inv`),
X11-a (`z / 2 ≠ -m` re-computed via `Complex.div_ofNat_re`,
Data/Complex/Basic.lean:763), X11-b (defeq shapes per fix F3).
-/
import Mathlib.NumberTheory.LSeries.ZetaZeros              -- riemannZeta API (transitively RiemannZeta.lean)
import Mathlib.NumberTheory.Harmonic.ZetaAsymp             -- riemannZeta_one_ne_zero (X7 design note)
import Mathlib.Analysis.Analytic.Order                     -- analyticOrderAt API (X11)
import Mathlib.Analysis.SpecialFunctions.Gamma.Deriv       -- Complex.differentiableAt_Gamma (X11)
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv         -- DifferentiableAt.const_cpow (X11)
import Mathlib.Analysis.Complex.CauchyIntegral             -- DifferentiableOn.analyticAt (X11)
-- + the built bridge module providing P1–P5 (`riemannZeta_zero_mem_critical_strip`);
--   non-built here — see the header comment. The eventual built PR imports it.

open Complex Filter
open scoped Real Topology

/-! ## X1. Definition

The Gate-0 / Annex-A normalization, verbatim: total, entire-by-construction,
no exceptional points. `completedRiemannZeta₀` is the pinned pole-removed
completion (RiemannZeta.lean:63). This does not restate or replace
`RiemannHypothesis`. -/

/-- The safe entire Riemann xi function: `ξ(s) = (1 + s(s−1)Λ₀(s)) / 2`,
where `Λ₀ = completedRiemannZeta₀`. Entire (X2), symmetric under `s ↦ 1 − s`
(X3), with `ξ(0) = ξ(1) = 1/2` (X4), zeros exactly the nontrivial zeta zeros
(X6, X9), and zeta's local analytic order inside the open strip (X11). -/
noncomputable def riemannXi (s : ℂ) : ℂ :=
  (1 + s * (s - 1) * completedRiemannZeta₀ s) / 2

/-! ## X2. Entirety -/

theorem differentiable_riemannXi : Differentiable ℂ riemannXi := by
  unfold riemannXi
  exact ((differentiable_const _).add
      ((differentiable_id.mul (differentiable_id.sub (differentiable_const _))).mul
        differentiable_completedZeta₀)).div_const _
  -- LOWCONF: OBLIG X2-a — `differentiable_id` is stated for `(id : E → E)` and
  -- `Differentiable.add`/`.sub`/`.mul` for Pi-operations, matched against the lambda
  -- only up to defeq (no `differentiable_id'` at the pin); alternate: pointwise
  -- `fun s => ((differentiableAt_const _).add (((differentiableAt_id.mul
  -- (differentiableAt_id.sub (differentiableAt_const _))).mul
  -- (differentiable_completedZeta₀ s)))).div_const _`, or the `@[to_fun]`-generated
  -- `Differentiable.fun_add`/`fun_mul`/`fun_sub` lambda forms.

/-! ## X3. Functional equation -/

theorem riemannXi_one_sub (s : ℂ) : riemannXi (1 - s) = riemannXi s := by
  unfold riemannXi
  rw [completedRiemannZeta₀_one_sub]
  ring

/-! ## X4. Endpoint values

Both values are read off the entire formula — `Λ` and `Gammaℝ` never appear —
per the `SOURCE_CONTRACTS.md` shared-notation requirement. X4 is also the
built-in sign self-check for the §Sign-derivation constant `+1`. -/

theorem riemannXi_zero : riemannXi 0 = 1 / 2 := by
  unfold riemannXi
  norm_num
  -- OBLIG X4-a: `0 * (0 - 1) * Λ₀ 0 = 0` via `zero_mul` inside norm_num's simp set;
  -- alternate: `simp [riemannXi]`.

theorem riemannXi_one : riemannXi 1 = 1 / 2 := by
  unfold riemannXi
  norm_num
  -- OBLIG X4-a: `(1 - 1) = 0`, then `mul_zero`/`zero_mul`; alternate: `simp [riemannXi]`.

/-! ## X5. Off-endpoint equality with `s(s−1)Λ(s)/2`

Sign source of truth: `completedRiemannZeta_eq` the THEOREM (RiemannZeta.lean:84),
`Λ(s) = Λ₀(s) − 1/s − 1/(1−s)`; the conflicting module comment is never used.
The exclusions `hs0`, `hs1` are exactly the denominators' nonvanishing. -/

theorem riemannXi_eq_of_ne {s : ℂ} (hs0 : s ≠ 0) (hs1 : s ≠ 1) :
    riemannXi s = s * (s - 1) * completedRiemannZeta s / 2 := by
  have h1s : (1 : ℂ) - s ≠ 0 := sub_ne_zero.mpr (Ne.symm hs1)
  unfold riemannXi
  rw [completedRiemannZeta_eq]
  -- goal: (1 + s*(s-1)*Λ₀ s)/2 = s*(s-1)*(Λ₀ s - 1/s - 1/(1-s))/2
  field_simp
  ring
  -- LOWCONF: OBLIG X5-a — the `field_simp` normal form is version-sensitive (same
  -- class as bridge P1-c) and could in principle close the goal itself, orphaning
  -- `ring`. Review fix F2: NO variant may be a bare `linear_combination` over
  -- inverses (inverses are atoms to `ring`); every variant must clear the
  -- denominators under `hs0`/`h1s`. F2-compliant alternate:
  --   have h1 : s * (s - 1) * (1 / s) = s - 1 := by
  --     rw [mul_one_div, mul_comm s (s - 1), mul_div_assoc, div_self hs0, mul_one]
  --   have h2 : s * (s - 1) * (1 / (1 - s)) = -s := by
  --     rw [mul_one_div, show s - 1 = -(1 - s) from by ring, mul_neg, neg_div,
  --       mul_div_assoc, div_self h1s, mul_one]
  --   then close with: rw [completedRiemannZeta_eq, mul_sub, mul_sub, h1, h2]; ring
  --   (second review, F-X5-ORPHAN-RING: a `linear_combination` closer is NOT
  --   admissible here; and if `field_simp` closes the goal itself, drop the
  --   trailing `ring` — 'no goals' error otherwise)

/-! ## X6. Exact zero correspondence

Set-coverage (the reverse direction's load-bearing step): the `Gammaℝ` zero
set `{-(2n) | n : ℕ}` decomposes exactly once as `{0} ∪ {-2(m+1) | m : ℕ}`;
`hs0` covers the first component (trivial zeros start at `−2`, so `htriv`
does NOT cover `0`) and `htriv` the second. Neither exclusion is redundant
and neither may be weakened — the `S0-SEMANTIC` boundary item. -/

theorem riemannXi_eq_zero_iff_riemannZeta_eq_zero {s : ℂ} (hs0 : s ≠ 0) (hs1 : s ≠ 1)
    (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) :
    riemannXi s = 0 ↔ riemannZeta s = 0 := by
  -- Gammaℝ s ≠ 0 under exactly the stated exclusions (set coverage above)
  have hG : Gammaℝ s ≠ 0 := by
    rw [Ne, Complex.Gammaℝ_eq_zero_iff]
    rintro ⟨n, rfl⟩
    cases n with
    -- (`cases` substitutes in `hs0`/`htriv`, unlike a tactic-`match` on the goal alone)
    | zero => exact hs0 (by norm_num)
      -- LOWCONF: OBLIG X6-a `n = 0` branch — `-(2 * ((0 : ℕ) : ℂ)) = 0` must be
      -- closed with `Nat.zero`-shaped cast after `cases`; alternate: `by simp`.
    | succ m => exact htriv ⟨m, by push_cast; ring⟩
      -- OBLIG X6-a witness cast: `-(2 * (↑(m + 1) : ℂ)) = -2 * (↑m + 1)`.
  have hs1' : s - 1 ≠ 0 := sub_ne_zero.mpr hs1
  rw [riemannXi_eq_of_ne hs0 hs1,                            -- X5
      riemannZeta_def_of_ne_zero hs0,                        -- ζ = Λ / Gammaℝ, only under s ≠ 0
      div_eq_zero_iff, div_eq_zero_iff]
  -- LHS: s*(s-1)*Λ s = 0 ∨ (2:ℂ) = 0 ; RHS: Λ s = 0 ∨ Gammaℝ s = 0
  constructor
  · rintro (h | h)
    · rcases mul_eq_zero.mp h with h' | hΛ
      · rcases mul_eq_zero.mp h' with h0 | h1
        · exact absurd h0 hs0
        · exact absurd h1 hs1'
      · exact Or.inl hΛ
    · exact absurd h two_ne_zero
  · rintro (hΛ | hGz)
    · exact Or.inl (by rw [hΛ, mul_zero])
    · exact absurd hGz hG

/-! ## X7. Nonvanishing on the closed right half-plane

`s = 1` is handled by the totalized-free value `riemannXi_one` (X4), so the
closed half-plane comes for free, mirroring the bridge's use of
`riemannZeta_ne_zero_of_one_le_re` (Nonvanishing.lean:410). -/

theorem riemannXi_ne_zero_of_one_le_re {s : ℂ} (hs : 1 ≤ s.re) : riemannXi s ≠ 0 := by
  rcases eq_or_ne s 1 with rfl | hs1
  · rw [riemannXi_one]; norm_num                               -- 1/2 ≠ 0
  · have hs0 : s ≠ 0 := by
      rintro rfl; rw [Complex.zero_re] at hs; linarith
    have htriv : ¬∃ n : ℕ, s = -2 * (n + 1) := by
      rintro ⟨n, rfl⟩
      rw [show ((-2 : ℂ) * ((n : ℂ) + 1)).re = -2 * ((n : ℝ) + 1) by
        simp [Complex.mul_re, Complex.natCast_re, Complex.natCast_im]] at hs
        -- LOWCONF: OBLIG X7-a (= bridge P2-a/P4-a shared discharge) — exact simp
        -- closure of the `.re` computation; alternate:
        -- rw [show ((-2 : ℂ) * ((n : ℂ) + 1)) = (((-2 * ((n : ℝ) + 1) : ℝ)) : ℂ) by
        --   push_cast; ring, Complex.ofReal_re] at hs
      nlinarith [Nat.cast_nonneg (α := ℝ) n]
    intro hz
    exact riemannZeta_ne_zero_of_one_le_re hs
      ((riemannXi_eq_zero_iff_riemannZeta_eq_zero hs0 hs1 htriv).mp hz)

/-! ## X8. Nonvanishing on the closed left half-plane (covers all negative even points)

Pure reflection: `re s ≤ 0 ⟹ re (1−s) ≥ 1`, then X3 + X7. The `s = 0` case is
subsumed: the reflection lands on `1`, handled by X7 via `riemannXi_one`. -/

theorem riemannXi_ne_zero_of_re_le_zero {s : ℂ} (hs : s.re ≤ 0) : riemannXi s ≠ 0 := by
  intro hz
  refine riemannXi_ne_zero_of_one_le_re (s := 1 - s) ?_ ?_
  · rw [Complex.sub_re, Complex.one_re]; linarith
  · rw [riemannXi_one_sub]; exact hz

/-! ## X9. Xi-side critical-strip localization

Hypothesis-free — unlike the zeta-side bridge P2, no trivial-zero hypothesis
is needed: X8 excludes the entire closed left half-plane including the
trivial points (the point of the xi normalization). -/

theorem riemannXi_zero_mem_critical_strip {s : ℂ} (hz : riemannXi s = 0) :
    0 < s.re ∧ s.re < 1 := by
  constructor
  · by_contra h; exact riemannXi_ne_zero_of_re_le_zero (not_lt.mp h) hz
  · by_contra h; exact riemannXi_ne_zero_of_one_le_re (not_lt.mp h) hz

/-! ## X10. RH equivalence via xi zeros

Left side is `_root_.RiemannHypothesis` verbatim (RiemannZeta.lean:182); no
competing proposition. The xi side needs no exclusions — X9 makes every xi
zero automatically nontrivial, non-pole, non-zero-point. Both directions
route through X6 with all three exclusions PROVED, never assumed: forward
from X9, reverse from BRIDGE P2 (`riemannZeta_zero_mem_critical_strip`,
sibling draft `RiemannTargetBridge.lean` — see header). No conjugation
symmetry anywhere. -/

theorem riemannHypothesis_iff_riemannXi_zeros_re_eq_half :
    RiemannHypothesis ↔ ∀ s : ℂ, riemannXi s = 0 → s.re = 1 / 2 := by
  constructor
  · -- forward: RH ⟹ xi zeros on the line
    intro hRH s hz
    obtain ⟨h0, h1⟩ := riemannXi_zero_mem_critical_strip hz            -- X9
    have hs0 : s ≠ 0 := fun e => by simp [e] at h0
    have hs1 : s ≠ 1 := fun e => by simp [e] at h1
    have htriv : ¬∃ n : ℕ, s = -2 * (n + 1) := by
      rintro ⟨n, rfl⟩
      rw [show ((-2 : ℂ) * ((n : ℂ) + 1)).re = -2 * ((n : ℝ) + 1) by
        simp [Complex.mul_re, Complex.natCast_re, Complex.natCast_im]] at h0
        -- LOWCONF: OBLIG X10-a — same cast discharge as X7-a / bridge P2-a;
        -- alternate as in X7.
      nlinarith [Nat.cast_nonneg (α := ℝ) n]
    exact hRH s ((riemannXi_eq_zero_iff_riemannZeta_eq_zero hs0 hs1 htriv).mp hz) htriv hs1
  · -- reverse: xi-line condition ⟹ RH; strip localization comes from BRIDGE P2
    intro h
    -- OBLIG X10-b: `RiemannHypothesis` is a semireducible def; unfold via `show`
    -- (identical to bridge P4-b/P5-a).
    show ∀ (s : ℂ) (_ : riemannZeta s = 0) (_ : ¬∃ n : ℕ, s = -2 * (n + 1)) (_ : s ≠ 1),
      s.re = 1 / 2
    intro s hz htriv _hs1
    -- BRIDGE PREREQUISITE P2 (sibling draft, referenced by name; NOT pinned Mathlib):
    obtain ⟨h0, h1⟩ := riemannZeta_zero_mem_critical_strip hz htriv
    have hs0 : s ≠ 0 := fun e => by simp [e] at h0
    have hs1 : s ≠ 1 := fun e => by simp [e] at h1
    exact h s ((riemannXi_eq_zero_iff_riemannZeta_eq_zero hs0 hs1 htriv).mpr hz)

/-! ## X11. Analytic-order transport

On the open strip, `ξ(z) = (z(z−1)/2 · Gammaℝ z) · ζ(z)` with an analytic
nonvanishing cofactor, so `analyticOrderAt` transports by
`analyticOrderAt_congr` + `analyticOrderAt_mul` + the order-zero unit law.
The factorization is asserted ONLY on the open strip (a genuine `𝓝 s`
neighborhood — never at `0`, `1`, or a boundary point);
`riemannZeta_def_of_ne_zero` is used only under the proved `z ≠ 0`;
`Gammaℝ z ≠ 0` comes from `re z > 0`. Order transport only: no divisor is
constructed (`S1-MULTIPLICITY` boundary). -/

theorem analyticOrderAt_riemannXi_eq_riemannZeta {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannXi s = analyticOrderAt riemannZeta s := by
  have hs0 : s ≠ 0 := fun e => by simp [e] at h0
  have hs1 : s ≠ 1 := fun e => by simp [e] at h1
  -- (1) OBLIG X11-G: Gammaℝ is analytic on the open right half-plane, ASSEMBLED from
  --     pinned parts — no pinned `Gammaℝ` differentiability/analyticity lemma exists
  --     (only `differentiable_Gammaℝ_inv`, Deligne.lean:88, the wrong direction).
  have hHopen : IsOpen {z : ℂ | 0 < z.re} := isOpen_lt continuous_const Complex.continuous_re
  have hGdiff : DifferentiableOn ℂ Gammaℝ {z : ℂ | 0 < z.re} := by
    intro z hz
    have hzre : (0 : ℝ) < z.re := hz
    -- OBLIG X11-a: `z / 2` avoids every Gamma pole since `re (z / 2) > 0`
    have hz2 : ∀ m : ℕ, z / 2 ≠ -m := by
      intro m e
      have h := congrArg Complex.re e
      rw [Complex.div_ofNat_re, Complex.neg_re, Complex.natCast_re] at h
        -- LOWCONF: OBLIG X11-a — `rw` must match the `OfNat` literal `2` against
        -- `Complex.div_ofNat_re` (Data/Complex/Basic.lean:763, `[n.AtLeastTwo]`);
        -- alternate: `simp only [Complex.div_ofNat_re, Complex.neg_re,
        -- Complex.natCast_re] at h`.
      have hm : (0 : ℝ) ≤ m := Nat.cast_nonneg (α := ℝ) m
      linarith
    -- second review, F-X11-GAMMAR-DEFEQ: expose the product through the rfl-def
    -- ONCE via `suffices` (the pin's own differentiable_Gammaℝ_inv rewrites Gammaℝ
    -- before its constructor chain rather than relying on raw delta/Pi defeq)
    suffices h : DifferentiableAt ℂ
        (fun t : ℂ => (π : ℂ) ^ (-t / 2) * Complex.Gamma (t / 2)) z from
      h.differentiableWithinAt
    exact ((differentiableAt_id.neg.div_const 2).const_cpow
        (Or.inl (Complex.ofReal_ne_zero.mpr Real.pi_ne_zero))).mul
      ((Complex.differentiableAt_Gamma _ hz2).comp
        (differentiableAt_id.div_const 2))
      -- review fix F1: `DifferentiableAt.comp` takes NO explicit point at the pin
      -- (FDeriv/Comp.lean:127); lambda-shape alternative: `DifferentiableAt.fun_comp'`
      -- (FDeriv/Comp.lean:121, conclusion `fun x => g (f x)`).
      -- LOWCONF: OBLIG X11-b / fix F3 (b),(c) — `differentiableAt_id.neg` is the
      -- Pi-neg `(-id)` defeq-matched against the exponent `fun z => -z / 2` inside
      -- `const_cpow`, `.mul` is Pi-mul defeq-matched against the unfolded `Gammaℝ`
      -- body (`Gammaℝ_def` is `rfl`, Deligne.lean:45), and `g ∘ f` vs the lambda in
      -- the Gamma factor; the identical incantation elaborates at the pin inside
      -- `differentiable_Gammaℝ_inv` (Deligne.lean:88); alternate: prefix with
      -- `simp only [Complex.Gammaℝ_def]`-style `show`, and/or use
      -- `DifferentiableAt.fun_comp'`.
  have hG : AnalyticAt ℂ Gammaℝ s := hGdiff.analyticAt (hHopen.mem_nhds h0)
  -- (2) the nonvanishing analytic cofactor u = fun z => z * (z - 1) / 2 * Gammaℝ z
  have hu : AnalyticAt ℂ (fun z : ℂ => z * (z - 1) / 2 * Gammaℝ z) s :=
    ((analyticAt_id.mul (analyticAt_id.sub analyticAt_const)).div_const).mul hG
    -- LOWCONF: OBLIG X11-b — `analyticAt_id` is stated for `id`, `AnalyticAt.mul`/
    -- `.sub` for Pi-operations, `AnalyticAt.div_const` as `(f · / c)`; all matched
    -- against the lambda only up to defeq/eta; fallback (one stroke, avoiding the
    -- `AnalyticAt` constructor chain entirely): prove
    -- `DifferentiableOn ℂ (fun z => z * (z - 1) / 2 * Gammaℝ z) {z | 0 < z.re}`
    -- from the everywhere-differentiable polynomial part and `hGdiff`, then apply
    -- `DifferentiableOn.analyticAt` once with `hHopen.mem_nhds h0`.
  have hu_ne : (fun z : ℂ => z * (z - 1) / 2 * Gammaℝ z) s ≠ 0 :=
    mul_ne_zero (div_ne_zero (mul_ne_zero hs0 (sub_ne_zero.mpr hs1)) two_ne_zero)
      (Complex.Gammaℝ_ne_zero_of_re_pos h0)
  -- (3) zeta is analytic at s (s ≠ 1 inside the strip)
  have hζ : AnalyticAt ℂ riemannZeta s :=
    analyticOn_riemannZeta s (Set.mem_compl_singleton_iff.mpr hs1)
  -- (4) pointwise factorization on the OPEN strip, upgraded to a 𝓝 s eventual equality
  have hstrip : IsOpen {z : ℂ | 0 < z.re ∧ z.re < 1} :=
    (isOpen_lt continuous_const Complex.continuous_re).and
      (isOpen_lt Complex.continuous_re continuous_const)
    -- fix F3 (a) discharged syntactically: `IsOpen.and` (Topology/Basic.lean:116) is
    -- stated on set-builders `{x | p x ∧ q x}`, avoiding the `∩`-vs-set-builder
    -- defeq gap of `.inter` entirely.
  have hfac : riemannXi =ᶠ[𝓝 s]
      (fun z : ℂ => z * (z - 1) / 2 * Gammaℝ z) * riemannZeta := by
    filter_upwards [hstrip.mem_nhds ⟨h0, h1⟩] with z hz
    obtain ⟨hz0, hz1⟩ := hz
    have hz0' : z ≠ 0 := fun e => by simp [e] at hz0
    have hz1' : z ≠ 1 := fun e => by simp [e] at hz1
    have hGz : Gammaℝ z ≠ 0 := Complex.Gammaℝ_ne_zero_of_re_pos hz0
    have hΛ : completedRiemannZeta z = Gammaℝ z * riemannZeta z := by
      rw [riemannZeta_def_of_ne_zero hz0']                   -- only under proved z ≠ 0
      exact (mul_div_cancel₀ _ hGz).symm
    simp only [Pi.mul_apply]
    rw [riemannXi_eq_of_ne hz0' hz1', hΛ]                    -- X5
    ring
  -- (5) order arithmetic: congr, product law, unit factor of order zero
  rw [analyticOrderAt_congr hfac, analyticOrderAt_mul hu hζ,
    hu.analyticOrderAt_eq_zero.mpr hu_ne, zero_add]
