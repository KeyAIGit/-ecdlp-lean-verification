import Mathlib
import Ecdlp.Proved.CocycleIntegration

/-!
# Query ambiguity for a closed binary edge cocycle

This file formalizes the information-theoretic core of
`GENERIC-COCYCLE-INTEGRATION-003`.

A binary edge labeling is represented by the finite set of edges carrying the
nonzero `ZMod 2` label. Equality of total cardinality modulo two represents the
known cycle-closure parity. The target potential difference across a cut is the
parity of the labeled edges inside that cut.

If one unqueried edge remains on each side of the cut, flipping those two edges
preserves the global closure parity and every queried answer, while changing the
target cut parity. Therefore exact determination from local edge queries requires
querying every edge on at least one side of the cut.

This is a lower bound only for the declared black-box local-edge model. It is
not an unconditional EDS, coordinate-circuit, or ECDLP lower bound.
-/

namespace Ecdlp.CocycleIntegration

/-- Two unqueried edges on opposite sides of a cut support indistinguishable
closed binary edge labelings with opposite target cut parity. -/
theorem two_unqueried_edges_hide_cut_parity
    {ι : Type*} [DecidableEq ι]
    (queried cut : Finset ι) (i j : ι)
    (hiQueried : i ∉ queried) (hjQueried : j ∉ queried)
    (hiCut : i ∈ cut) (hjCut : j ∉ cut) :
    ∃ e₀ e₁ : Finset ι,
      (∀ x ∈ queried, (x ∈ e₀ ↔ x ∈ e₁)) ∧
      e₀.card % 2 = e₁.card % 2 ∧
      (e₀ ∩ cut).card % 2 ≠ (e₁ ∩ cut).card % 2 := by
  have hij : i ≠ j := by
    intro h
    subst j
    exact hjCut hiCut
  refine ⟨∅, {i, j}, ?_, ?_, ?_⟩
  · intro x hx
    have hxi : x ≠ i := by
      intro h
      subst x
      exact hiQueried hx
    have hxj : x ≠ j := by
      intro h
      subst x
      exact hjQueried hx
    simp [hxi, hxj]
  · simp [hij]
  · simp [hij, hiCut, hjCut]

/-- If queried edge values together with the known global closure parity determine
cut parity for every binary labeling, the queried set contains the entire cut or
its entire complement. -/
theorem exact_closed_cut_decoder_covers_one_side
    {ι : Type*} [Fintype ι] [DecidableEq ι]
    (queried cut : Finset ι)
    (hdet : ∀ e₀ e₁ : Finset ι,
      e₀.card % 2 = e₁.card % 2 →
      (∀ x ∈ queried, (x ∈ e₀ ↔ x ∈ e₁)) →
      (e₀ ∩ cut).card % 2 = (e₁ ∩ cut).card % 2) :
    cut ⊆ queried ∨ (Finset.univ \ cut) ⊆ queried := by
  by_cases hcut : cut ⊆ queried
  · exact Or.inl hcut
  · right
    intro j hjComp
    by_contra hjQueried
    rw [Finset.not_subset] at hcut
    obtain ⟨i, hiCut, hiQueried⟩ := hcut
    have hjCut : j ∉ cut := by
      simpa using hjComp
    obtain ⟨e₀, e₁, hagree, hclosed, hdiff⟩ :=
      two_unqueried_edges_hide_cut_parity queried cut i j
        hiQueried hjQueried hiCut hjCut
    exact hdiff (hdet e₀ e₁ hclosed hagree)

/-- Exact black-box integration of a closed binary cocycle requires at least the
size of the smaller side of the target cut in local edge queries. -/
theorem exact_closed_cut_query_card_lower_bound
    {ι : Type*} [Fintype ι] [DecidableEq ι]
    (queried cut : Finset ι)
    (hdet : ∀ e₀ e₁ : Finset ι,
      e₀.card % 2 = e₁.card % 2 →
      (∀ x ∈ queried, (x ∈ e₀ ↔ x ∈ e₁)) →
      (e₀ ∩ cut).card % 2 = (e₁ ∩ cut).card % 2) :
    Nat.min cut.card (Finset.univ \ cut).card ≤ queried.card := by
  rcases exact_closed_cut_decoder_covers_one_side queried cut hdet with hcut | hcomp
  · exact le_trans (Nat.min_le_left _ _) (Finset.card_le_card hcut)
  · exact le_trans (Nat.min_le_right _ _) (Finset.card_le_card hcomp)

end Ecdlp.CocycleIntegration
