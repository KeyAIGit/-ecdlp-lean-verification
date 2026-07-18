import Mathlib
import Ecdlp.Proved.DivisionPolynomialEvalBridge
import Ecdlp.Proved.DivisionResultantTransport
import Ecdlp.Proved.CubicSeparable
import Ecdlp.Proved.TorsionStructure
import Ecdlp.Proved.FiveTorsionBridgeBar

/-!
# N13 at `n = 2`: `#E[2](𝔽̄_p) = 4` and `E[2](𝔽̄_p) ≅ ℤ/2 × ℤ/2`

The **even completion** of the `N13` torsion-structure family to `n ∈ {2, 3, 5, 7}` (every
prime for which a closure bridge has landed): for `secp256k1Bar` — secp256k1 base-changed to
`𝔽̄_p := AlgebraicClosure (ZMod Secp256k1.p)` — the 2-torsion subgroup has **exactly `4`
points** and is `≃+ ZMod 2 × ZMod 2`.

## Why the even case is structurally simpler

For `n = 2` there is **no division-polynomial multiplication formula** to invoke: a point
`P` is `2`-torsion iff it is its own negation,

  `2 • P = 0  ⟺  P = -P  ⟺  y = negY x y = -y  ⟺  2y = 0  ⟺  y = 0`   (char `≠ 2`),

and an affine curve point with `y = 0` is exactly `(x, 0)` with `x³ + 7 = 0` (from the curve
equation `y² = x³ + 7`). So

  `E[2](𝔽̄_p) = {O} ∪ {(x, 0) : x³ + 7 = 0}`,

and `X³ + 7` has exactly `3` distinct roots over `𝔽̄_p` (`CubicSeparable.lean`: it is
separable — its derivative `3X²` vanishes only at `x = 0`, where `x³ + 7 = 7 ≠ 0`). There is
**no `±y` split** (the `y = 0` fibre is a single point per root), so the count is
`1 + 3 = 4 = 2²` directly. The group is killed by `2` because every element is its own
negation.

## What this composes (nothing new is certified here — pure assembly)

* **The closure 2-torsion characterization** (this file, Step 2):
  `2 • (x, y) = 0 ⟺ y = 0`, the port of `TwoTorsionPoint.lean` to `secp256k1Bar` (the
  mapped-coefficient `negY = -y`, and `2 ≠ 0` transported from `𝔽_p`).
* **The exact root count** (`CubicSeparable.lean`): `X³ + 7` has exactly `3` distinct roots
  in `𝔽̄_p` (`secp256k1_cubic_roots_card_bar` + `secp256k1_cubic_roots_nodup_bar`).
* **The kernel-structure lemma N10(iii)** (`TorsionStructure.lean`): a group of order
  `2² = 4` killed by the prime `2` is `(ℤ/2)²`
  (`Ecdlp.Torsion.nonempty_addEquiv_zmod_prod_of_card_eq_sq`).

## Honest scope

This closes the structure result **only at `n = 2`** (and `#E[2] = 4` is here the exact
closure count, upgrading the `𝔽_p`-side bound `secp256k1_two_torsion_ncard_le (≤ 4)` of
`TwoTorsionCount.lean`). The uniform-`n` counting/separability program (`#E[n] = n²` for all
`n` prime to `p`, the general N10 core) remains open; `n = 2` is the specific small even case,
completing the landed-bridge family `{2, 3, 5, 7}`.

## Classical decidability

Mathlib's affine group law is stated under `[DecidableEq F]`, and `𝔽̄_p` has no computable
equality; following `DivisionResultantTransport.lean` / `ThreeTorsionStructure.lean` this file
works under `open scoped Classical`. All classical `Decidable` instances on the same
proposition are definitionally equal, so the statements compose with any classical
instantiation chosen by consumers.
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

