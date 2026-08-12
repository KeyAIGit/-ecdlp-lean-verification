import Mathlib

/-!
# Time--space tradeoff for checkpoint segment primitives

This file formalizes the finite counting core of
`STRUCTURED-SEGMENT-PRIMITIVE-004`.

A checkpoint-and-walk data structure stores a finite set of checkpoint states.
Online evaluation chooses one checkpoint and one offset from a bounded online
range, then deterministically decodes that pair to a target state. If every
target must be reachable, the number of checkpoint/offset pairs must be at least
the target-space cardinality.

For a cyclic group of order `n`, `S` stored checkpoints and a worst-case local
walk of fewer than `T` offsets therefore satisfy `n <= S*T` in this model.
Balancing the two resources gives the familiar square-root frontier.

This is a theorem only for the declared checkpoint/offset model. It does not
exclude a global theta, EDS, analytic, or coordinate circuit that evaluates a
long segment without being represented by checkpoint-plus-local-walk pairs.
-/

namespace Ecdlp.CocycleIntegration

/-- Any surjective checkpoint/offset decoder has at least as many encodings as
target states. -/
theorem checkpointDecoder_timeSpace_tradeoff
    {α : Type*} [Fintype α] [DecidableEq α]
    (checkpoints : Finset α) (onlineOffsets : ℕ)
    (decode : (↥checkpoints × Fin onlineOffsets) → α)
    (hdecode : Function.Surjective decode) :
    Fintype.card α ≤ checkpoints.card * onlineOffsets := by
  calc
    Fintype.card α ≤ Fintype.card (↥checkpoints × Fin onlineOffsets) :=
      Fintype.card_le_of_surjective decode hdecode
    _ = checkpoints.card * onlineOffsets := by simp

/-- Explicit checkpoint-and-walk form: if every target is obtained from one
stored checkpoint and one bounded online offset, storage times online range
covers the whole target space. -/
theorem checkpointWalk_timeSpace_tradeoff
    {α : Type*} [Fintype α] [DecidableEq α]
    (checkpoints : Finset α) (onlineOffsets : ℕ)
    (advance : α → Fin onlineOffsets → α)
    (hcover : ∀ target : α,
      ∃ checkpoint : ↥checkpoints, ∃ offset : Fin onlineOffsets,
        advance checkpoint.1 offset = target) :
    Fintype.card α ≤ checkpoints.card * onlineOffsets := by
  apply checkpointDecoder_timeSpace_tradeoff checkpoints onlineOffsets
    (fun state => advance state.1.1 state.2)
  intro target
  obtain ⟨checkpoint, offset, htarget⟩ := hcover target
  exact ⟨(checkpoint, offset), htarget⟩

/-- Version with a separately stated target-space cardinality. -/
theorem checkpointWalk_order_tradeoff
    {α : Type*} [Fintype α] [DecidableEq α]
    (checkpoints : Finset α) (onlineOffsets order : ℕ)
    (advance : α → Fin onlineOffsets → α)
    (hcover : ∀ target : α,
      ∃ checkpoint : ↥checkpoints, ∃ offset : Fin onlineOffsets,
        advance checkpoint.1 offset = target)
    (horder : Fintype.card α = order) :
    order ≤ checkpoints.card * onlineOffsets := by
  rw [← horder]
  exact checkpointWalk_timeSpace_tradeoff
    checkpoints onlineOffsets advance hcover

end Ecdlp.CocycleIntegration
