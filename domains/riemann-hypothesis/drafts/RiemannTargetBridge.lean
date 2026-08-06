/-
NON-BUILT DRAFT — route-neutral RH target bridge.

This file implements the frozen contract
`domains/riemann-hypothesis/TARGET_BRIDGE_CONTRACT.md` (DRAFT v2, 2026-08-05),
declarations P1-P5. It is NOT part of any lake target: it must not be imported
from `Ecdlp.lean` or any built module. RH-003 review is complete, and the
synchronized built counterpart landed in PR #299 (`288d65b`) after a green
kernel build, no-sorry gate, and per-row axiom audit. This reference copy
remains outside every lake target and is kept synchronized with that built
module.

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0).
Every cited lemma name and signature below was grep-verified at that exact
revision. Obligations discharged inline: P1-c (field cancellation), P1-d
(ℤ→ℕ→ℂ witness casts), P2-a/P4-a (real-part cast forms), P3-a (simp closure
of the ∨-iff), P4-b/P5-a (`RiemannHypothesis` def unfolding via `show`).
-/
import Mathlib.NumberTheory.LSeries.ZetaZeros          -- riemannZetaZeros, Nonvanishing (transitively)
import Mathlib.NumberTheory.Harmonic.ZetaAsymp          -- riemannZeta_one, riemannZeta_one_ne_zero
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Complex  -- Complex.cos_eq_zero_iff

open Complex
open scoped Real

/-! ## P1. Lower exclusion: no zeros in `re ≤ 0` except the trivial ones -/

