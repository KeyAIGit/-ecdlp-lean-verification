import Mathlib

/-!
# The Somos-4 recurrence for `normEDS` (the `n = 2` slice of Ward's theorem)

Mathlib defines `normEDS b c d : ℤ → R` and leaves open the TODO that it satisfies
`IsEllSequence` — equivalently the single master recurrence

`normEDS (m+n) * normEDS (m-n) = normEDS (m+1) * normEDS (m-1) * normEDS n ^ 2`
`                              - normEDS (n+1) * normEDS (n-1) * normEDS m ^ 2`   (★)

(with `isEllSequence_of_rec_one`, already in `Ecdlp/Proved/EllSequenceRecOne.lean`,
reducing the general `IsEllSequence` to the `n = 1` case of (★)).

This file proves the `n = 2` specialisation of (★) — the **Somos-4 slice** —

`normEDS (m+2) * normEDS (m-2) = b^2 * normEDS (m+1) * normEDS (m-1) - c * normEDS m ^ 2`

for every `m : ℤ` and over an arbitrary `CommRing R`. It is the scoped warm-up and the
companion identity for the full Ward induction: a single-parameter strong induction on
`m` via `normEDSRec'`, whose even branch clears the `* b` factor of `normEDS_even` in the
integral domain `MvPolynomial (Fin 3) ℤ` and then transports to any `CommRing` by the
evaluation hom together with `map_normEDS`.

The two `linear_combination` certificates for the odd/even inductive steps were designed
against a free sequence `W : ℤ → R` (so they match a symbolic-algebra cross-check exactly)
and are stated as the auxiliary lemmas below.
-/

namespace Ecdlp.NormEDS

variable {R : Type*} [CommRing R]

/-- Odd inductive step of the Somos-4 slice, phrased over a free sequence `W`. -/
private theorem somos4_odd_step (b c : R) (W : ℤ → R) (M : ℤ)
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

/-- Even inductive step of the Somos-4 slice, scaled by `b ^ 2`, phrased over a free `W`. -/
private theorem somos4_even_step_scaled (b c : R) (W : ℤ → R) (M : ℤ)
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

/-- The Somos-4 slice over an integral domain with `b ≠ 0`, for natural indices `n`. -/
private theorem somos4_dom [IsDomain R] (b c d : R) (hb : b ≠ 0) (n : ℕ) :
    normEDS b c d ((n:ℤ)+2) * normEDS b c d ((n:ℤ)-2)
      = b^2 * normEDS b c d ((n:ℤ)+1) * normEDS b c d ((n:ℤ)-1) - c * normEDS b c d (n:ℤ) ^ 2 := by
  refine normEDSRec'
    (P := fun k : ℕ => normEDS b c d ((k:ℤ)+2) * normEDS b c d ((k:ℤ)-2)
      = b^2 * normEDS b c d ((k:ℤ)+1) * normEDS b c d ((k:ℤ)-1) - c * normEDS b c d (k:ℤ) ^ 2)
    ?_ ?_ ?_ ?_ ?_ ?_ ?_ n
  · norm_num; ring
  · norm_num
  · norm_num; ring
  · have h5 := normEDS_odd b c d 2
    norm_num at h5 ⊢
    linear_combination h5
  · have h6 := normEDS_even b c d 3
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
    have key0 := somos4_even_step_scaled b c (normEDS b c d) M hEM1 hEMm1 hEM hOM hOMm1 ihm1 ih0 ih1
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
    have key := somos4_odd_step b c (normEDS b c d) M hOM1 hEM1 hEM hOM hOMm1 ih0 ih1
    have e : ((2*(m+2)+1:ℕ):ℤ) = 2*M+1 := by rw [hMdef]; push_cast; ring
    rw [e, show (2*M+1+2:ℤ)=2*M+3 by ring, show (2*M+1-2:ℤ)=2*M-1 by ring, show (2*M+1+1:ℤ)=2*M+2 by ring, show (2*M+1-1:ℤ)=2*M by ring]
    exact key

/-- The Somos-4 slice over an integral domain with `b ≠ 0`, for all integer indices. -/
private theorem somos4_dom_int [IsDomain R] (b c d : R) (hb : b ≠ 0) (m : ℤ) :
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

/-- **Somos-4 recurrence for `normEDS`** — the `n = 2` slice of Ward's master recurrence,
over an arbitrary `CommRing`, for every integer `m`. This is the companion identity for
the full `IsEllSequence (normEDS b c d)` induction (the open Mathlib TODO). -/
theorem normEDS_somos4 {R : Type*} [CommRing R] (b c d : R) (m : ℤ) :
    normEDS b c d (m+2) * normEDS b c d (m-2)
      = b^2 * normEDS b c d (m+1) * normEDS b c d (m-1) - c * normEDS b c d m ^ 2 := by
  let f : MvPolynomial (Fin 3) ℤ →+* R :=
    MvPolynomial.eval₂Hom (Int.castRingHom R) ![b, c, d]
  have hX : (MvPolynomial.X 0 : MvPolynomial (Fin 3) ℤ) ≠ 0 := MvPolynomial.X_ne_zero 0
  have hdom := somos4_dom_int (MvPolynomial.X 0) (MvPolynomial.X 1) (MvPolynomial.X 2) hX m
  have hmap := congrArg f hdom
  simp only [map_mul, map_sub, map_pow, map_normEDS] at hmap
  have hB : f (MvPolynomial.X 0) = b := by simp [f]
  have hC : f (MvPolynomial.X 1) = c := by simp [f]
  have hD : f (MvPolynomial.X 2) = d := by simp [f]
  rw [hB, hC, hD] at hmap
  linear_combination hmap

end Ecdlp.NormEDS
