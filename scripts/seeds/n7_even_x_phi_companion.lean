import Ecdlp.Proved.PrePsiSomos4
import Ecdlp.Proved.PrePsiPlusCompanion

/-!
# Candidate: the `Φ` half of the N7 even-x wall

For

* `U = preΨ(m - 1)^2 * preΨ(m + 2)`,
* `V = preΨ(m - 2) * preΨ(m + 1)^2`, and
* `T = preΨ(m + 1) * preΨ(m - 1)`,

the even recurrence gives `preΨ(2m) = preΨ(m) * (U - V)`.  The two odd
recurrences give a finite formula for
`preΨ(2m + 1) * preΨ(2m - 1)`.  Its only wider-index terms are `U + V`,
`U * V`, and `preΨ(m + 2) * preΨ(m - 2)`, supplied respectively by the
plus-companion identity and Somos-4.  The remaining two parity branches are
ring identities using the concrete secp256k1 parameters.

This file is an isolated candidate.  It is not imported by `Ecdlp.lean`.
-/

open Polynomial WeierstrassCurve

namespace Ecdlp.Curve

variable [Fact (Nat.Prime Secp256k1.p)]

/-- Polynomial doubling identity needed for the numerator half of
`N7Uniform.even_x_algebra`.  Evaluation at any `x` gives the wall's
`Φ(2k)` identity. -/
theorem n7_even_x_Φ_companion_candidate (m : ℤ) :
    secp256k1.Φ (2 * m) =
      secp256k1.Φ m ^ 4
        - 56 * secp256k1.Φ m * secp256k1.ΨSq m ^ 3 := by
  let P : ℤ → Polynomial (ZMod Secp256k1.p) := secp256k1.preΨ
  let S : ℤ → Polynomial (ZMod Secp256k1.p) := secp256k1.ΨSq
  let F : ℤ → Polynomial (ZMod Secp256k1.p) := secp256k1.Φ
  let B : Polynomial (ZMod Secp256k1.p) := secp256k1.Ψ₂Sq
  let C : Polynomial (ZMod Secp256k1.p) := secp256k1.Ψ₃
  let U : Polynomial (ZMod Secp256k1.p) := P (m - 1) ^ 2 * P (m + 2)
  let V : Polynomial (ZMod Secp256k1.p) := P (m - 2) * P (m + 1) ^ 2
  let T : Polynomial (ZMod Secp256k1.p) := P (m + 1) * P (m - 1)

  have hS : ∀ n : ℤ, S n = P n ^ 2 * (if Even n then B else 1) := fun _ => rfl
  have hF : ∀ n : ℤ,
      F n = X * S n - P (n + 1) * P (n - 1) * (if Even n then 1 else B) :=
    fun _ => rfl

  have hdouble : P (2 * m) = P m * (U - V) := by
    have h := secp256k1.preΨ_even m
    dsimp [P, U, V]
    linear_combination h

  have hoddPlus :
      P (2 * m + 1) =
        P (m + 2) * P m ^ 3 * (if Even m then B ^ 2 else 1)
          - P (m - 1) * P (m + 1) ^ 3 * (if Even m then 1 else B ^ 2) := by
    have h := secp256k1.preΨ_odd m
    dsimp [P, B]
    convert h using 2 <;> ring

  have hoddMinus :
      P (2 * m - 1) =
        P (m + 1) * P (m - 1) ^ 3 * (if Even (m - 1) then B ^ 2 else 1)
          - P (m - 2) * P m ^ 3 * (if Even (m - 1) then 1 else B ^ 2) := by
    have h := secp256k1.preΨ_odd (m - 1)
    dsimp [P, B]
    convert h using 2 <;> ring

  have hsomos :
      P (m + 2) * P (m - 2) =
        (if Even m then 1 else B ^ 2) * T - C * P m ^ 2 := by
    have h := secp256k1_preΨ_somos4 m
    dsimp [P, B, C, T] at h ⊢
    linear_combination h

  have hplus :
      U + V =
        6 * X ^ 2 * P m * T - (if Even m then B ^ 2 else 1) * P m ^ 3 := by
    have h := secp256k1_preΨ_plus_companion m
    dsimp [P, B, U, V, T]
    linear_combination h

  have hproduct :
      U * V =
        ((if Even m then 1 else B ^ 2) * T - C * P m ^ 2) * T ^ 2 := by
    calc
      U * V = (P (m + 2) * P (m - 2)) * T ^ 2 := by
        dsimp [U, V, T]
        ring
      _ = ((if Even m then 1 else B ^ 2) * T - C * P m ^ 2) * T ^ 2 := by
        rw [hsomos]

  have hdifference :
      (U - V) ^ 2 = (U + V) ^ 2 - 4 * (U * V) := by
    ring

  have hoddProduct :
      P (2 * m + 1) * P (2 * m - 1) =
        B ^ 2 * P m ^ 3 * T * (U + V)
          - (if Even m then B ^ 4 else 1) * P m ^ 6
              * (P (m + 2) * P (m - 2))
          - (if Even m then 1 else B ^ 4) * T ^ 4 := by
    rw [hoddPlus, hoddMinus]
    by_cases hm : Even m
    · have hm1 : ¬ Even (m - 1) := by
        intro h
        obtain ⟨r, hr⟩ := hm
        obtain ⟨s, hs⟩ := h
        omega
      simp only [hm, hm1, ↓reduceIte]
      dsimp [U, V, T]
      ring
    · have hm1 : Even (m - 1) := by
        rcases Int.even_or_odd m with he | ho
        · exact absurd he hm
        · obtain ⟨r, hr⟩ := ho
          exact ⟨r, by omega⟩
      simp only [hm, hm1, ↓reduceIte]
      dsimp [U, V, T]
      ring

  have hB : B = 4 * X ^ 3 + 28 := by
    dsimp [B]
    rw [secp256k1_Ψ₂Sq]
    simp only [map_ofNat]

  have hC : C = 3 * X ^ 4 + 84 * X := by
    dsimp [C]
    rw [secp256k1_Ψ₃]
    simp only [map_ofNat]
    ring

  have hcore :
      X * ((P m * (U - V)) ^ 2 * B)
          - P (2 * m + 1) * P (2 * m - 1)
        =
      (X * (P m ^ 2 * (if Even m then B else 1))
            - T * (if Even m then 1 else B)) ^ 4
          - 56
            * (X * (P m ^ 2 * (if Even m then B else 1))
                - T * (if Even m then 1 else B))
             * (P m ^ 2 * (if Even m then B else 1)) ^ 3 := by
    rw [show (P m * (U - V)) ^ 2 = P m ^ 2 * (U - V) ^ 2 by ring]
    rw [hoddProduct, hsomos, hdifference, hplus, hproduct]
    by_cases hm : Even m
    · simp only [hm, ↓reduceIte]
      rw [hB, hC]
      ring
    · simp only [hm, ↓reduceIte]
      rw [hB, hC]
      ring

  have h2m : Even (2 * m) := ⟨m, by ring⟩
  change F (2 * m) = F m ^ 4 - 56 * F m * S m ^ 3
  rw [hF (2 * m), hS (2 * m), hdouble, hF m, hS m]
  simp only [if_pos h2m]
  dsimp [T] at hcore ⊢
  exact hcore

end Ecdlp.Curve
