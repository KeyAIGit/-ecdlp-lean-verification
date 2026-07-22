import Mathlib
import Ecdlp.Proved.FourTorsionBridge
import Ecdlp.Proved.TorsionPointCount
import Ecdlp.Proved.FourDivisionPolynomial
import Ecdlp.Proved.AffinePointFinite
import Ecdlp.Proved.TwoTorsionCount

/-!
# The tight 4-torsion point count for secp256k1 over `𝔽_p`: `#E[4] ≤ 16`

The even-index entry of the `#E[n]` counting family (`TorsionPointCount.lean`: `#E[3]≤9`,
`#E[5]≤25`, `#E[7]≤49`), at the tight value `16 = 4²`. Unlike the odd cases, `n = 4` mixes two
kinds of torsion: the `y = 0` two-torsion (self-paired — one point per `x`) and the primitive
4-torsion (`±y`-paired). The generic `≤2m+1` fiber bound would over-count the self-paired points,
so we split instead:

  `E[4] = E[2] ⊔ P₄`,  `P₄ := {P | 4•P = 0 ∧ 2•P ≠ 0}` (the primitive 4-torsion),

and bound each part tightly: `#E[2] ≤ 4` (`secp256k1_two_torsion_ncard_le`) and `#P₄ ≤ 12`. The
`P₄` bound is a `≤2`-to-`1` fiber count over the roots of `preΨ₄` (degree `6`): via the 4-torsion
bridge `4•P = 0 ⟺ ψ₄(P) = 0` and the factorization `ψ₄(P) = 4y·(x⁶+140x³−392)`, a primitive point
(`2•P ≠ 0`, hence `y ≠ 0`) forces `preΨ₄(x) = 2·(x⁶+140x³−392) = 0`, so its `x` is one of the `≤6`
`preΨ₄`-roots; at most two `y` per `x` gives `≤ 12`. Hence `#E[4] ≤ 4 + 12 = 16`.