/-- **`secp256k1Bar` is an elliptic curve.** Registered file-locally (`private`) — instance
search does not unfold the `secp256k1Bar` definition to see it is a `.map`, so Mathlib's
instance for `W.map f` must be pointed at explicitly (as in `ThreeTorsionStructure.lean`). -/
private instance secp256k1Bar_isElliptic_two : secp256k1Bar.IsElliptic :=
  inferInstanceAs ((secp256k1.map φcl).IsElliptic)

/-! ## Coefficient extraction for the mapped curve (`aᵢ` are base-change images) -/

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

/-! ## Lifting an `x`-coordinate to a curve point (identical scaffold to the odd files)

Over the algebraically closed field every `x` carries a point `(x, liftY x)` of
`secp256k1Bar` (`exists_nonsingular_y`, `DivisionResultantTransport.lean`). At a root of the
2-torsion cubic the chosen `y` is *forced* to `0` (`y² = x³ + 7 = 0`), so `liftP` lands on the
canonical 2-torsion point `(x, 0)` — no `±y` choice is involved. -/

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

/-- The chosen `y` over any `x` satisfies the curve equation. -/
private theorem liftY_sq (x : AlgebraicClosure (ZMod Secp256k1.p)) :
    (liftY x) ^ 2 = x ^ 3 + 7 :=
  secp256k1Bar_curve_of_nonsingular x (liftY x) (liftY_nonsingular x)

/-- **At a root of `X³ + 7`, the chosen `y` is `0`** (the `y = 0` fibre): `(liftY x)² =
x³ + 7 = 0` forces `liftY x = 0`. This is the even-case replacement for the odd files'
`y ≠ 0`/`±y`-pairing argument — here `y` is uniquely `0`. -/
private theorem liftY_eq_zero_of_root {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : a ^ 3 + 7 = 0) : liftY a = 0 := by
  have h2 : (liftY a) ^ 2 = 0 := by rw [liftY_sq a, ha]
  exact (pow_eq_zero_iff (by norm_num : 2 ≠ 0)).mp h2

/-! ## The mapped 2-torsion cubic `X³ + 7` over `𝔽̄_p` -/

/-- The mapped cubic evaluated: `(X³ + 7).map φ` at `a` is `a³ + 7`. -/
private theorem cubicbar_eval (a : AlgebraicClosure (ZMod Secp256k1.p)) :
    ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).eval a = a ^ 3 + 7 := by
  simp only [Polynomial.map_add, Polynomial.map_pow, Polynomial.map_X,
    Polynomial.map_ofNat, map_ofNat, eval_add, eval_pow, eval_X, Polynomial.eval_ofNat]

/-- Exactly `3` roots over `𝔽̄_p`, restated in this file's vocabulary. -/
private theorem cubicbar_roots_card :
    ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).roots.card = 3 :=
  secp256k1_cubic_roots_card_bar

/-- The `3` roots are pairwise distinct, restated in this file's vocabulary. -/
private theorem cubicbar_roots_nodup :
    ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).roots.Nodup :=
  secp256k1_cubic_roots_nodup_bar

/-- The mapped cubic is nonzero (it has `3` roots; the zero polynomial has none). -/
private theorem cubicbar_ne_zero :
    (X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl ≠ 0 := by
  intro h0
  have hc := cubicbar_roots_card
  rw [h0, Polynomial.roots_zero] at hc
  simp at hc

/-- The dedup'd root Finset has exactly `3` elements (`Nodup` makes `toFinset` lossless). -/
private theorem cubicbar_roots_toFinset_card :
    ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).roots.toFinset.card = 3 := by
  have h := Multiset.toFinset_card_of_nodup cubicbar_roots_nodup
  rw [cubicbar_roots_card] at h
  exact h

