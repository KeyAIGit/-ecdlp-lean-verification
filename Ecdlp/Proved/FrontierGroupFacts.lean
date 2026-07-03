import Mathlib

/-!
# Frontier coverage: elementary finite-group / torsion facts (tier-0)

Knowledge-graph **coverage** nodes: standard Mathlib group/torsion lemmas restated in the ECDLP
ontology and closed by the zero-cost tier-0 layer (a direct Mathlib lemma or one standard tactic).
These are *restatements*, not novel results — they are tracked as a separate coverage tally in
`VERIFIED.md` and are **not** folded into the headline `~distinct` figure. Promoted in a batch from
the open `frontier_*` stems (`Ecdlp/Targets/`). Verified kernel-clean (no incomplete obligations,
no new axioms).
-/

namespace Ecdlp.Frontier

/-- Lagrange: every element's order divides the group order. -/
theorem orderOf_dvd_card' {G : Type*} [Group G] [Fintype G] (g : G) :
    orderOf g ∣ Fintype.card G := orderOf_dvd_card

/-- A finite group is nonempty: its cardinality is positive. -/
theorem card_pos' {G : Type*} [Group G] [Fintype G] : 0 < Fintype.card G :=
  Fintype.card_pos_iff.mpr ⟨1⟩

/-- Euler/Lagrange: `g ^ |G| = 1` in a finite group. -/
theorem pow_card_eq_one' {G : Type*} [Group G] [Fintype G] (g : G) :
    g ^ Fintype.card G = 1 := pow_card_eq_one

/-- The identity has order 1. -/
theorem orderOf_one' {G : Type*} [Group G] : orderOf (1 : G) = 1 := orderOf_one

/-- `addOrderOf a ∣ n ↔ n • a = 0` (order-divisibility characterization of torsion). -/
theorem addOrderOf_dvd_iff' {A : Type*} [AddGroup A] (a : A) (n : ℕ) :
    addOrderOf a ∣ n ↔ n • a = 0 := addOrderOf_dvd_iff_nsmul_eq_zero

/-- The identity is `n`-torsion for every `n`. -/
theorem zero_mem_torsionBy {A : Type*} [AddCommGroup A] (n : ℤ) :
    (0 : A) ∈ AddSubgroup.torsionBy A n := zero_mem _

/-- Torsion is closed under negation. -/
theorem neg_mem_torsionBy {A : Type*} [AddCommGroup A] (n : ℤ) (x : A)
    (hx : x ∈ AddSubgroup.torsionBy A n) : -x ∈ AddSubgroup.torsionBy A n := neg_mem hx

/-- Every element is `0`-torsion. -/
theorem mem_torsionBy_zero {A : Type*} [AddCommGroup A] (x : A) :
    x ∈ AddSubgroup.torsionBy A (0 : ℤ) := by simp

/-- The `0`-torsion subgroup is the whole group. -/
theorem torsionBy_zero_top {A : Type*} [AddCommGroup A] :
    AddSubgroup.torsionBy A (0 : ℤ) = ⊤ := by ext x; simp

/-- Only the identity is `1`-torsion: the `1`-torsion subgroup is trivial. -/
theorem torsionBy_one_bot {A : Type*} [AddCommGroup A] :
    AddSubgroup.torsionBy A (1 : ℤ) = ⊥ := by ext x; simp

end Ecdlp.Frontier
