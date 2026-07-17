import Mathlib
import Ecdlp.Proved.TorsionStructure

/-!
# The generic torsion-counting core: `Nat.card T = 2·m + 1` from a 2:1 cover

The three per-`ℓ` structure files (`{Three,Five,Seven}TorsionStructure.lean`,
`ℓ = 3, 5, 7`) each re-prove the same counting argument: the nonzero `ℓ`-torsion of the
closure curve is covered, exactly two-to-one, by the `m = (ℓ² − 1)/2` distinct roots of
a division polynomial, so `#E[ℓ] = 2m + 1 = ℓ²`, and the kernel-structure lemma N10(iii)
(`TorsionStructure.lean`) upgrades the count to `E[ℓ] ≅ (ℤ/ℓ)²`. This file extracts that
counting argument **once**, with no elliptic-curve theory at all:

* `torsion_card_of_divpoly_data` — a type `T` with a distinguished zero, a finset `R`
  of "roots" with `R.card = m`, two sections `pos, neg : K → T` hitting each root fiber
  in two distinct nonzero elements, and a cover of the nonzero part of `T` by those two
  sections, force `Nat.card T = 2·m + 1`. Finiteness of `T` is **derived** — the cover
  exhausts `T` by the explicit finset `{0} ∪ pos '' R ∪ neg '' R` — never assumed: no
  `Fintype`/`Finite` hypothesis appears, and the statement itself is decidability-free
  (the `DecidableEq` needed for the enumeration finset lives only inside the proof, so
  no classical instance is baked into the statement).

* `nonempty_addEquiv_zmod_prod_of_divpoly_data` — the composition with the compiled
  N10(iii) lemma `nonempty_addEquiv_zmod_prod_of_card_eq_sq`: if moreover `T` is an
  `AddCommGroup` killed by a prime `n` (`∀ t, n • t = 0`) and `2·m + 1 = n²`, then
  `Nonempty (T ≃+ ZMod n × ZMod n)`.

## Honest scope — what is NOT proved here

* **No curve, no polynomial, no field.** `R` is an arbitrary finset; that it is the
  root set of a division polynomial, that its cardinality is `(n² − 1)/2`, that each
  root carries an actual curve point `(x, ±y)` with `y ≠ 0`, and that torsion points
  project into `R` (the bridge iff) are the *caller's* obligations. All the
  arithmetic-geometric content — `char ≠ 2` for `pos r ≠ neg r`, `char ≠ n` and
  separability behind the root count, `IsAlgClosed` for the roots→points lift — is
  consumed upstream to *construct* the hypotheses; none of it appears, or is checked,
  here. Callers instantiating with `E(F)[n]` for `F` not algebraically closed simply
  cannot discharge the hypotheses (for secp256k1 over `𝔽_p` itself the cover data does
  not exist).
* The distinguished zero (the point `O` at the intended call sites) is counted by the
  `+ 1`, but the counting lemma does not identify it with a group identity — `[Zero T]`
  is all that is assumed there.
* "Exactly two per fiber" is encoded by the section data, not stated as a fiber
  cardinality: over each `r ∈ R` the fiber of `proj` contains the two distinct nonzero
  elements `pos r ≠ neg r`, and by `hcover` nothing else. No claim is made about
  fibers over `K \ R` (both sections may be junk there).
* The structure corollary produces a `Nonempty` — a noncomputable choice of
  isomorphism. No canonical basis, no Galois-equivariance, no pairing compatibility.
* For `n = 2` the side condition `2·m + 1 = n²` is unsatisfiable (odd ≠ 4), so the
  corollary is silently inapplicable — even torsion has a 1:1 (`y = 0`) fiber and must
  go through a different count, cf. `TwoTorsionCount.lean`.
-/

namespace Ecdlp.Torsion

/-- **The abstract 2:1-cover count.** If the nonzero part of `T` is covered by a finset
`R` of `m` "roots", two elements per root — the sections `pos, neg : K → T` are nonzero
on `R`, are split by the projection `proj` (`proj (pos r) = r = proj (neg r)`, which
forces both to be injective on `R`), are distinct fiberwise (`pos r ≠ neg r`), and every
nonzero `t : T` is `pos (proj t)` or `neg (proj t)` with `proj t ∈ R` — then
`Nat.card T = 2·m + 1`.

