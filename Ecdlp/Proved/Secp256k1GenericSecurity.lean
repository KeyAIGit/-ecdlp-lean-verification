import Mathlib
import Ecdlp.Proved.GenericGroupBound
import Ecdlp.Secp256k1Verified

/-!
# Generic-group security of secp256k1

Instantiating the generic-group lower bound (`Ecdlp.GenericGroup.generic_dlog_query_bound`)
at the secp256k1 group order `n` gives a machine-checked `> 2^127` lower bound on the
number of group operations any generic algorithm needs to solve the discrete log on
secp256k1: **≥ 128-bit security against generic attacks**.

The magnitude input `2^255 < n` is verified by `native_decide`. The primality of `n`
(a standard published fact — SEC 2) enters only as a hypothesis `[Fact n.Prime]`; it is
not an axiom, and a 256-bit primality is not brute-force decidable.
-/

namespace Ecdlp.GenericGroup

/-- `2^255 < n`: the secp256k1 group order exceeds `2^255` (machine-checked). -/
theorem two_pow_255_lt_secp256k1_n : 2 ^ 255 < Secp256k1.n := by native_decide

/-- **128-bit generic security of secp256k1.** Assuming the (standard, published)
primality of the group order `n`, any generic algorithm that solves the discrete
logarithm on secp256k1 for every challenge forms more than `2^127` group elements —
secp256k1 has ≥ 128-bit security against generic attacks. -/
theorem secp256k1_generic_security [Fact (Nat.Prime Secp256k1.n)]
    {q : ℕ} (F : Fin q → Aff Secp256k1.n)
    (hF : Function.Injective F)
    (hsolve : ∀ x : ZMod Secp256k1.n, ∃ i j, i ≠ j ∧ (F i).eval x = (F j).eval x) :
    2 ^ 127 < q := by
  have hnqq : Secp256k1.n ≤ q * q := generic_dlog_query_bound F hF hsolve
  by_contra hq
  push_neg at hq
  have h1 : q * q ≤ 2 ^ 254 := by
    calc q * q ≤ 2 ^ 127 * 2 ^ 127 := Nat.mul_le_mul hq hq
      _ = 2 ^ 254 := by ring
  have h2 : (2 : ℕ) ^ 254 < 2 ^ 255 := by norm_num
  have h3 : (2 : ℕ) ^ 255 < q * q := lt_of_lt_of_le two_pow_255_lt_secp256k1_n hnqq
  omega

end Ecdlp.GenericGroup
