import Ecdlp.Proved.FrozenProjectiveSecpLocalFiber

/-!
# Point semantics of the frozen projective secp256k1 chain

This file iterates the complete local Kummer-fiber theorem over the recursive
frozen projective chain.  Every valid projective intermediate representative
is retained: only its normalization is compared with a Kummer image.

The result is deliberately limited to point-valued seeds over the algebraic
closure.  It does not construct points from affine coordinates, identify an
`S17` root set, prove descent, or assert that the two local Kummer roots are
distinct.
-/

namespace Ecdlp.FrozenProjectiveSecpChainSemantics

open scoped BigOperators

open Ecdlp
open Ecdlp.Curve
open Ecdlp.FrozenProjectiveSemaev
open Ecdlp.FrozenProjectiveSecpLocalFiber

noncomputable section

abbrev Fp := Ecdlp.FrozenProjectiveSecpLocalFiber.Fp
abbrev FpBar := Ecdlp.FrozenProjectiveSecpLocalFiber.FpBar
abbrev BarCurve := Ecdlp.FrozenProjectiveSecpLocalFiber.BarCurve
abbrev BarPoint := Ecdlp.FrozenProjectiveSecpLocalFiber.BarPoint

local instance : DecidableEq FpBar := Classical.decEq _

private instance barCurve_isElliptic : BarCurve.IsElliptic :=
  inferInstanceAs
    ((secp256k1.map (algebraMap Fp FpBar)).IsElliptic)

/-- A point family chooses either a seed or its inverse at every index in the
specified finite prefix.  Values outside the prefix are irrelevant. -/
def SignedPointPrefix
    (seed lift : ℕ → BarPoint) (n : ℕ) : Prop :=
  ∀ i, i < n → lift i = seed i ∨ lift i = -seed i

/-- The finite left-to-right sum of a point family. -/
def signedPrefixSum (lift : ℕ → BarPoint) (n : ℕ) : BarPoint :=
  ∑ i ∈ Finset.range n, lift i

private theorem signedPrefixSum_succ
    (lift : ℕ → BarPoint) (n : ℕ) :
    signedPrefixSum lift (n + 1) = signedPrefixSum lift n + lift n := by
  simp [signedPrefixSum, Finset.sum_range_succ]

private theorem signedPrefixSum_update_last
    (lift : ℕ → BarPoint) (n : ℕ) (P : BarPoint) :
    signedPrefixSum (Function.update lift n P) (n + 1) =
      signedPrefixSum lift n + P := by
  rw [signedPrefixSum_succ]
  congr 1
  · apply Finset.sum_congr rfl
    intro i hi
    rw [Function.update_of_ne]
    exact ne_of_lt (Finset.mem_range.mp hi)
  · simp

private theorem barKummer_signed_pair
    (P Q P' Q' : BarPoint)
    (hP : P' = P ∨ P' = -P)
    (hQ : Q' = Q ∨ Q' = -Q) :
    barKummer (P' + Q') = barKummer (P + Q) ∨
      barKummer (P' + Q') = barKummer (P - Q) := by
  rcases hP with hP | hP
  · rcases hQ with hQ | hQ
    · rw [hP, hQ]
      exact Or.inl rfl
    · rw [hP, hQ]
      exact Or.inr (by simp [sub_eq_add_neg])
  · rcases hQ with hQ | hQ
    · rw [hP, hQ]
      right
      calc
        barKummer (-P + Q) = barKummer (-(P - Q)) := by
          congr 1
          abel
        _ = barKummer (P - Q) := barKummer_neg (P - Q)
    · rw [hP, hQ]
      left
      calc
        barKummer (-P + -Q) = barKummer (-(P + Q)) := by
          congr 1
          abel
        _ = barKummer (P + Q) := barKummer_neg (P + Q)

/-- Generic point semantics of the recursive frozen projective chain.

