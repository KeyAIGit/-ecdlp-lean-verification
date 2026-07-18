import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialEvalBridge
import Ecdlp.Proved.DivisionPolynomialSeparable
import Ecdlp.Proved.CoprimePsi2Psi5
import Ecdlp.Proved.DivisionResultantTransport
import Ecdlp.Proved.FiveTorsionBridgeBar
import Ecdlp.Proved.ThreeTorsionStructure
import Ecdlp.Proved.TorsionStructure

/-!
# N13 at `n = 5`: `#E[5](𝔽̄_p) = 25` and `E[5](𝔽̄_p) ≅ ℤ/5 × ℤ/5`

**The second full instance of node N13** of the `ψₙ ↔ E[n]` bridge decomposition
(`notes/DIVISION_POLY_TORSION_MAP.md`): for `secp256k1Bar` — secp256k1 base-changed to
`𝔽̄_p := AlgebraicClosure (ZMod Secp256k1.p)` — the 5-torsion subgroup has **exactly `25`
points** and is `≃+ ZMod 5 × ZMod 5`. This mirrors `ThreeTorsionStructure.lean` (the
`n = 3` instance) rung for rung; with this file the N13 instance count grows to
`n ∈ {3, 5}`.

## What this composes (nothing new is certified here — pure assembly)

* **The closure point-level bridge** (`FiveTorsionBridgeBar.lean`):
  `5 • (x, y) = 0 ⟺ ((secp256k1.preΨ' 5).map φ).eval x = 0` — N11 at `n = 5` over `𝔽̄_p`.
* **The exact root count** (`DivisionPolynomialSeparable.lean`):
  the mapped `preΨ₅` has exactly `12` pairwise-distinct roots in `𝔽̄_p`
  (`secp256k1_preΨ₅_roots_card_bar`, `secp256k1_preΨ₅_roots_nodup_bar`).
* **The `±y` pairing** (N12, this file): every `x ∈ 𝔽̄_p` lifts to a curve point
  (`exists_nonsingular_y`, `DivisionResultantTransport.lean`, applicable through the
  `secp256k1Bar.IsElliptic` instance registered in `ThreeTorsionStructure.lean`); at a
  `preΨ₅`-root the two points `(x, y)` and `(x, -y)` are distinct because `y ≠ 0`
  there — which is exactly what the Bézout certificate
  `secp256k1_isCoprime_Ψ₂Sq_preΨ₅` (`CoprimePsi2Psi5.lean`, stated for `secp256k1.Ψ₂Sq`
  and `secp256k1.preΨ' 5` over `𝔽_p` — precisely the object whose closure roots are
  counted above), transported to `𝔽̄_p[X]` via `IsCoprime.map` exactly as
  `DivisionPolynomialCoprime.lean` does, forbids: `y = 0` would make `Ψ₂Sq = 4(X³+7)`
  and `preΨ₅` share a root. Hence `#E[5] = 2·12 + 1 = 25`, by an explicit 25-element
  enumeration `{O} ∪ liftP '' roots ∪ (-liftP) '' roots`.
* **The kernel-structure lemma N10(iii)** (`TorsionStructure.lean`):
  a group of order `5² = 25` killed by the prime `5` is `(ℤ/5)²`
  (`Ecdlp.Torsion.nonempty_addEquiv_zmod_prod_of_card_eq_sq`).

## Honest scope

This closes N13 **only at `n = 5`** (joining the compiled `n = 3` instance). The
uniform-`n` counting half (degree of `[n]`, separability of `[n]`, `#E[n] = n²` for all
`n` prime to `p`) is the open program of N10(i)/(ii); `n = 7` would follow this file's
exact pattern once its closure bridge (the analogue of `FiveTorsionBridgeBar.lean`,
building on `SevenTorsionBridge.lean`) lands.

## Classical decidability

Mathlib's affine group law (`WeierstrassCurve.Affine.Point.add` and the `AddCommGroup`
instance on `Point`) is stated under `[DecidableEq F]`, and `𝔽̄_p` has no computable
equality. Following the compiled precedent of `ThreeTorsionStructure.lean`, this file
works under `open scoped Classical`; all classical `Decidable` instances on the same
proposition are definitionally equal, so the statements compose with any classical
instantiation chosen by consumers.

