import Ecdlp.Proved.FrozenProjectiveInfinityStrata
import Ecdlp.Proved.Secp256k1PrimeP
import Ecdlp.Proved.SemaevLeftFoldAffine

/-!
# The exact local secp256k1 Kummer fiber over the algebraic closure

This file identifies the complete projective output fiber of the frozen local
triquadratic `H` on two genuine secp256k1 points over `FpBar`.  The output is
compared only after canonical projective normalization: raw representatives
which differ by a nonzero scalar are never equated.

The proof covers identity inputs, distinct affine `x`-coordinates, the
ordinary tangent and cancellation branches, and the nonzero two-torsion that
exists over the algebraic closure.  In particular it does not use the
base-field theorem excluding nonzero two-torsion.

This is a local point/Kummer statement only.  It makes no recursive-root,
descent, recovery, solver, yield, rank, cost, or ECDLP-complexity claim.
-/

namespace Ecdlp.FrozenProjectiveSecpLocalFiber

open WeierstrassCurve.Affine
open Ecdlp.Curve
open Ecdlp.FrozenProjectiveSemaev

noncomputable section

/-- The secp256k1 base field. -/
abbrev Fp := ZMod Secp256k1.p

/-- The chosen algebraic closure of the secp256k1 base field. -/
abbrev FpBar := AlgebraicClosure Fp

/-- secp256k1 base-changed to the chosen algebraic closure. -/
abbrev BarCurve := secp256k1 ⁄ FpBar

/-- secp256k1 points over the chosen algebraic closure. -/
abbrev BarPoint := BarCurve.Point

local instance : DecidableEq FpBar := Classical.decEq _

private instance barCurve_isElliptic : BarCurve.IsElliptic :=
  inferInstanceAs
    ((secp256k1.map (algebraMap Fp FpBar)).IsElliptic)

/-- The canonical Kummer coordinate of a closure point: the group identity is
the point at infinity and an affine point maps to `[x:1]`. -/
def barKummer : BarPoint → ProjectivePair FpBar
  | 0 => .infinity
  | Point.some x _ _ => .affine x

@[simp] theorem barKummer_zero :
    barKummer (0 : BarPoint) = ProjectivePair.infinity := rfl

@[simp] theorem barKummer_some
    {x y : FpBar} (h : BarCurve.Nonsingular x y) :
    barKummer (Point.some x y h) = ProjectivePair.affine x := rfl

@[simp] theorem barKummer_neg (P : BarPoint) :
    barKummer (-P) = barKummer P := by
  rcases P with _ | ⟨x, y, h⟩
  · rfl
  · rfl

@[simp] theorem normalize_barKummer (P : BarPoint) :
    normalizeProjectivePair (barKummer P) = barKummer P := by
  rcases P with _ | ⟨x, y, h⟩
  · simp [barKummer, normalizeProjectivePair, ProjectivePair.infinity]
  · simp [barKummer, normalizeProjectivePair, ProjectivePair.affine]

private theorem barCurve_curve_of_nonsingular
    {x y : FpBar} (h : BarCurve.Nonsingular x y) :
    y ^ 2 = x ^ 3 + 7 := by
  have he : BarCurve.Equation x y := h.1
  rw [WeierstrassCurve.Affine.equation_iff] at he
  simp only [BarCurve, WeierstrassCurve.baseChange, WeierstrassCurve.map,
    secp256k1, map_zero, map_ofNat] at he
  linear_combination he

private theorem barCurve_negY (x y : FpBar) :
    BarCurve.negY x y = -y := by
  simp [WeierstrassCurve.Affine.negY, BarCurve,
    WeierstrassCurve.baseChange, WeierstrassCurve.map, secp256k1]

private theorem bar_two_ne_zero : (2 : FpBar) ≠ 0 := by
  have hbase' : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]
    decide
  have hbase : (2 : Fp) ≠ 0 := by simpa [Fp] using hbase'
  have hmap := (algebraMap Fp FpBar).injective.ne hbase
  simpa only [map_ofNat, map_zero] using hmap