At level `s`, the chain consumes exactly the seed prefix `0, …, s + 1`.
Every consumed seed may be used with either sign.  Conversely, every such
signed finite sum supplies a complete projective chain.  Since Kummer
coordinates identify a point with its inverse, no sign is privileged at the
first seed and no distinctness of alternative sums is claimed. -/
theorem frozenProjectiveChain_barKummer_iff_signedPrefixSum
    (seed : ℕ → BarPoint) (s : ℕ)
    (W : ProjectivePair FpBar) :
    FrozenProjectiveChain (fun i => barKummer (seed i)) s W ↔
      ∃ lift : ℕ → BarPoint,
        SignedPointPrefix seed lift (s + 2) ∧
        normalizeProjectivePair W =
          barKummer (signedPrefixSum lift (s + 2)) := by
  induction s generalizing W with
  | zero =>
      change
        HValue (barKummer (seed 0)).coord (barKummer (seed 1)).coord W.coord = 0 ↔
          ∃ lift : ℕ → BarPoint,
            SignedPointPrefix seed lift (0 + 2) ∧
            normalizeProjectivePair W =
              barKummer (signedPrefixSum lift (0 + 2))
      rw [HValue_barKummer_zero_iff]
      constructor
      · rintro (hplus | hminus)
        · refine ⟨seed, ?_, ?_⟩
          · intro i hi
            exact Or.inl rfl
          · simpa [signedPrefixSum, Finset.sum_range_succ] using hplus
        · let lift := Function.update seed 1 (-seed 1)
          refine ⟨lift, ?_, ?_⟩
          · intro i hi
            interval_cases i <;> simp [lift]
          · simpa [signedPrefixSum, lift, sub_eq_add_neg,
              Finset.sum_range_succ, Function.update_of_ne] using hminus
      · rintro ⟨lift, hsigned, hW⟩
        have h0 := hsigned 0 (by omega)
        have h1 := hsigned 1 (by omega)
        have hpair := barKummer_signed_pair
          (seed 0) (seed 1) (lift 0) (lift 1) h0 h1
        have hsum :
            signedPrefixSum lift 2 = lift 0 + lift 1 := by
          simp [signedPrefixSum, Finset.sum_range_succ]
        rw [hsum] at hW
        rcases hpair with hplus | hminus
        · exact Or.inl (hW.trans hplus)
        · exact Or.inr (hW.trans hminus)
  | succ s ih =>
      rw [FrozenProjectiveChain]
      constructor
      · rintro ⟨z, hz, hlocal⟩
        rcases (ih z).mp hz with ⟨lift, hsigned, hzsum⟩
        have hlocal' :
            HValue (barKummer (signedPrefixSum lift (s + 2))).coord
                (barKummer (seed (s + 2))).coord W.coord = 0 := by
          have hn :=
            (HValue_normalize_first_zero_iff z
              (barKummer (seed (s + 2))).coord W.coord).mp hlocal
          simpa only [hzsum] using hn
        rcases
            (HValue_barKummer_zero_iff
              (signedPrefixSum lift (s + 2)) (seed (s + 2)) W).mp hlocal' with
          hplus | hminus
        · let lift' := Function.update lift (s + 2) (seed (s + 2))
          refine ⟨lift', ?_, ?_⟩
          · intro i hi
            by_cases hilast : i = s + 2
            · subst i
              simp [lift']
            · have hiprefix : i < s + 2 := by omega
              simpa [lift', hilast] using hsigned i hiprefix
          · calc
              normalizeProjectivePair W =
                  barKummer
                    (signedPrefixSum lift (s + 2) + seed (s + 2)) := hplus
              _ = barKummer (signedPrefixSum lift' (s + 3)) := by
                rw [signedPrefixSum_update_last]
        · let lift' := Function.update lift (s + 2) (-seed (s + 2))
          refine ⟨lift', ?_, ?_⟩
          · intro i hi
            by_cases hilast : i = s + 2
            · subst i
              simp [lift']
            · have hiprefix : i < s + 2 := by omega
              simpa [lift', hilast] using hsigned i hiprefix
          · calc
              normalizeProjectivePair W =
                  barKummer
                    (signedPrefixSum lift (s + 2) - seed (s + 2)) := hminus
              _ = barKummer (signedPrefixSum lift' (s + 3)) := by
                rw [signedPrefixSum_update_last]
                simp [sub_eq_add_neg]
      · rintro ⟨lift, hsigned, hW⟩
        let S := signedPrefixSum lift (s + 2)
        have hprefixSigned : SignedPointPrefix seed lift (s + 2) := by
          intro i hi
          exact hsigned i (by omega)
        have hprefix :
            FrozenProjectiveChain (fun i => barKummer (seed i)) s
              (barKummer S) := by
          apply (ih (barKummer S)).mpr
          exact ⟨lift, hprefixSigned, normalize_barKummer S⟩
        refine ⟨barKummer S, hprefix, ?_⟩
        apply
          (HValue_barKummer_zero_iff S (seed (s + 2)) W).mpr
        have hlast := hsigned (s + 2) (by omega)
        rw [signedPrefixSum_succ] at hW
        rcases hlast with hlast | hlast
        · left
          simpa only [S, hlast] using hW
        · right
          simpa only [S, hlast, sub_eq_add_neg] using hW

/-! ## Explicit Boolean sign spelling -/

/-- Apply an explicitly chosen sign to a point. -/
def applyPointSign : Bool → BarPoint → BarPoint
  | true, P => P
  | false, P => -P

@[simp] theorem applyPointSign_true (P : BarPoint) :
    applyPointSign true P = P := rfl

@[simp] theorem applyPointSign_false (P : BarPoint) :
    applyPointSign false P = -P := rfl

/-- The same chain semantics with every `±` choice written explicitly as a
Boolean sign.  Only the first `s + 2` Boolean values are observed. -/
theorem frozenProjectiveChain_barKummer_iff_explicitSigns
    (seed : ℕ → BarPoint) (s : ℕ)
    (W : ProjectivePair FpBar) :
    FrozenProjectiveChain (fun i => barKummer (seed i)) s W ↔
      ∃ positive : ℕ → Bool,
        normalizeProjectivePair W =
          barKummer
            (∑ i ∈ Finset.range (s + 2),
              applyPointSign (positive i) (seed i)) := by
  rw [frozenProjectiveChain_barKummer_iff_signedPrefixSum]
  constructor
  · rintro ⟨lift, hsigned, hW⟩
    classical
    let positive : ℕ → Bool :=
      fun i => if lift i = seed i then true else false
    refine ⟨positive, ?_⟩
    rw [hW]
    congr 1
    apply Finset.sum_congr rfl
    intro i hi
    have hi' := hsigned i (Finset.mem_range.mp hi)
    by_cases hpositive : lift i = seed i
    · simp [positive, hpositive]
    · rcases hi' with hi' | hi'
      · exact (hpositive hi').elim
      · have hsign : positive i = false := by
          simp [positive, hpositive]
        rw [hsign, applyPointSign_false]
        exact hi'
  · rintro ⟨positive, hW⟩
    let lift : ℕ → BarPoint :=
      fun i => applyPointSign (positive i) (seed i)
    refine ⟨lift, ?_, ?_⟩
    · intro i _
      cases hsign : positive i <;> simp [lift, hsign]
    · simpa [signedPrefixSum, lift] using hW

/-! ## The literal fourteen-intermediate chart cover -/

/-- At frozen stage fourteen, the chart cover has exactly the signed-point
sum semantics for the sixteen consumed seeds.  Infinity-chart intermediate
slots remain part of `FrozenChartCover`; the theorem does not discard them. -/
theorem frozenChartCover_barKummer_iff_signedPrefixSum
    (seed : ℕ → BarPoint) (W : ProjectivePair FpBar) :
    FrozenChartCover (fun i => barKummer (seed i)) W ↔
      ∃ lift : ℕ → BarPoint,
        SignedPointPrefix seed lift 16 ∧
        normalizeProjectivePair W =
          barKummer (signedPrefixSum lift 16) := by
  exact
    (frozenProjectiveChain_iff_chartCover
      (fun i => barKummer (seed i)) W).symm.trans
        (by simpa using
          (frozenProjectiveChain_barKummer_iff_signedPrefixSum seed 14 W))

/-- Boolean `±` spelling of the stage-fourteen chart-cover corollary. -/
theorem frozenChartCover_barKummer_iff_explicitSigns
    (seed : ℕ → BarPoint) (W : ProjectivePair FpBar) :
    FrozenChartCover (fun i => barKummer (seed i)) W ↔
      ∃ positive : ℕ → Bool,
        normalizeProjectivePair W =
          barKummer
            (∑ i ∈ Finset.range 16,
              applyPointSign (positive i) (seed i)) := by
  exact
    (frozenProjectiveChain_iff_chartCover
      (fun i => barKummer (seed i)) W).symm.trans
        (by simpa using
          (frozenProjectiveChain_barKummer_iff_explicitSigns seed 14 W))

end

end Ecdlp.FrozenProjectiveSecpChainSemantics
