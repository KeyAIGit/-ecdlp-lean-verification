import Ecdlp.Proved.FrozenProjectiveGuardSystem

/-!
# A finite chart cover for the frozen projective witness chain

This file replaces the four-scalar guarded representation of each of the
fourteen intermediate projective slots by the standard two-chart cover of
`P¹`.  A mask selects `[1:0]` for its infinity slots and `[Xᵢ:1]` for every
remaining affine slot.  Each fixed chart therefore has fifteen literal `H`
equations and exactly `14 - I.card` scalar variables.

The union over all masks is proved equivalent to the existing stage-14
projective witness chain, to its guarded polynomial encoding, and, after an
injective base change to an algebraically closed target field, to the source
frozen `C₁₆` equation.  Target-field witnesses are not asserted to descend to
the source field.

Among the two cardinality theorems introduced here, only
`card_chartEquation` uses `native_decide`; `card_chartVar` has an ordinary
proof.  All degree statements are upper bounds and may be lowered by
coefficient cancellation.  This module makes no solver, rank, yield, recovery,
or cost claim.
-/

namespace Ecdlp.FrozenProjectiveSemaev

/-! ## Direct chart semantics -/

/-- Slots represented by the distinguished infinity chart `[1:0]`. -/
abbrev InfinityMask := Finset (Fin 14)

/-- One affine scalar for each slot not selected by the infinity mask. -/
abbrev ChartVar (I : InfinityMask) := {i : Fin 14 // i ∉ I}

/-- The fifteen `H` equations left after selecting one chart in every slot. -/
inductive ChartEquation
  | base
  | step (i : Fin 13)
  | final
  deriving DecidableEq, Fintype

/-- The selected representative in slot `i`: `[1:0]` on the infinity chart,
and `[Xᵢ:1]` on the affine chart. -/
noncomputable def chartPair
    {K : Type*} [Field K]
    (I : InfinityMask) (x : ChartVar I → K) (i : Fin 14) :
    ProjectivePair K :=
  if hi : i ∈ I then
    .infinity
  else
    .affine (x ⟨i, hi⟩)

/-- The literal value of one of the fifteen chart equations. -/
noncomputable def chartEquationValue
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K) :
    ChartEquation → K
  | .base =>
      HValue (q 0).coord (q 1).coord (chartPair I x 0).coord
  | .step i =>
      HValue (chartPair I x i.castSucc).coord
        (q (i + 2)).coord (chartPair I x i.succ).coord
  | .final =>
      HValue (chartPair I x ⟨13, by decide⟩).coord
        (q 15).coord y.coord

/-- A fixed mask chart is the common zero locus of its fifteen literal
`H` equations. -/
def FrozenChartSystem
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K) : Prop :=
  ∀ e : ChartEquation, chartEquationValue q y I x e = 0

/-- The finite cover over all choices of affine and infinity charts. -/
def FrozenChartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ (I : InfinityMask) (x : ChartVar I → K),
    FrozenChartSystem q y I x

/-! ## Projective normalization -/

/-- Simultaneous rescaling of the three projective arguments. -/
theorem HValue_scale
    {K : Type*} [Field K]
    (a b c : K) (q₁ q₂ q₃ : Axis → K) :
    HValue (fun t => a * q₁ t)
        (fun t => b * q₂ t)
        (fun t => c * q₃ t) =
      a ^ 2 * b ^ 2 * c ^ 2 * HValue q₁ q₂ q₃ := by
  unfold HValue
  ring

/-- Nonzero projective rescaling preserves and reflects vanishing of `H`. -/
theorem HValue_rescale_zero_iff
    {K : Type*} [Field K]
    {a b c : K} (ha : a ≠ 0) (hb : b ≠ 0) (hc : c ≠ 0)
    (q₁ q₂ q₃ : Axis → K) :
    HValue (fun t => a * q₁ t)
        (fun t => b * q₂ t)
        (fun t => c * q₃ t) = 0 ↔
      HValue q₁ q₂ q₃ = 0 := by
  rw [HValue_scale]
  simp [ha, hb, hc]

/-- The canonical representative chosen from the two-chart cover. -/
noncomputable def normalizeProjectivePair
    {K : Type*} [Field K] (z : ProjectivePair K) :
    ProjectivePair K := by
  classical
  exact
    if hz : z.v = 0 then
      .infinity
    else
      .affine (z.u / z.v)

/-- The nonzero scalar relating a representative to its chart normalization. -/
noncomputable def projectiveScale
    {K : Type*} [Field K] (z : ProjectivePair K) : K := by
  classical
  exact if z.v = 0 then z.u else z.v

