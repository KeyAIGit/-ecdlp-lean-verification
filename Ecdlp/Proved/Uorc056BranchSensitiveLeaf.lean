import Mathlib
import Ecdlp.Proved.Uorc056SignBlindCircuit

/-!
# UORC056 C24 branch-sensitive leaf and normalization-torsor boundary

This file formalizes the abstract information boundary used by the C24
classification. If two candidate worlds have identical public data but the
desired target differs, the target cannot factor through that public data.
The same statement is expressed for invariant data on a group orbit and for a
seeded construction: if a deterministic construction has separated outputs
while its public input is unchanged, its complete seed/state must itself be
separated.

These theorems do not assert that the concrete elliptic-curve public data have
such a collision. That identification is a separate mathematical obligation
for each proposed theta, p-adic, determinant, resultant, or GLV mechanism.
-/

namespace Ecdlp.UORC056

universe u v w t

/-- A target factors through public data when one decoder of the public datum
reproduces it in every world. -/
def FactorsThrough
    {World : Type u} {Data : Type v} {Output : Type w}
    (publicData : World → Data) (target : World → Output) : Prop :=
  ∃ decode : Data → Output, ∀ world, decode (publicData world) = target world

/-- One public-data collision with separated target values rules out every
universal decoder through that public datum. -/
theorem not_factorsThrough_of_collision
    {World : Type u} {Data : Type v} {Output : Type w}
    (publicData : World → Data) (target : World → Output)
    (left right : World)
    (hPublic : publicData left = publicData right)
    (hTarget : target left ≠ target right) :
    ¬ FactorsThrough publicData target := by
  rintro ⟨decode, hDecode⟩
  apply hTarget
  calc
    target left = decode (publicData left) := (hDecode left).symm
    _ = decode (publicData right) := congrArg decode hPublic
    _ = target right := hDecode right

/-- The two-world specialization used for a global branch pair. -/
theorem twoWorld_branch_sensitive_target_not_publicly_decodable
    {Data : Type v} {Output : Type w}
    (publicPlus publicMinus : Data)
    (targetPlus targetMinus : Output)
    (hPublic : publicPlus = publicMinus)
    (hTarget : targetPlus ≠ targetMinus) :
    ¬ ∃ decode : Data → Output,
        decode publicPlus = targetPlus ∧ decode publicMinus = targetMinus := by
  rintro ⟨decode, hPlus, hMinus⟩
  apply hTarget
  calc
    targetPlus = decode publicPlus := hPlus.symm
    _ = decode publicMinus := congrArg decode hPublic
    _ = targetMinus := hMinus

section Orbit

variable {Actor : Type u} {World : Type v} {Data : Type w} {Output : Type t}
variable [Group Actor] [MulAction Actor World]

/-- Invariant public data cannot compute a target that moves somewhere on the
same group orbit. This is the abstract normalization-torsor obstruction. -/
theorem invariant_public_data_cannot_compute_moving_target
    (publicData : World → Data) (target : World → Output)
    (hInvariant : ∀ actor world,
      publicData (actor • world) = publicData world)
    (actor : Actor) (world : World)
    (hTarget : target (actor • world) ≠ target world) :
    ¬ FactorsThrough publicData target := by
  exact not_factorsThrough_of_collision
    publicData target (actor • world) world
    (hInvariant actor world) hTarget

/-- In particular, invariant quotient data cannot choose every representative
of a nontrivial orbit. -/
theorem invariant_public_data_has_no_global_selector
    (publicData : World → Data)
    (hInvariant : ∀ actor world,
      publicData (actor • world) = publicData world)
    (actor : Actor) (world : World)
    (hMoves : actor • world ≠ world) :
    ¬ ∃ select : Data → World,
        ∀ candidate, select (publicData candidate) = candidate := by
  simpa [FactorsThrough] using
    (invariant_public_data_cannot_compute_moving_target
      (publicData := publicData)
      (target := fun candidate : World => candidate)
      hInvariant actor world hMoves)

end Orbit

/-- A deterministic construction cannot produce separated outputs from equal
public data and equal complete seed/state. Therefore any successful escape from
a public-data collision must put the separation into the seed/state itself. -/
theorem separated_output_forces_seed_separation
    {Data : Type u} {Seed : Type v} {Output : Type w}
    (construct : Data → Seed → Output)
    (publicPlus publicMinus : Data)
    (seedPlus seedMinus : Seed)
    (hPublic : publicPlus = publicMinus)
    (hOutput :
      construct publicPlus seedPlus ≠ construct publicMinus seedMinus) :
    seedPlus ≠ seedMinus := by
  intro hSeed
  apply hOutput
  rw [hPublic, hSeed]

/-- If the complete auxiliary state is itself unchanged across the two worlds,
a deterministic seeded construction remains unchanged. -/
theorem equal_public_and_seed_give_equal_output
    {Data : Type u} {Seed : Type v} {Output : Type w}
    (construct : Data → Seed → Output)
    (publicPlus publicMinus : Data)
    (seedPlus seedMinus : Seed)
    (hPublic : publicPlus = publicMinus)
    (hSeed : seedPlus = seedMinus) :
    construct publicPlus seedPlus = construct publicMinus seedMinus := by
  rw [hPublic, hSeed]

/-- Transporting a non-fixed seed through any deterministic aggregator does not
explain how that seed was produced. This converse-free implication records only
that equal seeds cannot yield separated outputs when public data agree. -/
theorem branch_sensitive_aggregate_requires_nonfixed_complete_state
    {Data : Type u} {State : Type v} {Output : Type w}
    (aggregate : Data → State → Output)
    (publicPlus publicMinus : Data)
    (statePlus stateMinus : State)
    (hPublic : publicPlus = publicMinus)
    (hSeparated :
      aggregate publicPlus statePlus ≠ aggregate publicMinus stateMinus) :
    statePlus ≠ stateMinus :=
  separated_output_forces_seed_separation
    aggregate publicPlus publicMinus statePlus stateMinus hPublic hSeparated

end Ecdlp.UORC056
