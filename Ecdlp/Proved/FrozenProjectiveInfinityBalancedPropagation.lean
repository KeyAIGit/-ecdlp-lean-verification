import Ecdlp.Proved.FrozenProjectiveInfinityStrata

/-!
# Distance propagation between isolated infinity slots

`FrozenProjectiveInfinityStrata` shows that two *adjacent* intermediate slots
cannot both use the infinity chart when every external input is affine, and
records the two endpoint determinant conditions.  This file continues that
analysis one and two steps further out, and derives the resulting exact mask
counts instead of asserting them.

The mechanism is the pair of forced-neighbour coordinate theorems already
proved in `FrozenProjectiveInfinityStrata`.  An infinity slot forces its affine
neighbour to be the projective normalization of the adjacent external input.
Two infinity slots at distance `d` therefore pin `d - 1` interior slots and
leave a relation purely among external inputs:

* `d = 1` is impossible — this is `frozenChartSystem_separatedInfinityMask`;
* `d = 2` forces `projectiveDet (q (a+2)) (q (a+3)) = 0`;
* `d = 3` forces `HValue (q (a+2)) (q (a+3)) (q (a+4)) = 0`.

Consequently, if all fifteen consecutive input determinants are nonzero, then
the admissible interior masks are exactly the subsets of the twelve interior
slots with pairwise gap at least three, of which there are `129`.  Adding the
`d = 3` triple conditions leaves the gap-at-least-four family, of which there
are `69`.  Both cardinalities are `native_decide` facts here; every structural
statement is an ordinary kernel-checked proof.

## Scope

Every theorem below is a *necessary* condition on the infinity mask.  Nothing
here is a sufficiency, solver, rank, yield, recovery, runtime, memory, arity,
degree or ECDLP-complexity claim.  A single affine chart does not mean a single
solution, a unique witness, or any reduction of the `2 ^ 128` generic bound.
The word "generic" is deliberately not used: the nonzero hypotheses below are
carried explicitly as hypotheses and no symbolic nonvanishing of any obstruction
polynomial is proved here.

The general gap-`d` shifted block obstruction for `d ≥ 4` and the balanced
prefix/suffix single-chart guard are **not** closed here; the exact remaining
blockers are recorded in `§ Recorded blockers` at the end of this file.
-/

namespace Ecdlp.FrozenProjectiveSemaev

/-! ## Index normalization helpers -/

private theorem castSucc_mk_eq {a : ℕ} (h : a < 13) :
    (⟨a, h⟩ : Fin 13).castSucc = (⟨a, by omega⟩ : Fin 14) := by
  ext
  simp

private theorem succ_mk_eq {a : ℕ} (h : a < 13) :
    (⟨a, h⟩ : Fin 13).succ = (⟨a + 1, by omega⟩ : Fin 14) := by
  ext
  simp

/-! ## Forced neighbours as projective normalizations -/

/-- An infinity slot on the left forces its affine right neighbour to be the
projective normalization of the adjacent external input. -/
theorem chartPair_succ_eq_normalize_of_leftInfinity
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (i : Fin 13)
    (hleft : i.castSucc ∈ I) (hright : i.succ ∉ I)
    (hq : (q (i + 2)).v ≠ 0)
    (hx : FrozenChartSystem q y I x) :
    chartPair I x i.succ = normalizeProjectivePair (q (i + 2)) := by
  have hcoord :=
    frozenChartSystem_leftInfinity_forces_rightCoordinate
      q y I x i hleft hright hq hx
  simp [chartPair, hright, normalizeProjectivePair, hq, hcoord]

/-- An infinity slot on the right forces its affine left neighbour to be the
projective normalization of the adjacent external input. -/
theorem chartPair_castSucc_eq_normalize_of_rightInfinity
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (i : Fin 13)
    (hleft : i.castSucc ∉ I) (hright : i.succ ∈ I)
    (hq : (q (i + 2)).v ≠ 0)
    (hx : FrozenChartSystem q y I x) :
    chartPair I x i.castSucc = normalizeProjectivePair (q (i + 2)) := by
  have hcoord :=
    frozenChartSystem_rightInfinity_forces_leftCoordinate
      q y I x i hleft hright hq hx
  simp [chartPair, hleft, normalizeProjectivePair, hq, hcoord]

