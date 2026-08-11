import Ecdlp.Proved.M16DirectPointSemantics

/-!
# Liftable/nonliftable partition semantics for direct M16 roots

This module partitions the sixteen actual point witnesses supplied by
`M16DirectPointSemantics` according to whether their prescribed base-field
`x`-coordinates lift to secp256k1 over the base field.  The liftable subtotal
descends to a base point, while the nonliftable subtotal is forced to be the
identity by the already-proved conditional Frobenius split.

The vanishing conclusion for the nonliftable subtotal is derived only from a
compatible actual point relation.  No arbitrary choice of algebraic-closure
lifts is asserted to have vanishing subtotal.  This file proves no witness
recovery, unconditional relation existence or uniqueness, solver, yield,
rank, or cost claim.
-/

namespace Ecdlp.M16PartitionedPointSemantics

open scoped BigOperators

open WeierstrassCurve.Affine
open Ecdlp.Curve
open Ecdlp.M16DirectSystemRootBridge
open Ecdlp.M16FactorBaseFinite
open Ecdlp.M16FactorBaseLiftable
open Ecdlp.M16FrobeniusPointSplit
open Ecdlp.SemaevLeftFoldAffine

noncomputable section

abbrev Fp := ZMod Secp256k1.p
abbrev FpBar := AlgebraicClosure Fp
abbrev BasePoint := secp256k1.toAffine.Point
abbrev BarCurve := secp256k1 ⁄ FpBar
abbrev BarPoint := BarCurve.Point

local instance : DecidableEq FpBar := Classical.decEq _

private instance barCurve_isElliptic : BarCurve.IsElliptic :=
  inferInstanceAs
    ((secp256k1.map (algebraMap Fp FpBar)).IsElliptic)

/-- The slots whose prescribed base-field coordinates lift to affine
secp256k1 points over the base field. -/
noncomputable def liftableSlots (x : Fin 16 → Fp) : Finset (Fin 16) := by
  classical
  exact Finset.univ.filter (fun i ↦ IsLiftable (x i))

/-- The complementary slots whose prescribed base-field coordinates do not
lift to affine secp256k1 points over the base field. -/
noncomputable def nonliftableSlots (x : Fin 16 → Fp) : Finset (Fin 16) := by
  classical
  exact Finset.univ.filter (fun i ↦ ¬ IsLiftable (x i))

@[simp] theorem mem_liftableSlots {x : Fin 16 → Fp} {i : Fin 16} :
    i ∈ liftableSlots x ↔ IsLiftable (x i) := by
  classical
  simp [liftableSlots]

@[simp] theorem mem_nonliftableSlots {x : Fin 16 → Fp} {i : Fin 16} :
    i ∈ nonliftableSlots x ↔ ¬ IsLiftable (x i) := by
  classical
  simp [nonliftableSlots]

theorem liftableSlots_disjoint_nonliftableSlots (x : Fin 16 → Fp) :
    Disjoint (liftableSlots x) (nonliftableSlots x) := by
  classical
  simp [Finset.disjoint_left, liftableSlots, nonliftableSlots]

theorem liftableSlots_union_nonliftableSlots (x : Fin 16 → Fp) :
    liftableSlots x ∪ nonliftableSlots x = Finset.univ := by
  classical
  ext i
  by_cases hi : IsLiftable (x i) <;>
    simp [liftableSlots, nonliftableSlots, hi]

/-- The total of all sixteen witnesses is the liftable subtotal followed by
the nonliftable subtotal. -/
theorem sum_eq_sum_liftable_add_sum_nonliftable
    (x : Fin 16 → Fp) (P : Fin 16 → BarPoint) :
    (∑ i, P i) =
      (∑ i ∈ liftableSlots x, P i) +
      (∑ i ∈ nonliftableSlots x, P i) := by
  classical
  calc
    (∑ i, P i) =
        ∑ i ∈ liftableSlots x ∪ nonliftableSlots x, P i := by
          rw [liftableSlots_union_nonliftableSlots]
    _ =
        (∑ i ∈ liftableSlots x, P i) +
        (∑ i ∈ nonliftableSlots x, P i) :=
      Finset.sum_union (liftableSlots_disjoint_nonliftableSlots x)

/-- Exact partitioned witness attached to a supplied base-field target point.

The target orientation is fixed as `C + R = 0`, matching the compatible
closure relation `(∑ i, P i) + includePoint R = 0`.  The predicate retains
the actual closure witnesses and does not claim that arbitrary lifts have the
same subtotals. -/
def PartitionedPointWitness (x : Fin 16 → Fp) (R : BasePoint) : Prop :=
  ∃ (P : Fin 16 → BarPoint) (C : BasePoint),
    (∀ i, LiesOver (x i) (P i)) ∧
    includePoint C = ∑ i ∈ liftableSlots x, P i ∧
    C + R = 0 ∧
    (∑ i ∈ nonliftableSlots x, P i) = 0

