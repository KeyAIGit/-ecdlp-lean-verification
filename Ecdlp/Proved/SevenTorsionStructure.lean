import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialEvalBridge
import Ecdlp.Proved.DivisionPolynomialSeparable
import Ecdlp.Proved.CoprimePsi2Psi7
import Ecdlp.Proved.DivisionResultantTransport
import Ecdlp.Proved.SevenTorsionBridgeBar
import Ecdlp.Proved.ThreeTorsionStructure
import Ecdlp.Proved.TorsionStructure

/-!
# N13 at `n = 7`: `#E[7](𝔽̄_p) = 49` and `E[7](𝔽̄_p) ≅ ℤ/7 × ℤ/7`

The `n = 7` instance of node N13 of the `ψₙ ↔ E[n]` bridge decomposition
(`notes/DIVISION_POLY_TORSION_MAP.md`), following `ThreeTorsionStructure.lean`
(the `n = 3` instance) rung for rung: for `secp256k1Bar` — secp256k1 base-changed to
`𝔽̄_p := AlgebraicClosure (ZMod Secp256k1.p)` — the 7-torsion subgroup has **exactly `49`
points** and is `≃+ ZMod 7 × ZMod 7`.

## What this composes (nothing new is certified here — pure assembly)

* **The closure point-level bridge** (`SevenTorsionBridgeBar.lean`):
  `7 • (x, y) = 0 ⟺ ((secp256k1.preΨ' 7).map φ).eval x = 0` — N11 at `n = 7` over `𝔽̄_p`.
* **The exact root count** (`DivisionPolynomialSeparable.lean`):
  the mapped `preΨ' 7` has exactly `24` pairwise-distinct roots in `𝔽̄_p`
  (`secp256k1_preΨ₇_roots_card_bar`, `secp256k1_preΨ₇_roots_nodup_bar`).
* **The `±y` pairing** (N12, this file): every `x ∈ 𝔽̄_p` lifts to a curve point
  (`exists_nonsingular_y`, `DivisionResultantTransport.lean`); at a `preΨ₇`-root the two
  points `(x, y)` and `(x, -y)` are distinct because `y ≠ 0` there — which is exactly
  what the transported Bézout certificate `secp256k1Bar_isCoprime_Ψ₂Sq_preΨ₇` (this
  file, from the `𝔽_p` certificate of `CoprimePsi2Psi7.lean`) forbids: `y = 0` would
  make `Ψ₂Sq = 4(X³+7)` and `preΨ₇` share a root. Hence `#E[7] = 2·24 + 1 = 49`, by an
  explicit 49-element enumeration `{O} ∪ liftP '' roots ∪ (-liftP) '' roots`.
* **The kernel-structure lemma N10(iii)** (`TorsionStructure.lean`):
  a group of order `7² = 49` killed by the prime `7` is `(ℤ/7)²`
  (`Ecdlp.Torsion.nonempty_addEquiv_zmod_prod_of_card_eq_sq`).

## Honest scope

This closes N13 **only at `n = 7`** (after `n = 3`, `ThreeTorsionStructure.lean`). The
uniform-`n` counting half (degree of `[n]`, separability of `[n]`, `#E[n] = n²` for all
`n` prime to `p`) remains the open program of N10(i)/(ii).

## Classical decidability

As in `ThreeTorsionStructure.lean`: Mathlib's affine group law is stated under
`[DecidableEq F]` and `𝔽̄_p` has no computable equality, so this file works under
`open scoped Classical`; all classical `Decidable` instances on the same proposition are
definitionally equal, so the statements compose with any classical instantiation chosen
by consumers.

No new axioms; no `decide`/`native_decide` in this file (the transported Bézout
certificate carries its own `native_decide` residue checks in `CoprimePsi2Psi7.lean`,
and the `p ∤ 2` fact is transported from the compiled template lemmas).
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

open scoped Classical

/-- The base-change hom `𝔽_p →+* 𝔽̄_p` (the same map `secp256k1Bar` is built from). -/
private noncomputable abbrev φcl :
    ZMod Secp256k1.p →+* AlgebraicClosure (ZMod Secp256k1.p) :=
  algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p))

