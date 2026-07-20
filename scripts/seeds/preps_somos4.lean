  -- normEDS at (Ψ₂Sq, Ψ₃, preΨ₄) is preΨ twisted by the parity factor:
  -- normEDS b c d n = preNormEDS (b^2) c d n * (Even n ? b : 1), and preΨ = preNormEDS (Ψ₂Sq^2) Ψ₃ preΨ₄.
  have hM : ∀ n : ℤ, normEDS secp256k1.Ψ₂Sq secp256k1.Ψ₃ secp256k1.preΨ₄ n
             = secp256k1.preΨ n * (if Even n then secp256k1.Ψ₂Sq else 1) := by
    intro n
    simp only [normEDS, WeierstrassCurve.preΨ]
  have hs := Ecdlp.NormEDS.normEDS_somos4 secp256k1.Ψ₂Sq secp256k1.Ψ₃ secp256k1.preΨ₄ m
  rw [hM (m + 2), hM (m - 2), hM (m + 1), hM (m - 1), hM m] at hs
  have hBne : secp256k1.Ψ₂Sq ≠ 0 := secp256k1_Ψ₂Sq_ne_zero
  have p2 : Even (m + 2) ↔ Even m := by simp [Int.even_add]
  have p2' : Even (m - 2) ↔ Even m := by simp [Int.even_sub]
  have p1 : Even (m + 1) ↔ ¬ Even m := by simp [Int.even_add_one]
  have p1' : Even (m - 1) ↔ ¬ Even m := by
    rw [Int.even_sub]; simp
  by_cases hm : Even m
  · simp only [p2, p2', p1, p1', hm, iff_true, iff_false, not_true, ↓reduceIte] at hs
    simp only [hm, ↓reduceIte]
    apply mul_left_cancel₀ (pow_ne_zero 2 hBne)
    linear_combination hs
  · simp only [p2, p2', p1, p1', hm, iff_false, iff_true, not_false_iff, ↓reduceIte] at hs
    simp only [hm, ↓reduceIte]
    linear_combination hs
