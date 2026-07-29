import Ecdlp.Proved.FrozenProjectiveChartSystem

/-!
# Infinity-stratum pruning for the frozen projective chart cover

This file extracts exact necessary conditions on the infinity mask of a
solution to the stage-14 frozen chart system.

For the triquadratic `H`, setting its first and third projective arguments to
`[1:0]` leaves the square of the middle argument's `v` coordinate.  Therefore,
when every external input is affine, two adjacent intermediate slots cannot
both use the infinity chart.  The admissible masks are consequently separated
subsets of the fourteen-slot path.

The file also records the two endpoint determinant conditions.  If both
endpoint determinants are nonzero, the first and last intermediate slots are
forced to be affine.  In that case the exact chart cover can be restricted to
377 interior separated masks, instead of all 16384 masks.  Without the endpoint
assumptions, the exact separated-mask cover has 987 masks.

The three finite cardinalities use `native_decide`.  The structural identities,
mask-necessity theorems, and cover equivalences are ordinary kernel-checked
proofs.  This file makes no sufficiency, solver, rank, yield, recovery, runtime,
memory, or ECDLP-complexity claim.
-/

namespace Ecdlp.FrozenProjectiveSemaev

/-! ## Local infinity identities -/

/-- The homogeneous determinant of two projective representatives. -/
def projectiveDet
    {K : Type*} [CommRing K] (a b : ProjectivePair K) : K :=
  a.u * b.v - a.v * b.u

/-- An infinity third argument reduces `H` to a squared determinant. -/
theorem HValue_third_infinity
    {K : Type*} [CommRing K] [Nontrivial K]
    (a b : ProjectivePair K) :
    HValue a.coord b.coord (ProjectivePair.infinity (K := K)).coord =
      projectiveDet a b ^ 2 := by
  simp [HValue, projectiveDet, ProjectivePair.coord,
    ProjectivePair.infinity]
  ring

/-- An infinity first argument reduces `H` to a squared determinant. -/
theorem HValue_first_infinity
    {K : Type*} [CommRing K] [Nontrivial K]
    (b c : ProjectivePair K) :
    HValue (ProjectivePair.infinity (K := K)).coord b.coord c.coord =
      projectiveDet b c ^ 2 := by
  simp [HValue, projectiveDet, ProjectivePair.coord,
    ProjectivePair.infinity]
  ring

/-- An infinity middle argument reduces `H` to a squared determinant. -/
theorem HValue_middle_infinity
    {K : Type*} [CommRing K] [Nontrivial K]
    (a c : ProjectivePair K) :
    HValue a.coord (ProjectivePair.infinity (K := K)).coord c.coord =
      projectiveDet a c ^ 2 := by
  simp [HValue, projectiveDet, ProjectivePair.coord,
    ProjectivePair.infinity]
  ring

/-- Infinity at both recursive endpoints exposes the middle `v` coordinate. -/
theorem HValue_first_third_infinity
    {K : Type*} [CommRing K] [Nontrivial K]
    (b : ProjectivePair K) :
    HValue (ProjectivePair.infinity (K := K)).coord b.coord
        (ProjectivePair.infinity (K := K)).coord =
      b.v ^ 2 := by
  simp [HValue, ProjectivePair.coord, ProjectivePair.infinity]

/-- Vanishing of the determinant against an affine right representative fixes
its affine coordinate. -/
theorem projectiveDet_affine_right_eq_zero_iff
    {K : Type*} [Field K]
    (q : ProjectivePair K) (t : K) (hq : q.v ≠ 0) :
    projectiveDet q (ProjectivePair.affine t) = 0 ↔
      t = q.u / q.v := by
  unfold projectiveDet
  simp only [ProjectivePair.affine]
  constructor
  · intro h
    apply (eq_div_iff hq).2
    linear_combination -h
  · intro h
    have hmul := (eq_div_iff hq).1 h
    linear_combination -hmul

