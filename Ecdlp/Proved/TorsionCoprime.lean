import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# Odd torsion meets 2-torsion trivially (a reachable leaf of the `ψₙ ↔ E[n]` bridge)

This is node **N12** of the division-polynomial ↔ torsion dependency map
(`notes/DIVISION_POLY_TORSION_MAP.md`): the elementary group-theoretic bookkeeping that
underlies the classical correspondence. For odd `n`, an `n`-torsion point that is also
2-torsion must be the identity — because its order divides both `n` and `2`, hence divides
`gcd(n, 2) = 1`. It is one of the LEAF nodes reachable *now* (pure finite-group theory over
the existing point group), independent of the CORE items (separability of `[n]`, `#E[n]=n²`)
that remain barriers. Needs only the machine-checked primality of `p` (for the point group);
no new axioms.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Odd torsion ∩ 2-torsion = {O}.** If `n` is odd and `P` is killed by both `n` and `2`,
then `P = O`: `addOrderOf P` divides `gcd(n, 2) = 1`. The `E[n] ∩ E[2] = {O}` bookkeeping
(bridge-map node N12) that lets odd division polynomials ignore the 2-torsion. -/
theorem secp256k1_odd_two_torsion_disjoint {n : ℕ} (hodd : Odd n)
    (P : secp256k1.toAffine.Point) (hn : n • P = 0) (h2 : (2 : ℕ) • P = 0) :
    P = 0 := by
  have hdn : addOrderOf P ∣ n := addOrderOf_dvd_of_nsmul_eq_zero hn
  have hd2 : addOrderOf P ∣ 2 := addOrderOf_dvd_of_nsmul_eq_zero h2
  have hcop : Nat.gcd n 2 = 1 := (Nat.coprime_two_right_iff_odd).mpr hodd
  have h1 : addOrderOf P ∣ 1 := hcop ▸ Nat.dvd_gcd hdn hd2
  rw [← addOrderOf_eq_one_iff]
  exact Nat.dvd_one.mp h1

end Ecdlp.Curve
