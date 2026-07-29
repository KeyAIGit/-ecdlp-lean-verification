import Ecdlp.Proved.FrozenRecursiveProjectiveWitness
import Mathlib.Tactic.DeriveFintype

/-!
# A finite guarded system for the frozen projective witness chain

This file materializes the stage-14 witness chain as fifteen literal `H`
equations together with fourteen normalization guards

`Aᵢ Uᵢ + Bᵢ Vᵢ - 1 = 0`.

There are fourteen slots, four scalar variables per slot, and hence 56
variables.  The equation index has fifteen `H` equations and fourteen guards,
for a total of 29.  The guards exclude `[0:0]` but retain the infinity
representative `[1:0]`.

The coefficient-map theorem below uses an injective map from the source field
to an algebraically closed target field.  Its target witnesses live in the
target field; no descent of those witnesses is asserted.

This is only a finite polynomial encoding of the already proved recursive
semantics.  It is not a solver, a recovery theorem, or a cost claim.
-/

namespace Ecdlp.FrozenProjectiveSemaev

/-! ## The finite variable and equation indices -/

/-- The four scalar coordinates attached to one guarded projective slot. -/
inductive GuardCoordinate
  | u
  | v
  | a
  | b
  deriving DecidableEq, Fintype

/-- Four scalar variables in each of the fourteen intermediate slots. -/
inductive GuardVar
  | slot (i : Fin 14) (c : GuardCoordinate)
  deriving DecidableEq, Fintype

/-- The literal equation inventory: one base equation, thirteen internal
steps, one final equation, and fourteen guards. -/
inductive GuardedEquation
  | base
  | step (i : Fin 13)
  | final
  | guard (i : Fin 14)
  deriving DecidableEq, Fintype

/-- The stage-14 guarded system has exactly 56 scalar variables. -/
theorem card_guardVar_fourteen : Fintype.card GuardVar = 56 := by
  native_decide

/-- The stage-14 guarded system has exactly 29 equations. -/
theorem card_guarded_equations_fourteen :
    Fintype.card GuardedEquation = 29 := by
  native_decide

/-! ## Literal multivariate polynomials -/

/-- The `U` or `V` polynomial of an intermediate projective slot. -/
noncomputable def guardProjectiveCoordinate
    {K : Type*} [CommRing K] (i : Fin 14) :
    Axis → MvPolynomial GuardVar K
  | .u => MvPolynomial.X (.slot i .u)
  | .v => MvPolynomial.X (.slot i .v)

/-- Embed the coordinates of a fixed projective pair as constants. -/
noncomputable def guardConstantCoordinate
    {K : Type*} [CommRing K] (q : ProjectivePair K) :
    Axis → MvPolynomial GuardVar K
  | a => MvPolynomial.C (q.coord a)

/-- The normalization guard `AᵢUᵢ + BᵢVᵢ - 1`. -/
noncomputable def guardEquation
    {K : Type*} [CommRing K] (i : Fin 14) :
    MvPolynomial GuardVar K :=
  MvPolynomial.X (.slot i .a) * MvPolynomial.X (.slot i .u) +
    MvPolynomial.X (.slot i .b) * MvPolynomial.X (.slot i .v) - 1

