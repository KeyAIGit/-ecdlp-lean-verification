import Mathlib

#check @normEDS_even

variable {R : Type*} [CommRing R]

-- ── verified abstract step certificates (Fable-designed, kernel-verified) ──
theorem somos4_odd_step (b c d : R) (W : ℤ → R) (M : ℤ)
    (hOM1 : W (2*M+3) = W (M+3) * W (M+1) ^ 3 - W M * W (M+2) ^ 3)
    (hEM1 : W (2*M+2) * b = W M ^ 2 * W (M+1) * W (M+3) - W (M-1) * W (M+1) * W (M+2) ^ 2)
    (hEM  : W (2*M) * b = W (M-1) ^ 2 * W M * W (M+2) - W (M-2) * W M * W (M+1) ^ 2)
    (hOM  : W (2*M+1) = W (M+2) * W M ^ 3 - W (M-1) * W (M+1) ^ 3)
    (hOMm1 : W (2*M-1) = W (M+1) * W (M-1) ^ 3 - W (M-2) * W M ^ 3)
    (ih0 : W (M+2) * W (M-2) = b ^ 2 * W (M+1) * W (M-1) - c * W M ^ 2)
    (ih1 : W (M+3) * W (M-1) = b ^ 2 * W (M+2) * W M - c * W (M+1) ^ 2) :
    W (2*M+3) * W (2*M-1) = b ^ 2 * W (2*M+2) * W (2*M) - c * W (2*M+1) ^ 2 := by
  linear_combination (norm := ring1)
      W (2*M-1) * hOM1 + (- b * W (2*M)) * hEM1
    + (- (W M ^ 2 * W (M+1) * W (M+3) - W (M-1) * W (M+1) * W (M+2) ^ 2)) * hEM
    + (c * (W (2*M+1) + (W (M+2) * W M ^ 3 - W (M-1) * W (M+1) ^ 3))) * hOM
    + (W (M+3) * W (M+1) ^ 3 - W M * W (M+2) ^ 3) * hOMm1
    + (W M * W (M+2) * (W (M+2) * W M ^ 3 - W (M-1) * W (M+1) ^ 3)) * ih0
    + (- W (M-1) * W (M+1) * (W (M+2) * W M ^ 3 - W (M-1) * W (M+1) ^ 3)) * ih1

theorem somos4_even_step_scaled (b c d : R) (W : ℤ → R) (M : ℤ)
    (hEM1 : W (2*M+2) * b = W M ^ 2 * W (M+1) * W (M+3) - W (M-1) * W (M+1) * W (M+2) ^ 2)
    (hEMm1 : W (2*M-2) * b = W (M-2) ^ 2 * W (M-1) * W (M+1) - W (M-3) * W (M-1) * W M ^ 2)
    (hEM  : W (2*M) * b = W (M-1) ^ 2 * W M * W (M+2) - W (M-2) * W M * W (M+1) ^ 2)
    (hOM  : W (2*M+1) = W (M+2) * W M ^ 3 - W (M-1) * W (M+1) ^ 3)
    (hOMm1 : W (2*M-1) = W (M+1) * W (M-1) ^ 3 - W (M-2) * W M ^ 3)
    (ihm1 : W (M+1) * W (M-3) = b ^ 2 * W M * W (M-2) - c * W (M-1) ^ 2)
    (ih0 : W (M+2) * W (M-2) = b ^ 2 * W (M+1) * W (M-1) - c * W M ^ 2)
    (ih1 : W (M+3) * W (M-1) = b ^ 2 * W (M+2) * W M - c * W (M+1) ^ 2) :
    b ^ 2 * (W (2*M+2) * W (2*M-2)) = b ^ 2 * (b ^ 2 * W (2*M+1) * W (2*M-1) - c * W (2*M) ^ 2) := by
  linear_combination (norm := ring1)
      (b * W (2*M-2)) * hEM1
    + (W (M+1) * (W M ^ 2 * W (M+3) - W (M-1) * W (M+2) ^ 2)) * hEMm1
    + (c * (b * W (2*M) + (W (M-1) ^ 2 * W M * W (M+2) - W (M-2) * W M * W (M+1) ^ 2))) * hEM
    + (- b ^ 4 * W (2*M-1)) * hOM
    + (- b ^ 4 * (W (M+2) * W M ^ 3 - W (M-1) * W (M+1) ^ 3)) * hOMm1
    + (- W (M-1) * W M ^ 2 * (W M ^ 2 * W (M+3) - W (M-1) * W (M+2) ^ 2)) * ihm1
    + (b ^ 2 * W M ^ 3 * (W (M-1) ^ 2 * W (M+2) + W (M-2) * W (M+1) ^ 2) - W (M-1) ^ 2 * W (M+1) ^ 2 * (W (M-2) * W (M+2) + b ^ 2 * W (M-1) * W (M+1) + c * W M ^ 2)) * ih0
    + (W M ^ 2 * (W (M-2) ^ 2 * W (M+1) ^ 2 - b ^ 2 * W (M-2) * W M ^ 3 + c * W (M-1) ^ 2 * W M ^ 2)) * ih1

