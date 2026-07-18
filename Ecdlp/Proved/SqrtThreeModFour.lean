import Mathlib
import Ecdlp.Proved.Secp256k1Params
import Ecdlp.Proved.Secp256k1PrimeP

/-!
# Square roots in `𝔽_q` for `q ≡ 3 (mod 4)`, and the secp256k1 field congruences

For a prime `q` with `q ≡ 3 (mod 4)` and a square `a ∈ 𝔽_q`, the closed form
`√a = a^((q+1)/4)` really is a square root: `(a^((q+1)/4))² = a`. This is the arithmetic
behind point *decompression* on curves over such a field (recover `y` from `x` given the
sign bit), and secp256k1's `p ≡ 3 (mod 4)` is exactly what makes it available.

## Contents
* `sqrt_of_three_mod_four` — the general finite-field theorem, every hypothesis explicit.
* `p_mod_twelve`, `p_mod_three` — the secp256k1 residue facts (`p ≡ 7 mod 12`, `p ≡ 1 mod 3`);
  `p_mod_four : p % 4 = 3` is reused from `Ecdlp/Proved/Secp256k1Params.lean`.
* `secp256k1_sqrt_of_isSquare` — the specialization to `q = Secp256k1.p`.

## Proof of the general theorem
Write the square as `a = b * b`. Then, using only exponent laws,
`(a^((q+1)/4))² = b^(4·((q+1)/4)) = b^(q+1)` because `4 ∣ q+1` (from `q % 4 = 3`).
Finally `b^(q+1) = b^q · b = b · b = a` by the Frobenius/Fermat identity
`ZMod.pow_card : b^q = b`, which holds for *every* `b` (including `b = 0`), so no case split
on `a = 0` is needed. The `ℕ`-division fact `4·((q+1)/4) = q+1` is discharged by `omega` from
`q % 4 = 3`. The proof is kernel-pure (no `native_decide`, no axioms beyond Mathlib's).

The two secp256k1 congruences are p-scale numeric facts, proved by `native_decide` (the
existing TCB convention for such facts in this repository).
-/

namespace Ecdlp.Curve

/-- **Square roots for primes `q ≡ 3 (mod 4)`.** If `a : ZMod q` is a square, then
`a^((q+1)/4)` squares back to `a`. (`IsSquare 0` holds, and the `b = 0` case is covered
uniformly by `ZMod.pow_card`, so no separate zero hypothesis is required.)

Fermat/Frobenius step: `ZMod.pow_card` (`b^q = b`). -/
theorem sqrt_of_three_mod_four {q : ℕ} [Fact (Nat.Prime q)] (hq : q % 4 = 3)
    {a : ZMod q} (ha : IsSquare a) : (a ^ ((q + 1) / 4)) ^ 2 = a := by
  obtain ⟨b, rfl⟩ := ha
  have key : ((b * b) ^ ((q + 1) / 4)) ^ 2 = b ^ (q + 1) := by
    rw [← pow_two, ← pow_mul, ← pow_mul]
    congr 1
    omega
  rw [key, pow_succ, ZMod.pow_card]

/-- `p ≡ 7 (mod 12)` for the secp256k1 base-field prime. Implies both `p ≡ 3 (mod 4)`
and `p ≡ 1 (mod 3)`. -/
theorem p_mod_twelve : Secp256k1.p % 12 = 7 := by native_decide

/-- `p ≡ 1 (mod 3)`: the base field `𝔽_p` contains the primitive cube roots of unity
underlying the GLV endomorphism. -/
theorem p_mod_three : Secp256k1.p % 3 = 1 := by native_decide

/-- **secp256k1 square roots via `a^((p+1)/4)`.** Specialization of
`sqrt_of_three_mod_four` to `q = Secp256k1.p`, discharging `p % 4 = 3` with the reused
`p_mod_four`. This is the field identity behind secp256k1 point decompression. -/
theorem secp256k1_sqrt_of_isSquare {a : ZMod Secp256k1.p} (ha : IsSquare a) :
    (a ^ ((Secp256k1.p + 1) / 4)) ^ 2 = a :=
  sqrt_of_three_mod_four p_mod_four ha

end Ecdlp.Curve
