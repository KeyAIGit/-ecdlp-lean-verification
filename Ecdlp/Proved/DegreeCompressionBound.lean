import Mathlib

/-!
# Fibres of a one-variable polynomial map: a `Finset`-level degree bound

Every fibre of `Polynomial.eval · p` is the root set of `p - C y`, hence has at most
`p.natDegree` points. This file states that at the level of an **arbitrary `Finset R`**,
together with the two counting corollaries that follow: a `k`-element target set pulls back
to at most `natDegree p * k` points, and the image of a finite set `s` has at least
`#s / natDegree p` points.

## Relation to Mathlib v4.31.0

Mathlib already has, over the *whole* domain:

* `Polynomial.card_roots'` (`Mathlib/Algebra/Polynomial/Roots.lean:79`) —
  `Multiset.card p.roots ≤ natDegree p`.
* `Polynomial.card_roots_sub_C'` (`Roots.lean:91`) —
  `0 < degree p → Multiset.card (p - C a).roots ≤ natDegree p`.
* `Polynomial.card_le_degree_of_subset_roots` (`Roots.lean:136`) —
  `Z.val ⊆ p.roots → #Z ≤ p.natDegree`.
* `Polynomial.preimage_eval_singleton` (`Roots.lean:628`) —
  `p ≠ C a → p.eval ⁻¹' {a} = (p - C a).rootSet R`.
* `Polynomial.ncard_rootSet_le` (`Roots.lean:947`) —
  `Set.ncard (p.rootSet B) ≤ p.natDegree`.
* `FiniteField.card_image_polynomial_eval` (`Mathlib/FieldTheory/Finite/Basic.lean:74`) —
  `0 < p.degree → Fintype.card R ≤ natDegree p * #(univ.image fun x => eval x p)`.

Note in particular that the fibre bound **is** already available in Mathlib in `Set`/`ncard`
form: `preimage_eval_singleton` composed with `ncard_rootSet_le` gives
`Set.ncard (p.eval ⁻¹' {y}) ≤ p.natDegree` in two named steps. What this file adds is the
three things that composition does not give:

1. **The `Finset` form relative to an arbitrary `s : Finset R`.** Everything above is either
   `Set.ncard` over the whole domain or `Finset` over `univ`. Screening a proposed subset of a
   field needs `#{x ∈ s | p.eval x = y}` for a general `s`, and the `Set.ncard` route would
   have to be pushed back through `Set.ncard_coe_finset` at each use site.
2. **The preimage-into-a-set form** `#{x ∈ s | p.eval x ∈ T} ≤ p.natDegree * #T`, absent in
   any form. (Mathlib does prove the single-fibre `Finset` step inside
   `card_image_polynomial_eval` at `Basic.lean:76-81`, but only as an anonymous
   `fun a _ => calc …` subterm, so it cannot be applied.)
3. **The subset generalisation of `card_image_polynomial_eval`** from `univ` to any `s`
   (`card_le_natDegree_mul_card_image`); `card_image_polynomial_eval_of_degree_pos` below
   recovers the Mathlib statement from it, so the generalisation is genuine.

## The hypothesis

For a *single* fibre over `y` the sharp hypothesis is `p ≠ C y` — the same hypothesis Mathlib
uses in `preimage_eval_singleton`. `p ≠ 0` is **not** enough uniformly in `y`: for a nonzero
constant `p = C c` we have `natDegree p = 0` while the fibre over `c` is all of `R`. Brute
force over `𝔽₅, 𝔽₇, 𝔽₁₁` and all `p ≠ 0` of degree `≤ 3` finds exactly **20** violating pairs
`(p, y)` of "`p ≠ 0 → #fibre ≤ natDegree p`" — one for each of the `4 + 6 + 10` nonzero
constants, and none at positive degree. `0 < p.natDegree` is therefore the uniform-in-`y`
strengthening (`card_fibre_le_natDegree'`), and is what the multi-fibre corollaries need.
For the root fibre `y = 0` the sharp hypothesis is just `p ≠ 0` (`C 0 = 0`); that case is
spelled out as `card_le_natDegree_of_forall_isRoot`.

The bound is tight: over `𝔽₇`, `p = X ^ 3` has fibres of size exactly `3 = natDegree p`
over `y = 1` and `y = 6` (and size `1` over `0`, `0` elsewhere).

## Relation to existing repository proofs

