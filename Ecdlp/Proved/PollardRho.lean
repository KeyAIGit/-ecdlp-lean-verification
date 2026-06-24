import Mathlib

/-!
# Pollard's rho: a collision always exists

Pollard's rho discrete-log method iterates a pseudo-random self-map `f` of the
group and waits for the iteration sequence to collide (`f^[i] x = f^[j] x`), which
exposes the discrete log. Its *correctness* rests on the pigeonhole fact that a
self-map of a finite set of `N` elements must repeat a value within `N` steps:
the iterates `x, f x, f² x, …, f^N x` are `N + 1` elements of an `N`-element set.

(The celebrated `O(√N)` *expected* running time is a birthday-paradox refinement;
the guaranteed existence of a collision within `N` steps is the pigeonhole core
formalized here.)
-/

namespace Ecdlp.GenericGroup

open Function

/-- **Pollard rho collision existence.** For any self-map `f` of a finite type and
any start `x`, the iteration sequence collides within `Fintype.card α` steps:
there are `i < j ≤ card α` with `f^[i] x = f^[j] x`. This is the pigeonhole
guarantee underlying Pollard's rho method. -/
theorem pollard_rho_collision {α : Type*} [Fintype α] [DecidableEq α]
    (f : α → α) (x : α) :
    ∃ i j, i < j ∧ j ≤ Fintype.card α ∧ f^[i] x = f^[j] x := by
  have hc : (Finset.univ : Finset α).card
      < (Finset.range (Fintype.card α + 1)).card := by
    rw [Finset.card_univ, Finset.card_range]; omega
  obtain ⟨a, ha, b, hb, hab, hfab⟩ :=
    Finset.exists_ne_map_eq_of_card_lt_of_maps_to hc
      (f := fun i => f^[i] x) (fun i _ => Finset.mem_univ _)
  rw [Finset.mem_range] at ha hb
  rcases lt_or_gt_of_ne hab with h | h
  · exact ⟨a, b, h, by omega, hfab⟩
  · exact ⟨b, a, h, by omega, hfab.symm⟩

/-- **Pollard rho ρ-shape.** The iteration sequence is eventually periodic: there
is a preperiod `μ` and a positive period `lam` with `f^[k + lam] x = f^[k] x` for
all `k ≥ μ`. This is the full "rho" structure (a tail feeding into a cycle) the
collision of `pollard_rho_collision` produces. -/
theorem pollard_rho_periodic {α : Type*} [Fintype α] [DecidableEq α]
    (f : α → α) (x : α) :
    ∃ μ lam, 0 < lam ∧ ∀ k, μ ≤ k → f^[k + lam] x = f^[k] x := by
  obtain ⟨i, j, hij, _, hfij⟩ := pollard_rho_collision f x
  have step : ∀ t, f^[t + i] x = f^[t + j] x := by
    intro t; simp only [Function.iterate_add_apply, hfij]
  refine ⟨i, j - i, by omega, ?_⟩
  intro k hk
  obtain ⟨t, rfl⟩ : ∃ t, k = t + i := ⟨k - i, by omega⟩
  have e1 : t + i + (j - i) = t + j := by omega
  rw [e1]
  exact (step t).symm

end Ecdlp.GenericGroup
