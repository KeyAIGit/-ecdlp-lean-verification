import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# The `[n]`-numerator dominates its denominator (Route-B degree crux)

First reachable leaf of **Route B** for `deg[n] = n²` (`notes/SEPARABILITY_ROUTES.md`), the
elementary polynomial route to the `ψₙ ↔ E[n]` bridge that avoids the invariant-differential
theory. The `x`-coordinate of `[n]P` is the rational function `x ∘ [n] = Φₙ / ψₙ²`, where
Mathlib supplies the numerator `Φₙ` (monic, degree `n²`, `natDegree_Φ`/`leadingCoeff_Φ`) and
the denominator square `ΨSqₙ` (degree `n² − 1`, `natDegree_ΨSq`). The degree of a rational map
in lowest terms is the max of numerator and denominator degrees; here the **numerator strictly
dominates** (`n² − 1 < n²`), so once coprimality `gcd(Φₙ, ΨSqₙ) = 1` is established (node B1),
this pins `deg[n] = n²`. We record the two degree facts and the strict domination for
secp256k1. Needs the machine-checked primality of `p` (so `ZMod p` is a field — `NoZeroDivisors`,
`Nontrivial`); no new axioms.
-/

namespace Ecdlp.Curve

open Polynomial

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **N4 (numerator degree): `deg Φₙ = n²`.** The secp256k1 `[n]`-numerator `Φₙ` is monic of
degree `n²` (`natAbs n` squared), a direct instance of Mathlib's `natDegree_Φ`. -/
theorem secp256k1_Φ_natDegree (n : ℤ) :
    (secp256k1.Φ n).natDegree = n.natAbs ^ 2 :=
  secp256k1.natDegree_Φ n

/-- **Denominator-square degree: `deg ΨSqₙ = n² − 1`** (for `n ≠ 0` in `𝔽_p`). Instance of
Mathlib's `natDegree_ΨSq`; `ΨSqₙ` is the univariate reduction of `ψₙ²`. -/
theorem secp256k1_ΨSq_natDegree (n : ℤ) (hn : (n : ZMod Secp256k1.p) ≠ 0) :
    (secp256k1.ΨSq n).natDegree = n.natAbs ^ 2 - 1 :=
  secp256k1.natDegree_ΨSq hn

/-- **Route-B degree crux: the numerator strictly dominates the denominator.** For `n ≠ 0` in
`𝔽_p`, `deg ΨSqₙ = n² − 1 < n² = deg Φₙ`. Hence the rational map `x ∘ [n] = Φₙ / ψₙ²` attains
its degree at the numerator: with coprimality (node B1) this gives `deg[n] = n²` — the
differential-free route to the multiplication-by-`n` degree. -/
theorem secp256k1_ΨSq_natDegree_lt_Φ (n : ℤ) (hn : (n : ZMod Secp256k1.p) ≠ 0) :
    (secp256k1.ΨSq n).natDegree < (secp256k1.Φ n).natDegree := by
  rw [secp256k1_Φ_natDegree n, secp256k1_ΨSq_natDegree n hn]
  have hne : n ≠ 0 := by rintro rfl; exact hn (by simp)
  have hm : 0 < n.natAbs := Int.natAbs_pos.mpr hne
  have h1 : 1 ≤ n.natAbs ^ 2 := Nat.one_le_pow _ _ hm
  omega

end Ecdlp.Curve