/-- Vanishing of the determinant against an affine left representative fixes
its affine coordinate. -/
theorem projectiveDet_affine_left_eq_zero_iff
    {K : Type*} [Field K]
    (q : ProjectivePair K) (t : K) (hq : q.v ≠ 0) :
    projectiveDet (ProjectivePair.affine t) q = 0 ↔
      t = q.u / q.v := by
  unfold projectiveDet
  simp only [ProjectivePair.affine]
  constructor
  · intro h
    apply (eq_div_iff hq).2
    linear_combination h
  · intro h
    have hmul := (eq_div_iff hq).1 h
    linear_combination hmul

/-! ## Necessary mask predicates -/

/-- Every external input is represented on the affine chart. -/
def AffineInputFamily
    {K : Type*} [Field K] (q : ℕ → ProjectivePair K) : Prop :=
  ∀ n : ℕ, (q n).v ≠ 0

/-- No two adjacent intermediate slots use the infinity chart. -/
def SeparatedInfinityMask (I : InfinityMask) : Prop :=
  ∀ i : Fin 13, ¬ (i.castSucc ∈ I ∧ i.succ ∈ I)

instance instDecidableSeparatedInfinityMask (I : InfinityMask) :
    Decidable (SeparatedInfinityMask I) := by
  unfold SeparatedInfinityMask
  infer_instance

/-- The first and last infinity choices satisfy their forced endpoint
determinant equations. -/
def EndpointCompatibleInfinityMask
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) : Prop :=
  ((0 : Fin 14) ∈ I → projectiveDet (q 0) (q 1) = 0) ∧
  ((13 : Fin 14) ∈ I → projectiveDet (q 15) y = 0)

/-- The exact necessary mask filter used by the pruned cover. -/
def AdmissibleInfinityMask
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) : Prop :=
  SeparatedInfinityMask I ∧ EndpointCompatibleInfinityMask q y I

/-- Separated masks with both boundary slots removed. -/
def InteriorSeparatedInfinityMask (I : InfinityMask) : Prop :=
  SeparatedInfinityMask I ∧
    (0 : Fin 14) ∉ I ∧ (13 : Fin 14) ∉ I

instance instDecidableInteriorSeparatedInfinityMask (I : InfinityMask) :
    Decidable (InteriorSeparatedInfinityMask I) := by
  unfold InteriorSeparatedInfinityMask
  infer_instance

private theorem eq_zero_of_sq_eq_zero
    {K : Type*} [Field K] {a : K} (h : a ^ 2 = 0) : a = 0 := by
  by_contra ha
  exact (pow_ne_zero 2 ha) h

/-- A chart solution with affine external inputs cannot have adjacent infinity
slots. -/
theorem frozenChartSystem_separatedInfinityMask
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x) :
    SeparatedInfinityMask I := by
  intro i hi
  rcases hi with ⟨hleft, hright⟩
  have h := hx (.step i)
  change
    HValue (chartPair I x i.castSucc).coord
      (q (i + 2)).coord (chartPair I x i.succ).coord = 0 at h
  have hleftPair :
      chartPair I x i.castSucc =
        ProjectivePair.infinity (K := K) := by
    simp [chartPair, hleft]
  have hrightPair :
      chartPair I x i.succ =
        ProjectivePair.infinity (K := K) := by
    simp [chartPair, hright]
  rw [hleftPair, hrightPair, HValue_first_third_infinity] at h
  exact (pow_ne_zero 2 (hq (i + 2))) h