theorem projectiveScale_ne_zero
    {K : Type*} [Field K] (z : ProjectivePair K) :
    projectiveScale z ≠ 0 := by
  classical
  rcases z.valid with hu | hv
  · by_cases hz : z.v = 0
    · simpa [projectiveScale, hz] using hu
    · change (if z.v = 0 then z.u else z.v) ≠ 0
      rw [if_neg hz]
      exact hz
  · by_cases hz : z.v = 0
    · exact (hv hz).elim
    · change (if z.v = 0 then z.u else z.v) ≠ 0
      rw [if_neg hz]
      exact hz

theorem coord_eq_projectiveScale_mul_normalize
    {K : Type*} [Field K] (z : ProjectivePair K) (a : Axis) :
    z.coord a =
      projectiveScale z * (normalizeProjectivePair z).coord a := by
  by_cases hz : z.v = 0
  · have hu : z.u ≠ 0 := by
      rcases z.valid with hu | hv
      · exact hu
      · exact (hv hz).elim
    cases a <;>
      simp [projectiveScale, normalizeProjectivePair, hz,
        ProjectivePair.coord, ProjectivePair.infinity]
  · cases a <;>
      simp [projectiveScale, normalizeProjectivePair, hz,
        ProjectivePair.coord, ProjectivePair.affine, div_eq_mul_inv]
    field_simp

/-- Normalize all three projective arguments without changing whether the
triquadratic vanishes. -/
theorem HValue_normalize_zero_iff
    {K : Type*} [Field K]
    (z₁ z₂ z₃ : ProjectivePair K) :
    HValue z₁.coord z₂.coord z₃.coord = 0 ↔
      HValue (normalizeProjectivePair z₁).coord
        (normalizeProjectivePair z₂).coord
        (normalizeProjectivePair z₃).coord = 0 := by
  have hcoord (z : ProjectivePair K) :
      z.coord =
        fun t => projectiveScale z * (normalizeProjectivePair z).coord t := by
    funext t
    exact coord_eq_projectiveScale_mul_normalize z t
  rw [hcoord z₁, hcoord z₂, hcoord z₃]
  exact HValue_rescale_zero_iff
    (projectiveScale_ne_zero z₁)
    (projectiveScale_ne_zero z₂)
    (projectiveScale_ne_zero z₃)
    _ _ _

theorem HValue_normalize_third_zero_iff
    {K : Type*} [Field K]
    (q₁ q₂ : Axis → K) (z : ProjectivePair K) :
    HValue q₁ q₂ z.coord = 0 ↔
      HValue q₁ q₂ (normalizeProjectivePair z).coord = 0 := by
  have hcoord :
      z.coord =
        fun t => projectiveScale z * (normalizeProjectivePair z).coord t := by
    funext t
    exact coord_eq_projectiveScale_mul_normalize z t
  rw [hcoord]
  simpa using
    (HValue_rescale_zero_iff
      (a := (1 : K)) (b := (1 : K)) (c := projectiveScale z)
      one_ne_zero one_ne_zero (projectiveScale_ne_zero z)
      q₁ q₂ (normalizeProjectivePair z).coord)

theorem HValue_normalize_first_zero_iff
    {K : Type*} [Field K]
    (z : ProjectivePair K) (q₂ q₃ : Axis → K) :
    HValue z.coord q₂ q₃ = 0 ↔
      HValue (normalizeProjectivePair z).coord q₂ q₃ = 0 := by
  have hcoord :
      z.coord =
        fun t => projectiveScale z * (normalizeProjectivePair z).coord t := by
    funext t
    exact coord_eq_projectiveScale_mul_normalize z t
  rw [hcoord]
  simpa using
    (HValue_rescale_zero_iff
      (a := projectiveScale z) (b := (1 : K)) (c := (1 : K))
      (projectiveScale_ne_zero z) one_ne_zero one_ne_zero
      (normalizeProjectivePair z).coord q₂ q₃)

theorem HValue_normalize_first_third_zero_iff
    {K : Type*} [Field K]
    (z₁ : ProjectivePair K) (q₂ : Axis → K)
    (z₃ : ProjectivePair K) :
    HValue z₁.coord q₂ z₃.coord = 0 ↔
      HValue (normalizeProjectivePair z₁).coord q₂
        (normalizeProjectivePair z₃).coord = 0 := by
  have hcoord₁ :
      z₁.coord =
        fun t => projectiveScale z₁ *
          (normalizeProjectivePair z₁).coord t := by
    funext t
    exact coord_eq_projectiveScale_mul_normalize z₁ t
  have hcoord₃ :
      z₃.coord =
        fun t => projectiveScale z₃ *
          (normalizeProjectivePair z₃).coord t := by
    funext t
    exact coord_eq_projectiveScale_mul_normalize z₃ t
  rw [hcoord₁, hcoord₃]
  simpa using
    (HValue_rescale_zero_iff
      (a := projectiveScale z₁) (b := (1 : K))
      (c := projectiveScale z₃)
      (projectiveScale_ne_zero z₁) one_ne_zero
      (projectiveScale_ne_zero z₃)
      (normalizeProjectivePair z₁).coord q₂
      (normalizeProjectivePair z₃).coord)