/-- A compatible actual point relation yields the exact partitioned witness.
In particular, the nonliftable subtotal is proved zero only after this
relation is supplied. -/
theorem partitionedPointWitness_of_compatible_point_relation
    (x : Fin 16 → Fp) (R : BasePoint) (P : Fin 16 → BarPoint)
    (hover : ∀ i, LiesOver (x i) (P i))
    (hsum : (∑ i, P i) + includePoint R = 0) :
    PartitionedPointWitness x R := by
  have hoverL : ∀ i ∈ liftableSlots x, LiesOver (x i) (P i) := by
    intro i _
    exact hover i
  have hlift : ∀ i ∈ liftableSlots x, IsLiftable (x i) := by
    intro i hi
    exact mem_liftableSlots.mp hi
  have hoverN : ∀ i ∈ nonliftableSlots x, LiesOver (x i) (P i) := by
    intro i _
    exact hover i
  have hnon : ∀ i ∈ nonliftableSlots x, ¬ IsLiftable (x i) := by
    intro i hi
    exact mem_nonliftableSlots.mp hi
  have hsum' :
      (∑ i ∈ liftableSlots x, P i) +
          (∑ i ∈ nonliftableSlots x, P i) + includePoint R = 0 := by
    rw [← sum_eq_sum_liftable_add_sum_nonliftable x P]
    exact hsum
  rcases split_partitioned_point_witnesses
      (liftableSlots x) (nonliftableSlots x) x x P P R
      hoverL hlift hoverN hnon hsum' with
    ⟨C, hC, hbase, hzero⟩
  have hCR : C + R = 0 := by
    apply includePoint_injective
    simpa only [map_add, map_zero] using hbase
  exact ⟨P, C, hover, hC, hCR, hzero⟩

/-- The partitioned data reconstructs its compatible actual point relation. -/
theorem exists_compatible_point_relation_of_partitionedPointWitness
    {x : Fin 16 → Fp} {R : BasePoint}
    (h : PartitionedPointWitness x R) :
    ∃ P : Fin 16 → BarPoint,
      (∀ i, LiesOver (x i) (P i)) ∧
      (∑ i, P i) + includePoint R = 0 := by
  rcases h with ⟨P, C, hover, hC, hCR, hzero⟩
  refine ⟨P, hover, ?_⟩
  rw [sum_eq_sum_liftable_add_sum_nonliftable x P, ← hC, hzero,
    add_zero]
  simpa only [map_add, map_zero] using congrArg includePoint hCR

/-- A partitioned witness is equivalent to a compatible actual point relation
with the same fixed target orientation. -/
theorem partitionedPointWitness_iff_exists_compatible_point_relation
    (x : Fin 16 → Fp) (R : BasePoint) :
    PartitionedPointWitness x R ↔
      ∃ P : Fin 16 → BarPoint,
        (∀ i, LiesOver (x i) (P i)) ∧
        (∑ i, P i) + includePoint R = 0 := by
  constructor
  · exact exists_compatible_point_relation_of_partitionedPointWitness
  · rintro ⟨P, hover, hsum⟩
    exact partitionedPointWitness_of_compatible_point_relation x R P hover hsum

/-- Exact partition theorem for the direct M16 root equation relative to an
actual supplied base-field target point. -/
theorem S17At_eq_zero_iff_partitionedPointWitness
    (x : Fin 16 → Fp) (X : Fp) (R : BasePoint)
    (hR : LiesOver X (includePoint R)) :
    S17At x X = 0 ↔ PartitionedPointWitness x R := by
  exact
    (Ecdlp.M16DirectPointSemantics.S17At_eq_zero_iff_exists_point_sum_add_target_eq_zero
        x X (includePoint R) hR).trans
      (partitionedPointWitness_iff_exists_compatible_point_relation x R).symm

/-- Thin specialization for sixteen coordinates already packaged in the exact
M16 factor-base subtype.  No additional factor-base or recovery conclusion is
introduced. -/
theorem S17At_factorBase_eq_zero_iff_partitionedPointWitness
    (x : Fin 16 → FactorBaseX) (X : Fp) (R : BasePoint)
    (hR : LiesOver X (includePoint R)) :
    S17At (fun i ↦ (x i).1) X = 0 ↔
      PartitionedPointWitness (fun i ↦ (x i).1) R :=
  S17At_eq_zero_iff_partitionedPointWitness
    (fun i ↦ (x i).1) X R hR

end

end Ecdlp.M16PartitionedPointSemantics
