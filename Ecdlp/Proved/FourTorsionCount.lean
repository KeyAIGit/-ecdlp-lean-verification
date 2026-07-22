import Mathlib
import Ecdlp.Proved.FourTorsionBridge
import Ecdlp.Proved.TorsionPointCount
import Ecdlp.Proved.FourDivisionPolynomial

/-!
# A point-count bound for the 4-torsion of secp256k1 over `𝔽_p`

The even-index entry of the `#E[n]` counting family (`TorsionPointCount.lean`, which has the
odd `#E[3]≤9`, `#E[5]≤25`, `#E[7]≤49`). Using the point-level 4-torsion bridge
`secp256k1_four_nsmul_eq_zero_iff` (`4•P = 0 ⟺ ψ₄(P) = 0`) and the factorization
`ψ₄(P) = 4y·(x⁶+140x³−392)` (so `ψ₄(P) = 0 ⟺ y = 0 ∨ preΨ₄(x) = 0`), every `4`-torsion point's
`x`-coordinate is a root of `g := (X³+7)·preΨ₄` (degree `9`): the `y = 0` branch gives an `X³+7`
root (the 2-torsion `x`-locus), the `y ≠ 0` branch a `preΨ₄` root (the primitive-4-torsion locus,
`preΨ₄ = 2·(x⁶+140x³−392)`). Feeding this into the generic `≤ 2m+1` fiber bound
`secp256k1_torsion_ncard_le` (each `x` has `≤ 2` points on the curve, plus `O`) gives

  **`#E[4](𝔽_p) ≤ 2·9 + 1 = 19`.**

**Honest scope — this is the *generic* bound, not the tight count.** The exact value is
`#E[4] = 16 = 4²`: the generic `≤ 2m+1` over-counts because the `3` two-torsion `x`-coordinates
(`y = 0`) are *self-paired* — each carries one point, not the `±y` pair the bound assumes — so the
tight count is `1 + 3·1 + 6·2 = 16`, three below `19`. Closing that gap (a per-fiber refinement
distinguishing the `y = 0` locus, or the group-theoretic `#E[4] = #E[2]·#im[2] ≤ #E[2]²`) is the
next step; this file records only the clean generic bound. No new `native_decide` beyond the
`7 ≠ 0` / `2 ≠ 0` residue facts.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **`#E[4](𝔽_p) ≤ 19`** — secp256k1 has at most 19 four-torsion points (set form). The generic
`≤ 2m+1` fiber bound with `m = 9 = deg((X³+7)·preΨ₄)`; the tight value is `16` (see module
docstring: the three `y = 0` two-torsion points are self-paired). Even-index companion of the odd
`#E[3]≤9` / `#E[5]≤25` / `#E[7]≤49`. -/
theorem secp256k1_four_torsion_ncard_le :
    Set.ncard {P : secp256k1.toAffine.Point | (4 : ℕ) • P = 0} ≤ 19 := by
  classical
  haveI : NeZero Secp256k1.p := ⟨(Fact.out : Nat.Prime Secp256k1.p).pos.ne'⟩
  have h2ne : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
    simpa using this
  -- `g = (X³ + 7) · preΨ₄`: nonzero, degree `9`, so `≤ 9` distinct roots.
  set g : (ZMod Secp256k1.p)[X] := (X ^ 3 + C 7) * secp256k1.preΨ₄ with hg
  have hcubic_ne : (X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]) ≠ 0 := by
    intro hz
    have h7 : (7 : ZMod Secp256k1.p) ≠ 0 := by
      have : ((7 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
        rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
      simpa using this
    have h0 : (X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).eval 0 = 0 := by rw [hz, eval_zero]
    simp only [eval_add, eval_pow, eval_X, eval_C] at h0
    exact h7 (by linear_combination h0)
  have hg_ne : g ≠ 0 := mul_ne_zero hcubic_ne secp256k1_preΨ₄_ne_zero
  have hcubic_deg : (X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).natDegree = 3 := by compute_degree!
  have hg_deg : g.natDegree = 9 := by
    rw [hg, natDegree_mul hcubic_ne secp256k1_preΨ₄_ne_zero, hcubic_deg,
      secp256k1_preΨ₄_natDegree]
  have hcard : g.roots.toFinset.card ≤ 9 :=
    (Multiset.toFinset_card_le _).trans ((card_roots' _).trans (le_of_eq hg_deg))
  -- Every nonzero 4-torsion point has its `x` among the roots of `g`.
  have hmem : ∀ (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y),
      (4 : ℕ) • Point.some x y h = 0 → x ∈ g.roots.toFinset := by
    intro x y h ht
    have hcurve : y ^ 2 = x ^ 3 + 7 := secp256k1_curve_of_nonsingular x y h
    have hev := (secp256k1_four_nsmul_eq_zero_iff x y h).mp ht
    have hψ4 : (secp256k1.ψ 4).evalEval x y = 4 * y * (x ^ 6 + 140 * x ^ 3 - 392) := by
      rw [secp256k1.ψ_four]
      simp only [evalEval_mul, evalEval_C]
      rw [secp256k1_preΨ₄_eval, secp256k1_psi2_evalEval]
      ring
    rw [hψ4] at hev
    -- `4y·(x⁶+140x³−392) = 0`, so `y = 0` or `x⁶+140x³−392 = 0`; either forces `g.eval x = 0`.
    rw [Multiset.mem_toFinset, mem_roots']
    refine ⟨hg_ne, ?_⟩
    rw [hg, IsRoot.def, eval_mul, eval_add, eval_pow, eval_X, eval_C, secp256k1_preΨ₄_eval]
    -- goal: `(x³ + 7) * (2x⁶ + 280x³ − 784) = 0`
    have h4ne : (4 : ZMod Secp256k1.p) ≠ 0 := by
      rw [show (4 : ZMod Secp256k1.p) = 2 * 2 by norm_num]; exact mul_ne_zero h2ne h2ne
    rcases mul_eq_zero.mp hev with h4y | hω
    · rcases mul_eq_zero.mp h4y with h4 | hy0
      · exact absurd h4 h4ne
      · -- `y = 0` ⟹ `x³ + 7 = 0` (curve), so the first factor vanishes.
        have hx3 : x ^ 3 + 7 = 0 := by rw [← hcurve, hy0]; ring
        rw [hx3, zero_mul]
    · -- `x⁶+140x³−392 = 0` ⟹ `2x⁶+280x³−784 = 2·(…) = 0`, so the second factor vanishes.
      have hf2 : (2 * x ^ 6 + 280 * x ^ 3 - 784 : ZMod Secp256k1.p) = 0 := by
        linear_combination (2 : ZMod Secp256k1.p) * hω
      rw [hf2, mul_zero]
  have hbound := secp256k1_torsion_ncard_le 4 9 g.roots.toFinset hcard hmem
  simpa using hbound

end Ecdlp.Curve
