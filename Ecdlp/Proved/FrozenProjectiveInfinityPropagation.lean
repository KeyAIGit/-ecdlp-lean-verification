import Ecdlp.Proved.FrozenProjectiveInfinityStrata

/-!
# Propagation from isolated infinity slots

This file continues the exact chart analysis of
`FrozenProjectiveInfinityStrata`.  It propagates the affine coordinates forced
next to an isolated infinity slot into the surrounding frozen equations.

There are four layers.

* Two infinity slots at distance two force a consecutive external-input
  projective determinant to vanish.
* Two infinity slots at distance three force a literal three-input `HValue`
  equation.  The two infinity slots next to the boundary force two further
  literal `HValue` equations.  Under named nonvanishing assumptions these
  facts give the exact mask counts `377 -> 129 -> 69 -> 36`; the independent
  boundary-only restriction gives `129 -> 60`.
* Every internal infinity slot forces a lower-stage frozen prefix or suffix
  specialization to vanish.  Six prefix and six suffix values suffice, with
  maximum frozen stage five rather than eleven.
* With affine external inputs, if those twelve balanced values and the two
  endpoint determinants are nonzero, the complete cover is exactly the
  single empty-mask affine chart.

The final statement is conditional.  It does not assert that the
nonvanishing locus is generic, that a chart has a unique witness, or that the
result changes relation yield, solving degree, runtime, memory, or ECDLP
complexity.  The four finite mask-cardinality theorems use `native_decide`
and therefore inherit its compiler-trust marker; the propagation identities,
one-way resultant argument, mask-necessity theorems, and cover equivalences
use ordinary proofs.
-/

namespace Ecdlp.FrozenProjectiveSemaev

/-! ## Distance-two propagation -/

/-- Interior separated masks with infinity slots also forbidden at distance
two. -/
def GapTwoInteriorInfinityMask (I : InfinityMask) : Prop :=
  InteriorSeparatedInfinityMask I ∧
    ∀ i : Fin 12,
      ¬ (i.castSucc.castSucc ∈ I ∧ i.succ.succ ∈ I)

instance instDecidableGapTwoInteriorInfinityMask (I : InfinityMask) :
    Decidable (GapTwoInteriorInfinityMask I) := by
  unfold GapTwoInteriorInfinityMask
  infer_instance

/-- If two infinity slots are separated by one affine slot, that affine slot
is forced to the normalized coordinate of two consecutive external inputs.
Consequently their projective determinant vanishes. -/
theorem frozenChartSystem_gapTwoInfinity_forces_det_zero
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (i : Fin 12)
    (hleft : i.castSucc.castSucc ∈ I)
    (hright : i.succ.succ ∈ I)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x) :
    projectiveDet (q (i + 2)) (q (i + 3)) = 0 := by
  have hsep :=
    frozenChartSystem_separatedInfinityMask q y I x hq hx
  have hmiddleLeft :
      (i.castSucc : Fin 13).succ ∉ I := by
    intro hmiddle
    exact hsep i.castSucc ⟨hleft, hmiddle⟩
  have hmiddleEq :
      (i.castSucc : Fin 13).succ =
        (i.succ : Fin 13).castSucc :=
    Fin.ext (by rfl)
  have hmiddleRight :
      (i.succ : Fin 13).castSucc ∉ I := by
    rw [← hmiddleEq]
    exact hmiddleLeft
  have hfromLeft :=
    frozenChartSystem_leftInfinity_forces_rightCoordinate
      q y I x i.castSucc hleft hmiddleLeft (hq (i + 2)) hx
  have hfromRight :=
    frozenChartSystem_rightInfinity_forces_leftCoordinate
      q y I x i.succ hmiddleRight hright (hq (i + 3)) hx
  have hvar :
      (⟨(i.castSucc : Fin 13).succ, hmiddleLeft⟩ : ChartVar I) =
        ⟨(i.succ : Fin 13).castSucc, hmiddleRight⟩ :=
    Subtype.ext hmiddleEq
  have hratio :
      (q (i + 2)).u / (q (i + 2)).v =
        (q (i + 3)).u / (q (i + 3)).v := by
    calc
      (q (i + 2)).u / (q (i + 2)).v =
          x ⟨(i.castSucc : Fin 13).succ, hmiddleLeft⟩ := by
            simpa using hfromLeft.symm
      _ = x ⟨(i.succ : Fin 13).castSucc, hmiddleRight⟩ := by
            rw [hvar]
      _ = (q (i + 3)).u / (q (i + 3)).v := by
            simpa using hfromRight
  unfold projectiveDet
  rw [sub_eq_zero]
  simpa [mul_comm] using
    (div_eq_div_iff (hq (i + 2)) (hq (i + 3))).mp hratio

/-- Uniform nonvanishing assumptions for all distance-two exceptional
determinants.  The first and last entries are redundant after endpoint
pruning; retaining them keeps the local guard indexed by the same `Fin 12`
family as the propagation theorem and yields a slightly smaller stated
regular locus than the maximal one. -/
def GapTwoDetRegular
    {K : Type*} [Field K] (q : ℕ → ProjectivePair K) : Prop :=
  ∀ i : Fin 12,
    projectiveDet (q (i + 2)) (q (i + 3)) ≠ 0

/-- Every solution mask satisfies the distance-two filter under the endpoint
and determinant nonvanishing assumptions. -/
theorem frozenChartSystem_gapTwoInteriorInfinityMask
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hgap : GapTwoDetRegular q)
    (hx : FrozenChartSystem q y I x) :
    GapTwoInteriorInfinityMask I := by
  have hadmissible :=
    frozenChartSystem_admissibleInfinityMask q y I x hq hx
  refine ⟨admissibleInfinityMask_interior
      q y I hbase hfinal hadmissible, ?_⟩
  intro i hi
  exact hgap i
    (frozenChartSystem_gapTwoInfinity_forces_det_zero
      q y I x i hi.1 hi.2 hq hx)