private theorem eval_of_mem {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : a ∈ ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).roots.toFinset) :
    ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).eval a = 0 :=
  (mem_roots'.mp (Multiset.mem_toFinset.mp ha)).2

private theorem mem_of_eval {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).eval a = 0) :
    a ∈ ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).roots.toFinset :=
  Multiset.mem_toFinset.mpr (mem_roots'.mpr ⟨cubicbar_ne_zero, ha⟩)

/-! ## Step 2: the closure 2-torsion characterization `2 • P = 0 ⟺ y = 0` -/


/-- The lifted point over a root of `X³ + 7` is 2-torsion (the bridge, `mpr` direction):
the root forces `liftY a = 0`, and `y = 0` is 2-torsion. -/
private theorem liftP_two_nsmul {a : AlgebraicClosure (ZMod Secp256k1.p)}
    (ha : ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).eval a = 0) :
    (2 : ℕ) • liftP a = 0 := by
  have ha' : a ^ 3 + 7 = 0 := by rw [← cubicbar_eval]; exact ha
  rw [liftP_def]
  exact (secp256k1Bar_two_nsmul_eq_zero_iff a (liftY a) (liftY_nonsingular a)).mpr
    (liftY_eq_zero_of_root ha')

/-! ## Step 3: the exact enumeration `E[2] = {O} ∪ {(x, 0) : x³ + 7 = 0}` -/

/-- The explicit 4-element Finset has card `4`: `1 + 3`, with `liftP` injective on the
`3`-element root set (project to `x`) and `0` not in its image (affine points are not `O`).
No `±y` split — each root contributes a single point `(x, 0)`. -/
private theorem two_torsion_finset_card :
    (insert (0 : secp256k1Bar.toAffine.Point)
      (((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).roots.toFinset.image liftP)).card
      = 4 := by
  have hinj : Set.InjOn liftP
      ↑(((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).roots.toFinset) := by
    intro a _ b _ hab
    simp only [liftP_def, Point.some.injEq] at hab
    exact hab.1
  have h0F : (0 : secp256k1Bar.toAffine.Point)
      ∉ ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).roots.toFinset.image liftP := by
    intro h0
    rw [Finset.mem_image] at h0
    obtain ⟨a, -, ha⟩ := h0
    rw [liftP_def] at ha
    exact Point.some_ne_zero (liftY_nonsingular a) ha
  have h1 := Finset.card_insert_of_notMem h0F
  have h3 : (((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).roots.toFinset.image liftP).card
      = 3 := (Finset.card_image_of_injOn hinj).trans cubicbar_roots_toFinset_card
  omega

/-- **The 2-torsion of `secp256k1Bar` is exactly the enumerated 4-element set.**
`⊆` is the bridge (`mp`): `2 • P = 0` forces `y = 0` and hence `x³ + 7 = 0`, so `P = (x, 0) =
liftP x` at a cubic root. `⊇` is the bridge (`mpr`) via `liftP_two_nsmul`. -/
private theorem two_torsion_set_eq :
    {P : secp256k1Bar.toAffine.Point | (2 : ℕ) • P = 0}
      = ↑(insert (0 : secp256k1Bar.toAffine.Point)
        (((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).roots.toFinset.image liftP)) := by
  ext P
  simp only [Set.mem_setOf_eq, Finset.mem_coe]
  constructor
  · intro hP
    rcases P with _ | ⟨x, y, h⟩
    · exact Finset.mem_insert_self 0 _
    · have hy : y = 0 := (secp256k1Bar_two_nsmul_eq_zero_iff x y h).mp hP
      subst hy
      have hc : (0 : AlgebraicClosure (ZMod Secp256k1.p)) ^ 2 = x ^ 3 + 7 :=
        secp256k1Bar_curve_of_nonsingular x 0 h
      have hx3 : x ^ 3 + 7 = 0 := by linear_combination -hc
      have hxroot : ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φcl).eval x = 0 := by
        rw [cubicbar_eval]; exact hx3
      have hxR := mem_of_eval hxroot
      have hlift0 : liftY x = 0 := liftY_eq_zero_of_root hx3
      refine Finset.mem_insert_of_mem (Finset.mem_image.mpr ⟨x, hxR, ?_⟩)
      rw [liftP_def, Point.some.injEq]
      exact ⟨rfl, hlift0⟩
  · intro hP
    rw [Finset.mem_insert] at hP
    rcases hP with rfl | hP
    · simp
    · rw [Finset.mem_image] at hP
      obtain ⟨a, haR, rfl⟩ := hP
      exact liftP_two_nsmul (eval_of_mem haR)

/-! ## The counting theorems -/

/-- **`#E[2](𝔽̄_p) = 4`** (set form). The 2-torsion of `secp256k1Bar` is exactly
`{O} ∪ {(x, 0) : x³ + 7 = 0}`: the mapped `X³ + 7` has exactly `3` distinct roots
(`secp256k1_cubic_roots_card_bar`), each carrying the single point `(x, 0)` (the `y = 0`
fibre), so `#E[2] = 3 + 1 = 4` on the nose. This upgrades the compiled `𝔽_p`-side bound
`secp256k1_two_torsion_ncard_le (≤ 4)` (`TwoTorsionCount.lean`) to an exact closure count. -/
theorem secp256k1Bar_two_torsion_ncard :
    Set.ncard {P : secp256k1Bar.toAffine.Point | (2 : ℕ) • P = 0} = 4 := by
  rw [two_torsion_set_eq, Set.ncard_coe_finset]
  exact two_torsion_finset_card

/-- **`#E[2](𝔽̄_p) = 4`** (`Nat.card` subtype form) — definitional reuse of the set form. -/
theorem secp256k1Bar_two_torsion_card :
    Nat.card {P : secp256k1Bar.toAffine.Point // (2 : ℕ) • P = 0} = 4 :=
  secp256k1Bar_two_torsion_ncard

/-- **`#E[2](𝔽̄_p) = 4`** (torsion-subgroup form): the cardinality of Mathlib's
`AddSubgroup.torsionBy` at `n = 2`. Membership rewrites to `2 • P = 0` by
`AddSubgroup.torsionBy.nsmul_iff`. -/
theorem secp256k1Bar_torsionBy_two_card :
    Nat.card
      ↥(AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((2 : ℕ) : ℤ)) = 4 := by
  have he : ↥(AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((2 : ℕ) : ℤ))
      ≃ {P : secp256k1Bar.toAffine.Point // (2 : ℕ) • P = 0} :=
    Equiv.subtypeEquivRight fun _ => AddSubgroup.torsionBy.nsmul_iff
  rw [Nat.card_congr he]
  exact secp256k1Bar_two_torsion_card

/-! ## The structure theorem: N13 at `n = 2` -/

/-- **`E[2](𝔽̄_p) ≅ ℤ/2 × ℤ/2` — N13 at `n = 2`, completing the family to `{2, 3, 5, 7}`.**
The 2-torsion subgroup of the closure curve is killed by the prime `2` (definitionally, as a
`torsionBy` subgroup — every element is its own negation) and has exactly `2² = 4` elements,
so the kernel-structure lemma N10(iii)
(`Ecdlp.Torsion.nonempty_addEquiv_zmod_prod_of_card_eq_sq`) classifies it as `(ℤ/2)²` — the
full 2-dimensional `𝔽₂`-plane predicted by the theory of elliptic curves over algebraically
closed fields of characteristic prime to `n`. -/
theorem secp256k1Bar_two_torsion_structure :
    Nonempty
      (↥(AddSubgroup.torsionBy secp256k1Bar.toAffine.Point ((2 : ℕ) : ℤ))
        ≃+ ZMod 2 × ZMod 2) := by
  haveI : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩
  exact Ecdlp.Torsion.nonempty_addEquiv_zmod_prod_of_card_eq_sq
    (fun a => AddSubgroup.torsionBy.nsmul a)
    (secp256k1Bar_torsionBy_two_card.trans (by norm_num))

end Ecdlp.Curve