No new axioms and no `native_decide` **in this file**; the imported Bézout certificate
of `CoprimePsi2Psi5.lean` carries its own audited `native_decide`s, and the only
`decide`s are the bridge file's `p ∤ c` facts over `ℕ`.
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
the `secp256k1Bar.IsElliptic` instance it needs is registered in
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

/-- The curve equation of `secp256k1Bar` at a nonsingular point: `y² = x³ + 7`.
Closure analogue of the compiled `secp256k1_curve_of_nonsingular`. -/
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

/-! ## The 12-element root set of the mapped `preΨ₅` -/

/-- Exactly `12` roots over `𝔽̄_p`, restated in this file's vocabulary. -/
private theorem preΨ₅bar_roots_card : ((secp256k1.preΨ' 5).map φcl).roots.card = 12 :=
  secp256k1_preΨ₅_roots_card_bar

/-- The `12` roots are pairwise distinct, restated in this file's vocabulary. -/
private theorem preΨ₅bar_roots_nodup : ((secp256k1.preΨ' 5).map φcl).roots.Nodup :=
  secp256k1_preΨ₅_roots_nodup_bar

/-- The mapped `preΨ₅` is nonzero (it has `12` roots; the zero polynomial has none). -/
private theorem preΨ₅bar_ne_zero : (secp256k1.preΨ' 5).map φcl ≠ 0 := by
  intro h0
  have hc := preΨ₅bar_roots_card
  rw [h0, Polynomial.roots_zero] at hc
  simp at hc

/-- The dedup'd root Finset has exactly `12` elements (`Nodup` makes `toFinset` lossless). -/
private theorem preΨ₅bar_roots_toFinset_card :
    ((secp256k1.preΨ' 5).map φcl).roots.toFinset.card = 12 := by
  have h := Multiset.toFinset_card_of_nodup preΨ₅bar_roots_nodup
  rw [preΨ₅bar_roots_card] at h
  exact h

private theorem eval_of_mem_preΨ₅bar_roots {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : a ∈ ((secp256k1.preΨ' 5).map φcl).roots.toFinset) :
    ((secp256k1.preΨ' 5).map φcl).eval a = 0 :=
  (mem_roots'.mp (Multiset.mem_toFinset.mp ha)).2

private theorem mem_preΨ₅bar_roots_of_eval {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ' 5).map φcl).eval a = 0) :
    a ∈ ((secp256k1.preΨ' 5).map φcl).roots.toFinset :=
  Multiset.mem_toFinset.mpr (mem_roots'.mpr ⟨preΨ₅bar_ne_zero, ha⟩)

/-! ## `y ≠ 0` at the `preΨ₅`-roots, from the `Ψ₂Sq ⊥ preΨ₅` Bézout certificate

`CoprimePsi2Psi5.lean` states its certificate for exactly the objects used here:
`IsCoprime secp256k1.Ψ₂Sq (secp256k1.preΨ' 5)` over `𝔽_p[X]` — `preΨ' 5` *is* the
genuine univariate 5-division polynomial (odd index, no `ψ₂` factor), the same
polynomial whose mapped roots were counted above. It is transported to `𝔽̄_p[X]` via
`IsCoprime.map (Polynomial.mapRingHom φ)` exactly as `DivisionPolynomialCoprime.lean`
transports its certificates. -/

/-- Coprime polynomials over a field have no common root (Bézout, evaluated). Mirror of
the compiled lemma of `DivisionPolynomialCoprime.lean` (restated here because that
helper is private to its file). -/
private theorem no_common_root {K : Type*} [Field K] {F G : K[X]} (h : IsCoprime F G)
    {x₀ : K} (hF : F.eval x₀ = 0) (hG : G.eval x₀ = 0) : False := by
  obtain ⟨u, v, huv⟩ := h
  have h1 := congrArg (Polynomial.eval x₀) huv
  simp [hF, hG] at h1

/-- The `Ψ₂Sq ⊥ preΨ₅` certificate, transported to the algebraic closure. -/
private theorem preΨ₅bar_isCoprime_Ψ₂Sq :
    IsCoprime ((secp256k1.Ψ₂Sq).map φcl) ((secp256k1.preΨ' 5).map φcl) := by
  have h := secp256k1_isCoprime_Ψ₂Sq_preΨ₅.map (Polynomial.mapRingHom φcl)
  simpa only [Polynomial.coe_mapRingHom] using h

/-- The mapped `Ψ₂Sq`, evaluated: `4(x³ + 7)` (base change of the compiled closed
form `secp256k1_Ψ₂Sq = C 4 * X³ + C 28`). -/
private theorem Ψ₂Sqbar_eval (a : AlgebraicClosure (ZMod Secp256k1.p)) :
    ((secp256k1.Ψ₂Sq).map φcl).eval a = 4 * (a ^ 3 + 7) := by
  rw [secp256k1_Ψ₂Sq]
  simp only [Polynomial.map_add, Polynomial.map_mul, Polynomial.map_pow,
    Polynomial.map_C, Polynomial.map_X, Polynomial.map_ofNat, map_ofNat, eval_add,
    eval_mul, eval_pow, eval_C, eval_X, Polynomial.eval_ofNat]
  ring

/-- **At a root of the mapped `preΨ₅`, `x³ + 7 ≠ 0`**: otherwise `Ψ₂Sq = 4(X³+7)` and
`preΨ₅` would share the root, contradicting the transported Bézout certificate
`secp256k1_isCoprime_Ψ₂Sq_preΨ₅`. This is the "`y ≠ 0` on nonzero 5-torsion" input of
the `±y` pairing — exactly what that coprimality (`E[2] ⊥ E[5]`) was staged for. -/
private theorem x_cube_add_seven_ne_zero_of_root
    {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ' 5).map φcl).eval a = 0) : a ^ 3 + 7 ≠ 0 := by
  intro h7
  have hΨ2 : ((secp256k1.Ψ₂Sq).map φcl).eval a = 0 := by
    rw [Ψ₂Sqbar_eval]
    linear_combination 4 * h7
  exact no_common_root preΨ₅bar_isCoprime_Ψ₂Sq hΨ2 ha

/-- The chosen `y` over any `x` satisfies the curve equation. -/
private theorem liftY_sq (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    (liftY x) ^ 2 = x ^ 3 + 7 :=
  secp256k1Bar_curve_of_nonsingular x (liftY x) (liftY_nonsingular x)

/-- At a `preΨ₅`-root, the chosen `y` is nonzero (`y = 0` would force `x³ + 7 = 0`). -/
private theorem liftY_ne_zero {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ' 5).map φcl).eval a = 0) : liftY a ≠ 0 := by
  intro h0
  have hsq := liftY_sq a
  rw [h0] at hsq
  exact x_cube_add_seven_ne_zero_of_root ha (by linear_combination -hsq)

/-- At a `preΨ₅`-root, `y ≠ -y` (char `≠ 2` and `y ≠ 0`): the two lifted points differ. -/
private theorem liftY_ne_neg {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ' 5).map φcl).eval a = 0) : liftY a ≠ -liftY a := by
  intro h
  have h2 : (2 : AlgebraicClosure (ZMod Secp256k1.p)) * liftY a = 0 := by
    linear_combination h
  rcases mul_eq_zero.mp h2 with h2' | hy0
  · exact two_ne_zero_bar h2'
  · exact liftY_ne_zero ha hy0

/-! ## 5-torsion membership of the enumerated points -/

/-- The lifted point over a `preΨ₅`-root is 5-torsion (the bridge, `mpr` direction). -/
private theorem liftP_five_nsmul {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((secp256k1.preΨ' 5).map φcl).eval a = 0) : (5 : ℕ) • liftP a = 0 :=
  (secp256k1Bar_five_torsion_iff_root a (liftY a) (liftY_nonsingular a)).mpr ha

/-- 5-torsion is closed under negation (via the `torsionBy` subgroup). -/
private theorem five_nsmul_neg {P : secp256k1Bar.toAffine.Point}
    (hP : (5 : ℕ) • P = 0) : (5 : ℕ) • (-P) = 0 := by
  have h1 : P ∈ AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((5 : ℕ) : ℤ) :=
    AddSubgroup.torsionBy.nsmul_iff.mpr hP
  exact AddSubgroup.torsionBy.nsmul_iff.mp (neg_mem h1)

/-! ## The exact enumeration: `E[5] = {O} ∪ liftP '' roots ∪ (-liftP) '' roots` -/

/-- The explicit 25-element Finset has card `25`: `1 + 12 + 12`, with the two 12-element
images disjoint (a shared point would force `y = -y` at a root) and `0` in neither. -/
private theorem five_torsion_finset_card :
    (insert (0 : secp256k1Bar.toAffine.Point)
      ((((secp256k1.preΨ' 5).map φcl).roots.toFinset.image liftP)
        ∪ (((secp256k1.preΨ' 5).map φcl).roots.toFinset.image fun a => -liftP a))).card
      = 25 := by
  -- `liftP` is injective (project to the `x`-coordinate).
  have hinj1 : Set.InjOn liftP ↑(((secp256k1.preΨ' 5).map φcl).roots.toFinset) := by
    intro a _ b _ hab
    simp only [liftP_def, Point.some.injEq] at hab
    exact hab.1
  have hinj2 : Set.InjOn (fun a => -liftP a)
      ↑(((secp256k1.preΨ' 5).map φcl).roots.toFinset) := by
    intro a ha b hb hab
    have h' : -liftP a = -liftP b := hab
    exact hinj1 ha hb (neg_inj.mp h')
  -- The two images are disjoint: `liftP a = -liftP b` forces `a = b` and `y = -y`.
  have hdisj : Disjoint ((((secp256k1.preΨ' 5).map φcl).roots.toFinset).image liftP)
      ((((secp256k1.preΨ' 5).map φcl).roots.toFinset).image fun a => -liftP a) := by
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
    exact liftY_ne_neg (eval_of_mem_preΨ₅bar_roots haR) hyy.symm
  -- `0` is in neither image (affine points are not the point at infinity).
  have h0F : (0 : secp256k1Bar.toAffine.Point)
      ∉ (((secp256k1.preΨ' 5).map φcl).roots.toFinset.image liftP)
        ∪ (((secp256k1.preΨ' 5).map φcl).roots.toFinset.image fun a => -liftP a) := by
    intro h0
    rw [Finset.mem_union] at h0
    rcases h0 with h0 | h0 <;> rw [Finset.mem_image] at h0 <;> obtain ⟨a, -, ha⟩ := h0
    · rw [liftP_def] at ha
      exact Point.some_ne_zero (liftY_nonsingular a) ha
    · have ha' : liftP a = 0 := neg_eq_zero.mp ha
      rw [liftP_def] at ha'
      exact Point.some_ne_zero (liftY_nonsingular a) ha'
  -- Count: 1 + (12 + 12) = 25.
  have h1 := Finset.card_insert_of_notMem h0F
  have h2 := Finset.card_union_of_disjoint hdisj
  have h3 : ((((secp256k1.preΨ' 5).map φcl).roots.toFinset).image liftP).card = 12 :=
    (Finset.card_image_of_injOn hinj1).trans preΨ₅bar_roots_toFinset_card
  have h4 : ((((secp256k1.preΨ' 5).map φcl).roots.toFinset).image
      fun a => -liftP a).card = 12 :=
    (Finset.card_image_of_injOn hinj2).trans preΨ₅bar_roots_toFinset_card
  omega

/-- **The 5-torsion of `secp256k1Bar` is exactly the enumerated 25-element set.**
`⊇` is the bridge (`mpr`) plus closure under negation; `⊆` is the bridge (`mp`) plus
the `±√(x³+7)` dichotomy: `y² = (liftY x)²` forces `y = ±liftY x`. -/
private theorem five_torsion_set_eq :
    {P : secp256k1Bar.toAffine.Point | (5 : ℕ) • P = 0}
      = ↑(insert (0 : secp256k1Bar.toAffine.Point)
        ((((secp256k1.preΨ' 5).map φcl).roots.toFinset.image liftP)
          ∪ (((secp256k1.preΨ' 5).map φcl).roots.toFinset.image fun a => -liftP a))) := by
  ext P
  simp only [Set.mem_setOf_eq, Finset.mem_coe]
  constructor
  · intro hP
    rcases P with _ | ⟨x, y, h⟩
    · exact Finset.mem_insert_self 0 _
    · have hroot : ((secp256k1.preΨ' 5).map φcl).eval x = 0 :=
        (secp256k1Bar_five_torsion_iff_root x y h).mp hP
      have hxR : x ∈ ((secp256k1.preΨ' 5).map φcl).roots.toFinset :=
        mem_preΨ₅bar_roots_of_eval hroot
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
    · exact liftP_five_nsmul (eval_of_mem_preΨ₅bar_roots haR)
    · exact five_nsmul_neg (liftP_five_nsmul (eval_of_mem_preΨ₅bar_roots haR))

/-! ## The counting theorems -/

/-- **`#E[5](𝔽̄_p) = 25`** (set form). The 5-torsion of `secp256k1Bar` is exactly
`{O} ∪ {(x, ±y) : preΨ₅(x) = 0}`: the mapped `preΨ₅` has exactly `12` distinct roots
(`secp256k1_preΨ₅_roots_card_bar`), each carrying exactly two points `(x, ±y)` with
`y ≠ 0` (`secp256k1_isCoprime_Ψ₂Sq_preΨ₅`, transported), so `#E[5] = 2·12 + 1 = 25`
on the nose — the counting half of N13 at `n = 5`. -/
theorem secp256k1Bar_five_torsion_ncard :
    Set.ncard {P : secp256k1Bar.toAffine.Point | (5 : ℕ) • P = 0} = 25 := by
  rw [five_torsion_set_eq, Set.ncard_coe_finset]
  exact five_torsion_finset_card

/-- **`#E[5](𝔽̄_p) = 25`** (`Nat.card` subtype form) — definitional reuse of the set
form, exactly as the compiled `secp256k1Bar_three_torsion_card`
(`ThreeTorsionStructure.lean`). -/
theorem secp256k1Bar_five_torsion_card :
    Nat.card {P : secp256k1Bar.toAffine.Point // (5 : ℕ) • P = 0} = 25 :=
  secp256k1Bar_five_torsion_ncard

/-- **`#E[5](𝔽̄_p) = 25`** (torsion-subgroup form): the cardinality of Mathlib's
`AddSubgroup.torsionBy` at `n = 5`, the vocabulary of `Torsion.lean` /
`CurveTorsion.lean`. Membership rewrites to `5 • P = 0` by
`AddSubgroup.torsionBy.nsmul_iff`. -/
theorem secp256k1Bar_torsionBy_five_card :
    Nat.card
      ↥(AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((5 : ℕ) : ℤ)) = 25 := by
  have he : ↥(AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((5 : ℕ) : ℤ))
      ≃ {P : secp256k1Bar.toAffine.Point // (5 : ℕ) • P = 0} :=
    Equiv.subtypeEquivRight fun _ => AddSubgroup.torsionBy.nsmul_iff
  rw [Nat.card_congr he]
  exact secp256k1Bar_five_torsion_card

/-! ## The structure theorem: N13 at `n = 5` -/

/-- **`E[5](𝔽̄_p) ≅ ℤ/5 × ℤ/5` — the second full N13 instance.** The 5-torsion subgroup
of the closure curve is killed by the prime `5` (definitionally, as a `torsionBy`
subgroup) and has exactly `5² = 25` elements, so the kernel-structure lemma N10(iii)
(`Ecdlp.Torsion.nonempty_addEquiv_zmod_prod_of_card_eq_sq`) classifies it as
`(ℤ/5)²` — the full 2-dimensional `𝔽₅`-plane predicted by the theory of elliptic
curves over algebraically closed fields of characteristic prime to `n`. -/
theorem secp256k1Bar_five_torsion_structure :
    Nonempty
      (↥(AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((5 : ℕ) : ℤ))
        ≃+ ZMod 5 × ZMod 5) := by
  haveI : Fact (Nat.Prime 5) := ⟨by norm_num⟩
  exact Ecdlp.Torsion.nonempty_addEquiv_zmod_prod_of_card_eq_sq
    (fun a => AddSubgroup.torsionBy.nsmul a)
    (secp256k1Bar_torsionBy_five_card.trans (by norm_num))

end Ecdlp.Curve
