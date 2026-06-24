import Mathlib
import Ecdlp.Secp256k1Verified
import Ecdlp.Proved.CubeRoot

/-!
# secp256k1 GLV factors have order exactly 3

Concrete instances of `Ecdlp.Proved.orderOf_eigenvalue_eq_three`: the field factor
`β ∈ 𝔽_p` and the scalar eigenvalue `λ ∈ ℤ/n` are both primitive cube roots of
unity (multiplicative order exactly 3) — the order-3 automorphism generating
secp256k1's GLV complex multiplication. Stated under the published primality of
`p` / `n` (a hypothesis, not an axiom).
-/

namespace Ecdlp.Curve

/-- secp256k1's field factor `β` has multiplicative order exactly 3 in `𝔽_p`. -/
theorem secp256k1_beta_orderOf [Fact (Nat.Prime Secp256k1.p)] :
    orderOf ((Secp256k1.beta : ZMod Secp256k1.p)) = 3 := by
  apply Ecdlp.Proved.orderOf_eigenvalue_eq_three
  · have h : ((Secp256k1.beta ^ 2 + Secp256k1.beta + 1 : ℕ) : ZMod Secp256k1.p) = 0 := by
      rw [ZMod.natCast_eq_zero_iff]
      exact Nat.dvd_of_mod_eq_zero Secp256k1.beta_field_eigenvalue
    push_cast at h
    linear_combination h
  · native_decide

/-- secp256k1's GLV eigenvalue `λ` has multiplicative order exactly 3 in `ℤ/n`. -/
theorem secp256k1_lambda_orderOf [Fact (Nat.Prime Secp256k1.n)] :
    orderOf ((Secp256k1.lam : ZMod Secp256k1.n)) = 3 := by
  apply Ecdlp.Proved.orderOf_eigenvalue_eq_three
  · have h : ((Secp256k1.lam ^ 2 + Secp256k1.lam + 1 : ℕ) : ZMod Secp256k1.n) = 0 := by
      rw [ZMod.natCast_eq_zero_iff]
      exact Nat.dvd_of_mod_eq_zero Secp256k1.glv_lambda_eigenvalue
    push_cast at h
    linear_combination h
  · native_decide

end Ecdlp.Curve
