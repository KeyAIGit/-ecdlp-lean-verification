import Ecdlp.Proved.PrePsiSomos4
import Ecdlp.Proved.PrePsiPlusCompanion

/-!
# Candidate: the `ΨSq` half of the N7 even-x wall

This seed replaces the incomplete recursive parity expansion in
`scripts/seeds/n7_even_x_psisq.lean`.  For

* `U = preΨ(m - 1)^2 * preΨ(m + 2)`,
* `V = preΨ(m - 2) * preΨ(m + 1)^2`, and
* `T = preΨ(m + 1) * preΨ(m - 1)`,

the doubling recurrence gives `preΨ(2m) = preΨ(m) * (U - V)`.  The proof
uses the finite decomposition

`(U - V)^2 = (U + V)^2 - 4 * U * V`.

The plus-companion theorem supplies `U + V`, while Somos-4 supplies
`U * V`.  After those two substitutions, each parity branch is a small
ring identity using the concrete secp256k1 parameters.

This file is an isolated candidate.  It is not imported by `Ecdlp.lean`.
-/

open Polynomial WeierstrassCurve

namespace Ecdlp.Curve

variable [Fact (Nat.Prime Secp256k1.p)]

/-- Polynomial doubling identity needed for the denominator half of
`N7Uniform.even_x_algebra`.  Evaluation at any `x` gives the wall's
`ΨSq(2k)` identity. -/
theorem n7_even_x_ΨSq_companion_candidate (m : ℤ) :
    secp256k1.ΨSq (2 * m) =
      4 * secp256k1.ΨSq m *
        (secp256k1.Φ m ^ 3 + 7 * secp256k1.ΨSq m ^ 3) := by
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

  have hsomos :
      P (m + 2) * P (m - 2) =
        (if Even m then 1 else B ^ 2) * P (m + 1) * P (m - 1) - C * P m ^ 2 := by
    simpa only [P, B, C] using secp256k1_preΨ_somos4 m

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
        dsimp [T]
        ring

  have hdifference :
      (U - V) ^ 2 = (U + V) ^ 2 - 4 * (U * V) := by
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
      B * (U - V) ^ 2 =
        4 * (if Even m then B else 1) *
          ((X * (P m ^ 2 * (if Even m then B else 1))
                - T * (if Even m then 1 else B)) ^ 3
            + 7 * (P m ^ 2 * (if Even m then B else 1)) ^ 3) := by
    rw [hdifference, hplus, hproduct]
    by_cases hm : Even m
    · simp only [hm, ↓reduceIte]
      rw [hB, hC]
      ring
    · simp only [hm, ↓reduceIte]
      rw [hB, hC]
      ring

  have h2m : Even (2 * m) := ⟨m, by ring⟩
  change S (2 * m) = 4 * S m * (F m ^ 3 + 7 * S m ^ 3)
  rw [hS (2 * m), if_pos h2m, hdouble, hF m, hS m]
  dsimp [U, V, T] at hcore ⊢
  linear_combination P m ^ 2 * hcore

end Ecdlp.Curve