/-- A nonzero constant of `𝔽_p` stays nonzero in `𝔽̄_p` (the base change is injective). -/
private theorem φcl_ne_zero {c : ZMod Secp256k1.p} (hc : c ≠ 0) : φcl c ≠ 0 := by
  intro h0
  exact hc (RingHom.injective φcl (by rw [map_zero]; exact h0))

/-- `2 ≠ 0` in `𝔽̄_p`: `p ∤ 2` over `𝔽_p`, transported along the injective base change. -/
private theorem two_ne_zero_bar : (2 : AlgebraicClosure (ZMod Secp256k1.p)) ≠ 0 := by
  have h2p : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using h
  have hφ := φcl_ne_zero h2p
  rwa [map_ofNat] at hφ

/-! ## Lifting an `x`-coordinate of `𝔽̄_p` to a curve point

Over the algebraically closed field every `x` carries a point `(x, liftY x)` of
`secp256k1Bar` (`exists_nonsingular_y`, compiled in `DivisionResultantTransport.lean`;
the `secp256k1Bar.IsElliptic` instance is the compiled one of
`ThreeTorsionStructure.lean`); the choice is fixed once via `Exists.choose`. -/

/-- A chosen `y`-coordinate over `x` on `secp256k1Bar`. -/
private noncomputable def liftY (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    AlgebraicClosure (ZMod Secp256k1.p) :=
  (exists_nonsingular_y secp256k1Bar x).choose

private theorem liftY_nonsingular (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.Nonsingular x (liftY x) :=
  (exists_nonsingular_y secp256k1Bar x).choose_spec

/-- The chosen curve point of `secp256k1Bar` over `x`. -/
private noncomputable def liftP (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.Point :=
  Point.some x (liftY x) (liftY_nonsingular x)

private theorem liftP_def (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    liftP x = Point.some x (liftY x) (liftY_nonsingular x) := rfl

/-! ## Coefficient extraction for the mapped curve -/

/-- The curve equation of `secp256k1Bar` at a nonsingular point: `y² = x³ + 7`. -/
private theorem secp256k1Bar_curve_of_nonsingular
    (x y : AlgebraicClosure (ZMod Secp256k1.p))
    (h : secp256k1Bar.toAffine.Nonsingular x y) : y ^ 2 = x ^ 3 + 7 := by
  have he : secp256k1Bar.toAffine.Equation x y := h.1
  rw [WeierstrassCurve.Affine.equation_iff] at he
  simp only [secp256k1Bar, WeierstrassCurve.map, WeierstrassCurve.map_a₁,
    WeierstrassCurve.map_a₂, WeierstrassCurve.map_a₃, WeierstrassCurve.map_a₄,
    WeierstrassCurve.map_a₆, secp256k1, map_zero, map_ofNat] at he
  linear_combination he

/-- Negation on `secp256k1Bar` is `y ↦ -y` (`a₁ = a₃ = 0` survive the base change). -/
private theorem secp256k1Bar_negY (x y : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.toAffine.negY x y = -y := by
  simp [WeierstrassCurve.Affine.negY, secp256k1Bar, WeierstrassCurve.map, secp256k1]

/-- `preΨ' 7` of the mapped curve is the mapped `preΨ' 7` (`WeierstrassCurve.map_preΨ'`),
matching the vocabulary of `secp256k1_preΨ₇_roots_card_bar`. -/
private theorem secp256k1Bar_preΨ₇_eq_map :
    secp256k1Bar.preΨ' 7 = (secp256k1.preΨ' 7).map φcl := by
  simp only [secp256k1Bar, WeierstrassCurve.map_preΨ']

/-! ## The 24-element root set of the mapped `preΨ' 7` -/

/-- Exactly `24` roots over `𝔽̄_p`, restated in this file's vocabulary. -/
private theorem Ψ₇bar_roots_card : ((secp256k1.preΨ' 7).map φcl).roots.card = 24 :=
  secp256k1_preΨ₇_roots_card_bar

/-- The `24` roots are pairwise distinct, restated in this file's vocabulary. -/
private theorem Ψ₇bar_roots_nodup : ((secp256k1.preΨ' 7).map φcl).roots.Nodup :=
  secp256k1_preΨ₇_roots_nodup_bar

/-- The mapped `preΨ' 7` is nonzero (it has `24` roots; the zero polynomial has none). -/
private theorem Ψ₇bar_ne_zero : (secp256k1.preΨ' 7).map φcl ≠ 0 := by
  intro h0
  have hc := Ψ₇bar_roots_card
  rw [h0, Polynomial.roots_zero] at hc
  simp at hc

/-- The dedup'd root Finset has exactly `24` elements (`Nodup` makes `toFinset` lossless). -/
private theorem Ψ₇bar_roots_toFinset_card :
    ((secp256k1.preΨ' 7).map φcl).roots.toFinset.card = 24 := by
  have h := Multiset.toFinset_card_of_nodup Ψ₇bar_roots_nodup
  rw [Ψ₇bar_roots_card] at h
  exact h

private theorem eval_of_mem_Ψ₇bar_roots {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : a ∈ ((secp256k1.preΨ' 7).map φcl).roots.toFinset) :
    ((secp256k1.preΨ' 7).map φcl).eval a = 0 :=
  (mem_roots'.mp (Multiset.mem_toFinset.mp ha)).2

private theorem mem_Ψ₇bar_roots_of_eval {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ' 7).map φcl).eval a = 0) :
    a ∈ ((secp256k1.preΨ' 7).map φcl).roots.toFinset :=
  Multiset.mem_toFinset.mpr (mem_roots'.mpr ⟨Ψ₇bar_ne_zero, ha⟩)

/-! ## `y ≠ 0` at the `preΨ₇`-roots, from the `Ψ₂Sq ⊥ preΨ₇` Bézout certificate -/

/-- Coprime polynomials over a field have no common root (Bézout, evaluated). Mirror of
the compiled lemma of `DivisionPolynomialCoprime.lean`. -/
private theorem no_common_root {K : Type*} [Field K] {F G : K[X]} (h : IsCoprime F G)
    {x₀ : K} (hF : F.eval x₀ = 0) (hG : G.eval x₀ = 0) : False := by
  obtain ⟨u, v, huv⟩ := h
  have h1 := congrArg (Polynomial.eval x₀) huv
  simp [hF, hG] at h1

/-- **The `Ψ₂Sq ⊥ preΨ₇` certificate (`CoprimePsi2Psi7.lean`), transported to the
algebraic closure** — the `IsCoprime.map` transport of `DivisionPolynomialCoprime.lean`,
one rung up. This is the "`y ≠ 0` on nonzero 7-torsion" input of the `±y` pairing. -/
theorem secp256k1Bar_isCoprime_Ψ₂Sq_preΨ₇ :
    IsCoprime secp256k1Bar.Ψ₂Sq (secp256k1Bar.preΨ' 7) := by
  have h := secp256k1_isCoprime_Ψ₂Sq_preΨ₇.map (Polynomial.mapRingHom φcl)
  simpa only [Polynomial.coe_mapRingHom, secp256k1Bar, WeierstrassCurve.map_Ψ₂Sq,
    WeierstrassCurve.map_preΨ'] using h

/-- `Ψ₂Sq` of the mapped curve, evaluated: `4(x³ + 7)` (base change of the compiled
closed form `secp256k1_Ψ₂Sq = C 4 * X³ + C 28`). -/
private theorem secp256k1Bar_Ψ₂Sq_eval (a : AlgebraicClosure (ZMod Secp256k1.p)) :
    secp256k1Bar.Ψ₂Sq.eval a = 4 * (a ^ 3 + 7) := by
  have hmap : secp256k1Bar.Ψ₂Sq = (secp256k1.Ψ₂Sq).map φcl := by
    simp only [secp256k1Bar, WeierstrassCurve.map_Ψ₂Sq]
  rw [hmap, secp256k1_Ψ₂Sq]
  simp only [Polynomial.map_add, Polynomial.map_mul, Polynomial.map_pow,
    Polynomial.map_C, Polynomial.map_X, Polynomial.map_ofNat, map_ofNat, eval_add,
    eval_mul, eval_pow, eval_C, eval_X, Polynomial.eval_ofNat]
  ring

/-- **At a root of the mapped `preΨ' 7`, `x³ + 7 ≠ 0`**: otherwise `Ψ₂Sq = 4(X³+7)` and
`preΨ₇` would share the root, contradicting the transported Bézout certificate
`secp256k1Bar_isCoprime_Ψ₂Sq_preΨ₇`. -/
private theorem x_cube_add_seven_ne_zero_of_root
    {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ' 7).map φcl).eval a = 0) : a ^ 3 + 7 ≠ 0 := by
  intro h7
  have hΨ2 : secp256k1Bar.Ψ₂Sq.eval a = 0 := by
    rw [secp256k1Bar_Ψ₂Sq_eval]
    linear_combination 4 * h7
  have hΨ7 : (secp256k1Bar.preΨ' 7).eval a = 0 := by
    rw [secp256k1Bar_preΨ₇_eq_map]
    exact ha
  exact no_common_root secp256k1Bar_isCoprime_Ψ₂Sq_preΨ₇ hΨ2 hΨ7

/-- The chosen `y` over any `x` satisfies the curve equation. -/
private theorem liftY_sq (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    (liftY x) ^ 2 = x ^ 3 + 7 :=
  secp256k1Bar_curve_of_nonsingular x (liftY x) (liftY_nonsingular x)

/-- At a `preΨ₇`-root, the chosen `y` is nonzero (`y = 0` would force `x³ + 7 = 0`). -/
private theorem liftY_ne_zero {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ' 7).map φcl).eval a = 0) : liftY a ≠ 0 := by
  intro h0
  have hsq := liftY_sq a
  rw [h0] at hsq
  exact x_cube_add_seven_ne_zero_of_root ha (by linear_combination -hsq)

/-- At a `preΨ₇`-root, `y ≠ -y` (char `≠ 2` and `y ≠ 0`): the two lifted points differ. -/
private theorem liftY_ne_neg {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ' 7).map φcl).eval a = 0) : liftY a ≠ -liftY a := by
  intro h
  have h2 : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * liftY a = 0 := by
    linear_combination h
  rcases mul_eq_zero.mp h2 with h2' | hy0
  · exact two_ne_zero_bar h2'
  · exact liftY_ne_zero ha hy0

/-! ## 7-torsion membership of the enumerated points -/

/-- The lifted point over a `preΨ₇`-root is 7-torsion (the bridge, `mpr` direction). -/
private theorem liftP_seven_nsmul {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ' 7).map φcl).eval a = 0) : (7 : ℕ) • liftP a = 0 :=
  (secp256k1Bar_seven_torsion_iff_root a (liftY a) (liftY_nonsingular a)).mpr ha

/-- 7-torsion is closed under negation (via the `torsionBy` subgroup). -/
private theorem seven_nsmul_neg {P : secp256k1Bar.toAffine.Point}
    (hP : (7 : ℕ) • P = 0) : (7 : ℕ) • (-P) = 0 := by
  have h1 : P ∈ AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((7 : ℕ) : ℤ) :=
    AddSubgroup.torsionBy.nsmul_iff.mpr hP
  exact AddSubgroup.torsionBy.nsmul_iff.mp (neg_mem h1)

/-! ## The exact enumeration: `E[7] = {O} ∪ liftP '' roots ∪ (-liftP) '' roots` -/

/-- The explicit 49-element Finset has card `49`: `1 + 24 + 24`, with the two 24-element
images disjoint (a shared point would force `y = -y` at a root) and `0` in neither. -/
private theorem seven_torsion_finset_card :
    (insert (0 : secp256k1Bar.toAffine.Point)
      ((((secp256k1.preΨ' 7).map φcl).roots.toFinset.image liftP)
        ∪ (((secp256k1.preΨ' 7).map φcl).roots.toFinset.image fun a => -liftP a))).card
      = 49 := by
  -- `liftP` is injective (project to the `x`-coordinate).
  have hinj1 : Set.InjOn liftP ↑(((secp256k1.preΨ' 7).map φcl).roots.toFinset) := by
    intro a _ b _ hab
    simp only [liftP_def, Point.some.injEq] at hab
    exact hab.1
  have hinj2 : Set.InjOn (fun a => -liftP a)
      ↑(((secp256k1.preΨ' 7).map φcl).roots.toFinset) := by
    intro a ha b hb hab
    have h' : -liftP a = -liftP b := hab
    exact hinj1 ha hb (neg_inj.mp h')
  -- The two images are disjoint: `liftP a = -liftP b` forces `a = b` and `y = -y`.
  have hdisj : Disjoint ((((secp256k1.preΨ' 7).map φcl).roots.toFinset).image liftP)
      ((((secp256k1.preΨ' 7).map φcl).roots.toFinset).image fun a => -liftP a) := by
    rw [Finset.disjoint_left]
    intro P hP hQ
    rw [Finset.mem_image] at hP hQ
    obtain ⟨a, haR, rfl⟩ := hP
    obtain ⟨b, -, hEq⟩ := hQ
    have hEq' : -liftP b = liftP a := hEq
    simp only [liftP_def] at hEq'
    rw [Point.neg_some, Point.some.injEq] at hEq'
    obtain ⟨hba, hyy⟩ := hEq'
    subst hba
    rw [secp256k1Bar_negY] at hyy
    exact liftY_ne_neg (eval_of_mem_Ψ₇bar_roots haR) hyy.symm
  -- `0` is in neither image (affine points are not the point at infinity).
  have h0F : (0 : secp256k1Bar.toAffine.Point)
      ∉ (((secp256k1.preΨ' 7).map φcl).roots.toFinset.image liftP)
        ∪ (((secp256k1.preΨ' 7).map φcl).roots.toFinset.image fun a => -liftP a) := by
    intro h0
    rw [Finset.mem_union] at h0
    rcases h0 with h0 | h0 <;> rw [Finset.mem_image] at h0 <;> obtain ⟨a, -, ha⟩ := h0
    · rw [liftP_def] at ha
      exact Point.some_ne_zero (liftY_nonsingular a) ha
    · have ha' : liftP a = 0 := neg_eq_zero.mp ha
      rw [liftP_def] at ha'
      exact Point.some_ne_zero (liftY_nonsingular a) ha'
  -- Count: 1 + (24 + 24) = 49.
  have h1 := Finset.card_insert_of_notMem h0F
  have h2 := Finset.card_union_of_disjoint hdisj
  have h3 : ((((secp256k1.preΨ' 7).map φcl).roots.toFinset).image liftP).card = 24 :=
    (Finset.card_image_of_injOn hinj1).trans Ψ₇bar_roots_toFinset_card
  have h4 : ((((secp256k1.preΨ' 7).map φcl).roots.toFinset).image
      fun a => -liftP a).card = 24 :=
    (Finset.card_image_of_injOn hinj2).trans Ψ₇bar_roots_toFinset_card
  omega

/-- **The 7-torsion of `secp256k1Bar` is exactly the enumerated 49-element set.**
`⊇` is the bridge (`mpr`) plus closure under negation; `⊆` is the bridge (`mp`) plus
the `±√(x³+7)` dichotomy: `y² = (liftY x)²` forces `y = ±liftY x`. -/
private theorem seven_torsion_set_eq :
    {P : secp256k1Bar.toAffine.Point | (7 : ℕ) • P = 0}
      = ↑(insert (0 : secp256k1Bar.toAffine.Point)
        ((((secp256k1.preΨ' 7).map φcl).roots.toFinset.image liftP)
          ∪ (((secp256k1.preΨ' 7).map φcl).roots.toFinset.image fun a => -liftP a))) := by
  ext P
  simp only [Set.mem_setOf_eq, Finset.mem_coe]
  constructor
  · intro hP
    rcases P with _ | ⟨x, y, h⟩
    · exact Finset.mem_insert_self 0 _
    · have hroot : ((secp256k1.preΨ' 7).map φcl).eval x = 0 :=
        (secp256k1Bar_seven_torsion_iff_root x y h).mp hP
      have hxR : x ∈ ((secp256k1.preΨ' 7).map φcl).roots.toFinset :=
        mem_Ψ₇bar_roots_of_eval hroot
      have hy2 : y ^ 2 = x ^ 3 + 7 := secp256k1Bar_curve_of_nonsingular x y h
      have hz2 : (liftY x) ^ 2 = x ^ 3 + 7 := liftY_sq x
      have hyz : (y - liftY x) * (y + liftY x) = 0 := by
        linear_combination hy2 - hz2
      refine Finset.mem_insert_of_mem ?_
      rcases mul_eq_zero.mp hyz with h1 | h2
      · -- `y = liftY x`: the point is `liftP x`.
        have hy : y = liftY x := sub_eq_zero.mp h1
        subst hy
        exact Finset.mem_union_left _ (Finset.mem_image.mpr ⟨x, hxR, rfl⟩)
      · -- `y = -liftY x`: the point is `-liftP x`.
        have hy : y = -liftY x := by linear_combination h2
        refine Finset.mem_union_right _ (Finset.mem_image.mpr ⟨x, hxR, ?_⟩)
        show -liftP x = Point.some x y h
        rw [liftP_def, Point.neg_some, Point.some.injEq]
        exact ⟨rfl, by rw [secp256k1Bar_negY]; exact hy.symm⟩
  · intro hP
    rw [Finset.mem_insert] at hP
    rcases hP with rfl | hP
    · simp
    rw [Finset.mem_union] at hP
    rcases hP with hP | hP <;> rw [Finset.mem_image] at hP <;>
      obtain ⟨a, haR, rfl⟩ := hP
    · exact liftP_seven_nsmul (eval_of_mem_Ψ₇bar_roots haR)
    · exact seven_nsmul_neg (liftP_seven_nsmul (eval_of_mem_Ψ₇bar_roots haR))

/-! ## The counting theorems -/

/-- **`#E[7](𝔽̄_p) = 49`** (set form). The 7-torsion of `secp256k1Bar` is exactly
`{O} ∪ {(x, ±y) : preΨ₇(x) = 0}`: the mapped `preΨ' 7` has exactly `24` distinct roots
(`secp256k1_preΨ₇_roots_card_bar`), each carrying exactly two points `(x, ±y)` with
`y ≠ 0` (`secp256k1Bar_isCoprime_Ψ₂Sq_preΨ₇`), so `#E[7] = 2·24 + 1 = 49` on the nose —
the counting half of N13 at `n = 7`. -/
theorem secp256k1Bar_seven_torsion_ncard :
    Set.ncard {P : secp256k1Bar.toAffine.Point | (7 : ℕ) • P = 0} = 49 := by
  rw [seven_torsion_set_eq, Set.ncard_coe_finset]
  exact seven_torsion_finset_card

/-- **`#E[7](𝔽̄_p) = 49`** (`Nat.card` subtype form) — definitional reuse of the set
form, exactly as `secp256k1Bar_three_torsion_card` (`ThreeTorsionStructure.lean`). -/
theorem secp256k1Bar_seven_torsion_card :
    Nat.card {P : secp256k1Bar.toAffine.Point // (7 : ℕ) • P = 0} = 49 :=
  secp256k1Bar_seven_torsion_ncard

/-- **`#E[7](𝔽̄_p) = 49`** (torsion-subgroup form): the cardinality of Mathlib's
`AddSubgroup.torsionBy` at `n = 7`, the vocabulary of `Torsion.lean` /
`CurveTorsion.lean`. Membership rewrites to `7 • P = 0` by
`AddSubgroup.torsionBy.nsmul_iff`. -/
theorem secp256k1Bar_torsionBy_seven_card :
    Nat.card
      ↥(AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((7 : ℕ) : ℤ)) = 49 := by
  have he : ↥(AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((7 : ℕ) : ℤ))
      ≃ {P : secp256k1Bar.toAffine.Point // (7 : ℕ) • P = 0} :=
    Equiv.subtypeEquivRight fun _ => AddSubgroup.torsionBy.nsmul_iff
  rw [Nat.card_congr he]
  exact secp256k1Bar_seven_torsion_card

/-! ## The structure theorem: N13 at `n = 7` -/

/-- **`E[7](𝔽̄_p) ≅ ℤ/7 × ℤ/7` — N13 at `n = 7`.** The 7-torsion subgroup of the closure
curve is killed by the prime `7` (definitionally, as a `torsionBy` subgroup) and has
exactly `7² = 49` elements, so the kernel-structure lemma N10(iii)
(`Ecdlp.Torsion.nonempty_addEquiv_zmod_prod_of_card_eq_sq`) classifies it as `(ℤ/7)²` —
the full 2-dimensional `𝔽₇`-plane predicted by the theory of elliptic curves over
algebraically closed fields of characteristic prime to `n`. -/
theorem secp256k1Bar_seven_torsion_structure :
    Nonempty
      (↥(AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((7 : ℕ) : ℤ))
        ≃+ ZMod 7 × ZMod 7) := by
  haveI : Fact (Nat.Prime 7) := ⟨by norm_num⟩
  exact Ecdlp.Torsion.nonempty_addEquiv_zmod_prod_of_card_eq_sq
    (fun a => AddSubgroup.torsionBy.nsmul a)
    (secp256k1Bar_torsionBy_seven_card.trans (by norm_num))

end Ecdlp.Curve