/-- Two representatives with equal affine normalization have vanishing
determinant. -/
theorem projectiveDet_eq_zero_of_normalize_eq
    {K : Type*} [Field K]
    (r s : ProjectivePair K) (hr : r.v ≠ 0) (hs : s.v ≠ 0)
    (h : r.u / r.v = s.u / s.v) :
    projectiveDet r s = 0 := by
  have hmul : r.u * s.v = s.u * r.v := (div_eq_div_iff hr hs).mp h
  unfold projectiveDet
  linear_combination hmul

/-! ## Distance-two propagation -/

/-- Two infinity slots at distance two force the determinant of the two
external inputs between them to vanish. -/
theorem frozenChartSystem_distance_two_forces_input_det
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x)
    (a : ℕ) (ha : a + 2 < 14)
    (h0 : (⟨a, by omega⟩ : Fin 14) ∈ I)
    (h2 : (⟨a + 2, by omega⟩ : Fin 14) ∈ I) :
    projectiveDet (q (a + 2)) (q (a + 3)) = 0 := by
  have hsep := frozenChartSystem_separatedInfinityMask q y I x hq hx
  -- the middle slot is affine
  have h1 : (⟨a + 1, by omega⟩ : Fin 14) ∉ I := by
    intro hmem
    refine hsep ⟨a, by omega⟩ ⟨?_, ?_⟩
    · rw [castSucc_mk_eq]; exact h0
    · rw [succ_mk_eq]; exact hmem
  -- the left infinity slot pins the middle slot to `q (a+2)`
  have hleft :
      chartPair I x (⟨a + 1, by omega⟩ : Fin 14) =
        normalizeProjectivePair (q (a + 2)) := by
    have hstep :=
      chartPair_succ_eq_normalize_of_leftInfinity q y I x ⟨a, by omega⟩
        (by rw [castSucc_mk_eq]; exact h0)
        (by rw [succ_mk_eq]; exact h1)
        (by simpa using hq (a + 2)) hx
    rw [succ_mk_eq] at hstep
    simpa using hstep
  -- the right infinity slot pins the same slot to `q (a+3)`
  have hright :
      chartPair I x (⟨a + 1, by omega⟩ : Fin 14) =
        normalizeProjectivePair (q (a + 3)) := by
    have hstep :=
      chartPair_castSucc_eq_normalize_of_rightInfinity q y I x
        ⟨a + 1, by omega⟩
        (by rw [castSucc_mk_eq]; exact h1)
        (by rw [succ_mk_eq]; exact h2)
        (by simpa using hq (a + 3)) hx
    rw [castSucc_mk_eq] at hstep
    simpa using hstep
  -- comparing the two normalizations
  have hnorm :
      normalizeProjectivePair (q (a + 2)) =
        normalizeProjectivePair (q (a + 3)) := by
    rw [← hleft, hright]
  have h2ne := hq (a + 2)
  have h3ne := hq (a + 3)
  have hval :
      (q (a + 2)).u / (q (a + 2)).v = (q (a + 3)).u / (q (a + 3)).v := by
    have := congrArg ProjectivePair.u hnorm
    simpa [normalizeProjectivePair, h2ne, h3ne, ProjectivePair.affine] using this
  exact projectiveDet_eq_zero_of_normalize_eq _ _ h2ne h3ne hval

/-! ## Distance-three propagation -/

/-- **Priority A.** Two infinity slots at distance three force the
triquadratic on the three external inputs between them to vanish.

