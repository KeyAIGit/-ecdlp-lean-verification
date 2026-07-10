import Mathlib
import Ecdlp.Proved.CurveCardinality

/-!
# secp256k1: the strong keystone `#E = n`, reduced to exactly the Hasse bound (conditional)

The **interval-uniqueness** piece (piece 3 of the certificate route, `notes/HASSE_RECON.md`),
made a fully machine-checked conditional theorem. Together with the proved `n ∣ #E`
(`secp256k1_n_dvd_card_point`, piece 1) it collapses the strong keystone to a **single** missing
input — the Hasse upper bound — with every other step in the Lean kernel.

`secp256k1_card_eq_n_of_hasse` takes the (integer form of the) Hasse bound as a hypothesis
`(p + 1 − #E)² ≤ 4p` and concludes `#E = n`. The proof: `#E` is a positive multiple `k·n` of the
base-point order `n` (piece 1 + finiteness); the two concrete integer facts `2n > p+1` and
`(2n − p − 1)² > 4p` (`native_decide`) force `k = 1`, since any `k ≥ 2` gives `#E ≥ 2n > p+1` and
hence `(p+1−#E)² = (#E−p−1)² ≥ (2n−p−1)² > 4p`, contradicting the hypothesis.

So the **only** thing between this repo and the strong keystone `#E(𝔽_p) = n` (cofactor 1) is a
proof of `(p+1−#E)² ≤ 4p` — the Hasse bound, absent from Mathlib v4.31 (a multi-month,
research-grade port: Frobenius on the Tate module + a positivity bound). This file proves
everything else. The two arithmetic facts trust the Lean compiler (`native_decide`,
`TRUST_REPORT.md`); the reduction structure is pure-kernel.
-/

open WeierstrassCurve.Affine

namespace Ecdlp.Curve

/-- **Strong keystone, modulo Hasse.** If the integer Hasse bound `(p + 1 − #E)² ≤ 4p` holds for
secp256k1, then `#E(𝔽_p) = n` (cofactor 1). Combined with the proved `n ∣ #E`, this isolates the
Hasse bound as the sole remaining input to the strong keystone; all else is kernel-checked. -/
theorem secp256k1_card_eq_n_of_hasse
    (h : ((Secp256k1.p : ℤ) + 1 - (Nat.card secp256k1.toAffine.Point : ℤ)) ^ 2
          ≤ 4 * (Secp256k1.p : ℤ)) :
    Nat.card secp256k1.toAffine.Point = Secp256k1.n := by
  haveI : Nonempty secp256k1.toAffine.Point := ⟨0⟩
  have hpos : 0 < Nat.card secp256k1.toAffine.Point := Nat.card_pos
  have hn_pos : 0 < Secp256k1.n := by native_decide
  obtain ⟨k, hk⟩ := secp256k1_n_dvd_card_point
  -- `k ≥ 1`, since `#E = n · k > 0` and `n > 0`.
  have hk_pos : 0 < k := by
    rcases Nat.eq_zero_or_pos k with h0 | h0
    · rw [h0, Nat.mul_zero] at hk; omega
    · exact h0
  -- The two concrete integer facts pinning the interval (compiler-evaluated).
  have hA : (Secp256k1.p : ℤ) + 1 < 2 * (Secp256k1.n : ℤ) := by native_decide
  have hB : 4 * (Secp256k1.p : ℤ) < (2 * (Secp256k1.n : ℤ) - Secp256k1.p - 1) ^ 2 := by
    native_decide
  -- Either `k = 1` (done) or `k ≥ 2` (contradiction with the Hasse hypothesis).
  rcases Nat.lt_or_ge k 2 with hk2 | hk2
  · interval_cases k
    · simp [hk]
  · exfalso
    -- `#E = n · k ≥ 2n`.
    have hN2 : 2 * (Secp256k1.n : ℤ) ≤ (Nat.card secp256k1.toAffine.Point : ℤ) := by
      have : (Nat.card secp256k1.toAffine.Point : ℤ) = (Secp256k1.n : ℤ) * (k : ℤ) := by
        rw [hk]; push_cast; ring
      rw [this]
      have hk2' : (2 : ℤ) ≤ (k : ℤ) := by exact_mod_cast hk2
      nlinarith [hn_pos, hk2']
    -- `#E - p - 1 ≥ 2n - p - 1 > 0`, so squaring is monotone and beats `4p`.
    nlinarith [h, hA, hB, hN2,
      mul_nonneg (by linarith : (0 : ℤ) ≤ (Nat.card secp256k1.toAffine.Point : ℤ) - 2 * Secp256k1.n)
        (by linarith : (0 : ℤ) ≤ (Nat.card secp256k1.toAffine.Point : ℤ) + 2 * Secp256k1.n
              - 2 * Secp256k1.p - 2)]

end Ecdlp.Curve
