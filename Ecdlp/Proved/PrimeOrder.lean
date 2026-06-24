import Mathlib

/-!
# Prime-order subgroup structure

Why secp256k1 fixes the base-point order `n` to be prime: in a finite group of
prime order, every non-identity element has order equal to the whole group — it
generates it. Equivalently there are no nontrivial proper subgroups, so there is
no small subgroup for a Pohlig–Hellman / small-subgroup attack to exploit.

Supports the prime-order claims (e.g. `sec2-secp256k1-group-006`,
`teske-prime-order-proof-003`).
-/

namespace Ecdlp.Proved

/-- In a finite group of prime order, every non-identity element generates the
    group: `orderOf g = |G|`. -/
theorem orderOf_eq_card_of_prime {G : Type*} [Group G] [Fintype G]
    (hp : (Fintype.card G).Prime) {g : G} (hg : g ≠ 1) :
    orderOf g = Fintype.card G := by
  rcases hp.eq_one_or_self_of_dvd (orderOf g) orderOf_dvd_card with h | h
  · exact absurd (orderOf_eq_one_iff.mp h) hg
  · exact h

end Ecdlp.Proved