The proof uses only the two forced-neighbour coordinate theorems and
projective normalization of `HValue`; it restates no semantics and calls no
solver. -/
theorem frozenChartSystem_distance_three_forces_input_HValue
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x)
    (a : ℕ) (ha : a + 3 < 14)
    (h0 : (⟨a, by omega⟩ : Fin 14) ∈ I)
    (h3 : (⟨a + 3, by omega⟩ : Fin 14) ∈ I) :
    HValue (q (a + 2)).coord (q (a + 3)).coord (q (a + 4)).coord = 0 := by
  have hsep := frozenChartSystem_separatedInfinityMask q y I x hq hx
  have h1 : (⟨a + 1, by omega⟩ : Fin 14) ∉ I := by
    intro hmem
    refine hsep ⟨a, by omega⟩ ⟨?_, ?_⟩
    · rw [castSucc_mk_eq]; exact h0
    · rw [succ_mk_eq]; exact hmem
  have h2 : (⟨a + 2, by omega⟩ : Fin 14) ∉ I := by
    intro hmem
    refine hsep ⟨a + 2, by omega⟩ ⟨?_, ?_⟩
    · rw [castSucc_mk_eq]; exact hmem
    · rw [succ_mk_eq]; exact h3
  have hleft :
      chartPair I x (⟨a + 1, by omega⟩ : Fin 14) =
        normalizeProjectivePair (q (a + 2)) := by
    have hstep :=
      chartPair_succ_eq_normalize_of_leftInfinity q y I x ⟨a, by omega⟩
        (by rw [castSucc_mk_eq]; exact h0)
        (by rw [succ_mk_eq]; exact h1)
        (by simpa using hq (a + 2)) hx
    rw [succ_mk_eq] at hstep
    simpa using hstep
  have hright :
      chartPair I x (⟨a + 2, by omega⟩ : Fin 14) =
        normalizeProjectivePair (q (a + 4)) := by
    have hstep :=
      chartPair_castSucc_eq_normalize_of_rightInfinity q y I x
        ⟨a + 2, by omega⟩
        (by rw [castSucc_mk_eq]; exact h2)
        (by rw [succ_mk_eq]; exact h3)
        (by simpa using hq (a + 4)) hx
    rw [castSucc_mk_eq] at hstep
    simpa using hstep
  -- the middle step equation, with both neighbours pinned
  have hmid := hx (.step ⟨a + 1, by omega⟩)
  change
    HValue (chartPair I x (⟨a + 1, by omega⟩ : Fin 13).castSucc).coord
      (q (((⟨a + 1, by omega⟩ : Fin 13) : ℕ) + 2)).coord
      (chartPair I x (⟨a + 1, by omega⟩ : Fin 13).succ).coord = 0 at hmid
  rw [castSucc_mk_eq, succ_mk_eq] at hmid
  have hidx : (((⟨a + 1, by omega⟩ : Fin 13) : ℕ) + 2) = a + 3 := by
    show a + 1 + 2 = a + 3
    omega
  rw [hidx] at hmid
  have hright' :
      chartPair I x (⟨a + 1 + 1, by omega⟩ : Fin 14) =
        normalizeProjectivePair (q (a + 4)) := by
    have : (⟨a + 1 + 1, by omega⟩ : Fin 14) = (⟨a + 2, by omega⟩ : Fin 14) := by
      ext
      simp
    rw [this]
    exact hright
  rw [hleft, hright'] at hmid
  exact
    (HValue_normalize_first_third_zero_iff
      (q (a + 2)) (q (a + 3)).coord (q (a + 4))).mpr hmid

/-- The exact `d = 3` instance of the shifted block obstruction: the
distance-three relation is literally the base member `C₂` of the frozen family
evaluated on the shifted input window. -/
theorem frozenChartSystem_distance_three_forces_shifted_frozenC_zero
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K)
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x)
    (a : ℕ) (ha : a + 3 < 14)
    (h0 : (⟨a, by omega⟩ : Fin 14) ∈ I)
    (h3 : (⟨a + 3, by omega⟩ : Fin 14) ∈ I) :
    specializeOver φ (fun n => q (a + 2 + n)) (q (a + 3 + 1))
        (frozenC k 0) = 0 := by
  rw [specializeOver_frozenC_zero]
  have hbase :=
    frozenChartSystem_distance_three_forces_input_HValue
      q y I x hq hx a ha h0 h3
  simpa using hbase

/-! ## Contrapositive pruning forms -/