-- ── the Somos-4 slice over a domain, ℕ indices ──
theorem somos4_dom [IsDomain R] (b c d : R) (hb : b ≠ 0) (n : ℕ) :
    normEDS b c d ((n:ℤ)+2) * normEDS b c d ((n:ℤ)-2)
      = b^2 * normEDS b c d ((n:ℤ)+1) * normEDS b c d ((n:ℤ)-1) - c * normEDS b c d (n:ℤ) ^ 2 := by
  refine normEDSRec'
    (P := fun k : ℕ => normEDS b c d ((k:ℤ)+2) * normEDS b c d ((k:ℤ)-2)
      = b^2 * normEDS b c d ((k:ℤ)+1) * normEDS b c d ((k:ℤ)-1) - c * normEDS b c d (k:ℤ) ^ 2)
    ?_ ?_ ?_ ?_ ?_ ?_ ?_ n
  · -- P 0
    norm_num <;> ring
  · -- P 1
    norm_num <;> ring
  · -- P 2
    norm_num <;> ring
  · -- P 3
    have h5 := normEDS_odd b c d 2
    norm_num at h5 ⊢
    linear_combination h5
  · -- P 4
    have h6 := normEDS_even b c d 3
    norm_num at h6 ⊢
    linear_combination h6
  · -- even step:  P (2*(m+3))
    intro m IH
    set M : ℤ := (m:ℤ) + 3 with hMdef
    have hEM1 : normEDS b c d (2*M+2) * b = normEDS b c d M ^ 2 * normEDS b c d (M+1) * normEDS b c d (M+3) - normEDS b c d (M-1) * normEDS b c d (M+1) * normEDS b c d (M+2) ^ 2 := by
      have h := normEDS_even b c d (M+1)
      rw [show (2*(M+1):ℤ)=2*M+2 by ring, show ((M+1)-1:ℤ)=M by ring, show ((M+1)+2:ℤ)=M+3 by ring, show ((M+1)-2:ℤ)=M-1 by ring, show ((M+1)+1:ℤ)=M+2 by ring] at h
      exact h
    have hEMm1 : normEDS b c d (2*M-2) * b = normEDS b c d (M-2) ^ 2 * normEDS b c d (M-1) * normEDS b c d (M+1) - normEDS b c d (M-3) * normEDS b c d (M-1) * normEDS b c d M ^ 2 := by
      have h := normEDS_even b c d (M-1)
      rw [show (2*(M-1):ℤ)=2*M-2 by ring, show ((M-1)-1:ℤ)=M-2 by ring, show ((M-1)+2:ℤ)=M+1 by ring, show ((M-1)-2:ℤ)=M-3 by ring, show ((M-1)+1:ℤ)=M by ring] at h
      exact h
    have hEM : normEDS b c d (2*M) * b = normEDS b c d (M-1) ^ 2 * normEDS b c d M * normEDS b c d (M+2) - normEDS b c d (M-2) * normEDS b c d M * normEDS b c d (M+1) ^ 2 :=
      normEDS_even b c d M
    have hOM : normEDS b c d (2*M+1) = normEDS b c d (M+2) * normEDS b c d M ^ 3 - normEDS b c d (M-1) * normEDS b c d (M+1) ^ 3 :=
      normEDS_odd b c d M
    have hOMm1 : normEDS b c d (2*M-1) = normEDS b c d (M+1) * normEDS b c d (M-1) ^ 3 - normEDS b c d (M-2) * normEDS b c d M ^ 3 := by
      have h := normEDS_odd b c d (M-1)
      rw [show (2*(M-1)+1:ℤ)=2*M-1 by ring, show ((M-1)+2:ℤ)=M+1 by ring, show ((M-1)-1:ℤ)=M-2 by ring, show ((M-1)+1:ℤ)=M by ring] at h
      exact h
    have ihm1 : normEDS b c d (M+1) * normEDS b c d (M-3) = b^2 * normEDS b c d M * normEDS b c d (M-2) - c * normEDS b c d (M-1) ^ 2 := by
      have h := IH (m+2) (by omega)
      rw [show ((m+2:ℕ):ℤ)=M-1 by rw [hMdef]; push_cast; ring] at h
      rw [show (M-1+2:ℤ)=M+1 by ring, show (M-1-2:ℤ)=M-3 by ring, show (M-1+1:ℤ)=M by ring, show (M-1-1:ℤ)=M-2 by ring] at h
      exact h
    have ih0 : normEDS b c d (M+2) * normEDS b c d (M-2) = b^2 * normEDS b c d (M+1) * normEDS b c d (M-1) - c * normEDS b c d M ^ 2 := by
      have h := IH (m+3) (by omega)
      rw [show ((m+3:ℕ):ℤ)=M by rw [hMdef]; push_cast; ring] at h
      exact h
    have ih1 : normEDS b c d (M+3) * normEDS b c d (M-1) = b^2 * normEDS b c d (M+2) * normEDS b c d M - c * normEDS b c d (M+1) ^ 2 := by
      have h := IH (m+4) (by omega)
      rw [show ((m+4:ℕ):ℤ)=M+1 by rw [hMdef]; push_cast; ring] at h
      rw [show (M+1+2:ℤ)=M+3 by ring, show (M+1-2:ℤ)=M-1 by ring, show (M+1+1:ℤ)=M+2 by ring, show (M+1-1:ℤ)=M by ring] at h
      exact h
    have key0 := somos4_even_step_scaled b c d (normEDS b c d) M hEM1 hEMm1 hEM hOM hOMm1 ihm1 ih0 ih1
    have key := mul_left_cancel₀ (pow_ne_zero 2 hb) key0
    have e : ((2*(m+3):ℕ):ℤ) = 2*M := by rw [hMdef]; push_cast; ring
    rw [e]
    exact key
  · -- odd step:  P (2*(m+2)+1)
    intro m IH
    set M : ℤ := (m:ℤ) + 2 with hMdef
    have hOM1 : normEDS b c d (2*M+3) = normEDS b c d (M+3) * normEDS b c d (M+1) ^ 3 - normEDS b c d M * normEDS b c d (M+2) ^ 3 := by
      have h := normEDS_odd b c d (M+1)
      rw [show (2*(M+1)+1:ℤ)=2*M+3 by ring, show ((M+1)+2:ℤ)=M+3 by ring, show ((M+1)-1:ℤ)=M by ring, show ((M+1)+1:ℤ)=M+2 by ring] at h
      exact h
    have hEM1 : normEDS b c d (2*M+2) * b = normEDS b c d M ^ 2 * normEDS b c d (M+1) * normEDS b c d (M+3) - normEDS b c d (M-1) * normEDS b c d (M+1) * normEDS b c d (M+2) ^ 2 := by
      have h := normEDS_even b c d (M+1)
      rw [show (2*(M+1):ℤ)=2*M+2 by ring, show ((M+1)-1:ℤ)=M by ring, show ((M+1)+2:ℤ)=M+3 by ring, show ((M+1)-2:ℤ)=M-1 by ring, show ((M+1)+1:ℤ)=M+2 by ring] at h
      exact h
    have hEM : normEDS b c d (2*M) * b = normEDS b c d (M-1) ^ 2 * normEDS b c d M * normEDS b c d (M+2) - normEDS b c d (M-2) * normEDS b c d M * normEDS b c d (M+1) ^ 2 :=
      normEDS_even b c d M
    have hOM : normEDS b c d (2*M+1) = normEDS b c d (M+2) * normEDS b c d M ^ 3 - normEDS b c d (M-1) * normEDS b c d (M+1) ^ 3 :=
      normEDS_odd b c d M
    have hOMm1 : normEDS b c d (2*M-1) = normEDS b c d (M+1) * normEDS b c d (M-1) ^ 3 - normEDS b c d (M-2) * normEDS b c d M ^ 3 := by
      have h := normEDS_odd b c d (M-1)
      rw [show (2*(M-1)+1:ℤ)=2*M-1 by ring, show ((M-1)+2:ℤ)=M+1 by ring, show ((M-1)-1:ℤ)=M-2 by ring, show ((M-1)+1:ℤ)=M by ring] at h
      exact h
    have ih0 : normEDS b c d (M+2) * normEDS b c d (M-2) = b^2 * normEDS b c d (M+1) * normEDS b c d (M-1) - c * normEDS b c d M ^ 2 := by
      have h := IH (m+2) (by omega)
      rw [show ((m+2:ℕ):ℤ)=M by rw [hMdef]; push_cast; ring] at h
      exact h
    have ih1 : normEDS b c d (M+3) * normEDS b c d (M-1) = b^2 * normEDS b c d (M+2) * normEDS b c d M - c * normEDS b c d (M+1) ^ 2 := by
      have h := IH (m+3) (by omega)
      rw [show ((m+3:ℕ):ℤ)=M+1 by rw [hMdef]; push_cast; ring] at h
      rw [show (M+1+2:ℤ)=M+3 by ring, show (M+1-2:ℤ)=M-1 by ring, show (M+1+1:ℤ)=M+2 by ring, show (M+1-1:ℤ)=M by ring] at h
      exact h
    have key := somos4_odd_step b c d (normEDS b c d) M hOM1 hEM1 hEM hOM hOMm1 ih0 ih1
    have e : ((2*(m+2)+1:ℕ):ℤ) = 2*M+1 := by rw [hMdef]; push_cast; ring
    rw [e, show (2*M+1+2:ℤ)=2*M+3 by ring, show (2*M+1-2:ℤ)=2*M-1 by ring, show (2*M+1+1:ℤ)=2*M+2 by ring, show (2*M+1-1:ℤ)=2*M by ring]
    exact key

