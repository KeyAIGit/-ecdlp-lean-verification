import Mathlib

/-!
# UORC-056 all-residue completion boundary

This file kernel-checks the elementary/index and exact-integer pieces of V11.
The analytic input

  |sum_{Q in H} omega(Q) chi(psi_3(Q))| <= 8 * sqrt(p)

is Shparlinski--Stange Lemma 5 specialized to the degree-four function
`psi_3`; that character-sum theorem is source-locked in the V11 note rather
than re-formalized in Lean.

The crucial machine certificate below is entirely integral:

  floor((n-1)/3)^2 > 2064^2 * p

for the public secp256k1 parameters.  Therefore the necessary completion bound
`floor((n-1)/3) <= 2064*sqrt(p)` cannot hold.
-/

namespace Ecdlp.EdsAllResidueCompletion

/-- The public secp256k1 base-field prime. -/
def secpP : ℕ :=
  115792089237316195423570985008687907853269984665640564039457584007908834671663

/-- The public secp256k1 prime subgroup order. -/
def secpN : ℕ :=
  115792089237316195423570985008687907852837564279074904382605163141518161494337

/-- Length of the initial block forced to `chi(psi_3([k]P))=+1` by an
all-residue EDS row. -/
def secpBlock : ℕ := (secpN - 1) / 3

/-- Deliberately coarse completion constant:
`8 * (2 + ln((n-1)/2)) < 8 * 258 = 2064` because `n < 2^256` and
`ln 2 < 1`. -/
def coarseCompletionConstant : ℕ := 2064

/-- If `k <= floor((n-1)/3)`, then the chain-rule index `3k` still lies below
`n`; hence both EDS residue signs are part of the assumed nonzero row. -/
theorem triple_le_order_sub_one
    (n k : ℕ)
    (hk : k ≤ (n - 1) / 3) :
    3 * k ≤ n - 1 := by
  omega

/-- Exact secp256k1 integer certificate. No floating-point approximation or
unproved square-root comparison enters this theorem. -/
theorem secpBlock_square_exceeds_completion_square :
    coarseCompletionConstant ^ 2 * secpP < secpBlock ^ 2 := by
  native_decide

/-- The same certificate written with the literal squared constant used by the
Python replay. -/
theorem secpBlock_square_exceeds_4260096_mul_p :
    4260096 * secpP < secpBlock ^ 2 := by
  native_decide

/-- Therefore any premise asserting the opposite integer square bound is
inconsistent with the fixed public parameters. -/
theorem no_secp_coarse_squared_completion_bound :
    ¬ secpBlock ^ 2 ≤ coarseCompletionConstant ^ 2 * secpP := by
  exact Nat.not_le_of_lt secpBlock_square_exceeds_completion_square

end Ecdlp.EdsAllResidueCompletion