`Ecdlp/Proved/SemaevDegree.lean:63-73` re-derives the chain
`Finset.card_le_card → Multiset.toFinset_card_le → Polynomial.card_roots' → natDegree`
by hand for one concrete polynomial; `Ecdlp/Proved/FourTorsionCount.lean:68` and `:113` do the
same for the `Multiset → Finset` part, and `:139` calls `Finset.card_le_mul_card_image` by hand.
Those are the sites this file abstracts. By contrast
`Ecdlp/Proved/DivisionPolynomialDegree.lean:36`, `Ecdlp/Proved/FiveTorsion.lean:51` and
`Ecdlp/Proved/ElevenTorsion.lean:54` are *`Multiset`-level* one-liners
(`(card_roots' _).trans _`) that mention no `Finset` at all; nothing here replaces them.

## Honest scope — what is NOT proved here

* This is a counting statement about **fibres of one-variable polynomial maps over an integral
  domain**. It is not a statement about ECDLP hardness, discrete-log cost, index calculus, or
  the security of any curve. Nothing here lower-bounds the work an algorithm must do.
* The two corollaries point in **opposite directions and must not be conflated**:
  * `card_preimage_le_natDegree_mul` is an **upper** bound on a carved-out set:
    `{x ∈ s | p.eval x ∈ T}` has at most `natDegree p * #T` elements, *independently of `#s`*.
    It does **not** say such a set is large; it can be empty. As a screen it refutes a claim of
    the form "my subset is cut out by a degree-`d` condition landing in a `k`-element target,
    and it has more than `d * k` elements".
  * `card_le_natDegree_mul_card_image` / `card_div_natDegree_le_card_image` are a **lower**
    bound on an image: `p` cannot compress `s` by a factor better than `natDegree p`. That is a
    statement about `s.image (p.eval ·)`, not about any subset of `s`.
* Applying either to a concrete proposal requires **separately** showing that the proposal has
  this shape. A set defined by a subgroup, a lattice condition, a multivariate relation, or an
  algebraic set of positive dimension is simply out of scope; surviving this screen is not
  soundness.
* **One variable only.** Semaev summation polynomials are multivariate; this file says nothing
  about them, and the naive fibre count does not transfer. (Mathlib's multivariate analogue is
  the Schwartz–Zippel bound, `Mathlib/Algebra/MvPolynomial/SchwartzZippel.lean`, which is a
  different and weaker statement.)
* No claim that a small image is *achievable*, that the image is computable, or that
  membership in it is decidable in useful time.
* `natDegree` of the zero polynomial is `0`, so `0 < p.natDegree` silently excludes `p = 0`;
  no separate nondegeneracy hypothesis is stated.
-/

namespace Ecdlp.Screen

open Finset Polynomial

variable {R : Type*} [CommRing R] [IsDomain R] [DecidableEq R]

/-! ## The fibre bound -/

/-- A polynomial of positive `natDegree` is not a constant. Bridges the sharp per-fibre
hypothesis `p ≠ C y` to the uniform one `0 < p.natDegree`. -/
theorem ne_C_of_natDegree_pos {p : R[X]} (hp : 0 < p.natDegree) (y : R) : p ≠ C y := by
  intro hpc
  rw [hpc, Polynomial.natDegree_C] at hp
  omega

/-- **Fibre bound, subset form.** A finite set on which `p` is constantly `y` has at most
`natDegree p` elements, provided `p` is not the constant `C y`. This is the shape the existing
hand-rolled proofs in `Ecdlp/Proved/` consume. -/
theorem card_le_natDegree_of_forall_eval_eq {p : R[X]} {y : R} (hp : p ≠ C y) {s : Finset R}
    (hs : ∀ x ∈ s, p.eval x = y) : #s ≤ p.natDegree := by
  have hsub : s ⊆ (p - C y).roots.toFinset := by
    intro x hx
    rw [Multiset.mem_toFinset]
    exact Polynomial.mem_roots_sub_C'.mpr ⟨hp, hs x hx⟩
  calc #s ≤ #(p - C y).roots.toFinset := Finset.card_le_card hsub
    _ ≤ Multiset.card (p - C y).roots := Multiset.toFinset_card_le _
    _ ≤ (p - C y).natDegree := Polynomial.card_roots' _
    _ = p.natDegree := Polynomial.natDegree_sub_C