/-- The mask associated to a full vector of projective representatives. -/
noncomputable def infinityMaskOf
    {K : Type*} [Field K] (z : Fin 14 → ProjectivePair K) :
    InfinityMask := by
  classical
  exact Finset.univ.filter fun i => (z i).v = 0

/-- Affine coordinates of those representatives not in the infinity mask. -/
noncomputable def chartCoordinates
    {K : Type*} [Field K] (z : Fin 14 → ProjectivePair K) :
    ChartVar (infinityMaskOf z) → K :=
  fun i => (z i).u / (z i).v

theorem chartPair_infinityMaskOf_eq_normalize
    {K : Type*} [Field K]
    (z : Fin 14 → ProjectivePair K) (i : Fin 14) :
    chartPair (infinityMaskOf z) (chartCoordinates z) i =
      normalizeProjectivePair (z i) := by
  by_cases hz : (z i).v = 0
  · simp [chartPair, infinityMaskOf, normalizeProjectivePair, hz]
  · simp [chartPair, infinityMaskOf, chartCoordinates,
      normalizeProjectivePair, hz]

/-! ## Equivalence with the recursive stage-14 chain -/

/-- Exact fixed-length witness-vector semantics for the stage-14 chain. -/
def FrozenChainVector
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (z : Fin 14 → ProjectivePair K) : Prop :=
  HValue (q 0).coord (q 1).coord (z 0).coord = 0 ∧
  (∀ i : Fin 13,
    HValue (z i.castSucc).coord (q (i + 2)).coord (z i.succ).coord = 0) ∧
  HValue (z ⟨13, by decide⟩).coord (q 15).coord y.coord = 0

theorem frozenProjectiveChain_iff_chainVector
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    FrozenProjectiveChain q 14 y ↔
      ∃ z : Fin 14 → ProjectivePair K, FrozenChainVector q y z := by
  constructor
  · intro h
    simp only [FrozenProjectiveChain] at h
    rcases h with ⟨z₁₃, h₁₃, hfinal⟩
    rcases h₁₃ with ⟨z₁₂, h₁₂, hstep₁₂⟩
    rcases h₁₂ with ⟨z₁₁, h₁₁, hstep₁₁⟩
    rcases h₁₁ with ⟨z₁₀, h₁₀, hstep₁₀⟩
    rcases h₁₀ with ⟨z₉, h₉, hstep₉⟩
    rcases h₉ with ⟨z₈, h₈, hstep₈⟩
    rcases h₈ with ⟨z₇, h₇, hstep₇⟩
    rcases h₇ with ⟨z₆, h₆, hstep₆⟩
    rcases h₆ with ⟨z₅, h₅, hstep₅⟩
    rcases h₅ with ⟨z₄, h₄, hstep₄⟩
    rcases h₄ with ⟨z₃, h₃, hstep₃⟩
    rcases h₃ with ⟨z₂, h₂, hstep₂⟩
    rcases h₂ with ⟨z₁, h₁, hstep₁⟩
    rcases h₁ with ⟨z₀, hbase, hstep₀⟩
    let z : Fin 14 → ProjectivePair K :=
      ![z₀, z₁, z₂, z₃, z₄, z₅, z₆, z₇, z₈, z₉, z₁₀, z₁₁, z₁₂, z₁₃]
    have hstep (i : Fin 13) :
        HValue (z i.castSucc).coord (q (i + 2)).coord
          (z i.succ).coord = 0 := by
      fin_cases i <;>
        simp [z, hstep₀, hstep₁, hstep₂, hstep₃, hstep₄, hstep₅,
          hstep₆, hstep₇, hstep₈, hstep₉, hstep₁₀, hstep₁₁, hstep₁₂]
    exact ⟨z, hbase, hstep, hfinal⟩
  · rintro ⟨z, hbase, hstep, hfinal⟩
    have hprefix :
        ∀ n : ℕ, (hn : n < 14) →
          FrozenProjectiveChain q n (z ⟨n, hn⟩) := by
      intro n
      induction n with
      | zero =>
          intro hn
          have hi : (⟨0, hn⟩ : Fin 14) = 0 := Fin.ext (by rfl)
          simpa only [FrozenProjectiveChain, hi] using hbase
      | succ n ih =>
          intro hn
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
    rw [FrozenProjectiveChain]
    exact ⟨z ⟨13, by decide⟩, hprefix 13 (by decide), hfinal⟩

