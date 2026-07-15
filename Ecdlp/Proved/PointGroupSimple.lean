import Mathlib
import Ecdlp.Proved.Secp256k1PrimeN
import Ecdlp.Proved.CurveCardinalityExact

/-!
# Structural security facts about the secp256k1 point group `E(𝔽_p)`

The rational-point group of secp256k1 is the additive group
`secp256k1.toAffine.Point`. Its exact order is the machine-checked prime `n`
(`Ecdlp.Curve.secp256k1_card_point_eq_n :
Nat.card secp256k1.toAffine.Point = Secp256k1.n`, with
`Ecdlp.Primality.secp256k1_n_prime` proving `n` prime). Because that order is
prime — equivalently, because secp256k1 has cofactor 1 — the point group has an
especially rigid structure: it admits no proper nontrivial subgroup, and every
nonzero point generates the whole group.

This is the point-group (curve) statement of small-subgroup / invalid-subgroup
attack resistance. It is the geometric counterpart of the scalar-ring fact
`Ecdlp.Curve.secp256k1_scalar_no_proper_subgroup` for `ℤ/n`, and is proved the
same way, with the only change being the cardinality bridge
(`secp256k1_card_point_eq_n` in place of `Nat.card_zmod`).
-/

namespace Ecdlp.Curve

/-- **secp256k1's prime-order point group has no proper nontrivial subgroup.**
Since `Nat.card secp256k1.toAffine.Point = n` is prime (cofactor 1), the only
additive subgroups of the rational-point group `E(𝔽_p)` are `⊥` and `⊤`.
Consequently there is no small-order subgroup — and no invalid-curve subgroup —
into which a point could be confined, closing off small-subgroup and
invalid-subgroup confinement attacks at the group level. -/
theorem secp256k1_point_group_no_proper_subgroup
    (H : AddSubgroup secp256k1.toAffine.Point) : H = ⊥ ∨ H = ⊤ := by
  haveI : Fact (Nat.card secp256k1.toAffine.Point).Prime :=
    ⟨by rw [secp256k1_card_point_eq_n]; exact Ecdlp.Primality.secp256k1_n_prime⟩
  exact H.eq_bot_or_eq_top_of_prime_card

/-- **Every nonzero point of secp256k1 generates the whole group.**
In the prime-order group `E(𝔽_p)`, any point `P ≠ 0` has `zmultiples P = ⊤`,
i.e. its cyclic subgroup is all of `E(𝔽_p)`. Every nonzero point is therefore a
valid full-order generator — a direct consequence of `#E(𝔽_p) = n` being prime. -/
theorem secp256k1_nonzero_point_generates
    (P : secp256k1.toAffine.Point) (hP : P ≠ 0) : AddSubgroup.zmultiples P = ⊤ := by
  rcases secp256k1_point_group_no_proper_subgroup (AddSubgroup.zmultiples P) with h | h
  · exact absurd (AddSubgroup.zmultiples_eq_bot.mp h) hP
  · exact h

/-- The secp256k1 point group `E(𝔽_p)` is a simple additive group: its only
additive subgroups are `⊥` and `⊤` (repackages
`secp256k1_point_group_no_proper_subgroup`). -/
instance : IsSimpleAddGroup secp256k1.toAffine.Point :=
  isSimpleAddGroup_of_prime_card (p := Secp256k1.n) secp256k1_card_point_eq_n

end Ecdlp.Curve