/-- The fifteen literal `H` equations and fourteen normalization guards. -/
noncomputable def guardedEquation
    {K : Type*} [CommRing K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    GuardedEquation → MvPolynomial GuardVar K
  | .base =>
      HValue (guardConstantCoordinate (q 0))
        (guardConstantCoordinate (q 1))
        (guardProjectiveCoordinate ⟨0, by decide⟩)
  | .step i =>
      HValue (guardProjectiveCoordinate i.castSucc)
        (guardConstantCoordinate (q (i + 2)))
        (guardProjectiveCoordinate i.succ)
  | .final =>
      HValue (guardProjectiveCoordinate ⟨13, by decide⟩)
        (guardConstantCoordinate (q 15))
        (guardConstantCoordinate y)
  | .guard i => guardEquation i

private theorem totalDegree_neg_le
    {K σ : Type*} [CommRing K] (p : MvPolynomial σ K) :
    (-p).totalDegree ≤ p.totalDegree := by
  have h :=
    MvPolynomial.totalDegree_mul
      (MvPolynomial.C (-1 : K) : MvPolynomial σ K) p
  simp at h ⊢

private theorem totalDegree_add_le_of_le
    {K σ : Type*} [CommRing K] {p r : MvPolynomial σ K} {d : ℕ}
    (hp : p.totalDegree ≤ d) (hr : r.totalDegree ≤ d) :
    (p + r).totalDegree ≤ d :=
  (MvPolynomial.totalDegree_add p r).trans (max_le hp hr)

private theorem totalDegree_sub_le_of_le
    {K σ : Type*} [CommRing K] {p r : MvPolynomial σ K} {d : ℕ}
    (hp : p.totalDegree ≤ d) (hr : r.totalDegree ≤ d) :
    (p - r).totalDegree ≤ d := by
  rw [sub_eq_add_neg]
  exact totalDegree_add_le_of_le hp ((totalDegree_neg_le r).trans hr)

private theorem totalDegree_mul_le_of_le
    {K σ : Type*} [CommRing K] {p r : MvPolynomial σ K} {d e : ℕ}
    (hp : p.totalDegree ≤ d) (hr : r.totalDegree ≤ e) :
    (p * r).totalDegree ≤ d + e :=
  (MvPolynomial.totalDegree_mul p r).trans (Nat.add_le_add hp hr)

private theorem totalDegree_pow_le_of_le
    {K σ : Type*} [CommRing K] {p : MvPolynomial σ K} {d n : ℕ}
    (hp : p.totalDegree ≤ d) :
    (p ^ n).totalDegree ≤ n * d :=
  (MvPolynomial.totalDegree_pow p n).trans (Nat.mul_le_mul_left n hp)

private theorem totalDegree_C_le
    {K σ : Type*} [CommRing K] (a : K) (d : ℕ) :
    (MvPolynomial.C a : MvPolynomial σ K).totalDegree ≤ d := by
  simp [MvPolynomial.totalDegree_C]

private theorem totalDegree_X_le_one
    {K σ : Type*} [CommRing K] [Nontrivial K] (i : σ) :
    (MvPolynomial.X i : MvPolynomial σ K).totalDegree ≤ 1 := by
  simp [MvPolynomial.totalDegree_X]

private theorem HValue_totalDegree_le
    {K σ : Type*} [CommRing K]
    (q₁ q₂ q₃ : Axis → MvPolynomial σ K) (d₁ d₂ d₃ : ℕ)
    (h₁ : ∀ a, (q₁ a).totalDegree ≤ d₁)
    (h₂ : ∀ a, (q₂ a).totalDegree ≤ d₂)
    (h₃ : ∀ a, (q₃ a).totalDegree ≤ d₃) :
    (HValue q₁ q₂ q₃).totalDegree ≤ 2 * d₁ + 2 * d₂ + 2 * d₃ := by
  have h₁u2 :
      (q₁ .u ^ 2).totalDegree ≤ 2 * d₁ :=
    totalDegree_pow_le_of_le (h₁ .u)
  have h₁v2 :
      (q₁ .v ^ 2).totalDegree ≤ 2 * d₁ :=
    totalDegree_pow_le_of_le (h₁ .v)
  have h₂u2 :
      (q₂ .u ^ 2).totalDegree ≤ 2 * d₂ :=
    totalDegree_pow_le_of_le (h₂ .u)
  have h₂v2 :
      (q₂ .v ^ 2).totalDegree ≤ 2 * d₂ :=
    totalDegree_pow_le_of_le (h₂ .v)
  have h₃u2 :
      (q₃ .u ^ 2).totalDegree ≤ 2 * d₃ :=
    totalDegree_pow_le_of_le (h₃ .u)
  have h₃v2 :
      (q₃ .v ^ 2).totalDegree ≤ 2 * d₃ :=
    totalDegree_pow_le_of_le (h₃ .v)
  have htwo :
      ((2 : MvPolynomial σ K)).totalDegree ≤ 0 := by
    simpa only [map_ofNat] using
      totalDegree_C_le (K := K) (σ := σ) (2 : K) 0
  have htwentyeight :
      ((28 : MvPolynomial σ K)).totalDegree ≤ 0 := by
    simpa only [map_ofNat] using
      totalDegree_C_le (K := K) (σ := σ) (28 : K) 0
  let D := 2 * d₁ + 2 * d₂ + 2 * d₃
  have ht₁ :
      (q₁ .u ^ 2 * q₂ .u ^ 2 * q₃ .v ^ 2).totalDegree ≤ D := by
    exact (totalDegree_mul_le_of_le
      (totalDegree_mul_le_of_le h₁u2 h₂u2) h₃v2).trans (by
        dsimp [D]
        omega)
  have ht₂ :
      (q₁ .u ^ 2 * q₂ .v ^ 2 * q₃ .u ^ 2).totalDegree ≤ D := by
    exact (totalDegree_mul_le_of_le
      (totalDegree_mul_le_of_le h₁u2 h₂v2) h₃u2).trans (by
        dsimp [D]
        omega)
  have ht₃ :
      (q₁ .v ^ 2 * q₂ .u ^ 2 * q₃ .u ^ 2).totalDegree ≤ D := by
    exact (totalDegree_mul_le_of_le
      (totalDegree_mul_le_of_le h₁v2 h₂u2) h₃u2).trans (by
        dsimp [D]
        omega)
  have ht₄ :
      (2 * q₁ .u ^ 2 * q₂ .u * q₂ .v * q₃ .u * q₃ .v).totalDegree ≤ D := by
    exact (totalDegree_mul_le_of_le
      (totalDegree_mul_le_of_le
        (totalDegree_mul_le_of_le
          (totalDegree_mul_le_of_le
            (totalDegree_mul_le_of_le htwo h₁u2) (h₂ .u))
          (h₂ .v))
        (h₃ .u))
      (h₃ .v)).trans (by
        dsimp [D]
        omega)
  have ht₅' :
      (2 * q₁ .u * q₁ .v * q₂ .u ^ 2 * q₃ .u * q₃ .v).totalDegree ≤ D := by
    exact (totalDegree_mul_le_of_le
      (totalDegree_mul_le_of_le
        (totalDegree_mul_le_of_le
          (totalDegree_mul_le_of_le
            (totalDegree_mul_le_of_le htwo (h₁ .u)) (h₁ .v))
          h₂u2)
        (h₃ .u))
      (h₃ .v)).trans (by
        dsimp [D]
        omega)
  have ht₆ :
      (2 * q₁ .u * q₁ .v * q₂ .u * q₂ .v * q₃ .u ^ 2).totalDegree ≤ D := by
    exact (totalDegree_mul_le_of_le
      (totalDegree_mul_le_of_le
        (totalDegree_mul_le_of_le
          (totalDegree_mul_le_of_le
            (totalDegree_mul_le_of_le htwo (h₁ .u)) (h₁ .v))
          (h₂ .u))
        (h₂ .v))
      h₃u2).trans (by
        dsimp [D]
        omega)
  have ht₇ :
      (q₁ .u * q₁ .v * q₂ .v ^ 2 * q₃ .v ^ 2).totalDegree ≤ D := by
    exact (totalDegree_mul_le_of_le
      (totalDegree_mul_le_of_le
        (totalDegree_mul_le_of_le (h₁ .u) (h₁ .v)) h₂v2)
      h₃v2).trans (by
        dsimp [D]
        omega)
  have ht₈ :
      (q₁ .v ^ 2 * q₂ .u * q₂ .v * q₃ .v ^ 2).totalDegree ≤ D := by
    exact (totalDegree_mul_le_of_le
      (totalDegree_mul_le_of_le
        (totalDegree_mul_le_of_le h₁v2 (h₂ .u)) (h₂ .v))
      h₃v2).trans (by
        dsimp [D]
        omega)
  have ht₉ :
      (q₁ .v ^ 2 * q₂ .v ^ 2 * q₃ .u * q₃ .v).totalDegree ≤ D := by
    exact (totalDegree_mul_le_of_le
      (totalDegree_mul_le_of_le
        (totalDegree_mul_le_of_le h₁v2 h₂v2) (h₃ .u))
      (h₃ .v)).trans (by
        dsimp [D]
        omega)
  have ht₇₈₉ :
      (28 * (
        q₁ .u * q₁ .v * q₂ .v ^ 2 * q₃ .v ^ 2 +
        q₁ .v ^ 2 * q₂ .u * q₂ .v * q₃ .v ^ 2 +
        q₁ .v ^ 2 * q₂ .v ^ 2 * q₃ .u * q₃ .v)).totalDegree ≤ D := by
    exact (totalDegree_mul_le_of_le htwentyeight
      (totalDegree_add_le_of_le
        (totalDegree_add_le_of_le ht₇ ht₈) ht₉)).trans (by
          dsimp [D]
          omega)
  exact totalDegree_sub_le_of_le
    (totalDegree_sub_le_of_le
      (totalDegree_sub_le_of_le
        (totalDegree_sub_le_of_le
          (totalDegree_add_le_of_le
            (totalDegree_add_le_of_le ht₁ ht₂) ht₃)
          ht₄)
        ht₅')
      ht₆)
    ht₇₈₉

/-- Every literal equation in the guarded system has total degree at most
four.  This is an upper bound: coefficient cancellation in a particular
characteristic may lower the actual degree. -/
theorem guardedEquation_totalDegree_le_four
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (e : GuardedEquation) :
    (guardedEquation q y e).totalDegree ≤ 4 := by
  cases e with
  | base =>
      refine (HValue_totalDegree_le
        (guardConstantCoordinate (q 0))
        (guardConstantCoordinate (q 1))
        (guardProjectiveCoordinate ⟨0, by decide⟩)
        0 0 1 ?_ ?_ ?_).trans ?_
      · intro a
        cases a <;> simp [guardConstantCoordinate, MvPolynomial.totalDegree_C]
      · intro a
        cases a <;> simp [guardConstantCoordinate, MvPolynomial.totalDegree_C]
      · intro a
        cases a <;> simp [guardProjectiveCoordinate, MvPolynomial.totalDegree_X]
      · omega
  | step i =>
      refine (HValue_totalDegree_le
        (guardProjectiveCoordinate i.castSucc)
        (guardConstantCoordinate (q (i + 2)))
        (guardProjectiveCoordinate i.succ)
        1 0 1 ?_ ?_ ?_).trans ?_
      · intro a
        cases a <;> simp [guardProjectiveCoordinate, MvPolynomial.totalDegree_X]
      · intro a
        cases a <;> simp [guardConstantCoordinate, MvPolynomial.totalDegree_C]
      · intro a
        cases a <;> simp [guardProjectiveCoordinate, MvPolynomial.totalDegree_X]
      · omega
  | final =>
      refine (HValue_totalDegree_le
        (guardProjectiveCoordinate ⟨13, by decide⟩)
        (guardConstantCoordinate (q 15))
        (guardConstantCoordinate y)
        1 0 0 ?_ ?_ ?_).trans ?_
      · intro a
        cases a <;> simp [guardProjectiveCoordinate, MvPolynomial.totalDegree_X]
      · intro a
        cases a <;> simp [guardConstantCoordinate, MvPolynomial.totalDegree_C]
      · intro a
        cases a <;> simp [guardConstantCoordinate, MvPolynomial.totalDegree_C]
      · omega
  | guard i =>
      simp only [guardedEquation, guardEquation]
      apply totalDegree_sub_le_of_le
      · apply totalDegree_add_le_of_le
        · exact (totalDegree_mul_le_of_le
            (totalDegree_X_le_one _) (totalDegree_X_le_one _)).trans (by omega)
        · exact (totalDegree_mul_le_of_le
            (totalDegree_X_le_one _) (totalDegree_X_le_one _)).trans (by omega)
      · simp

/-! ## Guarded recursive semantics -/

/-- Every valid projective representative admits a guard over a field. -/
private theorem exists_guard_coefficients
    {K : Type*} [Field K] (z : ProjectivePair K) :
    ∃ a b : K, a * z.u + b * z.v - 1 = 0 := by
  rcases z.valid with hu | hv
  · refine ⟨z.u⁻¹, 0, ?_⟩
    simp [hu]
  · refine ⟨0, z.v⁻¹, ?_⟩
    simp [hv]

/-- A guard excludes the irrelevant pair `[0:0]`. -/
theorem guardEquation_excludes_zero
    {K : Type*} [Field K] {u v a b : K}
    (h : a * u + b * v - 1 = 0) :
    u ≠ 0 ∨ v ≠ 0 := by
  by_contra hzero
  push Not at hzero
  rcases hzero with ⟨hu, hv⟩
  subst u
  subst v
  simp at h

/-- The infinity representative `[1:0]` satisfies a guard. -/
theorem guardEquation_preserves_infinity
    {K : Type*} [Field K] :
    (1 : K) * 1 + 0 * 0 - 1 = 0 := by
  ring

private noncomputable def selectedGuardA
    {K : Type*} [Field K] (z : ProjectivePair K) : K :=
  Classical.choose (exists_guard_coefficients z)

private noncomputable def selectedGuardB
    {K : Type*} [Field K] (z : ProjectivePair K) : K :=
  Classical.choose (Classical.choose_spec (exists_guard_coefficients z))

private theorem selectedGuard_spec
    {K : Type*} [Field K] (z : ProjectivePair K) :
    selectedGuardA z * z.u + selectedGuardB z * z.v - 1 = 0 :=
  Classical.choose_spec (Classical.choose_spec (exists_guard_coefficients z))

/-- The fixed stage-14 literal polynomial system: an assignment to the 56
scalar variables on which every one of the 29 indexed polynomials vanishes. -/
def FrozenGuardedProjectiveSystem
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Prop :=
  ∃ x : GuardVar → K,
    ∀ e : GuardedEquation,
      MvPolynomial.eval x (guardedEquation q y e) = 0

/-- The finite guarded system is exactly the stage-14 recursive projective
witness chain. -/
theorem frozenProjectiveChain_iff_guardedProjectiveSystem
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    FrozenProjectiveChain q 14 y ↔
      FrozenGuardedProjectiveSystem q y := by
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
    let x : GuardVar → K
      | .slot i .u => (z i).u
      | .slot i .v => (z i).v
      | .slot i .a => selectedGuardA (z i)
      | .slot i .b => selectedGuardB (z i)
    have hstep (i : Fin 13) :
        HValue (z i.castSucc).coord (q (i + 2)).coord
          (z i.succ).coord = 0 := by
      fin_cases i <;>
        simp [z, hstep₀, hstep₁, hstep₂, hstep₃, hstep₄, hstep₅,
          hstep₆, hstep₇, hstep₈, hstep₉, hstep₁₀, hstep₁₁, hstep₁₂]
    refine ⟨x, ?_⟩
    intro e
    cases e with
    | base =>
        simpa [guardedEquation, guardConstantCoordinate,
          guardProjectiveCoordinate, HValue, ProjectivePair.coord, x, z] using hbase
    | step i =>
        simpa [guardedEquation, guardConstantCoordinate,
          guardProjectiveCoordinate, HValue, ProjectivePair.coord, x] using hstep i
    | final =>
        simpa [guardedEquation, guardConstantCoordinate,
          guardProjectiveCoordinate, HValue, ProjectivePair.coord, x, z] using hfinal
    | guard i =>
        simpa [guardedEquation, guardEquation, x] using selectedGuard_spec (z i)
  · rintro ⟨x, hx⟩
    have hguard (i : Fin 14) :
        x (.slot i .a) * x (.slot i .u) +
          x (.slot i .b) * x (.slot i .v) - 1 = 0 := by
      simpa [guardedEquation, guardEquation] using hx (.guard i)
    let z : Fin 14 → ProjectivePair K := fun i =>
      { u := x (.slot i .u)
        v := x (.slot i .v)
        valid := guardEquation_excludes_zero (hguard i) }
    have hbase :
        HValue (q 0).coord (q 1).coord (z 0).coord = 0 := by
      simpa [guardedEquation, guardConstantCoordinate,
        guardProjectiveCoordinate, HValue, ProjectivePair.coord, z] using hx .base
    have hstep (i : Fin 13) :
        HValue (z i.castSucc).coord (q (i + 2)).coord
          (z i.succ).coord = 0 := by
      simpa [guardedEquation, guardConstantCoordinate,
        guardProjectiveCoordinate, HValue, ProjectivePair.coord, z] using hx (.step i)
    have hfinal :
        HValue (z ⟨13, by decide⟩).coord (q 15).coord y.coord = 0 := by
      simpa [guardedEquation, guardConstantCoordinate,
        guardProjectiveCoordinate, HValue, ProjectivePair.coord, z] using hx .final
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

/-! ## Injective coefficient-map binding -/

/-- Map a valid projective representative along an injective field map. -/
def mapProjectivePair
    {k K : Type*} [Field k] [Field K]
    (φ : k →+* K) (hφ : Function.Injective φ)
    (z : ProjectivePair k) : ProjectivePair K where
  u := φ z.u
  v := φ z.v
  valid := by
    rcases z.valid with hu | hv
    · left
      intro h
      apply hu
      apply hφ
      simpa using h
    · right
      intro h
      apply hv
      apply hφ
      simpa using h

@[simp] theorem mapProjectivePair_coord
    {k K : Type*} [Field k] [Field K]
    (φ : k →+* K) (hφ : Function.Injective φ)
    (z : ProjectivePair k) (a : Axis) :
    (mapProjectivePair φ hφ z).coord a = φ (z.coord a) := by
  cases a <;> rfl

private theorem map_specialize_eq_specializeOver
    {k K : Type*} [Field k] [Field K]
    (φ : k →+* K) (hφ : Function.Injective φ)
    (p : MvPolynomial Var k)
    (q : ℕ → ProjectivePair k) (y : ProjectivePair k) :
    φ (specialize q y p) =
      specializeOver φ
        (fun i => mapProjectivePair φ hφ (q i))
        (mapProjectivePair φ hφ y) p := by
  change
    (φ.comp (specialize q y)) p =
      (specializeOver φ
        (fun i => mapProjectivePair φ hφ (q i))
        (mapProjectivePair φ hφ y)) p
  apply MvPolynomial.hom_eq_hom
  · ext a
    simp [specialize, specializeOver]
  · intro i
    cases i with
    | leaf i a =>
        cases a <;>
          simp [specialize, specializeOver, assignment,
            mapProjectivePair, ProjectivePair.coord]
    | output a =>
        cases a <;>
          simp [specialize, specializeOver, assignment,
            mapProjectivePair, ProjectivePair.coord]

/-- Injective base change binds the source-field frozen `C₁₆` equation to the
finite guarded system over an algebraically closed target field.

The target witnesses need not descend to the source field. -/
theorem frozenRecS17_iff_guardedProjectiveSystem_over
    {k K : Type*} [Field k] [Field K] [IsAlgClosed K]
    (φ : k →+* K) (hφ : Function.Injective φ)
    (q : ℕ → ProjectivePair k) (y : ProjectivePair k) :
    specialize q y (frozenC k 14) = 0 ↔
      FrozenGuardedProjectiveSystem
        (fun i => mapProjectivePair φ hφ (q i))
        (mapProjectivePair φ hφ y) := by
  let qK : ℕ → ProjectivePair K :=
    fun i => mapProjectivePair φ hφ (q i)
  let yK : ProjectivePair K := mapProjectivePair φ hφ y
  calc
    specialize q y (frozenC k 14) = 0 ↔
        φ (specialize q y (frozenC k 14)) = 0 := by
      constructor
      · intro h
        simp [h]
      · intro h
        apply hφ
        simpa using h
    _ ↔ specializeOver φ qK yK (frozenC k 14) = 0 := by
      rw [map_specialize_eq_specializeOver
        (φ := φ) (hφ := hφ) (p := frozenC k 14) (q := q) (y := y)]
    _ ↔ FrozenProjectiveChain qK 14 yK :=
      specializeOver_frozenC16_eq_zero_iff_projectiveChain φ qK yK
    _ ↔ FrozenGuardedProjectiveSystem qK yK :=
      frozenProjectiveChain_iff_guardedProjectiveSystem qK yK

end Ecdlp.FrozenProjectiveSemaev
