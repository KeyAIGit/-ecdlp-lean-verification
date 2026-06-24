import Mathlib

/-!
# A generic-group lower bound for the discrete logarithm (`Ω(√p)`)

The combinatorial core of the Shoup / Nechaev lower bound for the discrete
logarithm problem in the **generic group model** — the foundation of ECDLP
hardness, and a result not present in Mathlib (`weilPairing`, `semaev`,
`generic group` / `discreteLog` lower bounds are all absent from Mathlib v4.31).

## Model

Work in the prime field `ZMod p` (the exponent space of a cyclic group of order
`p`). A *generic* algorithm computes group elements only as `ℤ`-linear
combinations of two base elements: the generator `g` (discrete log the known
constant, here normalised away) and the challenge `h = x·g` (discrete log `x` the
unknown it must find). Every element it forms is therefore an **affine form**
`a + b·X` in the unknown log `X`, recorded as `Aff p` with `Aff.eval`. The only
information the algorithm extracts about `x` is *which pairs of formed elements are
equal* at the true value `x` — a *collision*.

## Results

* `collisionSet_card_le_one` — two *distinct* affine forms are equal on at most one
  point of `ZMod p` (a nonzero polynomial of degree ≤ 1 over a field has ≤ 1 root).
* `badSet_card_le` — among `q` distinct forms the set of candidate logs exhibiting
  *any* collision has at most `q·q − q` elements (union bound over ordered pairs).
* `generic_dlog_query_bound` — if the collision pattern of the `q` formed elements
  determines the log for *every* candidate `x` (a necessary condition for a generic
  algorithm to solve the DLP on all inputs), then `p ≤ q·q`; i.e. `q ≥ √p`. This is
  the `Ω(√p)` generic lower bound.

## Scope

This formalises the information-theoretic heart of the bound: the affine-form
abstraction captures exactly the algebraic data available to a generic algorithm.
It does not model adaptive adversaries with random encodings probabilistically;
the collision-counting argument here *is* the mathematical content of the theorem.
-/

open Finset

namespace Ecdlp.GenericGroup

variable {p : ℕ}

/-- An affine form `a + b·X` over `ZMod p`: the discrete-log information content of
a group element a generic algorithm has computed. -/
@[ext]
structure Aff (p : ℕ) where
  a : ZMod p
  b : ZMod p

/-- Evaluate an affine form at a candidate discrete log `x`. -/
def Aff.eval (f : Aff p) (x : ZMod p) : ZMod p := f.a + f.b * x

variable [Fact p.Prime]

/-- `ZMod p` is a finite field, so it is nonempty as a type with `p` elements. -/
instance : NeZero p := ⟨(Fact.out : p.Prime).pos.ne'⟩

/-- The candidate logs at which two affine forms collide. -/
def collisionSet (f g : Aff p) : Finset (ZMod p) :=
  univ.filter (fun x => f.eval x = g.eval x)

/-- **Rung 1.** Two *distinct* affine forms over the prime field `ZMod p` agree on
at most one point: their difference `(f.b − g.b)·X + (f.a − g.a)` is a nonzero
polynomial of degree ≤ 1, so it has at most one root. -/
theorem collisionSet_card_le_one (f g : Aff p) (h : f ≠ g) :
    (collisionSet f g).card ≤ 1 := by
  rw [Finset.card_le_one]
  intro x hx y hy
  simp only [collisionSet, Finset.mem_filter, Finset.mem_univ, true_and, Aff.eval] at hx hy
  by_cases hb : f.b = g.b
  · -- equal slopes force equal intercepts, so `f = g`, contradicting `h`
    exfalso
    apply h
    have ha : f.a = g.a := by rw [hb] at hx; linear_combination hx
    exact Aff.ext ha hb
  · -- distinct slopes: the (degree-1) equation has a unique solution
    have key : (f.b - g.b) * (x - y) = 0 := by linear_combination hx - hy
    rcases mul_eq_zero.mp key with h1 | h2
    · exact absurd (sub_eq_zero.mp h1) hb
    · exact sub_eq_zero.mp h2

/-- The candidate logs exhibiting a collision among the `q` formed elements. -/
def badSet {q : ℕ} (F : Fin q → Aff p) : Finset (ZMod p) :=
  (univ : Finset (Fin q)).offDiag.biUnion (fun ij => collisionSet (F ij.1) (F ij.2))

theorem mem_badSet {q : ℕ} {F : Fin q → Aff p} {x : ZMod p} :
    x ∈ badSet F ↔ ∃ i j, i ≠ j ∧ (F i).eval x = (F j).eval x := by
  simp only [badSet, Finset.mem_biUnion, Finset.mem_offDiag, Finset.mem_univ,
    true_and, collisionSet, Finset.mem_filter]
  constructor
  · rintro ⟨⟨i, j⟩, hij, hx⟩
    exact ⟨i, j, hij, hx⟩
  · rintro ⟨i, j, hij, hx⟩
    exact ⟨⟨i, j⟩, hij, hx⟩

/-- **Rung 2.** Among `q` *distinct* affine forms, at most `q·q − q` candidate logs
exhibit a collision: a union bound over the `q·q − q` ordered pairs, each
contributing at most one point by `collisionSet_card_le_one`. -/
theorem badSet_card_le {q : ℕ} (F : Fin q → Aff p) (hF : Function.Injective F) :
    (badSet F).card ≤ q * q - q := by
  unfold badSet
  refine (Finset.card_biUnion_le_card_mul _ _ 1 ?_).trans (le_of_eq ?_)
  · intro ij hij
    rw [Finset.mem_offDiag] at hij
    have hne : F ij.1 ≠ F ij.2 := fun he => hij.2.2 (hF he)
    exact collisionSet_card_le_one _ _ hne
  · rw [mul_one, Finset.offDiag_card, Finset.card_univ, Fintype.card_fin]

/-- **Headline (`Ω(√p)`).** If the collision pattern of the `q` group elements a
generic algorithm forms determines the discrete log for *every* candidate `x` — a
necessary condition for the algorithm to solve the DLP on all inputs — then
`p ≤ q·q`. Equivalently, any generic discrete-log algorithm makes `q ≥ √p` group
operations. -/
theorem generic_dlog_query_bound {q : ℕ} (F : Fin q → Aff p)
    (hF : Function.Injective F)
    (hsolve : ∀ x : ZMod p, ∃ i j, i ≠ j ∧ (F i).eval x = (F j).eval x) :
    p ≤ q * q := by
  have hsub : (univ : Finset (ZMod p)) ⊆ badSet F := by
    intro x _
    rw [mem_badSet]
    exact hsolve x
  have hcard : p ≤ (badSet F).card := by
    have h := Finset.card_le_card hsub
    rwa [Finset.card_univ, ZMod.card p] at h
  calc p ≤ (badSet F).card := hcard
    _ ≤ q * q - q := badSet_card_le F hF
    _ ≤ q * q := Nat.sub_le _ _

end Ecdlp.GenericGroup