theorem frozenChainVector_normalize
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (z : Fin 14 → ProjectivePair K)
    (hz : FrozenChainVector q y z) :
    FrozenChainVector q y (fun i => normalizeProjectivePair (z i)) := by
  rcases hz with ⟨hbase, hstep, hfinal⟩
  constructor
  · exact
      (HValue_normalize_third_zero_iff
        (q 0).coord (q 1).coord (z 0)).mp hbase
  constructor
  · intro i
    exact
      (HValue_normalize_first_third_zero_iff
        (z i.castSucc) (q (i + 2)).coord (z i.succ)).mp (hstep i)
  · exact
      (HValue_normalize_first_zero_iff
        (z ⟨13, by decide⟩) (q 15).coord y.coord).mp hfinal

theorem frozenChainVector_iff_chartSystem
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K) :
    FrozenChainVector q y (chartPair I x) ↔
      FrozenChartSystem q y I x := by
  constructor
  · rintro ⟨hbase, hstep, hfinal⟩ e
    cases e with
    | base => simpa [chartEquationValue] using hbase
    | step i => simpa [chartEquationValue] using hstep i
    | final => simpa [chartEquationValue] using hfinal
  · intro h
    exact ⟨by simpa [chartEquationValue] using h .base,
      fun i => by simpa [chartEquationValue] using h (.step i),
      by simpa [chartEquationValue] using h .final⟩

/-- The union of the affine/infinity charts is exactly the existing stage-14
projective witness chain. -/
theorem frozenProjectiveChain_iff_chartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    FrozenProjectiveChain q 14 y ↔ FrozenChartCover q y := by
  rw [frozenProjectiveChain_iff_chainVector]
  constructor
  · rintro ⟨z, hz⟩
    let I := infinityMaskOf z
    let x := chartCoordinates z
    refine ⟨I, x, ?_⟩
    rw [← frozenChainVector_iff_chartSystem]
    have hn := frozenChainVector_normalize q y z hz
    have hp :
        chartPair (infinityMaskOf z) (chartCoordinates z) =
          fun i => normalizeProjectivePair (z i) := by
      funext i
      exact chartPair_infinityMaskOf_eq_normalize z i
    simpa only [I, x, hp] using hn
  · rintro ⟨I, x, hx⟩
    exact ⟨chartPair I x,
      (frozenChainVector_iff_chartSystem q y I x).mpr hx⟩

/-! ## Literal polynomial systems on a fixed chart -/

/-- Embed a fixed projective coordinate as a constant polynomial. -/
noncomputable def chartConstantPolynomialPair
    {K : Type*} [Field K] (z : ProjectivePair K) :
    Axis → MvPolynomial (ChartVar I) K
  | a => MvPolynomial.C (z.coord a)

/-- The polynomial representative selected in slot `i`: `[1:0]` when
`i ∈ I`, and `[Xᵢ:1]` otherwise. -/
noncomputable def chartPolynomialPair
    {K : Type*} [Field K] (I : InfinityMask) (i : Fin 14) :
    Axis → MvPolynomial (ChartVar I) K
  | .u =>
      if hi : i ∈ I then 1 else MvPolynomial.X ⟨i, hi⟩
  | .v =>
      if _hi : i ∈ I then 0 else 1

/-- The fifteen literal multivariate polynomials for one fixed chart. -/
noncomputable def chartPolynomialEquation
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) :
    ChartEquation → MvPolynomial (ChartVar I) K
  | .base =>
      HValue (chartConstantPolynomialPair (I := I) (q 0))
        (chartConstantPolynomialPair (I := I) (q 1))
        (chartPolynomialPair I ⟨0, by decide⟩)
  | .step i =>
      HValue (chartPolynomialPair I i.castSucc)
        (chartConstantPolynomialPair (I := I) (q (i + 2)))
        (chartPolynomialPair I i.succ)
  | .final =>
      HValue (chartPolynomialPair I ⟨13, by decide⟩)
        (chartConstantPolynomialPair (I := I) (q 15))
        (chartConstantPolynomialPair (I := I) y)

/-- Evaluating a selected polynomial pair gives the selected scalar pair. -/
theorem eval_chartPolynomialPair
    {K : Type*} [Field K]
    (I : InfinityMask) (x : ChartVar I → K)
    (i : Fin 14) (a : Axis) :
    MvPolynomial.eval x (chartPolynomialPair I i a) =
      (chartPair I x i).coord a := by
  by_cases hi : i ∈ I <;>
    cases a <;>
    simp [chartPolynomialPair, chartPair, hi, ProjectivePair.coord,
      ProjectivePair.infinity, ProjectivePair.affine]

/-- Evaluating a constant polynomial pair gives the original coordinate. -/
theorem eval_chartConstantPolynomialPair
    {K : Type*} [Field K]
    (I : InfinityMask) (x : ChartVar I → K)
    (z : ProjectivePair K) (a : Axis) :
    MvPolynomial.eval x (chartConstantPolynomialPair (I := I) z a) =
      z.coord a := by
  simp [chartConstantPolynomialPair]

