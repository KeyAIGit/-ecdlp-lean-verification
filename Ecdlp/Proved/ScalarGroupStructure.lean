import Mathlib
import Ecdlp.Proved.Secp256k1PrimeN

/-!
# Structural security facts about the secp256k1 scalar group `ℤ/n`

The scalar group of secp256k1 is the additive group `ZMod Secp256k1.n`, where
`n` is the (machine-checked prime, `Ecdlp.Primality.secp256k1_n_prime`) order of
the base point. Because `n` is prime, this group has an especially rigid
structure, which is exactly what rules out several classes of attacks.
-/

namespace Ecdlp.Curve

/-- **secp256k1's prime-order scalar group has no proper nontrivial subgroup.**
Since `Nat.card (ZMod n) = n` is prime, the only additive subgroups of the scalar
group `ℤ/n` are `⊥` and `⊤`. Consequently there is no small-order subgroup (and no
invalid-curve subgroup) into which a private key could be confined, closing off
small-subgroup / invalid-subgroup confinement attacks. -/
theorem secp256k1_scalar_no_proper_subgroup (H : AddSubgroup (ZMod Secp256k1.n)) :
    H = ⊥ ∨ H = ⊤ := by
  haveI : Fact (Nat.card (ZMod Secp256k1.n)).Prime :=
    ⟨by rw [Nat.card_zmod]; exact Ecdlp.Primality.secp256k1_n_prime⟩
  exact H.eq_bot_or_eq_top_of_prime_card

/-- **Every nonzero scalar generates: there are exactly `n − 1` full-order private keys.**
In the cyclic group `ℤ/n` with `n` prime, the number of elements of additive order
exactly `n` equals Euler's totient `φ(n) = n − 1`. Every one of the `n − 1` nonzero
scalars is therefore a generator, i.e. a valid full-order private key. -/
theorem secp256k1_scalar_num_generators :
    (Finset.univ.filter (fun a : ZMod Secp256k1.n => addOrderOf a = Secp256k1.n)).card
      = Secp256k1.n - 1 := by
  haveI : NeZero Secp256k1.n := ⟨Ecdlp.Primality.secp256k1_n_prime.pos.ne'⟩
  rw [IsAddCyclic.card_addOrderOf_eq_totient (d := Secp256k1.n) (by rw [ZMod.card]),
      Nat.totient_prime Ecdlp.Primality.secp256k1_n_prime]

/-- The secp256k1 scalar group `ℤ/n` is a simple additive group: its only additive
subgroups are `⊥` and `⊤` (repackages `secp256k1_scalar_no_proper_subgroup`). -/
instance : IsSimpleAddGroup (ZMod Secp256k1.n) :=
  isSimpleAddGroup_of_prime_card (p := Secp256k1.n) (Nat.card_zmod Secp256k1.n)

end Ecdlp.Curve