/-- The exact chart cover restricted by distance-two propagation. -/
def FrozenGapTwoInteriorChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ (I : InfinityMask) (x : ChartVar I → K),
    GapTwoInteriorInfinityMask I ∧ FrozenChartSystem q y I x

/-- Under the named assumptions, the complete chart cover is exactly its
distance-two propagated restriction. -/
theorem frozenChartCover_iff_gapTwoInteriorChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hgap : GapTwoDetRegular q) :
    FrozenChartCover q y ↔ FrozenGapTwoInteriorChartCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    exact ⟨I, x,
      frozenChartSystem_gapTwoInteriorInfinityMask
        q y I x hq hbase hfinal hgap hx, hx⟩
  · rintro ⟨I, x, _, hx⟩
    exact ⟨I, x, hx⟩

/-- The finite family used only to record the exact logical branch count. -/
def gapTwoInteriorInfinityMasks : Finset InfinityMask :=
  Finset.univ.filter GapTwoInteriorInfinityMask

/-- Twelve interior slots with selected positions at mutual distance at least
three have 129 masks. -/
theorem card_gapTwoInteriorInfinityMask :
    gapTwoInteriorInfinityMasks.card = 129 := by
  native_decide

/-! ## Distance-three propagation -/

/-- If two infinity slots are separated by two affine slots, those two
neighbors are forced by the outer infinity slots.  Substitution into the
middle step leaves the literal three-input `HValue` obstruction. -/
theorem frozenChartSystem_gapThreeInfinity_forces_HValue_zero
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (i : Fin 11)
    (hleft : i.castSucc.castSucc.castSucc ∈ I)
    (hright : i.succ.succ.succ ∈ I)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x) :
    HValue (q (i + 2)).coord (q (i + 3)).coord
      (q (i + 4)).coord = 0 := by
  have hsep :=
    frozenChartSystem_separatedInfinityMask q y I x hq hx
  have hleftNeighbor :
      (i.castSucc.castSucc : Fin 13).succ ∉ I := by
    intro hmiddle
    exact hsep i.castSucc.castSucc ⟨hleft, hmiddle⟩
  have hrightNeighbor :
      (i.succ.succ : Fin 13).castSucc ∉ I := by
    intro hmiddle
    exact hsep i.succ.succ ⟨hmiddle, hright⟩
  have hfromLeft :=
    frozenChartSystem_leftInfinity_forces_rightCoordinate
      q y I x i.castSucc.castSucc hleft hleftNeighbor
        (hq (i + 2)) hx
  have hfromRight :=
    frozenChartSystem_rightInfinity_forces_leftCoordinate
      q y I x i.succ.succ hrightNeighbor hright
        (hq (i + 4)) hx
  have hrightIndexEq :
      (i.succ.succ : Fin 13).castSucc =
        i.castSucc.succ.succ :=
    Fin.ext (by rfl)
  have hrightNeighbor' :
      i.castSucc.succ.succ ∉ I := by
    rw [← hrightIndexEq]
    exact hrightNeighbor
  have hfromRight' :
      x ⟨i.castSucc.succ.succ, hrightNeighbor'⟩ =
        (q (i + 4)).u / (q (i + 4)).v := by
    simpa using hfromRight
  let middle : Fin 13 := i.succ.castSucc
  have hmiddleLeft :
      middle.castSucc =
        (i.castSucc.castSucc : Fin 13).succ :=
    Fin.ext (by rfl)
  have hmiddleRight :
      middle.succ =
        (i.succ.succ : Fin 13).castSucc :=
    Fin.ext (by rfl)
  have hmiddle := hx (.step middle)
  change
    HValue (chartPair I x middle.castSucc).coord
      (q (middle + 2)).coord
      (chartPair I x middle.succ).coord = 0 at hmiddle
  have hleftPair :
      chartPair I x middle.castSucc =
        normalizeProjectivePair (q (i + 2)) := by
    rw [hmiddleLeft]
    have haffine :
        chartPair I x (i.castSucc.castSucc : Fin 13).succ =
          ProjectivePair.affine
            (x ⟨(i.castSucc.castSucc : Fin 13).succ,
              hleftNeighbor⟩) := by
      simp [chartPair, hleftNeighbor]
    rw [haffine, hfromLeft]
    simp [normalizeProjectivePair, hq (i + 2)]
  have hrightPair :
      chartPair I x middle.succ =
        normalizeProjectivePair (q (i + 4)) := by
    rw [hmiddleRight]
    have haffine :
        chartPair I x i.castSucc.succ.succ =
          ProjectivePair.affine
            (x ⟨i.castSucc.succ.succ, hrightNeighbor'⟩) := by
      simp [chartPair, hrightNeighbor']
    rw [hrightIndexEq, haffine, hfromRight']
    simp [normalizeProjectivePair, hq (i + 4)]
  rw [hleftPair, hrightPair] at hmiddle
  apply (HValue_normalize_first_third_zero_iff
    (q (i + 2)) (q (i + 3)).coord (q (i + 4))).mpr
  simpa [middle] using hmiddle

/-- The 129-mask predicate further restricted by the proved distance-three
obstruction. -/
def GapThreeInteriorInfinityMask (I : InfinityMask) : Prop :=
  GapTwoInteriorInfinityMask I ∧
    ∀ i : Fin 11,
      ¬ (i.castSucc.castSucc.castSucc ∈ I ∧
        i.succ.succ.succ ∈ I)

instance instDecidableGapThreeInteriorInfinityMask (I : InfinityMask) :
    Decidable (GapThreeInteriorInfinityMask I) := by
  unfold GapThreeInteriorInfinityMask
  infer_instance

/-- Uniform nonvanishing assumptions for all literal distance-three `HValue`
obstructions.  The first and last entries are redundant after endpoint
pruning; retaining the full `Fin 11` family keeps the local theorem and guard
indices aligned and yields a slightly smaller stated regular locus than the
maximal one. -/
def GapThreeHRegular
    {K : Type*} [Field K] (q : ℕ → ProjectivePair K) : Prop :=
  ∀ i : Fin 11,
    HValue (q (i + 2)).coord (q (i + 3)).coord
      (q (i + 4)).coord ≠ 0

/-- Every solution mask satisfies the distance-three filter under all named
endpoint, distance-two, and distance-three nonvanishing assumptions. -/
theorem frozenChartSystem_gapThreeInteriorInfinityMask
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hgapTwo : GapTwoDetRegular q)
    (hgapThree : GapThreeHRegular q)
    (hx : FrozenChartSystem q y I x) :
    GapThreeInteriorInfinityMask I := by
  refine ⟨frozenChartSystem_gapTwoInteriorInfinityMask
      q y I x hq hbase hfinal hgapTwo hx, ?_⟩
  intro i hi
  exact hgapThree i
    (frozenChartSystem_gapThreeInfinity_forces_HValue_zero
      q y I x i hi.1 hi.2 hq hx)

/-- Exact chart cover after the distance-two and distance-three propagation
layers. -/
def FrozenGapThreeInteriorChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ (I : InfinityMask) (x : ChartVar I → K),
    GapThreeInteriorInfinityMask I ∧ FrozenChartSystem q y I x

/-- Under the named assumptions, the complete chart cover is exactly its
distance-three propagated restriction. -/
theorem frozenChartCover_iff_gapThreeInteriorChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hgapTwo : GapTwoDetRegular q)
    (hgapThree : GapThreeHRegular q) :
    FrozenChartCover q y ↔ FrozenGapThreeInteriorChartCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    exact ⟨I, x,
      frozenChartSystem_gapThreeInteriorInfinityMask
        q y I x hq hbase hfinal hgapTwo hgapThree hx, hx⟩
  · rintro ⟨I, x, _, hx⟩
    exact ⟨I, x, hx⟩

def gapThreeInteriorInfinityMasks : Finset InfinityMask :=
  Finset.univ.filter GapThreeInteriorInfinityMask

/-- Twelve interior slots with selected positions at mutual distance at least
four have 69 masks. -/
theorem card_gapThreeInteriorInfinityMask :
    gapThreeInteriorInfinityMasks.card = 69 := by
  native_decide

/-! ## Boundary-near propagation -/

/-- Infinity in slot one forces the literal three-input prefix equation. -/
theorem frozenChartSystem_slotOneInfinity_forces_HValue_zero
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hone : (1 : Fin 14) ∈ I)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x) :
    HValue (q 0).coord (q 1).coord (q 2).coord = 0 := by
  have hsep :=
    frozenChartSystem_separatedInfinityMask q y I x hq hx
  have hzero : (0 : Fin 14) ∉ I := by
    intro hzero
    exact hsep (0 : Fin 13) ⟨hzero, hone⟩
  have hcoordinate :=
    frozenChartSystem_rightInfinity_forces_leftCoordinate
      q y I x (0 : Fin 13) hzero hone (hq 2) hx
  have hbase := hx .base
  change HValue (q 0).coord (q 1).coord
    (chartPair I x (0 : Fin 14)).coord = 0 at hbase
  have hpair :
      chartPair I x (0 : Fin 14) =
        ProjectivePair.affine (x ⟨0, hzero⟩) := by
    simp [chartPair, hzero]
  have hcoordinate' :
      x ⟨(0 : Fin 14), hzero⟩ = (q 2).u / (q 2).v := by
    simpa using hcoordinate
  rw [hpair, hcoordinate'] at hbase
  apply (HValue_normalize_third_zero_iff
    (q 0).coord (q 1).coord (q 2)).mpr
  simpa [normalizeProjectivePair, hq 2] using hbase

/-- Infinity in slot twelve forces the literal three-input suffix equation. -/
theorem frozenChartSystem_slotTwelveInfinity_forces_HValue_zero
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (htwelve : (12 : Fin 14) ∈ I)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x) :
    HValue (q 14).coord (q 15).coord y.coord = 0 := by
  have hsep :=
    frozenChartSystem_separatedInfinityMask q y I x hq hx
  have hthirteen : (13 : Fin 14) ∉ I := by
    intro hthirteen
    exact hsep (12 : Fin 13) ⟨htwelve, hthirteen⟩
  have hcoordinate :=
    frozenChartSystem_leftInfinity_forces_rightCoordinate
      q y I x (12 : Fin 13) htwelve hthirteen (hq 14) hx
  have hfinal := hx .final
  change HValue
    (chartPair I x (13 : Fin 14)).coord (q 15).coord y.coord = 0 at hfinal
  have hpair :
      chartPair I x (13 : Fin 14) =
        ProjectivePair.affine (x ⟨13, hthirteen⟩) := by
    simp [chartPair, hthirteen]
  have hcoordinate' :
      x ⟨(13 : Fin 14), hthirteen⟩ = (q 14).u / (q 14).v := by
    simpa using hcoordinate
  rw [hpair, hcoordinate'] at hfinal
  apply (HValue_normalize_first_zero_iff
    (q 14) (q 15).coord y.coord).mpr
  simpa [normalizeProjectivePair, hq 14] using hfinal

/-- The distance-two mask predicate with the two boundary-near infinity slots
also removed. -/
def BoundaryPropagatedInfinityMask (I : InfinityMask) : Prop :=
  GapTwoInteriorInfinityMask I ∧
    (1 : Fin 14) ∉ I ∧ (12 : Fin 14) ∉ I

instance instDecidableBoundaryPropagatedInfinityMask (I : InfinityMask) :
    Decidable (BoundaryPropagatedInfinityMask I) := by
  unfold BoundaryPropagatedInfinityMask
  infer_instance

/-- The two literal boundary-near exceptional equations are nonzero. -/
def BoundaryHRegular
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  HValue (q 0).coord (q 1).coord (q 2).coord ≠ 0 ∧
    HValue (q 14).coord (q 15).coord y.coord ≠ 0

/-- Every solution mask satisfies the 60-mask boundary-propagated predicate
under all named local nonvanishing assumptions. -/
theorem frozenChartSystem_boundaryPropagatedInfinityMask
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hgap : GapTwoDetRegular q)
    (hboundary : BoundaryHRegular q y)
    (hx : FrozenChartSystem q y I x) :
    BoundaryPropagatedInfinityMask I := by
  refine ⟨frozenChartSystem_gapTwoInteriorInfinityMask
      q y I x hq hbase hfinal hgap hx, ?_, ?_⟩
  · intro hone
    exact hboundary.1
      (frozenChartSystem_slotOneInfinity_forces_HValue_zero
        q y I x hone hq hx)
  · intro htwelve
    exact hboundary.2
      (frozenChartSystem_slotTwelveInfinity_forces_HValue_zero
        q y I x htwelve hq hx)

