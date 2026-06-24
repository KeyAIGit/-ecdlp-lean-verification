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

end Ecdlp.GenericGroup