-- ── reflect to all ℤ over a domain ──
theorem somos4_dom_int [IsDomain R] (b c d : R) (hb : b ≠ 0) (m : ℤ) :
    normEDS b c d (m+2) * normEDS b c d (m-2)
      = b^2 * normEDS b c d (m+1) * normEDS b c d (m-1) - c * normEDS b c d m ^ 2 := by
  by_cases h : 0 ≤ m
  · obtain ⟨k, rfl⟩ : ∃ k : ℕ, (k:ℤ) = m := ⟨m.toNat, Int.toNat_of_nonneg h⟩
    exact somos4_dom b c d hb k
  · have hk : (0:ℤ) ≤ -m := by omega
    obtain ⟨k, hk2⟩ : ∃ k : ℕ, (k:ℤ) = -m := ⟨(-m).toNat, Int.toNat_of_nonneg hk⟩
    have base := somos4_dom b c d hb k
    have e2 : m + 2 = -((k:ℤ) - 2) := by omega
    have e1 : m + 1 = -((k:ℤ) - 1) := by omega
    have e0 : m = -((k:ℤ)) := by omega
    have em1 : m - 1 = -((k:ℤ) + 1) := by omega
    have em2 : m - 2 = -((k:ℤ) + 2) := by omega
    rw [e2, e1, em1, em2, e0]
    simp only [normEDS_neg]
    linear_combination base

-- ── transport to an arbitrary CommRing (identity, unconditional) ──
theorem somos4 {R : Type*} [CommRing R] (b c d : R) (m : ℤ) :
    normEDS b c d (m+2) * normEDS b c d (m-2)
      = b^2 * normEDS b c d (m+1) * normEDS b c d (m-1) - c * normEDS b c d m ^ 2 := by
  let f : MvPolynomial (Fin 3) ℤ →+* R :=
    MvPolynomial.eval₂Hom (Int.castRingHom R) ![b, c, d]
  have hX : (MvPolynomial.X 0 : MvPolynomial (Fin 3) ℤ) ≠ 0 := MvPolynomial.X_ne_zero 0
  have hdom := somos4_dom_int (MvPolynomial.X 0) (MvPolynomial.X 1) (MvPolynomial.X 2) hX m
  have := congrArg f hdom
  simp only [map_mul, map_sub, map_pow, map_normEDS] at this
  have hB : f (MvPolynomial.X 0) = b := by simp [f]
  have hC : f (MvPolynomial.X 1) = c := by simp [f]
  have hD : f (MvPolynomial.X 2) = d := by simp [f]
  rw [hB, hC, hD] at this
  linear_combination this