/-- Exact chart cover after both local propagation layers. -/
def FrozenBoundaryPropagatedChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ (I : InfinityMask) (x : ChartVar I → K),
    BoundaryPropagatedInfinityMask I ∧ FrozenChartSystem q y I x

/-- Under the local nonvanishing assumptions, the complete chart cover is
exactly the 60-mask propagated restriction. -/
theorem frozenChartCover_iff_boundaryPropagatedChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hgap : GapTwoDetRegular q)
    (hboundary : BoundaryHRegular q y) :
    FrozenChartCover q y ↔ FrozenBoundaryPropagatedChartCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    exact ⟨I, x,
      frozenChartSystem_boundaryPropagatedInfinityMask
        q y I x hq hbase hfinal hgap hboundary hx, hx⟩
  · rintro ⟨I, x, _, hx⟩
    exact ⟨I, x, hx⟩

def boundaryPropagatedInfinityMasks : Finset InfinityMask :=
  Finset.univ.filter BoundaryPropagatedInfinityMask

/-- The ten remaining slots with selected positions at mutual distance at
least three have 60 masks. -/
theorem card_boundaryPropagatedInfinityMask :
    boundaryPropagatedInfinityMasks.card = 60 := by
  native_decide

/-- The boundary-propagated predicate with distance-three pairs also
removed. -/
def BoundaryGapThreeInfinityMask (I : InfinityMask) : Prop :=
  GapThreeInteriorInfinityMask I ∧
    (1 : Fin 14) ∉ I ∧ (12 : Fin 14) ∉ I