/-- Evaluation of every literal chart polynomial agrees with its direct
equation value. -/
theorem eval_chartPolynomialEquation
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (e : ChartEquation) :
    MvPolynomial.eval x (chartPolynomialEquation q y I e) =
      chartEquationValue q y I x e := by
  cases e with
  | base =>
      simp [chartPolynomialEquation, chartEquationValue, HValue,
        eval_chartPolynomialPair, eval_chartConstantPolynomialPair]
  | step i =>
      simp [chartPolynomialEquation, chartEquationValue, HValue,
        eval_chartPolynomialPair, eval_chartConstantPolynomialPair]
  | final =>
      simp [chartPolynomialEquation, chartEquationValue, HValue,
        eval_chartPolynomialPair, eval_chartConstantPolynomialPair]

/-- A polynomial assignment solves the fifteen equations of one fixed
chart. -/
def FrozenChartPolynomialSystem
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K) : Prop :=
  ∀ e : ChartEquation,
    MvPolynomial.eval x (chartPolynomialEquation q y I e) = 0

/-- The literal polynomial assignment semantics is exactly the direct chart
semantics. -/
theorem frozenChartPolynomialSystem_iff_chartSystem
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K) :
    FrozenChartPolynomialSystem q y I x ↔
      FrozenChartSystem q y I x := by
  simp only [FrozenChartPolynomialSystem, FrozenChartSystem,
    eval_chartPolynomialEquation]

/-- The finite union of all fixed-chart literal polynomial systems. -/
def FrozenChartPolynomialCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ (I : InfinityMask) (x : ChartVar I → K),
    FrozenChartPolynomialSystem q y I x

/-- The literal polynomial cover is exactly the direct finite chart cover. -/
theorem frozenChartPolynomialCover_iff_chartCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    FrozenChartPolynomialCover q y ↔ FrozenChartCover q y := by
  constructor
  · rintro ⟨I, x, hx⟩
    exact ⟨I, x,
      (frozenChartPolynomialSystem_iff_chartSystem q y I x).mp hx⟩
  · rintro ⟨I, x, hx⟩
    exact ⟨I, x,
      (frozenChartPolynomialSystem_iff_chartSystem q y I x).mpr hx⟩

/-! ## Named bridge theorems -/

/-- The literal chart-polynomial cover is exactly the stage-14 projective
witness chain. -/
theorem frozenProjectiveChain_iff_chartPolynomialCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    FrozenProjectiveChain q 14 y ↔
      FrozenChartPolynomialCover q y := by
  calc
    FrozenProjectiveChain q 14 y ↔ FrozenChartCover q y :=
      frozenProjectiveChain_iff_chartCover q y
    _ ↔ FrozenChartPolynomialCover q y :=
      (frozenChartPolynomialCover_iff_chartCover q y).symm

/-- The existing guarded polynomial system and the literal chart-polynomial
cover have exactly the same stage-14 semantics. -/
theorem frozenGuardedProjectiveSystem_iff_chartPolynomialCover
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    FrozenGuardedProjectiveSystem q y ↔
      FrozenChartPolynomialCover q y := by
  calc
    FrozenGuardedProjectiveSystem q y ↔ FrozenProjectiveChain q 14 y :=
      (frozenProjectiveChain_iff_guardedProjectiveSystem q y).symm
    _ ↔ FrozenChartPolynomialCover q y :=
      frozenProjectiveChain_iff_chartPolynomialCover q y

/-- Injective base change binds the source-field frozen `C₁₆` equation to the
literal chart-polynomial cover over an algebraically closed target field.

The target witnesses need not descend to the source field. -/
theorem frozenRecS17_iff_chartPolynomialCover_over
    {k K : Type*} [Field k] [Field K] [IsAlgClosed K]
    (φ : k →+* K) (hφ : Function.Injective φ)
    (q : ℕ → ProjectivePair k) (y : ProjectivePair k) :
    specialize q y (frozenC k 14) = 0 ↔
      FrozenChartPolynomialCover
        (fun i => mapProjectivePair φ hφ (q i))
        (mapProjectivePair φ hφ y) := by
  calc
    specialize q y (frozenC k 14) = 0 ↔
        FrozenGuardedProjectiveSystem
          (fun i => mapProjectivePair φ hφ (q i))
          (mapProjectivePair φ hφ y) :=
      frozenRecS17_iff_guardedProjectiveSystem_over φ hφ q y
    _ ↔ FrozenChartPolynomialCover
          (fun i => mapProjectivePair φ hφ (q i))
          (mapProjectivePair φ hφ y) :=
      frozenGuardedProjectiveSystem_iff_chartPolynomialCover _ _