/-- The `y = 0` case of `card_le_natDegree_of_forall_eval_eq`, where the sharp hypothesis
`p ≠ C 0` is just `p ≠ 0`. -/
theorem card_le_natDegree_of_forall_isRoot {p : R[X]} (hp : p ≠ 0) {s : Finset R}
    (hs : ∀ x ∈ s, p.eval x = 0) : #s ≤ p.natDegree :=
  card_le_natDegree_of_forall_eval_eq (by rwa [Polynomial.C_0]) hs

/-- **Fibre bound (sharp form).** Inside any finite set `s`, at most `natDegree p` points are
sent to `y` by `p`, provided `p` is not the constant `C y`. -/
theorem card_fibre_le_natDegree {p : R[X]} {y : R} (hp : p ≠ C y) (s : Finset R) :
    #{x ∈ s | p.eval x = y} ≤ p.natDegree :=
  card_le_natDegree_of_forall_eval_eq hp fun _x hx => (Finset.mem_filter.mp hx).2

/-- **Fibre bound (uniform form).** For a nonconstant `p`, *every* fibre inside `s` has at most
`natDegree p` points. -/
theorem card_fibre_le_natDegree' {p : R[X]} (hp : 0 < p.natDegree) (s : Finset R) (y : R) :
    #{x ∈ s | p.eval x = y} ≤ p.natDegree :=
  card_fibre_le_natDegree (ne_C_of_natDegree_pos hp y) s

/-- `degree`-phrased variant, matching the hypothesis shape used by
`FiniteField.card_image_polynomial_eval`. -/
theorem card_fibre_le_natDegree_of_degree_pos {p : R[X]} (hp : 0 < p.degree) (s : Finset R)
    (y : R) : #{x ∈ s | p.eval x = y} ≤ p.natDegree :=
  card_fibre_le_natDegree' (Polynomial.natDegree_pos_iff_degree_pos.mpr hp) s y

/-! ## Counting corollaries

Read the direction of each inequality carefully: `card_preimage_le_natDegree_mul` bounds a
preimage from **above**, `card_le_natDegree_mul_card_image` bounds an image from **below**.
-/

/-- **Preimage bound (upper).** The part of `s` that `p` maps into `T` has at most
`natDegree p * #T` elements — a bound independent of `#s`. It asserts nothing about that set
being nonempty or large. -/
theorem card_preimage_le_natDegree_mul {p : R[X]} (hp : 0 < p.natDegree) (s T : Finset R) :
    #{x ∈ s | p.eval x ∈ T} ≤ p.natDegree * #T :=
  Finset.card_le_mul_card_image_of_maps_to (f := fun x => p.eval x) (t := T)
    (fun _a ha => (Finset.mem_filter.mp ha).2) p.natDegree
    (fun b _ => card_fibre_le_natDegree' hp _ b)

/-- **Image bound (lower): no compression beyond the degree, over an arbitrary finite set.**
Generalises `FiniteField.card_image_polynomial_eval` from `univ` to any `s : Finset R`. -/
theorem card_le_natDegree_mul_card_image {p : R[X]} (hp : 0 < p.natDegree) (s : Finset R) :
    #s ≤ p.natDegree * #(s.image fun x => p.eval x) :=
  Finset.card_le_mul_card_image (f := fun x => p.eval x) s p.natDegree
    (fun b _ => card_fibre_le_natDegree' hp s b)

/-- The division phrasing of `card_le_natDegree_mul_card_image`. Strictly weaker, because `ℕ`
division truncates; prefer the multiplicative form. Stated because it is the phrasing prose
usually uses. -/
theorem card_div_natDegree_le_card_image {p : R[X]} (hp : 0 < p.natDegree) (s : Finset R) :
    #s / p.natDegree ≤ #(s.image fun x => p.eval x) :=
  Nat.div_le_of_le_mul (card_le_natDegree_mul_card_image hp s)

/-- Check that the subset generalisation really does recover the Mathlib statement
`FiniteField.card_image_polynomial_eval`, hypothesis for hypothesis. -/
theorem card_image_polynomial_eval_of_degree_pos [Fintype R] {p : R[X]} (hp : 0 < p.degree) :
    Fintype.card R ≤ p.natDegree * #(Finset.univ.image fun x => p.eval x) := by
  have h := card_le_natDegree_mul_card_image
    (Polynomial.natDegree_pos_iff_degree_pos.mpr hp) (Finset.univ : Finset R)
  rwa [Finset.card_univ] at h

end Ecdlp.Screen