instance instDecidableBoundaryGapThreeInfinityMask (I : InfinityMask) :
    Decidable (BoundaryGapThreeInfinityMask I) := by
  unfold BoundaryGapThreeInfinityMask
  infer_instance

/-- Every solution mask satisfies the combined local propagation predicate
under all named nonvanishing assumptions. -/
theorem frozenChartSystem_boundaryGapThreeInfinityMask
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hgapTwo : GapTwoDetRegular q)
    (hgapThree : GapThreeHRegular q)
    (hboundary : BoundaryHRegular q y)
    (hx : FrozenChartSystem q y I x) :
    BoundaryGapThreeInfinityMask I := by
  refine ⟨frozenChartSystem_gapThreeInteriorInfinityMask
      q y I x hq hbase hfinal hgapTwo hgapThree hx, ?_, ?_⟩
  · intro hone
    exact hboundary.1
      (frozenChartSystem_slotOneInfinity_forces_HValue_zero
        q y I x hone hq hx)
  · intro htwelve
    exact hboundary.2
      (frozenChartSystem_slotTwelveInfinity_forces_HValue_zero
        q y I x htwelve hq hx)

/-- Exact chart cover after all three local propagation layers. -/
def FrozenBoundaryGapThreeChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ (I : InfinityMask) (x : ChartVar I → K),
    BoundaryGapThreeInfinityMask I ∧ FrozenChartSystem q y I x

theorem frozenChartCover_iff_boundaryGapThreeChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hgapTwo : GapTwoDetRegular q)
    (hgapThree : GapThreeHRegular q)
    (hboundary : BoundaryHRegular q y) :
    FrozenChartCover q y ↔ FrozenBoundaryGapThreeChartCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    exact ⟨I, x,
      frozenChartSystem_boundaryGapThreeInfinityMask
        q y I x hq hbase hfinal hgapTwo hgapThree hboundary hx, hx⟩
  · rintro ⟨I, x, _, hx⟩
    exact ⟨I, x, hx⟩

def boundaryGapThreeInfinityMasks : Finset InfinityMask :=
  Finset.univ.filter BoundaryGapThreeInfinityMask

/-- Removing both boundary-near slots from the 69-mask family leaves 36
logical masks. -/
theorem card_boundaryGapThreeInfinityMask :
    boundaryGapThreeInfinityMasks.card = 36 := by
  native_decide

/-! ## Prefix obstruction values and the conditional affine chart -/

/-- Every prefix of a fixed chain vector is itself the corresponding frozen
projective chain. -/
theorem frozenChainVector_prefix
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (z : Fin 14 → ProjectivePair K)
    (hz : FrozenChainVector q y z)
    (n : ℕ) (hn : n < 14) :
    FrozenProjectiveChain q n (z ⟨n, hn⟩) := by
  rcases hz with ⟨hbase, hstep, _⟩
  induction n with
  | zero =>
      have hi : (⟨0, hn⟩ : Fin 14) = 0 := Fin.ext (by rfl)
      simpa only [FrozenProjectiveChain, hi] using hbase
  | succ n ih =>
      rw [FrozenProjectiveChain]
      refine ⟨z ⟨n, by omega⟩, ih (by omega), ?_⟩
      let i : Fin 13 := ⟨n, by omega⟩
      have hl :
          i.castSucc = (⟨n, by omega⟩ : Fin 14) :=
        Fin.ext (by rfl)
      have hr :
          i.succ = (⟨n + 1, hn⟩ : Fin 14) :=
        Fin.ext (by rfl)
      have hs := hstep i
      rw [hl, hr] at hs
      simpa [i] using hs