/-- If two consecutive external inputs have nonzero determinant, no two
infinity slots sit at distance two. -/
theorem frozenChartSystem_not_distance_two_of_det_ne_zero
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x)
    (a : ℕ) (ha : a + 2 < 14)
    (hdet : projectiveDet (q (a + 2)) (q (a + 3)) ≠ 0) :
    ¬ ((⟨a, by omega⟩ : Fin 14) ∈ I ∧ (⟨a + 2, by omega⟩ : Fin 14) ∈ I) := by
  intro hmem
  exact hdet
    (frozenChartSystem_distance_two_forces_input_det
      q y I x hq hx a ha hmem.1 hmem.2)

/-- If a window triquadratic is nonzero, no two infinity slots sit at
distance three. -/
theorem frozenChartSystem_not_distance_three_of_HValue_ne_zero
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x)
    (a : ℕ) (ha : a + 3 < 14)
    (hH :
      HValue (q (a + 2)).coord (q (a + 3)).coord (q (a + 4)).coord ≠ 0) :
    ¬ ((⟨a, by omega⟩ : Fin 14) ∈ I ∧ (⟨a + 3, by omega⟩ : Fin 14) ∈ I) := by
  intro hmem
  exact hH
    (frozenChartSystem_distance_three_forces_input_HValue
      q y I x hq hx a ha hmem.1 hmem.2)

/-! ## Mask families and their exact cardinalities -/

/-- No two selected slots are at distance one or two, and both boundary slots
are unselected. -/
def GapThreeInteriorInfinityMask (I : InfinityMask) : Prop :=
  InteriorSeparatedInfinityMask I ∧
    ∀ a : Fin 12, ¬ ((a.castSucc.castSucc ∈ I) ∧
      ((a.succ.succ : Fin 14) ∈ I))

instance instDecidableGapThreeInteriorInfinityMask (I : InfinityMask) :
    Decidable (GapThreeInteriorInfinityMask I) := by
  unfold GapThreeInteriorInfinityMask
  infer_instance

/-- The interior separated masks that additionally forbid distance two. -/
def gapThreeInteriorInfinityMasks : Finset InfinityMask :=
  Finset.univ.filter GapThreeInteriorInfinityMask

/-- Forbidding distances one and two on the twelve interior slots leaves
exactly `129` masks. -/
theorem card_gapThreeInteriorInfinityMask :
    gapThreeInteriorInfinityMasks.card = 129 := by
  native_decide

/-- Every solution mask lies in the `129`-element family once all consecutive
input determinants in the interior window are nonzero.

