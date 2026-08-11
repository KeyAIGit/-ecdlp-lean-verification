import Ecdlp.Proved.M16DirectPointSemantics
import Ecdlp.Proved.M16SolverGate

/-!
# Cancellation-pair output lower bounds for direct M16

The exact point semantics of the direct `S17At` equation retains repeated,
labelled source coordinates.  Fix a liftable affine factor-base point `A` and
the nonidentity target `R = -(A + A)`.  Seven independently selected pairs
`B_i, -B_i` then give the sixteen-point relation

`A + A + B_0 - B_0 + ... + B_6 - B_6 + R = 0`.

Putting each cancelling pair in its own two labelled source slots makes the
seven selected coordinates recoverable from the resulting assignment.  This
gives an injection from seven ordered factor-base choices into the distinct
direct-root set.  Restricting all seven choices to the liftable factor base
still gives a large family whose displayed point witnesses are base-field
points.

These are output-cardinality and witness-backpointer facts only.  They are not
PFPO, runtime, memory, solver-node, relation-rank, or ECDLP lower bounds.  The
constructed relations are deliberately degenerate: every cancelling pair has
zero net coefficient, so the family supplies no independence or rank claim.
-/

namespace Ecdlp.M16CancellationRootLowerBound

open scoped BigOperators

open WeierstrassCurve.Affine
open Ecdlp.Curve
open Ecdlp.M16DirectPointSemantics
open Ecdlp.M16DirectSystemRootBridge
open Ecdlp.M16FactorBaseFinite
open Ecdlp.M16FactorBaseLiftable
open Ecdlp.M16FrobeniusPointSplit
open Ecdlp.M16SolverGate
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

private def chainVarsEquiv : ChainVars ≃ (Fp × Fp × Fp × Fp) where
  toFun u := (u.x₁, u.x₂, u.x₃, u.x₄)
  invFun u := ⟨u.1, u.2.1, u.2.2.1, u.2.2.2⟩
  left_inv u := by cases u; rfl
  right_inv u := by rcases u with ⟨_, _, _, _⟩; rfl

private noncomputable instance chainVarsFintype : Fintype ChainVars :=
  Fintype.ofEquiv (Fp × Fp × Fp × Fp) chainVarsEquiv.symm

private noncomputable instance directSystem4Decidable (X : Fp) :
    DecidablePred (DirectSystem4 X) :=
  fun _ => Classical.propDecidable _

/-- Reduced roots whose sixteen coordinates all carry base-field liftability
proofs. -/
abbrev LiftableReducedRoot (X : Fp) :=
  {x : Fin 16 → LiftableFactorBaseX //
    S17At (fun i ↦ (x i).1.1) X = 0}

/-- The complete reduced root set, with no liftability restriction. -/
abbrev ReducedRoot (X : Fp) :=
  {x : Fin 16 → FactorBaseX //
    S17At (fun i ↦ (x i).1) X = 0}