/-- Normalizing only the output representative preserves and reflects a
frozen prefix chain. -/
theorem frozenProjectiveChain_normalize_output_iff
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (s : ℕ) (z : ProjectivePair K) :
    FrozenProjectiveChain q s (normalizeProjectivePair z) ↔
      FrozenProjectiveChain q s z := by
  cases s with
  | zero =>
      exact (HValue_normalize_third_zero_iff
        (q 0).coord (q 1).coord z).symm
  | succ s =>
      constructor
      · rintro ⟨w, hw, hlocal⟩
        exact ⟨w, hw,
          (HValue_normalize_third_zero_iff
            w.coord (q (s + 2)).coord z).mpr hlocal⟩
      · rintro ⟨w, hw, hlocal⟩
        exact ⟨w, hw,
          (HValue_normalize_third_zero_iff
            w.coord (q (s + 2)).coord z).mp hlocal⟩

/-! ## One-way resultant propagation over the base field -/

open Polynomial

/-- A common projective root forces the fixed-size TASK Sylvester determinant
to vanish over any field.

Only the reverse direction needs algebraic closure.  Keeping this implication
separate lets the infinity-propagation results apply directly over finite
fields such as the base field of secp256k1. -/
theorem taskSylvester_det_eq_zero_of_common_projective_root
    {K : Type*} [Field K]
    (f g : K[X]) {m n : ℕ}
    (hm : 0 < m) (hn : 0 < n)
    (hf : f.natDegree ≤ m) (hg : g.natDegree ≤ n)
    (hroot :
      Ecdlp.ProjectiveResultant.HasCommonProjectiveRoot f g m n) :
    (Ecdlp.TaskSylvester.taskSylvester f g m n).det = 0 := by
  rw [Ecdlp.TaskSylvester.det_taskSylvester_eq_resultant]
  rcases hroot with ⟨U, V, hUV, hF, hG⟩
  by_cases hV : V = 0
  · subst V
    have hU : U ≠ 0 := hUV.resolve_right (by simp)
    rw [Ecdlp.ProjectiveResultant.eval_homogenize_second_zero] at hF hG
    have hfc : f.coeff m = 0 :=
      (mul_eq_zero.mp hF).resolve_right (pow_ne_zero m hU)
    have hgc : g.coeff n = 0 :=
      (mul_eq_zero.mp hG).resolve_right (pow_ne_zero n hU)
    exact Polynomial.resultant_eq_zero_of_lt_lt f g m n
      (Ecdlp.ProjectiveResultant.natDegree_lt_of_le_of_coeff_eq_zero
        hm hf hfc)
      (Ecdlp.ProjectiveResultant.natDegree_lt_of_le_of_coeff_eq_zero
        hn hg hgc)
  · have hfeval : f.eval (U / V) = 0 := by
      rw [Polynomial.eval_homogenize hf ![U, V] (by simpa)] at hF
      exact (mul_eq_zero.mp hF).resolve_right (pow_ne_zero m hV)
    have hgeval : g.eval (U / V) = 0 := by
      rw [Polynomial.eval_homogenize hg ![U, V] (by simpa)] at hG
      exact (mul_eq_zero.mp hG).resolve_right (pow_ne_zero n hV)
    obtain ⟨p, r, _, _, hpr⟩ :=
      Polynomial.exists_mul_add_mul_eq_C_resultant
        f g hf hg (Or.inl hm.ne')
    have hev := congrArg (Polynomial.eval (U / V)) hpr
    simp only [Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_C,
      hfeval, hgeval, zero_mul, add_zero] at hev
    exact hev.symm

/-- A complete frozen projective chain forces the corresponding literal
frozen specialization to vanish over any target field.

This is the one-way half of
`specializeOver_frozenC_eq_zero_iff_projectiveChain`; it deliberately avoids
the algebraic-closure assumption needed to reconstruct roots from a
vanishing resultant. -/
theorem specializeOver_frozenC_eq_zero_of_projectiveChain
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (s : ℕ)
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    FrozenProjectiveChain q s y →
      specializeOver φ q y (frozenC k s) = 0 := by
  induction s generalizing y with
  | zero =>
      intro h
      rw [specializeOver_frozenC_zero]
      exact h
  | succ s ih =>
      rintro ⟨z, hprevious, hlocal⟩
      rw [specialize_frozenC_succ_over]
      apply taskSylvester_det_eq_zero_of_common_projective_root
        _ _ (by positivity) (by norm_num)
        (previousSliceAtOver_frozenC_natDegree_le φ s q)
        (localSliceAt_natDegree_le _ _)
      refine ⟨z.u, z.v, z.valid, ?_, ?_⟩
      · rw [eval_homogenize_previousSliceAtOver_frozenC]
        exact ih z hprevious
      · rw [eval_homogenize_localSliceAt]
        exact hlocal

/-- Slot `j + 1` is the internal slot governed by prefix stage `j`. -/
def internalInfinitySlot (j : Fin 12) : Fin 14 :=
  ⟨j + 1, by omega⟩

/-- The explicit lower-stage value obtained after substituting the affine
neighbor forced to the left of internal infinity slot `j + 1`.

At `j = 0` this is the literal value `H(q₀,q₁,q₂)`.  At `j = 11` it is a
stage-11 frozen prefix, never the full stage-14 target equation. -/
noncomputable def propagatedPrefixValue
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (j : Fin 12) : K :=
  specializeOver (RingHom.id K) q (q (j + 2)) (frozenC K j.val)

/-- The first propagated prefix obstruction is the literal boundary-near
three-input value. -/
theorem propagatedPrefixValue_zero
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) :
    propagatedPrefixValue q (0 : Fin 12) =
      HValue (q 0).coord (q 1).coord (q 2).coord := by
  simp [propagatedPrefixValue, specializeOver_frozenC_zero]