theorem riemannZeta_ne_zero_of_re_le_zero {s : ℂ} (hs : s.re ≤ 0)
    (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) : riemannZeta s ≠ 0 := by
  rcases eq_or_ne s 0 with rfl | hs0
  · -- totalized value at 0: `ζ(0) = -1/2 ≠ 0` (RiemannZeta.lean:149)
    rw [riemannZeta_zero]
    norm_num
  · have hw_re : 1 ≤ (1 - s).re := by
      rw [Complex.sub_re, Complex.one_re]
      linarith
    -- hypothesis `hs` of `riemannZeta_one_sub`, instantiated at `s := 1 - s`, by real parts
    have hw_nat : ∀ n : ℕ, (1 : ℂ) - s ≠ -n := by
      intro n h
      have h' := congrArg Complex.re h
      rw [Complex.sub_re, Complex.one_re, Complex.neg_re, Complex.natCast_re] at h'
      have hn : (0 : ℝ) ≤ n := Nat.cast_nonneg (α := ℝ) n
      linarith
    -- hypothesis `hs'` of `riemannZeta_one_sub` at `s := 1 - s`
    have hw_ne_one : (1 : ℂ) - s ≠ 1 := fun h => hs0 (by linear_combination -h)
    have hFE := riemannZeta_one_sub hw_nat hw_ne_one
    rw [show (1 : ℂ) - (1 - s) = s by ring] at hFE
    rw [hFE]
    refine mul_ne_zero (mul_ne_zero (mul_ne_zero (mul_ne_zero two_ne_zero ?_) ?_) ?_) ?_
    · -- `(2 * π) ^ (-(1 - s)) ≠ 0`: cpow vanishes only for base 0 (Pow/Complex.lean:45,49)
      exact Complex.cpow_ne_zero_iff.mpr
        (Or.inl (mul_ne_zero two_ne_zero (Complex.ofReal_ne_zero.mpr Real.pi_ne_zero)))
      -- alternate: simp only [ne_eq, Complex.cpow_eq_zero_iff, not_and_or, not_not];
      --   exact Or.inl (mul_ne_zero two_ne_zero (Complex.ofReal_ne_zero.mpr Real.pi_ne_zero))
    · -- `Gamma (1 - s) ≠ 0` since `re (1 - s) ≥ 1 > 0` (Beta.lean:453; fix F1)
      exact Complex.Gamma_ne_zero_of_re_pos (one_pos.trans_le hw_re)
    · -- `cos (π * (1 - s) / 2) ≠ 0`: the only genuine vanishing channel
      intro hcos
      obtain ⟨k, hk⟩ := Complex.cos_eq_zero_iff.mp hcos
      -- hk : ↑π * (1 - s) / 2 = (2 * ↑k + 1) * ↑π / 2
      have hpi : (π : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr Real.pi_ne_zero
      -- OBLIGATION P1-c: cancel the 2 and the π, in that order
      have h2 : (π : ℂ) * (1 - s) = (2 * (k : ℂ) + 1) * (π : ℂ) := by
        linear_combination 2 * hk
      have h3 : (1 : ℂ) - s = 2 * (k : ℂ) + 1 :=
        mul_left_cancel₀ hpi (by linear_combination h2)
        -- orientation check: `mul_left_cancel₀` wants `π * (1 - s) = π * (2*k + 1)`;
        -- `linear_combination h2` commutes the RHS of h2 into that shape
      have hs_eq : s = -2 * (k : ℂ) := by linear_combination -h3
      -- OBLIGATION P1-d: real part forces `0 ≤ k`; `s ≠ 0` forces `k ≠ 0`; hence `1 ≤ k`
      have hk_re : s.re = -2 * (k : ℝ) := by
        rw [hs_eq]
        simp [Complex.mul_re, Complex.intCast_re, Complex.intCast_im]
        -- alternate: rw [show ((-2 : ℂ) * (k : ℂ)) = (((-2 * (k : ℝ) : ℝ)) : ℂ) by
        --   push_cast; ring, Complex.ofReal_re]
      have hk0 : 0 ≤ k := by
        by_contra hneg
        push_neg at hneg
        have hkR : (k : ℝ) < 0 := by exact_mod_cast hneg
        have hpos : (0 : ℝ) < s.re := by rw [hk_re]; nlinarith
        linarith
      have hkne : k ≠ 0 := by                                   -- fix F2
        rintro rfl
        exact hs0 (by simpa using hs_eq)
      have hk1 : 1 ≤ k := by omega
      -- produce the exact trivial-zero witness `n := (k - 1).toNat`
      refine htriv ⟨(k - 1).toNat, ?_⟩
      rw [hs_eq, show (((k - 1).toNat : ℕ) : ℂ) = (k : ℂ) - 1 by
        rw [← Int.cast_natCast, Int.toNat_of_nonneg (by omega : (0 : ℤ) ≤ k - 1)]
        push_cast
        ring]
      ring
      -- (P1-d, first CI round: the primary `push_cast [Int.toNat_of_nonneg ...]`
      -- left `-(↑k * 2) = -2 - ↑(-1 + k).toNat * 2` unsolved — the ℕ→ℂ cast did
      -- not route through the ℤ-level lemma; this explicit-rewrite form is the
      -- audit-verified alternate, promoted to primary.)
    · -- `ζ(1 - s) ≠ 0` on the closed half-plane `re ≥ 1` (Nonvanishing.lean:410,
      -- strict-implicit ⦃s⦄ instantiated by the explicit argument)
      exact riemannZeta_ne_zero_of_one_le_re hw_re

/-! ## P2. Critical-strip localization of nontrivial zeros -/

theorem riemannZeta_zero_mem_critical_strip {s : ℂ} (hz : riemannZeta s = 0)
    (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) : 0 < s.re ∧ s.re < 1 := by
  constructor
  · by_contra h
    exact riemannZeta_ne_zero_of_re_le_zero (not_lt.mp h) htriv hz
  · by_contra h
    exact riemannZeta_ne_zero_of_one_le_re (not_lt.mp h) hz

/-- The line `re = 0` carries no zeta zeros at all (records the exact `re = 0`
treatment; the trivial-zero exclusion discharges itself since
`re (-2*(n+1)) = -(2*n+2) ≠ 0`). -/
theorem riemannZeta_ne_zero_of_re_eq_zero {s : ℂ} (hs : s.re = 0) : riemannZeta s ≠ 0 :=
  riemannZeta_ne_zero_of_re_le_zero hs.le (by
    rintro ⟨n, rfl⟩
    -- OBLIGATION P2-a: exact cast form of the real part
    rw [show ((-2 : ℂ) * ((n : ℂ) + 1)).re = -2 * ((n : ℝ) + 1) by
      simp [Complex.mul_re, Complex.natCast_re, Complex.natCast_im]] at hs
      -- alternate: rw [show ((-2 : ℂ) * ((n : ℂ) + 1)) = (((-2 * ((n : ℝ) + 1) : ℝ)) : ℂ) by
      --   push_cast; ring, Complex.ofReal_re]
    nlinarith [Nat.cast_nonneg (α := ℝ) n])                     -- fix F3

/-! ## P3. Reflection of zeros inside the strip -/

theorem riemannZeta_one_sub_eq_zero_iff {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    riemannZeta (1 - s) = 0 ↔ riemannZeta s = 0 := by
  have hs0 : s ≠ 0 := fun h => by simp [h] at h0
  have hs0' : (1 : ℂ) - s ≠ 0 := fun h => by
    have h' := congrArg Complex.re h
    rw [Complex.sub_re, Complex.one_re, Complex.zero_re] at h'
    linarith
  have hG : Gammaℝ s ≠ 0 := Complex.Gammaℝ_ne_zero_of_re_pos h0
  have hG' : Gammaℝ (1 - s) ≠ 0 := Complex.Gammaℝ_ne_zero_of_re_pos
    (by rw [Complex.sub_re, Complex.one_re]; linarith)
  rw [riemannZeta_def_of_ne_zero hs0', riemannZeta_def_of_ne_zero hs0,
    completedRiemannZeta_one_sub, div_eq_zero_iff, div_eq_zero_iff]
  -- OBLIGATION P3-a: both sides are now `completedRiemannZeta s = 0 ∨ Gammaℝ _ = 0`
  simp [hG, hG']
  -- alternate: rw [or_iff_left hG', or_iff_left hG]

/-! ## P4. Half-plane equivalence (strongest clean form) -/

theorem riemannHypothesis_iff_zero_free_gt_half :
    RiemannHypothesis ↔ ∀ s : ℂ, 1 / 2 < s.re → riemannZeta s ≠ 0 := by
  constructor
  · -- forward: RH ⟹ zero-free on the open half-plane `re > 1/2`
    intro hRH s hs hz
    have htriv : ¬∃ n : ℕ, s = -2 * (n + 1) := by
      rintro ⟨n, rfl⟩
      -- OBLIGATION P4-a: same cast computation as P2-a
      rw [show ((-2 : ℂ) * ((n : ℂ) + 1)).re = -2 * ((n : ℝ) + 1) by
        simp [Complex.mul_re, Complex.natCast_re, Complex.natCast_im]] at hs
      nlinarith [Nat.cast_nonneg (α := ℝ) n]                    -- fix F3
    have hs1 : s ≠ 1 := by rintro rfl; exact riemannZeta_one_ne_zero hz
    have h := hRH s hz htriv hs1
    rw [h] at hs
    exact lt_irrefl _ hs
  · -- reverse: uses P2 (strip) + P3 (reflection); no conjugation symmetry anywhere
    intro hfree
    -- OBLIGATION P4-b: `RiemannHypothesis` is a def; unfold it explicitly via `show`
    show ∀ (s : ℂ) (_ : riemannZeta s = 0) (_ : ¬∃ n : ℕ, s = -2 * (n + 1)) (_ : s ≠ 1),
      s.re = 1 / 2
    intro s hz htriv _hs1
    obtain ⟨h0, h1⟩ := riemannZeta_zero_mem_critical_strip hz htriv
    by_contra hne
    rcases lt_or_gt_of_ne hne with hlt | hgt
    · -- `s.re < 1/2`: reflect across the line; `1 - s` has `re > 1/2`
      have hz' : riemannZeta (1 - s) = 0 :=
        (riemannZeta_one_sub_eq_zero_iff h0 h1).mpr hz
      exact hfree (1 - s) (by rw [Complex.sub_re, Complex.one_re]; linarith) hz'
    · exact hfree s hgt hz

/-! ## P5. Critical-line equivalence via the zero-set object -/

/-- Free translation fact: `1` is not in the zero set (its totalized value is
nonzero, ZetaAsymp.lean:431). -/
theorem one_notMem_riemannZetaZeros : (1 : ℂ) ∉ riemannZetaZeros :=
  fun h => riemannZeta_one_ne_zero (mem_riemannZetaZeros.mp h)

theorem riemannHypothesis_iff_zetaZeros_re_eq_half :
    RiemannHypothesis ↔
      ∀ s ∈ riemannZetaZeros, (¬∃ n : ℕ, s = -2 * (n + 1)) → s.re = 1 / 2 := by
  constructor
  · intro hRH s hmem htriv
    have hz : riemannZeta s = 0 := mem_riemannZetaZeros.mp hmem
    have hs1 : s ≠ 1 := by rintro rfl; exact riemannZeta_one_ne_zero hz
    exact hRH s hz htriv hs1
  · intro h
    -- OBLIGATION P5-a: same def unfolding as P4-b
    show ∀ (s : ℂ) (_ : riemannZeta s = 0) (_ : ¬∃ n : ℕ, s = -2 * (n + 1)) (_ : s ≠ 1),
      s.re = 1 / 2
    intro s hz htriv _hs1
    exact h s (mem_riemannZetaZeros.mpr hz) htriv

/-- Literal source-side form ("all nontrivial zeros lie on the line", with both
exclusions); the `s ≠ 1` conjunct is redundant by `one_notMem_riemannZetaZeros`. -/
theorem riemannHypothesis_iff_zetaZeros_re_eq_half' :
    RiemannHypothesis ↔
      ∀ s ∈ riemannZetaZeros, (¬∃ n : ℕ, s = -2 * (n + 1)) ∧ s ≠ 1 → s.re = 1 / 2 := by
  rw [riemannHypothesis_iff_zetaZeros_re_eq_half]
  constructor
  · exact fun h s hmem ⟨htriv, _⟩ => h s hmem htriv
  · intro h s hmem htriv
    exact h s hmem ⟨htriv, fun e => one_notMem_riemannZetaZeros (e ▸ hmem)⟩