Pure counting: `T` carries only a distinguished zero. Finiteness is derived, not
assumed — the hypotheses exhaust `T` by the explicit finset
`{0} ∪ R.image pos ∪ R.image neg`, whose card is `1 + m + m`. At the intended call
sites `T` is a `torsionBy` subgroup of a curve's point group, `proj` the `x`-coordinate,
`pos`/`neg` the `(x, ±y)` lifts, and `R` the root set of a division polynomial; nothing
in the statement knows any of that. -/
theorem torsion_card_of_divpoly_data
    {T K : Type*} [Zero T] {m : ℕ}
    (R : Finset K) (hR : R.card = m)
    (proj : T → K) (pos neg : K → T)
    (hpos_zero : ∀ r ∈ R, pos r ≠ 0)
    (hneg_zero : ∀ r ∈ R, neg r ≠ 0)
    (hproj_pos : ∀ r ∈ R, proj (pos r) = r)
    (hproj_neg : ∀ r ∈ R, proj (neg r) = r)
    (hpos_neg : ∀ r ∈ R, pos r ≠ neg r)
    (hcover : ∀ t : T, t ≠ 0 → proj t ∈ R ∧ (t = pos (proj t) ∨ t = neg (proj t))) :
    Nat.card T = 2 * m + 1 := by
  classical
  -- `pos` and `neg` are injective on `R`: `proj` recovers the root.
  have hinjpos : Set.InjOn pos ↑R := by
    intro r hr r' hr' hEq
    have h1 : r = proj (pos r) := (hproj_pos r (Finset.mem_coe.mp hr)).symm
    rw [hEq, hproj_pos r' (Finset.mem_coe.mp hr')] at h1
    exact h1
  have hinjneg : Set.InjOn neg ↑R := by
    intro r hr r' hr' hEq
    have h1 : r = proj (neg r) := (hproj_neg r (Finset.mem_coe.mp hr)).symm
    rw [hEq, hproj_neg r' (Finset.mem_coe.mp hr')] at h1
    exact h1
  -- The two images are disjoint: a shared element would force `pos r = neg r`.
  have hdisjPN : Disjoint (R.image pos) (R.image neg) := by
    rw [Finset.disjoint_left]
    intro t htP htN
    obtain ⟨r, hr, hPr⟩ := Finset.mem_image.mp htP
    obtain ⟨r', hr', hNr⟩ := Finset.mem_image.mp htN
    have h1 : proj t = r := by rw [← hPr]; exact hproj_pos r hr
    have h2 : proj t = r' := by rw [← hNr]; exact hproj_neg r' hr'
    have hrr' : r = r' := h1.symm.trans h2
    subst hrr'
    exact hpos_neg r hr (hPr.trans hNr.symm)
  -- `0` lies in neither image.
  have hdisj0 : Disjoint ({0} : Finset T) (R.image pos ∪ R.image neg) := by
    rw [Finset.disjoint_left]
    intro t ht htU
    rw [Finset.mem_singleton] at ht
    subst ht
    rcases Finset.mem_union.mp htU with h | h
    · obtain ⟨r, hr, hPr⟩ := Finset.mem_image.mp h
      exact hpos_zero r hr hPr
    · obtain ⟨r, hr, hNr⟩ := Finset.mem_image.mp h
      exact hneg_zero r hr hNr
  -- The cover data makes the explicit finset exhaust `T` …
  have hall : ∀ t : T, t ∈ ({0} : Finset T) ∪ (R.image pos ∪ R.image neg) := by
    intro t
    simp only [Finset.mem_union, Finset.mem_singleton, Finset.mem_image]
    by_cases ht : t = 0
    · exact Or.inl ht
    · obtain ⟨hmem, hor⟩ := hcover t ht
      rcases hor with h | h
      · exact Or.inr (Or.inl ⟨proj t, hmem, h.symm⟩)
      · exact Or.inr (Or.inr ⟨proj t, hmem, h.symm⟩)
  -- … so the whole type *is* that finset; in particular `T` is finite.
  have huniv : (Set.univ : Set T)
      = ↑(({0} : Finset T) ∪ (R.image pos ∪ R.image neg)) :=
    (Set.eq_univ_of_forall fun t => Finset.mem_coe.mpr (hall t)).symm
  -- Count: `1 + (m + m) = 2m + 1`.
  calc Nat.card T
      = (Set.univ : Set T).ncard := (Set.ncard_univ T).symm
    _ = (↑(({0} : Finset T) ∪ (R.image pos ∪ R.image neg)) : Set T).ncard := by
        rw [huniv]
    _ = (({0} : Finset T) ∪ (R.image pos ∪ R.image neg)).card :=
        Set.ncard_coe_finset _
    _ = 2 * m + 1 := by
        rw [Finset.card_union_of_disjoint hdisj0,
          Finset.card_union_of_disjoint hdisjPN, Finset.card_singleton,
          Finset.card_image_of_injOn hinjpos, Finset.card_image_of_injOn hinjneg, hR]
        omega

/-- **Count + exponent ⇒ structure, in one call.** The 2:1-cover data gives
`Nat.card T = 2·m + 1`; the side condition `2·m + 1 = n²` (discharged by `norm_num` at
concrete call sites, e.g. `2·4 + 1 = 3²`) turns it into the exact hypothesis format of
the compiled N10(iii) lemma `nonempty_addEquiv_zmod_prod_of_card_eq_sq`
(`Nat.card T = n ^ 2`, kill hypothesis `∀ t, n • t = 0` with ℕ-scalars, `Fact n.Prime`
instance), which classifies `T ≃+ ZMod n × ZMod n` — mere existence, no canonical
isomorphism.

For `n = 2` the side condition is unsatisfiable, so no oddness hypothesis is needed:
the corollary simply cannot be invoked there. -/
theorem nonempty_addEquiv_zmod_prod_of_divpoly_data
    {T K : Type*} [AddCommGroup T] {n m : ℕ} [Fact n.Prime]
    (R : Finset K) (hR : R.card = m) (hsq : 2 * m + 1 = n ^ 2)
    (proj : T → K) (pos neg : K → T)
    (hpos_zero : ∀ r ∈ R, pos r ≠ 0)
    (hneg_zero : ∀ r ∈ R, neg r ≠ 0)
    (hproj_pos : ∀ r ∈ R, proj (pos r) = r)
    (hproj_neg : ∀ r ∈ R, proj (neg r) = r)
    (hpos_neg : ∀ r ∈ R, pos r ≠ neg r)
    (hcover : ∀ t : T, t ≠ 0 → proj t ∈ R ∧ (t = pos (proj t) ∨ t = neg (proj t)))
    (hkill : ∀ t : T, n • t = 0) :
    Nonempty (T ≃+ ZMod n × ZMod n) :=
  nonempty_addEquiv_zmod_prod_of_card_eq_sq hkill
    ((torsion_card_of_divpoly_data R hR proj pos neg hpos_zero hneg_zero
      hproj_pos hproj_neg hpos_neg hcover).trans hsq)

end Ecdlp.Torsion