/-- Nonvanishing of all twelve explicit propagated prefix values. -/
def PropagatedPrefixRegular
    {K : Type*} [Field K] (q : ℕ → ProjectivePair K) : Prop :=
  ∀ j : Fin 12, propagatedPrefixValue q j ≠ 0

/-- An internal infinity slot forces its propagated lower-stage prefix value
to vanish. -/
theorem frozenChartSystem_internalInfinity_forces_prefix_zero
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (j : Fin 12)
    (hj : internalInfinitySlot j ∈ I)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x) :
    propagatedPrefixValue q j = 0 := by
  have hsep :=
    frozenChartSystem_separatedInfinityMask q y I x hq hx
  have hrightSlot :
      j.castSucc.succ = internalInfinitySlot j :=
    Fin.ext (by rfl)
  have hright : j.castSucc.succ ∈ I := by
    rw [hrightSlot]
    exact hj
  have hleft : j.castSucc.castSucc ∉ I := by
    intro hleft
    exact hsep j.castSucc ⟨hleft, hright⟩
  have hcoordinate :=
    frozenChartSystem_rightInfinity_forces_leftCoordinate
      q y I x j.castSucc hleft hright (hq (j + 2)) hx
  have hvector :
      FrozenChainVector q y (chartPair I x) :=
    (frozenChainVector_iff_chartSystem q y I x).mpr hx
  have hprefix :=
    frozenChainVector_prefix q y (chartPair I x) hvector
      j.val (by omega)
  have hslot :
      (⟨j.val, by omega⟩ : Fin 14) = j.castSucc.castSucc :=
    Fin.ext (by rfl)
  rw [hslot] at hprefix
  have hpair :
      chartPair I x j.castSucc.castSucc =
        normalizeProjectivePair (q (j + 2)) := by
    have haffine :
        chartPair I x j.castSucc.castSucc =
          ProjectivePair.affine
            (x ⟨j.castSucc.castSucc, hleft⟩) := by
      simp [chartPair, hleft]
    rw [haffine, hcoordinate]
    simp [normalizeProjectivePair, hq (j + 2)]
  rw [hpair] at hprefix
  have hprefixOriginal :
      FrozenProjectiveChain q j.val (q (j + 2)) :=
    (frozenProjectiveChain_normalize_output_iff
      q j.val (q (j + 2))).mp hprefix
  exact
    specializeOver_frozenC_eq_zero_of_projectiveChain
      (RingHom.id K) j.val q (q (j + 2)) hprefixOriginal

/-- Under endpoint and propagated-prefix nonvanishing, every solution uses
the empty infinity mask. -/
theorem frozenChartSystem_propagatedPrefixRegular_mask_eq_empty
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hregular : PropagatedPrefixRegular q)
    (hx : FrozenChartSystem q y I x) :
    I = ∅ := by
  have hadmissible :=
    frozenChartSystem_admissibleInfinityMask q y I x hq hx
  have hinterior :=
    admissibleInfinityMask_interior q y I hbase hfinal hadmissible
  apply Finset.eq_empty_iff_forall_notMem.mpr
  intro i hi
  have hpos : 0 < i.val := by
    by_contra h
    have hi0 : i = (0 : Fin 14) := Fin.ext (by omega)
    exact hinterior.2.1 (by simpa [hi0] using hi)
  have hlt : i.val < 13 := by
    by_contra h
    have hi13 : i = (13 : Fin 14) := Fin.ext (by omega)
    exact hinterior.2.2 (by simpa [hi13] using hi)
  let j : Fin 12 := ⟨i.val - 1, by omega⟩
  have hslot : internalInfinitySlot j = i := by
    apply Fin.ext
    simp [internalInfinitySlot, j]
    omega
  exact hregular j
    (frozenChartSystem_internalInfinity_forces_prefix_zero
      q y I x j (by simpa [hslot] using hi) hq hx)

/-! ## Balanced prefix/suffix obstruction values -/

/-- The three-input value is symmetric in its first and third projective
arguments. -/
theorem HValue_swap_first_third
    {R : Type*} [CommRing R] (q₁ q₂ q₃ : Axis → R) :
    HValue q₁ q₂ q₃ = HValue q₃ q₂ q₁ := by
  unfold HValue
  ring

/-- External inputs for reading the frozen chain from the target end:
`q₁₅, y, q₁₄, q₁₃, ...`.

Together with first/third symmetry of `HValue`, this turns a suffix of the
original chain into an ordinary frozen prefix. -/
def reverseFrozenInputs
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    ℕ → ProjectivePair K
  | 0 => q 15
  | n + 1 =>
      match n with
      | 0 => y
      | m + 1 => q (14 - m)

/-- Every suffix of a fixed chain vector is a frozen prefix for the reversed
input family. -/
theorem frozenChainVector_suffix
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (z : Fin 14 → ProjectivePair K)
    (hz : FrozenChainVector q y z)
    (n : ℕ) (hn : n < 14) :
    FrozenProjectiveChain (reverseFrozenInputs q y) n
      (z ⟨13 - n, by omega⟩) := by
  rcases hz with ⟨_, hstep, hfinal⟩
  induction n with
  | zero =>
      rw [FrozenProjectiveChain]
      rw [HValue_cycle] at hfinal
      simpa [reverseFrozenInputs] using hfinal
  | succ n ih =>
      rw [FrozenProjectiveChain]
      refine ⟨z ⟨13 - n, by omega⟩, ih (by omega), ?_⟩
      let i : Fin 13 := ⟨12 - n, by omega⟩
      have hl :
          i.castSucc = (⟨12 - n, by omega⟩ : Fin 14) :=
        Fin.ext (by rfl)
      have hr :
          i.succ = (⟨13 - n, by omega⟩ : Fin 14) :=
        Fin.ext (by simp [i]; omega)
      have hinput : i.val + 2 = 14 - n := by
        simp [i]
        omega
      have houtput :
          (⟨13 - (n + 1), by omega⟩ : Fin 14) =
            ⟨12 - n, by omega⟩ :=
        Fin.ext (by
          change 13 - (n + 1) = 12 - n
          omega)
      have hreverse :
          reverseFrozenInputs q y (n + 2) = q (14 - n) := by
        simp [reverseFrozenInputs]
      have hs := hstep i
      rw [hl, hr, hinput] at hs
      rw [hreverse, houtput]
      rw [HValue_swap_first_third]
      exact hs