/-! ## Cardinalities -/

/-- There are exactly fifteen polynomial equations on every fixed chart.
This is the only cardinality theorem in this module proved by
`native_decide`. -/
theorem card_chartEquation : Fintype.card ChartEquation = 15 := by
  native_decide

/-- A mask removes exactly one affine variable for each infinity slot.  This
proof does not use `native_decide`. -/
theorem card_chartVar (I : InfinityMask) :
    Fintype.card (ChartVar I) = 14 - I.card := by
  simp [ChartVar, Fintype.card_subtype_compl]

/-! ## Total-degree upper bounds -/

private theorem chartTotalDegree_neg_le
    {K σ : Type*} [CommRing K] (p : MvPolynomial σ K) :
    (-p).totalDegree ≤ p.totalDegree := by
  have h :=
    MvPolynomial.totalDegree_mul
      (MvPolynomial.C (-1 : K) : MvPolynomial σ K) p
  simp at h ⊢

private theorem chartTotalDegree_add_le_of_le
    {K σ : Type*} [CommRing K]
    {p r : MvPolynomial σ K} {d : ℕ}
    (hp : p.totalDegree ≤ d) (hr : r.totalDegree ≤ d) :
    (p + r).totalDegree ≤ d :=
  (MvPolynomial.totalDegree_add p r).trans (max_le hp hr)

private theorem chartTotalDegree_sub_le_of_le
    {K σ : Type*} [CommRing K]
    {p r : MvPolynomial σ K} {d : ℕ}
    (hp : p.totalDegree ≤ d) (hr : r.totalDegree ≤ d) :
    (p - r).totalDegree ≤ d := by
  rw [sub_eq_add_neg]
  exact chartTotalDegree_add_le_of_le hp
    ((chartTotalDegree_neg_le r).trans hr)

private theorem chartTotalDegree_mul_le_of_le
    {K σ : Type*} [CommRing K]
    {p r : MvPolynomial σ K} {d e : ℕ}
    (hp : p.totalDegree ≤ d) (hr : r.totalDegree ≤ e) :
    (p * r).totalDegree ≤ d + e :=
  (MvPolynomial.totalDegree_mul p r).trans (Nat.add_le_add hp hr)

private theorem chartTotalDegree_pow_le_of_le
    {K σ : Type*} [CommRing K]
    {p : MvPolynomial σ K} {d n : ℕ}
    (hp : p.totalDegree ≤ d) :
    (p ^ n).totalDegree ≤ n * d :=
  (MvPolynomial.totalDegree_pow p n).trans
    (Nat.mul_le_mul_left n hp)

private theorem chartTotalDegree_C_le
    {K σ : Type*} [CommRing K] (a : K) (d : ℕ) :
    (MvPolynomial.C a : MvPolynomial σ K).totalDegree ≤ d := by
  simp [MvPolynomial.totalDegree_C]