/-- A chart solution enforces the determinant conditions at every selected
boundary infinity slot. -/
theorem frozenChartSystem_endpointCompatibleInfinityMask
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hx : FrozenChartSystem q y I x) :
    EndpointCompatibleInfinityMask q y I := by
  constructor
  · intro hzero
    have h := hx .base
    change
      HValue (q 0).coord (q 1).coord
        (chartPair I x (0 : Fin 14)).coord = 0 at h
    have hpair :
        chartPair I x (0 : Fin 14) =
          ProjectivePair.infinity (K := K) := by
      simp [chartPair, hzero]
    rw [hpair, HValue_third_infinity] at h
    exact eq_zero_of_sq_eq_zero h
  · intro hlast
    have h := hx .final
    change
      HValue (chartPair I x ⟨13, by decide⟩).coord
        (q 15).coord y.coord = 0 at h
    have hpair :
        chartPair I x ⟨13, by decide⟩ =
          ProjectivePair.infinity (K := K) := by
      simp [chartPair, hlast]
    rw [hpair, HValue_first_infinity] at h
    exact eq_zero_of_sq_eq_zero h

/-- If the left recursive slot is infinity and the right slot is affine, the
right affine coordinate is forced to the normalized current input. -/
theorem frozenChartSystem_leftInfinity_forces_rightCoordinate
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (i : Fin 13)
    (hleft : i.castSucc ∈ I) (hright : i.succ ∉ I)
    (hq : (q (i + 2)).v ≠ 0)
    (hx : FrozenChartSystem q y I x) :
    x ⟨i.succ, hright⟩ =
      (q (i + 2)).u / (q (i + 2)).v := by
  have h := hx (.step i)
  change
    HValue (chartPair I x i.castSucc).coord
      (q (i + 2)).coord (chartPair I x i.succ).coord = 0 at h
  have hleftPair :
      chartPair I x i.castSucc =
        ProjectivePair.infinity (K := K) := by
    simp [chartPair, hleft]
  have hrightPair :
      chartPair I x i.succ =
        ProjectivePair.affine (x ⟨i.succ, hright⟩) := by
    simp [chartPair, hright]
  rw [hleftPair, hrightPair, HValue_first_infinity] at h
  exact
    (projectiveDet_affine_right_eq_zero_iff
      (q (i + 2)) (x ⟨i.succ, hright⟩) hq).mp
        (eq_zero_of_sq_eq_zero h)

/-- If the right recursive slot is infinity and the left slot is affine, the
left affine coordinate is forced to the normalized current input. -/
theorem frozenChartSystem_rightInfinity_forces_leftCoordinate
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (i : Fin 13)
    (hleft : i.castSucc ∉ I) (hright : i.succ ∈ I)
    (hq : (q (i + 2)).v ≠ 0)
    (hx : FrozenChartSystem q y I x) :
    x ⟨i.castSucc, hleft⟩ =
      (q (i + 2)).u / (q (i + 2)).v := by
  have h := hx (.step i)
  change
    HValue (chartPair I x i.castSucc).coord
      (q (i + 2)).coord (chartPair I x i.succ).coord = 0 at h
  have hleftPair :
      chartPair I x i.castSucc =
        ProjectivePair.affine (x ⟨i.castSucc, hleft⟩) := by
    simp [chartPair, hleft]
  have hrightPair :
      chartPair I x i.succ =
        ProjectivePair.infinity (K := K) := by
    simp [chartPair, hright]
  rw [hleftPair, hrightPair, HValue_third_infinity] at h
  exact
    (projectiveDet_affine_left_eq_zero_iff
      (q (i + 2)) (x ⟨i.castSucc, hleft⟩) hq).mp
        (eq_zero_of_sq_eq_zero h)

/-- Every solution mask passes the exact necessary filter. -/
theorem frozenChartSystem_admissibleInfinityMask
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x) :
    AdmissibleInfinityMask q y I :=
  ⟨frozenChartSystem_separatedInfinityMask q y I x hq hx,
    frozenChartSystem_endpointCompatibleInfinityMask q y I x hx⟩

/-- Nonzero endpoint determinants force the first and last intermediate slots
to be affine. -/
theorem admissibleInfinityMask_interior
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hI : AdmissibleInfinityMask q y I) :
    InteriorSeparatedInfinityMask I := by
  rcases hI with ⟨hsep, hboundary⟩
  exact ⟨hsep,
    fun hzero => hbase (hboundary.1 hzero),
    fun hlast => hfinal (hboundary.2 hlast)⟩