private theorem bar_sixtyThree_ne_zero : (63 : FpBar) ≠ 0 := by
  have hbase' : ((63 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
    rw [Ne, ZMod.natCast_eq_zero_iff]
    decide
  have hbase : (63 : Fp) ≠ 0 := by simpa [Fp] using hbase'
  have hmap := (algebraMap Fp FpBar).injective.ne hbase
  simpa only [map_ofNat, map_zero] using hmap

private theorem ProjectivePair.eq_of_u_v_eq
    {A B : ProjectivePair FpBar}
    (hu : A.u = B.u) (hv : A.v = B.v) : A = B := by
  rcases A with ⟨au, av, ha⟩
  rcases B with ⟨bu, bv, hb⟩
  simp only at hu hv
  subst bu
  subst bv
  rfl

/-! ## Projective equality through the determinant -/

/-- The determinant against a canonical affine representative vanishes
exactly when the normalization of the arbitrary representative is that
affine representative. -/
theorem projectiveDet_eq_zero_iff_normalize_eq_affine
    (W : ProjectivePair FpBar) (x : FpBar) :
    projectiveDet W (ProjectivePair.affine x) = 0 ↔
      normalizeProjectivePair W = ProjectivePair.affine x := by
  by_cases hv : W.v = 0
  · have hu : W.u ≠ 0 := by
      rcases W.valid with hu | hv'
      · exact hu
      · exact (hv' hv).elim
    constructor
    · intro h
      simp [projectiveDet, ProjectivePair.affine, hv] at h
      exact (hu h).elim
    · intro h
      have hvEq := congrArg ProjectivePair.v h
      simp [normalizeProjectivePair, hv, ProjectivePair.infinity,
        ProjectivePair.affine] at hvEq
  · simp only [projectiveDet, ProjectivePair.affine,
      normalizeProjectivePair, dif_neg hv]
    constructor
    · intro h
      apply ProjectivePair.eq_of_u_v_eq
      · simp only [div_eq_iff hv]
        linear_combination h
      · rfl
    · intro h
      have hu := congrArg ProjectivePair.u h
      have hmul : W.u = x * W.v := (div_eq_iff hv).mp hu
      linear_combination hmul

/-- The determinant against the canonical infinity representative vanishes
exactly when the arbitrary representative normalizes to infinity. -/
theorem projectiveDet_eq_zero_iff_normalize_eq_infinity
    (W : ProjectivePair FpBar) :
    projectiveDet W (ProjectivePair.infinity (K := FpBar)) = 0 ↔
      normalizeProjectivePair W = ProjectivePair.infinity := by
  by_cases hv : W.v = 0
  · simp [projectiveDet, ProjectivePair.infinity,
      normalizeProjectivePair, hv]
  · constructor
    · intro h
      exact (hv (by simpa [projectiveDet, ProjectivePair.infinity] using h)).elim
    · intro h
      have hvEq := congrArg ProjectivePair.v h
      simp [normalizeProjectivePair, hv, ProjectivePair.infinity,
        ProjectivePair.affine] at hvEq

/-- Projective determinant zero is the normalized equality relation for a
canonical Kummer point. -/
theorem projectiveDet_barKummer_eq_zero_iff
    (W : ProjectivePair FpBar) (P : BarPoint) :
    projectiveDet W (barKummer P) = 0 ↔
      normalizeProjectivePair W = barKummer P := by
  rcases P with _ | ⟨x, y, h⟩
  · exact projectiveDet_eq_zero_iff_normalize_eq_infinity W
  · exact projectiveDet_eq_zero_iff_normalize_eq_affine W x

@[simp] theorem normalizeProjectivePair_idem (W : ProjectivePair FpBar) :
    normalizeProjectivePair (normalizeProjectivePair W) =
      normalizeProjectivePair W := by
  by_cases hv : W.v = 0
  · simp [normalizeProjectivePair, hv, ProjectivePair.infinity]
  · simp [normalizeProjectivePair, hv, ProjectivePair.affine]

private theorem affine_eq_affine_iff (x z : FpBar) :
    ProjectivePair.affine x = ProjectivePair.affine z ↔ x = z := by
  constructor
  · intro h
    exact congrArg ProjectivePair.u h
  · rintro rfl
    rfl

private theorem infinity_ne_affine (x : FpBar) :
    ProjectivePair.infinity ≠ ProjectivePair.affine x := by
  intro h
  have hv := congrArg ProjectivePair.v h
  change (0 : FpBar) = 1 at hv
  exact zero_ne_one hv

/-- Equality of canonical Kummer coordinates identifies exactly a point and
its sign mate. -/
theorem barKummer_eq_iff (P Q : BarPoint) :
    barKummer P = barKummer Q ↔ P = Q ∨ P = -Q := by
  rcases P with _ | ⟨x₁, y₁, h₁⟩ <;>
    rcases Q with _ | ⟨x₂, y₂, h₂⟩
  · simp
  · constructor
    · intro h
      exact (infinity_ne_affine x₂ h).elim
    · rintro (h | h)
      · exact (Point.some_ne_zero h₂ h.symm).elim
      · have hz : -(Point.some x₂ y₂ h₂) ≠ (0 : BarPoint) :=
          neg_ne_zero.mpr (Point.some_ne_zero h₂)
        exact (hz h.symm).elim
  · constructor
    · intro h
      exact (infinity_ne_affine x₁ h.symm).elim
    · rintro (h | h)
      · exact (Point.some_ne_zero h₁ h).elim
      · have hz : -(0 : BarPoint) = 0 := neg_zero
        exact (Point.some_ne_zero h₁ (h.trans hz)).elim
  · rw [barKummer_some, barKummer_some, affine_eq_affine_iff]
    exact Point.X_eq_iff

/-! ## Affine local fibers -/

private theorem barKummer_add_of_X_ne
    {x₁ y₁ x₂ y₂ : FpBar}
    (h₁ : BarCurve.Nonsingular x₁ y₁)
    (h₂ : BarCurve.Nonsingular x₂ y₂)
    (hx : x₁ ≠ x₂) :
    barKummer (Point.some x₁ y₁ h₁ + Point.some x₂ y₂ h₂) =
      ProjectivePair.affine
        (BarCurve.addX x₁ x₂ (BarCurve.slope x₁ x₂ y₁ y₂)) := by
  rw [Point.add_of_X_ne hx]
  rfl

private theorem barKummer_sub_of_X_ne
    {x₁ y₁ x₂ y₂ : FpBar}
    (h₁ : BarCurve.Nonsingular x₁ y₁)
    (h₂ : BarCurve.Nonsingular x₂ y₂)
    (hx : x₁ ≠ x₂) :
    barKummer (Point.some x₁ y₁ h₁ - Point.some x₂ y₂ h₂) =
      ProjectivePair.affine
        (BarCurve.addX x₁ x₂
          (BarCurve.slope x₁ x₂ y₁ (BarCurve.negY x₂ y₂))) := by
  rw [sub_eq_add_neg, Point.neg_some, Point.add_of_X_ne hx]
  rfl

private theorem HValue_affine_distinct_zero_iff
    {x₁ y₁ x₂ y₂ : FpBar}
    (h₁ : BarCurve.Nonsingular x₁ y₁)
    (h₂ : BarCurve.Nonsingular x₂ y₂)
    (hx : x₁ ≠ x₂) (z : FpBar) :
    HValue (ProjectivePair.affine x₁).coord
        (ProjectivePair.affine x₂).coord
        (ProjectivePair.affine z).coord = 0 ↔
      ProjectivePair.affine z =
          barKummer (Point.some x₁ y₁ h₁ + Point.some x₂ y₂ h₂) ∨
      ProjectivePair.affine z =
          barKummer (Point.some x₁ y₁ h₁ - Point.some x₂ y₂ h₂) := by
  have hc₁ := barCurve_curve_of_nonsingular h₁
  have hc₂ := barCurve_curve_of_nonsingular h₂
  rw [Ecdlp.SemaevLeftFoldAffine.HValue_affine_eq_S₃]
  rw [Ecdlp.Semaev.S₃_eq_zero_iff 0 7 x₁ y₁ x₂ y₂ z
    (by linear_combination hc₁) (by linear_combination hc₂) hx]
  rw [barKummer_add_of_X_ne h₁ h₂ hx,
    barKummer_sub_of_X_ne h₁ h₂ hx,
    affine_eq_affine_iff, affine_eq_affine_iff]
  rw [WeierstrassCurve.Affine.slope_of_X_ne hx,
    WeierstrassCurve.Affine.slope_of_X_ne hx, barCurve_negY]
  simp only [WeierstrassCurve.Affine.addX, BarCurve,
    WeierstrassCurve.baseChange, WeierstrassCurve.map, secp256k1,
    map_zero, sub_zero, zero_mul]
  have hd : x₁ - x₂ ≠ 0 := sub_ne_zero.mpr hx
  constructor
  · rintro (h | h)
    · left
      apply (eq_sub_iff_add_eq).2
      apply (eq_sub_iff_add_eq).2
      rw [div_pow, add_zero, eq_div_iff (pow_ne_zero 2 hd)]
      linear_combination h
    · right
      apply (eq_sub_iff_add_eq).2
      apply (eq_sub_iff_add_eq).2
      rw [div_pow, add_zero, eq_div_iff (pow_ne_zero 2 hd)]
      linear_combination h
  · rintro (h | h)
    · rw [h]
      left
      field_simp [hd]
      ring
    · rw [h]
      right
      field_simp [hd]
      ring

private theorem barKummer_add_self_of_Y_ne
    {x y : FpBar} (h : BarCurve.Nonsingular x y)
    (hy : y ≠ BarCurve.negY x y) :
    barKummer (Point.some x y h + Point.some x y h) =
      ProjectivePair.affine
        (BarCurve.addX x x (BarCurve.slope x x y y)) := by
  rw [Point.add_self_of_Y_ne hy]
  rfl

private theorem HValue_affine_self_affine_zero_iff_of_Y_ne
    {x y : FpBar} (h : BarCurve.Nonsingular x y)
    (hy : y ≠ BarCurve.negY x y) (z : FpBar) :
    HValue (ProjectivePair.affine x).coord
        (ProjectivePair.affine x).coord
        (ProjectivePair.affine z).coord = 0 ↔
      ProjectivePair.affine z =
        barKummer (Point.some x y h + Point.some x y h) := by
  have hc := barCurve_curve_of_nonsingular h
  have hy0 : y ≠ 0 := by
    intro hyz
    apply hy
    rw [hyz, barCurve_negY]
    simp
  have h2y : (2 : FpBar) * y ≠ 0 := mul_ne_zero bar_two_ne_zero hy0
  let ℓ : FpBar := BarCurve.slope x x y y
  have hℓ : ℓ * (2 * y) = 3 * x ^ 2 := by
    rw [show ℓ = BarCurve.slope x x y y from rfl,
      WeierstrassCurve.Affine.slope_of_Y_ne rfl hy, barCurve_negY]
    simp only [BarCurve, WeierstrassCurve.baseChange,
      WeierstrassCurve.map, secp256k1, map_zero, sub_zero, zero_mul]
    rw [show y - -y = 2 * y by ring]
    simpa using div_mul_cancel₀ (3 * x ^ 2) h2y
  let r : FpBar := BarCurve.addX x x (BarCurve.slope x x y y)
  have hr : 4 * y ^ 2 * r = x ^ 4 - 56 * x := by
    rw [show r = BarCurve.addX x x ℓ from rfl]
    simp only [WeierstrassCurve.Affine.addX, BarCurve,
      WeierstrassCurve.baseChange, WeierstrassCurve.map, secp256k1,
      map_zero, sub_zero, zero_mul]
    linear_combination (2 * y * ℓ + 3 * x ^ 2) * hℓ - 8 * x * hc
  have hfactor :
      HValue (ProjectivePair.affine x).coord
          (ProjectivePair.affine x).coord
          (ProjectivePair.affine z).coord =
        -(4 * y ^ 2) * (z - r) := by
    rw [Ecdlp.SemaevLeftFoldAffine.HValue_affine_eq_S₃]
    simp only [Ecdlp.Semaev.S₃]
    linear_combination (4 * z) * hc - hr
  have hcoef : -(4 * y ^ 2) ≠ 0 := by
    have hsquare : ((2 : FpBar) * y) ^ 2 ≠ 0 := pow_ne_zero 2 h2y
    intro hz
    apply hsquare
    linear_combination -hz
  rw [hfactor, mul_eq_zero]
  simp only [hcoef, false_or, sub_eq_zero]
  rw [barKummer_add_self_of_Y_ne h hy, affine_eq_affine_iff]

private theorem HValue_affine_self_affine_ne_zero_of_Y_eq
    {x y : FpBar} (h : BarCurve.Nonsingular x y)
    (hy : y = BarCurve.negY x y) (z : FpBar) :
    HValue (ProjectivePair.affine x).coord
        (ProjectivePair.affine x).coord
        (ProjectivePair.affine z).coord ≠ 0 := by
  have hc := barCurve_curve_of_nonsingular h
  have hy0 : y = 0 := by
    rw [barCurve_negY] at hy
    have h2y : (2 : FpBar) * y = 0 := by linear_combination hy
    exact (mul_eq_zero.mp h2y).resolve_left bar_two_ne_zero
  have hx3 : x ^ 3 = -7 := by
    rw [hy0] at hc
    linear_combination -hc
  have hseven : (7 : FpBar) ≠ 0 := by
    intro h7
    apply bar_sixtyThree_ne_zero
    linear_combination 9 * h7
  have hx : x ≠ 0 := by
    intro hx0
    rw [hx0] at hx3
    exact hseven (by linear_combination hx3)
  have hvalue :
      HValue (ProjectivePair.affine x).coord
          (ProjectivePair.affine x).coord
          (ProjectivePair.affine z).coord = -(63 * x) := by
    rw [Ecdlp.SemaevLeftFoldAffine.HValue_affine_eq_S₃]
    simp only [Ecdlp.Semaev.S₃]
    linear_combination (-4 * z + x) * hx3
  rw [hvalue]
  exact neg_ne_zero.mpr (mul_ne_zero bar_sixtyThree_ne_zero hx)

private theorem HValue_affine_self_normalize_zero_iff
    {x y : FpBar} (h : BarCurve.Nonsingular x y)
    (W : ProjectivePair FpBar) :
    HValue (ProjectivePair.affine x).coord
        (ProjectivePair.affine x).coord
        (normalizeProjectivePair W).coord = 0 ↔
      normalizeProjectivePair W =
          barKummer (Point.some x y h + Point.some x y h) ∨
      normalizeProjectivePair W =
          barKummer (Point.some x y h - Point.some x y h) := by
  by_cases hv : W.v = 0
  · simp only [normalizeProjectivePair, dif_pos hv]
    rw [HValue_third_infinity]
    simp [projectiveDet, ProjectivePair.affine, ProjectivePair.infinity,
      barKummer, sub_self]
  · simp only [normalizeProjectivePair, dif_neg hv]
    by_cases hy : y = BarCurve.negY x y
    · have hadd : Point.some x y h + Point.some x y h = (0 : BarPoint) :=
        Point.add_self_of_Y_eq hy
      have hne := HValue_affine_self_affine_ne_zero_of_Y_eq h hy (W.u / W.v)
      rw [hadd, sub_self]
      constructor
      · intro hz
        exact (hne hz).elim
      · rintro (hz | hz)
        · exact (infinity_ne_affine (W.u / W.v) hz.symm).elim
        · exact (infinity_ne_affine (W.u / W.v) hz.symm).elim
    · rw [HValue_affine_self_affine_zero_iff_of_Y_ne h hy]
      rw [sub_self, barKummer_zero]
      constructor
      · intro hsum
        exact Or.inl hsum
      · rintro (hsum | hinf)
        · exact hsum
        · exact (infinity_ne_affine (W.u / W.v) hinf.symm).elim

private theorem HValue_affine_pair_normalize_zero_iff
    {x₁ y₁ x₂ y₂ : FpBar}
    (h₁ : BarCurve.Nonsingular x₁ y₁)
    (h₂ : BarCurve.Nonsingular x₂ y₂)
    (W : ProjectivePair FpBar) :
    HValue (ProjectivePair.affine x₁).coord
        (ProjectivePair.affine x₂).coord
        (normalizeProjectivePair W).coord = 0 ↔
      normalizeProjectivePair W =
          barKummer (Point.some x₁ y₁ h₁ + Point.some x₂ y₂ h₂) ∨
      normalizeProjectivePair W =
          barKummer (Point.some x₁ y₁ h₁ - Point.some x₂ y₂ h₂) := by
  by_cases hx : x₁ ≠ x₂
  · by_cases hv : W.v = 0
    · simp only [normalizeProjectivePair, dif_pos hv]
      rw [HValue_third_infinity,
        barKummer_add_of_X_ne h₁ h₂ hx,
        barKummer_sub_of_X_ne h₁ h₂ hx]
      have hdet :
          projectiveDet (ProjectivePair.affine x₁)
              (ProjectivePair.affine x₂) = x₁ - x₂ := by
        simp [projectiveDet, ProjectivePair.affine]
      rw [hdet]
      constructor
      · intro hz
        exact (pow_ne_zero 2 (sub_ne_zero.mpr hx) hz).elim
      · rintro (hz | hz)
        · exact (infinity_ne_affine _ hz).elim
        · exact (infinity_ne_affine _ hz).elim
    · simp only [normalizeProjectivePair, dif_neg hv]
      exact HValue_affine_distinct_zero_iff h₁ h₂ hx (W.u / W.v)
  · have hxeq : x₁ = x₂ := not_ne_iff.mp hx
    subst x₂
    let P : BarPoint := Point.some x₁ y₁ h₁
    let Q : BarPoint := Point.some x₁ y₂ h₂
    have hsign : P = Q ∨ P = -Q :=
      (Point.X_eq_iff (W := BarCurve)).mp rfl
    rcases hsign with hPQ | hPQ
    · have hQ : Q = P := hPQ.symm
      simpa only [P, Q, hQ] using
        HValue_affine_self_normalize_zero_iff h₁ W
    · have hQ : Q = -P := by
        simpa using (congrArg Neg.neg hPQ).symm
      have hself := HValue_affine_self_normalize_zero_iff h₁ W
      simpa only [P, Q, hQ, sub_eq_add_neg, neg_neg, add_neg_cancel,
        add_zero, or_comm] using hself

/-! ## Complete local Kummer fiber -/

/-- The strongest local fiber statement after normalizing the arbitrary
projective output representative.  The two roots are precisely the Kummer
coordinates of `P + Q` and `P - Q`, with a disjunction that intentionally
allows the two roots to coincide. -/
theorem HValue_barKummer_normalize_zero_iff
    (P Q : BarPoint) (W : ProjectivePair FpBar) :
    HValue (barKummer P).coord (barKummer Q).coord
        (normalizeProjectivePair W).coord = 0 ↔
      normalizeProjectivePair W = barKummer (P + Q) ∨
      normalizeProjectivePair W = barKummer (P - Q) := by
  rcases P with _ | ⟨x₁, y₁, h₁⟩ <;>
    rcases Q with _ | ⟨x₂, y₂, h₂⟩
  · change
      HValue (ProjectivePair.infinity (K := FpBar)).coord
          (ProjectivePair.infinity (K := FpBar)).coord
          (normalizeProjectivePair W).coord = 0 ↔
        normalizeProjectivePair W =
            barKummer ((0 : BarPoint) + (0 : BarPoint)) ∨
        normalizeProjectivePair W =
            barKummer ((0 : BarPoint) - (0 : BarPoint))
    rw [HValue_first_infinity]
    have hswap :
        projectiveDet (ProjectivePair.infinity (K := FpBar))
            (normalizeProjectivePair W) =
          -projectiveDet (normalizeProjectivePair W)
            (ProjectivePair.infinity (K := FpBar)) := by
      simp [projectiveDet, ProjectivePair.infinity]
    rw [hswap]
    simp only [neg_sq, sq_eq_zero_iff,
      projectiveDet_eq_zero_iff_normalize_eq_infinity,
      normalizeProjectivePair_idem]
    simp
  · change
      HValue (ProjectivePair.infinity (K := FpBar)).coord
          (ProjectivePair.affine x₂).coord
          (normalizeProjectivePair W).coord = 0 ↔
        normalizeProjectivePair W =
            barKummer ((0 : BarPoint) + Point.some x₂ y₂ h₂) ∨
        normalizeProjectivePair W =
            barKummer ((0 : BarPoint) - Point.some x₂ y₂ h₂)
    rw [HValue_first_infinity]
    have hswap :
        projectiveDet (ProjectivePair.affine x₂)
            (normalizeProjectivePair W) =
          -projectiveDet (normalizeProjectivePair W)
            (ProjectivePair.affine x₂) := by
      simp [projectiveDet, ProjectivePair.affine]
      ring
    rw [hswap]
    simp only [neg_sq, sq_eq_zero_iff,
      projectiveDet_eq_zero_iff_normalize_eq_affine,
      normalizeProjectivePair_idem]
    simp
  · change
      HValue (ProjectivePair.affine x₁).coord
          (ProjectivePair.infinity (K := FpBar)).coord
          (normalizeProjectivePair W).coord = 0 ↔
        normalizeProjectivePair W =
            barKummer (Point.some x₁ y₁ h₁ + (0 : BarPoint)) ∨
        normalizeProjectivePair W =
            barKummer (Point.some x₁ y₁ h₁ - (0 : BarPoint))
    rw [HValue_middle_infinity]
    have hswap :
        projectiveDet (ProjectivePair.affine x₁)
            (normalizeProjectivePair W) =
          -projectiveDet (normalizeProjectivePair W)
            (ProjectivePair.affine x₁) := by
      simp [projectiveDet, ProjectivePair.affine]
      ring
    rw [hswap]
    simp only [neg_sq, sq_eq_zero_iff,
      projectiveDet_eq_zero_iff_normalize_eq_affine,
      normalizeProjectivePair_idem]
    simp
  · exact HValue_affine_pair_normalize_zero_iff h₁ h₂ W

/-- Arbitrary-output local secp256k1 Kummer fiber over the algebraic closure.
The left side uses the raw valid representative `W`; the right side compares
only its canonical normalization. -/
theorem HValue_barKummer_zero_iff
    (P Q : BarPoint) (W : ProjectivePair FpBar) :
    HValue (barKummer P).coord (barKummer Q).coord W.coord = 0 ↔
      normalizeProjectivePair W = barKummer (P + Q) ∨
      normalizeProjectivePair W = barKummer (P - Q) := by
  rw [HValue_normalize_third_zero_iff]
  exact HValue_barKummer_normalize_zero_iff P Q W

/-- Equivalent determinant form of the complete local fiber. -/
theorem HValue_barKummer_zero_iff_projectiveDet
    (P Q : BarPoint) (W : ProjectivePair FpBar) :
    HValue (barKummer P).coord (barKummer Q).coord W.coord = 0 ↔
      projectiveDet W (barKummer (P + Q)) = 0 ∨
      projectiveDet W (barKummer (P - Q)) = 0 := by
  rw [HValue_barKummer_zero_iff,
    projectiveDet_barKummer_eq_zero_iff,
    projectiveDet_barKummer_eq_zero_iff]

end

end Ecdlp.FrozenProjectiveSecpLocalFiber
