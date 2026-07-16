import Mathlib
import Ecdlp.Proved.NormEDSIsElliptic

/-!
# `normEDS` never has two consecutive zeros — Ward's apparition rigidity, abstractly

The scalar core of node **N5** (`gcd(Φₙ, ΨSqₙ) = 1`) of the `ψₙ ↔ E[n]` bridge
(`notes/DIVISION_POLY_TORSION_MAP.md`): after the evaluation bridge reduces a common
root of `ΨSq n` / `Φ n` to **two consecutive zeros of the scalar `normEDS` sequence**
(PR #171, `exists_normEDS_consecutive_eq_zero_of_not_isCoprime`), what remains is a
statement with no polynomials, no curve, and no evaluation — exactly the theorem of
this file:

> Over an integral domain, `W := normEDS b c d` has no two consecutive zeros,
> provided `¬(b = 0 ∧ c = 0)` and `¬(c = 0 ∧ d = 0)`.

The hypotheses are **sharp**: `(b, c, d) = (0, 0, d)` gives `W 2 = W 3 = 0`, and
`(b, 0, 0)` gives `W 3 = W 4 = d·b = 0`. On the curve they are discharged by the
already-proved coprimality certificates `CoprimePsi2Psi3` (no common root of
`Ψ₂Sq, Ψ₃`) and `CoprimePsi3PrePsi4` (no common root of `Ψ₃, preΨ₄`) — the
decomposition the certificate family was built for.

**Proof (Ward-style rank-of-apparition rigidity).** From `IsEllSequence` at `r = 1`
(via `normEDS_isEllSequence`, `Ecdlp/Proved/NormEDSIsElliptic.lean`), every zero
position `ρ` satisfies the translation identity

  `W (n + ρ) * W (n - ρ) = -(W (ρ + 1) * W (ρ - 1)) * W n ^ 2`   (∗)

Take `ρ` the **minimal** positive zero (so `ρ ≥ 2`, as `W 1 = 1`):
* **Case A** (`W (ρ+1) ≠ 0`): since also `W (ρ-1) ≠ 0` by minimality, (∗) turns a
  zero at `k` into a zero at `k - ρ` *with no case split* — so every zero index is
  divisible by `ρ`. Consecutive zeros would force `ρ ∣ 1`, contradiction.
* **Case B** (`W (ρ+1) = 0`): `ρ = 2` means `b = c = 0`; `ρ = 3` means `c = d = 0`
  (as `W 2 = b ≠ 0` by minimality); and `ρ ≥ 4` is self-contradictory — (∗) gives
  `W (2ρ-3) = 0`, while `normEDS_odd` at `m = ρ-2` then forces
  `W (ρ-3) * W (ρ-1)³ = 0`, both indices in `(0, ρ)`.

Every identity and the sharpness examples are numerically cross-checked over `𝔽_p`
in `scripts/certs/normeds_consecutive_zeros_check.py` (design insurance only —
nothing from it enters the proofs). Stated over a bare integral domain with no
curve in sight, this is an upstream (Mathlib) candidate alongside
`normEDS_isEllSequence`. No `native_decide`, no new axioms.
-/

namespace Ecdlp.NormEDS

variable {R : Type*}

/-- **Translation identity at a zero.** If `W ρ = 0` for `W = normEDS b c d`, then
`W (n + ρ) * W (n - ρ) = -(W (ρ + 1) * W (ρ - 1)) * W n ^ 2` for every `n` — the
`r = 1` slice of `IsEllSequence` at the zero position. This is Ward's key tool for
the rank of apparition. -/
theorem normEDS_shift_mul_shift_of_eq_zero [CommRing R] (b c d : R) {ρ : ℤ}
    (hρ : normEDS b c d ρ = 0) (n : ℤ) :
    normEDS b c d (n + ρ) * normEDS b c d (n - ρ)
      = -(normEDS b c d (ρ + 1) * normEDS b c d (ρ - 1)) * normEDS b c d n ^ 2 := by
  have h := normEDS_isEllSequence b c d n ρ 1
  rw [normEDS_one, hρ] at h
  linear_combination h

/-- **The descent step.** If `W ρ = 0` with both neighbours `W (ρ ± 1)` nonzero
(over a domain), then every zero descends by `ρ`: `W k = 0 → W (k - ρ) = 0`.
No case split — the square in the translation identity absorbs the ambiguity. -/
theorem normEDS_sub_eq_zero_of_eq_zero [CommRing R] [IsDomain R] (b c d : R) {ρ : ℤ}
    (hρ : normEDS b c d ρ = 0) (hA : normEDS b c d (ρ + 1) ≠ 0)
    (hB : normEDS b c d (ρ - 1) ≠ 0) {k : ℤ} (hk : normEDS b c d k = 0) :
    normEDS b c d (k - ρ) = 0 := by
  have h := normEDS_shift_mul_shift_of_eq_zero b c d hρ (k - ρ)
  rw [show k - ρ + ρ = k by ring, hk, zero_mul] at h
  have h2 : normEDS b c d (ρ + 1) * (normEDS b c d (ρ - 1) *
      (normEDS b c d (k - ρ) * normEDS b c d (k - ρ))) = 0 := by
    linear_combination h
  rcases mul_eq_zero.mp h2 with h' | h2
  · exact absurd h' hA
  rcases mul_eq_zero.mp h2 with h' | h2
  · exact absurd h' hB
  exact mul_self_eq_zero.mp h2

/-- ℕ-indexed core: consecutive zeros at `(N, N+1)` are impossible. -/
private theorem no_consec_aux [CommRing R] [IsDomain R] (b c d : R)
    (h23 : ¬(b = 0 ∧ c = 0)) (h34 : ¬(c = 0 ∧ d = 0)) (N : ℕ)
    (h0 : normEDS b c d (N : ℤ) = 0) (h1 : normEDS b c d ((N : ℤ) + 1) = 0) : False := by
  -- `W 1 = 1 ≠ 0` kills `N = 0`.
  rcases Nat.eq_zero_or_pos N with rfl | hNpos
  · rw [show ((0 : ℕ) : ℤ) + 1 = 1 by norm_num, normEDS_one] at h1
    exact one_ne_zero h1
  -- The minimal positive zero `ρ`.
  obtain ⟨ρ, ⟨hρpos, hρ0Z⟩, hmin⟩ : ∃ ρ : ℕ, (0 < ρ ∧ normEDS b c d (ρ : ℤ) = 0) ∧
      ∀ k : ℕ, 0 < k → normEDS b c d (k : ℤ) = 0 → ρ ≤ k := by
    have hne : {k : ℕ | 0 < k ∧ normEDS b c d (k : ℤ) = 0}.Nonempty := ⟨N, hNpos, h0⟩
    exact ⟨sInf _, Nat.sInf_mem hne, fun k hk hkz => Nat.sInf_le ⟨hk, hkz⟩⟩
  -- Minimality, phrased over ℤ.
  have hminZ : ∀ j : ℤ, 0 < j → j < (ρ : ℤ) → normEDS b c d j ≠ 0 := by
    intro j hj hjρ hzero
    have hk : ρ ≤ j.toNat := hmin j.toNat (by omega) (by rwa [Int.toNat_of_nonneg hj.le])
    omega
  -- `ρ ≥ 2`, since `W 1 = 1`.
  have hρ2 : 2 ≤ ρ := by
    rcases Nat.lt_or_ge ρ 2 with h | h
    · exfalso
      have hρ1 : ρ = 1 := by omega
      rw [hρ1, show ((1 : ℕ) : ℤ) = 1 by norm_num, normEDS_one] at hρ0Z
      exact one_ne_zero hρ0Z
    · exact h
  by_cases hcase : normEDS b c d ((ρ : ℤ) + 1) = 0
  · -- Case B: `ρ` and `ρ + 1` are both zeros.
    rcases Nat.lt_or_ge ρ 4 with hρ4 | hρ4
    · rcases Nat.lt_or_ge ρ 3 with hρ3 | hρ3
      · -- `ρ = 2`: `b = 0` and `c = 0`.
        have hρeq : ρ = 2 := by omega
        subst hρeq
        rw [show ((2 : ℕ) : ℤ) = 2 by norm_num, normEDS_two] at hρ0Z
        rw [show ((2 : ℕ) : ℤ) + 1 = 3 by norm_num, normEDS_three] at hcase
        exact h23 ⟨hρ0Z, hcase⟩
      · -- `ρ = 3`: `c = 0` and (since `b = W 2 ≠ 0` by minimality) `d = 0`.
        have hρeq : ρ = 3 := by omega
        subst hρeq
        have hbne : b ≠ 0 := by
          have h2 := hminZ 2 (by norm_num) (by omega)
          rwa [normEDS_two] at h2
        rw [show ((3 : ℕ) : ℤ) = 3 by norm_num, normEDS_three] at hρ0Z
        rw [show ((3 : ℕ) : ℤ) + 1 = 4 by norm_num, normEDS_four] at hcase
        rcases mul_eq_zero.mp hcase with hd | hb'
        · exact h34 ⟨hρ0Z, hd⟩
        · exact hbne hb'
    · -- `ρ ≥ 4` is self-contradictory.
      have h3ne : normEDS b c d 3 ≠ 0 := hminZ 3 (by norm_num) (by omega)
      -- (∗) at `n = ρ - 3`, with `W (ρ+1) = 0`: `W (2ρ-3) * W (-3) = 0`.
      have hs := normEDS_shift_mul_shift_of_eq_zero b c d hρ0Z ((ρ : ℤ) - 3)
      rw [show (ρ : ℤ) - 3 + ρ = 2 * ρ - 3 by ring, show (ρ : ℤ) - 3 - ρ = -3 by ring,
        hcase] at hs
      have hz : normEDS b c d (2 * (ρ : ℤ) - 3) * normEDS b c d (-3) = 0 := by
        linear_combination hs
      rw [normEDS_neg] at hz
      have h2ρ3 : normEDS b c d (2 * (ρ : ℤ) - 3) = 0 := by
        rcases mul_eq_zero.mp hz with h | h
        · exact h
        · exact absurd (neg_eq_zero.mp h) h3ne
      -- The odd doubling formula at `m = ρ - 2` then hits inside `(0, ρ)`.
      have hodd := normEDS_odd b c d ((ρ : ℤ) - 2)
      rw [show 2 * ((ρ : ℤ) - 2) + 1 = 2 * ρ - 3 by ring, show (ρ : ℤ) - 2 + 2 = ρ by ring,
        show (ρ : ℤ) - 2 - 1 = ρ - 3 by ring, show (ρ : ℤ) - 2 + 1 = ρ - 1 by ring,
        h2ρ3, hρ0Z] at hodd
      have hprod : normEDS b c d ((ρ : ℤ) - 3) * (normEDS b c d ((ρ : ℤ) - 1) *
          (normEDS b c d ((ρ : ℤ) - 1) * normEDS b c d ((ρ : ℤ) - 1))) = 0 := by
        linear_combination hodd
      rcases mul_eq_zero.mp hprod with h | hp
      · exact absurd h (hminZ ((ρ : ℤ) - 3) (by omega) (by omega))
      rcases mul_eq_zero.mp hp with h | hp
      · exact absurd h (hminZ ((ρ : ℤ) - 1) (by omega) (by omega))
      exact absurd (mul_self_eq_zero.mp hp) (hminZ ((ρ : ℤ) - 1) (by omega) (by omega))
  · -- Case A: descend by `ρ` — every zero index is divisible by `ρ`.
    have hρm1 : normEDS b c d ((ρ : ℤ) - 1) ≠ 0 := hminZ ((ρ : ℤ) - 1) (by omega) (by omega)
    have hdesc : ∀ M k : ℕ, k ≤ M → normEDS b c d (k : ℤ) = 0 → ρ ∣ k := by
      intro M
      induction M with
      | zero =>
        intro k hk _
        have hk0 : k = 0 := by omega
        subst hk0
        exact dvd_zero ρ
      | succ M IH =>
        intro k hk hkz
        rcases Nat.lt_or_ge k ρ with hlt | hge
        · rcases Nat.eq_zero_or_pos k with rfl | hkpos
          · exact dvd_zero ρ
          · exact absurd hkz (hminZ (k : ℤ) (by omega) (by omega))
        · rcases Nat.lt_or_ge k (M + 1) with hkM | hkM
          · exact IH k (by omega) hkz
          · have hstep : normEDS b c d ((k : ℤ) - ρ) = 0 :=
              normEDS_sub_eq_zero_of_eq_zero b c d hρ0Z hcase hρm1 hkz
            have hdvd' : ρ ∣ k - ρ := by
              refine IH (k - ρ) (by omega) ?_
              rw [show (((k - ρ : ℕ)) : ℤ) = (k : ℤ) - ρ by omega]
              exact hstep
            have h' : ρ ∣ k - ρ + ρ := dvd_add hdvd' dvd_rfl
            rwa [Nat.sub_add_cancel hge] at h'
    have hdvd0 : ρ ∣ N := hdesc N N le_rfl h0
    have hdvd1 : ρ ∣ N + 1 := by
      refine hdesc (N + 1) (N + 1) le_rfl ?_
      push_cast
      exact h1
    have hone : ρ ∣ 1 := by
      have h' := Nat.dvd_sub hdvd1 hdvd0
      rwa [show N + 1 - N = 1 by omega] at h'
    have : ρ = 1 := Nat.dvd_one.mp hone
    omega

/-- **`normEDS` has no two consecutive zeros** (Ward's apparition rigidity). Over an
integral domain, if `¬(b = 0 ∧ c = 0)` and `¬(c = 0 ∧ d = 0)` — both necessary — then
`normEDS b c d` never vanishes at both `n` and `n + 1`. This is the scalar heart of
N5: composed with the evaluation bridge, a common root of `ΨSq n` / `Φ n` would force
exactly such a pair. -/
theorem normEDS_not_consecutive_zeros [CommRing R] [IsDomain R] (b c d : R)
    (h23 : ¬(b = 0 ∧ c = 0)) (h34 : ¬(c = 0 ∧ d = 0)) (n : ℤ) :
    ¬(normEDS b c d n = 0 ∧ normEDS b c d (n + 1) = 0) := by
  rintro ⟨h0, h1⟩
  by_cases hn : 0 ≤ n
  · refine no_consec_aux b c d h23 h34 n.toNat ?_ ?_
    · rwa [Int.toNat_of_nonneg hn]
    · rw [Int.toNat_of_nonneg hn]
      exact h1
  · -- reflect via `W (-k) = -W k`
    have h0' : normEDS b c d (-n - 1) = 0 := by
      rw [show -n - 1 = -(n + 1) by ring, normEDS_neg, h1, neg_zero]
    have h1' : normEDS b c d (-n) = 0 := by
      rw [normEDS_neg, h0, neg_zero]
    refine no_consec_aux b c d h23 h34 (-n - 1).toNat ?_ ?_
    · rwa [Int.toNat_of_nonneg (by omega)]
    · rw [show (((-n - 1).toNat : ℤ)) + 1 = -n by omega]
      exact h1'

/-- Variant with the pair `(n - 1, n)` — the shape the evaluation-bridge descent
produces (`w n = 0` and `w (n - 1) = 0 ∨ w (n + 1) = 0`). -/
theorem normEDS_not_consecutive_zeros' [CommRing R] [IsDomain R] (b c d : R)
    (h23 : ¬(b = 0 ∧ c = 0)) (h34 : ¬(c = 0 ∧ d = 0)) (n : ℤ) :
    ¬(normEDS b c d n = 0 ∧ normEDS b c d (n - 1) = 0) := by
  rintro ⟨h0, h1⟩
  refine normEDS_not_consecutive_zeros b c d h23 h34 (n - 1) ⟨h1, ?_⟩
  rwa [show n - 1 + 1 = n by ring]

end Ecdlp.NormEDS
