  let W : WeierstrassCurve (ZMod Secp256k1.p) := secp256k1
  set P : ℤ → Polynomial (ZMod Secp256k1.p) := W.preΨ with hP
  set F : ℤ → Polynomial (ZMod Secp256k1.p) := W.Φ with hF'
  set S : ℤ → Polynomial (ZMod Secp256k1.p) := W.ΨSq with hS'
  set B : Polynomial (ZMod Secp256k1.p) := W.Ψ₂Sq with hB'
  -- secp256k1 has b₂=b₄=0, b₆=28, so Ψ₂Sq = 4X³ + 28 (fold C-numerals to plain numerals so the
  -- final `ring` sees the same atoms as the goal's `4`/`7`).
  have hBval : B = 4 * X ^ 3 + 28 := by
    rw [hB', secp256k1_Ψ₂Sq]; simp only [map_ofNat]
  have hBne : B ≠ 0 := by rw [hB']; exact secp256k1_Ψ₂Sq_ne_zero
  have hdef : ∀ m : ℤ, P (2 * m) = P (m - 1) ^ 2 * P m * P (m + 2)
      - P (m - 2) * P m * P (m + 1) ^ 2 := fun m => W.preΨ_even m
  have hS : ∀ m : ℤ, S m = P m ^ 2 * (if Even m then B else 1) := fun m => rfl
  -- ΨSq(2m) = preΨ(2m)²·B and preΨ(2m)=R(m), so ΨSq(2m)·B = R(m)²·B² (the earlier drafts dropped a
  -- factor of B², which is the `EXPR·Ψ₂Sq² = EXPR` the kernel kept flagging).
  have hSd : ∀ m : ℤ, S (2 * m) * B = (P (m - 1) ^ 2 * P m * P (m + 2)
      - P (m - 2) * P m * P (m + 1) ^ 2) ^ 2 * B ^ 2 := fun m => by
    have h1 : S (2 * m) = P (2 * m) ^ 2 * B := by rw [hS]; exact if_pos ⟨m, by ring⟩
    rw [h1, hdef m]; ring
  have hF : ∀ m : ℤ, F m = X * S m - P (m + 1) * P (m - 1) * (if Even m then 1 else B) :=
    fun m => rfl
  have hodd : ∀ t : ℤ, P (2 * t + 1) =
      P (t + 2) * P t ^ 3 * (if Even t then B ^ 2 else 1)
        - P (t - 1) * P (t + 1) ^ 3 * (if Even t then 1 else B ^ 2) := fun t => by
    have h := W.preΨ_odd t; rw [← hP, ← hB'] at h; convert h using 2 <;> ring
  have ht1 : ∀ t : ℤ, Even t → ¬ Even (t - 1) := fun t ht h => by
    obtain ⟨r, hr⟩ := ht; obtain ⟨s, hs⟩ := h; omega
  have ht2 : ∀ t : ℤ, Even t → Even (t - 2) := fun t ht => ht.sub even_two
  have ht3 : ∀ t : ℤ, Even t → ¬ Even (t + 1) := fun t ht h => by
    obtain ⟨r, hr⟩ := ht; obtain ⟨s, hs⟩ := h; omega
  have ht4 : ∀ t : ℤ, ¬ Even t → Even (t - 1) := fun t ht => by
    rcases Int.even_or_odd t with h | h
    · exact absurd h ht
    obtain ⟨r, hr⟩ := h; exact ⟨r, by omega⟩
  have ht5 : ∀ t : ℤ, ¬ Even t → ¬ Even (t - 2) := fun t ht h => by
    obtain ⟨r, hr⟩ := h; exact ht ⟨r + 1, by omega⟩
  have ht6 : ∀ t : ℤ, ¬ Even t → Even (t + 1) := fun t ht => by
    rcases Int.even_or_odd t with h | h
    · exact absurd h ht
    obtain ⟨r, hr⟩ := h; exact ⟨r + 1, by omega⟩
  have hEq : ∀ m : ℤ, S (2 * m) * (B * B) = (4 * S m * (F m ^ 3 + 7 * S m ^ 3)) * (B * B) := by
    intro m
    rcases Int.even_or_odd m with ⟨t, ht⟩ | ⟨t, ht⟩
    · rw [show m = 2 * t from by rw [ht]; ring]
      have he : Even (2 * t) := ⟨t, by ring⟩
      rw [show S (2 * (2 * t)) * (B * B) = (S (2 * (2 * t)) * B) * B by ring]
      rw [hSd (2 * t)]
      conv_rhs =>
        rw [hS (2 * t), hF (2 * t), hS (2 * t)]
      simp only [he, ↓reduceIte]
      -- normalize the integer indices to canonical `2*_` / `2*_+1` so the recurrences fire
      simp only [show (2 * t - 1 : ℤ) = 2 * (t - 1) + 1 from by ring,
        show (2 * t + 2 : ℤ) = 2 * (t + 1) from by ring,
        show (2 * t - 2 : ℤ) = 2 * (t - 1) from by ring]
      simp only [hdef, hodd]
      by_cases htc : Even t
      · simp only [htc, ht1 t htc, ht2 t htc, ht3 t htc, ↓reduceIte, mul_one, one_mul] <;>
          (try rw [hBval]) <;> ring
      · simp only [htc, ht4 t htc, ht5 t htc, ht6 t htc, ↓reduceIte, mul_one, one_mul] <;>
          (try rw [hBval]) <;> ring
    · rw [show m = 2 * t + 1 from by rw [ht]; ring]
      have hne : ¬ Even (2 * t + 1) := fun h => by obtain ⟨r, hr⟩ := h; omega
      rw [show S (2 * (2 * t + 1)) * (B * B) = (S (2 * (2 * t + 1)) * B) * B by ring]
      rw [hSd (2 * t + 1)]
      conv_rhs =>
        rw [hS (2 * t + 1), hF (2 * t + 1), hS (2 * t + 1)]
      simp only [hne, ↓reduceIte]
      -- normalize the integer indices to canonical `2*_` / `2*_+1` so the recurrences fire
      simp only [show (2 * t + 1 - 1 : ℤ) = 2 * t from by ring,
        show (2 * t + 1 + 2 : ℤ) = 2 * (t + 1) + 1 from by ring,
        show (2 * t + 1 - 2 : ℤ) = 2 * (t - 1) + 1 from by ring,
        show (2 * t + 1 + 1 : ℤ) = 2 * (t + 1) from by ring]
      simp only [hdef, hodd]
      by_cases htc : Even t
      · simp only [htc, ht1 t htc, ht2 t htc, ht3 t htc, ↓reduceIte, mul_one, one_mul] <;>
          (try rw [hBval]) <;> ring
      · simp only [htc, ht4 t htc, ht5 t htc, ht6 t htc, ↓reduceIte, mul_one, one_mul] <;>
          (try rw [hBval]) <;> ring
  have key : (B * B) * S (2 * k) = (B * B) * (4 * S k * (F k ^ 3 + 7 * S k ^ 3)) := by
    have := hEq k; ring_nf at this ⊢; linear_combination this
  exact mul_left_cancel₀ (mul_ne_zero hBne hBne) key