/-- The literal sixteen-row, 64-coordinate direct System-(4) root set. -/
abbrev DirectRoot (X : Fp) :=
  {u : Fin 16 → ChainVars // DirectSystem4 X u}

/-- A fixed lift in each nonempty two-element base-field fiber.  It is used
only to exhibit point witnesses, not as an executable square-root routine. -/
private noncomputable def chosenLiftFiber
    (x : LiftableFactorBaseX) : LiftFiber x :=
  Classical.choice <| (Fintype.card_pos_iff.mp <| by
    rw [card_liftFiber x]
    norm_num)

private noncomputable def chosenSignedPoint
    (x : LiftableFactorBaseX) : SignedAffineFactorBasePoint :=
  ⟨x, chosenLiftFiber x⟩

private noncomputable def chosenLiftPoint
    (x : LiftableFactorBaseX) : BasePoint :=
  toPoint (chosenSignedPoint x)

/-- A signed factor-base point remains visibly above its source coordinate
after the base-field point is included into the algebraic closure. -/
private theorem liesOver_include_toPoint
    (z : SignedAffineFactorBasePoint) :
    LiesOver z.1.1.1 (includePoint (toPoint z)) := by
  apply (liesOver_iff_barKummer_eq _ _).mpr
  rw [toPoint, includePoint_some]
  rfl

private theorem liesOver_include_chosenLiftPoint
    (x : LiftableFactorBaseX) :
    LiesOver x.1.1 (includePoint (chosenLiftPoint x)) := by
  exact liesOver_include_toPoint (chosenSignedPoint x)

private theorem liesOver_include_neg_chosenLiftPoint
    (x : LiftableFactorBaseX) :
    LiesOver x.1.1 (includePoint (-chosenLiftPoint x)) := by
  rw [map_neg]
  exact (liesOver_neg_iff _ _).mpr
    (liesOver_include_chosenLiftPoint x)

/-- Repeat seven labelled values in the fixed slot pairs `(2,3)`, `(4,5)`,
..., `(14,15)`, leaving the first two slots equal to the anchor. -/
private def pairedLeaves {T : Type*}
    (a : T) (z : Fin 7 → T) : Fin 16 → T :=
  ![a, a,
    z 0, z 0, z 1, z 1, z 2, z 2, z 3, z 3,
    z 4, z 4, z 5, z 5, z 6, z 6]

/-- The matching point family: the anchor occurs twice and every later pair
is a point followed by its inverse. -/
private def pairedPoints {G : Type*} [AddCommGroup G]
    (A : G) (B : Fin 7 → G) : Fin 16 → G :=
  ![A, A,
    B 0, -B 0, B 1, -B 1, B 2, -B 2, B 3, -B 3,
    B 4, -B 4, B 5, -B 5, B 6, -B 6]

private theorem sum_pairedPoints {G : Type*} [AddCommGroup G]
    (A : G) (B : Fin 7 → G) :
    (∑ i, pairedPoints A B i) = A + A := by
  simp [pairedPoints, Fin.sum_univ_succ]

private theorem pairedLeaves_injective {T : Type*} (a : T) :
    Function.Injective (pairedLeaves a) := by
  intro z w h
  funext j
  fin_cases j
  · simpa [pairedLeaves] using congrFun h (2 : Fin 16)
  · simpa [pairedLeaves] using congrFun h (4 : Fin 16)
  · simpa [pairedLeaves] using congrFun h (6 : Fin 16)
  · simpa [pairedLeaves] using congrFun h (8 : Fin 16)
  · simpa [pairedLeaves] using congrFun h (10 : Fin 16)
  · simpa [pairedLeaves] using congrFun h (12 : Fin 16)
  · simpa [pairedLeaves] using congrFun h (14 : Fin 16)

/-- The nonidentity target determined by an anchor point. -/
private def anchorTarget (a : SignedAffineFactorBasePoint) : BasePoint :=
  -(toPoint a + toPoint a)

private theorem anchorTarget_ne_zero (a : SignedAffineFactorBasePoint) :
    anchorTarget a ≠ 0 := by
  intro hzero
  have htwo : (2 : ℕ) • toPoint a = 0 := by
    simpa only [anchorTarget, two_nsmul] using neg_eq_zero.mp hzero
  exact toPoint_ne_zero a
    (secp256k1_no_nonzero_two_torsion (toPoint a) htwo)

private theorem exists_liesOver_include_of_ne_zero
    (R : BasePoint) (hR : R ≠ 0) :
    ∃ X : Fp, LiesOver X (includePoint R) := by
  rcases R with _ | ⟨x, y, h⟩
  · exact (hR rfl).elim
  · refine ⟨x, ?_⟩
    apply (liesOver_iff_barKummer_eq _ _).mpr
    rw [includePoint_some]
    rfl

/-- The seven-pair family restricted to liftable coordinates.  The proof
retains an explicit base-field point witness in every slot. -/
private noncomputable def liftableRootFamily
    (a : SignedAffineFactorBasePoint) (X : Fp)
    (hX : LiesOver X (includePoint (anchorTarget a))) :
    (Fin 7 → LiftableFactorBaseX) → LiftableReducedRoot X :=
  fun z ↦ ⟨pairedLeaves a.1 z, by
    apply
      (S17At_eq_zero_iff_exists_point_sum_add_target_eq_zero
        (fun i ↦ ((pairedLeaves a.1 z) i).1.1) X
        (includePoint (anchorTarget a)) hX).mpr
    let B : Fin 7 → BasePoint := fun j ↦ chosenLiftPoint (z j)
    let Pbase : Fin 16 → BasePoint := pairedPoints (toPoint a) B
    let P : Fin 16 → BarPoint := fun i ↦ includePoint (Pbase i)
    refine ⟨P, ?_, ?_⟩
    · intro i
      fin_cases i <;> simp only [pairedLeaves, P, Pbase, pairedPoints, B]
      all_goals first
        | exact liesOver_include_toPoint a
        | exact liesOver_include_chosenLiftPoint _
        | exact liesOver_include_neg_chosenLiftPoint _
    · have hbase : (∑ i, Pbase i) + anchorTarget a = 0 := by
        rw [sum_pairedPoints]
        simp [anchorTarget]
      have hmap := congrArg includePoint hbase
      simpa only [P, map_add, map_sum, map_zero] using hmap⟩

private theorem liftableRootFamily_injective
    (a : SignedAffineFactorBasePoint) (X : Fp)
    (hX : LiesOver X (includePoint (anchorTarget a))) :
    Function.Injective (liftableRootFamily a X hX) := by
  intro z w h
  apply pairedLeaves_injective a.1
  exact congrArg Subtype.val h

/-- The seven-pair family over the complete coordinate factor base.  Pair
points may live only over the algebraic closure, which is enough for the exact
direct-root semantics. -/
private noncomputable def reducedRootFamily
    (a : SignedAffineFactorBasePoint) (X : Fp)
    (hX : LiesOver X (includePoint (anchorTarget a))) :
    (Fin 7 → FactorBaseX) → ReducedRoot X :=
  fun z ↦ ⟨pairedLeaves a.1.1 z, by
    apply
      (S17At_eq_zero_iff_exists_point_sum_add_target_eq_zero
        (fun i ↦ ((pairedLeaves a.1.1 z) i).1) X
        (includePoint (anchorTarget a)) hX).mpr
    let B : Fin 7 → BarPoint := fun j ↦ closureLift (z j).1
    let P : Fin 16 → BarPoint := pairedPoints (includePoint (toPoint a)) B
    refine ⟨P, ?_, ?_⟩
    · intro i
      fin_cases i <;> simp only [pairedLeaves, P, pairedPoints, B]
      all_goals first
        | exact liesOver_include_toPoint a
        | exact liesOver_closureLift _
        | exact (liesOver_neg_iff _ _).mpr (liesOver_closureLift _)
    · rw [sum_pairedPoints]
      simp [anchorTarget]⟩

private theorem reducedRootFamily_injective
    (a : SignedAffineFactorBasePoint) (X : Fp)
    (hX : LiesOver X (includePoint (anchorTarget a))) :
    Function.Injective (reducedRootFamily a X hX) := by
  intro z w h
  apply pairedLeaves_injective a.1.1
  exact congrArg Subtype.val h

/-! ## Cardinal lower bounds -/

/-- Fixing any signed affine factor-base point produces one nonidentity target
with at least `U^7` fully liftable roots, and at least `D^7` roots in both the
reduced and literal direct-System representations.

The same seven values occupy fixed labelled slot pairs, so repeated values and
permutations do not create collisions in the embedding unless the two domain
functions were already equal. -/
theorem cancellation_pair_root_lower_bounds
    (a : SignedAffineFactorBasePoint) :
    let R : BasePoint := anchorTarget a
    R ≠ 0 ∧ ∃ X : Fp,
      LiesOver X (includePoint R) ∧
      283527 ^ 7 ≤ Fintype.card (LiftableReducedRoot X) ∧
      564522 ^ 7 ≤ Fintype.card (ReducedRoot X) ∧
      564522 ^ 7 ≤ Fintype.card (DirectRoot X) := by
  dsimp only
  have hR : anchorTarget a ≠ 0 := anchorTarget_ne_zero a
  refine ⟨hR, ?_⟩
  rcases exists_liesOver_include_of_ne_zero (anchorTarget a) hR with
    ⟨X, hX⟩
  refine ⟨X, hX, ?_, ?_, ?_⟩
  · calc
      283527 ^ 7 =
          Fintype.card (Fin 7 → LiftableFactorBaseX) := by
            rw [Fintype.card_fun, Fintype.card_fin,
              card_liftableFactorBaseX]
      _ ≤ Fintype.card (LiftableReducedRoot X) :=
        Fintype.card_le_of_injective (liftableRootFamily a X hX)
          (liftableRootFamily_injective a X hX)
  · calc
      564522 ^ 7 = Fintype.card (Fin 7 → FactorBaseX) := by
            rw [Fintype.card_fun, Fintype.card_fin, card_factorBaseX]
      _ ≤ Fintype.card (ReducedRoot X) :=
        Fintype.card_le_of_injective (reducedRootFamily a X hX)
          (reducedRootFamily_injective a X hX)
  · calc
      564522 ^ 7 ≤ Fintype.card (ReducedRoot X) := by
        calc
          564522 ^ 7 = Fintype.card (Fin 7 → FactorBaseX) := by
                rw [Fintype.card_fun, Fintype.card_fin, card_factorBaseX]
          _ ≤ Fintype.card (ReducedRoot X) :=
            Fintype.card_le_of_injective (reducedRootFamily a X hX)
              (reducedRootFamily_injective a X hX)
      _ = Fintype.card (DirectRoot X) :=
        (Fintype.card_congr (directSolEquivReduced X)).symm

/-- There exists a nonidentity target with all three cancellation-family
lower bounds.  The anchor exists because the already-counted signed affine
factor base has cardinality `567054`; this corollary introduces no additional
computation or counting leaf. -/
theorem exists_nonzero_target_root_lower_bounds :
    ∃ (R : BasePoint) (X : Fp),
      R ≠ 0 ∧ LiesOver X (includePoint R) ∧
      283527 ^ 7 ≤ Fintype.card (LiftableReducedRoot X) ∧
      564522 ^ 7 ≤ Fintype.card (ReducedRoot X) ∧
      564522 ^ 7 ≤ Fintype.card (DirectRoot X) := by
  obtain ⟨a⟩ : Nonempty SignedAffineFactorBasePoint :=
    Fintype.card_pos_iff.mp <| by
      rw [card_signedAffineFactorBasePoint]
      norm_num
  rcases cancellation_pair_root_lower_bounds a with
    ⟨hR, X, hX, hliftable, hreduced, hdirect⟩
  exact ⟨anchorTarget a, X, hR, hX, hliftable, hreduced, hdirect⟩

/-- The optimistic desk ceiling is already below the liftable cancellation
family's output cardinality.  This compares two natural numbers only; it does
not convert an output entry into a PFPO charge. -/
theorem maxRelationTermBudget_lt_liftable_cancellation_family :
    maxRelationTermBudget < 283527 ^ 7 := by
  calc
    maxRelationTermBudget < 2 ^ 115 :=
      maxRelationTermBudget_lt_two_pow_115
    _ < 2 ^ 126 := by norm_num
    _ = (2 ^ 18) ^ 7 := by norm_num [pow_mul]
    _ < 283527 ^ 7 := by norm_num

/-- For every anchor, the direct-root set at the supplied nonidentity target
has cardinality strictly above the optimistic desk ceiling.  This remains an
output-cardinality statement, not a runtime or PFPO lower bound. -/
theorem exists_target_budget_lt_directRoot_card
    (a : SignedAffineFactorBasePoint) :
    ∃ (R : BasePoint) (X : Fp),
      R ≠ 0 ∧ LiesOver X (includePoint R) ∧
      maxRelationTermBudget < Fintype.card (DirectRoot X) := by
  rcases cancellation_pair_root_lower_bounds a with
    ⟨hR, X, hX, _, _, hdirect⟩
  refine ⟨anchorTarget a, X, hR, hX, ?_⟩
  exact maxRelationTermBudget_lt_liftable_cancellation_family.trans_le
    (le_trans (by norm_num : 283527 ^ 7 ≤ 564522 ^ 7) hdirect)

end

end Ecdlp.M16CancellationRootLowerBound