private theorem chartHValue_totalDegree_le
    {K σ : Type*} [CommRing K]
    (q₁ q₂ q₃ : Axis → MvPolynomial σ K)
    (d₁ d₂ d₃ : ℕ)
    (h₁ : ∀ a, (q₁ a).totalDegree ≤ d₁)
    (h₂ : ∀ a, (q₂ a).totalDegree ≤ d₂)
    (h₃ : ∀ a, (q₃ a).totalDegree ≤ d₃) :
    (HValue q₁ q₂ q₃).totalDegree ≤
      2 * d₁ + 2 * d₂ + 2 * d₃ := by
  have h₁u2 :
      (q₁ .u ^ 2).totalDegree ≤ 2 * d₁ :=
    chartTotalDegree_pow_le_of_le (h₁ .u)
  have h₁v2 :
      (q₁ .v ^ 2).totalDegree ≤ 2 * d₁ :=
    chartTotalDegree_pow_le_of_le (h₁ .v)
  have h₂u2 :
      (q₂ .u ^ 2).totalDegree ≤ 2 * d₂ :=
    chartTotalDegree_pow_le_of_le (h₂ .u)
  have h₂v2 :
      (q₂ .v ^ 2).totalDegree ≤ 2 * d₂ :=
    chartTotalDegree_pow_le_of_le (h₂ .v)
  have h₃u2 :
      (q₃ .u ^ 2).totalDegree ≤ 2 * d₃ :=
    chartTotalDegree_pow_le_of_le (h₃ .u)
  have h₃v2 :
      (q₃ .v ^ 2).totalDegree ≤ 2 * d₃ :=
    chartTotalDegree_pow_le_of_le (h₃ .v)
  have htwo :
      ((2 : MvPolynomial σ K)).totalDegree ≤ 0 := by
    simpa only [map_ofNat] using
      chartTotalDegree_C_le (K := K) (σ := σ) (2 : K) 0
  have htwentyeight :
      ((28 : MvPolynomial σ K)).totalDegree ≤ 0 := by
    simpa only [map_ofNat] using
      chartTotalDegree_C_le (K := K) (σ := σ) (28 : K) 0
  let D := 2 * d₁ + 2 * d₂ + 2 * d₃
  have ht₁ :
      (q₁ .u ^ 2 * q₂ .u ^ 2 * q₃ .v ^ 2).totalDegree ≤ D := by
    exact (chartTotalDegree_mul_le_of_le
      (chartTotalDegree_mul_le_of_le h₁u2 h₂u2) h₃v2).trans (by
        dsimp [D]
        omega)
  have ht₂ :
      (q₁ .u ^ 2 * q₂ .v ^ 2 * q₃ .u ^ 2).totalDegree ≤ D := by
    exact (chartTotalDegree_mul_le_of_le
      (chartTotalDegree_mul_le_of_le h₁u2 h₂v2) h₃u2).trans (by
        dsimp [D]
        omega)
  have ht₃ :
      (q₁ .v ^ 2 * q₂ .u ^ 2 * q₃ .u ^ 2).totalDegree ≤ D := by
    exact (chartTotalDegree_mul_le_of_le
      (chartTotalDegree_mul_le_of_le h₁v2 h₂u2) h₃u2).trans (by
        dsimp [D]
        omega)
  have ht₄ :
      (2 * q₁ .u ^ 2 * q₂ .u * q₂ .v *
        q₃ .u * q₃ .v).totalDegree ≤ D := by
    exact (chartTotalDegree_mul_le_of_le
      (chartTotalDegree_mul_le_of_le
        (chartTotalDegree_mul_le_of_le
          (chartTotalDegree_mul_le_of_le
            (chartTotalDegree_mul_le_of_le htwo h₁u2)
            (h₂ .u))
          (h₂ .v))
        (h₃ .u))
      (h₃ .v)).trans (by
        dsimp [D]
        omega)
  have ht₅ :
      (2 * q₁ .u * q₁ .v * q₂ .u ^ 2 *
        q₃ .u * q₃ .v).totalDegree ≤ D := by
    exact (chartTotalDegree_mul_le_of_le
      (chartTotalDegree_mul_le_of_le
        (chartTotalDegree_mul_le_of_le
          (chartTotalDegree_mul_le_of_le
            (chartTotalDegree_mul_le_of_le htwo (h₁ .u))
            (h₁ .v))
          h₂u2)
        (h₃ .u))
      (h₃ .v)).trans (by
        dsimp [D]
        omega)
  have ht₆ :
      (2 * q₁ .u * q₁ .v * q₂ .u * q₂ .v *
        q₃ .u ^ 2).totalDegree ≤ D := by
    exact (chartTotalDegree_mul_le_of_le
      (chartTotalDegree_mul_le_of_le
        (chartTotalDegree_mul_le_of_le
          (chartTotalDegree_mul_le_of_le
            (chartTotalDegree_mul_le_of_le htwo (h₁ .u))
            (h₁ .v))
          (h₂ .u))
        (h₂ .v))
      h₃u2).trans (by
        dsimp [D]
        omega)
  have ht₇ :
      (q₁ .u * q₁ .v * q₂ .v ^ 2 *
        q₃ .v ^ 2).totalDegree ≤ D := by
    exact (chartTotalDegree_mul_le_of_le
      (chartTotalDegree_mul_le_of_le
        (chartTotalDegree_mul_le_of_le (h₁ .u) (h₁ .v))
        h₂v2)
      h₃v2).trans (by
        dsimp [D]
        omega)
  have ht₈ :
      (q₁ .v ^ 2 * q₂ .u * q₂ .v *
        q₃ .v ^ 2).totalDegree ≤ D := by
    exact (chartTotalDegree_mul_le_of_le
      (chartTotalDegree_mul_le_of_le
        (chartTotalDegree_mul_le_of_le h₁v2 (h₂ .u))
        (h₂ .v))
      h₃v2).trans (by
        dsimp [D]
        omega)
  have ht₉ :
      (q₁ .v ^ 2 * q₂ .v ^ 2 * q₃ .u *
        q₃ .v).totalDegree ≤ D := by
    exact (chartTotalDegree_mul_le_of_le
      (chartTotalDegree_mul_le_of_le
        (chartTotalDegree_mul_le_of_le h₁v2 h₂v2)
        (h₃ .u))
      (h₃ .v)).trans (by
        dsimp [D]
        omega)
  have ht₇₈₉ :
      (28 * (
        q₁ .u * q₁ .v * q₂ .v ^ 2 * q₃ .v ^ 2 +
        q₁ .v ^ 2 * q₂ .u * q₂ .v * q₃ .v ^ 2 +
        q₁ .v ^ 2 * q₂ .v ^ 2 * q₃ .u * q₃ .v)).totalDegree ≤ D := by
    exact (chartTotalDegree_mul_le_of_le htwentyeight
      (chartTotalDegree_add_le_of_le
        (chartTotalDegree_add_le_of_le ht₇ ht₈) ht₉)).trans (by
          dsimp [D]
          omega)
  exact chartTotalDegree_sub_le_of_le
    (chartTotalDegree_sub_le_of_le
      (chartTotalDegree_sub_le_of_le
        (chartTotalDegree_sub_le_of_le
          (chartTotalDegree_add_le_of_le
            (chartTotalDegree_add_le_of_le ht₁ ht₂) ht₃)
          ht₄)
        ht₅)
      ht₆)
    ht₇₈₉