/-- Slot `12 - j` is the internal slot governed from the target side by
suffix stage `j`. -/
def balancedSuffixInfinitySlot (j : Fin 6) : Fin 14 :=
  ⟨12 - j.val, by omega⟩

/-- The explicit lower-stage value obtained after substituting the affine
neighbor forced to the right of internal infinity slot `12 - j`.

For `j : Fin 6`, both this suffix family and the matching prefix family use
only frozen stages zero through five. -/
noncomputable def balancedSuffixValue
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (j : Fin 6) : K :=
  specializeOver (RingHom.id K) (reverseFrozenInputs q y)
    (q (14 - j.val)) (frozenC K j.val)

/-- The first balanced suffix obstruction is exactly the literal
boundary-near suffix value, after cyclic symmetry of `HValue`. -/
theorem balancedSuffixValue_zero
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    balancedSuffixValue q y (0 : Fin 6) =
      HValue (q 14).coord (q 15).coord y.coord := by
  rw [show balancedSuffixValue q y (0 : Fin 6) =
      HValue (q 15).coord y.coord (q 14).coord by
    simp [balancedSuffixValue, reverseFrozenInputs,
      specializeOver_frozenC_zero]]
  rw [HValue_cycle, HValue_cycle]

/-- Six prefix and six suffix nonvanishing conditions cover all twelve
internal infinity slots while keeping the maximum frozen stage equal to
five. -/
def BalancedPropagatedRegular
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  (∀ j : Fin 6,
    propagatedPrefixValue q ⟨j.val, by omega⟩ ≠ 0) ∧
  (∀ j : Fin 6, balancedSuffixValue q y j ≠ 0)

/-- An infinity slot in the right half forces its balanced lower-stage suffix
value to vanish. -/
theorem frozenChartSystem_balancedSuffixInfinity_forces_zero
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (j : Fin 6)
    (hj : balancedSuffixInfinitySlot j ∈ I)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x) :
    balancedSuffixValue q y j = 0 := by
  have hsep :=
    frozenChartSystem_separatedInfinityMask q y I x hq hx
  let i : Fin 13 := ⟨12 - j.val, by omega⟩
  have hleft : i.castSucc ∈ I := by
    simpa [i, balancedSuffixInfinitySlot] using hj
  have hright : i.succ ∉ I := by
    intro hright
    exact hsep i ⟨hleft, hright⟩
  have hinput : i.val + 2 = 14 - j.val := by
    simp [i]
    omega
  have hcoordinate :=
    frozenChartSystem_leftInfinity_forces_rightCoordinate
      q y I x i hleft hright (hq (i + 2)) hx
  rw [hinput] at hcoordinate
  have hvector :
      FrozenChainVector q y (chartPair I x) :=
    (frozenChainVector_iff_chartSystem q y I x).mpr hx
  have hsuffix :=
    frozenChainVector_suffix q y (chartPair I x) hvector
      j.val (by omega)
  have hslot :
      (⟨13 - j.val, by omega⟩ : Fin 14) = i.succ :=
    Fin.ext (by simp [i]; omega)
  rw [hslot] at hsuffix
  have hpair :
      chartPair I x i.succ =
        normalizeProjectivePair (q (14 - j.val)) := by
    have haffine :
        chartPair I x i.succ =
          ProjectivePair.affine (x ⟨i.succ, hright⟩) := by
      simp [chartPair, hright]
    rw [haffine, hcoordinate]
    simp [normalizeProjectivePair, hq (14 - j.val)]
  rw [hpair] at hsuffix
  have hsuffixOriginal :
      FrozenProjectiveChain (reverseFrozenInputs q y) j.val
        (q (14 - j.val)) :=
    (frozenProjectiveChain_normalize_output_iff
      (reverseFrozenInputs q y) j.val
      (q (14 - j.val))).mp hsuffix
  exact
    specializeOver_frozenC_eq_zero_of_projectiveChain
      (RingHom.id K) j.val (reverseFrozenInputs q y)
      (q (14 - j.val)) hsuffixOriginal

/-- Endpoint regularity plus the balanced six-prefix/six-suffix obstruction
conditions exclude every infinity slot over the original base field. -/
theorem frozenChartSystem_balancedPropagatedRegular_mask_eq_empty
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hregular : BalancedPropagatedRegular q y)
    (hx : FrozenChartSystem q y I x) :
    I = ∅ := by
  have hadmissible :=
    frozenChartSystem_admissibleInfinityMask q y I x hq hx
  have hinterior :=
    admissibleInfinityMask_interior q y I hbase hfinal hadmissible
  apply Finset.eq_empty_iff_forall_notMem.mpr
  intro i hi
  have hpos : 0 < i.val := by
    by_contra h
    have hi0 : i = (0 : Fin 14) := Fin.ext (by omega)
    exact hinterior.2.1 (by simpa [hi0] using hi)
  have hle12 : i.val ≤ 12 := by
    by_contra h
    have hi13 : i = (13 : Fin 14) := Fin.ext (by omega)
    exact hinterior.2.2 (by simpa [hi13] using hi)
  by_cases hleftHalf : i.val ≤ 6
  · let j : Fin 6 := ⟨i.val - 1, by omega⟩
    let j₁₂ : Fin 12 := ⟨j.val, by omega⟩
    have hslot : internalInfinitySlot j₁₂ = i := by
      apply Fin.ext
      simp [internalInfinitySlot, j₁₂, j]
      omega
    exact hregular.1 j
      (by
        simpa [j₁₂] using
          frozenChartSystem_internalInfinity_forces_prefix_zero
            q y I x j₁₂ (by simpa [hslot] using hi) hq hx)
  · let j : Fin 6 := ⟨12 - i.val, by omega⟩
    have hslot : balancedSuffixInfinitySlot j = i := by
      apply Fin.ext
      simp [balancedSuffixInfinitySlot, j]
      omega
    exact hregular.2 j
      (frozenChartSystem_balancedSuffixInfinity_forces_zero
        q y I x j (by simpa [hslot] using hi) hq hx)