This is the exact hypothesis that upgrades the proved `377`-element separated
interior family to `129`.  It is carried explicitly; no genericity is claimed
and no obstruction polynomial is shown to be symbolically nonzero. -/
theorem frozenChartSystem_gapThreeInteriorInfinityMask
    {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (I : InfinityMask) (x : ChartVar I → K)
    (hq : AffineInputFamily q)
    (hx : FrozenChartSystem q y I x)
    (hbase : projectiveDet (q 0) (q 1) ≠ 0)
    (hfinal : projectiveDet (q 15) y ≠ 0)
    (hdet : ∀ a : ℕ, a + 2 < 14 →
      projectiveDet (q (a + 2)) (q (a + 3)) ≠ 0) :
    GapThreeInteriorInfinityMask I := by
  refine ⟨?_, ?_⟩
  · exact
      admissibleInfinityMask_interior q y I hbase hfinal
        (frozenChartSystem_admissibleInfinityMask q y I x hq hx)
  · intro a hmem
    have ha : (a : ℕ) + 2 < 14 := by omega
    -- bridge the `castSucc`/`succ` indices used by the mask predicate to the
    -- explicit `Fin.mk` indices used by the propagation theorem
    have h0 : a.castSucc.castSucc = (⟨(a : ℕ), by omega⟩ : Fin 14) := by
      ext
      simp
    have h2 : (a.succ.succ : Fin 14) = (⟨(a : ℕ) + 2, ha⟩ : Fin 14) := by
      ext
      show (a : ℕ) + 1 + 1 = (a : ℕ) + 2
      omega
    rw [h0, h2] at hmem
    exact
      frozenChartSystem_not_distance_two_of_det_ne_zero
        q y I x hq hx (a : ℕ) ha (hdet (a : ℕ) ha) hmem

/-- The interior masks that additionally forbid distance three. -/
def GapFourInteriorInfinityMask (I : InfinityMask) : Prop :=
  GapThreeInteriorInfinityMask I ∧
    ∀ a : Fin 11, ¬ ((a.castSucc.castSucc.castSucc ∈ I) ∧
      ((a.succ.succ.succ : Fin 14) ∈ I))

instance instDecidableGapFourInteriorInfinityMask (I : InfinityMask) :
    Decidable (GapFourInteriorInfinityMask I) := by
  unfold GapFourInteriorInfinityMask
  infer_instance

def gapFourInteriorInfinityMasks : Finset InfinityMask :=
  Finset.univ.filter GapFourInteriorInfinityMask

/-- Forbidding distances one, two and three on the twelve interior slots leaves
exactly `69` masks. -/
theorem card_gapFourInteriorInfinityMask :
    gapFourInteriorInfinityMasks.card = 69 := by
  native_decide

/-! ## Axiom surface of the new results

These `#print axioms` commands are a **temporary diagnostic**, not repository
style: this development had no local Lean toolchain, so embedding them is the
only way to obtain the axiom output in the CI log.  The canonical mechanism is
the generated `Ecdlp/AxiomAudit.lean` / `Ecdlp/LedgerAxiomAudit.lean`, and these
lines should be deleted once the output has been recorded.
-/

#print axioms projectiveDet_eq_zero_of_normalize_eq
#print axioms chartPair_succ_eq_normalize_of_leftInfinity
#print axioms chartPair_castSucc_eq_normalize_of_rightInfinity
#print axioms frozenChartSystem_distance_two_forces_input_det
#print axioms frozenChartSystem_distance_three_forces_input_HValue
#print axioms frozenChartSystem_distance_three_forces_shifted_frozenC_zero
#print axioms frozenChartSystem_not_distance_two_of_det_ne_zero
#print axioms frozenChartSystem_not_distance_three_of_HValue_ne_zero
#print axioms frozenChartSystem_gapThreeInteriorInfinityMask
#print axioms card_gapThreeInteriorInfinityMask
#print axioms card_gapFourInteriorInfinityMask

/-! ## Recorded blockers

Two items from the TASK-025 brief are **not** closed here.  They are recorded
exactly rather than replaced by an assumption.

**B, general gap `d ≥ 4`.**  The intended statement is
`specializeOver φ (fun n => q (a+2+n)) (q (a+d+1)) (frozenC k (d-3)) = 0`.
The `d = 3` case is closed above.  For `d ≥ 4` the two pinned neighbours no
longer determine the whole window: at gap `4` the middle slot `a+2` is itself
free to be an infinity slot, because separatedness only forbids distance one.
The induction therefore needs a case split over the interior mask, and each
branch needs the missing bridge

    FrozenProjectiveChain q s y ↔ FrozenProjectiveChain q s (normalizeProjectivePair y)

i.e. invariance of the chain predicate under projective normalization of its
output argument.  `HValue_normalize_third_zero_iff` supplies the base case of
that bridge, but the successor case additionally needs invariance in the
existentially quantified intermediate witness, which is not available in the
current `FrozenProjectiveChain` API.  That single lemma is the exact blocker.

**C, balanced prefix/suffix single-chart guard.**  Beyond the `d ≥ 4` blocker
above, the prefix obstruction `P_k = specializeOver φ q (q (k+1)) (frozenC k (k-1))`
and the suffix obstruction `S_k = specializeOver φ (fun n => q (k+2+n)) y (frozenC k (12-k))`
each require the *reverse* implication of the chain/`frozenC` equivalence, which
in this development is available only over an algebraically closed target field
(`specializeOver_frozenC_eq_zero_iff_projectiveChain` carries `[IsAlgClosed K]`).
No emptiness statement for `I` is asserted here, and no arity, frozen-stage or
declared-degree figure is claimed, since none was proved.
-/

end Ecdlp.FrozenProjectiveSemaev