private theorem chartConstantPolynomialPair_totalDegree_le_zero
    {K : Type*} [Field K] (I : InfinityMask)
    (z : ProjectivePair K) (a : Axis) :
    (chartConstantPolynomialPair (I := I) z a).totalDegree ≤ 0 := by
  cases a <;>
    simp [chartConstantPolynomialPair, MvPolynomial.totalDegree_C]

private theorem chartPolynomialPair_totalDegree_le_one
    {K : Type*} [Field K] (I : InfinityMask)
    (i : Fin 14) (a : Axis) :
    (chartPolynomialPair (K := K) I i a).totalDegree ≤ 1 := by
  by_cases hi : i ∈ I <;>
    cases a <;>
    simp [chartPolynomialPair, hi, MvPolynomial.totalDegree_X]

/-- A base chart equation has total degree at most two. -/
theorem chartPolynomialEquation_base_totalDegree_le_two
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) :
    (chartPolynomialEquation q y I .base).totalDegree ≤ 2 := by
  refine (chartHValue_totalDegree_le
    (chartConstantPolynomialPair (I := I) (q 0))
    (chartConstantPolynomialPair (I := I) (q 1))
    (chartPolynomialPair I ⟨0, by decide⟩)
    0 0 1 ?_ ?_ ?_).trans ?_
  · exact fun a =>
      chartConstantPolynomialPair_totalDegree_le_zero I (q 0) a
  · exact fun a =>
      chartConstantPolynomialPair_totalDegree_le_zero I (q 1) a
  · exact fun a =>
      chartPolynomialPair_totalDegree_le_one I ⟨0, by decide⟩ a
  · simp

/-- Every internal step chart equation has total degree at most four. -/
theorem chartPolynomialEquation_step_totalDegree_le_four
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (i : Fin 13) :
    (chartPolynomialEquation q y I (.step i)).totalDegree ≤ 4 := by
  refine (chartHValue_totalDegree_le
    (chartPolynomialPair I i.castSucc)
    (chartConstantPolynomialPair (I := I) (q (i + 2)))
    (chartPolynomialPair I i.succ)
    1 0 1 ?_ ?_ ?_).trans ?_
  · exact fun a =>
      chartPolynomialPair_totalDegree_le_one I i.castSucc a
  · exact fun a =>
      chartConstantPolynomialPair_totalDegree_le_zero I (q (i + 2)) a
  · exact fun a =>
      chartPolynomialPair_totalDegree_le_one I i.succ a
  · simp

/-- A final chart equation has total degree at most two. -/
theorem chartPolynomialEquation_final_totalDegree_le_two
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) :
    (chartPolynomialEquation q y I .final).totalDegree ≤ 2 := by
  refine (chartHValue_totalDegree_le
    (chartPolynomialPair I ⟨13, by decide⟩)
    (chartConstantPolynomialPair (I := I) (q 15))
    (chartConstantPolynomialPair (I := I) y)
    1 0 0 ?_ ?_ ?_).trans ?_
  · exact fun a =>
      chartPolynomialPair_totalDegree_le_one I ⟨13, by decide⟩ a
  · exact fun a =>
      chartConstantPolynomialPair_totalDegree_le_zero I (q 15) a
  · exact fun a =>
      chartConstantPolynomialPair_totalDegree_le_zero I y a
  · simp

/-- Uniformly, every fixed-chart equation has total degree at most four.
This is only an upper bound: coefficient cancellation may lower it. -/
theorem chartPolynomialEquation_totalDegree_le_four
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (e : ChartEquation) :
    (chartPolynomialEquation q y I e).totalDegree ≤ 4 := by
  cases e with
  | base =>
      exact (chartPolynomialEquation_base_totalDegree_le_two q y I).trans
        (by omega)
  | step i =>
      exact chartPolynomialEquation_step_totalDegree_le_four q y I i
  | final =>
      exact (chartPolynomialEquation_final_totalDegree_le_two q y I).trans
        (by omega)

end Ecdlp.FrozenProjectiveSemaev