/-- The single chart with no infinity slots. -/
def FrozenAffineChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ x : ChartVar (∅ : InfinityMask) → K,
    FrozenChartSystem q y ∅ x

/-- The literal polynomial version of the single empty-mask chart. -/
def FrozenAffineChartPolynomialCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ x : ChartVar (∅ : InfinityMask) → K,
    FrozenChartPolynomialSystem q y ∅ x

/-- The full chart cover is exactly the single affine chart on the explicit
propagated-prefix regular locus. -/
theorem frozenChartCover_iff_affineChartCover_of_propagatedPrefixRegular
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hregular : PropagatedPrefixRegular q) :
    FrozenChartCover q y ↔ FrozenAffineChartCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    have hI :=
      frozenChartSystem_propagatedPrefixRegular_mask_eq_empty
        q y I x hq hbase hfinal hregular hx
    subst I
    exact ⟨x, hx⟩
  · rintro ⟨x, hx⟩
    exact ⟨∅, x, hx⟩

/-- The literal polynomial cover has the same exact single-chart restriction
on the propagated-prefix regular locus. -/
theorem frozenChartPolynomialCover_iff_affine_of_propagatedPrefixRegular
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hregular : PropagatedPrefixRegular q) :
    FrozenChartPolynomialCover q y ↔
      FrozenAffineChartPolynomialCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    have hchart :=
      (frozenChartPolynomialSystem_iff_chartSystem q y I x).mp hx
    have hI :=
      frozenChartSystem_propagatedPrefixRegular_mask_eq_empty
        q y I x hq hbase hfinal hregular hchart
    subst I
    exact ⟨x, hx⟩
  · rintro ⟨x, hx⟩
    exact ⟨∅, x, hx⟩

/-- The complete chart cover is exactly the single affine chart on the
balanced explicit regular locus, over the original base field. -/
theorem frozenChartCover_iff_affineChartCover_of_balancedPropagatedRegular
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hregular : BalancedPropagatedRegular q y) :
    FrozenChartCover q y ↔ FrozenAffineChartCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    have hI :=
      frozenChartSystem_balancedPropagatedRegular_mask_eq_empty
        q y I x hq hbase hfinal hregular hx
    subst I
    exact ⟨x, hx⟩
  · rintro ⟨x, hx⟩
    exact ⟨∅, x, hx⟩

/-- The literal polynomial cover has the same balanced single-chart
restriction over the original base field. -/
theorem frozenChartPolynomialCover_iff_affine_of_balancedPropagatedRegular
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hregular : BalancedPropagatedRegular q y) :
    FrozenChartPolynomialCover q y ↔
      FrozenAffineChartPolynomialCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    have hchart :=
      (frozenChartPolynomialSystem_iff_chartSystem q y I x).mp hx
    have hI :=
      frozenChartSystem_balancedPropagatedRegular_mask_eq_empty
        q y I x hq hbase hfinal hregular hchart
    subst I
    exact ⟨x, hx⟩
  · rintro ⟨x, hx⟩
    exact ⟨∅, x, hx⟩

/-- After the existing injective algebraically closed base change, the source
frozen stage-14 equation is exactly the single affine chart on the mapped
affine-input, endpoint-regular, balanced regular locus.

The algebraic-closure assumption here belongs only to the upstream
source-equation/witness-chain equivalence.  The propagation and empty-mask
theorems used after that bridge hold over every field.  Target witnesses are
not asserted to descend to the source field. -/
theorem frozenRecS17_iff_affineChartPolynomialCover_over_of_balancedPropagatedRegular
    {k K : Type*} [Field k] [Field K] [IsAlgClosed K]
    (φ : k →+* K) (hφ : Function.Injective φ)
    (q : ℕ → ProjectivePair k) (y : ProjectivePair k)
    (hq : AffineInputFamily
      (fun i => mapProjectivePair φ hφ (q i)))
    (hbase :
      projectiveDet
        (mapProjectivePair φ hφ (q 0))
        (mapProjectivePair φ hφ (q 1)) ≠ 0)
    (hfinal :
      projectiveDet
        (mapProjectivePair φ hφ (q 15))
        (mapProjectivePair φ hφ y) ≠ 0)
    (hregular :
      BalancedPropagatedRegular
        (fun i => mapProjectivePair φ hφ (q i))
        (mapProjectivePair φ hφ y)) :
    specialize q y (frozenC k 14) = 0 ↔
      FrozenAffineChartPolynomialCover
        (fun i => mapProjectivePair φ hφ (q i))
        (mapProjectivePair φ hφ y) := by
  exact
    (frozenRecS17_iff_chartPolynomialCover_over φ hφ q y).trans
      (frozenChartPolynomialCover_iff_affine_of_balancedPropagatedRegular
        (fun i => mapProjectivePair φ hφ (q i))
        (mapProjectivePair φ hφ y)
        hq hbase hfinal hregular)

end Ecdlp.FrozenProjectiveSemaev
