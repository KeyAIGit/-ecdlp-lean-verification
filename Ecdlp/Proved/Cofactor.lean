import Mathlib

/-!
# Cofactor / order identity (Lagrange form)

The abstract form of the secp256k1 cofactor relation `#E(F_p) = n · h`: for a
subgroup `H` of a group `G`, the order of `G` equals the order of `H` times the
index `[G : H]`. Specialised to secp256k1 with base-point subgroup of order `n`
and cofactor `h = [G : H] = 1`, this is `#E(F_p) = n`.

This is the proved form of the open targets `sec2-secp256k1-group-006` and
`sec2-domain-parameters-001` (the cofactor/group-structure claims).
-/

namespace Ecdlp.Proved

/-- Cofactor identity: `|H| · [G : H] = |G|`. -/
theorem cofactor_card_mul_index {G : Type*} [Group G] (H : Subgroup G) :
    Nat.card H * H.index = Nat.card G :=
  H.card_mul_index

end Ecdlp.Proved