Finiteness of every point set is free from the global `Finite W.Point` instance
(`AffinePointFinite.lean`). Reuses the public `px`/`py` projections and the `≤2`-per-`x` curve-fiber
argument of `TorsionPointCount.lean`. No new `native_decide` beyond the `7 ≠ 0` / `2 ≠ 0` facts.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- **`#E[4](𝔽_p) ≤ 16`** — the tight point count for the 4-torsion of secp256k1 (set form),
`16 = 4²`. Proved by the split `E[4] = E[2] ⊔ P₄` with `#E[2] ≤ 4` and a `≤2`-to-`1` fiber count
`#P₄ ≤ 12` over the six `preΨ₄`-roots. The even-index tight companion of `#E[3]≤9`, `#E[5]≤25`,
`#E[7]≤49`. -/
theorem secp256k1_four_torsion_ncard_le :
    Set.ncard {P : secp256k1.toAffine.Point | (4 : ℕ) • P = 0} ≤ 16 := by
  classical
  haveI : NeZero Secp256k1.p := ⟨(Fact.out : Nat.Prime Secp256k1.p).pos.ne'⟩
  have h2ne : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; native_decide
    simpa using this
  have h4ne : (4 : ZMod Secp256k1.p) ≠ 0 := by
    rw [show (4 : ZMod Secp256k1.p) = 2 * 2 by norm_num]; exact mul_ne_zero h2ne h2ne
  -- The point at infinity satisfies `2•O = 0`, so it is never a *primitive* 4-torsion point.
  have hzero2 : (2 : ℕ) • (Point.zero : secp256k1.toAffine.Point) = 0 := by
    rw [show (Point.zero : secp256k1.toAffine.Point) = 0 from rfl, two_nsmul, add_zero]
  -- The primitive 4-torsion set and the `≤ 6` bound on the `preΨ₄`-roots.
  set P4 := {P : secp256k1.toAffine.Point | (4 : ℕ) • P = 0 ∧ (2 : ℕ) • P ≠ 0} with hP4def
  have hXcard : secp256k1.preΨ₄.roots.toFinset.card ≤ 6 :=
    (Multiset.toFinset_card_le _).trans ((card_roots' _).trans (le_of_eq secp256k1_preΨ₄_natDegree))
  -- Every primitive 4-torsion point has its `x`-coordinate a root of `preΨ₄`.
  have hmem : ∀ (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y),
      (4 : ℕ) • Point.some x y h = 0 ∧ (2 : ℕ) • Point.some x y h ≠ 0 →
      x ∈ secp256k1.preΨ₄.roots.toFinset := by
    rintro x y h ⟨h4, h2⟩
    have hcurve : y ^ 2 = x ^ 3 + 7 := secp256k1_curve_of_nonsingular x y h
    have hy : y ≠ 0 := fun hy0 => h2 ((secp256k1_two_nsmul_eq_zero_iff x y h).mpr hy0)
    have hev := (secp256k1_four_nsmul_eq_zero_iff x y h).mp h4
    have hψ4 : (secp256k1.ψ 4).evalEval x y = 4 * y * (x ^ 6 + 140 * x ^ 3 - 392) := by
      rw [secp256k1.ψ_four]
      simp only [evalEval_mul, evalEval_C]
      rw [secp256k1_preΨ₄_eval, secp256k1_psi2_evalEval]
      ring
    rw [hψ4] at hev
    have hω : x ^ 6 + 140 * x ^ 3 - 392 = 0 := by
      rcases mul_eq_zero.mp hev with h4y | hω
      · rcases mul_eq_zero.mp h4y with hc | hc
        · exact absurd hc h4ne
        · exact absurd hc hy
      · exact hω
    rw [Multiset.mem_toFinset, mem_roots']
    refine ⟨secp256k1_preΨ₄_ne_zero, ?_⟩
    rw [IsRoot.def, secp256k1_preΨ₄_eval]
    linear_combination (2 : ZMod Secp256k1.p) * hω
  -- `#P₄ ≤ 12` by a `≤2`-to-`1` fiber count over `preΨ₄.roots`.
  haveI : Fintype ↥P4 := Fintype.ofFinite _
  have hP4card : Set.ncard P4 ≤ 12 := by
    have himg_sub : P4.toFinset.image px ⊆ secp256k1.preΨ₄.roots.toFinset := by
      intro a ha
      rw [Finset.mem_image] at ha
      obtain ⟨P, hPmem, hPa⟩ := ha
      rw [Set.mem_toFinset] at hPmem
      rcases P with _ | ⟨x, y, h⟩
      · exact absurd hzero2 hPmem.2
      · simp only [px] at hPa; rw [← hPa]; exact hmem x y h hPmem
    have hfib : ∀ a ∈ P4.toFinset.image px,
        (P4.toFinset.filter (fun P => px P = a)).card ≤ 2 := by
      intro a _
      have hpoly_ne : (X ^ 2 - C (a ^ 3 + 7) : (ZMod Secp256k1.p)[X]) ≠ 0 :=
        X_pow_sub_C_ne_zero (by norm_num) (a ^ 3 + 7)
      have hpoly_deg : (X ^ 2 - C (a ^ 3 + 7) : (ZMod Secp256k1.p)[X]).natDegree ≤ 2 := by
        compute_degree
      have hroots_card :
          (X ^ 2 - C (a ^ 3 + 7) : (ZMod Secp256k1.p)[X]).roots.toFinset.card ≤ 2 :=
        (Multiset.toFinset_card_le _).trans ((card_roots' _).trans hpoly_deg)
      refine le_trans ?_ hroots_card
      apply Finset.card_le_card_of_injOn py
      · intro P hP
        rw [Finset.mem_coe, Finset.mem_filter, Set.mem_toFinset] at hP
        obtain ⟨hPmem, hPa⟩ := hP
        rcases P with _ | ⟨x, y, h⟩
        · exact absurd hzero2 hPmem.2
        · simp only [px] at hPa; subst hPa
          have hcurve : y ^ 2 = x ^ 3 + 7 := secp256k1_curve_of_nonsingular x y h
          simp only [py, Finset.mem_coe, Multiset.mem_toFinset, mem_roots', IsRoot.def, eval_sub,
            eval_pow, eval_X, eval_C]
          exact ⟨hpoly_ne, by linear_combination hcurve⟩
      · intro P hP Q hQ hPQ
        rw [Finset.mem_coe, Finset.mem_filter, Set.mem_toFinset] at hP hQ
        rcases P with _ | ⟨x1, y1, h1⟩
        · exact absurd hzero2 hP.1.2
        rcases Q with _ | ⟨x2, y2, h2⟩
        · exact absurd hzero2 hQ.1.2
        · simp only [px] at hP hQ
          simp only [py] at hPQ
          have hxx : x1 = x2 := hP.2.trans hQ.2.symm
          subst hxx; subst hPQ; rfl
    rw [Set.ncard_eq_toFinset_card' P4]
    calc P4.toFinset.card
        ≤ 2 * (P4.toFinset.image px).card := by
          apply Finset.card_le_mul_card_image; exact hfib
      _ ≤ 2 * secp256k1.preΨ₄.roots.toFinset.card :=
          Nat.mul_le_mul_left 2 (Finset.card_le_card himg_sub)
      _ ≤ 2 * 6 := Nat.mul_le_mul_left 2 hXcard
  -- Combine: `E[4] ⊆ E[2] ∪ P₄`, so `#E[4] ≤ #E[2] + #P₄ ≤ 4 + 12`.
  have hsub : {P : secp256k1.toAffine.Point | (4 : ℕ) • P = 0}
      ⊆ {P : secp256k1.toAffine.Point | (2 : ℕ) • P = 0} ∪ P4 := by
    intro P hP
    by_cases h2 : (2 : ℕ) • P = 0
    · exact Or.inl h2
    · exact Or.inr ⟨hP, h2⟩
  calc Set.ncard {P : secp256k1.toAffine.Point | (4 : ℕ) • P = 0}
      ≤ Set.ncard ({P : secp256k1.toAffine.Point | (2 : ℕ) • P = 0} ∪ P4) :=
        Set.ncard_le_ncard hsub (Set.toFinite _)
    _ ≤ Set.ncard {P : secp256k1.toAffine.Point | (2 : ℕ) • P = 0} + Set.ncard P4 :=
        Set.ncard_union_le _ _
    _ ≤ 4 + 12 := Nat.add_le_add secp256k1_two_torsion_ncard_le hP4card
    _ = 16 := by norm_num

end Ecdlp.Curve
