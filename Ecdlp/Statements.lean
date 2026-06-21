/-
  ECDLP formalization targets (Mathlib-dependent). All proofs in this file are
  complete. Each theorem corresponds to a row of KG_CLAIM_FORMALIZATION_v1.csv
  with formal_status = "formalizable".
  Build: lake exe cache get && lake build
-/
import Mathlib

namespace Ecdlp.Targets

/-- [glv-subgroup-eigenvalue-006] Structural ZMod form of the GLV eigenvalue
    identity. If lam^2 + lam + 1 vanishes modulo n (the concrete secp256k1 fact
    proved by native_decide in Secp256k1Verified), then it vanishes in the
    commutative ring ZMod n. -/
theorem glv_eigenvalue_zmod (n lam : ℕ) (h : (lam ^ 2 + lam + 1) % n = 0) :
    ((lam : ZMod n) ^ 2 + (lam : ZMod n) + 1) = 0 := by
  have hd : n ∣ (lam ^ 2 + lam + 1) := Nat.dvd_of_mod_eq_zero h
  have hz : ((lam ^ 2 + lam + 1 : ℕ) : ZMod n) = 0 := by
    obtain ⟨k, hk⟩ := hd
    rw [hk]; push_cast; rw [ZMod.natCast_self]; ring
  push_cast at hz
  linear_combination hz

end Ecdlp.Targets
