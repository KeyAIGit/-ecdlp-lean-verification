import Mathlib
import Ecdlp.Proved.Secp256k1PMinusOneSmoothness

/-!
# The finite PKC M16 x-coordinate factor base

For the secp256k1 prime field, the source-faithful smooth-subgroup membership
equation is `x ^ 564522 = 1`.  This file packages its solution type and proves
that it has exactly `564522` elements.

The proof uses only the already-certified factorization of `p - 1`: since
`564522 ∣ p - 1`, the standard Mathlib roots-of-unity instance for `ZMod p`
contains all `564522`-th roots.  This is a finite-field cardinality statement,
not a claim that every such x-coordinate lifts to a secp256k1 point.
-/

namespace Ecdlp.M16FactorBaseFinite

/-- The complete x-coordinate root set selected by the M16 membership equation.

This is intentionally an x-coordinate type.  No curve-lift witness is part of
the subtype. -/
abbrev FactorBaseX :=
  {x : ZMod Secp256k1.p // x ^ 564522 = 1}

noncomputable instance : Fintype FactorBaseX := Fintype.ofFinite FactorBaseX

private theorem factorBaseDegree_dvd_p_sub_one :
    564522 ∣ Secp256k1.p - 1 := by
  rw [Ecdlp.Curve.secp256k1_p_sub_one_factorization,
    Ecdlp.Curve.secp256k1_p_sub_one_smooth_part_value]
  exact dvd_mul_right 564522 Ecdlp.Curve.pMinusOneCofactor

private noncomputable def factorBaseXEquivRootsOfUnity :
    FactorBaseX ≃ ↥(rootsOfUnity 564522 (ZMod Secp256k1.p)) where
  toFun x := rootsOfUnity.mkOfPowEq x.1 x.2
  invFun x :=
    ⟨(x.1 : ZMod Secp256k1.p), by
      simpa only [Units.val_pow_eq_pow_val, Units.val_one] using
        congrArg (fun u : (ZMod Secp256k1.p)ˣ => (u : ZMod Secp256k1.p)) x.2⟩
  left_inv x := by
    apply Subtype.ext
    exact rootsOfUnity.coe_mkOfPowEq x.2
  right_inv x := by
    apply rootsOfUnity.coe_injective
    exact rootsOfUnity.coe_mkOfPowEq _

/-- The M16 smooth-subgroup membership equation has exactly `D = 564522`
solutions in the secp256k1 prime field. -/
theorem card_factorBaseX : Fintype.card FactorBaseX = 564522 := by
  have hp_sub_one_ne : Secp256k1.p - 1 ≠ 0 :=
    Nat.sub_ne_zero_of_lt Ecdlp.Primality.secp256k1_p_prime.one_lt
  letI : NeZero (Secp256k1.p - 1) := ⟨hp_sub_one_ne⟩
  letI : HasEnoughRootsOfUnity (ZMod Secp256k1.p) 564522 :=
    HasEnoughRootsOfUnity.of_dvd (ZMod Secp256k1.p)
      factorBaseDegree_dvd_p_sub_one
  rw [← Nat.card_eq_fintype_card,
    Nat.card_congr factorBaseXEquivRootsOfUnity]
  exact HasEnoughRootsOfUnity.natCard_rootsOfUnity
    (ZMod Secp256k1.p) 564522

end Ecdlp.M16FactorBaseFinite