/-! ## Exact pruned covers -/

/-- The chart cover restricted to masks satisfying the necessary filter. -/
def FrozenAdmissibleChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ (I : InfinityMask) (x : ChartVar I → K),
    AdmissibleInfinityMask q y I ∧ FrozenChartSystem q y I x

/-- With affine external inputs, restricting to admissible masks loses no
solutions. -/
theorem frozenChartCover_iff_admissibleChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q) :
    FrozenChartCover q y ↔ FrozenAdmissibleChartCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    exact ⟨I, x,
      frozenChartSystem_admissibleInfinityMask q y I x hq hx, hx⟩
  · rintro ⟨I, x, _, hx⟩
    exact ⟨I, x, hx⟩

/-- The corresponding exact restriction of the literal polynomial cover. -/
def FrozenAdmissibleChartPolynomialCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ (I : InfinityMask) (x : ChartVar I → K),
    AdmissibleInfinityMask q y I ∧
      FrozenChartPolynomialSystem q y I x

/-- With affine external inputs, the literal polynomial cover is exactly its
admissible-mask restriction. -/
theorem frozenChartPolynomialCover_iff_admissible
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q) :
    FrozenChartPolynomialCover q y ↔
      FrozenAdmissibleChartPolynomialCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    have hdirect :=
      (frozenChartPolynomialSystem_iff_chartSystem q y I x).mp hx
    exact ⟨I, x,
      frozenChartSystem_admissibleInfinityMask q y I x hq hdirect, hx⟩
  · rintro ⟨I, x, _, hx⟩
    exact ⟨I, x, hx⟩

/-- The recursive chain is exactly the admissible literal polynomial cover
when all external inputs are affine. -/
theorem frozenProjectiveChain_iff_admissibleChartPolynomialCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q) :
    FrozenProjectiveChain q 14 y ↔
      FrozenAdmissibleChartPolynomialCover q y := by
  exact
    (frozenProjectiveChain_iff_chartPolynomialCover q y).trans
      (frozenChartPolynomialCover_iff_admissible q y hq)

/-- The chart cover restricted to separated masks whose two boundary slots are
affine. -/
def FrozenInteriorChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ (I : InfinityMask) (x : ChartVar I → K),
    InteriorSeparatedInfinityMask I ∧ FrozenChartSystem q y I x

/-- Under affine-input and nonzero-endpoint assumptions, the complete chart
cover is exactly the 377-mask interior separated cover. -/
theorem frozenChartCover_iff_interiorChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hq : AffineInputFamily q)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0) :
    FrozenChartCover q y ↔ FrozenInteriorChartCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    have hI :=
      frozenChartSystem_admissibleInfinityMask q y I x hq hx
    exact ⟨I, x,
      admissibleInfinityMask_interior q y I hbase hfinal hI, hx⟩
  · rintro ⟨I, x, _, hx⟩
    exact ⟨I, x, hx⟩

/-! ## Finite mask counts -/

/-- The full fourteen-slot powerset has `2^14 = 16384` masks. -/
theorem card_infinityMask :
    Fintype.card InfinityMask = 16384 := by
  native_decide

/-- A fourteen-slot path has 987 separated subsets. -/
def separatedInfinityMasks : Finset InfinityMask :=
  Finset.univ.filter SeparatedInfinityMask

theorem card_separatedInfinityMask :
    separatedInfinityMasks.card = 987 := by
  native_decide

/-- Removing both boundary slots leaves 377 separated subsets. -/
def interiorSeparatedInfinityMasks : Finset InfinityMask :=
  Finset.univ.filter InteriorSeparatedInfinityMask

theorem card_interiorSeparatedInfinityMask :
    interiorSeparatedInfinityMasks.card = 377 := by
  native_decide

end Ecdlp.FrozenProjectiveSemaev
