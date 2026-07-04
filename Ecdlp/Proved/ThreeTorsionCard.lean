import Mathlib
import Ecdlp.Proved.ThreeTorsionBridge
import Ecdlp.Proved.ThreeTorsion

/-!
# Set-level 3-torsion corollaries of the division-polynomial bridge for secp256k1

Consolidating the point-level bridge `secp256k1_three_nsmul_eq_zero_iff`
(`3 • P = 0 ⟺ ψ₃(P) = 0`) and `secp256k1_psi3_evalEval` (`ψ₃` evaluates to `3x⁴ + 84x`),
together with the existing degree-4 root bound `secp256k1_three_torsion_x_card_le`, into
concrete corollaries — culminating in `secp256k1_threeTorsionX_ncard_le`, which upgrades the
forward-only *root* bound to a bound on the actual *set* of 3-torsion `x`-coordinates:
secp256k1 has at most four nonzero 3-torsion `x`-values.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine Polynomial

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Target 1 — concrete corollary.** `3 • P = 0 ⟺ 3x⁴ + 84x = 0`. -/
theorem secp256k1_three_nsmul_eq_zero_iff_poly
    (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y) :
    (3 : ℕ) • (Point.some x y h) = 0 ↔ 3 * x ^ 4 + 84 * x = 0 := by
  rw [secp256k1_three_nsmul_eq_zero_iff, secp256k1_psi3_evalEval]

/-- Evaluating the univariate torsion polynomial `3X⁴ + 84X`. -/
theorem secp256k1_eval_threeTorsionPoly (x : ZMod Secp256k1.p) :
    (3 * X ^ 4 + 84 * X : (ZMod Secp256k1.p)[X]).eval x = 3 * x ^ 4 + 84 * x := by
  simp only [eval_add, eval_mul, eval_pow, eval_X, eval_ofNat]

/-- **Target 2 — root form.** `3 • P = 0 ⟺ x` is a root of the univariate
`3X⁴ + 84X` over `𝔽_p`. -/
theorem secp256k1_three_nsmul_eq_zero_iff_eval
    (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y) :
    (3 : ℕ) • (Point.some x y h) = 0 ↔
      (3 * X ^ 4 + 84 * X : (ZMod Secp256k1.p)[X]).eval x = 0 := by
  rw [secp256k1_three_nsmul_eq_zero_iff_poly, secp256k1_eval_threeTorsionPoly]

/-- The 3-division polynomial `Ψ₃` of secp256k1 evaluates to `3x⁴ + 84x`. -/
theorem secp256k1_Ψ₃_eval (x : ZMod Secp256k1.p) :
    secp256k1.Ψ₃.eval x = 3 * x ^ 4 + 84 * x := by
  rw [secp256k1_Ψ₃]
  simp only [eval_add, eval_mul, eval_pow, eval_X, eval_C, eval_ofNat]
  ring

/-- **Target 3 — membership.** The `x`-coordinate of any nonzero 3-torsion point of
secp256k1 lies in the root multiset of the degree-4 polynomial `Ψ₃`. -/
theorem secp256k1_three_torsion_x_mem_Ψ₃_roots
    (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y)
    (ht : (3 : ℕ) • (Point.some x y h) = 0) : x ∈ secp256k1.Ψ₃.roots := by
  rw [mem_roots']
  refine ⟨secp256k1_Ψ₃_ne_zero, ?_⟩
  rw [IsRoot.def, secp256k1_Ψ₃_eval]
  exact (secp256k1_three_nsmul_eq_zero_iff_poly x y h).mp ht

/-- The set of `x`-coordinates of nonzero 3-torsion points of secp256k1. -/
def threeTorsionX : Set (ZMod Secp256k1.p) :=
  {x | ∃ (y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y),
        (3 : ℕ) • (Point.some x y h) = 0}

/-- **Target 3 — characterization (⊆).** Every 3-torsion `x`-coordinate is a root of
`Ψ₃`; equivalently it satisfies `3x⁴ + 84x = 0`. -/
theorem secp256k1_threeTorsionX_subset_Ψ₃_roots :
    threeTorsionX ⊆ {x | x ∈ secp256k1.Ψ₃.roots} := by
  rintro x ⟨y, h, ht⟩
  exact secp256k1_three_torsion_x_mem_Ψ₃_roots x y h ht

/-- The de-duplicated 3-torsion root set has at most 4 elements (degree bound). -/
theorem secp256k1_Ψ₃_roots_toFinset_card_le :
    secp256k1.Ψ₃.roots.toFinset.card ≤ 4 :=
  (Multiset.toFinset_card_le _).trans secp256k1_three_torsion_x_card_le

/-- The set of 3-torsion `x`-coordinates is finite. -/
theorem secp256k1_threeTorsionX_finite : threeTorsionX.Finite := by
  apply Set.Finite.subset (secp256k1.Ψ₃.roots.toFinset.finite_toSet)
  rintro x ⟨y, h, ht⟩
  simp only [Finset.mem_coe, Multiset.mem_toFinset]
  exact secp256k1_three_torsion_x_mem_Ψ₃_roots x y h ht

/-- **Target 3 — card bound (the valuable one).** secp256k1 has at most 4 nonzero
3-torsion `x`-coordinates, upgrading the forward-only root bound to a bound on the
actual set of torsion `x`-coordinates. -/
theorem secp256k1_threeTorsionX_ncard_le : threeTorsionX.ncard ≤ 4 := by
  have hsub : threeTorsionX ⊆ (↑(secp256k1.Ψ₃.roots.toFinset) : Set (ZMod Secp256k1.p)) := by
    rintro x ⟨y, h, ht⟩
    simp only [Finset.mem_coe, Multiset.mem_toFinset]
    exact secp256k1_three_torsion_x_mem_Ψ₃_roots x y h ht
  calc threeTorsionX.ncard
      ≤ (↑(secp256k1.Ψ₃.roots.toFinset) : Set (ZMod Secp256k1.p)).ncard :=
        Set.ncard_le_ncard hsub (secp256k1.Ψ₃.roots.toFinset.finite_toSet)
    _ = secp256k1.Ψ₃.roots.toFinset.card := by simp
    _ ≤ 4 := secp256k1_Ψ₃_roots_toFinset_card_le

end Ecdlp.Curve
